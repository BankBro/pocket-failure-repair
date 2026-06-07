"""Repaired-molecule evaluation helpers."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from pfr.chemistry.rdkit_scaffold import load_first_molecule, summarize_ligand
from pfr.feedback.geometry import anchor_distance_error, contact_fingerprint_similarity, protein_ligand_geometry


def ligand_efficiency_proxy(vina_like_proxy: float | None, heavy_atoms: int | None) -> float | None:
    if vina_like_proxy is None or not heavy_atoms:
        return None
    return vina_like_proxy / float(heavy_atoms)


def sa_fallback_proxy(descriptors: dict[str, Any]) -> float | None:
    rotatable = descriptors.get("rotatable_bonds")
    heavy_atoms = descriptors.get("num_heavy_atoms")
    if rotatable is None or heavy_atoms is None:
        return None
    return 1.0 + min(9.0, float(rotatable) * 0.25 + float(heavy_atoms) * 0.03)


def vina_like_proxy_score(geometry: dict[str, Any], descriptors: dict[str, Any]) -> float | None:
    min_distance = geometry.get("min_protein_ligand_distance")
    clash_count = geometry.get("clash_count")
    if min_distance is None or clash_count is None:
        return None
    logp = float(descriptors.get("logp") or 0.0)
    rotatable = float(descriptors.get("rotatable_bonds") or 0.0)
    distance_penalty = abs(float(min_distance) - 3.0)
    return -0.2 * logp + 0.05 * rotatable + 2.0 * float(clash_count) + distance_penalty


def posebusters_like_pass(geometry: dict[str, Any], ligand_summary: dict[str, Any]) -> bool:
    return (
        ligand_summary.get("status") == "rdkit_ok"
        and ligand_summary.get("has_conformer") is True
        and geometry.get("clash_count") in (None, 0)
    )


def evaluate_repaired_record(row: dict[str, Any]) -> dict[str, Any]:
    repaired_path = row.get("repaired_ligand_path")
    failed_path = row.get("source_failed_ligand_path")
    protein_path = row.get("protein_path")
    reference_path = row.get("reference_ligand_path")
    ligand_summary = summarize_ligand(repaired_path) if repaired_path else {"status": "rdkit_read_failed"}
    geometry = protein_ligand_geometry(protein_path, repaired_path)
    failed_geometry = protein_ligand_geometry(protein_path, failed_path)
    anchor_error = anchor_distance_error(reference_path, repaired_path, row.get("anchor_atoms", []))
    failed_anchor_error = anchor_distance_error(reference_path, failed_path, row.get("anchor_atoms", []))
    contact = contact_fingerprint_similarity(protein_path, reference_path, repaired_path)
    failed_contact = contact_fingerprint_similarity(protein_path, reference_path, failed_path)
    scaffold_preserved = None
    if row.get("scaffold_smiles") is not None and ligand_summary.get("scaffold_smiles") is not None:
        scaffold_preserved = row.get("scaffold_smiles") == ligand_summary.get("scaffold_smiles")
    editable_valid = bool(ligand_summary.get("editable_atoms"))
    clash_count = geometry.get("clash_count")
    clash_free = clash_count in (None, 0)
    anchor_valid = anchor_error is None or anchor_error <= 1.0
    success = (
        ligand_summary.get("status") == "rdkit_ok"
        and scaffold_preserved is not False
        and editable_valid
        and clash_free
        and anchor_valid
        and row.get("sample_quality", {}).get("evaluable_for_repair") is not False
    )
    descriptors = ligand_summary.get("descriptors", {}) or {}
    vina_proxy = vina_like_proxy_score(geometry, descriptors)
    reference_geometry = protein_ligand_geometry(protein_path, reference_path)
    reference_summary = summarize_ligand(reference_path) if reference_path else {"descriptors": {}}
    reference_descriptors = reference_summary.get("descriptors", {}) or {}
    failed_summary = summarize_ligand(failed_path) if failed_path else {"descriptors": {}}
    failed_descriptors = failed_summary.get("descriptors", {}) or {}
    reference_vina_proxy = vina_like_proxy_score(reference_geometry, reference_descriptors)
    failed_vina_proxy = vina_like_proxy_score(failed_geometry, failed_descriptors)
    delta_vina_proxy = None if vina_proxy is None or reference_vina_proxy is None else vina_proxy - reference_vina_proxy
    vina_like_gain = None if vina_proxy is None or failed_vina_proxy is None else failed_vina_proxy - vina_proxy
    contact_similarity = contact.get("contact_similarity")
    failed_contact_similarity = failed_contact.get("contact_similarity")
    contact_recovery = contact.get("contact_recovery")
    failed_contact_recovery = failed_contact.get("contact_recovery")
    contact_similarity_gain = (
        None if contact_similarity is None or failed_contact_similarity is None else contact_similarity - failed_contact_similarity
    )
    contact_recovery_gain = None if contact_recovery is None or failed_contact_recovery is None else contact_recovery - failed_contact_recovery
    anchor_error_reduction = None if anchor_error is None or failed_anchor_error is None else failed_anchor_error - anchor_error
    clash_count_reduction = None
    if clash_count is not None and failed_geometry.get("clash_count") is not None:
        clash_count_reduction = int(failed_geometry.get("clash_count") or 0) - int(clash_count or 0)
    repair_gain_success = bool(
        success
        and (
            (contact_recovery_gain is not None and contact_recovery_gain > 0.05)
            or (contact_similarity_gain is not None and contact_similarity_gain > 0.05)
            or (anchor_error_reduction is not None and anchor_error_reduction > 1.0)
            or (clash_count_reduction is not None and clash_count_reduction > 0)
            or (vina_like_gain is not None and vina_like_gain > 0.5)
        )
    )
    return {
        "repair_id": row.get("repair_id"),
        "seed": row.get("seed"),
        "candidate_id": row.get("candidate_id"),
        "complex_id": row.get("complex_id"),
        "baseline": row.get("baseline"),
        "failure_type": row.get("failure_type"),
        "repaired_ligand_path": repaired_path,
        "source_failed_ligand_path": failed_path,
        "protein_path": protein_path,
        "reference_ligand_path": reference_path,
        "status": ligand_summary.get("status"),
        "sample_evaluable_for_repair": row.get("sample_quality", {}).get("evaluable_for_repair") is not False,
        "repaired_success": success,
        "repair_gain_success": repair_gain_success,
        "scaffold_preserved": scaffold_preserved,
        "editable_validity": editable_valid,
        "anchor_validity": anchor_valid,
        "anchor_distance_error": anchor_error,
        "failed_anchor_distance_error": failed_anchor_error,
        "anchor_error_reduction": anchor_error_reduction,
        "clash_count": clash_count,
        "failed_clash_count": failed_geometry.get("clash_count"),
        "clash_count_reduction": clash_count_reduction,
        "clash_free": clash_free,
        "min_protein_ligand_distance": geometry.get("min_protein_ligand_distance"),
        "failed_min_protein_ligand_distance": failed_geometry.get("min_protein_ligand_distance"),
        "posebusters_like_pass": posebusters_like_pass(geometry, ligand_summary),
        "contact_fingerprint_similarity": contact_similarity,
        "failed_contact_fingerprint_similarity": failed_contact_similarity,
        "contact_fingerprint_similarity_gain": contact_similarity_gain,
        "contact_recovery": contact_recovery,
        "failed_contact_recovery": failed_contact_recovery,
        "contact_recovery_gain": contact_recovery_gain,
        "reference_contact_count": contact.get("reference_contacts"),
        "candidate_contact_count": contact.get("candidate_contacts"),
        "failed_candidate_contact_count": failed_contact.get("candidate_contacts"),
        "vina_like_proxy": vina_proxy,
        "failed_vina_like_proxy": failed_vina_proxy,
        "delta_vina_like_proxy": delta_vina_proxy,
        "vina_like_gain": vina_like_gain,
        "ligand_efficiency_proxy": ligand_efficiency_proxy(vina_proxy, descriptors.get("num_heavy_atoms")),
        "sa_fallback": sa_fallback_proxy(descriptors),
        "qed": descriptors.get("qed"),
        "logp": descriptors.get("logp"),
        "rotatable_bonds": descriptors.get("rotatable_bonds"),
        "molecular_weight": descriptors.get("molecular_weight"),
        "record_level_output_budget": row.get("record_level_output_budget"),
        "internal_candidate_budget": row.get("internal_candidate_budget"),
        "internal_budget_type": row.get("internal_budget_type"),
        "candidate_pool_size": row.get("candidate_pool_size"),
        "editable_offset_pool_size": row.get("editable_offset_pool_size"),
        "source": "repaired_molecule_rdkit_geometry_eval_with_fallback_external_proxies",
    }



def fraction(values: list[bool | None]) -> float | None:
    present = [value for value in values if value is not None]
    if not present:
        return None
    return sum(present) / len(present)


def mean(values: list[float | int | None]) -> float | None:
    numeric = [float(value) for value in values if value is not None]
    if not numeric:
        return None
    return sum(numeric) / len(numeric)


def summarize_repaired_metrics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("baseline", "unknown"))].append(row)
    summaries: list[dict[str, Any]] = []
    for baseline, baseline_rows in sorted(grouped.items()):
        summaries.append(
            {
                "baseline": baseline,
                "num_repaired": len(baseline_rows),
                "num_sample_evaluable": sum(row["sample_evaluable_for_repair"] for row in baseline_rows),
                "repaired_success_rate": fraction([row["repaired_success"] for row in baseline_rows]),
                "repair_gain_success_rate": fraction([row.get("repair_gain_success") for row in baseline_rows]),
                "scaffold_preservation": fraction(
                    [row["scaffold_preserved"] for row in baseline_rows if row["scaffold_preserved"] is not None]
                ),
                "editable_validity": fraction([row["editable_validity"] for row in baseline_rows]),
                "anchor_validity": fraction([row["anchor_validity"] for row in baseline_rows]),
                "clash_free_rate": fraction([row["clash_free"] for row in baseline_rows]),
                "mean_clash_count": mean([row["clash_count"] for row in baseline_rows]),
                "mean_qed": mean([row["qed"] for row in baseline_rows]),
                "mean_logp": mean([row["logp"] for row in baseline_rows]),
                "mean_posebusters_like_pass": fraction([row.get("posebusters_like_pass") for row in baseline_rows]),
                "mean_contact_fingerprint_similarity": mean([row.get("contact_fingerprint_similarity") for row in baseline_rows]),
                "mean_contact_fingerprint_similarity_gain": mean(
                    [row.get("contact_fingerprint_similarity_gain") for row in baseline_rows]
                ),
                "mean_contact_recovery": mean([row.get("contact_recovery") for row in baseline_rows]),
                "mean_contact_recovery_gain": mean([row.get("contact_recovery_gain") for row in baseline_rows]),
                "mean_vina_like_proxy": mean([row.get("vina_like_proxy") for row in baseline_rows]),
                "mean_vina_like_gain": mean([row.get("vina_like_gain") for row in baseline_rows]),
                "mean_anchor_error_reduction": mean([row.get("anchor_error_reduction") for row in baseline_rows]),
                "mean_clash_count_reduction": mean([row.get("clash_count_reduction") for row in baseline_rows]),
                "mean_internal_candidate_budget": mean([row.get("internal_candidate_budget") for row in baseline_rows]),
                "internal_budget_types": sorted(
                    {str(row.get("internal_budget_type")) for row in baseline_rows if row.get("internal_budget_type") is not None}
                ),
                "mean_ligand_efficiency_proxy": mean([row.get("ligand_efficiency_proxy") for row in baseline_rows]),
                "mean_sa_fallback": mean([row.get("sa_fallback") for row in baseline_rows]),
                "source": "repaired_molecule_rdkit_geometry_eval_with_fallback_external_proxies",
            }
        )
    return summaries
