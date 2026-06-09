# DiffSBDD 原协议健全性与忠实度检查计划

> 本文档覆盖 DiffSBDD 审计路线图中的阶段 1. 阶段 1 的目标是先阅读官方论文, README 和关键代码, 摘录官方协议, 再设计并执行轻量原协议健全性与忠实度检查. 本阶段不是正式原论文复现, 不是正式失败率审计, 也不是修复 benchmark.

## 关联背景

上游路线图:

- `docs/plan/20260608-01-diffsbdd-audit-progression-plan.md`
- `docs/plan/20260603-02-third-party-failure-audit-alignment-plan.md`

已完成的阶段 0:

- 实验: `20260607-01-diffsbdd-single-method-third-party-audit-mvp`
- 报告: `docs/report/20260608-01-diffsbdd-single-method-third-party-audit-mvp-report.md`
- 结论: 最小推理, 输出捕获, 分母追踪, 元数据和评估器接线已经跑通.

阶段 1 要回答的问题是:

```text
我们运行 DiffSBDD 的方式是否足够接近官方代码和原始工作设置?
如果后续观察到失败证据, 是否能排除明显的运行偏差, 包装脚本偏差或参数缩小造成的假象?
```

## 目标与边界

本阶段覆盖:

- 官方论文, README, 命令示例和关键代码阅读.
- 官方协议摘录.
- 阶段 0 MVP 设置与官方设置的差异对照.
- 运行前资源检查.
- 轻量官方风格示例运行或小型官方风格测试.
- 输出捕获, 分母追踪, 基础指标和评估器接线复核.
- 阶段 1 通过条件, 暂停条件和报告要求.

本阶段不覆盖:

- 完整原论文指标复现.
- 大规模测试集评估.
- 本项目统一审计协议下的正式扩大样本.
- 正式失败标签生成.
- 正式失败率或可修复近失误占比.
- DiffLinker 或其他第三方方法.

## 建议实验身份

如果本阶段在 2026-06-08 执行, 建议使用:

```text
experiment_name = diffsbdd-original-protocol-sanity
experiment_id = 20260608-01-diffsbdd-original-protocol-sanity
```

如果实际执行日期不同, 按执行当天编号调整 `experiment_id`.

建议 run 命名:

```text
r001_official_example_3rfm_seed0_<configHash8>
r002_official_like_test_subset_seed0_<configHash8>
```

是否需要 `r002` 取决于前置阅读后确认官方测试流程是否可在资源预算内运行.

## 前置阅读任务

阶段 1 不应直接跑推理. 必须先阅读官方材料并形成协议摘录.

优先阅读:

- 官方论文.
- `third_party/diffsbdd/README.md`
- `third_party/diffsbdd/generate_ligands.py`
- `third_party/diffsbdd/test.py`
- `third_party/diffsbdd/lightning_modules.py`
- `third_party/diffsbdd/analysis/molecule_builder.py`
- `third_party/diffsbdd/analysis/metrics.py`
- `third_party/diffsbdd/analysis/docking.py`
- checkpoint 下载说明和官方示例命令.

阅读后至少写出:

```text
experiments/<experiment_id>/metadata/official_protocol_excerpt.md
experiments/<experiment_id>/metadata/official_protocol_checklist.json
```

其中 `official_protocol_checklist.json` 是项目自有 JSON metadata, 应写入 `schema_version` 和 `schema_path`. 若当前没有合适 schema, 可先在本阶段计划中提出新增 schema, 不要无 schema 写入项目自有 JSON.

## 官方协议摘录要点

协议摘录至少包含以下内容.

### 代码和 checkpoint

- 官方仓库地址.
- 本地仓库路径.
- 当前 commit.
- license.
- checkpoint 文件名, 来源, sha256, size 和访问类型.
- checkpoint 是否为官方来源.

### 数据和输入

- 官方训练数据和测试数据.
- 官方 split 或 example 来源.
- 官方 preprocessing.
- 官方示例输入与正式评估输入是否不同.
- 参考配体或口袋定义方式.
- 泄漏风险状态, 包括 training data unknown 时的处理方式.

### 生成参数

至少摘录:

- `n_samples`
- `batch_size`
- `num_nodes_lig`
- `all_frags`
- `sanitize`
- `relax`
- `resamplings`
- `jump_length`
- `timesteps`

并区分:

- 代码默认值.
- README 或官方示例命令值.
- 原论文实验值.
- 阶段 0 MVP 实际值.
- 阶段 1 拟采用值.

### 后处理和过滤

至少确认:

- 是否默认取最大片段.
- 是否默认执行 RDKit sanitize.
- 是否默认执行 UFF 几何松弛.
- 是否有重复生成直到获得足够有效分子的逻辑.
- 是否有过滤, 重排序, 对接或打分.
- raw output, processed output, selected output 的区别.

### 官方指标和分母

至少确认:

- 官方报告哪些基础指标, 例如 validity, connectivity, uniqueness, novelty, QED, SA, docking score.
- 每个指标的分母是什么.
- 失败生成, 无效分子, 被过滤分子是否进入分母.
- 官方输出是一次性生成固定数量, 还是重复生成直到达到固定有效数量.
- selected/final 分子是否经过过滤或排序.

## 阶段 0 与阶段 1 对照表

阶段 1 plan 执行前应填入如下对照表.

| 项目 | 官方代码默认 | 官方示例命令 | 原论文设置 | 阶段 0 MVP 设置 | 阶段 1 拟采用设置 | 偏离说明 |
|---|---|---|---|---|---|---|
| 输入 case | 待摘录 | 待摘录 | 待摘录 | `3rfm` | 待定 | 待定 |
| `n_samples` | 待摘录 | 待摘录 | 待摘录 | `3` | 待定 | 待定 |
| `batch_size` | 待摘录 | 待摘录 | 待摘录 | 默认等于 `n_samples` | 待定 | 待定 |
| `sanitize` | 待摘录 | 待摘录 | 待摘录 | 未启用 | 待定 | 待定 |
| `relax` | 待摘录 | 待摘录 | 待摘录 | 未启用 | 待定 | 待定 |
| 最大片段保留 | 待摘录 | 待摘录 | 待摘录 | 默认行为待核查 | 待定 | 待定 |
| 重复生成直到足够有效分子 | 待摘录 | 待摘录 | 待摘录 | 未使用 | 待定 | 待定 |
| 官方基础指标 | 待摘录 | 待摘录 | 待摘录 | 未作为主目标 | 待定 | 待定 |
| 对接或打分 | 待摘录 | 待摘录 | 待摘录 | 仅 Vina 辅助 evidence | 待定 | 待定 |
| 分母口径 | 待摘录 | 待摘录 | 待摘录 | `N_budget=3` metadata rows | 待定 | 待定 |

## 运行前资源检查

任何阶段 1 推理前, 必须重新写入或复用并确认:

```text
experiments/<experiment_id>/metadata/method_resource_check.jsonl
```

至少检查:

- 官方 repo, commit 和 license.
- checkpoint 来源, checksum, size 和访问类型.
- 官方数据或 example 是否需要授权, 登录, 付费或非官方镜像.
- 是否会超过 `configs/audit/resource_budget_v1.yaml`.
- 是否需要修改 DiffSBDD 核心采样, 模型逻辑, decoding, filtering, reranking, docking config 或 success definition.

遇到 gated access, license 不清, 非官方 checkpoint, checksum 不匹配, 资源可能超预算, 或需要修改 DiffSBDD 核心逻辑时, 暂停并记录 blocker.

## 实验设计

阶段 1 建议分两步, 先轻后重.

### 1. 官方示例忠实度检查

目标:

```text
确认官方 example 在接近官方默认设置下可以稳定生成输出, 并记录与阶段 0 MVP 的差异.
```

建议输入:

- `third_party/diffsbdd/example/3rfm.pdb`
- reference ligand `A:330`, 以官方命令或 README 为准.
- official checkpoint.

建议先使用官方示例命令或 README 推荐参数. 若官方默认 `n_samples=20` 且资源允许, 优先恢复到官方默认示例规模. 若因资源预算缩小, 必须标注为预算缩小的忠实度检查, 不能称为完整原协议.

### 2. 官方风格测试子集, 可选

仅当前置阅读确认 `test.py` 所需数据, split, 输入路径和资源预算可满足时执行.

目标:

```text
确认 DiffSBDD 自带测试流程中的有效性收集, 过滤和基础指标计算在本地环境可追溯.
```

若需要下载大数据, 使用授权资源, 或需要长时间调通路径, 应暂停, 记录为后续任务, 不让阶段 1 被测试子集阻塞.

## 输出规范

实验资产:

```text
experiments/<experiment_id>/
  configs/resolved/
  metadata/
  scripts/
```

run 输出:

```text
outputs/<experiment_id>/diffsbdd/<run_id>/
  captured_outputs/
  processed/
  logs/
  manifests/
  evaluator/
  summaries/
  official_like_metrics/
  run_metadata.json
  samples.jsonl
  output_manifest.json
  stage_attrition.json
```

必需 metadata:

- `run_metadata.json`
- `samples.jsonl`
- `output_manifest.json`
- `stage_attrition.json`
- `metadata/method_resource_check.jsonl`
- `metadata/env_info.json`
- `metadata/official_protocol_excerpt.md`

所有项目自有 JSON / JSONL metadata 必须写入 `schema_version` 和 `schema_path`.

## 评估和诊断边界

阶段 1 可运行:

- RDKit parse/sanitize.
- DiffSBDD 自带基础指标, 如果官方代码支持.
- PoseBusters `mol` 和 `dock`, 作为诊断接线和工具 evidence.
- PLIP 和 Vina, 仅作为辅助 evidence.

阶段 1 不生成:

- 正式 `labels.jsonl`.
- 正式 `label_summary.json`.
- 正式 failure prevalence.
- repair benchmark success/failure.

PoseBusters 中依赖参考配体或完整输入上下文的检查项, 例如 `mol_true_loaded`, 应单独记录为输入条件或工具条件相关 evidence, 不直接解释成方法正式失败.

## 阶段 1 通过条件

至少满足以下条件, 才能认为阶段 1 通过:

- 官方论文, README 和关键代码已阅读, 并有协议摘录.
- 官方 checkpoint, repo 和 license provenance 未改变.
- 所有相对官方默认或官方示例的偏离都被记录.
- 至少一个官方示例或官方风格 run 成功完成, 或清楚记录不能运行的 blocker.
- raw/final output 被捕获.
- sample metadata rows 保留完整分母.
- 基础有效性或连通性指标能够计算, 或明确记录官方代码无法在当前边界下计算的原因.
- evaluator 输出能够与样本 metadata 对齐.
- 工具失败, 输入限制和方法输出问题被分开记录.

## 暂停条件

遇到以下任一情况, 应暂停并记录 blocker:

- 官方论文, README 和代码给出的协议互相矛盾, 且无法判断以哪个为准.
- 需要获取新的大规模数据, 且大小或 license 不清.
- 需要使用非官方 checkpoint 或非官方数据镜像.
- checkpoint checksum 不匹配.
- 需要修改 DiffSBDD 模型, 采样, decoding 或后处理核心逻辑.
- 官方测试流程要求的资源超过预算.
- 输出明显异常, 且无法由参数或输入差异解释.

## 完成后记录

阶段 1 完成后必须:

- 追加 `docs/EXPERIMENT_LOG.md`.
- 必要时更新 `docs/STATUS.md`.
- 写阶段报告到 `docs/report/`, 建议命名:

```text
docs/report/YYYYMMDD-<num>-diffsbdd-original-protocol-sanity-report.md
```

报告只应声明阶段 1 的健全性与忠实度结论, 不应声明正式失败率或原论文完整复现.

## 建议立即任务

1. 阅读官方论文, README 和关键代码.
2. 填写官方协议摘录和阶段 0/阶段 1 对照表.
3. 根据摘录决定阶段 1 是否只跑官方 3RFM 示例, 或额外跑官方风格测试子集.
4. 完成 go/no-go resource check 后再运行推理.
