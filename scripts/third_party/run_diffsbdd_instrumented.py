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
import textwrap
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
STAGE_ATTRITION_SCHEMA_VERSION = "stage_attrition_v0_1"
STAGE_ATTRITION_SCHEMA_PATH = "schemas/third_party_audit/attrition/stage_attrition_v0_1.json"
DIAGNOSIS_SANITY_SCHEMA_PATH = "schemas/third_party_audit/diagnosis/diagnosis_sanity_v0_1.json"
EVALUATOR_TOOL_RESULT_SCHEMA_PATH = "schemas/third_party_audit/diagnosis/evaluator_tool_result_v0_1.json"
MVP_SANITY_SUMMARY_SCHEMA_VERSION = "mvp_sanity_summary_v0_1"
MVP_SANITY_SUMMARY_SCHEMA_PATH = "schemas/third_party_audit/diagnosis/mvp_sanity_summary_v0_1.json"


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


def split_sdf_records(path: Path, output_dir: Path) -> list[dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for index, block in enumerate(part for part in path.read_bytes().split(b"$$$$") if part.strip()):
        payload = b"\n" + block.strip(b"\r\n") + b"\n$$$$\n"
        sample_path = output_dir / f"sample_{index:03d}.sdf"
        sample_path.write_bytes(payload)
        records.append(
            {
                "index": index,
                "path": str(sample_path),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    return records


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_seeded_launcher(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            from __future__ import annotations

            import os
            import random
            import runpy
            import sys
            from pathlib import Path


            def main() -> int:
                seed = int(os.environ.get("PFR_DIFFSBDD_SEED", "0"))
                os.environ["PYTHONHASHSEED"] = str(seed)
                random.seed(seed)
                try:
                    import numpy as np

                    np.random.seed(seed)
                except Exception:
                    pass
                try:
                    import torch

                    torch.manual_seed(seed)
                    if torch.cuda.is_available():
                        torch.cuda.manual_seed_all(seed)
                except Exception:
                    pass
                script = sys.argv[1]
                script_path = Path(script).resolve()
                for candidate in [str(Path.cwd()), str(script_path.parent)]:
                    if candidate not in sys.path:
                        sys.path.insert(0, candidate)
                sys.argv = sys.argv[1:]
                runpy.run_path(str(script_path), run_name="__main__")
                return 0


            if __name__ == "__main__":
                raise SystemExit(main())
            """
        ),
        encoding="utf-8",
    )


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


def resolve_existing_path(value: str | None, repo: Path, current: Path) -> str | None:
    if value is None:
        return None
    if ":" in value and not Path(value).suffix:
        return None
    path = Path(value)
    if path.is_absolute() and path.exists():
        return str(path)
    if (current / path).exists():
        return str((current / path).resolve())
    if (repo / path).exists():
        return str((repo / path).resolve())
    return None


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
    normalized_records: list[dict[str, Any]],
    receptor_path: str | None,
    ref_ligand_path: str | None,
    exit_code: int | None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    raw_sha = sha256_file(molecule_path)
    command_failed = exit_code not in (0, None)
    for index in range(max(n_budget, n_final)):
        normalized_record = normalized_records[index] if index < len(normalized_records) else None
        normalized_path = normalized_record["path"] if normalized_record else None
        has_final = index < n_final and normalized_path is not None and not command_failed
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
                "molecule_path": normalized_path if has_final else None,
                "pose_path": normalized_path if has_final else None,
                "receptor_path": receptor_path,
                "reference_ligand_path": ref_ligand_path,
                "raw_sample_id": None,
                "raw_sha256": raw_sha if has_final else None,
                "normalized_sha256": normalized_record["sha256"] if normalized_record and has_final else None,
                "raw_output_path": str(molecule_path) if molecule_path.exists() else None,
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


def build_stage_attrition(
    *,
    run_id: str,
    method: str,
    dataset_view_id: str,
    complex_id: str,
    seed: int | None,
    n_budget: int,
    n_final: int,
    sample_count: int,
    exit_code: int | None,
) -> dict[str, Any]:
    command_failed = exit_code not in (0, None)
    n_missing = max(n_budget - n_final, 0)
    n_pipeline_failure = n_budget if command_failed else 0
    n_evaluable_preliminary = n_final if not command_failed else 0
    n_not_evaluable = max(sample_count - n_evaluable_preliminary, 0)
    return {
        "schema_version": STAGE_ATTRITION_SCHEMA_VERSION,
        "schema_path": STAGE_ATTRITION_SCHEMA_PATH,
        "method": method,
        "run_id": run_id,
        "dataset_view_id": dataset_view_id,
        "summary_scope": "mvp_sanity_metadata_pre_evaluator",
        "denominator_policy_version": "pfr_failure_statistics_v0_1_draft",
        "rows": [
            {
                "method": method,
                "run_id": run_id,
                "seed": seed,
                "dataset_view_id": dataset_view_id,
                "complex_id": complex_id,
                "pocket_id": None,
                "N_budget": n_budget,
                "N_raw_attempt_metadata": sample_count,
                "N_raw_captured": n_final,
                "N_original_failed_samples": 0,
                "N_parse_fail": None,
                "N_parsed": n_final,
                "N_rdkit_invalid": None,
                "N_rdkit_valid": None,
                "N_anchor_fail": None,
                "N_anchor_preserved": None,
                "N_docking_attempted": 0,
                "N_docking_failed": 0,
                "N_pose_available": n_final,
                "N_not_evaluable": n_not_evaluable,
                "N_evaluable": n_evaluable_preliminary,
                "N_rejected": 0,
                "N_selected": 0,
                "N_final": n_final,
                "N_repair_eligible": None,
                "notes": "MVP pre-evaluator attrition. Denominator is sample metadata rows, not only SDF file count.",
            }
        ],
        "mvp_required_counts": {
            "N_budget": n_budget,
            "N_raw_attempt_metadata": sample_count,
            "N_raw_captured": n_final,
            "N_final": n_final,
            "N_missing_output": n_missing,
            "N_pipeline_failure": n_pipeline_failure,
            "N_tool_failure": 0,
            "N_not_evaluable_by_reason": {
                "missing_output": n_missing,
                "pipeline_failure": n_pipeline_failure,
                "tool_failure": 0,
                "format_error": 0,
                "unknown": 0 if not command_failed else max(n_budget - n_missing, 0),
            },
        },
    }


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
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--experiment-id", default=None)
    parser.add_argument("--config-hash", default=None)
    parser.add_argument("--resolved-config", default=None)
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
    processed_dir = output_root / "processed" / "normalized_samples"
    log_dir = output_root / "logs"
    manifests_dir = output_root / "manifests"
    evaluator_dir = output_root / "evaluator"
    summaries_dir = output_root / "summaries"
    captured_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)
    evaluator_dir.mkdir(parents=True, exist_ok=True)
    summaries_dir.mkdir(parents=True, exist_ok=True)
    outfile = captured_dir / "generated.sdf"

    checkpoint = resolve_for_cwd(args.checkpoint, repo, current)
    pdbfile = resolve_for_cwd(args.pdbfile, repo, current)
    ref_ligand = resolve_for_cwd(args.ref_ligand, repo, current)
    receptor_path = resolve_existing_path(args.pdbfile, repo, current)
    ref_ligand_path = resolve_existing_path(args.ref_ligand, repo, current)

    generate_args = [str(checkpoint), "--pdbfile", str(pdbfile), "--outfile", str(outfile), "--n_samples", str(args.n_samples)]
    if ref_ligand:
        generate_args.extend(["--ref_ligand", str(ref_ligand)])
    if args.resi_list:
        generate_args.append("--resi_list")
        generate_args.extend(args.resi_list)
    if args.batch_size is not None:
        generate_args.extend(["--batch_size", str(args.batch_size)])
    if args.num_nodes_lig is not None:
        generate_args.extend(["--num_nodes_lig", str(args.num_nodes_lig)])
    if args.timesteps is not None:
        generate_args.extend(["--timesteps", str(args.timesteps)])

    env = os.environ.copy()
    if args.seed is not None:
        launcher_path = manifests_dir / "seeded_generate_ligands_launcher.py"
        write_seeded_launcher(launcher_path)
        env["PFR_DIFFSBDD_SEED"] = str(args.seed)
        env["PYTHONHASHSEED"] = str(args.seed)
        command = [args.python, str(launcher_path), "generate_ligands.py", *generate_args]
    else:
        command = [args.python, "generate_ligands.py", *generate_args]

    stdout_path = log_dir / "stdout.log"
    stderr_path = log_dir / "stderr.log"
    exit_code: int | None = None
    if args.dry_run:
        stdout_path.write_text("dry_run: command not executed\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
    else:
        with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
            completed = subprocess.run(command, cwd=repo, stdout=stdout, stderr=stderr, check=False, env=env)
        exit_code = completed.returncode

    n_final = count_sdf_records(outfile)
    normalized_records = split_sdf_records(outfile, processed_dir)
    try:
        method_commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        method_commit = None

    run_metadata = {
        "schema_version": RUN_METADATA_SCHEMA_VERSION,
        "schema_path": RUN_METADATA_SCHEMA_PATH,
        "experiment_id": args.experiment_id,
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
        "seed": args.seed,
        "sampling_budget": args.n_samples,
        "config_hash": args.config_hash,
        "resolved_config_path": args.resolved_config,
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
        "normalized_sample_count": len(normalized_records),
        "status": "dry_run" if args.dry_run else ("completed" if exit_code == 0 else "failed"),
        "claim_boundary": "mvp_sanity_not_formal_prevalence",
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
        normalized_records=normalized_records,
        receptor_path=receptor_path,
        ref_ligand_path=ref_ligand_path,
        exit_code=exit_code,
    )
    normalized_manifest_path = manifests_dir / "normalized_samples_manifest.json"
    write_json(
        normalized_manifest_path,
        {
            "schema_version": "diffsbdd_normalized_samples_manifest_v0_1",
            "schema_path": None,
            "run_id": args.run_id,
            "method": "DiffSBDD",
            "raw_output_path": str(outfile) if outfile.exists() else None,
            "raw_sha256": sha256_file(outfile),
            "records": normalized_records,
            "notes": "Experiment-local manifest; normalized sample SDF files are split from captured aggregate SDF without changing molecule content.",
        },
    )
    stage_attrition = build_stage_attrition(
        run_id=args.run_id,
        method="DiffSBDD",
        dataset_view_id=args.dataset_view_id,
        complex_id=args.complex_id,
        seed=args.seed,
        n_budget=args.n_samples,
        n_final=n_final,
        sample_count=len(samples),
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
            "stage_attrition": STAGE_ATTRITION_SCHEMA_PATH,
            "evaluator_tool_result": EVALUATOR_TOOL_RESULT_SCHEMA_PATH,
            "diagnosis_sanity": DIAGNOSIS_SANITY_SCHEMA_PATH,
            "mvp_sanity_summary": MVP_SANITY_SUMMARY_SCHEMA_PATH,
        },
        "captured_outputs": [str(outfile)] if outfile.exists() else [],
        "processed_outputs": [record["path"] for record in normalized_records],
        "logs": [str(stdout_path), str(stderr_path)],
        "manifests": [str(normalized_manifest_path)],
        "evaluator_outputs": [],
        "n_final_sdf_records": n_final,
        "n_output_artifacts": (1 if outfile.exists() else 0) + len(normalized_records),
        "sha256": {
            **({str(outfile): sha256_file(outfile)} if outfile.exists() else {}),
            **{record["path"]: record["sha256"] for record in normalized_records},
        },
        "notes": "Output capture manifest for single-method MVP sanity; no formal labels generated.",
    }

    write_json(output_root / "run_metadata.json", run_metadata)
    write_jsonl(output_root / "samples.jsonl", samples)
    write_json(output_root / "output_manifest.json", output_manifest)
    write_json(output_root / "stage_attrition.json", stage_attrition)
    write_json(
        summaries_dir / "mvp_generation_summary.json",
        {
            "schema_version": MVP_SANITY_SUMMARY_SCHEMA_VERSION,
            "schema_path": MVP_SANITY_SUMMARY_SCHEMA_PATH,
            "run_id": args.run_id,
            "method": "DiffSBDD",
            "summary_type": "generation_capture",
            "claim_boundary": "mvp_sanity_not_formal_prevalence",
            "counts": {
                "n_budget": args.n_samples,
                "n_final_sdf_records": n_final,
                "n_sample_metadata_rows": len(samples),
                "exit_code": exit_code,
                "status": run_metadata["status"],
            },
            "notes": "Generation/output-capture summary only. No formal labels or prevalence claims.",
        },
    )
    print(json.dumps({"run_id": args.run_id, "exit_code": exit_code, "n_final": n_final, "output_root": str(output_root)}, ensure_ascii=False))
    return 0 if args.dry_run or exit_code == 0 else exit_code


if __name__ == "__main__":
    raise SystemExit(main())
