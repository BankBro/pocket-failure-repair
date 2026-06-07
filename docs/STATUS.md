# STATUS

> 用于上下文压缩或新会话快速恢复。只保留当前最重要状态; 详细过程和历史迁移记录见 `docs/EXPERIMENT_LOG.md`。

## 当前主线

- 项目主线: Failure-feedback-conditioned repair for pocket-aware 3D local molecular editing。
- 当前阶段: `third_party_failure_audit_mvp_ready_to_start_small_scale_trial`。
- 当前优先事项: 先完成 DiffSBDD / DiffLinker 真实输出的小规模 failure audit MVP / output-capture trial, 再由真实失败分布决定 repair 重点。
- 重要边界: 现在不是 formal failure prevalence audit, 不是 repair benchmark, 不能宣称第三方方法正式失败率或论文主结果。

## 关键文档

- MVP 开跑边界: `docs/plan/20260604-01-third-party-failure-audit-mvp-trial-boundary-plan.md`
- 详细执行 SOP: `docs/plan/20260603-03-third-party-failure-audit-detailed-execution-plan.md`
- 高层对齐方案: `docs/plan/20260603-02-third-party-failure-audit-alignment-plan.md`
- 第三方 output capture 方案: `docs/plan/20260604-02-third-party-audit-mvp-output-capture-plan.md`
- failure taxonomy 调研报告: `docs/report/20260603-01-failure-taxonomy-research-report.md`
- 第一阶段 MVP 报告: `docs/report/20260603-03-third-party-failure-audit-mvp-report.md`
- 工具覆盖度复核报告: `docs/report/20260604-01-audit-tool-coverage-report.md`
- 完整历史记录: `docs/EXPERIMENT_LOG.md`

## 当前可用资产

- 开发 / data writer / smoke test 环境: Conda env `pfr`。
- official PLIP / Vina / PoseBusters evaluator 环境: Conda env `pfr-eval-tools`。
- 第三方方法推理环境: 按方法单独创建, 不与 evaluator 环境混用。
- DiffSBDD / DiffLinker 官方 repo、小型 checkpoint 和 wrapper dry-run metadata 已准备; 真实 inference 尚未执行。
- 第三方 audit schema 已统一放入 `schemas/third_party_audit/`, 覆盖 run metadata、sample metadata、output manifest、stage attrition、labels、resource check、blocker log、evaluator result 和 diagnosis sanity。
- config schema 已放入 `schemas/configs/`; 项目级 `configs/audit/`, `configs/data/`, `configs/third_party/` 配置应声明 `schema_version` 和 `schema_path`。
- canonical data schema 已放入 `schemas/data/`; 当前 `data/` 下项目自有 JSON / JSONL metadata 已完成 schema ref 迁移。

## 当前仓库结构状态

- `configs/` 只放项目级真实配置和状态记录; 单次运行 resolved config 放 `experiments/<experiment_id>/configs/resolved/`。
- `data/` 按 `data/datasets/<dataset_id>/` 组织 canonical dataset; raw 结构文件在 dataset-local `raw/<sample_id>/`, 全局 catalog 在 `data/catalog/`。
- `outputs/` 按 `outputs/<experiment_id>/` 组织实验输出; `metadata/`, `summaries/`, `tables/`, `figures/*.svg` 和 summary metrics 可提交, 大规模 JSONL、结构文件、工具报告、logs/work/captured outputs 默认忽略。
- `sources/` 保存文献、检索结果和调研 provenance, 不作为 canonical dataset 或实验输出。
- `third_party/` 保存外部仓库和长期 patch; wrapper / instrumentation 放 `scripts/third_party/`。
- `tmp/` 只放临时中间产物, 使用 `tmp/YYYYMMDD-<task-slug>/`, 任务结束后删除。
- 各关键目录已有 `README.md` / `AGENTS.md`; 具体目录规则以就近文件为准。

## 当前阻塞与风险

- DiffSBDD / DiffLinker 的 method-specific inference Conda env 尚未创建, 真实第三方 inference 尚未运行。
- formal audit 前还缺 PoseBusters / RDKit / PLIP 规则冻结、batch wrapper、统一 labeling pipeline 和 sanity set。
- Pocket2Mol / TargetDiff checkpoint 与数据涉及 Google Drive 且大小未知, 当前按 resource budget policy 暂停。
- MolCRAFT 为 NonCommercial/ShareAlike, 不作为默认 MVP 主实验; 可作为 restricted-license internal/supplementary audit 候选。
- 3DLinker license 不可见, 暂不 clone/run。
- Vina score 只能作为辅助 metric, 不能单独定义 repair success。

## 下一步

1. 创建 DiffSBDD 专用环境 `pfr-diffsbdd`, 记录版本, 运行 3RFM example 小规模 output-capture trial (`n_samples=3-10`)。
2. 创建 DiffLinker 专用环境 `pfr-difflinker`, 运行 HSP90 / case-study 小规模 output-capture trial, 单独标注 linker / stage-limited 边界。
3. 用真实或 dry-run output rows 跑 diagnosis sanity, 验证 `missing_data` / `tool_failure` / `pipeline_failure` / `not_evaluable` / `original_status` 不被静默删除。
4. formal audit 前冻结 PoseBusters、RDKit、PLIP 和 labeling pipeline, 并通过 `analysis-frozen` gate。

## 暂停条件

- 需要申请、登录、付费、联系作者或 gated access 的数据/checkpoint。
- Google Drive 或其他资源大小未知, 且可能超过 resource budget。
- license 不清楚, 或存在禁止使用/再分发/改造的风险。
- 需要使用非官方镜像、非官方数据源或不可信 checkpoint。
- 需要替换核心数据集、checkpoint 或官方资源来源。
- 需要修改原方法 sampling、decoding、filtering、reranking、docking config、success definition 或 candidate budget。
- checkpoint 训练数据未知, 但准备作为 clean 主结论证据。
- 单方法下载、存储或运行成本超过当前 resource budget。

## 维护原则

- `docs/STATUS.md` 只保留当前快照, 旧状态要及时删除或压缩。
- `docs/EXPERIMENT_LOG.md` 追加保存完整历史、命令、配置、输出路径、失败原因、阶段结论和下一步。
