# rgroup_smoke

本目录保存 `rgroup_smoke` 数据集的 dataset-scoped 资产。

## 结构

```text
rgroup_smoke/
  raw/<sample_id>/
  entries/index.jsonl
  entries/<sample_id>/entry.json
  splits/
  views/
  manifests/
    raw/
    entries/
    lineage/
```

- `raw/`: 该数据集的原始 protein/ligand 结构文件, 按 `sample_id` 分目录。
- `entries/`: 标准数据条目; `index.jsonl` 是批量读取入口, 每个 `entry.json` 与同名 raw sample 对应。
- `splits/`: train/validation/test 划分。
- `views/`: 面向具体任务的数据视图。
- `manifests/`: source、checksum、license/access、entry manifest 和 lineage 索引。
