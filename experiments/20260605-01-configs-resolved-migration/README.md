# 20260605-01-configs-resolved-migration

## Purpose

本实验记录 `configs/` resolved 配置迁移整理。目标是把绑定单次 `outputs/<experiment_id>/` 的配置移入对应 `experiments/<experiment_id>/configs/resolved/`, 并让项目级 `configs/` 只保留跨实验稳定模板、dataset config、audit protocol 和 tool lock。

## Main artifact

- `metadata/config_migration_manifest.json`
- `../../outputs/20260605-01-configs-resolved-migration/metadata/config_migration_manifest.json`

## Boundary

本次只整理配置路径和 provenance 记录, 不运行实验, 不重算指标, 不修改历史 output metadata 中的旧 path/hash。历史日志里的 `configs/...` 路径表示迁移前 provenance。
