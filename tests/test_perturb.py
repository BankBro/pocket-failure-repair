from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem

from pfr.chemistry.perturb import perturb_failed_molecule, write_sdf


def test_perturb_failed_molecule_writes_sdf(tmp_path: Path) -> None:
    mol = Chem.AddHs(Chem.MolFromSmiles("CCO"))
    AllChem.EmbedMolecule(mol, randomSeed=0)
    ligand_path = tmp_path / "ligand.sdf"
    writer = Chem.SDWriter(str(ligand_path))
    writer.write(mol)
    writer.close()

    perturbed = perturb_failed_molecule(ligand_path, "anchor_invalid")
    assert perturbed is not None
    output_path = write_sdf(tmp_path / "failed.sdf", perturbed)
    loaded = Chem.SDMolSupplier(str(output_path), removeHs=False)[0]

    assert loaded is not None
    assert loaded.GetNumAtoms() == mol.GetNumAtoms()
    assert output_path.exists()
