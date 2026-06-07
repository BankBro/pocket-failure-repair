# Audit configs

本目录保存第三方 failure audit 的核心协议配置。当前状态为 `draft-ready`, 尚未通过 `analysis-frozen` gate, 因此不能用于声明正式 failure prevalence 或 near-miss 结论。

## 文件说明

- `resource_budget_v1.yaml`: 第一阶段下载、存储、环境搭建和运行预算, 以及 unknown-size / gated / license 风险资源的阻塞规则。
- `diagnosis_label_config_v0_1.yaml`: failure diagnosis label 草案, 包括 evaluability status, primary/secondary labels, precedence 和 near-miss eligibility。
- `denominator_statistics_schema_v0_1.yaml`: denominator、stage attrition、prevalence、bootstrap 和 co-occurrence 的统计口径草案。
- `tool_versions.lock`: evaluator 环境、外部工具版本、CLI 路径和正式 PLIP/Vina 使用边界。

## 使用原则

- 正式 labeling / prevalence 统计前, 必须冻结 label config、tool versions、denominator schema 并记录 hash。
- `pfr-eval-tools` 只作为评估/诊断工具环境; 第三方方法推理环境应按方法单独创建。
- Vina score 只能作为辅助指标, 不能单独作为 repair success gate。
