# 第三方 Failure Audit MVP 开跑边界简要方案

日期: 2026-06-04
状态: `mvp_trial_boundary_draft`, `ready_to_start_small_scale_trial`

说明: `ready_to_start_small_scale_trial` 只表示本边界方案可用于启动小规模 trial, 不表示第三方方法环境、真实 inference 或 `analysis-frozen` gate 已完成。

## 1. 目的

本文档用于固定第一阶段 MVP 小规模 trial 的开跑边界。它不是 formal failure prevalence audit 方案, 也不是 repair benchmark 方案。

本阶段目标是用最小规模验证:

```text
第三方方法小规模输出
→ 输出捕获与元数据记录
→ RDKit / PoseBusters / PLIP / Vina 等诊断工具链路
→ tool_failure / not_evaluable / failure label 草案记录
→ 判断 audit pipeline 是否可继续推进
```

## 2. 当前阶段定位

当前阶段是:

```text
MVP / sanity wiring / small-scale output-capture trial
```

允许结论:

- 第三方方法环境是否能搭建。
- 小规模 inference 是否能产生输出。
- 输出是否能被统一收集和记录。
- 诊断工具链路是否能跑通。
- 哪些工具、规则、数据或 license 仍阻塞后续 formal audit。

不允许结论:

- 不宣称第三方方法正式失败率。
- 不宣称 repair benchmark 结果。
- 不把 adapted audit 称为原协议复现。
- 不用 Vina score 单独定义成功。

## 3. 第一轮方法范围

第一轮 MVP 默认只跑:

1. DiffSBDD。
2. DiffLinker。

说明: DiffLinker 属于 linker / stage-limited 候选方法, 与 DiffSBDD 的 SBDD 生成任务边界不同。MVP 阶段可共同用于输出捕获和诊断链路 sanity, 但后续不能把二者直接合并解释为同一类 raw SBDD failure prevalence。

其他候选方法暂不进入第一轮 MVP 主流程, 只保留为后续扩展或受限条件下的 supplementary/internal audit 候选。

## 4. 小规模运行规模

默认规模:

- 每个方法选择少量 case。
- 每个 case 生成 `n_samples=3-10`。
- 只用于 sanity check, 不用于正式统计。

如方法官方 example 已有更小默认配置, 优先使用官方小样例配置。除非必要, 不修改原方法 sampling、filtering、reranking、docking config 或 success definition。

## 5. PoseBusters MVP 暂用规则

MVP 阶段暂用:

- `mol`: 检查 ligand 自身化学与 3D 几何合理性。
- `dock`: 检查 ligand-pocket pose plausibility 和 protein-ligand clash / overlap。

暂不使用 `redock` 作为主配置。

注意: 该规则仅用于 MVP sanity wiring。进入 formal audit 前, 仍需在 `configs/audit/tool_versions.lock` 和相关 audit config 中正式冻结 PoseBusters 版本、config、输出列、阈值、label 映射和 wrapper 行为。

## 6. 环境边界

评估/诊断环境:

```text
conda env: pfr-eval-tools
用途: RDKit, PoseBusters, PLIP, OpenBabel, Meeko, Vina 等 evaluator tools
```

第三方方法推理环境需单独建立, 不与 `pfr-eval-tools` 混用。第一轮预计包括:

```text
pfr-diffsbdd
pfr-difflinker
```

每个方法环境建立后需记录:

- Python 版本。
- CUDA / PyTorch 版本。
- PyTorch Geometric / PyTorch Lightning 等关键依赖版本。
- RDKit / OpenBabel 等方法内依赖版本。
- repo URL、commit、license、checkpoint 来源。

## 7. 暂停条件

遇到以下情况应暂停并记录, 不自动绕过:

1. 需要申请、登录、付费、联系作者或 gated access 的数据/checkpoint。
2. Google Drive 或其他资源大小未知, 且可能超过 resource budget。
3. license 不清楚, 或存在禁止使用/再分发/改造的风险。
4. 需要使用非官方镜像、非官方数据源或不可信 checkpoint。
5. 需要替换核心数据集、checkpoint 或官方资源来源。
6. 需要修改原方法 sampling、decoding、filtering、reranking、docking config、success definition 或 candidate budget。
7. checkpoint 训练数据未知, 但准备作为 clean 主结论证据。
8. 单方法下载、存储或运行成本超过当前 resource budget。

## 8. 预期产物

MVP trial 结束后至少应产出:

- `experiment_name = xxx` 和 `experiment_id = YYYYMMDD-<num>-<experiment_name>`。
- `experiments/<experiment_id>/` 下的方法环境记录、命令、配置、专用脚本、metadata 和说明。
- `outputs/<experiment_id>/` 下的小规模 inference/output-capture 日志、captured method outputs 和 processed normalized outputs。
- 每个样本的 provenance metadata。
- evaluator 工具运行结果。
- tool_failure / pipeline_failure / not_evaluable 记录。
- MVP trial 小报告。

若为该 trial 新建 plan/report 文档, 文件名中的 `xxx` 优先使用同一个 `experiment_name`。

## 9. STATUS 与 EXPERIMENT_LOG 维护原则

实验过程中需要同时维护 `docs/STATUS.md` 和 `docs/EXPERIMENT_LOG.md`, 但二者职责不同:

- `docs/STATUS.md`: 只保留当前最重要的项目快照, 用于上下文压缩或新会话后的快速恢复。应及时删除或压缩旧状态, 不作为完整历史记录。
- `docs/EXPERIMENT_LOG.md`: 作为完整历史记录, 追加保存实验过程、`experiment_id`、命令、配置、输出路径、失败原因、阶段结论和下一步。

更新原则:

- 关键阶段开始/完成、重要阻塞出现或解除、下一步发生变化时, 同步更新 `docs/STATUS.md`。
- 每次阶段性实验、调研、工具核查或 trial 完成后, 追加 `docs/EXPERIMENT_LOG.md`。
- 不把长日志、过期状态和详细过程堆进 `docs/STATUS.md`; 这些应放入 `docs/EXPERIMENT_LOG.md` 或对应 report。

## 10. 与现有文档关系

本文件是以下文档的简要执行边界补充。

执行时的参考关系:

- 严格执行规范、阶段 gate、metadata、暂停规则和 claim ladder, 参考 `docs/plan/20260603-03-third-party-failure-audit-detailed-execution-plan.md`。
- 本次 MVP 先跑什么、跑多大、哪些临时边界, 参考本文档。

相关文档:

- `docs/plan/20260603-02-third-party-failure-audit-alignment-plan.md`: 高层对齐方案, 说明为什么先做第三方 failure audit, 以及 audit 与后续 repair benchmark 的关系。
- `docs/plan/20260603-03-third-party-failure-audit-detailed-execution-plan.md`: 详细执行 SOP, 规定阶段 gate、metadata、暂停条件、claim ladder 和 `analysis-frozen` 要求。
- `docs/report/20260603-03-third-party-failure-audit-mvp-report.md`: 第一阶段 MVP 已完成资产和当前未完成事项的阶段报告。
- `docs/report/20260604-01-audit-tool-coverage-report.md`: 当前第三方评估工具是否足够支撑 MVP / formal audit 的覆盖度复核报告。

若后续进入 formal audit, 应以 analysis-frozen 后的 label config、denominator schema、tool version lock 和 sanity set 为准。
