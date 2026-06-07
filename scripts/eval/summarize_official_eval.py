#!/usr/bin/env python3
"""Summarize official external tool evaluation outputs by baseline."""

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
            if line:
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
    fieldnames = list(rows[0].keys()) if rows else ["baseline"]
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
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("baseline", "unknown"))].append(row)
    summaries: list[dict[str, Any]] = []
    for baseline, baseline_rows in sorted(grouped.items()):
        summaries.append(
            {
                "baseline": baseline,
                "num_records": len(baseline_rows),
                "plip_available_rate": fraction([row.get("plip_available") for row in baseline_rows]),
                "plip_error_count": sum(1 for row in baseline_rows if row.get("plip_error")),
                "mean_plip_interaction_count": mean([row.get("plip_interaction_count") for row in baseline_rows]),
                "mean_plip_reference_interaction_count": mean(
                    [row.get("plip_reference_interaction_count") for row in baseline_rows]
                ),
                "mean_plip_failed_interaction_count": mean([row.get("plip_failed_interaction_count") for row in baseline_rows]),
                "mean_plip_repaired_interaction_count": mean(
                    [row.get("plip_repaired_interaction_count") for row in baseline_rows]
                ),
                "mean_plip_interaction_recovery": mean([row.get("plip_interaction_recovery") for row in baseline_rows]),
                "mean_plip_failed_interaction_recovery": mean(
                    [row.get("plip_failed_interaction_recovery") for row in baseline_rows]
                ),
                "mean_plip_interaction_recovery_gain": mean(
                    [row.get("plip_interaction_recovery_gain") for row in baseline_rows]
                ),
                "mean_plip_interaction_similarity": mean([row.get("plip_interaction_similarity") for row in baseline_rows]),
                "mean_plip_failed_interaction_similarity": mean(
                    [row.get("plip_failed_interaction_similarity") for row in baseline_rows]
                ),
                "mean_plip_interaction_similarity_gain": mean(
                    [row.get("plip_interaction_similarity_gain") for row in baseline_rows]
                ),
                "vina_available_rate": fraction([row.get("vina_available") for row in baseline_rows]),
                "vina_error_count": sum(1 for row in baseline_rows if row.get("vina_error")),
                "mean_vina_score_only_energy": mean([row.get("vina_score_only_energy") for row in baseline_rows]),
                "mean_internal_candidate_budget": mean([row.get("internal_candidate_budget") for row in baseline_rows]),
                "internal_budget_types": sorted(
                    {str(row.get("internal_budget_type")) for row in baseline_rows if row.get("internal_budget_type") is not None}
                ),
                "posebusters_available_rate": fraction([row.get("posebusters_available") for row in baseline_rows]),
                "posebusters_error_count": sum(1 for row in baseline_rows if row.get("posebusters_error")),
                "posebusters_full_pass_rate": fraction([row.get("posebusters_full_pass") for row in baseline_rows]),
                "source": "official_external_eval_summary",
            }
        )
    return summaries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--name", default="official_external_eval_summary")
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
            "notes": "Official external-tool summary. Vina values are score-only energies, not redocking success. PLIP values are interaction counts from generated protein-ligand complex PDBs.",
        },
    )
    write_csv(args.output_csv, summaries)
    print(f"Read {len(rows)} official external eval records")
    print(f"Wrote official summary JSON to {args.output_json}")
    print(f"Wrote official summary CSV to {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
