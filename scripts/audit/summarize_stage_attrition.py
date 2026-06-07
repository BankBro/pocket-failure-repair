#!/usr/bin/env python3
"""Summarize stage-wise attrition from third-party audit sample metadata.

This is a lightweight MVP utility. It only counts metadata rows and quality flags;
it does not assign formal failure labels or near-miss eligibility. Formal labels
must come from a frozen diagnosis protocol.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


STAGE_ATTRITION_SCHEMA_VERSION = "stage_attrition_v0_1"
STAGE_ATTRITION_SCHEMA_PATH = "schemas/third_party_audit/attrition/stage_attrition_v0_1.json"


def read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def summarize_group(rows: list[dict[str, Any]], run_metadata: dict[str, Any]) -> dict[str, Any]:
    first = rows[0] if rows else {}
    quality_missing = sum(1 for row in rows if row.get("quality_flags", {}).get("missing_final_output"))
    pipeline_fail = sum(1 for row in rows if row.get("quality_flags", {}).get("pipeline_failure"))
    final_rows = [row for row in rows if row.get("stage") == "final" or row.get("sample_role") == "final_output"]
    raw_rows = [row for row in rows if row.get("stage") == "raw" or row.get("sample_role") == "generation_attempt"]
    molecule_rows = [row for row in rows if row.get("molecule_path")]
    original_failed = [row for row in rows if row.get("sample_role") == "original_failed_sample" or row.get("original_status", {}).get("status") == "failed"]
    return {
        "method": first.get("method") or run_metadata.get("method"),
        "run_id": first.get("run_id") or run_metadata.get("run_id"),
        "seed": run_metadata.get("seed"),
        "dataset_view_id": first.get("dataset_view_id") or run_metadata.get("dataset_view_id"),
        "complex_id": first.get("complex_id"),
        "pocket_id": first.get("pocket_id"),
        "N_budget": run_metadata.get("sampling_budget"),
        "N_raw_attempt_metadata": len(raw_rows),
        "N_raw_captured": len([row for row in raw_rows if row.get("molecule_path") or row.get("raw_sha256")]),
        "N_original_failed_samples": len(original_failed),
        "N_parse_fail": None,
        "N_parsed": None,
        "N_rdkit_invalid": None,
        "N_rdkit_valid": None,
        "N_anchor_fail": None,
        "N_anchor_preserved": None,
        "N_docking_attempted": None,
        "N_docking_failed": None,
        "N_pose_available": len([row for row in rows if row.get("pose_path")]),
        "N_not_evaluable": quality_missing + pipeline_fail,
        "N_evaluable": len(molecule_rows),
        "N_rejected": len([row for row in rows if row.get("stage") == "rejected" or row.get("sample_role") == "rejected_candidate"]),
        "N_selected": len([row for row in rows if row.get("stage") == "selected" or row.get("sample_role") == "selected_candidate"]),
        "N_final": len(final_rows),
        "N_repair_eligible": None,
        "notes": "metadata-only attrition; no formal labels assigned",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-metadata", required=True)
    parser.add_argument("--samples", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    run_metadata = read_json(args.run_metadata)
    rows = read_jsonl(args.samples)
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            row.get("method") or run_metadata.get("method"),
            row.get("run_id") or run_metadata.get("run_id"),
            row.get("dataset_view_id") or run_metadata.get("dataset_view_id"),
            row.get("complex_id"),
        )
        grouped[key].append(row)
    attrition_rows = [summarize_group(group, run_metadata) for group in grouped.values()]
    payload = {
        "schema_version": STAGE_ATTRITION_SCHEMA_VERSION,
        "schema_path": STAGE_ATTRITION_SCHEMA_PATH,
        "summary_mode": "metadata_only_no_formal_labels",
        "method": run_metadata.get("method"),
        "run_id": run_metadata.get("run_id"),
        "dataset_view_id": run_metadata.get("dataset_view_id"),
        "denominator_policy_version": "pfr_failure_statistics_v0_1_draft",
        "rows": attrition_rows,
    }
    write_json(args.output, payload)
    print(json.dumps({"output": args.output, "rows": len(attrition_rows)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
