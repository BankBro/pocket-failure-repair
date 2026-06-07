# 第三方 Failure Audit MVP 小规模实验规划

> 计划落地目标文档: `docs/plan/20260604-02-third-party-audit-mvp-output-capture-plan.md`

## Context

本计划基于 `docs/plan/20260604-01-third-party-failure-audit-mvp-trial-boundary-plan.md` 制定, 目标是启动第一轮 MVP / sanity wiring / small-scale output-capture trial。当前阶段只验证第三方方法环境、最小 inference、输出捕获、provenance metadata 和 evaluator/diagnosis 链路是否跑通, 不产出正式 failure prevalence, 不产出 repair benchmark 结论。

本轮默认覆盖两个方法:

- DiffSBDD: SBDD / de novo 或 inpainting output-capture sanity。
- DiffLinker: linker / stage-limited output-capture sanity, 必须单独解释, 不与 DiffSBDD 合并为 raw SBDD failure prevalence。

## Recommended approach

### 1. 固定实验身份和目录

建议本次使用:

```text
experiment_name = third-party-audit-mvp-output-capture
experiment_id = 20260604-01-third-party-audit-mvp-output-capture
```

正式执行前先确认 `experiments/` 下没有同日冲突编号。实验资产和输出严格对应:

```text
experiments/<experiment_id>/
outputs/<experiment_id>/
outputs/<experiment_id>/<method>/<run_id>/
```

建议创建实验资产结构:

```text
experiments/<experiment_id>/
  README.md
  command.sh
  configs/
    project/
    audit/
    method/<method>/
    resolved/<method>/
  env/
  metadata/
    experiment_manifest.json
    run_metadata.jsonl
    method_resource_check.jsonl
    blockers.jsonl
    negative_results.jsonl
  scripts/
  notes.md
```

建议 run 级输出结构:

```text
outputs/<experiment_id>/<method>/<run_id>/
  captured_outputs/
  processed/
    normalized_samples/
  logs/
  manifests/
  evaluator/
  summaries/
  metrics/
  work/
  run_metadata.json
  samples.jsonl
  output_manifest.json
  stage_attrition.json
```

`run_id` 建议格式:

```text
r<NNN>_seed<seed>_budget<n>_<case>_<configHash8>
```

`sample_id` 必须全局唯一, 建议包含 `experiment_id`, `run_id`, `method`, `dataset_view_id`, `complex_id`, `stage`, `sample_index`。

### 2. 先做 go/no-go 预检查

在任何 inference 前完成以下检查, 并写入 `experiments/<experiment_id>/metadata/method_resource_check.jsonl`:

- repo URL, commit, code license。
- checkpoint source, license/terms, size, sha256, access type。
- example input / dataset source, license, checksum。
- training_data_status 和 leakage_check_status。
- 是否需要 gated access, 登录, 付费, 联系作者, 非官方镜像或未知大小下载。
- 是否超过 resource budget。
- 是否需要改 sampling, decoding, filtering, reranking, docking config, success definition 或 candidate budget。

默认 resource budget:

```text
max_download_per_method_gb = 10
max_storage_per_method_gb = 30
max_env_setup_wallclock_hours_per_method = 4
max_minimal_inference_trial_wallclock_hours_per_method = 8
max_gpu_hours_per_method_for_mvp = 24
max_cpu_hours_per_method_for_mvp = 24
max_checkpoint_count_per_method_for_mvp = 1
```

若资源受限、license 不清、大小未知可能超预算、checksum 不匹配、需要非官方来源或需要改算法, 立即记录 blocker 并暂停。

### 3. 环境规划

第三方推理环境与 evaluator 环境分离:

```text
pfr-diffsbdd      # DiffSBDD inference
pfr-difflinker    # DiffLinker inference
pfr-eval-tools    # RDKit, PoseBusters, PLIP, OpenBabel, Meeko, Vina 等 evaluator
```

每个环境至少记录:

- Python 版本。
- CUDA / driver / GPU。
- PyTorch, PyTorch Lightning, PyG。
- RDKit, OpenBabel, Bio/PDB 等方法依赖。
- PoseBusters, PLIP, Vina, Meeko 等 evaluator 版本和 CLI path。
- `conda_export.yml`, `pip_freeze.txt`, `env_info.json`。

执行前需确认 `pfr-eval-tools` 的实际 conda prefix / CLI path, 并写入 metadata。正式 PLIP/Vina provenance 必须与项目文档中的 evaluator 环境要求对齐。

### 4. DiffSBDD 最小 trial

首轮只跑官方最小 example:

```text
method = diffsbdd
case = 3rfm
seed = 0
n_samples = 3
```

若 `n_samples=3` 的输出捕获、metadata、logs 和 runtime 均正常, 再考虑扩到 `n_samples=5` 或 `10`, 或增加第二个官方 example。若官方 example 默认更小, 采用官方更小配置。

关键要求:

- 不假设 checkpoint/data 已可用, 先核查官方来源。
- 若从官方完整设置缩小到 MVP budget, 标注为 budget-reduced MVP sanity, 不称完整原协议复现。
- wrapper 只能做命令封装、stdout/stderr 捕获、manifest、metadata、checksums 和 missing rows, 不改模型逻辑或采样规则。
- `run_boundary_label` 按实际条件判定, 只有官方资源、未改算法、仅 logging/output capture 时才可写 `instrumented_reproduction`。

### 5. DiffLinker 最小 trial

首轮只跑官方 HSP90 case-study:

```text
method = difflinker
case = hsp90
seed = 0
n_samples = 3
anchors = 1,2
linker_size = 5
```

成功后最多扩到 `n_samples=10`。

关键要求:

- 明确 `task_type=linker`。
- 明确 `audit_scope=stage_limited_or_linker_only`。
- 默认 `raw_prevalence_eligible=false` 或 `pending_raw_lineage_proof`。
- 不与 DiffSBDD 合并为 raw SBDD failure prevalence。
- 若 anchors, linker_size 或输入需要修改才能跑通, 必须降级为 adapted / stage-limited, 不称忠实复现。

### 6. Metadata 和 denominator

每个 run 至少产出:

- `run_metadata.json`
- `samples.jsonl`
- `output_manifest.json`
- `stage_attrition.json`
- stdout/stderr logs
- raw / normalized 文件 manifest
- tool_failure / pipeline_failure / not_evaluable 记录

`samples.jsonl` 最低字段:

```text
sample_id
experiment_id
run_id
method
method_repo
method_commit
run_boundary_label
dataset_name
dataset_version
dataset_view_id
split_id
complex_id
pdb_id
pocket_id
stage
sample_role
sample_index
molecule_path
pose_path
receptor_path
raw_sample_id
raw_sha256
normalized_sha256
original_status
audit_labels
quality_flags
created_by_script_commit
```

计数必须来自 metadata JSONL, 不得只从 SDF 文件数推断。至少记录:

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

即使没有合法 SDF, 也要保留 sample metadata 行。

### 7. Evaluator / diagnosis wiring

MVP evaluator 只做 sanity / wiring pilot:

```text
RDKit
-> PoseBusters mol
-> PoseBusters dock
-> optional PLIP
-> optional Vina
-> evaluability mapper
```

要求:

- PoseBusters MVP 主配置只用 `mol` 和 `dock`, 不用 `redock`。
- PLIP/Vina 可用才跑。
- Vina score 只能作为辅助 metric, 不能单独定义 success/failure。
- 每个样本都保留 evaluator 记录, 包括 missing input, invalid SDF, parser failure, tool unavailable, timeout, command failure。
- analysis-frozen gate 前不生成正式 `labels.jsonl` / `label_summary.json`, 只生成 `evaluator/diagnosis_sanity.jsonl` 或 `evaluator/tool_results.jsonl`。

输出 summary 只使用以下措辞:

```text
coverage
evaluability count
tool error count
stage attrition
pilot/sanity diagnosis
```

不使用 formal prevalence wording。

### 8. 可复用路径和现有资产

执行前优先核查并复用以下项目资产:

- `experiments/20260603-01-third-party-failure-audit-mvp/configs/resolved/third_party/diffsbdd_audit_protocol.yaml`
- `experiments/20260603-01-third-party-failure-audit-mvp/configs/resolved/third_party/difflinker_audit_protocol.yaml`
- `configs/audit/diagnosis_label_config_v0_1.yaml`
- `configs/audit/tool_versions.lock`
- `schemas/third_party_audit/run/run_metadata_v0_1.json`
- `schemas/third_party_audit/samples/failure_sample_metadata_v0_1.json`
- `scripts/third_party/run_diffsbdd_instrumented.py`
- `scripts/third_party/run_difflinker_instrumented.py`
- `scripts/eval/eval_official_tools.py`
- `scripts/eval/eval_posebusters_one.py`

若现有 evaluator 脚本默认使用 PoseBusters `redock`, 本次 MVP 不直接沿用该默认行为。应改为可配置 `mol,dock` 或新建 audit 专用 wrapper。

### 9. 文档维护

阶段开始、阶段完成、关键 artifact 生成、重要 blocker 出现或解除时:

- 更新 `docs/STATUS.md` 的当前快照。
- 追加 `docs/EXPERIMENT_LOG.md` 的完整历史记录。

若完成后新建报告, 建议路径:

```text
docs/report/YYYYMMDD-<num>-third-party-audit-mvp-output-capture-report.md
```

报告必须分开写 DiffSBDD 和 DiffLinker, 并明确 claim boundary。

## Critical files to create or modify during implementation

预计会创建:

- `experiments/20260604-01-third-party-audit-mvp-output-capture/README.md`
- `experiments/20260604-01-third-party-audit-mvp-output-capture/command.sh`
- `experiments/20260604-01-third-party-audit-mvp-output-capture/configs/**`
- `experiments/20260604-01-third-party-audit-mvp-output-capture/env/**`
- `experiments/20260604-01-third-party-audit-mvp-output-capture/metadata/**`
- `outputs/20260604-01-third-party-audit-mvp-output-capture/<method>/<run_id>/**`

可能会修改或新增:

- `scripts/third_party/run_diffsbdd_instrumented.py`
- `scripts/third_party/run_difflinker_instrumented.py`
- `scripts/audit/run_evaluator_diagnosis_mvp.py` 或现有 evaluator wrapper
- `docs/STATUS.md`
- `docs/EXPERIMENT_LOG.md`

如发现既有 wrapper/config/schema 不存在或与 MVP 边界不一致, 优先新建实验专用轻量 wrapper 到 `experiments/<experiment_id>/scripts/`, 待复用稳定后再提升到根目录 `scripts/`。

## Verification

实施时按以下顺序验证:

1. 目录验证: `experiments/<experiment_id>/` 与 `outputs/<experiment_id>/` 一一对应, method/run 输出不散落到旧公共路径。
2. 资源验证: 每个方法有 resource check 记录, license/checkpoint/data/source/sha256/access 状态明确。
3. 环境验证: `pfr-diffsbdd`, `pfr-difflinker`, `pfr-eval-tools` 均有版本和路径记录。
4. Metadata 验证: `run_metadata.json`, `samples.jsonl`, `output_manifest.json`, `stage_attrition.json` 存在且关键字段完整。
5. Denominator 验证: `N_budget`, `N_raw_attempt_metadata`, `N_raw_captured`, `N_final`, not_evaluable/tool_failure/pipeline_failure 均可从 JSONL 回溯。
6. Output capture 验证: raw 文件保留原样, normalized 文件回指 raw sha256, stdout/stderr 未缺失。
7. Evaluator 验证: RDKit 和 PoseBusters `mol,dock` 至少完成 wiring 或明确记录 tool failure; PLIP/Vina 若不可用, 保留 unavailable 记录。
8. Claim 验证: summary 和日志中只写 MVP sanity / coverage / evaluability / attrition, 不写 formal prevalence, official reproduction, repair benchmark result 或 field-wide conclusion。
9. 文档验证: 阶段完成后 `docs/EXPERIMENT_LOG.md` 有追加记录, `docs/STATUS.md` 只保留当前关键快照。

## Stop conditions

遇到以下任一情况暂停并记录, 不自动绕过:

- 需要申请、登录、付费、联系作者或 gated access。
- 资源大小未知且可能超预算。
- license 或 redistribution 权限不清。
- 需要非官方镜像、非官方数据源或不可信 checkpoint。
- checkpoint checksum 不匹配。
- 需要替换核心数据集、checkpoint 或官方资源来源。
- 需要修改 sampling, decoding, filtering, reranking, docking config, success definition 或 candidate budget。
- 单方法下载、存储或运行成本超过 resource budget。
- checkpoint training data unknown, 但准备作为 clean no-leakage 主结论证据。

## Disallowed claims

本 MVP trial 不允许声称:

- formal failure prevalence。
- field-wide true failure distribution。
- official/original protocol reproduction 或原论文性能复现。
- repair benchmark result。
- repair success。
- DiffSBDD 与 DiffLinker 的合并 raw SBDD failure distribution。
- 只基于 Vina score 的 success/failure。
- BIBM 主张证据。

允许的结论只限于:

- 环境是否能搭建。
- 小规模 inference 是否能产出。
- 输出捕获和 metadata 是否完整。
- evaluator wiring 是否跑通。
- 哪些 resource, license, data, checkpoint, tool 或 protocol 问题阻塞下一阶段。
