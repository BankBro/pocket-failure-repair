# src 目录管理说明

`src/` 保存可复用的项目库代码。命令行入口、实验 glue code 和一次性运行脚本优先放 `scripts/` 或 `experiments/<experiment_id>/scripts/`; 能跨实验复用的业务逻辑再放入 `src/pfr/`。

## 当前结构

```text
src/pfr/
  baselines/      # baseline 逻辑
  chemistry/      # RDKit scaffold、扰动、坐标和分子工具
  data/           # data manifest、schema refs 和数据读取辅助
  evaluation/     # metrics 和 repair/evaluator 汇总逻辑
  feedback/       # geometry / interaction feedback 相关逻辑
  models/         # 模型代码
  utils/          # IO 和 schema-aware writer 等通用工具
  workflows/      # 可复用 workflow 封装
```

## 设计原则

- `src/pfr/` 中的逻辑应尽量是可复用、可测试、配置驱动的库代码。
- 不在 import 时写文件、下载资源、创建环境或启动外部工具。
- 不在库代码中硬编码具体 `experiment_id` 或 `outputs/<experiment_id>/`; 这些路径由 scripts、configs 或实验 resolved config 传入。
- data schema refs 统一从 `pfr.data.schema_refs` 获取, 不在多个模块复制常量。
- 新增 schema-covered JSON / JSONL writer 时, 优先使用 `pfr.utils.schema_io`; evaluator 脚本可通过 `scripts.eval.audit_common` 复用同一套 helper。
- 需要 heavy evaluator 或第三方方法环境时, 尽量隔离在 wrapper / script 层, 不让普通库导入隐式依赖它们。
- 修改 `src/pfr/` 后应补或运行对应 `tests/`。
