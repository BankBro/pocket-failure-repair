# DiffSBDD 审计阶段路线图

> 本文档记录 DiffSBDD 从已完成的单方法最小可行审计, 到后续原协议健全性与忠实度检查, 本项目审计协议下的扩大审计, 诊断协议冻结, 失败分布和可修复近失误子集分析的阶段流程框架. 它是 `docs/plan/20260603-02-third-party-failure-audit-alignment-plan.md` 在 DiffSBDD 上的阶段化落地路线, 不是正式失败率结果, 也不是原论文复现报告.

## 背景

当前已完成:

```text
DiffSBDD 单方法最小可行审计
```

对应实验:

- `experiment_id = 20260607-01-diffsbdd-single-method-third-party-audit-mvp`
- `run_id = r001_seed0_budget3_3rfm_47b93b20`
- 报告: `docs/report/20260608-01-diffsbdd-single-method-third-party-audit-mvp-report.md`

已验证的内容是最小闭环:

```text
最小推理
-> 捕获原始输出
-> 记录运行, 样本和阶段元数据
-> 追踪分母
-> 接通评估器和诊断健全性检查
```

尚未完成的内容包括 DiffSBDD 原协议健全性与忠实度检查, 本项目审计协议下的更大样本审计, 诊断协议冻结, 正式失败分布统计和可修复近失误子集定义.

## 目标

本路线图的目标是把 DiffSBDD 后续工作拆成可追踪阶段, 避免直接从最小可行审计跳到正式结论. 推荐路径为:

```text
DiffSBDD 最小可行审计, 已完成
-> DiffSBDD 原协议健全性与忠实度检查
-> DiffSBDD 在本项目审计协议下扩大样本
-> 冻结诊断协议
-> 统计失败分布和可修复近失误子集
```

每一阶段都应有明确输入, 输出, 准入条件, 暂停条件和结论边界.

## 结论边界

在完成诊断协议冻结和足够样本审计前, 不应声明:

- DiffSBDD 正式失败率.
- DiffSBDD 官方协议或原协议复现.
- DiffSBDD 领域级或 SBDD 方法总体结论.
- 修复 benchmark 结果.
- 可修复近失误子集的正式占比.

可以声明:

- 某一阶段的健全性, 忠实度或流程接线是否完成.
- 输出捕获和分母是否可追溯.
- 评估器覆盖度和工具结果计数.
- 当前阻塞, 风险和下一步准入条件.

## 阶段 0: 最小可行审计, 已完成

### 目的

验证 DiffSBDD 最小审计链路是否能跑通, 并确认包装脚本, 元数据, 分母和评估器接线不丢样本.

### 已完成证据

- 资源检查通过: `decision=go`, checkpoint 校验和匹配, 访问类型为公开.
- 使用 3RFM 示例完成推理, `n_samples=3`.
- `N_budget=3`, `N_final=3`, `N_evaluable=3`.
- 3 个标准化 SDF 记录均通过 RDKit parse/sanitize 检查.
- 已为 RDKit, PoseBusters `mol`, PoseBusters `dock`, PLIP, Vina 写入评估器结果行.
- 未生成正式标签.

### 主要产物

- `experiments/20260607-01-diffsbdd-single-method-third-party-audit-mvp/`
- `outputs/20260607-01-diffsbdd-single-method-third-party-audit-mvp/diffsbdd/r001_seed0_budget3_3rfm_47b93b20/`
- `docs/report/20260608-01-diffsbdd-single-method-third-party-audit-mvp-report.md`

### 准入条件

本阶段已完成. 它允许进入原协议健全性与忠实度检查, 但不允许声明正式失败分布.

## 阶段 1: 原协议健全性与忠实度检查

### 目的

确认本项目运行 DiffSBDD 的方式没有明显偏离官方代码和原始工作设置, 避免把包装脚本偏差, 环境问题或过度缩小配置造成的假象误认为方法失败.

### 建议实验身份

```text
experiment_name = diffsbdd-original-protocol-sanity
experiment_id = YYYYMMDD-<num>-diffsbdd-original-protocol-sanity
```

### 输入

优先使用:

- 官方 DiffSBDD 仓库: `third_party/diffsbdd`
- 官方 checkpoint: `third_party/diffsbdd/checkpoints/crossdocked_fullatom_cond.ckpt`
- 官方示例输入: `third_party/diffsbdd/example/3rfm.pdb`
- DiffSBDD 资源中记录的官方生成命令
- 现有方法推理环境: `pfr-diffsbdd`
- 现有评估器环境: `pfr-eval-tools`

### 前置阅读与协议摘录

阶段 1 开始运行前, 必须先阅读官方论文, README, 官方命令示例和关键代码, 并形成简短协议摘录. 该摘录应保存到对应实验目录, 也可在阶段 1 plan 或 report 中引用.

至少核查:

- 官方使用的 checkpoint, 数据集, 划分和预处理.
- 官方示例运行与正式评估流程是否不同.
- 默认 `n_samples`, `batch_size`, `sanitize`, `relax`, `resamplings`, `jump_length`, `timesteps`.
- 是否使用过滤, 最大片段保留, 几何松弛, 重排序, 对接或打分.
- 官方报告的基础指标, 例如 validity, connectivity, uniqueness, novelty, QED, SA 或 docking score.
- 官方分母口径, 例如一次性生成数量, 过滤后数量, selected 数量或重复生成直到得到足够 valid molecules.
- 本项目包装脚本和官方脚本在输出保存, 随机种子, 后处理和评估入口上的差异.

优先阅读代码:

- `third_party/diffsbdd/README.md`
- `third_party/diffsbdd/generate_ligands.py`
- `third_party/diffsbdd/test.py`
- `third_party/diffsbdd/lightning_modules.py`
- `third_party/diffsbdd/analysis/molecule_builder.py`
- `third_party/diffsbdd/analysis/metrics.py`
- `third_party/diffsbdd/analysis/docking.py`

若官方论文或 README 与代码默认值不一致, 应同时记录二者, 并在阶段 1 plan 中决定以哪个为准. 不清楚时不要直接跑正式推理.

### 设计

建议先做轻量忠实度检查, 不直接承诺完整论文复现:

```text
接近官方设置的示例运行
-> 捕获原始输出和最终输出
-> 对比官方默认参数与本项目 MVP 缩小参数
-> 计算可用的 DiffSBDD 自带基础指标
-> 使用冻结前评估器配置运行诊断健全性检查
-> 记录所有相对官方默认设置的偏离
```

需要特别记录:

- `n_samples`, `batch_size`, `sanitize`, `relax`, `resamplings`, `jump_length`, `timesteps`.
- 是否使用官方默认过滤, 最大片段保留和几何松弛.
- 是否改变采样, 解码, 重排序, 对接配置或成功定义.
- 是否只运行示例, 还是使用原测试划分子集.
- checkpoint 训练数据和泄漏风险状态.

### 必需输出

与最小可行审计运行保持同构:

```text
experiments/<experiment_id>/
  configs/resolved/
  metadata/
  scripts/

outputs/<experiment_id>/diffsbdd/<run_id>/
  captured_outputs/
  processed/
  logs/
  manifests/
  evaluator/
  summaries/
  run_metadata.json
  samples.jsonl
  output_manifest.json
  stage_attrition.json
```

若运行 DiffSBDD 自带 `test.py` 或官方风格评估 helper, 应额外保存:

```text
outputs/<experiment_id>/diffsbdd/<run_id>/official_like_metrics/
```

### 准入条件

进入阶段 2 前至少满足:

- 官方论文, README 和关键代码已阅读, 并形成协议摘录.
- 官方 checkpoint 和代码来源未改变.
- 所有相对官方默认设置的偏离都已明确记录.
- 输出数量, 基础有效性, 连通性和评估器覆盖度没有明显异常.
- 工具失败或输入限制已与方法失败分开记录.

### 暂停条件

遇到以下情况应暂停并记录阻塞:

- 需要非官方 checkpoint 或非官方数据替代.
- 原协议需要授权访问, 付费访问或许可不清的数据.
- 需要修改 DiffSBDD 核心采样或模型逻辑.
- 校验和不匹配.
- 资源成本可能超过预算.
- 接近官方设置的运行输出明显异常, 且无法由已记录设置解释.

## 阶段 2: DiffSBDD 在本项目审计协议下扩大样本

### 目的

在本项目统一审计协议下扩大 DiffSBDD 样本量, 用于观察可审计输出中的真实失败证据. 该阶段不称为原协议复现.

### 建议实验身份

```text
experiment_name = diffsbdd-our-audit-protocol-pilot
experiment_id = YYYYMMDD-<num>-diffsbdd-our-audit-protocol-pilot
```

### 输入

需要先定义:

- `dataset_id`
- `dataset_view_id`
- `split_id`
- 口袋定义规则
- 每个口袋的候选分子预算
- 随机种子列表
- 评估器工具配置
- 分母策略

如果使用规范数据集, 应按 `data/datasets/<dataset_id>/` 规范记录 raw, entries, splits, views 和 manifests.

### 设计

建议先做试点扩大, 不直接进入正式规模:

```text
小型审计数据视图
-> 固定每个口袋的 n_samples
-> 多个口袋和多个随机种子
-> 完整捕获输出
-> 写入逐样本元数据行
-> 记录评估器证据
-> 只做诊断健全性检查
```

该阶段重点不是最终标签, 而是测试统一审计协议能否稳定收集:

- 生成的最终输出.
- 缺失输出.
- 解析失败.
- 工具失败.
- 不可评估原因.
- 评估器覆盖度.
- 阶段流失.

### 必需输出

每个运行继续使用:

```text
run_metadata.json
samples.jsonl
output_manifest.json
stage_attrition.json
evaluator/evaluator_tool_results.jsonl
evaluator/diagnosis_sanity.jsonl
summaries/
```

跨运行汇总可写入:

```text
outputs/<experiment_id>/summaries/diffsbdd_audit_protocol_pilot_summary.json
outputs/<experiment_id>/tables/diffsbdd_audit_protocol_pilot_counts.tsv
```

### 准入条件

进入阶段 3 前至少满足:

- 数据视图和划分可由 schema 追溯.
- 每个运行的分母稳定且可审计.
- 评估器覆盖度足以起草标签规则.
- 缺失, 失败和不可评估样本行没有被静默删除.
- 没有未解决的方法环境阻塞.

## 阶段 3: 冻结诊断协议

### 目的

在正式统计失败率前冻结诊断规则, 避免看到结果后再调整标签定义.

### 必需决策

至少冻结:

- RDKit parse/sanitize 失败的标签归属.
- PoseBusters `mol` 检查项中哪些作为化学有效性或几何证据.
- PoseBusters `dock` 检查项中哪些作为蛋白-配体 pose 证据.
- `mol_true_loaded` 等依赖参考配体的检查项如何处理: 作为标签来源, 不适用, 还是输入限制.
- PLIP 证据是否只作为相互作用证据, 还是可以触发特定标签.
- Vina score 只作为辅助指标, 不单独定义成功或失败.
- 工具失败与方法失败的分离规则.
- 主标签和次级标签的优先级.
- 共现统计规则.
- 可修复近失误候选标准.

### 建议产物

```text
configs/audit/diagnosis_label_config_<version>.yaml
schemas/configs/audit/diagnosis_label_config_<version>.json
docs/plan/YYYYMMDD-<num>-diagnosis-protocol-freeze-plan.md
docs/report/YYYYMMDD-<num>-diagnosis-protocol-freeze-report.md
```

如果更新 schema 或配置版本, 必须记录 `schema_version` 和 `schema_path`, 并避免静默改变已被实验使用版本的语义.

### 准入条件

进入阶段 4 前至少满足:

- 标签配置版本已固定.
- 工具版本锁定文件已固定.
- 分母策略已固定.
- 代表性样本审计已经过人工抽查.
- 已记录已知工具限制和输入限制.

## 阶段 4: 失败分布与可修复近失误子集

### 目的

在冻结诊断协议下统计 DiffSBDD 输出的失败分布, 失败共现关系和可修复近失误子集.

### 输入

- 冻结后的诊断标签配置.
- 阶段 2 或更大规模审计输出.
- 稳定的评估器工具结果.
- 明确的分母表.

### 输出

建议输出:

```text
outputs/<experiment_id>/labels/labels.jsonl
outputs/<experiment_id>/summaries/label_summary.json
outputs/<experiment_id>/tables/failure_distribution.tsv
outputs/<experiment_id>/tables/failure_cooccurrence.tsv
outputs/<experiment_id>/tables/repairable_near_miss_candidates.tsv
docs/report/YYYYMMDD-<num>-diffsbdd-failure-distribution-report.md
```

### 结论边界

允许声明:

> 在指定审计协议, 冻结诊断规则, 指定 DiffSBDD checkpoint, 数据视图, 随机种子和采样预算下, 我们观察到如下失败证据分布.

不允许声明:

> DiffSBDD 的全局失败率.
> SBDD 方法的领域失败率.
> 原论文官方指标复现.
> 修复 benchmark 结果.

## 跨阶段记录位置

计划类文档:

```text
docs/plan/
```

实验配置, 脚本, 环境和资源检查:

```text
experiments/<experiment_id>/
```

真实运行输出和运行级元数据:

```text
outputs/<experiment_id>/
```

阶段报告:

```text
docs/report/
```

完整过程记录:

```text
docs/EXPERIMENT_LOG.md
```

当前项目快照:

```text
docs/STATUS.md
```

## 进入新阶段前的最小检查清单

每进入下一阶段前检查:

1. 是否有明确 `experiment_name` 和 `experiment_id`.
2. 是否完成运行前资源准入检查.
3. 是否明确结论边界.
4. 是否记录数据集版本, 数据视图, 划分和预处理.
5. 是否固定随机种子和候选分子预算.
6. 是否保留样本元数据行, 包括缺失, 失败和不可评估样本.
7. 是否记录评估器环境和工具版本.
8. 是否将所有项目自有 JSON / JSONL 元数据写入 `schema_version` 和 `schema_path`.
9. 是否追加 `docs/EXPERIMENT_LOG.md`.
10. 是否需要更新 `docs/STATUS.md` 或生成 `docs/report/`.

## 立即下一步

建议下一步是制定并执行:

```text
DiffSBDD 原协议健全性与忠实度检查
```

该实验应先用官方示例或原始测试子集做轻量忠实度检查, 明确官方默认设置与本项目最小可行审计设置之间的偏离, 再决定是否扩大到本项目审计协议试点.
