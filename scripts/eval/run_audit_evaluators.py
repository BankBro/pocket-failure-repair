#!/usr/bin/env python3
"""Run frozen-style audit evaluators for third-party generated samples."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rdkit import Chem

from scripts.eval.audit_common import (
    load_yaml,
    normalized_config_hash,
    now_utc,
    read_json,
    read_jsonl,
    sha256_file,
    with_schema_ref,
    write_json,
    write_jsonl,
    write_jsonl_with_schema,
)
from scripts.eval.eval_official_tools import run_plip, run_vina


EVALUATOR_RESULT_SCHEMA_PATH = "schemas/third_party_audit/diagnosis/evaluator_tool_result_v0_1.json"
EVALUATOR_INPUT_SCHEMA_PATH = "schemas/third_party_audit/diagnosis/evaluator_input_v0_1.json"
RUN_METADATA_SCHEMA_VERSION = "run_metadata_v0_1"
RUN_METADATA_SCHEMA_PATH = "schemas/third_party_audit/run/run_metadata_v0_1.json"
SAMPLE_SCHEMA_VERSION = "failure_sample_metadata_v0_1"
SAMPLE_SCHEMA_PATH = "schemas/third_party_audit/samples/failure_sample_metadata_v0_1.json"
STAGE_ATTRITION_SCHEMA_VERSION = "stage_attrition_v0_1"
STAGE_ATTRITION_SCHEMA_PATH = "schemas/third_party_audit/attrition/stage_attrition_v0_1.json"
OUTPUT_MANIFEST_SCHEMA_VERSION = "output_manifest_v0_1"
OUTPUT_MANIFEST_SCHEMA_PATH = "schemas/third_party_audit/run/output_manifest_v0_1.json"
MVP_SUMMARY_SCHEMA_VERSION = "mvp_sanity_summary_v0_1"
MVP_SUMMARY_SCHEMA_PATH = "schemas/third_party_audit/diagnosis/mvp_sanity_summary_v0_1.json"
POSEBUSTERS_RAW_RESULT_SCHEMA_PATH = "schemas/third_party_audit/diagnosis/posebusters_raw_result_v0_1.json"


def config_bundle(args: argparse.Namespace) -> dict[str, Any]:
    paths = {
        "receptor_prep_policy": Path(args.receptor_prep_policy),
        "evaluator_policy": Path(args.evaluator_policy),
        "label_config": Path(args.label_config),
        "denominator_config": Path(args.denominator_config),
        "analysis_frozen_gate": Path(args.gate_config),
        "tool_versions_lock": Path(args.tool_versions_lock),
    }
    payloads = {key: load_yaml(path) for key, path in paths.items()}
    hashes = {key: normalized_config_hash(path) for key, path in paths.items()}
    return {"paths": paths, "payloads": payloads, "hashes": hashes}


def copy_sample_molecule(source_path: str | None, destination: Path) -> tuple[str | None, str | None]:
    if not source_path:
        return None, None
    source = Path(source_path)
    if not source.exists():
        return None, None
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    return str(destination), sha256_file(destination)


def build_samples(
    source_samples: list[dict[str, Any]],
    source_run: dict[str, Any],
    receptor_prep: dict[str, Any],
    output_run_root: Path,
    run_id: str,
    configs: dict[str, Any],
) -> list[dict[str, Any]]:
    sample_dir = output_run_root / "processed" / "normalized_samples"
    samples: list[dict[str, Any]] = []
    for index, source in enumerate(source_samples):
        copied_path, copied_sha = copy_sample_molecule(
            source.get("molecule_path"),
            sample_dir / f"sample_{index:03d}.sdf",
        )
        sample = dict(source)
        sample.update(
            {
                "schema_version": SAMPLE_SCHEMA_VERSION,
                "schema_path": SAMPLE_SCHEMA_PATH,
                "sample_id": source["sample_id"],
                "parent_sample_id": source["sample_id"],
                "source_run_id": source.get("run_id"),
                "source_sample_id": source.get("sample_id"),
                "source_molecule_path": source.get("molecule_path"),
                "lineage_id": f"{run_id}::{source.get('run_id')}::{source.get('sample_id')}",
                "run_id": run_id,
                "run_boundary_label": "selected_output_residual_audit",
                "molecule_path": copied_path,
                "pose_path": copied_path,
                "normalized_sha256": copied_sha,
                "receptor_path": receptor_prep["cleaned_receptor_path"],
                "raw_receptor_path": receptor_prep["raw_receptor_path"],
                "cleaned_receptor_path": receptor_prep["cleaned_receptor_path"],
                "cleaned_receptor_sha256": receptor_prep["cleaned_receptor_sha256"],
                "reference_ligand_path": receptor_prep.get("reference_ligand_path"),
                "reference_ligand_record": receptor_prep["reference_ligand"],
                "receptor_prep_id": receptor_prep["receptor_prep_id"],
                "receptor_prep_record_path": str(output_run_root / "processed" / "receptors" / Path(args_receptor_record_path(receptor_prep)).name),
                "receptor_prep_policy_version": receptor_prep["receptor_prep_policy_version"],
                "receptor_prep_policy_hash": receptor_prep["receptor_prep_policy_hash"],
                "pocket_box": receptor_prep["pocket_box"],
                "evaluator_policy_version": configs["payloads"]["evaluator_policy"]["evaluator_policy_version"],
                "evaluator_policy_hash": configs["hashes"]["evaluator_policy"],
                "denominator_policy_version": configs["payloads"]["denominator_config"]["statistics_protocol_version"],
                "denominator_policy_hash": configs["hashes"]["denominator_config"],
                "label_protocol_version": configs["payloads"]["label_config"]["label_protocol_version"],
                "label_config_hash": configs["hashes"]["label_config"],
                "tool_versions_lock_hash": configs["hashes"]["tool_versions_lock"],
                "audit_labels": {},
                "quality_flags": {
                    **(source.get("quality_flags") or {}),
                    "final_only_selected_output_view": True,
                    "source_stage1_sample": True,
                },
            }
        )
        if copied_path is None:
            sample["quality_flags"]["missing_copied_molecule"] = True
        if "method" not in sample or not sample["method"]:
            sample["method"] = source_run.get("method", "DiffSBDD")
        samples.append(sample)
    return samples


def args_receptor_record_path(receptor_prep: dict[str, Any]) -> str:
    return str(receptor_prep.get("_record_path") or "receptor_prep.json")


def evaluator_input_row(sample: dict[str, Any], baseline: str) -> dict[str, Any]:
    molecule_path = sample.get("molecule_path")
    cleaned_receptor_path = sample["cleaned_receptor_path"]
    return with_schema_ref(
        {
            "sample_id": sample["sample_id"],
            "run_id": sample["run_id"],
            "method": sample["method"],
            "stage": sample.get("stage"),
            "sample_role": sample.get("sample_role"),
            "sample_index": sample.get("sample_index"),
            "complex_id": sample.get("complex_id"),
            "candidate_id": sample["sample_id"],
            "repair_id": sample["sample_id"],
            "baseline": baseline,
            "failure_type": None,
            "molecule_path": molecule_path,
            "repaired_ligand_path": molecule_path,
            "protein_path": cleaned_receptor_path,
            "cleaned_receptor_path": cleaned_receptor_path,
            "reference_ligand_path": sample.get("reference_ligand_path"),
            "source_failed_ligand_path": None,
            "receptor_prep_id": sample["receptor_prep_id"],
            "receptor_prep_record_path": sample["receptor_prep_record_path"],
            "pocket_box": sample["pocket_box"],
            "receptor_prep_policy_version": sample["receptor_prep_policy_version"],
            "receptor_prep_policy_hash": sample["receptor_prep_policy_hash"],
            "evaluator_policy_version": sample["evaluator_policy_version"],
            "evaluator_policy_hash": sample["evaluator_policy_hash"],
            "denominator_policy_version": sample["denominator_policy_version"],
            "denominator_policy_hash": sample["denominator_policy_hash"],
            "label_protocol_version": sample["label_protocol_version"],
            "label_config_hash": sample["label_config_hash"],
            "tool_versions_lock_hash": sample["tool_versions_lock_hash"],
        },
        EVALUATOR_INPUT_SCHEMA_PATH,
    )


def tool_row(
    sample: dict[str, Any],
    evaluator_name: str,
    status: str,
    metrics: dict[str, Any],
    errors: list[str],
    input_paths: list[str],
    output_paths: list[str],
    command: str | None = None,
    exit_code: int | None = None,
) -> dict[str, Any]:
    return with_schema_ref(
        {
            "sample_id": sample["sample_id"],
            "run_id": sample["run_id"],
            "method": sample["method"],
            "stage": sample.get("stage"),
            "sample_role": sample.get("sample_role"),
            "evaluator_name": evaluator_name,
            "evaluator_version": None,
            "evaluator_config": metrics.get("evaluator_config"),
            "input_paths": input_paths,
            "output_paths": output_paths,
            "command": command,
            "environment": "pfr-eval-tools",
            "status": status,
            "exit_code": exit_code,
            "stdout_path": None,
            "stderr_path": None,
            "metrics": metrics,
            "errors": errors,
            "created_time": now_utc(),
            "receptor_prep_id": sample.get("receptor_prep_id"),
            "receptor_prep_policy_hash": sample.get("receptor_prep_policy_hash"),
            "evaluator_policy_hash": sample.get("evaluator_policy_hash"),
            "tool_versions_lock_hash": sample.get("tool_versions_lock_hash"),
        },
        EVALUATOR_RESULT_SCHEMA_PATH,
    )


def run_rdkit(sample: dict[str, Any]) -> dict[str, Any]:
    path = sample.get("molecule_path")
    metrics: dict[str, Any] = {"evaluator_config": "SDMolSupplier_sanitize_false_then_SanitizeMol"}
    if not path or not Path(path).exists():
        return tool_row(sample, "rdkit", "input_missing", metrics, ["missing_molecule_path"], [], [])
    try:
        supplier = Chem.SDMolSupplier(str(path), sanitize=False, removeHs=False)
        mols = [mol for mol in supplier if mol is not None]
    except Exception as exc:
        return tool_row(sample, "rdkit", "format_error", metrics, [repr(exc)], [path], [])
    if not mols:
        return tool_row(sample, "rdkit", "format_error", metrics, ["rdkit_parse_returned_none"], [path], [])
    if len(mols) > 1:
        metrics["num_molecules_in_file"] = len(mols)
        return tool_row(sample, "rdkit", "format_error", metrics, ["multiple_molecules_in_single_sample_sdf"], [path], [])
    mol = mols[0]
    metrics["num_atoms"] = mol.GetNumAtoms()
    metrics["num_bonds"] = mol.GetNumBonds()
    metrics["has_3d_conformer"] = mol.GetNumConformers() > 0
    if mol.GetNumConformers() == 0:
        return tool_row(sample, "rdkit", "format_error", metrics, ["missing_3d_conformer"], [path], [])
    try:
        Chem.SanitizeMol(mol)
        metrics["sanitized"] = True
        metrics["smiles"] = Chem.MolToSmiles(mol)
        status = "passed"
        errors: list[str] = []
    except Exception as exc:
        metrics["sanitized"] = False
        status = "failed"
        errors = [repr(exc)]
    return tool_row(sample, "rdkit", status, metrics, errors, [path], [])


def posebusters_formal_status(metrics: dict[str, Any], layer: dict[str, Any]) -> tuple[str, list[str]]:
    errors: list[str] = []
    if metrics.get("posebusters_error"):
        return "tool_failure", [str(metrics["posebusters_error"])]
    checks = metrics.get("posebusters_bool_checks")
    if not isinstance(checks, dict):
        return "tool_failure", ["posebusters_bool_checks_missing"]
    report_values = metrics.get("posebusters_report_values")
    if not isinstance(report_values, dict):
        report_values = {}
    raw_columns = set(metrics.get("posebusters_columns") or report_values.keys())
    required_columns = list(layer.get("required_columns") or layer.get("frozen_columns") or [])
    conditional_columns = list(layer.get("conditional_columns") or [])
    frozen_columns = [*required_columns, *conditional_columns]
    failed_columns = [column for column in required_columns if checks.get(column) is False]
    missing_columns = [column for column in required_columns if column not in checks]
    conditional_failed = [column for column in conditional_columns if checks.get(column) is False]
    conditional_missing: list[str] = []
    unavailable_columns: list[str] = []
    unavailable_reasons: dict[str, str] = {}
    upstream_required_failed = bool(failed_columns)
    for column in conditional_columns:
        if column in checks:
            continue
        if column not in raw_columns:
            conditional_missing.append(column)
            continue
        reason = conditional_unavailable_reason(column, metrics, layer, checks, upstream_required_failed)
        if reason:
            unavailable_columns.append(column)
            unavailable_reasons[column] = reason
        else:
            conditional_missing.append(column)
    failed_columns.extend(conditional_failed)
    missing_columns.extend(conditional_missing)
    required_pass = not [column for column in required_columns if column in missing_columns] and not [
        column for column in failed_columns if column in required_columns
    ]
    conditional_coverage_pass = not unavailable_columns
    formal_pass = not missing_columns and not failed_columns
    formal_name = layer["formal_metric_name"]
    metrics[formal_name] = formal_pass
    metrics[f"{formal_name}_frozen_columns"] = frozen_columns
    metrics[f"{formal_name}_required_columns"] = required_columns
    metrics[f"{formal_name}_conditional_columns"] = conditional_columns
    metrics[f"{formal_name}_checked_columns"] = [column for column in frozen_columns if column in checks]
    metrics[f"{formal_name}_failed_columns"] = failed_columns
    metrics[f"{formal_name}_missing_columns"] = missing_columns
    metrics[f"{formal_name}_unavailable_columns"] = unavailable_columns
    metrics[f"{formal_name}_unavailable_reasons"] = unavailable_reasons
    metrics[f"{formal_name}_required_pass"] = required_pass
    metrics[f"{formal_name}_conditional_coverage_pass"] = conditional_coverage_pass
    metrics[f"{formal_name}_clean_pass"] = formal_pass and conditional_coverage_pass
    if missing_columns:
        errors.extend(f"missing_frozen_column:{column}" for column in missing_columns)
        return "tool_failure", errors
    if checks.get("mol_pred_loaded") is False:
        return "format_error", ["posebusters_mol_pred_load_failed"]
    return ("passed" if formal_pass else "failed"), errors


def conditional_unavailable_reason(
    column: str,
    metrics: dict[str, Any],
    layer: dict[str, Any],
    checks: dict[str, Any],
    upstream_required_failed: bool,
) -> str | None:
    report_values = metrics.get("posebusters_report_values")
    if not isinstance(report_values, dict):
        return None
    if column not in report_values or isinstance(report_values.get(column), bool) or report_values.get(column) is not None:
        return None
    policy = (layer.get("conditional_unavailable_allowed") or {}).get(column)
    if not isinstance(policy, dict):
        return None
    required_raw_columns = list(policy.get("required_raw_columns") or [])
    if any(raw_column not in report_values for raw_column in required_raw_columns):
        return None
    required_true_checks = list(policy.get("required_true_checks") or [])
    required_true = all(checks.get(check_name) is True for check_name in required_true_checks)
    if not required_true and not upstream_required_failed:
        return None
    stderr_head = str(metrics.get("stderr_head") or "")
    for pattern, reason in (policy.get("stderr_reason_patterns") or {}).items():
        if pattern in stderr_head:
            return str(reason)
    return str(policy.get("default_reason") or f"{column}_unavailable")


def run_posebusters(
    sample: dict[str, Any],
    evaluator_input_path: Path,
    index: int,
    layer: dict[str, Any],
    raw_dir: Path,
) -> dict[str, Any]:
    config = layer["config"]
    output_path = raw_dir / f"posebusters_{config}_{index:03d}.json"
    command = [
        sys.executable,
        str(ROOT / "scripts" / "eval" / "eval_posebusters_one.py"),
        "--repaired-candidates",
        str(evaluator_input_path),
        "--index",
        str(index),
        "--output",
        str(output_path),
        "--timeout",
        str(layer.get("inner_timeout_seconds", 300)),
        "--config",
        config,
    ]
    metrics: dict[str, Any] = {
        "evaluator_config": config,
        "posebusters_layer": layer.get("formal_metric_name"),
    }
    exit_code: int | None = None
    if not output_path.exists():
        try:
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
                timeout=int(layer.get("outer_timeout_seconds", 420)),
            )
            exit_code = result.returncode
            metrics["stdout_head"] = result.stdout[:1000]
            metrics["stderr_head"] = result.stderr[:1000]
        except subprocess.TimeoutExpired as exc:
            metrics["timeout_seconds"] = int(layer.get("outer_timeout_seconds", 420))
            metrics["stdout_head"] = (exc.stdout or "")[:1000]
            metrics["stderr_head"] = (exc.stderr or "")[:1000]
            return tool_row(
                sample,
                layer["evaluator_name"],
                "timeout",
                metrics,
                [f"timeout_after_{layer.get('outer_timeout_seconds', 420)}s"],
                [path for path in [sample.get("molecule_path"), sample.get("cleaned_receptor_path")] if path],
                [],
                " ".join(command),
                None,
            )
    else:
        metrics["reused_raw_output"] = True
    if output_path.exists():
        try:
            metrics.update(read_json(output_path))
        except Exception as exc:
            return tool_row(
                sample,
                layer["evaluator_name"],
                "tool_failure",
                metrics,
                [f"raw_output_read_failed:{exc!r}"],
                [path for path in [sample.get("molecule_path"), sample.get("cleaned_receptor_path")] if path],
                [str(output_path)],
                " ".join(command),
                exit_code,
            )
    status, errors = posebusters_formal_status(metrics, layer)
    if exit_code not in (0, None) and status != "failed":
        status = "tool_failure"
        errors.append(f"exit_code_{exit_code}")
    return tool_row(
        sample,
        layer["evaluator_name"],
        status,
        metrics,
        errors,
        [path for path in [sample.get("molecule_path"), sample.get("cleaned_receptor_path")] if path],
        [str(output_path)] if output_path.exists() else [],
        " ".join(command),
        exit_code,
    )


def run_optional_tool(sample: dict[str, Any], input_row: dict[str, Any], tool_name: str, work_dir: Path) -> dict[str, Any]:
    work_dir.mkdir(parents=True, exist_ok=True)
    metrics = run_plip(input_row, work_dir) if tool_name == "plip" else run_vina(input_row, work_dir)
    errors: list[str] = []
    available = metrics.get(f"{tool_name}_available")
    error = metrics.get(f"{tool_name}_error")
    if available is False:
        status = "unavailable"
        errors.append(str(error or "tool_unavailable"))
    elif error:
        error_text = str(error)
        if error_text.startswith("missing_"):
            status = "input_missing"
        elif error_text.endswith("_prepare_failed"):
            status = "format_error" if tool_name == "vina" and "ligand" in error_text else "tool_failure"
        else:
            status = "tool_failure"
        errors.append(error_text)
    else:
        status = "passed"
    metrics["evaluator_config"] = "auxiliary_score_only" if tool_name == "vina" else "reference_relative_interaction_evidence"
    return tool_row(
        sample,
        tool_name,
        status,
        metrics,
        errors,
        [path for path in [sample.get("molecule_path"), sample.get("cleaned_receptor_path")] if path],
        sorted(str(path) for path in work_dir.rglob("*") if path.is_file()),
    )


def build_stage_attrition(samples: list[dict[str, Any]], tool_rows: list[dict[str, Any]], source_run: dict[str, Any]) -> dict[str, Any]:
    rdkit_rows = [row for row in tool_rows if row["evaluator_name"] == "rdkit"]
    dock_rows = [row for row in tool_rows if row["evaluator_name"] == "posebusters_dock"]
    n_evaluable = sum(1 for row in rdkit_rows if row["status"] in {"passed", "failed"})
    run_id = samples[0]["run_id"] if samples else "unknown"
    method = samples[0]["method"] if samples else source_run.get("method", "DiffSBDD")
    dataset_view_id = samples[0].get("dataset_view_id", source_run.get("dataset_view_id", "unknown")) if samples else "unknown"
    return {
        "schema_version": STAGE_ATTRITION_SCHEMA_VERSION,
        "schema_path": STAGE_ATTRITION_SCHEMA_PATH,
        "method": method,
        "run_id": run_id,
        "dataset_view_id": dataset_view_id,
        "summary_scope": "frozen_style_post_evaluator_selected_output_residual",
        "denominator_policy_version": samples[0].get("denominator_policy_version") if samples else None,
        "denominator_policy_hash": samples[0].get("denominator_policy_hash") if samples else None,
        "rows": [
            {
                "method": method,
                "run_id": run_id,
                "seed": source_run.get("seed"),
                "dataset_view_id": dataset_view_id,
                "complex_id": samples[0].get("complex_id", "unknown") if samples else "unknown",
                "pocket_id": samples[0].get("pocket_id") if samples else None,
                "N_budget": source_run.get("sampling_budget"),
                "N_raw_attempt_metadata": len(samples),
                "N_raw_captured": len([sample for sample in samples if sample.get("molecule_path")]),
                "N_original_failed_samples": 0,
                "N_parse_fail": sum(1 for row in rdkit_rows if row["status"] in {"format_error", "input_missing"}),
                "N_parsed": sum(1 for row in rdkit_rows if row["status"] in {"passed", "failed"}),
                "N_rdkit_invalid": sum(1 for row in rdkit_rows if row["status"] == "failed"),
                "N_rdkit_valid": sum(1 for row in rdkit_rows if row["status"] == "passed"),
                "N_anchor_fail": None,
                "N_anchor_preserved": None,
                "N_docking_attempted": len(dock_rows),
                "N_docking_failed": sum(1 for row in dock_rows if row["status"] in {"failed", "tool_failure", "timeout", "format_error"}),
                "N_pose_available": len([sample for sample in samples if sample.get("pose_path")]),
                "N_not_evaluable": len(samples) - n_evaluable,
                "N_evaluable": n_evaluable,
                "N_rejected": 0,
                "N_selected": 0,
                "N_final": len([sample for sample in samples if sample.get("sample_role") == "final_output"]),
                "N_repair_eligible": None,
                "notes": "Frozen-style evaluator attrition. Denominator is sample metadata rows; source run contains final outputs only, so raw failure prevalence is not claimed.",
            }
        ],
    }


def write_run_metadata(
    output_run_root: Path,
    args: argparse.Namespace,
    source_run: dict[str, Any],
    configs: dict[str, Any],
    samples: list[dict[str, Any]],
) -> dict[str, Any]:
    payload = {
        "schema_version": RUN_METADATA_SCHEMA_VERSION,
        "schema_path": RUN_METADATA_SCHEMA_PATH,
        "experiment_id": args.experiment_id,
        "run_id": args.run_id,
        "method": source_run.get("method", "DiffSBDD"),
        "run_boundary_label": "selected_output_residual_audit",
        "upstream_repo": source_run.get("upstream_repo"),
        "upstream_commit": source_run.get("upstream_commit"),
        "fork_repo": None,
        "fork_branch": None,
        "fork_commit": None,
        "patches": [],
        "algorithm_changed": False,
        "checkpoint_id": source_run.get("checkpoint_id"),
        "checkpoint_source": source_run.get("checkpoint_source"),
        "checkpoint_sha256": source_run.get("checkpoint_sha256"),
        "training_data_status": source_run.get("training_data_status", "training_data_unknown"),
        "dataset_name": source_run.get("dataset_name", "third_party_repo_examples_v1"),
        "dataset_version": source_run.get("dataset_version", "cloned_repo_examples"),
        "raw_dataset_id": source_run.get("raw_dataset_id"),
        "dataset_view_id": source_run.get("dataset_view_id", "diffsbdd_example_3rfm_5ndu_v1"),
        "split_id": source_run.get("split_id", "example_only_no_formal_split"),
        "preprocessing_id": "frozen_evaluator_receptor_prep_v0_1",
        "raw_checksum": source_run.get("raw_checksum"),
        "view_checksum": source_run.get("view_checksum"),
        "split_checksum": source_run.get("split_checksum"),
        "leakage_check_status": source_run.get("leakage_check_status", "unknown_risk"),
        "leakage_report_path": source_run.get("leakage_report_path"),
        "seed": source_run.get("seed"),
        "sampling_budget": len(samples),
        "config_hash": configs["hashes"]["evaluator_policy"],
        "resolved_config_path": str(Path(args.experiment_dir) / "configs" / "resolved"),
        "command": " ".join(sys.argv),
        "environment": sys.executable,
        "hardware": None,
        "stdout_path": None,
        "stderr_path": None,
        "exit_code": 0,
        "output_manifest_path": str(output_run_root / "output_manifest.json"),
        "resource_budget_config_version": source_run.get("resource_budget_config_version", "pfr_third_party_audit_resource_budget_v1"),
        "resource_budget_config_hash": source_run.get("resource_budget_config_hash"),
        "label_protocol_version": configs["payloads"]["label_config"]["label_protocol_version"],
        "label_config_hash": configs["hashes"]["label_config"],
        "receptor_prep_policy_version": configs["payloads"]["receptor_prep_policy"]["receptor_prep_policy_version"],
        "receptor_prep_policy_hash": configs["hashes"]["receptor_prep_policy"],
        "evaluator_policy_version": configs["payloads"]["evaluator_policy"]["evaluator_policy_version"],
        "evaluator_policy_hash": configs["hashes"]["evaluator_policy"],
        "denominator_policy_version": configs["payloads"]["denominator_config"]["statistics_protocol_version"],
        "denominator_policy_hash": configs["hashes"]["denominator_config"],
        "analysis_frozen_gate_version": configs["payloads"]["analysis_frozen_gate"]["analysis_frozen_gate_version"],
        "analysis_frozen_gate_hash": configs["hashes"]["analysis_frozen_gate"],
        "tool_versions_lock_path": args.tool_versions_lock,
        "tool_versions_lock_hash": configs["hashes"]["tool_versions_lock"],
        "source_run_root": str(Path(args.source_run_root).resolve()),
        "n_source_sample_rows": len(samples),
        "claim_boundary": "selected_output_residual_audit_not_raw_failure_prevalence",
        "status": "completed",
    }
    write_json(output_run_root / "run_metadata.json", payload)
    return payload


def write_manifest(output_run_root: Path, run_id: str, method: str, artifacts: list[Path]) -> None:
    payload = {
        "schema_version": OUTPUT_MANIFEST_SCHEMA_VERSION,
        "schema_path": OUTPUT_MANIFEST_SCHEMA_PATH,
        "run_id": run_id,
        "method": method,
        "metadata_schemas": {
            "run_metadata": RUN_METADATA_SCHEMA_PATH,
            "sample_metadata": SAMPLE_SCHEMA_PATH,
            "stage_attrition": STAGE_ATTRITION_SCHEMA_PATH,
            "output_manifest": OUTPUT_MANIFEST_SCHEMA_PATH,
            "evaluator_input": EVALUATOR_INPUT_SCHEMA_PATH,
            "evaluator_tool_result": EVALUATOR_RESULT_SCHEMA_PATH,
            "posebusters_raw_result": POSEBUSTERS_RAW_RESULT_SCHEMA_PATH,
            "receptor_prep_record": "schemas/third_party_audit/receptor/receptor_prep_record_v0_1.json",
        },
        "captured_outputs": [],
        "processed_outputs": sorted(str(path) for path in (output_run_root / "processed").rglob("*") if path.is_file()),
        "logs": sorted(str(path) for path in (output_run_root / "logs").rglob("*") if path.is_file()),
        "manifests": sorted(str(path) for path in (output_run_root / "manifests").rglob("*") if path.is_file()),
        "evaluator_outputs": sorted(str(path) for path in artifacts if path.exists()),
        "sha256": {},
        "n_final_sdf_records": len(list((output_run_root / "processed" / "normalized_samples").glob("*.sdf"))),
        "n_output_artifacts": None,
        "notes": "Frozen-style unified evaluator output manifest. Source DiffSBDD inference outputs are provenance inputs, not regenerated here.",
    }
    all_paths = [
        output_run_root / "run_metadata.json",
        output_run_root / "samples.jsonl",
        output_run_root / "stage_attrition.json",
        *[path for path in (output_run_root / "processed").rglob("*") if path.is_file()],
        *[path for path in (output_run_root / "evaluator").rglob("*") if path.is_file()],
        *[path for path in (output_run_root / "summaries").rglob("*") if path.is_file()],
    ]
    payload["n_output_artifacts"] = len(all_paths)
    for path in all_paths:
        payload["sha256"][str(path)] = sha256_file(path)
    write_json(output_run_root / "output_manifest.json", payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run-root", required=True)
    parser.add_argument("--output-run-root", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--experiment-dir", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--receptor-prep-record", required=True)
    parser.add_argument("--receptor-prep-policy", default="configs/audit/receptor_prep_policy_v0_1.yaml")
    parser.add_argument("--evaluator-policy", default="configs/audit/evaluator_policy_v0_1.yaml")
    parser.add_argument("--label-config", default="configs/audit/diagnosis_label_config_v0_2.yaml")
    parser.add_argument("--denominator-config", default="configs/audit/denominator_statistics_schema_v0_1.yaml")
    parser.add_argument("--gate-config", default="configs/audit/analysis_frozen_gate_v0_1.yaml")
    parser.add_argument("--tool-versions-lock", default="configs/audit/tool_versions.lock")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--tools", default="rdkit,posebusters,plip,vina")
    args = parser.parse_args()

    source_run_root = Path(args.source_run_root).resolve()
    output_run_root = Path(args.output_run_root).resolve()
    evaluator_dir = output_run_root / "evaluator"
    raw_dir = evaluator_dir / "raw_tool_outputs"
    work_dir = evaluator_dir / "work"
    summaries_dir = output_run_root / "summaries"
    for directory in [raw_dir, work_dir, summaries_dir, output_run_root / "logs", output_run_root / "manifests"]:
        directory.mkdir(parents=True, exist_ok=True)

    configs = config_bundle(args)
    source_run = read_json(source_run_root / "run_metadata.json")
    source_samples = read_jsonl(source_run_root / "samples.jsonl")
    if args.limit is not None:
        source_samples = source_samples[: args.limit]
    receptor_prep_record_path = Path(args.receptor_prep_record).resolve()
    receptor_prep = read_json(receptor_prep_record_path)
    receptor_prep["_record_path"] = str(receptor_prep_record_path)

    # Copy receptor prep artifacts into this run so the run is self-contained.
    receptor_dir = output_run_root / "processed" / "receptors"
    receptor_dir.mkdir(parents=True, exist_ok=True)
    for key in ["cleaned_receptor_path", "reference_ligand_path"]:
        source_path = Path(receptor_prep[key])
        copied = receptor_dir / source_path.name
        if source_path.resolve() != copied.resolve():
            shutil.copyfile(source_path, copied)
        receptor_prep[key] = str(copied)
        receptor_prep[f"{key.removesuffix('_path')}_sha256"] = sha256_file(copied)
    copied_record_path = receptor_dir / receptor_prep_record_path.name
    receptor_prep_for_run = dict(receptor_prep)
    receptor_prep_for_run.pop("_record_path", None)
    receptor_prep_for_run["cleaned_receptor_path"] = receptor_prep["cleaned_receptor_path"]
    receptor_prep_for_run["reference_ligand_path"] = receptor_prep["reference_ligand_path"]
    receptor_prep_for_run["cleaned_receptor_sha256"] = sha256_file(receptor_prep["cleaned_receptor_path"])
    receptor_prep_for_run["reference_ligand_sha256"] = sha256_file(receptor_prep["reference_ligand_path"])
    write_json(copied_record_path, receptor_prep_for_run)
    receptor_prep["_record_path"] = str(copied_record_path)

    samples = build_samples(source_samples, source_run, receptor_prep, output_run_root, args.run_id, configs)
    evaluator_inputs = [evaluator_input_row(sample, "unified_evaluation_pipeline_alignment") for sample in samples]
    evaluator_input_path = evaluator_dir / "evaluator_input.jsonl"
    write_jsonl(output_run_root / "samples.jsonl", samples)
    write_jsonl_with_schema(evaluator_input_path, evaluator_inputs, EVALUATOR_INPUT_SCHEMA_PATH)

    evaluator_policy = configs["payloads"]["evaluator_policy"]
    tools = {tool.strip() for tool in args.tools.split(",") if tool.strip()}
    results: list[dict[str, Any]] = []
    for index, sample in enumerate(samples):
        input_row = evaluator_inputs[index]
        sample_work_dir = work_dir / sample["sample_id"]
        if "rdkit" in tools:
            results.append(run_rdkit(sample))
        if "posebusters" in tools:
            pb_policy = evaluator_policy["tools"]["posebusters"]
            ligand_layer = dict(pb_policy["ligand_core"])
            pocket_layer = dict(pb_policy["pocket_core"])
            for layer in [ligand_layer, pocket_layer]:
                layer["inner_timeout_seconds"] = pb_policy.get("inner_timeout_seconds", 300)
                layer["outer_timeout_seconds"] = pb_policy.get("outer_timeout_seconds", 420)
                results.append(run_posebusters(sample, evaluator_input_path, index, layer, raw_dir))
        if "plip" in tools:
            results.append(run_optional_tool(sample, input_row, "plip", sample_work_dir / "plip"))
        if "vina" in tools:
            results.append(run_optional_tool(sample, input_row, "vina", sample_work_dir / "vina"))

    tool_results_path = evaluator_dir / "evaluator_tool_results.jsonl"
    write_jsonl_with_schema(tool_results_path, results, EVALUATOR_RESULT_SCHEMA_PATH)
    stage_attrition = build_stage_attrition(samples, results, source_run)
    write_json(output_run_root / "stage_attrition.json", stage_attrition)
    run_metadata = write_run_metadata(output_run_root, args, source_run, configs, samples)

    status_counts: dict[str, int] = {}
    for row in results:
        key = f"{row['evaluator_name']}::{row['status']}"
        status_counts[key] = status_counts.get(key, 0) + 1
    summary_path = summaries_dir / "frozen_evaluator_summary.json"
    write_json(
        summary_path,
        {
            "schema_version": MVP_SUMMARY_SCHEMA_VERSION,
            "schema_path": MVP_SUMMARY_SCHEMA_PATH,
            "run_id": args.run_id,
            "method": run_metadata["method"],
            "summary_type": "frozen_style_evaluator_wiring",
            "claim_boundary": "selected_output_residual_audit_not_raw_failure_prevalence",
            "counts": {
                "num_samples": len(samples),
                "num_tool_result_rows": len(results),
                "tool_status_counts": status_counts,
            },
            "notes": "Frozen-style evaluator run using cleaned receptor and frozen PoseBusters columns. Labels and gate are generated by downstream scripts.",
        },
    )
    write_manifest(output_run_root, args.run_id, run_metadata["method"], [evaluator_input_path, tool_results_path, summary_path])
    print(
        {
            "run_id": args.run_id,
            "samples": len(samples),
            "tool_result_rows": len(results),
            "output_run_root": str(output_run_root),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
