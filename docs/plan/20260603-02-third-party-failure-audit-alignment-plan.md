# 第三方方法失败样本审计与修复实验对齐计划

关联调研报告: `docs/report/20260603-01-failure-taxonomy-research-report.md`, `docs/report/20260603-02-failure-taxonomy-research-zh-report.md`

本文档总结当前已对齐的实验前置原则、数据与第三方方法管理方案、失败样本审计逻辑和后续实验呈现方式。核心共识是: failure taxonomy 调研的首要用途不是直接决定修复哪类错误, 而是建立有文献和工具依据的 failure diagnosis protocol, 再用它去审计真实实验流程产生的失败样本分布。只有拿到真实失败分布后, 才应决定后续修复重点、数据构造、baseline/evaluation gate 和 BIBM 论文 claim。

## 1. 总体目标

后续具体实验的第一阶段目标是复现或运行代表性现有工作, 收集其真实实验流程中产生的 raw, intermediate, rejected, failed, selected 和 final 分子样本, 再用统一 diagnosis protocol 打标签, 统计真实失败类型分布、共现关系和 repairable near-miss subset 占比。

推荐的实验逻辑为:

```text
现有方法复现或运行
→ 收集全流程样本
→ 统一 failure labeling
→ 统计 failure prevalence / co-occurrence / repairable subset
→ 根据真实分布决定后续 repair task 和模型重点
```

因此, 这批实验一开始不是为了证明某个 repair model 最强, 而是为了回答真实实验条件下失败到底如何发生、哪些失败最常见、哪些失败值得作为 local repair 目标。

## 2. Failure taxonomy 调研的定位

前序 failure taxonomy 调研的作用是建立一套有文献和工具依据的 failure diagnosis protocol。它帮助我们明确:

- 哪些工具可以判定哪些错误。
- 哪些指标可以转化为 failure labels。
- 哪些只是 metric 或 filter, 不能直接当 primary failure type。
- 哪些错误可能属于 repairable near-miss。
- 哪些错误应排除或单独统计。

调研本身不能替代真实 outputs 的失败分布审计。后续模型重点不应只由文献预设, 而应由真实失败样本的分布和可修复性决定。

## 3. 当前小数据的定位

当前 smoke, smoke-plus, controlled perturbation 和 contact-degraded local-edit 数据不适合作为正式 failure prevalence 主证据。它们更适合用于:

- 工具链调试。
- Diagnosis protocol sanity check。
- Label rule 试运行。
- Denominator 和评价口径排雷。
- 小规模机制性验证。

正式失败分布应来自后续代表性现有方法在目标实验流程中自然产生的 outputs, 而不是当前人为构造或样本数很小的诊断数据。

## 4. 候选方法的可行性与可审计性分析

正式跑实验前, 应先对候选第三方工作做 feasibility / auditability assessment, 决定哪些方法值得复现、插桩和进入主 audit。

每个候选工作至少评估以下维度:

| 维度 | 需要确认的问题 |
|---|---|
| 任务相关性 | 是否接近 pocket-conditioned generation, linker design, local edit, docking/pose prediction 或 SBDD |
| 代码可用性 | 是否有官方代码, 是否能安装, 是否有清晰 inference script |
| 模型可用性 | 是否有 pretrained checkpoint, 或训练成本是否可接受 |
| 数据可用性 | 原始数据集、split、preprocessing 是否可获得 |
| 输出可审计性 | 是否能保存 raw/intermediate/rejected/final samples |
| 源码改动需求 | 是否只需 logging/instrumentation, 不改变算法逻辑 |
| 协议忠实度 | 能否忠于原方法的 sampling, filtering, docking, reranking 和 evaluation |
| 统一 audit 适配性 | 能否在我们的统一 audit dataset 或任务协议下运行 |
| 计算成本 | GPU/CPU/时间/存储是否可接受 |
| 质量和稳定性 | 是否容易崩溃, 输出是否基本合理, 是否需要大幅修代码 |
| 泄漏风险 | audit dataset 是否可能和原训练集重叠 |
| 主实验价值 | 适合作为主 audit、selected-output audit、stress-test、related work only 还是排除 |

候选方法决策建议分为:

- 主 audit 候选。
- Selected-output audit only。
- Stress-test / negative case。
- Related work only。
- 排除。

### 4.1 第一阶段 MVP、优先级与停止规则

本文档是完整原则框架, 不应被直接理解为第一阶段必须一次性完成的全部 SOP。正式工作流应进一步拆分优先级, 防止审计范围无限扩大。

建议优先级分为:

- P0: 第一阶段必须完成。包括候选方法可行性表、少量代表性方法试运行、最小 raw/selected/final 输出捕获、轻量 diagnosis protocol、stage-wise denominator 和阻塞记录。
- P1: 主实验需要完成。包括更稳定的 instrumentation、统一 audit dataset、主要工具链诊断、per-method/per-pocket 统计、泄漏检查和 repairable near-miss subset 估计。
- P2: 论文 artifact 或扩展实验再完成。包括更大方法池、更多 seeds、完整 raw/intermediate/rejected 保存、重工具链复核、人工 case adjudication 和公开 artifact 整理。

第一阶段建议先做“可审计性试运行 + 小规模真实 outputs audit”。可先筛选 5-8 个候选方法, 再选择 2-3 个最相关、最稳定、最容易保存 outputs 的方法进入第一轮 audit。第一轮结束时主要回答:

1. 哪些第三方方法真正可审计。
2. 真实 outputs 中是否存在非偶然的 repairable near-miss subset。
3. 哪些 failure types 值得进入第二阶段正式 repair benchmark。

每个方法应设置资源和时间上限。若安装、数据获取、checkpoint 获取或插桩长期失败, 应记录原因并降级或跳过, 不应让单个方法阻塞整个计划。

## 5. 方法质量与纳入原则

主 failure distribution audit 只纳入可信、相关、可运行、可审计且输出质量基本合理的方法。质量差的方法不应自动进入主分析, 否则会把工程失败、坏实现或预处理崩溃误当成领域真实失败分布。

建议三档处理:

1. 主分析方法: 可信、相关、可运行、输出可审计, 用于统计真实 failure prevalence。
2. Stress-test / negative case: 质量一般但能暴露典型失败模式, 可单独分析, 不并入主分布统计。
3. 排除方法: 不可复现、输出明显异常、需要大幅改算法、失败主要来自工程问题, 只记录排除原因。

核心原则是统计代表性方法的自然失败分布, 而不是统计低质量实现产生的垃圾输出。

同时, 主 audit 的结论边界必须提前收窄。即使审计的是第三方真实 outputs, 也不应直接声称得到整个领域的真实失败分布。更严谨的表述应是:

> 在一组代表性、可复现、可审计的开源方法和指定数据/协议下观察到的失败分布。

因此后续 BIBM 论文 claim 应按证据逐层建立:

1. 建立可复现的 failure diagnosis protocol。
2. 审计代表性可运行方法的真实 outputs。
3. 证明 repairable near-miss failures 在该审计范围内真实存在且有一定占比。
4. 基于该 subset 构造 repair benchmark。
5. 在同预算、同输入、同 evaluation gate 下比较 repair baselines 和本项目方法。

不能从有限方法的审计结果直接外推到所有 pocket-conditioned generation 或 SBDD 方法。

## 6. 忠于原始工作与统一 audit protocol

实验应分成两层。

### 6.1 原协议复现层

如果目标是验证某个方法是否跑通、是否接近原论文结果, 应尽量忠于原始工作:

- 原数据集版本。
- 原 train/validation/test split。
- 原 preprocessing。
- 原模型权重。
- 原 sampling budget。
- 原 filtering/reranking。
- 原 docking/scoring。
- 原评价指标和分母。

这部分可称为 original-protocol reproduction 或 sanity check。

### 6.2 本项目 audit protocol 层

如果目标是比较失败分布, 可以把方法放到我们的统一 audit dataset 和统一 diagnosis protocol 下运行。此时必须明确称为:

- Method X under our audit protocol。
- Adapted baseline。
- Instrumented reproduction。

不能把换数据、换评价或换任务后的结果称为原论文官方性能。

## 7. 数据集使用策略

数据集策略不是简单二选一。推荐双轨制:

1. 原协议复现: 原工作用什么数据集和 split, 就先用什么, 用于确认复现可信度。
2. 统一 audit dataset: 为回答我们关心的失败分布问题, 可补充统一数据集和统一诊断协议, 用于跨方法比较。

适合补充统一数据集的情况包括:

- 原数据集太小。
- 原数据集不覆盖我们关心的 pocket/local-edit/linker 场景。
- 原数据集只报告 final selected molecules, 不适合 failure audit。
- 多个方法原本数据集不同, 需要统一分母比较。
- 我们想知道方法在更接近本项目任务的数据上会产生什么失败。

不适合补充的情况包括:

- 新数据集和方法任务明显不匹配。
- 方法需要特殊输入, 强行适配会大改算法。
- 补数据集导致训练/测试泄漏风险。
- 补数据只是为了让某方法表现更好或更差。
- 无法保持相同 preprocessing, budget 和 evaluation。

### 7.1 多个方法共享同一数据集时的数据管理

如果多个第三方工作都声称使用同一个数据集, 不应让每个方法在各自目录里重复保存一份数据, 也不能简单假设它们的数据完全相同。推荐采用:

```text
canonical raw dataset
→ method-specific dataset view
→ concrete run metadata
```

核心原则是: 原始数据统一保存一份且尽量不可变; 不同方法的数据处理版本、split、过滤规则和输入格式作为不同 dataset view 管理; 原协议复现使用对应方法自己的 dataset view; 统一 failure audit 使用本项目统一 audit dataset view。

#### 7.1.1 原始数据只保存一份

同一个官方数据集版本只保存一份 canonical raw dataset, 例如:

```text
data/datasets/<dataset_id>/raw/
```

该目录应记录数据集名称、版本、来源、下载日期、license、citation、checksum、是否需要授权、是否允许再分发以及原始 split 是否可得。Raw dataset 层不应随意清洗、重命名或删除样本。

#### 7.1.2 不同 preprocessing 和 split 作为 dataset view

不同论文即使都写使用 PDBBind、CrossDocked 或 MOAD, 实际也可能使用不同版本、subset、split、receptor cleaning、ligand protonation、pocket radius、过滤规则或输入格式。因此应把它们记录为不同 dataset view, 例如:

```text
data/datasets/<dataset_id>/views/<method_name>_original_v1/
data/datasets/<dataset_id>/views/our_audit_protocol_v1/
```

如果经过核验证明多个方法确实使用同一个 dataset version、split、preprocessing 和输入格式, 可以共享同一个 dataset view。但不能仅因为论文都写了同一个数据集名称就默认共享。

每个 dataset view 至少应记录:

```yaml
source_dataset: "..."
source_version: "..."
source_path: "data/datasets/<dataset_id>/raw/..."
view_id: "..."
method: "..."
preprocessing_script: "..."
preprocessing_config: "..."
split_id: "..."
included_complexes: "..."
excluded_complexes: "..."
checksum: "..."
```

#### 7.1.3 原协议复现与统一 audit 的区别

原协议复现时, 应尽量忠于该方法原论文的数据版本、split、preprocessing、filtering、pocket definition、ligand preparation 和 evaluation input format。此时即使多个方法使用同名数据集, 也应分别记录各自的 original dataset view。

统一 audit protocol 时, 为了跨方法比较失败分布, 应尽量让多个方法运行在同一个 `our_audit_protocol_v1` dataset view 上, 并保持相同分母、输入约束、candidate budget 和 evaluation gate。此时结果应明确称为 method under our audit protocol, 不能称为原论文官方性能。

#### 7.1.4 Run metadata 必须记录数据来源

每个第三方 run 和后续失败样本 metadata 中应记录所使用的数据版本和 view, 例如:

```json
{
  "dataset_name": "PDBBind",
  "dataset_version": "2020",
  "source_dataset_path": "data/datasets/pdbbind_2020/raw/",
  "dataset_view_id": "our_audit_protocol_v1",
  "preprocessing_id": "pocket_radius10_clean_v1",
  "split_id": "audit_protocol_split_v1",
  "complex_id": "...",
  "pdb_id": "...",
  "raw_checksum": "...",
  "processed_checksum": "...",
  "leakage_check_status": "passed|possible_overlap|unknown|failed"
}
```

#### 7.1.5 共享数据集下的泄漏检查

多个方法共用或声称共用同一数据集时, 必须特别检查数据泄漏风险, 包括:

- audit/test complex 是否出现在某方法训练集中。
- PDB ID 是否重叠。
- protein sequence 是否高度相似。
- ligand 或 scaffold 是否重叠。
- 某方法的 test set 是否可能被另一个方法当作 train set。
- checkpoint 训练数据未知时, 应标记为 `training_data_unknown` 或 `leakage_risk_unknown`。
- 从 audit outputs 构造 repair benchmark 时, 应避免同一 method、pocket 或 complex 无隔离地同时用于 repair model 开发和最终测试。

简单原则是: 原始数据共享, 处理版本分开; 原协议复现忠于各自数据处理, 统一 audit 使用统一 dataset view; 所有 run 都必须记录 dataset version、view、split、preprocessing、checksum 和泄漏检查状态。

## 8. 原数据集获取不到时的处理

如果原工作的数据集获取不到, 不应硬凑成原协议复现。建议分情况处理:

- 有官方替代或公开子集: 使用作者提供或官方推荐的替代数据, 并说明原因。
- 原数据不可得但方法可运行: 放到我们的统一 audit dataset 上运行, 标注为 adapted / audit protocol。
- 只有 checkpoint 没有原数据: 可以用 checkpoint 在 audit dataset 上推理, 但需检查输入格式、preprocessing 和训练集重叠风险。
- 数据和方法都不可审计: 不进入主实验, 只作为 related work 或排除记录。

禁止随便找一个类似数据集然后声称复现了原论文协议。

### 8.1 源码、数据集或 checkpoint 获取受阻时的处理

如果后续 agent 在获取第三方源码、数据集、split、preprocessing 文件或 checkpoint 时遇到阻碍, 不应擅自替换核心资源, 也不应让单个方法长期阻塞整个实验计划。应先分类、记录、降级或标记 pending, 然后暂时跳过并继续下一个候选方法。

常见阻塞类型包括:

- 源码不可访问, repo 失效, branch/tag 不存在。
- license 不清楚或不允许使用。
- checkpoint 缺失, 官方下载链接失效。
- 数据集链接失效, 数据需要申请、登录或授权。
- 原始 split 或 preprocessing 文件缺失。
- 环境依赖无法安装或运行脚本缺失。
- 输出格式与论文描述不一致。
- 计算资源、存储或下载规模超出当前可接受范围。

Agent 可优先尝试官方或可核验 fallback, 例如官方 GitHub release, Zenodo, Figshare, OSF, HuggingFace, 作者补充材料, README, issue, release note, 官方替代数据集或公开 subset。但如果原数据、原 checkpoint 或原代码仍不可得, 不能随便换一个“相似资源”后继续声称 original-protocol reproduction。

每个阻塞尝试都应写入可行性表或实验日志, 至少记录:

```text
method:
resource:
attempted_source:
failure_type:
evidence:
decision:
fallback:
risk_note:
```

最终状态可标记为:

- `ready_for_original_repro`
- `ready_for_instrumented_audit`
- `audit_protocol_only`
- `selected_output_only`
- `blocked_pending_resource`
- `blocked_pending_user_decision`
- `related_work_only`
- `excluded_with_reason`

需要人工决策的情况应暂停并汇报, 包括: 需要申请受限数据, license 不清楚, 需要联系作者, 需要使用非官方镜像, 需要下载特别大的数据或 checkpoint, 需要替换核心数据集, 或需要改算法才能运行。

如果 agent 尝试合理路径后仍解决不了, 应如实记录阻塞原因和已尝试来源, 将该方法标记为 pending、降级或排除, 暂时跳过, 后续资源补齐后再回头处理。

## 9. 失败样本获取与插桩

很多原始工作可能只公开最终 top-k 分子、过滤后的 valid molecules、aggregate metrics 或少量 case study, 不会保存 raw generated attempts, invalid molecules, rejected candidates, docking failed samples, reranking 前候选或 intermediate poses。

因此后续应优先选择可运行、可插桩、可保存 raw/rejected/intermediate outputs 的开源方法。

如果原代码默认不保存失败样本, 可以进行 instrumented reproduction。优先顺序为:

```text
wrapper 捕获输出
→ logging / instrumentation patch
→ 如果必须改算法, 降级为 adapted baseline 或排除
```

可接受的改动包括:

- 保存 raw generated molecules。
- 保存 filter 前后 candidates。
- 保存 rejected samples 和 rejected reason。
- 保存 RDKit invalid / sanitization failure。
- 保存 docking input/output。
- 保存 reranking 前候选。
- 保存 intermediate poses。
- 保存 error logs。

不可接受的打桩改动包括:

- 改 sampling 策略。
- 改 model forward 或 decoding rule。
- 改 filtering threshold。
- 改 reranking score。
- 改 docking config。
- 改 success definition。
- 改 candidate budget。

如果只能拿到 final outputs, 只能做 selected-output residual failure audit, 不能称为 raw failure distribution。

## 10. 第三方代码管理

第三方实验和方法代码应采用“原始代码隔离 + 轻量插桩 + 项目统一接口”的管理方式。

推荐目录结构:

```text
third_party/
  <method>/

third_party_patches/
  <method>_capture_outputs.patch
  <method>_capture_rejected_candidates.patch

scripts/third_party/
  run_<method>_instrumented.py
  collect_<method>_outputs.py

scripts/audit/
  label_failure_outputs.py
  summarize_failure_prevalence.py

configs/third_party/
  <method>_original_protocol.yaml
  <method>_audit_protocol.yaml

experiments/<experiment_id>/
  command.sh
  configs/
  scripts/
  run_metadata.json
  notes.md

outputs/<experiment_id>/
  <method>/
    <run_id>/
```

其中先定义 `experiment_name = xxx`, 再定义 `experiment_id = YYYYMMDD-<num>-<experiment_name>`. 若该实验后续有 plan/report 文档, 文档文件名中的 `xxx` 优先使用同一个 `experiment_name`。`run_id` 可作为实验内部的 method/case/seed 子运行编号, 不替代 `experiment_id`。
每个第三方方法需要记录:

- repo URL。
- commit hash。
- license。
- checkpoint 来源。
- 原始数据来源。
- 是否做了 patch。
- patch 是否改变算法逻辑。
- 输出保存方式。
- conda/docker 环境、Python/CUDA/依赖版本。
- 完整运行命令、config hash、random seed、硬件信息和 stdout/stderr log。

Git 管理原则:

- 不提交大 checkpoint。
- 不提交大规模 raw outputs。
- 不提交大数据集。
- 提交 wrapper, configs, patch, notes, schema, summary 和小规模示例。
- 所有过程写入 `docs/EXPERIMENT_LOG.md`。

第三方资源还应有 license 和 artifact policy。需要确认第三方代码、checkpoint、数据集、PDB/protein/ligand 文件、生成分子 outputs 是否允许修改、使用、再分发或作为论文 artifact 公开。对于 license 不清楚、需要登录/申请或禁止再分发的资源, 只能记录来源、配置、摘要和可复现实验说明, 不能直接提交到仓库或公开 artifact。

### 10.1 Fork 与分支管理

如果第三方方法只需要原样运行、不改源码, 可以直接 clone 官方仓库到 `third_party/<method>/`, 并记录 upstream repo URL, commit hash, license, 环境和运行配置。

如果需要改源码来保存 raw, intermediate 或 rejected samples, 推荐 fork 官方仓库并新建本项目专用分支。分支命名应能反映改动性质, 例如:

```text
pfr-original-repro        # 尽量不改, 用于原协议复现
pfr-audit-logging         # 只加 logging/output capture, 不改变算法逻辑
pfr-audit-protocol        # 适配本项目 audit dataset, 但尽量不改算法
pfr-adapted-baseline      # 如果必须改输入、任务或流程, 明确降级为 adapted baseline
```

小规模、一次性的 logging 改动可以先保留为 patch 文件, 例如 `third_party_patches/<method>_capture_outputs.patch`。但如果某个方法要进入长期实验、主 audit 或论文复现, 应尽量使用 fork commit 固定版本。

每个第三方 run 的 metadata 应记录:

```json
{
  "method": "...",
  "upstream_repo": "...",
  "upstream_commit": "...",
  "fork_repo": "...",
  "fork_branch": "pfr-audit-logging",
  "fork_commit": "...",
  "patches": ["..."],
  "algorithm_changed": false
}
```

如果源码改动只增加日志、保存中间样本或捕获错误, 可称为 instrumented reproduction。如果改动影响 sampling, decoding, filtering, reranking, docking config, score function, success definition 或 candidate budget, 则必须降级为 adapted baseline, 不能再声称是忠实复现。

## 11. 失败样例管理

失败样例应作为可追溯的数据资产管理, 不能只是散落的 SDF 或 log。

推荐输出结构:

```text
outputs/<experiment_id>/<method>/<run_id>/
  captured_outputs/
  processed/
    normalized_samples/
  labels/
  summaries/
  logs/
  run_metadata.json
```

对应实验脚本、命令、配置快照和 metadata 应保存在 `experiments/<experiment_id>/`。
若某些失败样例后续要成为我们自己的训练/评估数据, 再整理到:

```text
data/datasets/failure_audit_<version>/entries/
```

每个样本必须有稳定唯一 ID, 例如:

```text
<method>_<dataset>_<complex_id>_<stage>_<sample_index>
```

每个样本应至少有一条 JSONL metadata 记录, 包括:

```json
{
  "sample_id": "...",
  "method": "...",
  "method_repo": "...",
  "method_commit": "...",
  "run_id": "...",
  "dataset": "...",
  "split": "...",
  "complex_id": "...",
  "receptor_path": "...",
  "ligand_path": "...",
  "stage": "raw|filtered|rejected|selected|final",
  "molecule_path": "...",
  "pose_path": "...",
  "original_status": {},
  "audit_labels": {},
  "quality_flags": {},
  "sha256": "..."
}
```

Captured method outputs 尽量不可变。若需要清洗、标准化、加氢或格式转换, 应另存到 `processed/normalized_samples/`, 并在 metadata 中记录原始路径、标准化后路径、脚本版本和清洗规则。

不可评价或质量差的样本不要直接删除, 而是保留记录并设置 `quality_flags`, 区分 molecule failure, pipeline failure, tool failure, missing data 和 low-quality reproduction。

从 audit outputs 进一步构造 repair 训练或评估数据时, 应避免二次泄漏。建议区分:

```text
audit-discovery set
repair-train set
repair-validation set
repair-test set
```

至少最终 repair-test set 应在 method、pocket、complex、protein family 或 scaffold 层面与模型开发数据隔离。不能无隔离地用同一批失败样本同时决定 repair focus、调参和做最终测试。

## 12. 失败标签记录方式

一个第三方方法产生的失败样本应同时记录两套信息。

### 12.1 原始工作自己的状态

用于忠实解释该样本在原方法流程中为什么被保留、丢弃或判为失败。字段可包括:

- original validity。
- original filter pass/fail。
- original score。
- original rank。
- original rejected reason。
- original success/failure definition。
- original stage。

### 12.2 我们统一 diagnosis protocol 的标签

用于跨方法统一比较失败分布。字段可包括:

- primary failure type。
- secondary failure tags。
- RDKit flags。
- PoseBusters failed columns。
- scaffold/anchor status。
- PLIP/ProLIF interaction loss。
- Arpeggio/MolProbity clash。
- property flags。
- pipeline failure status。

不能只用原始工作定义, 因为不同工作定义不统一。也不能无视原始工作定义, 因为它解释了样本所处阶段、被丢弃原因和原始分母变化。

## 13. Denominator 和阶段统计

所有失败率都必须说明分母, 不能混算。常见分母包括:

- raw generation attempts。
- parsed molecules。
- RDKit valid molecules。
- scaffold/anchor preserved molecules。
- docked poses。
- evaluable poses。
- rejected candidates。
- selected candidates。
- final outputs。
- PoseBusters-evaluable poses。
- repair-eligible near-miss subset。

每个 run 应至少输出 stage-wise attrition summary, 记录从 raw 到 final 的样本流失过程。

除 stage-wise denominator 外, 还应提前固定统计汇总方式, 避免某个生成样本数特别多的方法支配总体结论。建议至少报告:

- Per-method failure prevalence。
- Per-pocket 或 per-complex failure prevalence。
- Sample-weighted aggregate。
- Method-weighted aggregate。
- 多 seed 时的 mean/std 或 interval。
- 关键比例的 bootstrap confidence interval, 如果样本量允许。
- Multi-label co-occurrence matrix。
- `not_evaluable`, `tool_failure`, `pipeline_failure` 和 `missing_data` 的单独比例。

如果要汇总跨方法总体结果, 应同时展示 sample-weighted 和 method-weighted 版本, 并说明不可评价样本是否进入对应分母。

## 14. Primary failure type 与 secondary tags

由于一个样本可能同时有多个失败标签, 后续应采用:

```text
primary failure type + secondary diagnostic tags
```

Primary failure type 用于表示最主要、最可行动的错误类型。Secondary tags 用于记录具体工具证据和共现错误。

需要提前固定:

- primary failure type 怎么选。
- secondary tags 记录哪些工具证据。
- pipeline failure 是否单独记录。
- property failure 是否只作为 metric/filter。
- interaction loss 是否允许等价替代 interaction。
- docking score 差是否不能单独作为 primary label。

建议后续为 primary failure type 制定 precedence hierarchy, 避免多标签样本被主观挑选主错误。可采用类似顺序:

```text
pipeline/tool/missing-data failure
→ chemical invalid / RDKit parse or sanitize failure
→ graph/scaffold/anchor failure
→ global pose collapse / pocket detachment
→ local geometry / internal clash / protein-ligand clash
→ interaction/contact loss
→ property/filter-only failure
→ unknown / not evaluable
```

`not_evaluable`, `unknown`, `tool_failure`, `pipeline_failure` 和 `missing_data` 必须允许作为独立状态, 不能强行归入某个 molecular failure type。每批标签还应记录 diagnosis protocol version、tool versions、threshold config、label script commit 和 label config hash。

## 15. Repairable near-miss subset 定义

第一阶段最相关的失败子集应是 repairable near-miss local failures。建议定义条件包括:

- RDKit valid。
- Scaffold/anchor preserved。
- Ligand 仍在 pocket 附近。
- 失败主要来自局部 geometry, protein-ligand clash, anchor attachment, local pose/torsion 或 interaction/contact。
- 不是 pipeline failure。
- 不是严重 chemical invalid。
- 不是 scaffold/core 全局丢失。
- 不是完全 global pose collapse。
- 不是纯 property filter failure。

该 subset 的占比是后续任务价值的重要证据。如果占比高, fixed-scaffold local repair 主线更有说服力。如果占比低, 应调整任务重点或实验路线。

如果第一阶段发现 repairable near-miss subset 占比很低, 不应为了维持预设模型路线而改变 label 或 denominator。可选处理包括: 转向 selected-output residual failure audit, 缩小到更明确的 local-edit/linker 场景, 调整 repair task 定义, 将 diagnosis benchmark 作为更主要贡献, 或如实报告该负结果并重新评估 BIBM claim。

## 16. 后续 repair 实验评价原则

当进入修复模型比较时, 必须对齐以下内容:

- Budget fairness。
- no-feedback / identity / rerank-only / Best-of-N / rule repair / geometry refinement / learned repair / oracle / teacher / shallow policy。
- 是否使用 reference 或 oracle 信息。
- 是否同输入、同预算、同 evaluation gate。
- 不只看 Vina score。
- 同时看 RDKit valid, scaffold/anchor preservation, geometry/PoseBusters, pocket clash, interaction/contact recovery 和 repair gain。
- 必须报告相对 failed candidate 的 repair/recovery gain。

尤其要避免 identity/no-feedback 原地不动也被算作 repair 成功。

## 17. 最终实验数据与结果呈现

本节是远期论文结果呈现框架, 不是当前第一阶段 MVP 或第三方 failure audit 当前执行任务。它用于提前说明: 如果后续基于 audit 结果进入 repair benchmark 和完整论文实验, 最终证据应如何组织。

最终结果应分为 audit 结果和 repair 结果两部分。

### 17.1 Audit 结果

Audit 结果回答“真实失败分布是什么”。建议包括:

1. 方法可行性 / 可审计性表。
2. Stage-wise attrition table。
3. Failure label prevalence table。
4. Multi-label co-occurrence heatmap。
5. Repairable near-miss subset 占比。
6. Selected-output residual failure audit, 如果某些方法只能拿 final outputs。
7. 排除方法和排除原因。

### 17.2 Repair 结果

Repair 结果回答“我们能否修复其中有价值的失败”。建议包括:

1. Repair task dataset summary。
2. Baseline comparison table。
3. Failure-type stratified repair results。
4. Feedback ablation table。
5. Budget fairness audit。
6. Repair gain bar plot。
7. Case studies。
8. 负结果和边界案例。

论文叙事顺序建议为:

```text
候选方法可行性分析
→ 代表性方法真实输出失败分布
→ repairable near-miss failures 是真实存在的子集
→ 基于该子集构造 repair benchmark
→ 同预算 repair baseline 和我们方法比较
→ 分错误类型结果、feedback 消融、案例分析和局限性
```

## 18. 当前结论

当前对齐的实验原则可以概括为:

> 先基于文献和工具建立 failure diagnosis protocol, 再选择可信、相关、可审计的开源方法进行忠实或插桩复现, 收集真实流程中的 raw/intermediate/rejected/final 分子, 同时保留原方法状态和我们的统一 failure labels, 在固定 denominator 下统计真实失败分布和 repairable near-miss 占比, 最后再决定修复重点、数据构造、baseline、模型路线和 BIBM claim。

该原则应作为后续第三方方法复现、失败样本审计和 repair benchmark 构建的前置约束。
