"""Geometry-derived feedback for protein-ligand smoke evaluation."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from rdkit import Chem

from pfr.chemistry.rdkit_scaffold import load_first_molecule


PROTEIN_ELEMENTS = {
    "H",
    "C",
    "N",
    "O",
    "S",
    "P",
    "F",
    "CL",
    "BR",
    "I",
    "MG",
    "ZN",
    "FE",
    "CA",
    "NA",
    "K",
}


def distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def parse_pdb_atom_coords(path: str | Path) -> list[tuple[float, float, float]]:
    coords: list[tuple[float, float, float]] = []
    input_path = Path(path)
    if not input_path.exists():
        return coords
    for line in input_path.read_text(errors="ignore").splitlines():
        if not line.startswith(("ATOM", "HETATM")):
            continue
        element = line[76:78].strip().upper() or line[12:16].strip()[0].upper()
        if element not in PROTEIN_ELEMENTS:
            continue
        try:
            coords.append((float(line[30:38]), float(line[38:46]), float(line[46:54])))
        except ValueError:
            continue
    return coords


def ligand_atom_coords(path: str | Path) -> list[tuple[float, float, float]]:
    mol = load_first_molecule(path)
    if mol is None or mol.GetNumConformers() == 0:
        return []
    conf = mol.GetConformer()
    coords: list[tuple[float, float, float]] = []
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 1:
            continue
        pos = conf.GetAtomPosition(atom.GetIdx())
        coords.append((float(pos.x), float(pos.y), float(pos.z)))
    return coords


def protein_ligand_geometry(
    protein_path: str | Path | None, ligand_path: str | Path | None, clash_cutoff: float = 2.0
) -> dict[str, Any]:
    if not protein_path or not ligand_path:
        return {"min_protein_ligand_distance": None, "clash_count": None}
    protein = parse_pdb_atom_coords(protein_path)
    ligand = ligand_atom_coords(ligand_path)
    if not protein or not ligand:
        return {"min_protein_ligand_distance": None, "clash_count": None}
    min_dist = min(distance(p, l) for p in protein for l in ligand)
    clash_count = sum(1 for p in protein for l in ligand if distance(p, l) < clash_cutoff)
    return {"min_protein_ligand_distance": min_dist, "clash_count": clash_count}


def anchor_distance_error(reference_ligand_path: str | Path | None, candidate_ligand_path: str | Path | None, anchors: list[int]) -> float | None:
    if not reference_ligand_path or not candidate_ligand_path or not anchors:
        return None
    reference = load_first_molecule(reference_ligand_path)
    candidate = load_first_molecule(candidate_ligand_path)
    if reference is None or candidate is None:
        return None
    if reference.GetNumConformers() == 0 or candidate.GetNumConformers() == 0:
        return None
    ref_conf = reference.GetConformer()
    cand_conf = candidate.GetConformer()
    errors: list[float] = []
    for anchor in anchors:
        if anchor >= reference.GetNumAtoms() or anchor >= candidate.GetNumAtoms():
            continue
        ref_pos = ref_conf.GetAtomPosition(anchor)
        cand_pos = cand_conf.GetAtomPosition(anchor)
        errors.append(
            distance(
                (float(ref_pos.x), float(ref_pos.y), float(ref_pos.z)),
                (float(cand_pos.x), float(cand_pos.y), float(cand_pos.z)),
            )
        )
    if not errors:
        return None
    return max(errors)
