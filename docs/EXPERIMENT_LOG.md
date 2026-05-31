# EXPERIMENT_LOG

> 这个文档用于追加记录完整实验过程，可以逐渐变长。每个阶段都要记录目的、命令、配置、结果路径、结论和下一步判断。

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
- 输出路径：`README.md`、`docs/STATUS.md`、`docs/EXPERIMENT_LOG.md`、`docs/method_design.md`、`docs/literature_matrix.md`。
- 是否成功：成功。
- 失败原因或降级方案：无。
- 对本阶段结论的影响：项目可以进入文献检索、环境初始化和 smoke pipeline 设计。

### 命令与配置

```bash
mkdir -p configs data/raw data/processed data/splits src/pfr/{data,chemistry,feedback,models,baselines,evaluation,workflows,utils} scripts/{setup,data,train,eval,analysis} experiments/{smoke,main,ablations,baselines} outputs/{metrics,tables,figures,molecules,logs} docs tests third_party
mv 00_research_brief.md docs/research_brief.md
mv 01_project_protocol.md docs/project_protocol.md
mv 02_claude_goal_prompt.md docs/claude_goal_prompt.md
mv 03_status_template.md docs/STATUS.md
mv 04_experiment_log_template.md docs/EXPERIMENT_LOG.md
mv 05_bibm_execution_notes.md docs/bibm_execution_notes.md
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

- 完成 `docs/literature_matrix.md` 第一轮检索。
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
- 将第一轮证据写入 `docs/literature_matrix.md`。

### 背景与判断

- 为什么做这个实验：在启动模型实现或长期实验前, 需要先确认课题切口是否已经被已有工作覆盖。
- 需要验证的假设：本项目的核心差异在于 failed candidate + explicit failure feedback + pocket-aware local repair + same-budget evaluation 的组合。
- 与上一阶段的关系：承接项目初始化阶段, 进入文献和撞题风险确认。

### 插件 / Skill / Workflow 使用记录

- 使用的 plugin / skill / agent / workflow：CCS WebSearch MCP, OpenAlex API 查询, general-purpose research agents, Explore agent, Plan agent。
- 使用目的：检索论文/工具来源, 核验方法职责, 形成文献矩阵和撞题判断。
- 输入：目标方法列表与横向检索关键词。
- 输出路径：`docs/literature_matrix.md`, `docs/STATUS.md`, `docs/EXPERIMENT_LOG.md`。
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
- tables：`docs/literature_matrix.md`。
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
- AMG 与 MolJO 名称或方法归属仍有歧义, 已在 `docs/literature_matrix.md` 标注待验证。

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
- 输出路径：`experiments/smoke/pipeline_plan.json`。
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
- logs：`experiments/smoke/pipeline_plan.json`, `docs/EXPERIMENT_LOG.md`。
- checkpoints：无。

### 主要结果

| 指标 | 结果 | 备注 |
|---|---:|---|
| YAML config load | PASS | 四个配置均可读取 |
| pipeline steps | 4 | build_rgroup_dataset, generate_failed_candidates, extract_feedback, eval_baselines |
| dry-run output | PASS | 写入 `experiments/smoke/pipeline_plan.json` |
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

- 创建 `docs/paper_draft.md`, 写入 BIBM-style working draft。
- 初稿明确区分文献证据、工程 smoke 结果和未完成的真实分子实验。
- 初稿包含摘要、引言、相关工作、任务定义、方法概览、实验设计、当前实现状态、初步结果、讨论、局限、可复现与伦理、下一步。


