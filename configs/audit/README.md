# Audit configs

本目录保存第三方 failure audit 的核心协议配置。当前状态为 `draft-ready`, 尚未通过 `analysis-frozen` gate, 因此不能用于声明正式 failure prevalence 或 near-miss 结论。

## 文件说明

- `resource_budget_v1.yaml`: 第一阶段下载、存储、环境搭建和运行预算, 以及 unknown-size / gated / license 风险资源的阻塞规则。
- `diagnosis_label_config_v0_1.yaml`: failure diagnosis label 草案, 包括 evaluability status, primary/secondary labels, precedence 和 near-miss eligibility。
- `diagnosis_label_config_v0_2.yaml`: 统一评估流水线 v0.1 的标签映射冻结目标, 区分 not evaluable, PoseBusters frozen columns, PLIP 描述性证据和 Vina 辅助分数。
- `diagnosis_label_config_v0_3.yaml`: 统一评估流水线 v0.2 的标签映射冻结目标, 区分 PoseBusters `internal_energy=false` 和 `internal_energy` 条件列不可判定。
- `denominator_statistics_schema_v0_1.yaml`: denominator、stage attrition、prevalence、bootstrap 和 co-occurrence 的统计口径草案。
- `receptor_prep_policy_v0_1.yaml`: receptor 清理和 HETATM 复核规则, 包括 reference ligand 删除、unknown HETATM 8.0 A 复核距离和 Vina box 来源。
- `evaluator_policy_v0_1.yaml`: RDKit, PoseBusters, PLIP, Vina 的统一输入和冻结列口径。
- `evaluator_policy_v0_2.yaml`: 在 v0.1 基础上将 PoseBusters `internal_energy` 改为 conditional column, 记录 unavailable coverage。
- `analysis_frozen_gate_v0_1.yaml`: 正式失败分布统计前需要通过的 gate 检查项和 warning 项。
- `analysis_frozen_gate_v0_2.yaml`: 在 v0.1 基础上增加 PoseBusters `internal_energy` unavailable coverage gate。
- `tool_versions.lock`: evaluator 环境、外部工具版本、CLI 路径和正式 PLIP/Vina 使用边界。

## 使用原则

- 正式 labeling / prevalence 统计前, 必须冻结 label config、tool versions、denominator schema 并记录 hash。
- `pfr-eval-tools` 只作为评估/诊断工具环境; 第三方方法推理环境应按方法单独创建。
- Vina score 只能作为辅助指标, 不能单独作为 repair success gate。
