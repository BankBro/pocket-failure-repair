from pathlib import Path
import importlib.util

from pfr.baselines.smoke import summarize_baseline
from pfr.evaluation.metrics import is_evaluable_for_repair, is_successful_feedback, summarize_feedback_quality
from pfr.evaluation.repaired import summarize_repaired_metrics


CV_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "eval" / "cross_validate_repaired.py"
CV_SPEC = importlib.util.spec_from_file_location("cross_validate_repaired", CV_SCRIPT)
assert CV_SPEC is not None and CV_SPEC.loader is not None
cross_validate_repaired = importlib.util.module_from_spec(CV_SPEC)
CV_SPEC.loader.exec_module(cross_validate_repaired)
aggregate_folds = cross_validate_repaired.aggregate_folds
summarize_fold = cross_validate_repaired.summarize_fold

SPLIT_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "eval" / "summarize_repaired_split.py"
SPLIT_SPEC = importlib.util.spec_from_file_location("summarize_repaired_split", SPLIT_SCRIPT)
assert SPLIT_SPEC is not None and SPLIT_SPEC.loader is not None
summarize_repaired_split = importlib.util.module_from_spec(SPLIT_SPEC)
SPLIT_SPEC.loader.exec_module(summarize_repaired_split)
summarize_subset = summarize_repaired_split.summarize_subset


def test_feedback_success_rules() -> None:
    good = {"geometry": {"editable_region_validity": True, "clash_count": 0, "anchor_distance_error": 0.5}}
    clash = {"geometry": {"editable_region_validity": True, "clash_count": 1, "anchor_distance_error": 0.0}}
    anchor = {"geometry": {"editable_region_validity": True, "clash_count": 0, "anchor_distance_error": 2.0}}
    invalid = {"geometry": {"editable_region_validity": False, "clash_count": 0, "anchor_distance_error": 0.0}}

    assert is_successful_feedback(good)
    assert not is_successful_feedback(clash)
    assert not is_successful_feedback(anchor)
    assert not is_successful_feedback(invalid)


def test_feedback_quality_summary() -> None:
    rows = [
        {"geometry": {"editable_region_validity": True, "clash_count": 0, "anchor_distance_error": 0.0}},
        {"geometry": {"editable_region_validity": False, "clash_count": 1, "anchor_distance_error": 2.0}},
    ]

    summary = summarize_feedback_quality(rows)

    assert summary["num_candidates"] == 2
    assert summary["num_evaluable_for_repair"] == 2
    assert summary["repair_evaluable_rate"] == 1.0
    assert summary["same_budget_success_rate"] == 0.5
    assert summary["editable_validity"] == 0.5
    assert summary["anchor_validity"] == 0.5
    assert summary["clash_free_rate"] == 0.5


def test_sample_quality_evaluable_flag() -> None:
    evaluable = {"sample_quality": {"evaluable_for_repair": True}}
    excluded = {"sample_quality": {"evaluable_for_repair": False, "exclusion_reasons": ["protein_ligand_overlap"]}}
    legacy = {"geometry": {}}

    assert is_evaluable_for_repair(evaluable)
    assert not is_evaluable_for_repair(excluded)
    assert is_evaluable_for_repair(legacy)
    rows = [
        {"geometry": {"editable_region_validity": True, "clash_count": 0, "anchor_distance_error": 0.0}},
        {"geometry": {"editable_region_validity": True, "clash_count": 1, "anchor_distance_error": 0.0}},
    ]

    summary = summarize_baseline("best_of_n", rows)

    assert summary["baseline"] == "best_of_n"
    assert summary["num_candidates"] == 2
    assert summary["num_evaluable_for_repair"] == 2
    assert summary["repair_evaluable_rate"] == 1.0
    assert summary["same_budget_success_rate"] == 0.5
    assert summary["editable_validity"] == 1.0
    assert summary["clash_free_rate"] == 0.5


def test_repaired_summary_groups_by_baseline() -> None:
    rows = [
        {
            "baseline": "identity_failed_candidate",
            "sample_evaluable_for_repair": True,
            "repaired_success": False,
            "scaffold_preserved": True,
            "editable_validity": True,
            "anchor_validity": False,
            "clash_free": False,
            "clash_count": 3,
            "qed": 0.2,
            "logp": 1.0,
            "rotatable_bonds": 4,
        },
        {
            "baseline": "identity_failed_candidate",
            "sample_evaluable_for_repair": True,
            "repaired_success": True,
            "scaffold_preserved": True,
            "editable_validity": True,
            "anchor_validity": True,
            "clash_free": True,
            "clash_count": 0,
            "qed": 0.4,
            "logp": 3.0,
            "rotatable_bonds": 2,
        },
    ]

    summary = summarize_repaired_metrics(rows)[0]

    assert summary["baseline"] == "identity_failed_candidate"
    assert summary["num_repaired"] == 2
    assert summary["num_sample_evaluable"] == 2
    assert summary["repaired_success_rate"] == 0.5
    assert summary["scaffold_preservation"] == 1.0
    assert summary["anchor_validity"] == 0.5
    assert summary["mean_clash_count"] == 1.5


def test_leave_one_complex_fold_summary() -> None:
    rows = [
        {
            "complex_id": "1a4w",
            "baseline": "feedback_geometry_refinement",
            "sample_evaluable_for_repair": True,
            "repaired_success": True,
            "scaffold_preserved": True,
            "editable_validity": True,
            "anchor_validity": True,
            "clash_free": True,
            "clash_count": 0,
            "qed": 0.3,
            "logp": 2.0,
            "posebusters_like_pass": True,
            "contact_fingerprint_similarity": 0.8,
            "vina_like_proxy": 1.0,
        },
        {
            "complex_id": "3ptb",
            "baseline": "feedback_geometry_refinement",
            "sample_evaluable_for_repair": True,
            "repaired_success": False,
            "scaffold_preserved": True,
            "editable_validity": True,
            "anchor_validity": False,
            "clash_free": False,
            "clash_count": 2,
            "qed": 0.1,
            "logp": 1.0,
            "posebusters_like_pass": False,
            "contact_fingerprint_similarity": 0.4,
            "vina_like_proxy": 5.0,
        },
    ]

    folds = [summarize_fold(rows, complex_id) for complex_id in ["1a4w", "3ptb"]]
    aggregate = aggregate_folds(folds)[0]

    assert folds[0]["held_out_complex"] == "1a4w"
    assert folds[0]["metrics"][0]["repaired_success_rate"] == 1.0
    assert aggregate["baseline"] == "feedback_geometry_refinement"
    assert aggregate["num_folds"] == 2
    assert aggregate["fold_mean_repaired_success_rate"] == 0.5
    assert aggregate["fold_mean_mean_vina_like_proxy"] == 3.0


def test_repaired_split_subset_summary() -> None:
    rows = [
        {
            "complex_id": "train_complex",
            "baseline": "best_of_n",
            "sample_evaluable_for_repair": True,
            "repaired_success": True,
            "scaffold_preserved": True,
            "editable_validity": True,
            "anchor_validity": True,
            "clash_free": True,
            "clash_count": 0,
            "qed": 0.2,
            "logp": 1.0,
        },
        {
            "complex_id": "test_complex",
            "baseline": "best_of_n",
            "sample_evaluable_for_repair": True,
            "repaired_success": False,
            "scaffold_preserved": True,
            "editable_validity": True,
            "anchor_validity": False,
            "clash_free": False,
            "clash_count": 4,
            "qed": 0.1,
            "logp": 2.0,
        },
    ]

    split = summarize_subset(rows, "test", ["test_complex"])

    assert split["split"] == "test"
    assert split["num_complexes"] == 1
    assert split["num_repaired_records"] == 1
    assert split["metrics"][0]["baseline"] == "best_of_n"
    assert split["metrics"][0]["repaired_success_rate"] == 0.0
