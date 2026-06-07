#!/usr/bin/env python3
"""Run multi-seed contact-degraded local-edit repair experiments."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import yaml

from pfr.utils.io import read_jsonl


BASELINES = [
    "direct_regeneration",
    "best_of_n",
    "rerank_only",
    "no_failed_candidate_policy",
    "no_feedback_repair",
    "feedback_editable_contact_policy",
    "feedback_editable_geometry_only_policy",
    "feedback_editable_interaction_only_policy",
    "feedback_editable_global_only_policy",
    "feedback_editable_full_policy",
    "feedback_classified_editable_contact_policy",
    "feedback_directional_classified_editable_contact_policy",
    "feedback_learned_editable_contact_policy",
    "feedback_directional_learned_editable_contact_policy",
    "feedback_scaled_learned_editable_contact_policy",
    "feedback_budgeted_learned_editable_contact_policy",
    "feedback_ridge_editable_contact_policy",
    "feedback_learned_editable_contact_shuffled_policy",
    "feedback_budgeted_learned_editable_contact_shuffled_policy",
    "feedback_ridge_editable_contact_shuffled_policy",
    "feedback_geometry_refinement",
    "feedback_learned_geometry_policy",
    "feedback_kernel_geometry_policy",
    "feedback_knn_geometry_policy",
    "feedback_residual_ensemble_policy",
    "feedback_linear_refinement",
    "coordinate_rollback",
    "identity_failed_candidate",
    "feedback_rule_repair",
]


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def read_metrics(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    metrics = data.get("metrics", [])
    return metrics if isinstance(metrics, list) else []


def mean(values: list[float | int | None]) -> float | None:
    numeric = [float(value) for value in values if value is not None]
    if not numeric:
        return None
    return sum(numeric) / len(numeric)


def aggregate(seed_metrics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in seed_metrics:
        grouped.setdefault(str(row.get("baseline")), []).append(row)
    rows: list[dict[str, Any]] = []
    for baseline, subset in sorted(grouped.items()):
        rows.append(
            {
                "baseline": baseline,
                "num_seeds": len({row.get("seed") for row in subset}),
                "total_repaired": sum(int(row.get("num_repaired") or 0) for row in subset),
                "mean_repaired_success_rate": mean([row.get("repaired_success_rate") for row in subset]),
                "mean_repair_gain_success_rate": mean([row.get("repair_gain_success_rate") for row in subset]),
                "mean_contact_recovery_gain": mean([row.get("mean_contact_recovery_gain") for row in subset]),
                "mean_contact_similarity_gain": mean([row.get("mean_contact_fingerprint_similarity_gain") for row in subset]),
                "mean_anchor_error_reduction": mean([row.get("mean_anchor_error_reduction") for row in subset]),
                "mean_clash_count_reduction": mean([row.get("mean_clash_count_reduction") for row in subset]),
                "source": "contact_degraded_local_edit_multiseed_summary",
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", default="0,1,2")
    parser.add_argument("--dataset", default="data/datasets/rgroup_smoke_plus/entries/index.jsonl")
    parser.add_argument("--output-dir", default="outputs/20260601-05-contact-degraded-local-edit-core/metrics/contact_degraded_multiseed")
    args = parser.parse_args()

    seeds = [int(seed.strip()) for seed in args.seeds.split(",") if seed.strip()]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    all_seed_metrics: list[dict[str, Any]] = []
    run_records: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="contact_degraded_multiseed_") as tmp_name:
        tmp_dir = Path(tmp_name)
        for seed in seeds:
            data_config = {
                "name": f"failed_candidate_smoke_plus_contact_degraded_local_edit_seed{seed}",
                "seed": seed,
                "input": {"dataset_path": args.dataset},
                "output": {
                    "candidates_path": f"outputs/20260601-05-contact-degraded-local-edit-core/processed/failed_candidates_smoke_plus_contact_degraded_local_edit_seed{seed}.jsonl",
                    "failed_molecules_dir": f"outputs/20260601-05-contact-degraded-local-edit-core/processed/failed_molecules/smoke_plus_contact_degraded_local_edit_failed_seed{seed}",
                },
                "limits": {"max_per_example": 3, "min_contact_recovery_loss": 0.03},
            }
            feedback_config = {
                "name": f"feedback_smoke_plus_contact_degraded_local_edit_seed{seed}",
                "seed": seed,
                "input": {"candidates_path": data_config["output"]["candidates_path"]},
                "output": {"feedback_path": f"outputs/20260601-05-contact-degraded-local-edit-core/processed/feedback_smoke_plus_contact_degraded_local_edit_seed{seed}.jsonl"},
            }
            repair_config = {
                "name": f"repair_smoke_plus_contact_degraded_local_edit_seed{seed}",
                "seed": seed,
                "input": {
                    "candidates_path": data_config["output"]["candidates_path"],
                    "feedback_path": feedback_config["output"]["feedback_path"],
                },
                "output": {
                    "repaired_candidates_path": f"outputs/20260601-05-contact-degraded-local-edit-core/processed/repaired_candidates_smoke_plus_contact_degraded_local_edit_seed{seed}.jsonl",
                    "repaired_molecules_dir": f"outputs/20260601-05-contact-degraded-local-edit-core/processed/repaired_molecules/smoke_plus_contact_degraded_local_edit_repaired_seed{seed}",
                },
                "baselines": BASELINES,
            }
            eval_config = {
                "name": f"repaired_smoke_plus_contact_degraded_local_edit_seed{seed}",
                "seed": seed,
                "input": {"repaired_candidates_path": repair_config["output"]["repaired_candidates_path"]},
                "output": {
                    "evaluated_repaired_path": f"outputs/20260601-05-contact-degraded-local-edit-core/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed{seed}.jsonl",
                    "metrics_path": f"outputs/20260601-05-contact-degraded-local-edit-core/metrics/repaired_smoke_plus_contact_degraded_local_edit_seed{seed}.json",
                    "table_path": f"outputs/20260601-05-contact-degraded-local-edit-core/tables/repaired_smoke_plus_contact_degraded_local_edit_seed{seed}.csv",
                },
            }
            paths = {
                "data": tmp_dir / f"data_seed{seed}.yaml",
                "feedback": tmp_dir / f"feedback_seed{seed}.yaml",
                "repair": tmp_dir / f"repair_seed{seed}.yaml",
                "eval": tmp_dir / f"eval_seed{seed}.yaml",
            }
            write_yaml(paths["data"], data_config)
            write_yaml(paths["feedback"], feedback_config)
            write_yaml(paths["repair"], repair_config)
            write_yaml(paths["eval"], eval_config)
            run(["python", "scripts/data/generate_contact_degraded_local_edit_failures.py", "--config", str(paths["data"])])
            run(["python", "scripts/data/extract_feedback.py", "--config", str(paths["feedback"])])
            run(["python", "scripts/eval/repair_baselines.py", "--config", str(paths["repair"])])
            run(["python", "scripts/eval/eval_repaired.py", "--config", str(paths["eval"])])
            candidate_count = len(read_jsonl(data_config["output"]["candidates_path"]))
            metrics_path = Path(eval_config["output"]["metrics_path"])
            metrics = read_metrics(metrics_path)
            for row in metrics:
                row["seed"] = seed
                all_seed_metrics.append(row)
            run_records.append(
                {
                    "seed": seed,
                    "candidate_count": candidate_count,
                    "metrics_path": str(metrics_path),
                    "candidates_path": data_config["output"]["candidates_path"],
                    "repaired_candidates_path": repair_config["output"]["repaired_candidates_path"],
                }
            )

    summary = {
        "name": "contact_degraded_local_edit_multiseed_summary",
        "seeds": seeds,
        "runs": run_records,
        "metrics": aggregate(all_seed_metrics),
        "seed_metrics": all_seed_metrics,
    }
    output_path = output_dir / "summary.json"
    output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    csv_path = output_dir / "summary.csv"
    rows = summary["metrics"]
    if rows:
        import csv

        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    print(f"Wrote multiseed summary to {output_path}")
    print(f"Wrote multiseed table to {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
