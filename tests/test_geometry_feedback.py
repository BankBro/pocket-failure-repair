from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem

from pfr.feedback.geometry import anchor_distance_error, parse_pdb_atom_coords, protein_ligand_geometry


def write_ligand(path: Path, smiles: str = "CCO") -> None:
    mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
    AllChem.EmbedMolecule(mol, randomSeed=0)
    writer = Chem.SDWriter(str(path))
    writer.write(mol)
    writer.close()


def test_parse_pdb_atom_coords(tmp_path: Path) -> None:
    pdb = tmp_path / "protein.pdb"
    pdb.write_text(
        "ATOM      1  C   ALA A   1       0.000   0.000   0.000  1.00 20.00           C\n",
        encoding="utf-8",
    )

    assert parse_pdb_atom_coords(pdb) == [(0.0, 0.0, 0.0)]


def test_protein_ligand_geometry_and_anchor_error(tmp_path: Path) -> None:
    pdb = tmp_path / "protein.pdb"
    pdb.write_text(
        "ATOM      1  C   ALA A   1       0.000   0.000   0.000  1.00 20.00           C\n",
        encoding="utf-8",
    )
    ref = tmp_path / "ref.sdf"
    cand = tmp_path / "cand.sdf"
    write_ligand(ref)
    write_ligand(cand)

    geometry = protein_ligand_geometry(pdb, cand, clash_cutoff=100.0)
    error = anchor_distance_error(ref, cand, [0])

    assert geometry["min_protein_ligand_distance"] is not None
    assert geometry["clash_count"] > 0
    assert error is not None
    assert error < 1e-6
