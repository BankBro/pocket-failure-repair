# Smoke Data Manifest

> 记录用于最小 smoke pipeline 的公开 protein-ligand complex 小样本. 不提交原始结构文件到 git; 只提交来源、路径约定和校验信息.

## 路径约定

```text
data/datasets/rgroup_smoke/raw/<complex_id>/
  <complex_id>_protein.pdb
  <complex_id>_protein_clean.pdb
  <complex_id>_ligand.pdb
  <complex_id>_ligand.sdf
```

## manifest 表

| complex_id | protein_path | ligand_path | ligand_pdb_path | ligand_residue | source | source_url | license / terms | citation | checksum_protein | checksum_ligand | checksum_ligand_pdb | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1a4w | data/datasets/rgroup_smoke/raw/1a4w/1a4w_protein_clean.pdb | data/datasets/rgroup_smoke/raw/1a4w/1a4w_ligand.sdf | data/datasets/rgroup_smoke/raw/1a4w/1a4w_ligand.pdb | QWE:H:373 | RCSB PDB | https://www.rcsb.org/structure/1A4W | RCSB PDB usage policies | cite RCSB PDB entry | f1e5d730d8da0466d65610eb2ee50df4441b159186b151dc84967753701427e7 | ab0e8eb8f7ba5208efab96464c6ecb45218fce9efa02933febb1edb1ffaa4d3f | c90b7e840694a81360dc214c24d04648840f7aad2791fb8afdd6b3ed461083c2 | public smoke sample |
| 3ptb | data/datasets/rgroup_smoke/raw/3ptb/3ptb_protein_clean.pdb | data/datasets/rgroup_smoke/raw/3ptb/3ptb_ligand.sdf | data/datasets/rgroup_smoke/raw/3ptb/3ptb_ligand.pdb | BEN:A:1 | RCSB PDB | https://www.rcsb.org/structure/3PTB | RCSB PDB usage policies | cite RCSB PDB entry | f7c892e210f0ae6b1808fe3663310a73351b2847b81fb6d77fe595d3a425541e | aad8c7081fff29df75e055490e582591bcdd7252baa11dfaefdebc1a16ceb7d0 | 30eee424f8b7e87c4fcc1adb30dbb152017f940ba76901585bdcda34f5214a47 | public smoke sample |
| 1hsg | data/datasets/rgroup_smoke/raw/1hsg/1hsg_protein_clean.pdb | data/datasets/rgroup_smoke/raw/1hsg/1hsg_ligand.sdf | data/datasets/rgroup_smoke/raw/1hsg/1hsg_ligand.pdb | MK1:B:902 | RCSB PDB | https://www.rcsb.org/structure/1HSG | RCSB PDB usage policies | cite RCSB PDB entry | 6d34b641ec8e839e9188000e13c40a80db795d552044410360d807ed2ef341ac | 729ca15705d50ac24900eae6bb75c6f5cdfad3981995066dd00a5ee9aa10fd20 | 2317919784d586e1b6c151742ad687836e40b8ef54555df8220916c2ef2ceb77 | public smoke sample |

## 当前状态

- 已记录 3 个公开 smoke 样本.
- 原始结构文件位于 `data/datasets/rgroup_smoke/raw/`, 由 `.gitignore` 排除, 不提交到 git.
- 机器可复现时应重新运行 `python scripts/data/download_smoke_complexes.py --config experiments/20260531-01-smoke-file-pipeline/configs/resolved/data/smoke_download.yaml`.
