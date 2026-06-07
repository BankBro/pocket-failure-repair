# 第三方方法失败样本审计详细执行计划

目标文件: `/home/lyj/mnt/project/pocket-failure-repair/docs/plan/20260603-03-third-party-failure-audit-detailed-execution-plan.md`

上游对齐文件: `/home/lyj/mnt/project/pocket-failure-repair/docs/plan/20260603-02-third-party-failure-audit-alignment-plan.md`

文档状态: `persisted_draft`. 本文为已落盘的详细执行方案草案, 用于指导后续第三方方法 feasibility / auditability assessment, 第一阶段 MVP audit 设计, 以及 repair benchmark 构建规划。后续进入真实执行阶段时, 应按本文 §9.12 追加 `/home/lyj/mnt/project/pocket-failure-repair/docs/EXPERIMENT_LOG.md` 并同步 `/home/lyj/mnt/project/pocket-failure-repair/docs/STATUS.md`.

本文档把上游对齐计划中的原则固化为执行方案. 本文不重新推翻既有原则, 不给出实验结果, 不下载数据, 不 clone 第三方仓库, 不运行第三方方法或诊断工具. 后续任何执行都必须先满足本文定义的 feasibility, auditability, data provenance, leakage, diagnosis, denominator, repair benchmark 和 claim boundary 要求.

## 0. Scope, non-goals, persistence 和 BIBM claim 边界

### 0.1 Scope

本执行计划覆盖第三方方法 failure audit 的可行性评估, 可审计性评估, 第一阶段最小真实输出审计 MVP 的设计边界, failure diagnosis protocol 预注册, denominator/statistics 口径, repairable near-miss benchmark 预注册, baseline/evaluation fairness 设计, 以及 BIBM 论文 claim/artifact 边界.

第一轮工作的目标不是证明 repair model 最强, 而是回答以下执行性问题:

1. 哪些第三方 pocket-conditioned generation, linker/local edit, SBDD generation, docking/pose-conditioned generation 或 pocket-bound molecular output 方法可运行, 可追溯, 可审计.
2. 哪些方法能捕获自然流程中的 raw, parsed, normalized, filtered, rejected, selected, final 以及 upstream/original failed samples 等样本流转对象, 而不是只能看到 final/top-k outputs.
3. 每个方法适合进入 `original_protocol_reproduction`, `instrumented_reproduction`, `audit_protocol_run`, `adapted_baseline`, `stage_limited_audit`, `selected_output_residual_audit`, `related_work_only`, 还是 `excluded`.
4. 统一 diagnosis protocol, label schema, tool versions, thresholds, denominator, sample lineage 和 statistics 能否在真实 audit 前被冻结.
5. 后续第一阶段执行时, 2-3 个代表方法的小规模真实 output audit 能否捕获最小 raw/selected/final 或 stage-limited evidence, 并回答真实 outputs 中是否存在非偶然 repairable near-miss.
6. repairable near-miss subset 是否有可执行的 eligibility, split isolation, baseline 和 evaluation gate 设计, 以及低占比时如何降级.

### 0.2 当前文档阶段与后续执行阶段的分离

本文档阶段只制定方案, 不运行实验. 但是, 如果项目继续进入“第一阶段 MVP 执行”, 该执行不能只停留在表格和设计层面, 必须在冻结 schema/config/tool_versions/denominator/hash 后完成小规模真实输出审计.

必须区分以下两件事:

| 层级 | 允许内容 | 禁止内容 |
|---|---|---|
| 本文档规划阶段 | 固定 scope, gate, schema 草案, resource 阈值, trial design, claim boundary | 下载数据, clone repo, 运行第三方方法, 运行 diagnosis, 声称真实 prevalence |
| 后续第一阶段 MVP 执行 | 在冻结协议后运行 2-3 个代表方法的小规模真实 output audit, 捕获最小 raw/selected/final 或 stage-limited evidence, 记录 negative results | 在 schema/hash 未冻结前给正式标签, 从 final-only 推断 raw distribution, 把小样本外推为 field-wide conclusion |

### 0.3 Non-goals

本计划阶段明确不做以下事情:

- 不下载第三方数据, checkpoint 或大文件.
- 不 clone 第三方代码仓库.
- 不运行第三方训练, 推理, docking, labeling 或 repair 实验.
- 不把当前 smoke, smoke-plus, controlled perturbation 或 contact-degraded local-edit 数据当作正式 failure prevalence 证据.
- 不把现有 sanity/control 数据当作第三方真实 output near-miss prevalence 证据.
- 不把 adapted audit protocol 结果称为原论文官方复现性能.
- 不从 final-only outputs 推断 raw failure distribution.
- 不为了纳入更多方法而修改 sampling, decoding, filtering, reranking, docking config, candidate budget 或 success definition.
- 不用 Vina/docking score 单独证明 repair success.
- 不伪造数据, 结果, 引用, split, checksum, resource provenance 或 negative result.

### 0.4 目标文件落盘 gate

若本计划作为阶段交付物, 必须满足:

```text
plan_target_path=/home/lyj/mnt/project/pocket-failure-repair/docs/plan/20260603-03-third-party-failure-audit-detailed-execution-plan.md
persistence_status=exists_and_matches_accepted_markdown
```

在目标文件不存在或未包含最终接受版本时, 全部后续记录必须写:

```text
persistence_status=plan_draft_not_persisted
```

此状态下允许把本文作为讨论稿引用, 但不得在 `/home/lyj/mnt/project/pocket-failure-repair/docs/STATUS.md` 中写成“详细执行计划已落盘完成”.

### 0.5 BIBM scope statement

后续论文只能声称: 本项目在一组代表性, 可复现, 可审计的开源方法和指定 dataset view, split, budget, diagnosis protocol 与 evaluator 版本下, 观察并量化了这些方法输出流程中的失败模式, 并在其中定义 repairable near-miss subset 与相应 repair benchmark.

本项目不声称得到整个 SBDD, pocket-conditioned generation 或分子生成领域的真实失败分布. 对更广泛方法族的意义只能作为 motivation, hypothesis 或 future work, 不能作为已证实结论.

### 0.6 Claim ladder

| Claim level | 可允许主张 | 必需证据对象 | 禁止外推 |
|---|---|---|---|
| L0 | 建立 failure diagnosis protocol | `label_schema.json`, `label_config.yaml`, `tool_versions.lock`, threshold config, sanity check log | 不声称真实失败分布 |
| L1 | 完成候选方法 feasibility/auditability 评估 | method feasibility table, resource blocker log, artifact card | 不声称方法已复现或可比较 |
| L2 | 在 scoped methods/protocol 下审计 raw/intermediate/rejected/selected/final outputs | run manifest, sample metadata, stage attrition, denominator table | 不外推到未纳入方法或 final-only 方法 |
| L3 | 证明 repairable near-miss subset 在该范围内存在并估计占比 | fixed denominator prevalence, bootstrap interval, near-miss metadata | 不声称所有失败都可修 |
| L4 | 基于该 subset 构造 repair benchmark | dataset card, split policy, leakage report, inclusion/exclusion reason | 不把 audit-discovery 当作 final repair-test |
| L5 | 同输入, 同预算, 同 evaluation gate 下比较 repair baselines 和本项目方法 | baseline config, budget audit, paired gain, stratified results | 不用 Vina-only 或 best seed 证明 superiority |
| L6 | 对更广泛方法族提出意义 | discussion, limitation, hypothesis | 不能写成 field-wide true failure distribution |

### 0.7 Allowed wording vs forbidden wording

| 允许措辞 | 禁止措辞 |
|---|---|
| observed under our audit protocol | field-wide true failure distribution |
| original-protocol reproduction, when data/split/preprocessing/evaluation unchanged | official reproduction, when data or evaluation changed |
| instrumented reproduction, when only logging/output capture is added | reproduction, when sampling/filtering/reranking/docking changed |
| method under our audit protocol | original paper performance under substituted dataset |
| adapted baseline | faithful reproduction after algorithm-level adaptation |
| stage-limited audit | raw failure distribution from missing raw/N_budget lineage |
| selected-output residual audit | raw failure distribution from final-only outputs |
| repair gain on eligible near-miss failures | model solves pocket generation failures broadly |
| docking score as auxiliary metric | Vina-only success |
| improvement relative to failed candidate | repair success without target-failure resolution |

### 0.8 Resource budget and automatic blocking threshold

所有“资源可控”, “大下载”, “超大资源”, “训练成本可接受”等判断必须引用同一个 resource budget config. 后续执行前建议保存为配置, 并在 method feasibility table 和 resource blocker log 中记录 config hash. 若项目未显式修改, 默认阈值如下:

```yaml
resource_budget_config_version: pfr_third_party_audit_resource_budget_v1
max_download_per_method_gb: 10
max_total_download_gb_for_first_stage: 50
max_storage_per_method_gb: 30
max_total_storage_gb_for_first_stage: 100
max_env_setup_wallclock_hours_per_method: 4
max_paper_code_assessment_hours_per_method: 4
max_output_capture_assessment_hours_per_method: 8
max_minimal_inference_trial_wallclock_hours_per_method: 8
max_gpu_hours_per_method_for_mvp: 24
max_cpu_hours_per_method_for_mvp: 24
max_checkpoint_count_per_method_for_mvp: 1
allow_gated_data_without_user_decision: false
allow_non_official_mirror_without_user_decision: false
allow_paid_resource_without_user_decision: false
allow_contact_author_without_user_decision: false
unknown_core_resource_size_policy: blocked_pending_user_decision
```

规则:

- 任何核心资源超过阈值, 标记 `blocked_pending_user_decision`, 不由 agent 自行决定.
- 任何核心资源大小未知且无法由官方页面, DOI, release metadata 或 checksum manifest 估计到阈值以内, 标记 `blocked_pending_user_decision`.
- 任何受限数据, 登录/申请资源, 非官方镜像, 付费资源, 联系作者, 核心 dataset 替换, 训练数据未知 checkpoint 作为主证据, 或算法级适配, 都必须暂停并请求用户决策.
- 若用户批准更高预算, 必须记录新的 `resource_budget_config_version`, config hash, 用户决策来源和适用范围.

## 1. 阶段化执行总览

每个阶段都必须产出可追溯 evidence object. 单个方法不得无限阻塞整体计划. 默认停止上限为: paper/code assessment 半天, 环境可行性 1 天, 最小推理与输出捕获判断 1 天. 超过上限仍无法通过 gate 时, 必须降级, pending 或排除.

真实 output audit, labeling, near-miss 判定和统计必须等待 Phase 5 的 analysis-frozen gate 通过后才能执行. Phase 4 可以提前设计 trial, 但不能提前运行或生成正式标签.

| 阶段 | 名称 | 主要产物 | 核心 gate |
|---|---|---|---|
| Phase 0 | 协议, 边界与落盘预注册 | scope sheet, claim ladder, resource budget config, persistence gate, schema freeze checklist | 是否能在不跑实验前固定边界 |
| Phase 1 | 候选方法筛选与 feasibility table | longlist, hard exclusion log, feasibility table, decision tier | pre-screen gate |
| Phase 2 | 数据资产, dataset view, split 与 leakage SOP | raw manifest template, view manifest template, split registry, leakage checklist | data provenance gate |
| Phase 3 | 第三方代码, fork, patch, 插桩与资源阻塞评估 | method artifact card, instrumentation plan, resource blocker log | resource gate + instrumentation gate |
| Phase 4 | 第一轮最小 audit trial 设计 | 2-3 方法 trial plan, run boundary label, capture schema, stage denominator plan | audit-readiness design gate |
| Phase 5 | Diagnosis protocol, label schema 与统计口径冻结 | label schema/config, tool versions, stage attrition schema, statistics plan | diagnosis/statistics analysis-frozen gate |
| Phase 5E | 第一阶段 MVP 真实 output audit 执行 | 2-3 方法最小真实输出捕获, run metadata, labels, stage attrition, near-miss MVP evidence | frozen-protocol execution gate |
| Phase 6 | Repairable near-miss benchmark 与 baseline/evaluation 预注册或构造 | eligibility config, split policy, baseline taxonomy, budget fairness table, evaluation gate | repair-benchmark gate |
| Phase 7 | 结果呈现, negative result, artifact 与 BIBM claim 管理 | figure/table map, artifact registry, release tiers, reproducibility manifest | claim/artifact gate |

Phase 5E 不是本文档阶段要执行的工作, 但如果后续宣称“第一阶段 MVP 已完成”, Phase 5E 是必需的, 不能被替换为纯表格设计.

## 2. Phase 0: 协议与边界预注册

### 2.1 目标

在任何数据下载, 代码 clone 或实验运行之前, 固定本轮 audit 的范围, 非目标, run type 术语, claim ladder, schema 版本化原则, resource budget 和 stop rules, 防止后续出现 claim creep, denominator 漂移和 hindsight tuning.

### 2.2 输入

- 上游对齐计划: `/home/lyj/mnt/project/pocket-failure-repair/docs/plan/20260603-02-third-party-failure-audit-alignment-plan.md`.
- failure taxonomy 调研报告与现有 smoke/sanity 记录, 仅作为工具链和 schema 设计参考.
- 本次复核意见, `source_id=review_feedback_20260602_conversation`. 其中“六个角度审查结论”在本文中定义为: scope/claim boundary, method/resource feasibility, data/provenance/leakage, instrumentation/output lineage, diagnosis/statistics, repair/artifact/paper claim. 若后续把这些审查结论作为持久 evidence 使用, 必须在计划落盘时把来源, 日期, 审查项和修订响应追加到 `/home/lyj/mnt/project/pocket-failure-repair/docs/EXPERIMENT_LOG.md`, 或另存到符合命名规范的 `docs/report/` 审查报告, 并在本文档或日志中引用该路径.

### 2.3 输出

- 本详细执行计划, 持久化到目标文件后才算完成.
- `scope_and_claim_boundary` 记录项, 后续写入方法 feasibility table 和 run metadata.
- 术语表: `original_protocol_reproduction`, `instrumented_reproduction`, `audit_protocol_run`, `adapted_baseline`, `stage_limited_audit`, `selected_output_residual_audit`, `excluded`.
- 停止规则: paper/code assessment, environment assessment, output capture assessment 的时间/尝试上限.
- Resource budget config 和超阈值 blocking policy.
- Documentation update trigger: 何时追加 EXPERIMENT_LOG 和同步 STATUS.

### 2.4 执行步骤

1. 固定本计划的 non-goals, 特别是不运行实验, 不下载数据, 不 clone 仓库.
2. 固定 BIBM claim ladder, 并要求每个 claim 绑定 evidence object.
3. 固定 run boundary labels:
   - `original_protocol_reproduction`.
   - `instrumented_reproduction`.
   - `audit_protocol_run`.
   - `adapted_baseline`.
   - `stage_limited_audit`.
   - `selected_output_residual_audit`.
   - `excluded`.
4. 固定方法 final status:
   - `ready_for_original_repro`.
   - `ready_for_instrumented_audit`.
   - `raw_prevalence_main_audit_candidate`.
   - `stage_limited_audit_candidate`.
   - `audit_protocol_only`.
   - `selected_output_only`.
   - `blocked_pending_resource`.
   - `blocked_pending_user_decision`.
   - `related_work_only`.
   - `excluded_with_reason`.
5. 固定全局 stop rule. 单个方法超过预设时间或尝试次数后, 必须降级或跳过, 并保留 evidence.
6. 固定 `failed samples` 的流转语义: `failed` 不是默认 stage, 而是由 `sample_role` 和 `original_status.status` 保留的上游状态. 详见 §6.4.
7. 固定第一阶段真实 output audit 的依赖: 真实 output audit, labeling, near-miss 判定和统计只能在 Phase 5 analysis-frozen gate 之后执行.

### 2.5 Go/no-go criteria

Go 条件:

- 已明确本文只制定执行方案, 当前不下载, 不 clone, 不运行.
- 已固定 run type, method final status, claim ladder, forbidden wording, resource budget threshold 和 persistence gate.
- 已明确原始 failed samples 如何保留在 sample lineage 中.
- 后续每个结果表都被要求标注 denominator, protocol version, method category, raw outputs 是否被捕获.

No-go 条件:

- 仍允许把 audit protocol 结果写成原论文官方性能.
- 仍允许 final-only outputs 进入 raw failure distribution 主结论.
- 仍没有 stop rule 或 resource threshold, 导致单个方法可以无限阻塞或 agent 擅自判断资源.
- 仍没有将 `failed`, `rejected`, `final residual failure` 的语义区分清楚.

### 2.6 阻塞/失败处理

如果本阶段无法固定 scope 或术语, 不进入候选方法筛选. 必须先回到上游计划补充原则, 或请求用户确认是否接受更窄 claim. 若用户要求使用非官方资源, 超阈值下载, 受限数据或未知 license 资源作为主证据, 标记为 `blocked_pending_user_decision`.

## 3. Phase 1: 候选方法筛选与 feasibility table

### 3.1 目标

从候选第三方方法长名单中筛选可运行, 可追溯, 可审计且任务相关的方法. 第一轮建议先收集长名单, 用硬性排除条件过滤, 再按 feasibility table 打分, 最后选 5-8 个候选进入 paper/code-level assessment, 选 2-3 个进入第一轮最小 audit trial 设计.

候选筛选优先看是否能审计自然流程中的样本流转, 而不是只看论文指标高低. 硬性优先级为: 任务相关性和输出可审计性 > `N_budget` 到 raw attempt metadata 的可追踪性 > 代码/checkpoint/数据可用性 > 插桩是否不改算法 > 协议忠实度 > 计算成本 > 论文知名度.

### 3.2 输入

- 第三方方法论文, README, repository 页面, release, checkpoint 页面, dataset/split/preprocessing 说明, issue, supplementary material.
- 前序文献矩阵和 method design 文档.
- 本文定义的 inclusion/exclusion criteria, resource budget config 和 feasibility table schema.

### 3.3 输出

- `candidate_methods_longlist`.
- `hard_exclusion_log`.
- `method_feasibility_table`.
- `method_artifact_card` 草案.
- 5-8 个 paper/code-level assessment 候选.
- 2-3 个 first-round minimal audit trial 候选.
- 每个方法的 `decision_tier`, `final_status`, `run_boundary_label`.

### 3.4 Inclusion criteria

候选方法应满足至少一项任务相关性条件:

- pocket-conditioned molecule generation.
- linker design 或 local molecular edit.
- SBDD generation.
- docking/pose-conditioned generation.
- 可产生 pocket-bound molecular outputs 的 fragment growing, scaffold hopping, guided generation 或 conditional optimization.

优先纳入满足以下条件的方法:

- 官方或可信开源代码可用.
- 有 pretrained checkpoint, 或训练成本可接受且训练协议清楚.
- 有 inference script 或明确推理入口.
- 数据集, split, preprocessing, receptor/ligand preparation 可追溯.
- 能保存 `N_budget`, raw generation attempts, parsed molecules, rejected samples, selected candidates, final outputs, 或至少能明确哪些阶段不可捕获.
- 能显式保留 upstream/original failed samples 的样本身份与原始失败原因.
- 插桩只需要 wrapper/logging/output capture, 不改变算法逻辑.
- 输出预期为基本合理的 pocket-bound molecular outputs.
- license 无明显研究使用或 artifact 记录障碍.

### 3.5 Exclusion criteria

满足任一条件时, 应排除或降级:

- 源码不可得且无可核验 outputs.
- license 不清楚或禁止必要使用.
- 必须大改模型 forward, decoding, filtering, reranking 或 docking 才能运行.
- checkpoint 不可得, 且训练成本不可接受或训练协议不清楚.
- 数据或输入格式与 audit 任务明显不匹配.
- 输出主要是 pipeline/engineering failure, 无法代表方法自然失败分布.
- 只能产生不可评价或明显异常分子.
- 无法记录 denominator, run provenance, sample lineage 或 leakage status.
- 需要申请受限数据, 使用非官方镜像, 超阈值下载, 联系作者, 但尚未获得用户决策.

### 3.6 Feasibility table schema

每个方法一行. 判断值可用 0/1/2 或 low/medium/high 打分, 但 final decision 必须是离散状态. 每个证据字段必须追溯到论文, README, repo, release, checkpoint 页面, 数据说明, issue 或本地后续评估记录, 不允许只写主观判断.

| 字段 | 要求 |
|---|---|
| `method_name` | 方法名 |
| `paper_year` | 论文年份 |
| `task_type` | pocket generation, linker, local edit, docking/pose-conditioned 等 |
| `relevance_level` | high/medium/low, 附证据 |
| `repo_url` | 官方或可信 repo URL |
| `code_license` | license 类型和证据链接 |
| `code_status` | available, archived, broken_link, unavailable 等 |
| `inference_script_status` | clear, partial, missing, unknown |
| `checkpoint_status` | available, missing, gated, unknown, train_needed |
| `training_cost_if_no_checkpoint` | low/medium/high/unacceptable, 附估计和 resource config |
| `dataset_status` | original_available, gated, missing, unknown, audit_dataset_possible |
| `split_preprocessing_status` | complete, partial, missing, unclear |
| `expected_output_stages` | raw, parsed, normalized, filtered, rejected, docked, selected, final 中可预期阶段 |
| `N_budget_traceable` | yes/no/unknown. 是否能追踪配置生成预算 |
| `raw_attempt_metadata_traceable` | yes/no/needs_patch/unknown. 是否能为 raw attempt 生成 metadata, 即使没有合法 SDF |
| `raw_capture_possible` | yes/no/needs_patch/unknown |
| `rejected_capture_possible` | yes/no/needs_patch/unknown |
| `selected_final_capture_possible` | yes/no/unknown |
| `original_failed_sample_capture` | yes/no/needs_mapping/unknown. 是否能保留 upstream failed samples 的身份, 阶段, 原始原因 |
| `sample_role_status_model` | 是否能填充 `sample_role` 和 `original_status` |
| `instrumentation_needed` | none, wrapper, logging_patch, fork_patch, algorithm_change_required |
| `algorithm_change_required` | true/false/unknown, true 时不能称 instrumented reproduction |
| `original_protocol_repro_feasibility` | ready, feasible_with_minor_blocker, blocked, impossible, unknown |
| `audit_protocol_feasibility` | ready, feasible_with_adapter, selected_only, stage_limited, blocked, impossible |
| `raw_prevalence_eligibility` | eligible/stage_limited/selected_only/not_eligible |
| `leakage_risk` | passed, possible_overlap, unknown_risk, high_overlap, not_checked |
| `compute_cost_estimate` | CPU/GPU/时间估计, 附 resource threshold |
| `storage_download_size` | 预计下载和存储规模, 若未知写 unknown |
| `resource_budget_status` | within_budget, exceeds_budget, unknown_requires_decision |
| `environment_risk` | low/medium/high, 例如 CUDA/old dependency 风险 |
| `output_quality_risk` | low/medium/high, 是否可能主要工程崩溃或异常分子 |
| `blocking_resources` | checkpoint, dataset, split, preprocessing, license, environment 等 |
| `required_user_decision` | none 或受限数据/非官方镜像/超阈值下载/联系作者/核心替换等 |
| `decision_tier` | tier, 见 §3.7 |
| `final_status` | `ready_for_original_repro` 等离散状态 |
| `run_boundary_label` | `original_protocol_reproduction` 等标签 |
| `evidence_links` | 可核验证据列表 |
| `notes` | 简短备注, 不替代 evidence |

### 3.7 Method tiering

| Tier | 进入条件 | 允许主张 | 禁止宣称内容 |
|---|---|---|---|
| raw-prevalence main audit candidate | 任务高度相关, 官方或可信代码可用, checkpoint 或可接受训练路径存在, 数据/split/preprocessing 可追溯, `N_budget` 与 raw attempt metadata 可追踪, 至少 raw/selected/final 关键阶段可捕获或 raw missing 有 metadata 行, 插桩不改算法, 资源在阈值内, 输出质量合理 | 可进入 raw failure distribution 和 stage-wise attrition 主审计 | 不外推到全部领域 |
| instrumented audit candidate | 方法可运行且输出合理, 需要 wrapper/logging/patch 捕获中间样本, patch 不影响 sampling/filtering/reranking/docking/evaluation/budget, 且 raw lineage 可追踪时可升入 raw-prevalence main audit | 可称 instrumented reproduction 或 instrumented audit | 不能把 algorithm-changing patch 称 instrumented reproduction |
| stage-limited audit candidate | 能捕获 rejected/selected/final 或部分中间阶段, 但缺 `N_budget` 到 raw attempt metadata 的可追踪记录 | 只能报告被捕获阶段的 attrition 或 residual failure | 不能报告 raw failure distribution 或 N_budget-level failure burden |
| selected-output audit only | 只能获得 final/top-k/selected molecules, raw/rejected 捕获需要大改算法 | 只能报告 selected/final residual failure | 不能报告 raw failure distribution 或 stage-wise attrition 主结论 |
| stress-test / negative case | 质量一般但能暴露特定失败模式, 或工程风险较高 | 可作为 negative case 或 robustness note | 不并入 clean main audit 的代表性 failure distribution |
| audit-protocol-only adapted baseline | 原数据/split/preprocessing 不可得, 但代码/checkpoint 可在统一 audit dataset 上运行 | 可称 method under our audit protocol 或 adapted baseline | 不能称 original-protocol reproduction 或官方性能 |
| related work only | 任务相关但不可运行, 不可审计或资源不可得 | 只能作为背景或 blocked/excluded table | 不能作为实验方法或 prevalence 证据 |
| excluded_with_reason | license, resource, algorithm change, output quality 或 provenance 无法满足最低要求 | 只进入 excluded/blocked methods table | 不进入结果主表 |

### 3.8 Go/no-go criteria

Go to raw-prevalence main audit:

- 方法任务高度相关.
- 官方或可信代码可用.
- checkpoint 可用, 或训练路径清楚且成本在 resource budget 内.
- 数据/split/preprocessing 可追溯, 或统一 audit protocol 合理.
- 推理入口明确.
- `N_budget` 可追踪.
- raw attempt metadata 可捕获, 即使 raw molecule file 缺失也有 metadata 行.
- 至少 raw/selected/final 关键阶段可捕获, rejected 捕获可进一步增强 stage-wise attrition.
- 插桩不改变算法逻辑.
- compute/storage/license 风险在阈值内.
- 输出质量预期基本合理.

Go to stage-limited audit:

- 缺 raw/N_budget lineage, 但能捕获 rejected/selected/final 或其他中间阶段.
- 只用于该阶段分母下的 attrition/residual failure, 不能进入 raw-prevalence 主结论.

Go to selected-output audit only:

- 只能获得 final/top-k/selected outputs, 或 raw/rejected 捕获需要改算法.
- 只用于 residual failure audit, 不能用于 raw failure distribution.

Go to audit-protocol-only:

- 原数据, split 或 preprocessing 不可得, 但代码/checkpoint 可用于统一 audit dataset.
- 结果标题必须写 `method under our audit protocol` 或 `adapted baseline`.

No-go / exclude:

- license 不清且影响使用.
- 源码/checkpoint/数据均不可得.
- 必须改核心算法才能运行.
- 输出不可评价且主要来自工程崩溃.
- 资源需求超过预算且无用户批准.
- leakage risk 无法标记且会污染 clean main audit 或 repair-test.

Pending:

- 需要申请受限数据, 使用非官方镜像, 下载超阈值资源, 联系作者, 替换核心数据集, 接受训练数据未知 checkpoint 或做算法级适配时, 标记 `blocked_pending_user_decision`, 不由 agent 擅自决定.

### 3.9 阻塞/失败处理

每个阻塞必须记录以下字段:

```text
method:
resource:
attempted_source:
failure_type:
evidence:
resource_budget_config_version:
resource_estimate:
decision:
fallback:
risk_note:
```

常见 `failure_type` 包括: `repo_unavailable`, `license_unclear`, `checkpoint_missing`, `dataset_gated`, `split_missing`, `preprocessing_missing`, `environment_unresolved`, `output_format_mismatch`, `download_too_large`, `resource_size_unknown`, `training_cost_unacceptable`, `algorithm_change_required`.

阻塞处理规则:

- 官方或可核验 fallback 可尝试, 例如 official release, Zenodo, Figshare, OSF, HuggingFace, supplementary material, README issue.
- 非官方镜像, 受限数据, 需要登录/申请, 超阈值下载, 联系作者或核心资源替换必须暂停并请求用户决策.
- 若原数据不可得但方法可用, 降级为 `audit_protocol_only` 或 `adapted_baseline`, 不得冒充原协议复现.
- 若 checkpoint 不可得, 只有训练成本可接受且原训练协议清楚时才考虑 reproduction, 否则降级或排除.

## 4. Phase 2: 数据资产, dataset view, split 与 leakage SOP

### 4.1 目标

先建立数据台账, 再跑第三方方法. 每个方法进入 audit 前, 必须有 method data card, 能回答原论文数据版本, 原 split 是否可得, checkpoint 训练数据是否可得, 是否可能与目标 audit/test 重叠, 拟使用哪个 dataset view.

### 4.2 输入

- 候选方法 feasibility table.
- 方法论文和 README 中的数据, split, preprocessing, checkpoint training data 描述.
- 后续可能使用的 canonical raw dataset 名称和版本, 但本计划阶段不下载.

### 4.3 输出

- canonical raw dataset manifest template.
- dataset view manifest template.
- split registry template.
- leakage check checklist.
- method data card 中的数据字段.
- `training_data_unknown` 和 `leakage_check_status` 标记规则.

### 4.4 数据资产层级

数据资产采用三层结构:

```text
canonical raw dataset
→ dataset view
→ run/sample metadata
```

Canonical raw dataset 只保存官方原始版本, 建议路径:

```text
/home/lyj/mnt/project/pocket-failure-repair/data/datasets/<dataset_id>/raw/
```

Raw 层不清洗, 不重命名, 不删除样本, 不混入第三方 preprocessing 结果. 所有清洗, 格式转换, pocket 截取, receptor cleaning, 加氢, ligand preparation, 过滤和输入重排都必须输出到 dataset view.

Dataset view 建议路径:

```text
/home/lyj/mnt/project/pocket-failure-repair/data/datasets/<dataset_id>/views/<view_id>/
```

Split registry 建议路径:

```text
/home/lyj/mnt/project/pocket-failure-repair/data/datasets/<dataset_id>/splits/<split_id>.json
```

### 4.5 Canonical raw dataset manifest

每个 raw dataset 必须有 manifest. 受限或未获取数据只记录来源与状态, 不伪造本地路径.

| 字段 | 要求 |
|---|---|
| `dataset_name` | 数据集名称 |
| `dataset_version` | 官方版本或日期 |
| `source_url_or_reference` | 官方 URL, DOI, paper 或 data portal |
| `access_type` | public, gated, application_required, unavailable |
| `license` | license 或使用条款 |
| `citation` | 引用信息 |
| `acquisition_status` | not_requested, pending, acquired, blocked |
| `acquisition_date` | 获取日期, 未获取写 null |
| `raw_root` | 本地 raw path, 未获取写 null |
| `original_split_available` | yes/no/unknown |
| `redistribution_allowed` | yes/no/unclear |
| `file_count` | 文件数, 未获取写 null |
| `total_size` | 总大小, 未获取写 null |
| `checksum_manifest_path` | sha256 manifest 路径, 未获取写 null |
| `notes` | 备注和风险 |

Checksum 规则:

- raw 层记录每个原始文件 sha256 和 manifest sha256.
- processed view 层记录 `view_manifest_sha256`, `preprocessing_config_sha256`, `split_file_sha256`, `included_complexes_sha256`.
- run metadata 必须引用 raw checksum, view checksum 和 split checksum, 禁止只写目录名.

### 4.6 Dataset view manifest

每个第三方方法的 original-protocol preprocessing 和本项目统一 audit preprocessing 都必须是独立 dataset view. 不能仅因论文都写 PDBBind, CrossDocked 或 MOAD 就共享 view.

每个 view 至少记录:

| 字段 | 要求 |
|---|---|
| `view_id` | 稳定 ID |
| `parent_raw_dataset_id` | raw dataset ID |
| `method_name` | 绑定方法, our audit view 可写 `pfr_audit` |
| `protocol_type` | `original_protocol`, `our_audit_protocol`, `adapted` |
| `preprocessing_script` | 脚本路径或外部方法说明 |
| `preprocessing_config` | 配置路径和 hash |
| `receptor_cleaning` | receptor 清洗规则 |
| `ligand_preparation` | ligand 准备规则 |
| `pocket_definition` | pocket 定义来源 |
| `pocket_radius` | 半径或局部定义 |
| `filters` | 过滤规则 |
| `input_format` | 方法输入格式 |
| `split_id` | split registry ID |
| `included_complexes` | included list path 和 hash |
| `excluded_complexes` | excluded list path, reason 和 hash |
| `created_by` | agent/human ID |
| `created_time` | 创建时间 |
| `code_commit` | 处理脚本 commit |
| `checksum` | view manifest hash |

每个 dataset view 必须能回答四个问题: 来自哪个 raw dataset, 用了哪个 preprocessing, 用了哪个 split, 与哪个 method/protocol 绑定. 回答不了则不能作为主 audit 输入.

### 4.7 Split registry

每个 split 必须用稳定 ID 和 checksum 固定. 禁止在 run 脚本中临时随机划分后只记录 seed. 若必须随机划分, 也要先生成显式 split list 并入 registry.

每个 split 目录至少包含显式列表:

```text
train
validation
test
audit_discovery
repair_train
repair_validation
repair_test
```

即使某些集合为空也要写明. 原协议复现使用 third-party original split, 只用于 sanity check 或原协议结果. 统一 failure audit 使用 `our_audit_protocol` split, 用于跨方法比较. 两者结果标题和 run metadata 必须区分.

### 4.8 Leakage check 分层规则

Leakage report 至少输出 `passed`, `possible_overlap`, `unknown_risk`, `failed/high_overlap` 四类状态. `passed` 才能进入 clean main audit. `unknown_risk` 可进入探索性或 risk-annotated 分析, 不得与 clean subset 混成强主张证据.

检查层级:

| 层级 | 最低要求 | 规则 |
|---|---|---|
| PDB ID overlap | audit/test complexes 是否与训练集 PDB ID 相同 | 检查大小写, chain ID, complex alias, 同一 PDB 不同 ligand/chain |
| Complex ID overlap | complex 是否直接重叠 | exact overlap 为 high risk |
| Protein sequence overlap | 基于 receptor/protein sequence | >=90% identity 标记 possible/high protein overlap, >=30% identity 记录 family-level risk, 阈值需版本化 |
| Ligand exact overlap | canonical SMILES 和 InChIKey | exact ligand overlap 标记 high leakage risk |
| InChIKey first block | 结构骨架近似 exact | 记录 exact block overlap |
| Bemis-Murcko scaffold overlap | 固定 RDKit 版本和参数 | 不必自动排除, 但作为 scaffold_overlap_risk 分层报告 |
| Pocket/protein-family overlap | pocket cluster 或 protein family | 用于 repair-test 隔离和 sensitivity analysis |

若 checkpoint 只有权重, 没有训练列表或训练数据不可核验, 必须写:

```text
training_data_status=training_data_unknown
leakage_check_status=unknown_risk
```

这种方法不能进入 clean no-leakage 主结论, 除非后续补齐训练数据证据.

### 4.9 Audit/repair set 隔离

从第三方 audit outputs 构造 repair benchmark 前, 必须先固定:

```text
audit-discovery set
repair-train set
repair-validation set
repair-test set
```

Audit-discovery 只用于确定失败分布, near-miss 定义和任务重点. Repair-validation 用于阈值, prompt/rule, reranking 或 model checkpoint 选择. Repair-test 只做最终一次报告, 不得用于阈值选择, prompt/rule 设计, baseline 调参或模型选择.

最终 repair-test 至少在 method, complex/pocket, protein sequence cluster 或 scaffold 层面与开发数据隔离. 如果无法隔离, 不得进入 final repair-test claim.

### 4.10 Run metadata 强制数据字段

每个第三方 run 必须记录:

```json
{
  "method": "...",
  "repo_commit": "...",
  "checkpoint_id": "...",
  "checkpoint_source": "...",
  "training_data_status": "known|partial|training_data_unknown",
  "dataset_name": "...",
  "dataset_version": "...",
  "raw_dataset_id": "...",
  "dataset_view_id": "...",
  "split_id": "...",
  "preprocessing_id": "...",
  "raw_checksum": "...",
  "view_checksum": "...",
  "split_checksum": "...",
  "leakage_check_status": "passed|possible_overlap|unknown_risk|failed",
  "leakage_report_path": "...",
  "complex_id": "...",
  "pdb_id": "...",
  "sample_id": "...",
  "resource_budget_config_version": "...",
  "resource_budget_config_hash": "..."
}
```

### 4.11 Go/no-go criteria

Go for original-protocol reproduction:

- 官方数据版本, 原 split 或作者声明 split, checkpoint 训练来源, preprocessing 规则均可追溯.
- raw/view/split checksum 已记录.
- PDB/protein/ligand/scaffold overlap 风险已评估.

Go for clean main audit:

- 方法可运行且输出可审计.
- 使用统一 audit dataset view.
- audit complexes 不在已知训练集.
- PDB exact overlap 为 0.
- protein high-identity overlap 无高风险或已按规则排除.
- ligand exact overlap 无高风险.
- repair-test 与开发数据隔离.

Go only for exploratory/adapted audit:

- 原数据不可得但方法可运行.
- checkpoint 训练数据部分未知.
- 存在 scaffold/family-level possible_overlap.

No-go for clean claims:

- checkpoint 训练数据未知且无法排除 audit/test overlap.
- 训练列表缺失且方法很可能在同一数据集全集训练.
- audit/test PDB/complex 出现在 train set.
- run metadata 缺 dataset_view_id, split_id 或 checksum.

### 4.12 阻塞/失败处理

需要申请受限数据, license 不清楚, 需要非官方镜像, 需要替换核心数据集, 或需要使用训练数据未知但可能高重叠的 checkpoint 作为主证据时, 暂停并标记 `blocked_pending_user_decision`.

若无法取得训练侧 sequence, 标记 `missing_training_sequence` 并升级为 `unknown_risk`. 若 RDKit 解析 ligand/scaffold 失败, 记录 RDKit version, failure count 和失败样本, 不静默排除.

## 5. Phase 3: 第三方代码, fork, patch, 插桩与资源阻塞评估

### 5.1 目标

在不改变算法逻辑的前提下, 判断每个候选方法能否保存失败样本和中间样本. 如果需要代码改动, 明确 fork/patch 边界, 记录 `algorithm_changed`, 并决定是否仍可称 instrumented reproduction.

### 5.2 输入

- Phase 1 的候选方法和 feasibility row.
- repo URL, license, README, inference script, config, checkpoint 说明.
- Phase 2 的 dataset view/split/leakage 计划.
- Phase 0 的 resource budget config.

### 5.3 输出

- method artifact card.
- resource blocker log.
- fork/branch/patch 计划.
- instrumentation plan.
- output stage capture matrix.
- method-level final status.

### 5.4 第三方代码管理原则

推荐后续执行使用以下轻量资产结构, 但本计划阶段不 clone:

```text
/home/lyj/mnt/project/pocket-failure-repair/third_party/<method>/
/home/lyj/mnt/project/pocket-failure-repair/third_party_patches/<method>_capture_outputs.patch
/home/lyj/mnt/project/pocket-failure-repair/scripts/third_party/run_<method>_instrumented.py
/home/lyj/mnt/project/pocket-failure-repair/configs/third_party/<method>_original_protocol.yaml
/home/lyj/mnt/project/pocket-failure-repair/configs/third_party/<method>_audit_protocol.yaml
/home/lyj/mnt/project/pocket-failure-repair/experiments/<experiment_id>/
/home/lyj/mnt/project/pocket-failure-repair/outputs/<experiment_id>/<method>/<run_id>/
```

其中先定义 `experiment_name = xxx`, 再定义 `experiment_id = YYYYMMDD-<num>-<experiment_name>`. `experiment_id` 用于管理一次实验的脚本、命令、配置、metadata 和对应输出。`run_id` 是 `experiment_id` 下的子运行编号, 可用于区分 method、case、seed 或重复运行。若该实验有 plan/report 文档, 文档文件名中的 `xxx` 优先使用同一个 `experiment_name`。
Fork branch 建议:

| 分支 | 含义 |
|---|---|
| `pfr-original-repro` | 尽量不改, 用于原协议复现 |
| `pfr-audit-logging` | 只加 logging/output capture, 不改变算法逻辑 |
| `pfr-audit-protocol` | 适配本项目 audit dataset, 但尽量不改算法 |
| `pfr-adapted-baseline` | 必须改输入, 任务或流程时, 明确降级为 adapted baseline |

### 5.5 插桩边界

允许的插桩:

- 保存 raw generated molecules.
- 保存 raw attempt metadata, 包括没有合法分子文件的 attempt.
- 保存 filter 前后 candidates.
- 保存 rejected samples 和 rejected reasons.
- 保存 upstream/original failed samples 的 `sample_role` 和 `original_status`.
- 保存 RDKit invalid / sanitization failure.
- 保存 docking input/output.
- 保存 reranking 前候选.
- 保存 intermediate poses.
- 保存 stdout/stderr, error logs 和 tool failures.

禁止在 instrumented reproduction 中改动:

- sampling strategy.
- model forward.
- decoding rule.
- filtering threshold.
- reranking score.
- docking config.
- success definition.
- candidate budget.

只加 logging/output capture 且不改 sampling/filtering/reranking/evaluation 的, 可称 `instrumented_reproduction`. 换数据, 换分母, 换 evaluation gate 或改输入适配时, 只能称 `audit_protocol_run` 或 `adapted_baseline`.

### 5.6 Output stage capture matrix

每个方法必须先判断可捕获哪些 stage:

```text
raw generation attempts
parsed molecules
RDKit valid
normalized samples
filtered/rejected
docked/evaluable
selected
final
```

还必须判断是否能保留以下状态对象:

```text
original failed samples
original rejected samples
original selected samples
original final outputs
pipeline/tool/missing-data failures
```

只能捕获 final 的方法, 必须降级为 `selected-output audit only`. 能捕获 selected/rejected/final 但不能追踪 raw/N_budget 的方法, 降级为 `stage_limited_audit_candidate`. 能捕获 raw 但不能捕获 rejected 的方法, 可保留为 instrumented candidate, 但 rejected stage denominator 必须标记缺失.

### 5.7 Go/no-go criteria

Go for instrumented audit trial:

- 方法可运行预期明确.
- 输出质量可能合理.
- 需要 wrapper/logging/patch 捕获中间样本.
- patch 不影响 sampling, filtering, reranking, docking, evaluation 或 budget.
- 可记录 upstream commit, fork commit, patch list 和 `algorithm_changed=false`.
- 可追踪 `N_budget` 和 raw attempt metadata 时, 才能进入 raw-prevalence main audit.

No-go:

- 必须改模型 forward, decoding, filtering, reranking 或 docking config 才能获得输出.
- 输出格式不稳定且无法记录 lineage.
- 资源或 license 不允许必要使用.
- 无法区分 pipeline failure 和 molecular failure.

### 5.8 阻塞/失败处理

对源码, checkpoint, 数据, split, preprocessing, license, environment, 下载规模, 输出格式不一致分别记录:

```text
failure_type:
evidence:
attempted_source:
resource_budget_config_version:
fallback:
decision:
risk_note:
```

涉及非官方镜像, 超阈值下载, 作者联系, 受限资源, 训练未知 checkpoint, 核心资源替换或算法级适配时, 标记 `blocked_pending_user_decision`.

## 6. Phase 4: 第一轮最小 audit trial 设计

### 6.1 目标

为 2-3 个最相关, 最稳定, 最容易捕获 outputs 的方法设计最小 audit trial. 本阶段只制定 trial design 和 metadata schema, 不运行实验. 第一轮 MVP 设计应覆盖真实 output audit 执行所需的最小 raw/selected/final 捕获计划, stage-wise denominator 计划, original failed samples 保留策略, run boundary label 和降级决策.

Phase 4 可以先于 Phase 5 完成 trial design, 但不得在 Phase 5 analysis-frozen gate 之前执行真实 output audit, labeling, near-miss 判定或统计汇总.

### 6.2 输入

- 5-8 个候选的 feasibility table.
- Phase 2 数据/view/split/leakage SOP.
- Phase 3 output capture matrix 和 instrumentation plan.
- Phase 5 的 diagnosis/statistics draft schema, 仅用于 trial design. 真实执行必须等待 Phase 5 frozen schema/config/tool_versions/denominator/hash.

### 6.3 输出

- first-round trial method list, 建议 2-3 个方法.
- 每个方法的 `run_boundary_label`.
- 最小 output capture plan.
- `run_metadata.json` schema.
- `samples.jsonl` 或 equivalent metadata schema.
- stage-wise denominator plan.
- original failed samples status mapping.
- 降级或跳过决策.

### 6.4 失败样本, stage/status 和 metadata schema

推荐后续运行输出结构:

```text
/home/lyj/mnt/project/pocket-failure-repair/outputs/<experiment_id>/<method>/<run_id>/
  captured_outputs/
  processed/
    normalized_samples/
  labels/
  summaries/
  logs/
  run_metadata.json
```

对应实验脚本、命令、配置快照和 metadata 应保存在:

```text
/home/lyj/mnt/project/pocket-failure-repair/experiments/<experiment_id>/
```

Captured method outputs 尽量不可变. 若需要清洗, 标准化, 加氢或格式转换, 必须另存到 `processed/normalized_samples/`, 并在 metadata 中回指 source sample_id 和 source sha256.

样本唯一键建议:

```text
<method>_<dataset_view_id>_<complex_id>_<stage>_<sample_index>
```

必须采用以下语义区分:

| 字段 | 语义 | 示例 | 注意 |
|---|---|---|---|
| `stage` | 样本在流程中的捕获阶段 | `raw`, `parsed`, `normalized`, `filtered`, `rejected`, `docked`, `selected`, `final` | `failed` 不作为默认 stage |
| `sample_role` | 样本作为审计对象的角色 | `generation_attempt`, `original_failed_sample`, `rejected_candidate`, `selected_candidate`, `final_output`, `control_sanity_sample` | 用于显式保留 upstream failed samples |
| `original_status.status` | 第三方方法或上游流程给出的原始状态 | `failed`, `rejected`, `selected`, `final`, `passed`, `unknown` | `failed` 与 `rejected` 不混用 |
| `audit_labels.primary_label` | 本项目统一 diagnosis 的主标签 | `protein_ligand_clash` 等 | 不由第三方原始状态直接决定 |

解释:

- Upstream/original failed samples 必须保留为一等审计对象, 使用 `sample_role=original_failed_sample` 且 `original_status.status=failed`.
- `rejected` 表示第三方流程的 filter/rerank 分支状态, 是 stage 或 original status, 不自动等价于 molecular failure.
- `final` 表示最终输出阶段, final sample 仍可能被本项目诊断为 residual failure, 但不能由此推断 raw failure distribution.
- `failed` 不作为默认 stage, 避免与 rejected/final residual 混淆. 如果某第三方日志确实以 `failed` 命名某阶段, 应映射到最近的流程 stage, 并把原文保存在 `original_status.source_stage_name`.

每条样本 metadata 至少包含:

```json
{
  "sample_id": "...",
  "parent_sample_id": "...",
  "lineage_id": "...",
  "run_id": "...",
  "method": "...",
  "method_repo": "...",
  "method_commit": "...",
  "run_boundary_label": "instrumented_reproduction|audit_protocol_run|...",
  "dataset_name": "...",
  "dataset_version": "...",
  "dataset_view_id": "...",
  "split_id": "...",
  "complex_id": "...",
  "pdb_id": "...",
  "pocket_id": "...",
  "stage": "raw|parsed|normalized|filtered|rejected|docked|selected|final",
  "sample_role": "generation_attempt|original_failed_sample|rejected_candidate|selected_candidate|final_output|control_sanity_sample",
  "sample_index": 0,
  "molecule_path": "...",
  "pose_path": "...",
  "receptor_path": "...",
  "raw_sample_id": "...",
  "raw_sha256": "...",
  "normalized_sha256": "...",
  "original_status": {
    "status": "failed|rejected|selected|final|passed|unknown",
    "source_stage_name": "...",
    "failure_reason": "...",
    "rejection_reason": "...",
    "rank": null,
    "score": null,
    "source_file": "..."
  },
  "audit_labels": {},
  "quality_flags": {},
  "created_by_script_commit": "..."
}
```

Raw attempt 没有合法 SDF 时也应有 metadata 行, `molecule_path` 可为空, 但 missing data 或 format error 必须可追踪.

### 6.5 Original protocol vs audit protocol 边界

| Run type | 定义 | 可允许主张 |
|---|---|---|
| `original_protocol_reproduction` | 原数据版本, split, preprocessing, checkpoint, sampling, filtering, reranking, evaluation 均忠实 | 可作为原协议 sanity/reproduction claim, 仍需标注差异 |
| `instrumented_reproduction` | 仅增加 logging/output capture, 不改变算法逻辑 | 可称 instrumented reproduction |
| `audit_protocol_run` | 方法在本项目统一 dataset view, split, diagnosis protocol 下运行 | 可称 method under our audit protocol |
| `adapted_baseline` | 为适配输入, 任务或流程做了算法或协议变化 | 只能称 adapted baseline |
| `stage_limited_audit` | 只能捕获部分阶段, 缺 raw/N_budget lineage | 只能报告被捕获阶段的 attrition/residual failure |
| `selected_output_residual_audit` | 只能获得 selected/final/top-k outputs | 只能报告 residual failure, 不报告 raw distribution |
| `excluded` | 不满足最低可审计性 | 只进入 excluded/blocked methods table |

### 6.6 第一阶段 MVP 真实 output audit 执行边界

本文档不运行实验. 但后续如果进入第一阶段 MVP 执行, 最低要求是:

1. 选择 2-3 个代表性方法, 优先覆盖至少一个 raw-prevalence eligible 方法和一个可能 stage-limited/selected-only 方法.
2. 每个方法在冻结协议下运行小规模真实 output audit.
3. 对 raw-prevalence eligible 方法, 最少捕获 `N_budget`, raw attempt metadata, selected outputs, final outputs.
4. 对 stage-limited 方法, 明确记录缺失的 raw/N_budget lineage, 并只报告 stage-limited 结果.
5. 保留 original failed samples 的 `sample_role` 和 `original_status`.
6. 生成 `run_metadata.json`, `samples.jsonl`, `stage_attrition.json`, `labels.jsonl`, `label_summary.json`.
7. 回答真实 outputs 中是否存在非偶然 near-miss. “非偶然”在 MVP 中至少要求 near-miss 候选不是单个工具失败或单个孤立误标, 并通过固定 label_config 与人工 QC. 小样本仍只能称为 scoped MVP evidence, 不能外推为 field-wide prevalence.

### 6.7 Go/no-go criteria

Go:

- 每个 trial 方法至少能明确 `N_budget`, `N_raw_captured` 或其不可捕获原因, `N_final`, `run_id`, `seed`, `complex_id`, `dataset_view_id`.
- 能区分 molecular failure 与 pipeline/tool/missing_data failure.
- 能记录 raw/normalized 分离和 sample lineage.
- 能保留 `original_failed_sample` 的 status mapping.
- final-only 方法已单列为 selected-output residual audit.

No-go:

- 只能拿到 final selected outputs 却试图声明 raw failure distribution.
- 缺 run boundary label.
- 缺 dataset_view_id/split_id/checksum.
- 不可评价样本会被静默删除.
- 在 Phase 5 analysis-frozen gate 前执行真实 output labeling 或 near-miss 统计.

### 6.8 阻塞/失败处理

如果方法无法捕获 raw 或 rejected, 不强行改算法. 先判断是否降级为 `stage_limited_audit`, `selected_output_only` 或 `audit_protocol_only`. 如果最小 trial 设计仍无法保证 sample_id, stage, denominator 和 original_status/audit_labels 可追踪, 暂停该方法并转入下一个候选.

## 7. Phase 5: Diagnosis protocol, label schema 与统计口径冻结

### 7.1 目标

把 diagnosis protocol 从原则转为可执行规范. 第一轮真实 audit 前必须冻结 label schema, label config, tool versions, thresholds, precedence hierarchy, stage-wise JSONL schema, denominator definitions 和 label_config_hash 生成方式. 没有固定 schema/hash 的标签结果只能作为 pilot/sanity, 不能进入主 audit.

### 7.2 输入

- failure taxonomy 调研.
- Phase 4 sample metadata schema.
- 可用工具列表和后续 evaluator 候选, 如 RDKit, PoseBusters, PLIP/ProLIF, Arpeggio/MolProbity, Vina/GNINA, OpenBabel.
- 统计需求, 包括 stage-wise denominator, primary/secondary labels, not_evaluable, bootstrap 和 co-occurrence.
- 现有 smoke, smoke-plus, controlled perturbation, contact-degraded 数据, 仅可作为 diagnosis sanity set 候选, 不得作为正式 prevalence 证据.

### 7.3 输出

每个 run 至少应产出以下 artifacts, 所有路径和 checksum 必须进入 `run_metadata.json`:

```text
label_schema.json
label_config.yaml
tool_versions.lock
labels.jsonl
stage_attrition.json
label_summary.json
manual_adjudication.jsonl
```

### 7.4 Label schema

每条样本同时包含 `original_status` 和 `audit_labels`. `original_status` 解释样本在第三方流程内的状态. `audit_labels` 用于跨方法统一诊断.

`audit_labels` 至少包含:

```json
{
  "sample_id": "...",
  "run_id": "...",
  "method": "...",
  "complex_id": "...",
  "stage": "...",
  "sample_role": "...",
  "evaluability_status": "...",
  "primary_label": "...",
  "secondary_labels": [],
  "near_miss_eligible": false,
  "evidence": {},
  "tool_results": {},
  "thresholds": {},
  "label_protocol_version": "...",
  "label_script_commit": "...",
  "label_config_hash": "...",
  "adjudication_status": "not_reviewed|reviewed|overridden"
}
```

### 7.5 Primary labels

`primary_label` 必须单值, 只允许从固定枚举中选择. `not_evaluable` 不属于 primary_label 枚举, 由 `evaluability_status` 独立控制.

```text
missing_data
pipeline_failure
tool_failure
chemical_invalid
graph_or_scaffold_failure
anchor_failure
global_pose_failure
pocket_detachment
local_geometry_failure
protein_ligand_clash
interaction_or_contact_loss
property_filter_failure
selected_output_residual_failure
unknown
```

禁止临时新增同义标签. 新标签只能通过 `label_schema` 版本升级加入.

### 7.6 Evaluability and primary_label mapping

`evaluability_status` 独立于 `primary_label`, 枚举为:

```text
evaluable
not_evaluable_missing_data
not_evaluable_pipeline_failure
not_evaluable_tool_failure
not_evaluable_format_error
not_evaluable_stage_not_applicable
not_evaluable_unknown
```

映射规则:

| `evaluability_status` | `primary_label` 规则 | 统计位置 |
|---|---|---|
| `evaluable` | 使用 precedence hierarchy 得到 molecular 或 residual failure label | 进入对应 denominator 的 primary prevalence |
| `not_evaluable_missing_data` | `missing_data` | 单独进入 evaluability breakdown, 可进入 inclusive failure burden |
| `not_evaluable_pipeline_failure` | `pipeline_failure` | 单独进入 evaluability breakdown, 可进入 inclusive failure burden |
| `not_evaluable_tool_failure` | `tool_failure` | 单独进入 evaluability breakdown, 不得默认为 molecular failure |
| `not_evaluable_format_error` | 若为分子格式/化学解析问题, 可为 `chemical_invalid`; 若为输入缺失或工具崩溃, 使用 `missing_data` 或 `tool_failure` | 必须记录 reason |
| `not_evaluable_stage_not_applicable` | `unknown` 或按 schema 允许的 null-like value, 但不得作为 molecular failure 解释 | 只进入 evaluability/stage applicability breakdown |
| `not_evaluable_unknown` | `unknown` | 单独报告, 不得静默删除 |

统计时必须单独报告 not_evaluable, tool_failure, pipeline_failure, missing_data 的比例, 并明确它们是否进入 molecular failure prevalence 分母. 同一样本不得同时在 primary molecular prevalence 和 evaluability breakdown 中重复解释为两个不同 failure 类型.

### 7.7 Secondary labels and evidence

`secondary_labels` 允许多选, 用于保存细粒度工具证据. 示例枚举:

```text
rdkit_parse_failed
rdkit_sanitize_failed
valence_error
disconnected_graph
scaffold_missing
scaffold_changed
anchor_missing
anchor_distance_exceeded
ligand_outside_pocket
centroid_distance_exceeded
posebuster_geometry_failed
internal_clash
protein_ligand_clash
required_interaction_lost
contact_count_drop
docking_failed
vina_score_degraded
qed_filter_failed
sa_filter_failed
```

Secondary labels 不能覆盖 primary_label 的 precedence 决策. 工具输入, 输出, 失败码, command, stderr path, exit code, input checksum 必须进入 `tool_results` 或 evidence.

### 7.8 Precedence hierarchy

Primary label 由固定 precedence 自动选择. 推荐顺序:

```text
missing_data
→ pipeline_failure
→ tool_failure
→ chemical_invalid
→ graph_or_scaffold_failure
→ anchor_failure
→ global_pose_failure 或 pocket_detachment
→ local_geometry_failure
→ protein_ligand_clash
→ interaction_or_contact_loss
→ property_filter_failure
→ selected_output_residual_failure
→ unknown
```

`not_evaluable` 不应被强行并入 molecular failure type, 而应由 `evaluability_status` 控制. 若不可评价的原因就是缺文件或管线崩溃, primary_label 使用 `missing_data`, `pipeline_failure` 或 `tool_failure`.

### 7.9 Diagnosis sanity set 边界

至少需要一个 sanity set 证明标签脚本会保留 missing_data, tool_failure, pipeline_failure, not_evaluable, original failed samples 和 near-miss 候选, 而不是静默丢弃.

允许用于 sanity 的现有数据来源:

- smoke 数据.
- smoke-plus 数据.
- controlled perturbation 数据.
- contact-degraded local-edit 数据.
- 小型人工构造的 invalid/missing/tool-failure cases.

边界规则:

- 这些样本必须标记 `dataset_role=sanity_only` 或 `sample_role=control_sanity_sample`.
- 这些样本只能用于验证 schema, tool wiring, label precedence, not_evaluable handling 和 manual adjudication workflow.
- 这些样本不得进入第三方方法 failure prevalence, near-miss prevalence, repair benchmark sample count, main audit denominator 或 BIBM 主张证据.
- 若 sanity 结果导致阈值调整, 调整后的配置必须生成新的 `label_protocol_version` 和 `label_config_hash`. 调整前结果只作为 pilot/sanity 保留.

### 7.10 Tool versions, official evaluator environment, thresholds 和 label config hash

必须固定并记录 RDKit, PoseBusters, PLIP 或 ProLIF, Arpeggio 或 MolProbity, docking/Vina 或 GNINA, OpenBabel, Python, CUDA, 操作系统版本.

正式涉及 PLIP/Vina 的评估必须使用用户记忆指定的 evaluator 环境:

```text
/home/lyj/mnt/project/pfr-eval-tools
```

要求:

- `tool_versions.lock` 必须记录该环境路径, 激活方式, evaluator 版本, dependency versions, binary paths 和命令模板.
- `run_metadata.json` 必须记录实际 command, working directory, environment name/path, stdout/stderr path, exit code 和 input/output checksum.
- 若正式 PLIP/Vina evaluator 没有在 `/home/lyj/mnt/project/pfr-eval-tools` 或该环境不可用, 相关正式评估标记为 `blocked_pending_evaluator_environment`, 不得用其他环境结果冒充正式 evaluator provenance.
- Vina/docking score 只能作为辅助指标, 不得作为单独 success gate.

阈值必须写入 `label_config.yaml`, 包括:

- pocket proximity threshold.
- anchor RMSD 或距离阈值.
- scaffold match rule.
- clash distance threshold.
- contact/interaction loss 定义.
- PoseBusters pass/fail columns.
- property filters.
- docking score 仅作为辅助指标的规则.

`label_config_hash` 使用规范化后的 `label_config.yaml` 计算 sha256. 每条 `labels.jsonl` 和每个 summary 都记录同一 hash. 任何阈值, 工具列, label precedence 或枚举变化都必须生成新的 `label_config_hash` 和 `label_protocol_version`, 不得混合汇总.

### 7.11 Stage-wise label recording

对 raw, parsed, normalized, filtered, rejected, docked, selected, final 等阶段分别记录 labels. 每个样本需要 `parent_sample_id` 或 `lineage_id`, 追踪 raw attempt 到 selected/final 的流失.

`stage_attrition.json` 应按阶段记录:

```text
n_input
n_output
n_missing_data
n_pipeline_failure
n_tool_failure
n_not_evaluable
n_evaluable
n_molecular_failure
n_original_failed_samples
```

### 7.12 Manual adjudication protocol

人工复核触发条件:

- primary_label 为 `unknown`.
- `evaluability_status` 为 `not_evaluable_unknown`.
- 工具结果冲突.
- near-miss 候选.
- 高影响样本.
- label config 边界值附近.
- 每个方法/阶段的随机 QC 样本.

人工记录必须包含:

```text
adjudicator_id
blinded_fields
original_auto_label
final_label
reason
evidence_paths
decision_time
whether_override_auto_label
```

人工复核只写 `adjudicated_label`, 不覆盖 `auto_label` 原始记录. 若资源不足无法双人复核, 必须记录单人复核限制.

### 7.13 Repairable near-miss tagging in diagnosis

`near_miss_eligible` 是独立布尔字段或 subset label, 不等同于 primary_label. 初始条件由 `label_config` 固定:

- RDKit valid.
- scaffold/anchor preserved.
- ligand near pocket.
- 非 missing, pipeline 或 tool failure.
- 非 severe chemical invalid.
- 非 global pose collapse.
- primary_label 属于 local_geometry_failure, protein_ligand_clash, interaction_or_contact_loss 或 anchor_failure 的可局部修复子类.

Near-miss 规则不反向影响 primary_label 或 prevalence 统计.

### 7.14 Denominator 与统计对象

最小统计单元为 `sample_id`, 并保留:

```text
method
run_id
seed
dataset_view_id
complex_id
pocket_id
stage
sample_index
lineage_id
sample_role
original_status.status
```

所有计数必须回溯到 metadata JSONL, 不能只从 SDF 文件数推断.

#### Stage-wise denominator 定义

| Denominator | 入口条件 | 排除/注意 |
|---|---|---|
| `N_budget` | 配置要求的生成预算 | 方法崩溃导致未生成的差值记为 pipeline missing/crashed |
| `N_raw_attempt_metadata` | 实际捕获到 raw attempt metadata | raw 文件缺失也可有 metadata 行 |
| `N_raw_captured` | 有 raw molecule 或 raw attempt artifact | 不等于 N_budget, 缺失要解释 |
| `N_original_failed_samples` | 上游方法标记为 failed 的样本 | 通过 `sample_role` 和 `original_status.status` 记录, 不是 stage |
| `N_parsed` | 能被读取为分子记录 | parse fail 计入 chemical invalid 或 format error 上游分母 |
| `N_rdkit_valid` | RDKit parse/sanitize 通过 | 不进入 pose/interaction 前仍需保留 invalid 记录 |
| `N_anchor_preserved` | anchor/scaffold rule 通过 | 依赖 label_config |
| `N_docked` | attempted docking 或 pose generation | docking failed 单独计数 |
| `N_pose_available` | 有可用 3D pose | 不是所有 parsed 分子都有 pose |
| `N_evaluable` | 具备对应分子质量诊断所需输入 | tool failure/missing_data 不静默删除 |
| `N_rejected` | 被原方法 filter/rerank 拒绝 | 记录 rejected reason |
| `N_selected` | 被方法选中或进入 top-k | 与 raw 分母分开 |
| `N_final` | 最终输出 | final-only 方法只用此分母 |
| `N_repair_eligible` | 满足 near-miss eligibility | 不等于 audit failure prevalence 分母 |

Raw-prevalence 主审计必须可追踪 `N_budget` 和 `N_raw_attempt_metadata`. 如果只能追踪 `N_rejected`, `N_selected`, `N_final`, 则只能进入 `stage_limited_audit` 或 `selected_output_residual_audit`, 不能支撑 raw failure distribution 或 N_budget-level attrition 主结论.

Stage-wise denominator 必须按单调流转记录, 如 `N_budget >= N_raw_attempt_metadata >= N_parsed >= N_rdkit_valid >= N_anchor_preserved`. `N_rejected`, `N_selected`, `N_final` 可能来自流程分支, 需要 `stage_transition` 和 `parent_sample_id` 避免重复计数.

#### Attrition table 模板

每个 method-run-seed-complex 输出一行或多行:

```text
method, run_id, seed, dataset_view_id, complex_id, pocket_id,
N_budget, N_raw_attempt_metadata, N_raw_captured, N_original_failed_samples,
N_parse_fail, N_parsed, N_rdkit_invalid, N_rdkit_valid,
N_anchor_fail, N_anchor_preserved,
N_docking_attempted, N_docking_failed, N_pose_available,
N_not_evaluable, N_evaluable, N_rejected, N_selected, N_final,
N_repair_eligible
```

#### Failure prevalence 统计层级

至少报告:

- per-method prevalence.
- per-complex prevalence.
- per-pocket prevalence.
- sample-weighted aggregate.
- method-weighted aggregate.
- clean subset and risk-annotated subset.
- evaluability breakdown.
- original failed samples breakdown.

Inclusive prevalence 用于审计流程总失败负担, 例如 `count(label)/N_raw_attempt_metadata` 或 `count(label)/N_budget`. Evaluable-only prevalence 用于分子质量诊断, 例如 `count(label)/N_evaluable` 或 `count(label)/N_tool_evaluable`. 每张表标题必须标注分母.

跨方法聚合必须同时报告 sample-weighted 和 method-weighted. Sample-weighted 反映全部观测样本, 但可能被高产出方法支配. Method-weighted 先计算每个 method 的比例再对 methods 等权平均, 更适合回答代表性方法平均会出现什么失败.

#### Bootstrap interval

关键比例报告 95% bootstrap interval, 包括 primary failure type prevalence, repairable near-miss 占比, not_evaluable/tool_failure/pipeline_failure 比例. 主分析使用 cluster bootstrap, 重采样单位优先为 complex_id 或 pocket_id. 跨方法汇总使用 nested bootstrap, 先重采样 method, 再在 method 内重采样 complex/pocket. 重复次数建议 >=1000. 小样本格子如 n < 20 标记 `small_n`, 不做过度解释.

#### Multi-label co-occurrence matrix

Secondary tags 计算 pairwise 共现矩阵, 输出:

```text
count_ij
P(i and j)
P(j | i)
```

Primary failure type 是 precedence 后的互斥分布, 不混入 secondary tag 共现矩阵.

### 7.15 Draft-ready gate vs analysis-frozen gate

必须区分两个 gate:

| Gate | 用途 | 允许后续行为 | 禁止行为 |
|---|---|---|---|
| draft-ready gate | schema/config/tool plan 可用于 trial design 和 sanity | 设计 Phase 4 trial, 用 sanity set 测试 label script | 运行真实第三方 output audit 并生成正式 prevalence |
| analysis-frozen gate | schema/config/tool_versions/denominator/hash 已冻结 | 运行真实 audit, labeling, near-miss 判定和统计 | 临时改阈值后混合汇总旧结果 |

Analysis-frozen gate 必须满足:

- 已冻结 `label_schema.json`, `label_config.yaml`, precedence hierarchy, tool_versions, label_config_hash 生成方式和 stage-wise JSONL schema.
- 已固定 denominator definitions 和 raw-prevalence eligibility.
- 至少一个 sanity set 能证明标签脚本会保留 missing_data, tool_failure, pipeline_failure, not_evaluable, original failed samples, 而不是静默丢弃.
- run_metadata 能追踪 method commit, dataset view, sample lineage, original_status, audit_labels, label_protocol_version, label_script_commit 和 label_config_hash.
- 主分析表能生成 per-method, per-complex, sample-weighted aggregate, method-weighted aggregate, not_evaluable breakdown, 且每个比例有明确 denominator.

No-go:

- primary_label 依赖人工临时判断, 或没有固定 precedence hierarchy.
- 工具版本, 阈值, PoseBusters columns, interaction 定义或 clash/contact 阈值没有写入配置并计算 hash.
- 不可评价样本被删除.
- 只能拿 final selected outputs 却试图声明 raw failure distribution.
- 人工复核覆盖 auto_label 且不保留 override reason 和 evidence.

### 7.16 阻塞/失败处理

如果工具失败, 记录 `tool_failure`, `tool_name`, command, stderr_path, exit_code, input_checksum. 不得把工具失败默认为 molecular failure. 若第一轮 sanity check 后需要调阈值, 必须新建 `label_protocol_version` 并保留旧版本结果.

## 8. Phase 6: Repairable near-miss benchmark 与 baseline/evaluation 设计

### 8.1 目标

从真实第三方 audit outputs 中筛出 repair-eligible local failure subset, 构造后续 repair benchmark. Near-miss 不是人为扰动集合, 不是所有 failed molecules, 也不是 final-only selected output 的无差别集合.

在真实第三方 audit outputs, frozen labels, denominator table 和 near-miss evidence 存在前, Phase 6 只能作为预注册设计, 不得构造正式 repair benchmark, 不得报告 repair benchmark sample count, 不得提出 repair model 主张.

### 8.2 输入

预注册设计阶段允许的输入:

- 统一 diagnosis protocol draft 或 frozen version.
- near-miss eligibility 规则草案.
- audit-discovery, repair-train, repair-validation, repair-test split policy 草案.
- baseline/evaluation fairness 设计.

正式 benchmark 构造阶段必须额外具备:

- 真实第三方 audit outputs.
- frozen `labels.jsonl`.
- frozen stage-wise labels and attrition.
- `near_miss_eligible` metadata.
- leakage report 和 split isolation evidence.
- denominator/hash/tool_versions 完整 provenance.

### 8.3 输出

预注册阶段输出:

- `near_miss_eligibility_config` 草案或 frozen config.
- inclusion/exclusion reason schema.
- low-prevalence fallback policy.
- repair benchmark split policy.
- baseline taxonomy and budget fairness table.
- evaluation gate.
- repair gain reporting template.

正式构造阶段输出:

- near-miss subset manifest.
- repair benchmark dataset card.
- repair split manifest.
- leakage isolation report.
- baseline configs.
- evaluator provenance.

### 8.4 Near-miss inclusion/exclusion rules

Inclusion:

- RDKit valid.
- 可解析 3D pose.
- scaffold/core/anchor 保留.
- ligand 仍在 pocket 内或与参考 pocket 距离未全局漂移.
- primary failure 属于 local geometry, protein-ligand clash, anchor attachment/local torsion, interaction/contact loss.
- 不属于 pipeline, tool 或 missing-data failure.

Exclusion:

- pipeline/tool/missing-data failure.
- severe chemical invalid.
- scaffold/core 丢失.
- global pose collapse 或 pocket detachment.
- pure property/filter-only failure.
- not_evaluable samples.
- 只靠 Vina/property 变差定义的失败.
- 仅来自 sanity/control 数据的样本.

Near-miss metadata 必须记录:

```text
original method/status/stage
sample_role
primary failure type
secondary tags
eligibility decision
exclusion reason
evaluator evidence
source run_id
dataset_view_id
split_id
method_commit
label_config_hash
```

### 8.5 Low-prevalence fallback

不得因 near-miss 占比低而改 label, denominator 或 eligibility. 预注册 fallback:

- 转为 selected-output residual failure audit.
- 缩小到 local-edit/linker 场景子任务.
- 把 diagnosis benchmark 作为主贡献, repair 作为附录或小规模 case study.
- 报告负结果并暂缓 full repair model claim.
- 只对稳定存在的 failure type 做 narrowed-scope repair benchmark.

建议第一轮 MVP 仅估计可行性. 如果后续正式 audit 中 near-miss 总数或主要 failure type 样本量不足, 不做 full repair model claim. 若某一局部 failure type 有稳定样本量, 可转为 narrowed-scope claim.

### 8.6 Split isolation for repair benchmark

- `audit-discovery`: 只用于确定失败分布与任务定义.
- `repair-train`: 用于训练或规则开发.
- `repair-validation`: 用于调参, 早停, threshold, reranking rule, ablation 选择.
- `repair-test`: 只做最终一次报告.

Repair-test 至少在 method, complex/pocket, protein family 或 scaffold 层与开发数据隔离. 如果用 audit-discovery 决定哪些 failure types 进入 benchmark, repair-test 应来自后续冻结协议下的新 held-out methods/pockets/complexes 或严格隔离子集.

### 8.7 Baseline taxonomy

| Baseline 类别 | 说明 | 是否进入公平主表 |
|---|---|---|
| identity failed candidate | 原失败输入不变 | 作为下限, 需防伪成功 |
| no-feedback repair | 不使用 diagnosis feedback 的修复 | 是 |
| rerank-only | 从已有或重新生成候选中 rerank | 是, budget 必须等同 |
| Best-of-N resampling | 相同输入重新采样 N 个候选 | 是, N 和 evaluator calls 固定 |
| rule-based/local geometry repair | 局部规则或几何修复 | 是 |
| docking/force-field/geometry refinement | 对 pose 或构象优化 | 是, 步数和约束固定 |
| learned repair without feedback | 学习型修复但无显式 feedback | 是 |
| learned repair with feedback | 使用 failure feedback 的本项目或对照方法 | 是 |
| oracle/teacher upper bound | 使用 reference ligand, ground-truth pose, test label 或人工 oracle | 单独标注, 不与 non-oracle 混主表 |

### 8.8 Budget fairness protocol

每个 baseline 必须固定并记录:

```text
input failed candidate
candidate budget
optimization steps
wall-clock/GPU budget
docking calls
feedback calls
reference/oracle access
reranking pool size
evaluator calls
random seed
failure/timeout handling
```

所有 baseline 使用同一输入, 同一 split, 同一 evaluation gate. 若某 baseline 使用 reference ligand, ground-truth pose, oracle interaction 或 test label, 必须标为 oracle/teacher, 与 non-oracle 方法分表.

### 8.9 Evaluation gate

主 success 使用级联 gate, 不只看 Vina score:

```text
parse/RDKit valid
→ scaffold/anchor preserved
→ pocket proximity
→ geometry/PoseBusters/protein-ligand clash pass
→ target failure resolved
→ interaction/contact recovery 或 no-worse-than-failed
→ optional docking/property no-degradation metrics
```

主 success 要求 target failure resolved 且不引入关键新失败, 例如 RDKit invalid, scaffold loss, pocket detachment, severe clash. Vina/docking score 只能作为辅助指标. 涉及正式 PLIP/Vina 的 gate 必须满足 §7.10 的 `/home/lyj/mnt/project/pfr-eval-tools` 环境 provenance 要求.

### 8.10 Repair gain reporting 和 anti-pseudo-success

每个结果必须相对同一个 failed candidate 报告 delta/gain, 而不只报告 repaired molecule 的绝对分数. 至少报告:

- success gain.
- clash reduction.
- geometry pass gain.
- contact recovery gain.
- docking/property no-degradation.
- per-failure-type stratified gain.
- identity baseline normalized net improvement.

Identity/no-feedback/rerank-only 必须通过 non-trivial change 与 target-failure resolution 才能算 repair success. 若原 failed candidate 已通过某些 gate, 不能把保留这些 gate 计作修复收益.

### 8.11 Go/no-go criteria

Go to repair benchmark construction only after real audit evidence:

- main audit 显示 near-miss 在代表性可审计方法中非偶然存在.
- held-out repair-test 能在隔离 split 下形成足够样本.
- evaluator gate 可稳定运行.
- identity/no-feedback baseline 不能自然达到高成功率.
- 所有 near-miss 样本来自 frozen third-party audit outputs, 而不是 sanity/control 数据.

Go with narrowed scope:

- near-miss 总占比不高, 但在特定任务或 failure type, 如 local clash, anchor/torsion, interaction/contact loss, 有稳定样本量.
- benchmark 和论文 claim 限定到该子任务.

No-go for full repair model claim:

- near-miss 占比极低.
- 样本量不足.
- 主要失败来自 pipeline/tool/global collapse/chemical invalid.
- repair-test 无法与 audit-discovery 和 train/validation 隔离.
- 真实第三方 audit evidence 尚不存在.

No-go for fairness table:

- baseline 之间 candidate budget, oracle 信息, feedback 信息, evaluator calls 或输入 failed candidates 不一致且无法校正.

### 8.12 阻塞/失败处理

如果 near-miss 占比低, 不改 denominator 或 label. 按 fallback 降级. 如果某 baseline timeout 或 tool failure, 单独计数并说明是否进入分母. 如果 repair-test 被发现泄漏, 冻结该问题记录并重建隔离 split, 不能继续使用污染结果.

## 9. Phase 7: 结果呈现, negative result, artifact 与 BIBM claim 管理

### 9.1 目标

把所有主张绑定到 evidence object, 预防 claim creep, selected-output bias, denominator 混乱, instrumentation 污染, license/artifact 风险和 negative-result 隐藏.

### 9.2 输入

- Feasibility table.
- Resource blocker log.
- Dataset manifest, view manifest, split registry, leakage report.
- Run metadata, sample metadata, label summary, stage attrition.
- Near-miss eligibility report.
- Repair benchmark split manifest and baseline configs.
- License/artifact registry.

### 9.3 输出

- Audit result presentation template.
- Repair result presentation template.
- Negative results policy.
- Artifact registry.
- Release tiers.
- Reproducibility manifest.
- Paper figure/table map.
- EXPERIMENT_LOG/STATUS update entries.

### 9.4 Audit 结果呈现模板

必须分开呈现:

1. Method feasibility/auditability/license table.
2. Stage-wise attrition table.
3. Failure prevalence table.
4. Not-evaluable breakdown table.
5. Original failed samples status table.
6. Sample-weighted vs method-weighted aggregate table.
7. Multi-label co-occurrence heatmap.
8. Repairable near-miss subset prevalence with denominator and interval.
9. Stage-limited audit, 单独成表.
10. Selected-output residual audit, 单独成表.
11. Excluded/blocked methods table.

每张表必须标注 denominator, protocol version, method category, run boundary label, raw outputs 是否被捕获, clean subset or risk-annotated subset.

### 9.5 Repair 结果呈现模板

必须分开呈现:

1. Repair dataset summary.
2. Split/leakage summary.
3. Baseline comparison under fixed budget.
4. Failure-type stratified results.
5. Feedback ablation.
6. Budget fairness audit.
7. Repair gain relative to failed candidate.
8. Case studies.
9. Negative/boundary cases.

Case study 只能补充解释, 不能替代 gate-based aggregate evaluation. 所有可视化案例应来自预先定义的 test set, 避免只挑最好例子.

### 9.6 Negative results policy

负结果必须进入主文或附录, 包括:

- 方法不可复现.
- 资源受阻.
- license 不允许公开.
- 只能 final-output audit.
- 缺 raw/N_budget lineage, 只能 stage-limited audit.
- near-miss 占比低.
- 某类 failure 不可修.
- repair 导致 validity, geometry 或 interaction 恶化.
- identity/no-feedback baseline 已足够强.
- tool not_evaluable 比例高.
- checkpoint training data unknown 或 leakage risk unknown.

不得通过改 label, 改 denominator, 删除不可评价样本, 只展示最好 seed 或只展示 case study 来隐藏负结果.

### 9.7 License and artifact registry

为每个第三方 repo, checkpoint, dataset, split, protein/ligand file, generated output, patch, wrapper 和 summary 建立 artifact registry. 字段至少包括:

```text
artifact_id
artifact_type
source_url
license
citation
access_restriction
redistribution_permission
checksum
storage_location
public_release_decision
risk_note
```

Git 仓库只保存轻量可复现资产: scripts, wrappers, patches, configs, schemas, manifests, small examples, summary tables, figure scripts. 不提交大 checkpoint, 大数据集, 大规模 raw outputs 或受限第三方文件.

### 9.8 Artifact release tiers

| Tier | 可公开策略 | 示例 |
|---|---|---|
| Tier A | 可公开提交 | wrappers, configs, patches, schemas, small synthetic/example outputs, summary tables, manifests |
| Tier B | 可公开但需外部存储 | 允许再分发的大型 outputs 或 processed benchmark, 附 checksum |
| Tier C | 不公开再分发 | 受限数据, checkpoint, PDB/protein/ligand 文件或 license 不清资源, 只提供获取说明, scripts, checksum 和摘要 |
| Tier D | 不使用或需人工决策 | license unclear, 非官方镜像, 需要申请/登录且未授权的资源 |

### 9.9 Reproducibility manifest

每个 run 必须有 `run_metadata.json` 或等价记录:

```text
method
upstream repo/commit
fork repo/branch/commit
patch list
algorithm_changed
dataset name/version/view/split/checksum
checkpoint source/checksum
seed
sampling budget
config hash
command
environment
CUDA/Python/dependency versions
hardware
stdout/stderr log
output manifest
label protocol version
label config hash
resource budget config hash
evaluator environment path, especially /home/lyj/mnt/project/pfr-eval-tools for formal PLIP/Vina
```

### 9.10 Paper figure/table map

推荐主文和附录图表:

- Fig 1: audit-to-repair pipeline 与 claim ladder.
- Table 1: candidate method feasibility/auditability/license.
- Table 2: stage-wise attrition.
- Fig 2: failure prevalence by method and denominator.
- Fig 3: secondary tag co-occurrence heatmap.
- Fig 4: repairable near-miss subset by method/pocket.
- Table 3: repair benchmark dataset and splits.
- Table 4: baseline repair results under fixed budget.
- Fig 5: repair gain stratified by failure type.
- Appendix: excluded methods, blocked resources, license decisions, full manifests, negative results.

### 9.11 Go/no-go criteria

Go for raw failure distribution claim:

- 已捕获 raw/intermediate/rejected/selected/final 中至少关键阶段.
- `N_budget` 和 `N_raw_attempt_metadata` 可追踪.
- stage-wise denominator 完整.
- final-only 和 stage-limited 方法单独列为相应 audit 类型.

Go for cross-method comparison:

- 多个方法运行在同一 audit dataset view, 相同或可说明的 candidate budget, 统一 diagnosis protocol 和统一 denominator 口径下.
- 同时报告 sample-weighted 与 method-weighted.

Go for original-protocol reproduction claim:

- 使用原数据版本, split, preprocessing, checkpoint, sampling/filtering/reranking/evaluation.
- 改动仅限日志或输出捕获.

Go for public artifact release:

- 每个资源的 license, citation, checksum, 再分发权限和访问限制均已记录.
- license 不清或受限资源从公开包中移除, 以 manifest 和获取说明替代.

No-go:

- 没有 denominator 的比例进入主文结论.
- selected-only 或 stage-limited 方法并入 raw distribution.
- artifact license 未检查.
- negative results 被删去.
- 计划文件未落盘却声称 phase plan completed.

### 9.12 EXPERIMENT_LOG 和 STATUS 触发规则

若本计划最终作为重要阶段完成并落盘, 必须执行以下文档同步规则:

#### 计划落盘时

追加 `/home/lyj/mnt/project/pocket-failure-repair/docs/EXPERIMENT_LOG.md`:

```text
- date/time
- action=third_party_failure_audit_detailed_plan_persisted
- plan_path=/home/lyj/mnt/project/pocket-failure-repair/docs/plan/20260603-03-third-party-failure-audit-detailed-execution-plan.md
- upstream_plan=/home/lyj/mnt/project/pocket-failure-repair/docs/plan/20260603-02-third-party-failure-audit-alignment-plan.md
- review_source=review_feedback_20260602_conversation
- key_fixes=failed_sample_status_model, raw_denominator_gate, frozen_schema_dependency, sanity_only_boundary, resource_thresholds, docs_update_triggers, pfr_eval_tools_boundary
- next_step=Phase 1 candidate feasibility table or user decision if blocked
```

同步 `/home/lyj/mnt/project/pocket-failure-repair/docs/STATUS.md`:

```text
current_focus=third_party_failure_audit_phase_1_candidate_feasibility
latest_plan=/home/lyj/mnt/project/pocket-failure-repair/docs/plan/20260603-03-third-party-failure-audit-detailed-execution-plan.md
plan_status=persisted
main_next_gate=pre-screen gate
```

#### 每个 Phase gate 通过或失败时

追加 EXPERIMENT_LOG:

```text
phase:
gate:
outcome: passed|failed|degraded|blocked_pending_user_decision
artifacts:
negative_results:
blockers:
claim_level_allowed:
next_step:
```

同步 STATUS 的条件:

- 当前项目主焦点改变.
- 新的关键 artifact 生成, 如 feasibility table, dataset manifest, frozen label config, MVP run manifest, near-miss report.
- 出现会阻塞下一阶段的资源, license, leakage, evaluator 环境或用户决策问题.
- 正式第三方 audit run 开始或结束.
- BIBM claim level 发生升降级.

#### 不需要同步 STATUS 的情况

- 纯草稿讨论, 未落盘.
- 小的 wording 修订, 不改变 gate, artifact 或 next action.
- sanity set 内部调试, 未影响 frozen protocol.

## 10. 全局 go/no-go gates

| Gate | Go | 降级 | Stop |
|---|---|---|---|
| Persistence gate | 目标文件存在且包含最终接受版本 | draft_for_persistence | 文件不存在却要宣称计划已落盘 |
| Pre-screen gate | 任务相关, 可审计潜力高, evidence 可追溯 | related work only 或 stress-test | 任务不匹配, 无可核验输出 |
| Resource gate | code/checkpoint/data/split/license 至少满足一种可运行路径且在 resource threshold 内 | audit_protocol_only, selected_output_only, blocked_pending_resource | license 不允许, 核心资源不可得且无 fallback, 超阈值且未获批准 |
| Instrumentation gate | 只需 wrapper/logging/patch, 不改算法 | adapted baseline | 必须改 sampling/filtering/reranking/docking/evaluation |
| Raw denominator gate | `N_budget` 和 raw attempt metadata 可追踪 | stage-limited audit 或 selected-output residual audit | 缺 lineage 却试图报告 raw distribution |
| Quality gate | 输出预期基本合理, pipeline failure 可分离 | stress-test / negative case | 输出主要工程崩溃或不可评价 |
| Audit-readiness design gate | run metadata, sample lineage, dataset view, split, checksum, denominator, label protocol 都可设计 | selected-output residual audit 或 exploratory | 无法记录 denominator/provenance |
| Diagnosis/statistics analysis-frozen gate | schema/config/tool_versions/denominator/hash 冻结且 sanity 通过 | pilot/sanity only | 未冻结却进行正式 labeling/statistics |
| Leakage gate | clean subset passed, unknown risk 单独标注 | risk-annotated/exploratory | high overlap 污染 clean main audit 或 repair-test |
| MVP real-output execution gate | 2-3 方法小规模真实 output audit 产生可追溯 artifacts | narrower method subset or negative result | 无真实 outputs 却声称 MVP audit 完成 |
| Repair-benchmark gate | near-miss 非偶然存在, split 隔离, evaluator 稳定, baseline budget fair | narrowed scope 或 diagnosis benchmark | near-miss 极低, leakage 无法隔离, fairness 不成立, 无真实 audit evidence |
| Claim/artifact gate | claim 绑定 evidence, artifact license 清楚 | lower claim level, Tier C release | evidence 缺失或 license 禁止公开 |

## 11. 第一阶段 MVP checklist

第一阶段 MVP 分为 planning/design 部分和真实 output audit 执行部分. 本文档只覆盖 planning/design; 后续若要声称第一阶段 MVP 完成, 必须完成真实 output audit 执行部分.

### 11.1 候选方法与资源

- [ ] 收集候选方法长名单, 每项有 paper/repo/data/checkpoint evidence link.
- [ ] 应用 hard exclusion criteria, 记录排除原因.
- [ ] 完成 `method_feasibility_table`, 包含本文定义的所有字段.
- [ ] 记录 resource budget config version/hash.
- [ ] 选出 5-8 个进入 paper/code-level assessment.
- [ ] 选出 2-3 个进入 first-round minimal audit trial design.
- [ ] 每个方法有 `decision_tier`, `final_status`, `run_boundary_label`.
- [ ] 每个阻塞有 `failure_type`, `attempted_source`, `evidence`, `fallback`, `decision`, `risk_note`.

### 11.2 数据, split 与 leakage

- [ ] 每个候选方法有 method data card.
- [ ] raw dataset manifest template 已固定.
- [ ] dataset view manifest template 已固定.
- [ ] split registry template 已固定, 包含 train, validation, test, audit_discovery, repair_train, repair_validation, repair_test.
- [ ] checksum 字段和引用规则已固定.
- [ ] training_data_unknown 和 leakage_check_status 规则已固定.
- [ ] PDB, complex, protein sequence, ligand, InChIKey, scaffold, pocket/family overlap 检查计划已写入 checklist.

### 11.3 代码, patch 与插桩

- [ ] 每个候选方法有 output stage capture matrix.
- [ ] 明确可捕获 raw, parsed, rejected, selected, final 中哪些阶段.
- [ ] 明确 `N_budget` 和 raw attempt metadata 是否可追踪.
- [ ] 明确 original failed samples 如何映射到 `sample_role` 和 `original_status`.
- [ ] final-only 方法已降级为 selected-output residual audit.
- [ ] 缺 raw/N_budget lineage 的方法已降级为 stage-limited audit.
- [ ] patch 允许项和禁止项已固定.
- [ ] fork branch/patch 记录字段已固定.
- [ ] resource, environment, license, output format 阻塞升级路径已固定.

### 11.4 Diagnosis 与统计 draft-ready gate

- [ ] `label_schema.json` 草案已完成, 可用于 trial design.
- [ ] `label_config.yaml` 字段和 hash 生成方式草案已完成.
- [ ] primary labels 枚举草案已完成, 且不包含 `not_evaluable`.
- [ ] secondary labels 枚举草案已完成.
- [ ] precedence hierarchy 草案已完成.
- [ ] evaluability states 草案已完成.
- [ ] stage-wise denominator 定义草案已完成.
- [ ] attrition table 模板草案已完成.
- [ ] inclusive vs evaluable-only prevalence 口径草案已完成.
- [ ] sample-weighted vs method-weighted 聚合口径草案已完成.
- [ ] bootstrap 和 co-occurrence 计划草案已完成.
- [ ] sanity set 允许来源和 `sanity_only` 边界已写明.

### 11.5 Diagnosis 与统计 analysis-frozen gate

- [ ] `label_schema.json` 已冻结并记录 version/hash.
- [ ] `label_config.yaml` 已冻结并记录 version/hash.
- [ ] `tool_versions.lock` 已冻结.
- [ ] 正式 PLIP/Vina evaluator 环境 `/home/lyj/mnt/project/pfr-eval-tools` 已记录在 tool_versions/run_metadata 要求中.
- [ ] primary/secondary labels 和 precedence hierarchy 已冻结.
- [ ] evaluability mapping 已冻结.
- [ ] denominator definitions 和 raw denominator gate 已冻结.
- [ ] 至少一个 sanity set 已证明 missing_data/tool_failure/pipeline_failure/not_evaluable/original_failed_sample 不会被静默删除.
- [ ] 任何后续真实 output audit 均要求引用同一 frozen label_config_hash.

### 11.6 Near-miss 和 repair benchmark 预注册

- [ ] near-miss inclusion/exclusion 规则已固定.
- [ ] `near_miss_eligible` 不影响 primary_label 的原则已固定.
- [ ] 仅真实第三方 audit outputs 可进入正式 near-miss prevalence 的原则已固定.
- [ ] low-prevalence fallback 已预注册.
- [ ] audit-discovery, repair-train, repair-validation, repair-test 隔离规则已固定.
- [ ] baseline taxonomy 已固定.
- [ ] budget fairness table 字段已固定.
- [ ] evaluation gate 已固定, Vina-only success 被禁止.
- [ ] repair gain relative to failed candidate 的报告模板已固定.

### 11.7 第一阶段 MVP 真实 output audit 执行 checklist

后续执行若要声称第一阶段 MVP 完成, 必须满足:

- [ ] Phase 5 analysis-frozen gate 已通过.
- [ ] 2-3 个代表性方法已经完成最小真实 output audit run, 或记录了不可执行的 negative result.
- [ ] 每个 run 有 `run_metadata.json`, `samples.jsonl`, output manifest 和日志.
- [ ] raw-prevalence 方法有 `N_budget` 和 raw attempt metadata.
- [ ] stage-limited/selected-only 方法已单独标记, 未进入 raw distribution.
- [ ] original failed samples 已保留为 `sample_role=original_failed_sample` 和 `original_status.status=failed`.
- [ ] 标签结果引用 frozen `label_schema`, `label_config_hash`, `tool_versions.lock`.
- [ ] 已生成 stage_attrition 和 not_evaluable breakdown.
- [ ] 已以 scoped MVP evidence 回答真实 outputs 中是否存在非偶然 near-miss.
- [ ] 负结果和 blockers 已记录, 未因不理想结果修改 denominator 或 label.

### 11.8 BIBM claim, artifact 与文档更新

- [ ] claim ladder 已固定.
- [ ] allowed wording vs forbidden wording 已固定.
- [ ] negative results policy 已固定.
- [ ] artifact registry 字段已固定.
- [ ] release tiers A-D 已固定.
- [ ] reproducibility manifest 字段已固定.
- [ ] paper figure/table map 已固定.
- [ ] 计划落盘后已追加 `/home/lyj/mnt/project/pocket-failure-repair/docs/EXPERIMENT_LOG.md`.
- [ ] 计划落盘或 gate 状态改变后已同步 `/home/lyj/mnt/project/pocket-failure-repair/docs/STATUS.md`.

## 12. 后续 agent/workflow 任务拆分

后续执行建议拆成可并行但有 gate 依赖的 agent/workflow. 每个 agent 只提交可追溯 evidence, 不直接扩大 claim.

### 12.1 Method scout agent

任务:

- 收集候选方法长名单.
- 提取论文任务, repo, license, checkpoint, dataset, split, preprocessing, inference script, output stages.
- 填写 feasibility table 初稿.
- 给出 5-8 个 paper/code-level assessment 候选.

交付:

- `candidate_methods_longlist`.
- `method_feasibility_table` 初稿.
- `hard_exclusion_log`.
- evidence links.

Gate:

- 通过 pre-screen gate 后交给 code/resource agent 和 data steward agent.

### 12.2 Data steward agent

任务:

- 为每个候选方法建立 method data card.
- 设计 raw dataset manifest, dataset view manifest, split registry.
- 记录 training data status 和 leakage risk.
- 制定 overlap/leakage report 模板.

交付:

- raw manifest template.
- dataset view manifest template.
- split registry template.
- leakage checklist.
- method data card.

Gate:

- 通过 data provenance 和 leakage gate 后, 方法才可进入 clean main audit 设计.

### 12.3 Code/resource/instrumentation agent

任务:

- 审核 repo, license, inference script, checkpoint, environment 风险.
- 应用 resource budget threshold.
- 设计 fork branch 和 patch strategy.
- 判断 raw/rejected/selected/final capture 可行性.
- 判断 original failed samples status mapping 可行性.
- 记录 resource blocker.

交付:

- method artifact card.
- output stage capture matrix.
- instrumentation plan.
- resource blocker log.

Gate:

- 通过 resource gate 和 instrumentation gate 后, 方法进入 first-round trial design.

### 12.4 Audit metadata and run-plan agent

任务:

- 为 2-3 个方法制定 minimal audit trial plan.
- 定义 run_metadata, samples.jsonl, output manifest, lineage schema.
- 明确 run boundary label, denominator 和 sample_role/original_status model.

交付:

- first-round trial plan.
- run_metadata schema.
- sample metadata schema.
- stage denominator plan.

Gate:

- 通过 audit-readiness design gate 后, 等待 diagnosis/statistics analysis-frozen gate. 未冻结前不得实际运行真实 audit labeling 或 near-miss 统计.

### 12.5 Diagnosis/statistics agent

任务:

- 固定 label_schema, label_config, tool versions, thresholds.
- 固定 primary/secondary labels 和 precedence.
- 固定 not_evaluable/tool_failure/pipeline_failure/missing_data 处理.
- 固定 attrition, prevalence, bootstrap, co-occurrence 统计口径.
- 验证 sanity set, 但不把 sanity set 作为正式 prevalence evidence.
- 记录 `/home/lyj/mnt/project/pfr-eval-tools` 中 PLIP/Vina evaluator provenance 要求.

交付:

- `label_schema.json` draft and frozen version.
- `label_config.yaml` draft and frozen version.
- `tool_versions.lock`.
- statistics plan.
- sanity check log.

Gate:

- 通过 diagnosis/statistics analysis-frozen gate 后, 标签结果才可进入主 audit.

### 12.6 MVP audit execution agent

任务:

- 在 frozen protocol 下运行 2-3 个代表方法的小规模真实 output audit.
- 捕获最小 raw/selected/final 或 stage-limited evidence.
- 生成 run metadata, sample metadata, labels, attrition, summary.
- 记录 blockers 和 negative results.
- 回答真实 outputs 中是否存在非偶然 near-miss.

交付:

- run manifests.
- output manifests.
- labels and attrition.
- near-miss MVP evidence.
- negative result log.

Gate:

- 通过 frozen-protocol execution gate 后, 才能把真实 outputs 作为 L2/L3 scoped evidence.

### 12.7 Repair benchmark agent

任务:

- 在无真实 audit outputs 时, 只做 near-miss eligibility 和 benchmark 预注册.
- 在真实 audit evidence 存在后, 根据 frozen diagnosis protocol 构造 near-miss subset.
- 设计 audit-discovery/repair-train/repair-validation/repair-test split isolation.
- 设计 baseline taxonomy, budget fairness, evaluation gate, repair gain reporting.
- 制定 low-prevalence fallback.

交付:

- near-miss eligibility config.
- repair split policy.
- baseline/evaluation config.
- fallback decision tree.
- 若进入构造阶段, 交付 benchmark dataset card 和 split manifest.

Gate:

- 通过 repair-benchmark gate 后, 才能开展正式 repair benchmark 构建和 repair claim.

### 12.8 Claim/artifact/paper agent

任务:

- 将每个 claim 绑定 evidence object.
- 维护 artifact registry 和 release tiers.
- 规划 audit/repair result tables and figures.
- 确保 negative results 和 limitations 被保留.
- 维护 EXPERIMENT_LOG 和 STATUS 同步.

交付:

- claim-evidence matrix.
- artifact registry.
- reproducibility manifest template.
- paper figure/table map.
- docs update log.

Gate:

- 通过 claim/artifact gate 后, 才能把结果写入 BIBM 主文或 artifact 包.

## 13. 最小执行顺序建议

后续真正执行时, 建议按以下顺序推进:

```text
Phase 0 scope/resource/persistence freeze
→ persist this plan to /home/lyj/mnt/project/pocket-failure-repair/docs/plan/20260603-03-third-party-failure-audit-detailed-execution-plan.md
→ append EXPERIMENT_LOG and sync STATUS
→ Phase 1 candidate feasibility table
→ Phase 2 data/view/split/leakage templates
→ Phase 3 code/resource/instrumentation assessment
→ Phase 4 2-3 methods minimal audit trial design
→ Phase 5 diagnosis/statistics draft-ready sanity
→ Phase 5 diagnosis/statistics analysis-frozen gate
→ Phase 5E first-stage MVP real-output audit execution under frozen protocol
→ review L2/L3 evidence: raw/stage denominator, near-miss evidence, leakage status
→ Phase 6 repair benchmark pre-registration or construction only if real audit evidence exists
→ Phase 7 BIBM claim/artifact packaging
```

关键约束:

- Trial design 可以先行, 但任何真实 output audit, labeling, near-miss 判定和统计必须在 `label_schema`, `label_config`, `tool_versions`, denominator definitions, resource config 和 hash 冻结后执行.
- 如果后续只完成 Phase 1-4 设计, 只能声称“完成详细执行计划和 trial design”, 不能声称“完成第一阶段 MVP audit”.
- 如果要声称第一阶段 MVP audit 已完成, Phase 5E 的小规模真实 output audit 是必需的, 不是 optional.
- 在没有真实第三方 audit outputs 之前, repair model 主张必须保持 pending.
- 在 near-miss 占比, leakage status, denominator 和 baseline fairness 未通过 gate 之前, 不进入 full repair benchmark claim.
- 若任何关键 evidence object 缺失, 降低 claim level, 不补写不可追溯结论.
