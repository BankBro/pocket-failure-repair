# schemas

`schemas/` 保存项目中结构化 metadata / config 的字段规范。schema 文件本身使用 JSON Schema; 被约束的实例可以是 JSON、JSONL 或 YAML。它不是实验数据目录, 也不保存运行结果; 它定义 metadata 或配置文件应该有哪些字段、字段类型是什么、哪些字段必须存在。

## 主要用途

- 给生成 metadata 的脚本和 wrapper 使用, 确保写出的 `run_metadata.json`, `samples.jsonl`, `stage_attrition.json`, `labels.jsonl` 等文件格式稳定。生成的 JSON / JSONL 应写入 `schema_version` 和 `schema_path`, 明确声明自己遵循哪个 schema。
- 给 validator / evaluator / analysis 脚本使用, 在批量读取前检查字段是否完整、口径是否一致。
- 给人和协作 agent 使用, 作为审阅 metadata、写报告和扩展审计流程时的字段合同。

## 当前结构

```text
schemas/
  third_party_audit/
    run/
      run_metadata_v0_1.json
      output_manifest_v0_1.json
    samples/
      failure_sample_metadata_v0_1.json
    diagnosis/
      evaluator_input_v0_1.json
      label_v0_1.json
      evaluator_tool_result_v0_1.json
      posebusters_raw_result_v0_1.json
      diagnosis_sanity_v0_1.json
      mvp_sanity_summary_v0_1.json
      label_summary_v0_1.json
      prevalence_summary_v0_1.json
      analysis_frozen_gate_result_v0_1.json
    attrition/
      stage_attrition_v0_1.json
    receptor/
      receptor_prep_record_v0_1.json
      receptor_prep_index_v0_1.json
    resources/
      method_resource_check_v0_1.json
      blocker_log_v0_1.json
      environment_info_v0_1.json
      official_protocol_checklist_v0_1.json
  configs/
    audit/
      receptor_prep_policy_v0_1.json
      evaluator_policy_v0_1.json
      evaluator_policy_v0_2.json
      analysis_frozen_gate_v0_1.json
      analysis_frozen_gate_v0_2.json
      diagnosis_label_config_v0_1.json
      diagnosis_label_config_v0_2.json
      diagnosis_label_config_v0_3.json
      denominator_statistics_config_v0_1.json
      resource_budget_config_v0_1.json
      tool_versions_lock_v0_1.json
      manual_decisions_v0_1.json
    data/
      downloads/
        rcsb_download_config_v0_1.json
      builds/
        rgroup_dataset_config_v0_1.json
    third_party/
      method_protocol_config_v0_1.json
  data/
    README.md
    catalog/
      dataset_catalog_v0_1.json
      dataset_layout_migration_v0_1.json
      dataset_raw_reconciliation_v0_1.json
    datasets/
      entries/
        dataset_entry_v0_1.json
      splits/
        dataset_split_v0_1.json
      views/
        dataset_view_v0_1.json
      manifests/
        raw/
          dataset_raw_manifest_v0_1.json
        entries/
          dataset_entries_manifest_v0_1.json
        lineage/
          dataset_lineage_raw_to_entry_v0_1.json
          dataset_lineage_entry_to_raw_v0_1.json
```

## 当前 schema 说明

### third_party_audit

- `third_party_audit/run/run_metadata_v0_1.json`: 第三方方法单次 run 的 metadata 格式, 用于记录 method、run_id、command、checkpoint、commit、tool versions、输出路径等。
- `third_party_audit/run/output_manifest_v0_1.json`: 单次第三方 run 的输出清单格式, 用于记录 captured outputs、logs、sha256 和关联 metadata schema。
- `third_party_audit/samples/failure_sample_metadata_v0_1.json`: 第三方方法逐样本 JSONL metadata 格式, 用于记录样本级输出、结构路径、生成状态和诊断字段。
- `third_party_audit/receptor/receptor_prep_record_v0_1.json`: cleaned receptor 与同名 receptor prep JSON 的字段格式, 用于记录 reference ligand 删除、HETATM 处理、pocket box 和 receptor sha256。
- `third_party_audit/receptor/receptor_prep_index_v0_1.json`: 单次 run 下 receptor prep record 的轻量索引格式。
- `third_party_audit/diagnosis/evaluator_input_v0_1.json`: 统一 evaluator 输入 JSONL 行格式, 用于把样本、cleaned receptor、reference ligand、pocket box 和 policy hash 传给评估工具。
- `third_party_audit/diagnosis/label_v0_1.json`: failure / diagnosis label 的字段格式, 用于统一人工或自动诊断标签。
- `third_party_audit/diagnosis/evaluator_tool_result_v0_1.json`: MVP evaluator 工具逐样本结果 JSONL 行格式。
- `third_party_audit/diagnosis/posebusters_raw_result_v0_1.json`: `eval_posebusters_one.py` 生成的 PoseBusters 单样本 raw wrapper JSON 格式, 用于保存 full report 的 JSON-safe 原始列和值。
- `third_party_audit/diagnosis/diagnosis_sanity_v0_1.json`: analysis-frozen 前 diagnosis sanity / tool wiring 结果 JSONL 行格式, 不用于 formal prevalence。
- `third_party_audit/diagnosis/mvp_sanity_summary_v0_1.json`: MVP sanity 小结 JSON 格式, 只记录 coverage、工具 wiring 和 denominator 摘要, 不用于 formal prevalence。
- `third_party_audit/diagnosis/label_summary_v0_1.json`: frozen-style labels 的逐 run 汇总格式。
- `third_party_audit/diagnosis/prevalence_summary_v0_1.json`: 分母视图和 selected-output residual prevalence 摘要格式。
- `third_party_audit/diagnosis/analysis_frozen_gate_result_v0_1.json`: analysis-frozen gate 机器可读检查结果格式。
- `third_party_audit/attrition/stage_attrition_v0_1.json`: stage attrition 统计格式, 用于记录 `N_budget`, `N_raw_captured`, `N_final`, `N_missing_output`, `N_tool_failure` 等阶段计数。
- `third_party_audit/resources/method_resource_check_v0_1.json`: 第三方方法 inference 前 go/no-go resource check JSONL 行格式。
- `third_party_audit/resources/blocker_log_v0_1.json`: 第三方 audit 中资源、license、环境、数据或协议阻塞记录 JSONL 行格式。
- `third_party_audit/resources/environment_info_v0_1.json`: 第三方方法 inference 或 evaluator 环境快照格式, 用于记录 Python、Conda prefix、核心包版本和 import 错误。
- `third_party_audit/resources/official_protocol_checklist_v0_1.json`: 第三方方法原协议阅读和忠实度 gate 的核对清单格式, 用于记录论文、README、代码默认值、示例命令、checkpoint、数据、分母和偏离说明是否已检查。

#### 第三方 audit 输出文件映射

| 输出文件或记录 | `schema_version` | `schema_path` |
| --- | --- | --- |
| `run_metadata.json` | `run_metadata_v0_1` | `schemas/third_party_audit/run/run_metadata_v0_1.json` |
| `output_manifest.json` | `output_manifest_v0_1` | `schemas/third_party_audit/run/output_manifest_v0_1.json` |
| `samples.jsonl` | `failure_sample_metadata_v0_1` | `schemas/third_party_audit/samples/failure_sample_metadata_v0_1.json` |
| `stage_attrition.json` | `stage_attrition_v0_1` | `schemas/third_party_audit/attrition/stage_attrition_v0_1.json` |
| receptor prep record JSON | `receptor_prep_record_v0_1` | `schemas/third_party_audit/receptor/receptor_prep_record_v0_1.json` |
| `receptor_prep_index.json` | `receptor_prep_index_v0_1` | `schemas/third_party_audit/receptor/receptor_prep_index_v0_1.json` |
| `evaluator_input.jsonl` | `evaluator_input_v0_1` | `schemas/third_party_audit/diagnosis/evaluator_input_v0_1.json` |
| `labels.jsonl` | `label_v0_1` | `schemas/third_party_audit/diagnosis/label_v0_1.json` |
| evaluator tool result JSONL | `evaluator_tool_result_v0_1` | `schemas/third_party_audit/diagnosis/evaluator_tool_result_v0_1.json` |
| PoseBusters raw wrapper JSON | `posebusters_raw_result_v0_1` | `schemas/third_party_audit/diagnosis/posebusters_raw_result_v0_1.json` |
| diagnosis sanity JSONL | `diagnosis_sanity_v0_1` | `schemas/third_party_audit/diagnosis/diagnosis_sanity_v0_1.json` |
| MVP sanity summary JSON | `mvp_sanity_summary_v0_1` | `schemas/third_party_audit/diagnosis/mvp_sanity_summary_v0_1.json` |
| `label_summary.json` | `label_summary_v0_1` | `schemas/third_party_audit/diagnosis/label_summary_v0_1.json` |
| `prevalence_summary.json` | `prevalence_summary_v0_1` | `schemas/third_party_audit/diagnosis/prevalence_summary_v0_1.json` |
| `analysis_frozen_gate_result.json` | `analysis_frozen_gate_result_v0_1` | `schemas/third_party_audit/diagnosis/analysis_frozen_gate_result_v0_1.json` |
| method resource check JSONL | `method_resource_check_v0_1` | `schemas/third_party_audit/resources/method_resource_check_v0_1.json` |
| blocker log JSONL | `blocker_log_v0_1` | `schemas/third_party_audit/resources/blocker_log_v0_1.json` |
| `env_info.json` | `environment_info_v0_1` | `schemas/third_party_audit/resources/environment_info_v0_1.json` |
| `official_protocol_checklist.json` | `official_protocol_checklist_v0_1` | `schemas/third_party_audit/resources/official_protocol_checklist_v0_1.json` |

### configs

`schemas/configs/` 定义 `configs/` 下项目级配置文件本身的字段格式。保留在 `configs/audit/`, `configs/data/`, `configs/third_party/` 的 YAML / lock 文件应在文件顶部写入自己的 `schema_version` 和 `schema_path`。

| 配置文件类别 | `schema_version` | `schema_path` |
| --- | --- | --- |
| audit diagnosis label config | `config_audit_diagnosis_label_v0_1` | `schemas/configs/audit/diagnosis_label_config_v0_1.json` |
| audit diagnosis label config v0.2 | `config_audit_diagnosis_label_v0_2` | `schemas/configs/audit/diagnosis_label_config_v0_2.json` |
| audit diagnosis label config v0.3 | `config_audit_diagnosis_label_v0_3` | `schemas/configs/audit/diagnosis_label_config_v0_3.json` |
| audit denominator statistics config | `config_audit_denominator_statistics_v0_1` | `schemas/configs/audit/denominator_statistics_config_v0_1.json` |
| audit receptor prep policy config | `config_audit_receptor_prep_policy_v0_1` | `schemas/configs/audit/receptor_prep_policy_v0_1.json` |
| audit evaluator policy config | `config_audit_evaluator_policy_v0_1` | `schemas/configs/audit/evaluator_policy_v0_1.json` |
| audit evaluator policy config v0.2 | `config_audit_evaluator_policy_v0_2` | `schemas/configs/audit/evaluator_policy_v0_2.json` |
| audit analysis-frozen gate config | `config_audit_analysis_frozen_gate_v0_1` | `schemas/configs/audit/analysis_frozen_gate_v0_1.json` |
| audit analysis-frozen gate config v0.2 | `config_audit_analysis_frozen_gate_v0_2` | `schemas/configs/audit/analysis_frozen_gate_v0_2.json` |
| audit resource budget config | `config_audit_resource_budget_v0_1` | `schemas/configs/audit/resource_budget_config_v0_1.json` |
| audit tool versions lock | `config_audit_tool_versions_lock_v0_1` | `schemas/configs/audit/tool_versions_lock_v0_1.json` |
| audit manual decisions config | `config_audit_manual_decisions_v0_1` | `schemas/configs/audit/manual_decisions_v0_1.json` |
| R-group dataset build config | `config_data_rgroup_dataset_v0_1` | `schemas/configs/data/builds/rgroup_dataset_config_v0_1.json` |
| RCSB download config | `config_data_rcsb_download_v0_1` | `schemas/configs/data/downloads/rcsb_download_config_v0_1.json` |
| third-party method protocol/status config | `config_third_party_method_protocol_v0_1` | `schemas/configs/third_party/method_protocol_config_v0_1.json` |

### data

- `data/datasets/entries/dataset_entry_v0_1.json`: canonical dataset entry 格式, 用于 `entries/<sample_id>/entry.json` 和 `entries/index.jsonl` 的每一行。
- `data/datasets/splits/dataset_split_v0_1.json`: dataset split 格式, 用于 `data/datasets/<dataset_id>/splits/*.json`; 新 writer 的 `excluded_examples` 使用包含 `complex_id` 和 `reasons` 的结构化记录。
- `data/datasets/views/dataset_view_v0_1.json`: dataset view manifest 格式, 用于 `data/datasets/<dataset_id>/views/*.json`。
- `data/datasets/manifests/raw/dataset_raw_manifest_v0_1.json`: raw source/checksum manifest 格式, 用于 `data/datasets/<dataset_id>/manifests/raw/*.json`。
- `data/datasets/manifests/entries/dataset_entries_manifest_v0_1.json`: entries manifest 格式, 用于 `data/datasets/<dataset_id>/manifests/entries/*.json`。
- `data/datasets/manifests/lineage/dataset_lineage_raw_to_entry_v0_1.json`: raw 到 entry 的 lineage 索引格式。
- `data/datasets/manifests/lineage/dataset_lineage_entry_to_raw_v0_1.json`: entry 到 raw 的 lineage 索引格式。
- `data/catalog/dataset_catalog_v0_1.json`: 全局 dataset catalog 格式, 用于 `data/catalog/dataset_catalog_v1.json`。
- `data/catalog/dataset_layout_migration_v0_1.json`: data layout 迁移记录格式, 用于 `data/catalog/dataset_layout_migration_*.json`。
- `data/catalog/dataset_raw_reconciliation_v0_1.json`: 跨数据集 raw 重复与 checksum 差异记录格式, 用于 `data/catalog/*raw_reconciliation*.json`。

## 使用原则

- 新增项目自有 JSON / JSONL / YAML 时, 先判断归属: 项目级 config 对应 `schemas/configs/`, canonical data 对应 `schemas/data/`, 第三方 audit 输出对应 `schemas/third_party_audit/`。
- 已有 schema 能表达时复用现有 schema; 不能表达时先新增或升级 schema, 再写对应 metadata / config。
- schema-covered 文件应写入 `schema_version` 和 `schema_path`; 明确例外包括 Conda environment 文件和外部工具原生输出。外部工具原生输出不要强行改格式, 项目自有 wrapper metadata / manifest 才写 schema refs。
- 新增项目自有 JSON / JSONL 写出代码时, 优先使用 `pfr.utils.schema_io` 或 `scripts.eval.audit_common` 暴露的 schema-aware writer, 从 schema `const` 自动注入 `schema_version` 和 `schema_path`; 不要在多个脚本复制双常量。
- 人工判断应进入 schema-covered YAML, 例如单次实验的 `experiments/<experiment_id>/configs/resolved/audit/manual_decisions.yaml`; 输出 JSON / JSONL 只记录该 YAML 的来源追踪字段, 不嵌入整份 YAML。
- schema 是版本化合同, 不是可随意覆盖的一次性模板。旧版本一旦被实验 metadata 或报告引用, 不应静默改写语义。
- 已被使用的版本应尽量固定。旧实验继续指向旧 schema, 新实验可以选择继续使用旧版本或切换到新版本。
- 需要不兼容变更时, 新建下一个版本, 例如 `*_v0_2.json`, 并在相关实验 metadata 或报告中说明迁移原因。
- 不兼容变更包括: 改 required 字段、改字段类型、改字段含义、改 success / failure / attrition 统计口径、删除旧字段或让旧 metadata 无法按原语义解释。
- 兼容性小修可以保留原版本, 例如 typo、description、注释性说明、增加非 required 字段或放宽字段约束; 但仍应避免影响历史 metadata 的解释。
- schema 只规定格式, 不定义实验结论。success / failure 的科学口径仍应以 audit config、experiment report 和 analysis protocol 为准。
- 新增 schema 时, 文件名应包含用途和版本号; 若已位于领域子目录下, 文件名可以省略重复领域前缀, 例如 `third_party_audit/run/output_manifest_v0_1.json`。
- 不要静默改历史实验或历史输出 metadata; 如需让旧文件符合新 schema, 应作为显式 migration 记录到 `docs/EXPERIMENT_LOG.md`, 并说明范围、目标 schema 和校验结果。
