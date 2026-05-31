#!/usr/bin/env python3
"""Build a minimal R-group smoke dataset from prepared complex metadata."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from pfr.chemistry.rdkit_scaffold import summarize_ligand
from pfr.utils.io import load_yaml, write_json, write_jsonl


def build_row(ligand_path: Path, protein_path: Path | None) -> dict[str, Any]:
    ligand_summary = summarize_ligand(ligand_path)
    row = {
        "complex_id": ligand_path.parent.name,
        "protein_path": str(protein_path) if protein_path else None,
        "ligand_path": str(ligand_path),
        "editable_smiles": None,
    }
    row.update(ligand_summary)
    return row


def discover_complexes(complexes_dir: Path, max_complexes: int) -> list[dict[str, Any]]:
    if not complexes_dir.exists():
        return []
    rows: list[dict[str, Any]] = []
    for index, ligand_path in enumerate(sorted(complexes_dir.glob("**/*_ligand.*"))):
        if index >= max_complexes:
            break
        protein_candidates = sorted(ligand_path.parent.glob("*_protein.*"))
        protein_path = protein_candidates[0] if protein_candidates else None
        rows.append(build_row(ligand_path, protein_path))
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
            "num_rdkit_ok": sum(row.get("status") == "rdkit_ok" for row in rows),
            "notes": "Smoke split only; all discovered examples are assigned to train.",
        },
    )

    print(f"Wrote {len(rows)} examples to {dataset_path}")
    print(f"Wrote split metadata to {split_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
