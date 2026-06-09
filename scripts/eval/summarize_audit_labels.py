#!/usr/bin/env python3
"""Summarize frozen-style audit labels and denominator views."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.eval.audit_common import read_json, read_jsonl, with_schema_ref, write_json, write_json_with_schema


LABEL_SUMMARY_SCHEMA_PATH = "schemas/third_party_audit/diagnosis/label_summary_v0_1.json"
PREVALENCE_SUMMARY_SCHEMA_PATH = "schemas/third_party_audit/diagnosis/prevalence_summary_v0_1.json"


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def count_secondary(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        for label in row.get("secondary_labels") or []:
            counts[label] = counts.get(label, 0) + 1
    return dict(sorted(counts.items()))


def internal_energy_coverage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    false_sample_ids: list[str] = []
    unavailable_sample_ids: list[str] = []
    for row in rows:
        evidence = row.get("evidence") or {}
        failed = evidence.get("posebusters_ligand_core_failed_columns") or []
        unavailable = evidence.get("posebusters_ligand_core_unavailable_columns") or []
        if "internal_energy" in failed:
            false_sample_ids.append(str(row.get("sample_id")))
        if "internal_energy" in unavailable:
            unavailable_sample_ids.append(str(row.get("sample_id")))
    denominator = len(rows)
    return {
        "internal_energy_false_count": len(false_sample_ids),
        "internal_energy_false_sample_ids": sorted(false_sample_ids),
        "internal_energy_unavailable_count": len(unavailable_sample_ids),
        "internal_energy_unavailable_fraction": (len(unavailable_sample_ids) / denominator) if denominator else None,
        "internal_energy_unavailable_sample_ids": sorted(unavailable_sample_ids),
    }


def prevalence(count: int, denominator: int | None) -> float | None:
    if denominator is None or denominator <= 0:
        return None
    return count / denominator


def build_summaries(run_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    labels = read_jsonl(run_root / "labels.jsonl")
    stage_attrition = read_json(run_root / "stage_attrition.json")
    row = (stage_attrition.get("rows") or [{}])[0]
    method = labels[0]["method"] if labels else stage_attrition.get("method", "unknown")
    run_id = labels[0]["run_id"] if labels else stage_attrition.get("run_id", run_root.name)
    final_only = all("final_only_selected_output_view" in (label.get("secondary_labels") or []) for label in labels) if labels else True
    evaluable = [label for label in labels if label.get("evaluability_status") == "evaluable"]
    failure_like = [label for label in labels if label.get("primary_label") != "unknown"]
    if row:
        row["N_evaluable"] = len(evaluable)
        row["N_not_evaluable"] = len(labels) - len(evaluable)
        row["notes"] = (
            "Frozen-style post-label attrition. N_evaluable follows labels.jsonl, including tool failures "
            "from frozen evaluator requirements."
        )
        stage_attrition["summary_scope"] = "frozen_style_post_label_selected_output_residual"
        write_json(run_root / "stage_attrition.json", stage_attrition)

    label_summary = with_schema_ref(
        {
            "run_id": run_id,
            "method": method,
            "summary_type": "frozen_style_label_summary",
            "counts": {
                "num_labels": len(labels),
                "evaluability_status": count_by(labels, "evaluability_status"),
                "primary_label": count_by(labels, "primary_label"),
                "secondary_label": count_secondary(labels),
                "near_miss_eligible": {
                    "true": sum(1 for label in labels if label.get("near_miss_eligible") is True),
                    "false": sum(1 for label in labels if label.get("near_miss_eligible") is False),
                },
                "posebusters_internal_energy": internal_energy_coverage(labels),
            },
            "claim_boundary": "selected_output_residual_audit_not_raw_failure_prevalence"
            if final_only
            else "specified_scope_only_no_global_prevalence",
            "notes": "Automatic labels without manual adjudication. Vina is auxiliary; PLIP reference recovery is descriptive evidence.",
        },
        LABEL_SUMMARY_SCHEMA_PATH,
    )

    n_budget = row.get("N_budget")
    n_raw_attempt_metadata = row.get("N_raw_attempt_metadata")
    n_evaluable = len(evaluable)
    n_final = row.get("N_final")
    prevalence_summary = with_schema_ref(
        {
            "run_id": run_id,
            "method": method,
            "prevalence_views": {
                "inclusive_failure_burden": {
                    "status": "downgraded_final_only_source" if final_only else "available",
                    "denominators": {
                        "N_budget": n_budget,
                        "N_raw_attempt_metadata": n_raw_attempt_metadata,
                    },
                    "failure_like_count": len(failure_like),
                    "prevalence": None if final_only else prevalence(len(failure_like), n_raw_attempt_metadata),
                    "notes": "Not claimed for final-only DiffSBDD stage 1 source outputs." if final_only else None,
                },
                "evaluable_only_molecular_prevalence": {
                    "status": "descriptive_selected_scope_only" if final_only else "available",
                    "denominator": n_evaluable,
                    "failure_like_count": sum(1 for label in evaluable if label.get("primary_label") != "unknown"),
                    "prevalence": prevalence(sum(1 for label in evaluable if label.get("primary_label") != "unknown"), n_evaluable),
                },
                "selected_output_residual_prevalence": {
                    "status": "available",
                    "denominator": n_final,
                    "failure_like_count": len(failure_like),
                    "prevalence": prevalence(len(failure_like), n_final),
                    "primary_label_counts": count_by(labels, "primary_label"),
                },
            },
            "claim_boundary": "selected_output_residual_audit_not_raw_failure_prevalence"
            if final_only
            else "specified_scope_only_no_global_prevalence",
            "notes": "These summaries do not claim DiffSBDD global failure prevalence, official reproduction, clean-test generalization or repair benchmark results.",
        },
        PREVALENCE_SUMMARY_SCHEMA_PATH,
    )
    return label_summary, prevalence_summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", required=True)
    args = parser.parse_args()
    run_root = Path(args.run_root).resolve()
    summaries_dir = run_root / "summaries"
    summaries_dir.mkdir(parents=True, exist_ok=True)
    label_summary, prevalence_summary = build_summaries(run_root)
    write_json_with_schema(summaries_dir / "label_summary.json", label_summary, LABEL_SUMMARY_SCHEMA_PATH)
    write_json_with_schema(summaries_dir / "prevalence_summary.json", prevalence_summary, PREVALENCE_SUMMARY_SCHEMA_PATH)
    print({"run_root": str(run_root), "labels": label_summary["counts"]["num_labels"]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
