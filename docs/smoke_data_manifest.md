# Smoke Data Manifest

> 记录用于最小 smoke pipeline 的公开 protein-ligand complex 小样本. 不提交原始结构文件到 git; 只提交来源、路径约定和校验信息.

## 路径约定

每个 complex 放在独立目录中:

```text
data/raw/smoke_complexes/<complex_id>/
  <complex_id>_protein.pdb
  <complex_id>_ligand.sdf
  README.md
```

当前脚本会扫描 `data/raw/smoke_complexes/**/_ligand.*`, 并在同目录中寻找 `*_protein.*`.

## manifest 表

| complex_id | protein_path | ligand_path | source | source_url | license / terms | citation | checksum_protein | checksum_ligand | notes |
|---|---|---|---|---|---|---|---|---|---|
| TBD | data/raw/smoke_complexes/TBD/TBD_protein.pdb | data/raw/smoke_complexes/TBD/TBD_ligand.sdf | TBD | TBD | TBD | TBD | TBD | TBD | 待下载公开样本 |

## 选择标准

- 来源公开且可引用, 优先 PDBBind / RCSB PDB / CrossDocked 常见公开结构.
- ligand 具有 3D 坐标, 且能被 RDKit 读取.
- protein 与 ligand 坐标系一致.
- 结构大小适合 smoke test, 不用于声称模型性能.
- 每个样本保留来源 URL, 下载日期, 引用信息和校验和.

## 后续命令模板

```bash
# 创建目标环境后运行
python scripts/setup/check_environment.py

# 放入 1-3 个公开 complex 后运行
python scripts/data/build_rgroup_dataset.py --config configs/data/rgroup_smoke.yaml
python scripts/data/generate_failed_candidates.py --config configs/data/failed_candidate_smoke.yaml
python scripts/data/extract_feedback.py --config configs/feedback/smoke.yaml
python scripts/eval/eval_baselines.py --config configs/baselines/smoke.yaml
```

## 当前状态

- 尚未下载真实公开样本.
- 当前 pipeline 已通过 toy fixture 测试, 但真实化学处理需要 RDKit 环境.
