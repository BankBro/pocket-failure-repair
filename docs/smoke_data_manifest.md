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
| 1a4w | data/raw/smoke_complexes/1a4w/1a4w_protein.pdb | data/raw/smoke_complexes/1a4w/1a4w_ligand.sdf | RCSB PDB | https://www.rcsb.org/structure/1A4W | RCSB PDB usage policies | cite RCSB PDB entry | 11779ea2ad6a87636dd4c86b56660e157a799aef3354e24bbfa991348d473921 | 354351e7cb746a48bc3099a84a71fea5f8997666e686ea2b7012437d548d13e5 | public smoke sample |
| 1hvr | data/raw/smoke_complexes/1hvr/1hvr_protein.pdb | data/raw/smoke_complexes/1hvr/1hvr_ligand.sdf | RCSB PDB | https://www.rcsb.org/structure/1HVR | RCSB PDB usage policies | cite RCSB PDB entry | c8d3f238d3269a66823454d4681b71467b4677a18751ce094047961620b338cb | 1ea917adbdba4df0ebb5e2a69cbd15600aff5e0168758575735ef57ef4cf4974 | public smoke sample |
| 3ptb | data/raw/smoke_complexes/3ptb/3ptb_protein.pdb | data/raw/smoke_complexes/3ptb/3ptb_ligand.sdf | RCSB PDB | https://www.rcsb.org/structure/3PTB | RCSB PDB usage policies | cite RCSB PDB entry | 288f7954d4d013fa8eab3808e1037e2958e2dcd12c9eca65a3f1014404a9f9a2 | 606d6739d3ecc6e8feee84cc276fd40a1cd9a628bc01edbac8543b1b810789d5 | public smoke sample |

## 当前状态

- 已记录 3 个公开 smoke 样本.
- 原始结构文件位于 `data/raw/smoke_complexes/`, 由 `.gitignore` 排除, 不提交到 git.
- 机器可复现时应重新运行 `python scripts/data/download_smoke_complexes.py --config configs/data/smoke_download.yaml`.
