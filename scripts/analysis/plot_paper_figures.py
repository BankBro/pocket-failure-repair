#!/usr/bin/env python3
"""Write paper-ready SVG figures for contact-degraded local-edit results."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def load_rows(path: str) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return list(data.get("rows", data.get("metrics", [])))


def svg_bar_chart(
    path: Path,
    title: str,
    labels: list[str],
    values: list[float],
    colors: list[str],
    ylabel: str = "Official PLIP recovery gain",
    width: int = 980,
    height: int = 520,
) -> None:
    margin_left = 95
    margin_right = 30
    margin_top = 70
    margin_bottom = 145
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    min_v = min(0.0, min(values))
    max_v = max(0.0, max(values))
    pad = max(0.01, (max_v - min_v) * 0.15)
    min_v -= pad
    max_v += pad

    def y(value: float) -> float:
        return margin_top + (max_v - value) / (max_v - min_v) * plot_h

    n = len(values)
    gap = 18
    bar_w = max(18, (plot_w - gap * (n - 1)) / n)
    zero_y = y(0.0)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="32" text-anchor="middle" font-family="Arial" font-size="22" font-weight="bold">{html.escape(title)}</text>',
        f'<text x="22" y="{margin_top + plot_h/2}" transform="rotate(-90 22 {margin_top + plot_h/2})" text-anchor="middle" font-family="Arial" font-size="14">{html.escape(ylabel)}</text>',
        f'<line x1="{margin_left}" y1="{zero_y:.2f}" x2="{width-margin_right}" y2="{zero_y:.2f}" stroke="#333" stroke-width="1.5"/>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top+plot_h}" stroke="#333" stroke-width="1"/>',
    ]
    for tick in [-0.15, -0.10, -0.05, 0.0, 0.05]:
        if min_v <= tick <= max_v:
            ty = y(tick)
            lines.append(f'<line x1="{margin_left-5}" y1="{ty:.2f}" x2="{width-margin_right}" y2="{ty:.2f}" stroke="#ddd" stroke-width="1"/>')
            lines.append(f'<text x="{margin_left-10}" y="{ty+4:.2f}" text-anchor="end" font-family="Arial" font-size="12">{tick:.2f}</text>')
    for i, (label, value, color) in enumerate(zip(labels, values, colors)):
        x = margin_left + i * (bar_w + gap)
        top = y(max(value, 0.0))
        bottom = y(min(value, 0.0))
        h = max(1.0, bottom - top)
        lines.append(f'<rect x="{x:.2f}" y="{top:.2f}" width="{bar_w:.2f}" height="{h:.2f}" fill="{color}"/>')
        lines.append(f'<text x="{x + bar_w/2:.2f}" y="{top - 7 if value >= 0 else bottom + 17:.2f}" text-anchor="middle" font-family="Arial" font-size="12">{value:+.4f}</text>')
        lx = x + bar_w / 2
        ly = margin_top + plot_h + 20
        safe = html.escape(label)
        lines.append(f'<text x="{lx:.2f}" y="{ly:.2f}" transform="rotate(45 {lx:.2f} {ly:.2f})" text-anchor="start" font-family="Arial" font-size="12">{safe}</text>')
    lines.append('</svg>')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = load_rows("outputs/20260602-02-contact-degraded-policy-variants/metrics/official_eval_contact_degraded_multiseed_learned_policy_comparison.json")
    by_role = {row["comparison_role"]: row for row in rows}
    main_roles = [
        ("No-feedback", "no_feedback_budget1_reference", "#9aa0a6"),
        ("Rerank", "rerank_budget1_reference", "#9aa0a6"),
        ("Classified", "classified_budget1", "#4e79a7"),
        ("Budgeted learned", "budgeted_learned_budget10", "#59a14f"),
        ("Editable search", "editable_search_budget10_reference", "#f28e2b"),
        ("Best-of-N", "best_of_n_higher_budget_reference", "#e15759"),
        ("Direct regen", "direct_regeneration_higher_budget_reference", "#e15759"),
    ]
    svg_bar_chart(
        Path("outputs/20260602-03-paper-ready-contact-degraded-reporting/figures/paper_contact_degraded_main_results.svg"),
        "Contact-degraded local-edit official PLIP recovery",
        [label for label, _, _ in main_roles],
        [float(by_role[role]["official_plip_recovery_gain"]) for _, role, _ in main_roles],
        [color for _, _, color in main_roles],
    )
    ablation_roles = [
        ("No-feedback", "no_feedback_budget1_reference", "#9aa0a6"),
        ("Shuf learned", "shuffled_learned_budget1", "#bab0ab"),
        ("Learned", "learned_budget1", "#4e79a7"),
        ("Shuf ridge", "shuffled_ridge_budget1", "#bab0ab"),
        ("Ridge", "ridge_budget1", "#4e79a7"),
        ("Classified", "classified_budget1", "#4e79a7"),
        ("Shuf budgeted", "shuffled_budgeted_learned_budget10", "#bab0ab"),
        ("Budgeted", "budgeted_learned_budget10", "#59a14f"),
        ("Editable search", "editable_search_budget10_reference", "#f28e2b"),
    ]
    svg_bar_chart(
        Path("outputs/20260602-03-paper-ready-contact-degraded-reporting/figures/paper_contact_degraded_feedback_ablation.svg"),
        "Diagnostic feedback ablation",
        [label for label, _, _ in ablation_roles],
        [float(by_role[role]["official_plip_recovery_gain"]) for _, role, _ in ablation_roles],
        [color for _, _, color in ablation_roles],
        height=560,
    )
    case = json.loads(Path("outputs/20260602-03-paper-ready-contact-degraded-reporting/metrics/paper_case_contact_degraded_3ert_seed2.json").read_text(encoding="utf-8"))
    labels = []
    values = []
    colors = []
    label_map = {
        "no_feedback_repair": "No-feedback",
        "rerank_only": "Rerank",
        "feedback_classified_editable_contact_policy": "Classified",
        "feedback_learned_editable_contact_policy": "Learned",
        "feedback_budgeted_learned_editable_contact_policy": "Budgeted",
        "feedback_editable_contact_policy": "Editable search",
        "feedback_editable_full_policy": "Full search",
    }
    for row in case["methods"]:
        labels.append(label_map.get(row["baseline"], row["baseline"]))
        values.append(float(row["plip_repaired_interaction_count"]))
        colors.append("#4e79a7" if row["plip_interaction_recovery_gain"] else "#9aa0a6")
    svg_bar_chart(
        Path("outputs/20260602-03-paper-ready-contact-degraded-reporting/figures/paper_case_contact_degraded_3ert_seed2_interactions.svg"),
        "3ERT seed2 case: repaired PLIP interaction count",
        labels,
        values,
        colors,
        ylabel="Repaired PLIP interaction count",
        height=520,
    )
    print("Wrote paper SVG figures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
