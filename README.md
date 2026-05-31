# pocket-failure-repair

Failure-feedback-conditioned repair for pocket-aware 3D local molecular editing.

本项目研究一个更窄的 pocket-aware molecular generation 问题：给定 protein pocket、fixed scaffold、editable region 和一个已经失败的局部编辑候选，模型能否利用当前失败反馈进行定向局部修复，并在相同生成预算下比 direct regeneration、Best-of-N、rerank-only 和普通 guidance 更可靠。

## 当前阶段

项目初始化阶段。当前进展和下一步计划见：

- `docs/STATUS.md`
- `docs/EXPERIMENT_LOG.md`

## 目录结构

```text
pocket-failure-repair/
  configs/                 # 实验配置
  data/
    raw/                   # 原始数据
    processed/             # 处理后数据
    splits/                # scaffold/protein/pocket split
  src/
    pfr/
      data/                # 数据读取、口袋裁剪、R-group/scaffold/anchor 切分
      chemistry/           # RDKit 工具、分子性质、坐标与合法性处理
      feedback/            # clash、PLIP、Vina、PoseBusters、interaction feedback
      models/              # repair/refinement 模型
      baselines/           # Best-of-N、rerank-only、direct regeneration 等 baseline
      evaluation/          # 指标计算、多 seed 汇总、统计分析
      workflows/           # 端到端流程封装
      utils/               # 配置、日志、随机种子、IO 等通用工具
  scripts/
    setup/                 # 环境与外部工具检查
    data/                  # 数据构建脚本
    train/                 # 训练脚本
    eval/                  # 评估脚本
    analysis/              # 表格、图、失败案例分析
  experiments/
    smoke/                 # 小样本 smoke experiments
    main/                  # 主实验
    ablations/             # 消融实验
    baselines/             # baseline 实验
  outputs/
    metrics/               # 原始指标
    tables/                # 论文表格
    figures/               # 论文图
    molecules/             # 生成/修复分子
    logs/                  # 长日志
  docs/                    # 项目文档
  tests/                   # 测试
  third_party/             # 外部仓库或工具
```

## 子实验代码放置原则

- 可复用逻辑放在 `src/pfr/`。
- 可执行实验入口放在 `scripts/`。
- 参数配置放在 `configs/`。
- 单次实验运行记录放在 `experiments/`。
- 汇总后的论文结果放在 `outputs/`。

## 最小可行任务

Single R-group failed-candidate repair:

```text
protein pocket
+ original ligand
+ fixed scaffold
+ editable R-group mask
+ anchor atoms
+ failed candidate
+ feedback features
→ repaired editable region / repaired local molecule
```

## 计划中的主要模块

1. 文献矩阵与撞题分析。
2. protein-ligand complex 数据构造。
3. scaffold / R-group / anchor 切分。
4. failed candidate 生成。
5. feedback feature 提取。
6. baseline 实现。
7. no-feedback repair 与 feedback-conditioned repair 模型。
8. 统一评估、多 seed、消融和结果汇总。
9. BIBM 风格论文初稿。

## 学术与实验原则

- 不伪造数据、结果或引用。
- 不只报告最好 seed。
- 不隐藏负结果。
- 不只用 Vina 证明方法有效。
- 所有结论必须可追溯到代码、配置、数据、日志、指标和文献。
