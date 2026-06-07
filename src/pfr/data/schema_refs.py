"""Schema reference helpers for canonical dataset metadata."""

from __future__ import annotations

from typing import Any


DATA_SCHEMA_REFS: dict[str, dict[str, str]] = {
    "dataset_entry": {
        "schema_version": "dataset_entry_v0_1",
        "schema_path": "schemas/data/datasets/entries/dataset_entry_v0_1.json",
    },
    "dataset_split": {
        "schema_version": "dataset_split_v0_1",
        "schema_path": "schemas/data/datasets/splits/dataset_split_v0_1.json",
    },
    "dataset_view": {
        "schema_version": "dataset_view_v0_1",
        "schema_path": "schemas/data/datasets/views/dataset_view_v0_1.json",
    },
    "dataset_raw_manifest": {
        "schema_version": "dataset_raw_manifest_v0_1",
        "schema_path": "schemas/data/datasets/manifests/raw/dataset_raw_manifest_v0_1.json",
    },
    "dataset_entries_manifest": {
        "schema_version": "dataset_entries_manifest_v0_1",
        "schema_path": "schemas/data/datasets/manifests/entries/dataset_entries_manifest_v0_1.json",
    },
    "dataset_lineage_raw_to_entry": {
        "schema_version": "dataset_lineage_raw_to_entry_v0_1",
        "schema_path": "schemas/data/datasets/manifests/lineage/dataset_lineage_raw_to_entry_v0_1.json",
    },
    "dataset_lineage_entry_to_raw": {
        "schema_version": "dataset_lineage_entry_to_raw_v0_1",
        "schema_path": "schemas/data/datasets/manifests/lineage/dataset_lineage_entry_to_raw_v0_1.json",
    },
    "dataset_catalog": {
        "schema_version": "dataset_catalog_v0_1",
        "schema_path": "schemas/data/catalog/dataset_catalog_v0_1.json",
    },
    "dataset_layout_migration": {
        "schema_version": "dataset_layout_migration_v0_1",
        "schema_path": "schemas/data/catalog/dataset_layout_migration_v0_1.json",
    },
    "dataset_raw_reconciliation": {
        "schema_version": "dataset_raw_reconciliation_v0_1",
        "schema_path": "schemas/data/catalog/dataset_raw_reconciliation_v0_1.json",
    },
}


def data_schema_ref(schema_key: str) -> dict[str, str]:
    """Return a copy of the schema reference for a canonical data metadata type."""
    try:
        return dict(DATA_SCHEMA_REFS[schema_key])
    except KeyError as exc:
        known = ", ".join(sorted(DATA_SCHEMA_REFS))
        raise KeyError(f"unknown data schema key {schema_key!r}; known keys: {known}") from exc


def with_data_schema_ref(record: dict[str, Any], schema_key: str) -> dict[str, Any]:
    """Return a shallow copy of record with the expected data schema reference."""
    schema_ref = data_schema_ref(schema_key)
    updated = dict(record)
    for key, expected_value in schema_ref.items():
        existing_value = updated.get(key)
        if existing_value is not None and existing_value != expected_value:
            raise ValueError(f"{key} already set to {existing_value!r}; expected {expected_value!r}")
        updated[key] = expected_value
    return updated
