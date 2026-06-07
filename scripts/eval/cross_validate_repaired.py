#!/usr/bin/env python3
"""Summarize repaired-molecule metrics by leave-one-complex smoke folds."""

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
    "scaffold_preservation",
    "anchor_validity",
    "editable_validity",
    "mean_clash_count",
    "mean_qed",
    "mean_logp",
    "mean_posebusters_like_pass",
    "mean_contact_fingerprint_similarity",
    "mean_contact_recovery",
    "mean_vina_like_proxy",
    "mean_ligand_efficiency_proxy",
    "mean_sa_fallback",
]


def mean(values: list[float | int | None]) -> float | None:
    numeric = [float(value) for value in values if value is not None]
    if not numeric:
        return None
    return sum(numeric) / len(numeric)


def summarize_fold(rows: list[dict[str, Any]], held_out_complex: str) -> dict[str, Any]:
    fold_rows = [row for row in rows if row.get("complex_id") == held_out_complex]
    return {
        "held_out_complex": held_out_complex,
        "num_repaired_records": len(fold_rows),
        "metrics": summarize_repaired_metrics(fold_rows),
    }


def aggregate_folds(folds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_baseline: dict[str, list[dict[str, Any]]] = {}
    for fold in folds:
        for row in fold["metrics"]:
            by_baseline.setdefault(str(row["baseline"]), []).append(row)
    aggregate: list[dict[str, Any]] = []
    for baseline, rows in sorted(by_baseline.items()):
        summary: dict[str, Any] = {
            "baseline": baseline,
            "num_folds": len(rows),
            "mean_num_repaired": mean([row.get("num_repaired") for row in rows]),
        }
        for key in METRIC_KEYS:
            summary[f"fold_mean_{key}"] = mean([row.get(key) for row in rows])
        aggregate.append(summary)
    return aggregate


def write_csv(path: str | Path, folds: list[dict[str, Any]], aggregate: list[dict[str, Any]]) -> Path:
    output_path = ensure_parent(path)
    rows: list[dict[str, Any]] = []
    for fold in folds:
        for metric in fold["metrics"]:
            row = {"scope": "fold", "held_out_complex": fold["held_out_complex"]}
            row.update(metric)
            rows.append(row)
    for metric in aggregate:
        row = {"scope": "aggregate", "held_out_complex": "mean_over_folds"}
        row.update(metric)
        rows.append(row)
    fieldnames = sorted({key for row in rows for key in row}) if rows else ["scope", "held_out_complex", "baseline"]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="outputs/20260601-01-smoke-repair-baselines/processed/evaluated_repaired_smoke.jsonl")
    parser.add_argument("--metrics-path", default="outputs/20260601-01-smoke-repair-baselines/metrics/repaired_smoke_leave_one_complex.json")
    parser.add_argument("--table-path", default="outputs/20260601-01-smoke-repair-baselines/tables/repaired_smoke_leave_one_complex.csv")
    args = parser.parse_args()

    rows = read_jsonl(args.input)
    complexes = sorted({str(row.get("complex_id")) for row in rows if row.get("complex_id")})
    folds = [summarize_fold(rows, complex_id) for complex_id in complexes]
    aggregate = aggregate_folds(folds)
    summary = {
        "name": "repaired_smoke_leave_one_complex",
        "input": args.input,
        "complexes": complexes,
        "num_folds": len(folds),
        "folds": folds,
        "aggregate_metrics": aggregate,
        "notes": "Smoke-level leave-one-complex reporting over already generated repaired molecules; this is a per-complex audit summary, not a larger independent split or official cross-validation benchmark.",
    }
    write_json(args.metrics_path, summary)
    write_csv(args.table_path, folds, aggregate)
    print(f"Read {len(rows)} evaluated repaired records")
    print(f"Wrote leave-one-complex metrics to {args.metrics_path}")
    print(f"Wrote leave-one-complex table to {args.table_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
