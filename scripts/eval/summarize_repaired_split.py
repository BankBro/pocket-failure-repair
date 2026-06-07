#!/usr/bin/env python3
"""Summarize repaired-molecule metrics by a prepared complex split."""

from __future__ import annotations

import argparse
import csv
import json
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


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def summarize_subset(rows: list[dict[str, Any]], split_name: str, complex_ids: list[str]) -> dict[str, Any]:
    allowed = set(complex_ids)
    subset = [row for row in rows if row.get("complex_id") in allowed]
    return {
        "split": split_name,
        "complex_ids": complex_ids,
        "num_complexes": len(complex_ids),
        "num_repaired_records": len(subset),
        "metrics": summarize_repaired_metrics(subset),
    }


def write_csv(path: str | Path, splits: list[dict[str, Any]]) -> Path:
    output_path = ensure_parent(path)
    rows: list[dict[str, Any]] = []
    for split in splits:
        for metric in split["metrics"]:
            row = {
                "split": split["split"],
                "num_complexes": split["num_complexes"],
                "num_repaired_records": split["num_repaired_records"],
            }
            row.update(metric)
            rows.append(row)
    fieldnames = sorted({key for row in rows for key in row}) if rows else ["split", "baseline"]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluated", default="outputs/20260601-02-smoke-plus-expansion-and-variants/processed/evaluated_repaired_smoke_plus.jsonl")
    parser.add_argument("--split", default="data/datasets/rgroup_smoke_plus/splits/rgroup_smoke_plus_split_v1.json")
    parser.add_argument("--metrics-path", default="outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus_split.json")
    parser.add_argument("--table-path", default="outputs/20260601-02-smoke-plus-expansion-and-variants/tables/repaired_smoke_plus_split.csv")
    args = parser.parse_args()

    rows = read_jsonl(args.evaluated)
    split = load_json(args.split)
    split_summaries = [
        summarize_subset(rows, "train", list(split.get("train", []))),
        summarize_subset(rows, "validation", list(split.get("validation", []))),
        summarize_subset(rows, "test", list(split.get("test", []))),
    ]
    summary = {
        "name": "repaired_smoke_plus_split",
        "evaluated": args.evaluated,
        "split_path": args.split,
        "split_seed": split.get("seed"),
        "splits": split_summaries,
        "notes": "Deterministic complex-level smoke-plus split summary. This is larger than the original 3-complex smoke set, but remains a small public smoke benchmark with fallback proxy metrics.",
    }
    write_json(args.metrics_path, summary)
    write_csv(args.table_path, split_summaries)
    print(f"Read {len(rows)} evaluated repaired records")
    print(f"Wrote split metrics to {args.metrics_path}")
    print(f"Wrote split table to {args.table_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
