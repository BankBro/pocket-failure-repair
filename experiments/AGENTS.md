# experiments/AGENTS.md

## 实验目录规则

- 本目录下每次实验必须先定义 `experiment_name = xxx`, 再定义独立 `experiment_id = YYYYMMDD-<num>-<experiment_name>`。
- 若为某个实验新建 `docs/plan/` 或 `docs/report/` 文档, 文件名中的 `xxx` 优先使用该实验的 `experiment_name`。
- 每次实验的脚本、命令、配置快照、metadata 和说明放在 `experiments/<experiment_id>/`; 实际使用的配置快照放 `experiments/<experiment_id>/configs/resolved/`。
- 生成实验级 JSON / JSONL metadata 时, 若 `schemas/` 下已有对应 schema, 必须按 schema 写入字段, 并在输出中记录 `schema_version` 和 `schema_path`。
- schema 是可升级的版本化合同, 不是固定死的模板; 已被历史实验使用的版本不要静默改语义, 不兼容变更应新增 schema 版本并让新实验显式引用。
- 实验输入若使用 canonical dataset, 引用 `data/datasets/<dataset_id>/entries/index.jsonl` 或 dataset-local `raw/<sample_id>/`; 不把单次实验派生产物写回 `data/datasets/`。
- 对应输出放在 `outputs/<experiment_id>/`, 两边目录名必须一致。
- output-level manifest、hash registry、migration manifest 或 artifact registry 放在 `outputs/<experiment_id>/metadata/`; 实验管理 metadata 放在 `experiments/<experiment_id>/metadata/`。
- 跨实验复用的稳定脚本放根目录 `scripts/`; 单次实验专用脚本放 `experiments/<experiment_id>/scripts/`。
- 单次实验临时第三方 patch 放 `experiments/<experiment_id>/patches/`; 长期复用 patch 放 `third_party/patches/<method>/`; wrapper/instrumentation 放 `scripts/third_party/`。
- 不把大规模运行产物、per-sample JSONL、结构文件、工具原生报告、日志或临时 work 加入 git; 需要保留的关键信息提升为 summary、table、figure 或 metadata manifest。
- 实验完成或阶段性完成后, 在 `docs/EXPERIMENT_LOG.md` 追加记录 `experiment_id`、命令、配置、输出路径、结论、失败原因和下一步。
- 详细目录结构和字段说明见 `experiments/README.md`。
