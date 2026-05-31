# STATUS

> 这个文档用于压缩上下文后的快速恢复。保持简短，只记录当前最重要的信息。详细过程写入 `EXPERIMENT_LOG.md`。

## 当前阶段快照

- 当前阶段：项目初始化 / research scaffold setup。
- 当前主线：Failure-feedback-conditioned repair for pocket-aware 3D local molecular editing。
- 当前 commit：0693688 Initial commit。
- 当前环境：尚未创建 conda 环境；`environment.yml` 待补。
- 当前数据版本：尚无数据下载或处理。
- 当前最好结果：尚无实验结果。
- 当前主要阻塞：需要先完成文献检索与撞题分析，再确定数据源、baseline 和最小 smoke pipeline。

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

- 创建项目目录框架：`configs/`, `data/`, `src/pfr/`, `scripts/`, `experiments/`, `outputs/`, `docs/`, `tests/`, `third_party/`。
- 将原始项目文档归位到 `docs/`。
- 新增 `README.md`、`docs/method_design.md`、`docs/literature_matrix.md` 骨架。
- 明确子实验代码放置原则：核心逻辑进 `src/pfr/`，实验入口进 `scripts/`，配置进 `configs/`，运行记录进 `experiments/`，汇总结果进 `outputs/`。

## 最近实验结果摘要

| 日期 | 实验 | 配置 | 结果 | 结论 |
|---|---|---|---|---|
| 2026-05-31 | 项目初始化 | N/A | 目录与文档骨架完成 | 可进入文献检索和环境初始化 |

## 当前关键判断

- 课题主线必须保持在 failed-candidate-conditioned local molecular repair，而不是泛泛 pocket-aware generation。
- 下一阶段最关键风险是撞题风险，需要优先完成文献矩阵。
- 在任何模型开发前，应先跑通数据构造、failed candidate 构造、feedback 提取和 baseline smoke pipeline。

## 短期计划

未来 1-3 天：

1. 完成第一轮文献检索和 `docs/literature_matrix.md` 撞题分析。
2. 补 `environment.yml` 和 `scripts/setup/check_environment.py`。
3. 设计最小 smoke pipeline：少量 protein-ligand complex → R-group 切分 → failed candidate → feedback → baseline metrics。

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
