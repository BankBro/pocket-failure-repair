#!/usr/bin/env python3
"""Generate minimal failed-candidate records for smoke testing."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from pfr.chemistry.perturb import perturb_failed_molecule, write_sdf
from pfr.utils.io import load_yaml, read_jsonl, write_jsonl


def make_candidate(
    example: dict[str, Any], failure_type: str, index: int, seed: int, failed_molecules_dir: Path | None
) -> dict[str, Any]:
    candidate_id = f"{example.get('complex_id', 'example')}_{failure_type}_{index}"
    failed_ligand_path = example.get("ligand_path")
    if failed_molecules_dir and failed_ligand_path:
        mol = perturb_failed_molecule(failed_ligand_path, failure_type, example.get("editable_atoms", []))
        if mol is not None:
            failed_ligand_path = str(write_sdf(failed_molecules_dir / f"{candidate_id}.sdf", mol))
    return {
        "candidate_id": candidate_id,
        "complex_id": example.get("complex_id"),
        "failure_type": failure_type,
        "failure_reason": failure_type,
        "seed": seed,
        "source": "smoke_rdkit_perturbed_molecule",
        "protein_path": example.get("protein_path"),
        "ligand_path": example.get("ligand_path"),
        "failed_ligand_path": failed_ligand_path,
        "ligand_smiles": example.get("ligand_smiles"),
        "scaffold_smiles": example.get("scaffold_smiles"),
        "scaffold_atoms": example.get("scaffold_atoms", []),
        "editable_atoms": example.get("editable_atoms", []),
        "anchor_atoms": example.get("anchor_atoms", []),
        "descriptors": example.get("descriptors", {}),
        "dataset_status": example.get("status"),
        "sample_quality": example.get("sample_quality", {}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_yaml(args.config)
    seed = int(config.get("seed", 0))
    input_path = config["input"]["dataset_path"]
    output_path = config["output"]["candidates_path"]
    failed_molecules_dir = config.get("output", {}).get("failed_molecules_dir")
    failed_molecules_dir_path = Path(failed_molecules_dir) if failed_molecules_dir else None
    failure_types = list(config.get("failure_types", []))
    candidates_per_example = int(config.get("limits", {}).get("candidates_per_example", len(failure_types) or 1))

    examples = read_jsonl(input_path)
    rows: list[dict[str, Any]] = []
    for example in examples:
        selected_types = failure_types[:candidates_per_example] or ["unknown_failure"]
        for index, failure_type in enumerate(selected_types):
            rows.append(make_candidate(example, failure_type, index, seed, failed_molecules_dir_path))

    write_jsonl(output_path, rows)
    print(f"Read {len(examples)} examples from {input_path}")
    print(f"Wrote {len(rows)} failed candidates to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
