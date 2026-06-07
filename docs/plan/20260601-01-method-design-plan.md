# Method Design

## 研究题目

Failure-Feedback-Conditioned Repair for Pocket-Aware 3D Local Molecular Editing.

中文表述：面向蛋白口袋约束 3D 局部分子编辑的失败反馈条件化修复方法。

## 核心任务

给定 protein pocket、fixed scaffold、editable region 和一个已经失败的局部编辑候选，模型利用 failed candidate 及其 feedback features，在同一个 editable region 内生成 repaired candidate。

本任务强调 failed-candidate-conditioned local repair，而不是从零生成整分子、普通 R-group generation、rerank-only 或单纯 affinity guidance。

## 输入与输出

### 输入

- Protein pocket。
- Original ligand。
- Fixed scaffold。
- Editable R-group mask。
- Anchor atoms。
- Failed candidate。
- Feedback features。

### 输出

- Repaired editable region。
- Repaired local molecule。
- Optional: repaired 3D coordinates and confidence / score estimates。

## 数据构造

### 数据来源

待文献与工具调研后确定。候选方向包括公开 protein-ligand complex 数据集和已有 pocket-aware generation benchmark 使用的数据。

### 处理流程

1. 读取 protein-ligand complex。
2. 提取 ligand 周围 pocket。
3. 对 ligand 做 scaffold / editable R-group 切分。
4. 标记 anchor atoms。
5. 校验 fixed scaffold 与 editable region 的可重建性。
6. 构建 train / validation / test split。

### 数据校验

- Molecule validity。
- Scaffold preservation。
- Anchor validity。
- Editable region connectivity。
- Protein-ligand coordinate alignment。
- Split leakage check。

### 当前 smoke-plus 数据状态

- 已构造 12-complex RCSB smoke-plus set: 1A4W, 3PTB, 1HSG, 1HVR, 2BR1, 3ERT, 1M17, 2HYY, 3G0E, 4DLI, 4ERW, 5P21。
- 当前 RDKit readable: 12/12; `sample_quality.evaluable_for_repair`: 12/12。
- Deterministic split seed 0: train 6, validation 3, test 3, 记录在 `data/datasets/rgroup_smoke_plus/splits/rgroup_smoke_plus_split_v1.json`。
- 当前实现已包含 7 个 controlled/semi-realistic smoke-plus failure types: clash, interaction_loss, anchor_invalid, geometry_invalid, linker_too_flexible, drug_likeness_drop, score_hacking。新增类型会对 editable region 做局部坐标扰动或原子类型替换, 比纯全分子平移更接近局部生成失败, 但仍不是 generator/docking/local proposal 真实失败。
- 另有独立 local-proposal pool 诊断版本: `scripts/data/generate_local_proposal_failures.py` 从 editable-region local translation / zigzag / atom-substitution proposals 中生成 72 个 `smoke_local_proposal_pool_rdkit` failed candidates 和 864 个 repaired records。该版本用于逼近 local proposal failure, 但仍是 RDKit proposal pool, 不能表述为真实外部生成器或 docking loop 输出。
- Vina docked pose 诊断当前分为两类: full-pose docked failures 使用 template topology + Vina coordinates, 暴露大 anchor drift 且非 oracle repair success 0.0；anchor-preserved local-edit failures 只替换 editable-region 坐标并保留 scaffold/anchor, 但当前 3 条样本 identity/no-feedback basic success 已 1.0。新增 repair-gain 指标后, no-feedback/identity/rerank gain_success 为 0.0, 说明该指标能避免把“原地不动”误判为 repair。


## Failed Candidate 构造

初期优先用可控人工扰动，后续接入已有生成器失败样本。

候选失败类型：

- Protein-ligand clash。
- Interaction loss。
- Anchor invalid。
- Linker / R-group too flexible。
- Drug-likeness drop。
- Score hacking。
- Geometry invalid。
- Editable region invalid。

每个 failed candidate 需要保留：

- 失败候选结构。
- 失败类型或弱标签。
- 失败反馈特征。
- 对应 original / reference ligand。
- 生成方式与随机种子。

## Feedback Features

### Global feedback

- Vina score / ΔVina。
- QED。
- SA。
- logP。
- Rotatable bonds。
- Ligand efficiency。
- PoseBusters pass/fail。

### Geometry feedback

- Clash count。
- Clash pair features。
- Anchor distance violation。
- Steric overlap。
- Pocket occupancy。
- Local distance / angle / torsion violation。

### Interaction feedback

- PLIP interaction fingerprint。
- Hydrogen bond recovery。
- Hydrophobic contact recovery。
- Salt bridge recovery。
- π interaction recovery。
- Interaction similarity to reference ligand。

### Feedback encoding options

- Global numeric vector。
- Atom-level features。
- Pair-level features。
- Interaction fingerprint embedding。
- Failure-type embedding。
- Latent feedback vector。

## 模型设计

### Baseline repair model

No-feedback repair:

```text
pocket + scaffold + failed candidate → repaired candidate
```

### Feedback-conditioned repair model

```text
pocket + scaffold + failed candidate + feedback → repaired candidate
```

### 候选模型方向

- Equivariant GNN local repair。
- Diffusion-based local refinement。
- Conditional R-group decoder。
- Fragment replacement / coordinate refinement hybrid。

当前实现状态：

- `feedback_geometry_refinement` 是当前主要非 oracle smoke 方法, 使用 pocket geometry proxy 在候选池中选择 repaired molecule。
- `feedback_learned_geometry_policy` 是轻量 oracle-free ridge geometry policy: 先用 failed candidate 的 pocket geometry proxy 生成 pseudo-label translation target, 再用 feedback features 拟合 ridge linear policy。它不使用 reference-pose rollback target, 但仍只是 smoke-level learned baseline, 不是 publication-level 模型。
- `feedback_kernel_geometry_policy` 使用相似 feedback features 的 RBF kernel averaging 预测 oracle-free pseudo-label offset; smoke-plus multiseed 只略高于 no-feedback, 是弱结果。
- `feedback_knn_geometry_policy` 使用最近邻 feedback feature 的离散 pseudo-label offset; 在 4-type smoke-plus 中曾优于 ridge policy, 但扩展到 7-type controlled/semi-realistic failures 后 seeds 0/1/2 mean success 0.6905, 低于 ridge policy 0.7421, 显示该非参数策略对 failure-type 分布敏感。
- `feedback_residual_ensemble_policy` 是新增 oracle-free learned baseline: ridge feedback-to-offset policy + RBF kernel residual correction + predicted-offset neighborhood geometry selection。它在 seed 0 expanded smoke-plus fallback success 上达到 0.7976, 高于 ridge 0.7500 和 geometry refinement 0.7857；local-proposal pool success 0.9028, 高于 ridge/geometry refinement 0.8750。但它仍依赖 geometry pseudo-label 和局部 geometry selection, 且 Vina-like proxy 不如 geometry refinement, 不能视为最终 publication-level 模型。
- `feedback_anchor_alignment_policy` 是针对真实 Vina docked pose smoke 新增的诊断 baseline: 保留 failed candidate 拓扑, 在 identity、anchor-centroid translation 和 anchor rigid alignment 候选中按 geometry score 选择。当前结果是负面的: 在 3 个成功转换的 docked pose failed candidates 上 fallback success 仍为 0.0, 说明简单 anchor 对齐无法解决 docking pose 的 anchor drift, 且刚体对齐容易制造 clash。该 policy 只作为诊断消融, 不应作为最终模型主张。
- `feedback_editable_contact_policy` 是新增 anchor-preserving, editable-region-only 诊断 baseline: 只对 editable atoms 应用小步局部 offset, 按 protein-ligand contact count、clash penalty 和 anchor penalty 的 oracle-free proxy 选择候选。在 5 个 contact-degraded local-edit failed candidates 上 fallback basic success 1.0, repair_gain_success 1.0, mean contact recovery gain 0.1039, 高于 identity/no-feedback/rerank/Best-of-N 的 gain 0.0；但 official PLIP recovery gain 只有 +0.0105, 因此只能作为启发式 upper-bound 和下一步模型设计依据。
- `feedback_learned_editable_contact_policy` 是新增 leave-complex-out learned editable-only baseline: 对每个 held-out complex, 用其他 complexes 的 oracle-free editable contact proxy target 形成训练行, 再按 feedback features 最近邻选择 editable offset。contact-degraded local-edit subset 的 seeds 0/1/2 聚合中, fallback repair_gain_success 0.6667, mean contact recovery gain 0.0519, 高于 no-feedback/identity/rerank/Best-of-N 的 0.0, 是当前最接近论文主张的 learned smoke 正信号, 但仍是 offset-level 轻量 policy。
- `feedback_linear_refinement` 使用 reference-centroid 监督目标, 只作为 sanity check, 不应计入非 oracle learned model 主张。
- 下一步需要把 kNN/ridge policy 扩展为更严格的 local repair/refinement, 并引入 geometry-only / interaction-only / full-feedback 消融。


## Baselines

必须包含：

1. Direct regeneration。
2. Best-of-N。
3. Rerank-only。
4. No-feedback repair。
5. Global-score-only feedback。
6. Geometry-only feedback。
7. Interaction-only feedback。
8. Full feedback repair。

## Evaluation Metrics

主指标：

- Same-budget basic success rate: molecule validity + scaffold preservation + editable validity + anchor validity + clash-free。
- Same-budget repair-gain success rate: basic success + at least one improvement over the failed candidate, including fallback contact gain, official PLIP interaction recovery/similarity gain, anchor error reduction, clash-count reduction, or Vina-like proxy improvement。
- Scaffold preservation。
- Editable validity。
- Anchor validity。
- Protein-ligand clash。
- PoseBusters pass。
- PLIP interaction recovery / similarity。
- Vina / ΔVina。
- Ligand efficiency。
- QED。
- SA。
- logP。
- Rotatable bonds。

实验设计：

- 至少 3 seeds。
- 至少一个 split 的交叉验证。
- 主实验。
- Baseline 对比。
- 消融实验。
- 成功案例与失败案例。

当前 smoke-plus 指标状态：

- 已完成 seeds 0/1/2 repaired-molecule fallback proxy aggregation。
- 已完成 deterministic train/validation/test split summary。
- 已在独立 `pfr-eval-tools` 环境完成 smoke 和 smoke-plus 官方 PLIP+Vina score-only/interaction-count 评估, 但这些不是 redocking success 或完整 publication-level 指标。
- smoke-plus PLIP 480/480 写出且 0 error；初次 Vina 280/480 写出 score-only energy, 200/480 preparation failure, 失败集中在 1M17, 2BR1, 3ERT, 3G0E, 5P21；加入 receptor `--default_altloc A` retry 和 ligand `--charge_model zero` retry 后, retry 版 Vina score-only coverage 达到 480/480 且 0 error。
- PoseBusters bounded subset20 已通过隔离子进程完成: 20 条覆盖 10 个 baselines 和 2 个 failed candidates, 18/20 写出 46 checks, 2/20 timeout, 0/18 full pass；完整稳定批处理仍未完成。
- PoseBusters expanded subset35 已完成: 35/35 写出 summary, 11/35 subprocess timeout, 24 条可判定记录 full pass 为 0；因此 PoseBusters 仍只能作为 bounded diagnostic, 不能作为稳定主指标。
- 独立 local-proposal pool 诊断已完成: 72 failed candidates / 864 repaired records, `feedback_geometry_refinement` 和 ridge `feedback_learned_geometry_policy` fallback success 均为 0.875, 高于 no-feedback 0.8194 和 direct regeneration 0.7361；但该结果仍是 fallback proxy 和 RDKit proposal pool, 不是 publication-level 真实失败样本结果。
- 扩展 1008-record repaired set 的官方 PLIP+Vina score-only retry 已完成: PLIP 1008/1008 且 0 error, Vina score-only 1008/1008 且 0 error。主要非 oracle baselines 中, ridge `feedback_learned_geometry_policy` mean PLIP interaction count 11.2143, mean Vina score-only -5.9780；`feedback_geometry_refinement` 为 10.8452 / -4.6964；`best_of_n` 为 11.0952 / -3.5315；`direct_regeneration` 为 10.7381 / -0.4444。该结果只说明官方 interaction-count / score-only coverage 和初步排序信号, 不能解释为 redocking success。
- 扩展 1008-record 官方 PLIP+Vina 已新增 failure-type 细分: `outputs/20260601-04-vina-pose-and-local-edit-diagnostics/metrics/official_eval_smoke_plus_expanded_plip_vina_retry_by_failure_type.json` 和 CSV。anchor_invalid 上 direct/no-feedback/Best-of-N 的 mean Vina score-only 为正且很差, geometry refinement -1.9027, ridge -0.1542, 显示反馈修复能修正一部分 anchor drift；interaction_loss 和 score_hacking 上 ridge 的 Vina score-only 优于 direct/geometry/no-feedback, 但 linker_too_flexible 和 drug_likeness_drop 上 no-feedback 或 Best-of-N 仍很强, 说明 failure-type heterogeneity 仍是主要分析重点。
- contact-degraded local-edit coverage 已扩展为 `max_per_example=3`, `min_contact_recovery_loss=0.03`: seeds 0/1/2 分别得到 19/17/17 candidates。扩展后 no-feedback / identity / rerank / Best-of-N / geometry-only / global-only 的 mean repair_gain_success 仍为 0.0；interaction-only 0.5676, full editable policy 0.6047, learned editable-contact 0.2642。扩展 key-baseline official PLIP recovery gain 显示 learned editable-contact +0.0065, full editable +0.0301, interaction-only +0.0104, no-feedback/geometry/global 0.0, Best-of-N -0.0591。相比 5 candidates/seed 设置, learned 正信号明显变弱, 说明小样本结果存在乐观偏差；但 interaction feedback 仍是主要有效信号。`no_failed_candidate_policy` 从 reference ligand 出发, 只能作为 reference-only oracle sanity。

## Ablation Plan

- No-feedback。
- Global-score-only。
- Geometry-only。
- Interaction-only。
- Rerank-only。
- Best-of-N。
- Full feedback。

## 成功标准

Full feedback repair 在相同生成预算下稳定超过 Best-of-N、rerank-only 和 direct regeneration，并且提升不只体现在 Vina 上，还体现在几何合法性、anchor 合法性、interaction recovery 和 drug-likeness 相关指标上。

## 失败与转向标准

如果 full feedback repair 不能稳定超过简单 baseline，则转向：

- 更强 feedback encoder。
- 更合理 failed candidate 数据构造。
- 更窄任务，例如 clash repair 或 interaction recovery。
- 将项目定位为 repair benchmark / diagnostic benchmark。
