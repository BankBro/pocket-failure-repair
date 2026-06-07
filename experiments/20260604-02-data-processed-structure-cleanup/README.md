# 20260604-02-data-processed-structure-cleanup

experiment_name = data-processed-structure-cleanup
experiment_id = 20260604-02-data-processed-structure-cleanup

本目录记录 2026-06-04 对迁移前旧 processed 布局派生产物的结构规整。当前 canonical dataset entry 已改为 `data/datasets/<dataset_id>/entries/index.jsonl`。

## 目标

- 保留当时的 canonical reusable dataset, 现已迁为 entries:

```text
data/datasets/rgroup_smoke/entries/index.jsonl
data/datasets/rgroup_smoke_plus/entries/index.jsonl
```

- 将非 canonical 派生产物按实验归档到:

```text
outputs/<experiment_id>/processed/
```

- 同步更新可执行配置、脚本默认路径、实验配置快照、文档和指标 metadata 中对迁移前旧 processed JSONL 派生产物的引用。

## 输出

迁移清单与校验记录:

```text
outputs/20260604-02-data-processed-structure-cleanup/metadata/data_processed_migration_manifest.json
```

## 边界

- 初始采用 copy-and-retarget: 复制到新路径并更新引用。
- 用户确认后已删除迁移前旧 processed 布局中的 87 个非 canonical 派生产物源文件。
- 保留 `data/datasets/rgroup_smoke/entries/index.jsonl` 和 `data/datasets/rgroup_smoke_plus/entries/index.jsonl`。
- 不执行 `git rm` / `git rm --cached`。
- 不修改 `.gitignore`。
- 不重算实验结果, 不改变 JSONL 内容。
