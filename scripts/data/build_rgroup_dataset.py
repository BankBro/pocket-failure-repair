#!/usr/bin/env python3
"""Build a minimal R-group smoke dataset from prepared complex metadata."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

from pfr.data.schema_refs import with_data_schema_ref
from pfr.chemistry.rdkit_scaffold import summarize_ligand
from pfr.feedback.geometry import structure_quality_flags
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
    row["sample_quality"] = structure_quality_flags(
        status=row.get("status"),
        protein_path=row.get("protein_path"),
        ligand_path=row.get("ligand_path"),
        scaffold_atoms=row.get("scaffold_atoms", []),
        anchor_atoms=row.get("anchor_atoms", []),
        editable_atoms=row.get("editable_atoms", []),
    )
    return row


def choose_ligand_path(complex_dir: Path) -> Path | None:
    for pattern in ("*_ligand.pdb", "*_ligand.sdf", "*_ligand.*"):
        candidates = sorted(complex_dir.glob(pattern))
        if candidates:
            return candidates[0]
    return None


def discover_complexes(complexes_dir: Path, max_complexes: int) -> list[dict[str, Any]]:
    if not complexes_dir.exists():
        return []
    rows: list[dict[str, Any]] = []
    for complex_dir in sorted(path for path in complexes_dir.iterdir() if path.is_dir()):
        if len(rows) >= max_complexes:
            break
        ligand_path = choose_ligand_path(complex_dir)
        if ligand_path is None:
            continue
        protein_candidates = sorted(complex_dir.glob("*_protein_clean.*")) or sorted(complex_dir.glob("*_protein.*"))
        protein_path = protein_candidates[0] if protein_candidates else None
        rows.append(build_row(ligand_path, protein_path))
    return rows


def prepare_entry_rows(
    rows: list[dict[str, Any]], dataset_name: str, dataset_version: str, entry_index_path: Path
) -> list[dict[str, Any]]:
    entries_dir = entry_index_path.parent
    prepared: list[dict[str, Any]] = []
    for row in rows:
        sample_id = str(row.get("sample_id") or row["complex_id"])
        entry_path = entries_dir / sample_id / "entry.json"
        updated = dict(row)
        updated["dataset_id"] = dataset_name
        updated["dataset_version"] = dataset_version
        updated["sample_id"] = sample_id
        updated["entry_path"] = str(entry_path)
        provenance = updated.get("provenance") if isinstance(updated.get("provenance"), dict) else {}
        provenance.update(
            {
                "entry_collection_path": str(entry_index_path),
                "layout_version": "dataset_entries_v1",
            }
        )
        updated["provenance"] = provenance
        prepared.append(with_data_schema_ref(updated, "dataset_entry"))
    return prepared


def write_entry_files(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        write_json(row["entry_path"], row)


def stable_score(value: str, seed: int) -> int:
    digest = hashlib.sha256(f"{seed}:{value}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def split_complex_ids(rows: list[dict[str, Any]], seed: int, fractions: dict[str, Any] | None) -> dict[str, list[str]]:
    complex_ids = [str(row["complex_id"]) for row in rows]
    if not fractions or len(complex_ids) < 5:
        return {"train": complex_ids, "validation": [], "test": []}
    ordered = sorted(complex_ids, key=lambda value: stable_score(value, seed))
    validation_fraction = float(fractions.get("validation", 0.0))
    test_fraction = float(fractions.get("test", 0.0))
    validation_count = int(round(len(ordered) * validation_fraction))
    test_count = int(round(len(ordered) * test_fraction))
    if validation_fraction > 0 and validation_count == 0:
        validation_count = 1
    if test_fraction > 0 and test_count == 0:
        test_count = 1
    if validation_count + test_count >= len(ordered):
        overflow = validation_count + test_count - len(ordered) + 1
        test_count = max(0, test_count - overflow)
    validation = sorted(ordered[:validation_count])
    test = sorted(ordered[validation_count : validation_count + test_count])
    held_out = set(validation) | set(test)
    train = sorted(complex_id for complex_id in complex_ids if complex_id not in held_out)
    return {"train": train, "validation": validation, "test": test}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_yaml(args.config)
    input_config = config.get("input", {})
    output_config = config.get("output", {})
    complexes_dir = Path(input_config.get("complexes_dir", "data/datasets/rgroup_smoke/raw"))
    max_complexes = int(input_config.get("max_complexes", 3))
    seed = int(config.get("seed", 0))

    rows = discover_complexes(complexes_dir, max_complexes)
    dataset_path_value = output_config["dataset_path"]
    dataset_id = str(config.get("dataset_id") or config.get("name", "dataset"))
    dataset_version = str(config.get("dataset_version", "v1"))
    rows = prepare_entry_rows(rows, dataset_id, dataset_version, Path(dataset_path_value))
    split = split_complex_ids(rows, seed, config.get("split"))
    dataset_path = write_jsonl(dataset_path_value, rows)
    write_entry_files(rows)
    split_metadata = with_data_schema_ref(
        {
            "name": config.get("name"),
            "dataset_id": dataset_id,
            "dataset_version": dataset_version,
            "seed": seed,
            "train": split["train"],
            "validation": split["validation"],
            "test": split["test"],
            "num_examples": len(rows),
            "num_rdkit_ok": sum(row.get("status") == "rdkit_ok" for row in rows),
            "num_evaluable_for_repair": sum(row.get("sample_quality", {}).get("evaluable_for_repair") for row in rows),
            "excluded_examples": [
                {
                    "complex_id": row["complex_id"],
                    "reasons": row.get("sample_quality", {}).get("exclusion_reasons", []),
                }
                for row in rows
                if not row.get("sample_quality", {}).get("evaluable_for_repair")
            ],
            "notes": "Deterministic smoke split by complex ID when split fractions are configured. Examples marked non-evaluable must not be used for model-performance claims.",
        },
        "dataset_split",
    )
    split_path = write_json(output_config["split_path"], split_metadata)

    print(f"Wrote {len(rows)} examples to {dataset_path}")
    print(f"Wrote split metadata to {split_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
