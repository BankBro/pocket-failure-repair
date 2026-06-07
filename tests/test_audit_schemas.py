import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_audit_schema_refs_are_self_consistent() -> None:
    for path in sorted((ROOT / "schemas" / "third_party_audit").rglob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        properties = payload.get("properties", {})
        schema_version = properties.get("schema_version", {}).get("const")
        schema_path = properties.get("schema_path", {}).get("const")
        if schema_version is None and schema_path is None:
            continue
        assert schema_version is not None, path
        assert schema_path == path.relative_to(ROOT).as_posix()
