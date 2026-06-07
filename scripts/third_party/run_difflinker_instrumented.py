#!/usr/bin/env python3
"""Run DiffLinker through a lightweight output-capture wrapper.

This wrapper records command provenance and per-attempt metadata for a minimal
case-study trial. It does not modify DiffLinker sampling, decoding, filtering,
reranking, scoring, or candidate budget.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


RUN_BOUNDARY_LABEL = "instrumented_reproduction"
RESOURCE_BUDGET_VERSION = "pfr_third_party_audit_resource_budget_v1"
LABEL_PROTOCOL_VERSION = "pfr_failure_diagnosis_v0_1_draft"
RUN_METADATA_SCHEMA_VERSION = "run_metadata_v0_1"
RUN_METADATA_SCHEMA_PATH = "schemas/third_party_audit/run/run_metadata_v0_1.json"
SAMPLE_METADATA_SCHEMA_VERSION = "failure_sample_metadata_v0_1"
SAMPLE_METADATA_SCHEMA_PATH = "schemas/third_party_audit/samples/failure_sample_metadata_v0_1.json"
OUTPUT_MANIFEST_SCHEMA_VERSION = "output_manifest_v0_1"
OUTPUT_MANIFEST_SCHEMA_PATH = "schemas/third_party_audit/run/output_manifest_v0_1.json"


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def resolve_for_repo(value: str, repo: Path, current: Path) -> str:
    path = Path(value)
    if path.is_absolute():
        return str(path)
    if (current / path).exists():
        return str((current / path).resolve())
    if (repo / path).exists():
        return str((repo / path).resolve())
    return value


def find_output_files(captured_dir: Path) -> list[Path]:
    if not captured_dir.exists():
        return []
    return sorted([p for p in captured_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".sdf", ".xyz", ".smi"}])


def build_samples(
    *,
    run_id: str,
    method_commit: str | None,
    dataset_view_id: str,
    split_id: str,
    complex_id: str,
    n_budget: int,
    output_files: list[Path],
    exit_code: int | None,
) -> list[dict[str, Any]]:
    sdf_like = [p for p in output_files if p.suffix.lower() in {".sdf", ".xyz", ".smi"}]
    rows: list[dict[str, Any]] = []
    command_failed = exit_code not in (0, None)
    for index in range(max(n_budget, len(sdf_like))):
        artifact = sdf_like[index] if index < len(sdf_like) else None
        has_final = artifact is not None and not command_failed
        rows.append(
            {
                "schema_version": SAMPLE_METADATA_SCHEMA_VERSION,
                "schema_path": SAMPLE_METADATA_SCHEMA_PATH,
                "sample_id": f"difflinker_{dataset_view_id}_{complex_id}_{'final' if has_final else 'raw'}_{index}",
                "parent_sample_id": None,
                "lineage_id": f"{run_id}::{index}",
                "run_id": run_id,
                "method": "DiffLinker",
                "method_repo": "https://github.com/igashov/DiffLinker",
                "method_commit": method_commit,
                "run_boundary_label": RUN_BOUNDARY_LABEL,
                "dataset_name": "third_party_repo_examples_v1",
                "dataset_version": "cloned_repo_examples",
                "dataset_view_id": dataset_view_id,
                "split_id": split_id,
                "complex_id": complex_id,
                "pdb_id": None,
                "pocket_id": None,
                "stage": "final" if has_final else "raw",
                "sample_role": "final_output" if has_final else "generation_attempt",
                "sample_index": index,
                "molecule_path": str(artifact) if has_final else None,
                "pose_path": str(artifact) if has_final else None,
                "receptor_path": None,
                "raw_sample_id": None,
                "raw_sha256": sha256_file(artifact) if artifact else None,
                "normalized_sha256": None,
                "original_status": {
                    "status": "final" if has_final else ("failed" if command_failed else "unknown"),
                    "source_stage_name": "DiffLinker generate_with_pocket aggregate output directory",
                    "failure_reason": "command_exit_nonzero" if command_failed and not has_final else None,
                    "rejection_reason": None,
                    "rank": None,
                    "score": None,
                    "source_file": str(artifact) if artifact else None,
                },
                "audit_labels": {},
                "quality_flags": {"missing_final_output": not has_final, "pipeline_failure": bool(command_failed and not has_final)},
                "created_by_script_commit": None,
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--fragments", required=True)
    parser.add_argument("--pocket", default=None)
    parser.add_argument("--protein", default=None)
    parser.add_argument("--model", required=True)
    parser.add_argument("--linker-size", required=True)
    parser.add_argument("--anchors", default=None)
    parser.add_argument("--n-samples", type=int, default=10)
    parser.add_argument("--n-steps", type=int, default=None)
    parser.add_argument("--max-batch-size", type=int, default=64)
    parser.add_argument("--random-seed", type=int, default=None)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--dataset-view-id", default="difflinker_case_studies_v1")
    parser.add_argument("--split-id", default="example_only_no_formal_split")
    parser.add_argument("--complex-id", default="hsp90")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.pocket is None and args.protein is None:
        parser.error("Provide --pocket for generate_with_pocket.py or --protein for generate_with_protein.py")

    current = Path.cwd()
    repo = Path(args.repo).resolve()
    output_root = Path(args.output_root).resolve()
    captured_dir = output_root / "captured_outputs"
    log_dir = output_root / "logs"
    captured_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    fragments = resolve_for_repo(args.fragments, repo, current)
    model = resolve_for_repo(args.model, repo, current)
    script = "generate_with_pocket.py" if args.pocket is not None else "generate_with_protein.py"
    command = [args.python, script, "--fragments", fragments, "--model", model, "--linker_size", str(args.linker_size), "--output", str(captured_dir), "--n_samples", str(args.n_samples), "--max_batch_size", str(args.max_batch_size)]
    if args.pocket is not None:
        command.extend(["--pocket", resolve_for_repo(args.pocket, repo, current)])
    if args.protein is not None:
        command.extend(["--protein", resolve_for_repo(args.protein, repo, current)])
    if args.anchors:
        command.extend(["--anchors", args.anchors])
    if args.n_steps is not None:
        command.extend(["--n_steps", str(args.n_steps)])
    if args.random_seed is not None:
        command.extend(["--random_seed", str(args.random_seed)])

    stdout_path = log_dir / "stdout.log"
    stderr_path = log_dir / "stderr.log"
    exit_code: int | None = None
    if args.dry_run:
        stdout_path.write_text("dry_run: command not executed\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
    else:
        with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
            completed = subprocess.run(command, cwd=repo, stdout=stdout, stderr=stderr, check=False)
        exit_code = completed.returncode

    try:
        method_commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        method_commit = None

    output_files = find_output_files(captured_dir)
    run_metadata = {
        "schema_version": RUN_METADATA_SCHEMA_VERSION,
        "schema_path": RUN_METADATA_SCHEMA_PATH,
        "run_id": args.run_id,
        "method": "DiffLinker",
        "run_boundary_label": RUN_BOUNDARY_LABEL,
        "upstream_repo": "https://github.com/igashov/DiffLinker",
        "upstream_commit": method_commit,
        "fork_repo": None,
        "fork_branch": None,
        "fork_commit": None,
        "patches": [],
        "algorithm_changed": False,
        "checkpoint_id": "pockets_difflinker_full.ckpt",
        "checkpoint_source": "https://zenodo.org/records/10988017/files/pockets_difflinker_full_no_anchors_fc_pdb_excluded.ckpt?download=1",
        "checkpoint_sha256": sha256_file(Path(model)),
        "training_data_status": "training_data_unknown",
        "dataset_name": "third_party_repo_examples_v1",
        "dataset_version": "cloned_repo_examples",
        "raw_dataset_id": "third_party_repo_examples_v1",
        "dataset_view_id": args.dataset_view_id,
        "split_id": args.split_id,
        "preprocessing_id": "repo_case_study_as_is",
        "raw_checksum": None,
        "view_checksum": None,
        "split_checksum": None,
        "leakage_check_status": "unknown_risk",
        "leakage_report_path": None,
        "seed": args.random_seed,
        "sampling_budget": args.n_samples,
        "config_hash": None,
        "command": " ".join(command),
        "environment": args.python,
        "hardware": None,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "exit_code": exit_code,
        "output_manifest_path": str(output_root / "output_manifest.json"),
        "resource_budget_config_version": RESOURCE_BUDGET_VERSION,
        "resource_budget_config_hash": None,
        "label_protocol_version": LABEL_PROTOCOL_VERSION,
        "label_config_hash": None,
        "tool_versions_lock_path": "configs/audit/tool_versions.lock",
        "n_output_artifacts": len(output_files),
        "status": "dry_run" if args.dry_run else ("completed" if exit_code == 0 else "failed"),
    }
    samples = build_samples(
        run_id=args.run_id,
        method_commit=method_commit,
        dataset_view_id=args.dataset_view_id,
        split_id=args.split_id,
        complex_id=args.complex_id,
        n_budget=args.n_samples,
        output_files=output_files,
        exit_code=exit_code,
    )
    output_manifest = {
        "schema_version": OUTPUT_MANIFEST_SCHEMA_VERSION,
        "schema_path": OUTPUT_MANIFEST_SCHEMA_PATH,
        "run_id": args.run_id,
        "method": "DiffLinker",
        "metadata_schemas": {
            "run_metadata": RUN_METADATA_SCHEMA_PATH,
            "samples": SAMPLE_METADATA_SCHEMA_PATH,
            "output_manifest": OUTPUT_MANIFEST_SCHEMA_PATH,
        },
        "captured_outputs": [str(p) for p in output_files],
        "logs": [str(stdout_path), str(stderr_path)],
        "n_output_artifacts": len(output_files),
        "sha256": {str(p): sha256_file(p) for p in output_files},
    }

    write_json(output_root / "run_metadata.json", run_metadata)
    write_jsonl(output_root / "samples.jsonl", samples)
    write_json(output_root / "output_manifest.json", output_manifest)
    print(json.dumps({"run_id": args.run_id, "exit_code": exit_code, "n_output_artifacts": len(output_files), "output_root": str(output_root)}, ensure_ascii=False))
    return 0 if args.dry_run or exit_code == 0 else exit_code


if __name__ == "__main__":
    raise SystemExit(main())
