#!/usr/bin/env python3
"""Build a minimal R-group smoke dataset from prepared complex metadata."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from pfr.utils.io import load_yaml, write_json, write_jsonl


def discover_complexes(complexes_dir: Path, max_complexes: int) -> list[dict[str, Any]]:
    if not complexes_dir.exists():
        return []
    rows: list[dict[str, Any]] = []
    for index, ligand_path in enumerate(sorted(complexes_dir.glob("**/*_ligand.*"))):
        if index >= max_complexes:
            break
        protein_candidates = sorted(ligand_path.parent.glob("*_protein.*"))
        rows.append(
            {
                "complex_id": ligand_path.parent.name,
                "protein_path": str(protein_candidates[0]) if protein_candidates else None,
                "ligand_path": str(ligand_path),
                "scaffold_smiles": None,
                "editable_smiles": None,
                "anchor_atoms": [],
                "status": "metadata_only",
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_yaml(args.config)
    input_config = config.get("input", {})
    output_config = config.get("output", {})
    complexes_dir = Path(input_config.get("complexes_dir", "data/raw/smoke_complexes"))
    max_complexes = int(input_config.get("max_complexes", 3))

    rows = discover_complexes(complexes_dir, max_complexes)
    dataset_path = write_jsonl(output_config["dataset_path"], rows)
    split_path = write_json(
        output_config["split_path"],
        {
            "name": config.get("name"),
            "seed": config.get("seed"),
            "train": [row["complex_id"] for row in rows],
            "validation": [],
            "test": [],
            "num_examples": len(rows),
            "notes": "Smoke split only; empty if no prepared *_ligand files are present.",
        },
    )

    print(f"Wrote {len(rows)} examples to {dataset_path}")
    print(f"Wrote split metadata to {split_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
