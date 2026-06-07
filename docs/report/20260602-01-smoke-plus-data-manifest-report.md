# Smoke Data Manifest

> 记录用于最小 smoke pipeline 的公开 protein-ligand complex 小样本. 不提交原始结构文件到 git; 只提交来源、路径约定和校验信息.

## 路径约定

```text
data/datasets/rgroup_smoke_plus/raw/<complex_id>/
  <complex_id>_protein.pdb
  <complex_id>_protein_clean.pdb
  <complex_id>_ligand.pdb
  <complex_id>_ligand.sdf
```

## manifest 表

| complex_id | protein_path | ligand_path | ligand_pdb_path | ligand_residue | source | source_url | license / terms | citation | checksum_protein | checksum_ligand | checksum_ligand_pdb | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1a4w | data/datasets/rgroup_smoke_plus/raw/1a4w/1a4w_protein_clean.pdb | data/datasets/rgroup_smoke_plus/raw/1a4w/1a4w_ligand.sdf | data/datasets/rgroup_smoke_plus/raw/1a4w/1a4w_ligand.pdb | QWE:H:373 | RCSB PDB | https://www.rcsb.org/structure/1A4W | RCSB PDB usage policies | cite RCSB PDB entry | f1e5d730d8da0466d65610eb2ee50df4441b159186b151dc84967753701427e7 | 48cfb99482a829995bb487691411856e43d4376d6f537e1a8285d86f798b048a | c90b7e840694a81360dc214c24d04648840f7aad2791fb8afdd6b3ed461083c2 | public smoke sample |
| 3ptb | data/datasets/rgroup_smoke_plus/raw/3ptb/3ptb_protein_clean.pdb | data/datasets/rgroup_smoke_plus/raw/3ptb/3ptb_ligand.sdf | data/datasets/rgroup_smoke_plus/raw/3ptb/3ptb_ligand.pdb | BEN:A:1 | RCSB PDB | https://www.rcsb.org/structure/3PTB | RCSB PDB usage policies | cite RCSB PDB entry | f7c892e210f0ae6b1808fe3663310a73351b2847b81fb6d77fe595d3a425541e | b34cf82dbd453d3fd6a115b443c24d8d25dac5f613ddf4dc957519962c3ed40e | 30eee424f8b7e87c4fcc1adb30dbb152017f940ba76901585bdcda34f5214a47 | public smoke sample |
| 1hsg | data/datasets/rgroup_smoke_plus/raw/1hsg/1hsg_protein_clean.pdb | data/datasets/rgroup_smoke_plus/raw/1hsg/1hsg_ligand.sdf | data/datasets/rgroup_smoke_plus/raw/1hsg/1hsg_ligand.pdb | MK1:B:902 | RCSB PDB | https://www.rcsb.org/structure/1HSG | RCSB PDB usage policies | cite RCSB PDB entry | 6d34b641ec8e839e9188000e13c40a80db795d552044410360d807ed2ef341ac | 86e8397d9cae1a53189a359bb06ffe02073cb435582ce161878654342e9a4049 | 2317919784d586e1b6c151742ad687836e40b8ef54555df8220916c2ef2ceb77 | public smoke sample |
| 1hvr | data/datasets/rgroup_smoke_plus/raw/1hvr/1hvr_protein_clean.pdb | data/datasets/rgroup_smoke_plus/raw/1hvr/1hvr_ligand.sdf | data/datasets/rgroup_smoke_plus/raw/1hvr/1hvr_ligand.pdb | XK2:A:263 | RCSB PDB | https://www.rcsb.org/structure/1HVR | RCSB PDB usage policies | cite RCSB PDB entry | 433d8194071e41bd52306cf18417a544dc4a54ad1a425e344c00fbb72c54c55e | f5ef3dc854e87db7a36b2fad98093d0a390fe0731880d41b8d9891c7b279c783 | 91dee43a9b689667660ad01608d6e265a5c989d1f36f9ae4bb76a3d454545627 | public smoke sample |
| 2br1 | data/datasets/rgroup_smoke_plus/raw/2br1/2br1_protein_clean.pdb | data/datasets/rgroup_smoke_plus/raw/2br1/2br1_ligand.sdf | data/datasets/rgroup_smoke_plus/raw/2br1/2br1_ligand.pdb | PFP:A:1277 | RCSB PDB | https://www.rcsb.org/structure/2BR1 | RCSB PDB usage policies | cite RCSB PDB entry | 3eb14f481427edc2b59b9f03087bd58d82ccef63391ecd9824d50ca15e13ebb3 | 6f0b3d8fa04d8fc8270de8cded238daed06a17cbd3f9249ed889733c3d03a3bf | 75ab9618561a20eb0cf3e361b6a160652402843cb74c85eadaad3940212f88b6 | public smoke sample |
| 3ert | data/datasets/rgroup_smoke_plus/raw/3ert/3ert_protein_clean.pdb | data/datasets/rgroup_smoke_plus/raw/3ert/3ert_ligand.sdf | data/datasets/rgroup_smoke_plus/raw/3ert/3ert_ligand.pdb | OHT:A:600 | RCSB PDB | https://www.rcsb.org/structure/3ERT | RCSB PDB usage policies | cite RCSB PDB entry | 701b52e10bf4896b5a98f9fcb6e57b28a2282b943bf9b36c1d270958fbaed34a | 8d7fa23f101a8c656ecb33b6731921e75a7d44cba4b28e2958c91d8aabdaead6 | 9fb48de72798200c3600144f328f921c65b1c2c9dc7615fdc73b339154bbba93 | public smoke sample |
| 1m17 | data/datasets/rgroup_smoke_plus/raw/1m17/1m17_protein_clean.pdb | data/datasets/rgroup_smoke_plus/raw/1m17/1m17_ligand.sdf | data/datasets/rgroup_smoke_plus/raw/1m17/1m17_ligand.pdb | AQ4:A:999 | RCSB PDB | https://www.rcsb.org/structure/1M17 | RCSB PDB usage policies | cite RCSB PDB entry | 90f1650577a6ed6d5b4157f836797b173e6f5074d6fcc9095bc33713c33d0fdf | cc6525e5e4bd4507e7f72d81e8b8725139855ebfa3a0c470dd83e3d35aeb6c0f | 62b9002ac00b80bd0f7e3a28a0c954b01573f523f9165653272dc338e28322e5 | public smoke sample |
| 2hyy | data/datasets/rgroup_smoke_plus/raw/2hyy/2hyy_protein_clean.pdb | data/datasets/rgroup_smoke_plus/raw/2hyy/2hyy_ligand.sdf | data/datasets/rgroup_smoke_plus/raw/2hyy/2hyy_ligand.pdb | STI:A:600 | RCSB PDB | https://www.rcsb.org/structure/2HYY | RCSB PDB usage policies | cite RCSB PDB entry | 7b01cdf5189eb53dda15076af249537060cf40c11d06aebf0c7cbc4ad59860a5 | 28a6d5232dae6437a460e873afb4c586318188c9ee6b5cbb297e9037591f46cb | 02be52b854a8c8619412768d989a6070533b5bc3f51598bf6ea7ea55b18f0f31 | public smoke sample |
| 3g0e | data/datasets/rgroup_smoke_plus/raw/3g0e/3g0e_protein_clean.pdb | data/datasets/rgroup_smoke_plus/raw/3g0e/3g0e_ligand.sdf | data/datasets/rgroup_smoke_plus/raw/3g0e/3g0e_ligand.pdb | B49:A:9000 | RCSB PDB | https://www.rcsb.org/structure/3G0E | RCSB PDB usage policies | cite RCSB PDB entry | 2081bf450826b273fb558653aa4681f03834c2b3e408ca2535d53b0ad8f4736d | 1fbee33767be8203eea4b604280d7dddeb40ad6ca9449fdb4db2f701da090a85 | b4183600af71a7c216aa8fea8cae945f83a226a72b19f528713fe7decf26abc8 | public smoke sample |
| 4dli | data/datasets/rgroup_smoke_plus/raw/4dli/4dli_protein_clean.pdb | data/datasets/rgroup_smoke_plus/raw/4dli/4dli_ligand.sdf | data/datasets/rgroup_smoke_plus/raw/4dli/4dli_ligand.pdb | IRG:A:401 | RCSB PDB | https://www.rcsb.org/structure/4DLI | RCSB PDB usage policies | cite RCSB PDB entry | 56232452b5f7e1c93f60341eedb0e611a4b4da68257bb6459a93ff4a902e1528 | c2db4beab97360ed19ea6482870d1ed5b91c0e4efcb58ee0a349940196f7b770 | 2030b603ae2b99a5aa4063a97ec8f7828c0f04086d06d8858e5cd6048f6f2e80 | public smoke sample |
| 4erw | data/datasets/rgroup_smoke_plus/raw/4erw/4erw_protein_clean.pdb | data/datasets/rgroup_smoke_plus/raw/4erw/4erw_ligand.sdf | data/datasets/rgroup_smoke_plus/raw/4erw/4erw_ligand.pdb | STU:A:301 | RCSB PDB | https://www.rcsb.org/structure/4ERW | RCSB PDB usage policies | cite RCSB PDB entry | 92ecac00441be75a1847da19e108faa304c58740105d933c17d4172e6b4e7b9f | 3f76ac37b71ecd3ee97ac1a0c04d7253d5cfd7e32fec23db3f7adbad62ef3388 | e95720d94280839f99272a0971bfc6514f9f1eeb8d9d18721c111bb657c9d17a | public smoke sample |
| 5p21 | data/datasets/rgroup_smoke_plus/raw/5p21/5p21_protein_clean.pdb | data/datasets/rgroup_smoke_plus/raw/5p21/5p21_ligand.sdf | data/datasets/rgroup_smoke_plus/raw/5p21/5p21_ligand.pdb | GNP:A:167 | RCSB PDB | https://www.rcsb.org/structure/5P21 | RCSB PDB usage policies | cite RCSB PDB entry | 389d8eacc7e4e2ac1d2e0adee1ab2e97098a577e42c65c5464fba9898615eec3 | 751365c4427ba56ee6d9528b909d61850e56ff0d37ab372da15068517f1a56e9 | 19f1d54e699e5a02974703e0c72170f18d8f87e48577ea903c1cb430766a654c | public smoke sample |

## 当前状态

- 已记录 12 个公开 smoke 样本.
- 原始结构文件位于 `data/datasets/rgroup_smoke_plus/raw/`, 由 `.gitignore` 排除, 不提交到 git.
- 机器可复现时应重新运行 `python scripts/data/download_smoke_complexes.py --config experiments/20260601-02-smoke-plus-expansion-and-variants/configs/resolved/data/smoke_plus_download.yaml`.
