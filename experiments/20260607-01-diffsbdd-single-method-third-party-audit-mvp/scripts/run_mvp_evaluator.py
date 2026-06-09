#!/usr/bin/env python3
"""Run MVP evaluator wiring for the DiffSBDD single-method audit trial."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rdkit import Chem

from scripts.eval.eval_official_tools import run_plip, run_vina


EVALUATOR_SCHEMA_VERSION = "evaluator_tool_result_v0_1"
EVALUATOR_SCHEMA_PATH = "schemas/third_party_audit/diagnosis/evaluator_tool_result_v0_1.json"
DIAGNOSIS_SCHEMA_VERSION = "diagnosis_sanity_v0_1"
DIAGNOSIS_SCHEMA_PATH = "schemas/third_party_audit/diagnosis/diagnosis_sanity_v0_1.json"
STAGE_ATTRITION_SCHEMA_VERSION = "stage_attrition_v0_1"
STAGE_ATTRITION_SCHEMA_PATH = "schemas/third_party_audit/attrition/stage_attrition_v0_1.json"
MVP_SUMMARY_SCHEMA_VERSION = "mvp_sanity_summary_v0_1"
MVP_SUMMARY_SCHEMA_PATH = "schemas/third_party_audit/diagnosis/mvp_sanity_summary_v0_1.json"
OUTPUT_MANIFEST_SCHEMA_PATH = "schemas/third_party_audit/run/output_manifest_v0_1.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def evaluator_input_row(sample: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "mvp_evaluator_input_v0_1",
        "schema_path": None,
        "repair_id": sample["sample_id"],
        "candidate_id": sample["sample_id"],
        "complex_id": sample["complex_id"],
        "baseline": "diffsbdd_single_method_mvp",
        "failure_type": None,
        "seed": 0,
        "repaired_ligand_path": sample.get("molecule_path"),
        "protein_path": sample.get("receptor_path"),
        "reference_ligand_path": sample.get("reference_ligand_path"),
        "source_failed_ligand_path": None,
        "sample_id": sample["sample_id"],
        "run_id": sample["run_id"],
        "method": sample["method"],
        "stage": sample.get("stage"),
        "sample_role": sample.get("sample_role"),
    }


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
    return {
        "schema_version": EVALUATOR_SCHEMA_VERSION,
        "schema_path": EVALUATOR_SCHEMA_PATH,
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
        "created_time": "2026-06-07T19:33:02Z",
    }


def run_rdkit(sample: dict[str, Any]) -> dict[str, Any]:
    path = sample.get("molecule_path")
    if not path or not Path(path).exists():
        return tool_row(sample, "rdkit", "input_missing", {}, ["missing_molecule_path"], [], [])
    metrics: dict[str, Any] = {"evaluator_config": "MolFromSDF+SanitizeMol"}
    errors: list[str] = []
    try:
        supplier = Chem.SDMolSupplier(str(path), removeHs=False, sanitize=False)
        mol = next((mol for mol in supplier if mol is not None), None)
        if mol is None:
            return tool_row(sample, "rdkit", "format_error", metrics, ["rdkit_parse_returned_none"], [path], [])
        metrics["num_atoms"] = mol.GetNumAtoms()
        metrics["num_bonds"] = mol.GetNumBonds()
        try:
            Chem.SanitizeMol(mol)
            metrics["sanitized"] = True
            metrics["smiles"] = Chem.MolToSmiles(mol)
            status = "passed"
        except Exception as exc:
            metrics["sanitized"] = False
            errors.append(repr(exc))
            status = "failed"
        return tool_row(sample, "rdkit", status, metrics, errors, [path], [])
    except Exception as exc:
        return tool_row(sample, "rdkit", "tool_failure", metrics, [repr(exc)], [path], [])


def run_posebusters(sample: dict[str, Any], evaluator_input: Path, index: int, config: str, raw_dir: Path) -> dict[str, Any]:
    output_path = raw_dir / f"posebusters_{config}_{index:03d}.json"
    command = [
        sys.executable,
        str(ROOT / "scripts" / "eval" / "eval_posebusters_one.py"),
        "--repaired-candidates",
        str(evaluator_input),
        "--index",
        str(index),
        "--output",
        str(output_path),
        "--timeout",
        "60",
        "--config",
        config,
    ]
    result = subprocess.run(command, check=False, capture_output=True, text=True, cwd=ROOT, timeout=75)
    metrics: dict[str, Any] = {
        "evaluator_config": config,
        "stdout_head": result.stdout[:1000],
        "stderr_head": result.stderr[:1000],
    }
    errors: list[str] = []
    if output_path.exists():
        try:
            metrics.update(read_json(output_path))
        except Exception as exc:
            errors.append(f"raw_output_read_failed:{exc!r}")
    if result.returncode != 0 or metrics.get("posebusters_error"):
        status = "tool_failure"
        errors.append(str(metrics.get("posebusters_error") or f"exit_code_{result.returncode}"))
    elif metrics.get("posebusters_full_pass") is False:
        status = "failed"
    elif metrics.get("posebusters_full_pass") is True:
        status = "passed"
    else:
        status = "unknown"
    return tool_row(
        sample,
        f"posebusters_{config}",
        status,
        metrics,
        errors,
        [path for path in [sample.get("molecule_path"), sample.get("receptor_path")] if path],
        [str(output_path)] if output_path.exists() else [],
        " ".join(command),
        result.returncode,
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
        status = "not_applicable" if str(error).startswith("missing_input") else "tool_failure"
        errors.append(str(error))
    else:
        status = "passed"
    metrics["evaluator_config"] = "optional_auxiliary_score_only" if tool_name == "vina" else "optional_interaction_fingerprint"
    return tool_row(
        sample,
        tool_name,
        status,
        metrics,
        errors,
        [path for path in [sample.get("molecule_path"), sample.get("receptor_path")] if path],
        sorted(str(path) for path in work_dir.rglob("*") if path.is_file()),
    )


def build_diagnosis_rows(samples: list[dict[str, Any]], tool_rows: list[dict[str, Any]], tool_results_path: Path) -> list[dict[str, Any]]:
    by_sample: dict[str, list[dict[str, Any]]] = {}
    for index, row in enumerate(tool_rows, start=1):
        row["result_ref"] = f"{tool_results_path}#L{index}"
        by_sample.setdefault(row["sample_id"], []).append(row)

    diagnosis_rows = []
    for sample in samples:
        rows = by_sample.get(sample["sample_id"], [])
        rdkit = next((row for row in rows if row["evaluator_name"] == "rdkit"), None)
        core = [row for row in rows if row["evaluator_name"] in {"rdkit", "posebusters_mol", "posebusters_dock"}]
        if not sample.get("molecule_path"):
            evaluability = "not_evaluable_missing_data"
        elif rdkit and rdkit["status"] in {"format_error", "input_missing"}:
            evaluability = "not_evaluable_format_error"
        elif any(row["status"] == "tool_failure" for row in core):
            evaluability = "not_evaluable_tool_failure"
        else:
            evaluability = "evaluable"
        diagnosis_rows.append(
            {
                "schema_version": DIAGNOSIS_SCHEMA_VERSION,
                "schema_path": DIAGNOSIS_SCHEMA_PATH,
                "sample_id": sample["sample_id"],
                "run_id": sample["run_id"],
                "method": sample["method"],
                "stage": sample.get("stage"),
                "sample_role": sample.get("sample_role"),
                "diagnosis_mode": "mvp_sanity",
                "evaluability_status": evaluability,
                "provisional_labels": {
                    "primary_label": None,
                    "secondary_labels": [],
                    "near_miss_candidate": None,
                },
                "tool_result_refs": [row["result_ref"] for row in rows],
                "evidence": {
                    "tool_status": {row["evaluator_name"]: row["status"] for row in rows},
                    "claim_boundary": "no formal labels generated",
                },
                "label_protocol_version": "pfr_failure_diagnosis_v0_1_draft",
                "label_config_hash": None,
                "claim_boundary": "mvp_sanity_not_formal_prevalence",
                "notes": "MVP evaluator wiring only. Vina, if present, is auxiliary score-only evidence.",
            }
        )
    return diagnosis_rows


def update_stage_attrition(path: Path, diagnosis_rows: list[dict[str, Any]], tool_rows: list[dict[str, Any]]) -> None:
    payload = read_json(path)
    rows = payload.get("rows", [])
    if rows:
        row = rows[0]
        rdkit_rows = [item for item in tool_rows if item["evaluator_name"] == "rdkit"]
        dock_rows = [item for item in tool_rows if item["evaluator_name"] == "posebusters_dock"]
        row["N_parse_fail"] = sum(1 for item in rdkit_rows if item["status"] in {"format_error", "input_missing"})
        row["N_parsed"] = sum(1 for item in rdkit_rows if item["status"] in {"passed", "failed"})
        row["N_rdkit_invalid"] = sum(1 for item in rdkit_rows if item["status"] == "failed")
        row["N_rdkit_valid"] = sum(1 for item in rdkit_rows if item["status"] == "passed")
        row["N_docking_attempted"] = len(dock_rows)
        row["N_docking_failed"] = sum(1 for item in dock_rows if item["status"] in {"failed", "tool_failure"})
        row["N_evaluable"] = sum(1 for item in diagnosis_rows if item["evaluability_status"] == "evaluable")
        row["N_not_evaluable"] = len(diagnosis_rows) - row["N_evaluable"]
        row["notes"] = "MVP post-evaluator attrition. Denominator is sample metadata rows, not only SDF file count."
    reason_counts: dict[str, int] = {}
    for item in diagnosis_rows:
        if item["evaluability_status"] != "evaluable":
            reason = item["evaluability_status"].removeprefix("not_evaluable_")
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
    payload["summary_scope"] = "mvp_sanity_post_evaluator"
    payload["mvp_required_counts"]["N_tool_failure"] = sum(1 for item in tool_rows if item["status"] == "tool_failure")
    payload["mvp_required_counts"]["N_not_evaluable_by_reason"].update(reason_counts)
    write_json(path, payload)


def update_output_manifest(path: Path, extra_paths: list[Path]) -> None:
    payload = read_json(path)
    payload.setdefault("metadata_schemas", {})["mvp_sanity_summary"] = MVP_SUMMARY_SCHEMA_PATH
    payload["evaluator_outputs"] = sorted({*payload.get("evaluator_outputs", []), *(str(path) for path in extra_paths)})
    payload.setdefault("sha256", {})
    for extra_path in extra_paths:
        if extra_path.exists():
            payload["sha256"][str(extra_path)] = sha256_file(extra_path)
    payload["n_output_artifacts"] = len(payload.get("captured_outputs", [])) + len(payload.get("processed_outputs", []))
    payload["notes"] = "Output capture and evaluator sanity manifest. No formal labels generated."
    write_json(path, payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", required=True)
    args = parser.parse_args()

    run_root = Path(args.run_root).resolve()
    evaluator_dir = run_root / "evaluator"
    raw_dir = evaluator_dir / "raw_tool_outputs"
    work_dir = evaluator_dir / "work"
    summaries_dir = run_root / "summaries"
    raw_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    summaries_dir.mkdir(parents=True, exist_ok=True)

    samples = read_jsonl(run_root / "samples.jsonl")
    evaluator_inputs = [evaluator_input_row(sample) for sample in samples]
    evaluator_input_path = evaluator_dir / "evaluator_input.jsonl"
    write_jsonl(evaluator_input_path, evaluator_inputs)

    results: list[dict[str, Any]] = []
    for index, sample in enumerate(samples):
        input_row = evaluator_inputs[index]
        sample_work_dir = work_dir / sample["sample_id"]
        sample_work_dir.mkdir(parents=True, exist_ok=True)
        results.append(run_rdkit(sample))
        for config in ["mol", "dock"]:
            results.append(run_posebusters(sample, evaluator_input_path, index, config, raw_dir))
        for tool_name in ["plip", "vina"]:
            results.append(run_optional_tool(sample, input_row, tool_name, sample_work_dir / tool_name))

    tool_results_path = evaluator_dir / "evaluator_tool_results.jsonl"
    write_jsonl(tool_results_path, results)
    diagnosis_rows = build_diagnosis_rows(samples, results, tool_results_path)
    diagnosis_path = evaluator_dir / "diagnosis_sanity.jsonl"
    write_jsonl(diagnosis_path, diagnosis_rows)

    update_stage_attrition(run_root / "stage_attrition.json", diagnosis_rows, results)
    summary_path = summaries_dir / "evaluator_summary.json"
    status_counts: dict[str, int] = {}
    for row in results:
        key = f"{row['evaluator_name']}::{row['status']}"
        status_counts[key] = status_counts.get(key, 0) + 1
    write_json(
        summary_path,
        {
            "schema_version": MVP_SUMMARY_SCHEMA_VERSION,
            "schema_path": MVP_SUMMARY_SCHEMA_PATH,
            "run_id": samples[0]["run_id"] if samples else run_root.name,
            "method": samples[0]["method"] if samples else "DiffSBDD",
            "summary_type": "evaluator_wiring",
            "claim_boundary": "mvp_sanity_not_formal_prevalence",
            "counts": {
                "num_samples": len(samples),
                "num_tool_result_rows": len(results),
                "num_diagnosis_rows": len(diagnosis_rows),
                "tool_status_counts": status_counts,
                "evaluability_counts": {
                    status: sum(1 for row in diagnosis_rows if row["evaluability_status"] == status)
                    for status in sorted({row["evaluability_status"] for row in diagnosis_rows})
                },
            },
            "notes": "Evaluator wiring summary only. No formal labels or prevalence claims.",
        },
    )
    generation_summary = summaries_dir / "mvp_generation_summary.json"
    if generation_summary.exists():
        payload = read_json(generation_summary)
        payload.setdefault("schema_version", MVP_SUMMARY_SCHEMA_VERSION)
        payload.setdefault("schema_path", MVP_SUMMARY_SCHEMA_PATH)
        payload.setdefault("summary_type", "generation_capture")
        payload.setdefault("claim_boundary", "mvp_sanity_not_formal_prevalence")
        if "counts" not in payload:
            payload["counts"] = {
                "n_budget": payload.pop("n_budget", None),
                "n_final_sdf_records": payload.pop("n_final_sdf_records", None),
                "n_sample_metadata_rows": payload.pop("n_sample_metadata_rows", None),
                "exit_code": payload.pop("exit_code", None),
                "status": payload.pop("status", None),
            }
        payload.setdefault("notes", "Generation/output-capture summary only. No formal labels or prevalence claims.")
        write_json(generation_summary, payload)
    update_output_manifest(run_root / "output_manifest.json", [tool_results_path, diagnosis_path, summary_path, evaluator_input_path])
    print(json.dumps({"run_root": str(run_root), "tool_result_rows": len(results), "diagnosis_rows": len(diagnosis_rows)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
