#!/usr/bin/env python3
"""Download a tiny auditable smoke set from public RCSB endpoints."""

from __future__ import annotations

import argparse
import time
import urllib.request
from pathlib import Path
from typing import Any

from pfr.data.manifest import sha256_file, write_docs_manifest
from pfr.data.schema_refs import with_data_schema_ref
from pfr.utils.io import ensure_parent, load_yaml, write_json


def download(url: str, path: Path, retries: int = 3) -> None:
    ensure_parent(path)
    if path.exists() and path.stat().st_size > 0:
        return
    request = urllib.request.Request(url, headers={"User-Agent": "pocket-failure-repair-smoke/0.1"})
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                path.write_bytes(response.read())
            return
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(2 * attempt)
    raise RuntimeError(f"failed to download {url}: {last_error}")


def write_receptor_only_pdb(input_path: Path, output_path: Path) -> Path:
    ensure_parent(output_path)
    lines = []
    for line in input_path.read_text(errors="ignore").splitlines():
        if line.startswith("ATOM"):
            lines.append(line)
        elif line.startswith(("TER", "END")):
            lines.append(line)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


WATER_AND_IONS = {"HOH", "WAT", "DOD", "NA", "K", "CL", "CA", "MG", "ZN"}


def extract_ligand_pdb(input_path: Path, output_path: Path) -> tuple[Path, str | None]:
    residues: dict[tuple[str, str, str], list[str]] = {}
    for line in input_path.read_text(errors="ignore").splitlines():
        if not line.startswith("HETATM"):
            continue
        resname = line[17:20].strip()
        if resname in WATER_AND_IONS:
            continue
        chain = line[21].strip()
        resseq = line[22:26].strip()
        icode = line[26].strip()
        residues.setdefault((resname, chain, resseq + icode), []).append(line)
    if not residues:
        output_path.write_text("END\n", encoding="utf-8")
        return output_path, None
    key, lines = max(residues.items(), key=lambda item: len(item[1]))
    ensure_parent(output_path)
    output_path.write_text("\n".join(lines + ["END"]) + "\n", encoding="utf-8")
    return output_path, ":".join(part for part in key if part)


def infer_dataset_id_from_raw_dir(raw_dir: Path) -> str | None:
    parts = raw_dir.parts
    for index in range(len(parts) - 2):
        if parts[index] == "data" and parts[index + 1] == "datasets" and parts[index + 3 : index + 4] == ("raw",):
            return parts[index + 2]
    return None


def build_raw_manifest_payload(rows: list[dict[str, Any]], output: dict[str, Any]) -> dict[str, Any]:
    raw_dir = Path(output["complexes_dir"])
    payload: dict[str, Any] = {"source": "RCSB PDB", "complexes": rows}
    dataset_id = output.get("dataset_id") or infer_dataset_id_from_raw_dir(raw_dir)
    if dataset_id:
        payload["dataset_id"] = str(dataset_id)
    if output.get("dataset_version") is not None:
        payload["dataset_version"] = str(output["dataset_version"])
    return with_data_schema_ref(payload, "dataset_raw_manifest")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_yaml(args.config)
    output = config["output"]
    templates = config["rcsb"]
    complexes_dir = Path(output["complexes_dir"])
    rows: list[dict[str, Any]] = []

    for pdb_id_raw in config.get("pdb_ids", []):
        pdb_id = str(pdb_id_raw).lower()
        complex_dir = complexes_dir / pdb_id
        protein_path = complex_dir / f"{pdb_id}_protein.pdb"
        protein_clean_path = complex_dir / f"{pdb_id}_protein_clean.pdb"
        ligand_path = complex_dir / f"{pdb_id}_ligand.sdf"
        ligand_pdb_path = complex_dir / f"{pdb_id}_ligand.pdb"
        pdb_url = templates["pdb_url_template"].format(pdb_id=pdb_id.upper())
        ligand_url = templates["ligand_sdf_url_template"].format(pdb_id=pdb_id.upper())

        download(pdb_url, protein_path)
        write_receptor_only_pdb(protein_path, protein_clean_path)
        extracted_ligand_pdb_path, ligand_residue = extract_ligand_pdb(protein_path, ligand_pdb_path)
        download(ligand_url, ligand_path)
        rows.append(
            {
                "complex_id": pdb_id,
                "protein_path": str(protein_clean_path),
                "protein_raw_path": str(protein_path),
                "ligand_path": str(ligand_path),
                "ligand_pdb_path": str(extracted_ligand_pdb_path),
                "ligand_residue": ligand_residue,
                "source_url": f"https://www.rcsb.org/structure/{pdb_id.upper()}",
                "download_urls": {"protein_pdb": pdb_url, "ligand_sdf": ligand_url},
                "checksum_protein": sha256_file(protein_clean_path),
                "checksum_protein_raw": sha256_file(protein_path),
                "checksum_ligand": sha256_file(ligand_path),
                "checksum_ligand_pdb": sha256_file(extracted_ligand_pdb_path),
            }
        )
        print(f"Downloaded {pdb_id}: {protein_path}, {ligand_path}")

    write_json(output["manifest_path"], build_raw_manifest_payload(rows, output))
    docs_manifest_path = output.get("docs_manifest_path")
    if docs_manifest_path:
        write_docs_manifest(Path(docs_manifest_path), rows, config_path=args.config, raw_dir=str(complexes_dir))
    print(f"Wrote manifest to {output['manifest_path']}")
    if docs_manifest_path:
        print(f"Updated docs manifest at {docs_manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
