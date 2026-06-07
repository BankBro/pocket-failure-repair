# AGENTS.md

## 协作与文本规范

- 交互语言: 与仓库内的任何协作型 Agent 交互时, 以及与用户交互过程中, 请始终使用中文, 以保持沟通一致性.
- 文本格式: 所有写入文件或终端的文本使用 UTF-8; 中文说明使用英文标点.
- 文档目录: `docs/plan/` 用于研究规划、实验方案、路线图和阶段计划; `docs/report/` 用于实验报告、审计报告、阶段结果和复盘. 新建文档应按内容放入对应子目录.
- 文档命名: `docs/plan/` 下新建 Markdown 文档使用 `YYYYMMDD-<num>-xxx-plan.md`; `docs/report/` 下新建 Markdown 文档使用 `YYYYMMDD-<num>-xxx-report.md`. `<num>` 表示当天第几个新建文档. 如果文档对应某个实验, `xxx` 优先使用该实验的 `experiment_name`; 如果 plan 和 report 对应同一个实验或审计, 只要求中间的 `xxx` 相同; 日期和 `<num>` 可以不同, 因为计划时间和完成时间可能不同. 已有文档不需要改名.
- 关键状态文档: `docs/STATUS.md` 只记录当前最重要的项目快照, 用于上下文压缩或新会话后的快速恢复; `docs/EXPERIMENT_LOG.md` 追加记录完整实验、调研和阶段性工作过程, 包括输出、结论、失败原因和下一步.
- 中间产物管理: 需要创建临时脚本或中间文件时, 放在 `tmp/YYYYMMDD-<task-slug>/`, 其中 `<task-slug>` 使用简短英文 kebab-case; 任务结束后删除该子目录及其内容, 不把 `tmp/` 当长期资产目录.
- 实验目录规范: 每次实验先定义 `experiment_name = xxx`, 再定义 `experiment_id = YYYYMMDD-<num>-<experiment_name>`; 实验脚本、命令、配置和 metadata 放在 `experiments/<experiment_id>/`, 对应输出放在 `outputs/<experiment_id>/`. 详细规范见 `experiments/README.md` 和 `experiments/AGENTS.md`.
- Conda 环境规范: 项目开发、data writer、RDKit scaffold/geometry 和 smoke pipeline 测试默认使用 `pfr`; official PLIP / Vina / PoseBusters evaluator 使用 `pfr-eval-tools`; 第三方方法推理按方法单独创建环境, 不与 evaluator 环境混用.
- Metadata / config schema 规范: 新增项目自有 JSON / JSONL / YAML metadata 或配置时, 先判断归属并查 `schemas/README.md`: config schema 放 `schemas/configs/`, canonical data schema 放 `schemas/data/`, 第三方 audit 输出 schema 放 `schemas/third_party_audit/`. 若已有 schema, 必须按 schema 写入字段, 并记录 `schema_version` 和 `schema_path`; 明确例外包括 Conda environment 文件和外部工具原生输出. schema 是版本化合同, 已被实验使用的版本不要静默改语义; 改 required 字段、字段类型、字段含义或统计口径时应新增 schema 版本.
- 第三方 audit schema 规范: 当前第三方审计 schema 统一放在 `schemas/third_party_audit/`; 具体 schema 清单和输出文件映射见 `schemas/README.md`, protocol config 的 `metadata_schemas` key 映射见 `configs/README.md`. 历史 `schemas/audit/third_party_*` 路径只作为旧报告或旧 outputs provenance, 不作为新输出推荐路径.
- 数据目录规范: canonical dataset 统一放在 `data/datasets/<dataset_id>/`, 其中 `raw/<sample_id>/` 保存原始结构, `entries/index.jsonl` 是批量读取入口, `entries/<sample_id>/entry.json` 与同名 raw sample 对齐, `splits/`, `views/`, `manifests/` 分别保存划分、任务视图和 lineage/checksum/source 清单. 全局 dataset catalog 放在 `data/catalog/`; 第三方 audit 规则和第三方方法状态记录放入 `configs/audit/` 或 `configs/third_party/`, 不放入 `data/`; 单次运行配置放入对应 `experiments/<experiment_id>/configs/resolved/`.
- 文献与来源材料规范: `sources/` 保存论文、检索结果和人工调研 provenance, 不作为 canonical dataset、实验输出或第三方源码目录; 使用来源支撑结论时, 在 `docs/report/` 或 `docs/EXPERIMENT_LOG.md` 中引用对应来源路径和关键信息.
- 第三方源码与 patch 规范: 外部仓库放在 `third_party/`; 长期 patch、实验临时 patch 和 wrapper/instrumentation 的具体放置规则见 `third_party/README.md`.
