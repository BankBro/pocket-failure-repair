# 第三方 Failure Audit 第一阶段 MVP Checklist 与 Agent 任务拆分

日期: 2026-06-03
状态: `phase1_mvp_assets_prepared`, `真实输出 audit 尚未执行`, `analysis-frozen gate 尚未通过`

## 1. 本轮目标边界

本轮从计划推进到可执行资产和小规模真实输出 audit 准备。已完成候选方法 feasibility table、数据 / dataset view / split / leakage 台账、第三方资源阻塞记录、失败样本 metadata schema、diagnosis label config、denominator/statistics schema、MVP checklist、后续 agent 任务拆分, 并为代表方法准备了最小可审计性试运行 wrapper。

本轮没有声称完成第三方真实 failure prevalence audit。DiffSBDD 和 DiffLinker 只完成官方 repo/checkpoint 准备、wrapper dry-run metadata 和 stage attrition dry-run。因为方法专用 PyTorch/PyG/Lightning 环境尚未创建, 真实 inference 未执行。任何正式 labeling、near-miss 判定或 prevalence 统计仍必须等待 analysis-frozen gate。

## 2. 关键产物清单

### 2.1 全局 audit 配置与 schema

| 产物 | 路径 | 状态 | 用途 |
|---|---|---|---|
| Resource budget config | `configs/audit/resource_budget_v1.yaml` | 已创建 | 固定第一阶段下载、存储、环境、运行预算和 blocking policy |
| Diagnosis label config draft | `configs/audit/diagnosis_label_config_v0_1.yaml` | 已创建, draft-ready | 固定 primary/secondary labels、evaluability、precedence、near-miss 草案 |
| Denominator/statistics schema draft | `configs/audit/denominator_statistics_schema_v0_1.yaml` | 已创建, draft-ready | 固定 denominator、stage attrition、prevalence、bootstrap 和 co-occurrence 口径草案 |
| Tool versions lock draft | `configs/audit/tool_versions.lock` | 已创建, draft-ready | 记录 `pfr` / `pfr-eval-tools` 环境与正式 PLIP/Vina 使用边界 |
| Sample metadata schema | `schemas/audit/third_party_failure_sample_metadata_v0_1.json` | 已创建 | 约束 `samples.jsonl` 行结构 |
| Run metadata schema | `schemas/audit/third_party_run_metadata_v0_1.json` | 已创建 | 约束 `run_metadata.json` |
| Stage attrition schema | `schemas/audit/third_party_stage_attrition_v0_1.json` | 已创建 | 约束 `stage_attrition.json` |
| Label schema | `schemas/audit/third_party_label_schema_v0_1.json` | 已创建, draft-ready | 约束未来 `labels.jsonl`; 尚未 frozen |

### 2.2 方法与资源台账

| 产物 | 路径 | 状态 | 用途 |
|---|---|---|---|
| Feasibility table JSON | `outputs/20260603-01-third-party-failure-audit-mvp/metadata/method_feasibility_table_v1.json` | 已创建 | 8 个候选方法的可行性 / 可审计性 / 阻塞 / tier 记录 |
| Feasibility table CSV | `outputs/20260603-01-third-party-failure-audit-mvp/metadata/method_feasibility_table_v1.csv` | 已创建 | 表格版, 便于论文和人工审阅 |
| Resource blocker log | `outputs/20260603-01-third-party-failure-audit-mvp/metadata/resource_blocker_log_v1.jsonl` | 已创建 | 记录 Google Drive 未知大小、license、环境等阻塞 |
| Artifact registry | `outputs/20260603-01-third-party-failure-audit-mvp/metadata/artifact_registry_v1.json` | 已创建 | 记录 repo/checkpoint/source/license/checksum/release tier |
| Audit asset hash manifest | `outputs/20260603-01-third-party-failure-audit-mvp/metadata/audit_asset_hash_manifest_v1.json` | 已创建 | 记录本轮关键轻量资产和 checkpoint hash |

### 2.3 数据 / view / split / leakage 台账

| 产物 | 路径 | 状态 | 用途 |
|---|---|---|---|
| Raw dataset manifest | `data/templates/third_party_audit/raw_dataset_manifest_v1.json` | 已创建 | 记录 CrossDocked、Binding MOAD、repo examples 的获取状态 |
| Dataset view manifest | `data/templates/third_party_audit/dataset_view_manifest_v1.json` | 已创建 | 记录 DiffSBDD/DiffLinker/Pocket2Mol/TargetDiff example view |
| Split registry template | `data/templates/third_party_audit/split_registry_template_v1.json` | 已创建 | 固定 split registry 字段和 example-only split |
| Leakage checklist | `data/templates/third_party_audit/leakage_checklist_v1.json` | 已创建 | 固定 PDB/complex/protein/ligand/scaffold/checkpoint training-data 检查 |

### 2.4 第三方方法配置和 wrapper

| 方法 | 产物 | 路径 | 状态 |
|---|---|---|---|
| DiffSBDD | original protocol config | `configs/third_party/diffsbdd_original_protocol.yaml` | 已创建 |
| DiffSBDD | audit protocol config | `configs/third_party/diffsbdd_audit_protocol.yaml` | 已创建 |
| DiffSBDD | wrapper | `scripts/third_party/run_diffsbdd_instrumented.py` | 已创建, py_compile 通过, dry-run 通过 |
| DiffLinker | original protocol config | `configs/third_party/difflinker_original_protocol.yaml` | 已创建 |
| DiffLinker | audit protocol config | `configs/third_party/difflinker_audit_protocol.yaml` | 已创建 |
| DiffLinker | wrapper | `scripts/third_party/run_difflinker_instrumented.py` | 已创建, py_compile 通过, dry-run 通过 |
| Pocket2Mol | audit protocol config | `configs/third_party/pocket2mol_audit_protocol.yaml` | 已创建, blocked_pending_user_decision |
| TargetDiff | audit protocol config | `configs/third_party/targetdiff_audit_protocol.yaml` | 已创建, blocked_pending_user_decision |
| 通用 | stage attrition summary | `scripts/audit/summarize_stage_attrition.py` | 已创建, py_compile 通过, dry-run summary 通过 |

### 2.5 第三方 repo 与 checkpoint 准备

| 方法 | Repo local path | Commit | License | Checkpoint 状态 |
|---|---|---|---|---|
| DiffSBDD | `third_party/diffsbdd` | `5d0d38d16c8932a0339fd2ce3f67ade98bbdff27` | MIT | Zenodo `crossdocked_fullatom_cond.ckpt` 已下载, SHA256 `07f86764bf569aafbc40a9c15fc02de8e2550437dd0f17f657eab3abe66c372c` |
| DiffLinker | `third_party/difflinker` | `fafbe47afe6cf068e9e1b23e7145377fb0f89f89` | MIT | Zenodo `pockets_difflinker_full.ckpt` 已下载, SHA256 `695ef7d634c09db4b9635c4e5efebad23385b8432f0687b6eae5e726ba7883f9` |
| Pocket2Mol | `third_party/pocket2mol` | `836a0c4ce487297ad24bc54ac2ebd163de13242c` | MIT | Google Drive checkpoint size unknown, 未下载 |
| TargetDiff | `third_party/targetdiff` | `142f1eb7178480d435fe0b8cb95a99beb48997c7` | MIT | Google Drive checkpoint/data size unknown, 未下载 |

注意: `.gitignore` 已更新, `third_party/*`, `*.ckpt`, `*.pt`, `*.pth` 和第三方 MVP 输出中的 captured/log 运行产物被忽略, 防止提交第三方源码、大 checkpoint、方法输出和日志。`third_party/README.md` 作为说明文件保留。

## 3. MVP checklist

### 3.1 候选方法与资源

- [x] 收集 6-8 个候选方法, 每项有 repo / paper / checkpoint / data / inference evidence。
- [x] 完成 `method_feasibility_table_v1`。
- [x] 记录 `resource_budget_config_version`。
- [x] 选出第一轮优先方法: DiffSBDD、DiffLinker, 以及 blocked/resource-decision 后的 Pocket2Mol 或 TargetDiff。
- [x] 每个方法有 `decision_tier`, `final_status`, `run_boundary_label`。
- [x] 每个阻塞有 `failure_type`, `attempted_source`, `evidence`, `fallback`, `decision`, `risk_note`。
- [x] 只下载官方、公开、规模明确且低于预算的 Zenodo checkpoint。
- [x] 未下载 Google Drive/未知大小资源。

### 3.2 数据, split 与 leakage

- [x] Raw dataset manifest template 已固定。
- [x] Dataset view manifest template 已固定。
- [x] Split registry template 已固定。
- [x] Leakage checklist 已固定。
- [x] `training_data_unknown` 与 `leakage_check_status=unknown_risk` 规则已应用到 example views。
- [ ] 正式 clean audit 的 raw/view/split checksum 尚未冻结。
- [ ] PDB/protein/ligand/scaffold overlap 尚未执行, 因本轮只做 example-output-capture sanity 准备。

### 3.3 代码, patch 与插桩

- [x] DiffSBDD output capture wrapper 已创建。
- [x] DiffLinker output capture wrapper 已创建。
- [x] Wrapper 记录 run metadata、sample metadata、output manifest 和 logs path。
- [x] Wrapper 标记 `algorithm_changed=false`, 不修改第三方算法源码。
- [x] Dry-run 已生成 `run_metadata.json`, `samples.jsonl`, `stage_attrition.json`。
- [ ] 方法专用 PyTorch/PyG/Lightning 环境尚未创建。
- [ ] 真实 inference 尚未运行。
- [ ] DiffSBDD raw invalid / dropped attempt 的精细 rejected reason 仍需 patch 或后处理。
- [ ] DiffLinker NaN retry / parse/read failure 的精细 tool failure 仍需 patch 或后处理。

### 3.4 Diagnosis 与统计 draft-ready gate

- [x] `label_schema` 草案已完成。
- [x] `label_config` 草案已完成。
- [x] primary labels / secondary labels / precedence hierarchy 草案已完成。
- [x] evaluability states 草案已完成。
- [x] denominator 与 attrition table 草案已完成。
- [x] inclusive vs evaluable-only、sample-weighted vs method-weighted、bootstrap/co-occurrence 计划草案已完成。
- [x] sanity-only 边界已写入 config。
- [ ] Analysis-frozen gate 尚未通过。
- [ ] 正式 label_config hash 尚未计算。
- [ ] tool_versions 对方法专用 env 尚未冻结。
- [ ] sanity set 尚未运行标签脚本验证 missing/tool/pipeline/not_evaluable 不被静默删除。

### 3.5 第一阶段 MVP 真实 output audit 执行 readiness

- [x] DiffSBDD 和 DiffLinker 已具备最小 trial config + wrapper + checkpoint + dry-run metadata。
- [x] Pocket2Mol 和 TargetDiff 已有 repo + protocol config + blocker decision path。
- [x] dry-run stage attrition 证明 metadata pipeline 可生成 denominator rows。
- [ ] 真实 output audit run 尚未执行。
- [ ] labels.jsonl 和 label_summary.json 尚未生成。
- [ ] near-miss MVP evidence 尚不存在。
- [ ] 不能声称第一阶段真实 audit 完成。

## 4. 后续 agent 任务拆分

### Agent A: Method environment setup agent

目标: 为 DiffSBDD 或 DiffLinker 创建方法专用 conda env, 固定版本并做 import / CLI smoke。

输入:

- `third_party/diffsbdd/environment.yaml`
- `third_party/difflinker/environment.yml`
- `configs/audit/resource_budget_v1.yaml`
- `configs/audit/tool_versions.lock`

交付:

- 方法环境创建日志。
- 更新后的 method-specific tool versions lock。
- `torch`, `pytorch_lightning`, `rdkit`, `openbabel`, `Bio` import/version check。
- 若失败, 追加 `resource_blocker_log_v1.jsonl`。

Gate:

- 环境安装单方法超过 4h 或需要非官方镜像时停止并记录 blocker。

### Agent B: DiffSBDD minimal output-capture trial agent

目标: 在方法 env 可用后运行 DiffSBDD 3RFM example 的最小 `n_samples=3-10` output-capture trial。

输入:

- `configs/third_party/diffsbdd_audit_protocol.yaml`
- `scripts/third_party/run_diffsbdd_instrumented.py`
- `third_party/diffsbdd/checkpoints/crossdocked_fullatom_cond.ckpt`

交付:

- `outputs/20260603-01-third-party-failure-audit-mvp/diffsbdd/<run_id>/run_metadata.json`
- `samples.jsonl`
- `output_manifest.json`
- `stage_attrition.json`
- stdout/stderr logs

Gate:

- 只做 output capture sanity, 不做正式 labels/prevalence。
- 若 wrapper 发现 final count 小于 budget, 保留 missing/pipeline rows, 不静默删除。

### Agent C: DiffLinker minimal output-capture trial agent

目标: 在方法 env 可用后运行 DiffLinker case-study `n_samples=3-10` output-capture trial。

输入:

- `configs/third_party/difflinker_audit_protocol.yaml`
- `scripts/third_party/run_difflinker_instrumented.py`
- `third_party/difflinker/models/pockets_difflinker_full.ckpt`

交付:

- 与 Agent B 相同结构的 run artifacts。
- SDF/XYZ 输出格式检查。
- stage-limited / linker-only 边界说明。

Gate:

- 如果 anchors/linker_size 设置无法忠实表达 case study, 不改 sampling 规则来追结果, 只记录 failure/blocker。

### Agent D: Diagnosis sanity agent

目标: 用现有 smoke/smoke-plus/control samples 和 dry-run missing-output rows 验证 label schema、not_evaluable、tool_failure、pipeline_failure、manual adjudication skeleton。

输入:

- `configs/audit/diagnosis_label_config_v0_1.yaml`
- `schemas/audit/third_party_label_schema_v0_1.json`
- dry-run `samples.jsonl`

交付:

- sanity-only `labels.jsonl`
- sanity summary
- 是否保留 missing/tool/pipeline/not_evaluable rows 的证明
- 如需改阈值, 新版本 label_config 草案

Gate:

- 不把 sanity-only labels 写入正式 third-party prevalence。

### Agent E: Resource decision scout agent

目标: 在不下载未知大小 Google Drive 文件的前提下, 尝试用官方 API/页面/metadata 估计 Pocket2Mol/TargetDiff checkpoint 和 data size。

输入:

- `configs/third_party/pocket2mol_audit_protocol.yaml`
- `configs/third_party/targetdiff_audit_protocol.yaml`

交付:

- size estimate evidence。
- 如果仍未知, 保持 `blocked_pending_user_decision`。
- 如果明确低于预算且无需登录, 可建议下一步下载, 但不自动执行超过本轮授权边界的未知资源。

Gate:

- 需要登录、非官方镜像或 size 仍未知时停止。

### Agent F: Documentation/status agent

目标: 每个 gate 后追加 `docs/EXPERIMENT_LOG.md`, 并保持 `docs/STATUS.md` 简短。

交付:

- 每阶段日志条目。
- STATUS 当前阶段快照。
- 不把 dry-run 或 selected/final-only evidence 写成 raw prevalence。

## 5. 当前阻塞项

1. `pfr` 与 `pfr-eval-tools` 当前都缺少第三方方法 inference 需要的 PyTorch/PyG/Lightning 组合, 因此未执行真实 DiffSBDD/DiffLinker inference。
2. Pocket2Mol 与 TargetDiff 的核心 checkpoint/data 位于 Google Drive 且当前大小未知, 按 resource budget policy 标记 `blocked_pending_user_decision`, 未下载。
3. MolCRAFT 为 CC-BY-NC-SA 4.0 NonCommercial/ShareAlike, 不作为默认第一阶段 MVP。
4. 3DLinker license 不可见, 标记 `blocked_pending_user_decision`, 未 clone/run。
5. Analysis-frozen gate 未通过, 因此没有 formal labels、prevalence、near-miss evidence 或 repair benchmark sample count。

## 6. 推荐下一步

优先顺序:

1. 用 tmux/单独 agent 创建 DiffSBDD 方法环境, 因其 SDF 输出和 SBDD/local-edit 任务最贴合。
2. 环境可用后运行 DiffSBDD example `n_samples=3-10` output-capture trial, 只作为 output-capture sanity。
3. 再创建 DiffLinker 环境并运行 case-study trial, 单独报告 linker/stage-limited 边界。
4. 用 dry-run + 实际 output rows 跑 diagnosis sanity, 证明 not_evaluable/missing/tool/pipeline rows 不被静默删除。
5. 若要推进 Pocket2Mol/TargetDiff, 先解决 Google Drive 资源大小和许可/登录问题。
