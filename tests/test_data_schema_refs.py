import fnmatch
import hashlib
import json
from pathlib import Path
from typing import Any

from pfr.data.schema_refs import DATA_SCHEMA_REFS


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"


def data_schema_key(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "data/catalog/dataset_catalog_v1.json":
        return "dataset_catalog"
    if fnmatch.fnmatch(rel, "data/catalog/dataset_layout_migration_*.json"):
        return "dataset_layout_migration"
    if fnmatch.fnmatch(rel, "data/catalog/*raw_reconciliation*.json"):
        return "dataset_raw_reconciliation"
    if fnmatch.fnmatch(rel, "data/datasets/*/entries/*/entry.json"):
        return "dataset_entry"
    if fnmatch.fnmatch(rel, "data/datasets/*/splits/*.json"):
        return "dataset_split"
    if fnmatch.fnmatch(rel, "data/datasets/*/views/*.json"):
        return "dataset_view"
    if fnmatch.fnmatch(rel, "data/datasets/*/manifests/raw/*.json"):
        return "dataset_raw_manifest"
    if fnmatch.fnmatch(rel, "data/datasets/*/manifests/entries/*.json"):
        return "dataset_entries_manifest"
    if fnmatch.fnmatch(rel, "data/datasets/*/manifests/lineage/raw_to_entry_index_v1.json"):
        return "dataset_lineage_raw_to_entry"
    if fnmatch.fnmatch(rel, "data/datasets/*/manifests/lineage/entry_to_raw_index_v1.json"):
        return "dataset_lineage_entry_to_raw"
    raise AssertionError(f"no schema mapping for {rel}")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        assert isinstance(row, dict), f"{path}:{line_number}"
        rows.append(row)
    return rows


def assert_schema_ref(path: Path, payload: dict[str, Any], schema_key: str) -> None:
    schema_ref = DATA_SCHEMA_REFS[schema_key]
    assert payload.get("schema_version") == schema_ref["schema_version"], path
    assert payload.get("schema_path") == schema_ref["schema_path"], path

    schema_path = ROOT / schema_ref["schema_path"]
    assert schema_path.exists(), path
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema_ref["schema_version"] == schema["properties"]["schema_version"]["const"], path
    assert schema_ref["schema_path"] == schema["properties"]["schema_path"]["const"], path
    for required_key in schema.get("required", []):
        assert required_key in payload, (path, required_key)


def test_all_data_json_and_jsonl_instances_declare_schema_refs() -> None:
    json_paths = sorted(DATA_ROOT.rglob("*.json"))
    jsonl_paths = sorted(DATA_ROOT.rglob("*.jsonl"))
    assert json_paths
    assert jsonl_paths

    for path in json_paths:
        schema_key = data_schema_key(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict), path
        assert_schema_ref(path, payload, schema_key)

    for path in jsonl_paths:
        assert path.name == "index.jsonl", path
        for row in read_jsonl(path):
            assert_schema_ref(path, row, "dataset_entry")


def test_entry_index_sha256_refs_match_current_index_files() -> None:
    for dataset_root in sorted(path for path in (DATA_ROOT / "datasets").iterdir() if path.is_dir()):
        index_path = dataset_root / "entries" / "index.jsonl"
        entry_index_sha256 = hashlib.sha256(index_path.read_bytes()).hexdigest()

        for manifest_path in sorted((dataset_root / "manifests" / "entries").glob("*.json")):
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            assert payload["entry_index_sha256"] == entry_index_sha256, manifest_path

        for lineage_path in sorted((dataset_root / "manifests" / "lineage").glob("*.json")):
            payload = json.loads(lineage_path.read_text(encoding="utf-8"))
            for raw_record in payload.get("raw_to_entry", []):
                for link in raw_record.get("links", []):
                    assert link["entry_index_sha256"] == entry_index_sha256, lineage_path
            for entry_record in payload.get("entry_to_raw", []):
                for link in entry_record.get("raw_links", []):
                    assert link["entry_index_sha256"] == entry_index_sha256, lineage_path
