# Smoke Data Manifest

> 记录用于最小 smoke pipeline 的公开 protein-ligand complex 小样本. 不提交原始结构文件到 git; 只提交来源、路径约定和校验信息.

## 路径约定

```text
data/raw/smoke_complexes/<complex_id>/
  <complex_id>_protein.pdb
  <complex_id>_ligand.sdf
```

## manifest 表

| complex_id | protein_path | ligand_path | source | source_url | license / terms | citation | checksum_protein | checksum_ligand | notes |
|---|---|---|---|---|---|---|---|---|---|
| 1a4w | data/raw/smoke_complexes/1a4w/1a4w_protein.pdb | data/raw/smoke_complexes/1a4w/1a4w_ligand.sdf | RCSB PDB | https://www.rcsb.org/structure/1A4W | RCSB PDB usage policies | cite RCSB PDB entry | 11779ea2ad6a87636dd4c86b56660e157a799aef3354e24bbfa991348d473921 | b7a72cea3334a5a2bba233ac37809668fb18993ba54985522a5abbfd1eaa5f17 | public smoke sample |
| 3ptb | data/raw/smoke_complexes/3ptb/3ptb_protein.pdb | data/raw/smoke_complexes/3ptb/3ptb_ligand.sdf | RCSB PDB | https://www.rcsb.org/structure/3PTB | RCSB PDB usage policies | cite RCSB PDB entry | 288f7954d4d013fa8eab3808e1037e2958e2dcd12c9eca65a3f1014404a9f9a2 | f3d39512ca218f257c2b3f71b961a0129be8b9aec9224f681184733e9a1365ee | public smoke sample |
| 1hsg | data/raw/smoke_complexes/1hsg/1hsg_protein.pdb | data/raw/smoke_complexes/1hsg/1hsg_ligand.sdf | RCSB PDB | https://www.rcsb.org/structure/1HSG | RCSB PDB usage policies | cite RCSB PDB entry | d430675c358060808ef614002cfdcfcfa824714d89f1240adf5749d2ba60fed2 | 7c8ca05c575296ff8722c8181464a0e0b8ed5bf25db40c8330e84d0ee60fbdab | public smoke sample |

## 当前状态

- 已记录 3 个公开 smoke 样本.
- 原始结构文件位于 `data/raw/smoke_complexes/`, 由 `.gitignore` 排除, 不提交到 git.
- 机器可复现时应重新运行 `python scripts/data/download_smoke_complexes.py --config configs/data/smoke_download.yaml`.
