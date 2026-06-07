# scripts 目录管理说明

本目录保存跨实验复用的项目级脚本。单次实验专用脚本应放在 `experiments/<experiment_id>/scripts/`, 只有稳定复用后再提升到这里。

## 顶层结构

```text
scripts/
  analysis/
  audit/
  data/
  eval/
  setup/
  third_party/
  train/
```

## 子目录职责

- `analysis/`: 结果汇总、表格、图和报告辅助分析脚本。
- `audit/`: failure audit、metadata 检查、denominator、labeling 或 provenance 相关脚本。
- `data/`: 数据下载、构建、清理、manifest、entries 和 dataset view 生成脚本。
- `eval/`: evaluator、baseline evaluation、官方工具 wrapper 和 metrics 计算脚本。
- `setup/`: 环境、dry-run、资源准备和 smoke pipeline 规划脚本。
- `third_party/`: 第三方方法运行 wrapper、output capture 和轻量 instrumentation 入口。
- `train/`: 模型训练或训练相关工具脚本。

## 脚本设计原则

- 脚本应尽量配置驱动, 默认路径必须符合 `experiments/<experiment_id>/` 和 `outputs/<experiment_id>/` 规范。
- 不要让无参 dry-run 写入历史 experiment 或 outputs 路径; 如需持久化, 使用显式参数。
- 配置快照、resolved config 和 run metadata 写入 `experiments/<experiment_id>/`; 项目级 `configs/` 只保留跨实验稳定真实配置和协议。
- 生成 JSON / JSONL metadata 的脚本应参考 `schemas/` 中对应 schema, 并在输出中写入 `schema_version` 和 `schema_path`; 若需要不兼容字段变更, 应新增 schema 版本。
- 项目开发、`scripts/data/*` writer 和 smoke pipeline 测试默认使用 Conda env `pfr`; official PLIP / Vina / PoseBusters evaluator 使用 `pfr-eval-tools`。
- 实际产物写入 `outputs/<experiment_id>/`。
- 数据构建脚本若生成 canonical dataset, 默认写入 `data/datasets/<dataset_id>/entries/index.jsonl`, 并同步生成 `data/datasets/<dataset_id>/entries/<sample_id>/entry.json`。
- `scripts/data/` 下的 canonical dataset writer 应按 `schemas/data/README.md` 的映射写入 `schema_version`, `schema_path`, `dataset_id` 和 `dataset_version`; 优先复用 `pfr.data.schema_refs`, 不要在多个脚本中复制 schema 常量。
- 数据下载脚本若生成 raw dataset, 默认写入 `data/datasets/<dataset_id>/raw/<sample_id>/`, 不写迁移前旧式顶层 raw 目录。
- 第三方 wrapper 只能做命令封装、日志捕获、metadata、manifest 和 output capture; 不得默认修改 sampling、decoding、filtering、reranking、docking config、success definition 或 candidate budget。

## 记录要求

新增或修改脚本时, 若会影响实验输出路径、metadata schema、denominator 或 evaluation 口径, 同步更新相关 config、README/CLAUDE、docs plan/report 和 `docs/EXPERIMENT_LOG.md`。
