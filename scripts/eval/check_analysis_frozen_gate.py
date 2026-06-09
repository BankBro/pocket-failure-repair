#!/usr/bin/env python3
"""Check whether a run satisfies the v0.1 analysis-frozen gate."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.eval.audit_common import (
    finalize_output_manifest,
    load_yaml,
    normalized_config_hash,
    now_utc,
    read_json,
    read_jsonl,
    sha256_file,
    with_schema_ref,
    write_json_with_schema,
)
from scripts.eval.build_audit_labels import classify


GATE_RESULT_SCHEMA_PATH = "schemas/third_party_audit/diagnosis/analysis_frozen_gate_result_v0_1.json"


def config_paths(args: argparse.Namespace) -> dict[str, Path]:
    return {
        "receptor_prep_policy": Path(args.receptor_prep_policy).resolve(),
        "evaluator_policy": Path(args.evaluator_policy).resolve(),
        "label_config": Path(args.label_config).resolve(),
        "denominator_config": Path(args.denominator_config).resolve(),
        "analysis_frozen_gate": Path(args.gate_config).resolve(),
        "tool_versions_lock": Path(args.tool_versions_lock).resolve(),
    }


def config_hashes(paths: dict[str, Path]) -> dict[str, str]:
    return {key: normalized_config_hash(path) for key, path in paths.items()}


def synthetic_tool_row(name: str, status: str, metrics: dict[str, Any] | None = None, errors: list[str] | None = None) -> dict[str, Any]:
    return {
        "evaluator_name": name,
        "status": status,
        "metrics": metrics or {},
        "errors": errors or [],
    }


def sanity_sample(**overrides: Any) -> dict[str, Any]:
    sample = {
        "sample_id": "sanity",
        "run_id": "sanity_run",
        "method": "DiffSBDD",
        "complex_id": "3rfm",
        "stage": "final",
        "sample_role": "final_output",
        "molecule_path": "/tmp/sample.sdf",
        "quality_flags": {"final_only_selected_output_view": True},
        "original_status": {"status": "final"},
    }
    sample.update(overrides)
    return sample


def passing_tools() -> dict[str, dict[str, Any]]:
    return {
        "rdkit": synthetic_tool_row("rdkit", "passed"),
        "posebusters_mol": synthetic_tool_row(
            "posebusters_mol",
            "passed",
            {"posebusters_ligand_core_pass_failed_columns": []},
        ),
        "posebusters_dock": synthetic_tool_row(
            "posebusters_dock",
            "passed",
            {"posebusters_pocket_core_pass_failed_columns": []},
        ),
        "plip": synthetic_tool_row("plip", "passed", {"plip_interaction_count": 1}),
        "vina": synthetic_tool_row("vina", "passed", {"vina_score_only_energy": -1.0}),
    }


def run_sanity_set() -> list[dict[str, Any]]:
    cases: list[tuple[str, dict[str, Any], dict[str, dict[str, Any]], str, str]] = []
    cases.append(("valid final output", sanity_sample(), passing_tools(), "evaluable", "unknown"))
    cases.append(("missing ligand", sanity_sample(molecule_path=None), passing_tools(), "not_evaluable_missing_data", "missing_data"))
    cases.append(("broken SDF", sanity_sample(), {**passing_tools(), "rdkit": synthetic_tool_row("rdkit", "format_error")}, "not_evaluable_format_error", "unknown"))
    cases.append(("pipeline failure", sanity_sample(quality_flags={"pipeline_failure": True}), passing_tools(), "not_evaluable_pipeline_failure", "pipeline_failure"))
    cases.append(("tool timeout", sanity_sample(), {**passing_tools(), "posebusters_dock": synthetic_tool_row("posebusters_dock", "timeout")}, "not_evaluable_tool_failure", "tool_failure"))
    cases.append(("Meeko ligand prepare failure", sanity_sample(), {**passing_tools(), "vina": synthetic_tool_row("vina", "format_error", errors=["ligand_prepare_failed"])}, "not_evaluable_format_error", "unknown"))
    cases.append(("Meeko receptor prepare failure", sanity_sample(), {**passing_tools(), "vina": synthetic_tool_row("vina", "tool_failure", errors=["receptor_prepare_failed"])}, "not_evaluable_tool_failure", "tool_failure"))
    cases.append(
        (
            "Vina pass trap",
            sanity_sample(),
            {
                **passing_tools(),
                "posebusters_dock": synthetic_tool_row(
                    "posebusters_dock",
                    "failed",
                    {"posebusters_pocket_core_pass_failed_columns": ["minimum_distance_to_protein"]},
                ),
            },
            "evaluable",
            "protein_ligand_clash",
        )
    )
    cases.append(("original failed/rejected sample", sanity_sample(sample_role="original_failed_sample"), passing_tools(), "evaluable", "unknown"))
    cases.append(("final-only outputs", sanity_sample(), passing_tools(), "evaluable", "unknown"))

    results: list[dict[str, Any]] = []
    for case_name, sample, tools, expected_eval, expected_label in cases:
        classified = classify(sample, tools)
        passed = classified["evaluability_status"] == expected_eval and classified["primary_label"] == expected_label
        results.append(
            {
                "case": case_name,
                "passed": passed,
                "expected_evaluability_status": expected_eval,
                "observed_evaluability_status": classified["evaluability_status"],
                "expected_primary_label": expected_label,
                "observed_primary_label": classified["primary_label"],
            }
        )
    return results


def load_required(run_root: Path) -> dict[str, Any]:
    return {
        "run_metadata": read_json(run_root / "run_metadata.json"),
        "samples": read_jsonl(run_root / "samples.jsonl"),
        "evaluator_inputs": read_jsonl(run_root / "evaluator" / "evaluator_input.jsonl"),
        "tool_results": read_jsonl(run_root / "evaluator" / "evaluator_tool_results.jsonl"),
        "labels": read_jsonl(run_root / "labels.jsonl"),
        "stage_attrition": read_json(run_root / "stage_attrition.json"),
        "output_manifest": read_json(run_root / "output_manifest.json"),
    }


def internal_energy_coverage(tool_results: list[dict[str, Any]]) -> dict[str, Any]:
    mol_rows = [row for row in tool_results if row.get("evaluator_name") == "posebusters_mol"]
    false_sample_ids: list[str] = []
    unavailable_sample_ids: list[str] = []
    unavailable_reasons: dict[str, str] = {}
    for row in mol_rows:
        metrics = row.get("metrics") or {}
        failed = metrics.get("posebusters_ligand_core_pass_failed_columns") or []
        unavailable = metrics.get("posebusters_ligand_core_pass_unavailable_columns") or []
        sample_id = str(row.get("sample_id"))
        if "internal_energy" in failed:
            false_sample_ids.append(sample_id)
        if "internal_energy" in unavailable:
            unavailable_sample_ids.append(sample_id)
            reasons = metrics.get("posebusters_ligand_core_pass_unavailable_reasons") or {}
            unavailable_reasons[sample_id] = str(reasons.get("internal_energy") or "unknown")
    denominator = len(mol_rows)
    return {
        "denominator_posebusters_mol_rows": denominator,
        "internal_energy_false_count": len(false_sample_ids),
        "internal_energy_false_sample_ids": sorted(false_sample_ids),
        "internal_energy_unavailable_count": len(unavailable_sample_ids),
        "internal_energy_unavailable_fraction": (len(unavailable_sample_ids) / denominator) if denominator else None,
        "internal_energy_unavailable_sample_ids": sorted(unavailable_sample_ids),
        "internal_energy_unavailable_reasons": dict(sorted(unavailable_reasons.items())),
    }


def internal_energy_unavailable_threshold(gate_config: dict[str, Any]) -> float | None:
    thresholds = gate_config.get("coverage_thresholds") or {}
    value = thresholds.get("internal_energy_unavailable_fraction")
    if not isinstance(value, dict):
        return None
    active_phase = thresholds.get("active_phase", "mvp_sanity")
    threshold = value.get(active_phase)
    return float(threshold) if threshold is not None else None


def update_output_manifest(run_root: Path) -> None:
    finalize_output_manifest(run_root)


def check_gate(run_root: Path, args: argparse.Namespace) -> dict[str, Any]:
    paths = config_paths(args)
    hashes = config_hashes(paths)
    payloads = {key: load_yaml(path) for key, path in paths.items()}
    data = load_required(run_root)
    run_metadata = data["run_metadata"]
    samples = data["samples"]
    evaluator_inputs = data["evaluator_inputs"]
    tool_results = data["tool_results"]
    labels = data["labels"]
    stage_row = (data["stage_attrition"].get("rows") or [{}])[0]
    coverage = internal_energy_coverage(tool_results)

    blocking: list[str] = []
    warnings: list[str] = []

    expected_metadata_hash_fields = {
        "receptor_prep_policy_hash": hashes["receptor_prep_policy"],
        "evaluator_policy_hash": hashes["evaluator_policy"],
        "label_config_hash": hashes["label_config"],
        "denominator_policy_hash": hashes["denominator_config"],
        "analysis_frozen_gate_hash": hashes["analysis_frozen_gate"],
        "tool_versions_lock_hash": hashes["tool_versions_lock"],
    }
    for field, expected in expected_metadata_hash_fields.items():
        if run_metadata.get(field) != expected:
            blocking.append(f"run_metadata.{field}_mismatch")

    receptor_records = sorted({sample.get("receptor_prep_record_path") for sample in samples if sample.get("receptor_prep_record_path")})
    if not receptor_records:
        blocking.append("receptor_prep_record_missing")
    for record_path in receptor_records:
        record = read_json(record_path)
        if record.get("unresolved_review_required_count") != 0:
            blocking.append(f"receptor_prep_unresolved_hetero_atoms:{record_path}")
        if record.get("cleaned_receptor_sha256") != sha256_file(record.get("cleaned_receptor_path", "")):
            blocking.append(f"cleaned_receptor_sha256_mismatch:{record_path}")

    cleaned_paths = {sample.get("cleaned_receptor_path") for sample in samples}
    for row in evaluator_inputs:
        if row.get("protein_path") != row.get("cleaned_receptor_path"):
            blocking.append(f"evaluator_input_not_using_cleaned_receptor:{row.get('sample_id')}")
        if row.get("cleaned_receptor_path") not in cleaned_paths:
            blocking.append(f"evaluator_input_cleaned_receptor_unknown:{row.get('sample_id')}")

    for row in tool_results:
        if row.get("evaluator_name") == "posebusters_mol":
            missing = row.get("metrics", {}).get("posebusters_ligand_core_pass_missing_columns")
            if missing:
                blocking.append(f"posebusters_mol_missing_frozen_columns:{row.get('sample_id')}")
            unavailable = row.get("metrics", {}).get("posebusters_ligand_core_pass_unavailable_columns") or []
            if "internal_energy" in unavailable:
                warnings.append(f"posebusters_internal_energy_unavailable:{row.get('sample_id')}")
        if row.get("evaluator_name") == "posebusters_dock":
            missing = row.get("metrics", {}).get("posebusters_pocket_core_pass_missing_columns")
            if missing:
                blocking.append(f"posebusters_dock_missing_frozen_columns:{row.get('sample_id')}")
        if row.get("evaluator_name") == "vina":
            metrics = row.get("metrics", {})
            if metrics.get("vina_generated_ligand_centroid_fallback_used") is True:
                blocking.append(f"vina_generated_ligand_centroid_fallback:{row.get('sample_id')}")
            if metrics.get("vina_box_definition_source") == "generated_ligand_centroid_fallback":
                blocking.append(f"vina_generated_ligand_centroid_box_source:{row.get('sample_id')}")
            if metrics.get("vina_score_comparability") == "non_comparable":
                warnings.append(f"vina_zero_charge_retry_non_comparable:{row.get('sample_id')}")

    if stage_row.get("N_raw_attempt_metadata") != len(samples):
        blocking.append("stage_attrition_N_raw_attempt_metadata_mismatch")
    if len(labels) != len(samples):
        blocking.append("label_rows_do_not_match_samples")

    required_artifacts = [
        run_root / "run_metadata.json",
        run_root / "samples.jsonl",
        run_root / "stage_attrition.json",
        run_root / "evaluator" / "evaluator_input.jsonl",
        run_root / "evaluator" / "evaluator_tool_results.jsonl",
        run_root / "labels.jsonl",
        run_root / "summaries" / "label_summary.json",
        run_root / "summaries" / "prevalence_summary.json",
    ]
    for artifact in required_artifacts:
        if not artifact.exists():
            blocking.append(f"required_artifact_missing:{artifact}")

    sanity_results = run_sanity_set()
    if not all(item["passed"] for item in sanity_results):
        blocking.append("sanity_set_failed")

    if all((sample.get("quality_flags") or {}).get("final_only_selected_output_view") for sample in samples):
        warnings.append("final_only_outputs_selected_output_residual_view_only")
    if run_metadata.get("training_data_status") in {"training_data_unknown", "unknown"} or run_metadata.get("leakage_check_status") in {"unknown_risk", "not_checked"}:
        warnings.append("training_data_or_leakage_status_unknown_claim_boundary_required")
    warnings.append("plip_reference_recovery_descriptive_only")
    threshold = internal_energy_unavailable_threshold(payloads["analysis_frozen_gate"])
    unavailable_fraction = coverage.get("internal_energy_unavailable_fraction")
    if coverage["internal_energy_unavailable_count"]:
        warnings.append(
            "posebusters_internal_energy_unavailable_coverage:"
            f"{coverage['internal_energy_unavailable_count']}/{coverage['denominator_posebusters_mol_rows']}"
        )
    if threshold is not None and unavailable_fraction is not None and unavailable_fraction > threshold:
        blocking.append(
            "posebusters_internal_energy_unavailable_fraction_exceeds_threshold:"
            f"{unavailable_fraction:.6f}>{threshold:.6f}"
        )

    gate_status = "failed" if blocking else ("passed_with_warnings" if warnings else "passed")
    return with_schema_ref(
        {
            "gate_status": gate_status,
            "blocking_failures": sorted(set(blocking)),
            "warnings": sorted(set(warnings)),
            "checked_inputs": {
                "run_root": str(run_root),
                "num_samples": len(samples),
                "num_tool_results": len(tool_results),
                "num_labels": len(labels),
                "receptor_prep_records": receptor_records,
                "required_artifacts_present": all(path.exists() for path in required_artifacts),
            },
            "coverage": {
                "posebusters_internal_energy": coverage,
                "internal_energy_unavailable_threshold": threshold,
            },
            "config_hashes": {key: value for key, value in hashes.items() if key != "tool_versions_lock"},
            "tool_versions_lock_hash": hashes["tool_versions_lock"],
            "required_artifacts_present": all(path.exists() for path in required_artifacts),
            "sanity_set_results": sanity_results,
            "claim_boundary": "selected_output_residual_audit_not_raw_failure_prevalence"
            if "final_only_outputs_selected_output_residual_view_only" in warnings
            else "specified_scope_only_no_global_prevalence",
            "policy_versions": {
                "receptor_prep_policy_version": payloads["receptor_prep_policy"].get("receptor_prep_policy_version"),
                "evaluator_policy_version": payloads["evaluator_policy"].get("evaluator_policy_version"),
                "label_protocol_version": payloads["label_config"].get("label_protocol_version"),
                "analysis_frozen_gate_version": payloads["analysis_frozen_gate"].get("analysis_frozen_gate_version"),
            },
            "created_time": now_utc(),
        },
        GATE_RESULT_SCHEMA_PATH,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--receptor-prep-policy", default="configs/audit/receptor_prep_policy_v0_1.yaml")
    parser.add_argument("--evaluator-policy", default="configs/audit/evaluator_policy_v0_1.yaml")
    parser.add_argument("--label-config", default="configs/audit/diagnosis_label_config_v0_2.yaml")
    parser.add_argument("--denominator-config", default="configs/audit/denominator_statistics_schema_v0_1.yaml")
    parser.add_argument("--gate-config", default="configs/audit/analysis_frozen_gate_v0_1.yaml")
    parser.add_argument("--tool-versions-lock", default="configs/audit/tool_versions.lock")
    args = parser.parse_args()
    run_root = Path(args.run_root).resolve()
    result = check_gate(run_root, args)
    output_path = run_root / "summaries" / "analysis_frozen_gate_result.json"
    write_json_with_schema(output_path, result, GATE_RESULT_SCHEMA_PATH)
    update_output_manifest(run_root)
    print({"run_root": str(run_root), "gate_status": result["gate_status"], "blocking": len(result["blocking_failures"])})
    return 0 if result["gate_status"] != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
