#!/usr/bin/env python3
"""Summarize official external tool outputs by baseline and failure type."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if isinstance(row, dict):
                rows.append(row)
    return rows


def write_json(path: str | Path, data: Any) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: str | Path, rows: list[dict[str, Any]]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else ["baseline", "failure_type"]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def mean(values: list[float | int | None]) -> float | None:
    numeric = [float(value) for value in values if value is not None]
    if not numeric:
        return None
    return sum(numeric) / len(numeric)


def fraction(values: list[bool | None]) -> float | None:
    present = [value for value in values if value is not None]
    if not present:
        return None
    return sum(present) / len(present)


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (str(row.get("baseline", "unknown")), str(row.get("failure_type", "unknown")))
        grouped[key].append(row)
    summaries: list[dict[str, Any]] = []
    for (baseline, failure_type), subset in sorted(grouped.items()):
        summaries.append(
            {
                "baseline": baseline,
                "failure_type": failure_type,
                "num_records": len(subset),
                "plip_available_rate": fraction([row.get("plip_available") for row in subset]),
                "plip_error_count": sum(1 for row in subset if row.get("plip_error")),
                "mean_plip_interaction_count": mean([row.get("plip_interaction_count") for row in subset]),
                "mean_plip_reference_interaction_count": mean([row.get("plip_reference_interaction_count") for row in subset]),
                "mean_plip_failed_interaction_count": mean([row.get("plip_failed_interaction_count") for row in subset]),
                "mean_plip_repaired_interaction_count": mean([row.get("plip_repaired_interaction_count") for row in subset]),
                "mean_plip_interaction_recovery": mean([row.get("plip_interaction_recovery") for row in subset]),
                "mean_plip_failed_interaction_recovery": mean([row.get("plip_failed_interaction_recovery") for row in subset]),
                "mean_plip_interaction_recovery_gain": mean([row.get("plip_interaction_recovery_gain") for row in subset]),
                "mean_plip_interaction_similarity": mean([row.get("plip_interaction_similarity") for row in subset]),
                "mean_plip_failed_interaction_similarity": mean([row.get("plip_failed_interaction_similarity") for row in subset]),
                "mean_plip_interaction_similarity_gain": mean([row.get("plip_interaction_similarity_gain") for row in subset]),
                "vina_available_rate": fraction([row.get("vina_available") for row in subset]),
                "vina_error_count": sum(1 for row in subset if row.get("vina_error")),
                "mean_vina_score_only_energy": mean([row.get("vina_score_only_energy") for row in subset]),
                "source": "official_external_eval_by_failure_type",
            }
        )
    return summaries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--name", default="official_external_eval_by_failure_type")
    args = parser.parse_args()

    rows = read_jsonl(args.input)
    summaries = summarize(rows)
    write_json(
        args.output_json,
        {
            "name": args.name,
            "input": args.input,
            "num_records": len(rows),
            "metrics": summaries,
            "notes": "Official external-tool summary by baseline and failure_type. Vina values are score-only energies, not redocking success. PLIP values are interaction counts.",
        },
    )
    write_csv(args.output_csv, summaries)
    print(f"Read {len(rows)} official external eval records")
    print(f"Wrote {len(summaries)} grouped metrics")
    print(f"Wrote official by-failure JSON to {args.output_json}")
    print(f"Wrote official by-failure CSV to {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
