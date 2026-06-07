from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem

from pfr.chemistry.perturb import perturb_failed_molecule, write_sdf


def first_atom_position(mol: Chem.Mol) -> tuple[float, float, float]:
    pos = mol.GetConformer().GetAtomPosition(0)
    return (round(float(pos.x), 3), round(float(pos.y), 3), round(float(pos.z), 3))


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


def test_realistic_failure_types_change_coordinates_or_atom_types(tmp_path: Path) -> None:
    mol = Chem.AddHs(Chem.MolFromSmiles("CCO"))
    AllChem.EmbedMolecule(mol, randomSeed=1)
    ligand_path = tmp_path / "ligand.sdf"
    writer = Chem.SDWriter(str(ligand_path))
    writer.write(mol)
    writer.close()

    for failure_type in ("interaction_loss", "linker_too_flexible", "drug_likeness_drop", "score_hacking"):
        perturbed = perturb_failed_molecule(ligand_path, failure_type, [0, 1, 2])
        assert perturbed is not None
        changed_position = first_atom_position(perturbed) != first_atom_position(mol)
        changed_atoms = [atom.GetAtomicNum() for atom in perturbed.GetAtoms()] != [atom.GetAtomicNum() for atom in mol.GetAtoms()]
        assert changed_position or changed_atoms
