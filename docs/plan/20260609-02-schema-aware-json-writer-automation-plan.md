# 基于 schema 的 JSON 自动填充计划

日期: 2026-06-09

状态: planned

关联文档:

- `docs/plan/20260608-03-unified-evaluation-pipeline-alignment-plan.md`
- `docs/plan/20260609-01-posebusters-internal-energy-conditional-gate-plan.md`
- `docs/report/20260609-01-posebusters-internal-energy-conditional-gate-report.md`

## 背景

当前统一评估流水线已经能生成 `run_metadata.json`, `samples.jsonl`, `evaluator_tool_results.jsonl`, `labels.jsonl`, `stage_attrition.json`, `output_manifest.json` 和多个 summary 文件. 这些文件已经大多包含 `schema_version` 和 `schema_path`, 但很多字段仍由各脚本手写常量或手工拼装.

这会带来几个问题:

- `schema_version` 和 `schema_path` 在脚本里重复维护, 容易与 schema 文件中的 `const` 漂移.
- `metadata_schemas` 映射在多个脚本中重复出现, key 和路径可能不一致.
- `output_manifest.json` 的 sha256 需要在所有输出最终写完后刷新, 否则后续脚本改写文件会让 manifest 过期.
- 人工判断字段和自动事实字段没有统一边界, 后续扩大样本量时容易手改 JSON.
- 人工拍板内容如果散落在报告或脚本参数中, 难以进入机器可读的来源追踪记录.

本计划定义一套基于 schema 的自动写出机制: 人工只编辑少量 schema-covered YAML, 代码负责生成项目自有 JSON / JSONL, 并自动注入 schema refs, hash, path 和来源追踪记录.

## 目标

1. 项目自有 JSON / JSONL 默认由代码生成, 不手工编辑.
2. `schema_version` 和 `schema_path` 从 JSON Schema 的 `const` 自动注入.
3. 人工判断集中写入 schema-covered YAML, 例如 `manual_decisions.yaml`.
4. 输出 JSON / JSONL 只记录人工 YAML 的路径, hash, version 和相关 `decision_id`, 不嵌入整份 YAML.
5. builder 负责业务字段, writer 只负责 schema refs 和轻量结构校验.
6. 逐步迁移统一评估流水线, 先从单行 envelope 输出开始, 再迁移 labels, summaries, gate 和 manifest finalizer.
7. 通过测试保证新输出零缺失 schema refs, 冲突 refs 必须报错, manifest hash 最终一致.

## 非目标

- 不自动重写历史 outputs.
- 不直接改变现有 `write_json()` / `write_jsonl()` 的默认行为.
- 不让 writer 自动猜测科学语义, 例如 `primary_label`, `gate_status`, `claim_boundary`, `training_data_status`.
- 不把第三方工具原生输出强行改成本项目 schema.
- 不把工具结果, 统计计数, pass/fail 或 label 结果写入人工 YAML.
- 不在本计划中声明正式 failure prevalence 或 repair benchmark result.

## 字段责任边界

### 代码自动填充

以下字段原则上不应人工填写:

- schema refs: `schema_version`, `schema_path`.
- 运行事实: `command`, `environment`, `created_time`, `exit_code`, `stdout_path`, `stderr_path`.
- 路径和校验: `molecule_path`, `cleaned_receptor_path`, `normalized_sha256`, `cleaned_receptor_sha256`, `sha256`, `*_hash`.
- 样本身份: `sample_id`, `lineage_id`, `parent_sample_id`, `source_sample_id`, `stage`, `sample_role`.
- 工具原始结果: RDKit, PoseBusters, PLIP, Vina 的 `metrics`, `errors`, `status`, raw report values.
- 冻结规则结果: frozen columns pass/fail, failed columns, unavailable columns.
- 诊断标签: `evaluability_status`, `primary_label`, `secondary_labels`, `near_miss_eligible`.
- 汇总和 gate: `stage_attrition.rows.*`, `label_summary.counts`, `prevalence_summary.prevalence_views`, `gate_status`, `blocking_failures`, `warnings`.
- manifest 字段: artifact path lists, artifact sha256, `n_output_artifacts`.

### 配置驱动填充

以下字段来自冻结配置或 resolved config, 由代码读取后写入输出:

- `evaluator_policy_version`, `evaluator_policy_hash`.
- `label_protocol_version`, `label_config_hash`.
- `denominator_policy_version`, `denominator_policy_hash`.
- `receptor_prep_policy_version`, `receptor_prep_policy_hash`.
- `analysis_frozen_gate_version`, `analysis_frozen_gate_hash`.
- `tool_versions_lock_hash`.
- frozen columns, thresholds, label precedence, denominator views.

### 人工填写或拍板

人工只保留少量真正需要判断的字段, 推荐集中放入 `manual_decisions.yaml`:

- 方法和运行边界: `run_boundary_label`, `algorithm_changed`, 是否接受 protocol deviation.
- 结论边界: `claim_boundary`.
- 数据和泄漏边界: `training_data_status`, `leakage_check_status`, `leakage_report_path`.
- 资源和权限: gated access, license, non-official mirror, paid resource, checkpoint 来源可信度.
- receptor 复核: reference ligand 选择, unknown HETATM 去留, whitelist 更新决定.
- 人工标签复核: `adjudication_status`, `manual_adjudication_id`, override reason, evidence refs.
- denominator membership 的人工例外判断.

## 总体设计

推荐数据流:

```text
resolved YAML configs
+ manual_decisions.yaml
-> load_schema_yaml
-> builder 生成业务字段
-> write_schema_json / write_schema_jsonl 自动注入 schema refs
-> evaluator / label / summary / gate outputs
-> manifest finalizer 最后刷新 output_manifest.json 和 sha256
```

核心原则:

- schema 是格式合同.
- YAML 是人工输入.
- builder 是业务规则执行者.
- writer 是安全写出层.
- output manifest 是最终文件清单和来源追踪索引.

## Phase 1: schema-aware writer

### 新增位置

推荐新增通用模块:

```text
src/pfr/utils/schema_io.py
```

同时在 evaluator 侧保留薄 wrapper:

```text
scripts/eval/audit_common.py
```

这样可以让现有 evaluator 脚本继续从 `audit_common.py` 导入, 同时把核心逻辑放在可复用 package 中.

### 推荐 API

```python
@dataclass(frozen=True)
class SchemaRef:
    schema_version: str
    schema_path: str
    schema_file: Path
    schema: dict[str, Any]

def load_schema_ref(schema_path: str | Path, *, root: Path = ROOT) -> SchemaRef: ...

def with_schema_ref(
    payload: dict[str, Any],
    schema_path: str | Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]: ...

def validate_schema_ref_fields(payload: dict[str, Any], schema_ref: SchemaRef) -> None: ...

def validate_required_fields(payload: dict[str, Any], schema_ref: SchemaRef) -> None: ...

def write_json_with_schema(
    path: str | Path,
    payload: dict[str, Any],
    schema_path: str | Path,
    *,
    validate: str = "light",
) -> Path: ...

def write_jsonl_with_schema(
    path: str | Path,
    rows: Iterable[dict[str, Any]],
    schema_path: str | Path,
    *,
    validate: str = "light",
) -> Path: ...
```

### 自动注入规则

`load_schema_ref()` 只从 schema 文件读取:

```json
"schema_version": {"const": "..."}
"schema_path": {"const": "..."}
```

写出时:

- 如果 payload 没有 `schema_version` / `schema_path`, 自动注入.
- 如果 payload 已有且与 schema const 一致, 保留.
- 如果 payload 已有但与 schema const 冲突, 默认报错.
- 只有显式 `overwrite=True` 时才允许覆盖冲突 refs, 并且测试中应覆盖该行为.

禁止从输出文件名推断 schema version. 调用方必须显式传入 `schema_path` 或 artifact role.

### 校验范围

第一版默认轻量校验:

- schema 文件存在.
- schema 中存在 `schema_version.const` 和 `schema_path.const`.
- `schema_path.const` 等于 schema 文件相对仓库根目录的 POSIX path.
- payload 或 JSONL row 是 object.
- required 字段存在.
- `schema_version` / `schema_path` 与 const 一致.

完整 JSON Schema 校验可以作为后续增强, 不作为 Phase 1 必需项.

## Phase 2: 人工 YAML 配置

### 新增 schema 和模板

新增:

```text
schemas/configs/audit/manual_decisions_v0_1.json
```

单次实验使用 resolved 副本:

```text
experiments/<experiment_id>/configs/resolved/audit/manual_decisions.yaml
```

`configs/` 不放空模板. 若需要示例, 放在本计划、报告或测试 fixture 中; 真实人工决策文件只在具体实验的 resolved config 中保存.

### YAML 字段建议

```yaml
schema_version: config_audit_manual_decisions_v0_1
schema_path: schemas/configs/audit/manual_decisions_v0_1.json

manual_decisions_version: pfr_manual_decisions_v0_1
created_date: "2026-06-09"
updated_time: "2026-06-09T00:00:00Z"
status: draft_ready
purpose: schema-aware JSON automation manual decisions

scope:
  experiment_id: null
  run_id: null
  method: null
  dataset_view_id: null

applies_to_configs:
  evaluator_policy_hash: null
  label_config_hash: null
  receptor_prep_policy_hash: null
  denominator_policy_hash: null
  analysis_frozen_gate_hash: null

decisions:
  - decision_id: md_example_001
    decision_type: claim_boundary
    status: active
    target:
      target_type: run
      run_id: null
    decision: selected_output_residual_audit_not_raw_failure_prevalence
    reason: selected-output residual audit cannot support raw failure prevalence claim.
    evidence_refs: []
    made_by: human_reviewer
    made_time: "2026-06-09T00:00:00Z"
    supersedes: null
    risk_note: null
```

### 输出中的来源追踪字段

受 manual decisions 影响的 JSON / JSONL 应记录轻量来源追踪字段:

```json
{
  "manual_decisions_path": "experiments/.../configs/resolved/audit/manual_decisions.yaml",
  "manual_decisions_schema_version": "config_audit_manual_decisions_v0_1",
  "manual_decisions_schema_path": "schemas/configs/audit/manual_decisions_v0_1.json",
  "manual_decisions_version": "pfr_manual_decisions_v0_1",
  "manual_decisions_hash": "sha256:...",
  "manual_decisions_status": "frozen",
  "manual_decision_ids": ["md_001"],
  "manual_decisions_validation_status": "passed"
}
```

落点:

- `run_metadata.json`: 记录整次 run 使用的 manual YAML path, version, hash 和 active decision ids.
- `samples.jsonl`: 只在样本级人工决策影响该样本时记录 `manual_decision_ids`.
- `receptor_prep_record.json`: 记录 reference ligand 和 HETATM 复核相关 `manual_decision_ids`.
- `labels.jsonl`: 对人工 adjudication 或 override 记录 `manual_decision_ids`.
- `analysis_frozen_gate_result.json`: 在 `config_hashes` 或相邻字段记录 `manual_decisions_hash`, 在 `checked_inputs` 记录 manual decisions 文件和 active decision 数量.
- `output_manifest.json`: 在 manifest 的 config inputs 或 sha256 清单中记录 manual decisions YAML, 不把它放进 `metadata_schemas`.

## Phase 3: 小范围迁移

优先迁移单行或单 payload builder, 不改变业务语义:

1. `scripts/eval/eval_posebusters_one.py`
   - `evaluator/raw_tool_outputs/posebusters_*.json`.
   - 由 `write_json_with_schema(..., posebusters_raw_result_v0_1.json)` 写出.

2. `scripts/eval/run_audit_evaluators.py`
   - `evaluator_input_row()`.
   - `tool_row()`.
   - 写出 `evaluator_input.jsonl` 和 `evaluator_tool_results.jsonl` 时自动注入 schema refs.

3. `scripts/eval/build_audit_labels.py`
   - `labels.jsonl`.
   - 保留现有 label 规则, 只迁移 envelope 写出.

4. `scripts/eval/summarize_audit_labels.py`
   - `label_summary.json`.
   - `prevalence_summary.json`.

5. `scripts/eval/check_analysis_frozen_gate.py`
   - `analysis_frozen_gate_result.json`.

暂缓迁移:

- `run_metadata.json`: 同名文件覆盖不同运行边界, 先不做统一 builder.
- `samples.jsonl`: DiffSBDD capture 和 unified evaluator 的语义不同, 先保留各自 builder.
- `stage_attrition.json`: 存在 pre-evaluator, post-evaluator, post-label 多种口径, 先不统一.
- `output_manifest.json`: 先设计 finalizer, 再迁移.
- `summaries/frozen_evaluator_summary.json`: 现有 schema 和 claim boundary 可能不一致, 需先决定新 schema 或 summary 类型.

## Phase 4: manifest finalizer

新增 manifest finalizer, 在所有输出写完后执行:

```text
labels.jsonl
summaries/*.json
stage_attrition.json
evaluator/*.jsonl
raw_tool_outputs/*.json
processed/*
-> finalize_output_manifest()
-> output_manifest.json
```

finalizer 负责:

- 收集 captured, processed, evaluator, summary, manifest 文件.
- 计算每个 artifact 的 sha256.
- 统一写 `metadata_schemas` canonical key.
- 写 `n_output_artifacts`.
- 检查 manifest 中记录的文件均存在.
- 检查 manifest 生成后没有后续脚本再改写受记录文件.

如果后续脚本必须改写某个文件, 必须重新运行 finalizer.

## 测试计划

新增或扩展测试:

1. writer guard 测试
   - payload 缺 schema refs 时自动注入.
   - payload refs 一致时通过.
   - payload refs 冲突时报错.
   - writer 不按路径推断 schema version.

2. schema required 测试
   - 缺 required 字段时报错.
   - schema 文件缺少 `schema_version.const` 或 `schema_path.const` 时报错.

3. JSONL writer 测试
   - 每一行都自动注入 schema refs.
   - 某一行 required 缺失时整体失败, 不写半截输出.

4. manual decisions YAML 测试
   - `schemas/configs/audit/manual_decisions_v0_1.json` 的 schema refs 自洽.
   - required 字段完整.
   - `decision_type`, `status`, `target_type` 定义枚举.

5. 统一评估流水线最小 tmp-run 测试
   - 不运行外部工具.
   - 用纯函数生成最小 evaluator input, tool result, label, summary 和 gate result.
   - 检查 schema refs, required 字段和跨文件 run_id / sample_id 一致性.

6. manifest finalizer 测试
   - manifest sha256 等于最终文件内容.
   - `n_output_artifacts == len(sha256)`.
   - canonical `metadata_schemas` key 无漂移.

## 验收标准

Phase 1 完成时:

- 新增 schema-aware writer.
- 现有 `write_json()` / `write_jsonl()` 行为不变.
- writer 单元测试通过.
- `pytest -q` 通过.

Phase 2 完成时:

- 新增 `manual_decisions_v0_1` schema.
- config schema refs 测试通过.
- 文档说明人工 YAML 只放人工决策, 不放自动事实或工具结果.

Phase 3 完成时:

- 新生成的 PoseBusters raw wrapper, evaluator input, evaluator tool result, labels, summaries, gate result 均通过 schema-aware writer 写出.
- 这些输出不再手写 `schema_version` / `schema_path` 双常量.
- 业务标签和 gate 结果与迁移前保持一致.

Phase 4 完成时:

- `output_manifest.json` 最后统一生成或刷新.
- manifest sha256 与最终文件内容一致.
- 新实验输出没有缺失 schema refs 的项目自有 JSON / JSONL.

## 风险和缓解

| 风险 | 缓解 |
|---|---|
| writer 自动填错语义字段 | writer 只填 schema refs, 语义字段由 builder 或 YAML 显式传入 |
| 历史 outputs 暴露大量 schema 缺失 | 不重写历史输出, 用 legacy allowlist 或只对新实验启用严格检查 |
| manifest hash 被后续改写破坏 | 所有生成步骤结束后运行 finalizer, finalizer 后不再改写受记录文件 |
| `run_metadata` 等同名文件语义混用 | 暂不做一刀切统一 builder, 保留按阶段专用 builder |
| YAML 变成隐藏的结果编辑入口 | schema 限制人工 YAML 只包含 decision, reason 和 evidence refs |
| 完整 JSON Schema 校验引入依赖成本 | Phase 1 先做轻量校验, 后续再评估是否引入完整 validator |

## 预期产物

计划落地后应生成报告:

```text
docs/report/20260609-02-schema-aware-json-writer-automation-report.md
```

报告应记录:

- 实际新增或修改的 schema, YAML, writer 和测试文件.
- 哪些输出已迁移到 schema-aware writer.
- 哪些输出暂缓迁移及原因.
- manual decisions YAML 是否已接入.
- manifest finalizer 是否已实现.
- pytest 结果.
- 剩余风险和下一步.
