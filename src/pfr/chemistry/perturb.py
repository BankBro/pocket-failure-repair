"""RDKit molecule perturbation helpers for smoke failed candidates."""

from __future__ import annotations

from pathlib import Path

from rdkit import Chem

from pfr.chemistry.rdkit_scaffold import load_first_molecule


def translate_molecule(mol: Chem.Mol, dx: float, dy: float, dz: float) -> Chem.Mol:
    copy = Chem.Mol(mol)
    if copy.GetNumConformers() == 0:
        return copy
    conf = copy.GetConformer()
    for atom_idx in range(copy.GetNumAtoms()):
        pos = conf.GetAtomPosition(atom_idx)
        conf.SetAtomPosition(atom_idx, (pos.x + dx, pos.y + dy, pos.z + dz))
    return copy


def perturb_failed_molecule(ligand_path: str | Path, failure_type: str) -> Chem.Mol | None:
    mol = load_first_molecule(ligand_path)
    if mol is None:
        return None
    if failure_type == "clash":
        return translate_molecule(mol, 0.5, 0.0, 0.0)
    if failure_type == "anchor_invalid":
        return translate_molecule(mol, 2.0, 0.0, 0.0)
    if failure_type == "geometry_invalid":
        return translate_molecule(mol, 0.0, 2.0, 0.0)
    return Chem.Mol(mol)


def write_sdf(path: str | Path, mol: Chem.Mol) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = Chem.SDWriter(str(output_path))
    writer.write(mol)
    writer.close()
    return output_path
