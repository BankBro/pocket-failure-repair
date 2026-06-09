"""Helpers for writing schema-covered JSON and JSONL records."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class SchemaRef:
    schema_version: str
    schema_path: str
    schema_file: Path
    schema: dict[str, Any]


def _ensure_object(payload: Any, *, label: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object")
    return payload


def _schema_file(schema_path: str | Path, *, root: Path = ROOT) -> Path:
    path = Path(schema_path)
    return path if path.is_absolute() else root / path


def load_schema_ref(schema_path: str | Path, *, root: Path = ROOT) -> SchemaRef:
    """Load schema refs from JSON Schema const fields."""
    schema_file = _schema_file(schema_path, root=root)
    if not schema_file.exists():
        raise ValueError(f"schema file does not exist: {schema_file}")
    schema = _ensure_object(json.loads(schema_file.read_text(encoding="utf-8")), label=str(schema_file))
    properties = _ensure_object(schema.get("properties"), label=f"{schema_file}:properties")
    version_spec = _ensure_object(properties.get("schema_version"), label=f"{schema_file}:schema_version")
    path_spec = _ensure_object(properties.get("schema_path"), label=f"{schema_file}:schema_path")
    schema_version = version_spec.get("const")
    schema_path_const = path_spec.get("const")
    if not isinstance(schema_version, str) or not schema_version:
        raise ValueError(f"{schema_file} must define properties.schema_version.const")
    if not isinstance(schema_path_const, str) or not schema_path_const:
        raise ValueError(f"{schema_file} must define properties.schema_path.const")
    try:
        actual_path = schema_file.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"schema file is not under root {root}: {schema_file}") from exc
    if schema_path_const != actual_path:
        raise ValueError(
            f"{schema_file} schema_path const {schema_path_const!r} does not match {actual_path!r}"
        )
    return SchemaRef(
        schema_version=schema_version,
        schema_path=schema_path_const,
        schema_file=schema_file,
        schema=schema,
    )


def validate_schema_ref_fields(payload: dict[str, Any], schema_ref: SchemaRef) -> None:
    expected = {
        "schema_version": schema_ref.schema_version,
        "schema_path": schema_ref.schema_path,
    }
    for key, expected_value in expected.items():
        actual_value = payload.get(key)
        if actual_value != expected_value:
            raise ValueError(f"{key} is {actual_value!r}; expected {expected_value!r}")


def validate_required_fields(payload: dict[str, Any], schema_ref: SchemaRef) -> None:
    required = schema_ref.schema.get("required") or []
    if not isinstance(required, list):
        raise ValueError(f"{schema_ref.schema_file} required must be a list")
    missing = [field for field in required if field not in payload]
    if missing:
        raise ValueError(f"missing required fields for {schema_ref.schema_path}: {', '.join(missing)}")


def validate_payload(payload: dict[str, Any], schema_ref: SchemaRef, *, validate: str = "light") -> None:
    if validate == "none":
        return
    if validate != "light":
        raise ValueError(f"unsupported schema validation mode: {validate!r}")
    validate_schema_ref_fields(payload, schema_ref)
    validate_required_fields(payload, schema_ref)


def with_schema_ref(
    payload: dict[str, Any],
    schema_path: str | Path,
    *,
    overwrite: bool = False,
    root: Path = ROOT,
) -> dict[str, Any]:
    """Return a shallow copy of payload with schema refs from the schema const fields."""
    schema_ref = load_schema_ref(schema_path, root=root)
    updated = dict(payload)
    for key, expected_value in {
        "schema_version": schema_ref.schema_version,
        "schema_path": schema_ref.schema_path,
    }.items():
        existing_value = updated.get(key)
        if existing_value is not None and existing_value != expected_value and not overwrite:
            raise ValueError(f"{key} already set to {existing_value!r}; expected {expected_value!r}")
        updated[key] = expected_value
    return updated


def write_json_with_schema(
    path: str | Path,
    payload: dict[str, Any],
    schema_path: str | Path,
    *,
    validate: str = "light",
    root: Path = ROOT,
) -> Path:
    schema_ref = load_schema_ref(schema_path, root=root)
    output_payload = with_schema_ref(payload, schema_ref.schema_path, root=root)
    validate_payload(output_payload, schema_ref, validate=validate)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path


def write_jsonl_with_schema(
    path: str | Path,
    rows: Iterable[dict[str, Any]],
    schema_path: str | Path,
    *,
    validate: str = "light",
    root: Path = ROOT,
) -> Path:
    schema_ref = load_schema_ref(schema_path, root=root)
    output_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        row = _ensure_object(row, label=f"{path}:row{index}")
        output_row = with_schema_ref(row, schema_ref.schema_path, root=root)
        validate_payload(output_row, schema_ref, validate=validate)
        output_rows.append(output_row)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in output_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return output_path
