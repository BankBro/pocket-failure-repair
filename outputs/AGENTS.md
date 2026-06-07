# outputs/AGENTS.md

## Agent 操作规则

- 写入任何实验输出前, 先确认 `experiment_id = YYYYMMDD-<num>-<experiment_name>` 并使用 `outputs/<experiment_id>/`。
- 每个 `outputs/<experiment_id>/` 应有对应的 `experiments/<experiment_id>/`; 不要创建孤立输出目录。
- 默认使用 `processed/`, `logs/`, `metrics/`, `tables/`, `summaries/`, `figures/`, `work/` 等语义目录。
- output-level manifest、hash registry、migration manifest 或 artifact registry 放入 `metadata/`, 不与 `metrics/` 或 `processed/` 混用。
- 不要新建或推荐旧式 `raw/`, `normalized/`, `raw_outputs/`, `normalized_outputs/` 作为默认目录。
- 第三方方法捕获输出使用 `captured_outputs/`; normalized 或转换后的样本放入 `processed/normalized_samples/`。
- per-run metadata 必须足以追溯命令、配置、输入、输出、seed、commit/hash 和工具版本。
- 生成 `run_metadata.json`, `samples.jsonl`, `stage_attrition.json` 等 JSON / JSONL metadata 时, 若 `schemas/` 下已有对应 schema, 必须写入 `schema_version` 和 `schema_path`。
- 新第三方 audit outputs 的 schema refs 应使用 `schemas/third_party_audit/` 分层路径和去前缀版本名; 完整输出文件映射见 `schemas/README.md`。
- schema 是可升级的版本化合同; 输出 metadata 应继续指向生成时使用的 schema 版本, 不要因后续 schema 升级而静默改写历史 outputs metadata。
- 移动或重命名 outputs 后, 同步更新引用这些路径的 configs、scripts、docs、manifests 和 metadata。
- 若要把稳定输出提升为 canonical dataset, 必须进入 `data/datasets/<dataset_id>/entries/` 并维护 dataset-local manifests/lineage; 不要从 `outputs/` 直接充当 dataset root。
- 默认只提交轻量 provenance 和汇总结果, 如 `metadata/`, `summaries/`, `tables/`, `figures/*.svg` 和 summary metrics; 不要把大规模运行产物、受限第三方输出、日志、工具报告、结构文件、per-sample JSONL 或行级 processed/metrics 结果加入 git。
