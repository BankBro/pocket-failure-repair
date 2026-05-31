"""Metric helpers for smoke and full evaluation pipelines."""

from __future__ import annotations

from typing import Any


def is_successful_feedback(row: dict[str, Any]) -> bool:
    geometry = row.get("geometry", {})
    if geometry.get("editable_region_validity") is False:
        return False
    if geometry.get("clash_count", 0) not in (None, 0):
        return False
    if float(geometry.get("anchor_distance_error") or 0.0) > 1.0:
        return False
    return True


def fraction(values: list[bool]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def summarize_feedback_quality(feedback_rows: list[dict[str, Any]]) -> dict[str, Any]:
    successes = [is_successful_feedback(row) for row in feedback_rows]
    editable_valid = [row.get("geometry", {}).get("editable_region_validity") is not False for row in feedback_rows]
    anchor_valid = [float(row.get("geometry", {}).get("anchor_distance_error") or 0.0) <= 1.0 for row in feedback_rows]
    clash_free = [row.get("geometry", {}).get("clash_count", 0) in (None, 0) for row in feedback_rows]
    return {
        "num_candidates": len(feedback_rows),
        "same_budget_success_rate": fraction(successes),
        "editable_validity": fraction(editable_valid),
        "anchor_validity": fraction(anchor_valid),
        "clash_free_rate": fraction(clash_free),
    }
