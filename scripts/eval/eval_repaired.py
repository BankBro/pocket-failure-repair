#!/usr/bin/env python3
"""Evaluate repaired molecule outputs with RDKit and geometry metrics."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from pfr.evaluation.repaired import evaluate_repaired_record, summarize_repaired_metrics
from pfr.utils.io import ensure_parent, load_yaml, read_jsonl, write_json, write_jsonl


def write_csv(path: str | Path, rows: list[dict[str, Any]]) -> Path:
    output_path = ensure_parent(path)
    fieldnames = list(rows[0].keys()) if rows else ["baseline", "num_repaired", "repaired_success_rate"]
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
    repaired_rows = read_jsonl(config["input"]["repaired_candidates_path"])
    evaluated_rows = [evaluate_repaired_record(row) for row in repaired_rows]
    summaries = summarize_repaired_metrics(evaluated_rows)

    write_jsonl(config["output"]["evaluated_repaired_path"], evaluated_rows)
    write_json(
        config["output"]["metrics_path"],
        {
            "name": config.get("name"),
            "seed": config.get("seed"),
            "num_repaired_records": len(evaluated_rows),
            "metrics": summaries,
            "notes": "Repaired-molecule RDKit/geometry smoke evaluation; includes deterministic/rule baselines, oracle sanity checks, and lightweight oracle-free learned geometry policy where configured. Fallback proxy metrics are not official PoseBusters/PLIP/Vina results.",
        },
    )
    write_csv(config["output"]["table_path"], summaries)
    print(f"Read {len(repaired_rows)} repaired candidate records")
    print(f"Wrote evaluated repaired records to {config['output']['evaluated_repaired_path']}")
    print(f"Wrote repaired metrics to {config['output']['metrics_path']}")
    print(f"Wrote repaired table to {config['output']['table_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
