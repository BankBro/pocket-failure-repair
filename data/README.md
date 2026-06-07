# data 目录管理说明

本目录保存项目数据资产和数据 lineage 记录。当前主结构按 dataset 组织, 不把单次实验输出混入本目录。

## 顶层结构

```text
data/
  datasets/
    <dataset_id>/
      README.md
      raw/<sample_id>/
      entries/index.jsonl
      entries/<sample_id>/entry.json
      splits/
      views/
      manifests/
        raw/
        entries/
        lineage/
  catalog/
```

## 子目录职责

- `datasets/<dataset_id>/raw/`: 该数据集的原始输入文件, 按 `sample_id` 分目录。不要覆盖、清洗、重命名或删除原始结构内容。
- `datasets/<dataset_id>/entries/`: 数据集标准条目。`index.jsonl` 是脚本批量读取入口; `entries/<sample_id>/entry.json` 与 `raw/<sample_id>/` 直接对应。
- `datasets/<dataset_id>/splits/`: train / validation / test 划分文件。
- `datasets/<dataset_id>/views/`: 面向具体任务的数据视图。
- `datasets/<dataset_id>/manifests/`: source、checksum、license/access、entries manifest 和 lineage 索引。
- `catalog/`: 跨数据集 catalog 和 reconciliation 记录, 不混合具体样本条目。

## Lineage 索引

每个 dataset 自己维护结构化 lineage:

```text
data/datasets/<dataset_id>/manifests/lineage/
  raw_to_entry_index_v1.json
  entry_to_raw_index_v1.json
```

正常查 lineage 时先选 `dataset_id`, 再使用该数据集自己的索引。不要依赖全文搜索作为正常 lineage 查找方式。

## Schema 映射

`schemas/data/` 定义 canonical data JSON / JSONL 的字段规范。新生成或重写以下文件时, 应写入仓库相对的 `schema_path` 和对应 `schema_version`:

| data 文件 | schema_version | schema_path |
| --- | --- | --- |
| `datasets/<dataset_id>/entries/index.jsonl` 每一行 | `dataset_entry_v0_1` | `schemas/data/datasets/entries/dataset_entry_v0_1.json` |
| `datasets/<dataset_id>/entries/<sample_id>/entry.json` | `dataset_entry_v0_1` | `schemas/data/datasets/entries/dataset_entry_v0_1.json` |
| `datasets/<dataset_id>/splits/*.json` | `dataset_split_v0_1` | `schemas/data/datasets/splits/dataset_split_v0_1.json` |
| `datasets/<dataset_id>/views/*.json` | `dataset_view_v0_1` | `schemas/data/datasets/views/dataset_view_v0_1.json` |
| `datasets/<dataset_id>/manifests/raw/*.json` | `dataset_raw_manifest_v0_1` | `schemas/data/datasets/manifests/raw/dataset_raw_manifest_v0_1.json` |
| `datasets/<dataset_id>/manifests/entries/*.json` | `dataset_entries_manifest_v0_1` | `schemas/data/datasets/manifests/entries/dataset_entries_manifest_v0_1.json` |
| `datasets/<dataset_id>/manifests/lineage/raw_to_entry_index_v1.json` | `dataset_lineage_raw_to_entry_v0_1` | `schemas/data/datasets/manifests/lineage/dataset_lineage_raw_to_entry_v0_1.json` |
| `datasets/<dataset_id>/manifests/lineage/entry_to_raw_index_v1.json` | `dataset_lineage_entry_to_raw_v0_1` | `schemas/data/datasets/manifests/lineage/dataset_lineage_entry_to_raw_v0_1.json` |
| `catalog/dataset_catalog_v1.json` | `dataset_catalog_v0_1` | `schemas/data/catalog/dataset_catalog_v0_1.json` |
| `catalog/dataset_layout_migration_*.json` | `dataset_layout_migration_v0_1` | `schemas/data/catalog/dataset_layout_migration_v0_1.json` |
| `catalog/*raw_reconciliation*.json` | `dataset_raw_reconciliation_v0_1` | `schemas/data/catalog/dataset_raw_reconciliation_v0_1.json` |

`schema_version` 表示文件格式版本; `dataset_version` 表示数据集内容版本, 两者不要混用。文件名里的 `*_v1`, `dataset_view_id`, manifest id 或 layout version 不是 `schema_version`。

本节约束新生成的 data metadata。已有 legacy 文件若缺少 `schema_path` 或使用旧式 `schema_version`, 应在单独迁移步骤中处理, 不要无记录地批量回填。

## 记录要求

新增或移动数据时, 至少记录 source path、target path、checksum、生成脚本或命令、日期、license/access 状态和是否可再分发。重要变更追加到 `docs/EXPERIMENT_LOG.md`, 当前快照必要时更新 `docs/STATUS.md`。
