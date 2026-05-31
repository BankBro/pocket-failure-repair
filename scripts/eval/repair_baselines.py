#!/usr/bin/env python3
"""Run minimal repair baselines for smoke candidates."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from pfr.chemistry.rdkit_scaffold import load_first_molecule
from pfr.chemistry.perturb import write_sdf
from pfr.utils.io import load_yaml, read_jsonl, write_jsonl


def choose_source_path(candidate: dict[str, Any], baseline: str, feedback: dict[str, Any] | None) -> tuple[str | None, str]:
    if baseline == "coordinate_rollback":
        return candidate.get("ligand_path"), "always_use_original_ligand"
    if baseline == "identity_failed_candidate":
        return candidate.get("failed_ligand_path"), "always_use_failed_candidate"
    if baseline == "feedback_rule_repair":
        geometry = (feedback or {}).get("geometry", {})
        failure_type = candidate.get("failure_type")
        needs_rollback = (
            failure_type in {"clash", "anchor_invalid", "geometry_invalid"}
            or geometry.get("clash_count", 0) not in (None, 0)
            or float(geometry.get("anchor_distance_error") or 0.0) > 1.0
            or geometry.get("editable_region_validity") is False
        )
        if needs_rollback:
            return candidate.get("ligand_path"), "feedback_rule_selected_original_ligand"
        return candidate.get("failed_ligand_path"), "feedback_rule_kept_failed_candidate"
    return candidate.get("failed_ligand_path"), "unknown_baseline_default_failed_candidate"


def repair_candidate(
    candidate: dict[str, Any], baseline: str, output_dir: Path, feedback: dict[str, Any] | None
) -> dict[str, Any] | None:
    source_path, decision = choose_source_path(candidate, baseline, feedback)
    if not source_path:
        return None
    mol = load_first_molecule(source_path)
    if mol is None:
        return None
    repair_id = f"{candidate['candidate_id']}__{baseline}"
    repaired_path = write_sdf(output_dir / f"{repair_id}.sdf", mol)
    return {
        "repair_id": repair_id,
        "candidate_id": candidate.get("candidate_id"),
        "complex_id": candidate.get("complex_id"),
        "baseline": baseline,
        "failure_type": candidate.get("failure_type"),
        "decision": decision,
        "source_failed_ligand_path": candidate.get("failed_ligand_path"),
        "repaired_ligand_path": str(repaired_path),
        "scaffold_smiles": candidate.get("scaffold_smiles"),
        "anchor_atoms": candidate.get("anchor_atoms", []),
        "editable_atoms": candidate.get("editable_atoms", []),
        "source": "smoke_repair_baseline",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_yaml(args.config)
    candidates = read_jsonl(config["input"]["candidates_path"])
    feedback_rows = read_jsonl(config["input"].get("feedback_path", "")) if config["input"].get("feedback_path") else []
    feedback_by_id = {row.get("candidate_id"): row for row in feedback_rows}
    output_dir = Path(config["output"]["repaired_molecules_dir"])
    baselines = list(config.get("baselines", []))
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        feedback = feedback_by_id.get(candidate.get("candidate_id"))
        for baseline in baselines:
            row = repair_candidate(candidate, baseline, output_dir, feedback)
            if row is not None:
                rows.append(row)
    write_jsonl(config["output"]["repaired_candidates_path"], rows)
    print(f"Read {len(candidates)} failed candidates")
    print(f"Read {len(feedback_rows)} feedback records")
    print(f"Wrote {len(rows)} repaired candidate records to {config['output']['repaired_candidates_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
