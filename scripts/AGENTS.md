# scripts/AGENTS.md

## Agent 操作规则

- 根目录 `scripts/` 只放跨实验复用脚本; 单次实验专用脚本放 `experiments/<experiment_id>/scripts/`。
- 新脚本的默认输出路径必须遵守 `experiments/<experiment_id>/` 与 `outputs/<experiment_id>/` 对应关系; canonical dataset 资产除外, 应写入 `data/datasets/<dataset_id>/`。
- dry-run 或检查类脚本无参运行时不要写历史 experiment metadata 或 outputs; 写文件必须通过显式参数或明确 config。
- 项目开发、`scripts/data/*` writer、RDKit scaffold/geometry 和 smoke pipeline 测试默认使用 Conda env `pfr`; official PLIP / Vina / PoseBusters evaluator 使用 `pfr-eval-tools`。
- resolved config、命令快照和 run metadata 应写到 `experiments/<experiment_id>/`, 不写到 `outputs/processed/`。
- 生成 JSON / JSONL metadata 的脚本应优先参考 `schemas/` 中对应 schema; 输出文件应记录 `schema_version` 和 `schema_path`, 不要随意 invent 字段或改变已版本化 schema 的字段语义。
- 运行产物、metrics、tables、figures、logs 和 temporary work 写到 `outputs/<experiment_id>/`。
- 第三方 wrapper 使用 `captured_outputs/` 捕获方法输出; 不使用 `raw_outputs/` 作为默认目录名。
- 第三方 wrapper 新生成的 `run_metadata.json`, `samples.jsonl`, `output_manifest.json`, `stage_attrition.json` 应优先引用 `schemas/third_party_audit/` 下的分层 schema, 并使用去掉 `third_party_` 前缀后的 `schema_version`, 例如 `run_metadata_v0_1`, `failure_sample_metadata_v0_1`, `output_manifest_v0_1`。
- 第三方 audit 输出文件到 schema 的完整映射见 `schemas/README.md`; protocol config 的 `metadata_schemas` key 映射见 `configs/README.md`。
- 不要在 wrapper 中改变第三方方法的 sampling、decoding、filtering、reranking、docking config、success definition 或 candidate budget; 如必须改变, 必须降级标注为 adapted baseline。
- 新增或更新 canonical dataset writer 时, 同步写 `entries/index.jsonl` 和 `entries/<sample_id>/entry.json`, 并维护 `data/datasets/<dataset_id>/manifests/lineage/`。
- 新增或更新 `scripts/data/*` writer 时, 按 `schemas/data/README.md` 写入 data schema ref 和 `dataset_version`, 优先复用 `pfr.data.schema_refs`; 不要把 manifest/file instance version 充当 `schema_version`。
