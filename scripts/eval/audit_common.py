#!/usr/bin/env python3
"""Shared helpers for third-party audit evaluator scripts."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pfr.utils.schema_io import (  # noqa: E402
    SchemaRef,
    load_schema_ref,
    validate_required_fields,
    validate_schema_ref_fields,
    with_schema_ref,
    write_json_with_schema,
    write_jsonl_with_schema,
)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number} must contain a JSON object")
            rows.append(row)
    return rows


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def append_jsonl(path: str | Path, row: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def sha256_file(path: str | Path) -> str | None:
    input_path = Path(path)
    if not input_path.exists() or not input_path.is_file():
        return None
    digest = hashlib.sha256()
    with input_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_with_prefix(path: str | Path) -> str | None:
    digest = sha256_file(path)
    return f"sha256:{digest}" if digest else None


def load_yaml(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a YAML object")
    return payload


def normalized_config_hash(path: str | Path) -> str:
    input_path = Path(path)
    payload = yaml.safe_load(input_path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        data = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    else:
        data = input_path.read_bytes()
    return "sha256:" + hashlib.sha256(data).hexdigest()


def relpath(path: str | Path, root: Path = ROOT) -> str:
    input_path = Path(path)
    try:
        return input_path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(input_path)


def ensure_abs(path: str | Path) -> Path:
    input_path = Path(path)
    return input_path if input_path.is_absolute() else (ROOT / input_path)


THIRD_PARTY_AUDIT_METADATA_SCHEMAS: dict[str, str] = {
    "run_metadata": "schemas/third_party_audit/run/run_metadata_v0_1.json",
    "output_manifest": "schemas/third_party_audit/run/output_manifest_v0_1.json",
    "sample_metadata": "schemas/third_party_audit/samples/failure_sample_metadata_v0_1.json",
    "stage_attrition": "schemas/third_party_audit/attrition/stage_attrition_v0_1.json",
    "receptor_prep_record": "schemas/third_party_audit/receptor/receptor_prep_record_v0_1.json",
    "receptor_prep_index": "schemas/third_party_audit/receptor/receptor_prep_index_v0_1.json",
    "evaluator_input": "schemas/third_party_audit/diagnosis/evaluator_input_v0_1.json",
    "label": "schemas/third_party_audit/diagnosis/label_v0_1.json",
    "evaluator_tool_result": "schemas/third_party_audit/diagnosis/evaluator_tool_result_v0_1.json",
    "posebusters_raw_result": "schemas/third_party_audit/diagnosis/posebusters_raw_result_v0_1.json",
    "diagnosis_sanity": "schemas/third_party_audit/diagnosis/diagnosis_sanity_v0_1.json",
    "mvp_sanity_summary": "schemas/third_party_audit/diagnosis/mvp_sanity_summary_v0_1.json",
    "label_summary": "schemas/third_party_audit/diagnosis/label_summary_v0_1.json",
    "prevalence_summary": "schemas/third_party_audit/diagnosis/prevalence_summary_v0_1.json",
    "analysis_frozen_gate_result": "schemas/third_party_audit/diagnosis/analysis_frozen_gate_result_v0_1.json",
    "method_resource_check": "schemas/third_party_audit/resources/method_resource_check_v0_1.json",
    "blocker_log": "schemas/third_party_audit/resources/blocker_log_v0_1.json",
    "official_protocol_checklist": "schemas/third_party_audit/resources/official_protocol_checklist_v0_1.json",
    "preprocess_metadata": "schemas/third_party_audit/resources/preprocess_metadata_v0_1.json",
}


def _existing_files(paths: list[Path]) -> list[Path]:
    return sorted({path for path in paths if path.exists() and path.is_file()})


def _metadata_schemas_for_run(root: Path, existing: dict[str, Any]) -> dict[str, str]:
    metadata_schemas = {
        key: value
        for key, value in existing.items()
        if (
            isinstance(key, str)
            and isinstance(value, str)
            and THIRD_PARTY_AUDIT_METADATA_SCHEMAS.get(key) == value
        )
    }
    presence_checks = {
        "run_metadata": root / "run_metadata.json",
        "output_manifest": root / "output_manifest.json",
        "sample_metadata": root / "samples.jsonl",
        "stage_attrition": root / "stage_attrition.json",
        "evaluator_input": root / "evaluator" / "evaluator_input.jsonl",
        "evaluator_tool_result": root / "evaluator" / "evaluator_tool_results.jsonl",
        "label": root / "labels.jsonl",
        "label_summary": root / "summaries" / "label_summary.json",
        "prevalence_summary": root / "summaries" / "prevalence_summary.json",
        "analysis_frozen_gate_result": root / "summaries" / "analysis_frozen_gate_result.json",
        "mvp_sanity_summary": root / "summaries" / "frozen_evaluator_summary.json",
    }
    for key, path in presence_checks.items():
        if path.exists():
            metadata_schemas[key] = THIRD_PARTY_AUDIT_METADATA_SCHEMAS[key]
    if any((root / "processed" / "receptors").glob("*.json")):
        metadata_schemas["receptor_prep_record"] = THIRD_PARTY_AUDIT_METADATA_SCHEMAS["receptor_prep_record"]
    if any((root / "evaluator" / "raw_tool_outputs").glob("posebusters_*.json")):
        metadata_schemas["posebusters_raw_result"] = THIRD_PARTY_AUDIT_METADATA_SCHEMAS["posebusters_raw_result"]
    if (root / "receptor_prep_index.json").exists():
        metadata_schemas["receptor_prep_index"] = THIRD_PARTY_AUDIT_METADATA_SCHEMAS["receptor_prep_index"]
    return dict(sorted(metadata_schemas.items()))


def finalize_output_manifest(run_root: str | Path) -> dict[str, Any]:
    """Refresh output_manifest.json after all run artifacts have been written."""
    root = Path(run_root)
    manifest_path = root / "output_manifest.json"
    manifest = read_json(manifest_path)
    processed_outputs = _existing_files(list((root / "processed").rglob("*")))
    log_outputs = _existing_files(list((root / "logs").rglob("*")))
    manifest_outputs = _existing_files(list((root / "manifests").rglob("*")))
    evaluator_outputs = _existing_files(
        [
            *list((root / "evaluator").rglob("*")),
            root / "labels.jsonl",
            *list((root / "summaries").rglob("*")),
        ]
    )
    core_outputs = _existing_files(
        [
            root / "run_metadata.json",
            root / "samples.jsonl",
            root / "stage_attrition.json",
        ]
    )
    captured_outputs = [Path(path) for path in manifest.get("captured_outputs", [])]
    captured_outputs = _existing_files(captured_outputs)
    all_paths = _existing_files(
        [*core_outputs, *captured_outputs, *processed_outputs, *log_outputs, *manifest_outputs, *evaluator_outputs]
    )
    manifest.update(
        {
            "metadata_schemas": _metadata_schemas_for_run(root, manifest.get("metadata_schemas", {})),
            "captured_outputs": [str(path) for path in captured_outputs],
            "processed_outputs": [str(path) for path in processed_outputs],
            "logs": [str(path) for path in log_outputs],
            "manifests": [str(path) for path in manifest_outputs],
            "evaluator_outputs": [str(path) for path in evaluator_outputs],
            "sha256": {str(path): sha256_file(path) for path in all_paths},
            "n_output_artifacts": len(all_paths),
        }
    )
    manifest = with_schema_ref(manifest, THIRD_PARTY_AUDIT_METADATA_SCHEMAS["output_manifest"])
    write_json(manifest_path, manifest)
    return manifest
