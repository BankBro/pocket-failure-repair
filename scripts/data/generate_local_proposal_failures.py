#!/usr/bin/env python3
"""Generate local-proposal failed candidates for smoke-plus diagnostics."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from pfr.chemistry.perturb import translate_atoms, write_sdf, zigzag_atoms, mutate_first_valid_atom, valid_editable_atoms
from pfr.chemistry.rdkit_scaffold import load_first_molecule
from pfr.feedback.geometry import anchor_distance_error, protein_ligand_geometry
from pfr.utils.io import load_yaml, read_jsonl, write_jsonl


PROPOSAL_PATTERNS = [
    ("local_translation", (0.9, -0.4, 0.3)),
    ("local_translation", (-0.7, 0.8, -0.2)),
    ("local_translation", (0.2, 1.1, 0.6)),
    ("local_zigzag", 0.8),
    ("local_zigzag", 1.1),
    ("local_atom_substitution", (16, 17, 9, 7)),
]


def proposal_molecule(ligand_path: str | Path, editable_atoms: list[int], proposal_index: int) -> tuple[str, Any] | tuple[str, None]:
    mol = load_first_molecule(ligand_path)
    if mol is None:
        return ("rdkit_read_failed", None)
    editable = valid_editable_atoms(mol, editable_atoms)
    pattern, value = PROPOSAL_PATTERNS[proposal_index % len(PROPOSAL_PATTERNS)]
    if pattern == "local_translation":
        dx, dy, dz = value
        return (pattern, translate_atoms(mol, editable, dx, dy, dz))
    if pattern == "local_zigzag":
        return (pattern, zigzag_atoms(mol, editable, float(value)))
    if pattern == "local_atom_substitution":
        return (pattern, mutate_first_valid_atom(mol, editable, value) or zigzag_atoms(mol, editable, 0.5))
    return (pattern, mol)


def classify_failure(example: dict[str, Any], failed_ligand_path: str | Path, proposal_kind: str) -> str:
    geometry = protein_ligand_geometry(example.get("protein_path"), failed_ligand_path)
    clash_count = geometry.get("clash_count")
    anchor_error = anchor_distance_error(example.get("ligand_path"), failed_ligand_path, example.get("anchor_atoms", []))
    if clash_count not in (None, 0):
        return "local_proposal_clash"
    if anchor_error is not None and anchor_error > 1.0:
        return "local_proposal_anchor_drift"
    if proposal_kind == "local_atom_substitution":
        return "local_proposal_atom_substitution"
    return "local_proposal_geometry_drift"


def make_candidate(example: dict[str, Any], proposal_index: int, seed: int, failed_molecules_dir: Path) -> dict[str, Any] | None:
    ligand_path = example.get("ligand_path")
    if not ligand_path:
        return None
    proposal_kind, mol = proposal_molecule(ligand_path, example.get("editable_atoms", []), proposal_index)
    if mol is None:
        return None
    complex_id = example.get("complex_id", "example")
    temporary_id = f"{complex_id}_local_proposal_{proposal_index}"
    failed_path = write_sdf(failed_molecules_dir / f"{temporary_id}.sdf", mol)
    failure_type = classify_failure(example, failed_path, proposal_kind)
    candidate_id = f"{complex_id}_{failure_type}_{proposal_index}"
    final_path = failed_molecules_dir / f"{candidate_id}.sdf"
    if final_path != failed_path:
        failed_path.replace(final_path)
        failed_path = final_path
    return {
        "candidate_id": candidate_id,
        "complex_id": example.get("complex_id"),
        "failure_type": failure_type,
        "failure_reason": failure_type,
        "proposal_kind": proposal_kind,
        "proposal_index": proposal_index,
        "seed": seed,
        "source": "smoke_local_proposal_pool_rdkit",
        "protein_path": example.get("protein_path"),
        "ligand_path": example.get("ligand_path"),
        "failed_ligand_path": str(failed_path),
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
    examples = read_jsonl(config["input"]["dataset_path"])
    output_path = config["output"]["candidates_path"]
    failed_molecules_dir = Path(config["output"]["failed_molecules_dir"])
    proposals_per_example = int(config.get("limits", {}).get("proposals_per_example", len(PROPOSAL_PATTERNS)))

    rows: list[dict[str, Any]] = []
    for example in examples:
        for proposal_index in range(proposals_per_example):
            candidate = make_candidate(example, proposal_index, seed, failed_molecules_dir)
            if candidate is not None:
                rows.append(candidate)

    write_jsonl(output_path, rows)
    print(f"Read {len(examples)} examples from {config['input']['dataset_path']}")
    print(f"Wrote {len(rows)} local-proposal failed candidates to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
