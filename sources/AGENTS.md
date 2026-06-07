# AGENTS.md

## sources 目录协作规则

- 本目录是文献和检索证据缓存, 不是 canonical data、实验输出或第三方源码目录。
- 不要把 `sources/` 下的 PDF / TXT / research JSON 当作 `data/datasets/` 输入, 除非另有明确的数据构建计划和 license/access 记录。
- 新增来源时保留可核验 provenance: DOI、arXiv ID、URL、检索 query、检索日期、数据库或工具名称。
- 不伪造引用、不伪造检索结果、不把未核验来源写成已验证结论。
- research JSON / XML 默认是外部检索原始记录, 不强行写入本项目 `schema_version` / `schema_path`; 若要长期作为项目自有结构化 metadata 读取, 先在 `schemas/` 下补 schema。
- 大型数据包、第三方 checkpoint、受限数据和不可再分发资源不放入本目录。
- 将来源用于论证时, 在 `docs/report/` 或 `docs/EXPERIMENT_LOG.md` 中引用对应文件路径和关键来源信息。
