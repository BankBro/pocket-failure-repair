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

具体模型选择需在文献调研和 smoke baseline 后确定。

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

- Same-budget success rate。
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
