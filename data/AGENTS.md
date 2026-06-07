# data/AGENTS.md

## Agent 操作规则

- 不要把单次实验产物写入 `data/`; 默认写入 `outputs/<experiment_id>/`。
- 新数据集按 `data/datasets/<dataset_id>/` 建立独立 root, 不把多个 dataset 的 raw、entries、splits、views 或 lineage 混在一起。
- `data/templates/` 已退役; 第三方 audit 规则放入 `configs/audit/`, 第三方方法状态/协议记录放入 `configs/third_party/`, 字段格式合同放入 `schemas/third_party_audit/`, 不放回 `data/`。
- 不要直接删除、清洗、重命名或覆盖 `data/datasets/<dataset_id>/raw/` 里的原始文件。需要处理时, 先创建 manifest 记录问题和决策。
- `entries/index.jsonl` 是 canonical dataset entry index; 每条 entry 应有对应的 `entries/<sample_id>/entry.json`, 并与 `raw/<sample_id>/` 对齐。
- 新增或更新 canonical data writer 时, 先检查 `schemas/data/README.md` 和对应 schema; schema-covered JSON / JSONL 必须写入正确的 `schema_version` 和 `schema_path`, 优先复用 `pfr.data.schema_refs`。
- 运行 canonical data writer、RDKit scaffold/geometry 或 smoke pipeline 相关测试时, 默认使用 Conda env `pfr`; 不使用默认 shell 环境代替。
- `dataset_version` 是数据内容版本, `schema_version` 是文件格式版本; 不要把文件名版本、manifest id、view id 或 layout version 写成 `schema_version`。
- raw 结构文件本身不写 schema ref; source、checksum、license/access 和 schema ref 写入 dataset manifest。
- 对已有 legacy data metadata, 不要无记录地声称其符合新 schema; 要么保留 legacy 状态, 要么作为单独迁移记录后再回填。
- split registry 使用 `data/datasets/<dataset_id>/splits/<split_id>.json`, 不使用旧式 `data/splits/` 或顶层 manifest split 目录。
- 新增或更新 canonical entries 时, 同步维护 `data/datasets/<dataset_id>/manifests/lineage/raw_to_entry_index_v1.json` 和 `data/datasets/<dataset_id>/manifests/lineage/entry_to_raw_index_v1.json`, 并更新 `data/catalog/dataset_catalog_v1.json`; 不依赖全文搜索作为正常 lineage 查找方式。
- 遇到 gated access、需要登录/申请/付费、license 不清、大小未知可能超预算或非官方来源时, 暂停并记录 blocker, 不自动替换来源。
- 不提交大数据集、受限数据、第三方 checkpoint 或不可再分发资产。
