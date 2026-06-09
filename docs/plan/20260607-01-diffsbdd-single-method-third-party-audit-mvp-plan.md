# DiffSBDD 单方法 Third-party Audit MVP 计划

> 本文档是 `docs/plan/20260604-02-third-party-audit-mvp-output-capture-plan.md` 的单方法执行版。原计划默认覆盖 DiffSBDD 和 DiffLinker 两个方法, 本轮先只做 DiffSBDD, 用于跑通最小第三方模型审计闭环。

## Context

当前目标不是正式复现第三方论文, 也不是产出正式 failure prevalence。当前目标是先验证一条最小链路是否可行:

```text
DiffSBDD 最小 inference
-> captured output
-> run/sample/stage metadata
-> evaluator/diagnosis sanity wiring
-> blocker 和 coverage 记录
```

单方法 MVP 的好处是边界更清楚, 资源风险更低, 更容易先把 output capture, schema refs, evaluator wiring 和 denominator 记录做扎实。DiffLinker 本轮暂不执行, 后续可在本轮经验稳定后单独建计划或复用本计划结构。

## Scope

本轮只覆盖:

```text
method = DiffSBDD
task_type = SBDD / de novo or inpainting output-capture sanity
scope = single_method_mvp_sanity
```

本轮不覆盖:

- DiffLinker inference。
- cross-method comparison。
- DiffSBDD 与 DiffLinker 合并 failure distribution。
- formal failure prevalence。
- repair benchmark result。
- official/original protocol reproduction 或原论文性能复现。
- BIBM 主张证据。

## Experiment Identity

建议使用:

```text
experiment_name = diffsbdd-single-method-third-party-audit-mvp
experiment_id = 20260607-01-diffsbdd-single-method-third-party-audit-mvp
```

实验资产和输出严格对应:

```text
experiments/20260607-01-diffsbdd-single-method-third-party-audit-mvp/
outputs/20260607-01-diffsbdd-single-method-third-party-audit-mvp/
outputs/20260607-01-diffsbdd-single-method-third-party-audit-mvp/diffsbdd/<run_id>/
```

## Inputs And Reused Assets

执行前优先复用和核查:

- `configs/third_party/diffsbdd_method_status.yaml`
- `experiments/20260603-01-third-party-failure-audit-mvp/configs/resolved/third_party/diffsbdd_audit_protocol.yaml`
- `configs/audit/resource_budget_v1.yaml`
- `configs/audit/tool_versions.lock`
- `schemas/third_party_audit/run/run_metadata_v0_1.json`
- `schemas/third_party_audit/run/output_manifest_v0_1.json`
- `schemas/third_party_audit/samples/failure_sample_metadata_v0_1.json`
- `schemas/third_party_audit/attrition/stage_attrition_v0_1.json`
- `schemas/third_party_audit/diagnosis/evaluator_tool_result_v0_1.json`
- `schemas/third_party_audit/diagnosis/diagnosis_sanity_v0_1.json`
- `schemas/third_party_audit/resources/method_resource_check_v0_1.json`
- `schemas/third_party_audit/resources/blocker_log_v0_1.json`
- `scripts/third_party/run_diffsbdd_instrumented.py`
- `scripts/eval/eval_posebusters_one.py`
- `scripts/eval/eval_official_tools.py`

若现有 wrapper 与本轮边界不一致, 优先在 `experiments/<experiment_id>/scripts/` 新建实验专用轻量 wrapper, 不直接改第三方模型逻辑。

## Go/No-Go Checks

任何 inference 前先完成 DiffSBDD 的 resource check, 并写入:

```text
experiments/<experiment_id>/metadata/method_resource_check.jsonl
```

至少确认:

- 官方 repo URL, commit, license。
- checkpoint 官方来源, license/terms, sha256, access type, size。
- example input / dataset source, license, checksum。
- training data status 和 leakage check status。
- 是否需要 gated access, 登录, 付费, 联系作者, 非官方镜像或未知大小下载。
- 是否超过 `configs/audit/resource_budget_v1.yaml` 的 per-method budget。
- 是否需要修改 sampling, decoding, filtering, reranking, docking config, success definition 或 candidate budget。

遇到 license 不清, gated access, 非官方 checkpoint, checksum 不匹配, 或资源可能超预算时, 暂停并记录 blocker, 不自动绕过。

## Minimal Trial

首轮只跑 DiffSBDD 官方最小 example, 以 output capture 和 metadata 完整性为优先目标:

```text
method = diffsbdd
case = 3rfm
seed = 0
n_samples = 3
```

若官方 example 默认配置更小, 采用官方更小配置。若必须缩小官方设置以符合 MVP budget, 标注为 `budget_reduced_mvp_sanity`, 不称完整原协议复现。

`run_id` 建议格式:

```text
r001_seed0_budget3_3rfm_<configHash8>
```

## Required Outputs

每个 run 至少产出:

```text
outputs/<experiment_id>/diffsbdd/<run_id>/
  captured_outputs/
  processed/normalized_samples/
  logs/
  manifests/
  evaluator/
  summaries/
  run_metadata.json
  samples.jsonl
  output_manifest.json
  stage_attrition.json
```

其中 `run_metadata.json`, `samples.jsonl`, `output_manifest.json`, `stage_attrition.json` 必须写入 `schema_version` 和 `schema_path`。即使没有合法 SDF, 也要保留 sample metadata 行, 不能只按 SDF 文件数推断 denominator。

至少记录:

```text
N_budget
N_raw_attempt_metadata
N_raw_captured
N_final
N_missing_output
N_pipeline_failure
N_tool_failure
N_not_evaluable_by_reason
```

## Evaluator And Diagnosis Boundary

MVP evaluator 只做 sanity wiring:

```text
RDKit
-> PoseBusters mol,dock
-> optional PLIP
-> optional Vina
-> evaluability mapper
```

要求:

- PoseBusters MVP 主配置只用 `mol` 和 `dock`, 不用 `redock`。
- PLIP/Vina 可用才跑, 不可用时记录 `tool_unavailable`。
- Vina score 只能作为辅助 metric, 不能单独定义 success/failure。
- analysis-frozen gate 前不生成正式 `labels.jsonl` / `label_summary.json`。
- summary 只使用 `coverage`, `evaluability count`, `tool error count`, `stage attrition`, `pilot/sanity diagnosis` 等措辞。

## Verification

完成本轮后至少验证:

1. 目录验证: `experiments/<experiment_id>/` 与 `outputs/<experiment_id>/` 一一对应, 输出不散落到旧公共路径。
2. 资源验证: DiffSBDD 有 resource check 记录, license/checkpoint/data/source/sha256/access 状态明确。
3. 环境验证: DiffSBDD inference 环境与 `pfr-eval-tools` evaluator 环境分离, 版本和路径可追溯。
4. Metadata 验证: `run_metadata.json`, `samples.jsonl`, `output_manifest.json`, `stage_attrition.json` 存在且字段完整。
5. Denominator 验证: attempt, captured, final, missing, tool failure, pipeline failure 均可从 JSON/JSONL 回溯。
6. Output capture 验证: raw captured outputs 保留原样, normalized 文件回指 raw sha256。
7. Evaluator 验证: RDKit 和 PoseBusters `mol,dock` 至少完成 wiring 或明确记录 tool failure。
8. Claim 验证: 不写 formal prevalence, official reproduction, repair benchmark result 或 field-wide conclusion。

## Reporting

阶段完成后追加 `docs/EXPERIMENT_LOG.md`, 并按需要更新 `docs/STATUS.md`。若形成报告, 建议路径:

```text
docs/report/YYYYMMDD-<num>-diffsbdd-single-method-third-party-audit-mvp-report.md
```

报告只写 DiffSBDD 单方法 MVP sanity 结论, 不与 DiffLinker 或其他第三方方法比较。
