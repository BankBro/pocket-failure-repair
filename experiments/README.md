# 实验目录管理规范

本目录用于管理每次实验的运行记录、专用脚本、配置快照和 metadata。跨实验复用的稳定脚本仍放在项目根目录的 `scripts/`。

## experiment_id

每次实验必须先定义短实验名, 再定义完整实验代号:

```text
experiment_name = xxx
experiment_id = YYYYMMDD-<num>-<experiment_name>
```

示例:

```text
20260604-01-diffsbdd-mvp-trial
20260604-02-difflinker-mvp-trial
```

其中:

- `experiment_name`: 简短英文 kebab-case 实验名, 对应模板中的 `xxx`。
- `YYYYMMDD`: 实验创建日期。
- `<num>`: 当天第几个实验, 从 `01` 开始。

若后续为该实验新建 `docs/plan/` 或 `docs/report/` 文档, 文档文件名中的 `xxx` 优先使用同一个 `experiment_name`。

## 目录对应关系

每个实验在 `experiments/` 和 `outputs/` 下使用同一个 `experiment_id`:

```text
experiments/<experiment_id>/
outputs/<experiment_id>/
```

`experiments/<experiment_id>/` 保存运行记录和实验专用资产; `outputs/<experiment_id>/` 保存该实验产生的输出。

## 推荐 experiments 结构

```text
experiments/<experiment_id>/
  README.md
  command.sh
  configs/
    resolved/
  metadata/
  scripts/
  patches/
  run_metadata.json
  notes.md
```

用途:

- `README.md`: 本实验目的、范围、输入、运行方式和结果索引。
- `command.sh`: 实际执行命令或命令入口。
- `configs/resolved/`: 本实验实际使用的 resolved config, 包括已经填入具体 seed、输入路径、输出路径和参数的配置快照。
- `metadata/`: 实验管理 metadata, 如 pipeline plan、迁移清单、asset/hash manifest、输入输出路径索引和 provenance。
- `scripts/`: 只服务本实验的专用脚本。
- `patches/`: 只服务本实验的一次性第三方源码 patch; 长期复用 patch 应提升到 `third_party/patches/<method>/`。
- `run_metadata.json`: command、环境、commit、seed、config hash、输入输出路径等可追溯信息。
- `notes.md`: 临时观察、失败原因、人工检查记录。

## Metadata 与 schema

- `experiments/<experiment_id>/metadata/` 和实验级 `run_metadata.json` 用于记录实验管理 metadata, 如 command、config snapshot、pipeline plan、迁移清单、输入输出路径和 provenance。
- 单次实验的实际配置快照放 `experiments/<experiment_id>/configs/resolved/`, 不放项目级 `configs/`, 也不放 `outputs/`。
- 生成 JSON / JSONL metadata 时, 若 `schemas/` 下已有对应 schema, 输出文件应写入 `schema_version` 和 `schema_path`, 明确声明遵循哪个字段规范。
- schema 不是固定死的模板, 而是可升级的版本化合同。已被历史实验引用的版本应保持语义稳定; 若需要改 required 字段、字段类型、字段含义或统计口径, 应新增版本, 例如从 `v0_1` 升到 `v0_2`。
- 旧实验继续指向旧 schema, 新实验可以显式切换到新 schema; 不要为了新实验静默改写旧 schema 语义。

## 推荐 outputs 结构

```text
outputs/<experiment_id>/
  metadata/
  processed/
    cases/
    failed_molecules/
    repaired_molecules/
    manifests/
  logs/
  metrics/
  tables/
  summaries/
  figures/
  work/
```

用途:

- `metadata/`: output-level provenance、manifest、hash registry、migration manifest 或 artifact registry; 不放指标主体。
- `processed/`: 本实验产生并可被后续分析读取的派生产物, 如 case summaries、failed/repaired molecules 和运行 manifest。
- `logs/`: stdout/stderr、工具日志和长日志。
- `metrics/`: 原始指标 JSON。
- `tables/`: 指标表格 CSV/TSV。
- `summaries/`: 汇总 JSON/CSV/Markdown。
- `figures/`: 本实验生成的图。
- `work/`: 临时工作目录或可丢弃中间文件; 重要结果应提升到 `processed/`, `metrics/`, `tables/` 或 `summaries/`。

如果一次实验包含多个 method、case、seed 或 run, 可在实验目录内部继续分层, 例如:

```text
outputs/<experiment_id>/
  diffsbdd/case_3rfm/seed_0/
  diffsbdd/case_3rfm/seed_1/
```

或:

```text
outputs/<experiment_id>/
  run_s0/
  run_s1/
```

## 脚本放置原则

- 跨实验复用、稳定、项目级脚本放 `scripts/`。
- 只服务某一次实验的脚本放 `experiments/<experiment_id>/scripts/`。
- 如果某个实验专用脚本后续被多个实验复用, 应提升到根目录 `scripts/`, 并改成配置驱动。
- 参与生成结果的脚本路径和 commit/hash 必须写入 `run_metadata.json` 或等价 metadata。
- 一次性中间脚本或中间文件不属于实验资产时, 放 `tmp/YYYYMMDD-<task-slug>/` 并在任务结束后删除。

## 记录原则

- `docs/EXPERIMENT_LOG.md` 记录阶段性历史, 必须引用 `experiment_id`、`experiments/<experiment_id>/` 和 `outputs/<experiment_id>/`。
- `docs/STATUS.md` 只记录当前最重要状态, 不堆长日志或单次实验细节。
- 大 checkpoint、大数据集、大规模 raw outputs、受限第三方文件、per-sample JSONL、结构文件、工具原生报告和日志不提交到 git; git 只保存轻量可复现资产, 如脚本、resolved config、patch、schema、manifest、小样例、summary、table 和 figure。
- 实验若引用 canonical dataset, 应指向 `data/datasets/<dataset_id>/entries/index.jsonl`, `data/datasets/<dataset_id>/entries/<sample_id>/entry.json` 或 `data/datasets/<dataset_id>/raw/<sample_id>/`; 单次实验派生产物仍放在 `outputs/<experiment_id>/processed/`, 不提升到 `data/datasets/`。
- `outputs/` 下的可提交/默认忽略边界以 `outputs/README.md` 和 `.gitignore` 为准; 需要保留的关键信息应提升为 `metadata/`, `summaries/`, `tables/`, `figures/` 或 summary metrics。
