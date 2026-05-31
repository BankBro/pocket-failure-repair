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


def write_docs_manifest(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Smoke Data Manifest",
        "",
        "> 记录用于最小 smoke pipeline 的公开 protein-ligand complex 小样本. 不提交原始结构文件到 git; 只提交来源、路径约定和校验信息.",
        "",
        "## 路径约定",
        "",
        "```text",
        "data/raw/smoke_complexes/<complex_id>/",
        "  <complex_id>_protein.pdb",
        "  <complex_id>_ligand.sdf",
        "```",
        "",
        "## manifest 表",
        "",
        "| complex_id | protein_path | ligand_path | source | source_url | license / terms | citation | checksum_protein | checksum_ligand | notes |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {complex_id} | {protein_path} | {ligand_path} | RCSB PDB | {source_url} | RCSB PDB usage policies | cite RCSB PDB entry | {checksum_protein} | {checksum_ligand} | public smoke sample |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## 当前状态",
            "",
            f"- 已记录 {len(rows)} 个公开 smoke 样本.",
            "- 原始结构文件位于 `data/raw/smoke_complexes/`, 由 `.gitignore` 排除, 不提交到 git.",
            "- 机器可复现时应重新运行 `python scripts/data/download_smoke_complexes.py --config configs/data/smoke_download.yaml`.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
