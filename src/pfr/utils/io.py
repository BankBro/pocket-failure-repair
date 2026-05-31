"""Shared helpers for lightweight smoke scripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import yaml


def load_yaml(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{config_path} must contain a YAML mapping")
    return data


def ensure_parent(path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    input_path = Path(path)
    if not input_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{input_path}:{line_number} must contain a JSON object")
            rows.append(row)
    return rows


def write_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> Path:
    output_path = ensure_parent(path)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return output_path


def write_json(path: str | Path, data: Any) -> Path:
    output_path = ensure_parent(path)
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return output_path
