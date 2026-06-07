# docs/AGENTS.md

## 文档协作规范

- 交互语言: 文档相关讨论, 文档审阅, 以及与协作型 Agent 讨论文档时, 始终使用中文.
- 文本格式: 所有文档使用 UTF-8; 中文说明使用英文标点.
- 文档目录: `docs/plan/` 用于研究规划、实验方案、路线图和阶段计划; `docs/report/` 用于实验报告、审计报告、阶段结果和复盘. 新建文档应按内容放入对应子目录.
- 文档命名: `docs/plan/` 下新建 Markdown 文档使用 `YYYYMMDD-<num>-xxx-plan.md`; `docs/report/` 下新建 Markdown 文档使用 `YYYYMMDD-<num>-xxx-report.md`. `<num>` 表示当天第几个新建文档. 如果文档对应某个实验, `xxx` 优先使用该实验的 `experiment_name`; 如果 plan 和 report 对应同一个实验或审计, 只要求中间的 `xxx` 相同; 日期和 `<num>` 可以不同, 因为计划时间和完成时间可能不同. 已有文档不需要改名.
- 文档目标: 所有研究结论必须能追溯到代码, 配置, 数据版本, 日志, 原始指标, 文献来源或实验记录.
- 禁止事项: 不伪造数据, 不伪造结果, 不伪造引用, 不只报告最好 seed, 不隐藏负结果, 不为了结果好看临时改指标定义, 不只用 Vina 分数证明方法有效.

## 关键文档职责

- `STATUS.md`: 只记录当前最重要的项目快照, 用于上下文压缩后的快速恢复. 保持简短.
- `EXPERIMENT_LOG.md`: 追加记录完整实验过程, 包括 purpose/目的, `experiment_id`, 环境, 数据版本, 命令, 配置, 输出路径, 指标, 结论, 失败原因和下一步.
- `docs/plan/`: 维护研究规划、路线图、实验方案和阶段计划.
- `docs/report/`: 维护调研报告、实验报告、审计报告、阶段结果和复盘.

## 写作要求

- 结论要区分: 已验证结论, 初步证据, 推测, 待验证假设.
- 记录失败, 阻塞和负结果; 它们是方向调整依据.
- 引用论文, 工具或仓库时, 必须保留可核验来源信息.
- 更新重要阶段后, 同步更新 `STATUS.md`; 实验或阶段性工作完成后, 追加 `EXPERIMENT_LOG.md`.
- 记录实验时必须引用对应 `experiment_id`, 以及 `experiments/<experiment_id>/` 和 `outputs/<experiment_id>/` 路径. 实验目录规范见 `../experiments/README.md`.
- 记录 canonical dataset 时使用当前 `data/datasets/<dataset_id>/` 结构: `raw/<sample_id>/`, `entries/index.jsonl`, `entries/<sample_id>/entry.json`, `splits/`, `views/`, `manifests/`. 历史日志中迁移前旧路径可以保留, 但必须能看出是 historical provenance, 不能写成当前推荐结构。
- 不创建脱离项目主线的临时说明文档; 优先更新现有文档.
