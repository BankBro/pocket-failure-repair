# Outputs Legacy Structure Cleanup

experiment_name = outputs-legacy-structure-cleanup
experiment_id = 20260604-01-outputs-legacy-structure-cleanup

本目录记录 `outputs/` 旧式 artifact family bucket 到 `outputs/<experiment_id>/` 结构的迁移。

迁移 manifest:

```text
outputs/20260604-01-outputs-legacy-structure-cleanup/metadata/outputs_migration_manifest.json
```

本次只移动历史产物路径并更新引用, 不重算实验结果。
