#!/usr/bin/env python3
"""Build anchor-preserved local-edit failures from Vina docked poses."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from rdkit import Chem

from pfr.chemistry.perturb import valid_editable_atoms, write_sdf
from pfr.chemistry.rdkit_scaffold import load_first_molecule
from pfr.feedback.geometry import anchor_distance_error, protein_ligand_geometry
from pfr.utils.io import load_yaml, read_jsonl, write_jsonl


def copy_editable_coordinates(reference_path: str | Path, docked_path: str | Path, editable_atoms: list[int]) -> Any | None:
    reference = load_first_molecule(reference_path)
    docked = load_first_molecule(docked_path)
    if reference is None or docked is None:
        return None
    if reference.GetNumConformers() == 0 or docked.GetNumConformers() == 0:
        return None
    editable = valid_editable_atoms(reference, editable_atoms)
    editable = [atom_idx for atom_idx in editable if atom_idx < docked.GetNumAtoms()]
    if not editable:
        return None
    repaired = Chem.Mol(reference)
    ref_conf = repaired.GetConformer()
    docked_conf = docked.GetConformer()
    for atom_idx in editable:
        ref_conf.SetAtomPosition(atom_idx, docked_conf.GetAtomPosition(atom_idx))
    return repaired


def classify_failure(example: dict[str, Any], failed_ligand_path: str | Path) -> str:
    geometry = protein_ligand_geometry(example.get("protein_path"), failed_ligand_path)
    clash_count = geometry.get("clash_count")
    anchor_error = anchor_distance_error(example.get("ligand_path"), failed_ligand_path, example.get("anchor_atoms", []))
    if clash_count not in (None, 0):
        return "vina_local_edit_clash"
    if anchor_error is not None and anchor_error > 1.0:
        return "vina_local_edit_anchor_drift"
    return "vina_local_edit_geometry_drift"


def make_candidate(example: dict[str, Any], index: int, failed_molecules_dir: Path) -> dict[str, Any] | None:
    ligand_path = example.get("ligand_path")
    docked_path = example.get("failed_ligand_path")
    if not ligand_path or not docked_path:
        return None
    mol = copy_editable_coordinates(ligand_path, docked_path, example.get("editable_atoms", []))
    if mol is None:
        return None
    complex_id = example.get("complex_id", "example")
    temporary_id = f"{complex_id}_vina_local_edit_{index}"
    failed_path = write_sdf(failed_molecules_dir / f"{temporary_id}.sdf", mol)
    failure_type = classify_failure(example, failed_path)
    candidate_id = f"{complex_id}_{failure_type}_{index}"
    final_path = failed_molecules_dir / f"{candidate_id}.sdf"
    if final_path != failed_path:
        failed_path.replace(final_path)
        failed_path = final_path
    return {
        "candidate_id": candidate_id,
        "complex_id": example.get("complex_id"),
        "failure_type": failure_type,
        "failure_reason": "editable_region_coordinates_from_vina_docked_pose_with_reference_scaffold_anchor",
        "source": "vina_local_edit_template_topology",
        "source_candidate_id": example.get("candidate_id"),
        "protein_path": example.get("protein_path"),
        "ligand_path": example.get("ligand_path"),
        "failed_ligand_path": str(failed_path),
        "ligand_smiles": example.get("ligand_smiles"),
        "scaffold_smiles": example.get("scaffold_smiles"),
        "scaffold_atoms": example.get("scaffold_atoms", []),
        "editable_atoms": example.get("editable_atoms", []),
        "anchor_atoms": example.get("anchor_atoms", []),
        "descriptors": example.get("descriptors", {}),
        "dataset_status": example.get("dataset_status"),
        "sample_quality": example.get("sample_quality", {}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_yaml(args.config)
    examples = read_jsonl(config["input"]["docked_candidates_path"])
    output_path = config["output"]["candidates_path"]
    failed_molecules_dir = Path(config["output"]["failed_molecules_dir"])

    rows = [candidate for index, example in enumerate(examples) if (candidate := make_candidate(example, index, failed_molecules_dir))]
    write_jsonl(output_path, rows)
    print(f"Read {len(examples)} Vina docked candidates from {config['input']['docked_candidates_path']}")
    print(f"Wrote {len(rows)} Vina-local-edit failed candidates to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
