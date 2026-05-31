from pfr.baselines.smoke import summarize_baseline
from pfr.evaluation.metrics import is_successful_feedback, summarize_feedback_quality


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
    assert summary["same_budget_success_rate"] == 0.5
    assert summary["editable_validity"] == 0.5
    assert summary["anchor_validity"] == 0.5
    assert summary["clash_free_rate"] == 0.5


def test_smoke_baseline_summary_uses_quality_metrics() -> None:
    rows = [
        {"geometry": {"editable_region_validity": True, "clash_count": 0, "anchor_distance_error": 0.0}},
        {"geometry": {"editable_region_validity": True, "clash_count": 1, "anchor_distance_error": 0.0}},
    ]

    summary = summarize_baseline("best_of_n", rows)

    assert summary["baseline"] == "best_of_n"
    assert summary["num_candidates"] == 2
    assert summary["same_budget_success_rate"] == 0.5
    assert summary["editable_validity"] == 1.0
    assert summary["clash_free_rate"] == 0.5
