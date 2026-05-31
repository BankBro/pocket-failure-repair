# STATUS

> 这个文档用于压缩上下文后的快速恢复。保持简短，只记录当前最重要的信息。详细过程写入 `EXPERIMENT_LOG.md`。

## 当前阶段快照

- 当前阶段：最小 smoke pipeline 配置和 dry-run 入口已创建；准备实现数据/反馈/baseline 脚本。
- 当前主线：Failure-feedback-conditioned repair for pocket-aware 3D local molecular editing。
- 当前 commit：511daa9 Initialize research project scaffold。
- 当前环境：`environment.yml` 已创建；当前激活环境为 Python 3.12.11 / flash-vqg, 缺少必需依赖 RDKit；目标 conda 环境 `pfr` 尚未创建。
- 当前数据版本：尚无数据下载或处理。
- 当前最好结果：尚无实验结果。
- 当前主要阻塞：需要二轮核验 AMG / MolJO 等歧义方法, 并补全 DiffDec / DiffLEOP / DecompDiff / DecompOpt / DecompDPO 的原文指标和代码仓库；工程上下一步是补环境文件与最小 smoke pipeline。

## 可用工具与插件

- 已安装 plugin：当前可见 Context7 文档查询、CCS WebSearch；Exa MCP 已安装但需要认证后使用。
- 可用 skill：literature-review、research-lookup、deep-research、paper-lookup、citation-management、rdkit、pytorch-lightning、torch-geometric、optimize-for-gpu、scientific-visualization、code-review、verify、run、security-review、loop 等。
- 可用 MCP：Context7 documentation MCP、CCS WebSearch MCP、Exa MCP authentication endpoints。
- 可用 subagent：Explore、Plan、general-purpose、claude-code-guide、codex rescue 等。
- 可用 workflow：Workflow 工具可用，但仅在用户明确要求 workflow / multi-agent orchestration 时调用。
- 当前优先使用策略：文献检索优先用 research / literature / web search 类能力；库和工具文档优先用 Context7；代码实现后关键节点使用 code-review / verify；长期实验前先 smoke。
- 不可用工具及降级方案：Exa 未认证时降级到 CCS WebSearch、research-lookup、官方文档、论文页、GitHub CLI 或本地脚本。
- 安全注意事项：不上传密钥、token、未公开数据、私有路径到不可信服务；外部插件或仓库接入前记录用途、来源和权限风险。

## 最近完成的工作

- 第一轮文献矩阵已更新：`docs/literature_matrix.md` 记录 DiffDec, DiffLEOP, AMG, MolJO, DecompDPO, DecompDiff, DecompOpt, PoseBusters, PLIP, AutoDock Vina 的初步证据和撞题风险。
- 第一轮未发现同时覆盖 failed candidate 输入、explicit failure feedback、pocket-aware 3D local repair 和 same-budget repair evaluation 的直接撞题工作。
- 当前直接撞题风险暂定 Low, 相邻工作风险 Medium；需要在二轮原文阅读中重点核验 pocket-aware lead optimization / scaffold decoration / structure-based optimization 方法。
- 创建项目目录框架：`configs/`, `data/`, `src/pfr/`, `scripts/`, `experiments/`, `outputs/`, `docs/`, `tests/`, `third_party/`。
- 将原始项目文档归位到 `docs/`。
- 新增 `README.md`、`docs/method_design.md`、`docs/literature_matrix.md` 骨架。
- 明确子实验代码放置原则：核心逻辑进 `src/pfr/`，实验入口进 `scripts/`，配置进 `configs/`，运行记录进 `experiments/`，汇总结果进 `outputs/`。

## 最近实验结果摘要

| 日期 | 实验 | 配置 | 结果 | 结论 |
|---|---|---|---|---|
| 2026-05-31 | 项目初始化 | N/A | 目录与文档骨架完成 | 可进入文献检索和环境初始化 |
| 2026-05-31 | 第一轮文献与撞题分析 | OpenAlex + 研究 Agent + 工具文档 | 未发现直接撞题；相邻工作风险 Medium | 保留 failed-candidate-conditioned local repair 定位, 下一步补环境和 smoke pipeline |
| 2026-05-31 | 环境初始化检查 | `python scripts/setup/check_environment.py` | 当前环境缺少 RDKit, 可用 CUDA RTX 3090 | 已创建 `environment.yml`, 需后续创建 `pfr` conda 环境 |
| 2026-05-31 | smoke pipeline dry-run | `python scripts/setup/smoke_pipeline_dry_run.py` | YAML 配置可读, 已生成 `experiments/smoke/pipeline_plan.json` | 4 个实际处理脚本仍待实现 |

## 当前关键判断

- 课题主线必须保持在 failed-candidate-conditioned local molecular repair，而不是泛泛 pocket-aware generation。
- 下一阶段最关键风险是撞题风险，需要优先完成文献矩阵。
- 在任何模型开发前，应先跑通数据构造、failed candidate 构造、feedback 提取和 baseline smoke pipeline。

## 短期计划

未来 1-3 天：

1. 实现 smoke pipeline 的 4 个脚本入口: `build_rgroup_dataset.py`, `generate_failed_candidates.py`, `extract_feedback.py`, `eval_baselines.py`。
2. 创建并激活 `pfr` conda 环境, 运行 `python scripts/setup/check_environment.py` 确认 RDKit 等必需依赖可用。
3. 二轮阅读 DiffDec, DiffLEOP, DecompDPO, DecompDiff, DecompOpt 原文, 核验 AMG / MolJO 歧义方法并补全代码仓库与指标。

## 中期计划

未来 1-3 周：

1. 实现数据处理、失败候选生成和 feedback extraction。
2. 实现 direct regeneration、Best-of-N、rerank-only、no-feedback repair baseline。
3. 完成主指标计算、多 seed 汇总和第一版消融实验。

## 长期计划

面向 BIBM 投稿：

1. 完成 feedback-conditioned repair 模型和完整 baseline 对比。
2. 完成至少 3 seeds、至少一个 split 的交叉验证、成功/失败案例分析。
3. 完成 BIBM 风格论文初稿、图表、可复现说明和局限性分析。

## 常用命令

```bash
# 环境
conda activate pfr

# TODO: 环境检查
python scripts/setup/check_environment.py

# TODO: smoke 数据构造
python scripts/data/build_rgroup_dataset.py --config configs/data/rgroup_smoke.yaml

# TODO: failed candidate 构造
python scripts/data/generate_failed_candidates.py --config configs/data/failed_candidate_smoke.yaml

# TODO: baseline 评估
python scripts/eval/eval_baselines.py --config configs/baselines/smoke.yaml
```

## 需要优先阅读的文件

- `docs/STATUS.md`
- `docs/EXPERIMENT_LOG.md`
- `docs/literature_matrix.md`
- `docs/method_design.md`
- `docs/research_brief.md`
- `docs/project_protocol.md`
- `docs/bibm_execution_notes.md`
