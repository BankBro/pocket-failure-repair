"""Baseline summary helpers."""

from __future__ import annotations

from typing import Any

from pfr.evaluation.metrics import summarize_feedback_quality


def summarize_baseline(name: str, feedback_rows: list[dict[str, Any]]) -> dict[str, Any]:
    quality = summarize_feedback_quality(feedback_rows)
    return {
        "baseline": name,
        "num_candidates": quality["num_candidates"],
        "same_budget_success_rate": quality["same_budget_success_rate"],
        "scaffold_preservation": None,
        "editable_validity": quality["editable_validity"],
        "anchor_validity": quality["anchor_validity"],
        "clash_count": None,
        "clash_free_rate": quality["clash_free_rate"],
        "posebusters_pass": None,
        "plip_interaction_recovery": None,
        "vina_delta": None,
        "qed": None,
        "sa": None,
        "logp": None,
        "rotatable_bonds": None,
        "source": "smoke_rdkit_feedback_template",
    }


def summarize_baselines(names: list[str], feedback_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [summarize_baseline(name, feedback_rows) for name in names]
