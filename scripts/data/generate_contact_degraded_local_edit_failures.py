#!/usr/bin/env python3
"""Build anchor-preserved contact-degraded local-edit failed candidates."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

from rdkit import Chem

from pfr.chemistry.perturb import valid_editable_atoms, write_sdf
from pfr.chemistry.rdkit_scaffold import load_first_molecule
from pfr.feedback.geometry import anchor_distance_error, contact_fingerprint_similarity, protein_ligand_geometry
from pfr.utils.io import load_yaml, read_jsonl, write_jsonl


def heavy_atom_centroid(mol: Chem.Mol, atoms: list[int] | None = None) -> tuple[float, float, float] | None:
    if mol.GetNumConformers() == 0:
        return None
    selected = atoms or [atom.GetIdx() for atom in mol.GetAtoms() if atom.GetAtomicNum() > 1]
    selected = [idx for idx in selected if 0 <= idx < mol.GetNumAtoms() and mol.GetAtomWithIdx(idx).GetAtomicNum() > 1]
    if not selected:
        return None
    conf = mol.GetConformer()
    count = float(len(selected))
    return (
        sum(float(conf.GetAtomPosition(idx).x) for idx in selected) / count,
        sum(float(conf.GetAtomPosition(idx).y) for idx in selected) / count,
        sum(float(conf.GetAtomPosition(idx).z) for idx in selected) / count,
    )


def unit_vector(vector: tuple[float, float, float]) -> tuple[float, float, float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm < 1e-9:
        return (1.0, 0.0, 0.0)
    return (vector[0] / norm, vector[1] / norm, vector[2] / norm)


def perturb_editable_region(
    mol: Chem.Mol,
    editable_atoms: list[int],
    offset: tuple[float, float, float],
    zigzag_scale: float,
) -> Chem.Mol:
    edited = Chem.Mol(mol)
    if edited.GetNumConformers() == 0:
        return edited
    editable = valid_editable_atoms(edited, editable_atoms)
    conf = edited.GetConformer()
    for order, atom_idx in enumerate(editable):
        pos = conf.GetAtomPosition(atom_idx)
        sign = -1.0 if order % 2 else 1.0
        conf.SetAtomPosition(
            atom_idx,
            (
                pos.x + offset[0] + sign * zigzag_scale,
                pos.y + offset[1] + ((order % 3) - 1) * zigzag_scale * 0.5,
                pos.z + offset[2] - sign * zigzag_scale * 0.25,
            ),
        )
    return edited


def candidate_offsets(reference: Chem.Mol, editable_atoms: list[int], seed: int) -> list[tuple[str, tuple[float, float, float], float]]:
    ligand_centroid = heavy_atom_centroid(reference)
    editable_centroid = heavy_atom_centroid(reference, editable_atoms)
    if ligand_centroid is None or editable_centroid is None:
        direction = (1.0, 0.0, 0.0)
    else:
        direction = unit_vector(
            (
                editable_centroid[0] - ligand_centroid[0],
                editable_centroid[1] - ligand_centroid[1],
                editable_centroid[2] - ligand_centroid[2],
            )
        )
    perpendicular = unit_vector((-direction[1], direction[0], direction[2] * 0.25))
    candidates: list[tuple[str, tuple[float, float, float], float]] = []
    for scale in (0.8, 1.2, 1.6, 2.0, 2.4):
        candidates.append((f"radial_out_{scale:.1f}", tuple(scale * value for value in direction), 0.05 * (seed % 3)))
        candidates.append((f"radial_in_{scale:.1f}", tuple(-scale * value for value in direction), 0.05 * ((seed + 1) % 3)))
    for scale in (0.6, 1.0, 1.4):
        candidates.append((f"tangent_{scale:.1f}", tuple(scale * value for value in perpendicular), 0.1))
        candidates.append((f"tangent_neg_{scale:.1f}", tuple(-scale * value for value in perpendicular), 0.1))
    return candidates


def degradation_score(example: dict[str, Any], failed_path: Path) -> dict[str, Any]:
    contact = contact_fingerprint_similarity(example.get("protein_path"), example.get("ligand_path"), failed_path)
    reference_contact = contact_fingerprint_similarity(example.get("protein_path"), example.get("ligand_path"), example.get("ligand_path"))
    geometry = protein_ligand_geometry(example.get("protein_path"), failed_path)
    anchor_error = anchor_distance_error(example.get("ligand_path"), failed_path, example.get("anchor_atoms", []))
    recovery = contact.get("contact_recovery")
    reference_recovery = reference_contact.get("contact_recovery")
    recovery_loss = None if recovery is None or reference_recovery is None else reference_recovery - recovery
    return {
        "contact_recovery": recovery,
        "contact_similarity": contact.get("contact_similarity"),
        "reference_contact_recovery": reference_recovery,
        "contact_recovery_loss": recovery_loss,
        "clash_count": geometry.get("clash_count"),
        "min_protein_ligand_distance": geometry.get("min_protein_ligand_distance"),
        "anchor_distance_error": anchor_error,
    }


def make_candidates(
    example: dict[str, Any],
    index: int,
    failed_molecules_dir: Path,
    seed: int,
    max_per_example: int,
    min_recovery_loss: float,
) -> list[dict[str, Any]]:
    ligand_path = example.get("ligand_path")
    if not ligand_path:
        return []
    reference = load_first_molecule(ligand_path)
    if reference is None or reference.GetNumConformers() == 0:
        return []
    editable = valid_editable_atoms(reference, example.get("editable_atoms", []))
    if not editable:
        return []
    complex_id = example.get("complex_id", "example")
    temporary_dir = failed_molecules_dir / "candidates"
    passing: list[tuple[float, str, Path, dict[str, Any]]] = []
    for label, offset, zigzag_scale in candidate_offsets(reference, editable, seed + index):
        mol = perturb_editable_region(reference, editable, offset, zigzag_scale)
        temporary_path = write_sdf(temporary_dir / f"{complex_id}_contact_degraded_{index}_{label}.sdf", mol)
        score = degradation_score(example, temporary_path)
        clash_count = score.get("clash_count")
        anchor_error = score.get("anchor_distance_error")
        recovery_loss = score.get("contact_recovery_loss")
        if clash_count not in (None, 0):
            continue
        if anchor_error is not None and anchor_error > 1.0:
            continue
        if recovery_loss is None or recovery_loss <= min_recovery_loss:
            continue
        passing.append((float(recovery_loss), label, temporary_path, score))
    passing.sort(key=lambda item: item[0], reverse=True)
    rows: list[dict[str, Any]] = []
    for rank, (_, label, temporary_path, score) in enumerate(passing[:max_per_example]):
        candidate_id = f"{complex_id}_contact_degraded_local_edit_{index}_{rank}"
        failed_path = failed_molecules_dir / f"{candidate_id}.sdf"
        temporary_path.replace(failed_path)
        rows.append(
            {
                "candidate_id": candidate_id,
                "complex_id": example.get("complex_id"),
                "failure_type": "contact_degraded_local_edit",
                "failure_reason": f"anchor_preserved_editable_region_contact_degradation_selected_{label}",
                "source": "contact_degraded_anchor_preserved_local_edit",
                "protein_path": example.get("protein_path"),
                "ligand_path": example.get("ligand_path"),
                "failed_ligand_path": str(failed_path),
                "ligand_smiles": example.get("ligand_smiles"),
                "scaffold_smiles": example.get("scaffold_smiles"),
                "scaffold_atoms": example.get("scaffold_atoms", []),
                "editable_atoms": example.get("editable_atoms", []),
                "anchor_atoms": example.get("anchor_atoms", []),
                "descriptors": example.get("descriptors", {}),
                "dataset_status": example.get("status"),
                "sample_quality": example.get("sample_quality", {}),
                "contact_degradation": score,
                "seed": seed,
                "contact_degradation_rank": rank,
            }
        )
    return rows


def make_candidate(example: dict[str, Any], index: int, failed_molecules_dir: Path, seed: int) -> dict[str, Any] | None:
    rows = make_candidates(example, index, failed_molecules_dir, seed, max_per_example=1, min_recovery_loss=0.05)
    return rows[0] if rows else None
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_yaml(args.config)
    seed = int(config.get("seed", 0))
    examples = read_jsonl(config["input"]["dataset_path"])
    output_path = config["output"]["candidates_path"]
    failed_molecules_dir = Path(config["output"]["failed_molecules_dir"])
    limits = config.get("limits", {}) or {}
    max_per_example = int(limits.get("max_per_example", 1))
    min_recovery_loss = float(limits.get("min_contact_recovery_loss", 0.05))
    rows = [
        candidate
        for index, example in enumerate(examples)
        for candidate in make_candidates(example, index, failed_molecules_dir, seed, max_per_example, min_recovery_loss)
    ]
    write_jsonl(output_path, rows)
    print(f"Read {len(examples)} dataset examples from {config['input']['dataset_path']}")
    print(f"Wrote {len(rows)} contact-degraded local-edit failed candidates to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
