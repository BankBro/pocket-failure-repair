import json
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ENV = {"PYTHONPATH": str(ROOT / "src")}


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        env={**ENV},
        text=True,
        capture_output=True,
        check=True,
    )


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_smoke_pipeline_with_toy_complex(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw" / "toy_complex"
    raw_dir.mkdir(parents=True)
    ligand_path = raw_dir / "toy_ligand.sdf"
    protein_path = raw_dir / "toy_protein.pdb"
    ligand_path.write_text("toy ligand placeholder\n", encoding="utf-8")
    protein_path.write_text("toy protein placeholder\n", encoding="utf-8")

    dataset_path = tmp_path / "processed" / "rgroup_smoke.jsonl"
    split_path = tmp_path / "splits" / "rgroup_smoke_split.json"
    candidates_path = tmp_path / "processed" / "failed_candidates_smoke.jsonl"
    feedback_path = tmp_path / "processed" / "feedback_smoke.jsonl"
    metrics_path = tmp_path / "outputs" / "metrics" / "baselines_smoke.json"
    table_path = tmp_path / "outputs" / "tables" / "baselines_smoke.csv"

    rgroup_config = tmp_path / "configs" / "rgroup.yaml"
    failed_config = tmp_path / "configs" / "failed.yaml"
    feedback_config = tmp_path / "configs" / "feedback.yaml"
    baseline_config = tmp_path / "configs" / "baseline.yaml"

    write_yaml(
        rgroup_config,
        {
            "name": "toy_rgroup",
            "seed": 0,
            "input": {"complexes_dir": str(tmp_path / "raw"), "max_complexes": 1},
            "output": {"dataset_path": str(dataset_path), "split_path": str(split_path)},
        },
    )
    write_yaml(
        failed_config,
        {
            "name": "toy_failed",
            "seed": 0,
            "input": {"dataset_path": str(dataset_path)},
            "output": {"candidates_path": str(candidates_path)},
            "failure_types": ["clash", "anchor_invalid"],
            "limits": {"candidates_per_example": 2},
        },
    )
    write_yaml(
        feedback_config,
        {
            "name": "toy_feedback",
            "input": {"candidates_path": str(candidates_path)},
            "output": {"feedback_path": str(feedback_path)},
        },
    )
    write_yaml(
        baseline_config,
        {
            "name": "toy_baseline",
            "seed": 0,
            "input": {"feedback_path": str(feedback_path)},
            "output": {"metrics_path": str(metrics_path), "table_path": str(table_path)},
            "baselines": ["best_of_n", "rerank_only"],
        },
    )

    run_script("scripts/data/build_rgroup_dataset.py", "--config", str(rgroup_config))
    run_script("scripts/data/generate_failed_candidates.py", "--config", str(failed_config))
    run_script("scripts/data/extract_feedback.py", "--config", str(feedback_config))
    run_script("scripts/eval/eval_baselines.py", "--config", str(baseline_config))

    dataset = read_jsonl(dataset_path)
    candidates = read_jsonl(candidates_path)
    feedback = read_jsonl(feedback_path)
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    assert len(dataset) == 1
    assert dataset[0]["protein_path"] == str(protein_path)
    assert dataset[0]["ligand_path"] == str(ligand_path)
    assert len(candidates) == 2
    assert {row["failure_type"] for row in candidates} == {"clash", "anchor_invalid"}
    assert len(feedback) == 2
    assert any(row["geometry"]["clash_count"] == 1 for row in feedback)
    assert any(row["geometry"]["anchor_distance_error"] == 2.0 for row in feedback)
    assert metrics["num_feedback_records"] == 2
    assert [row["baseline"] for row in metrics["metrics"]] == ["best_of_n", "rerank_only"]
    assert table_path.exists()
