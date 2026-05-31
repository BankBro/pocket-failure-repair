#!/usr/bin/env python3
"""Generate minimal failed-candidate records for smoke testing."""

from __future__ import annotations

import argparse
from typing import Any

from pfr.utils.io import load_yaml, read_jsonl, write_jsonl


def make_candidate(example: dict[str, Any], failure_type: str, index: int, seed: int) -> dict[str, Any]:
    return {
        "candidate_id": f"{example.get('complex_id', 'example')}_{failure_type}_{index}",
        "complex_id": example.get("complex_id"),
        "failure_type": failure_type,
        "failure_reason": failure_type,
        "seed": seed,
        "source": "smoke_rdkit_descriptor_placeholder",
        "protein_path": example.get("protein_path"),
        "ligand_path": example.get("ligand_path"),
        "failed_ligand_path": example.get("ligand_path"),
        "ligand_smiles": example.get("ligand_smiles"),
        "scaffold_smiles": example.get("scaffold_smiles"),
        "scaffold_atoms": example.get("scaffold_atoms", []),
        "editable_atoms": example.get("editable_atoms", []),
        "anchor_atoms": example.get("anchor_atoms", []),
        "descriptors": example.get("descriptors", {}),
        "dataset_status": example.get("status"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_yaml(args.config)
    seed = int(config.get("seed", 0))
    input_path = config["input"]["dataset_path"]
    output_path = config["output"]["candidates_path"]
    failure_types = list(config.get("failure_types", []))
    candidates_per_example = int(config.get("limits", {}).get("candidates_per_example", len(failure_types) or 1))

    examples = read_jsonl(input_path)
    rows: list[dict[str, Any]] = []
    for example in examples:
        selected_types = failure_types[:candidates_per_example] or ["unknown_failure"]
        for index, failure_type in enumerate(selected_types):
            rows.append(make_candidate(example, failure_type, index, seed))

    write_jsonl(output_path, rows)
    print(f"Read {len(examples)} examples from {input_path}")
    print(f"Wrote {len(rows)} failed candidates to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
