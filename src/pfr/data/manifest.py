"""Utilities for auditable public smoke-data manifests."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_docs_manifest(path: Path, rows: list[dict[str, Any]], config_path: str | None = None, raw_dir: str = "data/datasets/rgroup_smoke/raw") -> None:
    lines = [
        "# Smoke Data Manifest",
        "",
        "> 记录用于最小 smoke pipeline 的公开 protein-ligand complex 小样本. 不提交原始结构文件到 git; 只提交来源、路径约定和校验信息.",
        "",
        "## 路径约定",
        "",
        "```text",
        f"{raw_dir}/<complex_id>/",
        "  <complex_id>_protein.pdb",
        "  <complex_id>_protein_clean.pdb",
        "  <complex_id>_ligand.pdb",
        "  <complex_id>_ligand.sdf",
        "```",
        "",
        "## manifest 表",
        "",
        "| complex_id | protein_path | ligand_path | ligand_pdb_path | ligand_residue | source | source_url | license / terms | citation | checksum_protein | checksum_ligand | checksum_ligand_pdb | notes |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        display_row = {
            **row,
            "ligand_pdb_path": row.get("ligand_pdb_path", "N/A"),
            "ligand_residue": row.get("ligand_residue", "N/A"),
            "checksum_ligand_pdb": row.get("checksum_ligand_pdb", "N/A"),
        }
        lines.append(
            "| {complex_id} | {protein_path} | {ligand_path} | {ligand_pdb_path} | {ligand_residue} | RCSB PDB | {source_url} | RCSB PDB usage policies | cite RCSB PDB entry | {checksum_protein} | {checksum_ligand} | {checksum_ligand_pdb} | public smoke sample |".format(
                **display_row
            )
        )
    lines.extend(
        [
            "",
            "## 当前状态",
            "",
            f"- 已记录 {len(rows)} 个公开 smoke 样本.",
            f"- 原始结构文件位于 `{raw_dir}/`, 由 `.gitignore` 排除, 不提交到 git.",
            f"- 机器可复现时应重新运行 `python scripts/data/download_smoke_complexes.py --config {config_path or 'configs/data/downloads/rcsb_smoke.yaml'}`.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
