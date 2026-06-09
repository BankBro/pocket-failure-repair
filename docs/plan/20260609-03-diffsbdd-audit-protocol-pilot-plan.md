# DiffSBDD 官方数据集审计协议 pilot 计划

日期: `2026-06-09`

状态: `planned`

experiment_name: `diffsbdd-audit-protocol-pilot`

experiment_id: `20260609-03-diffsbdd-audit-protocol-pilot`

## 结论边界

本计划冻结下一轮 DiffSBDD 审计 pilot 的实验协议. 这轮不再以 README 单 pocket `3rfm` 作为主实验, 而是进入 DiffSBDD 官方使用的数据集 test view 上直接生成和审计输出.

本计划仍是 pilot, 不是 formal failure prevalence audit, 不是官方论文完整复现, 不是 cross-method comparison, 也不是 repair benchmark result. 它要验证的是: 在官方数据集 test split, 官方推荐采样流程和本项目统一 evaluator 下, 是否能稳定记录 raw attempt denominator, candidate / selected / final 样本, evaluator 输出, diagnosis 标签和 gate 结果.

## 依据

本计划的冻结规则来自以下本地材料:

- DiffSBDD README: `third_party/diffsbdd/README.md`.
- DiffSBDD 数据集处理代码: `third_party/diffsbdd/process_bindingmoad.py`, `third_party/diffsbdd/process_crossdock.py`.
- DiffSBDD test-set 采样代码: `third_party/diffsbdd/test.py`.
- DiffSBDD 单 pocket 采样代码: `third_party/diffsbdd/generate_ligands.py`.
- DiffSBDD 工具函数: `third_party/diffsbdd/utils.py`.
- DiffSBDD full-atom conditional 配置: `third_party/diffsbdd/configs/moad_fullatom_cond.yml`, `third_party/diffsbdd/configs/crossdock_fullatom_cond.yml`.
- DiffSBDD 官方预计算 Binding MOAD split: `third_party/diffsbdd/data/moad_train.txt`, `third_party/diffsbdd/data/moad_val.txt`, `third_party/diffsbdd/data/moad_test.txt`.
- DiffSBDD CrossDocked split 辅助清单: `third_party/diffsbdd/data/timesplit_no_lig_or_rec_overlap_train`, `third_party/diffsbdd/data/timesplit_no_lig_or_rec_overlap_val`, `third_party/diffsbdd/data/timesplit_test`.
- DiffSBDD 论文文本: `sources/papers_20260602/diffsbdd_2210.13695.txt`.
- 阶段 1 官方协议摘录: `experiments/20260608-01-diffsbdd-original-protocol-sanity/metadata/official_protocol_excerpt.md`.
- 统一评估流水线计划: `docs/plan/20260608-03-unified-evaluation-pipeline-alignment-plan.md`.
- schema-aware writer 自动化计划: `docs/plan/20260609-02-schema-aware-json-writer-automation-plan.md`.

关键依据如下:

- 官方 README 的 test-set 采样入口是 `python test.py <checkpoint>.ckpt --test_dir <bindingmoad_dir>/processed_noH/test/ --outdir <output_dir> --sanitize`.
- `test.py` 默认 `n_samples=100`, `batch_size=120`, `MAXITER=10`, `MAXNTRIES=10`.
- `test.py` 对每个 pocket 先请求一批 raw molecules, 再用 `process_molecule` 处理, 收集有效分子, 直到有效分子数量达到 `n_samples` 或超过迭代上限.
- 论文 Section 3 相关实验每个 pocket 目标约为 100 个生成配体; exact number 可能因方法和处理流程略有变化.
- 论文采样时按数据集调整 ligand size 分布均值: CrossDocked 使用 `n_nodes_bias=5`, Binding MOAD 使用 `n_nodes_bias=10`.
- Binding MOAD 官方处理脚本默认使用预计算 split, 本地 `moad_test.txt` 当前包含 130 个 test pocket id.
- CrossDocked 官方处理脚本依赖原始 `split_by_name.pt`; 当前工作区尚无完整 processed CrossDocked test 目录.

## 本轮选择的数据集和 pocket

### 主轨道

本轮 pilot 主轨道冻结为:

- dataset: `Binding MOAD`.
- representation: `full-atom`.
- model mode: `pocket_conditioning`.
- checkpoint: `moad_fullatom_cond.ckpt`.
- test split source: `third_party/diffsbdd/data/moad_test.txt`.
- processed test input: `<bindingmoad_dir>/processed_noH_full/test/` 或等价的 official DiffSBDD processed full-atom no-H test directory.

选择 Binding MOAD 作为第一条直接数据集审计轨道的原因:

- 官方 README 的 test-set 示例直接指向 Binding MOAD processed test 目录.
- 官方仓库自带 Binding MOAD 预计算 split 清单.
- 论文报告了 Binding MOAD full-atom conditional 模型结果.
- Binding MOAD split 在论文中按 EC Number main class 分割, 比继续用单个 README 示例更接近数据集级审计.

当前本地只已有 `crossdocked_fullatom_cond.ckpt`, 尚未见 `moad_fullatom_cond.ckpt`. 因此执行前必须先做 resource check: 官方 Zenodo checkpoint 是否可访问, license 是否清楚, size 是否在预算内, sha256 是否记录, checkpoint 是否与 Binding MOAD full-atom conditional 配置匹配. 未通过前不得启动 inference.

### pilot subset

pilot subset 冻结为 `moad_test.txt` 官方顺序中的前 20 个 pocket. 不人工挑选, 不按结果好坏筛选, 不替换失败 pocket.

冻结列表:

| index | case_id |
|---:|---|
| 0 | `5NDU-bio2_8V2:B:201` |
| 1 | `6PB9-bio1_PAM:A:301` |
| 2 | `2GM1-bio1_2AZ:A:371` |
| 3 | `3K3B-bio1_L31:A:371` |
| 4 | `3L9H-bio1_EMQ:A:601` |
| 5 | `2UYI-bio1_K02:A:604` |
| 6 | `5NCF-bio2_8T5:B:204` |
| 7 | `3F7H-bio2_419:B:1` |
| 8 | `1LT6-bio2_GAA:M:104` |
| 9 | `3F7I-bio1_G13:A:1` |
| 10 | `1EEI-bio1_GAA:G:507` |
| 11 | `2PG2-bio1_K01:A:604` |
| 12 | `1FD7-bio1_AI1:H:104` |
| 13 | `1YRS-bio2_L47:B:603` |
| 14 | `2PG2-bio1_K01:B:604` |
| 15 | `2VL8-bio1_CTS:A:1544` |
| 16 | `1J6Z-bio1_RHO:A:1381` |
| 17 | `3KEN-bio1_ZZD:A:370` |
| 18 | `1LT6-bio1_GAA:H:104` |
| 19 | `2FL6-bio2_N5T:B:605` |

如果任一 pocket 的 processed PDB, reference SDF 或 pocket residue txt 缺失, 本轮不得自动换成下一个 pocket. 应记录 blocker 或 data coverage issue, 再决定是否重新处理官方数据.

### full test view

pilot 通过后, 同一协议直接扩展到 `moad_test.txt` 的全部 130 个 test pockets. full test view 不在本计划中直接声明正式失败率; 只有 formal 前置条件全部满足后, 才允许进入正式分布分析.

### CrossDocked 第二轨道

CrossDocked 是 DiffSBDD 使用的另一个核心数据集, 且本地已有 `crossdocked_fullatom_cond.ckpt`. 但当前工作区没有完整 `processed_crossdock_noH_full/test/` 或原始 `split_by_name.pt` 处理结果. 因此 CrossDocked 本轮冻结为第二轨道, 不作为 `20260609-03` pilot 主执行目标.

CrossDocked 轨道进入执行前必须满足:

- 原始 CrossDocked / Pocket2Mol 数据来源, license, size 和 checksum 已记录.
- `split_by_name.pt` 可追溯到官方或论文一致来源.
- `process_crossdock.py --no_H` 处理日志和输出 checksum 已记录.
- 使用 `crossdocked_fullatom_cond.ckpt`.
- 采样时使用 `n_nodes_bias=5`.
- test split 与 checkpoint training split 的 leakage 状态已记录.

## seed 和采样预算

### 每个 case 的 seed

本轮 pilot 每个 pocket 只使用 1 个 seed:

```text
seeds = [0]
```

理由:

- 官方论文以每个 pocket 约 100 个生成配体作为主要统计单位, 不是多 seed 平均.
- `test.py` 的一次 pocket run 已经通过 100 个 final samples 表达随机生成分布.
- 多 seed 会把 pilot 从 20 pocket x 100 final samples 扩大到数倍, 先不作为第一轮直接数据集审计预算.

如果需要复核随机性, 后续可在通过 pilot 后新增固定 sentinel pockets 的 seed `1` 和 `2`, 但这些结果必须单独标注为 reproducibility check, 不混入本轮主 denominator.

### 每个 seed 的 raw attempts 和 final samples

本轮采用 official `test.py` 风格的 valid-target loop, 而不是 `generate_ligands.py` 的固定 request count.

冻结参数:

| 参数 | Binding MOAD pilot 值 | 来源 / 理由 |
|---|---:|---|
| `n_samples` | `100` | `test.py` 默认值, 论文每 pocket 约 100 个配体 |
| `batch_size` | `120` | `test.py` 默认值 |
| `MAXITER` | `10` | `test.py` 常量 |
| `MAXNTRIES` | `10` | `test.py` 常量 |
| `sanitize` | `true` | README test-set 命令包含 `--sanitize` |
| `relax` | `false` | README test-set 命令未启用 |
| `all_frags` | `false` | 默认保留 largest fragment |
| `timesteps` | `null` | 使用 checkpoint / config 默认 diffusion steps |
| `n_nodes_bias` | `10` | 论文 Section 3 Binding MOAD 设置 |
| `n_nodes_min` | `0` | `test.py` 默认值 |
| `fix_n_nodes` | `false` | 论文主采样使用 size distribution + bias, 不固定 reference atom count |
| `resamplings` | `10` | `test.py` 默认值, conditional model 中通常不影响 |
| `jump_length` | `1` | `test.py` 默认值 |

raw attempt denominator 按真实请求数记录:

```text
raw_attempts_per_pocket_seed = batch_size * n_batches_requested
n_batches_requested in [1, 10]
raw_attempt_cap_per_pocket_seed = 1200
final_samples_target_per_pocket_seed = 100
```

例如某 pocket 第一批 120 个 raw attempts 中至少 100 个可以处理成 valid molecule, 则:

```text
N_raw_attempt = 120
N_processed_valid_candidate >= 100
N_selected = 100
N_final = 100
N_rejected_for_budget = N_processed_valid_candidate - 100
```

如果第一批不足 100 个 valid molecule, 继续请求下一批 120 个 raw attempts, 直到 `N_processed_valid_candidate >= 100` 或达到 `MAXITER=10`. 若达到上限仍不足 100, 该 pocket/seed 标为 `generation_incomplete`, 记录实际 denominator, 暂停或降级解释, 不自动补别的 pocket.

pilot 总目标:

```text
N_cases = 20
N_seeds_per_case = 1
N_final_target_total = 20 * 1 * 100 = 2000
N_raw_attempt_min_total = 20 * 1 * 120 = 2400
N_raw_attempt_cap_total = 20 * 1 * 1200 = 24000
```

## denominator 记录

主 denominator 只能来自 sample metadata, 不能从 SDF 文件数量倒推.

每个 raw attempt 都必须在 `samples.jsonl` 中有一行, 即使这个 attempt 没有可写 SDF. 对每行至少记录:

- `sample_id`.
- `case_id`.
- `dataset_name`.
- `dataset_split`.
- `checkpoint_id`.
- `seed`.
- `batch_index`.
- `attempt_index_within_batch`.
- `attempt_index_within_case_seed`.
- `sample_role`.
- `raw_attempt_status`.
- `candidate_status`.
- `selection_status`.
- `final_status`.
- `paths`.
- `schema_version`.
- `schema_path`.

建议状态枚举:

| 字段 | 允许值 |
|---|---|
| `sample_role` | `raw_attempt`, `processed_candidate`, `selected_final`, `rejected_invalid`, `rejected_over_budget`, `missing_unobservable` |
| `raw_attempt_status` | `requested`, `generated_observable`, `generated_unobservable_none`, `batch_failed`, `not_reached_due_to_stop` |
| `candidate_status` | `not_processed`, `processed_valid`, `processed_invalid`, `processing_error` |
| `selection_status` | `selected_first_100_valid`, `not_selected_invalid`, `not_selected_over_budget`, `not_selected_incomplete_run` |
| `final_status` | `final_sdf_written`, `no_final_output_expected`, `missing_final_output`, `generation_incomplete` |

如果现有 `schemas/third_party_audit/sample_metadata_v0_1.json` 不能表达这些字段, 实施前新增 `sample_metadata_v0_2.json`, 并让 writer 从 schema 自动填充 `schema_version` 和 `schema_path`.

## captured / rejected / selected / final 保存方式

本轮不直接使用未改造的 `third_party/diffsbdd/test.py` 作为唯一执行入口, 因为原脚本只写 raw/processed SDF, 不能完整暴露每个 raw attempt 的 denominator 和 rejected 状态. 应新增项目 wrapper, 例如:

```text
scripts/third_party/run_diffsbdd_dataset_instrumented.py
```

该 wrapper 必须复刻 `test.py` 的采样循环和参数, 调用 DiffSBDD 官方模型 API, 但不得修改 DiffSBDD 核心 sampling, decoding, model weights, filtering, reranking, docking config 或 success definition.

每个 run 的目录结构冻结为:

```text
outputs/20260609-03-diffsbdd-audit-protocol-pilot/diffsbdd/<run_id>/
  run_metadata.json
  samples.jsonl
  output_manifest.json
  stage_attrition.json
  captured_outputs/
    raw_batches/<case_id>/batch_000.sdf
    raw_batches/<case_id>/batch_001.sdf
    stdout.txt
    stderr.txt
  processed/
    candidate_samples/<case_id>/
    rejected_samples/<case_id>/
    selected_samples/<case_id>/
    normalized_samples/<case_id>/
    receptors/
  manifests/
    dataset_subset_manifest.json
    checkpoint_manifest.json
    raw_attempt_manifest.json
    selected_final_manifest.json
  logs/
  evaluator/
  summaries/
```

保存规则:

- `captured_outputs/raw_batches/<case_id>/batch_*.sdf`: 保存每批 observable raw molecules. 如果模型返回 `None`, SDF 中没有对应分子, 但 `samples.jsonl` 中必须有对应 raw attempt 行.
- `processed/candidate_samples/<case_id>/`: 保存经过 `process_molecule` 后的 valid candidate molecule. candidate 数可大于 100.
- `processed/rejected_samples/<case_id>/`: 保存可序列化的 rejected molecule 和拒绝原因. 对不可序列化或 `None` 的 rejected attempt, 只在 metadata 中记录, 不伪造 SDF.
- `processed/selected_samples/<case_id>/`: 保存按 official order 选择的前 100 个 valid molecule.
- `processed/normalized_samples/<case_id>/`: 保存 evaluator 使用的 final SDF, 与 selected samples 一一对应.
- `stage_attrition.json`: 逐 pocket / seed 汇总 `N_raw_attempt`, `N_raw_observable`, `N_processed_valid_candidate`, `N_rejected_invalid`, `N_rejected_over_budget`, `N_selected`, `N_final`, `N_evaluable`, `N_tool_failure`.
- `output_manifest.json`: 记录全部输出文件的 relative path, size, sha256 和 artifact role.

`selected` 和 `final` 在本轮 pilot 中语义相同: final samples 是 selected samples 的 evaluator-ready normalized 版本. 仍保留两个目录, 是为了以后支持 reranking 或 top-k selection 时不改变下游 schema.

## evaluator 冻结

本轮继续使用统一评估流水线 v0.2:

- evaluator policy: `configs/audit/evaluator_policy_v0_2.yaml`.
- analysis-frozen gate: `configs/audit/analysis_frozen_gate_v0_2.yaml`.
- diagnosis label config: `configs/audit/diagnosis_label_config_v0_3.yaml`.
- receptor prep policy: `configs/audit/receptor_prep_policy_v0_1.yaml`.
- denominator config: `configs/audit/denominator_statistics_schema_v0_1.yaml`.
- tool versions lock: `configs/audit/tool_versions.lock`.

执行时应把这些配置复制到:

```text
experiments/20260609-03-diffsbdd-audit-protocol-pilot/configs/resolved/audit/
```

并把 hash 写入 `run_metadata.json`, evaluator input, labels, summaries 和 gate result.

环境冻结:

- 项目脚本, metadata writer, schema 校验和 summaries: `pfr`.
- DiffSBDD inference: `pfr-diffsbdd` 或独立 `pfr-diffsbdd-moad`, 不和 evaluator 混用.
- evaluator: `pfr-eval-tools`.

evaluator 输入必须使用 cleaned receptor:

```text
official processed receptor PDB
+ reference ligand SDF / ligand id
-> receptor preparation
-> cleaned receptor PDB
-> tool-specific inputs
```

Binding MOAD processed test PDB 可能已经删除 reference ligand, 但仍必须生成 receptor prep metadata, 记录 reference ligand 来源, HETATM 清理 / 复核结果, cleaned receptor sha256, Vina box 来源和 unresolved review count.

## formal 前置条件

以下条件全部满足前, 只能声明 pilot audit evidence, 不得声明 formal failure prevalence:

1. `moad_fullatom_cond.ckpt` 来自官方 Zenodo, checksum, size, license, access type 已记录.
2. Binding MOAD raw / processed 数据来源, license, size, checksum, processing command, processing log 已记录.
3. `moad_test.txt` checksum 已记录, processed test 目录中的 PDB / SDF / TXT 与 test split 清单一致.
4. checkpoint 与数据集配对: Binding MOAD checkpoint 只和 Binding MOAD test view 形成主结论; CrossDocked checkpoint 不混入 Binding MOAD formal denominator.
5. training data / leakage 状态已冻结: 至少要记录官方 split 规则, train/val/test 清单 checksum, processed train_smiles provenance 和 test pocket 是否出现在 train split.
6. raw attempt denominator 完整: 每个 requested attempt 都有 `samples.jsonl` 行, denominator 不依赖 SDF 文件数量.
7. wrapper 没有修改 DiffSBDD 核心模型, 采样, decoding, filtering, reranking, docking config 或 success definition.
8. receptor prep 无 unresolved HETATM review items.
9. evaluator configs, diagnosis label config, denominator policy, tool versions lock 都有 hash, 且传播到输出 metadata.
10. `analysis_frozen_gate_v0_2` 通过. 若进入 formal analysis, `internal_energy_unavailable_fraction` 使用 `formal_analysis` 阈值 `<= 0.05`, 不是 MVP sanity 的 `0.10`.
11. PLIP reference interaction recovery 仍作为 reference-relative 描述性证据, 除非另行冻结 required interactions.
12. Vina 只作为辅助 metric, 不作为唯一 success gate.
13. 输出 manifest 完整, 所有项目自有 JSON / JSONL 都写入 `schema_version` 和 `schema_path`.
14. pilot report 明确区分 `raw attempt view`, `selected final view`, `evaluable-only view`, 不混用分母.

## go/no-go resource check

执行 inference 前必须先完成 go/no-go resource check, 写入:

```text
experiments/20260609-03-diffsbdd-audit-protocol-pilot/metadata/method_resource_check.jsonl
```

resource check 至少覆盖:

- DiffSBDD repo commit 和 license.
- Binding MOAD checkpoint source, checkpoint size, sha256, access type.
- Binding MOAD raw download URL, compressed size, extracted size, license / terms.
- processed data output size estimate.
- `moad_test.txt` entry count 和 sha256.
- processed test PDB / SDF / TXT coverage.
- training data / leakage status.
- GPU availability, GPU memory, expected GPU hours.
- evaluator CPU time estimate.
- storage budget estimate.
- 是否需要 gated access, 付费, 登录, 联系作者或非官方镜像.

当前 resource budget 参考 `configs/audit/resource_budget_v1.yaml`:

- 单方法下载上限: `10 GB`.
- 单方法存储上限: `30 GB`.
- 单方法 MVP GPU 上限: `24 h`.
- 单方法 MVP CPU 上限: `24 h`.
- 不允许在未拍板时使用 gated data, 非官方镜像, paid resource 或联系作者.

如果 Binding MOAD raw + processed 数据超过预算, 本轮暂停, 记录 blocker. 不自动切到非官方 mirror 或缩小数据集伪装成官方数据集审计.

## run 编号

建议先拆成两个 run:

```text
r001_moad_resource_check_<configHash8>
r002_moad_test20_seed0_n100_bias10_<configHash8>
```

如果 r002 在前 3 个 pocket 就出现系统性 wrapper / evaluator 失败, 可以停止并保留 partial run, 不继续烧完整预算.

如果 r002 通过 gate, full test view 后续使用:

```text
r003_moad_test130_seed0_n100_bias10_<configHash8>
```

`r003` 不应在 `r002` report 完成前启动.

## 输出路径

实验资产:

```text
experiments/20260609-03-diffsbdd-audit-protocol-pilot/
  configs/resolved/
  metadata/
  scripts/
  manifests/
```

run 输出:

```text
outputs/20260609-03-diffsbdd-audit-protocol-pilot/diffsbdd/<run_id>/
```

报告路径:

```text
docs/report/20260609-04-diffsbdd-audit-protocol-pilot-report.md
```

如果实际执行和报告不是 2026-06-09 当天完成, 按 `docs/AGENTS.md` 的命名规则使用完成当天的日期和当天序号, 但中间的 `diffsbdd-audit-protocol-pilot` 保持一致.

完成后追加:

```text
docs/EXPERIMENT_LOG.md
```

必要时更新:

```text
docs/STATUS.md
```

## 暂停条件

出现任一情况立即暂停, 记录 blocker, 不自动绕过:

- `moad_fullatom_cond.ckpt` 无法从官方来源获取.
- checkpoint checksum 与记录不一致.
- checkpoint license 或访问条件不清.
- Binding MOAD 数据需要登录, 付费, 联系作者, 或只能从非官方镜像获取.
- 数据下载, 解压或 processed 输出预计超过 resource budget.
- processed test 目录无法与 `moad_test.txt` 对齐.
- 需要手工替换缺失 pocket, 删除困难 pocket, 或按结果筛选 pocket.
- 需要修改 DiffSBDD 核心 model, sampling, decoding, filtering, reranking, docking config 或 success definition.
- wrapper 无法记录每个 raw attempt denominator.
- receptor prep 存在 unresolved HETATM review items.
- evaluator config hash 未传播到 run metadata / labels / summaries / gate result.
- `internal_energy_unavailable_fraction` 超过当前 active phase 阈值.
- tool timeout 大面积发生, 导致 evaluator 结果主要反映工具失败而不是样本证据.
- 用户要求将 pilot 结果解释成 formal failure prevalence, official reproduction 或 repair benchmark result.

## 实施顺序

1. 创建 experiment 目录, resolved config, dataset subset manifest 和 resource check writer.
2. 获取或定位官方 `moad_fullatom_cond.ckpt`, 记录 checksum, size 和 license.
3. 获取或定位 Binding MOAD raw / processed 数据, 记录来源和 checksum.
4. 用官方 `process_bindingmoad.py` 生成或核验 `processed_noH_full/test/`.
5. 校验 `moad_test.txt` 前 20 个 pocket 的 PDB / SDF / TXT coverage.
6. 新增或改造 dataset-level DiffSBDD instrumented wrapper, 复刻 `test.py` 采样循环.
7. 若 sample metadata schema 不够表达 raw attempt 状态, 新增 schema 并接入 schema-aware writer.
8. 执行 `r002_moad_test20_seed0_n100_bias10_<configHash8>`.
9. 对 selected final samples 跑统一 evaluator v0.2.
10. 生成 summaries, denominator statistics, label summary, prevalence summary 和 gate result.
11. 生成 report, 只解释 pilot scope 内的结果和 blocker.
12. 通过 `pytest -q` 后再考虑 full test view `r003`.

## 预期产物检查表

每个 run 至少应有:

- `run_metadata.json`.
- `samples.jsonl`.
- `stage_attrition.json`.
- `output_manifest.json`.
- `captured_outputs/`.
- `processed/candidate_samples/`.
- `processed/rejected_samples/`.
- `processed/selected_samples/`.
- `processed/normalized_samples/`.
- `processed/receptors/`.
- `logs/`.
- `manifests/`.
- `evaluator/`.
- `summaries/`.

所有项目自有 JSON / JSONL / YAML metadata 必须写入 `schema_version` 和 `schema_path`, 明确例外只包括 Conda export, pip freeze 和外部工具原生输出.
