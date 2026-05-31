# pocket-failure-repair 项目执行协议

## 项目原则

本项目目标是产出可复现、可审计、可投稿的完整研究闭环。所有实验结论必须能追溯到代码、配置、数据版本、日志、原始指标、文献来源和实验记录。

禁止伪造数据、伪造结果、伪造引用、只报告最好 seed、隐藏负结果、为了结果好看而临时改指标定义、只用 Vina 分数证明方法有效。

失败、阻塞和负结果必须记录，它们也是判断方向是否需要调整的重要证据。

## 推荐项目结构

```text
pocket-failure-repair/
  configs/
  data/
    raw/
    processed/
    splits/
  src/
    pfr/
      data/
      chemistry/
      feedback/
      models/
      baselines/
      evaluation/
      workflows/
      utils/
  scripts/
    setup/
    data/
    train/
    eval/
    analysis/
  experiments/
    smoke/
    main/
    ablations/
    baselines/
  outputs/
    metrics/
    tables/
    figures/
    molecules/
    logs/
  docs/
    STATUS.md
    EXPERIMENT_LOG.md
    literature_matrix.md
    method_design.md
  tests/
  third_party/
  environment.yml
  README.md
```

## 环境管理

- 使用 conda 新建独立环境；
- 固定 `environment.yml`；
- 外部工具安装方式必须记录；
- 大规模下载数据或运行 GPU 任务前先做 smoke test；
- GPU 空闲时可用本机 GPU，但必须记录设备、显存、运行时间和随机种子。

## Plugin / Skill / MCP / Workflow 使用规范

项目启动后必须先盘点当前 Claude Code 环境能力，包括可用 plugin、skill、MCP、subagent、workflow、code review、debug、verify、run、batch 等能力，并记录到 `docs/STATUS.md` 的“可用工具与插件”小节。

优先使用相关工具完成对应任务：

- search / deep-research / Exa 类插件：文献检索、相似工作检索、论文元信息核验、开源仓库搜索；
- GitHub 类插件：检索、阅读、复现相关开源仓库；
- code intelligence / LSP 类插件：跳转定义、查找引用、静态诊断、大代码库理解；
- Python / data / science / plot / report 类 skill：数据清洗、统计分析、绘图、表格、论文图生成；
- debug / verify / code-review / security-review 类 skill：关键代码合入前、长期实验运行前、结果汇总前必须主动使用；
- workflow / batch / loop 类能力：用于文献检索批处理、多 seed 实验、多 baseline 评估、表格和论文图自动生成。

插件或 skill 不可用时，需要记录原因，并降级为本地脚本、官方 API、curl、git、Python 或手动检索流程。

安装新插件前必须确认来源可信、权限合理、用途明确、是否有替代方案、是否可能读取或上传密钥、token、服务器隐私路径、未公开数据。不要把任何密钥、token、私有路径、未公开数据上传到不可信服务。

## 建议分工

如果 Claude Code 环境支持 subagents，就创建或调用以下角色；如果不支持，就按角色模拟执行。

- Literature Agent：文献检索、撞题核查、文献矩阵。
- Repository Agent：相关 GitHub 仓库检索、阅读和复现。
- Engineering Agent：环境、项目结构、测试、debug、code review。
- Data Agent：数据准备、R-group / scaffold / anchor 切分、失败候选构造。
- Feedback Agent：RDKit、Vina、PLIP、PoseBusters、clash、interaction feedback。
- Model Agent：no-feedback repair、feedback-conditioned repair、local refinement。
- Baseline Agent：Best-of-N、rerank-only、direct regeneration、规则修复及开源 baseline。
- Evaluation Agent：多 seed、交叉验证、统计显著性、图表。
- Writing Agent：论文初稿、图表、related work、limitations、reproducibility。

## 阶段推进原则

每个阶段必须遵循：

1. 明确阶段目标；
2. 小样本 smoke；
3. 记录配置和命令；
4. 运行实验；
5. 保存原始结果；
6. 生成表格和简短结论；
7. 更新 `docs/STATUS.md`；
8. 追加 `docs/EXPERIMENT_LOG.md`；
9. 重要节点提交 git commit。

## 方向调整机制

如果发现当前方向不可行，例如与已有工作高度重合、数据构造不可控、baseline 无法复现、修复模型没有超过简单 Best-of-N、反馈信号没有实际影响生成分布、结果只在人工失败样本上成立但真实生成失败不成立，则必须启动新的 workflow 重新评估方向，并在 `docs/EXPERIMENT_LOG.md` 中记录证据和调整理由。
