from pathlib import Path

from pfr.data.manifest import sha256_file, write_docs_manifest


def test_sha256_file(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("abc", encoding="utf-8")

    assert sha256_file(path) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_write_docs_manifest(tmp_path: Path) -> None:
    path = tmp_path / "manifest.md"
    rows = [
        {
            "complex_id": "1abc",
            "protein_path": "data/raw/smoke_complexes/1abc/1abc_protein.pdb",
            "ligand_path": "data/raw/smoke_complexes/1abc/1abc_ligand.sdf",
            "source_url": "https://www.rcsb.org/structure/1ABC",
            "checksum_protein": "protein-sha",
            "checksum_ligand": "ligand-sha",
        }
    ]

    write_docs_manifest(path, rows)
    text = path.read_text(encoding="utf-8")

    assert "1abc" in text
    assert "https://www.rcsb.org/structure/1ABC" in text
    assert "protein-sha" in text
    assert "ligand-sha" in text
    assert "不提交到 git" in text
