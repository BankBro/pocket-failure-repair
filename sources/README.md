# sources 目录管理说明

`sources/` 保存文献、网页、检索结果和人工调研材料的原始证据缓存。它用于支撑 `docs/plan/`, `docs/report/`, `docs/STATUS.md` 和 `docs/EXPERIMENT_LOG.md` 中的可追溯结论。

## 内容范围

- 论文 PDF、从 PDF 提取的 TXT、官方文档快照或链接记录。
- 学术检索、GitHub 检索、OpenAlex / Crossref / Semantic Scholar / arXiv 等查询结果的 JSON / XML。
- 人工调研 notes、检索 summary 或与文献矩阵相关的轻量证据文件。

## 不属于这里的内容

- canonical dataset: 放 `data/datasets/<dataset_id>/`。
- 实验输出、metrics、figures、logs: 放 `outputs/<experiment_id>/`。
- 实验命令、resolved config、run metadata: 放 `experiments/<experiment_id>/`。
- 第三方仓库、checkpoint 或 method code: 放 `third_party/` 或按规则记录 blocker。

## 记录要求

- 新增来源时, 文件名应尽量包含日期、来源或论文标识, 例如 `research_YYYYMMDD_<source>_<topic>.json` 或 `<method>_<arxiv_id>.pdf`。
- 能记录 DOI、arXiv ID、URL、检索 query、检索日期、数据库名称或工具名称时, 应保留在文件内容或相邻说明中。
- `sources/` 中的 research JSON / XML 是检索 provenance, 不默认要求写项目 schema refs; 若将来把某类来源提升为项目自有结构化 metadata, 再在 `schemas/` 下定义 schema。
- 结论不要只写在 `sources/`; 需要进入项目主线的判断应整理到 `docs/report/` 或 `docs/EXPERIMENT_LOG.md`。
