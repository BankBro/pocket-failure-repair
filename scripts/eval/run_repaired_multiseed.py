#!/usr/bin/env python3
"""Run smoke repaired-molecule baselines over multiple seeds."""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from pfr.utils.io import ensure_parent, load_yaml, write_json


ROOT = Path(__file__).resolve().parents[2]


def run_command(args: list[str]) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def write_seed_config(base_config_path: Path, seed: int, output_dir: Path, config_dir: Path) -> tuple[Path, Path]:
    config = copy.deepcopy(load_yaml(base_config_path))
    config["seed"] = seed
    config["output"]["repaired_candidates_path"] = str(output_dir / f"repaired_candidates_seed_{seed}.jsonl")
    config["output"]["repaired_molecules_dir"] = str(output_dir / f"molecules_seed_{seed}")
    config_path = config_dir / f"repair_seed_{seed}.yaml"
    ensure_parent(config_path)
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")

    eval_config = {
        "name": f"repaired_smoke_seed_{seed}",
        "seed": seed,
        "input": {"repaired_candidates_path": config["output"]["repaired_candidates_path"]},
        "output": {
            "evaluated_repaired_path": str(output_dir / f"evaluated_repaired_seed_{seed}.jsonl"),
            "metrics_path": str(output_dir / f"repaired_metrics_seed_{seed}.json"),
            "table_path": str(output_dir / f"repaired_metrics_seed_{seed}.csv"),
        },
    }
    eval_config_path = config_dir / f"eval_repaired_seed_{seed}.yaml"
    eval_config_path.write_text(json.dumps(eval_config, indent=2, ensure_ascii=False), encoding="utf-8")
    return config_path, eval_config_path


def load_metrics(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))["metrics"]


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def aggregate(seed_metrics: dict[int, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    by_baseline: dict[str, list[dict[str, Any]]] = {}
    for rows in seed_metrics.values():
        for row in rows:
            by_baseline.setdefault(str(row["baseline"]), []).append(row)
    summaries: list[dict[str, Any]] = []
    for baseline, rows in sorted(by_baseline.items()):
        summaries.append(
            {
                "baseline": baseline,
                "num_seeds": len(rows),
                "mean_repaired_success_rate": mean([float(row["repaired_success_rate"]) for row in rows]),
                "mean_clash_free_rate": mean([float(row["clash_free_rate"]) for row in rows]),
                "mean_scaffold_preservation": mean([float(row["scaffold_preservation"]) for row in rows]),
                "mean_anchor_validity": mean([float(row["anchor_validity"]) for row in rows]),
                "mean_editable_validity": mean([float(row["editable_validity"]) for row in rows]),
                "mean_clash_count": mean([float(row["mean_clash_count"]) for row in rows]),
                "mean_posebusters_like_pass": mean([float(row["mean_posebusters_like_pass"]) for row in rows if row.get("mean_posebusters_like_pass") is not None]),
                "mean_contact_fingerprint_similarity": mean([float(row["mean_contact_fingerprint_similarity"]) for row in rows if row.get("mean_contact_fingerprint_similarity") is not None]),
                "mean_contact_recovery": mean([float(row["mean_contact_recovery"]) for row in rows if row.get("mean_contact_recovery") is not None]),
                "mean_vina_like_proxy": mean([float(row["mean_vina_like_proxy"]) for row in rows if row.get("mean_vina_like_proxy") is not None]),
                "mean_ligand_efficiency_proxy": mean([float(row["mean_ligand_efficiency_proxy"]) for row in rows if row.get("mean_ligand_efficiency_proxy") is not None]),
                "mean_sa_fallback": mean([float(row["mean_sa_fallback"]) for row in rows if row.get("mean_sa_fallback") is not None]),
                "seed_values": {str(seed): next(r for r in metrics if r["baseline"] == baseline)["repaired_success_rate"] for seed, metrics in seed_metrics.items()},
            }
        )
    return summaries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repair-config", default="experiments/20260601-01-smoke-repair-baselines/configs/resolved/baselines/repair_smoke.yaml")
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    parser.add_argument("--output-dir", default="outputs/20260601-01-smoke-repair-baselines/processed/multiseed_repaired")
    parser.add_argument("--config-dir", default=None, help="Directory for resolved per-seed repair/eval config snapshots. Defaults to experiments/<experiment_id>/configs/resolved/multiseed_repaired when --output-dir is under outputs/<experiment_id>/.")
    parser.add_argument("--summary-path", default="outputs/20260601-01-smoke-repair-baselines/metrics/repaired_smoke_multiseed.json")
    args = parser.parse_args()

    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.config_dir is None:
        output_parts = Path(args.output_dir).parts
        if len(output_parts) >= 2 and output_parts[0] == "outputs":
            config_dir = ROOT / "experiments" / output_parts[1] / "configs" / "resolved" / "multiseed_repaired"
        else:
            config_dir = output_dir / "configs"
    else:
        config_dir = ROOT / args.config_dir
    config_dir.mkdir(parents=True, exist_ok=True)
    seed_metrics: dict[int, list[dict[str, Any]]] = {}
    for seed in args.seeds:
        repair_config, eval_config = write_seed_config(ROOT / args.repair_config, seed, output_dir, config_dir)
        run_command([sys.executable, "scripts/eval/repair_baselines.py", "--config", str(repair_config)])
        run_command([sys.executable, "scripts/eval/eval_repaired.py", "--config", str(eval_config)])
        seed_metrics[seed] = load_metrics(output_dir / f"repaired_metrics_seed_{seed}.json")

    summary = {
        "name": "repaired_smoke_multiseed",
        "seeds": args.seeds,
        "aggregate_metrics": aggregate(seed_metrics),
        "notes": "Multi-seed smoke over deterministic/rule/geometry/linear refinement baselines; seeds affect local translation/editable-shift candidate pools while feedback_linear_refinement remains a leave-one-complex supervised smoke sanity check.",
    }
    write_json(ROOT / args.summary_path, summary)
    print(f"Wrote multi-seed repaired summary to {args.summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
