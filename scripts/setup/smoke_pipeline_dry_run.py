#!/usr/bin/env python3
"""Dry-run the intended smoke pipeline without requiring molecular data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


STEPS = [
    {
        "name": "build_rgroup_dataset",
        "config": "configs/data/builds/rgroup_smoke.yaml",
        "script": "scripts/data/build_rgroup_dataset.py",
        "outputs": ["data/datasets/rgroup_smoke/entries/index.jsonl", "data/datasets/rgroup_smoke/splits/rgroup_smoke_split_v1.json"],
    },
    {
        "name": "generate_failed_candidates",
        "config": "experiments/20260531-01-smoke-file-pipeline/configs/resolved/data/failed_candidate_smoke.yaml",
        "script": "scripts/data/generate_failed_candidates.py",
        "outputs": ["outputs/20260531-01-smoke-file-pipeline/processed/failed_candidates_smoke.jsonl"],
    },
    {
        "name": "extract_feedback",
        "config": "experiments/20260531-01-smoke-file-pipeline/configs/resolved/feedback/smoke.yaml",
        "script": "scripts/data/extract_feedback.py",
        "outputs": ["outputs/20260531-01-smoke-file-pipeline/processed/feedback_smoke.jsonl"],
    },
    {
        "name": "eval_baselines",
        "config": "experiments/20260531-01-smoke-file-pipeline/configs/resolved/baselines/smoke.yaml",
        "script": "scripts/eval/eval_baselines.py",
        "outputs": ["outputs/20260531-01-smoke-file-pipeline/metrics/baselines_smoke.json", "outputs/20260531-01-smoke-file-pipeline/tables/baselines_smoke.csv"],
    },
]


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def check_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return load_yaml(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-plan", type=Path, default=None, help="Optional path for writing the dry-run plan. If omitted, the plan is printed only.")
    args = parser.parse_args()

    plan: list[dict[str, Any]] = []
    for step in STEPS:
        config_path = Path(step["config"])
        config = check_config(config_path)
        entry = {
            "name": step["name"],
            "script": step["script"],
            "config": str(config_path),
            "config_name": config.get("name"),
            "outputs": step["outputs"],
            "command": f"python {step['script']} --config {config_path}",
            "script_exists": Path(step["script"]).exists(),
        }
        plan.append(entry)

    if args.write_plan is not None:
        args.write_plan.parent.mkdir(parents=True, exist_ok=True)
        args.write_plan.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("Smoke pipeline dry-run plan:")
    for entry in plan:
        status = "ready" if entry["script_exists"] else "script pending"
        print(f"  - {entry['name']}: {status}")
        print(f"    {entry['command']}")
    if args.write_plan is not None:
        print(f"\nPlan written to {args.write_plan}")
    else:
        print("\nPlan not written; pass --write-plan to persist it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
