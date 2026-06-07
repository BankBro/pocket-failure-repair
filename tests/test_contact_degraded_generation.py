from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "data" / "generate_contact_degraded_local_edit_failures.py"
SPEC = spec_from_file_location("generate_contact_degraded_local_edit_failures", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
GENERATOR = module_from_spec(SPEC)
SPEC.loader.exec_module(GENERATOR)


def write_test_ligand(path: Path) -> None:
    mol = Chem.AddHs(Chem.MolFromSmiles("CCCO"))
    AllChem.EmbedMolecule(mol, randomSeed=7)
    writer = Chem.SDWriter(str(path))
    writer.write(mol)
    writer.close()


def test_make_candidates_respects_max_per_example(tmp_path: Path) -> None:
    ligand_path = tmp_path / "ligand.sdf"
    protein_path = tmp_path / "protein.pdb"
    write_test_ligand(ligand_path)
    protein_path.write_text(
        "ATOM      1  C   ALA A   1       1.000   0.000   0.000  1.00 20.00           C\n"
        "ATOM      2  O   ALA A   1       2.000   0.000   0.000  1.00 20.00           O\n"
        "END\n",
        encoding="utf-8",
    )
    example = {
        "complex_id": "toy",
        "protein_path": str(protein_path),
        "ligand_path": str(ligand_path),
        "editable_atoms": [1, 2, 3],
        "anchor_atoms": [0],
        "scaffold_atoms": [0],
        "sample_quality": {"evaluable_for_repair": True},
    }

    rows = GENERATOR.make_candidates(example, 0, tmp_path / "failed", seed=0, max_per_example=2, min_recovery_loss=-1.0)

    assert 0 < len(rows) <= 2
    assert all(row["failure_type"] == "contact_degraded_local_edit" for row in rows)
    assert [row["contact_degradation_rank"] for row in rows] == list(range(len(rows)))
    assert all(Path(row["failed_ligand_path"]).exists() for row in rows)
