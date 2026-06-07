#!/usr/bin/env python3
"""Summarize smoke metrics into auditable outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pfr.utils.io import ensure_parent, load_yaml, read_jsonl, write_json


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_svg_bar_chart(path: str | Path, rows: list[dict[str, Any]], metric: str) -> Path:
    output_path = ensure_parent(path)
    width = 720
    height = 260
    margin_left = 170
    bar_height = 28
    gap = 18
    max_width = 460
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="20" y="30" font-family="sans-serif" font-size="18" font-weight="bold">Smoke placeholder success rates</text>',
        '<text x="20" y="52" font-family="sans-serif" font-size="12" fill="#666">Pipeline validation only; not chemistry-aware model evidence.</text>',
    ]
    y = 82
    for row in rows:
        value = row.get(metric)
        value_float = float(value or 0.0)
        bar_width = int(max_width * value_float)
        label = row.get("baseline", "unknown")
        lines.append(f'<text x="20" y="{y + 19}" font-family="monospace" font-size="13">{label}</text>')
        lines.append(f'<rect x="{margin_left}" y="{y}" width="{bar_width}" height="{bar_height}" fill="#4c78a8"/>')
        lines.append(f'<rect x="{margin_left}" y="{y}" width="{max_width}" height="{bar_height}" fill="none" stroke="#ccc"/>')
        lines.append(f'<text x="{margin_left + max_width + 10}" y="{y + 19}" font-family="sans-serif" font-size="13">{value_float:.2f}</text>')
        y += bar_height + gap
    lines.append("</svg>")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_yaml(args.config)
    metrics = load_json(config["input"]["metrics_path"])
    rows = metrics.get("metrics", [])
    repaired_metrics = (
        load_json(config["input"].get("repaired_metrics_path", ""))
        if config["input"].get("repaired_metrics_path")
        else {}
    )
    repaired_metric_rows = repaired_metrics.get("metrics", [])
    repaired_evaluations = (
        read_jsonl(config["input"].get("repaired_evaluations_path", ""))
        if config["input"].get("repaired_evaluations_path")
        else []
    )
    repaired_eval_by_repair_id = {row.get("repair_id"): row for row in repaired_evaluations}
    repaired_eval_by_candidate: dict[str, list[dict[str, Any]]] = {}
    for row in repaired_evaluations:
        repaired_eval_by_candidate.setdefault(str(row.get("candidate_id")), []).append(row)
    summary = {
        "name": config.get("name"),
        "result_type": config.get("labels", {}).get("result_type"),
        "warning": config.get("labels", {}).get("warning"),
        "num_baselines": len(rows),
        "num_evaluable_for_repair": metrics.get("num_evaluable_for_repair"),
        "non_evaluable_feedback_records": max(
            0, int(metrics.get("num_feedback_records") or 0) - int(metrics.get("num_evaluable_for_repair") or 0)
        ),
        "baselines": [row.get("baseline") for row in rows],
        "success_rates": {row.get("baseline"): row.get("same_budget_success_rate") for row in rows},
        "repaired_molecule_success_rates": {
            row.get("baseline"): row.get("repaired_success_rate") for row in repaired_metric_rows
        },
        "repaired_molecule_metrics_path": config["input"].get("repaired_metrics_path"),
        "repaired_failure_type_metrics_path": config["input"].get("repaired_failure_type_metrics_path"),
        "repaired_num_records": repaired_metrics.get("num_repaired_records"),
        "notes": metrics.get("notes"),
    }
    candidates = read_jsonl(config["input"].get("candidates_path", "")) if config["input"].get("candidates_path") else []
    feedback = read_jsonl(config["input"].get("feedback_path", "")) if config["input"].get("feedback_path") else []
    feedback_by_id = {row.get("candidate_id"): row for row in feedback}
    repaired_candidates = (
        read_jsonl(config["input"].get("repaired_candidates_path", ""))
        if config["input"].get("repaired_candidates_path")
        else []
    )
    repairs_by_candidate: dict[str, list[dict[str, Any]]] = {}
    for repair in repaired_candidates:
        repair_eval = repaired_eval_by_repair_id.get(repair.get("repair_id"), {})
        repairs_by_candidate.setdefault(str(repair.get("candidate_id")), []).append(
            {**repair, "repaired_evaluation": repair_eval}
        )
    case_rows = []
    for candidate in candidates:
        feedback_row = feedback_by_id.get(candidate.get("candidate_id"), {})
        case_rows.append(
            {
                "candidate_id": candidate.get("candidate_id"),
                "complex_id": candidate.get("complex_id"),
                "failure_type": candidate.get("failure_type"),
                "failed_ligand_path": candidate.get("failed_ligand_path"),
                "repair_outputs": repairs_by_candidate.get(str(candidate.get("candidate_id")), []),
                "scaffold_smiles": candidate.get("scaffold_smiles"),
                "source": candidate.get("source"),
                "feedback_source": feedback_row.get("source"),
                "sample_quality": feedback_row.get("sample_quality", {}),
                "repair_evaluable": feedback_row.get("sample_quality", {}).get("evaluable_for_repair"),
                "repair_exclusion_reasons": feedback_row.get("sample_quality", {}).get("exclusion_reasons", []),
                "global": feedback_row.get("global", {}),
            }
        )
    cases = {
        "result_type": summary["result_type"],
        "warning": summary["warning"],
        "failed_candidate_cases": case_rows,
        "notes": "Failed molecule SDF files and repaired baseline SDF files are generated for smoke candidates; repaired evaluations are RDKit/geometry checks on rule baselines, not learned-model evidence.",
    }

    write_json(config["output"]["summary_path"], summary)
    write_json(config["output"]["cases_path"], cases)
    write_svg_bar_chart(config["output"]["figure_path"], rows, "same_budget_success_rate")
    print(f"Wrote summary to {config['output']['summary_path']}")
    print(f"Wrote cases to {config['output']['cases_path']}")
    print(f"Wrote figure to {config['output']['figure_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
