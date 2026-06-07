# 20260604-03-experiments-legacy-output-cleanup

experiment_name = experiments-legacy-output-cleanup
experiment_id = 20260604-03-experiments-legacy-output-cleanup

本目录记录 2026-06-04 对 legacy `experiments/smoke*` 输出散落, `outputs/<experiment_id>/raw/` / `normalized/` 生成产物语义, 以及 split/raw manifest 位置的规整。

## 输出

```text
outputs/20260604-03-experiments-legacy-output-cleanup/metadata/experiments_legacy_output_cleanup_manifest.json
```

## 边界

- 本次不修改 `.gitignore`。
- 本次不重算实验结果。
- 本次将 legacy experiments 输出和 generated raw/normalized artifacts 迁入 experiment-scoped `processed/` 命名空间。
- 本次集中 raw manifest 与 canonical split manifest。
- 本次不删除迁移前旧 raw 布局中的原始结构文件; clean receptor / extracted ligand PDB 的 raw/processed 边界和重复 checksum 问题先记录到 manifest, 后续单独 reconciliation。当前 canonical raw root 已迁到 `data/datasets/<dataset_id>/raw/`。
