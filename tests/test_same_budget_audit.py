from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "eval" / "audit_same_budget.py"
SPEC = spec_from_file_location("audit_same_budget", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
summarize = MODULE.summarize
infer_seed_from_path = MODULE.infer_seed_from_path


def row(candidate_id: str, baseline: str, seed: int = 0, **extra):
    data = {
        "candidate_id": candidate_id,
        "baseline": baseline,
        "seed": seed,
        "repaired_success": True,
        "repair_gain_success": False,
        "contact_recovery_gain": 0.0,
        "internal_candidate_budget": 1,
        "internal_budget_type": "unit_test_budget",
    }
    data.update(extra)
    return data


def test_same_budget_audit_passes_for_one_record_per_candidate_and_baseline():
    rows = [
        row("c1", "a"),
        row("c2", "a"),
        row("c1", "b"),
        row("c2", "b"),
    ]

    metrics, audit = summarize(rows)

    assert audit["record_level_all_baselines_same_budget"] is True
    assert audit["record_level_same_budget_failures"] == []
    assert audit["internal_budget_metadata_available"] is True
    assert audit["strict_internal_candidate_budget_equal"] is True
    assert {metric["baseline"]: metric["coverage_rate"] for metric in metrics} == {"a": 1.0, "b": 1.0}


def test_same_budget_audit_flags_missing_and_duplicate_records():
    rows = [
        row("c1", "a"),
        row("c2", "a"),
        row("c1", "a"),
        row("c1", "b"),
    ]

    metrics, audit = summarize(rows)
    by_baseline = {metric["baseline"]: metric for metric in metrics}

    assert audit["record_level_all_baselines_same_budget"] is False
    assert audit["record_level_same_budget_failures"] == ["a", "b"]
    assert by_baseline["a"]["duplicate_candidate_records"] == 1
    assert by_baseline["b"]["missing_candidate_count"] == 1
    assert by_baseline["b"]["record_level_same_budget_pass"] is False


def test_same_budget_audit_exposes_internal_budget_inequality():
    rows = [
        row("c1", "a", internal_candidate_budget=1, internal_budget_type="single"),
        row("c2", "a", internal_candidate_budget=1, internal_budget_type="single"),
        row("c1", "b", internal_candidate_budget=10, internal_budget_type="pool"),
        row("c2", "b", internal_candidate_budget=10, internal_budget_type="pool"),
    ]

    metrics, audit = summarize(rows)
    by_baseline = {metric["baseline"]: metric for metric in metrics}

    assert audit["record_level_all_baselines_same_budget"] is True
    assert audit["internal_budget_metadata_available"] is True
    assert audit["strict_internal_candidate_budget_equal"] is False
    assert audit["internal_candidate_budget_values"] == [1.0, 10.0]
    assert by_baseline["a"]["internal_budget_types"] == ["single"]
    assert by_baseline["b"]["internal_candidate_budget_mean"] == 10.0


def test_same_budget_audit_does_not_use_mean_as_strict_budget_equality():
    rows = [
        row("c1", "a", internal_candidate_budget=1),
        row("c2", "a", internal_candidate_budget=3),
        row("c1", "b", internal_candidate_budget=2),
        row("c2", "b", internal_candidate_budget=2),
    ]

    _, audit = summarize(rows)

    assert audit["record_level_all_baselines_same_budget"] is True
    assert audit["internal_candidate_budget_values"] == [1.0, 2.0, 3.0]
    assert audit["strict_internal_candidate_budget_equal"] is False


def test_same_budget_audit_requires_complete_internal_budget_metadata_for_strict_pass():
    rows = [
        row("c1", "a", internal_candidate_budget=1),
        row("c1", "b", internal_candidate_budget=None, internal_budget_type=None),
    ]

    _, audit = summarize(rows)

    assert audit["record_level_all_baselines_same_budget"] is True
    assert audit["internal_budget_metadata_available"] is False
    assert audit["strict_internal_candidate_budget_equal"] is False


def test_infer_seed_from_path_accepts_common_seed_separators():
    assert infer_seed_from_path("evaluated_repaired_seed0.jsonl") == 0
    assert infer_seed_from_path("evaluated_repaired_seed_1.jsonl") == 1
    assert infer_seed_from_path("evaluated_repaired_seed-2.jsonl") == 2
    assert infer_seed_from_path("evaluated_repaired_seed.3.jsonl") == 3
