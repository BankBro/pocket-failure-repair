"""RDKit helpers for scaffold and editable-region smoke processing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rdkit import Chem
from rdkit.Chem import Crippen, Descriptors, Lipinski, QED, rdMolDescriptors
from rdkit.Chem.Scaffolds import MurckoScaffold


def load_first_molecule(path: str | Path) -> Chem.Mol | None:
    input_path = Path(path)
    suffix = input_path.suffix.lower()
    if suffix == ".sdf":
        supplier = Chem.SDMolSupplier(str(input_path), removeHs=False)
        for mol in supplier:
            if mol is not None:
                return mol
        return None
    if suffix in {".mol", ".mol2"}:
        return Chem.MolFromMolFile(str(input_path), removeHs=False, sanitize=True)
    return None


def molecule_descriptors(mol: Chem.Mol) -> dict[str, Any]:
    heavy_atoms = mol.GetNumHeavyAtoms()
    return {
        "num_atoms": mol.GetNumAtoms(),
        "num_heavy_atoms": heavy_atoms,
        "qed": float(QED.qed(mol)),
        "logp": float(Crippen.MolLogP(mol)),
        "rotatable_bonds": int(Lipinski.NumRotatableBonds(mol)),
        "molecular_weight": float(Descriptors.MolWt(mol)),
        "heavy_atom_molecular_weight": float(Descriptors.HeavyAtomMolWt(mol)),
        "tpsa": float(rdMolDescriptors.CalcTPSA(mol)),
    }


def scaffold_atom_indices(mol: Chem.Mol) -> list[int]:
    scaffold = MurckoScaffold.GetScaffoldForMol(mol)
    if scaffold is None or scaffold.GetNumAtoms() == 0:
        return []
    match = mol.GetSubstructMatch(scaffold)
    return sorted(int(index) for index in match)


def editable_atom_indices(mol: Chem.Mol, scaffold_atoms: list[int]) -> list[int]:
    scaffold_set = set(scaffold_atoms)
    return [atom.GetIdx() for atom in mol.GetAtoms() if atom.GetIdx() not in scaffold_set]


def anchor_atom_indices(mol: Chem.Mol, scaffold_atoms: list[int], editable_atoms: list[int]) -> list[int]:
    scaffold_set = set(scaffold_atoms)
    editable_set = set(editable_atoms)
    anchors: set[int] = set()
    for bond in mol.GetBonds():
        begin = bond.GetBeginAtomIdx()
        end = bond.GetEndAtomIdx()
        if begin in scaffold_set and end in editable_set:
            anchors.add(begin)
        elif end in scaffold_set and begin in editable_set:
            anchors.add(end)
    return sorted(anchors)


def summarize_ligand(path: str | Path) -> dict[str, Any]:
    mol = load_first_molecule(path)
    if mol is None:
        return {"status": "rdkit_read_failed"}
    Chem.SanitizeMol(mol)
    smiles = Chem.MolToSmiles(Chem.RemoveHs(mol), canonical=True)
    scaffold_atoms = scaffold_atom_indices(mol)
    editable_atoms = editable_atom_indices(mol, scaffold_atoms)
    anchors = anchor_atom_indices(mol, scaffold_atoms, editable_atoms)
    scaffold_smiles = None
    scaffold = MurckoScaffold.GetScaffoldForMol(mol)
    if scaffold is not None and scaffold.GetNumAtoms() > 0:
        scaffold_smiles = Chem.MolToSmiles(Chem.RemoveHs(scaffold), canonical=True)
    return {
        "status": "rdkit_ok",
        "ligand_smiles": smiles,
        "scaffold_smiles": scaffold_smiles,
        "scaffold_atoms": scaffold_atoms,
        "editable_atoms": editable_atoms,
        "anchor_atoms": anchors,
        "descriptors": molecule_descriptors(Chem.RemoveHs(mol)),
        "has_conformer": mol.GetNumConformers() > 0,
    }
