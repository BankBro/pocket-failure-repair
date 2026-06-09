# DiffSBDD 阶段 1 官方协议摘录

experiment_id: `20260608-01-diffsbdd-original-protocol-sanity`

method: `DiffSBDD`

created_time: `2026-06-08T04:43:15Z`

## 结论边界

本摘录用于阶段 1 的原协议健全性与忠实度检查. 它只支持判断本项目是否能在接近官方 README 示例的设置下运行 DiffSBDD, 捕获输出, 保留分母并记录偏离. 它不支持完整原论文复现, 正式失败率, 跨方法比较或 repair benchmark 结论.

## 来源

- 官方论文: Schneuing 等, Structure-based drug design with equivariant diffusion models, Nature Computational Science 4, 899-909, 2024, DOI `10.1038/s43588-024-00737-x`.
- arXiv: `https://arxiv.org/abs/2210.13695`.
- 官方仓库: `https://github.com/arneschneuing/DiffSBDD`.
- 本地仓库: `third_party/diffsbdd`, commit `5d0d38d16c8932a0339fd2ce3f67ade98bbdff27`.
- checkpoint 记录: Zenodo `https://zenodo.org/records/8183747`.
- 本地 README 和代码: `third_party/diffsbdd/README.md`, `generate_ligands.py`, `test.py`, `lightning_modules.py`, `analysis/molecule_builder.py`, `analysis/metrics.py`, `analysis/docking.py`.

## 代码和 checkpoint

- 官方仓库 license: MIT, 本地 `third_party/diffsbdd/LICENSE` 已核查.
- 使用 checkpoint: `crossdocked_fullatom_cond.ckpt`.
- 本地路径: `third_party/diffsbdd/checkpoints/crossdocked_fullatom_cond.ckpt`.
- 官方来源: DiffSBDD README 指向 Zenodo record `8183747`.
- 本地 sha256: `07f86764bf569aafbc40a9c15fc02de8e2550437dd0f17f657eab3abe66c372c`.
- 本地大小: `17861341` bytes.
- 访问类型: public.

## 数据和输入

- 论文和 README 涉及两个主要 benchmark 数据来源: CrossDocked 和 Binding MOAD.
- README 的 de novo design 示例使用 `example/3rfm.pdb`, reference ligand `A:330`, checkpoint `checkpoints/crossdocked_fullatom_cond.ckpt`, `n_samples=20`.
- `utils.get_pocket_from_ligand` 将 pocket 定义为任一 residue atom 到 reference ligand atom 距离小于 8 angstrom 的标准氨基酸 residue 集合.
- 阶段 1 本轮只运行 README 3RFM 示例, 不获取或冻结完整 CrossDocked / Binding MOAD 测试数据.
- 训练数据和本项目样本泄漏状态仍为 `training_data_unknown` 和 `unknown_risk`. 因此本阶段不能作为 clean-test evidence.

## 生成参数

`generate_ligands.py` 的代码默认值:

- `n_samples`: 20.
- `batch_size`: 若未指定, 等于 `n_samples`.
- `num_nodes_lig`: 若未指定, 从条件大小分布采样.
- `all_frags`: false.
- `sanitize`: false.
- `relax`: false.
- `resamplings`: 10.
- `jump_length`: 1.
- `timesteps`: null, 即使用训练设置.
- `largest_frag`: true, 因为调用模型时传入 `largest_frag=not args.all_frags`.

README 3RFM 示例命令:

```bash
python generate_ligands.py checkpoints/crossdocked_fullatom_cond.ckpt --pdbfile example/3rfm.pdb --outfile example/3rfm_mol.sdf --ref_ligand A:330 --n_samples 20
```

阶段 0 MVP 实际设置:

- case: `3rfm`.
- seed: `0`.
- `n_samples`: 3.
- output capture wrapper: `scripts/third_party/run_diffsbdd_instrumented.py`.
- 结论边界: MVP sanity, 不声称官方协议复现.

阶段 1 r001 拟采用设置:

- case: `3rfm`.
- seed: `0`.
- `n_samples`: 20.
- `batch_size`: 未显式指定, 由 `generate_ligands.py` 设为 20.
- `sanitize`: false.
- `relax`: false.
- `all_frags`: false.
- `timesteps`: null.
- run_id: `r001_official_example_3rfm_seed0_78d8cd91`.

相对 README 示例的偏离:

- 输出路径重定向到 `outputs/20260608-01-diffsbdd-original-protocol-sanity/diffsbdd/<run_id>/captured_outputs/generated.sdf`.
- 使用项目 wrapper 设置 seed, 捕获 stdout/stderr, 写 run metadata, samples, output manifest 和 attrition.
- 不修改 DiffSBDD 采样, decoding, filtering, reranking, docking config 或 success definition.

## 后处理和过滤

- `generate_ligands.py` 加载模型后调用 `LigandPocketDDPM.generate_ligands`.
- 如果 `num_nodes_lig` 未提供, 模型从 pocket-conditioned size distribution 采样 ligand atom count.
- `build_molecule` 默认通过 OpenBabel 从坐标和原子类型构建 RDKit molecule.
- `process_molecule` 支持 `sanitize`, `largest_frag`, `relax_iter`.
- README 3RFM 示例未启用 `--sanitize` 或 `--relax`.
- README 3RFM 示例默认不传 `--all_frags`, 因而保留最大片段.
- `utils.write_sdf_file` 只写非 `None` molecule. 因此最终 SDF 记录数可能少于请求的 `n_samples`.

## test.py 流程差异

`test.py` 是测试集流程, 与单 pocket README 示例不同:

- 默认 `n_samples=100`.
- 默认 `batch_size=120`.
- 输出目录包含 `raw`, `processed`, `pocket_times`.
- 对每个 pocket 先关闭过滤生成 batch, 再用 `process_molecule` 处理并收集有效分子.
- while loop 会重复生成, 直到 `valid_molecules` 达到 `n_samples`, 或超过 `MAXITER=10`.
- 每个 pocket 最多 retry `MAXNTRIES=10`.
- README 的 test set command 示例包含 `--sanitize`.
- 本轮未运行 `test.py`, 因为 processed test data 和 split/checksum 未冻结.

## 官方指标和分母

代码中可见的基础指标包括:

- validity.
- connectivity.
- uniqueness.
- novelty.
- QED.
- SA.
- LogP.
- Lipinski.
- diversity.
- optional smina score.

`BasicMolecularMetrics` 的分母关系:

- validity: valid molecule 数 / generated molecule 数.
- connectivity: connected molecule 数 / valid molecule 数.
- uniqueness: unique connected SMILES 数 / connected molecule 数, 需要 dataset smiles list 时才有意义.
- novelty: novel unique SMILES 数 / unique connected SMILES 数, 需要 training smiles list 时才有意义.

本项目阶段 1 的 denominator policy:

- `N_budget` 取请求生成数, r001 为 20.
- 即使最终 SDF 记录数少于 20, 仍保留 20 行 sample metadata.
- evaluator 和 attrition 不能只靠 SDF 文件数推断分母.

## go/no-go 结论

本轮资源检查结论为 `go`, 但只针对 r001 官方 README 3RFM 示例 sanity. r002 官方风格测试子集被 `deferred`, 原因是完整 processed test data, split 和 checksum 未获取或冻结. 阶段 1 后续若要运行 test.py 子集, 应先把测试数据来源, license, size, checksum, split 和资源预算单独冻结.
