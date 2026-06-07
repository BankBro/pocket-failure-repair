# AGENTS.md

## src 目录协作规则

- `src/pfr/` 只放跨实验复用的库逻辑; 单次实验专用代码放 `experiments/<experiment_id>/scripts/`, 稳定 CLI 入口放 `scripts/`。
- 保持模块 import 无副作用: 不写文件、不联网、不下载 checkpoint、不启动外部工具。
- 路径、seed、tool version、output root 和实验 ID 应由 config 或调用方传入, 不在库代码中硬编码具体实验路径。
- 生成或处理 schema-covered metadata 时, 复用对应 helper, 例如 `pfr.data.schema_refs`; 不复制散落的 `schema_version` / `schema_path` 常量。
- 项目开发和测试默认使用 Conda env `pfr`; evaluator-heavy 逻辑不要让普通 `pfr` 单元测试隐式依赖 `pfr-eval-tools`。
- 修改 reusable 逻辑时同步更新或新增 `tests/` 中的聚焦测试。
- 不把第三方方法源码、checkpoint、数据集或实验输出放入 `src/`。
