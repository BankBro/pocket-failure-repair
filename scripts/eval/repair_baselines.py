#!/usr/bin/env python3
"""Run minimal repair baselines for smoke candidates."""

from __future__ import annotations

import argparse
import math
import os
import tempfile
from pathlib import Path
from typing import Any

from rdkit import Chem
from rdkit.Chem import rdMolAlign

from pfr.chemistry.rdkit_scaffold import load_first_molecule, molecule_descriptors
from pfr.chemistry.perturb import translate_molecule, write_sdf
from pfr.feedback.geometry import anchor_distance_error, contact_fingerprint, parse_pdb_atom_coords, protein_ligand_geometry
from pfr.utils.io import load_yaml, read_jsonl, write_jsonl


FAILURE_TYPES = [
    "clash",
    "anchor_invalid",
    "geometry_invalid",
    "interaction_loss",
    "linker_too_flexible",
    "drug_likeness_drop",
    "score_hacking",
    "local_proposal_clash",
    "local_proposal_anchor_drift",
    "local_proposal_atom_substitution",
    "local_proposal_geometry_drift",
    "contact_degraded_local_edit",
]


def molecule_centroid(mol: Any) -> tuple[float, float, float] | None:
    if mol is None or mol.GetNumConformers() == 0:
        return None
    conf = mol.GetConformer()
    coords: list[tuple[float, float, float]] = []
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 1:
            continue
        pos = conf.GetAtomPosition(atom.GetIdx())
        coords.append((float(pos.x), float(pos.y), float(pos.z)))
    if not coords:
        return None
    count = float(len(coords))
    return (
        sum(coord[0] for coord in coords) / count,
        sum(coord[1] for coord in coords) / count,
        sum(coord[2] for coord in coords) / count,
    )


def centroid_translation_target(candidate: dict[str, Any]) -> tuple[float, float, float] | None:
    failed_path = candidate.get("failed_ligand_path")
    reference_path = candidate.get("ligand_path")
    if not failed_path or not reference_path:
        return None
    failed = load_first_molecule(failed_path)
    reference = load_first_molecule(reference_path)
    failed_centroid = molecule_centroid(failed)
    reference_centroid = molecule_centroid(reference)
    if failed_centroid is None or reference_centroid is None:
        return None
    return (
        reference_centroid[0] - failed_centroid[0],
        reference_centroid[1] - failed_centroid[1],
        reference_centroid[2] - failed_centroid[2],
    )


def numeric_feature(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def editable_pocket_direction_features(candidate: dict[str, Any]) -> list[float]:
    source_path = candidate.get("failed_ligand_path")
    protein_path = candidate.get("protein_path")
    editable_atoms = set(candidate.get("editable_atoms", []))
    mol = load_first_molecule(source_path) if source_path else None
    protein = parse_pdb_atom_coords(protein_path) if protein_path else []
    if mol is None or mol.GetNumConformers() == 0 or not protein or not editable_atoms:
        return [0.0, 0.0, 0.0, 1.0, 0.0]
    conf = mol.GetConformer()
    coords: list[tuple[float, float, float]] = []
    for atom in mol.GetAtoms():
        if atom.GetIdx() not in editable_atoms or atom.GetAtomicNum() == 1:
            continue
        pos = conf.GetAtomPosition(atom.GetIdx())
        coords.append((float(pos.x), float(pos.y), float(pos.z)))
    if not coords:
        return [0.0, 0.0, 0.0, 1.0, 0.0]
    count = float(len(coords))
    centroid = (
        sum(coord[0] for coord in coords) / count,
        sum(coord[1] for coord in coords) / count,
        sum(coord[2] for coord in coords) / count,
    )
    nearest = min(protein, key=lambda coord: math.sqrt(sum((coord[i] - centroid[i]) ** 2 for i in range(3))))
    vector = tuple(nearest[i] - centroid[i] for i in range(3))
    dist = math.sqrt(sum(value * value for value in vector))
    if dist <= 1e-8:
        return [0.0, 0.0, 0.0, 0.0, min(len(protein) / 5000.0, 1.0)]
    return [
        vector[0] / dist,
        vector[1] / dist,
        vector[2] / dist,
        min(dist / 10.0, 1.0),
        min(len(protein) / 5000.0, 1.0),
    ]


def feedback_features(candidate: dict[str, Any], feedback: dict[str, Any] | None, include_direction: bool = False) -> list[float]:
    geometry = (feedback or {}).get("geometry", {})
    sample_quality = candidate.get("sample_quality", {})
    contact_degradation = candidate.get("contact_degradation", {})
    descriptors = candidate.get("descriptors", {})
    failure_type = str(candidate.get("failure_type", ""))
    contact_recovery_loss = numeric_feature(contact_degradation.get("contact_recovery_loss"))
    contact_similarity = numeric_feature(contact_degradation.get("contact_similarity"), 1.0)
    features = [
        1.0,
        *[1.0 if failure_type == known else 0.0 for known in FAILURE_TYPES],
        numeric_feature(geometry.get("anchor_distance_error")) / 5.0,
        numeric_feature(geometry.get("clash_count")) / 10.0,
        numeric_feature(geometry.get("min_protein_ligand_distance"), 5.0) / 5.0,
        1.0 if geometry.get("editable_region_validity") is not False else 0.0,
        1.0 if sample_quality.get("evaluable_for_repair") is not False else 0.0,
        numeric_feature(geometry.get("editable_atom_count")) / 50.0,
        contact_recovery_loss,
        1.0 - contact_similarity,
        numeric_feature(contact_degradation.get("contact_recovery"), 1.0),
        numeric_feature(contact_degradation.get("contact_degradation_rank")) / 10.0,
        numeric_feature(descriptors.get("rotatable_bonds")) / 20.0,
        numeric_feature(descriptors.get("qed")),
    ]
    if include_direction:
        features.extend(editable_pocket_direction_features(candidate))
    return features


def shuffled_feedback_by_candidate(
    candidates: list[dict[str, Any]], feedback_rows: list[dict[str, Any]], seed: int
) -> dict[Any, dict[str, Any]]:
    ordered_candidate_ids = [candidate.get("candidate_id") for candidate in candidates if candidate.get("candidate_id") is not None]
    ordered_feedback = [row for row in feedback_rows if row.get("candidate_id") is not None]
    if len(ordered_feedback) < 2:
        return {row.get("candidate_id"): row for row in ordered_feedback}
    offset = 1 + (seed % (len(ordered_feedback) - 1))
    rotated = ordered_feedback[offset:] + ordered_feedback[:offset]
    return {candidate_id: feedback for candidate_id, feedback in zip(ordered_candidate_ids, rotated)}


def solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float] | None:
    size = len(vector)
    augmented = [row[:] + [vector[index]] for index, row in enumerate(matrix)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < 1e-12:
            return None
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        divisor = augmented[col][col]
        augmented[col] = [value / divisor for value in augmented[col]]
        for row in range(size):
            if row == col:
                continue
            factor = augmented[row][col]
            if factor == 0.0:
                continue
            augmented[row] = [value - factor * augmented[col][idx] for idx, value in enumerate(augmented[row])]
    return [row[-1] for row in augmented]


def fit_ridge_linear_model(
    training_rows: list[tuple[list[float], tuple[float, float, float]]], ridge: float = 1e-3
) -> list[list[float]] | None:
    if not training_rows:
        return None
    num_features = len(training_rows[0][0])
    xtx = [[0.0 for _ in range(num_features)] for _ in range(num_features)]
    xty = [[0.0, 0.0, 0.0] for _ in range(num_features)]
    for features, target in training_rows:
        for i in range(num_features):
            for j in range(num_features):
                xtx[i][j] += features[i] * features[j]
            for axis in range(3):
                xty[i][axis] += features[i] * target[axis]
    for i in range(1, num_features):
        xtx[i][i] += ridge
    coefficients: list[list[float]] = []
    for axis in range(3):
        solution = solve_linear_system(xtx, [row[axis] for row in xty])
        if solution is None:
            return None
        coefficients.append(solution)
    return coefficients


def dot(values: list[float], weights: list[float]) -> float:
    return sum(value * weight for value, weight in zip(values, weights))


def bounded_offset(value: float, limit: float = 3.0) -> float:
    return max(-limit, min(limit, value))


def refinement_offsets(seed: int) -> list[tuple[float, float, float]]:
    base = [
        (0.0, 0.0, 0.0),
        (-0.5, 0.0, 0.0),
        (0.5, 0.0, 0.0),
        (0.0, -0.5, 0.0),
        (0.0, 0.5, 0.0),
        (0.0, 0.0, -0.5),
        (0.0, 0.0, 0.5),
        (-1.0, 0.0, 0.0),
        (0.0, -1.0, 0.0),
        (0.0, 0.0, -1.0),
    ]
    shift = (seed % 3) * 0.1
    return [(x - shift, y + shift, z) for x, y, z in base]


def local_offsets(seed: int) -> list[tuple[float, float, float]]:
    scale = 0.15 + 0.05 * (seed % 3)
    return [
        (scale, 0.0, 0.0),
        (0.0, scale, 0.0),
        (0.0, 0.0, scale),
        (-scale, scale, 0.0),
        (0.0, -scale, scale),
    ]


def perturb_editable_coordinates(mol: Any, editable_atoms: list[int], offset: tuple[float, float, float]) -> Any:
    repaired = Chem.Mol(mol)
    if repaired.GetNumConformers() == 0:
        return repaired
    editable = [atom for atom in editable_atoms if atom < repaired.GetNumAtoms()]
    if not editable:
        editable = [atom.GetIdx() for atom in repaired.GetAtoms() if atom.GetAtomicNum() > 1]
    conf = repaired.GetConformer()
    for atom_idx in editable:
        pos = conf.GetAtomPosition(atom_idx)
        conf.SetAtomPosition(atom_idx, (pos.x + offset[0], pos.y + offset[1], pos.z + offset[2]))
    return repaired


def mutate_first_editable_atom(mol: Any, editable_atoms: list[int], atomic_num: int) -> Any | None:
    editable = [atom for atom in editable_atoms if atom < mol.GetNumAtoms()]
    if not editable:
        return None
    source_atom = mol.GetAtomWithIdx(editable[0])
    max_valence = {6: 4, 7: 3, 8: 2, 16: 6}.get(atomic_num)
    if max_valence is None or source_atom.GetTotalValence() > max_valence:
        return None
    repaired = Chem.RWMol(mol)
    atom = repaired.GetAtomWithIdx(editable[0])
    if atom.GetAtomicNum() == atomic_num or atom.GetAtomicNum() == 1:
        return None
    atom.SetAtomicNum(atomic_num)
    candidate = repaired.GetMol()
    try:
        Chem.SanitizeMol(candidate)
    except Exception:
        return None
    return candidate


def candidate_pool_molecules(candidate: dict[str, Any], mol: Any, seed: int) -> list[tuple[str, Any]]:
    pool: list[tuple[str, Any]] = []
    editable_atoms = candidate.get("editable_atoms", [])
    for index, offset in enumerate(refinement_offsets(seed)):
        pool.append((f"translation_{index}", translate_molecule(mol, *offset)))
    for index, offset in enumerate(local_offsets(seed)):
        pool.append((f"local_editable_shift_{index}", perturb_editable_coordinates(mol, editable_atoms, offset)))
    for atomic_num in (6, 7, 8, 16):
        mutated = mutate_first_editable_atom(mol, editable_atoms, atomic_num)
        if mutated is not None:
            pool.append((f"editable_atom_to_{atomic_num}", mutated))
    return pool


def anchor_centroid_translation_target(candidate: dict[str, Any]) -> tuple[float, float, float] | None:
    failed_path = candidate.get("failed_ligand_path")
    reference_path = candidate.get("ligand_path")
    anchors = [int(anchor) for anchor in candidate.get("anchor_atoms", [])]
    if not failed_path or not reference_path or not anchors:
        return None
    failed = load_first_molecule(failed_path)
    reference = load_first_molecule(reference_path)
    if failed is None or reference is None or failed.GetNumConformers() == 0 or reference.GetNumConformers() == 0:
        return None
    failed_conf = failed.GetConformer()
    reference_conf = reference.GetConformer()
    offsets: list[tuple[float, float, float]] = []
    for anchor in anchors:
        if anchor >= failed.GetNumAtoms() or anchor >= reference.GetNumAtoms():
            continue
        failed_pos = failed_conf.GetAtomPosition(anchor)
        reference_pos = reference_conf.GetAtomPosition(anchor)
        offsets.append(
            (
                float(reference_pos.x - failed_pos.x),
                float(reference_pos.y - failed_pos.y),
                float(reference_pos.z - failed_pos.z),
            )
        )
    if not offsets:
        return None
    count = float(len(offsets))
    return (
        bounded_offset(sum(offset[0] for offset in offsets) / count, limit=12.0),
        bounded_offset(sum(offset[1] for offset in offsets) / count, limit=12.0),
        bounded_offset(sum(offset[2] for offset in offsets) / count, limit=12.0),
    )


def repair_with_anchor_alignment_policy(candidate: dict[str, Any], output_dir: Path) -> tuple[Path | None, str]:
    source_path = candidate.get("failed_ligand_path")
    reference_path = candidate.get("ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    reference = load_first_molecule(reference_path) if reference_path else None
    if mol is None:
        return None, "feedback_anchor_alignment_policy_failed_to_read_failed_candidate"
    anchors = [int(anchor) for anchor in candidate.get("anchor_atoms", [])]
    valid_map = [
        (anchor, anchor)
        for anchor in anchors
        if reference is not None and anchor < mol.GetNumAtoms() and anchor < reference.GetNumAtoms()
    ]
    repair_id = f"{candidate['candidate_id']}__feedback_anchor_alignment_policy"
    candidates_to_score: list[tuple[str, Any]] = [("identity", Chem.Mol(mol))]
    offset = anchor_centroid_translation_target(candidate)
    if offset is not None:
        candidates_to_score.append(
            (
                "anchor_centroid_offset_{dx:.3f}_{dy:.3f}_{dz:.3f}".format(dx=offset[0], dy=offset[1], dz=offset[2]),
                translate_molecule(mol, *offset),
            )
        )
    if reference is not None and len(valid_map) >= 3:
        aligned = Chem.Mol(mol)
        try:
            rmsd = rdMolAlign.AlignMol(aligned, reference, atomMap=valid_map)
            candidates_to_score.append(("anchor_rigid_align_rmsd_{rmsd:.3f}".format(rmsd=float(rmsd)), aligned))
        except RuntimeError:
            pass
    best_path: Path | None = None
    best_label = "none"
    best_score: dict[str, Any] | None = None
    for index, (label, repaired) in enumerate(candidates_to_score):
        candidate_path = write_sdf(output_dir / f"{repair_id}__candidate_{index}_{label}.sdf", repaired)
        score = selection_geometry_score(candidate, candidate_path)
        if best_score is None or float(score["score"]) < float(best_score["score"]):
            best_path = candidate_path
            best_label = label
            best_score = score
    if best_path is None or best_score is None:
        return None, "feedback_anchor_alignment_policy_no_candidate"
    final_path = output_dir / f"{repair_id}.sdf"
    final_path.write_bytes(best_path.read_bytes())
    return final_path, "feedback_anchor_alignment_policy_selected_{label}_score_{score:.3f}".format(
        label=best_label, score=float(best_score["score"])
    )

def repair_with_geometry_refinement(
    candidate: dict[str, Any], output_dir: Path, seed: int
) -> tuple[Path | None, str]:
    source_path = candidate.get("failed_ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    if mol is None:
        return None, "feedback_geometry_refinement_failed_to_read_failed_candidate"
    repair_id = f"{candidate['candidate_id']}__feedback_geometry_refinement"
    best_path: Path | None = None
    best_score: dict[str, Any] | None = None
    best_label = "none"
    for index, (label, repaired) in enumerate(candidate_pool_molecules(candidate, mol, seed)):
        candidate_path = write_sdf(output_dir / f"{repair_id}__candidate_{index}_{label}.sdf", repaired)
        score = selection_geometry_score(candidate, candidate_path)
        if best_score is None or float(score["score"]) < float(best_score["score"]):
            best_score = score
            best_path = candidate_path
            best_label = label
    if best_path is None or best_score is None:
        return None, "feedback_geometry_refinement_no_candidate"
    final_path = output_dir / f"{repair_id}.sdf"
    final_path.write_bytes(best_path.read_bytes())
    return final_path, "feedback_geometry_refinement_selected_{label}_oracle_free_geometry_score_{score:.3f}".format(
        label=best_label,
        score=float(best_score["score"]),
    )


def build_linear_training_rows(
    candidates: list[dict[str, Any]], feedback_by_id: dict[Any, dict[str, Any]], heldout_complex_id: str | None
) -> list[tuple[list[float], tuple[float, float, float]]]:
    rows: list[tuple[list[float], tuple[float, float, float]]] = []
    for candidate in candidates:
        if heldout_complex_id is not None and candidate.get("complex_id") == heldout_complex_id:
            continue
        target = centroid_translation_target(candidate)
        if target is None:
            continue
        feedback = feedback_by_id.get(candidate.get("candidate_id"))
        rows.append((feedback_features(candidate, feedback), target))
    return rows


def oracle_free_geometry_target(candidate: dict[str, Any], seed: int) -> tuple[float, float, float] | None:
    source_path = candidate.get("failed_ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    if mol is None:
        return None
    best_offset: tuple[float, float, float] | None = None
    best_score: dict[str, Any] | None = None
    job_dir = Path(os.environ.get("CLAUDE_JOB_DIR", "outputs/logs"))
    job_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="oracle_free_targets_", dir=job_dir) as tmp_name:
        tmp_dir = Path(tmp_name)
        for index, offset in enumerate(refinement_offsets(seed) + local_offsets(seed)):
            repaired = translate_molecule(mol, *offset)
            tmp_path = write_sdf(tmp_dir / f"{candidate['candidate_id']}__candidate_{index}.sdf", repaired)
            score = selection_geometry_score(candidate, tmp_path)
            if best_score is None or float(score["score"]) < float(best_score["score"]):
                best_score = score
                best_offset = offset
    return best_offset


def cached_oracle_free_geometry_target(
    candidate: dict[str, Any], seed: int, target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None]
) -> tuple[float, float, float] | None:
    key = ("geometry", candidate.get("candidate_id"), seed)
    if key not in target_cache:
        target_cache[key] = oracle_free_geometry_target(candidate, seed)
    return target_cache[key]


def build_oracle_free_training_rows(
    candidates: list[dict[str, Any]],
    feedback_by_id: dict[Any, dict[str, Any]],
    heldout_complex_id: str | None,
    seed: int,
    target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None],
) -> list[tuple[list[float], tuple[float, float, float]]]:
    rows: list[tuple[list[float], tuple[float, float, float]]] = []
    for candidate in candidates:
        if heldout_complex_id is not None and candidate.get("complex_id") == heldout_complex_id:
            continue
        target = cached_oracle_free_geometry_target(candidate, seed, target_cache)
        if target is None:
            continue
        feedback = feedback_by_id.get(candidate.get("candidate_id"))
        rows.append((feedback_features(candidate, feedback), target))
    return rows


def learned_geometry_coefficients(
    candidates: list[dict[str, Any]],
    feedback_by_id: dict[Any, dict[str, Any]],
    heldout_complex_id: str,
    seed: int,
    target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None],
    coefficient_cache: dict[tuple[str | None, int, str], list[list[float]] | None],
) -> list[list[float]] | None:
    key: tuple[str | None, int, str] = (heldout_complex_id, seed, "geometry")
    if key not in coefficient_cache:
        training_rows = build_oracle_free_training_rows(candidates, feedback_by_id, heldout_complex_id, seed, target_cache)
        coefficient_cache[key] = fit_ridge_linear_model(training_rows)
    coefficients = coefficient_cache[key]
    if coefficients is not None:
        return coefficients
    fallback_key: tuple[str | None, int, str] = (None, seed, "geometry")
    if fallback_key not in coefficient_cache:
        training_rows = build_oracle_free_training_rows(candidates, feedback_by_id, None, seed, target_cache)
        coefficient_cache[fallback_key] = fit_ridge_linear_model(training_rows)
    return coefficient_cache[fallback_key]


def repair_with_learned_geometry_policy(
    candidate: dict[str, Any],
    output_dir: Path,
    seed: int,
    candidates: list[dict[str, Any]],
    feedback_by_id: dict[Any, dict[str, Any]],
    target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None],
    coefficient_cache: dict[tuple[str | None, int, str], list[list[float]] | None],
) -> tuple[Path | None, str]:
    source_path = candidate.get("failed_ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    if mol is None:
        return None, "feedback_learned_geometry_policy_failed_to_read_failed_candidate"
    coefficients = learned_geometry_coefficients(
        candidates,
        feedback_by_id,
        str(candidate.get("complex_id")),
        seed,
        target_cache,
        coefficient_cache,
        cache_namespace=cache_namespace,
    )
    if coefficients is None:
        return None, "feedback_learned_geometry_policy_no_oracle_free_training_signal"
    features = feedback_features(candidate, feedback_by_id.get(candidate.get("candidate_id")))
    dx, dy, dz = [bounded_offset(dot(features, axis_weights), limit=1.5) for axis_weights in coefficients]
    repaired = translate_molecule(mol, dx, dy, dz)
    repair_id = f"{candidate['candidate_id']}__feedback_learned_geometry_policy"
    repaired_path = write_sdf(output_dir / f"{repair_id}.sdf", repaired)
    return repaired_path, "feedback_learned_geometry_policy_oracle_free_pseudo_label_translation_{dx:.3f}_{dy:.3f}_{dz:.3f}".format(
        dx=dx, dy=dy, dz=dz
    )


def ridge_offset(features: list[float], coefficients: list[list[float]], limit: float = 1.5) -> tuple[float, float, float]:
    return tuple(bounded_offset(dot(features, axis_weights), limit=limit) for axis_weights in coefficients)  # type: ignore[return-value]


def residual_ensemble_offset(
    features: list[float],
    training_rows: list[tuple[list[float], tuple[float, float, float]]],
    coefficients: list[list[float]],
) -> tuple[float, float, float] | None:
    if not training_rows:
        return None
    base = ridge_offset(features, coefficients)
    scale = max(median_positive_distance(training_rows), 1e-6)
    residual = [0.0, 0.0, 0.0]
    total_weight = 0.0
    for train_features, target in training_rows:
        train_base = ridge_offset(train_features, coefficients)
        distance = feature_distance(features, train_features)
        weight = math.exp(-0.5 * (distance / scale) ** 2)
        total_weight += weight
        for axis in range(3):
            residual[axis] += weight * (target[axis] - train_base[axis])
    if total_weight <= 1e-12:
        return base
    return tuple(bounded_offset(base[axis] + residual[axis] / total_weight, limit=1.5) for axis in range(3))  # type: ignore[return-value]


def offset_neighborhood(offset: tuple[float, float, float], seed: int) -> list[tuple[float, float, float]]:
    radius = 0.2 + 0.05 * (seed % 3)
    dx, dy, dz = offset
    return [
        (dx, dy, dz),
        (dx + radius, dy, dz),
        (dx - radius, dy, dz),
        (dx, dy + radius, dz),
        (dx, dy - radius, dz),
        (dx, dy, dz + radius),
        (dx, dy, dz - radius),
    ]


def repair_with_residual_ensemble_policy(
    candidate: dict[str, Any],
    output_dir: Path,
    seed: int,
    candidates: list[dict[str, Any]],
    feedback_by_id: dict[Any, dict[str, Any]],
    target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None],
    training_cache: dict[tuple[str | None, int, str], list[tuple[list[float], tuple[float, float, float]]]],
    coefficient_cache: dict[tuple[str | None, int, str], list[list[float]] | None],
) -> tuple[Path | None, str]:
    source_path = candidate.get("failed_ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    if mol is None:
        return None, "feedback_residual_ensemble_policy_failed_to_read_failed_candidate"
    heldout_complex_id = str(candidate.get("complex_id"))
    key: tuple[str | None, int, str] = (heldout_complex_id, seed, "geometry")
    if key not in training_cache:
        training_cache[key] = build_oracle_free_training_rows(candidates, feedback_by_id, heldout_complex_id, seed, target_cache)
    training_rows = training_cache[key]
    if not training_rows:
        fallback_key: tuple[str | None, int, str] = (None, seed, "geometry")
        if fallback_key not in training_cache:
            training_cache[fallback_key] = build_oracle_free_training_rows(candidates, feedback_by_id, None, seed, target_cache)
        training_rows = training_cache[fallback_key]
        heldout_complex_id = "None"
    coefficients = learned_geometry_coefficients(candidates, feedback_by_id, heldout_complex_id, seed, target_cache, coefficient_cache)
    if coefficients is None:
        return None, "feedback_residual_ensemble_policy_no_oracle_free_training_signal"
    features = feedback_features(candidate, feedback_by_id.get(candidate.get("candidate_id")))
    offset = residual_ensemble_offset(features, training_rows, coefficients)
    if offset is None:
        return None, "feedback_residual_ensemble_policy_no_residual_offset"
    repair_id = f"{candidate['candidate_id']}__feedback_residual_ensemble_policy"
    best_path: Path | None = None
    best_score: dict[str, Any] | None = None
    best_offset = offset
    for index, candidate_offset in enumerate(offset_neighborhood(offset, seed)):
        repaired = translate_molecule(mol, *candidate_offset)
        candidate_path = write_sdf(output_dir / f"{repair_id}__candidate_{index}.sdf", repaired)
        score = selection_geometry_score(candidate, candidate_path)
        if best_score is None or float(score["score"]) < float(best_score["score"]):
            best_score = score
            best_path = candidate_path
            best_offset = candidate_offset
    if best_path is None or best_score is None:
        return None, "feedback_residual_ensemble_policy_no_candidate"
    final_path = output_dir / f"{repair_id}.sdf"
    final_path.write_bytes(best_path.read_bytes())
    return final_path, "feedback_residual_ensemble_policy_ridge_plus_kernel_residual_offset_{dx:.3f}_{dy:.3f}_{dz:.3f}_score_{score:.3f}".format(
        dx=best_offset[0], dy=best_offset[1], dz=best_offset[2], score=float(best_score["score"])
    )


def feature_distance(left: list[float], right: list[float]) -> float:
    return math.sqrt(sum((a - b) * (a - b) for a, b in zip(left, right)))


def median_positive_distance(training_rows: list[tuple[list[float], tuple[float, float, float]]]) -> float:
    distances: list[float] = []
    for i, (left, _) in enumerate(training_rows):
        for right, _ in training_rows[:i]:
            distance = feature_distance(left, right)
            if distance > 1e-9:
                distances.append(distance)
    if not distances:
        return 1.0
    distances.sort()
    return distances[len(distances) // 2]


def kernel_geometry_offset(
    features: list[float], training_rows: list[tuple[list[float], tuple[float, float, float]]], bandwidth: float | None = None
) -> tuple[float, float, float] | None:
    if not training_rows:
        return None
    scale = max(bandwidth or median_positive_distance(training_rows), 1e-6)
    weighted = [0.0, 0.0, 0.0]
    total_weight = 0.0
    for train_features, target in training_rows:
        distance = feature_distance(features, train_features)
        weight = math.exp(-0.5 * (distance / scale) ** 2)
        total_weight += weight
        for axis in range(3):
            weighted[axis] += weight * target[axis]
    if total_weight <= 1e-12:
        return None
    return tuple(value / total_weight for value in weighted)  # type: ignore[return-value]


def repair_with_kernel_geometry_policy(
    candidate: dict[str, Any],
    output_dir: Path,
    seed: int,
    candidates: list[dict[str, Any]],
    feedback_by_id: dict[Any, dict[str, Any]],
    target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None],
    training_cache: dict[tuple[str | None, int, str], list[tuple[list[float], tuple[float, float, float]]]],
) -> tuple[Path | None, str]:
    source_path = candidate.get("failed_ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    if mol is None:
        return None, "feedback_kernel_geometry_policy_failed_to_read_failed_candidate"
    heldout_complex_id = str(candidate.get("complex_id"))
    key: tuple[str | None, int, str] = (heldout_complex_id, seed, "geometry")
    if key not in training_cache:
        training_cache[key] = build_oracle_free_training_rows(candidates, feedback_by_id, heldout_complex_id, seed, target_cache)
    training_rows = training_cache[key]
    if not training_rows:
        fallback_key: tuple[str | None, int, str] = (None, seed, "geometry")
        if fallback_key not in training_cache:
            training_cache[fallback_key] = build_oracle_free_training_rows(candidates, feedback_by_id, None, seed, target_cache)
        training_rows = training_cache[fallback_key]
    features = feedback_features(candidate, feedback_by_id.get(candidate.get("candidate_id")))
    offset = kernel_geometry_offset(features, training_rows)
    if offset is None:
        return None, "feedback_kernel_geometry_policy_no_oracle_free_training_signal"
    dx, dy, dz = [bounded_offset(value, limit=1.5) for value in offset]
    repaired = translate_molecule(mol, dx, dy, dz)
    repair_id = f"{candidate['candidate_id']}__feedback_kernel_geometry_policy"
    repaired_path = write_sdf(output_dir / f"{repair_id}.sdf", repaired)
    return repaired_path, "feedback_kernel_geometry_policy_oracle_free_rbf_translation_{dx:.3f}_{dy:.3f}_{dz:.3f}".format(
        dx=dx, dy=dy, dz=dz
    )


def nearest_geometry_offset(
    features: list[float], training_rows: list[tuple[list[float], tuple[float, float, float]]]
) -> tuple[float, float, float] | None:
    if not training_rows:
        return None
    _, target = min(training_rows, key=lambda row: feature_distance(features, row[0]))
    return target


def feature_standard_deviations(training_rows: list[tuple[list[float], tuple[float, float, float]]]) -> list[float]:
    if not training_rows:
        return []
    num_features = len(training_rows[0][0])
    deviations: list[float] = []
    for index in range(num_features):
        values = [row[0][index] for row in training_rows if index < len(row[0])]
        if not values:
            deviations.append(1.0)
            continue
        mean_value = sum(values) / len(values)
        variance = sum((value - mean_value) ** 2 for value in values) / len(values)
        deviation = math.sqrt(variance)
        deviations.append(deviation if deviation > 1e-8 else 1.0)
    return deviations


def scaled_feature_distance(features: list[float], other: list[float], deviations: list[float]) -> float:
    return sum(((left - right) / deviation) ** 2 for left, right, deviation in zip(features, other, deviations))


def nearest_scaled_geometry_offset(
    features: list[float], training_rows: list[tuple[list[float], tuple[float, float, float]]]
) -> tuple[float, float, float] | None:
    if not training_rows:
        return None
    deviations = feature_standard_deviations(training_rows)
    _, target = min(training_rows, key=lambda row: scaled_feature_distance(features, row[0], deviations))
    return target


def repair_with_knn_geometry_policy(
    candidate: dict[str, Any],
    output_dir: Path,
    seed: int,
    candidates: list[dict[str, Any]],
    feedback_by_id: dict[Any, dict[str, Any]],
    target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None],
    training_cache: dict[tuple[str | None, int, str], list[tuple[list[float], tuple[float, float, float]]]],
) -> tuple[Path | None, str]:
    source_path = candidate.get("failed_ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    if mol is None:
        return None, "feedback_knn_geometry_policy_failed_to_read_failed_candidate"
    heldout_complex_id = str(candidate.get("complex_id"))
    key: tuple[str | None, int, str] = (heldout_complex_id, seed, "geometry")
    if key not in training_cache:
        training_cache[key] = build_oracle_free_training_rows(candidates, feedback_by_id, heldout_complex_id, seed, target_cache)
    training_rows = training_cache[key]
    if not training_rows:
        fallback_key: tuple[str | None, int, str] = (None, seed, "geometry")
        if fallback_key not in training_cache:
            training_cache[fallback_key] = build_oracle_free_training_rows(candidates, feedback_by_id, None, seed, target_cache)
        training_rows = training_cache[fallback_key]
    features = feedback_features(candidate, feedback_by_id.get(candidate.get("candidate_id")))
    offset = nearest_geometry_offset(features, training_rows)
    if offset is None:
        return None, "feedback_knn_geometry_policy_no_oracle_free_training_signal"
    dx, dy, dz = [bounded_offset(value, limit=1.5) for value in offset]
    repaired = translate_molecule(mol, dx, dy, dz)
    repair_id = f"{candidate['candidate_id']}__feedback_knn_geometry_policy"
    repaired_path = write_sdf(output_dir / f"{repair_id}.sdf", repaired)
    return repaired_path, "feedback_knn_geometry_policy_oracle_free_nearest_translation_{dx:.3f}_{dy:.3f}_{dz:.3f}".format(
        dx=dx, dy=dy, dz=dz
    )


def editable_contact_score(candidate: dict[str, Any], ligand_path: Path) -> dict[str, Any]:
    geometry = protein_ligand_geometry(candidate.get("protein_path"), ligand_path)
    clash_count = geometry.get("clash_count")
    min_distance = geometry.get("min_protein_ligand_distance")
    anchor_error = anchor_distance_error(candidate.get("ligand_path"), ligand_path, candidate.get("anchor_atoms", []))
    contacts = contact_fingerprint(candidate.get("protein_path"), ligand_path)
    score = -float(len(contacts))
    score += float(clash_count or 0) * 25.0
    if min_distance is None:
        score += 1000.0
    elif float(min_distance) < 2.0:
        score += (2.0 - float(min_distance)) * 20.0
    if anchor_error is not None and anchor_error > 1.0:
        score += (float(anchor_error) - 1.0) * 50.0
    return {
        "score": score,
        "contact_count": len(contacts),
        "clash_count": clash_count,
        "min_protein_ligand_distance": min_distance,
        "anchor_distance_error": anchor_error,
    }


def editable_repair_offsets(seed: int) -> list[tuple[float, float, float]]:
    radius = 0.25 + 0.05 * (seed % 3)
    return [
        (0.0, 0.0, 0.0),
        (radius, 0.0, 0.0),
        (-radius, 0.0, 0.0),
        (0.0, radius, 0.0),
        (0.0, -radius, 0.0),
        (0.0, 0.0, radius),
        (0.0, 0.0, -radius),
        (2.0 * radius, -radius, 0.0),
        (-radius, 2.0 * radius, 0.0),
        (0.0, -radius, 2.0 * radius),
    ]


def editable_candidate_score(candidate: dict[str, Any], ligand_path: Path, mode: str) -> dict[str, Any]:
    contact_score = editable_contact_score(candidate, ligand_path)
    mol = load_first_molecule(ligand_path)
    global_score = global_ligand_score(mol) if mol is not None else {"score": 1000.0}
    if mode == "interaction_only":
        score = -float(contact_score["contact_count"])
    elif mode == "geometry_only":
        score = float(contact_score.get("clash_count") or 0) * 25.0
        min_distance = contact_score.get("min_protein_ligand_distance")
        anchor_error = contact_score.get("anchor_distance_error")
        if min_distance is None:
            score += 1000.0
        elif float(min_distance) < 2.0:
            score += (2.0 - float(min_distance)) * 20.0
        if anchor_error is not None and anchor_error > 1.0:
            score += (float(anchor_error) - 1.0) * 50.0
    elif mode == "global_only":
        score = float(global_score["score"])
    else:
        score = float(contact_score["score"]) + 0.1 * float(global_score["score"])
    return {**contact_score, "score": score, "global_score": global_score.get("score"), "mode": mode}


def repair_with_editable_ablation_policy(
    candidate: dict[str, Any], output_dir: Path, seed: int, baseline: str, mode: str
) -> tuple[Path | None, str]:
    source_path = candidate.get("failed_ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    if mol is None:
        return None, f"{baseline}_failed_to_read_failed_candidate"
    editable_atoms = candidate.get("editable_atoms", [])
    repair_id = f"{candidate['candidate_id']}__{baseline}"
    best_path: Path | None = None
    best_score: dict[str, Any] | None = None
    best_offset = (0.0, 0.0, 0.0)
    for index, offset in enumerate(editable_repair_offsets(seed)):
        repaired = perturb_editable_coordinates(mol, editable_atoms, offset)
        candidate_path = write_sdf(output_dir / f"{repair_id}__candidate_{index}.sdf", repaired)
        score = editable_candidate_score(candidate, candidate_path, mode)
        if best_score is None or float(score["score"]) < float(best_score["score"]):
            best_score = score
            best_path = candidate_path
            best_offset = offset
    if best_path is None or best_score is None:
        return None, f"{baseline}_no_candidate"
    final_path = output_dir / f"{repair_id}.sdf"
    final_path.write_bytes(best_path.read_bytes())
    return final_path, "{baseline}_mode_{mode}_offset_{dx:.3f}_{dy:.3f}_{dz:.3f}_contacts_{contacts}_score_{score:.3f}".format(
        baseline=baseline,
        mode=mode,
        dx=best_offset[0],
        dy=best_offset[1],
        dz=best_offset[2],
        contacts=int(best_score["contact_count"]),
        score=float(best_score["score"]),
    )


def repair_with_no_failed_candidate_policy(candidate: dict[str, Any], output_dir: Path, seed: int) -> tuple[Path | None, str]:
    reference_path = candidate.get("ligand_path")
    mol = load_first_molecule(reference_path) if reference_path else None
    if mol is None:
        return None, "no_failed_candidate_policy_failed_to_read_reference_ligand"
    baseline = "no_failed_candidate_policy"
    editable_atoms = candidate.get("editable_atoms", [])
    repair_id = f"{candidate['candidate_id']}__{baseline}"
    best_path: Path | None = None
    best_score: dict[str, Any] | None = None
    best_offset = (0.0, 0.0, 0.0)
    for index, offset in enumerate(editable_repair_offsets(seed)):
        repaired = perturb_editable_coordinates(mol, editable_atoms, offset)
        candidate_path = write_sdf(output_dir / f"{repair_id}__candidate_{index}.sdf", repaired)
        loaded = load_first_molecule(candidate_path)
        score = global_ligand_score(loaded) if loaded is not None else {"score": 1000.0}
        if best_score is None or float(score["score"]) < float(best_score["score"]):
            best_score = score
            best_path = candidate_path
            best_offset = offset
    if best_path is None or best_score is None:
        return None, "no_failed_candidate_policy_no_candidate"
    final_path = output_dir / f"{repair_id}.sdf"
    final_path.write_bytes(best_path.read_bytes())
    return final_path, "no_failed_candidate_policy_reference_only_global_score_offset_{dx:.3f}_{dy:.3f}_{dz:.3f}_score_{score:.3f}".format(
        dx=best_offset[0], dy=best_offset[1], dz=best_offset[2], score=float(best_score["score"])
    )


def editable_contact_target(candidate: dict[str, Any], seed: int) -> tuple[float, float, float] | None:
    source_path = candidate.get("failed_ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    if mol is None:
        return None
    editable_atoms = candidate.get("editable_atoms", [])
    best_offset: tuple[float, float, float] | None = None
    best_score: dict[str, Any] | None = None
    job_dir = Path(os.environ.get("CLAUDE_JOB_DIR", "outputs/logs"))
    job_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="editable_contact_targets_", dir=job_dir) as tmp_name:
        tmp_dir = Path(tmp_name)
        for index, offset in enumerate(editable_repair_offsets(seed)):
            repaired = perturb_editable_coordinates(mol, editable_atoms, offset)
            tmp_path = write_sdf(tmp_dir / f"{candidate['candidate_id']}__editable_contact_{index}.sdf", repaired)
            score = editable_contact_score(candidate, tmp_path)
            if best_score is None or float(score["score"]) < float(best_score["score"]):
                best_score = score
                best_offset = offset
    return best_offset


def cached_editable_contact_target(
    candidate: dict[str, Any], seed: int, target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None]
) -> tuple[float, float, float] | None:
    key = ("editable_contact", candidate.get("candidate_id"), seed)
    if key not in target_cache:
        target_cache[key] = editable_contact_target(candidate, seed)
    return target_cache[key]


def offset_label(offset: tuple[float, float, float] | None, seed: int) -> int | None:
    if offset is None:
        return None
    offsets = editable_repair_offsets(seed)
    distances = [sum((float(a) - float(b)) ** 2 for a, b in zip(offset, trial)) for trial in offsets]
    return min(range(len(offsets)), key=lambda index: distances[index])


def fit_nearest_offset_label_rows(
    candidates: list[dict[str, Any]],
    feedback_by_id: dict[Any, dict[str, Any]],
    heldout_complex_id: str | None,
    seed: int,
    target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None],
    include_direction: bool = False,
) -> list[tuple[list[float], int]]:
    rows: list[tuple[list[float], int]] = []
    for candidate in candidates:
        if heldout_complex_id is not None and candidate.get("complex_id") == heldout_complex_id:
            continue
        label = offset_label(cached_editable_contact_target(candidate, seed, target_cache), seed)
        if label is None:
            continue
        rows.append((feedback_features(candidate, feedback_by_id.get(candidate.get("candidate_id")), include_direction), label))
    return rows


def classified_editable_contact_offset(
    candidate: dict[str, Any],
    seed: int,
    candidates: list[dict[str, Any]],
    feedback_by_id: dict[Any, dict[str, Any]],
    target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None],
    label_cache: dict[tuple[str | None, int, str], list[tuple[list[float], int]]],
    cache_namespace: str,
    include_direction: bool = False,
) -> tuple[float, float, float] | None:
    heldout_complex_id = str(candidate.get("complex_id"))
    key = (heldout_complex_id, seed, cache_namespace)
    if key not in label_cache:
        label_cache[key] = fit_nearest_offset_label_rows(candidates, feedback_by_id, heldout_complex_id, seed, target_cache, include_direction)
    rows = label_cache[key]
    if not rows:
        fallback_key = (None, seed, cache_namespace)
        if fallback_key not in label_cache:
            label_cache[fallback_key] = fit_nearest_offset_label_rows(candidates, feedback_by_id, None, seed, target_cache, include_direction)
        rows = label_cache[fallback_key]
    if not rows:
        return None
    features = feedback_features(candidate, feedback_by_id.get(candidate.get("candidate_id")), include_direction)
    best_features, label = min(rows, key=lambda row: sum((a - b) ** 2 for a, b in zip(features, row[0])))
    return editable_repair_offsets(seed)[label]


def repair_with_classified_editable_contact_policy(
    candidate: dict[str, Any],
    output_dir: Path,
    seed: int,
    candidates: list[dict[str, Any]],
    feedback_by_id: dict[Any, dict[str, Any]],
    target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None],
    label_cache: dict[tuple[str | None, int, str], list[tuple[list[float], int]]],
    baseline: str = "feedback_classified_editable_contact_policy",
    include_direction: bool = False,
) -> tuple[Path | None, str]:
    source_path = candidate.get("failed_ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    if mol is None:
        return None, f"{baseline}_failed_to_read_failed_candidate"
    offset = classified_editable_contact_offset(
        candidate,
        seed,
        candidates,
        feedback_by_id,
        target_cache,
        label_cache,
        cache_namespace=baseline,
        include_direction=include_direction,
    )
    if offset is None:
        return None, f"{baseline}_no_training_signal"
    repaired = perturb_editable_coordinates(mol, candidate.get("editable_atoms", []), offset)
    repair_id = f"{candidate['candidate_id']}__{baseline}"
    repaired_path = write_sdf(output_dir / f"{repair_id}.sdf", repaired)
    score = editable_contact_score(candidate, repaired_path)
    return repaired_path, "{baseline}_classified_offset_{dx:.3f}_{dy:.3f}_{dz:.3f}_contacts_{contacts}_score_{score:.3f}".format(
        baseline=baseline,
        dx=offset[0],
        dy=offset[1],
        dz=offset[2],
        contacts=int(score["contact_count"]),
        score=float(score["score"]),
    )


def build_editable_contact_training_rows(
    candidates: list[dict[str, Any]],
    feedback_by_id: dict[Any, dict[str, Any]],
    heldout_complex_id: str | None,
    seed: int,
    target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None],
    include_direction: bool = False,
) -> list[tuple[list[float], tuple[float, float, float]]]:
    rows: list[tuple[list[float], tuple[float, float, float]]] = []
    for candidate in candidates:
        if heldout_complex_id is not None and candidate.get("complex_id") == heldout_complex_id:
            continue
        target = cached_editable_contact_target(candidate, seed, target_cache)
        if target is None:
            continue
        feedback = feedback_by_id.get(candidate.get("candidate_id"))
        rows.append((feedback_features(candidate, feedback, include_direction), target))
    return rows


def learned_editable_contact_offset(
    candidate: dict[str, Any],
    seed: int,
    candidates: list[dict[str, Any]],
    feedback_by_id: dict[Any, dict[str, Any]],
    target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None],
    training_cache: dict[tuple[str | None, int, str], list[tuple[list[float], tuple[float, float, float]]]],
    cache_namespace: str = "editable_contact",
    include_direction: bool = False,
    scale_features: bool = False,
) -> tuple[float, float, float] | None:
    heldout_complex_id = str(candidate.get("complex_id"))
    key: tuple[str | None, int, str] = (heldout_complex_id, seed, cache_namespace)
    if key not in training_cache:
        training_cache[key] = build_editable_contact_training_rows(
            candidates, feedback_by_id, heldout_complex_id, seed, target_cache, include_direction
        )
    training_rows = training_cache[key]
    if not training_rows:
        fallback_key: tuple[str | None, int, str] = (None, seed, cache_namespace)
        if fallback_key not in training_cache:
            training_cache[fallback_key] = build_editable_contact_training_rows(
                candidates, feedback_by_id, None, seed, target_cache, include_direction
            )
        training_rows = training_cache[fallback_key]
    features = feedback_features(candidate, feedback_by_id.get(candidate.get("candidate_id")), include_direction)
    if scale_features:
        return nearest_scaled_geometry_offset(features, training_rows)
    return nearest_geometry_offset(features, training_rows)


def ridge_editable_contact_coefficients(
    candidates: list[dict[str, Any]],
    feedback_by_id: dict[Any, dict[str, Any]],
    heldout_complex_id: str,
    seed: int,
    target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None],
    coefficient_cache: dict[tuple[str | None, int, str], list[list[float]] | None],
    cache_namespace: str = "editable_contact",
) -> list[list[float]] | None:
    key: tuple[str | None, int, str] = (heldout_complex_id, seed, cache_namespace)
    if key not in coefficient_cache:
        training_rows = build_editable_contact_training_rows(candidates, feedback_by_id, heldout_complex_id, seed, target_cache)
        coefficient_cache[key] = fit_ridge_linear_model(training_rows, ridge=1e-2)
    coefficients = coefficient_cache[key]
    if coefficients is not None:
        return coefficients
    fallback_key: tuple[str | None, int, str] = (None, seed, cache_namespace)
    if fallback_key not in coefficient_cache:
        training_rows = build_editable_contact_training_rows(candidates, feedback_by_id, None, seed, target_cache)
        coefficient_cache[fallback_key] = fit_ridge_linear_model(training_rows, ridge=1e-2)
    return coefficient_cache[fallback_key]


def repair_with_ridge_editable_contact_policy(
    candidate: dict[str, Any],
    output_dir: Path,
    seed: int,
    candidates: list[dict[str, Any]],
    feedback_by_id: dict[Any, dict[str, Any]],
    target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None],
    coefficient_cache: dict[tuple[str | None, int, str], list[list[float]] | None],
    baseline: str = "feedback_ridge_editable_contact_policy",
    cache_namespace: str = "editable_contact",
) -> tuple[Path | None, str]:
    source_path = candidate.get("failed_ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    if mol is None:
        return None, f"{baseline}_failed_to_read_failed_candidate"
    coefficients = ridge_editable_contact_coefficients(
        candidates,
        feedback_by_id,
        str(candidate.get("complex_id")),
        seed,
        target_cache,
        coefficient_cache,
        cache_namespace=cache_namespace,
    )
    if coefficients is None:
        return None, f"{baseline}_no_training_signal"
    features = feedback_features(candidate, feedback_by_id.get(candidate.get("candidate_id")))
    dx, dy, dz = [bounded_offset(dot(features, axis_weights), limit=0.8) for axis_weights in coefficients]
    repaired = perturb_editable_coordinates(mol, candidate.get("editable_atoms", []), (dx, dy, dz))
    repair_id = f"{candidate['candidate_id']}__{baseline}"
    repaired_path = write_sdf(output_dir / f"{repair_id}.sdf", repaired)
    score = editable_contact_score(candidate, repaired_path)
    return repaired_path, "{baseline}_offset_{dx:.3f}_{dy:.3f}_{dz:.3f}_contacts_{contacts}_score_{score:.3f}".format(
        baseline=baseline,
        dx=dx,
        dy=dy,
        dz=dz,
        contacts=int(score["contact_count"]),
        score=float(score["score"]),
    )


def repair_with_learned_editable_contact_policy(
    candidate: dict[str, Any],
    output_dir: Path,
    seed: int,
    candidates: list[dict[str, Any]],
    feedback_by_id: dict[Any, dict[str, Any]],
    target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None],
    training_cache: dict[tuple[str | None, int, str], list[tuple[list[float], tuple[float, float, float]]]],
    baseline: str = "feedback_learned_editable_contact_policy",
    include_direction: bool = False,
    scale_features: bool = False,
) -> tuple[Path | None, str]:
    source_path = candidate.get("failed_ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    if mol is None:
        return None, f"{baseline}_failed_to_read_failed_candidate"
    offset = learned_editable_contact_offset(
        candidate,
        seed,
        candidates,
        feedback_by_id,
        target_cache,
        training_cache,
        cache_namespace=baseline,
        include_direction=include_direction,
        scale_features=scale_features,
    )
    if offset is None:
        return None, f"{baseline}_no_training_signal"
    dx, dy, dz = [bounded_offset(value, limit=0.8) for value in offset]
    repaired = perturb_editable_coordinates(mol, candidate.get("editable_atoms", []), (dx, dy, dz))
    repair_id = f"{candidate['candidate_id']}__{baseline}"
    repaired_path = write_sdf(output_dir / f"{repair_id}.sdf", repaired)
    score = editable_contact_score(candidate, repaired_path)
    distance_mode = "scaled_nearest_offset" if scale_features else "nearest_offset"
    return repaired_path, "{baseline}_{distance_mode}_{dx:.3f}_{dy:.3f}_{dz:.3f}_contacts_{contacts}_score_{score:.3f}".format(
        baseline=baseline,
        distance_mode=distance_mode,
        dx=dx,
        dy=dy,
        dz=dz,
        contacts=int(score["contact_count"]),
        score=float(score["score"]),
    )


def budgeted_learned_offsets(base_offset: tuple[float, float, float], seed: int) -> list[tuple[float, float, float]]:
    bx, by, bz = base_offset
    radius = 0.12 + 0.03 * (seed % 3)
    deltas = [
        (0.0, 0.0, 0.0),
        (radius, 0.0, 0.0),
        (-radius, 0.0, 0.0),
        (0.0, radius, 0.0),
        (0.0, -radius, 0.0),
        (0.0, 0.0, radius),
        (0.0, 0.0, -radius),
        (radius, -radius, 0.0),
        (-radius, radius, 0.0),
        (0.0, -radius, radius),
    ]
    return [
        (
            bounded_offset(bx + dx, limit=0.8),
            bounded_offset(by + dy, limit=0.8),
            bounded_offset(bz + dz, limit=0.8),
        )
        for dx, dy, dz in deltas
    ]


def repair_with_budgeted_learned_editable_contact_policy(
    candidate: dict[str, Any],
    output_dir: Path,
    seed: int,
    candidates: list[dict[str, Any]],
    feedback_by_id: dict[Any, dict[str, Any]],
    target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None],
    training_cache: dict[tuple[str | None, int, str], list[tuple[list[float], tuple[float, float, float]]]],
    baseline: str = "feedback_budgeted_learned_editable_contact_policy",
) -> tuple[Path | None, str]:
    source_path = candidate.get("failed_ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    if mol is None:
        return None, f"{baseline}_failed_to_read_failed_candidate"
    offset = learned_editable_contact_offset(
        candidate, seed, candidates, feedback_by_id, target_cache, training_cache, cache_namespace=baseline
    )
    if offset is None:
        return None, f"{baseline}_no_training_signal"
    editable_atoms = candidate.get("editable_atoms", [])
    repair_id = f"{candidate['candidate_id']}__{baseline}"
    best_path: Path | None = None
    best_score: dict[str, Any] | None = None
    best_offset = (0.0, 0.0, 0.0)
    for index, trial_offset in enumerate(budgeted_learned_offsets(offset, seed)):
        repaired = perturb_editable_coordinates(mol, editable_atoms, trial_offset)
        candidate_path = write_sdf(output_dir / f"{repair_id}__candidate_{index}.sdf", repaired)
        score = editable_contact_score(candidate, candidate_path)
        if best_score is None or float(score["score"]) < float(best_score["score"]):
            best_score = score
            best_path = candidate_path
            best_offset = trial_offset
    if best_path is None or best_score is None:
        return None, f"{baseline}_no_candidate"
    final_path = output_dir / f"{repair_id}.sdf"
    final_path.write_bytes(best_path.read_bytes())
    return final_path, "{baseline}_budget10_offset_{dx:.3f}_{dy:.3f}_{dz:.3f}_contacts_{contacts}_score_{score:.3f}".format(
        baseline=baseline,
        dx=best_offset[0],
        dy=best_offset[1],
        dz=best_offset[2],
        contacts=int(best_score["contact_count"]),
        score=float(best_score["score"]),
    )


def repair_with_linear_refinement(
    candidate: dict[str, Any],
    output_dir: Path,
    candidates: list[dict[str, Any]],
    feedback_by_id: dict[Any, dict[str, Any]],
) -> tuple[Path | None, str]:
    source_path = candidate.get("failed_ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    if mol is None:
        return None, "feedback_linear_refinement_failed_to_read_failed_candidate"
    training_rows = build_linear_training_rows(candidates, feedback_by_id, str(candidate.get("complex_id")))
    coefficients = fit_ridge_linear_model(training_rows)
    if coefficients is None:
        training_rows = build_linear_training_rows(candidates, feedback_by_id, None)
        coefficients = fit_ridge_linear_model(training_rows)
    if coefficients is None:
        return None, "feedback_linear_refinement_no_supervised_training_signal"
    features = feedback_features(candidate, feedback_by_id.get(candidate.get("candidate_id")))
    dx, dy, dz = [bounded_offset(dot(features, axis_weights), limit=3.0) for axis_weights in coefficients]
    repaired = translate_molecule(mol, dx, dy, dz)
    repair_id = f"{candidate['candidate_id']}__feedback_linear_refinement"
    repaired_path = write_sdf(output_dir / f"{repair_id}.sdf", repaired)
    return repaired_path, "feedback_linear_refinement_reference_centroid_sanity_translation_{dx:.3f}_{dy:.3f}_{dz:.3f}".format(
        dx=dx, dy=dy, dz=dz
    )


def selection_geometry_score(candidate: dict[str, Any], ligand_path: Path) -> dict[str, Any]:
    geometry = protein_ligand_geometry(candidate.get("protein_path"), ligand_path)
    clash_count = geometry.get("clash_count")
    min_distance = geometry.get("min_protein_ligand_distance")
    score = float(clash_count or 0) * 10.0
    if min_distance is None:
        score += 1000.0
    else:
        score += abs(float(min_distance) - 2.5)
    return {
        "score": score,
        "clash_count": clash_count,
        "min_protein_ligand_distance": min_distance,
    }


def score_written_candidate(candidate: dict[str, Any], ligand_path: Path) -> dict[str, Any]:
    return selection_geometry_score(candidate, ligand_path)


def write_candidate_molecule(
    candidate: dict[str, Any], output_dir: Path, baseline: str, mol: Any, suffix: str
) -> Path:
    repair_id = f"{candidate['candidate_id']}__{baseline}"
    return write_sdf(output_dir / f"{repair_id}{suffix}.sdf", mol)


def write_translated_candidate(
    candidate: dict[str, Any], output_dir: Path, baseline: str, mol: Any, suffix: str, offset: tuple[float, float, float]
) -> Path:
    translated = translate_molecule(mol, *offset)
    return write_candidate_molecule(candidate, output_dir, baseline, translated, suffix)


def repair_with_direct_regeneration(candidate: dict[str, Any], output_dir: Path, seed: int) -> tuple[Path | None, str]:
    source_path = candidate.get("failed_ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    if mol is None:
        return None, "direct_regeneration_failed_to_read_failed_candidate"
    pool = candidate_pool_molecules(candidate, mol, seed)
    if not pool:
        return None, "direct_regeneration_no_candidate"
    index = (seed + len(str(candidate.get("candidate_id", "")))) % len(pool)
    label, repaired = pool[index]
    repaired_path = write_candidate_molecule(candidate, output_dir, "direct_regeneration", repaired, "")
    return repaired_path, f"direct_regeneration_selected_{label}_from_local_rgroup_candidate_pool"


def global_ligand_score(mol: Any) -> dict[str, Any]:
    descriptors = molecule_descriptors(mol)
    qed = numeric_feature(descriptors.get("qed"))
    logp = numeric_feature(descriptors.get("logp"))
    rotatable = numeric_feature(descriptors.get("rotatable_bonds"))
    tpsa = numeric_feature(descriptors.get("tpsa"))
    score = -qed + max(0.0, abs(logp - 2.5) - 2.5) + max(0.0, rotatable - 10.0) * 0.1
    score += max(0.0, tpsa - 140.0) * 0.01
    return {
        "score": score,
        "qed": qed,
        "logp": logp,
        "rotatable_bonds": rotatable,
        "tpsa": tpsa,
    }


def repair_with_best_of_n(candidate: dict[str, Any], output_dir: Path, seed: int) -> tuple[Path | None, str]:
    source_path = candidate.get("failed_ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    if mol is None:
        return None, "best_of_n_failed_to_read_failed_candidate"
    best_path: Path | None = None
    best_score: dict[str, Any] | None = None
    for index, (label, repaired) in enumerate(candidate_pool_molecules(candidate, mol, seed)):
        candidate_path = write_candidate_molecule(candidate, output_dir, "best_of_n", repaired, f"__candidate_{index}_{label}")
        translated = load_first_molecule(candidate_path)
        if translated is None:
            continue
        score = global_ligand_score(translated)
        if best_score is None or float(score["score"]) < float(best_score["score"]):
            best_score = score
            best_path = candidate_path
    if best_path is None or best_score is None:
        return None, "best_of_n_no_candidate"
    final_path = output_dir / f"{candidate['candidate_id']}__best_of_n.sdf"
    final_path.write_bytes(best_path.read_bytes())
    return final_path, "best_of_n_global_score_only_selected_ligand_score_{score:.3f}".format(
        score=float(best_score["score"])
    )


def repair_with_rerank_only(candidate: dict[str, Any], output_dir: Path) -> tuple[Path | None, str]:
    source_path = candidate.get("failed_ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    if mol is None:
        return None, "rerank_only_failed_to_read_failed_candidate"
    repaired_path = write_translated_candidate(candidate, output_dir, "rerank_only", mol, "", (0.0, 0.0, 0.0))
    score = score_written_candidate(candidate, repaired_path)
    return repaired_path, "rerank_only_oracle_free_kept_failed_candidate_score_{score:.3f}".format(
        score=float(score["score"])
    )


def repair_budget_metadata(baseline: str, candidate: dict[str, Any], seed: int) -> dict[str, Any]:
    source_path = candidate.get("failed_ligand_path")
    mol = load_first_molecule(source_path) if source_path else None
    candidate_pool_count = len(candidate_pool_molecules(candidate, mol, seed)) if mol is not None else None
    editable_pool_count = len(editable_repair_offsets(seed))
    residual_pool_count = len(offset_neighborhood((0.0, 0.0, 0.0), seed))
    anchor_alignment_budget = 3
    if baseline in {"best_of_n", "feedback_geometry_refinement"}:
        internal_candidate_budget = candidate_pool_count
        budget_type = "candidate_pool_selection"
    elif baseline == "feedback_anchor_alignment_policy":
        internal_candidate_budget = anchor_alignment_budget
        budget_type = "anchor_alignment_selection"
    elif baseline in {
        "feedback_editable_contact_policy",
        "feedback_editable_geometry_only_policy",
        "feedback_editable_interaction_only_policy",
        "feedback_editable_global_only_policy",
        "feedback_editable_full_policy",
        "feedback_budgeted_learned_editable_contact_policy",
        "feedback_budgeted_learned_editable_contact_shuffled_policy",
        "no_failed_candidate_policy",
    }:
        internal_candidate_budget = editable_pool_count
        budget_type = "editable_offset_selection"
    elif baseline == "feedback_residual_ensemble_policy":
        internal_candidate_budget = residual_pool_count
        budget_type = "residual_offset_selection"
    elif baseline == "direct_regeneration":
        internal_candidate_budget = candidate_pool_count
        budget_type = "candidate_pool_index_selection"
    elif baseline in {"rerank_only", "identity_failed_candidate", "no_feedback_repair"}:
        internal_candidate_budget = 1
        budget_type = "single_failed_candidate"
    elif baseline in {"coordinate_rollback", "feedback_rule_repair"}:
        internal_candidate_budget = 1
        budget_type = "reference_or_rule_copy"
    else:
        internal_candidate_budget = 1
        budget_type = "single_policy_output"
    return {
        "record_level_output_budget": 1,
        "internal_candidate_budget": internal_candidate_budget,
        "internal_budget_type": budget_type,
        "candidate_pool_size": candidate_pool_count,
        "editable_offset_pool_size": editable_pool_count,
    }


def repair_candidate(
    candidate: dict[str, Any],
    baseline: str,
    output_dir: Path,
    feedback: dict[str, Any] | None,
    seed: int,
    candidates: list[dict[str, Any]],
    feedback_by_id: dict[Any, dict[str, Any]],
    shuffled_feedback_by_id: dict[Any, dict[str, Any]],
    learned_target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None],
    learned_coefficient_cache: dict[tuple[str | None, int, str], list[list[float]] | None],
    kernel_training_cache: dict[tuple[str | None, int, str], list[tuple[list[float], tuple[float, float, float]]]],
    label_training_cache: dict[tuple[str | None, int, str], list[tuple[list[float], int]]],
) -> dict[str, Any] | None:
    if baseline == "feedback_anchor_alignment_policy":
        repaired_path, decision = repair_with_anchor_alignment_policy(candidate, output_dir)
        if repaired_path is None:
            return None
    elif baseline == "feedback_geometry_refinement":
        repaired_path, decision = repair_with_geometry_refinement(candidate, output_dir, seed)
        if repaired_path is None:
            return None
    elif baseline == "feedback_learned_geometry_policy":
        repaired_path, decision = repair_with_learned_geometry_policy(
            candidate,
            output_dir,
            seed,
            candidates,
            feedback_by_id,
            learned_target_cache,
            learned_coefficient_cache,
        )
        if repaired_path is None:
            return None
    elif baseline == "feedback_kernel_geometry_policy":
        repaired_path, decision = repair_with_kernel_geometry_policy(
            candidate,
            output_dir,
            seed,
            candidates,
            feedback_by_id,
            learned_target_cache,
            kernel_training_cache,
        )
        if repaired_path is None:
            return None
    elif baseline == "feedback_knn_geometry_policy":
        repaired_path, decision = repair_with_knn_geometry_policy(
            candidate,
            output_dir,
            seed,
            candidates,
            feedback_by_id,
            learned_target_cache,
            kernel_training_cache,
        )
        if repaired_path is None:
            return None
    elif baseline == "feedback_residual_ensemble_policy":
        repaired_path, decision = repair_with_residual_ensemble_policy(
            candidate,
            output_dir,
            seed,
            candidates,
            feedback_by_id,
            learned_target_cache,
            kernel_training_cache,
            learned_coefficient_cache,
        )
        if repaired_path is None:
            return None
    elif baseline in {
        "feedback_editable_contact_policy",
        "feedback_editable_geometry_only_policy",
        "feedback_editable_interaction_only_policy",
        "feedback_editable_global_only_policy",
        "feedback_editable_full_policy",
    }:
        mode = {
            "feedback_editable_contact_policy": "full",
            "feedback_editable_geometry_only_policy": "geometry_only",
            "feedback_editable_interaction_only_policy": "interaction_only",
            "feedback_editable_global_only_policy": "global_only",
            "feedback_editable_full_policy": "full",
        }[baseline]
        repaired_path, decision = repair_with_editable_ablation_policy(candidate, output_dir, seed, baseline, mode)
        if repaired_path is None:
            return None
    elif baseline == "feedback_classified_editable_contact_policy":
        repaired_path, decision = repair_with_classified_editable_contact_policy(
            candidate,
            output_dir,
            seed,
            candidates,
            feedback_by_id,
            learned_target_cache,
            label_training_cache,
        )
        if repaired_path is None:
            return None
    elif baseline == "feedback_directional_classified_editable_contact_policy":
        repaired_path, decision = repair_with_classified_editable_contact_policy(
            candidate,
            output_dir,
            seed,
            candidates,
            feedback_by_id,
            learned_target_cache,
            label_training_cache,
            baseline=baseline,
            include_direction=True,
        )
        if repaired_path is None:
            return None
    elif baseline == "feedback_learned_editable_contact_policy":
        repaired_path, decision = repair_with_learned_editable_contact_policy(
            candidate,
            output_dir,
            seed,
            candidates,
            feedback_by_id,
            learned_target_cache,
            kernel_training_cache,
        )
        if repaired_path is None:
            return None
    elif baseline == "feedback_directional_learned_editable_contact_policy":
        repaired_path, decision = repair_with_learned_editable_contact_policy(
            candidate,
            output_dir,
            seed,
            candidates,
            feedback_by_id,
            learned_target_cache,
            kernel_training_cache,
            baseline=baseline,
            include_direction=True,
        )
        if repaired_path is None:
            return None
    elif baseline == "feedback_scaled_learned_editable_contact_policy":
        repaired_path, decision = repair_with_learned_editable_contact_policy(
            candidate,
            output_dir,
            seed,
            candidates,
            feedback_by_id,
            learned_target_cache,
            kernel_training_cache,
            baseline=baseline,
            scale_features=True,
        )
        if repaired_path is None:
            return None
    elif baseline == "feedback_budgeted_learned_editable_contact_policy":
        repaired_path, decision = repair_with_budgeted_learned_editable_contact_policy(
            candidate,
            output_dir,
            seed,
            candidates,
            feedback_by_id,
            learned_target_cache,
            kernel_training_cache,
        )
        if repaired_path is None:
            return None
    elif baseline == "feedback_ridge_editable_contact_policy":
        repaired_path, decision = repair_with_ridge_editable_contact_policy(
            candidate,
            output_dir,
            seed,
            candidates,
            feedback_by_id,
            learned_target_cache,
            learned_coefficient_cache,
        )
        if repaired_path is None:
            return None
    elif baseline == "feedback_learned_editable_contact_shuffled_policy":
        repaired_path, decision = repair_with_learned_editable_contact_policy(
            candidate,
            output_dir,
            seed,
            candidates,
            shuffled_feedback_by_id,
            learned_target_cache,
            kernel_training_cache,
            baseline=baseline,
        )
        if repaired_path is None:
            return None
    elif baseline == "feedback_budgeted_learned_editable_contact_shuffled_policy":
        repaired_path, decision = repair_with_budgeted_learned_editable_contact_policy(
            candidate,
            output_dir,
            seed,
            candidates,
            shuffled_feedback_by_id,
            learned_target_cache,
            kernel_training_cache,
            baseline=baseline,
        )
        if repaired_path is None:
            return None
    elif baseline == "feedback_ridge_editable_contact_shuffled_policy":
        repaired_path, decision = repair_with_ridge_editable_contact_policy(
            candidate,
            output_dir,
            seed,
            candidates,
            shuffled_feedback_by_id,
            learned_target_cache,
            learned_coefficient_cache,
            baseline=baseline,
            cache_namespace=baseline,
        )
        if repaired_path is None:
            return None
    elif baseline == "no_failed_candidate_policy":
        repaired_path, decision = repair_with_no_failed_candidate_policy(candidate, output_dir, seed)
        if repaired_path is None:
            return None
    elif baseline == "feedback_linear_refinement":
        repaired_path, decision = repair_with_linear_refinement(candidate, output_dir, candidates, feedback_by_id)
        if repaired_path is None:
            return None
    elif baseline == "direct_regeneration":
        repaired_path, decision = repair_with_direct_regeneration(candidate, output_dir, seed)
        if repaired_path is None:
            return None
    elif baseline == "best_of_n":
        repaired_path, decision = repair_with_best_of_n(candidate, output_dir, seed)
        if repaired_path is None:
            return None
    elif baseline == "rerank_only":
        repaired_path, decision = repair_with_rerank_only(candidate, output_dir)
        if repaired_path is None:
            return None
    else:
        if baseline == "coordinate_rollback":
            source_path, decision = candidate.get("ligand_path"), "coordinate_rollback_uses_reference_ligand_smoke_oracle"
        elif baseline in {"identity_failed_candidate", "no_feedback_repair"}:
            source_path, decision = candidate.get("failed_ligand_path"), f"{baseline}_uses_failed_candidate"
        elif baseline == "feedback_rule_repair":
            geometry = (feedback or {}).get("geometry", {})
            failure_type = candidate.get("failure_type")
            needs_rollback = (
                failure_type in {"clash", "anchor_invalid", "geometry_invalid"}
                or geometry.get("clash_count", 0) not in (None, 0)
                or float(geometry.get("anchor_distance_error") or 0.0) > 1.0
                or geometry.get("editable_region_validity") is False
            )
            if needs_rollback:
                source_path, decision = candidate.get("ligand_path"), "feedback_rule_selected_original_ligand_smoke_oracle"
            else:
                source_path, decision = candidate.get("failed_ligand_path"), "feedback_rule_kept_failed_candidate"
        else:
            source_path, decision = candidate.get("failed_ligand_path"), "unknown_baseline_default_failed_candidate"
        if not source_path:
            return None
        mol = load_first_molecule(source_path)
        if mol is None:
            return None
        repair_id = f"{candidate['candidate_id']}__{baseline}"
        repaired_path = write_sdf(output_dir / f"{repair_id}.sdf", mol)
    repair_id = f"{candidate['candidate_id']}__{baseline}"
    return {
        "repair_id": repair_id,
        "seed": seed,
        "candidate_id": candidate.get("candidate_id"),
        "complex_id": candidate.get("complex_id"),
        "baseline": baseline,
        "failure_type": candidate.get("failure_type"),
        "decision": decision,
        "source_failed_ligand_path": candidate.get("failed_ligand_path"),
        "repaired_ligand_path": str(repaired_path),
        "protein_path": candidate.get("protein_path"),
        "reference_ligand_path": candidate.get("ligand_path"),
        "sample_quality": candidate.get("sample_quality", {}),
        "dataset_status": candidate.get("dataset_status"),
        "scaffold_smiles": candidate.get("scaffold_smiles"),
        "scaffold_atoms": candidate.get("scaffold_atoms", []),
        "anchor_atoms": candidate.get("anchor_atoms", []),
        "editable_atoms": candidate.get("editable_atoms", []),
        **repair_budget_metadata(baseline, candidate, seed),
        "source": "smoke_repair_baseline",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_yaml(args.config)
    seed = int(config.get("seed", 0))
    candidates = read_jsonl(config["input"]["candidates_path"])
    feedback_rows = read_jsonl(config["input"].get("feedback_path", "")) if config["input"].get("feedback_path") else []
    feedback_by_id = {row.get("candidate_id"): row for row in feedback_rows}
    shuffled_feedback_by_id = shuffled_feedback_by_candidate(candidates, feedback_rows, seed)
    output_dir = Path(config["output"]["repaired_molecules_dir"])
    baselines = list(config.get("baselines", []))
    learned_target_cache: dict[tuple[Any, ...], tuple[float, float, float] | None] = {}
    learned_coefficient_cache: dict[tuple[str | None, int, str], list[list[float]] | None] = {}
    kernel_training_cache: dict[tuple[str | None, int, str], list[tuple[list[float], tuple[float, float, float]]]] = {}
    label_training_cache: dict[tuple[str | None, int, str], list[tuple[list[float], int]]] = {}
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        feedback = feedback_by_id.get(candidate.get("candidate_id"))
        for baseline in baselines:
            row = repair_candidate(
                candidate,
                baseline,
                output_dir,
                feedback,
                seed,
                candidates,
                feedback_by_id,
                shuffled_feedback_by_id,
                learned_target_cache,
                learned_coefficient_cache,
                kernel_training_cache,
                label_training_cache,
            )
            if row is not None:
                rows.append(row)
    write_jsonl(config["output"]["repaired_candidates_path"], rows)
    print(f"Read {len(candidates)} failed candidates")
    print(f"Read {len(feedback_rows)} feedback records")
    print(f"Wrote {len(rows)} repaired candidate records to {config['output']['repaired_candidates_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
