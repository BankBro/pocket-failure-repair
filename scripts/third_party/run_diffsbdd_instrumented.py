#!/usr/bin/env python3
"""Run DiffSBDD through a lightweight output-capture wrapper.

This wrapper adds run metadata, stdout/stderr capture, and per-attempt sample
metadata. It does not modify DiffSBDD sampling, decoding, filtering, reranking,
or scoring logic. Formal labeling/statistics must still wait for the frozen audit
protocol.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
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


def count_sdf_records(path: Path) -> int:
    if not path.exists():
        return 0
    data = path.read_bytes()
    return sum(1 for block in data.split(b"$$$$") if block.strip())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def resolve_for_cwd(value: str | None, repo: Path, current: Path) -> str | None:
    if value is None:
        return None
    # Chain/residue ligand identifiers such as A:330 are not paths.
    if ":" in value and not Path(value).suffix:
        return value
    path = Path(value)
    if path.is_absolute():
        return str(path)
    if (current / path).exists():
        return str((current / path).resolve())
    if (repo / path).exists():
        return value
    return value


def build_samples(
    *,
    run_id: str,
    method: str,
    method_repo: str,
    method_commit: str | None,
    dataset_view_id: str,
    split_id: str,
    complex_id: str,
    pdb_id: str | None,
    n_budget: int,
    n_final: int,
    molecule_path: Path,
    exit_code: int | None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    raw_sha = sha256_file(molecule_path)
    command_failed = exit_code not in (0, None)
    for index in range(max(n_budget, n_final)):
        has_final = index < n_final and molecule_path.exists() and not command_failed
        sample_id = f"diffsbdd_{dataset_view_id}_{complex_id}_{'final' if has_final else 'raw'}_{index}"
        quality_flags: dict[str, Any] = {}
        if not has_final:
            quality_flags["missing_final_output"] = True
            if command_failed:
                quality_flags["pipeline_failure"] = True
        rows.append(
            {
                "schema_version": SAMPLE_METADATA_SCHEMA_VERSION,
                "schema_path": SAMPLE_METADATA_SCHEMA_PATH,
                "sample_id": sample_id,
                "parent_sample_id": None,
                "lineage_id": f"{run_id}::{index}",
                "run_id": run_id,
                "method": method,
                "method_repo": method_repo,
                "method_commit": method_commit,
                "run_boundary_label": RUN_BOUNDARY_LABEL,
                "dataset_name": "third_party_repo_examples_v1",
                "dataset_version": "cloned_repo_examples",
                "dataset_view_id": dataset_view_id,
                "split_id": split_id,
                "complex_id": complex_id,
                "pdb_id": pdb_id,
                "pocket_id": None,
                "stage": "final" if has_final else "raw",
                "sample_role": "final_output" if has_final else "generation_attempt",
                "sample_index": index,
                "molecule_path": str(molecule_path) if has_final else None,
                "pose_path": str(molecule_path) if has_final else None,
                "receptor_path": None,
                "raw_sample_id": None,
                "raw_sha256": raw_sha if has_final else None,
                "normalized_sha256": None,
                "original_status": {
                    "status": "final" if has_final else ("failed" if command_failed else "unknown"),
                    "source_stage_name": "DiffSBDD generate_ligands.py aggregate SDF",
                    "failure_reason": "command_exit_nonzero" if command_failed and not has_final else None,
                    "rejection_reason": None,
                    "rank": None,
                    "score": None,
                    "source_file": str(molecule_path) if molecule_path.exists() else None,
                },
                "audit_labels": {},
                "quality_flags": quality_flags,
                "created_by_script_commit": None,
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Path to the DiffSBDD repository.")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--pdbfile", required=True)
    parser.add_argument("--ref-ligand", default=None)
    parser.add_argument("--resi-list", nargs="*", default=None)
    parser.add_argument("--n-samples", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--num-nodes-lig", type=int, default=None)
    parser.add_argument("--timesteps", type=int, default=None)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--dataset-view-id", default="diffsbdd_example_3rfm_5ndu_v1")
    parser.add_argument("--split-id", default="example_only_no_formal_split")
    parser.add_argument("--complex-id", default="3rfm")
    parser.add_argument("--pdb-id", default="3rfm")
    parser.add_argument("--dry-run", action="store_true", help="Write metadata without launching DiffSBDD.")
    args = parser.parse_args()

    current = Path.cwd()
    repo = Path(args.repo).resolve()
    output_root = Path(args.output_root).resolve()
    captured_dir = output_root / "captured_outputs"
    log_dir = output_root / "logs"
    captured_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    outfile = captured_dir / "generated.sdf"

    checkpoint = resolve_for_cwd(args.checkpoint, repo, current)
    pdbfile = resolve_for_cwd(args.pdbfile, repo, current)
    ref_ligand = resolve_for_cwd(args.ref_ligand, repo, current)

    command = [args.python, "generate_ligands.py", str(checkpoint), "--pdbfile", str(pdbfile), "--outfile", str(outfile), "--n_samples", str(args.n_samples)]
    if ref_ligand:
        command.extend(["--ref_ligand", str(ref_ligand)])
    if args.resi_list:
        command.append("--resi_list")
        command.extend(args.resi_list)
    if args.batch_size is not None:
        command.extend(["--batch_size", str(args.batch_size)])
    if args.num_nodes_lig is not None:
        command.extend(["--num_nodes_lig", str(args.num_nodes_lig)])
    if args.timesteps is not None:
        command.extend(["--timesteps", str(args.timesteps)])

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

    n_final = count_sdf_records(outfile)
    try:
        method_commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        method_commit = None

    run_metadata = {
        "schema_version": RUN_METADATA_SCHEMA_VERSION,
        "schema_path": RUN_METADATA_SCHEMA_PATH,
        "run_id": args.run_id,
        "method": "DiffSBDD",
        "run_boundary_label": RUN_BOUNDARY_LABEL,
        "upstream_repo": "https://github.com/arneschneuing/DiffSBDD",
        "upstream_commit": method_commit,
        "fork_repo": None,
        "fork_branch": None,
        "fork_commit": None,
        "patches": [],
        "algorithm_changed": False,
        "checkpoint_id": "crossdocked_fullatom_cond.ckpt",
        "checkpoint_source": "https://zenodo.org/record/8183747/files/crossdocked_fullatom_cond.ckpt?download=1",
        "checkpoint_sha256": sha256_file(Path(str(checkpoint))) if checkpoint else None,
        "training_data_status": "training_data_unknown",
        "dataset_name": "third_party_repo_examples_v1",
        "dataset_version": "cloned_repo_examples",
        "raw_dataset_id": "third_party_repo_examples_v1",
        "dataset_view_id": args.dataset_view_id,
        "split_id": args.split_id,
        "preprocessing_id": "repo_example_as_is",
        "raw_checksum": None,
        "view_checksum": None,
        "split_checksum": None,
        "leakage_check_status": "unknown_risk",
        "leakage_report_path": None,
        "seed": None,
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
        "n_final_sdf_records": n_final,
        "status": "dry_run" if args.dry_run else ("completed" if exit_code == 0 else "failed"),
    }

    samples = build_samples(
        run_id=args.run_id,
        method="DiffSBDD",
        method_repo="https://github.com/arneschneuing/DiffSBDD",
        method_commit=method_commit,
        dataset_view_id=args.dataset_view_id,
        split_id=args.split_id,
        complex_id=args.complex_id,
        pdb_id=args.pdb_id,
        n_budget=args.n_samples,
        n_final=n_final,
        molecule_path=outfile,
        exit_code=exit_code,
    )
    output_manifest = {
        "schema_version": OUTPUT_MANIFEST_SCHEMA_VERSION,
        "schema_path": OUTPUT_MANIFEST_SCHEMA_PATH,
        "run_id": args.run_id,
        "method": "DiffSBDD",
        "metadata_schemas": {
            "run_metadata": RUN_METADATA_SCHEMA_PATH,
            "samples": SAMPLE_METADATA_SCHEMA_PATH,
            "output_manifest": OUTPUT_MANIFEST_SCHEMA_PATH,
        },
        "captured_outputs": [str(outfile)] if outfile.exists() else [],
        "logs": [str(stdout_path), str(stderr_path)],
        "n_final_sdf_records": n_final,
        "sha256": {str(outfile): sha256_file(outfile)} if outfile.exists() else {},
    }

    write_json(output_root / "run_metadata.json", run_metadata)
    write_jsonl(output_root / "samples.jsonl", samples)
    write_json(output_root / "output_manifest.json", output_manifest)
    print(json.dumps({"run_id": args.run_id, "exit_code": exit_code, "n_final": n_final, "output_root": str(output_root)}, ensure_ascii=False))
    return 0 if args.dry_run or exit_code == 0 else exit_code


if __name__ == "__main__":
    raise SystemExit(main())
