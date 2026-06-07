#!/usr/bin/env python3
"""Summarize PoseBusters checks into task-relevant submetrics."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


CHECK_GROUPS = {
    "loading_and_sanitization": {
        "mol_pred_loaded",
        "mol_true_loaded",
        "mol_cond_loaded",
        "sanitization",
        "inchi_convertible",
        "all_atoms_connected",
        "no_radicals",
        "passes_valence_checks",
        "passes_kekulization",
        "no_radicals_before_sanitization",
    },
    "reference_consistency": {
        "molecular_formula",
        "molecular_bonds",
        "double_bond_stereochemistry",
        "tetrahedral_chirality",
        "inchi_crystal_valid",
        "inchi_docked_valid",
        "inchi_overall",
        "hydrogens",
        "net_charge",
        "protons",
        "stereo_sp3",
        "stereo_sp3_inverted",
        "stereo_type",
        "stereochemistry_preserved",
    },
    "ligand_geometry": {
        "bond_lengths",
        "bond_angles",
        "internal_steric_clash",
        "aromatic_ring_flatness",
        "non-aromatic_ring_non-flatness",
        "double_bond_flatness",
        "internal_energy",
    },
    "pocket_geometry": {
        "protein-ligand_maximum_distance",
        "minimum_distance_to_protein",
        "minimum_distance_to_organic_cofactors",
        "minimum_distance_to_inorganic_cofactors",
        "minimum_distance_to_waters",
        "volume_overlap_with_protein",
        "volume_overlap_with_organic_cofactors",
        "volume_overlap_with_inorganic_cofactors",
        "volume_overlap_with_waters",
    },
    "redock_rmsd": {"rmsd_≤_2å"},
}


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


def group_rate(checks: dict[str, bool], names: set[str]) -> float | None:
    values = [checks[name] for name in names if name in checks]
    if not values:
        return None
    return sum(values) / len(values)


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row.get("baseline", "unknown")), str(row.get("failure_type", "unknown")))].append(row)
    output: list[dict[str, Any]] = []
    for (baseline, failure_type), subset in sorted(grouped.items()):
        judged = [row for row in subset if isinstance(row.get("posebusters_bool_checks"), dict)]
        summary: dict[str, Any] = {
            "baseline": baseline,
            "failure_type": failure_type,
            "num_records": len(subset),
            "num_judged": len(judged),
            "timeout_or_error_count": sum(1 for row in subset if row.get("posebusters_error")),
            "full_pass_rate": _mean([row.get("posebusters_full_pass") for row in judged]),
        }
        for group_name, checks in CHECK_GROUPS.items():
            summary[f"{group_name}_pass_rate"] = _mean(
                [group_rate(row.get("posebusters_bool_checks", {}), checks) for row in judged]
            )
            summary[f"{group_name}_all_pass_rate"] = _mean(
                [all(row.get("posebusters_bool_checks", {}).get(name, True) for name in checks if name in row.get("posebusters_bool_checks", {})) for row in judged]
            )
        output.append(summary)
    return output


def _mean(values: list[Any]) -> float | None:
    numeric = [float(value) for value in values if value is not None]
    if not numeric:
        return None
    return sum(numeric) / len(numeric)


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--name", default="posebusters_submetrics")
    args = parser.parse_args()

    rows = read_jsonl(args.input)
    metrics = summarize(rows)
    write_json(
        args.output_json,
        {
            "name": args.name,
            "input": args.input,
            "num_records": len(rows),
            "metrics": metrics,
            "notes": "PoseBusters checks grouped into task-relevant submetrics. Full pass can be too strict for local editing because reference-consistency checks may fail by design.",
        },
    )
    write_csv(args.output_csv, metrics)
    print(f"Read {len(rows)} PoseBusters records")
    print(f"Wrote {len(metrics)} grouped PoseBusters submetrics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
