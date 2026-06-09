#!/usr/bin/env python3
"""Build frozen-style audit labels from evaluator tool results."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.eval.audit_common import (
    load_yaml,
    normalized_config_hash,
    read_jsonl,
    sha256_file,
    with_schema_ref,
    write_jsonl_with_schema,
)


LABEL_SCHEMA_PATH = "schemas/third_party_audit/diagnosis/label_v0_1.json"


def group_tool_results(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    for index, row in enumerate(rows, start=1):
        row["result_ref"] = f"evaluator/evaluator_tool_results.jsonl#L{index}"
        grouped.setdefault(row["sample_id"], {})[row["evaluator_name"]] = row
    return grouped


def status(tool: dict[str, dict[str, Any]], name: str) -> str | None:
    row = tool.get(name)
    return str(row.get("status")) if row else None


def metrics(tool: dict[str, dict[str, Any]], name: str) -> dict[str, Any]:
    row = tool.get(name) or {}
    payload = row.get("metrics")
    return payload if isinstance(payload, dict) else {}


def unique(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def failed_columns_for(metrics_row: dict[str, Any], metric_name: str) -> list[str]:
    value = metrics_row.get(f"{metric_name}_failed_columns")
    return list(value) if isinstance(value, list) else []


def unavailable_columns_for(metrics_row: dict[str, Any], metric_name: str) -> list[str]:
    value = metrics_row.get(f"{metric_name}_unavailable_columns")
    return list(value) if isinstance(value, list) else []


def classify(sample: dict[str, Any], tool: dict[str, dict[str, Any]]) -> dict[str, Any]:
    secondary: list[str] = []
    evidence: dict[str, Any] = {
        "tool_status": {name: row.get("status") for name, row in sorted(tool.items())},
        "claim_boundary": "selected_output_residual_audit_not_raw_failure_prevalence",
        "final_only_selected_output_view": bool((sample.get("quality_flags") or {}).get("final_only_selected_output_view")),
    }

    if evidence["final_only_selected_output_view"]:
        secondary.append("final_only_selected_output_view")

    quality_flags = sample.get("quality_flags") or {}
    original_status = sample.get("original_status") or {}
    if quality_flags.get("pipeline_failure") or original_status.get("failure_reason") == "command_exit_nonzero":
        return {
            "evaluability_status": "not_evaluable_pipeline_failure",
            "primary_label": "pipeline_failure",
            "secondary_labels": unique(secondary),
            "near_miss_eligible": False,
            "evidence": evidence,
        }

    if not sample.get("molecule_path"):
        return {
            "evaluability_status": "not_evaluable_missing_data",
            "primary_label": "missing_data",
            "secondary_labels": unique(secondary),
            "near_miss_eligible": False,
            "evidence": evidence,
        }

    rdkit_status = status(tool, "rdkit")
    if rdkit_status in {None, "input_missing"}:
        secondary.append("rdkit_parse_failed")
        return {
            "evaluability_status": "not_evaluable_missing_data",
            "primary_label": "missing_data",
            "secondary_labels": unique(secondary),
            "near_miss_eligible": False,
            "evidence": evidence,
        }
    if rdkit_status == "format_error":
        secondary.append("rdkit_parse_failed")
        return {
            "evaluability_status": "not_evaluable_format_error",
            "primary_label": "unknown",
            "secondary_labels": unique(secondary),
            "near_miss_eligible": False,
            "evidence": evidence,
        }
    if rdkit_status in {"tool_failure", "timeout", "unavailable"}:
        secondary.append("tool_timeout" if rdkit_status == "timeout" else "rdkit_parse_failed")
        return {
            "evaluability_status": "not_evaluable_tool_failure",
            "primary_label": "tool_failure",
            "secondary_labels": unique(secondary),
            "near_miss_eligible": False,
            "evidence": evidence,
        }
    if rdkit_status == "failed":
        secondary.append("rdkit_sanitize_failed")
        return {
            "evaluability_status": "evaluable",
            "primary_label": "chemical_invalid",
            "secondary_labels": unique(secondary),
            "near_miss_eligible": False,
            "evidence": evidence,
        }

    for name in ["posebusters_mol", "posebusters_dock"]:
        tool_status = status(tool, name)
        if tool_status in {"tool_failure", "timeout", "unavailable"}:
            if tool_status == "timeout":
                secondary.append("tool_timeout")
            return {
                "evaluability_status": "not_evaluable_tool_failure",
                "primary_label": "tool_failure",
                "secondary_labels": unique(secondary),
                "near_miss_eligible": False,
                "evidence": evidence,
            }
        if tool_status == "format_error":
            secondary.append("posebusters_mol_pred_load_failed")
            return {
                "evaluability_status": "not_evaluable_format_error",
                "primary_label": "unknown",
                "secondary_labels": unique(secondary),
                "near_miss_eligible": False,
                "evidence": evidence,
            }

    mol_metrics = metrics(tool, "posebusters_mol")
    mol_failed = failed_columns_for(mol_metrics, "posebusters_ligand_core_pass")
    mol_unavailable = unavailable_columns_for(mol_metrics, "posebusters_ligand_core_pass")
    if mol_unavailable:
        evidence["posebusters_ligand_core_unavailable_columns"] = mol_unavailable
        evidence["posebusters_ligand_core_unavailable_reasons"] = mol_metrics.get(
            "posebusters_ligand_core_pass_unavailable_reasons",
            {},
        )
        if "internal_energy" in mol_unavailable:
            secondary.append("posebusters_internal_energy_unavailable")
    if status(tool, "posebusters_mol") == "failed":
        evidence["posebusters_ligand_core_failed_columns"] = mol_failed
        if "all_atoms_connected" in mol_failed:
            secondary.append("disconnected_graph")
            return {
                "evaluability_status": "evaluable",
                "primary_label": "graph_or_scaffold_failure",
                "secondary_labels": unique(secondary),
                "near_miss_eligible": False,
                "evidence": evidence,
            }
        if {"sanitization", "inchi_convertible", "no_radicals"} & set(mol_failed):
            secondary.append("rdkit_sanitize_failed")
            return {
                "evaluability_status": "evaluable",
                "primary_label": "chemical_invalid",
                "secondary_labels": unique(secondary),
                "near_miss_eligible": False,
                "evidence": evidence,
            }
        secondary.append("posebusters_geometry_failed")
        if "internal_steric_clash" in mol_failed:
            secondary.append("internal_clash")
        if "internal_energy" in mol_failed:
            secondary.append("high_internal_energy_evidence")
        return {
            "evaluability_status": "evaluable",
            "primary_label": "local_geometry_failure",
            "secondary_labels": unique(secondary),
            "near_miss_eligible": True,
            "evidence": evidence,
        }
    if "internal_energy" in mol_unavailable:
        evidence["no_core_failure_detected_with_energy_unavailable"] = True
        secondary.append("no_core_failure_detected_with_energy_unavailable")

    dock_metrics = metrics(tool, "posebusters_dock")
    dock_failed = failed_columns_for(dock_metrics, "posebusters_pocket_core_pass")
    if status(tool, "posebusters_dock") == "failed":
        evidence["posebusters_pocket_core_failed_columns"] = dock_failed
        if "protein-ligand_maximum_distance" in dock_failed:
            secondary.append("ligand_outside_pocket")
            return {
                "evaluability_status": "evaluable",
                "primary_label": "pocket_detachment",
                "secondary_labels": unique(secondary),
                "near_miss_eligible": False,
                "evidence": evidence,
            }
        if {"minimum_distance_to_protein", "volume_overlap_with_protein"} & set(dock_failed):
            secondary.append("protein_ligand_clash")
            return {
                "evaluability_status": "evaluable",
                "primary_label": "protein_ligand_clash",
                "secondary_labels": unique(secondary),
                "near_miss_eligible": True,
                "evidence": evidence,
            }
        return {
            "evaluability_status": "evaluable",
            "primary_label": "global_pose_failure",
            "secondary_labels": unique(secondary),
            "near_miss_eligible": False,
            "evidence": evidence,
        }

    vina_status = status(tool, "vina")
    vina_metrics = metrics(tool, "vina")
    if vina_status == "format_error":
        secondary.append("vina_ligand_prepare_failed")
        return {
            "evaluability_status": "not_evaluable_format_error",
            "primary_label": "unknown",
            "secondary_labels": unique(secondary),
            "near_miss_eligible": False,
            "evidence": evidence,
        }
    if vina_status == "tool_failure" and any("receptor_prepare_failed" in str(error) for error in (tool.get("vina") or {}).get("errors", [])):
        secondary.extend(["vina_receptor_prepare_failed", "receptor_prep_sensitive"])
        return {
            "evaluability_status": "not_evaluable_tool_failure",
            "primary_label": "tool_failure",
            "secondary_labels": unique(secondary),
            "near_miss_eligible": False,
            "evidence": evidence,
        }
    if vina_metrics.get("vina_score_comparability") == "non_comparable":
        secondary.append("vina_score_non_comparable")
    if status(tool, "plip") == "passed":
        evidence["plip_interaction_count"] = metrics(tool, "plip").get("plip_interaction_count")
        evidence["plip_reference_recovery"] = metrics(tool, "plip").get("plip_interaction_recovery")
    if vina_status == "passed":
        evidence["vina_score_only_energy"] = vina_metrics.get("vina_score_only_energy")
        evidence["vina_score_role"] = "auxiliary_metric_only"

    evidence["no_frozen_failure_detected"] = True
    return {
        "evaluability_status": "evaluable",
        "primary_label": "unknown",
        "secondary_labels": unique(secondary),
        "near_miss_eligible": False,
        "evidence": evidence,
    }


def build_label_rows(samples: list[dict[str, Any]], tool_results: list[dict[str, Any]], label_config: dict[str, Any], label_hash: str) -> list[dict[str, Any]]:
    by_sample = group_tool_results(tool_results)
    script_hash = sha256_file(Path(__file__))
    rows: list[dict[str, Any]] = []
    for sample in samples:
        tool = by_sample.get(sample["sample_id"], {})
        classified = classify(sample, tool)
        rows.append(
            with_schema_ref(
                {
                    "sample_id": sample["sample_id"],
                    "run_id": sample["run_id"],
                    "method": sample["method"],
                    "complex_id": sample["complex_id"],
                    "stage": sample.get("stage", "final"),
                    "sample_role": sample.get("sample_role", "final_output"),
                    "evaluability_status": classified["evaluability_status"],
                    "primary_label": classified["primary_label"],
                    "secondary_labels": classified["secondary_labels"],
                    "near_miss_eligible": classified["near_miss_eligible"],
                    "evidence": {
                        **classified["evidence"],
                        "receptor_prep_id": sample.get("receptor_prep_id"),
                        "receptor_prep_policy_hash": sample.get("receptor_prep_policy_hash"),
                        "evaluator_policy_hash": sample.get("evaluator_policy_hash"),
                        "tool_versions_lock_hash": sample.get("tool_versions_lock_hash"),
                    },
                    "tool_results": {
                        name: {
                            "status": row.get("status"),
                            "result_ref": row.get("result_ref"),
                            "errors": row.get("errors"),
                        }
                        for name, row in sorted(tool.items())
                    },
                    "thresholds": {
                        "label_mapping_source": label_config.get("schema_path"),
                        "posebusters_ligand_core": "columns_from_evaluator_policy",
                        "posebusters_pocket_core": "columns_from_evaluator_policy",
                        "vina_role": "auxiliary_score_only",
                        "plip_reference_recovery_role": "descriptive_evidence",
                    },
                    "label_protocol_version": label_config["label_protocol_version"],
                    "label_script_commit": script_hash,
                    "label_config_hash": label_hash,
                    "adjudication_status": "not_reviewed",
                    "manual_adjudication_id": None,
                    "quality_notes": "Generated by frozen-style automatic label builder; no manual adjudication.",
                    "receptor_prep_id": sample.get("receptor_prep_id"),
                    "receptor_prep_policy_hash": sample.get("receptor_prep_policy_hash"),
                    "evaluator_policy_hash": sample.get("evaluator_policy_hash"),
                    "denominator_policy_hash": sample.get("denominator_policy_hash"),
                    "tool_versions_lock_hash": sample.get("tool_versions_lock_hash"),
                },
                LABEL_SCHEMA_PATH,
            )
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--label-config", default="configs/audit/diagnosis_label_config_v0_2.yaml")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    run_root = Path(args.run_root).resolve()
    label_config_path = Path(args.label_config).resolve()
    label_config = load_yaml(label_config_path)
    samples = read_jsonl(run_root / "samples.jsonl")
    tool_results = read_jsonl(run_root / "evaluator" / "evaluator_tool_results.jsonl")
    labels = build_label_rows(samples, tool_results, label_config, normalized_config_hash(label_config_path))
    output_path = Path(args.output).resolve() if args.output else run_root / "labels.jsonl"
    write_jsonl_with_schema(output_path, labels, LABEL_SCHEMA_PATH)
    print({"run_root": str(run_root), "label_rows": len(labels), "output": str(output_path)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
