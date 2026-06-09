# PoseBusters internal_energy 条件冻结规则 v0.2 计划

日期: 2026-06-09

状态: planned

关联文档:

- `docs/plan/20260608-03-unified-evaluation-pipeline-alignment-plan.md`
- `docs/report/20260608-03-unified-evaluation-pipeline-alignment-report.md`

## 背景

在 DiffSBDD 当前统一评估流水线试运行中, PoseBusters `mol` 配置下的 `internal_energy` 在两个样本上没有返回布尔值. 当前 v0.1 gate 把它表达为 `missing_frozen_column:internal_energy`, 进而把样本标成 `tool_failure`.

后续复核显示, 这个表达过于粗糙. PoseBusters 原始 full report 中并不是没有 `internal_energy` 这一列, 而是该列值为 `NaN`. 直接原因是 PoseBusters 的 energy ratio 模块无法为对应分子生成参考构象 ensemble, 典型日志为:

```text
Failed to generate conformations.
```

因此, 当前问题不是 PoseBusters 整体不可用, 也不是样本文件完全坏掉, 而是:

- 样本可由 RDKit 读取, sanitize 通过, 化学图大体可解析.
- 样本存在独立的三维局部几何异常证据, 例如 `bond_lengths=false` 或 `bond_angles=false`.
- `internal_energy=NaN` 本身表示该 PoseBusters 子检查项不可判定, 不能直接解释为通过或失败.
- 当前 wrapper / gate 缺少“列存在但不可判定”的表达层, 所以误写成 frozen column 缺失.

本计划定义 v0.2 规则, 用于修正 `internal_energy=NaN` 的状态表达, 同时保持 v0.1 历史解释不漂移.

## 目标

1. 不修改 PoseBusters 官方核心逻辑.
2. 不静默改变 v0.1 冻结规则语义, 而是新增 v0.2 evaluator / gate / label 配置.
3. 区分三种状态:
   - frozen column 真缺失.
   - frozen column 返回 `false`.
   - conditional column 存在但不可判定.
4. 不把 `internal_energy=NaN` 当作 pass, 也不把它直接当作 failure.
5. 保留 `internal_energy=false` 作为高内部能量证据.
6. 对 `internal_energy=NaN` 建立运行级 coverage 统计和 coverage gate.
7. 让当前 `sample_011` 和 `sample_016` 从 `tool_failure` 更正为可评价的 `local_geometry_failure`, 并保留 `internal_energy_unavailable` 诊断.

## 非目标

- 不重新定义 PoseBusters 原始指标.
- 不修改 RDKit / ETKDG / UFF 参数来强行让 `internal_energy` 给出布尔值.
- 不把当前 selected-output residual view 解释为正式 failure prevalence.
- 不声明 DiffSBDD 方法总体失败率.
- 不把 `internal_energy=NaN` 单独解释为分子失败.

## v0.2 核心规则

### 1. PoseBusters ligand core 列分层

`posebusters_ligand_core` 继续使用:

```text
config = mol
```

v0.2 将列分为 required columns 和 conditional columns.

required columns:

```text
mol_pred_loaded
sanitization
inchi_convertible
all_atoms_connected
no_radicals
bond_lengths
bond_angles
internal_steric_clash
aromatic_ring_flatness
non-aromatic_ring_non-flatness
double_bond_flatness
```

conditional columns:

```text
internal_energy
```

### 2. `internal_energy` 判定规则

| 原始状态 | v0.2 解释 | 样本级状态 | gate 行为 |
|---|---|---|---|
| `internal_energy=true` | 已判定且通过 | 不触发失败 | 不阻塞 |
| `internal_energy=false` | 已判定且失败 | `local_geometry_failure`, 附加 `high_internal_energy_evidence` | 不作为工具失败阻塞 |
| `internal_energy=NaN/null`, 且满足 unavailable 条件 | 条件列不可判定 | 不作为 pass/fail, 附加 `posebusters_internal_energy_unavailable` | coverage warning, 按阈值决定是否阻塞 |
| 原始 full report 中 `internal_energy` 真的缺失 | 冻结列缺失或配置漂移 | `tool_failure` | gate blocker |
| PoseBusters 整体报错, 超时, wrapper nonzero | 工具失败 | `tool_failure` | gate blocker |

### 3. 允许 `internal_energy_unavailable` 的条件

只有同时满足以下条件时, 才允许把 `internal_energy=NaN/null` 归为 `posebusters_internal_energy_unavailable`:

1. PoseBusters 进程无整体异常.
2. wrapper 保存了 PoseBusters full report 的原始列名和值.
3. 原始 full report 中 `internal_energy` 列存在.
4. `mol_pred_loaded=true`.
5. `sanitization=true`.
6. `inchi_convertible=true`.
7. `energy_ratio` 和 `ensemble_avg_energy` 等 energy ratio 相关列存在.
8. `internal_energy` 是非布尔不可判定值, 例如 `NaN`, `pd.NA`, 或 JSON-safe 后的 `null`.

原因字段按证据强度记录:

- 如果 stderr 或 raw report 明确包含 `Failed to generate conformations.`, 记录 `energy_ratio_conformer_ensemble_unavailable`.
- 如果只能确认 energy ratio 相关列不可判定, 记录 `energy_ratio_unavailable`.
- 如果缺少 full report 原始证据, 不允许归为 unavailable, 应按 gate blocker 处理.

### 4. coverage gate

v0.2 必须统计:

```text
internal_energy_false_count
internal_energy_unavailable_count
internal_energy_unavailable_fraction
internal_energy_unavailable_sample_ids
```

推荐阈值:

| 阶段 | 阈值 | gate 行为 |
|---|---:|---|
| MVP sanity / 小样本接线验证 | `internal_energy_unavailable_fraction <= 10%` | `passed_with_warnings` |
| MVP sanity / 小样本接线验证 | `internal_energy_unavailable_fraction > 10%` | `failed` 或降级为仅接线证据 |
| 后续 formal analysis | `internal_energy_unavailable_fraction <= 5%` | `passed_with_warnings` |
| 后续 formal analysis | `internal_energy_unavailable_fraction > 5%` | `failed` 或必须降级解释 |

`passed_with_warnings` 只表示 required evaluator wiring 和 required frozen columns 可用, 但 conditional column 存在覆盖缺口. 它不表示 PoseBusters 全部评估项都完整通过.

### 5. 边界样本

如果 `internal_energy=NaN/null`, 且其他 required core 几何列也失败, 样本按对应核心失败标注, `internal_energy_unavailable` 只作为附加诊断.

示例:

```text
bond_lengths=false
internal_energy=null
```

应标为:

```text
evaluability_status = evaluable
primary_label = local_geometry_failure
secondary/evidence = posebusters_internal_energy_unavailable
```

如果 `internal_energy=NaN/null`, 但其他 required core columns 全部通过, 样本不能称为 clean pass. 推荐标记为:

```text
no_core_failure_detected_with_energy_unavailable
```

该状态不进入 failure count, 也不进入 clean-pass count, 应作为 coverage-limited / unknown evidence 处理.

## 当前 run 的重新解释

当前涉及两个样本:

```text
sample_011
sample_016
```

v0.1 表达:

```text
tool_failure
missing_frozen_column:internal_energy
```

v0.2 推荐表达:

| 样本 | v0.2 primary label | 主证据 | 附加诊断 |
|---|---|---|---|
| `sample_011` | `local_geometry_failure` | `bond_lengths=false` | `posebusters_internal_energy_unavailable` |
| `sample_016` | `local_geometry_failure` | `bond_lengths=false`, `bond_angles=false` | `posebusters_internal_energy_unavailable` |

解释边界:

- 这两个样本不是 SDF 文件坏掉.
- 这两个样本不是 PoseBusters 整体失败.
- 这两个样本有局部三维几何异常.
- `internal_energy=NaN` 不是 failure 证据, 只是该 energy ratio 子项不可判定.

## 需要新增或修改的文件

### 配置

新增:

```text
configs/audit/evaluator_policy_v0_2.yaml
configs/audit/analysis_frozen_gate_v0_2.yaml
configs/audit/diagnosis_label_config_v0_3.yaml
```

新增对应 schema:

```text
schemas/configs/audit/evaluator_policy_v0_2.json
schemas/configs/audit/analysis_frozen_gate_v0_2.json
schemas/configs/audit/diagnosis_label_config_v0_3.json
```

v0.1 文件不静默改义.

### wrapper 和 evaluator

修改:

```text
scripts/eval/eval_posebusters_one.py
scripts/eval/run_audit_evaluators.py
scripts/eval/build_audit_labels.py
scripts/eval/check_analysis_frozen_gate.py
```

`eval_posebusters_one.py` 需要新增 JSON-safe 原始报告字段:

```text
posebusters_report_values
posebusters_non_boolean_checks
posebusters_unavailable_columns
posebusters_unavailable_reasons
```

JSON-safe 转换必须覆盖:

- `NaN` -> `null`.
- `inf` / `-inf` -> `null`.
- `pd.NA` -> `null`.
- `numpy.bool_` -> Python `bool`.
- `numpy.integer` -> Python `int`.
- `numpy.floating` -> Python `float` 或 `null`.

`run_audit_evaluators.py` 需要输出规范化字段:

```text
posebusters_ligand_core_pass_required_columns
posebusters_ligand_core_pass_conditional_columns
posebusters_ligand_core_pass_failed_columns
posebusters_ligand_core_pass_missing_columns
posebusters_ligand_core_pass_unavailable_columns
posebusters_ligand_core_pass_unavailable_reasons
posebusters_ligand_core_required_pass
posebusters_ligand_core_conditional_coverage_pass
```

`build_audit_labels.py` 不应直接从 raw PoseBusters full report 猜测标签, 应优先消费 evaluator 规范化后的 failed / missing / unavailable 字段.

`check_analysis_frozen_gate.py` 需要:

- 真缺 required column 时阻塞.
- 允许的 conditional unavailable 不阻塞, 但写入 warning 和 coverage summary.
- 超过 coverage 阈值时按阶段配置阻塞或降级.

## 测试计划

至少新增以下单元测试:

1. `internal_energy=NaN`, 原始列存在且满足 unavailable 条件: formal status 不是 `tool_failure`, `missing_columns=[]`, `unavailable_columns=["internal_energy"]`.
2. `internal_energy=false`: formal status 为 `failed`, failed columns 包含 `internal_energy`, label 进入 `local_geometry_failure`, evidence 包含 `high_internal_energy_evidence`.
3. 原始 full report 中 `internal_energy` 真缺失: 仍为 `tool_failure` 和 gate blocker.
4. `bond_lengths=false + internal_energy=NaN`: label 为 `evaluable + local_geometry_failure`, evidence 包含 `posebusters_internal_energy_unavailable`.
5. 只有 `internal_energy=NaN`, 其他 required columns 全通过: 不标为 `local_geometry_failure`, 不标为 clean pass, evidence 包含 `no_core_failure_detected_with_energy_unavailable`.
6. gate 对 `internal_energy_unavailable_fraction <= MVP threshold`: `passed_with_warnings`.
7. gate 对 `internal_energy_unavailable_fraction > MVP threshold`: `failed` 或按配置降级.
8. v0.1 回归: 旧 `frozen_columns` 配置行为不变, 真缺列仍失败.
9. JSON-safe 转换: `np.nan`, `pd.NA`, `np.bool_`, `np.float64`, `inf` 均能写出合法 JSON.

回归命令:

```bash
conda run -n pfr env PYTHONPATH=src pytest -q
```

## 重新运行计划

实现 v0.2 后, 对当前 DiffSBDD 统一评估 run 重新生成:

```text
evaluator/evaluator_tool_results.jsonl
labels.jsonl
summaries/label_summary.json
summaries/prevalence_summary.json
summaries/analysis_frozen_gate_result.json
output_manifest.json
```

推荐新 run 或新 rerun 标识包含:

```text
evaluator_policy_v0_2
analysis_frozen_gate_v0_2
diagnosis_label_config_v0_3
```

若复用同一输出目录, 必须保留旧结果备份或明确记录 rerun provenance. 更推荐新建 run_id, 避免 v0.1 和 v0.2 结果混在一起.

## 报告产物

落地本计划后必须生成对应 report 文档, 放入:

```text
docs/report/YYYYMMDD-<num>-posebusters-internal-energy-conditional-gate-report.md
```

其中 `YYYYMMDD-<num>` 按报告生成当天的 `docs/report/` 命名顺序确定. report 至少应覆盖:

1. 本次 v0.2 修改动机: `internal_energy=NaN` 是列存在但不可判定, 不是 frozen column 真缺失.
2. 实际改动清单: config, schema, wrapper, evaluator, label, gate, tests.
3. 与 v0.1 的语义差异: v0.1 保守 gate failed, v0.2 区分 unavailable 后按 coverage gate 处理.
4. 当前 run 重新评估结果: gate status, blocker, warning, affected sample ids.
5. 当前 `sample_011` 和 `sample_016` 的新标签解释.
6. `internal_energy_false_count`, `internal_energy_unavailable_count`, `internal_energy_unavailable_fraction`.
7. 测试命令和结果.
8. claim boundary: 本轮仍是 selected-output residual 分析, 不能解释为正式 failure prevalence.

report 完成后, 应按项目规范追加 `docs/EXPERIMENT_LOG.md`. 如该规则变更影响当前项目快照, 同步更新 `docs/STATUS.md`.

## 报告措辞

报告中可以写:

```text
在 v0.2 评估规则下, analysis-frozen gate 为 passed_with_warnings. warning 仅表示 PoseBusters internal_energy 条件列在部分样本上不可判定, 不表示该项通过或失败. 当前局部几何失败标签来自独立的 bond_lengths 和 bond_angles 证据. 本轮仍是 selected-output residual 分析, 不能解释为正式 failure prevalence.
```

报告中不能写:

- PoseBusters 评估全部通过.
- DiffSBDD 失败率为 `5/20`.
- `internal_energy=NaN` 说明分子失败.
- 当前结果是 formal failure prevalence.

可使用的更保守统计名:

```text
selected-output residual finding count
当前样本集中的 failure-like evidence count
internal_energy unavailable coverage
```

## 验收标准

1. v0.2 配置和 schema 均存在, 且记录 `schema_version` 和 `schema_path`.
2. wrapper 保存 PoseBusters full report JSON-safe 值.
3. evaluator 能区分 missing, failed, unavailable.
4. label 能把当前两个样本解释为 `local_geometry_failure` 加 unavailable 诊断.
5. gate 能输出 `passed_with_warnings`, 且 warning 可追溯到样本 id 和 unavailable reason.
6. coverage summary 同时给出 `internal_energy_false_count` 和 `internal_energy_unavailable_count`.
7. 测试覆盖 v0.1 回归和 v0.2 新语义.
8. 生成对应 report 文档, 并追加 `docs/EXPERIMENT_LOG.md`.
9. `pytest -q` 通过.
