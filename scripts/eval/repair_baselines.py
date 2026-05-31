#!/usr/bin/env python3
"""Run minimal repair baselines for smoke candidates."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from pfr.chemistry.rdkit_scaffold import load_first_molecule
from pfr.chemistry.perturb import write_sdf
from pfr.utils.io import load_yaml, read_jsonl, write_jsonl


def repair_candidate(candidate: dict[str, Any], baseline: str, output_dir: Path) -> dict[str, Any] | None:
    source_path = candidate.get("ligand_path") if baseline == "coordinate_rollback" else candidate.get("failed_ligand_path")
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
    output_dir = Path(config["output"]["repaired_molecules_dir"])
    baselines = list(config.get("baselines", []))
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        for baseline in baselines:
            row = repair_candidate(candidate, baseline, output_dir)
            if row is not None:
                rows.append(row)
    write_jsonl(config["output"]["repaired_candidates_path"], rows)
    print(f"Read {len(candidates)} failed candidates")
    print(f"Wrote {len(rows)} repaired candidate records to {config['output']['repaired_candidates_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
