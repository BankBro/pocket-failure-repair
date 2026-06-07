# configs 目录管理说明

`configs/` 放项目级真实配置。这里的“config”不是泛指所有 YAML/JSON, 而是指会影响数据构建、第三方 audit、评估口径、工具版本或资源边界的配置文件。

本目录主要放这些文件:

- 规则文件: 项目当前默认遵守的稳定口径, 例如 label 定义、denominator 统计口径、tool version lock、resource budget。
- 数据构建配置: 当前 canonical dataset 的构建输入、输出和过滤参数。
- 第三方方法状态/协议记录: 当前项目对第三方方法资源、checkpoint、license、运行边界和 blocker 的记录。

本目录不放空模板, 也不放单次实验的实际配置快照。某次运行真正使用的 resolved config 应放在 `experiments/<experiment_id>/configs/resolved/`, 便于以后追溯当时的输入、参数和路径。

判断标准:

- 会被多个实验复用, 或代表项目当前统一口径/当前资源状态 -> 放 `configs/`。
- 只属于某一次实验, 已经填入具体 `experiment_id`, seed, output path 或临时参数 -> 放 `experiments/<experiment_id>/configs/resolved/`。
- 只是给人复制填空的 skeleton/template -> 不放 `configs/`; 优先用 `schemas/configs/` 定义格式, 或在具体实验中保存已 resolved 的配置。
- 是脚本参数记录、命令快照或运行 metadata -> 放 `experiments/<experiment_id>/`, 不放 `configs/`。

## 顶层结构

```text
configs/
  audit/
  data/
    downloads/
    builds/
  third_party/
  environment_ml_optional.yml
```

## 子目录职责

- `audit/`: audit 规则文件, 如 diagnosis labels、denominator schema、tool version lock 和 resource budget。
- `data/downloads/`: raw 数据下载源配置, 例如 RCSB smoke 下载配置。
- `data/builds/`: canonical dataset 构建配置, 例如从 dataset-local `raw/` 生成 `entries/` 和 `splits/` 的 R-group build 配置。
- `third_party/`: 第三方方法的 original protocol、audit protocol/status 记录、blocked/pending resource policy。
- `environment_ml_optional.yml`: 标准 Conda environment 文件, 按 Conda 生态格式维护, 不要求写入本项目的 `schema_version` / `schema_path`。
- 单次实验的 failed candidate、feedback、baseline、repair、eval summary 配置应进入 `experiments/<experiment_id>/configs/resolved/`。

## 配置路径规则

- 项目级配置不应默认写入具体 `outputs/<experiment_id>/`; 单次运行路径应进入 `experiments/<experiment_id>/configs/resolved/`。
- 运行前应将实际 resolved config 复制或生成到 `experiments/<experiment_id>/configs/resolved/`。
- 配置里的运行产物路径应落在对应 `outputs/<experiment_id>/`。
- 配置里的实验资产、命令快照、resolved config 和 metadata 应落在 `experiments/<experiment_id>/`。
- 第三方 output capture 使用 `captured_outputs/`; normalized 或转换结果使用 `processed/normalized_samples/`。
- split manifest 使用 `data/datasets/<dataset_id>/splits/<split_id>.json`。

## Config schema refs

保留在 `configs/audit/`, `configs/data/`, `configs/third_party/` 的配置文件应在文件顶部写入 `schema_version` 和 `schema_path`, 指向 `schemas/configs/` 下对应 schema。`configs/environment_ml_optional.yml` 是 Conda environment 文件例外, 按 Conda 格式维护。config schema 只定义配置文件本身的格式; 第三方 audit 跑完后生成的 metadata/output schema 仍见 `schemas/third_party_audit/`。

具体映射见 `schemas/README.md` 的 `configs` 小节。

## 第三方 audit schema refs

第三方 resolved audit protocol 中的 `metadata_schemas` 使用以下 key 到 schema path 的映射。实际协议只需要列出该方法会生成或消费的 metadata 类型, 但已生成的 JSON / JSONL metadata 必须写入同一组 `schema_version` 和 `schema_path`。

| `metadata_schemas` key | schema path |
| --- | --- |
| `run_metadata` | `schemas/third_party_audit/run/run_metadata_v0_1.json` |
| `output_manifest` | `schemas/third_party_audit/run/output_manifest_v0_1.json` |
| `sample_metadata` | `schemas/third_party_audit/samples/failure_sample_metadata_v0_1.json` |
| `stage_attrition` | `schemas/third_party_audit/attrition/stage_attrition_v0_1.json` |
| `label` | `schemas/third_party_audit/diagnosis/label_v0_1.json` |
| `evaluator_tool_result` | `schemas/third_party_audit/diagnosis/evaluator_tool_result_v0_1.json` |
| `diagnosis_sanity` | `schemas/third_party_audit/diagnosis/diagnosis_sanity_v0_1.json` |
| `method_resource_check` | `schemas/third_party_audit/resources/method_resource_check_v0_1.json` |
| `blocker_log` | `schemas/third_party_audit/resources/blocker_log_v0_1.json` |

输出文件名、`schema_version` 和 `schema_path` 的完整对应关系见 `schemas/README.md`。

## 修改规则

- 修改 evaluation gate、denominator、label precedence、tool config 或 success definition 时, 必须同步更新相关 docs/report, 并在 `docs/EXPERIMENT_LOG.md` 记录。
- audit configs 当前若未通过 `analysis-frozen` gate, 只能用于 MVP sanity 或 draft protocol, 不能用于正式 failure prevalence claim。
- 历史日志、output metadata 或 migration manifest 中保留的旧 `configs/...` 路径是迁移前 provenance, 不代表当前推荐放置位置。
