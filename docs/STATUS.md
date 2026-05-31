# STATUS

> 这个文档用于压缩上下文后的快速恢复。保持简短，只记录当前最重要的信息。详细过程写入 `EXPERIMENT_LOG.md`。

## 当前阶段快照

- 当前阶段：`pfr` base conda 环境已验证, RDKit scaffold/R-group/anchor 提取、failed molecule SDF 生成、结构推导 feedback 和规则型 feedback repair 已接入 smoke pipeline；当前公开 smoke 样本存在严重 protein-ligand overlap 负结果。
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
| 2026-05-31 | smoke pipeline 空数据端到端 | `PYTHONPATH=src python scripts/...` | 4 个脚本入口均可运行, 空输入可生成空输出和占位指标 | 等待真实小样本数据与 RDKit 环境 |
| 2026-05-31 | smoke pipeline toy 测试 | `pytest -q` | 1 passed | toy complex 可生成 dataset, failed candidates, feedback 和 baseline metrics |
| 2026-05-31 | baseline / metric 模块化 | `pytest -q` | 4 passed | 成功判定和 baseline 汇总已抽到 `src/pfr/evaluation` 与 `src/pfr/baselines` |
| 2026-05-31 | RCSB smoke 数据下载 | `download_smoke_complexes.py` | 下载 1a4w, 1hvr, 3ptb 并写入 SHA256 manifest | raw 数据不提交 git, 来源记录在 `docs/smoke_data_manifest.md` |
| 2026-05-31 | 公开样本文件级 smoke | smoke pipeline scripts | 3 examples, 12 failed candidates, 12 feedback records, placeholder metrics written | 输出 `outputs/metrics/baselines_smoke.json`, `outputs/tables/baselines_smoke.csv` |
| 2026-05-31 | pfr base 环境验证 | `conda run -n pfr ...` | RDKit required checks passed, `pytest -q`: 6 passed, smoke pipeline rerun passed | PLIP/Torch/Vina 等仍为可选缺失工具 |
| 2026-05-31 | RDKit scaffold/R-group 提取 | `build_rgroup_dataset.py` + RDKit | 3/3 ligand 可读, 1HSG 有 scaffold/R-group/anchor, 1A4W/3PTB 无 Murcko scaffold | 无 scaffold 样本作为负例保留, 后续需更合适 benchmark 样本 |
| 2026-05-31 | RDKit feedback 指标 | `extract_feedback.py` + `eval_baselines.py` | RDKit descriptors 写入 feedback, anchor_validity 0.25, success rate 0.0833 | 仍是 template failure labels, 非 repaired-molecule 性能 |
| 2026-05-31 | failed molecule SDF 生成 | `generate_failed_candidates.py` | 12 个 failed candidate SDF + cases JSON | 仍为可控平移扰动, 不是模型修复结果 |
| 2026-05-31 | 最小 repair baseline | `repair_baselines.py` | 24 个 repaired SDF, coordinate_rollback 和 identity_failed_candidate | baseline 可运行, 但尚非 feedback-conditioned model |
| 2026-05-31 | receptor-only protein 清理 | `download_smoke_complexes.py` | 生成 `_protein_clean.pdb`, manifest 指向 clean receptor | clash 仍为 0 成功率, 说明样本/ligand 提取仍需改进 |
| 2026-05-31 | 结构推导 geometry feedback | `pfr.feedback.geometry` | min protein-ligand distance 和 clash_count 已从坐标计算；当前 clash_free_rate 0, success rate 0 | 暴露 smoke 数据坐标/ligand 选择问题, 作为负结果记录 |
| 2026-05-31 | 规则型 feedback repair | `repair_baselines.py` | 36 个 repaired SDF, 其中 feedback_rule_repair 12 个 | 最小 feedback-conditioned baseline 可运行, 仍非学习模型 |
| 2026-05-31 | smoke 输出汇总 | `summarize_smoke_results.py` | 生成 summary JSON, SVG figure, cases JSON | 均标注为 RDKit file-level smoke, 非真实模型性能 |

## 当前关键判断

- 课题主线必须保持在 failed-candidate-conditioned local molecular repair，而不是泛泛 pocket-aware generation。
- 下一阶段最关键风险是撞题风险，需要优先完成文献矩阵。
- 在任何模型开发前，应先跑通数据构造、failed candidate 构造、feedback 提取和 baseline smoke pipeline。

## 短期计划

未来 1-3 天：

1. 增加更适合 R-group repair 的公开含 scaffold 样本, 避免 smoke 数据中过多无 scaffold ligand。
2. 集成 PoseBusters 或自实现距离 clash 检查, 让 feedback 从 template 进一步转为 structure-derived。
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
- `docs/paper_draft.md`
- `docs/bibm_execution_notes.md`
