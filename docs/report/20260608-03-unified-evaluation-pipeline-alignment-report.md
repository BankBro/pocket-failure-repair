# 统一评估流水线对齐落地报告

## 基本信息

- 对应计划: `docs/plan/20260608-03-unified-evaluation-pipeline-alignment-plan.md`
- 实验名称: `unified-evaluation-pipeline-alignment`
- 实验 ID: `20260608-02-unified-evaluation-pipeline-alignment`
- 方法: DiffSBDD
- 输入来源: DiffSBDD 阶段 1 README 3RFM 示例 sanity run
- 源 run: `outputs/20260608-01-diffsbdd-original-protocol-sanity/diffsbdd/r001_official_example_3rfm_seed0_78d8cd91/`
- 本轮 run: `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r001_frozen_eval_diffsbdd_stage1_3rfm_78d8cd91/`

本轮没有重新运行 DiffSBDD inference, 只使用阶段 1 已生成的 20 个 final SDF 样本作为输入, 对统一 receptor preparation, evaluator policy, labels, denominator 和 analysis-frozen gate 进行落地验证.

## 已完成内容

- 新增并冻结目标配置:
  - `configs/audit/receptor_prep_policy_v0_1.yaml`
  - `configs/audit/evaluator_policy_v0_1.yaml`
  - `configs/audit/analysis_frozen_gate_v0_1.yaml`
  - `configs/audit/diagnosis_label_config_v0_2.yaml`
- 新增 receptor prep, evaluator input, label summary, prevalence summary 和 gate result schema.
- 实现统一脚本:
  - `scripts/eval/prepare_receptor.py`
  - `scripts/eval/run_audit_evaluators.py`
  - `scripts/eval/build_audit_labels.py`
  - `scripts/eval/summarize_audit_labels.py`
  - `scripts/eval/check_analysis_frozen_gate.py`
- 对 3RFM 执行 receptor preparation:
  - 删除 reference ligand `CFF A:330`.
  - 生成 cleaned receptor PDB 和 reference ligand PDB.
  - `unresolved_review_required_count=0`.
  - Vina box 来自 reference ligand heavy atom centroid, 未使用 generated ligand centroid fallback.
- 对 20 个样本执行 frozen-style evaluator:
  - RDKit: 20 passed.
  - PoseBusters ligand core: 15 passed, 3 failed, 2 tool_failure.
  - PoseBusters pocket core: 20 passed.
  - PLIP: 20 passed.
  - Vina score-only: 20 passed.
- 生成 `labels.jsonl`, `label_summary.json`, `prevalence_summary.json` 和 `analysis_frozen_gate_result.json`.
- 保存环境记录:
  - `metadata/conda_export.yml`
  - `metadata/pip_freeze.txt`
  - `metadata/env_info.json`
  - `metadata/evaluator_conda_export.yml`
  - `metadata/evaluator_pip_freeze.txt`
  - `metadata/evaluator_env_info.json`

## 结果

本轮 gate 结果为 `failed`.

阻塞项:

- `posebusters_mol_missing_frozen_columns:diffsbdd_diffsbdd_example_3rfm_5ndu_v1_3rfm_final_11`
- `posebusters_mol_missing_frozen_columns:diffsbdd_diffsbdd_example_3rfm_5ndu_v1_3rfm_final_16`

解释: v0.1 evaluator policy 把 PoseBusters ligand core 的 `internal_energy` 列列为 frozen column. 在两个样本的 PoseBusters `mol` 输出中该列缺失. 按计划规则, frozen column 缺失不能默认当作 pass, 必须作为 gate blocking failure 记录.

warnings:

- 当前输入是阶段 1 final-only outputs, 只能作为 selected-output residual view, 不能声明 raw failure distribution.
- PLIP reference interaction recovery 在 v0.1 中只是描述性 evidence, 不是硬失败标签.
- DiffSBDD checkpoint 训练数据 / leakage 状态仍为 unknown risk, 不能声明 clean-test 或 clean generalization.

Label summary:

- labels: 20
- evaluable: 18
- not_evaluable_tool_failure: 2
- primary labels:
  - `unknown`: 15
  - `local_geometry_failure`: 3
  - `tool_failure`: 2
- near_miss_eligible: 3

Prevalence summary 仅作为 selected-output residual 描述:

- `selected_output_residual_prevalence`: 5 / 20 = 0.25
- `evaluable_only_molecular_prevalence`: 3 / 18 = 0.1667
- `inclusive_failure_burden`: downgraded, 不声明正式 raw prevalence.

以上数字不是 DiffSBDD 正式失败率, 不是 official/original protocol reproduction 结果, 也不是 repair benchmark result.

## 主要产物

- `run_metadata.json`
- `samples.jsonl`
- `stage_attrition.json`
- `output_manifest.json`
- `processed/receptors/3rfm_A_330_CFF_cleaned_receptor.pdb`
- `processed/receptors/3rfm_A_330_CFF_reference_ligand.pdb`
- `processed/receptors/3rfm_A_330_CFF_receptor_prep.json`
- `evaluator/evaluator_input.jsonl`
- `evaluator/evaluator_tool_results.jsonl`
- `labels.jsonl`
- `summaries/frozen_evaluator_summary.json`
- `summaries/label_summary.json`
- `summaries/prevalence_summary.json`
- `summaries/analysis_frozen_gate_result.json`

## 验证

- `conda run -n pfr env PYTHONPATH=src pytest -q` -> `36 passed`.
- Gate sanity set 全部通过, 覆盖 missing ligand, broken SDF, pipeline failure, tool timeout, Meeko ligand/receptor prepare failure, Vina pass trap, original failed/rejected sample 和 final-only outputs.

## 结论和下一步

统一评估流水线的代码、配置、schema 和 3RFM frozen-style evaluator run 已落地, 但 analysis-frozen gate 未通过. 当前不能进入更大样本 DiffSBDD formal audit, 也不能声明正式 failure prevalence.

下一步应先处理 PoseBusters ligand core frozen column 策略:

1. 调研 `internal_energy` 在 PoseBusters `mol` 输出中缺失的条件.
2. 决定 `internal_energy` 是否继续作为必需 frozen column, 或拆成 optional diagnostic column.
3. 若修改冻结策略, 更新 `evaluator_policy_v0_1` 或新增 v0.2 policy, 重新计算 hash, 重跑 gate.
