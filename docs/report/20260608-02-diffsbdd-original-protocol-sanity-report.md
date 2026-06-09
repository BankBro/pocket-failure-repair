# DiffSBDD 原协议健全性与忠实度检查报告

experiment_id: `20260608-01-diffsbdd-original-protocol-sanity`

run_id: `r001_official_example_3rfm_seed0_78d8cd91`

日期: `2026-06-08`

## 结论

阶段 1 已完成一个 DiffSBDD 官方 README 3RFM 示例的原协议健全性与忠实度 sanity run. 结果支持以下有限结论: 本项目可以在官方 repo, 官方 Zenodo checkpoint, README 示例参数 `n_samples=20`, reference ligand `A:330` 下运行 DiffSBDD, 捕获输出, 保留 20 行 denominator metadata, 计算基础分子 sanity metrics, 并接通 evaluator/diagnosis metadata.

本报告不声明完整原论文复现, 不声明正式 failure prevalence, 不声明 cross-method comparison, 不声明 repair benchmark result.

## 做了什么

1. 阅读并摘录官方材料:
   - 官方论文: Structure-based drug design with equivariant diffusion models, Nature Computational Science, DOI `10.1038/s43588-024-00737-x`.
   - 官方仓库 README 和代码: `third_party/diffsbdd/README.md`, `generate_ligands.py`, `test.py`, `lightning_modules.py`, `analysis/molecule_builder.py`, `analysis/metrics.py`, `analysis/docking.py`.
   - 协议摘录: `experiments/20260608-01-diffsbdd-original-protocol-sanity/metadata/official_protocol_excerpt.md`.
   - checklist: `experiments/20260608-01-diffsbdd-original-protocol-sanity/metadata/official_protocol_checklist.json`.

2. 完成运行前资源检查:
   - `decision=go`, 仅针对 README 3RFM 示例 run.
   - repo commit: `5d0d38d16c8932a0339fd2ce3f67ade98bbdff27`.
   - license: MIT.
   - checkpoint: `crossdocked_fullatom_cond.ckpt`.
   - checkpoint sha256: `07f86764bf569aafbc40a9c15fc02de8e2550437dd0f17f657eab3abe66c372c`.
   - checkpoint size: `17861341` bytes.
   - resource check: `experiments/20260608-01-diffsbdd-original-protocol-sanity/metadata/method_resource_check.jsonl`.

3. 执行官方示例 sanity run:
   - 输入: `third_party/diffsbdd/example/3rfm.pdb`.
   - pocket reference: `A:330`.
   - `n_samples=20`.
   - seed: `0`.
   - wrapper 只设置 seed, 捕获 stdout/stderr, 拆分 SDF, 写 metadata. 未修改 DiffSBDD sampling, decoding, filtering, reranking, docking config 或 success definition.

4. 记录环境:
   - DiffSBDD 推理环境: `pfr-diffsbdd`.
   - evaluator 环境: `pfr-eval-tools`.
   - 环境记录在 `experiments/20260608-01-diffsbdd-original-protocol-sanity/metadata/`.

## 主要结果

输出路径:

```text
outputs/20260608-01-diffsbdd-original-protocol-sanity/diffsbdd/r001_official_example_3rfm_seed0_78d8cd91/
```

generation/output capture:

- `exit_code=0`.
- `N_budget=20`.
- `N_raw_attempt_metadata=20`.
- `N_raw_captured=20`.
- `N_final=20`.
- `N_missing_output=0`.
- `N_pipeline_failure=0`.
- `samples.jsonl` 保留 20 行 sample metadata, denominator 不依赖 SDF 文件数推断.

基础 official-like molecular sanity metrics:

- `N_parsed=20`.
- `N_valid=20`.
- `N_connected=20`.
- `N_unique_connected_smiles=20`.
- `validity_over_budget=1.0`.
- `connectivity_over_valid=1.0`.
- `uniqueness_over_connected=1.0`.
- `novelty=null`, 因为 training SMILES / official train set provenance 未冻结.
- 结果文件: `official_like_metrics/basic_molecular_metrics.json`.

evaluator/diagnosis wiring:

- evaluator tool result rows: `100`.
- diagnosis sanity rows: `20`.
- tool status counts:
  - `rdkit::passed=20`.
  - `plip::passed=20`.
  - `vina::passed=20`.
  - `posebusters_mol::failed=19`.
  - `posebusters_dock::failed=19`.
  - `posebusters_mol::timeout=1`.
  - `posebusters_dock::timeout=1`.
- diagnosis evaluability:
  - `evaluable=19`.
  - `not_evaluable_tool_failure=1`, 对应样本 11 的 PoseBusters mol/dock timeout.

PoseBusters failure 和 timeout 只作为阶段 1 evaluator wiring evidence. 由于本阶段没有冻结正式 diagnosis protocol, 且部分 PoseBusters 检查依赖 reference/true ligand 或完整输入条件, 这些结果不能解释为 DiffSBDD 正式失败率.

后续 timeout 复查:

- 对原 timeout 样本 index `11` 使用更长等待重跑 PoseBusters.
- 内层 timeout 从 `30` 秒提高到 `300` 秒, 外层 shell 保护为 `420` 秒.
- `mol` 和 `dock` 均完成, 不再是 timeout.
- `mol` 结果: full pass 为 false, failed checks 为 `bond_lengths`, `mol_true_loaded`.
- `dock` 结果: full pass 为 false, failed checks 为 `bond_lengths`, `minimum_distance_to_organic_cofactors`, `volume_overlap_with_organic_cofactors`, `mol_true_loaded`, `most_extreme_clash_protein`, `not_too_far_away_inorganic_cofactors`, `not_too_far_away_waters`.
- retry summary: `summaries/posebusters_timeout300_retry_summary.json`.
- 原始 evaluator rows 保留原阶段 1 的 45 秒 timeout 策略事实, 不静默改写.

## 已记录的偏离

- 阶段 0 使用 `n_samples=3`; 阶段 1 已恢复 README 示例的 `n_samples=20`.
- 阶段 1 使用项目 wrapper 设置 seed 并捕获输出, 因而是 instrumented sanity run, 不是无包装的官方命令直接复现.
- 输出路径从 README 的 `example/3rfm_mol.sdf` 重定向到 `outputs/<experiment_id>/.../captured_outputs/generated.sdf`.
- `test.py` 官方风格测试子集没有运行. 原因是 processed test data, split 和 checksum 未获取或冻结.

## 当前 blocker 和风险

- 无 active blocker 阻止 README 3RFM 示例 sanity.
- `r002_official_like_test_subset` 已 defer, 因为完整测试数据来源, license, size, split 和 checksum 需要另行冻结.
- `training_data_status=training_data_unknown`, `leakage_check_status=unknown_risk`, 所以本阶段不能作为 clean-test 结论.
- PoseBusters 第 11 个样本的 `mol` 和 `dock` 检查在原 45 秒外层 timeout 下超时, 已记录为工具条件 evidence. 后续 300 秒内层 timeout 复查可以完成, 结果为 failed checks 而非 timeout.

## 验证

- 轻量 metadata 检查: 13 类 JSON/JSONL 文件, 150 个文件或行通过 required/const/schema ref 检查.
- RDKit sanity: 20 个 normalized SDF 均 parse ok, sanitize ok.
- 项目测试: `conda run -n pfr env PYTHONPATH=src pytest -q` -> `32 passed in 0.76s`.

## 下一步

1. 若要继续阶段 1 的 `test.py` 子集, 先冻结 processed test data 来源, split, checksum, license 和资源预算.
2. 进入阶段 2 前, 将本阶段偏离说明纳入 DiffSBDD audit protocol.
3. formal audit 前冻结 PoseBusters, RDKit, PLIP, Vina 和 labeling pipeline, 再谈 failure distribution 或 near-miss subset.
