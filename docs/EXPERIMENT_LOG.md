# EXPERIMENT_LOG

> 这个文档用于追加记录完整实验过程，可以逐渐变长。每个阶段都要记录目的、命令、配置、结果路径、结论和下一步判断。

---

## 2026-06-05 / configs resolved 配置迁移整理

- 阶段名称: `configs-resolved-migration`
- experiment_id: `20260605-01-configs-resolved-migration`
- 实验记录目录: `experiments/20260605-01-configs-resolved-migration/`
- 输出记录目录: `outputs/20260605-01-configs-resolved-migration/`
- 迁移清单: `experiments/20260605-01-configs-resolved-migration/metadata/config_migration_manifest.json`

### 阶段目标

- 收敛项目级 `configs/`, 只保留跨实验稳定模板、audit protocol、tool lock 和 canonical dataset 配置。
- 将绑定单次 `outputs/<experiment_id>/` 的 smoke / smoke-plus / repair / eval resolved 配置迁入对应 `experiments/<experiment_id>/configs/resolved/`。
- 对 mixed config 保留实验 resolved snapshot, 同时把项目级版本改为模板或路径无关协议。

### 主要操作

- 已将 `configs/baselines/*.yaml`, `configs/feedback/*.yaml`, `configs/data/failed_candidate_*.yaml` 和顶层 eval summary 配置迁到对应实验的 `configs/resolved/`。
- `configs/data/smoke_download.yaml` 与 `configs/data/smoke_plus_download.yaml` 的完整当前版本已保存到实验 resolved 目录; 项目级模板移到 `configs/data/download_templates/`。
- DiffSBDD / DiffLinker audit protocol 的完整 MVP resolved 版本已保存到 `experiments/20260603-01-third-party-failure-audit-mvp/configs/resolved/third_party/`; 项目级 `configs/third_party/*_audit_protocol.yaml` 保留为带 `{experiment_id}` / `{run_id}` 占位的模板。
- 已同步 active script 默认路径: `scripts/setup/smoke_pipeline_dry_run.py`, `scripts/eval/run_repaired_multiseed.py`, `scripts/data/download_smoke_complexes.py`, `src/pfr/data/manifest.py`。

### 边界说明

- 本次只整理配置路径和 provenance, 不运行实验, 不重算指标。
- 历史日志、历史 output metadata 和 hash manifest 中的旧 `configs/...` 路径保留为迁移前 provenance, 不代表当前推荐放置位置。
- 部分 `docking_like` / `local_proposal` 配置保留 mixed output root 的历史快照, 未静默归一化输出路径。

---

## 2026-06-07 / data metadata schema ref 迁移

- 阶段名称: `data-metadata-schema-ref-migration`
- 负责人 / agent: Codex
- 环境: `pfr`
- 数据范围: `data/` 下项目自有 JSON / JSONL metadata。

### 阶段目标

- 将当前 canonical data metadata 从 legacy `schema_version` 或缺失 `schema_path` 状态迁移到显式 `schema_version` / `schema_path`。
- 让 `data/` 下当前 JSON / JSONL metadata 都能追溯到 `schemas/data/` 中的具体 schema。
- 只迁移 metadata refs 和由此引起的 entry index checksum, 不重算实验结果, 不改写 raw `.pdb` / `.sdf` 结构文件。

### 主要操作

- 补充 catalog 特殊记录 schema: `schemas/data/catalog/dataset_layout_migration_v0_1.json` 和 `schemas/data/catalog/dataset_raw_reconciliation_v0_1.json`。
- 更新 schema 映射文档: `data/README.md`, `data/catalog/README.md`, `schemas/data/README.md`, `schemas/README.md`。
- 对 `data/datasets/rgroup_smoke/` 和 `data/datasets/rgroup_smoke_plus/` 下的 entries, splits, views, raw manifests, entries manifests 和 lineage manifests 补齐当前 schema refs。
- 对 `data/catalog/dataset_catalog_v1.json`, `data/catalog/dataset_layout_migration_20260604_v1.json`, `data/catalog/rcsb_smoke_raw_reconciliation_v1.json` 补齐当前 schema refs。
- 因为 `entries/index.jsonl` 每行补入 schema refs 会改变文件内容, 已同步更新对应 entries manifest 和 lineage link 中的 `entry_index_sha256`。
- 新增 `tests/test_data_schema_refs.py`, 用于检查 `data/` 下 JSON / JSONL schema refs 和 `entry_index_sha256` 一致性。

### 命令与校验

```bash
conda run -n pfr env PYTHONPATH=src python tmp/20260607-data-metadata-schema-ref-migration/migrate_data_metadata_schema_refs.py
conda run -n pfr env PYTHONPATH=src pytest -q tests/test_data_schema_refs.py tests/test_config_schema_refs.py tests/test_audit_schemas.py tests/test_download_smoke_complexes.py tests/test_smoke_pipeline.py
```

### 输出与结果

- 迁移脚本报告: `changed_files=32`, `validated_json_files=30`, `validated_jsonl_rows=15`。
- 本次临时迁移脚本按中间产物处理, 执行和校验后删除, 不作为长期项目脚本保留。
- raw 结构文件未改写; 历史 `outputs/` 和历史 `experiments/` metadata 未纳入本次迁移范围。

### 结论

- 当前 `data/` 下项目自有 JSON / JSONL metadata 已具备显式 schema refs。
- 后续新增或调整 data metadata 时, 应先查 `schemas/data/README.md`, 复用或升级 schema, 并在 writer 输出中写入 `schema_version` 和 `schema_path`。

---

## 日志条目模板

### 日期 / 阶段

- 日期：
- 阶段名称：
- 负责人 / agent：
- commit：
- 环境：
- GPU / CPU：
- 数据版本：
- 随机种子：

### 阶段目标

- 
- 
- 

### 背景与判断

- 为什么做这个实验：
- 需要验证的假设：
- 与上一阶段的关系：

### 插件 / Skill / Workflow 使用记录

- 使用的 plugin / skill / agent / workflow：
- 使用目的：
- 输入：
- 输出路径：
- 是否成功：
- 失败原因或降级方案：
- 对本阶段结论的影响：

### 命令与配置

```bash
# command here
```

配置文件：

- 

### 输出文件

- metrics：
- tables：
- figures：
- molecules：
- logs：
- checkpoints：

### 主要结果

| 指标 | 结果 | 备注 |
|---|---:|---|
| same-budget success rate | | |
| scaffold preservation | | |
| editable validity | | |
| anchor validity | | |
| clash count | | |
| PoseBusters pass | | |
| PLIP interaction recovery | | |
| Vina / ΔVina | | |
| ligand efficiency | | |
| QED | | |
| SA | | |

### 结论

- 
- 
- 

### 失败 / 异常 / 负结果

- 
- 
- 

### 下一步

- 
- 
- 

---

## 实验日志

### 2026-05-31 / 项目初始化

- 日期：2026-05-31
- 阶段名称：项目初始化与文档归位
- 负责人 / agent：Claude Code
- commit：0693688 Initial commit
- 环境：尚未创建 conda 环境
- GPU / CPU：未使用
- 数据版本：无
- 随机种子：无

### 阶段目标

- 创建项目目录框架。
- 将原始项目文档归位到 `docs/`。
- 建立 README、方法设计和文献矩阵骨架。
- 更新 `docs/STATUS.md`，便于后续恢复上下文。

### 背景与判断

- 为什么做这个实验：项目需要先形成可复现、可审计的工程结构，再进入文献检索、环境搭建和 smoke pipeline。
- 需要验证的假设：无实验假设，本阶段是工程初始化。
- 与上一阶段的关系：承接根目录原始研究说明文档。

### 插件 / Skill / Workflow 使用记录

- 使用的 plugin / skill / agent / workflow：未使用外部插件或 workflow；使用本地文件与 shell 工具。
- 使用目的：创建目录、移动文档、写入文档骨架。
- 输入：根目录初始 Markdown 文档。
- 输出路径：`README.md`、`docs/STATUS.md`、`docs/EXPERIMENT_LOG.md`、`docs/plan/20260601-01-method-design-plan.md`、`docs/report/20260601-02-literature-matrix-report.md`。
- 是否成功：成功。
- 失败原因或降级方案：无。
- 对本阶段结论的影响：项目可以进入文献检索、环境初始化和 smoke pipeline 设计。

### 命令与配置

```bash
mkdir -p configs data/raw data/processed data/splits src/pfr/{data,chemistry,feedback,models,baselines,evaluation,workflows,utils} scripts/{setup,data,train,eval,analysis} experiments/{smoke,main,ablations,baselines} outputs/{metrics,tables,figures,molecules,logs} docs tests third_party
mv 00_research_brief.md docs/plan/20260601-05-research-brief-plan.md
mv 01_project_protocol.md docs/plan/20260601-04-project-protocol-plan.md
mv 02_claude_goal_prompt.md docs/plan/20260601-03-claude-goal-prompt-plan.md
mv 03_status_template.md docs/STATUS.md
mv 04_experiment_log_template.md docs/EXPERIMENT_LOG.md
mv 05_bibm_execution_notes.md docs/plan/20260601-02-bibm-execution-notes-plan.md
```

配置文件：

- 暂无。

### 输出文件

- metrics：无。
- tables：无。
- figures：无。
- molecules：无。
- logs：`docs/EXPERIMENT_LOG.md`。
- checkpoints：无。

### 主要结果

| 指标 | 结果 | 备注 |
|---|---:|---|
| same-budget success rate | N/A | 尚未实验 |
| scaffold preservation | N/A | 尚未实验 |
| editable validity | N/A | 尚未实验 |
| anchor validity | N/A | 尚未实验 |
| clash count | N/A | 尚未实验 |
| PoseBusters pass | N/A | 尚未实验 |
| PLIP interaction recovery | N/A | 尚未实验 |
| Vina / ΔVina | N/A | 尚未实验 |
| ligand efficiency | N/A | 尚未实验 |
| QED | N/A | 尚未实验 |
| SA | N/A | 尚未实验 |

### 结论

- 项目工程骨架已创建。
- 原始文档已归位到 `docs/`。
- 下一步应优先进行文献检索与撞题分析。

### 失败 / 异常 / 负结果

- 尚无实验失败。
- Read 工具在本会话中对 Markdown 文件误传空 `pages` 参数导致读取失败，已通过正确参数或 shell 文本读取绕过；不影响项目文件。

### 下一步

- 完成 `docs/report/20260601-02-literature-matrix-report.md` 第一轮检索。
- 补 `environment.yml`。
- 设计并实现最小 smoke pipeline。

---

### 2026-05-31 / 第一轮文献与撞题分析

- 日期：2026-05-31
- 阶段名称：第一轮文献检索与撞题分析
- 负责人 / agent：Claude Code + general-purpose research agents
- commit：511daa9 Initialize research project scaffold
- 环境：尚未创建 conda 环境；使用当前系统 Python 进行 OpenAlex 查询
- GPU / CPU：未使用 GPU
- 数据版本：无
- 随机种子：无

### 阶段目标

- 检索 DiffDec, DiffLEOP, AMG, MolJO, DecompDPO, DecompDiff, DecompOpt, PoseBusters, PLIP, AutoDock Vina 的可核验来源。
- 判断是否存在 failed-candidate-conditioned pocket-aware 3D local repair 的直接撞题工作。
- 将第一轮证据写入 `docs/report/20260601-02-literature-matrix-report.md`。

### 背景与判断

- 为什么做这个实验：在启动模型实现或长期实验前, 需要先确认课题切口是否已经被已有工作覆盖。
- 需要验证的假设：本项目的核心差异在于 failed candidate + explicit failure feedback + pocket-aware local repair + same-budget evaluation 的组合。
- 与上一阶段的关系：承接项目初始化阶段, 进入文献和撞题风险确认。

### 插件 / Skill / Workflow 使用记录

- 使用的 plugin / skill / agent / workflow：CCS WebSearch MCP, OpenAlex API 查询, general-purpose research agents, Explore agent, Plan agent。
- 使用目的：检索论文/工具来源, 核验方法职责, 形成文献矩阵和撞题判断。
- 输入：目标方法列表与横向检索关键词。
- 输出路径：`docs/report/20260601-02-literature-matrix-report.md`, `docs/STATUS.md`, `docs/EXPERIMENT_LOG.md`。
- 是否成功：部分成功。
- 失败原因或降级方案：CCS WebSearch 对部分查询返回反爬/非结果 HTML；arXiv API 一次超时。已降级到 OpenAlex API, 研究 Agent 检索和官方文档/DOI 来源。
- 对本阶段结论的影响：可支持第一轮撞题判断, 但 AMG / MolJO 和部分模型指标仍需二轮原文核验。

### 命令与配置

```bash
python - <<'PY'
# 使用 urllib 查询 OpenAlex works API, 检索 DiffDec, DiffLEOP, DecompDPO, DecompDiff, DecompOpt 等方法元数据。
PY
```

配置文件：

- 暂无。

### 输出文件

- metrics：无。
- tables：`docs/report/20260601-02-literature-matrix-report.md`。
- figures：无。
- molecules：无。
- logs：`docs/EXPERIMENT_LOG.md`。
- checkpoints：无。

### 主要结果

| 指标 | 结果 | 备注 |
|---|---:|---|
| same-budget success rate | N/A | 尚未实验 |
| scaffold preservation | N/A | 尚未实验 |
| editable validity | N/A | 尚未实验 |
| anchor validity | N/A | 尚未实验 |
| clash count | N/A | 尚未实验 |
| PoseBusters pass | N/A | 尚未实验 |
| PLIP interaction recovery | N/A | 尚未实验 |
| Vina / ΔVina | N/A | 尚未实验 |
| ligand efficiency | N/A | 尚未实验 |
| QED | N/A | 尚未实验 |
| SA | N/A | 尚未实验 |

### 文献与撞题结论

- 第一轮未发现同时满足 failed candidate 作为输入, explicit failure feedback, pocket-aware 3D local repair, same-budget repair vs Best-of-N/rerank-only 的直接撞题工作。
- DiffDec, DiffLEOP, DecompDPO, DecompDiff, DecompOpt 是中等风险相邻工作, 需要二轮读原文确认输入条件、指标、代码和 baseline。
- PoseBusters, PLIP, AutoDock Vina 更适合作为 feedback / evaluation / scoring 组件, 不是本项目的直接竞争方法。
- AMG 与 MolJO 名称或方法归属仍有歧义, 已在 `docs/report/20260601-02-literature-matrix-report.md` 标注待验证。

### 失败 / 异常 / 负结果

- CCS WebSearch 对核心查询返回反爬/非结果 HTML, 未能直接使用。
- arXiv API 查询出现一次超时。
- Read 工具若误传空 `pages` 参数会失败；后续应避免给 Markdown 读取传空页码。
- 未找到 direct failed-candidate-conditioned molecular repair 或 same-budget repair vs Best-of-N/rerank-only 的直接结果。

### 下一步

- 补 `environment.yml` 和 `scripts/setup/check_environment.py`。
- 设计最小 smoke pipeline。
- 二轮核验 DiffDec, DiffLEOP, DecompDPO, DecompDiff, DecompOpt 原文和代码仓库。
- 继续核验 AMG / MolJO 的正式方法名与来源。

---

### 2026-05-31 / 环境初始化检查

- 日期：2026-05-31
- 阶段名称：环境初始化文件与依赖检查
- 负责人 / agent：Claude Code
- commit：511daa9 Initialize research project scaffold
- 环境：当前 shell 为 Python 3.12.11 / flash-vqg；目标环境 `pfr` 尚未创建
- GPU / CPU：检测到 NVIDIA GeForce RTX 3090, 23.6 GiB
- 数据版本：无
- 随机种子：无

### 阶段目标

- 创建 `environment.yml`, 固定后续项目环境的主要依赖。
- 创建 `scripts/setup/check_environment.py`, 用于区分必需依赖与可选科学工具。
- 在当前环境中运行检查, 记录缺失项。

### 背景与判断

- 为什么做这个实验：在设计 smoke pipeline 前, 需要明确 RDKit, PyTorch, PLIP, PoseBusters, Vina 等依赖是否可用。
- 需要验证的假设：当前机器可运行基础 Python 检查, 但项目专用环境可能尚未创建。
- 与上一阶段的关系：第一轮文献确认后, 工程上进入环境和最小 pipeline 准备。

### 插件 / Skill / Workflow 使用记录

- 使用的 plugin / skill / agent / workflow：未使用外部插件；使用本地 Python 脚本。
- 使用目的：检查项目依赖和 GPU 可见性。
- 输入：`environment.yml`, `scripts/setup/check_environment.py`。
- 输出路径：终端输出, `docs/STATUS.md`, `docs/EXPERIMENT_LOG.md`。
- 是否成功：部分成功。
- 失败原因或降级方案：当前激活环境缺少必需依赖 RDKit；目标 `pfr` conda 环境尚未创建。
- 对本阶段结论的影响：后续需先用 `conda env create -f environment.yml` 或等价方式创建环境, 再运行 smoke pipeline。

### 命令与配置

```bash
python scripts/setup/check_environment.py
```

配置文件：

- `environment.yml`
- `scripts/setup/check_environment.py`

### 输出文件

- metrics：无。
- tables：无。
- figures：无。
- molecules：无。
- logs：`docs/EXPERIMENT_LOG.md`。
- checkpoints：无。

### 主要结果

| 指标 | 结果 | 备注 |
|---|---:|---|
| Python version | 3.12.11 | 当前 shell 环境, 非目标 `pfr` 环境 |
| required dependency check | FAIL | 缺少 RDKit |
| CUDA visible | Yes | RTX 3090, 23.6 GiB |
| optional tools | partial / missing | torch 可用；torch_geometric, vina, posebusters, plip, meeko 缺失 |

### 结论

- `environment.yml` 已创建, 目标 Python 版本为 3.11。
- `scripts/setup/check_environment.py` 可运行并能报告必需/可选依赖状态。
- 当前环境不是项目目标环境, 缺少 RDKit, 暂不适合运行化学 smoke pipeline。

### 失败 / 异常 / 负结果

- 当前环境缺少 RDKit。
- `vina`, `obabel`, `posebusters`, `plip`, `meeko`, `torch_geometric` 在当前环境中不可用或未安装。
- Torch 可用且能看到 GPU, 但后续仍需在 `pfr` 环境中重新确认。

### 下一步

- 创建并激活 `pfr` conda 环境。
- 重新运行 `python scripts/setup/check_environment.py`。
- 在 RDKit 可用后实现最小 R-group / failed-candidate / feedback smoke pipeline。

---

### 2026-05-31 / smoke pipeline dry-run 设计

- 日期：2026-05-31
- 阶段名称：最小 smoke pipeline 配置与 dry-run
- 负责人 / agent：Claude Code
- commit：511daa9 Initialize research project scaffold
- 环境：当前 shell 为 Python 3.12.11 / flash-vqg；未依赖 RDKit
- GPU / CPU：未使用 GPU
- 数据版本：无真实数据；只生成 pipeline plan
- 随机种子：0

### 阶段目标

- 明确最小 smoke pipeline 的四个阶段: R-group 数据构造, failed candidate 构造, feedback 提取, baseline 评估。
- 创建对应 YAML 配置文件。
- 创建 dry-run 脚本, 在无真实数据和无 RDKit 的情况下验证配置可读、流水线顺序和输出路径。

### 背景与判断

- 为什么做这个实验：当前项目环境尚未创建, 不能运行化学处理; 但可以先固定端到端接口和配置, 降低后续实现歧义。
- 需要验证的假设：流水线可以拆成四个可独立实现的脚本, 并通过配置连接输入输出。
- 与上一阶段的关系：承接环境检查结果, 在不安装依赖的前提下推进低风险本地工作。

### 插件 / Skill / Workflow 使用记录

- 使用的 plugin / skill / agent / workflow：未使用外部插件；使用本地 Python dry-run。
- 使用目的：验证 smoke pipeline 配置和阶段顺序。
- 输入：`configs/data/rgroup_smoke.yaml`, `configs/data/failed_candidate_smoke.yaml`, `configs/feedback/smoke.yaml`, `configs/baselines/smoke.yaml`。
- 输出路径：`experiments/20260531-01-smoke-file-pipeline/metadata/pipeline_plan.json`。
- 是否成功：成功。
- 失败原因或降级方案：实际处理脚本尚未实现, dry-run 将其标为 `script pending`。
- 对本阶段结论的影响：后续应优先实现四个脚本入口。

### 命令与配置

```bash
python scripts/setup/smoke_pipeline_dry_run.py
```

配置文件：

- `configs/data/rgroup_smoke.yaml`
- `configs/data/failed_candidate_smoke.yaml`
- `configs/feedback/smoke.yaml`
- `configs/baselines/smoke.yaml`

### 输出文件

- metrics：无。
- tables：无。
- figures：无。
- molecules：无。
- logs：`experiments/20260531-01-smoke-file-pipeline/metadata/pipeline_plan.json`, `docs/EXPERIMENT_LOG.md`。
- checkpoints：无。

### 主要结果

| 指标 | 结果 | 备注 |
|---|---:|---|
| YAML config load | PASS | 四个配置均可读取 |
| pipeline steps | 4 | build_rgroup_dataset, generate_failed_candidates, extract_feedback, eval_baselines |
| dry-run output | PASS | 写入 `experiments/20260531-01-smoke-file-pipeline/metadata/pipeline_plan.json` |
| actual processing scripts | 4/4 | 均已实现最小可运行入口 |
| empty-input end-to-end run | PASS | 生成空 JSONL, split, metrics JSON 和 CSV 后已清理产物 |
| toy-input pytest | PASS | `pytest -q`: 1 passed |
| metric module pytest | PASS | `pytest -q`: 4 passed |

### 结论

- 最小 smoke pipeline 的输入输出协议已固定到配置文件中。
- dry-run 已能生成命令计划和输出路径。
- 四个实际脚本入口已实现: `scripts/data/build_rgroup_dataset.py`, `scripts/data/generate_failed_candidates.py`, `scripts/data/extract_feedback.py`, `scripts/eval/eval_baselines.py`。
- 空数据端到端运行已通过, 后续需要真实小样本与 RDKit 环境。
- 已新增 `tests/test_smoke_pipeline.py`, 使用 toy complex fixture 验证非空输入下 dataset, failed candidates, feedback 和 baseline metrics 输出。
- 已将 success 判定和 baseline 汇总逻辑抽到 `src/pfr/evaluation/metrics.py` 和 `src/pfr/baselines/smoke.py`, 并新增 `tests/test_metrics.py`。

### 失败 / 异常 / 负结果

- 当前没有真实 protein-ligand complex 输入。
- 四个实际处理脚本仅为最小占位实现, 尚未包含 RDKit R-group 切分、真实构象扰动、PLIP/PoseBusters/Vina 调用或化学指标计算。
- 由于 RDKit 缺失, 暂未运行真实化学结构处理。

### 下一步

- 创建并激活 `pfr` conda 环境。
- 重新运行 `python scripts/setup/check_environment.py`。
- 准备 1-3 个公开 protein-ligand complex 小样本。
- 在 RDKit 可用后把占位脚本替换为真实 R-group / failed-candidate / feedback 逻辑。

---

### 2026-05-31 / 写作与数据接入准备

- 日期：2026-05-31
- 阶段名称：BIBM 论文初稿骨架与 smoke 数据 manifest
- 负责人 / agent：Claude Code
- commit：56b0842 Draft BIBM paper scaffold, 8caf76d Modularize smoke metrics
- 环境：未使用额外环境
- GPU / CPU：未使用
- 数据版本：尚无真实数据
- 随机种子：无

### 阶段目标

- 创建 BIBM-style working draft, 但不夸大当前工程 smoke 结果。
- 创建 smoke 数据 manifest 模板, 为后续公开小样本接入保留来源、许可、引用和校验信息。

### 命令与配置

```bash
pytest -q
```

配置文件：

- `docs/report/20260602-02-paper-draft-report.md`
- `docs/report/20260601-01-smoke-data-manifest-report.md`

### 输出文件

- metrics：无真实分子指标。
- tables：无真实实验表格。
- figures：无。
- molecules：无。
- logs：`docs/EXPERIMENT_LOG.md`。
- checkpoints：无。

### 主要结果

| 指标 | 结果 | 备注 |
|---|---:|---|
| BIBM draft scaffold | PASS | 已创建 `docs/report/20260602-02-paper-draft-report.md` |
| smoke data manifest | PASS | 已创建 `docs/report/20260601-01-smoke-data-manifest-report.md` |
| tests | PASS | `pytest -q`: 4 passed |

### 结论

- 论文初稿已包含摘要、引言、相关工作、任务定义、方法概览、实验设计、当前实现状态、初步结果、讨论、局限、可复现与伦理、下一步。
- 初稿明确当前没有真实分子实验或模型性能结论。
- 数据 manifest 明确不提交原始结构文件到 git, 只记录来源和校验信息。

### 失败 / 异常 / 负结果

- 尚未下载真实 protein-ligand complex。
- 尚未生成真实 metrics、figures、molecules 或 BIBM 可投稿结果。
- 完整研究闭环仍未完成。

### 下一步

- 创建并激活 `pfr` conda 环境。
- 下载或准备 1-3 个公开可引用 protein-ligand complex 小样本。
- 实现真实 RDKit R-group 切分和反馈提取。

---

### 2026-05-31 / 公开 RCSB smoke 数据与文件级 pipeline

- 日期：2026-05-31
- 阶段名称：公开 RCSB smoke 数据下载与文件级 pipeline
- 负责人 / agent：Claude Code
- commit：c5b8b03 Document smoke data intake
- 环境：当前 shell Python 3.12.11 / flash-vqg；`pfr` 环境创建仍在后台完成中
- GPU / CPU：未使用 GPU
- 数据版本：RCSB PDB entries 1A4W, 1HVR, 3PTB；SHA256 记录在 `docs/report/20260601-01-smoke-data-manifest-report.md`
- 随机种子：0

### 阶段目标

- 从公开 RCSB PDB endpoints 下载 1-3 个可审计 smoke complex。
- 记录来源 URL, 路径和 SHA256, raw 数据不提交 git。
- 使用真实文件路径运行当前文件级 smoke pipeline, 生成 metrics 和 table 输出。

### 插件 / Skill / Workflow 使用记录

- 使用的 plugin / skill / agent / workflow：未使用外部插件；使用本地 Python 和 RCSB 公开 endpoints。
- 使用目的：下载公开 smoke 数据并验证 pipeline 输入输出。
- 输入：`configs/data/smoke_download.yaml`, RCSB PDB IDs 1A4W, 1HVR, 3PTB。
- 输出路径：`data/datasets/rgroup_smoke/raw/`, `docs/report/20260601-01-smoke-data-manifest-report.md`, `outputs/20260531-01-smoke-file-pipeline/metrics/baselines_smoke.json`, `outputs/20260531-01-smoke-file-pipeline/tables/baselines_smoke.csv`。
- 是否成功：成功。
- 失败原因或降级方案：无。
- 对本阶段结论的影响：证明 pipeline 可处理真实公开文件路径, 但化学逻辑仍是 placeholder, 不能作为模型性能结果。

### 命令与配置

```bash
PYTHONPATH=src python scripts/data/download_smoke_complexes.py --config configs/data/smoke_download.yaml
PYTHONPATH=src python scripts/data/build_rgroup_dataset.py --config configs/data/rgroup_smoke.yaml
PYTHONPATH=src python scripts/data/generate_failed_candidates.py --config configs/data/failed_candidate_smoke.yaml
PYTHONPATH=src python scripts/data/extract_feedback.py --config configs/feedback/smoke.yaml
PYTHONPATH=src python scripts/eval/eval_baselines.py --config configs/baselines/smoke.yaml
```

配置文件：

- `configs/data/smoke_download.yaml`
- `configs/data/rgroup_smoke.yaml`
- `configs/data/failed_candidate_smoke.yaml`
- `configs/feedback/smoke.yaml`
- `configs/baselines/smoke.yaml`

### 输出文件

- metrics：`outputs/20260531-01-smoke-file-pipeline/metrics/baselines_smoke.json`
- tables：`outputs/20260531-01-smoke-file-pipeline/tables/baselines_smoke.csv`
- figures：无。
- molecules：无。
- logs：`docs/EXPERIMENT_LOG.md`, `docs/report/20260601-01-smoke-data-manifest-report.md`
- checkpoints：无。

### 主要结果

| 指标 | 结果 | 备注 |
|---|---:|---|
| public complexes | 3 | 1A4W, 1HVR, 3PTB |
| dataset examples | 3 | 文件级 metadata |
| failed candidates | 12 | 4 placeholder failure types per example |
| feedback records | 12 | placeholder geometry feedback |
| baseline rows | 4 | direct_regeneration, best_of_n, rerank_only, no_feedback_repair |
| same-budget success rate | 0.0 | structure-derived clash makes all current failed candidates unsuccessful |
| editable validity | 0.5 | template failure label metric |
| anchor validity | 0.1667 | only a subset of 1HSG candidates remains anchor-valid after structural anchor error |
| clash-free rate | 0.0 | coordinate-derived protein-ligand clash count is nonzero for all candidates |
| summary output | PASS | `outputs/20260531-01-smoke-file-pipeline/metrics/smoke_summary.json` |
| figure output | PASS | `outputs/20260531-01-smoke-file-pipeline/figures/smoke_success_rates.svg` |
| cases output | PASS | `outputs/20260531-01-smoke-file-pipeline/processed/cases/smoke_cases.json`, empty until molecule-level repair exists |

### 结论

- 公开 smoke 数据下载和来源记录已跑通。
- 下载脚本已生成 receptor-only `_protein_clean.pdb`, 只保留 ATOM/TER/END 记录。
- `docs/report/20260601-01-smoke-data-manifest-report.md` 已更新为 clean receptor 路径和 SHA256。
- 清理后 coordinate-derived clash 仍未改善到可用水平, 说明当前 smoke ligand/pocket 样本选择或 RCSB ligand endpoint 仍不适合最终评估。
- 这是重要负结果: 单纯去除 HETATM 不足以得到可用于评价的无重叠 receptor-ligand complex。
- 已生成 smoke summary JSON, SVG figure 和 cases JSON, 且全部标注为 placeholder/file-level 结果。
- 当前结果只是占位逻辑验证, 不能作为真实分子修复有效性证据。

### 失败 / 异常 / 负结果

- raw 数据位于 `data/raw/`, 按 `.gitignore` 不提交。
- `data/processed/` 和 `data/splits/` 也不提交, 可由脚本重建。
- RDKit R-group 切分、PLIP/PoseBusters/Vina 仍未接入。

### 下一步

- `repair_baselines.py` 已新增 `feedback_rule_repair`, 根据 feedback geometry 和 failure_type 在 coordinate rollback 与 identity failed candidate 之间选择。
- 当前 repaired candidate records 为 36 条: coordinate_rollback 12, identity_failed_candidate 12, feedback_rule_repair 12。
- `outputs/20260531-01-smoke-file-pipeline/processed/cases/smoke_cases.json` 已包含每个 failed candidate 对应的 repair outputs。
- 该 feedback repair 是规则型最小 baseline, 不是学习模型。





---

### 2026-06-01 / 实验日志恢复说明

- 日期：2026-06-01
- 阶段名称：覆盖事故后的实验日志恢复
- 负责人 / agent：Claude Code
- commit：65e95ee Clean receptor files for smoke data
- 环境：本地 git + 当前会话 transcript / 已落盘 metrics
- GPU / CPU：未使用 GPU
- 数据版本：不适用
- 随机种子：不适用

### 背景与判断

- 本会话中误用 `Write` 将 `docs/EXPERIMENT_LOG.md` 临时覆盖为占位文本。
- 已立即从 `git show HEAD:docs/EXPERIMENT_LOG.md` 恢复最后提交版本, 并根据当前会话已读 transcript、已落盘 metrics、configs 和输出路径追加恢复性日志。
- 以下恢复条目用于保留后续阶段的可审计脉络；若需逐命令精确复核, 以对应 metrics/jsonl/csv/log 文件和 git diff 为准。

### 失败 / 异常 / 负结果

- 覆盖事故本身是一次文档操作错误, 已记录。
- 恢复条目不会伪造不存在的结果；只记录本会话已验证或已落盘的输出路径和指标。

---

### 2026-06-01 / smoke sample quality 标记与 PDB pose ligand

- 日期：2026-06-01
- 阶段名称：smoke pipeline 样本质量标记与不可评价负结果显式化
- 负责人 / agent：Claude Code + RDKit skill
- commit：65e95ee Clean receptor files for smoke data
- 环境：`pfr` conda 环境, Python 3.11.15, RDKit 2026.03.2
- GPU / CPU：未使用 GPU
- 数据版本：RCSB smoke entries 1A4W, 1HVR, 3PTB
- 随机种子：0

### 阶段目标

- 给 smoke examples, failed candidates, feedback records, baseline metrics 和 summary 加入 `sample_quality` / repair evaluability 标记。
- 将 protein-ligand overlap, missing scaffold, missing anchor 等样本级问题从方法失败中区分出来。
- 优先从 PDB HETATM 提取同坐标系 ligand pose, 避免 RCSB ligand SDF endpoint 与 receptor 坐标不一致。

### 命令与配置

```bash
PYTHONPATH=src conda run -n pfr python scripts/data/download_smoke_complexes.py --config configs/data/smoke_download.yaml
PYTHONPATH=src conda run -n pfr pytest -q tests
PYTHONPATH=src conda run -n pfr python scripts/data/build_rgroup_dataset.py --config configs/data/rgroup_smoke.yaml
PYTHONPATH=src conda run -n pfr python scripts/data/generate_failed_candidates.py --config configs/data/failed_candidate_smoke.yaml
PYTHONPATH=src conda run -n pfr python scripts/data/extract_feedback.py --config configs/feedback/smoke.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/eval_baselines.py --config configs/baselines/smoke.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/repair_baselines.py --config configs/baselines/repair_smoke.yaml
PYTHONPATH=src conda run -n pfr python scripts/analysis/summarize_smoke_results.py --config configs/eval_smoke_summary.yaml
```

### 输出文件

- metrics：`outputs/20260531-01-smoke-file-pipeline/metrics/baselines_smoke.json`, `outputs/20260531-01-smoke-file-pipeline/metrics/smoke_summary.json`
- tables：`outputs/20260531-01-smoke-file-pipeline/tables/baselines_smoke.csv`
- figures：`outputs/20260531-01-smoke-file-pipeline/figures/smoke_success_rates.svg`
- molecules：`outputs/20260531-01-smoke-file-pipeline/processed/cases/smoke_cases.json`, `outputs/20260531-01-smoke-file-pipeline/processed/failed_molecules/smoke_failed/`, `outputs/20260601-01-smoke-repair-baselines/processed/repaired_molecules/smoke_repaired/`

### 主要结果

| 指标 | 结果 | 备注 |
|---|---:|---|
| dataset examples | 3 | 1A4W, 1HVR, 3PTB |
| evaluable dataset examples | 3 | PDB HETATM ligand pose 优先 |
| feedback records | 12 | 4 failure types x 3 examples |
| evaluable feedback records | 7 | `num_evaluable_for_repair`: 7 |
| non-evaluable feedback records | 5 | `smoke_summary.json` 明确记录 |
| repair evaluable rate | 0.5833 | 7/12 |

### 结论

- `sample_quality` 已贯穿 dataset, failed candidates, feedback records, baseline metrics 和 case summary。
- 当前 success metrics 仍是 smoke/file-level 结果, 不能作为真实模型性能证据。

### 失败 / 异常 / 负结果

- 当前 success metrics 仍来自 failed-candidate feedback records, 不是 repaired molecule 的真实性能。
- 本阶段没有引入 PLIP, PoseBusters 或 Vina。

---

### 2026-06-01 / repaired-molecule 级 smoke 评估与统一 baseline 输出

- 日期：2026-06-01
- 阶段名称：规则和非 oracle baselines 的 repaired-molecule 输出统一
- 负责人 / agent：Claude Code
- commit：65e95ee Clean receptor files for smoke data
- 环境：`pfr` conda 环境, Python 3.11.15, RDKit 2026.03.2
- GPU / CPU：未使用 GPU
- 数据版本：RCSB smoke entries 1A4W, 1HVR, 3PTB
- 随机种子：0, 1, 2

### 阶段目标

- 将 `direct_regeneration`, `best_of_n`, `rerank_only`, `no_feedback_repair`, `coordinate_rollback`, `identity_failed_candidate`, `feedback_rule_repair` 统一为 actual repaired molecule outputs。
- 使用 `scripts/eval/eval_repaired.py` 对实际输出 SDF 统一评估。
- 去除 direct / Best-of-N / rerank-only 对 reference-ligand oracle 的依赖, 仅保留 rollback / rule sanity check 的明确 oracle 标注。

### 命令与配置

```bash
PYTHONPATH=src conda run -n pfr python scripts/eval/repair_baselines.py --config configs/baselines/repair_smoke.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/eval_repaired.py --config configs/baselines/eval_repaired_smoke.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/run_repaired_multiseed.py
PYTHONPATH=src conda run -n pfr python scripts/analysis/summarize_smoke_results.py --config configs/eval_smoke_summary.yaml
PYTHONPATH=src conda run -n pfr pytest -q tests
```

### 输出文件

- metrics：`outputs/20260601-01-smoke-repair-baselines/metrics/repaired_smoke.json`, `outputs/20260601-01-smoke-repair-baselines/metrics/repaired_smoke_multiseed.json`, `outputs/20260531-01-smoke-file-pipeline/metrics/smoke_summary.json`
- tables：`outputs/20260601-01-smoke-repair-baselines/tables/repaired_smoke.csv`, `outputs/20260601-01-smoke-repair-baselines/processed/multiseed_repaired/repaired_metrics_seed_*.csv`
- molecules：`outputs/20260601-01-smoke-repair-baselines/processed/repaired_molecules/smoke_repaired/`, `outputs/20260601-01-smoke-repair-baselines/processed/multiseed_repaired/molecules_seed_*/`

### 主要结果

| baseline | mean repaired success | 备注 |
|---|---:|---|
| feedback_geometry_refinement | 0.6389 | 非回滚 feedback geometry 平移/局部候选搜索 smoke 结果 |
| best_of_n | 0.5 | global-score-only candidate selection |
| direct_regeneration | 0.4444 | local candidate pool selection |
| no_feedback_repair | 0.5 | 当前等同 failed candidate |
| feedback_linear_refinement | 1.0 | reference-centroid supervised sanity check, 不作为真实模型结论 |

### 结论

- repaired-molecule 输出和评估口径已统一。
- `feedback_geometry_refinement` 在 smoke repaired-molecule fallback proxy 中超过 no-feedback / Best-of-N / direct regeneration。
- `feedback_linear_refinement` 使用 reference-derived centroid target, 只能作为 sanity check。

### 失败 / 异常 / 负结果

- smoke 数据只有 3 个 complexes, 不能支持泛化结论。
- fallback proxy 不是官方 PLIP/PoseBusters/Vina。

---

### 2026-06-01 / smoke-plus 数据, split 与 fallback proxy 汇总

- 日期：2026-06-01
- 阶段名称：12-complex smoke-plus repaired-molecule fallback proxy 评估
- 负责人 / agent：Claude Code
- commit：65e95ee Clean receptor files for smoke data
- 环境：`pfr` conda 环境, Python 3.11.15, RDKit 2026.03.2
- GPU / CPU：CPU；未使用 GPU
- 数据版本：12-complex smoke-plus set, manifest 见 `docs/report/20260602-01-smoke-plus-data-manifest-report.md`
- 随机种子：0, 1, 2

### 阶段目标

- 将 smoke 从 3 complexes 扩展到 12 complexes。
- 使用 deterministic complex split train 6 / validation 3 / test 3。
- 在 repaired-molecule 级别汇总 fallback proxy 指标。

### 命令与配置

```bash
PYTHONPATH=src conda run -n pfr python scripts/eval/run_repaired_multiseed.py --repair-config configs/baselines/repair_smoke_plus.yaml --seeds 0 1 2 --output-dir outputs/20260601-02-smoke-plus-expansion-and-variants/processed/multiseed_repaired --summary-path outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus_multiseed.json
PYTHONPATH=src conda run -n pfr python scripts/eval/summarize_repaired_split.py
PYTHONPATH=src conda run -n pfr python scripts/analysis/summarize_smoke_results.py --config configs/eval_smoke_plus_summary.yaml
```

### 输出文件

- metrics：`outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus.json`, `outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus_multiseed.json`, `outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus_split.json`, `outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/smoke_plus_summary.json`
- tables：`outputs/20260601-02-smoke-plus-expansion-and-variants/tables/repaired_smoke_plus.csv`, `outputs/20260601-02-smoke-plus-expansion-and-variants/tables/repaired_smoke_plus_split.csv`
- figures：`outputs/20260601-02-smoke-plus-expansion-and-variants/figures/smoke_plus_success_rates.svg`
- molecules：`outputs/20260601-02-smoke-plus-expansion-and-variants/processed/repaired_molecules/smoke_plus_repaired/`, `outputs/20260601-02-smoke-plus-expansion-and-variants/processed/cases/smoke_plus_cases.json`

### 主要结果

| baseline | mean success | pose-like | contact similarity | vina-like proxy |
|---|---:|---:|---:|---:|
| feedback_geometry_refinement | 0.6181 | 0.8819 | 0.8397 | 1.0705 |
| feedback_learned_geometry_policy | 0.5069 | 0.7917 | 0.8430 | 1.2527 |
| best_of_n | 0.4792 | 0.6042 | 0.7819 | 4.6569 |
| direct_regeneration | 0.4444 | 0.6389 | 0.7558 | 4.8356 |

### 结论

- smoke-plus fallback proxy 支持 “geometry feedback repair 优于重新生成/Best-of-N/no-feedback” 的初步信号。
- `feedback_learned_geometry_policy` 是 oracle-free ridge pseudo-label translation policy, 有正信号但弱于 hand-crafted geometry-search baseline。

### 失败 / 异常 / 负结果

- 当前 failed candidates 仍主要是可控扰动。
- fallback proxy 不能替代官方 PoseBusters/PLIP/Vina 或 redocking success。

---

### 2026-06-01 / 官方 PLIP+Vina smoke-plus retry coverage

- 日期：2026-06-01
- 阶段名称：官方 PLIP 与 Vina score-only smoke-plus 评估及 retry 修复
- 负责人 / agent：Claude Code
- commit：65e95ee Clean receptor files for smoke data
- 环境：`pfr-eval-tools` conda 环境, PoseBusters, PLIP, Vina, Meeko, OpenBabel 可用
- GPU / CPU：CPU；未使用 GPU
- 数据版本：`outputs/20260601-02-smoke-plus-expansion-and-variants/processed/repaired_candidates_smoke_plus.jsonl`
- 随机种子：0

### 阶段目标

- 用官方 PLIP 和 AutoDock Vina score-only 评估 smoke-plus repaired candidates。
- 诊断并修复 Vina preparation failures。
- 保留 command metadata 和 retry 路径。

### 输出文件

- metrics：`outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_plip_vina.jsonl`, `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_plip_vina_retry.jsonl`
- summaries：`outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_plip_vina_retry_summary.json`
- logs：`outputs/20260601-04-vina-pose-and-local-edit-diagnostics/logs/official_eval_smoke_plus_plip_vina_retry.log`

### 主要结果

| 指标 | 结果 | 备注 |
|---|---:|---|
| PLIP records | 480/480 | 0 PLIP errors |
| initial Vina score-only | 280/480 | 200 preparation failures |
| retry Vina score-only | 480/480 | 0 Vina errors |
| failing complexes before retry | 5 | 1M17, 2BR1, 3ERT, 3G0E, 5P21 |
| receptor retry | success | `--default_altloc A` |
| ligand retry | success | `--charge_model zero` |

### 结论

- 官方 PLIP/Vina score-only 链条已在 smoke-plus 上达到完整写出覆盖。
- retry 解决了 receptor alternate-location 和 ligand Gasteiger charge NaN 相关 preparation failures。
- 官方结果仍是 score-only/interaction-count, 不能等同 redocking success。

### 失败 / 异常 / 负结果

- 不允许只用 Vina score-only 证明方法有效。
- PLIP mean interaction count 不能替代 interaction recovery/similarity。

---

### 2026-06-01 / official PoseBusters bounded subset20

- 日期：2026-06-01
- 阶段名称：官方 PoseBusters 子进程隔离与 bounded subset20 诊断
- 负责人 / agent：Claude Code
- commit：65e95ee Clean receptor files for smoke data
- 环境：`pfr-eval-tools` conda 环境
- GPU / CPU：CPU；未使用 GPU
- 数据版本：`outputs/20260601-03-smoke-plus-official-tool-evaluation/processed/repaired_candidates_smoke_plus_posebusters_subset20.jsonl`
- 随机种子：0

### 阶段目标

- 避免 PoseBusters 单条记录 hang 阻塞整批评估。
- 使用子进程隔离和 timeout 写出 structured JSON failure。
- 在 bounded subset20 上检查官方 plausibility checks。

### 命令与配置

```bash
conda run -n pfr-eval-tools python scripts/eval/eval_official_tools.py --repaired-candidates outputs/20260601-03-smoke-plus-official-tool-evaluation/processed/repaired_candidates_smoke_plus_posebusters_subset20.jsonl --output outputs/20260601-03-smoke-plus-official-tool-evaluation/metrics/official_eval_smoke_plus_posebusters_subset20.jsonl --tools posebusters --posebusters-timeout 20 --keep-work-dir outputs/20260601-03-smoke-plus-official-tool-evaluation/logs/official_eval_smoke_plus_posebusters_subset20
python scripts/eval/summarize_official_eval.py --input outputs/20260601-03-smoke-plus-official-tool-evaluation/metrics/official_eval_smoke_plus_posebusters_subset20.jsonl --output-json outputs/20260601-03-smoke-plus-official-tool-evaluation/metrics/official_eval_smoke_plus_posebusters_subset20_summary.json --output-csv outputs/20260601-03-smoke-plus-official-tool-evaluation/tables/official_eval_smoke_plus_posebusters_subset20_summary.csv --name official_eval_smoke_plus_posebusters_subset20
```

### 输出文件

- metrics：`outputs/20260601-03-smoke-plus-official-tool-evaluation/metrics/official_eval_smoke_plus_posebusters_subset20.jsonl`, `outputs/20260601-03-smoke-plus-official-tool-evaluation/metrics/official_eval_smoke_plus_posebusters_subset20_summary.json`
- tables：`outputs/20260601-03-smoke-plus-official-tool-evaluation/tables/official_eval_smoke_plus_posebusters_subset20_summary.csv`
- logs：`outputs/20260601-03-smoke-plus-official-tool-evaluation/logs/official_eval_smoke_plus_posebusters_subset20/`

### 主要结果

| 指标 | 结果 | 备注 |
|---|---:|---|
| subset records | 20 | first 20 smoke-plus repaired candidates |
| completed check records | 18/20 | 46 boolean checks each |
| timeout records | 2/20 | both `best_of_n` |
| completed full pass | 0/18 | all completed records failed at least one check |
| mean passed checks | 33 | completed records |

### 结论

- 子进程隔离和 timeout JSON 记录可用。
- subset20 的 PoseBusters full pass 为 0/18 completed records, 是重要负结果。
- PoseBusters 仍应作为诊断指标, 不是当前稳定主指标。

### 失败 / 异常 / 负结果

- 2/20 timeout。
- 18 条 completed records 均未 full pass。
- subset 仅覆盖部分 failed candidates, 不是全 smoke-plus 统计。

---

### 2026-06-01 / oracle-free kernel geometry policy smoke-plus negative result

- 日期：2026-06-01
- 阶段名称：oracle-free kernel geometry policy smoke-plus 评估
- 负责人 / agent：Claude Code
- commit：65e95ee Clean receptor files for smoke data
- 环境：`pfr` conda 环境, Python 3.11.15, RDKit 2026.03.2
- GPU / CPU：CPU；未使用 GPU
- 数据版本：`outputs/20260601-02-smoke-plus-expansion-and-variants/processed/failed_candidates_smoke_plus.jsonl`, `outputs/20260601-02-smoke-plus-expansion-and-variants/processed/feedback_smoke_plus.jsonl`, 12-complex smoke-plus set
- 随机种子：0, 1, 2

### 阶段目标

- 在 ridge translation policy 之外增加更非线性的 oracle-free feedback policy。
- 使用 failed-candidate geometry proxy pseudo-label, 不使用 reference-pose centroid rollback target。
- 检查 RBF kernel feedback policy 是否能稳定超过 Best-of-N, no-feedback 和现有 learned baseline。

### 输出文件

- metrics：`outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus.json`, `outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus_multiseed.json`
- tables：`outputs/20260601-02-smoke-plus-expansion-and-variants/tables/repaired_smoke_plus.csv`, `outputs/20260601-02-smoke-plus-expansion-and-variants/processed/multiseed_repaired/repaired_metrics_seed_*.csv`
- molecules：`outputs/20260601-02-smoke-plus-expansion-and-variants/processed/repaired_molecules/smoke_plus_repaired/`, `outputs/20260601-02-smoke-plus-expansion-and-variants/processed/multiseed_repaired/molecules_seed_*/`

### 主要结果

| 指标 | 结果 | 备注 |
|---|---:|---|
| tests | 14 passed | after implementation |
| feedback_kernel_geometry_policy mean success | 0.4861 | seeds 0/1/2 |
| feedback_kernel_geometry_policy pose-like pass | 0.6736 | fallback proxy |
| feedback_kernel_geometry_policy contact similarity | 0.8000 | contact fingerprint proxy |
| feedback_kernel_geometry_policy vina-like proxy | 2.8033 | fallback proxy, lower is better |
| feedback_learned_geometry_policy mean success | 0.5069 | existing ridge learned policy |
| feedback_geometry_refinement mean success | 0.6181 | non-learned geometry-search baseline |
| best_of_n mean success | 0.4792 | global-score-only baseline |
| no_feedback_repair mean success | 0.4792 | no-feedback baseline |

### 结论

- `feedback_kernel_geometry_policy` 工程上可运行, 但效果弱。
- kernel policy 弱于现有 ridge learned policy 和 geometry-search baseline。
- 这是负结果/弱改进, 不能包装成方法成功。

### 失败 / 异常 / 负结果

- RBF kernel averaging 对离散 repair offset pseudo-label 不够有效。
- 当前 pseudo-label 仍来自 geometry proxy, 不含真实 generator/docking failure 反馈。

---

### 2026-06-01 / oracle-free kNN geometry policy smoke-plus multiseed signal

- 日期：2026-06-01
- 阶段名称：oracle-free kNN geometry policy smoke-plus 多 seed 评估
- 负责人 / agent：Claude Code
- commit：65e95ee Clean receptor files for smoke data
- 环境：`pfr` conda 环境, Python 3.11.15, RDKit 2026.03.2
- GPU / CPU：CPU；未使用 GPU
- 数据版本：`outputs/20260601-02-smoke-plus-expansion-and-variants/processed/failed_candidates_smoke_plus.jsonl`, `outputs/20260601-02-smoke-plus-expansion-and-variants/processed/feedback_smoke_plus.jsonl`, 12-complex smoke-plus set
- 随机种子：0, 1, 2

### 阶段目标

- 在 kernel averaging 负结果后, 使用 nearest-neighbor discrete pseudo-label action selection。
- 复用 oracle-free geometry pseudo-label, 不使用 reference-pose centroid rollback target。
- 用 smoke-plus seeds 0/1/2 验证 kNN policy 是否稳定优于 ridge/kernel/no-feedback。

### 命令与配置

```bash
PYTHONPATH=src conda run -n pfr python scripts/eval/repair_baselines.py --config configs/baselines/repair_smoke_plus.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/eval_repaired.py --config configs/baselines/eval_repaired_smoke_plus.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/run_repaired_multiseed.py --repair-config configs/baselines/repair_smoke_plus.yaml --seeds 0 1 2 --output-dir outputs/20260601-02-smoke-plus-expansion-and-variants/processed/multiseed_repaired --summary-path outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus_multiseed.json
PYTHONPATH=src conda run -n pfr pytest -q
PYTHONPATH=src conda run -n pfr python scripts/eval/summarize_repaired_split.py
PYTHONPATH=src conda run -n pfr python scripts/analysis/summarize_smoke_results.py --config configs/eval_smoke_plus_summary.yaml
```

### 输出文件

- metrics：`outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus.json`, `outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus_multiseed.json`, `outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus_split.json`, `outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/smoke_plus_summary.json`
- tables：`outputs/20260601-02-smoke-plus-expansion-and-variants/tables/repaired_smoke_plus.csv`, `outputs/20260601-02-smoke-plus-expansion-and-variants/tables/repaired_smoke_plus_split.csv`, `outputs/20260601-02-smoke-plus-expansion-and-variants/processed/multiseed_repaired/repaired_metrics_seed_*.csv`
- figures：`outputs/20260601-02-smoke-plus-expansion-and-variants/figures/smoke_plus_success_rates.svg`
- molecules：`outputs/20260601-02-smoke-plus-expansion-and-variants/processed/repaired_molecules/smoke_plus_repaired/`, `outputs/20260601-02-smoke-plus-expansion-and-variants/processed/multiseed_repaired/molecules_seed_*/`, `outputs/20260601-02-smoke-plus-expansion-and-variants/processed/cases/smoke_plus_cases.json`

### 主要结果

| baseline | mean success | pose-like | contact similarity | vina-like proxy | seed success values |
|---|---:|---:|---:|---:|---|
| feedback_geometry_refinement | 0.6181 | 0.8819 | 0.8397 | 1.0705 | 0.6250 / 0.6250 / 0.6042 |
| feedback_knn_geometry_policy | 0.5833 | 0.8264 | 0.8229 | 1.3079 | 0.5625 / 0.5625 / 0.6250 |
| feedback_learned_geometry_policy | 0.5069 | 0.7917 | 0.8430 | 1.2527 | 0.5208 / 0.4792 / 0.5208 |
| feedback_kernel_geometry_policy | 0.4861 | 0.6736 | 0.8000 | 2.8033 | 0.4583 / 0.5000 / 0.5000 |
| best_of_n | 0.4792 | 0.6042 | 0.7819 | 4.6569 | 0.4792 / 0.4792 / 0.4792 |
| no_feedback_repair | 0.4792 | 0.6042 | 0.7901 | 4.6812 | 0.4792 / 0.4792 / 0.4792 |
| direct_regeneration | 0.4444 | 0.6389 | 0.7558 | 4.8356 | 0.4375 / 0.4375 / 0.4583 |

### 结论

- `feedback_knn_geometry_policy` 是当前最好的 oracle-free learned signal: mean success 0.5833, 稳定高于 ridge learned policy、kernel policy、Best-of-N/no-feedback 和 direct regeneration。
- kNN 仍低于非学习 `feedback_geometry_refinement` 0.6181, 且 contact similarity / vina-like proxy 没有全面超过 ridge policy。
- 这支持 smoke-level 正信号, 但仍不是 publication-level feedback-conditioned repair model。

### 失败 / 异常 / 负结果

- 指标仍是 RDKit/geometry fallback proxy, 不是 PoseBusters full pass 或 official redocking success。
- failed candidates 仍是可控扰动, 不是真实生成/对接失败。
- kNN 的提高可能来自离散 pseudo-label 与当前扰动模板匹配, 需要更真实失败样本验证。

### 下一步

- 继续 task #49, 构造更真实 failed candidates。
- 引入 geometry-only / interaction-only / full-feedback 消融字段。
- 将 kNN policy 作为 smoke-level oracle-free baseline, 而不是最终主方法。


---

### 2026-06-01 / controlled semi-realistic failed candidates smoke-plus expansion

- 日期：2026-06-01
- 阶段名称：扩展 controlled/semi-realistic failed candidates 与 failure-type split 诊断
- 负责人 / agent：Claude Code
- commit：65e95ee Clean receptor files for smoke data
- 环境：`pfr` conda 环境, Python 3.11.15, RDKit 2026.03.2
- GPU / CPU：CPU；未使用 GPU
- 数据版本：12-complex smoke-plus set, `data/datasets/rgroup_smoke_plus/entries/index.jsonl`
- 随机种子：0, 1, 2

### 阶段目标

- 将 failed candidates 从 4 个纯可控扰动类型扩展到 7 个 controlled/semi-realistic failure types。
- 新增 `linker_too_flexible`, `drug_likeness_drop`, `score_hacking`, 并让 `interaction_loss` / `geometry_invalid` 更多作用于 editable region。
- 生成 repaired-molecule failure-type split, 避免总体 success rate 掩盖哪些失败类型真正需要修复。

### 背景与判断

- 为什么做这个实验：此前 stop hook 和项目目标均指出 failed candidates 仍偏可控扰动, 不足以支撑 BIBM 级主张。
- 需要验证的假设：局部 editable-region 坐标扰动和原子类型替换可比全分子平移更接近局部生成失败, 并暴露 no-feedback 易过关的失败类型。
- 与上一阶段的关系：承接 oracle-free ridge/kernel/kNN policies, 将测试集从 48 failed candidates / seed 扩展到 84 failed candidates / seed。

### 命令与配置

```bash
PYTHONPATH=src conda run -n pfr python scripts/data/generate_failed_candidates.py --config configs/data/failed_candidate_smoke_plus.yaml
PYTHONPATH=src conda run -n pfr python scripts/data/extract_feedback.py --config configs/feedback/smoke_plus.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/repair_baselines.py --config configs/baselines/repair_smoke_plus.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/eval_repaired.py --config configs/baselines/eval_repaired_smoke_plus.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/run_repaired_multiseed.py --repair-config configs/baselines/repair_smoke_plus.yaml --seeds 0 1 2 --output-dir outputs/20260601-02-smoke-plus-expansion-and-variants/processed/multiseed_repaired --summary-path outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus_multiseed.json
PYTHONPATH=src conda run -n pfr python scripts/eval/summarize_repaired_by_failure_type.py
PYTHONPATH=src conda run -n pfr python scripts/eval/summarize_repaired_split.py
PYTHONPATH=src conda run -n pfr python scripts/eval/eval_baselines.py --config configs/baselines/smoke_plus.yaml
PYTHONPATH=src conda run -n pfr python scripts/analysis/summarize_smoke_results.py --config configs/eval_smoke_plus_summary.yaml
PYTHONPATH=src conda run -n pfr pytest -q
```

### 输出文件

- metrics：`outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus.json`, `outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus_multiseed.json`, `outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus_by_failure_type.json`, `outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus_split.json`, `outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/smoke_plus_summary.json`
- tables：`outputs/20260601-02-smoke-plus-expansion-and-variants/tables/repaired_smoke_plus.csv`, `outputs/20260601-02-smoke-plus-expansion-and-variants/tables/repaired_smoke_plus_by_failure_type.csv`, `outputs/20260601-02-smoke-plus-expansion-and-variants/tables/repaired_smoke_plus_split.csv`
- figures：`outputs/20260601-02-smoke-plus-expansion-and-variants/figures/smoke_plus_success_rates.svg`
- molecules：`outputs/20260601-02-smoke-plus-expansion-and-variants/processed/failed_molecules/smoke_plus_failed/`, `outputs/20260601-02-smoke-plus-expansion-and-variants/processed/repaired_molecules/smoke_plus_repaired/`, `outputs/20260601-02-smoke-plus-expansion-and-variants/processed/cases/smoke_plus_cases.json`
- logs：background multiseed output `b3qtadd45.output`
- checkpoints：无

### 主要结果

| 指标 | 结果 | 备注 |
|---|---:|---|
| failed candidates per seed | 84 | 12 complexes x 7 failure types |
| repaired records per seed | 1008 | 84 failed candidates x 12 baselines |
| tests | 15 passed | `PYTHONPATH=src conda run -n pfr pytest -q` |
| feedback_geometry_refinement mean success | 0.7897 | seeds 0/1/2 fallback proxy |
| feedback_learned_geometry_policy mean success | 0.7421 | ridge oracle-free learned policy |
| feedback_knn_geometry_policy mean success | 0.6905 | lower than ridge after 7-type expansion |
| feedback_kernel_geometry_policy mean success | 0.6865 | similar to no-feedback, weaker proxy result |
| best_of_n mean success | 0.6746 | global-score-only baseline |
| no_feedback_repair mean success | 0.6905 | high because some added failure types pass geometry checks without repair |
| direct_regeneration mean success | 0.5714 | local candidate pool baseline |

### failure-type 诊断

- `anchor_invalid`: no-feedback success 0.0; ridge 0.0833; kNN 0.25; geometry refinement 0.4167。
- `interaction_loss`: no-feedback 0.5833; ridge 0.9167; kNN 0.8333; geometry refinement 1.0。
- `score_hacking`: no-feedback 0.6667; ridge 0.75; kNN 0.75; geometry refinement 0.9167。
- `drug_likeness_drop`, `geometry_invalid`, `clash` 中 no-feedback 也常过关, 说明总体 success rate 会高估这些失败类型的修复难度。

### 结论

- 已完成 task #49 的一个阶段性版本: failed candidates 从纯全分子平移扰动扩展到 editable-region 局部扰动和原子类型替换。
- 扩展集更能暴露 failure-type heterogeneity: anchor_invalid / interaction_loss / score_hacking 更适合作为当前 repair 能力诊断；drug_likeness_drop 等需要更合适的属性/interaction 指标, 不能只用几何 success 判断。
- 扩展后 ridge oracle-free policy 高于 Best-of-N/direct regeneration, 但 no-feedback 也很高, 所以必须分 failure type 和指标族报告。

### 失败 / 异常 / 负结果

- 新增失败类型仍是 controlled/semi-realistic, 不是 generator/docking/local proposal 真实失败。
- 扩展 1008-record 集合尚未重跑官方 PLIP/Vina 和 PoseBusters；旧 480-record 官方 PLIP/Vina 结果不能直接外推到新集合。
- `drug_likeness_drop` 在当前 fallback geometry success 定义下经常 no-op 过关, 需要 QED/SA/logP/interaction 或 learned scoring 维度补充。

### 下一步

- 接入真实 local proposal / docking loop / generator 失败候选, 或至少从多个 perturbation seeds 中筛出确实失败且多指标失败的候选。
- 对扩展 1008-record 集合重跑官方 PLIP/Vina retry, 并选择 bounded PoseBusters subset 做诊断。

## 2026-06-01 / 扩展集官方 PoseBusters subset35 与 local-proposal pool 诊断

### 环境与数据版本

- commit：65e95ee Clean receptor files for smoke data
- 环境：`pfr` conda 环境用于 RDKit pipeline；`pfr-eval-tools` conda 环境用于 PoseBusters。
- CPU/GPU：CPU；未使用 GPU。
- 数据版本：12-complex smoke-plus set；基础 controlled/semi-realistic failed candidates 为 84/seed, repaired records 为 1008/seed。

### 阶段目标

- 对扩展后的 7-type repaired set 运行 bounded PoseBusters subset 诊断, 不再沿用旧 subset20。
- 在 controlled/semi-realistic perturbations 之外, 增加一个独立 local-proposal pool 数据版本, 用多个 editable-region local proposals 生成失败候选。
- 该 local-proposal pool 只标记为 `smoke_local_proposal_pool_rdkit`, 不能表述为真实深度生成器或 docking loop 的失败输出。

### 命令与配置

```bash
# subset35: 7 failure types x 5 key baselines
PYTHONPATH=src conda run -n pfr-eval-tools python scripts/eval/eval_official_tools.py --repaired-candidates outputs/20260601-03-smoke-plus-official-tool-evaluation/processed/repaired_candidates_smoke_plus_posebusters_expanded_subset35.jsonl --output outputs/20260601-03-smoke-plus-official-tool-evaluation/metrics/official_eval_smoke_plus_expanded_posebusters_subset35.jsonl --tools posebusters --posebusters-timeout 20
PYTHONPATH=src conda run -n pfr-eval-tools python scripts/eval/summarize_official_eval.py --input outputs/20260601-03-smoke-plus-official-tool-evaluation/metrics/official_eval_smoke_plus_expanded_posebusters_subset35.jsonl --output-json outputs/20260601-03-smoke-plus-official-tool-evaluation/metrics/official_eval_smoke_plus_expanded_posebusters_subset35_summary.json --output-csv outputs/20260601-03-smoke-plus-official-tool-evaluation/tables/official_eval_smoke_plus_expanded_posebusters_subset35_summary.csv --name official_eval_smoke_plus_expanded_posebusters_subset35

# local-proposal pool
PYTHONPATH=src conda run -n pfr python scripts/data/generate_local_proposal_failures.py --config configs/data/failed_candidate_smoke_plus_local_proposal.yaml
PYTHONPATH=src conda run -n pfr python scripts/data/extract_feedback.py --config configs/feedback/smoke_plus_local_proposal.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/repair_baselines.py --config configs/baselines/repair_smoke_plus_local_proposal.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/eval_repaired.py --config configs/baselines/eval_repaired_smoke_plus_local_proposal.yaml
PYTHONPATH=src conda run -n pfr pytest -q
```

### 输出文件

- PoseBusters subset：`outputs/20260601-03-smoke-plus-official-tool-evaluation/processed/repaired_candidates_smoke_plus_posebusters_expanded_subset35.jsonl`, `outputs/20260601-03-smoke-plus-official-tool-evaluation/metrics/official_eval_smoke_plus_expanded_posebusters_subset35.jsonl`, `outputs/20260601-03-smoke-plus-official-tool-evaluation/metrics/official_eval_smoke_plus_expanded_posebusters_subset35_summary.json`, `outputs/20260601-03-smoke-plus-official-tool-evaluation/tables/official_eval_smoke_plus_expanded_posebusters_subset35_summary.csv`。
- local-proposal candidates：`outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_candidates_smoke_plus_local_proposal.jsonl`, `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_molecules/smoke_plus_local_proposal_failed/`。
- local-proposal repaired/eval：`outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/repaired_candidates_smoke_plus_local_proposal.jsonl`, `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/evaluated_repaired_smoke_plus_local_proposal.jsonl`, `outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus_local_proposal.json`, `outputs/20260601-02-smoke-plus-expansion-and-variants/tables/repaired_smoke_plus_local_proposal.csv`, `outputs/20260601-02-smoke-plus-expansion-and-variants/processed/repaired_molecules/smoke_plus_local_proposal_repaired/`。
- 新增脚本与配置：`scripts/data/generate_local_proposal_failures.py`, `configs/data/failed_candidate_smoke_plus_local_proposal.yaml`, `configs/feedback/smoke_plus_local_proposal.yaml`, `configs/baselines/repair_smoke_plus_local_proposal.yaml`, `configs/baselines/eval_repaired_smoke_plus_local_proposal.yaml`。

### 主要结果

| 指标 | 结果 | 备注 |
|---|---:|---|
| PoseBusters subset35 records | 35 | 7 failure types x 5 key baselines |
| PoseBusters subprocess timeout | 11/35 | 主要体现为 `subprocess_timeout_after_25s` |
| PoseBusters judged records full pass | 0/24 | full pass 仍无阳性 |
| local-proposal failed candidates | 72 | 12 complexes x 6 proposals |
| local-proposal repaired records | 864 | 72 candidates x 12 baselines |
| local-proposal failure type counts | atom_substitution 12, clash 13, geometry_drift 47 | 未产生 anchor_drift 主导样本 |
| tests | 15 passed | `PYTHONPATH=src conda run -n pfr pytest -q` |
| local-proposal feedback_geometry_refinement success | 0.875 | fallback proxy |
| local-proposal feedback_learned_geometry_policy success | 0.875 | ridge oracle-free policy, fallback proxy |
| local-proposal no_feedback_repair success | 0.8194 | no-feedback 仍较高 |
| local-proposal direct_regeneration success | 0.7361 | baseline |

### 结论

- 扩展 PoseBusters subset35 说明 PoseBusters 仍不能作为当前稳定主指标：timeout 仍存在, 可判定记录 full pass 为 0。
- local-proposal pool 比固定 7 类 controlled perturbation 更接近“从多个局部候选中产生失败样本”的实验设定, 但仍是 RDKit proposal pool, 不是真实 generator/docking/local proposal 系统失败。
- 在 local-proposal pool 上, geometry refinement 和 ridge policy 的 fallback success 高于 no-feedback/direct regeneration, 但 no-feedback 仍高, 因此仍只能作为 smoke-level positive evidence。

### 失败 / 异常 / 负结果

- `best_of_n` 在 subset35 PoseBusters 中 7/7 timeout, 其他 key baselines 各 1/7 timeout；该结果提示 subset 和工具运行时仍需稳定化。
- local-proposal pool 未覆盖真实深度生成器失败模式, 后续仍需要接入 generator/docking/local proposal 的真实候选池。

## 2026-06-01 / 扩展 1008-record 官方 PLIP+Vina score-only retry 完成

### 环境与数据版本

- commit：65e95ee Clean receptor files for smoke data
- 环境：`pfr-eval-tools` conda 环境, PoseBusters / PLIP / Vina / Meeko / OpenBabel 已安装。
- CPU/GPU：CPU；未使用 GPU。
- 数据版本：`outputs/20260601-02-smoke-plus-expansion-and-variants/processed/repaired_candidates_smoke_plus.jsonl`, 1008 repaired records = 84 failed candidates x 12 baselines。

### 阶段目标

- 对扩展 7-type smoke-plus repaired set 重跑官方 PLIP interaction-count 和 Vina score-only retry。
- 验证旧 480-record coverage 不能外推的问题, 并为扩展集生成独立 JSONL / summary / CSV。

### 命令与配置

```bash
tmux new-session -d -s pfr_expanded_plip_vina 'PYTHONPATH=src conda run -n pfr-eval-tools python scripts/eval/eval_official_tools.py --repaired-candidates outputs/20260601-02-smoke-plus-expansion-and-variants/processed/repaired_candidates_smoke_plus.jsonl --output outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_expanded_plip_vina_retry.jsonl --tools plip,vina > outputs/20260601-04-vina-pose-and-local-edit-diagnostics/logs/official_eval_smoke_plus_expanded_plip_vina_retry.log 2>&1; PYTHONPATH=src conda run -n pfr-eval-tools python scripts/eval/summarize_official_eval.py --input outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_expanded_plip_vina_retry.jsonl --output-json outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_expanded_plip_vina_retry_summary.json --output-csv outputs/20260601-04-vina-pose-and-local-edit-diagnostics/tables/official_eval_smoke_plus_expanded_plip_vina_retry_summary.csv --name official_eval_smoke_plus_expanded_plip_vina_retry >> outputs/20260601-04-vina-pose-and-local-edit-diagnostics/logs/official_eval_smoke_plus_expanded_plip_vina_retry.log 2>&1'
```

### 输出文件

- raw JSONL：`outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_expanded_plip_vina_retry.jsonl`
- summary JSON：`outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_expanded_plip_vina_retry_summary.json`
- summary CSV：`outputs/20260601-04-vina-pose-and-local-edit-diagnostics/tables/official_eval_smoke_plus_expanded_plip_vina_retry_summary.csv`
- log：`outputs/20260601-04-vina-pose-and-local-edit-diagnostics/logs/official_eval_smoke_plus_expanded_plip_vina_retry.log`

### 主要结果

| baseline | records | PLIP errors | Vina errors | mean PLIP interaction count | mean Vina score-only energy |
|---|---:|---:|---:|---:|---:|
| direct_regeneration | 84 | 0 | 0 | 10.7381 | -0.4444 |
| best_of_n | 84 | 0 | 0 | 11.0952 | -3.5315 |
| no_feedback_repair | 84 | 0 | 0 | 11.2500 | -3.5682 |
| feedback_geometry_refinement | 84 | 0 | 0 | 10.8452 | -4.6964 |
| feedback_learned_geometry_policy | 84 | 0 | 0 | 11.2143 | -5.9780 |
| feedback_kernel_geometry_policy | 84 | 0 | 0 | 11.0952 | -4.3388 |
| feedback_knn_geometry_policy | 84 | 0 | 0 | 10.6190 | -3.7577 |
| coordinate_rollback | 84 | 0 | 0 | 11.6667 | -8.8129 |
| feedback_rule_repair | 84 | 0 | 0 | 11.4167 | -8.4290 |

### 结论

- 扩展 1008-record 集合的官方 PLIP+Vina coverage 已补齐: PLIP 1008/1008 且 0 error, Vina score-only 1008/1008 且 0 error。
- 在非 oracle smoke baselines 中, ridge `feedback_learned_geometry_policy` 的 Vina score-only mean energy 优于 geometry refinement, Best-of-N, no-feedback 和 direct regeneration；PLIP interaction-count 与 no-feedback / Best-of-N 接近, 不是单独强证据。
- rollback/rule sanity baselines 仍显示更好的 Vina score-only, 但它们包含 reference/规则 sanity 信息, 不能作为非 oracle 方法主张。

### 失败 / 异常 / 负结果

- Vina 仍为 score-only, 不是 redocking success, 不能单独证明 repaired candidate 有真实结合优势。
- PLIP 当前汇总是 interaction count, 不是 interaction recovery / similarity, 后续仍需与 reference interaction fingerprint 做更细指标。
- PoseBusters 在 expanded subset35 上仍存在 timeout 和 0 full pass, 官方几何稳定性仍是主要阻塞。
- 追加 PoseBusters diagnostic subset10 后发现, full pass 为 0 的主因不只是 pocket clash: 8/8 可判定记录失败 `molecular_formula`, `molecular_bonds`, `tetrahedral_chirality`, `inchi_overall`, `hydrogens`, `stereochemistry_preserved` 等 reference-consistency/redock checks；同时有 protein/cofactor/water distance checks 和少量 bond/angle/clash failures。当前 repair task 允许 local editing / atom substitution, 因此 PoseBusters redock full-pass 协议与任务定义存在不完全匹配, 后续应拆分报告 chemical validity / geometry sanity / pocket distance 子集, 而不是只用 full pass。

### failure-type 官方细分补充

- 已新增 `scripts/eval/summarize_official_by_failure_type.py`。
- 输出：`outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_expanded_plip_vina_retry_by_failure_type.json`, `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/tables/official_eval_smoke_plus_expanded_plip_vina_retry_by_failure_type.csv`。
- 结果规模：1008 raw records 汇总为 84 个 baseline x failure_type groups。
- `anchor_invalid`: direct_regeneration mean Vina 19.6452, best_of_n 17.5125, no_feedback 17.2667, feedback_geometry_refinement -1.9027, ridge feedback_learned_geometry_policy -0.1542。该类型最清楚体现 feedback repair 对 anchor drift 的修正信号, 但绝对值仍不强。
- `interaction_loss`: ridge -6.6949, best_of_n -6.0239, no_feedback -6.1416, geometry refinement -3.3468, direct -1.9897。ridge 有 score-only 优势, 但 no-feedback/Best-of-N 也强。
- `score_hacking`: ridge -5.1704, no_feedback -4.4959, best_of_n -4.4692, geometry refinement -3.8620, direct -1.7637；ridge 的 PLIP interaction count 也较高, 但仍只是 interaction count。
- `linker_too_flexible` 和 `drug_likeness_drop`: no-feedback 或 Best-of-N 仍表现很强, 说明这些 failure types 不能只靠几何/score-only 判断修复成功。
- 继续增强 learned repair model, 不把 ridge/kNN policy 当作最终主方法。

## 2026-06-01 / oracle-free residual ensemble repair policy

### 环境与数据版本

- commit：65e95ee Clean receptor files for smoke data
- 环境：`pfr` conda 环境, Python 3.11.15, RDKit 2026.03.2。
- CPU/GPU：CPU；未使用 GPU。
- 数据版本：expanded smoke-plus 84 failed candidates, 新增 baseline 后 1092 repaired records；local-proposal pool 72 failed candidates, 新增 baseline 后 936 repaired records。

### 阶段目标

- 在 ridge/kernel/kNN 之外增强 oracle-free learned repair, 但仍不使用 reference rollback target。
- 新增 `feedback_residual_ensemble_policy`: ridge offset + RBF kernel residual correction + predicted-offset neighborhood geometry selection。

### 命令与配置

```bash
PYTHONPATH=src conda run -n pfr python scripts/eval/repair_baselines.py --config configs/baselines/repair_smoke_plus.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/eval_repaired.py --config configs/baselines/eval_repaired_smoke_plus.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/repair_baselines.py --config configs/baselines/repair_smoke_plus_local_proposal.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/eval_repaired.py --config configs/baselines/eval_repaired_smoke_plus_local_proposal.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/summarize_repaired_by_failure_type.py --evaluated outputs/20260601-02-smoke-plus-expansion-and-variants/processed/evaluated_repaired_smoke_plus.jsonl --metrics-path outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus_by_failure_type.json --table-path outputs/20260601-02-smoke-plus-expansion-and-variants/tables/repaired_smoke_plus_by_failure_type.csv
PYTHONPATH=src conda run -n pfr pytest -q
```

### 主要结果

| 数据版本 | baseline | success | pose-like | contact similarity | Vina-like proxy |
|---|---|---:|---:|---:|---:|
| expanded smoke-plus | direct_regeneration | 0.5476 | 0.6190 | 0.8007 | 2.8024 |
| expanded smoke-plus | best_of_n | 0.6905 | 0.7500 | 0.8937 | 1.9166 |
| expanded smoke-plus | no_feedback_repair | 0.6905 | 0.7500 | 0.8937 | 1.9676 |
| expanded smoke-plus | feedback_learned_geometry_policy | 0.7500 | 0.8571 | 0.8888 | 1.0920 |
| expanded smoke-plus | feedback_geometry_refinement | 0.7857 | 0.9524 | 0.8765 | 0.7128 |
| expanded smoke-plus | feedback_residual_ensemble_policy | 0.7976 | 0.9048 | 0.8855 | 0.8451 |
| local-proposal pool | direct_regeneration | 0.7361 | 0.7500 | 0.8509 | 1.3441 |
| local-proposal pool | no_feedback_repair | 0.8194 | 0.8194 | 0.9422 | 1.0486 |
| local-proposal pool | feedback_learned_geometry_policy | 0.8750 | 0.8889 | 0.9198 | 0.9588 |
| local-proposal pool | feedback_geometry_refinement | 0.8750 | 0.9583 | 0.8879 | 0.6486 |
| local-proposal pool | feedback_residual_ensemble_policy | 0.9028 | 0.9028 | 0.9126 | 0.8687 |

### failure-type split

- `interaction_loss`: residual ensemble 0.9167, ridge 0.9167, geometry refinement 1.0, no-feedback 0.5833。
- `score_hacking`: residual ensemble 0.9167, ridge 0.75, geometry refinement 0.9167, no-feedback 0.6667。
- `linker_too_flexible`: residual ensemble 0.8333, ridge 0.75, geometry refinement 0.75, no-feedback 0.75。
- `anchor_invalid`: residual ensemble 0.0833, ridge 0.0833, geometry refinement 0.4167, no-feedback 0.0。anchor repair 仍是弱点。

### 结论

- `feedback_residual_ensemble_policy` 在 expanded smoke-plus 和 local-proposal pool 的 fallback success 上均优于 ridge/kernel/kNN, 是当前最强 oracle-free learned repair baseline。
- 它没有使用 reference-centroid rollback target, 但仍依赖 oracle-free geometry pseudo-label 和 local geometry selection, 仍不是最终 publication-level 模型。
- 该 policy 改善了 interaction_loss / score_hacking / linker_too_flexible, 但 anchor_invalid 仍明显弱于 geometry refinement, 说明 anchor-specific feedback/action 还不充分。

### 失败 / 异常 / 负结果

- residual ensemble 的 Vina-like proxy 不如 geometry refinement, 说明 success rate 提升不是所有指标一致提升。
- no-feedback 在 drug_likeness_drop / geometry_invalid / clash 仍很强, 说明这些 failure types 当前定义仍不能充分区分 feedback repair。
- 新增 baseline 后 repaired set 变为 1092 records, 此前 1008-record 官方 PLIP/Vina 结果对应旧 baseline 集合；若要纳入 residual ensemble 的官方 PLIP/Vina, 需要单独重跑或增量跑该 baseline。

## 2026-06-01 / Vina-selected docking-like failed candidates

### 环境与数据版本

- commit：65e95ee Clean receptor files for smoke data
- 环境：`pfr` 和 `pfr-eval-tools` conda 环境。
- CPU/GPU：CPU；未使用 GPU。
- 候选来源：从 `smoke_local_proposal_pool_rdkit` 72 个 failed candidates 运行 Vina score-only, 每个 complex 选择最高 energy 的 local proposal 作为 docking-like score failure。

### 阶段目标

- 在 controlled perturbation 和 RDKit local-proposal pool 之外, 构造一个由官方 Vina score-only 选择的 docking-like failed candidate subset。
- 该集合来源仍是 RDKit local proposals + Vina score-only selection, 不是真实 docking search 或 deep generator 输出。

### 命令与配置

```bash
PYTHONPATH=src conda run -n pfr-eval-tools python scripts/eval/eval_official_tools.py --repaired-candidates outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_candidates_smoke_plus_local_proposal_for_vina.jsonl --output outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_local_proposal_failed_vina.jsonl --tools vina
PYTHONPATH=src conda run -n pfr-eval-tools python scripts/eval/summarize_official_eval.py --input outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_local_proposal_failed_vina.jsonl --output-json outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_local_proposal_failed_vina_summary.json --output-csv outputs/20260601-04-vina-pose-and-local-edit-diagnostics/tables/official_eval_smoke_plus_local_proposal_failed_vina_summary.csv --name official_eval_smoke_plus_local_proposal_failed_vina
PYTHONPATH=src conda run -n pfr python scripts/data/extract_feedback.py --config configs/feedback/smoke_plus_docking_like.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/repair_baselines.py --config configs/baselines/repair_smoke_plus_docking_like.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/eval_repaired.py --config configs/baselines/eval_repaired_smoke_plus_docking_like.yaml
PYTHONPATH=src conda run -n pfr pytest -q
```

### 输出文件

- Vina probe input：`outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_candidates_smoke_plus_local_proposal_for_vina.jsonl`
- Vina probe output：`outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_local_proposal_failed_vina.jsonl`, summary JSON/CSV。
- docking-like failed set：`outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_candidates_smoke_plus_docking_like.jsonl`
- docking-like feedback/repaired/eval：`outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/feedback_smoke_plus_docking_like.jsonl`, `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/repaired_candidates_smoke_plus_docking_like.jsonl`, `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/evaluated_repaired_smoke_plus_docking_like.jsonl`, `outputs/20260601-02-smoke-plus-expansion-and-variants/metrics/repaired_smoke_plus_docking_like.json`, `outputs/20260601-02-smoke-plus-expansion-and-variants/tables/repaired_smoke_plus_docking_like.csv`。

### 主要结果

| baseline | success | pose-like | contact similarity | Vina-like proxy |
|---|---:|---:|---:|---:|
| direct_regeneration | 0.5000 | 0.5000 | 0.8426 | 2.3456 |
| best_of_n | 0.5000 | 0.5000 | 0.8818 | 2.2202 |
| no_feedback_repair | 0.5000 | 0.5000 | 0.8818 | 2.2850 |
| feedback_geometry_refinement | 1.0000 | 1.0000 | 0.8802 | 0.6105 |
| feedback_learned_geometry_policy | 0.8333 | 0.8333 | 0.8472 | 2.1260 |
| feedback_kernel_geometry_policy | 0.8333 | 0.8333 | 0.8753 | 1.0663 |
| feedback_knn_geometry_policy | 0.7500 | 0.7500 | 0.8118 | 2.3145 |
| feedback_residual_ensemble_policy | 0.8333 | 0.8333 | 0.8433 | 1.3673 |

### 结论

- Vina-selected docking-like subset 比普通 local-proposal pool 更能区分 feedback repair: direct / Best-of-N / no-feedback success 均为 0.5, geometry refinement 达到 1.0。
- learned policies 均优于 no-feedback, 但 residual ensemble 在该 subset 上不如 geometry refinement, 且 Vina-like proxy 也弱于 geometry refinement。
- 该结果支持“feedback-conditioned repair 对 score-selected failures 有用”的初步证据, 但样本数只有 12, 且仍不是真实 docking search 或 generator 输出。

### 失败 / 异常 / 负结果

- 运行 Vina probe 时 RDKit 对 PDB reference ligand 产生 `Cannot convert 'HET' to unsigned int` 警告, 但 72/72 Vina score-only energy 写出且 0 error；后续应将 reference ligand 统一转成 SDF 或修正 reader 警告。
- docking-like subset 只有每 complex 1 条, 不能作为主实验结论。
- residual ensemble 在该集合上未超过 geometry refinement, 说明 learned policy 仍需 anchor/action-specific 建模。

## 2026-06-01 / PoseBusters submetrics, residual official PLIP+Vina, and Vina docked pose smoke

### 环境与数据版本

- commit：65e95ee Clean receptor files for smoke data
- 环境：`pfr` 和 `pfr-eval-tools` conda 环境。
- CPU/GPU：CPU；未使用 GPU。
- 数据版本：PoseBusters diagnostic subset10, residual-only expanded smoke-plus 84 records, Vina docked pose smoke 4 records。

### 阶段目标

- 拆分 PoseBusters full pass 为更符合 local editing task 的子指标。
- 给新增 `feedback_residual_ensemble_policy` 补官方 PLIP+Vina score-only 指标。
- 用实际 Vina docking 生成少量 docked pose failed candidates, 不再只用 Vina score-only selection。

### 命令与配置

```bash
PYTHONPATH=src conda run -n pfr python scripts/eval/summarize_posebusters_submetrics.py --input outputs/20260601-03-smoke-plus-official-tool-evaluation/metrics/official_eval_smoke_plus_posebusters_diagnostic_subset10.jsonl --output-json outputs/20260601-03-smoke-plus-official-tool-evaluation/metrics/official_eval_smoke_plus_posebusters_diagnostic_subset10_submetrics.json --output-csv outputs/20260601-03-smoke-plus-official-tool-evaluation/tables/official_eval_smoke_plus_posebusters_diagnostic_subset10_submetrics.csv --name official_eval_smoke_plus_posebusters_diagnostic_subset10_submetrics
PYTHONPATH=src conda run -n pfr-eval-tools python scripts/eval/eval_official_tools.py --repaired-candidates outputs/20260602-01-contact-degraded-budget-and-ablation/processed/repaired_candidates_smoke_plus_residual_only.jsonl --output outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_residual_plip_vina.jsonl --tools plip,vina
PYTHONPATH=src conda run -n pfr-eval-tools python scripts/eval/summarize_official_eval.py --input outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_residual_plip_vina.jsonl --output-json outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_residual_plip_vina_summary.json --output-csv outputs/20260601-04-vina-pose-and-local-edit-diagnostics/tables/official_eval_smoke_plus_residual_plip_vina_summary.csv --name official_eval_smoke_plus_residual_plip_vina
PYTHONPATH=src conda run -n pfr-eval-tools python scripts/data/generate_vina_docked_failures.py --input outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_candidates_smoke_plus_docking_like.jsonl --output outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_candidates_smoke_plus_vina_docked_pose_smoke.jsonl --molecules-dir outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_molecules/smoke_plus_vina_docked_failed --limit 4 --exhaustiveness 4 --seed 0
PYTHONPATH=src conda run -n pfr python scripts/data/extract_feedback.py --config configs/feedback/smoke_plus_vina_docked_pose_smoke.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/repair_baselines.py --config configs/baselines/repair_smoke_plus_vina_docked_pose_smoke.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/eval_repaired.py --config configs/baselines/eval_repaired_smoke_plus_vina_docked_pose_smoke.yaml
PYTHONPATH=src conda run -n pfr pytest -q
```

### 输出文件

- PoseBusters submetrics：`outputs/20260601-03-smoke-plus-official-tool-evaluation/metrics/official_eval_smoke_plus_posebusters_diagnostic_subset10_submetrics.json`, CSV。
- residual official：`outputs/20260602-01-contact-degraded-budget-and-ablation/processed/repaired_candidates_smoke_plus_residual_only.jsonl`, `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_residual_plip_vina.jsonl`, summary JSON/CSV。
- Vina docked pose smoke：`scripts/data/generate_vina_docked_failures.py`, `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_candidates_smoke_plus_vina_docked_pose_smoke.jsonl`, `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_molecules/smoke_plus_vina_docked_failed/`, feedback/repaired/eval JSONL, metrics JSON/CSV。

### 主要结果

- PoseBusters submetrics: diagnostic subset10 中可判定记录的 loading/sanitization 多为 1.0, reference_consistency all-pass 为 0.0；pocket_geometry 和 ligand_geometry 随 failure type / baseline 变化。说明 full pass 为 0 主要被 reference consistency 和局部几何共同驱动, 不应单独作为 local editing task 主指标。
- residual official PLIP+Vina: 84/84 PLIP 和 Vina score-only, 0 error；mean PLIP interaction count 11.0357, mean Vina score-only -6.0994。该 Vina score-only 略优于此前 ridge -5.9780, 但 PLIP count 略低于 ridge 11.2143。
- Vina docked pose smoke: 4/4 成功生成 docked pose SDF, 但 repaired pipeline 只写出 40/52 records, 因为部分 docked SDF 出现 RDKit sanitization / explicit valence warning。所有非 oracle baseline fallback success 为 0.0, coordinate rollback 可作为 oracle sanity 但不计入主张。

### 失败 / 异常 / 负结果

- Vina docked pose SDF 由 PDBQT 转 SDF 后存在 valence/sanitization 问题, 暴露真实 docking pose 接入比 score-only selection 更难。
- Vina docked pose smoke 的 4 条样本中, anchor errors 可很大, 但当前 learned policies 没有修复成功；这进一步说明 anchor/action-specific model 是下一阶段关键。
- residual ensemble 官方 Vina score-only 有轻微优势, 但 PLIP interaction count 未超过 ridge, 且仍不是 redocking success。

## 2026-06-01 / Workflow 撞题风险复核

### 阶段目标

- 用 Workflow 并行复核当前方向是否与已有 pocket-aware generation / optimization / benchmark 方法直接撞题。
- 重点比较 DiffDec, DiffLEOP/Diffleop, DecompOpt, DecompDPO, DecompDiff, MolJO, Delete, D3FG, BoKDiff, CBGBench, AMG, PoseBusters, PLIP, AutoDock Vina。

### 工具与输出

- Workflow run id: `wf_dc68b5c0-d07`。
- 输出文件：`/tmp/claude-1001/-home-lyj-mnt-project-pocket-failure-repair/77d0dfd2-ff1d-402b-85df-4dae3054ad8b/tasks/w170tixb0.output`。
- Transcript 目录：`/home/lyj/.claude/projects/-home-lyj-mnt-project-pocket-failure-repair/99dcac94-7446-40e1-b108-7b733f6113fa/subagents/workflows/wf_dc68b5c0-d07`。
- 使用 6 个 agents, 约 313k tokens, 207 tool uses。

### 主要结论

- 直接撞题风险: Low。
- 相邻工作风险: Medium。
- 未发现已有方法同时满足 `protein pocket + fixed scaffold/editable region + failed local candidate + explicit structured failure feedback + same-budget repair evaluation`。
- 最强相邻风险来自: DiffDec / D3FG 的 pocket-aware scaffold decoration / elaboration, DiffLEOP / DecompOpt / Delete / MolJO 的 structure-based lead/local optimization, DecompDPO 的 preference / energy alignment, BoKDiff 的 Best-of-N / Best-of-K reranking, CBGBench 的 benchmark 统一框架。

### 对论文定位的要求

- 最安全定位是 `failed-candidate-conditioned diagnostic local repair under same generation budget`。
- 避免泛泛声称新的 pocket-aware molecule generation, R-group generation, affinity-guided lead optimization, diffusion molecular optimization 或 docking-score optimization。
- 必须保留 same-budget baseline 和 ablation: direct regeneration, Best-of-N, rerank-only, no-feedback, geometry-only, interaction-only, full feedback。
- 必须继续接入更真实 failed candidates, 否则可能被审稿人认为只是 controlled perturbation benchmark 或普通 local optimization 的变体。

### 更新

- 已将第三轮 workflow 复核摘要写入 `docs/report/20260601-02-literature-matrix-report.md`。


## 2026-06-01 / Vina docked pose topology repair 与 anchor-policy 诊断

### 阶段目标

- 修复真实 Vina docked pose failed candidate 接入中的 PDBQT->SDF valence / sanitization 伪影。
- 检查 docked pose failure 是否可由简单非 oracle anchor repair policy 修复。
- 对修复后的 docked pose smoke 输出补跑官方 PLIP / Vina score-only, 并记录负结果。

### 代码与配置

- 修改 `scripts/data/generate_vina_docked_failures.py`:
  - 不再直接信任 OpenBabel 从 PDBQT 反推的 bond order。
  - 使用原始 failed ligand template topology, 合并 Vina docked PDBQT 的重原子坐标。
  - 成功 records 写入 `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_candidates_smoke_plus_vina_docked_pose_smoke.jsonl`。
  - 失败尝试写入 `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_candidates_smoke_plus_vina_docked_pose_smoke.errors.jsonl`。
- 修改 `scripts/eval/repair_baselines.py`:
  - 新增 `feedback_anchor_alignment_policy` 诊断 baseline。
  - 候选包括 identity, anchor-centroid translation, anchor rigid alignment, 最终按 geometry score 选择, 避免刚体对齐无条件制造 clash。
- 修改 `configs/baselines/repair_smoke_plus_vina_docked_pose_smoke.yaml`:
  - 加入 `feedback_anchor_alignment_policy`。

### 命令

```bash
PYTHONPATH=src conda run -n pfr python -m py_compile scripts/data/generate_vina_docked_failures.py scripts/eval/repair_baselines.py
PYTHONPATH=src conda run -n pfr-eval-tools python scripts/data/generate_vina_docked_failures.py --input outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_candidates_smoke_plus_docking_like.jsonl --output outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_candidates_smoke_plus_vina_docked_pose_smoke.jsonl --molecules-dir outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_molecules/smoke_plus_vina_docked_failed --limit 4 --exhaustiveness 4 --seed 0
PYTHONPATH=src conda run -n pfr python scripts/data/extract_feedback.py --config configs/feedback/smoke_plus_vina_docked_pose_smoke.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/repair_baselines.py --config configs/baselines/repair_smoke_plus_vina_docked_pose_smoke.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/eval_repaired.py --config configs/baselines/eval_repaired_smoke_plus_vina_docked_pose_smoke.yaml
PYTHONPATH=src conda run -n pfr-eval-tools python scripts/eval/eval_official_tools.py --repaired-candidates outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/repaired_candidates_smoke_plus_vina_docked_pose_smoke.jsonl --output outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_docked_pose_plip_vina.jsonl --tools plip,vina
PYTHONPATH=src conda run -n pfr python scripts/eval/summarize_official_eval.py --input outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_docked_pose_plip_vina.jsonl --output-json outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_docked_pose_plip_vina_summary.json --output-csv outputs/20260601-04-vina-pose-and-local-edit-diagnostics/tables/official_eval_smoke_plus_vina_docked_pose_plip_vina_summary.csv
PYTHONPATH=src conda run -n pfr pytest -q
```

### 输出

- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_candidates_smoke_plus_vina_docked_pose_smoke.jsonl`: 3 successful Vina docked pose failed candidates。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_candidates_smoke_plus_vina_docked_pose_smoke.errors.jsonl`: 1 failed attempt, `1hvr topology_coordinate_merge_failed:atom_count_mismatch:46:49`。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/repaired_candidates_smoke_plus_vina_docked_pose_smoke.jsonl`: 42 repaired records。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/repaired_smoke_plus_vina_docked_pose_smoke.json`。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_docked_pose_plip_vina.jsonl`: 42/42 official PLIP + Vina score-only records。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_docked_pose_plip_vina_summary.json`。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/tables/official_eval_smoke_plus_vina_docked_pose_plip_vina_summary.csv`。

### 主要结果

- Vina docked pose conversion: 3/4 input attempts produced RDKit-readable template-topology docked failed candidates。
- 1HVR 仍因 PDBQT / coordinate atom count mismatch 失败, 已写入 sidecar, 不再污染 repair/eval 汇总。
- Repaired fallback metrics on 3 successful docked candidates:
  - `feedback_anchor_alignment_policy`: success 0.0, anchor_validity 0.0, clash_free 1.0, mean contact similarity 0.573, mean Vina-like proxy 0.604。
  - `feedback_geometry_refinement`: success 0.0, anchor_validity 0.0, clash_free 1.0。
  - `feedback_residual_ensemble_policy`: success 0.0, anchor_validity 0.0, clash_free 0.6667。
  - `no_feedback_repair`: success 0.0, anchor_validity 0.0, clash_free 1.0。
  - `coordinate_rollback` / `feedback_rule_repair`: success 1.0 as oracle sanity only。
- Official PLIP/Vina on 42 repaired records: PLIP 42/42, Vina score-only 42/42, both 0 error。
  - `no_feedback_repair`: mean PLIP 10.0, mean Vina score-only -9.7777。
  - `feedback_anchor_alignment_policy`: mean PLIP 8.0, mean Vina score-only -7.4430。
  - `feedback_geometry_refinement`: mean PLIP 8.3333, mean Vina score-only -7.4177。
  - `feedback_residual_ensemble_policy`: mean PLIP 9.0, mean Vina score-only 8.1833。
  - `coordinate_rollback`: mean PLIP 11.0, mean Vina score-only -7.5030。

### 结论

- 已修复此前 1A4W 由 OpenBabel bond-order 反推导致的 valence/sanitization 伪影: 现在使用 template topology + Vina coordinates。
- 真实 Vina docked pose failures 的主失败不是 clash, 而是大 anchor drift / atom mapping / pose alignment 问题。
- 简单 anchor-centroid / rigid alignment 不足以修复真实 docked pose failure; 刚体对齐还可能制造严重 protein-ligand clash, 所以当前 `feedback_anchor_alignment_policy` 只能作为负结果诊断 baseline。
- Vina score-only 在这批真实 docked pose smoke 中偏好未修复 docked pose, 甚至优于 oracle rollback 的 score-only, 因此不能作为 repair success 主证据；必须依赖 anchor validity, contact/PLIP recovery, PoseBusters submetrics 和 task-specific success。

### 失败 / 阻塞 / 下一步

- 1HVR PDBQT coordinate merge 仍失败, 需要更稳健的 atom correspondence / Meeko pose export 处理。
- 非 oracle learned policies 在真实 docked pose 上 success 仍为 0.0, 说明 publication-level 模型需要显式 anchor/action-aware local editing, 而不是全分子平移或简单 geometry pseudo-label。
- 下一步应优先把真实 failed candidate 扩展到更多可转换 docked poses, 并实现 anchor-preserving editable-region-only repair action。

## 2026-06-01 / Anchor-preserved Vina local-edit failed candidates

### 阶段目标

- 构造比 full-molecule Vina docked pose 更符合 fixed scaffold / anchor local editing 设定的失败候选。
- 方法: 以成功转换的 Vina docked pose 为坐标来源, 只替换 reference ligand 的 editable atoms 坐标, 保留 reference scaffold / anchor 坐标与原始拓扑。
- 检查该子集能否区分 no-feedback, Best-of-N, feedback geometry 和 learned policies。

### 代码与配置

- 新增 `scripts/data/generate_vina_local_edit_failures.py`。
- 新增配置:
  - `configs/data/failed_candidate_smoke_plus_vina_local_edit.yaml`。
  - `configs/feedback/smoke_plus_vina_local_edit.yaml`。
  - `configs/baselines/repair_smoke_plus_vina_local_edit.yaml`。
  - `configs/baselines/eval_repaired_smoke_plus_vina_local_edit.yaml`。

### 命令

```bash
PYTHONPATH=src conda run -n pfr python scripts/data/generate_vina_local_edit_failures.py --config configs/data/failed_candidate_smoke_plus_vina_local_edit.yaml
PYTHONPATH=src conda run -n pfr python scripts/data/extract_feedback.py --config configs/feedback/smoke_plus_vina_local_edit.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/repair_baselines.py --config configs/baselines/repair_smoke_plus_vina_local_edit.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/eval_repaired.py --config configs/baselines/eval_repaired_smoke_plus_vina_local_edit.yaml
PYTHONPATH=src conda run -n pfr-eval-tools python scripts/eval/eval_official_tools.py --repaired-candidates outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/repaired_candidates_smoke_plus_vina_local_edit.jsonl --output outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_local_edit_plip_vina.jsonl --tools plip,vina
PYTHONPATH=src conda run -n pfr python scripts/eval/summarize_official_eval.py --input outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_local_edit_plip_vina.jsonl --output-json outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_local_edit_plip_vina_summary.json --output-csv outputs/20260601-04-vina-pose-and-local-edit-diagnostics/tables/official_eval_smoke_plus_vina_local_edit_plip_vina_summary.csv
```

### 输出

- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/failed_candidates_smoke_plus_vina_local_edit.jsonl`: 3 failed candidates, all `vina_local_edit_geometry_drift`。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/repaired_candidates_smoke_plus_vina_local_edit.jsonl`: 42 repaired records。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/repaired_smoke_plus_vina_local_edit.json`。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_local_edit_plip_vina.jsonl`: 42/42 official PLIP + Vina records, 0 PLIP/Vina errors。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_local_edit_plip_vina_summary.json`。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/tables/official_eval_smoke_plus_vina_local_edit_plip_vina_summary.csv`。

### 主要结果

- Fallback repaired success:
  - `identity_failed_candidate`, `no_feedback_repair`, `rerank_only`, `best_of_n`, `direct_regeneration`, `feedback_geometry_refinement`, `feedback_anchor_alignment_policy`, `feedback_learned_geometry_policy`, `feedback_kernel_geometry_policy`, `feedback_knn_geometry_policy`, `feedback_residual_ensemble_policy`: all success 1.0。
  - `feedback_linear_refinement`: success 0.3333, anchor_validity 0.3333, clash_free 0.3333。
- Official PLIP/Vina:
  - `no_feedback_repair` / `identity_failed_candidate` / `rerank_only`: mean PLIP 9.3333, mean Vina score-only -8.6403。
  - `best_of_n`: mean PLIP 9.0, mean Vina score-only -8.6340。
  - `feedback_anchor_alignment_policy` / `feedback_rule_repair`: mean PLIP 9.3333, mean Vina score-only -8.6403。
  - `coordinate_rollback`: mean PLIP 11.0, mean Vina score-only -7.5030。
  - `feedback_residual_ensemble_policy`: mean PLIP 7.0, mean Vina score-only -7.2083。

### 结论

- Anchor-preserved Vina local-edit candidates 更符合 fixed scaffold / anchor 设定, 但当前构造过于容易: failed candidate 本身已经满足 scaffold / anchor / clash 成功条件, no-feedback 与 identity 已经 1.0 success。
- 该子集不能作为主实验区分 feedback repair 方法, 只能作为任务边界诊断: 保留 anchor 后, 当前 success 定义不足以捕捉 editable-region interaction degradation。
- 下一步若继续使用 local-edit Vina 坐标, 必须把主指标扩展为相对 failed candidate 的 PLIP/contact recovery、editable-region geometry improvement 或 reference interaction recovery, 否则 no-feedback 会自然胜出。

### 失败 / 阻塞 / 下一步

- 当前 local-edit 子集只有 3 条, 且全是 geometry_drift, 不构成 BIBM 级证据。
- 需要构造 interaction-loss / local-clash / anchor-preserved but contact-degraded 的真实候选, 并将 success 定义从“基础合法性”升级到“相对失败候选有修复增益”。

## 2026-06-01 / Repair-gain 指标加入与 Vina 诊断集重评

### 阶段目标

- 修复 anchor-preserved Vina local-edit 子集中 identity/no-feedback basic success 1.0 导致的误判。
- 在统一 repaired evaluation 中加入相对 failed candidate 的 repair-gain 指标, 让“原地不动”不能被记为有效修复。

### 代码变更

- 修改 `src/pfr/evaluation/repaired.py`:
  - 每条 repaired record 新增 `source_failed_ligand_path`。
  - 新增 failed-vs-repaired 比较字段: `failed_anchor_distance_error`, `anchor_error_reduction`, `failed_clash_count`, `clash_count_reduction`, `failed_contact_fingerprint_similarity`, `contact_fingerprint_similarity_gain`, `failed_contact_recovery`, `contact_recovery_gain`, `failed_vina_like_proxy`, `vina_like_gain`。
  - 新增 `repair_gain_success`: 在 basic success 基础上, 需要 contact recovery/similarity gain, anchor error reduction, clash-count reduction 或 Vina-like proxy improvement 中至少一个成立。
  - baseline summary 新增 `repair_gain_success_rate`, mean contact gain, mean anchor reduction, mean clash reduction, mean Vina-like gain。

### 命令

```bash
PYTHONPATH=src conda run -n pfr python -m py_compile src/pfr/evaluation/repaired.py
PYTHONPATH=src conda run -n pfr pytest -q
PYTHONPATH=src conda run -n pfr python scripts/eval/eval_repaired.py --config configs/baselines/eval_repaired_smoke_plus_vina_docked_pose_smoke.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/eval_repaired.py --config configs/baselines/eval_repaired_smoke_plus_vina_local_edit.yaml
```

### 输出

- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/evaluated_repaired_smoke_plus_vina_docked_pose_smoke.jsonl`。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/repaired_smoke_plus_vina_docked_pose_smoke.json`。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/evaluated_repaired_smoke_plus_vina_local_edit.jsonl`。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/repaired_smoke_plus_vina_local_edit.json`。

### 主要结果

- Full-pose Vina docked failures:
  - All non-oracle baselines: basic success 0.0, repair_gain_success 0.0。
  - `coordinate_rollback` / `feedback_rule_repair`: basic success 1.0, gain_success 1.0, mean contact recovery gain 0.258, mean anchor error reduction 10.39; oracle sanity only。
- Anchor-preserved Vina local-edit failures:
  - `identity_failed_candidate`, `no_feedback_repair`, `rerank_only`: basic success 1.0, repair_gain_success 0.0。
  - `best_of_n`: basic success 1.0, repair_gain_success 0.0。
  - `direct_regeneration`, `feedback_kernel_geometry_policy`, `feedback_learned_geometry_policy`: gain_success 0.3333, mostly driven by proxy gain rather than robust contact gain。
  - `feedback_residual_ensemble_policy`: basic success 1.0, gain_success 0.0。
  - `coordinate_rollback`: basic success 1.0, gain_success 1.0, mean contact recovery gain 0.102; oracle sanity only。

### 结论

- `repair_gain_success` 成功解决了 anchor-preserved local-edit 中 “failed candidate 本身已经合法, identity/no-feedback 也算成功” 的误判。
- 目前非 oracle 方法在更真实 full-pose docking failure 上没有 gain, 在 anchor-preserved local-edit 上只有零星 proxy-driven gain, 仍不足以形成 BIBM 级主张。
- 后续主实验应同时报告 basic success 与 repair-gain success, 并把 gain 指标扩展到 official PLIP interaction recovery / similarity, 而不是只用 fallback contact 或 Vina-like proxy。

### 失败 / 下一步

- 当前 gain_success 阈值仍是 smoke-level heuristic, 需要在 method_design 和论文中明确为 diagnostic/fallback 指标。
- 下一步应实现 PLIP interaction fingerprint recovery/similarity, 并构造真正 contact-degraded but anchor-preserved 的 failed candidates。

## 2026-06-01 / Official PLIP interaction gain 接入与 Vina 诊断集重评

### 阶段目标

- 将上一阶段的 repair-gain 从 fallback contact proxy 扩展到官方 PLIP interaction fingerprint recovery / similarity。
- 对 full-pose Vina docked failures 和 anchor-preserved Vina local-edit failures 重新评估 reference / failed / repaired 三方 PLIP interaction gain。
- 检查 identity/no-feedback 是否仍被判为零增益, 并记录当前非 oracle 方法是否真正恢复 reference interactions。

### 代码变更

- 修改 `scripts/eval/eval_official_tools.py`:
  - `parse_plip_xml()` 现在输出 residue-level `plip_interaction_fingerprint` 和 `plip_interaction_fingerprint_count`, fingerprint key 为 `interaction_type|chain|resnr|restype`。
  - `run_plip()` 现在分别对 repaired, failed 和 reference ligand 运行 PLIP, 并输出 `plip_repaired_*`, `plip_failed_*`, `plip_reference_*` 字段。
  - 新增 `plip_interaction_recovery`, `plip_failed_interaction_recovery`, `plip_interaction_recovery_gain`, `plip_interaction_similarity`, `plip_failed_interaction_similarity`, `plip_interaction_similarity_gain`。
  - `merge_complex_pdb()` 增加 PDB ligand 读取支持, 以便 reference ligand PDB 也能参与 PLIP 计算。
  - official JSONL base record 保留 `protein_path`, `reference_ligand_path`, `source_failed_ligand_path`。
- 修改 `scripts/eval/summarize_official_eval.py` 和 `scripts/eval/summarize_official_by_failure_type.py`:
  - summary 新增 PLIP reference/failed/repaired interaction count, recovery, similarity 和 gain 的均值字段。
- 新增 `tests/test_official_plip_gain.py`:
  - 覆盖 PLIP XML residue fingerprint 解析和 Jaccard/recovery 计算。

### 命令

```bash
PYTHONPATH=src conda run -n pfr python -m py_compile scripts/eval/eval_official_tools.py scripts/eval/summarize_official_eval.py scripts/eval/summarize_official_by_failure_type.py
PYTHONPATH=src conda run -n pfr pytest -q
PYTHONPATH=src conda run -n pfr-eval-tools python scripts/eval/eval_official_tools.py --repaired-candidates outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/repaired_candidates_smoke_plus_vina_local_edit.jsonl --output outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_local_edit_plip_gain.jsonl --tools plip --keep-work-dir outputs/20260601-04-vina-pose-and-local-edit-diagnostics/logs/official_eval_smoke_plus_vina_local_edit_plip_gain
PYTHONPATH=src conda run -n pfr-eval-tools python scripts/eval/eval_official_tools.py --repaired-candidates outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/repaired_candidates_smoke_plus_vina_docked_pose_smoke.jsonl --output outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_docked_pose_plip_gain.jsonl --tools plip --keep-work-dir outputs/20260601-04-vina-pose-and-local-edit-diagnostics/logs/official_eval_smoke_plus_vina_docked_pose_plip_gain
PYTHONPATH=src conda run -n pfr python scripts/eval/summarize_official_eval.py --input outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_local_edit_plip_gain.jsonl --output-json outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_local_edit_plip_gain_summary.json --output-csv outputs/20260601-04-vina-pose-and-local-edit-diagnostics/tables/official_eval_smoke_plus_vina_local_edit_plip_gain_summary.csv --name official_eval_smoke_plus_vina_local_edit_plip_gain_summary
PYTHONPATH=src conda run -n pfr python scripts/eval/summarize_official_eval.py --input outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_docked_pose_plip_gain.jsonl --output-json outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_docked_pose_plip_gain_summary.json --output-csv outputs/20260601-04-vina-pose-and-local-edit-diagnostics/tables/official_eval_smoke_plus_vina_docked_pose_plip_gain_summary.csv --name official_eval_smoke_plus_vina_docked_pose_plip_gain_summary
PYTHONPATH=src conda run -n pfr python scripts/eval/summarize_official_by_failure_type.py --input outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_local_edit_plip_gain.jsonl --output-json outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_local_edit_plip_gain_by_failure_type.json --output-csv outputs/20260601-04-vina-pose-and-local-edit-diagnostics/tables/official_eval_smoke_plus_vina_local_edit_plip_gain_by_failure_type.csv --name official_eval_smoke_plus_vina_local_edit_plip_gain_by_failure_type
PYTHONPATH=src conda run -n pfr python scripts/eval/summarize_official_by_failure_type.py --input outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_docked_pose_plip_gain.jsonl --output-json outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_docked_pose_plip_gain_by_failure_type.json --output-csv outputs/20260601-04-vina-pose-and-local-edit-diagnostics/tables/official_eval_smoke_plus_vina_docked_pose_plip_gain_by_failure_type.csv --name official_eval_smoke_plus_vina_docked_pose_plip_gain_by_failure_type
```

### 输出

- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_local_edit_plip_gain.jsonl`: 42/42 PLIP records, 0 repaired-side PLIP errors。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_local_edit_plip_gain_summary.json`。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/tables/official_eval_smoke_plus_vina_local_edit_plip_gain_summary.csv`。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_local_edit_plip_gain_by_failure_type.json`。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/tables/official_eval_smoke_plus_vina_local_edit_plip_gain_by_failure_type.csv`。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_docked_pose_plip_gain.jsonl`: 42/42 PLIP records, 0 repaired-side PLIP errors。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_docked_pose_plip_gain_summary.json`。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/tables/official_eval_smoke_plus_vina_docked_pose_plip_gain_summary.csv`。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_vina_docked_pose_plip_gain_by_failure_type.json`。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/tables/official_eval_smoke_plus_vina_docked_pose_plip_gain_by_failure_type.csv`。

### 主要结果

- Anchor-preserved Vina local-edit PLIP gain:
  - `identity_failed_candidate`, `no_feedback_repair`, `rerank_only`: mean recovery 0.5823, failed recovery 0.5823, recovery gain 0.0, similarity gain 0.0。
  - `best_of_n`: mean recovery 0.5823, recovery gain 0.0, similarity gain 0.0152。
  - `feedback_geometry_refinement`: mean recovery 0.3961, recovery gain -0.1861, similarity gain -0.1333。
  - `feedback_residual_ensemble_policy`: mean recovery 0.3961, recovery gain -0.1861, similarity gain -0.1531。
  - `coordinate_rollback`: mean recovery 1.0, recovery gain 0.4177, similarity gain 0.5342; oracle sanity only。
- Full-pose Vina docked PLIP gain:
  - `identity_failed_candidate`, `no_feedback_repair`, `rerank_only`, `best_of_n`: mean recovery 0.3338, failed recovery 0.3338, recovery gain 0.0。
  - `feedback_geometry_refinement`: mean recovery 0.4104, recovery gain 0.0766, similarity gain 0.0950, 但 fallback basic/gain success 仍为 0.0, 因 anchor validity 失败。
  - `feedback_residual_ensemble_policy`: mean recovery 0.2022, recovery gain -0.1316, similarity gain -0.0808。
  - `coordinate_rollback` / `feedback_rule_repair`: mean recovery 1.0, recovery gain 0.6662, similarity gain 0.8007; oracle sanity only。
- `pytest -q`: 17 passed。

### 结论

- 官方 PLIP interaction recovery / similarity 已接入, 可以在 official_eval JSONL 中直接比较 reference, failed 和 repaired 三方 interaction fingerprints。
- 新指标确认: identity/no-feedback/rerank 在两个 Vina 诊断集上的 PLIP recovery gain 都是 0.0, 因此不会被误读为真正 repair。
- 当前非 oracle 方法仍没有形成稳定正信号: local-edit 上 geometry / residual policies 反而降低 PLIP recovery; full-pose docked 上 geometry refinement 有轻微 PLIP recovery gain, 但 anchor validity 仍失败, 不能算 task success。
- 这强化了当前方向判断: 需要真正 anchor-preserving, editable-region-only 的 repair action, 而不是全分子平移或 geometry-only candidate selection。

### 失败 / 限制 / 下一步

- 当前 PLIP fingerprint 是 residue-level, 不包含 ligand atom correspondence 或距离分箱; 可作为官方 interaction diagnostic, 但还不是最终 publication-level interaction metric。
- 部分 PLIP XML residue 字段出现 `resnr=0` 的伪残基, 已保留在原始 JSONL 中用于审计; 后续应研究是否来自 RDKit PDB block residue numbering, 并在 paper 中说明或改为更稳健的 residue mapping。
- 下一步应构造 contact-degraded but anchor-preserved failed candidates, 并把 PLIP recovery gain 纳入 `repair_gain_success` 的正式判定或单独报告为 primary interaction-gain 指标。

## 2026-06-01 / Contact-degraded anchor-preserved local-edit 与 editable-contact repair

### 阶段目标

- 响应 Vina local-edit 子集“failed candidate 本身已经 basic success 1.0”的问题, 构造真正 contact-degraded 但 scaffold/anchor 保持的 local-edit failed candidates。
- 实现一个不移动 scaffold/anchor、只调整 editable atoms 的 oracle-free repair baseline, 验证 failure-feedback-conditioned local repair 是否能在 same-budget 下超过 identity/no-feedback/rerank/Best-of-N。
- 用 fallback contact gain 和 official PLIP interaction gain 同时审计, 避免只靠 Vina 或只靠基础合法性。

### 代码与配置

- 新增 `scripts/data/generate_contact_degraded_local_edit_failures.py`:
  - 输入 `data/datasets/rgroup_smoke_plus/entries/index.jsonl`。
  - 只扰动 editable atoms, 保持 scaffold/anchor 坐标不动。
  - 从 radial/tangent 小位移池中选择无 clash、anchor error <= 1.0 且 fallback contact recovery loss > 0.05 的 failed candidate。
- 新增配置:
  - `configs/data/failed_candidate_smoke_plus_contact_degraded_local_edit.yaml`。
  - `configs/feedback/smoke_plus_contact_degraded_local_edit.yaml`。
  - `configs/baselines/repair_smoke_plus_contact_degraded_local_edit.yaml`。
  - `configs/baselines/eval_repaired_smoke_plus_contact_degraded_local_edit.yaml`。
- 修改 `scripts/eval/repair_baselines.py`:
  - 新增 `feedback_editable_contact_policy`。
  - 该 policy 只对 editable atoms 应用小步 offset, 用 protein-ligand contact count、clash penalty、anchor penalty 的 oracle-free proxy 选择候选。

### 命令

```bash
PYTHONPATH=src conda run -n pfr python -m py_compile scripts/data/generate_contact_degraded_local_edit_failures.py scripts/eval/repair_baselines.py
PYTHONPATH=src conda run -n pfr pytest -q
PYTHONPATH=src conda run -n pfr python scripts/data/generate_contact_degraded_local_edit_failures.py --config configs/data/failed_candidate_smoke_plus_contact_degraded_local_edit.yaml
PYTHONPATH=src conda run -n pfr python scripts/data/extract_feedback.py --config configs/feedback/smoke_plus_contact_degraded_local_edit.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/repair_baselines.py --config configs/baselines/repair_smoke_plus_contact_degraded_local_edit.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/eval_repaired.py --config configs/baselines/eval_repaired_smoke_plus_contact_degraded_local_edit.yaml
PYTHONPATH=src conda run -n pfr-eval-tools python scripts/eval/eval_official_tools.py --repaired-candidates outputs/20260601-05-contact-degraded-local-edit-core/processed/repaired_candidates_smoke_plus_contact_degraded_local_edit.jsonl --output outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain.jsonl --tools plip --keep-work-dir outputs/20260601-05-contact-degraded-local-edit-core/logs/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain
PYTHONPATH=src conda run -n pfr python scripts/eval/summarize_official_eval.py --input outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain.jsonl --output-json outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_summary.json --output-csv outputs/20260601-05-contact-degraded-local-edit-core/tables/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_summary.csv --name official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_summary
PYTHONPATH=src conda run -n pfr python scripts/eval/summarize_official_by_failure_type.py --input outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain.jsonl --output-json outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_by_failure_type.json --output-csv outputs/20260601-05-contact-degraded-local-edit-core/tables/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_by_failure_type.csv --name official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_by_failure_type
```

### 输出

- `outputs/20260601-05-contact-degraded-local-edit-core/processed/failed_candidates_smoke_plus_contact_degraded_local_edit.jsonl`: 5 failed candidates from 12 smoke-plus examples。
- `outputs/20260601-05-contact-degraded-local-edit-core/processed/feedback_smoke_plus_contact_degraded_local_edit.jsonl`: 5 feedback records。
- `outputs/20260601-05-contact-degraded-local-edit-core/processed/repaired_candidates_smoke_plus_contact_degraded_local_edit.jsonl`: 70 repaired records。
- `outputs/20260601-05-contact-degraded-local-edit-core/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit.jsonl`。
- `outputs/20260601-05-contact-degraded-local-edit-core/metrics/repaired_smoke_plus_contact_degraded_local_edit.json`。
- `outputs/20260601-05-contact-degraded-local-edit-core/tables/repaired_smoke_plus_contact_degraded_local_edit.csv`。
- `outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain.jsonl`: 70/70 PLIP records, 0 repaired-side PLIP errors。
- `outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_summary.json`。
- `outputs/20260601-05-contact-degraded-local-edit-core/tables/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_summary.csv`。
- `outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_by_failure_type.json`。
- `outputs/20260601-05-contact-degraded-local-edit-core/tables/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_by_failure_type.csv`。

### 主要结果

- Failed candidate quality:
  - 5/12 smoke-plus examples 生成满足条件的 contact-degraded local-edit failures。
  - fallback contact recovery loss range: 0.095-0.261。
  - all selected candidates: clash_count 0, anchor_distance_error 0.0。
- Fallback repaired evaluation:
  - `identity_failed_candidate`, `no_feedback_repair`, `rerank_only`, `best_of_n`: basic success 1.0, repair_gain_success 0.0, mean contact recovery gain 0.0。
  - `feedback_editable_contact_policy`: basic success 1.0, repair_gain_success 1.0, mean contact recovery gain 0.1039, mean contact similarity gain 0.0897。
  - `feedback_geometry_refinement`: basic success 0.8, repair_gain_success 0.2, mean contact recovery gain 0.0111, mean anchor error reduction -0.7000。
  - `feedback_residual_ensemble_policy`: basic success 0.8, repair_gain_success 0.2, mean contact recovery gain 0.0167, mean anchor error reduction -0.6776。
  - `coordinate_rollback`: basic success 1.0, repair_gain_success 1.0, mean contact recovery gain 0.1469; oracle sanity only。
- Official PLIP interaction gain:
  - `identity_failed_candidate`, `no_feedback_repair`, `rerank_only`, `feedback_rule_repair`: mean PLIP recovery 0.8117, failed recovery 0.8117, recovery gain 0.0。
  - `best_of_n`: mean recovery 0.8011, recovery gain -0.0105, similarity gain +0.0067。
  - `feedback_editable_contact_policy`: mean recovery 0.8222, recovery gain +0.0105, similarity gain -0.0021。
  - `feedback_geometry_refinement`: mean recovery 0.6434, recovery gain -0.1682。
  - `feedback_residual_ensemble_policy`: mean recovery 0.7647, recovery gain -0.0470。
  - `coordinate_rollback`: mean recovery 1.0, recovery gain +0.1883; oracle sanity only。
- `pytest -q`: 17 passed。

### 结论

- contact-degraded local-edit subset 是当前更合理的 fixed scaffold / anchor 诊断集: failed candidate 已经 basic-success 合法, 但存在可量化 contact recovery loss。
- `feedback_editable_contact_policy` 是第一个明确超过 identity/no-feedback/rerank/Best-of-N 的非 oracle editable-only repair-gain baseline, 但该结论主要由 fallback distance-contact gain 支持。
- Official PLIP recovery gain 方向为正但很弱 (+0.0105), 说明 residue-level PLIP 指标对这种小步 editable-coordinate repair 不够敏感, 或当前 policy 只恢复距离 contact 而未稳定恢复 PLIP interaction class。
- 当前仍不能宣称 BIBM 级主结果; 但已经形成一个可审计的更窄切口: anchor-preserved contact-degraded local-edit repair under same budget。

### 失败 / 限制 / 下一步

- 5/12 覆盖仍太小, 需要扩大 offset/search 或接入更多 complexes。
- `feedback_editable_contact_policy` 是 heuristic candidate selection, 不是 learned model; 下一步应把 editable-only action space 扩展为 learned policy 或 interaction-conditioned scoring。
- Official PLIP gain 很弱, 下一步需要按 interaction type / residue diagnostics 分析失败原因, 并考虑 atom-level 或 distance-binned PLIP/contact hybrid 指标。

## 2026-06-01 / Learned editable-contact policy 初步验证

### 阶段目标

- 将 contact-degraded local-edit 的启发式 editable-contact policy 推进为非 oracle learned baseline。
- 采用 leave-complex-out 设置, 避免用同一 complex 的 target 直接指导自身修复。
- 检查 learned policy 是否在 fallback repair-gain 和 official PLIP interaction gain 上超过 identity/no-feedback/rerank/Best-of-N。

### 代码与配置

- 修改 `scripts/eval/repair_baselines.py`:
  - 新增 `editable_contact_target()` 和 `build_editable_contact_training_rows()`。
  - 新增 `feedback_learned_editable_contact_policy`。
  - 对每个 held-out complex, 使用其他 complexes 的 oracle-free editable contact proxy 最佳 offset 作为训练 target。
  - 推理时按 feedback feature 最近邻选择 offset, 且只移动 editable atoms, 不移动 scaffold/anchor。
- 修改 `configs/baselines/repair_smoke_plus_contact_degraded_local_edit.yaml`:
  - 加入 `feedback_learned_editable_contact_policy`。

### 命令

```bash
PYTHONPATH=src conda run -n pfr python -m py_compile scripts/eval/repair_baselines.py
PYTHONPATH=src conda run -n pfr pytest -q
PYTHONPATH=src conda run -n pfr python scripts/eval/repair_baselines.py --config configs/baselines/repair_smoke_plus_contact_degraded_local_edit.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/eval_repaired.py --config configs/baselines/eval_repaired_smoke_plus_contact_degraded_local_edit.yaml
PYTHONPATH=src conda run -n pfr-eval-tools python scripts/eval/eval_official_tools.py --repaired-candidates outputs/20260601-05-contact-degraded-local-edit-core/processed/repaired_candidates_smoke_plus_contact_degraded_local_edit.jsonl --output outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain.jsonl --tools plip --keep-work-dir outputs/20260601-05-contact-degraded-local-edit-core/logs/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain
PYTHONPATH=src conda run -n pfr python scripts/eval/summarize_official_eval.py --input outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain.jsonl --output-json outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_summary.json --output-csv outputs/20260601-05-contact-degraded-local-edit-core/tables/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_summary.csv --name official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_summary
PYTHONPATH=src conda run -n pfr python scripts/eval/summarize_official_by_failure_type.py --input outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain.jsonl --output-json outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_by_failure_type.json --output-csv outputs/20260601-05-contact-degraded-local-edit-core/tables/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_by_failure_type.csv --name official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_by_failure_type
```

### 输出

- `outputs/20260601-05-contact-degraded-local-edit-core/processed/repaired_candidates_smoke_plus_contact_degraded_local_edit.jsonl`: 75 repaired records after adding learned policy。
- `outputs/20260601-05-contact-degraded-local-edit-core/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit.jsonl`。
- `outputs/20260601-05-contact-degraded-local-edit-core/metrics/repaired_smoke_plus_contact_degraded_local_edit.json`。
- `outputs/20260601-05-contact-degraded-local-edit-core/tables/repaired_smoke_plus_contact_degraded_local_edit.csv`。
- `outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain.jsonl`: 75/75 PLIP records。
- `outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_summary.json`。
- `outputs/20260601-05-contact-degraded-local-edit-core/tables/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_summary.csv`。
- `outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_by_failure_type.json`。
- `outputs/20260601-05-contact-degraded-local-edit-core/tables/official_eval_smoke_plus_contact_degraded_local_edit_plip_gain_by_failure_type.csv`。

### 主要结果

- Fallback repaired evaluation:
  - `feedback_learned_editable_contact_policy`: basic success 1.0, repair_gain_success 0.6, mean contact recovery gain 0.0492, mean contact similarity gain 0.0364, anchor error reduction 0.0。
  - `feedback_editable_contact_policy`: basic success 1.0, repair_gain_success 1.0, mean contact recovery gain 0.1039; heuristic upper-bound。
  - `no_feedback_repair`, `identity_failed_candidate`, `rerank_only`, `best_of_n`: basic success 1.0, repair_gain_success 0.0。
  - `feedback_residual_ensemble_policy`: basic success 0.8, repair_gain_success 0.4, mean anchor error reduction -0.4971。
  - `coordinate_rollback`: basic success 1.0, repair_gain_success 1.0, oracle sanity only。
- Official PLIP interaction gain:
  - `feedback_learned_editable_contact_policy`: recovery gain +0.0355, similarity gain +0.0201, mean recovery 0.8472。
  - `feedback_editable_contact_policy`: recovery gain +0.0105, similarity gain -0.0021。
  - `no_feedback_repair`: recovery gain 0.0。
  - `best_of_n`: recovery gain -0.0105。
  - `feedback_residual_ensemble_policy`: recovery gain -0.0434。
  - `coordinate_rollback`: recovery gain +0.1883, oracle sanity only。
- `pytest -q`: 17 passed。

### 结论

- Learned editable-contact policy 在 contact-degraded local-edit subset 上首次给出与研究主张一致的非 oracle learned 正信号: same-budget 下超过 no-feedback, rerank-only, Best-of-N, 并且 fallback contact gain 与 official PLIP recovery gain 方向一致。
- 该结果仍是 smoke-level: 只有 5 个 failed candidates, single seed, offset-level nearest-neighbor policy, 不能作为 BIBM 级最终结论。
- 相比启发式 editable-contact policy, learned policy fallback gain 较弱, 但 official PLIP gain 更强, 说明 PLIP residue-level interaction 与 distance-contact proxy 的偏好不完全一致。

### 失败 / 限制 / 下一步

- 需要扩大 contact-degraded candidate 覆盖率和 seeds, 否则统计不稳。
- 需要把 learned policy 从 nearest-neighbor offset 扩展到更连续的 feedback-conditioned editable action model。
- 需要做 ablation: geometry-only, interaction-only, full feedback, no-failed-candidate, global-score-only。

## 2026-06-01 / Contact-degraded 3-seed fallback ablation

### 阶段目标

- 将 contact-degraded local-edit 诊断从单 seed 扩展到 seeds 0/1/2。
- 在相同 editable-only action space 下加入 geometry-only, interaction-only, global-only 和 full-feedback ablation。
- 验证 learned editable-contact policy 是否稳定超过 no-feedback, rerank-only, Best-of-N, geometry-only 和 global-only。

### 代码与配置

- 修改 `scripts/eval/repair_baselines.py`:
  - 新增 editable-only ablation scoring: `geometry_only`, `interaction_only`, `global_only`, `full`。
  - 新增 baselines: `feedback_editable_geometry_only_policy`, `feedback_editable_interaction_only_policy`, `feedback_editable_global_only_policy`, `feedback_editable_full_policy`。
- 修改 `configs/baselines/repair_smoke_plus_contact_degraded_local_edit.yaml`:
  - 加入上述 ablation baselines。
- 新增 `scripts/eval/run_contact_degraded_multiseed.py`:
  - 自动为 seeds 0/1/2 生成临时 data/feedback/repair/eval 配置。
  - 写出 seed-specific candidates, feedback, repaired records, evaluated records, metrics 和 tables。
  - 聚合输出 `outputs/20260601-05-contact-degraded-local-edit-core/metrics/contact_degraded_multiseed/summary.json` 和 CSV。

### 命令

```bash
PYTHONPATH=src conda run -n pfr python -m py_compile scripts/eval/run_contact_degraded_multiseed.py scripts/eval/repair_baselines.py scripts/data/generate_contact_degraded_local_edit_failures.py
PYTHONPATH=src conda run -n pfr pytest -q
PYTHONPATH=src conda run -n pfr python scripts/eval/run_contact_degraded_multiseed.py --seeds 0,1,2
```

### 输出

- Seed-specific:
  - `outputs/20260601-05-contact-degraded-local-edit-core/processed/failed_candidates_smoke_plus_contact_degraded_local_edit_seed{0,1,2}.jsonl`: each 5 failed candidates。
  - `outputs/20260601-05-contact-degraded-local-edit-core/processed/feedback_smoke_plus_contact_degraded_local_edit_seed{0,1,2}.jsonl`。
  - `outputs/20260601-05-contact-degraded-local-edit-core/processed/repaired_candidates_smoke_plus_contact_degraded_local_edit_seed{0,1,2}.jsonl`: each 95 repaired records。
  - `outputs/20260601-05-contact-degraded-local-edit-core/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed{0,1,2}.jsonl`。
  - `outputs/20260601-05-contact-degraded-local-edit-core/metrics/repaired_smoke_plus_contact_degraded_local_edit_seed{0,1,2}.json`。
  - `outputs/20260601-05-contact-degraded-local-edit-core/tables/repaired_smoke_plus_contact_degraded_local_edit_seed{0,1,2}.csv`。
- Aggregated:
  - `outputs/20260601-05-contact-degraded-local-edit-core/metrics/contact_degraded_multiseed/summary.json`。
  - `outputs/20260601-05-contact-degraded-local-edit-core/metrics/contact_degraded_multiseed/summary.csv`。

### 主要结果

- Across seeds 0/1/2, each seed produced 5 contact-degraded local-edit failed candidates and 95 repaired records。
- 3-seed mean fallback metrics:
  - `feedback_learned_editable_contact_policy`: success 1.0, repair_gain_success 0.6667, mean contact recovery gain 0.0519, mean contact similarity gain 0.0403。
  - `feedback_editable_interaction_only_policy`: success 0.9333, repair_gain_success 0.9333, mean contact recovery gain 0.0937。
  - `feedback_editable_full_policy`: success 1.0, repair_gain_success 1.0, mean contact recovery gain 0.1029。
  - `feedback_editable_contact_policy`: success 1.0, repair_gain_success 1.0, mean contact recovery gain 0.1029。
  - `feedback_editable_geometry_only_policy`: success 1.0, repair_gain_success 0.0。
  - `feedback_editable_global_only_policy`: success 1.0, repair_gain_success 0.0。
  - `no_feedback_repair`, `identity_failed_candidate`, `rerank_only`: success 1.0, repair_gain_success 0.0。
  - `best_of_n`: success 1.0, repair_gain_success 0.0, mean contact recovery gain -0.0002。
  - `feedback_residual_ensemble_policy`: success 0.8667, repair_gain_success 0.2, mean contact recovery gain 0.0307, mean contact similarity gain -0.0403。
  - `coordinate_rollback`: success 1.0, repair_gain_success 1.0, oracle sanity only。
- `pytest -q`: 17 passed。

### 结论

- contact-degraded local-edit 3-seed fallback ablation 支持当前核心机制判断: interaction/contact feedback 是该子任务上的有效信号, 而 geometry-only 和 global-score-only 在 repair-gain 指标上没有贡献。
- Learned editable-contact policy 在 leave-complex-out 条件下稳定超过 no-feedback, rerank-only, Best-of-N, geometry-only 和 global-only, 但弱于 interaction-only/full heuristic upper-bound。
- 该结果仍是 smoke-level, 因为每 seed 只有 5 个 failed candidates, 且 learned policy 是 nearest-neighbor offset 选择而非深度模型。

### 失败 / 限制 / 下一步

- Official PLIP 3-seed interaction gain 已完成并补充如下。
- 需要扩大 contact-degraded failed candidate 覆盖率, 当前每 seed 只有 5/12 examples 通过筛选。
- `no_failed_candidate_policy` 已实现, 但由于从 reference ligand 出发, 属于 reference-only oracle sanity, 不作为公平主 baseline。
- 后续需要更连续的 feedback-conditioned editable action model。

### Official PLIP 3-seed 补充

- `outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_plip_gain.jsonl`: 285 records, 0 repaired-side PLIP errors。
- `outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_plip_gain_summary.json`。
- `outputs/20260601-05-contact-degraded-local-edit-core/tables/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_plip_gain_summary.csv`。
- 3-seed official PLIP recovery gain:
  - `feedback_learned_editable_contact_policy`: +0.0425, similarity gain +0.0310。
  - `feedback_editable_contact_policy`: +0.0354。
  - `feedback_editable_interaction_only_policy`: +0.0284。
  - `feedback_editable_full_policy`: +0.0354。
  - `feedback_editable_geometry_only_policy`, `feedback_editable_global_only_policy`, `no_feedback_repair`, `rerank_only`: 0.0。
  - `best_of_n`: -0.0581。
  - `coordinate_rollback`: +0.1883, oracle sanity only。

## 2026-06-01 / Expanded contact-degraded coverage 复核

### 阶段目标

- 检查上一轮 5 candidates/seed 的 contact-degraded 结论是否存在样本选择乐观偏差。
- 扩展每个 complex 可保留的 contact-degraded candidates 数量, 在同一 seeds 0/1/2 设置下重跑 ablation。
- 用官方 PLIP 对关键 baselines 做扩展验证。

### 代码与配置

- 修改 `scripts/data/generate_contact_degraded_local_edit_failures.py`:
  - 新增 `make_candidates()` 支持每个 example 输出多个通过筛选的 failed candidates。
  - 新增配置读取: `limits.max_per_example` 和 `limits.min_contact_recovery_loss`。
- 修改 `configs/data/failed_candidate_smoke_plus_contact_degraded_local_edit.yaml`:
  - `max_per_example: 3`。
  - `min_contact_recovery_loss: 0.03`。
- 修改 `scripts/eval/run_contact_degraded_multiseed.py`:
  - seed-specific data config 同步使用 `max_per_example: 3`, `min_contact_recovery_loss: 0.03`。

### 命令

```bash
PYTHONPATH=src conda run -n pfr python -m py_compile scripts/data/generate_contact_degraded_local_edit_failures.py scripts/eval/run_contact_degraded_multiseed.py
PYTHONPATH=src conda run -n pfr pytest -q
PYTHONPATH=src conda run -n pfr python scripts/data/generate_contact_degraded_local_edit_failures.py --config configs/data/failed_candidate_smoke_plus_contact_degraded_local_edit.yaml
PYTHONPATH=src conda run -n pfr python scripts/eval/run_contact_degraded_multiseed.py --seeds 0,1,2
PYTHONPATH=src conda run -n pfr pytest -q
```

### 输出

- `outputs/20260601-05-contact-degraded-local-edit-core/processed/failed_candidates_smoke_plus_contact_degraded_local_edit.jsonl`: seed 0 expanded set, 19 candidates across 7 complexes。
- `outputs/20260601-05-contact-degraded-local-edit-core/processed/failed_candidates_smoke_plus_contact_degraded_local_edit_seed0.jsonl`: 19 candidates。
- `outputs/20260601-05-contact-degraded-local-edit-core/processed/failed_candidates_smoke_plus_contact_degraded_local_edit_seed1.jsonl`: 17 candidates。
- `outputs/20260601-05-contact-degraded-local-edit-core/processed/failed_candidates_smoke_plus_contact_degraded_local_edit_seed2.jsonl`: 17 candidates。
- `outputs/20260601-05-contact-degraded-local-edit-core/processed/repaired_candidates_smoke_plus_contact_degraded_local_edit_seed0.jsonl`: 380 repaired records。
- `outputs/20260601-05-contact-degraded-local-edit-core/processed/repaired_candidates_smoke_plus_contact_degraded_local_edit_seed1.jsonl`: 340 repaired records。
- `outputs/20260601-05-contact-degraded-local-edit-core/processed/repaired_candidates_smoke_plus_contact_degraded_local_edit_seed2.jsonl`: 340 repaired records。
- `outputs/20260601-05-contact-degraded-local-edit-core/metrics/contact_degraded_multiseed/summary.json` and CSV。

### 主要结果

- Candidate coverage improved from 5/5/5 to 19/17/17 candidates for seeds 0/1/2。
- Added `tests/test_contact_degraded_generation.py` to cover multi-candidate contact-degraded generation and `max_per_example` behavior。
- `pytest -q`: 18 passed after adding this generator regression test。
- Seed 0 expanded set covers 7 complexes: 1M17, 2BR1, 3ERT, 3G0E, 5P21, 1A4W, 4ERW。
- Seed 0 fallback contact recovery loss: min 0.0313, max 0.2609, mean 0.1119。
- 3-seed expanded fallback metrics:
  - `feedback_learned_editable_contact_policy`: success 0.9236, repair_gain_success 0.2642, mean contact recovery gain 0.0156。
  - `feedback_editable_interaction_only_policy`: success 0.7007, repair_gain_success 0.5676, mean contact recovery gain 0.0487。
  - `feedback_editable_full_policy`: success 1.0, repair_gain_success 0.6047, mean contact recovery gain 0.0627。
  - `feedback_editable_geometry_only_policy`: success 1.0, repair_gain_success 0.0。
  - `feedback_editable_global_only_policy`: success 1.0, repair_gain_success 0.0。
  - `no_feedback_repair`, `identity_failed_candidate`, `rerank_only`, `best_of_n`: repair_gain_success 0.0。
  - `feedback_residual_ensemble_policy`: success 0.9432, repair_gain_success 0.1094, mean contact recovery gain -0.0209。
  - `no_failed_candidate_policy`: repair_gain_success 0.9649, but this starts from reference ligand and remains reference-only oracle sanity。

### 结论

- 扩大候选覆盖后, learned editable-contact positive signal 仍高于 no-feedback / rerank / Best-of-N / geometry-only / global-only, 但从 0.6667 降至 0.2642, 说明上一轮小样本结果偏乐观。
- interaction-only / full editable policies 仍明显强于 geometry-only / global-only, 支持 interaction feedback 是该诊断任务的有效信号。
- 当前结果更可信但也更保守: 有机制正信号, 尚不足 BIBM 级主结果。

### 失败 / 限制 / 下一步

- learned policy 仍是 nearest-neighbor offset-level model。
- candidate 覆盖虽扩展到 53 total candidates, 仍来自 12-complex smoke-plus 小集合。
- key-baseline official PLIP completed: `outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_expanded_key_baselines_plip_gain.jsonl`, 477 records, 0 repaired-side PLIP errors。
- Summary outputs: `outputs/20260601-05-contact-degraded-local-edit-core/metrics/official_eval_smoke_plus_contact_degraded_local_edit_expanded_key_baselines_plip_gain_summary.json`, `outputs/20260601-05-contact-degraded-local-edit-core/tables/official_eval_smoke_plus_contact_degraded_local_edit_expanded_key_baselines_plip_gain_summary.csv`。
- Expanded official PLIP recovery gain:
  - `feedback_learned_editable_contact_policy`: +0.0065, similarity gain -0.0119。
  - `feedback_editable_full_policy`: +0.0301, similarity gain -0.0071。
  - `feedback_editable_interaction_only_policy`: +0.0104, similarity gain -0.0304。
  - `feedback_editable_geometry_only_policy`, `feedback_editable_global_only_policy`, `no_feedback_repair`, `rerank_only`: 0.0。
  - `best_of_n`: -0.0591。
  - `coordinate_rollback`: +0.1864, oracle sanity only。
- 官方 PLIP 正信号比 fallback contact 更弱, 但方向仍支持 interaction/full feedback 优于 no-feedback 和 score/global baselines。

## 2026-06-02 / Contact-degraded same-budget 记录级审计

### 阶段目标

补强 contact-degraded anchor-preserved local-edit 诊断集的 same-budget 证据, 检查三 seed 已评估 repaired records 中每个 baseline 是否覆盖同一 failed-candidate 集合, 是否存在漏评或重复记录导致的记录级预算不公平。

### 代码与配置

- 新增 `scripts/eval/audit_same_budget.py`: 只读取 evaluated repaired JSONL, 汇总每个 baseline 的 unique candidate coverage, missing candidate count, duplicate records, records-per-candidate 和 gain 指标。
- 新增 `tests/test_same_budget_audit.py`: 覆盖 one-record-per-candidate pass, missing baseline record 和 duplicate candidate record fail 两类情况。
- 复用输入:
  - `outputs/20260601-05-contact-degraded-local-edit-core/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed0.jsonl`
  - `outputs/20260601-05-contact-degraded-local-edit-core/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed1.jsonl`
  - `outputs/20260601-05-contact-degraded-local-edit-core/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed2.jsonl`

### 命令

```bash
PYTHONPATH=src pytest -q tests/test_same_budget_audit.py
PYTHONPATH=src python scripts/eval/audit_same_budget.py   --input outputs/20260601-05-contact-degraded-local-edit-core/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed0.jsonl   --input outputs/20260601-05-contact-degraded-local-edit-core/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed1.jsonl   --input outputs/20260601-05-contact-degraded-local-edit-core/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed2.jsonl   --output-json outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/same_budget_audit_smoke_plus_contact_degraded_local_edit_multiseed.json   --output-csv outputs/20260602-01-contact-degraded-budget-and-ablation/tables/same_budget_audit_smoke_plus_contact_degraded_local_edit_multiseed.csv   --name same_budget_audit_smoke_plus_contact_degraded_local_edit_multiseed
PYTHONPATH=src pytest -q tests/test_metrics.py tests/test_official_plip_gain.py tests/test_contact_degraded_generation.py tests/test_same_budget_audit.py
```

### 输出

- `outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/same_budget_audit_smoke_plus_contact_degraded_local_edit_multiseed.json`
- `outputs/20260602-01-contact-degraded-budget-and-ablation/tables/same_budget_audit_smoke_plus_contact_degraded_local_edit_multiseed.csv`

### 主要结果

- `tests/test_same_budget_audit.py`: 2 passed。
- same-budget audit 读取 1113 条 evaluated repaired records。
- 覆盖 21 个 baseline, expected candidates = 53。
- `record_level_all_baselines_same_budget = true`。
- `record_level_same_budget_failures = []`。
- 每个 baseline 均为 53 records / 53 unique candidates / coverage 1.0 / duplicate 0。
- 关键记录级结果示例:
  - `feedback_editable_contact_policy`: repair_gain_success_rate 0.6038, mean_contact_recovery_gain 0.0626。
  - `feedback_editable_full_policy`: repair_gain_success_rate 0.6038, mean_contact_recovery_gain 0.0626。
  - `feedback_editable_interaction_only_policy`: repair_gain_success_rate 0.5660, mean_contact_recovery_gain 0.0488。
  - `feedback_learned_editable_contact_policy`: 仍弱于 full fallback, 需要继续改进。
  - `best_of_n`: repair_gain_success_rate 0.0, mean_contact_recovery_gain -0.0026。
  - `direct_regeneration`: repair_gain_success_rate 0.0566, mean_contact_recovery_gain -0.0245。
  - `coordinate_rollback`: repair_gain_success_rate 0.9623, mean_contact_recovery_gain 0.1177, 仍应标注为 reference-oracle sanity upper bound, 不能作为可部署 baseline。

### 结论

三 seed contact-degraded local-edit 诊断集在记录级 same-budget 上通过: 所有 baseline 对同一 53 个 failed candidates 都有且仅有一条 evaluated repaired record。该审计支持“同一 failed-candidate 集合上的同预算比较”这一论文叙事, 但只证明记录级公平, 不证明 Best-of-N 等方法内部 proposal count 完全等价。

### 失败 / 限制 / 下一步

- 扩展测试 `tests/test_metrics.py tests/test_official_plip_gain.py tests/test_contact_degraded_generation.py tests/test_same_budget_audit.py` 在当前 shell 环境失败, 原因是该环境缺少 `rdkit`; 新增 same-budget 测试本身不依赖 RDKit 且已通过。后续应在 `pfr` conda 环境中复跑相关 RDKit 测试。
- 审计是 record-level, 不含 wall-clock, internal proposal count, sampling attempts 或 GPU/CPU cost; 下一步若要支撑 strict same-budget, 需在 repair 输出中记录每个 baseline 的 internal proposal budget / attempts / selection pool size。
- 下一步继续增强 oracle-free learned editable-contact/diagnostic-feedback policy, 并加入 shuffled-feedback/no-failed-candidate 等更严格消融。

## 2026-06-02 / Internal candidate budget metadata 与 strict same-budget 审计

### 阶段目标

将上一轮 same-budget 审计从 record-level coverage 扩展到 internal candidate/proposal budget 可见层面, 避免把 Best-of-N, direct candidate-pool selection, editable offset search 和 single policy output 混同为严格同预算。

### 代码变更

- `scripts/eval/repair_baselines.py`:
  - 新增 `repair_budget_metadata`。
  - 每条 repaired candidate 记录新增 `record_level_output_budget`, `internal_candidate_budget`, `internal_budget_type`, `candidate_pool_size`, `editable_offset_pool_size`。
  - `best_of_n`, `direct_regeneration`, `feedback_geometry_refinement` 等记录 candidate pool selection budget。
  - `feedback_editable_*` ablation 记录 editable offset selection budget。
  - `feedback_learned_editable_contact_policy`, `feedback_ridge_editable_contact_policy` 等记录 single policy output budget。
- `src/pfr/evaluation/repaired.py`:
  - evaluated repaired records 透传上述 budget 字段。
  - repaired metrics 汇总新增 `mean_internal_candidate_budget` 和 `internal_budget_types`。
- `scripts/eval/audit_same_budget.py`:
  - 审计新增 `internal_budget_metadata_available`, `internal_candidate_budget_values`, `strict_internal_candidate_budget_equal`。
  - 每个 baseline 汇总 internal budget min/max/mean/type。
- `tests/test_same_budget_audit.py`:
  - 新增 internal budget equality 与 inequality 覆盖。

### 命令

```bash
conda run -n pfr env PYTHONPATH=src pytest -q tests/test_same_budget_audit.py tests/test_metrics.py tests/test_official_plip_gain.py tests/test_contact_degraded_generation.py
conda run -n pfr env PYTHONPATH=src python scripts/eval/run_contact_degraded_multiseed.py --seeds 0,1,2 --output-dir outputs/20260601-05-contact-degraded-local-edit-core/metrics/contact_degraded_multiseed
conda run -n pfr env PYTHONPATH=src python scripts/eval/audit_same_budget.py   --input outputs/20260601-05-contact-degraded-local-edit-core/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed0.jsonl   --input outputs/20260601-05-contact-degraded-local-edit-core/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed1.jsonl   --input outputs/20260601-05-contact-degraded-local-edit-core/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed2.jsonl   --output-json outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/same_budget_audit_smoke_plus_contact_degraded_local_edit_multiseed.json   --output-csv outputs/20260602-01-contact-degraded-budget-and-ablation/tables/same_budget_audit_smoke_plus_contact_degraded_local_edit_multiseed.csv   --name same_budget_audit_smoke_plus_contact_degraded_local_edit_multiseed
```

### 输出

- `outputs/20260601-05-contact-degraded-local-edit-core/processed/repaired_candidates_smoke_plus_contact_degraded_local_edit_seed{0,1,2}.jsonl`
- `outputs/20260601-05-contact-degraded-local-edit-core/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed{0,1,2}.jsonl`
- `outputs/20260601-05-contact-degraded-local-edit-core/metrics/contact_degraded_multiseed/summary.json`
- `outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/same_budget_audit_smoke_plus_contact_degraded_local_edit_multiseed.json`
- `outputs/20260602-01-contact-degraded-budget-and-ablation/tables/same_budget_audit_smoke_plus_contact_degraded_local_edit_multiseed.csv`

### 主要结果

- pfr 环境相关测试: 12 passed。
- contact-degraded multiseed 复跑:
  - seed0: 19 failed candidates, 399 repaired records。
  - seed1: 17 failed candidates, 357 repaired records。
  - seed2: 17 failed candidates, 357 repaired records。
  - total: 53 failed candidates, 1113 evaluated repaired records。
- same-budget audit:
  - `record_level_all_baselines_same_budget = true`。
  - `record_level_same_budget_failures = []`。
  - `internal_budget_metadata_available = true`。
  - `internal_candidate_budget_values = [1.0, 10.0, 16.1132]`。
  - `strict_internal_candidate_budget_equal = false`。
- 代表性 internal budget:
  - `no_feedback_repair`, `rerank_only`: 1.0, single failed candidate。
  - `feedback_learned_editable_contact_policy`: 1.0, single policy output, repair_gain_success_rate 0.2642。
  - `feedback_editable_contact_policy`: 10.0, editable offset selection, repair_gain_success_rate 0.6038。
  - `best_of_n`: 16.1132, candidate pool selection, repair_gain_success_rate 0.0。
  - `direct_regeneration`: 16.1132, candidate pool index selection, repair_gain_success_rate 0.0566。
  - `coordinate_rollback`: 1.0, reference/rule copy, repair_gain_success_rate 0.9623, oracle upper bound。

### 结论

记录级 same-budget 公平性成立: 所有 baseline 对同一 53 个 failed candidates 各输出一条 evaluated repaired record。严格 internal candidate budget 不成立: candidate-pool / editable-search 方法使用的内部候选预算高于 single policy output 和 no-feedback/rerank。论文中必须分别报告 record-level same-budget 与 internal candidate budget, 不能把当前结果表述为严格同 proposal budget。

### 失败 / 限制 / 下一步

- 这是重要负面/限制结果, 但对论文有价值: 它让 same-budget 声明更可审计, 防止过度声称。
- 当前 learned editable-contact policy 在 single policy output budget 下有 repair-gain 正信号, 但弱于 full editable-search fallback; 下一步应优先增强 learned policy, 或设计 equalized internal budget 版本, 例如限制所有方法为 1-shot, 或给 learned policy 同等 10/16 candidate proposal budget 后再比较。
- 还需将 internal budget metadata 接入官方 PLIP/Vina summary 或最终表格, 使官方 recovery gain 也能按预算类型分层解释。

## 2026-06-02 / Equalized learned editable-contact budget 与审计 blocker 修复

### 阶段目标

针对 strict internal budget 审计发现的问题, 实现一个与 editable-search 同为 10 internal candidates 的 learned editable-contact policy, 并修复独立审查发现的 cache 串用和 strict budget 误判 blocker, 然后重跑 contact-degraded 三 seed fallback 对照。

### 代码变更

- `scripts/eval/repair_baselines.py`:
  - 新增 `feedback_budgeted_learned_editable_contact_policy`: 先预测 learned editable-contact offset, 再以该 offset 为中心生成 10 个局部候选并用 editable-contact score 选择。
  - geometry pseudo-label cache 与 editable-contact pseudo-label cache 加入命名空间, 避免 `(candidate_id, seed)` / `(complex_id, seed)` 串用不同语义 target。
  - repaired records 透传 `seed`。
  - 修正 internal budget metadata: `no_failed_candidate_policy` 为 10 editable offsets, `feedback_residual_ensemble_policy` 为 7 residual offsets, `feedback_anchor_alignment_policy` 为 anchor-alignment selection, `feedback_budgeted_learned_editable_contact_policy` 为 10 editable-offset selection。
- `src/pfr/evaluation/repaired.py`:
  - 透传 `seed`, `protein_path`, `reference_ligand_path` 和 internal budget 字段, 以支持官方评估和多 seed 审计。
- `scripts/eval/audit_same_budget.py`:
  - `strict_internal_candidate_budget_equal` 改为基于所有记录的 internal budget value set, 不再只比较 baseline mean。
  - 缺失 internal metadata 时 strict pass 为 false。
  - seed path inference 支持 `seed0`, `seed_1`, `seed-2`, `seed.3`。
- `tests/test_same_budget_audit.py`:
  - 增加 mean-equality false positive, missing metadata, seed separator 测试。

### 命令

```bash
conda run -n pfr env PYTHONPATH=src pytest -q tests/test_same_budget_audit.py tests/test_metrics.py tests/test_official_plip_gain.py tests/test_contact_degraded_generation.py
conda run -n pfr env PYTHONPATH=src python scripts/eval/run_contact_degraded_multiseed.py --seeds 0,1,2 --output-dir outputs/20260601-05-contact-degraded-local-edit-core/metrics/contact_degraded_multiseed
conda run -n pfr env PYTHONPATH=src python scripts/eval/audit_same_budget.py   --input outputs/20260601-05-contact-degraded-local-edit-core/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed0.jsonl   --input outputs/20260601-05-contact-degraded-local-edit-core/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed1.jsonl   --input outputs/20260601-05-contact-degraded-local-edit-core/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed2.jsonl   --output-json outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/same_budget_audit_smoke_plus_contact_degraded_local_edit_multiseed.json   --output-csv outputs/20260602-01-contact-degraded-budget-and-ablation/tables/same_budget_audit_smoke_plus_contact_degraded_local_edit_multiseed.csv   --name same_budget_audit_smoke_plus_contact_degraded_local_edit_multiseed
```

### 输出

- `outputs/20260601-05-contact-degraded-local-edit-core/metrics/contact_degraded_multiseed/summary.json`
- `outputs/20260601-05-contact-degraded-local-edit-core/metrics/contact_degraded_multiseed/summary.csv`
- `outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/same_budget_audit_smoke_plus_contact_degraded_local_edit_multiseed.json`
- `outputs/20260602-01-contact-degraded-budget-and-ablation/tables/same_budget_audit_smoke_plus_contact_degraded_local_edit_multiseed.csv`

### 主要结果

- 回归测试: 15 passed。
- contact-degraded 三 seed: 53 failed candidates, 22 baselines, 1166 evaluated repaired records。
- record-level same-budget:
  - `record_level_all_baselines_same_budget = true`。
  - `record_level_same_budget_failures = []`。
- internal budget:
  - `internal_budget_metadata_available = true`。
  - `internal_candidate_budget_values = [1.0, 7.0, 10.0, 16.0, 17.0]`。
  - `strict_internal_candidate_budget_equal = false`。
- fallback repair-gain 结果:
  - `no_feedback_repair`: gain_success 0.0, contact_recovery_gain 0.0, budget 1。
  - `rerank_only`: gain_success 0.0, contact_recovery_gain 0.0, budget 1。
  - `feedback_learned_editable_contact_policy`: gain_success 0.2642, contact_recovery_gain 0.0156, budget 1。
  - `feedback_budgeted_learned_editable_contact_policy`: gain_success 0.3189, contact_recovery_gain 0.0330, budget 10。
  - `feedback_editable_contact_policy` / `feedback_editable_full_policy`: gain_success 0.6047, contact_recovery_gain 0.0627, budget 10。
  - `best_of_n`: gain_success 0.0, contact_recovery_gain -0.0027, budget 16-17。
  - `direct_regeneration`: gain_success 0.0588, contact_recovery_gain -0.0243, budget 16-17。
  - geometry learned/kernel/kNN/residual policies after cache namespace fix remain weak or negative on contact-degraded repair gain。

### 结论

Budgeted learned editable-contact policy 在相同 10-candidate editable-offset budget 下较 1-shot learned policy 有明显提升, 但仍显著弱于 handcrafted/full editable-contact search fallback。该结果支持 “learned diagnostic-feedback policy 有初步正信号, 但当前不足以作为最终 BIBM 级方法结论”。same-budget 叙事必须区分 record-level output budget, editable-offset budget, residual-offset budget 和 candidate-pool budget。

### 失败 / 限制 / 下一步

- 独立审查发现的 cache 串用是 blocker, 已修复并重跑；修复后 geometry learned/kernel/kNN/residual 结果变弱, 说明此前部分数值可能被错误 cache 污染, 旧结果不应再引用。
- strict internal budget 仍不成立, 因 baseline 预算类型不同。最终论文应按 budget type 分层或构造完全 equalized budget 子表。
- 已生成 `outputs/20260602-01-contact-degraded-budget-and-ablation/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed0_key_equalized_budget.jsonl`, 并启动 seed0 key-baseline 官方 PLIP/Vina 对照；该官方结果完成后需追加记录, 当前不要提前声称官方 interaction gain 成立。

## 2026-06-02 / Seed0 key-baseline official PLIP/Vina equalized-budget 对照

### 阶段目标

在修复 `eval_repaired` 路径透传后, 对 contact-degraded seed0 的 key baselines 跑官方 PLIP/Vina, 检查 fallback/contact 指标中的 repair gain 是否在 official PLIP interaction recovery 上也有支持。

### 代码与数据

- `src/pfr/evaluation/repaired.py`: 透传 `protein_path`, `reference_ligand_path`, `seed` 和 internal budget 字段。
- `scripts/eval/eval_official_tools.py`: 官方评估输出透传 internal budget 字段。
- `scripts/eval/summarize_official_eval.py`: 官方汇总增加 `mean_internal_candidate_budget` 与 `internal_budget_types`。
- 输入子集: `outputs/20260602-01-contact-degraded-budget-and-ablation/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed0_key_equalized_budget.jsonl`。
- 子集规模: 9 key baselines x 19 seed0 failed candidates = 171 records。

### 命令

```bash
conda run -n pfr-eval-tools env PYTHONPATH=src python scripts/eval/eval_official_tools.py   --repaired-candidates outputs/20260602-01-contact-degraded-budget-and-ablation/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_seed0_key_equalized_budget.jsonl   --output outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_seed0_key_equalized_budget_plip_vina.jsonl   --tools plip,vina   --keep-work-dir outputs/20260602-01-contact-degraded-budget-and-ablation/work/official_eval/contact_degraded_seed0_key_equalized_budget
conda run -n pfr env PYTHONPATH=src python scripts/eval/summarize_official_eval.py   --input outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_seed0_key_equalized_budget_plip_vina.jsonl   --output-json outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_seed0_key_equalized_budget_plip_vina_summary.json   --output-csv outputs/20260602-01-contact-degraded-budget-and-ablation/tables/official_eval_smoke_plus_contact_degraded_local_edit_seed0_key_equalized_budget_plip_vina_summary.csv   --name official_eval_smoke_plus_contact_degraded_local_edit_seed0_key_equalized_budget_plip_vina_summary
```

### 输出

- `outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_seed0_key_equalized_budget_plip_vina.jsonl`
- `outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_seed0_key_equalized_budget_plip_vina_summary.json`
- `outputs/20260602-01-contact-degraded-budget-and-ablation/tables/official_eval_smoke_plus_contact_degraded_local_edit_seed0_key_equalized_budget_plip_vina_summary.csv`

### 主要结果

- 171 official records。
- PLIP: 171/171 available, 0 error。
- Vina score-only: 171/171 available, 0 error。
- Official PLIP interaction recovery gain:
  - `no_feedback_repair`: 0.0。
  - `rerank_only`: 0.0。
  - `feedback_learned_editable_contact_policy`: +0.0093, budget 1。
  - `feedback_budgeted_learned_editable_contact_policy`: +0.0146, budget 10。
  - `feedback_editable_contact_policy` / `feedback_editable_full_policy`: +0.0254, budget 10。
  - `feedback_ridge_editable_contact_policy`: +0.0053, budget 1。
  - `best_of_n`: -0.0217, budget 16.1 mean。
  - `direct_regeneration`: -0.0970, budget 16.1 mean。
- Vina score-only energy 不应当解释为 repair success; no-feedback/rerank 的 Vina 均值约 -6.959, editable-search 约 -7.041, budgeted learned 约 -6.917, direct regeneration 约 -5.099。

### 结论

官方 PLIP seed0 key-baseline 对照支持一个弱正向结论: learned/budgeted learned/editable-search feedback policies 在 interaction recovery gain 上高于 no-feedback/rerank, Best-of-N 和 direct regeneration 没有恢复 interaction。这个信号与 fallback/contact 指标方向一致, 但幅度较小, 且目前只覆盖 seed0 key baselines, 不能作为最终 BIBM 级结论。

### 失败 / 限制 / 下一步

- 这是 seed0 key-baseline official check, 不是 full 3-seed official result。
- PLIP recovery gain 幅度小: budgeted learned +0.0146, editable-search +0.0254。需要 3-seed key-baseline official PLIP/Vina 或更大 contact-degraded set 验证稳定性。
- Vina 是 score-only, 只能作为补充描述, 不能作为成功判据。
- 下一步应扩展 key-baseline official PLIP/Vina 到 seeds 0/1/2, 并继续改进 learned policy, 目标是在官方 PLIP recovery gain 上接近 editable-search fallback。

## 2026-06-02 / Official PLIP/Vina multiseed 环境误用记录

### 阶段目标

将 seed0 key-baseline official PLIP/Vina 对照扩展到 contact-degraded seeds 0/1/2, 覆盖 9 key baselines x 53 failed candidates = 477 records。

### 失败尝试

首次三种子 official eval 错误地使用了 `pfr` 环境运行 `scripts/eval/eval_official_tools.py`。该命令写出了 477 行 JSONL, 但 summary 显示所有 baseline 的 PLIP/Vina 指标均为 `null`。进一步检查原始错误字段后确认:

- `plip_error`: `plip_cli_missing` x 477。
- `vina_error`: `missing_cli:mk_prepare_ligand.py,mk_prepare_receptor.py,vina` x 477。
- 输入路径字段如 `protein_path`, `reference_ligand_path`, `source_failed_ligand_path`, `repaired_ligand_path` 存在, 因此问题不是路径透传, 而是 official CLI 环境错误。

### 原因

项目采用双环境分工: `pfr` 用于 RDKit-first pipeline 和 summary; `pfr-eval-tools` 才包含 `plip`, `vina`, `mk_prepare_ligand.py`, `mk_prepare_receptor.py`。seed0 成功记录中的命令也使用了 `conda run -n pfr-eval-tools ... eval_official_tools.py`, 但三种子扩展时误用了 `pfr`。

### 修正动作

已在 `docs/report/20260601-03-optional-tool-notes-report.md` 增加 official evaluation environment pitfalls, 明确:

- `eval_official_tools.py` 必须用 `pfr-eval-tools`。
- `summarize_official_eval.py` 可用 `pfr`。
- official 输出不能只看行数, 必须检查 `plip_error` 和 `vina_error`。
- 出现 `plip_cli_missing` 或 `missing_cli:mk_prepare_ligand.py,mk_prepare_receptor.py,vina` 时, 该输出不能作为 official result 报告。

### 附带工具坑

本轮还重复触发了 Claude `Read` 工具的 `pages: ""` 错误。`pages` 只用于 PDF, 普通文本文件读取时必须省略。该注意事项也已写入 `docs/report/20260601-03-optional-tool-notes-report.md`。

### 当前状态

已用正确环境重新启动三种子 official PLIP/Vina:

```bash
conda run -n pfr-eval-tools env PYTHONPATH=src python scripts/eval/eval_official_tools.py \
  --repaired-candidates outputs/20260602-01-contact-degraded-budget-and-ablation/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_multiseed_key_equalized_budget.jsonl \
  --output outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_key_equalized_budget_plip_vina.jsonl \
  --tools plip,vina \
  --keep-work-dir outputs/20260602-01-contact-degraded-budget-and-ablation/work/official_eval/contact_degraded_multiseed_key_equalized_budget
```

正确环境重跑完成前, 不得引用此前 477-row all-error 文件作为三种子 official evidence。

## 2026-06-02 / Contact-degraded 三种子 key-baseline official PLIP/Vina

### 阶段目标

将 seed0 key-baseline official PLIP/Vina 对照扩展到 seeds 0/1/2, 验证 contact-degraded anchor-preserved local-edit 诊断集上的 feedback repair 正信号是否跨 seed 保持。

### 输入与配置

- 输入: `outputs/20260602-01-contact-degraded-budget-and-ablation/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_multiseed_key_equalized_budget.jsonl`。
- 输出: `outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_key_equalized_budget_plip_vina.jsonl`。
- Summary JSON: `outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_key_equalized_budget_plip_vina_summary.json`。
- Summary CSV: `outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_key_equalized_budget_plip_vina_summary.csv`。
- 覆盖: 9 key baselines x 53 failed candidates = 477 records。
- 正确运行环境: `pfr-eval-tools` for `eval_official_tools.py`; `pfr` for `summarize_official_eval.py`。

### 命令

```bash
conda run -n pfr-eval-tools env PYTHONPATH=src python scripts/eval/eval_official_tools.py \
  --repaired-candidates outputs/20260602-01-contact-degraded-budget-and-ablation/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_multiseed_key_equalized_budget.jsonl \
  --output outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_key_equalized_budget_plip_vina.jsonl \
  --tools plip,vina \
  --keep-work-dir outputs/20260602-01-contact-degraded-budget-and-ablation/work/official_eval/contact_degraded_multiseed_key_equalized_budget
conda run -n pfr env PYTHONPATH=src python scripts/eval/summarize_official_eval.py \
  --input outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_key_equalized_budget_plip_vina.jsonl \
  --output-json outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_key_equalized_budget_plip_vina_summary.json \
  --output-csv outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_key_equalized_budget_plip_vina_summary.csv \
  --name contact_degraded_multiseed_key_equalized_budget_plip_vina
```

### 质量检查

- 输出记录数: 477。
- `plip_error`: `None` x 477。
- `vina_error`: `None` x 477。
- `plip_available`: `True` x 477。
- `vina_available`: `True` x 477。

### 主要结果

| Baseline | Records | Internal budget | Official PLIP recovery gain | Official PLIP similarity gain | Vina score-only |
|---|---:|---:|---:|---:|---:|
| `feedback_editable_contact_policy` | 53 | 10.0 | +0.0301 | -0.0071 | -6.9934 |
| `feedback_editable_full_policy` | 53 | 10.0 | +0.0301 | -0.0071 | -6.9934 |
| `feedback_budgeted_learned_editable_contact_policy` | 53 | 10.0 | +0.0099 | -0.0083 | -6.9294 |
| `feedback_ridge_editable_contact_policy` | 53 | 1.0 | +0.0076 | +0.0083 | -6.5593 |
| `feedback_learned_editable_contact_policy` | 53 | 1.0 | +0.0065 | -0.0119 | -6.5991 |
| `no_feedback_repair` | 53 | 1.0 | 0.0000 | 0.0000 | -6.9855 |
| `rerank_only` | 53 | 1.0 | 0.0000 | 0.0000 | -6.9855 |
| `best_of_n` | 53 | 16.1 | -0.0591 | -0.0553 | -6.8985 |
| `direct_regeneration` | 53 | 16.1 | -0.1441 | -0.1900 | -4.7090 |

### 结论

三种子 official PLIP 结果支持一个保守结论: feedback-conditioned editable-contact/full repair 在 interaction recovery gain 上优于 no-feedback/rerank, 并且 Best-of-N/direct regeneration 在该 contact-degraded diagnostic set 上平均为负。learned/budgeted learned policy 有弱正信号, 但仍明显弱于 editable-search fallback。

### 限制与下一步

- 这仍是 key-baseline diagnostic subset, 不是完整 BIBM 级最终实验。
- strict internal candidate budget 不相等: budget=1, budget=10 和 budget≈16.1 混在同一表中, 最终论文应分层报告或构造 budget=1 / budget=10 子表。
- Vina 是 score-only, 不作为 repair success 判据；例如 no-feedback/rerank 的 Vina 均值接近 editable-contact, 但 PLIP recovery gain 为 0。
- PLIP similarity gain 对多数 feedback policies 仍略负, 说明 recovery gain 改善不等价于整体 interaction fingerprint 更相似。
- 下一步应补 budget=1 / budget=10 公平表、shuffled-feedback 消融、进一步增强 oracle-free learned editable-contact policy, 并继续把结果写入论文初稿。

## 2026-06-02 / Shuffled-feedback 消融: learned editable-contact policies

### 阶段目标

验证 contact-degraded local-edit 诊断集中 learned/ridge editable-contact policies 的收益是否来自具体 feedback 内容, 而不是仅来自 policy 结构或 offset 搜索预算。

### 代码与配置

- `scripts/eval/repair_baselines.py`: 新增确定性 shuffled feedback mapping 和三个 shuffled baselines:
  - `feedback_learned_editable_contact_shuffled_policy`。
  - `feedback_budgeted_learned_editable_contact_shuffled_policy`。
  - `feedback_ridge_editable_contact_shuffled_policy`。
- `scripts/eval/run_contact_degraded_multiseed.py`: 将 shuffled baselines 加入 contact-degraded multiseed baseline 列表。
- cache namespace 已按 baseline 隔离, 避免 normal/shuffled learned/ridge training cache 串用。

### 验证

```bash
python -m py_compile scripts/eval/repair_baselines.py scripts/eval/run_contact_degraded_multiseed.py
conda run -n pfr env PYTHONPATH=src pytest -q tests/test_same_budget_audit.py tests/test_metrics.py tests/test_contact_degraded_generation.py
```

结果: 13 passed。seed0 probe 生成 57 repaired records, 每个 shuffled baseline 19 条。

### Fallback 评估输出

- `outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/contact_degraded_shuffled_ablation_summary.json`。
- `outputs/20260602-01-contact-degraded-budget-and-ablation/tables/contact_degraded_shuffled_ablation_summary.csv`。

三种子 fallback 对比:

| Baseline | gain_success | contact recovery gain | contact similarity gain |
|---|---:|---:|---:|
| normal learned | 0.2642 | +0.0156 | +0.0029 |
| shuffled learned | 0.0568 | +0.0024 | -0.0067 |
| normal budgeted learned | 0.3189 | +0.0330 | +0.0274 |
| shuffled budgeted learned | 0.1723 | +0.0277 | +0.0217 |
| normal ridge | 0.2116 | +0.0178 | -0.0063 |
| shuffled ridge | 0.1331 | +0.0080 | -0.0050 |

Fallback 指标显示 shuffled-feedback 明显削弱 learned/ridge policies, 但 budgeted shuffled 仍有一定收益, 说明 candidate/offset search 本身也贡献了部分恢复。

### Official PLIP/Vina 评估

- 输入: `outputs/20260602-01-contact-degraded-budget-and-ablation/processed/evaluated_repaired_smoke_plus_contact_degraded_local_edit_multiseed_shuffled_ablation.jsonl`。
- Official 输出: `outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_shuffled_ablation_plip_vina.jsonl`。
- Summary: `outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_shuffled_ablation_plip_vina_summary.json`。
- 对照表: `outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_contact_degraded_multiseed_shuffled_feedback_comparison.json`, `outputs/20260602-01-contact-degraded-budget-and-ablation/tables/official_eval_contact_degraded_multiseed_shuffled_feedback_comparison.csv`。
- 质量检查: 159 records, `plip_error=None` x 159, `vina_error=None` x 159。

Official PLIP recovery gain 对比:

| Baseline | Budget | PLIP recovery gain | PLIP similarity gain | Vina score-only |
|---|---:|---:|---:|---:|
| no-feedback | 1 | 0.0000 | 0.0000 | -6.9855 |
| normal learned | 1 | +0.0065 | -0.0119 | -6.5991 |
| shuffled learned | 1 | +0.0007 | -0.0188 | -6.9422 |
| normal ridge | 1 | +0.0076 | +0.0083 | -6.5593 |
| shuffled ridge | 1 | -0.0053 | -0.0251 | -6.8626 |
| normal budgeted learned | 10 | +0.0099 | -0.0083 | -6.9294 |
| shuffled budgeted learned | 10 | -0.0012 | -0.0205 | -6.9473 |
| editable-search reference | 10 | +0.0301 | -0.0071 | -6.9934 |

### 结论

Shuffled-feedback official 消融支持一个更强但仍保守的机制结论: 具体 diagnostic feedback 内容对 learned/ridge editable-contact repair 的 official interaction recovery 有贡献。正常反馈在 budget=1 和 budget=10 下均优于 shuffled feedback, 而 shuffled baselines 的 official PLIP recovery gain 接近 0 或为负。

### 限制与下一步

- 信号仍小: normal learned/ridge official recovery gain 约 +0.0065 到 +0.0076, budgeted learned +0.0099。
- `feedback_editable_contact_policy` / full fallback 仍强于 learned policies, 表明当前 learned policy 不是最终 publication-level model。
- Vina score-only 与 PLIP recovery 不一致, 继续只作为补充描述。
- 下一步应把 budget-fair 和 shuffled 消融写入 paper draft 的 Results/Ablation/Limitation, 并继续改进 oracle-free learned policy。

## 2026-06-02 / Classified editable-contact policy 改进尝试

### 阶段目标

改进 oracle-free learned editable-contact policy, 缩小其与 budget=10 editable-search fallback 的差距。Explore 子代理建议优先把连续 offset 最近邻/回归改为 10 个 fixed editable offsets 的离散分类, 因为当前 editable-search fallback 的动作空间就是这 10 个 offsets。

### 代码改动

- `scripts/eval/repair_baselines.py`:
  - `FAILURE_TYPES` 增加 `contact_degraded_local_edit`。
  - `feedback_features` 增加 oracle-free contact-degradation diagnostics: contact recovery loss, contact similarity loss, failed contact recovery, degradation rank, rotatable bonds, QED。
  - 新增 `feedback_classified_editable_contact_policy`, 用 leave-one-complex nearest-neighbor label classification 预测 10 个 editable offsets 中的一个。
  - label training cache 按 baseline namespace 隔离。
- `scripts/eval/run_contact_degraded_multiseed.py`: baseline 列表加入 `feedback_classified_editable_contact_policy`。

### 验证与输出

- seed0 probe: 19 repaired records。
- 三种子 fallback summary: `outputs/20260602-02-contact-degraded-policy-variants/metrics/contact_degraded_classified_policy_summary.json`。
- Official PLIP/Vina output: `outputs/20260602-02-contact-degraded-policy-variants/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_classified_policy_plip_vina.jsonl`。
- Official summary: `outputs/20260602-02-contact-degraded-policy-variants/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_classified_policy_plip_vina_summary.json`。
- Combined comparison: `outputs/20260602-02-contact-degraded-policy-variants/metrics/official_eval_contact_degraded_multiseed_learned_policy_comparison.json`, `outputs/20260602-02-contact-degraded-policy-variants/tables/official_eval_contact_degraded_multiseed_learned_policy_comparison.csv`。

Official quality check: 53 records, `plip_error=None` x 53, `vina_error=None` x 53。

### 结果

Fallback metrics:

- `feedback_classified_editable_contact_policy`: gain_success 0.2466, contact recovery gain +0.0221, contact similarity gain +0.0006。
- Normal learned: gain_success 0.2642, contact recovery gain +0.0156。
- Ridge: gain_success 0.2116, contact recovery gain +0.0178。
- Budgeted learned: gain_success 0.3189, contact recovery gain +0.0330。
- Editable-search/full fallback: gain_success 0.6047, contact recovery gain +0.0627。

Official PLIP recovery gain:

| Baseline | Budget | PLIP recovery gain | PLIP similarity gain |
|---|---:|---:|---:|
| no-feedback | 1 | 0.0000 | 0.0000 |
| shuffled learned | 1 | +0.0007 | -0.0188 |
| shuffled ridge | 1 | -0.0053 | -0.0251 |
| learned | 1 | +0.0065 | -0.0119 |
| ridge | 1 | +0.0076 | +0.0083 |
| classified | 1 | +0.0090 | -0.0108 |
| budgeted learned | 10 | +0.0099 | -0.0083 |
| editable-search/full | 10 | +0.0301 | -0.0071 |

### 结论

Classified policy 是一个有效但有限的小改进: 在 budget=1 official PLIP recovery gain 上略高于 learned/ridge, 且明显高于 shuffled controls 和 no-feedback。但它没有解决核心弱点: learned policy 仍远弱于 budget=10 editable-search fallback, 且 fallback gain_success 不超过原 learned。

### 下一步

- 若继续改 learned policy, 应考虑 top-k classified + budgeted fixed pool 或更丰富的 pocket/contact directional features。
- 论文中应将 classified policy 报为 incremental learned baseline, 不能声称已达到 publication-level learned repair model。

## 2026-06-02 / Paper-ready contact-degraded 表格与案例素材

### 阶段目标

把 contact-degraded local-edit 诊断链条中已经完成的三种子 official PLIP/Vina、budget-fair、shuffled-feedback 和 classified learned policy 结果整理成论文可引用的表格与案例素材, 减少后续 paper draft 中手工复制数字导致的错误。

### 输入来源

- 主 official key-baseline summary: `outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_key_equalized_budget_plip_vina_summary.json`。
- shuffled-feedback official summary: `outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_shuffled_ablation_plip_vina_summary.json`。
- classified policy official summary: `outputs/20260602-02-contact-degraded-policy-variants/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_classified_policy_plip_vina_summary.json`。
- learned policy 合并对照: `outputs/20260602-02-contact-degraded-policy-variants/metrics/official_eval_contact_degraded_multiseed_learned_policy_comparison.json`。
- case study official rows: `outputs/20260602-01-contact-degraded-budget-and-ablation/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_key_equalized_budget_plip_vina.jsonl` 和 `outputs/20260602-02-contact-degraded-policy-variants/metrics/official_eval_smoke_plus_contact_degraded_local_edit_multiseed_classified_policy_plip_vina.jsonl`。

### 新增脚本

- `scripts/analysis/write_paper_tables.py`: 从 JSON summary 自动生成 Markdown/CSV 论文表格, 避免手工抄数。

### 输出

- 主结果表:
  - `outputs/20260602-03-paper-ready-contact-degraded-reporting/tables/paper_contact_degraded_main_results.md`。
  - `outputs/20260602-03-paper-ready-contact-degraded-reporting/tables/paper_contact_degraded_main_results.csv`。
- feedback 消融表:
  - `outputs/20260602-03-paper-ready-contact-degraded-reporting/tables/paper_contact_degraded_feedback_ablation.md`。
  - `outputs/20260602-03-paper-ready-contact-degraded-reporting/tables/paper_contact_degraded_feedback_ablation.csv`。
- 代表性案例:
  - `outputs/20260602-03-paper-ready-contact-degraded-reporting/tables/paper_case_contact_degraded_3ert_seed2.md`。
  - `outputs/20260602-03-paper-ready-contact-degraded-reporting/metrics/paper_case_contact_degraded_3ert_seed2.json`。

### 表格内容摘要

主结果表显示:

- budget=1:
  - no-feedback: official PLIP recovery gain 0.0000。
  - rerank-only: 0.0000。
  - classified feedback: +0.0090。
- budget=10:
  - budgeted learned feedback: +0.0099。
  - editable-contact search: +0.0301。
- higher-budget references:
  - Best-of-N: -0.0591, mean internal budget 16.1。
  - direct regeneration: -0.1441, mean internal budget 16.1。

Feedback 消融表显示:

- shuffled learned +0.0007 vs learned +0.0065。
- shuffled ridge -0.0053 vs ridge +0.0076。
- shuffled budgeted learned -0.0012 vs budgeted learned +0.0099。

### Case study

选择 `3ert_contact_degraded_local_edit_6_0`, seed 2。该 case 的 reference / failed / repaired PLIP interaction counts 为:

- no-feedback: 10 / 8 / 8, recovery gain 0.0000。
- rerank-only: 10 / 8 / 8, recovery gain 0.0000。
- classified feedback: 10 / 8 / 9, recovery gain +0.1250。
- learned feedback: 10 / 8 / 9, recovery gain +0.1250。
- budgeted learned feedback: 10 / 8 / 9, recovery gain +0.1250。
- editable-contact/full search: 10 / 8 / 9, recovery gain +0.1250。

该案例可用于论文 case study, 展示 failed candidate 丢失 interaction 后, feedback-conditioned repair 能恢复一个 PLIP interaction, 而 no-feedback/rerank 原地不动没有 recovery gain。

### 限制

- 这些表格和案例仍来自 contact-degraded diagnostic subset, 不是 benchmark-scale 结果。
- classified / learned policy 的平均 official gain 仍小, 不能声称已经达到 publication-level learned model。
- case study 是单例展示, 不能替代三种子统计结论。
- Vina score-only 仍只作为补充列, 不作为 repair success 判据。

### 下一步

继续将 `docs/report/20260602-02-paper-draft-report.md` 补成完整 BIBM 风格初稿结构: Abstract, Introduction, Related Work, Method, Experiments, Results, Ablation, Case Study, Limitations, Ethics/Reproducibility。

## 2026-06-02 / Directional classified policy 负结果

### 阶段目标

尝试增强 budget=1 oracle-free classified editable-contact policy。思路是在原离散 offset 分类特征中加入 failed editable centroid 到最近蛋白原子的方向和距离, 希望提供 pocket-side directional signal。

### 代码改动

- `scripts/eval/repair_baselines.py`:
  - 引入 `parse_pdb_atom_coords`。
  - 新增 `editable_pocket_direction_features(candidate)`。
  - 新增 `feedback_directional_classified_editable_contact_policy`。
  - 修正为方向特征只对 directional policy 生效, 不污染原 `feedback_classified_editable_contact_policy`。
- `scripts/eval/run_contact_degraded_multiseed.py`: baseline 列表加入 directional classified policy。

### 验证

seed0 probe 成功生成 38 records, 包含普通 classified 和 directional classified 各 19 条。directional policy 的 offset 选择确实与普通 classified 不同。

### 三种子 fallback 结果

输出: `outputs/20260602-02-contact-degraded-policy-variants/metrics/contact_degraded_directional_classified_policy_summary.json`。

- `feedback_directional_classified_editable_contact_policy`: gain_success 0.1878, contact recovery gain -0.0039, contact similarity gain -0.0437, clash_count_reduction -0.4912。
- 对照 `feedback_classified_editable_contact_policy`: gain_success 0.2466, contact recovery gain +0.0221, contact similarity gain +0.0006。
- 对照 `feedback_learned_editable_contact_policy`: gain_success 0.2642, contact recovery gain +0.0156。

### 结论

Directional features 这个最小实现是负结果。它降低了 fallback contact recovery 和 similarity, 且引入更多 clash degradation。原因可能是最近蛋白原子方向过于局部/噪声大, 与 10 个 fixed offset 的真实 contact-recovery target 不一致。

### 决策

不继续跑 official PLIP/Vina, 避免把明显 fallback 负结果扩展为昂贵 official run。主结论仍使用普通 classified / learned / budgeted learned / editable-search 结果。该负结果保留在实验日志中, 作为 learned policy 改进方向的排除项。


## 2026-06-02 / Directional learned editable-contact policy 负结果

### 阶段目标

在 directional classified 负结果后, 检查同一 pocket-side directional signal 是否能帮助 nearest-neighbor learned editable-contact policy。新增 `feedback_directional_learned_editable_contact_policy`, 在 learned editable-contact 训练和预测特征中可选加入 `editable_pocket_direction_features(candidate)`, 但保持普通 learned/classified/ridge baseline 默认路径不变。

### 代码改动

- `scripts/eval/repair_baselines.py`:
  - `build_editable_contact_training_rows(...)` 新增 `include_direction` 参数。
  - `learned_editable_contact_offset(...)` 新增 `include_direction` 参数, 并用 baseline namespace 隔离 cache。
  - `repair_with_learned_editable_contact_policy(...)` 新增 `include_direction` 参数。
  - `repair_candidate(...)` 新增 `feedback_directional_learned_editable_contact_policy` 分支。
- `scripts/eval/run_contact_degraded_multiseed.py`: baseline 列表加入 `feedback_directional_learned_editable_contact_policy`。
- 语法验证: `python -m py_compile scripts/eval/repair_baselines.py scripts/eval/run_contact_degraded_multiseed.py` 通过。

### 运行与输出

直接使用 `pfr` 环境 Python 运行三 seed fallback 筛选, 复用已有 contact-degraded local-edit failed candidates 和 feedback:

- seed0: 19 failed candidates -> 19 repaired records。
- seed1: 17 failed candidates -> 17 repaired records。
- seed2: 17 failed candidates -> 17 repaired records。

主要输出:

- `outputs/20260602-02-contact-degraded-policy-variants/metrics/contact_degraded_directional_learned_policy_summary.json`
- `outputs/20260602-02-contact-degraded-policy-variants/metrics/contact_degraded_directional_learned_policy/seed0.json`
- `outputs/20260602-02-contact-degraded-policy-variants/metrics/contact_degraded_directional_learned_policy/seed1.json`
- `outputs/20260602-02-contact-degraded-policy-variants/metrics/contact_degraded_directional_learned_policy/seed2.json`
- `outputs/20260602-02-contact-degraded-policy-variants/processed/repaired_candidates_contact_degraded_directional_learned_seed0.jsonl`
- `outputs/20260602-02-contact-degraded-policy-variants/processed/repaired_candidates_contact_degraded_directional_learned_seed1.jsonl`
- `outputs/20260602-02-contact-degraded-policy-variants/processed/repaired_candidates_contact_degraded_directional_learned_seed2.jsonl`
- `outputs/20260602-02-contact-degraded-policy-variants/processed/evaluated_repaired_contact_degraded_directional_learned_seed0.jsonl`
- `outputs/20260602-02-contact-degraded-policy-variants/processed/evaluated_repaired_contact_degraded_directional_learned_seed1.jsonl`
- `outputs/20260602-02-contact-degraded-policy-variants/processed/evaluated_repaired_contact_degraded_directional_learned_seed2.jsonl`

### 三种子 fallback 结果

`feedback_directional_learned_editable_contact_policy`:

- total repaired: 53。
- mean repaired success rate: 0.8865。
- mean repair gain success rate: 0.1878。
- mean contact recovery gain: -0.0039。
- mean contact similarity gain: -0.0437。
- mean anchor error reduction: 0.0000。
- mean clash count reduction: -0.4912。

对照当前已有结果:

- 普通 learned editable-contact: gain_success 0.2642, fallback contact recovery gain +0.0156。
- 普通 classified editable-contact: gain_success 0.2466, fallback contact recovery gain +0.0221。
- directional classified: gain_success 0.1878, contact recovery gain -0.0039, contact similarity gain -0.0437。

### 结论

Directional learned 与 directional classified 呈现同型负结果: 最近蛋白原子方向/距离特征没有提升 learned policy, 反而降低 contact recovery/similarity 并增加 clash degradation。该 signal 可能过于局部和噪声化, 与当前 10 fixed offsets 的 pseudo target 不匹配。

### 决策

不继续跑 official PLIP/Vina, 因为 fallback contact recovery 已为负且与 directional classified 负结果一致。后续 learned policy 改进不应继续沿用这个最近蛋白原子方向特征; 应转向更稳健的 pocket/contact 表征, 更真实 failed candidates, 或能直接学习 interaction-restoration 的 oracle-free policy。


## 2026-06-02 / Scaled learned editable-contact policy 小幅正结果

### 阶段目标

在 directional feature 负结果后, 检查普通 nearest-neighbor learned editable-contact policy 是否被 feedback feature 尺度混杂削弱。新增 `feedback_scaled_learned_editable_contact_policy`, 只在该 opt-in baseline 中按训练集 feature standard deviation 缩放 nearest-neighbor 距离, 不加入最近蛋白原子方向特征, 不改变既有 learned/classified/ridge/budgeted 结果。

### 代码改动

- `scripts/eval/repair_baselines.py`:
  - 新增 `feature_standard_deviations(...)`, `scaled_feature_distance(...)`, `nearest_scaled_geometry_offset(...)`。
  - `learned_editable_contact_offset(...)` 新增 `scale_features` 参数, 默认 `False`。
  - `repair_with_learned_editable_contact_policy(...)` 新增 `scale_features` 参数, 默认 `False`。
  - `repair_candidate(...)` 新增 `feedback_scaled_learned_editable_contact_policy` 分支。
- `scripts/eval/run_contact_degraded_multiseed.py`: baseline 列表加入 `feedback_scaled_learned_editable_contact_policy`。
- 验证:
  - `PYTHONPATH=src /home/lyj/miniconda3/envs/pfr/bin/python -m py_compile scripts/eval/repair_baselines.py scripts/eval/run_contact_degraded_multiseed.py` 通过。
  - `git diff --check -- scripts/eval/repair_baselines.py scripts/eval/run_contact_degraded_multiseed.py` 通过。

### fallback 三种子运行

复用 contact-degraded local-edit seeds 0/1/2 failed candidates 和 feedback, 只运行新增 baseline:

- seed0: 19 failed candidates -> 19 repaired records。
- seed1: 17 failed candidates -> 17 repaired records。
- seed2: 17 failed candidates -> 17 repaired records。

输出:

- `outputs/20260602-02-contact-degraded-policy-variants/metrics/contact_degraded_scaled_learned_policy_summary.json`
- `outputs/20260602-02-contact-degraded-policy-variants/metrics/contact_degraded_scaled_learned_policy/seed0.json`
- `outputs/20260602-02-contact-degraded-policy-variants/metrics/contact_degraded_scaled_learned_policy/seed1.json`
- `outputs/20260602-02-contact-degraded-policy-variants/metrics/contact_degraded_scaled_learned_policy/seed2.json`
- `outputs/20260602-02-contact-degraded-policy-variants/processed/repaired_candidates_contact_degraded_scaled_learned_seed0.jsonl`
- `outputs/20260602-02-contact-degraded-policy-variants/processed/repaired_candidates_contact_degraded_scaled_learned_seed1.jsonl`
- `outputs/20260602-02-contact-degraded-policy-variants/processed/repaired_candidates_contact_degraded_scaled_learned_seed2.jsonl`
- `outputs/20260602-02-contact-degraded-policy-variants/processed/evaluated_repaired_contact_degraded_scaled_learned_seed0.jsonl`
- `outputs/20260602-02-contact-degraded-policy-variants/processed/evaluated_repaired_contact_degraded_scaled_learned_seed1.jsonl`
- `outputs/20260602-02-contact-degraded-policy-variants/processed/evaluated_repaired_contact_degraded_scaled_learned_seed2.jsonl`

Fallback summary:

| 指标 | 结果 |
|---|---:|
| total repaired | 53 |
| mean repaired success rate | 0.8865 |
| mean repair gain success rate | 0.2466 |
| mean contact recovery gain | +0.0221 |
| mean contact similarity gain | +0.0006 |
| mean anchor error reduction | 0.0000 |
| mean clash count reduction | -0.1331 |

### official PLIP/Vina 运行

合并三种子 repaired records 到:

- `outputs/20260602-02-contact-degraded-policy-variants/processed/repaired_candidates_contact_degraded_scaled_learned_multiseed.jsonl`

第一次 official 汇总出现全错误:

- `plip_error`: `plip_cli_missing` 53/53。
- `vina_error`: `missing_cli:mk_prepare_ligand.py,mk_prepare_receptor.py,vina` 53/53。

原因不是方法失败, 而是虽然使用了 `pfr-eval-tools` Python, 但没有把 `/home/lyj/miniconda3/envs/pfr-eval-tools/bin` 放入 `PATH`, CLI 不可见。该 all-error 输出不能作为 official 结果。

随后用正确环境重跑:

```bash
PATH=/home/lyj/miniconda3/envs/pfr-eval-tools/bin:$PATH \
PYTHONPATH=/home/lyj/mnt/project/pocket-failure-repair/src \
/home/lyj/miniconda3/envs/pfr-eval-tools/bin/python scripts/eval/eval_official_tools.py \
  --repaired-candidates outputs/20260602-02-contact-degraded-policy-variants/processed/repaired_candidates_contact_degraded_scaled_learned_multiseed.jsonl \
  --output outputs/20260602-02-contact-degraded-policy-variants/metrics/official_eval_contact_degraded_scaled_learned_plip_vina.jsonl \
  --tools plip,vina
```

最终 official 输出:

- `outputs/20260602-02-contact-degraded-policy-variants/metrics/official_eval_contact_degraded_scaled_learned_plip_vina.jsonl`
- `outputs/20260602-02-contact-degraded-policy-variants/metrics/official_eval_contact_degraded_scaled_learned_plip_vina_summary.json`
- `outputs/20260602-02-contact-degraded-policy-variants/tables/official_eval_contact_degraded_scaled_learned_plip_vina_summary.csv`

Official error check:

- records: 53。
- PLIP available rate: 1.0。
- Vina available rate: 1.0。
- `plip_error`: 0。
- `vina_error`: 0。

Official summary:

| 指标 | 结果 |
|---|---:|
| PLIP recovery gain | +0.0090 |
| PLIP similarity gain | -0.0176 |
| mean repaired PLIP interaction count | 9.8113 |
| mean failed PLIP interaction count | 9.4340 |
| mean reference PLIP interaction count | 10.8113 |
| mean Vina score-only energy | -6.5812 |
| mean internal candidate budget | 1.0 |

### 对照与结论

- 普通 1-shot learned official PLIP recovery gain: +0.0065。
- Scaled 1-shot learned official PLIP recovery gain: +0.0090。
- Classified budget=1 official PLIP recovery gain: +0.0090。
- Budgeted learned budget=10 official PLIP recovery gain: +0.0099。
- Full editable-search budget=10 official PLIP recovery gain: +0.0301。

Scaled feature distance 能把 nearest-neighbor learned policy 从 +0.0065 提升到约 +0.0090, 接近 classified 和 budgeted learned 的 official PLIP recovery gain。这说明原始 feature 尺度确实可能影响 budget=1 learned policy, 是一个有用的低风险改进。

但该结果仍然很弱: PLIP similarity gain 为 -0.0176, fallback gain_success 0.2466 不高, 且远弱于 budget=10 full editable-search +0.0301。因此它只能作为 learned policy 诊断和小幅正结果, 不能作为 BIBM 最终主模型证据。

### 下一步

- 保留 scaled learned 作为 budget=1 learned ablation 候选。
- 不继续最近蛋白原子 directional feature。
- 下一步应探索更稳健的 pocket/contact shell 表征或 interaction-restoration target, 而不是只做单个最近原子方向。
- 后续论文表格中应把 scaled learned 与 learned/classified/ridge/budgeted/full-search 同列, 并明确 internal budget=1 vs budget=10 差异。

## 2026-06-02 / BIBM neural repair model 路线设计报告

### 阶段目标

- 深入分析如果目标是 BIBM full paper, 本项目的最终模型应该如何设计。
- 明确 neural repair model 的输入输出、架构路线、学习方法、数据利用、数据集选择、评估要求和主要风险。
- 在不启动新实验的前提下, 收敛出三个可行方案并形成文档报告。

### 插件 / Skill / Workflow 使用记录

- 使用的 skill: `academic-pipeline`。
- 使用的 workflow: `bibm-neural-repair-route-panel`。
- 使用目的: 以 ultracode 多 agent 方式从模型设计、数据评估、审稿风险和综合路线四个角度并行分析 BIBM 级神经修复模型路线。
- 输入: 当前项目状态、contact-degraded local-edit 三 seed 结果、shallow learned policy 证据、BIBM full paper 目标和用户关于模型/数据/学习方法的设计问题。
- 输出文档: `docs/plan/20260602-02-bibm-neural-repair-model-routes-plan.md`。
- 是否成功: 成功。
- 是否启动新实验: 否。本阶段只做路线设计和文档整理, 没有运行新的 repair/eval 实验。

### 主要结论

1. 当前 shallow learned policies, 包括 nearest-neighbor、scaled nearest-neighbor、ridge、classifier 和 budgeted learned, 只能作为 baseline、ablation 或 teacher-student 前置证据, 不能作为最终 BIBM 主模型。
2. 后续主张应收敛为 `failure-feedback-conditioned neural local repair model`, 即模型读取 failed candidate、protein pocket、editable/anchor masks 和 structured failure feedback, 输出 editable-region local repair action 或 coordinate refinement。
3. 推荐三个可行方案:
   - 方案一: Teacher-Student Feedback-Conditioned EGNN LocalEditNet。
   - 方案二: Self-Supervised FF-EGNN Iterative Diagnostic Refiner。
   - 方案三: Failure-Feedback-Conditioned Local Flow/Diffusion Refinement。
4. 最推荐方案一作为第一主线: 用当前 editable-contact search teacher 产生 pseudo-label, 训练 EGNN/GVP/PaiNN 风格的 student model 预测 editable-region repair action。
5. 方案二适合作为方案一增强: 加入 self-supervised corruption-denoising pretraining、iterative repair 和 hard-negative preference learning。
6. 方案三创新性最高但风险最大: fixed-topology local flow/diffusion refinement 需要 10k+ repair pairs 和严格 top-K budget 审计, 不适合作为第一版主线。

### 数据路线判断

- 当前 12-complex smoke-plus 和 53 contact-degraded failed candidates 只能用于 sanity、overfit、case study 和 closed-loop debug。
- BIBM full paper 主实验至少需要从 PDBbind refined/general、Binding MOAD 或 CrossDocked 清洗子集中构建数百到数千 protein-ligand complexes。
- 每个 complex 应生成多个 failed candidates, 目标先达到 5k-40k teacher-labeled repair examples。
- split 必须按 held-out complex / scaffold / protein target 或 sequence cluster, 不能按 failed candidate record 随机切分。

### 评估路线判断

- 主指标应为 relative repair gain, 尤其是 official PLIP interaction recovery/similarity gain。
- 必须同时报告 scaffold preservation、anchor drift、editable validity、clash、geometry validity、bounded PoseBusters diagnostic 和 Vina supplemental。
- Vina score-only 不能作为 repair success。
- 必须保留 no-feedback、shuffled-feedback、rerank-only、Best-of-N、direct regeneration、shallow learned policies 和 editable-contact search teacher 作为对照。

### 输出文件

- `docs/plan/20260602-02-bibm-neural-repair-model-routes-plan.md`。
- `docs/STATUS.md` 已同步记录该路线报告和后续主线判断。

### 下一步

- 先冻结 teacher trace schema, 包括 failed complex、structured feedback、teacher top-1/top-M actions、negative actions、score deltas 和 split id。
- 再实现方案一 MVP: EGNN encoder + feedback encoder + editable coordinate/action decoder + confidence head。
- 先做 10-50 cases overfit 和 action replay check, 再扩展到 PDBbind/Binding MOAD 等公开 complex 数据。
- 在方案一有效后, 再加入方案二的 self-supervised pretraining 或方案三的 local flow/diffusion variant。

---

### 2026-06-03 / failure taxonomy 与可修复性边界文献调研

- 日期：2026-06-03
- 阶段名称：失败样本错误类型与可修复性边界相关工作调研
- 负责人 / agent：Claude Code + ultracode workflow / subagents
- commit：65e95ee Clean receptor files for smoke data
- 环境：未运行项目代码；仅使用文献、benchmark、官方工具文档和代码仓库调研
- GPU / CPU：未使用 GPU；未运行本地实验
- 数据版本：未统计本项目 outputs
- 随机种子：N/A

### 阶段目标

- 根据 `docs/plan/20260603-01-failure-taxonomy-research-plan.md` 调研 failed sample / failed molecule / bad pose / invalid output 的定义、判定工具、样本来源、采样流程、统计方式和可修复性边界。
- 明确是否存在面向 failed ligand repair 或 fixed-scaffold pocket-aware local editing 的统一 failure taxonomy。
- 为后续 project-specific operational multi-label taxonomy 和本地 failure prevalence audit 设计提供证据基础。

### 背景与判断

- 为什么做这个调研：当前需要先弄清相关工作如何定义和判定失败样本, 避免在后续本地审计前臆造标签、阈值或可修复性边界。
- 需要验证的假设：文献中可能不存在统一 repair-oriented failure taxonomy, 但可以从 PoseBusters, RDKit, docking RMSD, PLIP/ProLIF/ODDT, linker/fragment constrained generation 等来源整理 operational criteria。
- 与上一阶段的关系：承接 BIBM full-paper 路线规划中对 failed candidate 来源、failure type prevalence 和 repair in-scope/out-of-scope 的讨论。

### 插件 / Skill / Workflow 使用记录

- 使用的 plugin / skill / agent / workflow：ultracode workflow, 多个 research subagents, scientific-writing skill 相关写作规范补充。
- 使用目的：并行调研结构条件分子生成、docking/pose plausibility、protein-ligand interaction/clash、constrained editing/linker design、repair/refinement 和判定工具依据。
- 输入：`docs/plan/20260603-01-failure-taxonomy-research-plan.md`。
- 输出路径：`docs/report/20260603-01-failure-taxonomy-research-report.md`。
- 是否成功：最终成功写入报告。
- 失败原因或降级方案：第一轮 workflow 在综合阶段因一个子 agent 未调用 StructuredOutput 而失败；前序 5 组文献证据和 4 组工具证据已完成并保留。随后从已完成 transcript 中恢复 46 条文献/工作证据和 31 条工具/判定方法证据, 并手动综合为报告。一个 recovery workflow 因等待过久被停止, 未影响最终报告。
- 对本阶段结论的影响：保留了失败和降级过程, 结论只基于可核验论文、benchmark、官方工具文档或代码仓库, 未引入本地实验比例判断。

### 命令与配置

```bash
# 未运行本项目代码, 未复现实验, 未统计本地 outputs。
# 主要操作为读取调研计划、执行多 agent 文献/工具调研、整理 Markdown 报告。
```

配置文件：

- N/A

### 输出文件

- report：`docs/report/20260603-01-failure-taxonomy-research-report.md`
- plan：`docs/plan/20260603-01-failure-taxonomy-research-plan.md`
- metrics：N/A
- tables：报告内包含文献/工作证据表、工具/判定方法证据表和候选 failure labels 表
- figures：N/A
- molecules：N/A
- logs：workflow/subagent transcript 位于会话目录, 不作为项目正式输出
- checkpoints：N/A

### 主要结果

| 指标 | 结果 | 备注 |
|---|---:|---|
| 文献/工作证据 | 46 条 | 来自 5 组调研方向 |
| 工具/判定方法证据 | 31 条 | 来自 4 组工具/operational criteria 方向 |
| 本地代码运行 | 0 | 未运行项目代码 |
| 本地 outputs 统计 | 0 | 未统计本项目样本占比 |
| 复现实验 | 0 | 未复现实验 |

### 结论

- 未发现面向 failed ligand repair 或 fixed-scaffold pocket-aware local editing 的统一系统 failure taxonomy。
- 现有工作主要分散报告 validity, RMSD success, PoseBusters checks, docking/reranking metrics, interaction fingerprints, linker recovery, scaffold/anchor constraints 和 property filters。
- 多标签 failure taxonomy 更适合作为本项目自己的 operational taxonomy 设计, 不能写成文献共识。
- 第一阶段 repair 应优先聚焦 scaffold/anchor 保留前提下的 near-miss local failures, 如局部 3D geometry 异常、protein-ligand clash / volume overlap、anchor/attachment mismatch、局部 pose/torsion 问题, 以及 key interaction/contact loss secondary tag。
- 严重 chemical invalid、scaffold/anchor 丢失、整体 pose 错位、docking/evaluation run failure、纯 property filter failure 应排除或单独统计, 不宜作为第一阶段 fixed-scaffold local repair 主目标。

### 失败 / 异常 / 负结果

- 第一轮 workflow 在综合阶段失败, 但已从已完成子任务恢复证据并手动综合。
- 未发现已有文献系统统计本项目目标 near-miss local failure 在真实 baseline/generated failed outputs 中的比例；该缺口支持后续开展本地 failure prevalence audit。
- 文献中未发现普遍支持单样本多 failure labels 的统一 repair taxonomy；多标签设计应明确为本项目 operational taxonomy。

### 下一步

- 基于报告更新 `docs/plan/20260601-01-method-design-plan.md` 中的 failure taxonomy, primary/secondary labels, in-scope/out-of-scope 和 repairability boundary。
- 设计本地 failure prevalence audit, 固定 denominator、工具配置、输入清洗、PoseBusters/PLIP/RDKit/anchor mapping 协议。
- 在后续实验规划中区分 raw outputs, valid molecules, docked poses, selected candidates, rejected candidates 和 repair-eligible near-miss candidates。

## 2026-06-03 / 第三方 failure audit 第一阶段 MVP 基础资产落地

### 阶段目标

从 `docs/plan/20260603-02-third-party-failure-audit-alignment-plan.md` 和 `docs/plan/20260603-03-third-party-failure-audit-detailed-execution-plan.md` 推进到第一阶段可执行资产。目标是完成候选方法 feasibility table、数据 / dataset view / split / leakage 台账、第三方资源阻塞记录、失败样本 metadata schema、diagnosis label config、denominator/statistics schema、MVP checklist、后续 agent 任务拆分, 并在不触发暂停条件的范围内准备 2-3 个代表方法的最小可审计性试运行。

### 背景与判断

- 本阶段承接 failure taxonomy 调研结论: 先建立可追溯的 diagnosis protocol 和真实 output audit 资产, 再由真实失败分布决定 repair focus。
- 本阶段不声称完成第三方真实 failure prevalence audit。DiffSBDD / DiffLinker 仅完成 repo、checkpoint、wrapper dry-run 和 metadata pipeline 准备, 未运行真实 inference。
- 现有 smoke/smoke-plus/control 数据仍只允许作为 sanity-only, 不能进入第三方真实 prevalence denominator。

### 插件 / Skill / Agent 使用记录

- 使用 Explore 子 agent 只读盘点仓库现有资产, 输出结论: 当前无 `configs/audit`, `configs/third_party`, `schemas/audit`, `scripts/audit`, `scripts/third_party`, `outputs/20260603-01-third-party-failure-audit-mvp` 等第三方 audit 专用资产。
- 使用 general-purpose 子 agent 调研候选方法, 输出 8 个候选及证据, 优先候选为 DiffSBDD、DiffLinker、Pocket2Mol, TargetDiff 作为较重但重要的后续候选。
- 主会话补充读取官方 README/LICENSE, clone 官方 repo, 下载小型官方 Zenodo checkpoint, 并生成配置、schema、台账、wrapper 和报告。

### 命令与配置

关键命令类型:

```bash
# 只读读取计划与现有文档
# git ls-remote / git clone --depth 1 官方 GitHub repo
# HEAD 请求估计 Zenodo checkpoint size
# 下载 DiffSBDD / DiffLinker 官方 Zenodo checkpoint
# python -m py_compile scripts/third_party/run_diffsbdd_instrumented.py scripts/third_party/run_difflinker_instrumented.py scripts/audit/summarize_stage_attrition.py
# wrapper dry-run 生成 run_metadata.json / samples.jsonl
# summarize_stage_attrition.py 生成 dry-run stage_attrition.json
```

新增或更新配置:

- `configs/audit/resource_budget_v1.yaml`
- `configs/audit/diagnosis_label_config_v0_1.yaml`
- `configs/audit/denominator_statistics_schema_v0_1.yaml`
- `configs/audit/tool_versions.lock`
- `configs/third_party/diffsbdd_original_protocol.yaml`
- `configs/third_party/diffsbdd_audit_protocol.yaml`
- `configs/third_party/difflinker_original_protocol.yaml`
- `configs/third_party/difflinker_audit_protocol.yaml`
- `configs/third_party/pocket2mol_audit_protocol.yaml`
- `configs/third_party/targetdiff_audit_protocol.yaml`

### 输出文件

主要轻量资产:

- MVP report / checklist / agent tasks: `docs/report/20260603-03-third-party-failure-audit-mvp-report.md`
- Feasibility table: `outputs/20260603-01-third-party-failure-audit-mvp/metadata/method_feasibility_table_v1.json`, `outputs/20260603-01-third-party-failure-audit-mvp/metadata/method_feasibility_table_v1.csv`
- Resource blocker log: `outputs/20260603-01-third-party-failure-audit-mvp/metadata/resource_blocker_log_v1.jsonl`
- Artifact registry: `outputs/20260603-01-third-party-failure-audit-mvp/metadata/artifact_registry_v1.json`
- Asset hash manifest: `outputs/20260603-01-third-party-failure-audit-mvp/metadata/audit_asset_hash_manifest_v1.json`
- Raw dataset manifest: `data/templates/third_party_audit/raw_dataset_manifest_v1.json`
- Dataset view manifest: `data/templates/third_party_audit/dataset_view_manifest_v1.json`
- Split registry template: `data/templates/third_party_audit/split_registry_template_v1.json`
- Leakage checklist: `data/templates/third_party_audit/leakage_checklist_v1.json`
- Sample metadata schema: `schemas/audit/third_party_failure_sample_metadata_v0_1.json`
- Run metadata schema: `schemas/audit/third_party_run_metadata_v0_1.json`
- Stage attrition schema: `schemas/audit/third_party_stage_attrition_v0_1.json`
- Label schema: `schemas/audit/third_party_label_schema_v0_1.json`
- DiffSBDD wrapper: `scripts/third_party/run_diffsbdd_instrumented.py`
- DiffLinker wrapper: `scripts/third_party/run_difflinker_instrumented.py`
- Stage attrition summarizer: `scripts/audit/summarize_stage_attrition.py`

第三方 repo / checkpoint 资产:

- `third_party/diffsbdd`, commit `5d0d38d16c8932a0339fd2ce3f67ade98bbdff27`, MIT。
- `third_party/difflinker`, commit `fafbe47afe6cf068e9e1b23e7145377fb0f89f89`, MIT。
- `third_party/pocket2mol`, commit `836a0c4ce487297ad24bc54ac2ebd163de13242c`, MIT。
- `third_party/targetdiff`, commit `142f1eb7178480d435fe0b8cb95a99beb48997c7`, MIT。
- DiffSBDD checkpoint: `third_party/diffsbdd/checkpoints/crossdocked_fullatom_cond.ckpt`, SHA256 `07f86764bf569aafbc40a9c15fc02de8e2550437dd0f17f657eab3abe66c372c`。
- DiffLinker checkpoint: `third_party/difflinker/models/pockets_difflinker_full.ckpt`, SHA256 `695ef7d634c09db4b9635c4e5efebad23385b8432f0687b6eae5e726ba7883f9`。

Dry-run artifacts:

- `outputs/20260603-01-third-party-failure-audit-mvp/diffsbdd/diffsbdd_dryrun_v0_1/run_metadata.json`
- `outputs/20260603-01-third-party-failure-audit-mvp/diffsbdd/diffsbdd_dryrun_v0_1/samples.jsonl`
- `outputs/20260603-01-third-party-failure-audit-mvp/diffsbdd/diffsbdd_dryrun_v0_1/stage_attrition.json`
- `outputs/20260603-01-third-party-failure-audit-mvp/difflinker/difflinker_dryrun_v0_1/run_metadata.json`
- `outputs/20260603-01-third-party-failure-audit-mvp/difflinker/difflinker_dryrun_v0_1/samples.jsonl`
- `outputs/20260603-01-third-party-failure-audit-mvp/difflinker/difflinker_dryrun_v0_1/stage_attrition.json`

### 主要结果

| 指标 | 结果 | 备注 |
|---|---:|---|
| Feasibility table methods | 8 | DiffSBDD, DiffLinker, Pocket2Mol, TargetDiff, DeLinker, LiGAN, MolCRAFT, 3DLinker |
| Resource blocker rows | 6 | Pocket2Mol, TargetDiff, MolCRAFT, 3DLinker, LiGAN, method env |
| 官方 repo cloned | 4 | DiffSBDD, DiffLinker, Pocket2Mol, TargetDiff |
| 小型官方 checkpoint downloaded | 2 | DiffSBDD Zenodo 17.03 MiB, DiffLinker Zenodo 23.03 MiB |
| Google Drive / unknown-size resources downloaded | 0 | 遵守 resource budget blocking policy |
| Wrapper scripts created | 2 | DiffSBDD, DiffLinker |
| Wrapper dry-runs | 2 | 均成功生成 metadata 和 attrition dry-run |
| JSON assets parse check | passed | schema/manifest/table/registry JSON 均可解析 |
| Method inference runs | 0 | 方法专用 PyTorch/PyG/Lightning 环境尚未创建 |
| Formal labels / prevalence | 0 | analysis-frozen gate 未通过 |

### 结论

- 第一阶段 MVP 的 planning/design 和最小 output-capture readiness 资产已落地, claim level 仍停留在 L0-L1/L2 preparation, 不能声称真实 failure prevalence。
- DiffSBDD 是第一优先最小真实 output-capture trial 候选: 官方实现, MIT, 小型 Zenodo checkpoint, SDF 输出, 覆盖 SBDD de novo / inpainting local-edit。
- DiffLinker 是第二优先候选: 官方实现, MIT, 小型 Zenodo checkpoint, `.xyz/.sdf` 输出, 覆盖 linker / pocket-conditioned linker；但必须单独报告 linker/stage-limited 边界, 不并入 full SBDD raw prevalence。
- Pocket2Mol 具有较好 raw lineage 潜力, 因 `sample_for_pdb.py` 保存 `queue/failed/finished/duplicate` pool states, 但 checkpoint/data 在 Google Drive 且 size unknown, 按 policy 暂停下载。
- TargetDiff 是重要 SBDD baseline, 但 checkpoint/data 同样在 Google Drive 且 size unknown, 环境风险更高, 当前作为 second MVP candidate。

### 失败 / 异常 / 负结果

- GitHub API 查询一度触发 rate limit, 已降级为 WebFetch、git ls-remote 和本地 clone/README 读取。
- `pfr` 环境缺少 `torch`, `torch_geometric`, `pytorch_lightning`, `openbabel` Python module, `easydict`, `lmdb`；`pfr-eval-tools` 也缺 `torch` 和 `pytorch_lightning`, 因此未执行真实 third-party inference。
- Google Drive / unknown-size checkpoint/data 未下载, 包括 Pocket2Mol 和 TargetDiff 核心资源。
- MolCRAFT license 为 CC-BY-NC-SA 4.0 NonCommercial/ShareAlike, 不作为默认 MVP。
- 3DLinker license 不可见, 标记 `blocked_pending_user_decision`, 未 clone/run。
- Wrapper dry-run 只证明 metadata/denominator pipeline 可写, 不证明方法可运行或输出质量。

### 下一步

1. 优先用 tmux 或子 agent 创建 DiffSBDD 方法环境, 记录 Python/CUDA/PyTorch/PyG/Lightning/RDKit/OpenBabel 版本。
2. 环境可用后运行 DiffSBDD 3RFM example `n_samples=3-10` output-capture trial, 只作为 output-capture sanity, 不做 formal prevalence。
3. 再创建 DiffLinker 方法环境并运行 HSP90 case-study trial, 单独报告 linker/stage-limited 边界。
4. 用 dry-run / 实际 output rows 做 diagnosis sanity, 验证 missing_data / tool_failure / pipeline_failure / not_evaluable / original_status 不被静默删除。
5. 若要推进 Pocket2Mol 或 TargetDiff, 先解决 Google Drive 资源大小、登录和训练数据 overlap 风险。

## 2026-06-04 / 第三方 audit 工具覆盖度复核

### 阶段目标

基于 `docs/report/20260603-01-failure-taxonomy-research-report.md` 的调研结论和当前 `configs/audit/*` 配置, 判断现有外部评估工具是否足够支撑第一阶段 MVP 与后续 formal audit。

### 输出文件

- 正式小报告: `docs/report/20260604-01-audit-tool-coverage-report.md`

### 主要结论

- 当前 RDKit, OpenBabel, Meeko, PLIP, Vina, PoseBusters 工具栈对第一阶段 MVP / sanity wiring 基本足够。
- 正式 third-party failure prevalence audit 仍未达到 `analysis-frozen` 要求。
- 最大缺口是 PoseBusters 版本、config、输出列、阈值和 wrapper 尚未完整冻结。
- PLIP 还缺 interaction/contact-loss parser 与冻结规则。
- RDKit 还需冻结 sanitize/scaffold/anchor mapping 规则。
- Vina 只能作为辅助 metric, 不能作为 repair success gate。

### 下一步

1. 更新 `configs/audit/tool_versions.lock`, 正式记录 PoseBusters 版本、config 和输出边界。
2. 实现 RDKit / PoseBusters / PLIP 的 audit wrapper 或 labeling pipeline。
3. 用 sanity set 验证 missing/tool/pipeline/not_evaluable/original_failed_sample rows 不被静默删除。


---

## 2026-06-04 / data processed 派生产物结构规整

### 环境与数据版本

- 日期: 2026-06-04。
- 阶段名称: data processed 派生产物结构规整。
- 负责人 / agent: Claude Code + ultracode workflow。
- 环境: 本地文件系统与 Python 脚本; 未运行模型或 evaluator。
- 数据版本: `data/processed/` 当前 89 个 JSONL 文件。
- experiment_id: `20260604-02-data-processed-structure-cleanup`。
- 实验目录: `experiments/20260604-02-data-processed-structure-cleanup/`。
- 输出目录: `outputs/20260604-02-data-processed-structure-cleanup/`。

### 阶段目标

- 审计 `data/processed/` 下 JSONL 产物的引用关系和实验归属。
- 保留 canonical reusable processed dataset, 将派生 failed/feedback/repaired/evaluated JSONL 按实验归档到 `outputs/<experiment_id>/processed/`。
- 同步更新可执行配置、脚本默认路径、实验配置快照、文档和 metrics metadata 中的路径引用。
- 不删除源文件, 不执行 `git rm` / `git rm --cached`, 不修改 `.gitignore`。

### 插件 / Skill / Workflow 使用记录

- 使用的 plugin / skill / agent / workflow: ultracode workflow `audit-data-processed-organization`。
- 使用目的: 并行审计 `data/processed/` 文件家族、引用来源、迁移映射和风险。
- 输出: workflow 结果指出共有 89 个 JSONL, 其中 2 个 canonical keep candidates, 87 个派生产物迁移候选; 引用主要来自 configs, scripts, docs, experiments 和 outputs metadata。
- 风险修正: 避免用宽泛 seed glob 误吞 classified/key/shuffled/directional/probe 变体; PoseBusters subset 归到 official-tool evaluation; 保留 migration manifest 的 legacy source 字段。

### 规整动作

- 生成迁移清单: `outputs/20260604-02-data-processed-structure-cleanup/metadata/data_processed_migration_manifest.json`。
- 保留 canonical 数据:
  - `data/datasets/rgroup_smoke/entries/index.jsonl`
  - `data/datasets/rgroup_smoke_plus/entries/index.jsonl`
- 复制 87 个派生 JSONL 到对应 `outputs/<experiment_id>/processed/` 目录, 并用 sha256 校验 source / target 内容一致。
- 同步更新 81 个文本文件中的 275 处路径引用。
- 单独修正 `scripts/eval/run_contact_degraded_multiseed.py` 中 seed 动态输出路径, 防止未来运行继续写入旧派生产物位置。

### 目标归档分组

- `outputs/20260531-01-smoke-file-pipeline/processed/`: smoke failed candidates 和 feedback。
- `outputs/20260601-01-smoke-repair-baselines/processed/`: smoke repaired / evaluated records。
- `outputs/20260601-02-smoke-plus-expansion-and-variants/processed/`: smoke-plus 基础链条。
- `outputs/20260601-03-smoke-plus-official-tool-evaluation/processed/`: PoseBusters official-tool subset candidates。
- `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/processed/`: Vina / local-proposal / docking-like 诊断分支。
- `outputs/20260601-05-contact-degraded-local-edit-core/processed/`: contact-degraded local-edit core 和基础 seed 链条。
- `outputs/20260602-01-contact-degraded-budget-and-ablation/processed/`: key / shuffled / residual ablation。
- `outputs/20260602-02-contact-degraded-policy-variants/processed/`: classified / directional / learned policy variants。

### 验证

- 迁移清单覆盖 89 个 JSONL: keep 2, copy-and-retarget 87。
- 所有 target 文件存在, sha256 校验通过。
- 除迁移清单自身为审计保留 source_path 外, 全仓库搜索未发现非 canonical 派生产物旧路径引用。
- 全仓库搜索未发现旧派生产物路径模式残留。
- `configs/**/*.yaml` 中关键 path 字段的目标文件或父目录存在。

### 结论

- `data/processed/` 的有效引用边界已收敛为 canonical R-group processed dataset。
- 派生 failed / feedback / repaired / evaluated records 已按实验归入 `outputs/<experiment_id>/processed/`, 符合当前实验目录规范。
- 本次只做结构规整与路径重定向, 不重算指标, 不改变 JSONL 内容, 不产生新的实验结论。

### 失败 / 异常 / 负结果

- 源文件仍保留在旧目录, 这是有意的 copy-and-retarget 安全策略; 后续 `.gitignore` / git tracking cleanup 阶段再决定删除或 untrack。
- 部分历史 outputs metadata 和文档引用已被 retarget 到新路径, 但 migration manifest 中仍保留 legacy source_path 以维持审计可追溯性。

### 下一步

- 进入 `.gitignore` 与 git tracking cleanup 阶段前, 先重新检查工作区状态。
- 后续若确认无旧路径消费者, 再决定是否删除或 untrack 旧目录中的派生产物源文件。


### 2026-06-04 / data processed 旧派生产物源文件删除补充

- 根据用户确认, 在 `data/processed/` 规整和引用重定向验证通过后, 删除旧目录中的 87 个派生 JSONL 源文件。
- 保留 canonical processed dataset:
  - `data/datasets/rgroup_smoke/entries/index.jsonl`
  - `data/datasets/rgroup_smoke_plus/entries/index.jsonl`
- 删除前确认所有对应 target 文件均存在于 `outputs/<experiment_id>/processed/`。
- 更新迁移清单: `outputs/20260604-02-data-processed-structure-cleanup/metadata/data_processed_migration_manifest.json`。
- 删除后验证:
  - `data/processed/*.jsonl` 只剩 2 个 canonical rgroup 文件。
  - missing target count = 0。
  - 非 canonical 旧路径引用残留 = 0。
- 本步骤没有修改 `.gitignore`, 没有执行 `git rm` / `git rm --cached`, 没有重算实验结果。

## 2026-06-04 / experiments legacy 输出与 data manifest 结构规整

- experiment_id: `20260604-03-experiments-legacy-output-cleanup`.
- 用户约束: 本轮不修改 `.gitignore`; 先完成除 `.gitignore` 外的命名和管理方式规整。
- 使用 ultracode workflow 多代理审查 legacy experiments, data manifests, scripts/configs 默认路径和 README metadata 缺口。
- 创建实验记录目录: `experiments/20260604-03-experiments-legacy-output-cleanup/`.
- 创建输出 metadata: `outputs/20260604-03-experiments-legacy-output-cleanup/metadata/experiments_legacy_output_cleanup_manifest.json`.
- 迁移 legacy experiments 输出:
  - `experiments/smoke/pipeline_plan.json` -> `experiments/20260531-01-smoke-file-pipeline/metadata/pipeline_plan.json`.
  - `experiments/smoke/multiseed_repaired/` -> `outputs/20260601-01-smoke-repair-baselines/processed/multiseed_repaired/`.
  - `experiments/smoke_plus/multiseed_repaired/` -> `outputs/20260601-02-smoke-plus-expansion-and-variants/processed/multiseed_repaired/`.
- 迁移 generated artifact 语义路径:
  - `outputs/<experiment_id>/raw/` 下 generated cases / failed molecules -> `outputs/<experiment_id>/processed/cases/` 或 `processed/failed_molecules/`.
  - `outputs/<experiment_id>/normalized/` 下 repaired molecule artifacts -> `outputs/<experiment_id>/processed/repaired_molecules/`.
- 迁移 data manifest / split:
  - `data/splits/rgroup_smoke_split.json` -> `data/manifests/splits/rgroup_smoke_split_v1.json`.
  - `data/splits/rgroup_smoke_plus_split.json` -> `data/manifests/splits/rgroup_smoke_plus_split_v1.json`.
  - `data/raw/*/manifest.json` -> `data/manifests/raw/*_raw_manifest_v1.json`.
- 新增 canonical lineage manifests:
  - `data/manifests/processed/rgroup_smoke_processed_manifest_v1.json`.
  - `data/manifests/processed/rgroup_smoke_plus_processed_manifest_v1.json`.
  - `data/manifests/views/rgroup_smoke_view_v1.json`.
  - `data/manifests/views/rgroup_smoke_plus_view_v1.json`.
  - `data/manifests/raw/rcsb_smoke_raw_reconciliation_v1.json`.
- 对重复 raw root 和 ligand checksum 不一致问题只记录, 未删除或重写 `data/raw/` 结构文件。
- 补齐 10 个 dated experiment README 的 `experiment_name`, 并为所有 dated experiments 写入 `metadata/manifest_index.json`.
- 修正 `experiments/20260604-02-data-processed-structure-cleanup/README.md` 中关于旧 `data/processed/` 源文件未删除的过时说明。
- 更新脚本/配置默认路径, 避免继续写入 legacy `experiments/smoke*`, `outputs/<id>/raw/`, `outputs/<id>/normalized/`, 以及由 data download 脚本直接写 `docs/report/`.
- 清理源码树中的 `__pycache__` / `.pyc` 运行产物。
- 验证结果:
  - legacy `experiments/smoke`, `experiments/smoke_plus`, `experiments/ablations`, `experiments/baselines`, `experiments/main` 均已不存在。
  - `outputs/*/raw` 和 `outputs/*/normalized` 空目录已移除。
  - `data/processed/*.jsonl` 仍只保留 `rgroup_smoke.jsonl` 和 `rgroup_smoke_plus.jsonl`.
  - 旧路径引用只保留在本次 cleanup manifest / notes / historical log 等审计字段中, 可执行配置和脚本默认路径未发现未允许残留。
  - `.gitignore` 未在本轮修改。
- 测试:
  - 初次用当前 shell 的 `flash-vqg` Python 跑 targeted tests 失败, 原因是该环境缺 RDKit, 非本轮路径改动问题。
  - 使用项目环境重跑通过: `PYTHONDONTWRITEBYTECODE=1 conda run -n pfr env PYTHONPATH=src python -m pytest tests/test_download_smoke_complexes.py tests/test_smoke_pipeline.py tests/test_same_budget_audit.py -q` -> `10 passed`.
- 后续仍需单独处理 `.gitignore` / git tracking cleanup, 以防大量 outputs/logs/work/raw data 或 local runtime 产物误入 git。

## 2026-06-04 / 残留运行产物路径落点修复

- 目的: 复核并修复 cleanup 后仍可能导致新运行产物落到不合规路径的脚本、配置和当前规范残留。
- 使用 ultracode workflow 审计 scripts/configs/docs/runtime writers, 重点检查 `experiments/smoke*`, `outputs/*/raw`, `outputs/*/normalized`, `data/splits`, third-party `raw_outputs`, 以及配置快照混入 outputs 的问题。
- 修复 `scripts/setup/smoke_pipeline_dry_run.py`: `--write-plan` 默认值改为 `None`; 无参运行只打印 dry-run plan, 不再默认写入或覆盖 `experiments/20260531-01-smoke-file-pipeline/metadata/pipeline_plan.json`。
- 修复 third-party wrapper 输出语义:
  - `scripts/third_party/run_diffsbdd_instrumented.py` 使用 `captured_outputs/` 代替 `raw_outputs/`。
  - `scripts/third_party/run_difflinker_instrumented.py` 使用 `captured_outputs/` 代替 `raw_outputs/`。
  - `configs/third_party/diffsbdd_audit_protocol.yaml` 和 `configs/third_party/difflinker_audit_protocol.yaml` 的 output expectations 同步改为 `captured_outputs/`。
  - 已将已有 dry-run 目录 `outputs/20260603-01-third-party-failure-audit-mvp/{diffsbdd,difflinker}/*/raw_outputs` 重命名为 `captured_outputs`, 并同步更新对应 dry-run JSON metadata 中的路径字段。
- 修复 `experiments/README.md`: 推荐 outputs 结构改为 `processed/`, `logs/`, `metrics/`, `tables/`, `summaries/`, `figures/`, `work/`; 不再推荐 `outputs/<experiment_id>/raw/` 和 `normalized/`。
- 修复 `scripts/eval/run_repaired_multiseed.py`: per-seed repair/eval config snapshots 默认写入 `experiments/<experiment_id>/configs/resolved/multiseed_repaired/`, 不再混入 `outputs/<experiment_id>/processed/multiseed_repaired/`。已迁移已有 smoke 和 smoke-plus multiseed `repair_seed_*.yaml` / `eval_repaired_seed_*.yaml` 到对应 experiment configs 目录。
- 修复当前 SOP stale split 路径: `docs/plan/20260603-03-third-party-failure-audit-detailed-execution-plan.md` 中 split registry 建议路径改为 `data/manifests/splits/<split_id>.json`; `data/templates/third_party_audit/split_registry_template_v1.json` 注释同步更新。
- 同步修正文档中的当前输出结构措辞: third-party plan/report/alignment 文档中将 method output capture 路径改为 `captured_outputs/` 和 `processed/normalized_samples/` 语义。历史日志和 migration manifest 中旧路径保留为历史 source/迁移记录。
- 验证:
  - `python scripts/setup/smoke_pipeline_dry_run.py` 无参运行只打印 plan, 输出 `Plan not written; pass --write-plan to persist it.`。
  - DiffSBDD / DiffLinker wrapper dry-run 使用临时 output-root 验证, 均创建 `captured_outputs/` 和 `logs/`, 不创建 `raw_outputs/`。
  - `PYTHONDONTWRITEBYTECODE=1 python -m py_compile scripts/setup/smoke_pipeline_dry_run.py scripts/eval/run_repaired_multiseed.py scripts/third_party/run_diffsbdd_instrumented.py scripts/third_party/run_difflinker_instrumented.py` 通过。
  - `PYTHONDONTWRITEBYTECODE=1 conda run -n pfr env PYTHONPATH=src python -m pytest tests/test_download_smoke_complexes.py tests/test_smoke_pipeline.py tests/test_same_budget_audit.py -q` -> `10 passed`。
  - 未发现新生成 `.pyc` 文件。
- 本步骤仍未修改 `.gitignore`, 未执行 git add / git rm / git commit, 未重算实验结果。

## 2026-06-04 / raw-to-processed lineage 索引补齐

- 目的: 回应用户指出“全文搜索 raw 路径太低效”和“多个数据集不能混在同一个 lineage 索引”的问题, 为当前 canonical `data/raw/` 与 `data/processed/` 建立按数据集分目录的结构化索引。
- 新增目录: `data/datasets/<dataset_id>/lineage/`; 旧的按类型顶层 `data/manifests/lineage/` 已迁入按数据集组织的新结构。
- 新增/修正索引结构:
  - `data/catalog/dataset_catalog_v1.json`: 只登记每个 dataset 的 manifest root 和 lineage index 路径, 不混合具体 raw/processed 记录。
  - `data/datasets/rgroup_smoke/manifests/lineage/raw_to_entry_index_v1.json` 和 `processed_to_raw_index_v1.json`: 仅记录 `rgroup_smoke` 数据集内部的 raw/processed 对应关系。
  - `data/datasets/rgroup_smoke_plus/manifests/lineage/raw_to_entry_index_v1.json` 和 `processed_to_raw_index_v1.json`: 仅记录 `rgroup_smoke_plus` 数据集内部的 raw/processed 对应关系。
- 删除早先混合多个数据集的顶层 `raw_to_processed_index_v1.json` 和 `processed_to_raw_index_v1.json`, 避免把多个 dataset 混在同一个查找文件里。
- 覆盖范围: 当前 canonical smoke 和 smoke-plus processed datasets, 即 `data/datasets/rgroup_smoke/entries/index.jsonl` 和 `data/datasets/rgroup_smoke_plus/entries/index.jsonl`。
- 索引规模:
  - `rgroup_smoke`: 6 个 raw path entry / 3 条 processed record。
  - `rgroup_smoke_plus`: 24 个 raw path entry / 12 条 processed record。
- 更新 `data/README.md`: 增加按 dataset_id 分目录的 `data/datasets/<dataset_id>/lineage/` 说明, 明确正常 lineage 查找先选 dataset, 再查该 dataset 自己的索引。
- 更新 `data/CLAUDE.md`: 要求新增或更新 canonical `data/processed/` dataset 时同步维护 `data/datasets/<dataset_id>/lineage/` 下的索引和 `data/catalog/dataset_catalog_v1.json`。
- 本步骤没有改动 raw 文件, 没有重算实验结果, 没有修改 `.gitignore`, 没有执行 git add / git rm / git commit。

## 2026-06-04 / data manifest 按数据集重组

- 目的: 回应用户确认的结构方案, 将 `data/manifests/raw`, `processed`, `splits`, `views`, `lineage` 从按类型分散组织改为按 dataset_id 聚合组织。
- 新结构:
  - `data/datasets/rgroup_smoke/manifests/raw/`, `processed/`, `views/`, `splits/`, `lineage/`。
  - `data/datasets/rgroup_smoke_plus/manifests/raw/`, `processed/`, `views/`, `splits/`, `lineage/`。
  - `data/catalog/dataset_catalog_v1.json`: 全局数据集目录, 只登记 dataset 和各自 manifest 路径。
  - `data/catalog/rcsb_smoke_raw_reconciliation_v1.json`: 跨 `rgroup_smoke` / `rgroup_smoke_plus` 的 raw 重复和 ligand checksum 差异记录。
  - `data/templates/third_party_audit/`: 保留为全局 third-party audit 模板区; 若后续有绑定具体 dataset 的 third-party audit manifest, 应放入 `data/datasets/<dataset_id>/manifests/third_party_audit/`。
- 已迁移文件:
  - raw manifests -> `data/datasets/<dataset_id>/raw/`。
  - processed manifests -> `data/datasets/<dataset_id>/processed/`。
  - split manifests -> `data/datasets/<dataset_id>/splits/`。
  - view manifests -> `data/datasets/<dataset_id>/views/`。
  - lineage indexes -> `data/datasets/<dataset_id>/lineage/`。
- 已删除或移除空的旧类型目录: `data/manifests/raw/`, `processed/`, `splits/`, `views/`, `lineage/`。
- 已同步更新 configs、scripts、data docs、active docs、experiment metadata 中的旧 manifest 路径引用。
- 验证:
  - `rgroup_smoke`: raw 1, processed 1, views 1, splits 1, lineage 2。
  - `rgroup_smoke_plus`: raw 1, processed 1, views 1, splits 1, lineage 2。
  - `data/catalog/dataset_catalog_v1.json` 中所有登记路径均存在。
  - 除历史 `docs/EXPERIMENT_LOG.md` 和 outputs migration/provenance 记录外, 未发现 `data/manifests/raw|processed|splits|views|lineage` 旧路径引用残留。
- 本步骤没有改动 raw 文件, 没有重算实验结果, 没有修改 `.gitignore`, 没有执行 git add / git rm / git commit。

## 2026-06-04 / 顶层目录 README 与 CLAUDE 管理说明补齐

- 新增文档:
  - `data/README.md`: 说明 `raw/`, `processed`, `manifests` 的职责, 以及 raw 数据不可随意改写、processed 只保存跨实验 canonical dataset、split manifest 使用 `data/datasets/<dataset_id>/splits/` 等规则。
  - `data/CLAUDE.md`: 约束 agent 不把单次实验产物写入 `data/`, 不自动删除或改写 `data/raw/`, 遇到 gated/license/unknown-size 资源暂停记录。
  - `outputs/README.md`: 说明 `outputs/<experiment_id>/` 与 `experiments/<experiment_id>/` 的一一对应关系, 推荐 `processed/`, `logs/`, `metrics/`, `tables/`, `summaries/`, `figures/`, `work/` 结构, 并固定 third-party `captured_outputs/` 语义。
  - `outputs/CLAUDE.md`: 约束 agent 使用规范输出目录, 不新建旧式 `raw/`, `normalized/`, `raw_outputs/`, `normalized_outputs/`, 移动 outputs 后同步更新引用。
  - `scripts/README.md`: 说明 `analysis/`, `audit/`, `data/`, `eval/`, `setup/`, `third_party/`, `train/` 的脚本职责和默认路径设计原则。
  - `scripts/CLAUDE.md`: 约束 agent 将跨实验复用脚本放根目录 `scripts/`, 单次实验脚本放 `experiments/<experiment_id>/scripts/`, dry-run 无参不写历史路径, third-party wrapper 使用 `captured_outputs/`。
  - `configs/README.md`: 说明 `audit/`, `baselines/`, `data/`, `feedback/`, `third_party/` 的配置职责, resolved config 应写入 `experiments/<experiment_id>/configs/resolved/`。
  - `configs/CLAUDE.md`: 约束 agent 不把 config snapshot 写入 `outputs/`, third-party config 不使用 `raw_outputs/`, split 使用 `data/datasets/<dataset_id>/splits/`, audit config 未冻结前不声明 formal prevalence。
- 已有 `configs/audit/README.md` 保留, 作为 audit config 子目录的更细说明。
- 更新 `docs/STATUS.md` 的仓库结构规整快照, 加入顶层目录管理说明已补齐的状态。
- 本步骤仍未修改 `.gitignore`, 未执行 git add / git rm / git commit, 未重算实验结果。

## 2026-06-04 / data dataset-root 与 entries 结构重组

> 注: 本日志中早期条目保留的 `data/raw/`, `data/processed/` 或旧 `data/manifests/*` 路径均表示迁移前历史布局/provenance, 不代表当前推荐结构。当前推荐结构见 `data/README.md` 和 `data/datasets/README.md`。

- 目的: 按用户确认的新结构, 将 `data/` 从顶层 `raw/`, `processed/`, `manifests/datasets/` 布局重组为 dataset root 布局, 降低 `processed` 命名歧义, 让 raw 与 entries 可通过同一 `sample_id` 直接对应。
- 目标结构:
  - `data/datasets/<dataset_id>/raw/<sample_id>/...`
  - `data/datasets/<dataset_id>/entries/index.jsonl`
  - `data/datasets/<dataset_id>/entries/<sample_id>/entry.json`
  - `data/datasets/<dataset_id>/splits/`
  - `data/datasets/<dataset_id>/views/`
  - `data/datasets/<dataset_id>/manifests/{raw,entries,lineage}/`
  - `data/catalog/`
  - `data/templates/third_party_audit/`
- 已迁移 dataset:
  - `rgroup_smoke`: 3 个 raw sample, 3 条 `entries/index.jsonl` 记录, 3 个 per-sample `entry.json`。
  - `rgroup_smoke_plus`: 12 个 raw sample, 12 条 `entries/index.jsonl` 记录, 12 个 per-sample `entry.json`。
- 已同步更新:
  - `data/README.md`, `data/CLAUDE.md`, `data/datasets/**/README.md`, `data/catalog/dataset_catalog_v1.json`, `data/catalog/rcsb_smoke_raw_reconciliation_v1.json`。
  - `configs/data/*`, `configs/baselines/*`, `configs/feedback/*`, `scripts/*`, `src/pfr/data/manifest.py`, `tests/test_download_smoke_complexes.py` 等活跃路径引用。
  - `scripts/data/build_rgroup_dataset.py` 现在写 `entries/index.jsonl` 时也会写 `entries/<sample_id>/entry.json`, 并保留原有字段, 追加 `dataset_id`, `dataset_version`, `sample_id`, `entry_path`, `provenance.entry_collection_path`。
- 新增迁移记录: `data/catalog/dataset_layout_migration_20260604_v1.json`。
- 保留边界:
  - 未修改 `.gitignore`。
  - 未执行 `git add`, `git rm`, `git commit`, `git push`。
  - 未重算实验结果。
  - raw 文件内容未被清洗或改写; 只是从旧 root 迁移到 dataset-local `raw/<sample_id>/`。
  - 历史实验日志和历史 output metadata 中的旧路径可作为 provenance 保留, 不代表当前活跃布局。

## 2026-06-07 / data templates 退役

- 目的: 删除未接入 `schemas/` 的 `data/templates/` 模板目录, 明确第三方 audit 生成内容应参考 `schemas/audit/`, 稳定协议和模板配置应进入 `configs/audit/` 或 `configs/third_party/`, 不再放入 `data/`。
- 已删除 `data/templates/` 及其 `third_party_audit/` 下的旧模板 JSON。
- 已更新活跃引用:
  - `scripts/third_party/run_diffsbdd_instrumented.py` 和 `scripts/third_party/run_difflinker_instrumented.py`: `leakage_report_path` 改为 `null`, 不再指向已删除 checklist。
  - `data/catalog/dataset_catalog_v1.json`: 移除 `third_party_audit_templates` 全局模板登记, 并更新 `created_or_updated`。
  - `README.md`, `AGENTS.md`, `data/README.md`, `docs/STATUS.md`: 移除或更新 `data/templates/` 当前结构说明。
- 历史 `docs/report/**`, `docs/EXPERIMENT_LOG.md` 旧条目和 `outputs/**` 中的旧路径保留为 historical provenance, 不代表当前推荐结构。
- 验证: `data/catalog/dataset_catalog_v1.json` JSON 解析通过; 活跃 `scripts/`, `data/`, `README.md`, `AGENTS.md`, `docs/STATUS.md` 不再依赖 `data/templates/`。

## 2026-06-07 / third-party audit MVP schema 补齐

- 目的: 为第三方 audit MVP 中会生成但原先缺少格式合同的文件补充 `schemas/audit/` 规范, 避免继续依赖已退役的 `data/templates/`。
- 新增 schema:
  - `schemas/audit/third_party_output_manifest_v0_1.json`
  - `schemas/audit/third_party_method_resource_check_v0_1.json`
  - `schemas/audit/third_party_blocker_log_v0_1.json`
  - `schemas/audit/third_party_evaluator_tool_result_v0_1.json`
  - `schemas/audit/third_party_diagnosis_sanity_v0_1.json`
- 更新 `schemas/README.md`, 将新增 schema 纳入 audit 清单和用途说明。
- 更新 `scripts/third_party/run_diffsbdd_instrumented.py` 和 `scripts/third_party/run_difflinker_instrumented.py`: 新生成的 `output_manifest.json` 写入 `schema_version=third_party_output_manifest_v0_1` 和对应 `schema_path`。
- 新增 `tests/test_audit_schemas.py`, 检查 audit schema 的 `schema_path` 与实际路径一致。
- 验证:
  - `conda run -n pfr env PYTHONPATH=src pytest -q tests/test_audit_schemas.py tests/test_download_smoke_complexes.py tests/test_smoke_pipeline.py` -> 6 passed。
  - `conda run -n pfr env PYTHONPATH=src python -m py_compile scripts/third_party/run_diffsbdd_instrumented.py scripts/third_party/run_difflinker_instrumented.py` -> 通过。
  - `schemas/audit/*.json` 共 9 个 JSON schema 均可解析。

## 2026-06-07 / third-party audit schema 目录分层重命名

- 目的: 将第三方 audit schema 从泛化的 `schemas/audit/` 迁入更明确的 `schemas/third_party_audit/`, 并按生成对象分子目录管理, 避免文件名继续重复 `third_party_` 前缀。
- 新结构:
  - `schemas/third_party_audit/run/run_metadata_v0_1.json`
  - `schemas/third_party_audit/run/output_manifest_v0_1.json`
  - `schemas/third_party_audit/samples/failure_sample_metadata_v0_1.json`
  - `schemas/third_party_audit/diagnosis/label_v0_1.json`
  - `schemas/third_party_audit/diagnosis/evaluator_tool_result_v0_1.json`
  - `schemas/third_party_audit/diagnosis/diagnosis_sanity_v0_1.json`
  - `schemas/third_party_audit/attrition/stage_attrition_v0_1.json`
  - `schemas/third_party_audit/resources/method_resource_check_v0_1.json`
  - `schemas/third_party_audit/resources/blocker_log_v0_1.json`
- 已同步更新活跃 wrapper、audit summary 脚本、third-party protocol config、`schemas/README.md`、`outputs/README.md`、`docs/STATUS.md` 和 `tests/test_audit_schemas.py`。
- 新生成的第三方 audit metadata 现在使用去前缀后的 `schema_version`, 例如 `run_metadata_v0_1`, `failure_sample_metadata_v0_1`, `output_manifest_v0_1`, `stage_attrition_v0_1`。
- 历史 `docs/report/**`, 旧日志条目和既有 `outputs/**` 中的 `schemas/audit/third_party_*` 路径保留为 historical provenance, 不代表当前推荐路径。
- 验证:
  - `rg --no-ignore --hidden -n "schemas/audit/|third_party_(run_metadata|failure_sample_metadata|label_schema|stage_attrition|output_manifest|method_resource_check|blocker_log|evaluator_tool_result|diagnosis_sanity)_v0_1" schemas tests scripts configs README.md AGENTS.md outputs/README.md data/README.md docs/STATUS.md docs/plan` -> 无活跃残留。
  - `conda run -n pfr env PYTHONPATH=src python -c "...json.loads..."` -> `parsed 9 third_party_audit schemas`。
  - `conda run -n pfr env PYTHONPATH=src pytest -q tests/test_audit_schemas.py tests/test_download_smoke_complexes.py tests/test_smoke_pipeline.py` -> 6 passed。
  - `conda run -n pfr env PYTHONPATH=src python -m py_compile scripts/third_party/run_diffsbdd_instrumented.py scripts/third_party/run_difflinker_instrumented.py scripts/audit/summarize_stage_attrition.py` -> 通过。

## 2026-06-07 / config schema refs 补齐

- 目的: 让 `configs/audit/`, `configs/data/`, `configs/third_party/` 中保留的项目级配置文件明确声明自己的 schema 来源和版本, 避免 config 与 metadata schema 混淆。
- 新增 `schemas/configs/`:
  - `schemas/configs/audit/diagnosis_label_config_v0_1.json`
  - `schemas/configs/audit/denominator_statistics_config_v0_1.json`
  - `schemas/configs/audit/resource_budget_config_v0_1.json`
  - `schemas/configs/audit/tool_versions_lock_v0_1.json`
  - `schemas/configs/data/rgroup_dataset_config_v0_1.json`
  - `schemas/configs/data/rcsb_download_config_v0_1.json`
  - `schemas/configs/third_party/method_protocol_config_v0_1.json`
- 已给 `configs/audit/`, `configs/data/`, `configs/third_party/` 下 14 个配置文件补充顶部 `schema_version` 和 `schema_path`。
- 已更新 `configs/README.md`, `configs/AGENTS.md`, `schemas/README.md`, `schemas/AGENTS.md` 和 `docs/STATUS.md`。
- 新增 `tests/test_config_schema_refs.py`, 检查 config 文件声明的 schema ref 与 `schemas/configs/` 中的 const 一致。
- 验证:
  - `conda run -n pfr env PYTHONPATH=src python -c "...json.loads..."` -> `parsed 7 config schemas`。
  - `conda run -n pfr env PYTHONPATH=src python -c "...yaml.safe_load..."` -> `parsed 14 config files`。
  - `conda run -n pfr env PYTHONPATH=src pytest -q tests/test_config_schema_refs.py tests/test_audit_schemas.py tests/test_download_smoke_complexes.py tests/test_smoke_pipeline.py` -> 7 passed。

## 2026-06-07 / configs template cleanup

- 目的: 按当前定义收紧 `configs/`: 项目级 `configs/` 只保留真实规则、数据构建配置和第三方方法状态/协议记录; 复制填空式 run template 不再放入 `configs/`。
- 已将 RCSB 下载配置从 `configs/data/download_templates/` 迁到 `configs/data/downloads/`, 并更新活跃代码和测试引用:
  - `src/pfr/data/manifest.py`
  - `tests/test_download_smoke_complexes.py`
  - `configs/README.md`
- 已清理 `configs/third_party/`:
  - `diffsbdd_original_protocol.yaml` -> `diffsbdd_method_status.yaml`
  - `difflinker_original_protocol.yaml` -> `difflinker_method_status.yaml`
  - `pocket2mol_audit_protocol.yaml` -> `pocket2mol_method_status.yaml`
  - `targetdiff_audit_protocol.yaml` -> `targetdiff_method_status.yaml`
  - 移除 project-level `diffsbdd_audit_protocol.yaml` 和 `difflinker_audit_protocol.yaml`; 当前以 `experiments/20260603-01-third-party-failure-audit-mvp/configs/resolved/third_party/` 下的 resolved protocol 为准。
- 已给上述 resolved third-party protocol 补充 `schema_version`, `schema_path` 和 `metadata_schemas`。
- 已更新 `README.md`, `AGENTS.md`, `configs/README.md`, `configs/AGENTS.md`, `docs/STATUS.md`, `docs/plan/20260604-02-third-party-audit-mvp-output-capture-plan.md`。
- 已扩展 `tests/test_config_schema_refs.py`, 禁止 project-level `configs/` 中出现 `{experiment_id}`, `{run_id}`, `{n_samples}` 或 `mvp_trial_template_not_executed` 这类 run template 占位。
- 历史 `docs/EXPERIMENT_LOG.md`, `docs/report/**`, 迁移 manifest 和旧 outputs 中的旧路径保留为 provenance, 不代表当前推荐结构。
- 验证:
  - `rg --no-ignore --hidden -n "download_templates|configs/third_party/(diffsbdd_audit_protocol|difflinker_audit_protocol)\\.yaml|mvp_trial_template_not_executed|\\{experiment_id\\}|\\{run_id\\}|\\{n_samples\\}" configs src tests README.md AGENTS.md docs/STATUS.md docs/plan outputs/README.md schemas/README.md schemas/AGENTS.md` -> 仅命中 `tests/test_config_schema_refs.py` 中的 forbidden token 列表。
  - `conda run -n pfr env PYTHONPATH=src python -c "...yaml.safe_load..."` -> `parsed 14 config files`。
  - `conda run -n pfr env PYTHONPATH=src pytest -q tests/test_config_schema_refs.py tests/test_audit_schemas.py tests/test_download_smoke_complexes.py tests/test_smoke_pipeline.py` -> 8 passed。

## 2026-06-07 / configs data downloads-builds 分层

- 目的: 将 `configs/data/` 下 raw 下载配置和 canonical dataset 构建配置分开管理, 避免 `downloads/` 与根目录 build config 混放。
- 新结构:
  - `configs/data/downloads/rcsb_smoke.yaml`
  - `configs/data/downloads/rcsb_smoke_plus.yaml`
  - `configs/data/builds/rgroup_smoke.yaml`
  - `configs/data/builds/rgroup_smoke_plus.yaml`
- 已更新活跃引用:
  - `scripts/setup/smoke_pipeline_dry_run.py`: 默认 `build_rgroup_dataset` config 改为 `configs/data/builds/rgroup_smoke.yaml`。
  - `data/datasets/rgroup_smoke/manifests/entries/rgroup_smoke_entries_manifest_v1.json`: `build_config_path` 改为新 build config 路径。
  - `data/datasets/rgroup_smoke_plus/manifests/entries/rgroup_smoke_plus_entries_manifest_v1.json`: `build_config_path` 改为新 build config 路径。
  - `configs/README.md`, `configs/AGENTS.md`, `docs/STATUS.md`: 明确 `downloads/` = raw 数据怎么下载, `builds/` = raw 数据怎么构建成 canonical dataset。
- 历史 `docs/EXPERIMENT_LOG.md`, 迁移 manifest 或旧实验 metadata 中的 `configs/data/rgroup_smoke*.yaml` 旧路径保留为 provenance, 不代表当前推荐路径。
- 验证:
  - `find configs/data -maxdepth 1 -type f` -> 无输出, `configs/data` 根下不再散放配置文件。
  - `rg --no-ignore --hidden -n "configs/data/rgroup_smoke|configs/data/rgroup_smoke_plus|configs/data/download_templates" configs src tests README.md AGENTS.md docs/STATUS.md docs/plan schemas/README.md schemas/AGENTS.md data scripts` -> 无活跃残留。
  - `conda run -n pfr env PYTHONPATH=src pytest -q tests/test_config_schema_refs.py tests/test_download_smoke_complexes.py tests/test_smoke_pipeline.py` -> 7 passed。
  - `conda run -n pfr env PYTHONPATH=src python scripts/setup/smoke_pipeline_dry_run.py` -> dry-run plan 使用 `configs/data/builds/rgroup_smoke.yaml`, 未写入文件。

## 2026-06-07 / schemas configs data downloads-builds 分层

- 目的: 让 `schemas/configs/data/` 与 `configs/data/` 保持同构分层, 区分 raw 下载配置 schema 和 canonical dataset 构建配置 schema。
- 新结构:
  - `schemas/configs/data/downloads/rcsb_download_config_v0_1.json`
  - `schemas/configs/data/builds/rgroup_dataset_config_v0_1.json`
- 已更新:
  - 两个 schema 文件内部 `$id` 和 `schema_path.const`。
  - `configs/data/downloads/rcsb_smoke*.yaml` 的 `schema_path`。
  - `configs/data/builds/rgroup_smoke*.yaml` 的 `schema_path`。
  - `schemas/README.md` 和 `schemas/AGENTS.md`。
- 验证:
  - `conda run -n pfr env PYTHONPATH=src python -c "...json.loads..."` -> `parsed 7 config schemas`。
  - `rg --no-ignore --hidden -n "schemas/configs/data/(rgroup_dataset_config|rcsb_download_config)_v0_1\\.json" schemas configs tests docs/STATUS.md docs/plan README.md AGENTS.md data scripts src` -> 无活跃残留。
  - `conda run -n pfr env PYTHONPATH=src pytest -q tests/test_config_schema_refs.py tests/test_audit_schemas.py tests/test_download_smoke_complexes.py tests/test_smoke_pipeline.py` -> 8 passed。

## 2026-06-07 / config schema mapping 子 agent 复核修补

- 目的: 用子 agent 独立复核新会话是否能从仓库文件恢复 config/schema 映射关系, 并补齐其发现的小风险。
- 子 agent 结论: AGENTS 入口和 README 映射主体完整; 仍建议补 `environment_ml_optional.yml` 例外说明、修正 `data/AGENTS.md` 旧“模板配置”措辞、加强测试约束。
- 已修补:
  - `configs/README.md`: 明确 `configs/environment_ml_optional.yml` 是标准 Conda environment 文件例外, 不要求本项目 `schema_version` / `schema_path`。
  - `data/AGENTS.md`: 将旧“稳定协议和模板配置”改为第三方 audit 规则、第三方方法状态/协议记录和 schema 合同的当前分工。
  - `tests/test_config_schema_refs.py`: 新增检查 `configs/data/` 和 `schemas/configs/data/` 根下不能散放文件, 并检查 resolved third-party protocol 的 `metadata_schemas` 均指向存在的 schema。
- 验证:
  - `find configs/data -maxdepth 1 -type f -print; find schemas/configs/data -maxdepth 1 -type f -print` -> 无输出。
  - `conda run -n pfr env PYTHONPATH=src pytest -q tests/test_config_schema_refs.py tests/test_audit_schemas.py tests/test_download_smoke_complexes.py tests/test_smoke_pipeline.py` -> 10 passed。

## 2026-06-07 / DiffSBDD 单方法 third-party audit MVP sanity run

- 目的: 按 `docs/plan/20260607-01-diffsbdd-single-method-third-party-audit-mvp-plan.md` 只执行 DiffSBDD 单方法 MVP sanity, 跑通最小 inference -> output capture -> metadata/denominator -> evaluator/diagnosis wiring。未执行 DiffLinker, 未做 cross-method comparison, 未声明 formal failure prevalence, official reproduction 或 repair benchmark result。
- 实验身份:
  - `experiment_name=diffsbdd-single-method-third-party-audit-mvp`
  - `experiment_id=20260607-01-diffsbdd-single-method-third-party-audit-mvp`
  - `run_id=r001_seed0_budget3_3rfm_47b93b20`
- Go/no-go resource check:
  - 写入 `experiments/20260607-01-diffsbdd-single-method-third-party-audit-mvp/metadata/method_resource_check.jsonl`, `decision=go`, `resource_status=ready`, `blockers=[]`。
  - DiffSBDD repo: `third_party/diffsbdd`, remote `https://github.com/arneschneuing/DiffSBDD.git`, commit `5d0d38d16c8932a0339fd2ce3f67ade98bbdff27`, license `MIT`。
  - Checkpoint: `third_party/diffsbdd/checkpoints/crossdocked_fullatom_cond.ckpt`, size `17861341` bytes, sha256 `07f86764bf569aafbc40a9c15fc02de8e2550437dd0f17f657eab3abe66c372c`, access type `public`, checksum matched configured value。
  - Example input: `third_party/diffsbdd/example/3rfm.pdb`, reference ligand `A:330`。
  - Training/leakage: `training_data_status=training_data_unknown`, `leakage_check_status=unknown_risk`; 因此本轮只作为 MVP sanity wiring, 不能作为 clean formal conclusion。
- 环境:
  - 创建并使用独立 method inference 环境 `pfr-diffsbdd`, 不与 evaluator 环境混用。
  - 环境记录写入 `experiments/20260607-01-diffsbdd-single-method-third-party-audit-mvp/metadata/env_info.json`, `conda_export.yml`, `pip_freeze.txt`。
  - `pfr-diffsbdd` 关键版本: Python `3.10.19`, torch `2.0.1`, CUDA `11.8`, pytorch-lightning `1.8.4`, RDKit `2022.03.2`, OpenBabel `3.1.0`, setuptools pinned to `80.10.2` 以恢复 `pkg_resources` 兼容性。
- Resolved config:
  - `experiments/20260607-01-diffsbdd-single-method-third-party-audit-mvp/configs/resolved/third_party/diffsbdd_single_method_mvp_trial.yaml`, sha256 `47b93b2080d6006c3d13210f1e6392154040f1989b2f822ed4a448f244949226`。
  - 复用并归档 `diffsbdd_method_status.yaml`, 20260603 resolved protocol, `resource_budget_v1.yaml`, `tool_versions.lock`。
- Inference 与 output capture:
  - 使用 `scripts/third_party/run_diffsbdd_instrumented.py` 跑官方 3RFM example 的 budget-reduced MVP sanity: `seed=0`, `n_samples=3`。
  - 首次尝试因 seeded launcher 未把 DiffSBDD repo 加入 `sys.path` 失败, 已归档到 `outputs/20260607-01-diffsbdd-single-method-third-party-audit-mvp/diffsbdd/r001_seed0_budget3_3rfm_47b93b20/logs/attempt_001_seed_launcher_sys_path_failure/`。
  - 修复 launcher 后 run 完成: `status=completed`, `exit_code=0`, `N_budget=3`, `N_raw_attempt_metadata=3`, `N_raw_captured=3`, `N_final=3`, `N_missing_output=0`, `N_pipeline_failure=0`, `N_tool_failure=0`。
  - raw output 保留在 `captured_outputs/generated.sdf`, sha256 `48cdd08b1d09d5beb2e33638a83254d2d18d2d211e75ca6acafe4abbeebc7d4e`; normalized samples 写入 `processed/normalized_samples/sample_000.sdf` 至 `sample_002.sdf`, 并在 `samples.jsonl` 中逐行保留 sample metadata。
  - SDF splitting 曾发现空 title line 被剥离导致 RDKit parse 失败, 已修正为保留合法 SDF record 结构; `pfr-eval-tools` 中 3 个 normalized SDF 均 `parsed sanitized`。
- Evaluator / diagnosis wiring:
  - 新增实验专用 runner `experiments/20260607-01-diffsbdd-single-method-third-party-audit-mvp/scripts/run_mvp_evaluator.py`。
  - 使用 `pfr-eval-tools` 跑 RDKit, PoseBusters `mol`, PoseBusters `dock`, optional PLIP, optional Vina。
  - 输出 `evaluator/evaluator_input.jsonl`, `evaluator/evaluator_tool_results.jsonl`, `evaluator/diagnosis_sanity.jsonl`, `evaluator/raw_tool_outputs/posebusters_*.json`, `summaries/evaluator_summary.json`。
  - Tool result rows: `15`; diagnosis rows: `3`。
  - Tool status counts: `rdkit::passed=3`, `plip::passed=3`, `vina::passed=3`, `posebusters_mol::failed=3`, `posebusters_dock::failed=3`。
  - 代表性 PoseBusters `mol` failure 为 `mol_true_loaded`, 与 MVP 未传 true/reference ligand 给该检查有关; `dock` 代表性 failed checks 包括 `minimum_distance_to_organic_cofactors`, `volume_overlap_with_organic_cofactors`, `mol_true_loaded`, `most_extreme_clash_protein`, `not_too_far_away_inorganic_cofactors`, `not_too_far_away_waters`。这些仅作为 sanity evaluator evidence, 未生成正式 labels。
- Schema / denominator 验证:
  - 所有本轮项目自有 JSON/JSONL metadata 均写入 `schema_version` 和 `schema_path`。
  - 轻量 schema subset validator 检查 `method_resource_check.jsonl`, `env_info.json`, `run_metadata.json`, `samples.jsonl`, `output_manifest.json`, `stage_attrition.json`, `evaluator_tool_results.jsonl`, `diagnosis_sanity.jsonl`, `mvp_generation_summary.json`, `evaluator_summary.json` -> `schema_subset_validation=passed rows_checked=28 files_checked=10`。
  - `stage_attrition.json` 明确记录 denominator 来自 sample metadata rows, 不是仅按 SDF 文件数推断; post-evaluator `N_evaluable=3`, `N_parsed=3`, `N_rdkit_valid=3`, `N_docking_attempted=3`, `N_docking_failed=3`。
- 代码与 schema 支撑:
  - `scripts/third_party/run_diffsbdd_instrumented.py`: 增加 seed/experiment/config 参数, seeded launcher, normalized sample splitting, required output dirs, schema refs, generation summary。
  - `scripts/eval/eval_posebusters_one.py` 和 `scripts/eval/eval_official_tools.py`: 增加 PoseBusters config 参数, 支持 MVP 使用 `mol` / `dock` 而非默认 `redock`。
  - 新增 `schemas/third_party_audit/resources/environment_info_v0_1.json` 和 `schemas/third_party_audit/diagnosis/mvp_sanity_summary_v0_1.json`, 并更新 `schemas/README.md`。
- 验证:
  - `conda run -n pfr-eval-tools python ...RDKit normalized SDF parse check...` -> `sample_000.sdf parsed sanitized`, `sample_001.sdf parsed sanitized`, `sample_002.sdf parsed sanitized`。
  - `conda run -n pfr-eval-tools python experiments/20260607-01-diffsbdd-single-method-third-party-audit-mvp/scripts/run_mvp_evaluator.py --run-root outputs/20260607-01-diffsbdd-single-method-third-party-audit-mvp/diffsbdd/r001_seed0_budget3_3rfm_47b93b20` -> `tool_result_rows=15`, `diagnosis_rows=3`。
  - `python tmp/20260607-diffsbdd-schema-validate/validate_outputs.py` -> `schema_subset_validation=passed rows_checked=28 files_checked=10`。
  - `conda run -n pfr env PYTHONPATH=src pytest -q` -> `32 passed in 0.79s`。
- 当前结论:
  - DiffSBDD 单方法 third-party audit MVP sanity 闭环已跑通: resource check, minimal inference, output capture, sample metadata, denominator, evaluator/diagnosis wiring 和 blocker/coverage 记录均可回溯。
  - 当前没有 go/no-go active blocker; 仍保留 training/leakage unknown risk, 因此不做 formal prevalence 或 clean generalization claim。
- 下一步:
  - 在单独计划中运行 DiffLinker MVP sanity, 不与本轮 DiffSBDD 混合统计。
  - formal audit 前冻结 PoseBusters/RDKit/PLIP/Vina rule config, 明确 `mol_true_loaded` 等 reference-dependent checks 的解释口径, 再进入 analysis-frozen gate。

## 2026-06-08 / DiffSBDD 阶段 1 原协议健全性与忠实度 sanity

- 目的: 按 `docs/plan/20260608-02-diffsbdd-original-protocol-sanity-plan.md` 落地 DiffSBDD 阶段 1, 先读官方论文, README 和关键代码, 形成原协议摘录, 再运行官方 README 3RFM 示例规模 sanity。未做完整原论文复现, 未做 formal failure prevalence, 未做 cross-method comparison, 未做 repair benchmark。
- 实验身份:
  - `experiment_name=diffsbdd-original-protocol-sanity`
  - `experiment_id=20260608-01-diffsbdd-original-protocol-sanity`
  - `run_id=r001_official_example_3rfm_seed0_78d8cd91`
- 官方材料阅读与协议摘录:
  - 阅读官方论文 `Structure-based drug design with equivariant diffusion models`, DOI `10.1038/s43588-024-00737-x`, arXiv `2210.13695`, 官方 README 和关键代码。
  - 关键代码包括 `third_party/diffsbdd/generate_ligands.py`, `test.py`, `lightning_modules.py`, `analysis/molecule_builder.py`, `analysis/metrics.py`, `analysis/docking.py`。
  - 写入 `experiments/20260608-01-diffsbdd-original-protocol-sanity/metadata/official_protocol_excerpt.md`。
  - 新增并使用 `schemas/third_party_audit/resources/official_protocol_checklist_v0_1.json`, checklist 写入 `experiments/20260608-01-diffsbdd-original-protocol-sanity/metadata/official_protocol_checklist.json`。
- Resolved config 与资源检查:
  - 写入 `experiments/20260608-01-diffsbdd-original-protocol-sanity/configs/resolved/third_party/diffsbdd_original_protocol_sanity.yaml`, sha256 `78d8cd918b5d2e6171aaa720ad14be162567f2854c76031d426a48387d927775`。
  - 复用并归档 `resource_budget_v1.yaml`, `tool_versions.lock`, `diffsbdd_method_status.yaml`, 以及 20260603 DiffSBDD audit protocol source。
  - `method_resource_check.jsonl`: `decision=go`, 仅针对 README 3RFM 示例 sanity。
  - Repo: `third_party/diffsbdd`, commit `5d0d38d16c8932a0339fd2ce3f67ade98bbdff27`, license `MIT`。
  - Checkpoint: `crossdocked_fullatom_cond.ckpt`, official Zenodo source, size `17861341` bytes, sha256 `07f86764bf569aafbc40a9c15fc02de8e2550437dd0f17f657eab3abe66c372c`, access type `public`。
  - Resource evidence: method tree `30M`, workspace free disk `385G`, GPU `NVIDIA GeForce RTX 3090, 24576 MiB total, 24097 MiB free`。
  - `r002_official_like_test_subset` deferred, 因为 processed test data, split 和 checksum 未获取或冻结。
- 环境:
  - DiffSBDD inference 使用 `pfr-diffsbdd`, evaluator 使用 `pfr-eval-tools`, 两者不混用。
  - 方法环境记录: `metadata/env_info.json`, `conda_export.yml`, `pip_freeze.txt`。
  - evaluator 环境记录: `metadata/evaluator_env_info.json`, `evaluator_conda_export.yml`, `evaluator_pip_freeze.txt`。
- Inference 与 output capture:
  - 使用 `scripts/third_party/run_diffsbdd_instrumented.py` 运行 README 3RFM example: `--pdbfile example/3rfm.pdb --ref_ligand A:330 --n_samples 20 --seed 0`。
  - wrapper 仅设置 seed, 捕获输出, 写 metadata, 拆分 SDF, 未修改 DiffSBDD sampling, decoding, filtering, reranking, docking config 或 success definition。
  - Run 完成: `exit_code=0`, `status=completed`, `N_budget=20`, `N_raw_attempt_metadata=20`, `N_raw_captured=20`, `N_final=20`, `N_missing_output=0`, `N_pipeline_failure=0`。
  - 输出保留在 `outputs/20260608-01-diffsbdd-original-protocol-sanity/diffsbdd/r001_official_example_3rfm_seed0_78d8cd91/`, 包括 `captured_outputs/generated.sdf`, `processed/normalized_samples/sample_000.sdf` 至 `sample_019.sdf`, `run_metadata.json`, `samples.jsonl`, `output_manifest.json`, `stage_attrition.json`, `logs/`, `manifests/`, `evaluator/`, `summaries/`, `official_like_metrics/`。
- Official-like 基础指标:
  - 新增 `experiments/20260608-01-diffsbdd-original-protocol-sanity/scripts/compute_basic_official_like_metrics.py`, 在 `pfr-diffsbdd` 中复用 DiffSBDD `analysis.metrics` 相关逻辑。
  - `basic_molecular_metrics.json`: `N_budget=20`, `N_parsed=20`, `N_valid=20`, `N_connected=20`, `N_unique_connected_smiles=20`。
  - `validity_over_budget=1.0`, `connectivity_over_valid=1.0`, `uniqueness_over_connected=1.0`, `novelty=null`, novelty 未计算原因是 training SMILES / official train set provenance 未冻结。
- Evaluator / diagnosis wiring:
  - 新增阶段 1 evaluator runner `experiments/20260608-01-diffsbdd-original-protocol-sanity/scripts/run_stage1_evaluator.py`。
  - 初次 evaluator 在 sample index `11` 的 PoseBusters `mol` 调用外层 75s timeout 后中断, 已修补为超时写 `timeout` tool row 并继续, 同时复用已生成的 raw PoseBusters 输出。
  - 最终 evaluator 输出: `tool_result_rows=100`, `diagnosis_rows=20`。
  - Tool status counts: `rdkit::passed=20`, `plip::passed=20`, `vina::passed=20`, `posebusters_mol::failed=19`, `posebusters_dock::failed=19`, `posebusters_mol::timeout=1`, `posebusters_dock::timeout=1`。
  - Diagnosis evaluability: `evaluable=19`, `not_evaluable_tool_failure=1`, 对应 sample index `11` 的 PoseBusters mol/dock timeout。
  - PoseBusters failure/timeout 仅作为 stage 1 evaluator wiring evidence, 不解释为 DiffSBDD formal failure prevalence。
- Schema / metadata 验证:
  - `pfr` 和 `pfr-eval-tools` 均无 `jsonschema`, 因此本轮做轻量 required/const/schema ref 检查。
  - 检查 `official_protocol_checklist.json`, `env_info.json`, `evaluator_env_info.json`, `method_resource_check.jsonl`, `run_metadata.json`, `samples.jsonl`, `output_manifest.json`, `stage_attrition.json`, `evaluator_tool_results.jsonl`, `diagnosis_sanity.jsonl`, `evaluator_summary.json`, `mvp_generation_summary.json`, `basic_molecular_metrics.json` -> `passed_lightweight_required_const_check`, `metadata_items=13`, `rows_or_files_checked=150`。
  - RDKit sanity: 20 个 normalized SDF 均 parse ok, sanitize ok。
- 报告:
  - 写入 `docs/report/20260608-02-diffsbdd-original-protocol-sanity-report.md`。
- 验证:
  - `conda run -n pfr-diffsbdd python experiments/20260608-01-diffsbdd-original-protocol-sanity/scripts/compute_basic_official_like_metrics.py --run-root outputs/20260608-01-diffsbdd-original-protocol-sanity/diffsbdd/r001_official_example_3rfm_seed0_78d8cd91` -> `N_parsed=20`, `N_valid=20`, `N_connected=20`。
  - `conda run -n pfr-eval-tools python experiments/20260608-01-diffsbdd-original-protocol-sanity/scripts/run_stage1_evaluator.py --run-root outputs/20260608-01-diffsbdd-original-protocol-sanity/diffsbdd/r001_official_example_3rfm_seed0_78d8cd91` -> `tool_result_rows=100`, `diagnosis_rows=20`。
  - `conda run -n pfr env PYTHONPATH=src pytest -q` -> `32 passed in 0.76s`。
- 当前结论:
  - DiffSBDD 阶段 1 的 README 3RFM 官方示例 sanity 已完成。它证明本项目可以按接近官方 README 示例的设置运行 DiffSBDD 并完成 output capture, denominator, official-like basic metrics 和 evaluator wiring。
  - 这仍不是完整原论文复现。完整 `test.py` 官方风格测试子集需要先冻结数据来源, split, checksum, license 和资源预算。
- 下一步:
  - 若继续阶段 1 子任务, 先为 `test.py` 子集做单独 resource/data gate。
  - 若进入阶段 2, 使用本阶段偏离表更新 DiffSBDD audit protocol, 扩大样本量前冻结 evaluator/diagnosis protocol。

## 2026-06-08 / DiffSBDD 阶段 1 PoseBusters timeout 样本复查

- 目的: 对阶段 1 原始 evaluator 中 sample index `11` 的 PoseBusters `mol` 和 `dock` timeout 做长等待复查, 判断是否只是 timeout 过短.
- 输入:
  - run: `outputs/20260608-01-diffsbdd-original-protocol-sanity/diffsbdd/r001_official_example_3rfm_seed0_78d8cd91/`
  - evaluator input: `evaluator/evaluator_input.jsonl`
  - sample index: `11`
  - sample id: `diffsbdd_diffsbdd_example_3rfm_5ndu_v1_3rfm_final_11`
- 原策略:
  - stage 1 evaluator 内层 `--timeout=30` 秒, 外层 `subprocess.run(... timeout=45)` 秒.
  - 原始结果记录为 `posebusters_mol::timeout=1`, `posebusters_dock::timeout=1`.
- 复查策略:
  - `timeout 420s conda run -n pfr-eval-tools python scripts/eval/eval_posebusters_one.py ... --index 11 --timeout 300 --config mol`
  - `timeout 420s conda run -n pfr-eval-tools python scripts/eval/eval_posebusters_one.py ... --index 11 --timeout 300 --config dock`
- 复查输出:
  - `evaluator/raw_tool_outputs/retry_timeout300/posebusters_mol_011.json`
  - `evaluator/raw_tool_outputs/retry_timeout300/posebusters_dock_011.json`
  - `summaries/posebusters_timeout300_retry_summary.json`
- 复查结果:
  - `mol` 完成, `posebusters_full_pass=false`, `posebusters_num_passed=14`, `posebusters_num_checks=16`, failed checks 为 `bond_lengths`, `mol_true_loaded`.
  - `dock` 完成, `posebusters_full_pass=false`, `posebusters_num_passed=23`, `posebusters_num_checks=30`, failed checks 为 `bond_lengths`, `minimum_distance_to_organic_cofactors`, `volume_overlap_with_organic_cofactors`, `mol_true_loaded`, `most_extreme_clash_protein`, `not_too_far_away_inorganic_cofactors`, `not_too_far_away_waters`.
- 结论:
  - sample index `11` 的 PoseBusters 原始 timeout 主要说明 45 秒外层 timeout 对该样本过短.
  - 延长等待后工具可以完成, 结果从 timeout 转为 failed checks.
  - 原始 evaluator rows 保留当时 timeout 策略下的事实, 不静默改写正式阶段 1 outputs.
  - 该复查仍只作为 stage 1 sanity/evaluator evidence, 不作为 formal failure prevalence.

## 2026-06-08 / 统一评估流水线对齐落地

- 目的: 按 `docs/plan/20260608-03-unified-evaluation-pipeline-alignment-plan.md` 落地第三方审计统一评估流水线 v0.1. 本轮不重新运行 DiffSBDD inference, 使用阶段 1 README 3RFM 示例 20 个 final SDF 样本作为输入.
- 实验身份:
  - `experiment_name=unified-evaluation-pipeline-alignment`
  - `experiment_id=20260608-02-unified-evaluation-pipeline-alignment`
  - `run_id=r001_frozen_eval_diffsbdd_stage1_3rfm_78d8cd91`
- 新增配置和 schema:
  - `configs/audit/receptor_prep_policy_v0_1.yaml`
  - `configs/audit/evaluator_policy_v0_1.yaml`
  - `configs/audit/analysis_frozen_gate_v0_1.yaml`
  - `configs/audit/diagnosis_label_config_v0_2.yaml`
  - 新增 receptor prep record/index, evaluator input, label summary, prevalence summary 和 analysis-frozen gate result schema.
- 新增脚本:
  - `scripts/eval/audit_common.py`
  - `scripts/eval/prepare_receptor.py`
  - `scripts/eval/run_audit_evaluators.py`
  - `scripts/eval/build_audit_labels.py`
  - `scripts/eval/summarize_audit_labels.py`
  - `scripts/eval/check_analysis_frozen_gate.py`
  - `scripts/eval/eval_official_tools.py` 更新为优先使用 frozen pocket box, 并记录 Vina box source, PDBQT sha256 和 score comparability.
- Receptor preparation:
  - 输入 `third_party/diffsbdd/example/3rfm.pdb`, reference ligand `A:330`.
  - 输出 `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r001_frozen_eval_diffsbdd_stage1_3rfm_78d8cd91/processed/receptors/`.
  - 删除 `CFF A:330`, cleaned receptor atom count `2250`, raw hetero group count `1`, cleaned hetero group count `0`, `unresolved_review_required_count=0`.
  - Vina box center `[7.7566, -33.4076, -32.8478]`, size `[14.054, 12.0, 12.299]`, source `reference_ligand_heavy_atom_centroid`.
- Frozen evaluator:
  - 输入源 run: `outputs/20260608-01-diffsbdd-original-protocol-sanity/diffsbdd/r001_official_example_3rfm_seed0_78d8cd91/`.
  - 输出 run: `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r001_frozen_eval_diffsbdd_stage1_3rfm_78d8cd91/`.
  - 使用 `pfr-eval-tools` 运行 RDKit, PoseBusters `mol`, PoseBusters `dock`, PLIP, Vina score-only.
  - Tool result rows `100`.
  - Tool status counts: `rdkit::passed=20`, `posebusters_mol::passed=15`, `posebusters_mol::failed=3`, `posebusters_mol::tool_failure=2`, `posebusters_dock::passed=20`, `plip::passed=20`, `vina::passed=20`.
- Labels / summaries:
  - `labels.jsonl`: 20 rows.
  - `label_summary.json`: `evaluable=18`, `not_evaluable_tool_failure=2`, primary labels `unknown=15`, `local_geometry_failure=3`, `tool_failure=2`, `near_miss_eligible=3`.
  - `prevalence_summary.json`: selected-output residual view `5/20=0.25`; evaluable-only selected-scope view `3/18=0.1667`; inclusive failure burden downgraded, 不声明 raw prevalence.
- Gate:
  - `analysis_frozen_gate_result.json`: `gate_status=failed`.
  - Blocking failures:
    - `posebusters_mol_missing_frozen_columns:diffsbdd_diffsbdd_example_3rfm_5ndu_v1_3rfm_final_11`
    - `posebusters_mol_missing_frozen_columns:diffsbdd_diffsbdd_example_3rfm_5ndu_v1_3rfm_final_16`
  - 原因: v0.1 evaluator policy 把 `internal_energy` 列列入 PoseBusters ligand core frozen columns, 但这两个样本的 PoseBusters `mol` 输出缺少该列. 按规则不能默认 pass, 必须阻塞 formal analysis.
  - Warnings: final-only outputs 只能作为 selected-output residual view; PLIP reference recovery 仅为描述性 evidence; training/leakage status 仍为 unknown risk.
  - Gate sanity set 全部通过.
- 环境记录:
  - `experiments/20260608-02-unified-evaluation-pipeline-alignment/metadata/conda_export.yml`
  - `metadata/pip_freeze.txt`
  - `metadata/env_info.json`
  - `metadata/evaluator_conda_export.yml`
  - `metadata/evaluator_pip_freeze.txt`
  - `metadata/evaluator_env_info.json`
- 报告:
  - `docs/report/20260608-03-unified-evaluation-pipeline-alignment-report.md`.
- 验证:
  - `conda run -n pfr env PYTHONPATH=src pytest -q` -> `36 passed in 0.77s`.
- 当前结论:
  - 统一评估流水线落地完成, 但 analysis-frozen gate 未通过. 当前不能进入更大样本 DiffSBDD formal audit, 不能声明正式 failure prevalence.
  - 下一步应调研 PoseBusters `internal_energy` 缺列条件, 决定保留为 required frozen column, 改为 optional diagnostic column, 或新增 evaluator policy v0.2 后重跑 gate.

## 2026-06-09 / PoseBusters internal_energy 条件冻结规则 v0.2 落地

- 目的: 按 `docs/plan/20260609-01-posebusters-internal-energy-conditional-gate-plan.md` 修正 PoseBusters `internal_energy=NaN` 被 v0.1 wrapper/gate 误表达为 missing frozen column 的问题.
- 版本化规则:
  - 保留 v0.1 配置和 r001 结果语义不变.
  - 新增 `configs/audit/evaluator_policy_v0_2.yaml`, 将 PoseBusters ligand core 的 `internal_energy` 从无条件 required frozen column 改为 conditional column.
  - 新增 `configs/audit/analysis_frozen_gate_v0_2.yaml`, 对 `internal_energy_unavailable_fraction` 设置 MVP sanity 阈值 `0.10`, formal analysis 阈值 `0.05`.
  - 新增 `configs/audit/diagnosis_label_config_v0_3.yaml`, 记录 `posebusters_internal_energy_unavailable`, `high_internal_energy_evidence` 和 `no_core_failure_detected_with_energy_unavailable`.
  - 新增对应 config schema, 并更新 `configs/audit/README.md` 和 `schemas/README.md`.
- 代码改动:
  - `scripts/eval/eval_posebusters_one.py` 保存 JSON-safe full report 值, non-boolean checks, unavailable columns 和 unavailable reasons.
  - `scripts/eval/run_audit_evaluators.py` 区分 required, conditional, failed, missing 和 unavailable columns.
  - `scripts/eval/build_audit_labels.py` 将 `internal_energy=false` 作为高内部能量证据, 将 `internal_energy=NaN/null` 作为附加 unavailable 诊断.
  - `scripts/eval/summarize_audit_labels.py` 和 `scripts/eval/check_analysis_frozen_gate.py` 输出 internal energy coverage.
  - `tests/test_unified_evaluation_pipeline.py` 增加 v0.2 语义和 v0.1 回归测试.
- r002 evaluator:
  - `experiment_id=20260608-02-unified-evaluation-pipeline-alignment`.
  - `run_id=r002_frozen_eval_diffsbdd_stage1_3rfm_v02_fbfc8032`.
  - 输出路径: `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r002_frozen_eval_diffsbdd_stage1_3rfm_v02_fbfc8032/`.
  - 输入源 run 仍为 `outputs/20260608-01-diffsbdd-original-protocol-sanity/diffsbdd/r001_official_example_3rfm_seed0_78d8cd91/`.
  - 使用 v0.1 receptor prep record, 不重新运行 DiffSBDD inference.
- r002 结果:
  - Tool result rows `100`.
  - Tool status counts: `rdkit::passed=20`, `posebusters_mol::passed=15`, `posebusters_mol::failed=5`, `posebusters_dock::passed=20`, `plip::passed=20`, `vina::passed=20`.
  - Labels `20`, 全部 `evaluable`.
  - Primary labels: `unknown=15`, `local_geometry_failure=5`.
  - near_miss_eligible `5`.
  - `internal_energy_false_count=0`.
  - `internal_energy_unavailable_count=2`, fraction `0.10`, sample ids 为 `*_final_11` 和 `*_final_16`.
  - `*_final_11`: `local_geometry_failure`, 主证据 `bond_lengths=false`, 附加 `posebusters_internal_energy_unavailable`.
  - `*_final_16`: `local_geometry_failure`, 主证据 `bond_lengths=false`, `bond_angles=false`, 附加 `posebusters_internal_energy_unavailable`.
- Gate:
  - `analysis_frozen_gate_result.json`: `gate_status=passed_with_warnings`, blocking failures `0`.
  - Warnings: final-only selected-output residual view, training/leakage unknown, PLIP descriptive only, `posebusters_internal_energy_unavailable:*_final_11`, `posebusters_internal_energy_unavailable:*_final_16`, `posebusters_internal_energy_unavailable_coverage:2/20`.
  - `passed_with_warnings` 只表示 required evaluator wiring 和 required frozen columns 可用, 且 conditional `internal_energy` 有 coverage warning; 不表示 PoseBusters 全部评估项完整通过.
- 报告:
  - `docs/report/20260609-01-posebusters-internal-energy-conditional-gate-report.md`.
- 验证:
  - `conda run -n pfr env PYTHONPATH=src pytest -q` -> `43 passed in 0.80s`.
- 当前结论:
  - v0.2 已解决 r001 的 `internal_energy` missing frozen column blocker, 将两个样本从 `tool_failure` 更正为可评价的 `local_geometry_failure` 加 unavailable 诊断.
  - 本轮仍是 selected-output residual 分析, 不能解释为正式 failure prevalence, official reproduction 或 repair benchmark result.

## 2026-06-09 / PoseBusters raw wrapper 输出 schema 化

- 目的: 为 `evaluator/raw_tool_outputs/posebusters_*.json` 补充项目自有 raw PoseBusters result schema, 让 raw wrapper 输出也具备 `schema_version` 和 `schema_path`.
- 新增 schema:
  - `schemas/third_party_audit/diagnosis/posebusters_raw_result_v0_1.json`.
- 代码和文档更新:
  - `scripts/eval/eval_posebusters_one.py` 的 `base_result` 写入 `schema_version=posebusters_raw_result_v0_1` 和 `schema_path=schemas/third_party_audit/diagnosis/posebusters_raw_result_v0_1.json`.
  - `scripts/eval/run_audit_evaluators.py` 和 `scripts/eval/check_analysis_frozen_gate.py` 的 output manifest schema 映射增加 `posebusters_raw_result`.
  - `schemas/README.md` 的第三方 audit 输出文件映射增加 PoseBusters raw wrapper JSON.
  - `configs/README.md` 的 `metadata_schemas` key 映射增加 `posebusters_raw_result`.
  - `tests/test_unified_evaluation_pipeline.py` 增加 raw result schema refs 测试.
- r003 验证 run:
  - `run_id=r003_frozen_eval_diffsbdd_stage1_3rfm_v02_rawschema_fbfc8032`.
  - 输出路径: `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r003_frozen_eval_diffsbdd_stage1_3rfm_v02_rawschema_fbfc8032/`.
  - 重新运行 v0.2 evaluator, labels, summaries 和 gate, 不重新运行 DiffSBDD inference.
  - 40 个 `evaluator/raw_tool_outputs/posebusters_*.json` 均写入 `posebusters_raw_result_v0_1` schema refs.
  - `output_manifest.json` 的 `metadata_schemas.posebusters_raw_result` 指向 `schemas/third_party_audit/diagnosis/posebusters_raw_result_v0_1.json`.
  - Gate: `passed_with_warnings`, blocking `0`, internal energy unavailable coverage 仍为 `2/20`.
- 验证:
  - `conda run -n pfr env PYTHONPATH=src pytest -q` -> `44 passed in 0.78s`.

## 2026-06-09 / 基于 schema 的 JSON 自动填充第一版落地

- 目的: 按 `docs/plan/20260609-02-schema-aware-json-writer-automation-plan.md` 落地 schema-aware writer, 减少项目自有 JSON / JSONL 中手写 `schema_version` 和 `schema_path` 的重复维护.
- 新增:
  - `src/pfr/utils/schema_io.py`: 从 JSON Schema `const` 自动读取 schema refs, 提供 `with_schema_ref`, `write_json_with_schema`, `write_jsonl_with_schema` 和轻量 required/const 校验.
  - `schemas/configs/audit/manual_decisions_v0_1.json`: 后续人工拍板 YAML 的 config schema.
  - `tests/test_schema_io.py`: 覆盖 schema ref 注入, 冲突报错, required 校验, JSONL 失败不写半截输出, manual decisions schema 和 manifest finalizer.
- 迁移:
  - `scripts/eval/eval_posebusters_one.py`: PoseBusters raw wrapper JSON 通过 schema-aware writer 写出.
  - `scripts/eval/run_audit_evaluators.py`: `evaluator_input.jsonl` 和 `evaluator_tool_results.jsonl` 通过 schema-aware JSONL writer 写出.
  - `scripts/eval/build_audit_labels.py`: `labels.jsonl` 通过 schema-aware JSONL writer 写出.
  - `scripts/eval/summarize_audit_labels.py`: `label_summary.json` 和 `prevalence_summary.json` 通过 schema-aware writer 写出.
  - `scripts/eval/check_analysis_frozen_gate.py`: `analysis_frozen_gate_result.json` 通过 schema-aware writer 写出, gate 末尾调用 `finalize_output_manifest()` 刷新 manifest sha256.
- 暂缓:
  - `run_metadata.json`, `samples.jsonl`, `stage_attrition.json` 和初始 `output_manifest.json` 的统一 builder, 因为它们跨阶段语义不同或需要最终 finalizer 统一处理.
  - 未重写历史 outputs.
- 文档:
  - 更新 `docs/plan/20260609-02-schema-aware-json-writer-automation-plan.md`, 明确不在 `configs/audit/` 放空模板.
  - 更新 `schemas/README.md`, `configs/README.md`, `src/README.md`, `AGENTS.md`.
  - 新增报告 `docs/report/20260609-02-schema-aware-json-writer-automation-report.md`.
- 验证:
  - `conda run -n pfr env PYTHONPATH=src pytest -q` -> `51 passed in 0.79s`.

## 2026-06-09 / schema-aware writer 端到端验证 run r004

- 目的: 按 `docs/plan/20260609-02-schema-aware-json-writer-automation-plan.md` 的下一步, 用真实 evaluator run 验证 schema-aware writer, PoseBusters raw schema, labels, summaries, analysis-frozen gate 和 `output_manifest.json` finalizer 能端到端协同.
- 输入:
  - 源 run: `outputs/20260608-01-diffsbdd-original-protocol-sanity/diffsbdd/r001_official_example_3rfm_seed0_78d8cd91/`.
  - receptor prep record: `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r003_frozen_eval_diffsbdd_stage1_3rfm_v02_rawschema_fbfc8032/processed/receptors/3rfm_A_330_CFF_receptor_prep.json`.
  - configs: `experiments/20260608-02-unified-evaluation-pipeline-alignment/configs/resolved/audit/` 下 v0.2 evaluator/gate 和 v0.3 label config.
- 输出:
  - `run_id=r004_schema_writer_finalizer_e2e_diffsbdd_stage1_3rfm_v02_fbfc8032`.
  - 输出路径: `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r004_schema_writer_finalizer_e2e_diffsbdd_stage1_3rfm_v02_fbfc8032/`.
- 执行:
  - `pfr-eval-tools`: `scripts/eval/run_audit_evaluators.py`, tools `rdkit,posebusters,plip,vina`.
  - `pfr`: `scripts/eval/build_audit_labels.py`, `scripts/eval/summarize_audit_labels.py`, `scripts/eval/check_analysis_frozen_gate.py`.
- 结果:
  - evaluator tool rows `100`.
  - raw PoseBusters JSON `40`, 均写入 `schema_version=posebusters_raw_result_v0_1`.
  - `evaluator_input.jsonl` `20` 行, `evaluator_tool_results.jsonl` `100` 行, `labels.jsonl` `20` 行, 均带对应 schema refs.
  - Labels: `evaluable=20`, primary labels `unknown=15`, `local_geometry_failure=5`, `near_miss_eligible=5`.
  - PoseBusters `internal_energy_unavailable_count=2/20`, sample ids 为 `*_final_11` 和 `*_final_16`; `internal_energy_false_count=0`.
  - Gate: `passed_with_warnings`, blocking failures `0`.
  - Warnings: final-only selected-output residual view, training/leakage unknown, PLIP descriptive only, `internal_energy` unavailable coverage `2/20`.
  - `output_manifest.json`: `n_output_artifacts=293`, `sha256` 条目 `293`, 缺失 `0`, checksum mismatch `0`, 未把 `output_manifest.json` 自身列入 sha256.
- 报告:
  - `docs/report/20260609-03-schema-aware-json-writer-e2e-validation-report.md`.
- 验证:
  - `conda run -n pfr env PYTHONPATH=src pytest -q` -> `51 passed in 0.77s`.
- 当前结论:
  - schema-aware writer 第一版已通过真实统一评估流水线验证.
  - 该 run 仍是 selected-output residual view, 不能解释为 DiffSBDD 正式 failure prevalence, official protocol reproduction 或 repair benchmark result.

## 2026-06-09 / DiffSBDD 官方数据集审计协议 pilot 计划冻结

- 目的: 将下一轮 DiffSBDD 审计从 README 单 pocket 小测试推进到官方数据集 test view 的直接审计输出.
- 新增计划:
  - `docs/plan/20260609-03-diffsbdd-audit-protocol-pilot-plan.md`.
- 冻结主轨道:
  - dataset: Binding MOAD.
  - checkpoint: `moad_fullatom_cond.ckpt`, 执行前必须做官方来源, license, size 和 sha256 resource check.
  - split: `third_party/diffsbdd/data/moad_test.txt`.
  - pilot subset: 官方 test split 顺序前 20 个 pockets.
  - 每 pocket 使用 seed `0`, official `test.py` 风格目标 `100` 个 final samples, `batch_size=120`, `sanitize=true`, `n_nodes_bias=10`.
- denominator 规则:
  - 主分母来自 `samples.jsonl`, 每个 raw attempt 都必须有 metadata 行.
  - raw attempts 按真实 batch 请求数记录, 每 pocket/seed 最少 `120`, 最多 `1200`.
  - candidate, rejected, selected 和 final 样本分开保存, 不从 SDF 数量倒推分母.
- evaluator:
  - 继续使用 `evaluator_policy_v0_2`, `analysis_frozen_gate_v0_2`, `diagnosis_label_config_v0_3`.
- 重要边界:
  - 这只是 protocol pilot plan, 尚未启动 inference.
  - CrossDocked 被列为第二轨道, 需要 `split_by_name.pt` 和 processed test data resource check 后再执行.
  - 计划明确 formal 前置条件, 包括 training/leakage 状态, receptor prep 无 unresolved HETATM, output manifest 完整, 以及 formal analysis 下 `internal_energy_unavailable_fraction <= 0.05`.

## 2026-06-09 / Binding MOAD raw 数据和 DiffSBDD MOAD checkpoint 获取记录补齐

- 目的: 为 DiffSBDD Binding MOAD audit protocol pilot 补齐 resource/provenance 记录, 避免只留下下载文件而缺少来源、checksum、删除压缩包策略和 claim boundary.
- 数据来源:
  - Binding MOAD 结构实验文件: Zenodo `10.5281/zenodo.13375913`, `every.csv`, `every_part_a.zip`, `every_part_b.zip`.
  - DiffSBDD checkpoint: Zenodo `10.5281/zenodo.8183747`, `moad_fullatom_cond.ckpt`.
- 本地资产:
  - dataset root: `data/datasets/binding_moad_zenodo13375913/`.
  - raw data: `raw/every.csv`, `raw/BindingMOAD_2020/`.
  - checkpoint: `third_party/diffsbdd/checkpoints/moad_fullatom_cond.ckpt`.
  - checksum: `manifests/downloaded_files.md5`, `manifests/downloaded_files.sha256`.
  - logs: `logs/download_extract_20260609T122121Z.log`, `logs/download_resume_20260609T145128Z.log`, `logs/wget_resume_20260609T145306Z.log`.
- 校验和规模:
  - `raw/BindingMOAD_2020/*.bio*` 文件数: `59346`.
  - `moad_fullatom_cond.ckpt` sha256: `58bd5f6c532e64a727f92779c6d3d7f274e5df7b0d345e4900a99dd341192561`.
  - `every.csv` sha256: `4567a4a1fef9ddc58fe4ecab8ac8c829661943481ba67daf6ea9f962769812a9`.
  - `every_part_a.zip` sha256: `329ae164168a20c7831b7f06515d84252659c560ab6a2fc6c01acf88d7349cb5`.
  - `every_part_b.zip` sha256: `0768cfd8d365443031c750c72e3f379bad99ac3443fa905aace8da0cad9bd1de`.
- 保留/删除策略:
  - `every_part_a.zip` 和 `every_part_b.zip` 已在 checksum 校验和解压后删除, 以控制单方法存储占用.
  - `every.csv`, checksum 文件, 下载/解压日志和 raw manifest 保留.
- 新增记录:
  - `data/datasets/binding_moad_zenodo13375913/README.md`.
  - `data/datasets/binding_moad_zenodo13375913/manifests/raw/binding_moad_zenodo13375913_raw_manifest_v1.json`.
  - `data/datasets/binding_moad_zenodo13375913/entries/index.jsonl`, 当前为空, 表示 raw 已获取但 canonical sample entries 尚未 materialize.
  - `data/datasets/binding_moad_zenodo13375913/manifests/entries/binding_moad_zenodo13375913_entries_manifest_v1.json`.
  - `experiments/20260609-03-diffsbdd-audit-protocol-pilot/configs/resolved/audit/manual_decisions.yaml`.
  - `experiments/20260609-03-diffsbdd-audit-protocol-pilot/metadata/method_resource_check.jsonl`.
- 下载命令记录:
  - 实际完成过程的断点续传日志在 `data/datasets/binding_moad_zenodo13375913/logs/wget_resume_20260609T145306Z.log`.
  - 可复现的 `aria2c` 下载, checksum, copy 和 unzip 命令已补入 `data/datasets/binding_moad_zenodo13375913/README.md` 和 raw manifest 的 `download_session.reproducible_commands`.
- 计划修正:
  - `docs/plan/20260609-03-diffsbdd-audit-protocol-pilot-plan.md` 中 `moad_test.txt` 非空条目数从 `129` 更正为 `130`, 对应 full view run id 从 `moad_test129` 更正为 `moad_test130`.
- 结论边界:
  - 本轮 resource check 的 `decision=go` 只表示可以进入 DiffSBDD Binding MOAD audit pilot 的数据处理准备.
  - 由于 Zenodo 结构包是第三方归档副本, 且 processed test coverage, split 对齐和 training/leakage 状态尚未冻结, 不能据此声明 official/original protocol reproduction, formal failure prevalence, clean-test status 或 repair benchmark result.
- 验证:
  - 轻量语法检查: raw manifest JSON, method_resource_check JSONL 和 manual_decisions YAML 均可解析.
  - `conda run -n pfr pytest -q tests/test_data_schema_refs.py tests/test_config_schema_refs.py tests/test_audit_schemas.py tests/test_schema_io.py` -> `14 passed in 0.24s`.
  - `git diff --check` -> passed.

## 2026-06-09 / DiffSBDD Binding MOAD 官方脚本预处理完成

- 目的: 按 `docs/plan/20260609-03-diffsbdd-audit-protocol-pilot-plan.md` 将已获取的 Binding MOAD raw 结构包处理成 DiffSBDD `moad_fullatom_cond.ckpt` 对应的 `processed_noH_full/`, 为后续官方 test view audit pilot 准备输入.
- 配置:
  - resolved config: `experiments/20260609-03-diffsbdd-audit-protocol-pilot/configs/resolved/data/binding_moad_preprocess_diffsbdd.yaml`.
  - metadata schema: `schemas/third_party_audit/resources/preprocess_metadata_v0_1.json`.
  - config schema: `schemas/configs/data/preprocessing/diffsbdd_binding_moad_preprocess_config_v0_1.json`.
- 执行:
  - 环境: `pfr-diffsbdd`.
  - 方式: CPU 串行, 不使用 GPU.
  - 命令: `conda run -n pfr-diffsbdd bash -lc 'cd third_party/diffsbdd && python -W ignore process_bindingmoad.py data/datasets/binding_moad_zenodo13375913/raw --outdir data/datasets/binding_moad_zenodo13375913/work/diffsbdd/processed_noH_full'`, 实际命令使用绝对路径.
  - 日志: `experiments/20260609-03-diffsbdd-audit-protocol-pilot/logs/binding_moad_preprocess_diffsbdd.log`.
- 输出:
  - processed dir: `data/datasets/binding_moad_zenodo13375913/work/diffsbdd/processed_noH_full/`, 大小约 `1.5G`, 不提交.
  - 顶层输出: `train.npz`, `val.npz`, `test.npz`, `train_smiles.npy`, `size_distribution.npy`, `summary.txt`.
  - metadata: `experiments/20260609-03-diffsbdd-audit-protocol-pilot/metadata/binding_moad_preprocess_metadata.json`.
- 结果:
  - 主命令 exit code `0`, 运行时间约 `4193` 秒.
  - summary before: train `40354`, val `246`, test `130`.
  - summary after: train `40353`, val `246`, test `130`.
  - test coverage: `moad_test.txt` 的 `130` 个条目全部具备 SDF/TXT, 并对齐到 `92` 个 pocket PDB; missing `0`.
  - 记录状态: `completed_with_warnings`.
- Warning:
  - train count 比 preflight split 少 `1`; 当前不影响只使用 test view 的 pilot, 但已记录.
  - 日志出现 RDKit explicit valence warning `1536` 条, Open Babel PerceiveBondOrders/kekulization warning `3157` 条.
  - 日志出现 1 次非阻断 `libXrender.so.1` 缺失提示; 主进程仍 exit `0` 且生成预期输出.
- 结论边界:
  - 本轮只说明 DiffSBDD Binding MOAD pilot 的 `processed_noH_full/test/` 输入已准备好.
  - 不声明 official/original protocol reproduction, formal failure prevalence, clean-test status 或 repair benchmark result.
- 下一步:
  - 冻结 pilot subset: `moad_test.txt` 官方顺序前 20 个 pockets.
  - 实现或核查 dataset-level DiffSBDD instrumented wrapper, 记录 raw attempt denominator, captured/rejected/selected/final 样本.
  - 进入 inference 前继续保留 training/leakage unknown 风险, 并使用已冻结的 evaluator policy v0.2, analysis-frozen gate v0.2 和 diagnosis label config v0.3.
