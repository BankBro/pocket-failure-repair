import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG_ROOTS = [
    ROOT / "configs" / "audit",
    ROOT / "configs" / "data",
    ROOT / "configs" / "third_party",
]
DATA_CONFIG_ROOT = ROOT / "configs" / "data"
DATA_CONFIG_SCHEMA_ROOT = ROOT / "schemas" / "configs" / "data"
RESOLVED_THIRD_PARTY_PROTOCOL_ROOT = (
    ROOT / "experiments" / "20260603-01-third-party-failure-audit-mvp" / "configs" / "resolved" / "third_party"
)


def iter_config_files() -> list[Path]:
    paths: list[Path] = []
    for root in CONFIG_ROOTS:
        for path in root.rglob("*"):
            if path.is_file() and path.name != "README.md":
                paths.append(path)
    return sorted(paths)


def test_configs_declare_existing_schema_refs() -> None:
    for path in iter_config_files():
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict), path
        schema_version = payload.get("schema_version")
        schema_path = payload.get("schema_path")
        assert isinstance(schema_version, str) and schema_version, path
        assert isinstance(schema_path, str) and schema_path, path

        schema_file = ROOT / schema_path
        assert schema_file.exists(), path
        schema_payload = json.loads(schema_file.read_text(encoding="utf-8"))
        expected_version = schema_payload.get("properties", {}).get("schema_version", {}).get("const")
        expected_path = schema_payload.get("properties", {}).get("schema_path", {}).get("const")
        assert schema_version == expected_version, path
        assert schema_path == expected_path, path


def test_project_level_configs_do_not_contain_run_templates() -> None:
    forbidden_tokens = [
        "{experiment_id}",
        "{run_id}",
        "{n_samples}",
        "mvp_trial_template_not_executed",
    ]
    for path in iter_config_files():
        text = path.read_text(encoding="utf-8")
        for token in forbidden_tokens:
            assert token not in text, path


def test_data_config_roots_do_not_contain_loose_files() -> None:
    loose_config_files = [path for path in DATA_CONFIG_ROOT.iterdir() if path.is_file()]
    loose_schema_files = [path for path in DATA_CONFIG_SCHEMA_ROOT.iterdir() if path.is_file()]
    assert loose_config_files == []
    assert loose_schema_files == []


def test_resolved_third_party_protocol_schema_refs_are_valid() -> None:
    for path in sorted(RESOLVED_THIRD_PARTY_PROTOCOL_ROOT.glob("*.yaml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict), path

        schema_path = payload.get("schema_path")
        schema_version = payload.get("schema_version")
        assert isinstance(schema_path, str) and schema_path, path
        assert isinstance(schema_version, str) and schema_version, path

        schema_file = ROOT / schema_path
        assert schema_file.exists(), path
        schema_payload = json.loads(schema_file.read_text(encoding="utf-8"))
        assert schema_version == schema_payload.get("properties", {}).get("schema_version", {}).get("const"), path
        assert schema_path == schema_payload.get("properties", {}).get("schema_path", {}).get("const"), path

        metadata_schemas = (
            payload.get("mvp_trial", {})
            .get("output_expectations", {})
            .get("metadata_schemas", {})
        )
        assert isinstance(metadata_schemas, dict) and metadata_schemas, path
        for key, value in metadata_schemas.items():
            assert isinstance(key, str) and key, path
            assert isinstance(value, str) and value, path
            assert (ROOT / value).exists(), (path, key, value)
