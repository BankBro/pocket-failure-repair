# PoseBusters internal_energy 条件冻结规则 v0.2 落地报告

## 基本信息

- 对应计划: `docs/plan/20260609-01-posebusters-internal-energy-conditional-gate-plan.md`
- 上游统一评估计划: `docs/plan/20260608-03-unified-evaluation-pipeline-alignment-plan.md`
- 实验名称: `unified-evaluation-pipeline-alignment`
- 实验 ID: `20260608-02-unified-evaluation-pipeline-alignment`
- 方法: DiffSBDD
- 源 run: `outputs/20260608-01-diffsbdd-original-protocol-sanity/diffsbdd/r001_official_example_3rfm_seed0_78d8cd91/`
- v0.1 对照 run: `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r001_frozen_eval_diffsbdd_stage1_3rfm_78d8cd91/`
- 本轮 v0.2 run: `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r002_frozen_eval_diffsbdd_stage1_3rfm_v02_fbfc8032/`

本轮没有重新运行 DiffSBDD inference, 只重新运行统一 evaluator, labels, summaries 和 analysis-frozen gate. 输入仍是阶段 1 README 3RFM 示例的 20 个 final SDF 样本.

## 修改动机

v0.1 gate 把 PoseBusters ligand core 的 `internal_energy` 作为无条件必需 frozen column. 在 sample index `11` 和 `16` 上, wrapper 只保存布尔检查, 因而把 `internal_energy=NaN` 表达成 `missing_frozen_column:internal_energy`, 并将样本标为 `tool_failure`.

复核显示, PoseBusters 原始 full report 中 `internal_energy` 列存在, 但值为 `NaN`. 直接原因是 energy ratio 模块无法生成参考构象 ensemble, 日志为 `Failed to generate conformations.`. 这表示该子检查项不可判定, 不是 PoseBusters 整体失败, 也不能单独解释为分子失败.

## 已完成改动

- 新增 v0.2 配置:
  - `configs/audit/evaluator_policy_v0_2.yaml`
  - `configs/audit/analysis_frozen_gate_v0_2.yaml`
  - `configs/audit/diagnosis_label_config_v0_3.yaml`
- 新增对应 config schema:
  - `schemas/configs/audit/evaluator_policy_v0_2.json`
  - `schemas/configs/audit/analysis_frozen_gate_v0_2.json`
  - `schemas/configs/audit/diagnosis_label_config_v0_3.json`
- 更新文档索引:
  - `configs/audit/README.md`
  - `schemas/README.md`
- 修改 evaluator wrapper:
  - `scripts/eval/eval_posebusters_one.py` 现在保存 `posebusters_report_values`, `posebusters_non_boolean_checks`, `posebusters_unavailable_columns`, `posebusters_unavailable_reasons`.
  - `NaN`, `inf`, `pd.NA`, numpy scalar 会转成 JSON-safe 值.
- 修改 evaluator / label / gate:
  - `scripts/eval/run_audit_evaluators.py` 区分 required columns, conditional columns, failed, missing, unavailable.
  - `scripts/eval/build_audit_labels.py` 把 `internal_energy=false` 记录为 `high_internal_energy_evidence`, 把 `internal_energy=NaN` 记录为 `posebusters_internal_energy_unavailable`.
  - `scripts/eval/summarize_audit_labels.py` 统计 internal energy coverage.
  - `scripts/eval/check_analysis_frozen_gate.py` 对 unavailable coverage 给出 warning, 并按阈值判断是否阻塞.
- 补充测试:
  - `tests/test_unified_evaluation_pipeline.py`

v0.1 配置和 v0.1 run 没有静默改写.

## v0.2 规则摘要

PoseBusters ligand core v0.2 把 `internal_energy` 改为 conditional column:

- `internal_energy=true`: 条件项已判定且通过.
- `internal_energy=false`: 条件项已判定且失败, 作为 `local_geometry_failure` 的高内部能量证据.
- `internal_energy=NaN/null`: 若原始 full report 中列存在且 energy ratio 相关列存在, 记录为 `posebusters_internal_energy_unavailable`, 不作为 pass/fail.
- `internal_energy` 原始列真缺失, PoseBusters 整体报错或 wrapper 失败: 仍作为 gate blocker.

本轮 active phase 为 MVP sanity, `internal_energy_unavailable_fraction` 阈值为 `0.10`.

## 重新评估结果

Tool status counts:

- `rdkit::passed=20`
- `posebusters_mol::passed=15`
- `posebusters_mol::failed=5`
- `posebusters_dock::passed=20`
- `plip::passed=20`
- `vina::passed=20`

Label summary:

- labels: 20
- evaluable: 20
- primary labels:
  - `unknown`: 15
  - `local_geometry_failure`: 5
- near_miss_eligible: 5

PoseBusters internal energy coverage:

- `internal_energy_false_count=0`
- `internal_energy_unavailable_count=2`
- `internal_energy_unavailable_fraction=0.10`
- unavailable sample ids:
  - `diffsbdd_diffsbdd_example_3rfm_5ndu_v1_3rfm_final_11`
  - `diffsbdd_diffsbdd_example_3rfm_5ndu_v1_3rfm_final_16`

Gate:

- `gate_status=passed_with_warnings`
- blocking failures: none
- warnings:
  - `posebusters_internal_energy_unavailable:*_final_11`
  - `posebusters_internal_energy_unavailable:*_final_16`
  - `posebusters_internal_energy_unavailable_coverage:2/20`
  - `final_only_outputs_selected_output_residual_view_only`
  - `training_data_or_leakage_status_unknown_claim_boundary_required`
  - `plip_reference_recovery_descriptive_only`

## 样本解释

`sample_011`:

- v0.1: `tool_failure`, 原因为 `missing_frozen_column:internal_energy`.
- v0.2: `evaluable + local_geometry_failure`.
- 主证据: `bond_lengths=false`.
- 附加诊断: `posebusters_internal_energy_unavailable`, reason 为 `energy_ratio_conformer_ensemble_unavailable`.

`sample_016`:

- v0.1: `tool_failure`, 原因为 `missing_frozen_column:internal_energy`.
- v0.2: `evaluable + local_geometry_failure`.
- 主证据: `bond_lengths=false`, `bond_angles=false`.
- 附加诊断: `posebusters_internal_energy_unavailable`, reason 为 `energy_ratio_conformer_ensemble_unavailable`.

这两个样本不是 SDF 文件坏掉, 也不是 PoseBusters 整体失败. `internal_energy=NaN` 只表示该 energy ratio 子项不可判定; 这两个样本的局部几何失败标签来自独立的 `bond_lengths` 和 `bond_angles` 证据.

## 产物

- `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r002_frozen_eval_diffsbdd_stage1_3rfm_v02_fbfc8032/run_metadata.json`
- `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r002_frozen_eval_diffsbdd_stage1_3rfm_v02_fbfc8032/samples.jsonl`
- `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r002_frozen_eval_diffsbdd_stage1_3rfm_v02_fbfc8032/evaluator/evaluator_tool_results.jsonl`
- `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r002_frozen_eval_diffsbdd_stage1_3rfm_v02_fbfc8032/labels.jsonl`
- `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r002_frozen_eval_diffsbdd_stage1_3rfm_v02_fbfc8032/summaries/label_summary.json`
- `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r002_frozen_eval_diffsbdd_stage1_3rfm_v02_fbfc8032/summaries/prevalence_summary.json`
- `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r002_frozen_eval_diffsbdd_stage1_3rfm_v02_fbfc8032/summaries/analysis_frozen_gate_result.json`
- `docs/report/20260609-01-posebusters-internal-energy-conditional-gate-report.md`

## 验证

- `conda run -n pfr env PYTHONPATH=src pytest -q` -> `43 passed in 0.80s`.
- r002 evaluator -> `samples=20`, `tool_result_rows=100`.
- r002 labels -> `label_rows=20`.
- r002 gate -> `gate_status=passed_with_warnings`, `blocking=0`.

## Claim boundary

本轮仍是 selected-output residual 分析. `passed_with_warnings` 只表示 required evaluator wiring 和 required frozen columns 可用, 且 `internal_energy` conditional column 有 2/20 的 coverage warning. 不能解释为 PoseBusters 全部评估项完整通过, 不能解释为 DiffSBDD 正式 failure prevalence, 不能声明 official/original protocol reproduction 或 repair benchmark result.

可保守描述为: 当前 20 个 selected final outputs 中有 5 个样本存在 failure-like evidence, 均为 `local_geometry_failure`. 这个数字不能外推为 DiffSBDD 总体失败率.

## 下一步

- 后续更大样本 DiffSBDD audit 可以使用 evaluator policy v0.2, 但 formal analysis 阶段建议将 `internal_energy_unavailable_fraction` 阈值收紧到 `0.05`.
- 扩大样本前仍需冻结 raw attempt denominator, 数据来源, training/leakage 状态和 claim boundary.
