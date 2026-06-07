#!/usr/bin/env python3
"""Write paper-ready result tables for contact-degraded local-edit experiments."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def load_rows(path: str) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return list(data.get("rows", data.get("metrics", [])))


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "--"
    if isinstance(value, str):
        return value
    return f"{float(value):.{digits}f}"


def write_markdown(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def main() -> int:
    comparison = load_rows("outputs/20260602-02-contact-degraded-policy-variants/metrics/official_eval_contact_degraded_multiseed_learned_policy_comparison.json")
    main_roles = {
        "no_feedback_budget1_reference",
        "rerank_budget1_reference",
        "classified_budget1",
        "budgeted_learned_budget10",
        "editable_search_budget10_reference",
        "best_of_n_higher_budget_reference",
        "direct_regeneration_higher_budget_reference",
    }
    role_labels = {
        "no_feedback_budget1_reference": "No-feedback",
        "rerank_budget1_reference": "Rerank-only",
        "classified_budget1": "Classified feedback",
        "budgeted_learned_budget10": "Budgeted learned feedback",
        "editable_search_budget10_reference": "Editable-contact search",
        "best_of_n_higher_budget_reference": "Best-of-N",
        "direct_regeneration_higher_budget_reference": "Direct regeneration",
        "shuffled_learned_budget1": "Shuffled learned",
        "shuffled_ridge_budget1": "Shuffled ridge",
        "learned_budget1": "Learned feedback",
        "ridge_budget1": "Ridge feedback",
        "shuffled_budgeted_learned_budget10": "Shuffled budgeted learned",
        "editable_full_budget10_reference": "Full editable search",
    }
    main_rows = []
    for row in comparison:
        if row["comparison_role"] not in main_roles:
            continue
        budget = row["mean_internal_candidate_budget"]
        if float(budget) > 10.0:
            budget_label = f"{float(budget):.1f} ref"
        else:
            budget_label = fmt(budget, 0)
        main_rows.append(
            [
                role_labels[row["comparison_role"]],
                budget_label,
                fmt(row["official_plip_recovery_gain"]),
                fmt(row["official_plip_similarity_gain"]),
                fmt(row["vina_score_only_energy"]),
                str(row["plip_error_count"]),
                str(row["vina_error_count"]),
            ]
        )
    headers = ["Method", "Internal budget", "PLIP recovery gain", "PLIP similarity gain", "Vina score-only", "PLIP errors", "Vina errors"]
    write_markdown(Path("outputs/20260602-03-paper-ready-contact-degraded-reporting/tables/paper_contact_degraded_main_results.md"), headers, main_rows)
    write_csv(Path("outputs/20260602-03-paper-ready-contact-degraded-reporting/tables/paper_contact_degraded_main_results.csv"), headers, main_rows)

    ablation_roles = {
        "no_feedback_budget1_reference",
        "shuffled_learned_budget1",
        "learned_budget1",
        "shuffled_ridge_budget1",
        "ridge_budget1",
        "classified_budget1",
        "shuffled_budgeted_learned_budget10",
        "budgeted_learned_budget10",
        "editable_search_budget10_reference",
    }
    ablation_rows = []
    for row in comparison:
        if row["comparison_role"] not in ablation_roles:
            continue
        ablation_rows.append(
            [
                role_labels[row["comparison_role"]],
                fmt(row["mean_internal_candidate_budget"], 0),
                fmt(row["official_plip_recovery_gain"]),
                fmt(row["official_plip_similarity_gain"]),
                fmt(row["vina_score_only_energy"]),
            ]
        )
    ablation_headers = ["Method", "Budget", "PLIP recovery gain", "PLIP similarity gain", "Vina score-only"]
    write_markdown(Path("outputs/20260602-03-paper-ready-contact-degraded-reporting/tables/paper_contact_degraded_feedback_ablation.md"), ablation_headers, ablation_rows)
    write_csv(Path("outputs/20260602-03-paper-ready-contact-degraded-reporting/tables/paper_contact_degraded_feedback_ablation.csv"), ablation_headers, ablation_rows)
    print("Wrote paper tables")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
