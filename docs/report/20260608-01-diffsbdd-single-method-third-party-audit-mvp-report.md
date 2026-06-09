# DiffSBDD 单方法 Third-party Audit MVP 简要报告

## 摘要

本轮完成了 DiffSBDD 单方法 third-party audit MVP sanity 实验。实验目标是验证最小闭环是否可运行: resource go/no-go check, DiffSBDD minimal inference, output capture, sample metadata, denominator tracking, evaluator/diagnosis wiring, blocker/coverage 记录。

本报告只覆盖 DiffSBDD。未执行 DiffLinker, 未做 cross-method comparison, 未声明 formal failure prevalence, 未声明 official/original protocol reproduction, 也未声明 repair benchmark result。

## 实验身份

- `experiment_name`: `diffsbdd-single-method-third-party-audit-mvp`
- `experiment_id`: `20260607-01-diffsbdd-single-method-third-party-audit-mvp`
- `run_id`: `r001_seed0_budget3_3rfm_47b93b20`
- `method`: `DiffSBDD`
- `case`: `3rfm`
- `seed`: `0`
- `n_samples`: `3`
- `claim_boundary`: `mvp_sanity_not_formal_prevalence`

主要路径:

- 实验资产: `experiments/20260607-01-diffsbdd-single-method-third-party-audit-mvp/`
- run 输出: `outputs/20260607-01-diffsbdd-single-method-third-party-audit-mvp/diffsbdd/r001_seed0_budget3_3rfm_47b93b20/`
- 详细过程记录: `docs/EXPERIMENT_LOG.md`

## Resource Check

Inference 前已完成 go/no-go resource check, 并写入:

`experiments/20260607-01-diffsbdd-single-method-third-party-audit-mvp/metadata/method_resource_check.jsonl`

关键结果:

- `decision=go`
- `resource_status=ready`
- Code license: `MIT`
- Checkpoint access type: `public`
- Checkpoint size: `17861341` bytes
- Checkpoint sha256: `07f86764bf569aafbc40a9c15fc02de8e2550437dd0f17f657eab3abe66c372c`
- Training data status: `training_data_unknown`
- Leakage check status: `unknown_risk`

因此本轮只支持 MVP sanity 结论。由于 training/leakage 状态未知, 本轮结果不能作为 clean formal audit conclusion。

## 环境与配置

DiffSBDD inference 使用独立 Conda 环境 `pfr-diffsbdd`, evaluator 使用 `pfr-eval-tools`, 未混用。

环境记录:

- `experiments/20260607-01-diffsbdd-single-method-third-party-audit-mvp/metadata/env_info.json`
- `experiments/20260607-01-diffsbdd-single-method-third-party-audit-mvp/metadata/conda_export.yml`
- `experiments/20260607-01-diffsbdd-single-method-third-party-audit-mvp/metadata/pip_freeze.txt`

Resolved trial config:

- `experiments/20260607-01-diffsbdd-single-method-third-party-audit-mvp/configs/resolved/third_party/diffsbdd_single_method_mvp_trial.yaml`
- sha256: `47b93b2080d6006c3d13210f1e6392154040f1989b2f822ed4a448f244949226`

## Output Capture 与 Denominator

run 已生成 required outputs:

- `run_metadata.json`
- `samples.jsonl`
- `output_manifest.json`
- `stage_attrition.json`
- `captured_outputs/generated.sdf`
- `processed/normalized_samples/sample_000.sdf`
- `processed/normalized_samples/sample_001.sdf`
- `processed/normalized_samples/sample_002.sdf`
- `logs/`
- `manifests/`
- `evaluator/`
- `summaries/`

核心 denominator 结果:

- `N_budget=3`
- `N_raw_attempt_metadata=3`
- `N_raw_captured=3`
- `N_final=3`
- `N_missing_output=0`
- `N_pipeline_failure=0`
- `N_tool_failure=0`
- `N_not_evaluable=0`
- `N_evaluable=3`

denominator 来自 sample metadata rows, 不是只按 SDF 文件数推断。3 个 normalized SDF 均已在 `pfr-eval-tools` 中通过 RDKit parse/sanitize 检查。

## Evaluator 与 Diagnosis Sanity

本轮 evaluator 只做 sanity wiring。运行工具包括:

- RDKit
- PoseBusters `mol`
- PoseBusters `dock`
- optional PLIP
- optional Vina

输出:

- `evaluator/evaluator_input.jsonl`
- `evaluator/evaluator_tool_results.jsonl`
- `evaluator/diagnosis_sanity.jsonl`
- `evaluator/raw_tool_outputs/posebusters_*.json`
- `summaries/evaluator_summary.json`

结果计数:

- tool result rows: `15`
- diagnosis rows: `3`
- `rdkit::passed=3`
- `plip::passed=3`
- `vina::passed=3`
- `posebusters_mol::failed=3`
- `posebusters_dock::failed=3`

PoseBusters `mol` 的代表性 failed check 为 `mol_true_loaded`, 与 MVP 未传入 true/reference ligand 给该检查有关。PoseBusters `dock` 的代表性 failed checks 包括 `minimum_distance_to_organic_cofactors`, `volume_overlap_with_organic_cofactors`, `mol_true_loaded`, `most_extreme_clash_protein`, `not_too_far_away_inorganic_cofactors`, `not_too_far_away_waters`。

这些结果只作为 evaluator wiring evidence。当前没有生成正式 `labels.jsonl` 或 `label_summary.json`, 也不把 PoseBusters sanity failure 解释为 formal failure prevalence。

## Blocker 与风险

当前没有 active blocker。已记录的非阻断风险包括:

- DiffSBDD checkpoint training data status 为 `training_data_unknown`。
- Leakage check status 为 `unknown_risk`。
- PoseBusters 部分检查依赖 true/reference ligand, MVP 输入口径需要在 formal audit 前冻结。
- Vina score 仅可作为辅助 metric, 不能单独定义 success/failure。

一次失败尝试已归档:

`outputs/20260607-01-diffsbdd-single-method-third-party-audit-mvp/diffsbdd/r001_seed0_budget3_3rfm_47b93b20/logs/attempt_001_seed_launcher_sys_path_failure/`

失败原因是 seeded launcher 未把 DiffSBDD repo 加入 `sys.path`, 修复后同一 run 完成。

## 验证

已完成验证:

- Required output 目录和文件齐全。
- 3 个 normalized SDF 均可 RDKit parse/sanitize。
- 本轮项目自有 JSON/JSONL 均写入 `schema_version` 和 `schema_path`。
- 轻量 schema subset validation 通过: `rows_checked=28`, `files_checked=10`。
- 项目测试通过: `conda run -n pfr env PYTHONPATH=src pytest -q` -> `32 passed`。

## 结论

DiffSBDD 单方法 third-party audit MVP sanity 闭环已跑通。当前结果证明最小链路可以捕获输出, 保留 denominator, 生成 schema-traceable metadata, 并将 RDKit/PoseBusters/PLIP/Vina 的 evaluator evidence 写入 diagnosis sanity。

本轮不支持 formal failure prevalence, original protocol reproduction, cross-method comparison 或 repair benchmark conclusion。

## 下一步

1. formal audit 前冻结 PoseBusters/RDKit/PLIP/Vina 规则口径, 特别是 reference-dependent checks。
2. 单独为 DiffLinker 建立 method-specific inference 环境和 MVP sanity run, 不与本轮 DiffSBDD 混合统计。
3. 在 analysis-frozen gate 后再考虑正式 label pipeline 和 failure prevalence audit。
