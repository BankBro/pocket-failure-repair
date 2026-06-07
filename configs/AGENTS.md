# configs/AGENTS.md

## Agent 操作规则

- `configs/` 只保存项目级真实配置, 包括规则文件、数据构建配置和第三方方法状态/协议记录; 具体定义、例子和判断标准见 `configs/README.md`。
- 单次运行 resolved config 写入 `experiments/<experiment_id>/configs/resolved/`, 不长期保留在项目级 `configs/`。
- 保留在 `configs/audit/`, `configs/data/`, `configs/third_party/` 的配置文件应写入 `schema_version` 和 `schema_path`; config schema 映射见 `schemas/README.md` 的 `configs` 小节。
- 不要把绑定具体 `outputs/<experiment_id>/` 的 failed candidate、feedback、baseline、repair 或 eval summary 配置长期放在项目级 `configs/`。
- 不要把运行生成的 config snapshot 写入 `outputs/`。
- `configs/data/downloads/` 放 raw 数据下载源配置; `configs/data/builds/` 放 canonical dataset 构建配置, 不要把 data config 散放在 `configs/data/` 根下。
- 修改项目级配置默认输出路径时, 不要绑定某个具体 `outputs/<experiment_id>/`; 具体运行路径应写入 `experiments/<experiment_id>/configs/resolved/`。
- 第三方方法配置使用 `captured_outputs/`, 不使用 `raw_outputs/` 作为默认目录。
- 第三方 audit protocol 中的 `metadata_schemas` 应指向 `schemas/third_party_audit/{run,samples,attrition,diagnosis,resources}/...`, 不使用旧 `schemas/audit/third_party_*` 路径。
- 第三方 audit protocol 的 `metadata_schemas` key 到具体 schema path 的映射见 `configs/README.md`; 不要在本文件维护长清单。
- split 路径使用 `data/datasets/<dataset_id>/splits/<split_id>.json`, 不使用旧式 `data/splits/`。
- 修改 audit label、denominator、tool version、resource budget、evaluation gate 或 success definition 时, 必须记录边界, 并避免从 MVP sanity 输出声明 formal prevalence 或 repair benchmark 结果。
- Vina score 只能作为辅助 metric, 不能单独定义 success/failure。
- 遇到 license 不清、gated access、未知下载大小或非官方资源需求时, 配置应标注 blocker/pending, 不自动替换来源。
