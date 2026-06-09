from __future__ import annotations

from argparse import Namespace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.eval.build_audit_labels import classify
from scripts.eval.check_analysis_frozen_gate import internal_energy_coverage, run_sanity_set
from scripts.eval.eval_posebusters_one import POSEBUSTERS_RAW_RESULT_SCHEMA_PATH, POSEBUSTERS_RAW_RESULT_SCHEMA_VERSION, base_result, json_safe
from scripts.eval.prepare_receptor import build_record
from scripts.eval.run_audit_evaluators import posebusters_formal_status


def pdb_line(record: str, serial: int, atom: str, residue: str, chain: str, resi: int, x: float, y: float, z: float, element: str) -> str:
    return (
        f"{record:<6}{serial:5d} {atom:<4} {residue:>3} {chain:1}{resi:4d}    "
        f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00 20.00          {element:>2}"
    )


def test_prepare_receptor_removes_reference_and_records_unknown_near_pocket(tmp_path: Path) -> None:
    raw = tmp_path / "tiny.pdb"
    raw.write_text(
        "\n".join(
            [
                pdb_line("ATOM", 1, "CA", "ALA", "A", 1, 10.0, 0.0, 0.0, "C"),
                pdb_line("HETATM", 2, "C1", "CFF", "A", 330, 0.0, 0.0, 0.0, "C"),
                pdb_line("HETATM", 3, "N1", "CFF", "A", 330, 1.0, 0.0, 0.0, "N"),
                pdb_line("HETATM", 4, "C1", "UNK", "A", 331, 2.0, 0.0, 0.0, "C"),
                "CONECT    2    3",
                "END",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    record = build_record(
        Namespace(
            raw_receptor=str(raw),
            reference_ligand="A:330",
            case_id="tiny",
            output_dir=str(tmp_path / "out"),
            policy="configs/audit/receptor_prep_policy_v0_1.yaml",
            output_prefix=None,
            index=None,
            run_id=None,
        )
    )
    cleaned = Path(record["cleaned_receptor_path"]).read_text(encoding="utf-8")
    assert "CFF" not in cleaned
    assert "CONECT    2" not in cleaned
    assert record["reference_ligand"]["residue_name"] == "CFF"
    assert record["unresolved_review_required_count"] == 1
    assert record["review_required_hetero_atoms"][0]["residue_name"] == "UNK"
    assert record["pocket_box"]["generated_ligand_centroid_fallback_used"] is False


def test_posebusters_frozen_columns_ignore_extra_full_report_booleans() -> None:
    layer = {
        "formal_metric_name": "posebusters_ligand_core_pass",
        "frozen_columns": ["mol_pred_loaded", "sanitization"],
    }
    metrics = {
        "posebusters_bool_checks": {
            "mol_pred_loaded": True,
            "sanitization": True,
            "mol_true_loaded": False,
        }
    }
    status, errors = posebusters_formal_status(metrics, layer)
    assert status == "passed"
    assert errors == []
    assert metrics["posebusters_ligand_core_pass"] is True


def internal_energy_layer() -> dict[str, object]:
    return {
        "formal_metric_name": "posebusters_ligand_core_pass",
        "required_columns": ["mol_pred_loaded", "sanitization", "inchi_convertible", "bond_lengths"],
        "conditional_columns": ["internal_energy"],
        "conditional_unavailable_allowed": {
            "internal_energy": {
                "required_true_checks": ["mol_pred_loaded", "sanitization", "inchi_convertible"],
                "required_raw_columns": ["internal_energy", "energy_ratio", "ensemble_avg_energy"],
                "default_reason": "energy_ratio_unavailable",
                "stderr_reason_patterns": {
                    "Failed to generate conformations.": "energy_ratio_conformer_ensemble_unavailable",
                },
            }
        },
    }


def test_posebusters_internal_energy_nan_is_unavailable_not_missing() -> None:
    metrics = {
        "posebusters_bool_checks": {
            "mol_pred_loaded": True,
            "sanitization": True,
            "inchi_convertible": True,
            "bond_lengths": True,
        },
        "posebusters_report_values": {
            "mol_pred_loaded": True,
            "sanitization": True,
            "inchi_convertible": True,
            "bond_lengths": True,
            "internal_energy": None,
            "energy_ratio": None,
            "ensemble_avg_energy": None,
        },
        "stderr_head": "Energy ratio module failed: Failed to generate conformations.",
    }
    status, errors = posebusters_formal_status(metrics, internal_energy_layer())
    assert status == "passed"
    assert errors == []
    assert metrics["posebusters_ligand_core_pass_missing_columns"] == []
    assert metrics["posebusters_ligand_core_pass_unavailable_columns"] == ["internal_energy"]
    assert metrics["posebusters_ligand_core_pass_unavailable_reasons"]["internal_energy"] == "energy_ratio_conformer_ensemble_unavailable"
    assert metrics["posebusters_ligand_core_pass_conditional_coverage_pass"] is False
    assert metrics["posebusters_ligand_core_pass_clean_pass"] is False


def test_posebusters_internal_energy_false_is_failed_column() -> None:
    metrics = {
        "posebusters_bool_checks": {
            "mol_pred_loaded": True,
            "sanitization": True,
            "inchi_convertible": True,
            "bond_lengths": True,
            "internal_energy": False,
        },
        "posebusters_report_values": {
            "internal_energy": False,
            "energy_ratio": 99.0,
            "ensemble_avg_energy": 1.0,
        },
    }
    status, errors = posebusters_formal_status(metrics, internal_energy_layer())
    assert status == "failed"
    assert errors == []
    assert metrics["posebusters_ligand_core_pass_failed_columns"] == ["internal_energy"]


def test_posebusters_internal_energy_raw_column_missing_still_blocks() -> None:
    metrics = {
        "posebusters_bool_checks": {
            "mol_pred_loaded": True,
            "sanitization": True,
            "inchi_convertible": True,
            "bond_lengths": True,
        },
        "posebusters_report_values": {
            "mol_pred_loaded": True,
            "sanitization": True,
            "inchi_convertible": True,
            "bond_lengths": True,
        },
    }
    status, errors = posebusters_formal_status(metrics, internal_energy_layer())
    assert status == "tool_failure"
    assert errors == ["missing_frozen_column:internal_energy"]
    assert metrics["posebusters_ligand_core_pass_missing_columns"] == ["internal_energy"]


def test_json_safe_converts_non_json_numbers() -> None:
    assert json_safe(float("nan")) is None
    assert json_safe(float("inf")) is None
    assert json_safe(True) is True
    assert json_safe(3) == 3
    assert json_safe(1.25) == 1.25


def test_posebusters_raw_base_result_has_schema_refs() -> None:
    result = base_result({"candidate_id": "c1", "complex_id": "3rfm"}, 7, "mol")
    assert result["schema_version"] == POSEBUSTERS_RAW_RESULT_SCHEMA_VERSION
    assert result["schema_path"] == POSEBUSTERS_RAW_RESULT_SCHEMA_PATH
    assert result["input_index"] == 7
    assert result["posebusters_config"] == "mol"


def test_label_mapping_vina_pass_does_not_override_pocket_failure() -> None:
    sample = {
        "sample_id": "s1",
        "run_id": "r1",
        "method": "DiffSBDD",
        "complex_id": "3rfm",
        "stage": "final",
        "sample_role": "final_output",
        "molecule_path": "/tmp/s1.sdf",
        "quality_flags": {"final_only_selected_output_view": True},
        "original_status": {"status": "final"},
    }
    tool = {
        "rdkit": {"status": "passed", "metrics": {}, "errors": []},
        "posebusters_mol": {"status": "passed", "metrics": {"posebusters_ligand_core_pass_failed_columns": []}, "errors": []},
        "posebusters_dock": {
            "status": "failed",
            "metrics": {"posebusters_pocket_core_pass_failed_columns": ["minimum_distance_to_protein"]},
            "errors": [],
        },
        "vina": {"status": "passed", "metrics": {"vina_score_only_energy": -7.0}, "errors": []},
    }
    result = classify(sample, tool)
    assert result["evaluability_status"] == "evaluable"
    assert result["primary_label"] == "protein_ligand_clash"
    assert "protein_ligand_clash" in result["secondary_labels"]


def test_label_mapping_geometry_failure_with_internal_energy_unavailable() -> None:
    sample = {
        "sample_id": "s1",
        "run_id": "r1",
        "method": "DiffSBDD",
        "complex_id": "3rfm",
        "stage": "final",
        "sample_role": "final_output",
        "molecule_path": "/tmp/s1.sdf",
        "quality_flags": {"final_only_selected_output_view": True},
        "original_status": {"status": "final"},
    }
    tool = {
        "rdkit": {"status": "passed", "metrics": {}, "errors": []},
        "posebusters_mol": {
            "status": "failed",
            "metrics": {
                "posebusters_ligand_core_pass_failed_columns": ["bond_lengths"],
                "posebusters_ligand_core_pass_unavailable_columns": ["internal_energy"],
                "posebusters_ligand_core_pass_unavailable_reasons": {
                    "internal_energy": "energy_ratio_conformer_ensemble_unavailable",
                },
            },
            "errors": [],
        },
        "posebusters_dock": {"status": "passed", "metrics": {"posebusters_pocket_core_pass_failed_columns": []}, "errors": []},
        "vina": {"status": "passed", "metrics": {"vina_score_only_energy": -7.0}, "errors": []},
    }
    result = classify(sample, tool)
    assert result["evaluability_status"] == "evaluable"
    assert result["primary_label"] == "local_geometry_failure"
    assert "posebusters_internal_energy_unavailable" in result["secondary_labels"]
    assert result["evidence"]["posebusters_ligand_core_unavailable_columns"] == ["internal_energy"]


def test_label_mapping_energy_unavailable_without_core_failure_is_not_clean_pass() -> None:
    sample = {
        "sample_id": "s1",
        "run_id": "r1",
        "method": "DiffSBDD",
        "complex_id": "3rfm",
        "stage": "final",
        "sample_role": "final_output",
        "molecule_path": "/tmp/s1.sdf",
        "quality_flags": {"final_only_selected_output_view": True},
        "original_status": {"status": "final"},
    }
    tool = {
        "rdkit": {"status": "passed", "metrics": {}, "errors": []},
        "posebusters_mol": {
            "status": "passed",
            "metrics": {
                "posebusters_ligand_core_pass_failed_columns": [],
                "posebusters_ligand_core_pass_unavailable_columns": ["internal_energy"],
            },
            "errors": [],
        },
        "posebusters_dock": {"status": "passed", "metrics": {"posebusters_pocket_core_pass_failed_columns": []}, "errors": []},
        "vina": {"status": "passed", "metrics": {"vina_score_only_energy": -7.0}, "errors": []},
    }
    result = classify(sample, tool)
    assert result["evaluability_status"] == "evaluable"
    assert result["primary_label"] == "unknown"
    assert "no_core_failure_detected_with_energy_unavailable" in result["secondary_labels"]
    assert result["evidence"]["no_frozen_failure_detected"] is True


def test_internal_energy_coverage_counts_false_and_unavailable() -> None:
    rows = [
        {
            "sample_id": "s1",
            "evaluator_name": "posebusters_mol",
            "metrics": {"posebusters_ligand_core_pass_failed_columns": ["internal_energy"]},
        },
        {
            "sample_id": "s2",
            "evaluator_name": "posebusters_mol",
            "metrics": {
                "posebusters_ligand_core_pass_unavailable_columns": ["internal_energy"],
                "posebusters_ligand_core_pass_unavailable_reasons": {"internal_energy": "energy_ratio_unavailable"},
            },
        },
        {"sample_id": "s3", "evaluator_name": "posebusters_dock", "metrics": {}},
    ]
    coverage = internal_energy_coverage(rows)
    assert coverage["denominator_posebusters_mol_rows"] == 2
    assert coverage["internal_energy_false_count"] == 1
    assert coverage["internal_energy_unavailable_count"] == 1
    assert coverage["internal_energy_unavailable_fraction"] == 0.5


def test_analysis_gate_sanity_set_passes() -> None:
    results = run_sanity_set()
    assert results
    assert all(item["passed"] for item in results)
