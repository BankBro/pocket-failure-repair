# docs 目录管理说明

`docs/` 保存项目规划、阶段报告、当前状态和完整实验日志。所有研究结论都应能追溯到代码、配置、数据版本、日志、原始指标、文献来源或实验记录。

## 顶层文件

- `STATUS.md`: 当前最重要的项目快照, 用于上下文压缩或新会话快速恢复。保持简短, 不堆长日志。
- `EXPERIMENT_LOG.md`: 追加记录完整实验、调研和阶段性工作过程, 包括目的、`experiment_id`、环境、命令、配置、输出路径、指标、结论、失败原因和下一步。

## 子目录

- `plan/`: 研究规划、实验方案、路线图和阶段计划。
- `report/`: 调研报告、实验报告、审计报告、阶段结果和复盘。

## 命名规则

- `docs/plan/` 下新建 Markdown 文档使用 `YYYYMMDD-<num>-xxx-plan.md`。
- `docs/report/` 下新建 Markdown 文档使用 `YYYYMMDD-<num>-xxx-report.md`。
- `<num>` 表示当天第几个新建文档。若文档对应某个实验, `xxx` 优先使用该实验的 `experiment_name`。
- plan 和 report 对应同一个实验或审计时, 只要求中间的 `xxx` 相同; 日期和 `<num>` 可以不同。

## 写作要求

- 结论要区分已验证结论、初步证据、推测和待验证假设。
- 记录失败、阻塞和负结果; 不隐藏负结果, 不只报告最好 seed。
- 引用论文、工具或仓库时, 保留可核验来源信息, 并优先指向 `sources/` 中对应 provenance。
- 记录实验时必须引用 `experiment_id`, `experiments/<experiment_id>/` 和 `outputs/<experiment_id>/`。
- 记录 canonical dataset 时使用当前 `data/datasets/<dataset_id>/` 结构, 不把历史迁移前路径写成当前推荐结构。
