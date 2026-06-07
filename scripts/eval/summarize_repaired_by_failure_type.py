#!/usr/bin/env python3
"""Summarize repaired-molecule metrics by failure type."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from pfr.evaluation.repaired import summarize_repaired_metrics
from pfr.utils.io import ensure_parent, read_jsonl, write_json


METRIC_KEYS = [
    "repaired_success_rate",
    "clash_free_rate",
    "anchor_validity",
    "editable_validity",
    "mean_clash_count",
    "mean_posebusters_like_pass",
    "mean_contact_fingerprint_similarity",
    "mean_contact_recovery",
    "mean_vina_like_proxy",
    "mean_ligand_efficiency_proxy",
]


def summarize_by_failure_type(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failure_types = sorted({str(row.get("failure_type")) for row in rows})
    summaries: list[dict[str, Any]] = []
    for failure_type in failure_types:
        subset = [row for row in rows if str(row.get("failure_type")) == failure_type]
        summaries.append(
            {
                "failure_type": failure_type,
                "num_repaired_records": len(subset),
                "metrics": summarize_repaired_metrics(subset),
            }
        )
    return summaries


def write_csv(path: str | Path, summaries: list[dict[str, Any]]) -> Path:
    output_path = ensure_parent(path)
    rows: list[dict[str, Any]] = []
    for summary in summaries:
        for metric in summary["metrics"]:
            row = {
                "failure_type": summary["failure_type"],
                "num_repaired_records": summary["num_repaired_records"],
            }
            row.update({key: metric.get(key) for key in ["baseline", *METRIC_KEYS]})
            rows.append(row)
    fieldnames = ["failure_type", "baseline", "num_repaired_records", *METRIC_KEYS]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluated", default="outputs/20260601-02-smoke-plus-expansion-and-variants/processed/evaluated_repaired_smoke_plus.jsonl")
    parser.add_argument("--metrics-path", default="outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus_by_failure_type.json")
    parser.add_argument("--table-path", default="outputs/20260601-02-smoke-plus-expansion-and-variants/tables/repaired_smoke_plus_by_failure_type.csv")
    args = parser.parse_args()

    rows = read_jsonl(args.evaluated)
    summaries = summarize_by_failure_type(rows)
    summary = {
        "name": "repaired_smoke_plus_by_failure_type",
        "evaluated": args.evaluated,
        "failure_types": summaries,
        "notes": "Failure-type split over repaired-molecule fallback proxy metrics; useful for diagnosing which failures are truly repaired versus easy no-op cases.",
    }
    write_json(args.metrics_path, summary)
    write_csv(args.table_path, summaries)
    print(f"Read {len(rows)} evaluated repaired records")
    print(f"Wrote failure-type metrics to {args.metrics_path}")
    print(f"Wrote failure-type table to {args.table_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
