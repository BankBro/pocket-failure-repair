# data/catalog

本目录保存跨数据集 catalog 和 reconciliation manifest。

- `dataset_catalog_v1.json`: 数据集级索引目录, 只登记 dataset root 和关键 manifest 路径。
- `dataset_layout_migration_20260604_v1.json`: 顶层 raw/processed/manifests 布局迁入 dataset-scoped 布局的迁移记录。
- `rcsb_smoke_raw_reconciliation_v1.json`: smoke / smoke-plus raw 重复与 checksum 差异记录。

这些 JSON 都是项目自有 catalog metadata, 应写入 `schema_version` 和 `schema_path`; 具体映射见 `../README.md` 和 `../../schemas/data/README.md`。
