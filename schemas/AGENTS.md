# AGENTS.md

## schemas 目录协作规则

- 本目录只保存项目自有结构化 metadata / config 的字段规范, schema 文件本身使用 JSON Schema; 被约束的实例可以是 JSON、JSONL 或 YAML, 但本目录不保存实验数据、模型输出或分析结果。
- 修改 schema 前, 先确认它是否已经被 `outputs/**/metadata`, `experiments/**/metadata`, `docs/report/**` 或审计脚本引用。
- 已被历史实验使用的 schema 视为版本化合同, 不是可随意覆盖的一次性模板。除错别字、description 或纯说明性字段外, 不要静默改变旧版本语义。
- 不兼容变更应新增版本文件, 例如从 `v0_1` 升到 `v0_2`, 并保留旧版本; 旧实验继续指向旧 schema, 新实验再显式切换到新 schema。
- 改 required 字段、字段类型、字段含义、success / failure / attrition 统计口径, 或删除旧字段, 都属于不兼容变更。
- 第三方 audit schema 放在 `schemas/third_party_audit/` 下, 按 `run/`, `samples/`, `diagnosis/`, `attrition/`, `resources/` 分层; 文件名和 `schema_version` 省略重复的 `third_party_` 前缀, 例如 `output_manifest_v0_1`。
- 第三方 audit schema 的完整清单、用途和输出文件映射见 `schemas/README.md`; 不要在本文件重复维护长清单。
- config schema 放在 `schemas/configs/` 下, 用于约束 `configs/audit/`, `configs/data/`, `configs/third_party/` 中项目级配置文件自身的格式; 具体清单见 `schemas/README.md`。
- data config schema 与 `configs/data/` 保持同构分层: `schemas/configs/data/downloads/` 约束 raw 下载配置, `schemas/configs/data/builds/` 约束 canonical dataset 构建配置。
- data schema 放在 `schemas/data/` 下, 按 `catalog/`, `datasets/entries/`, `datasets/splits/`, `datasets/views/`, `datasets/manifests/{raw,entries,lineage}/` 分层; 不再使用旧式扁平 `schemas/data/dataset_*.json` 路径。
- 新增或修改 schema 后, 同步更新 `schemas/README.md` 中的用途说明。
- 新增项目自有 JSON / JSONL / YAML 时, 先复用已有 schema; 若现有 schema 不能表达, 先新增或升级 schema, 再写对应 metadata / config。
- 字段命名、required 字段、stage attrition 计数和 failure label 口径应与 `configs/audit/`, `configs/third_party/`, 相关实验 report 保持一致。
- 不要用 schema 单独声明实验成功、失败率或论文结论; schema 只定义 metadata 格式。
- 中文说明使用英文标点, 文件内容使用 UTF-8。
