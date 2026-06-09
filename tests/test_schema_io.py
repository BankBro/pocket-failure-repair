import hashlib
import json
from pathlib import Path
import sys

import pytest

from pfr.utils.schema_io import (
    load_schema_ref,
    with_schema_ref,
    write_json_with_schema,
    write_jsonl_with_schema,
)


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.eval.audit_common import finalize_output_manifest  # noqa: E402


def write_schema(root: Path, relpath: str, *, required: list[str] | None = None) -> Path:
    schema_path = root / relpath
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path.write_text(
        json.dumps(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "required": ["schema_version", "schema_path", *(required or [])],
                "properties": {
                    "schema_version": {"type": "string", "const": "tmp_schema_v0_1"},
                    "schema_path": {"type": "string", "const": relpath},
                    "sample_id": {"type": "string"},
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return schema_path


def test_schema_ref_is_loaded_from_schema_const(tmp_path: Path) -> None:
    write_schema(tmp_path, "schemas/tmp_schema_v0_1.json")

    schema_ref = load_schema_ref("schemas/tmp_schema_v0_1.json", root=tmp_path)

    assert schema_ref.schema_version == "tmp_schema_v0_1"
    assert schema_ref.schema_path == "schemas/tmp_schema_v0_1.json"


def test_with_schema_ref_injects_refs_and_rejects_conflicts(tmp_path: Path) -> None:
    schema_path = write_schema(tmp_path, "schemas/tmp_schema_v0_1.json")

    payload = with_schema_ref({"sample_id": "s1"}, schema_path, root=tmp_path)
    assert payload["schema_version"] == "tmp_schema_v0_1"
    assert payload["schema_path"] == "schemas/tmp_schema_v0_1.json"

    with pytest.raises(ValueError, match="schema_version already set"):
        with_schema_ref({"schema_version": "wrong"}, schema_path, root=tmp_path)


def test_write_json_with_schema_checks_required_fields(tmp_path: Path) -> None:
    schema_path = write_schema(tmp_path, "schemas/tmp_schema_v0_1.json", required=["sample_id"])
    output_path = tmp_path / "out" / "record.json"

    with pytest.raises(ValueError, match="missing required fields"):
        write_json_with_schema(output_path, {}, schema_path, root=tmp_path)
    assert not output_path.exists()

    write_json_with_schema(output_path, {"sample_id": "s1"}, schema_path, root=tmp_path)
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "tmp_schema_v0_1"
    assert payload["sample_id"] == "s1"


def test_write_jsonl_with_schema_validates_all_rows_before_writing(tmp_path: Path) -> None:
    schema_path = write_schema(tmp_path, "schemas/tmp_schema_v0_1.json", required=["sample_id"])
    output_path = tmp_path / "rows.jsonl"

    with pytest.raises(ValueError, match="missing required fields"):
        write_jsonl_with_schema(output_path, [{"sample_id": "s1"}, {}], schema_path, root=tmp_path)
    assert not output_path.exists()

    write_jsonl_with_schema(output_path, [{"sample_id": "s1"}, {"sample_id": "s2"}], schema_path, root=tmp_path)
    rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]
    assert [row["schema_path"] for row in rows] == ["schemas/tmp_schema_v0_1.json"] * 2


def test_schema_path_const_must_match_schema_location(tmp_path: Path) -> None:
    schema_path = write_schema(tmp_path, "schemas/tmp_schema_v0_1.json")
    payload = json.loads(schema_path.read_text(encoding="utf-8"))
    payload["properties"]["schema_path"]["const"] = "schemas/not_the_file_name.json"
    schema_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="does not match"):
        load_schema_ref(schema_path, root=tmp_path)


def test_manual_decisions_schema_declares_required_enums() -> None:
    schema_ref = load_schema_ref("schemas/configs/audit/manual_decisions_v0_1.json", root=ROOT)
    schema = schema_ref.schema

    assert schema_ref.schema_version == "config_audit_manual_decisions_v0_1"
    assert "decisions" in schema["required"]
    decision_schema = schema["properties"]["decisions"]["items"]
    assert "decision_type" in decision_schema["required"]
    assert "claim_boundary" in decision_schema["properties"]["decision_type"]["enum"]
    assert "target_type" in decision_schema["properties"]["target"]["required"]
    assert "sample" in decision_schema["properties"]["target"]["properties"]["target_type"]["enum"]


def test_finalize_output_manifest_refreshes_sha256_after_all_outputs(tmp_path: Path) -> None:
    run_root = tmp_path / "run"
    (run_root / "processed").mkdir(parents=True)
    (run_root / "evaluator").mkdir()
    (run_root / "summaries").mkdir()
    (run_root / "logs").mkdir()
    (run_root / "manifests").mkdir()
    files = [
        run_root / "run_metadata.json",
        run_root / "samples.jsonl",
        run_root / "stage_attrition.json",
        run_root / "processed" / "sample.sdf",
        run_root / "evaluator" / "evaluator_input.jsonl",
        run_root / "summaries" / "label_summary.json",
    ]
    for index, path in enumerate(files):
        path.write_text(f"payload-{index}\n", encoding="utf-8")
    output_manifest = {
        "schema_version": "output_manifest_v0_1",
        "schema_path": "schemas/third_party_audit/run/output_manifest_v0_1.json",
        "run_id": "r1",
        "metadata_schemas": {},
        "captured_outputs": [],
        "logs": [],
        "sha256": {},
    }
    (run_root / "output_manifest.json").write_text(json.dumps(output_manifest), encoding="utf-8")

    manifest = finalize_output_manifest(run_root)

    assert manifest["metadata_schemas"]["evaluator_input"] == "schemas/third_party_audit/diagnosis/evaluator_input_v0_1.json"
    assert manifest["n_output_artifacts"] == len(files)
    for path in files:
        assert manifest["sha256"][str(path)] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert str(run_root / "output_manifest.json") not in manifest["sha256"]
