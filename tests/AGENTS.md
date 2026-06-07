# AGENTS.md

## tests 目录协作规则

- 新增功能、schema、config 路径、data writer 或 audit wrapper 时, 优先添加聚焦测试, 覆盖最容易破坏的合同。
- 默认测试命令使用 `conda run -n pfr env PYTHONPATH=src pytest -q ...`。
- 不让默认测试依赖网络、GPU、大模型 checkpoint、完整第三方方法环境或外部服务。
- 需要 evaluator 工具链的测试必须明确依赖 `pfr-eval-tools`, 并避免成为默认快速测试的隐式要求。
- 测试产生的文件写入 `tmp_path`; 不把测试临时产物写入真实 `data/`, `experiments/` 或 `outputs/`。
- schema-covered JSON / JSONL / YAML 变更应有测试检查 `schema_version`, `schema_path` 和关键 required 字段。
- 不通过放宽断言来掩盖真实回归。若旧 fixture 需要升级, 先确认是否属于显式 migration。
