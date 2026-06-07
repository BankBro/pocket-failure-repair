from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from pfr.data.manifest import sha256_file, write_docs_manifest


ROOT = Path(__file__).resolve().parents[1]


def load_download_script():
    script = ROOT / "scripts" / "data" / "download_smoke_complexes.py"
    spec = spec_from_file_location("download_smoke_complexes", script)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sha256_file(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("abc", encoding="utf-8")

    assert sha256_file(path) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_build_raw_manifest_payload_adds_schema_ref() -> None:
    module = load_download_script()
    rows = [{"complex_id": "1abc", "protein_path": "protein.pdb", "ligand_path": "ligand.sdf"}]

    payload = module.build_raw_manifest_payload(
        rows,
        {
            "complexes_dir": "data/datasets/rgroup_smoke/raw",
            "dataset_version": "v1",
        },
    )

    assert payload["schema_version"] == "dataset_raw_manifest_v0_1"
    assert payload["schema_path"] == "schemas/data/datasets/manifests/raw/dataset_raw_manifest_v0_1.json"
    assert payload["dataset_id"] == "rgroup_smoke"
    assert payload["dataset_version"] == "v1"
    assert payload["source"] == "RCSB PDB"
    assert payload["complexes"] == rows


def test_write_docs_manifest(tmp_path: Path) -> None:
    path = tmp_path / "manifest.md"
    rows = [
        {
            "complex_id": "1abc",
            "protein_path": "data/datasets/rgroup_smoke/raw/1abc/1abc_protein.pdb",
            "ligand_path": "data/datasets/rgroup_smoke/raw/1abc/1abc_ligand.sdf",
            "source_url": "https://www.rcsb.org/structure/1ABC",
            "checksum_protein": "protein-sha",
            "checksum_ligand": "ligand-sha",
        }
    ]

    write_docs_manifest(path, rows, config_path="configs/data/downloads/rcsb_smoke.yaml")
    text = path.read_text(encoding="utf-8")

    assert "1abc" in text
    assert "https://www.rcsb.org/structure/1ABC" in text
    assert "protein-sha" in text
    assert "ligand-sha" in text
    assert "不提交到 git" in text
