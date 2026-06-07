# pocket-failure-repair

Failure-feedback-conditioned repair for pocket-aware 3D local molecular editing.

本项目研究一个更窄的 pocket-aware molecular generation 问题：给定 protein pocket、fixed scaffold、editable region 和一个已经失败的局部编辑候选，模型能否利用当前失败反馈进行定向局部修复，并在相同生成预算下比 direct regeneration、Best-of-N、rerank-only 和普通 guidance 更可靠。

## 当前阶段

当前项目主线是 failure audit / repair pipeline 的可复现实验工程化。最新阶段、阻塞和下一步以以下文档为准：

- `docs/STATUS.md`
- `docs/EXPERIMENT_LOG.md`

## 目录结构

```text
pocket-failure-repair/
  configs/                 # 项目级真实配置: 规则文件、数据构建配置和第三方方法状态记录
  data/
    datasets/
      <dataset_id>/
        raw/                 # 原始 protein/ligand 结构, 按 sample_id 分目录
        entries/             # 标准数据条目: index.jsonl + entries/<sample_id>/entry.json
        splits/              # train/validation/test split
        views/               # 任务或方法视图
        manifests/           # source/checksum/lineage 等数据清单
    catalog/                 # 跨数据集 catalog 和 reconciliation manifest
  sources/                  # 文献、检索结果和调研来源材料
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
    audit/                 # failure audit、metadata 检查和 provenance 脚本
    third_party/           # 第三方方法 wrapper、output capture 和 instrumentation
  experiments/
    <experiment_id>/       # 每次实验的命令、resolved config、专用脚本和 metadata
  outputs/
    <experiment_id>/       # 与 experiments/<experiment_id>/ 同名的输出目录
      metadata/            # output-level manifest、hash、migration 或 artifact registry
      processed/           # 派生产物, 大规模 JSONL 默认不提交
      metrics/             # 指标 JSON / summary
      tables/              # 表格 CSV/TSV/Markdown
      figures/             # 图, 轻量 SVG 可提交
      summaries/           # 汇总 JSON/CSV/Markdown
      logs/                # 长日志, 默认不提交
      work/                # 临时工作目录, 默认不提交
  schemas/                 # JSON Schema; 约束项目自有 JSON / JSONL / YAML metadata/config
  docs/
    plan/                  # 研究规划、实验方案和路线图
    report/                # 调研报告、实验报告、审计报告和复盘
    STATUS.md              # 当前项目快照
    EXPERIMENT_LOG.md      # 完整阶段和实验日志
  tests/                   # 测试
  third_party/             # 外部仓库或工具
  patent/                  # 专利交底素材草案
  tmp/                     # 临时中间产物, 使用后清理
```

## 子实验代码放置原则

- 可复用逻辑放在 `src/pfr/`。
- 跨实验复用的稳定可执行脚本放在 `scripts/`。
- 项目级真实配置放在 `configs/`, 包括规则文件、数据构建配置和第三方方法状态记录; 绑定单次运行的 resolved config 放在 `experiments/<experiment_id>/configs/resolved/`。详细定义见 `configs/README.md`。
- 每次实验先定义 `experiment_name = xxx`, 再定义 `experiment_id = YYYYMMDD-<num>-<experiment_name>`, 并在 `experiments/<experiment_id>/` 管理该实验的命令、配置、专用脚本、metadata 和说明。
- 该实验产生的输出放在对应的 `outputs/<experiment_id>/`。
- 汇总后的论文结果也应放在对应的 `outputs/<experiment_id>/tables/`, `outputs/<experiment_id>/figures/`, `outputs/<experiment_id>/metrics/` 等子目录, 不再写入顶层公共 bucket。
- 文献 PDF、检索 JSON/XML 和人工调研来源材料放在 `sources/`; 项目结论应整理到 `docs/report/` 或 `docs/EXPERIMENT_LOG.md`, 不只停留在来源缓存中。
- 临时脚本或中间文件放在 `tmp/YYYYMMDD-<task-slug>/`, `<task-slug>` 使用简短英文 kebab-case; 任务结束后删除对应子目录, 不把 `tmp/` 当长期资产目录。
- 详细规范见 `experiments/README.md`。

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

## Audit / evaluation tools

第三方 failure audit 的外部评估工具信息记录在:

- `configs/audit/tool_versions.lock`: evaluator 环境、工具版本、CLI 路径。
- `configs/audit/diagnosis_label_config_v0_1.yaml`: failure diagnosis labels 与工具判定边界。

当前开发 / data writer / smoke test 环境:

- Conda env: `pfr`
- 用途: 项目开发、canonical data writer、RDKit scaffold / geometry、smoke pipeline 测试。
- 示例: `conda run -n pfr env PYTHONPATH=src pytest -q tests/test_smoke_pipeline.py`

当前 evaluator 环境:

- Conda env: `pfr-eval-tools`
- 路径: `/home/lyj/miniconda3/envs/pfr-eval-tools/`
- 主要工具: RDKit, PLIP, AutoDock Vina, OpenBabel, Meeko, PoseBusters。

第三方方法推理环境应按方法单独创建, 不与 `pfr-eval-tools` 混用。

## 学术与实验原则

- 不伪造数据、结果或引用。
- 不只报告最好 seed。
- 不隐藏负结果。
- 不只用 Vina 证明方法有效。
- 所有结论必须可追溯到代码、配置、数据、日志、指标和文献。
