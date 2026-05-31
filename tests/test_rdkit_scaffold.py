from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem

from pfr.chemistry.rdkit_scaffold import summarize_ligand


def test_summarize_ligand_from_sdf(tmp_path: Path) -> None:
    mol = Chem.AddHs(Chem.MolFromSmiles("c1ccccc1CCO"))
    AllChem.EmbedMolecule(mol, randomSeed=0)
    path = tmp_path / "ligand.sdf"
    writer = Chem.SDWriter(str(path))
    writer.write(mol)
    writer.close()

    summary = summarize_ligand(path)

    assert summary["status"] == "rdkit_ok"
    assert summary["ligand_smiles"]
    assert summary["scaffold_smiles"] == "c1ccccc1"
    assert summary["scaffold_atoms"]
    assert summary["editable_atoms"]
    assert summary["anchor_atoms"]
    assert summary["descriptors"]["num_heavy_atoms"] == 9
    assert summary["has_conformer"]
