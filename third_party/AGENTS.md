# AGENTS.md

## third_party 目录协作规则

- 本目录只放官方第三方方法仓库、轻量资源说明和可复用 patch 资产; 不放项目自有 wrapper 代码、实验输出或 canonical dataset。
- 克隆下来的第三方源码视为外部 artifact, 默认不要直接改 upstream source tree。必须改源码时, 先判断是否改变算法行为, 并在实验记录和报告中标注。
- 长期复用 patch 放 `third_party/patches/<method>/`; 单次实验临时 patch 放 `experiments/<experiment_id>/patches/`; 不需要修改 upstream 的 wrapper / instrumentation 放 `scripts/third_party/`。
- algorithm-changing patch 不能再声称是 original protocol reproduction, 应标注为 adapted baseline 或 adapted run。
- 不提交大 checkpoint、大数据集、第三方 generated outputs、长日志或不可再分发资产。资源 URL、commit、license、checkpoint 状态和 blocker 写入 `configs/third_party/`, `docs/report/` 或对应实验记录。
- 第三方方法真实推理按方法单独创建 Conda 环境; 不与 `pfr-eval-tools` evaluator 环境混用。
- 遇到 gated access、登录/申请/付费、license 不清、大小未知可能超预算或非官方资源时, 暂停并记录 blocker, 不自动替换来源。
- 第三方方法输出写入 `outputs/<experiment_id>/<method>/<run_id>/captured_outputs/`; 不写回 `third_party/`。
