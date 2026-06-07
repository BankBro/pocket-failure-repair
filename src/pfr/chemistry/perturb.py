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


def valid_editable_atoms(mol: Chem.Mol, editable_atoms: list[int] | None) -> list[int]:
    valid = [atom_idx for atom_idx in editable_atoms or [] if 0 <= atom_idx < mol.GetNumAtoms()]
    if valid:
        return valid
    return [atom.GetIdx() for atom in mol.GetAtoms() if atom.GetAtomicNum() > 1]


def translate_atoms(mol: Chem.Mol, atom_indices: list[int], dx: float, dy: float, dz: float) -> Chem.Mol:
    copy = Chem.Mol(mol)
    if copy.GetNumConformers() == 0:
        return copy
    conf = copy.GetConformer()
    for atom_idx in atom_indices:
        pos = conf.GetAtomPosition(atom_idx)
        conf.SetAtomPosition(atom_idx, (pos.x + dx, pos.y + dy, pos.z + dz))
    return copy


def zigzag_atoms(mol: Chem.Mol, atom_indices: list[int], scale: float) -> Chem.Mol:
    copy = Chem.Mol(mol)
    if copy.GetNumConformers() == 0:
        return copy
    conf = copy.GetConformer()
    for offset_index, atom_idx in enumerate(atom_indices):
        sign = -1.0 if offset_index % 2 else 1.0
        pos = conf.GetAtomPosition(atom_idx)
        conf.SetAtomPosition(
            atom_idx,
            (pos.x + sign * scale, pos.y + (offset_index % 3 - 1) * scale * 0.5, pos.z - sign * scale * 0.25),
        )
    return copy


def mutate_first_valid_atom(mol: Chem.Mol, atom_indices: list[int], atomic_numbers: tuple[int, ...]) -> Chem.Mol | None:
    for atom_idx in atom_indices:
        atom = mol.GetAtomWithIdx(atom_idx)
        if atom.GetAtomicNum() == 1:
            continue
        for atomic_num in atomic_numbers:
            max_valence = {6: 4, 7: 3, 8: 2, 9: 1, 16: 6, 17: 1}.get(atomic_num)
            if max_valence is None or atom.GetTotalValence() > max_valence or atom.GetAtomicNum() == atomic_num:
                continue
            candidate = Chem.RWMol(mol)
            candidate.GetAtomWithIdx(atom_idx).SetAtomicNum(atomic_num)
            mutated = candidate.GetMol()
            try:
                Chem.SanitizeMol(mutated)
            except Exception:
                continue
            return mutated
    return None


def perturb_failed_molecule(
    ligand_path: str | Path, failure_type: str, editable_atoms: list[int] | None = None
) -> Chem.Mol | None:
    mol = load_first_molecule(ligand_path)
    if mol is None:
        return None
    editable = valid_editable_atoms(mol, editable_atoms)
    if failure_type == "clash":
        return translate_molecule(mol, 0.5, 0.0, 0.0)
    if failure_type == "interaction_loss":
        return translate_atoms(mol, editable, 0.0, 1.2, 0.4)
    if failure_type == "anchor_invalid":
        return translate_molecule(mol, 2.0, 0.0, 0.0)
    if failure_type == "geometry_invalid":
        return zigzag_atoms(mol, editable, 0.7)
    if failure_type == "linker_too_flexible":
        return zigzag_atoms(mol, editable, 1.2)
    if failure_type == "drug_likeness_drop":
        return mutate_first_valid_atom(mol, editable, (16, 17, 9, 7)) or zigzag_atoms(mol, editable, 0.4)
    if failure_type == "score_hacking":
        return translate_atoms(mol, editable, -0.8, 0.8, -0.8)
    return Chem.Mol(mol)


def write_sdf(path: str | Path, mol: Chem.Mol) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = Chem.SDWriter(str(output_path))
    writer.write(mol)
    writer.close()
    return output_path
