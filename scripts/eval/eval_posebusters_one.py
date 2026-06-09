#!/usr/bin/env python3
"""Run PoseBusters for one repaired record and write one JSON result."""

from __future__ import annotations

import argparse
import json
import math
import signal
import sys
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.eval.audit_common import load_schema_ref, with_schema_ref, write_json_with_schema  # noqa: E402

POSEBUSTERS_RAW_RESULT_SCHEMA_PATH = "schemas/third_party_audit/diagnosis/posebusters_raw_result_v0_1.json"
POSEBUSTERS_RAW_RESULT_SCHEMA_VERSION = load_schema_ref(POSEBUSTERS_RAW_RESULT_SCHEMA_PATH).schema_version


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


def json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, int) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        return float(value) if math.isfinite(value) else None
    item = getattr(value, "item", None)
    if callable(item):
        try:
            item_value = item()
        except Exception:
            item_value = None
        if item_value is not None and item_value is not value:
            return json_safe(item_value)
    if type(value).__name__ == "NAType":
        return None
    try:
        if value != value:
            return None
    except Exception:
        pass
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return [json_safe(item_value) for item_value in value]
    if isinstance(value, dict):
        return {str(key): json_safe(item_value) for key, item_value in value.items()}
    return str(value)


def unavailable_reasons(report_values: dict[str, Any], columns: list[str]) -> dict[str, str]:
    reasons: dict[str, str] = {}
    for column in columns:
        if column == "internal_energy" and "energy_ratio" in report_values and "ensemble_avg_energy" in report_values:
            reasons[column] = "energy_ratio_unavailable"
        else:
            reasons[column] = "non_boolean_value_unavailable"
    return reasons


def base_result(row: dict[str, Any] | None, index: int, config: str = "redock") -> dict[str, Any]:
    row = row or {}
    return with_schema_ref(
        {
            "input_index": index,
            "repair_id": row.get("repair_id"),
            "candidate_id": row.get("candidate_id"),
            "complex_id": row.get("complex_id"),
            "baseline": row.get("baseline"),
            "failure_type": row.get("failure_type"),
            "repaired_ligand_path": row.get("repaired_ligand_path"),
            "posebusters_config": config,
            "source": "official_posebusters_single_record",
        },
        POSEBUSTERS_RAW_RESULT_SCHEMA_PATH,
    )


def evaluate(row: dict[str, Any], index: int, timeout: int, config: str) -> dict[str, Any]:
    result = base_result(row, index, config)
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
            buster = PoseBusters(config=config, max_workers=0)
            table = buster.bust(
                row.get("repaired_ligand_path"),
                mol_true=row.get("reference_ligand_path"),
                mol_cond=row.get("protein_path"),
                full_report=True,
            )
        record = table.iloc[0].to_dict() if len(table) else {}
        report_values = {key: json_safe(value) for key, value in record.items()}
        bool_checks = {key: value for key, value in report_values.items() if isinstance(value, bool)}
        non_boolean_checks = {key: value for key, value in report_values.items() if not isinstance(value, bool)}
        unavailable_columns = [key for key, value in report_values.items() if value is None]
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
                "posebusters_report_values": report_values,
                "posebusters_non_boolean_checks": non_boolean_checks,
                "posebusters_unavailable_columns": unavailable_columns,
                "posebusters_unavailable_reasons": unavailable_reasons(report_values, unavailable_columns),
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
    parser.add_argument("--config", default="redock")
    args = parser.parse_args()
    try:
        rows = read_jsonl(args.repaired_candidates)
    except Exception as exc:
        write_json_with_schema(
            args.output,
            {
                **base_result(None, args.index, args.config),
                "posebusters_available": None,
                "posebusters_error": "input_read_failed",
                "posebusters_exception": repr(exc),
                "posebusters_traceback_head": traceback.format_exc()[:2000],
            },
            POSEBUSTERS_RAW_RESULT_SCHEMA_PATH,
        )
        return 1
    if args.index < 0 or args.index >= len(rows):
        write_json_with_schema(
            args.output,
            {
                **base_result(None, args.index, args.config),
                "posebusters_available": None,
                "posebusters_error": "input_index_out_of_range",
                "num_input_rows": len(rows),
            },
            POSEBUSTERS_RAW_RESULT_SCHEMA_PATH,
        )
        return 1
    result = evaluate(rows[args.index], args.index, args.timeout, args.config)
    write_json_with_schema(args.output, result, POSEBUSTERS_RAW_RESULT_SCHEMA_PATH)
    return 0 if not result.get("posebusters_error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
