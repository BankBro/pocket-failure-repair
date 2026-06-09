# schema-aware JSON writer 端到端验证报告

日期: 2026-06-09

对应计划: `docs/plan/20260609-02-schema-aware-json-writer-automation-plan.md`

## 概要

本轮按计划做了一次真实端到端验证, 用 DiffSBDD 阶段 1 的 20 个 3RFM 生成样本重新跑统一评估流水线 v0.2. 目的不是重新运行 DiffSBDD inference, 而是验证 schema-aware writer, raw PoseBusters schema, labels, summaries, analysis-frozen gate 和 `output_manifest.json` finalizer 能在真实 evaluator run 中协同工作.

## 输入与输出

- 输入源 run: `outputs/20260608-01-diffsbdd-original-protocol-sanity/diffsbdd/r001_official_example_3rfm_seed0_78d8cd91/`.
- receptor prep record: `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r003_frozen_eval_diffsbdd_stage1_3rfm_v02_rawschema_fbfc8032/processed/receptors/3rfm_A_330_CFF_receptor_prep.json`.
- 新 run_id: `r004_schema_writer_finalizer_e2e_diffsbdd_stage1_3rfm_v02_fbfc8032`.
- 输出路径: `outputs/20260608-02-unified-evaluation-pipeline-alignment/diffsbdd/r004_schema_writer_finalizer_e2e_diffsbdd_stage1_3rfm_v02_fbfc8032/`.
- 使用配置: `experiments/20260608-02-unified-evaluation-pipeline-alignment/configs/resolved/audit/` 下的 `evaluator_policy_v0_2.yaml`, `diagnosis_label_config_v0_3.yaml`, `analysis_frozen_gate_v0_2.yaml`, `receptor_prep_policy_v0_1.yaml`, `denominator_statistics_schema_v0_1.yaml`, `tool_versions.lock`.

## 结果

- evaluator tool rows: `100`.
- raw PoseBusters outputs: `40` 个 `evaluator/raw_tool_outputs/posebusters_*.json`, 均带 `schema_version=posebusters_raw_result_v0_1`.
- `evaluator_input.jsonl`: `20` 行, schema `evaluator_input_v0_1`.
- `evaluator_tool_results.jsonl`: `100` 行, schema `evaluator_tool_result_v0_1`.
- `labels.jsonl`: `20` 行, schema `label_v0_1`.
- label summary: `evaluable=20`, primary labels `unknown=15`, `local_geometry_failure=5`, near-miss eligible `5`.
- PoseBusters `internal_energy`: `false_count=0`, `unavailable_count=2/20`, sample ids 为 `*_final_11` 和 `*_final_16`.
- gate: `passed_with_warnings`, blocking failures `0`.
- warnings: final-only selected-output residual view, training/leakage unknown, PLIP descriptive only, `internal_energy` unavailable coverage `2/20`.
- manifest finalizer: `n_output_artifacts=293`, `sha256` 条目 `293`, 缺失文件 `0`, checksum mismatch `0`, 且未把 `output_manifest.json` 自身列入 sha256.

## 结论

schema-aware writer 第一版已通过真实 evaluator run 验证. 当前端到端链路可以生成带 schema refs 的 raw PoseBusters JSON, evaluator input/tool results, labels, summaries 和 gate result, 并在 gate 末尾刷新最终 `output_manifest.json`.

本结果仍只属于 selected-output residual view. 由于输入是 DiffSBDD 阶段 1 final-only 输出, 且 training data / leakage 状态仍未知, 不能解释为 DiffSBDD 正式 failure prevalence, official protocol reproduction 或 repair benchmark result.

## 验证命令

已运行:

```bash
conda run -n pfr-eval-tools env PYTHONPATH=src python scripts/eval/run_audit_evaluators.py ...
conda run -n pfr env PYTHONPATH=src python scripts/eval/build_audit_labels.py ...
conda run -n pfr env PYTHONPATH=src python scripts/eval/summarize_audit_labels.py ...
conda run -n pfr env PYTHONPATH=src python scripts/eval/check_analysis_frozen_gate.py ...
conda run -n pfr env PYTHONPATH=src pytest -q
```

测试结果:

```text
51 passed in 0.77s
```

## 下一步

- 后续 DiffSBDD under audit protocol 更大样本 run 可以默认复用当前 v0.2 评估流水线和 schema-aware writer.
- 进入 formal analysis 前, 仍需冻结 raw attempt denominator, candidate budget, selected/final 输出记录口径, 并收紧 `internal_energy_unavailable_fraction` coverage 阈值.
- 如出现人工拍板, 应按 `schemas/configs/audit/manual_decisions_v0_1.json` 在具体实验 resolved config 中保存 `manual_decisions.yaml`.
