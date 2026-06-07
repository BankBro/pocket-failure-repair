#!/usr/bin/env python3
"""Run PoseBusters for one repaired record and write one JSON result."""

from __future__ import annotations

import argparse
import json
import signal
import traceback
from pathlib import Path
from typing import Any


class Timeout:
    def __init__(self, seconds: int) -> None:
        self.seconds = seconds
        self.previous: Any = None

    def __enter__(self) -> None:
        self.previous = signal.signal(signal.SIGALRM, self._handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, exc_type: Any, exc: Any, traceback_obj: Any) -> None:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, self.previous)

    def _handle_timeout(self, signum: int, frame: Any) -> None:
        raise TimeoutError(f"timed out after {self.seconds}s")


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


def write_json(path: str | Path, data: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def base_result(row: dict[str, Any] | None, index: int) -> dict[str, Any]:
    row = row or {}
    return {
        "input_index": index,
        "repair_id": row.get("repair_id"),
        "candidate_id": row.get("candidate_id"),
        "complex_id": row.get("complex_id"),
        "baseline": row.get("baseline"),
        "failure_type": row.get("failure_type"),
        "repaired_ligand_path": row.get("repaired_ligand_path"),
        "source": "official_posebusters_single_record",
    }


def evaluate(row: dict[str, Any], index: int, timeout: int) -> dict[str, Any]:
    result = base_result(row, index)
    try:
        from posebusters import PoseBusters
    except Exception as exc:
        result.update(
            {
                "posebusters_available": False,
                "posebusters_error": "posebusters_import_failed",
                "posebusters_exception": repr(exc),
                "posebusters_traceback_head": traceback.format_exc()[:2000],
            }
        )
        return result
    try:
        with Timeout(timeout):
            buster = PoseBusters(config="redock", max_workers=0)
            table = buster.bust(
                row.get("repaired_ligand_path"),
                mol_true=row.get("reference_ligand_path"),
                mol_cond=row.get("protein_path"),
                full_report=True,
            )
        record = table.iloc[0].to_dict() if len(table) else {}
        bool_checks = {key: bool(value) for key, value in record.items() if isinstance(value, bool)}
        bool_values = list(bool_checks.values())
        result.update(
            {
                "posebusters_available": True,
                "posebusters_full_pass": all(bool_values) if bool_values else None,
                "posebusters_num_checks": len(bool_values),
                "posebusters_num_passed": sum(bool_values),
                "posebusters_failed_checks": [key for key, value in bool_checks.items() if not value],
                "posebusters_passed_checks": [key for key, value in bool_checks.items() if value],
                "posebusters_bool_checks": bool_checks,
                "posebusters_columns": list(record.keys()),
            }
        )
    except Exception as exc:
        result.update(
            {
                "posebusters_available": True,
                "posebusters_error": str(exc) or exc.__class__.__name__,
                "posebusters_exception": repr(exc),
                "posebusters_traceback_head": traceback.format_exc()[:2000],
            }
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repaired-candidates", required=True)
    parser.add_argument("--index", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=int, default=45)
    args = parser.parse_args()
    try:
        rows = read_jsonl(args.repaired_candidates)
    except Exception as exc:
        write_json(
            args.output,
            {
                **base_result(None, args.index),
                "posebusters_available": None,
                "posebusters_error": "input_read_failed",
                "posebusters_exception": repr(exc),
                "posebusters_traceback_head": traceback.format_exc()[:2000],
            },
        )
        return 1
    if args.index < 0 or args.index >= len(rows):
        write_json(
            args.output,
            {
                **base_result(None, args.index),
                "posebusters_available": None,
                "posebusters_error": "input_index_out_of_range",
                "num_input_rows": len(rows),
            },
        )
        return 1
    result = evaluate(rows[args.index], args.index, args.timeout)
    write_json(args.output, result)
    return 0 if not result.get("posebusters_error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
