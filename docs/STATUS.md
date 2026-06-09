# STATUS

> 用于上下文压缩或新会话快速恢复。只保留当前最重要状态; 详细过程和历史迁移记录见 `docs/EXPERIMENT_LOG.md`。

## 当前主线

- 项目主线: Failure-feedback-conditioned repair for pocket-aware 3D local molecular editing。
- 当前阶段: `diffsbdd_binding_moad_processed_test_ready_for_pilot`。
- 当前优先事项: 按 `docs/plan/20260609-03-diffsbdd-audit-protocol-pilot-plan.md` 进入 DiffSBDD Binding MOAD test view 审计 pilot. Binding MOAD raw 结构包, `moad_fullatom_cond.ckpt` 和 DiffSBDD `processed_noH_full/test/` 已准备好; 下一步冻结官方 test split 前 20 个 pockets, 然后核查或实现 dataset-level DiffSBDD instrumented wrapper, 记录 raw attempt denominator, captured/rejected/selected/final 样本。
- 重要边界: 现在不是 formal failure prevalence audit, 不是 repair benchmark, 不能宣称第三方方法正式失败率或论文主结果。

## 关键文档

- MVP 开跑边界: `docs/plan/20260604-01-third-party-failure-audit-mvp-trial-boundary-plan.md`
- 详细执行 SOP: `docs/plan/20260603-03-third-party-failure-audit-detailed-execution-plan.md`
- 高层对齐方案: `docs/plan/20260603-02-third-party-failure-audit-alignment-plan.md`
- 第三方 output capture 方案: `docs/plan/20260604-02-third-party-audit-mvp-output-capture-plan.md`
- DiffSBDD 单方法 MVP 计划: `docs/plan/20260607-01-diffsbdd-single-method-third-party-audit-mvp-plan.md`
- DiffSBDD 审计阶段路线图: `docs/plan/20260608-01-diffsbdd-audit-progression-plan.md`
- DiffSBDD 阶段 1 计划: `docs/plan/20260608-02-diffsbdd-original-protocol-sanity-plan.md`
- DiffSBDD 官方数据集审计协议 pilot 计划: `docs/plan/20260609-03-diffsbdd-audit-protocol-pilot-plan.md`
- 统一评估流水线对齐计划: `docs/plan/20260608-03-unified-evaluation-pipeline-alignment-plan.md`
- PoseBusters `internal_energy` 条件冻结计划: `docs/plan/20260609-01-posebusters-internal-energy-conditional-gate-plan.md`
- schema-aware JSON writer 自动化计划: `docs/plan/20260609-02-schema-aware-json-writer-automation-plan.md`
- DiffSBDD 单方法 MVP 简报: `docs/report/20260608-01-diffsbdd-single-method-third-party-audit-mvp-report.md`
- DiffSBDD 阶段 1 报告: `docs/report/20260608-02-diffsbdd-original-protocol-sanity-report.md`
- 统一评估流水线落地报告: `docs/report/20260608-03-unified-evaluation-pipeline-alignment-report.md`
- PoseBusters `internal_energy` 条件冻结落地报告: `docs/report/20260609-01-posebusters-internal-energy-conditional-gate-report.md`
- schema-aware JSON writer 自动化报告: `docs/report/20260609-02-schema-aware-json-writer-automation-report.md`
- schema-aware writer 端到端验证报告: `docs/report/20260609-03-schema-aware-json-writer-e2e-validation-report.md`
- failure taxonomy 调研报告: `docs/report/20260603-01-failure-taxonomy-research-report.md`
- 第一阶段 MVP 报告: `docs/report/20260603-03-third-party-failure-audit-mvp-report.md`
- 工具覆盖度复核报告: `docs/report/20260604-01-audit-tool-coverage-report.md`
- 完整历史记录: `docs/EXPERIMENT_LOG.md`

## 当前可用资产

- 开发 / data writer / smoke test 环境: Conda env `pfr`。
- official PLIP / Vina / PoseBusters evaluator 环境: Conda env `pfr-eval-tools`。
- DiffSBDD 推理环境: Conda env `pfr-diffsbdd`, 由 `third_party/diffsbdd/environment.yaml` 创建并记录在 `experiments/20260607-01-diffsbdd-single-method-third-party-audit-mvp/metadata/`。
- 第三方方法推理环境: 按方法单独创建, 不与 evaluator 环境混用。
- DiffSBDD 单方法 MVP sanity 已完成: run `outputs/20260607-01-diffsbdd-single-method-third-party-audit-mvp/diffsbdd/r001_seed0_budget3_3rfm_47b93b20/`, `N_budget=3`, `N_final=3`, `N_evaluable=3`, evaluator tool rows `15`, diagnosis rows `3`。
- DiffSBDD 阶段 1 README 3RFM 官方示例 sanity 已完成: run `outputs/20260608-01-diffsbdd-original-protocol-sanity/diffsbdd/r001_official_example_3rfm_seed0_78d8cd91/`, `N_budget=20`, `N_final=20`, `N_valid=20`, `N_connected=20`, evaluator tool rows `100`, diagnosis rows `20`, `evaluable=19`, `not_evaluable_tool_failure=1`。
- 统一评估流水线 v0.1 已落地但 gate 未通过: run `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r001_frozen_eval_diffsbdd_stage1_3rfm_78d8cd91/`, receptor prep `unresolved_review_required_count=0`, evaluator tool rows `100`, labels `20`, `evaluable=18`, `not_evaluable_tool_failure=2`, gate status `failed`; 失败原因为 v0.1 将 PoseBusters `internal_energy=NaN` 保守表达为 missing frozen column。
- 统一评估流水线 v0.2 已落地且 gate 通过带 warning: run `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r002_frozen_eval_diffsbdd_stage1_3rfm_v02_fbfc8032/`, evaluator tool rows `100`, labels `20`, 全部 `evaluable`, primary labels `unknown=15`, `local_geometry_failure=5`, gate status `passed_with_warnings`, `internal_energy_unavailable_count=2/20`。
- PoseBusters raw wrapper 输出已 schema 化: schema `schemas/third_party_audit/diagnosis/posebusters_raw_result_v0_1.json`, 验证 run `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r003_frozen_eval_diffsbdd_stage1_3rfm_v02_rawschema_fbfc8032/`, 40 个 `evaluator/raw_tool_outputs/posebusters_*.json` 均写入 schema refs, gate status `passed_with_warnings`。
- schema-aware JSON writer 第一版已落地并完成真实端到端验证: `src/pfr/utils/schema_io.py` 和 `scripts/eval/audit_common.py` 可从 schema `const` 自动注入 `schema_version` / `schema_path`; PoseBusters raw wrapper, evaluator input/tool result, labels, label/prevalence summary 和 gate result 已迁移. 新增人工拍板 YAML schema `schemas/configs/audit/manual_decisions_v0_1.json`. 自动化报告见 `docs/report/20260609-02-schema-aware-json-writer-automation-report.md`.
- schema-aware writer 端到端验证 run 已完成: run `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r004_schema_writer_finalizer_e2e_diffsbdd_stage1_3rfm_v02_fbfc8032/`, evaluator tool rows `100`, raw PoseBusters JSON `40`, labels `20`, gate status `passed_with_warnings`, blocking `0`, `output_manifest.json` finalizer 校验 `n_output_artifacts=293`, sha256 mismatch `0`. 报告见 `docs/report/20260609-03-schema-aware-json-writer-e2e-validation-report.md`.
- DiffSBDD Binding MOAD pilot resource acquisition 已完成: dataset root `data/datasets/binding_moad_zenodo13375913/`, raw manifest `manifests/raw/binding_moad_zenodo13375913_raw_manifest_v1.json`, entries manifest `manifests/entries/binding_moad_zenodo13375913_entries_manifest_v1.json`, manual decisions `experiments/20260609-03-diffsbdd-audit-protocol-pilot/configs/resolved/audit/manual_decisions.yaml`, resource check `experiments/20260609-03-diffsbdd-audit-protocol-pilot/metadata/method_resource_check.jsonl`. 当前 raw `BindingMOAD_2020/*.bio*` 文件数为 `59346`; `every_part_a.zip` 和 `every_part_b.zip` 已在 checksum 校验和解压后删除; `moad_test.txt` 非空条目数为 `130`.
- DiffSBDD Binding MOAD preprocessing 已完成: resolved config `experiments/20260609-03-diffsbdd-audit-protocol-pilot/configs/resolved/data/binding_moad_preprocess_diffsbdd.yaml`, metadata `experiments/20260609-03-diffsbdd-audit-protocol-pilot/metadata/binding_moad_preprocess_metadata.json`, processed dir `data/datasets/binding_moad_zenodo13375913/work/diffsbdd/processed_noH_full/` 本地保留但不提交. 主命令 exit `0`, 输出大小约 `1.5G`, `moad_test.txt` 的 `130` 个 test 条目 coverage `130/130`, missing `0`; 状态为 `completed_with_warnings`, 因为 train count 少 `1` 且日志有 RDKit/Open Babel warning.
- DiffSBDD 阶段 1 协议摘录和 checklist 已记录在 `experiments/20260608-01-diffsbdd-original-protocol-sanity/metadata/official_protocol_excerpt.md` 和 `official_protocol_checklist.json`。
- DiffLinker 官方 repo、小型 checkpoint 和 wrapper dry-run metadata 已准备; 真实 inference 尚未执行。
- 第三方 audit schema 已统一放入 `schemas/third_party_audit/`, 覆盖 run metadata、sample metadata、output manifest、stage attrition、labels、resource check、blocker log、evaluator result、diagnosis sanity、receptor prep、evaluator input、label/prevalence summary 和 gate result。
- config schema 已放入 `schemas/configs/`; 项目级 `configs/audit/`, `configs/data/`, `configs/third_party/` 配置应声明 `schema_version` 和 `schema_path`。
- canonical data schema 已放入 `schemas/data/`; 当前 `data/` 下项目自有 JSON / JSONL metadata 已完成 schema ref 迁移。

## 当前仓库结构状态

- `configs/` 只放项目级真实配置和状态记录; 单次运行 resolved config 放 `experiments/<experiment_id>/configs/resolved/`。
- `data/` 按 `data/datasets/<dataset_id>/` 组织 canonical dataset; raw 结构文件在 dataset-local `raw/<sample_id>/`, 全局 catalog 在 `data/catalog/`。
- `outputs/` 按 `outputs/<experiment_id>/` 组织实验输出; `metadata/`, `summaries/`, `tables/`, `figures/*.svg` 和 summary metrics 可提交, 大规模 JSONL、结构文件、工具报告、logs/work/captured outputs 默认忽略。
- `sources/` 保存文献、检索结果和调研 provenance, 不作为 canonical dataset 或实验输出。
- `third_party/` 保存外部仓库和长期 patch; wrapper / instrumentation 放 `scripts/third_party/`。
- `tmp/` 只放临时中间产物, 使用 `tmp/YYYYMMDD-<task-slug>/`, 任务结束后删除。
- 各关键目录已有 `README.md` / `AGENTS.md`; 具体目录规则以就近文件为准。

## 当前阻塞与风险

- DiffSBDD checkpoint 训练数据 / leakage 状态仍为未知风险; 当前结果只支持 MVP / 阶段 1 sanity 和 Binding MOAD processed-test pilot 准备, 不支持 clean formal conclusion。
- DiffSBDD `processed_noH_full/test/` 已生成并通过 `moad_test.txt` coverage 检查, 但 pilot subset, raw attempt denominator instrumentation 和 leakage/training overlap 状态仍未冻结。
- DiffSBDD 阶段 1 原始 evaluator 在 45 秒外层 timeout 策略下有 `posebusters_mol::failed=19`, `posebusters_dock::failed=19`, sample index `11` mol/dock timeout; 后续 300 秒内层 timeout 复查 sample index `11` 可完成, 结果为 failed checks 而非 timeout. 这些只作为 evaluator wiring evidence, 不能解释成正式失败率.
- DiffLinker 的 method-specific inference Conda env 尚未创建, 真实第三方 inference 尚未运行。
- v0.2 analysis-frozen gate 当前为 `passed_with_warnings`, 不是无 warning 的正式通过. Warning 包括 final-only selected-output residual view, training/leakage unknown, PLIP descriptive only, 以及 `internal_energy_unavailable_count=2/20`。
- 当前统一评估流水线 v0.2 的 selected-output residual view 仅为描述性结果: `unknown=15`, `local_geometry_failure=5`; r004 端到端验证复现该口径, 不能解释为 DiffSBDD 正式失败率。
- Pocket2Mol / TargetDiff checkpoint 与数据涉及 Google Drive 且大小未知, 当前按 resource budget policy 暂停。
- MolCRAFT 为 NonCommercial/ShareAlike, 不作为默认 MVP 主实验; 可作为 restricted-license internal/supplementary audit 候选。
- 3DLinker license 不可见, 暂不 clone/run。
- Vina score 只能作为辅助 metric, 不能单独定义 repair success。

## 下一步

1. 冻结 DiffSBDD Binding MOAD pilot subset: `third_party/diffsbdd/data/moad_test.txt` 官方顺序前 20 个 pockets, 明确每 pocket/seed 的 raw attempts 和 final sample 目标。
2. 新增或核查 dataset-level DiffSBDD instrumented wrapper, 复刻 `test.py` 的 valid-target loop, 但完整记录 raw attempt denominator, candidate, rejected, selected 和 final 样本。
3. 用已生成的 `processed_noH_full/test/` 运行前 20 个 pockets 的 pilot inference, 输出到 `outputs/20260609-03-diffsbdd-audit-protocol-pilot/diffsbdd/<run_id>/`。
4. 默认使用 evaluator policy v0.2, analysis-frozen gate v0.2 和 diagnosis label config v0.3; 若进入 formal analysis, 将 `internal_energy_unavailable_fraction` 阈值从 MVP sanity 的 `0.10` 收紧到 `0.05`。
5. 继续保持 claim boundary: 当前阶段只做数据集审计 pilot, 不声明 clean-test formal failure prevalence, official/original protocol reproduction 或 repair benchmark result。

## 暂停条件

- 需要申请、登录、付费、联系作者或 gated access 的数据/checkpoint。
- Google Drive 或其他资源大小未知, 且可能超过 resource budget。
- license 不清楚, 或存在禁止使用/再分发/改造的风险。
- 需要使用非官方镜像、非官方数据源或不可信 checkpoint。
- 需要替换核心数据集、checkpoint 或官方资源来源。
- 需要修改原方法 sampling、decoding、filtering、reranking、docking config、success definition 或 candidate budget。
- checkpoint 训练数据未知, 但准备作为 clean 主结论证据。
- 单方法下载、存储或运行成本超过当前 resource budget。

## 维护原则

- `docs/STATUS.md` 只保留当前快照, 旧状态要及时删除或压缩。
- `docs/EXPERIMENT_LOG.md` 追加保存完整历史、命令、配置、输出路径、失败原因、阶段结论和下一步。
