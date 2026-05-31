#!/usr/bin/env python3
"""Download a tiny auditable smoke set from public RCSB endpoints."""

from __future__ import annotations

import argparse
import time
import urllib.request
from pathlib import Path
from typing import Any

from pfr.data.manifest import sha256_file, write_docs_manifest
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
        ligand_path = complex_dir / f"{pdb_id}_ligand.sdf"
        pdb_url = templates["pdb_url_template"].format(pdb_id=pdb_id.upper())
        ligand_url = templates["ligand_sdf_url_template"].format(pdb_id=pdb_id.upper())

        download(pdb_url, protein_path)
        download(ligand_url, ligand_path)
        rows.append(
            {
                "complex_id": pdb_id,
                "protein_path": str(protein_path),
                "ligand_path": str(ligand_path),
                "source_url": f"https://www.rcsb.org/structure/{pdb_id.upper()}",
                "download_urls": {"protein_pdb": pdb_url, "ligand_sdf": ligand_url},
                "checksum_protein": sha256_file(protein_path),
                "checksum_ligand": sha256_file(ligand_path),
            }
        )
        print(f"Downloaded {pdb_id}: {protein_path}, {ligand_path}")

    write_json(output["manifest_path"], {"source": "RCSB PDB", "complexes": rows})
    write_docs_manifest(Path(output["docs_manifest_path"]), rows)
    print(f"Wrote manifest to {output['manifest_path']}")
    print(f"Updated docs manifest at {output['docs_manifest_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
