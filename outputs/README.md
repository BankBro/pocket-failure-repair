# outputs 目录管理说明

本目录保存每次实验实际产生的输出。每个输出目录必须对应一个同名的 `experiments/<experiment_id>/` 目录。

## experiment_id 对应关系

```text
experiments/<experiment_id>/
outputs/<experiment_id>/
```

`experiments/<experiment_id>/` 保存命令、配置快照、脚本和 metadata; `outputs/<experiment_id>/` 保存运行产物、指标、日志、图和中间工作文件。

## 推荐结构

```text
outputs/<experiment_id>/
  metadata/
  processed/
  logs/
  metrics/
  tables/
  summaries/
  figures/
  work/
```

用途:

- `metadata/`: 描述本输出目录的 provenance、manifest、hash registry、migration manifest 或 artifact registry; 不是指标主体。
- `processed/`: 本实验产生并可被后续分析读取的派生产物, 如 case summaries、failed/repaired molecules、normalized samples 和 manifests。
- `logs/`: stdout/stderr、工具日志和长日志。
- `metrics/`: 原始指标 JSON。
- `tables/`: 指标表格 CSV/TSV。
- `summaries/`: 汇总 JSON/CSV/Markdown。
- `figures/`: 本实验生成的图。
- `work/`: 临时工作目录或可丢弃中间文件; 重要结果应提升到 `processed/`, `metrics/`, `tables/` 或 `summaries/`。

## 第三方方法输出

第三方方法 run 可继续按 method/run 分层:

```text
outputs/<experiment_id>/<method>/<run_id>/
  captured_outputs/
  processed/
    normalized_samples/
  logs/
  manifests/
  evaluator/
  summaries/
  metrics/
  work/
  run_metadata.json
  samples.jsonl
  output_manifest.json
  stage_attrition.json
```

`captured_outputs/` 表示捕获的 method outputs, 不等价于正式 raw failure prevalence。formal audit 前只能称为 MVP sanity、coverage、evaluability 或 output-capture trial。
第三方工具原生输出文件保留其原始格式, 不要求强行写入本项目的 `schema_version` / `schema_path`; 项目自有的 run metadata、sample metadata、manifest、attrition、label 或 evaluator 结果才按下列 schema refs 写入。

这些 JSON / JSONL metadata 应声明生成时参考的 schema:

```text
run_metadata.json
  schema_version: run_metadata_v0_1
  schema_path: schemas/third_party_audit/run/run_metadata_v0_1.json

samples.jsonl
  schema_version: failure_sample_metadata_v0_1
  schema_path: schemas/third_party_audit/samples/failure_sample_metadata_v0_1.json

stage_attrition.json
  schema_version: stage_attrition_v0_1
  schema_path: schemas/third_party_audit/attrition/stage_attrition_v0_1.json
```

`output_manifest.json`, `labels.jsonl`, evaluator result JSONL, diagnosis sanity JSONL, resource check JSONL 和 blocker log JSONL 的完整 schema 映射见 `schemas/README.md`; protocol config 中的 `metadata_schemas` key 映射见 `configs/README.md`。

schema 不是固定死的模板, 而是可升级的版本化合同。历史 outputs metadata 继续指向生成时使用的 schema 版本; 若后续需要改 required 字段、字段类型、字段含义或统计口径, 应新增 schema 版本, 不要静默改写旧版本语义。

## 放置规则

- 不要在 `outputs/` 根目录直接散放文件。
- 不要新建旧式 `raw/`, `normalized/`, `raw_outputs/`, `normalized_outputs/` 目录作为默认输出结构。
- 配置快照应放在 `experiments/<experiment_id>/configs/` 或 `experiments/<experiment_id>/configs/resolved/`, 不放在 `outputs/`。
- 输出引用迁移后, 同步更新 configs、scripts、docs 和 manifests 中的引用路径。
- 如果输出后续被提升为跨实验复用 dataset, 应新建或更新 `data/datasets/<dataset_id>/entries/`, `raw/`, `splits/`, `views/`, `manifests/`; 不要直接把 `outputs/<experiment_id>/processed/` 当作 canonical dataset。
- 默认可提交轻量 provenance 和汇总结果: `metadata/`, `summaries/`, `tables/`, `figures/*.svg`, 以及 summary metrics。`metadata/` 应用于 output-level manifest、hash、migration 或 artifact registry, 不放指标主体或大规模 per-sample 结果。
- 默认不提交重产物: `logs/`, `work/`, `captured_outputs/`, 第三方工具原生报告, 结构文件, `processed/**/*.jsonl`, `processed/cases/*.json`, `metrics/**/*.jsonl` 和输出目录下的临时 YAML config。需要保留的关键信息应提升为 summary、table、figure 或 metadata manifest。
