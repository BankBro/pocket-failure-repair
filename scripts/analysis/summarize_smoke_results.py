#!/usr/bin/env python3
"""Summarize smoke metrics into auditable outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pfr.utils.io import ensure_parent, load_yaml, write_json


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
    summary = {
        "name": config.get("name"),
        "result_type": config.get("labels", {}).get("result_type"),
        "warning": config.get("labels", {}).get("warning"),
        "num_baselines": len(rows),
        "num_feedback_records": metrics.get("num_feedback_records"),
        "baselines": [row.get("baseline") for row in rows],
        "success_rates": {row.get("baseline"): row.get("same_budget_success_rate") for row in rows},
        "notes": metrics.get("notes"),
    }
    cases = {
        "result_type": summary["result_type"],
        "warning": summary["warning"],
        "success_cases": [],
        "failure_cases": [],
        "notes": "Molecule-level cases are not available until chemistry-aware repair is implemented.",
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
