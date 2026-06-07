# data schemas

`schemas/data/` 保存 canonical dataset 相关 JSON / JSONL 文件的字段规范。它只定义格式合同, 不保存数据本身。

## 当前结构

```text
schemas/data/
  catalog/
    dataset_catalog_v0_1.json
    dataset_layout_migration_v0_1.json
    dataset_raw_reconciliation_v0_1.json
  datasets/
    entries/
      dataset_entry_v0_1.json
    splits/
      dataset_split_v0_1.json
    views/
      dataset_view_v0_1.json
    manifests/
      raw/
        dataset_raw_manifest_v0_1.json
      entries/
        dataset_entries_manifest_v0_1.json
      lineage/
        dataset_lineage_raw_to_entry_v0_1.json
        dataset_lineage_entry_to_raw_v0_1.json
```

## 覆盖范围

```text
data/datasets/<dataset_id>/entries/<sample_id>/entry.json
数据集 entry, 对应 dataset_entry_v0_1.json

data/datasets/<dataset_id>/entries/index.jsonl
每一行同样对应 dataset_entry_v0_1.json

data/datasets/<dataset_id>/splits/*.json
数据集划分, 对应 dataset_split_v0_1.json

data/datasets/<dataset_id>/views/*.json
数据集任务视图, 对应 dataset_view_v0_1.json

data/datasets/<dataset_id>/manifests/raw/*.json
raw source/checksum manifest, 对应 dataset_raw_manifest_v0_1.json

data/datasets/<dataset_id>/manifests/entries/*.json
entries manifest, 对应 dataset_entries_manifest_v0_1.json

data/datasets/<dataset_id>/manifests/lineage/raw_to_entry_index_v1.json
raw 到 entry 的 lineage 索引, 对应 dataset_lineage_raw_to_entry_v0_1.json

data/datasets/<dataset_id>/manifests/lineage/entry_to_raw_index_v1.json
entry 到 raw 的 lineage 索引, 对应 dataset_lineage_entry_to_raw_v0_1.json

data/catalog/dataset_catalog_v1.json
全局 dataset catalog, 对应 dataset_catalog_v0_1.json

data/catalog/dataset_layout_migration_*.json
数据布局迁移记录, 对应 dataset_layout_migration_v0_1.json

data/catalog/*raw_reconciliation*.json
跨数据集 raw 重复与 checksum 差异记录, 对应 dataset_raw_reconciliation_v0_1.json
```

## 版本原则

- schema 是可升级的版本化合同, 不是固定死的模板。
- 旧 dataset 文件若已经声明某个 schema 版本, 不应因为新需求静默改旧 schema 语义。
- 不兼容变更应新增版本, 例如 `dataset_entry_v0_2.json`。
- `schema_version` 表示文件格式版本; `dataset_version` 表示数据集内容版本。两者不要混用。

## Writer 接入

新生成或重写 schema-covered data JSON / JSONL 时, writer 应写入仓库相对的 `schema_path` 和对应 `schema_version`:

| data 文件 | schema_version | schema_path |
| --- | --- | --- |
| `data/datasets/<dataset_id>/entries/index.jsonl` 每一行 | `dataset_entry_v0_1` | `schemas/data/datasets/entries/dataset_entry_v0_1.json` |
| `data/datasets/<dataset_id>/entries/<sample_id>/entry.json` | `dataset_entry_v0_1` | `schemas/data/datasets/entries/dataset_entry_v0_1.json` |
| `data/datasets/<dataset_id>/splits/*.json` | `dataset_split_v0_1` | `schemas/data/datasets/splits/dataset_split_v0_1.json` |
| `data/datasets/<dataset_id>/views/*.json` | `dataset_view_v0_1` | `schemas/data/datasets/views/dataset_view_v0_1.json` |
| `data/datasets/<dataset_id>/manifests/raw/*.json` | `dataset_raw_manifest_v0_1` | `schemas/data/datasets/manifests/raw/dataset_raw_manifest_v0_1.json` |
| `data/datasets/<dataset_id>/manifests/entries/*.json` | `dataset_entries_manifest_v0_1` | `schemas/data/datasets/manifests/entries/dataset_entries_manifest_v0_1.json` |
| `data/datasets/<dataset_id>/manifests/lineage/raw_to_entry_index_v1.json` | `dataset_lineage_raw_to_entry_v0_1` | `schemas/data/datasets/manifests/lineage/dataset_lineage_raw_to_entry_v0_1.json` |
| `data/datasets/<dataset_id>/manifests/lineage/entry_to_raw_index_v1.json` | `dataset_lineage_entry_to_raw_v0_1` | `schemas/data/datasets/manifests/lineage/dataset_lineage_entry_to_raw_v0_1.json` |
| `data/catalog/dataset_catalog_v1.json` | `dataset_catalog_v0_1` | `schemas/data/catalog/dataset_catalog_v0_1.json` |
| `data/catalog/dataset_layout_migration_*.json` | `dataset_layout_migration_v0_1` | `schemas/data/catalog/dataset_layout_migration_v0_1.json` |
| `data/catalog/*raw_reconciliation*.json` | `dataset_raw_reconciliation_v0_1` | `schemas/data/catalog/dataset_raw_reconciliation_v0_1.json` |

`schema_version` / `schema_path` 应优先由 `pfr.data.schema_refs` 提供, 不要在多个 writer 中复制常量。`dataset_split_v0_1` 中的新 writer 标准 `excluded_examples` 记录为对象, 包含 `complex_id` 和 `reasons`; string item 只用于兼容旧式记录。

当前已接入的活跃 writer:

- `scripts/data/build_rgroup_dataset.py`: 写 `dataset_entry_v0_1` 和 `dataset_split_v0_1`。
- `scripts/data/download_smoke_complexes.py`: 写 `dataset_raw_manifest_v0_1`。

已有 data 文件若缺少 `schema_path` 或使用旧式 `schema_version`, 应作为单独 metadata migration 处理; 不要在 writer 接入时无记录地批量回填。
