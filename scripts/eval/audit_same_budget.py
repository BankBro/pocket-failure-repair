#!/usr/bin/env python3
"""Audit record-level same-budget coverage for repaired-candidate evaluations."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

from pfr.utils.io import read_jsonl, write_json


def mean(values: list[float | int | bool | None]) -> float | None:
    numeric = [float(value) for value in values if value is not None]
    if not numeric:
        return None
    return sum(numeric) / len(numeric)


def fraction(values: list[bool | None]) -> float | None:
    present = [value for value in values if value is not None]
    if not present:
        return None
    return sum(1.0 for value in present if value) / len(present)


def read_inputs(paths: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        for row in read_jsonl(path):
            row = dict(row)
            row["audit_input_path"] = path
            rows.append(row)
    return rows


def candidate_key(row: dict[str, Any]) -> str:
    seed = row.get("seed")
    candidate_id = str(row.get("candidate_id", "unknown"))
    if seed is None:
        return candidate_id
    return f"seed={seed}::{candidate_id}"


def infer_seed_from_path(path: str) -> int | None:
    marker = "seed"
    name = Path(path).stem
    if marker not in name:
        return None
    suffix = name.rsplit(marker, 1)[-1].lstrip("_-.")
    digits = ""
    for char in suffix:
        if char.isdigit():
            digits += char
        else:
            break
    return int(digits) if digits else None


def attach_missing_seed(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        if row.get("seed") is None:
            row["seed"] = infer_seed_from_path(str(row.get("audit_input_path", "")))


def summarize(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    attach_missing_seed(rows)
    all_candidates = {candidate_key(row) for row in rows if row.get("candidate_id") is not None}
    by_baseline: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_baseline[str(row.get("baseline", "unknown"))].append(row)

    summaries: list[dict[str, Any]] = []
    expected_count = len(all_candidates)
    for baseline, subset in sorted(by_baseline.items()):
        counts_by_candidate: dict[str, int] = defaultdict(int)
        for row in subset:
            counts_by_candidate[candidate_key(row)] += 1
        covered = set(counts_by_candidate)
        missing = sorted(all_candidates - covered)
        duplicate_records = sum(max(0, count - 1) for count in counts_by_candidate.values())
        record_counts = list(counts_by_candidate.values())
        internal_budgets = [row.get("internal_candidate_budget") for row in subset]
        summaries.append(
            {
                "baseline": baseline,
                "num_records": len(subset),
                "unique_candidates": len(covered),
                "expected_candidates": expected_count,
                "coverage_rate": len(covered) / expected_count if expected_count else None,
                "missing_candidate_count": len(missing),
                "duplicate_candidate_records": duplicate_records,
                "records_per_candidate_min": min(record_counts) if record_counts else None,
                "records_per_candidate_max": max(record_counts) if record_counts else None,
                "records_per_candidate_mean": mean(record_counts),
                "record_level_same_budget_pass": len(missing) == 0 and duplicate_records == 0,
                "internal_candidate_budget_min": min([int(value) for value in internal_budgets if value is not None], default=None),
                "internal_candidate_budget_max": max([int(value) for value in internal_budgets if value is not None], default=None),
                "internal_candidate_budget_mean": mean(internal_budgets),
                "internal_budget_types": sorted({str(row.get("internal_budget_type")) for row in subset if row.get("internal_budget_type") is not None}),
                "internal_budget_available_rate": len([value for value in internal_budgets if value is not None]) / len(subset) if subset else None,
                "repaired_success_rate": fraction([row.get("repaired_success") for row in subset]),
                "repair_gain_success_rate": fraction([row.get("repair_gain_success") for row in subset]),
                "mean_contact_recovery_gain": mean([row.get("contact_recovery_gain") for row in subset]),
                "mean_contact_similarity_gain": mean([row.get("contact_fingerprint_similarity_gain") for row in subset]),
                "mean_anchor_error_reduction": mean([row.get("anchor_error_reduction") for row in subset]),
                "mean_clash_count_reduction": mean([row.get("clash_count_reduction") for row in subset]),
                "missing_candidate_examples": missing[:5],
                "source": "record_and_internal_budget_audit",
            }
        )

    pass_values = [row["record_level_same_budget_pass"] for row in summaries]
    available_internal = [row for row in summaries if row["internal_budget_available_rate"] == 1.0]
    all_internal_values = [
        row.get("internal_candidate_budget")
        for row in rows
        if row.get("internal_candidate_budget") is not None
    ]
    internal_value_set = {float(value) for value in all_internal_values}
    strict_equal = None
    if summaries:
        strict_equal = len(available_internal) == len(summaries) and len(internal_value_set) == 1
    audit = {
        "num_input_records": len(rows),
        "num_baselines": len(summaries),
        "expected_candidates": expected_count,
        "record_level_all_baselines_same_budget": bool(summaries) and all(pass_values),
        "record_level_same_budget_failures": [
            row["baseline"] for row in summaries if not row["record_level_same_budget_pass"]
        ],
        "internal_budget_metadata_available": len(available_internal) == len(summaries) and bool(summaries),
        "internal_candidate_budget_values": sorted(internal_value_set),
        "strict_internal_candidate_budget_equal": strict_equal,
        "notes": "Record-level audit verifies equal evaluated repaired records per failed candidate and baseline. Internal budget fields expose proposal/selection pool differences when repair records contain internal_candidate_budget.",
    }
    return summaries, audit


def write_csv(path: str | Path, rows: list[dict[str, Any]]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else ["baseline"]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True, help="Evaluated repaired JSONL path. Repeat for seeds.")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--name", default="same_budget_audit")
    args = parser.parse_args()

    rows = read_inputs(args.input)
    metrics, audit = summarize(rows)
    write_json(
        args.output_json,
        {
            "name": args.name,
            "inputs": args.input,
            "audit": audit,
            "metrics": metrics,
        },
    )
    write_csv(args.output_csv, metrics)
    print(f"Read {len(rows)} evaluated repaired records")
    print(f"Wrote same-budget audit JSON to {args.output_json}")
    print(f"Wrote same-budget audit CSV to {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
