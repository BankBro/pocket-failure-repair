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
