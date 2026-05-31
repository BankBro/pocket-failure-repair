#!/usr/bin/env python3
"""Evaluate placeholder smoke baselines with a shared metrics schema."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from pfr.utils.io import ensure_parent, load_yaml, read_jsonl, write_json


def success_from_feedback(row: dict[str, Any]) -> bool:
    geometry = row.get("geometry", {})
    if geometry.get("editable_region_validity") is False:
        return False
    if geometry.get("clash_count", 0) not in (None, 0):
        return False
    if float(geometry.get("anchor_distance_error") or 0.0) > 1.0:
        return False
    return True


def summarize_baseline(name: str, feedback_rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(feedback_rows)
    successes = sum(success_from_feedback(row) for row in feedback_rows)
    success_rate = successes / total if total else None
    return {
        "baseline": name,
        "num_candidates": total,
        "same_budget_success_rate": success_rate,
        "scaffold_preservation": None,
        "editable_validity": None,
        "anchor_validity": None,
        "clash_count": None,
        "posebusters_pass": None,
        "plip_interaction_recovery": None,
        "vina_delta": None,
        "qed": None,
        "sa": None,
        "logp": None,
        "rotatable_bonds": None,
        "source": "smoke_placeholder",
    }


def write_csv(path: str | Path, rows: list[dict[str, Any]]) -> Path:
    output_path = ensure_parent(path)
    fieldnames = list(rows[0].keys()) if rows else ["baseline", "num_candidates", "same_budget_success_rate"]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_yaml(args.config)
    feedback_path = config["input"]["feedback_path"]
    metrics_path = config["output"]["metrics_path"]
    table_path = config["output"]["table_path"]
    baselines = list(config.get("baselines", []))
    feedback_rows = read_jsonl(feedback_path)
    rows = [summarize_baseline(name, feedback_rows) for name in baselines]

    write_json(
        metrics_path,
        {
            "name": config.get("name"),
            "seed": config.get("seed"),
            "num_feedback_records": len(feedback_rows),
            "metrics": rows,
            "notes": "Placeholder smoke metrics; replace with chemistry-aware metrics after RDKit data path is available.",
        },
    )
    write_csv(table_path, rows)
    print(f"Read {len(feedback_rows)} feedback records from {feedback_path}")
    print(f"Wrote metrics to {metrics_path}")
    print(f"Wrote table to {table_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
