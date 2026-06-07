# BIBM 神经修复模型路线报告

> 项目: `pocket-failure-repair`  
> 日期: 2026-06-02  
> 目标: 面向 BIBM full paper 的 `Failure-Feedback-Conditioned Repair for Pocket-Aware 3D Local Molecular Editing` 主模型路线设计。  
> 说明: 本报告是模型路线设计文档, 不是新实验结果。当前已有实验只能证明 failure feedback 存在机制级正信号, 不能直接作为最终投稿级 neural model 结果。

## 1. 当前判断

当前项目已经证明了一个重要但还不充分的事实:

> 在 contact-degraded, anchor-preserved local-edit 诊断任务中, failure feedback 对 interaction recovery 有可测的正向信号。

当前关键证据包括:

- 三 seed contact-degraded local-edit set: 53 failed candidates。
- `no_feedback_repair` / `rerank_only`: official PLIP recovery gain 为 0.0。
- `Best-of-N` / `direct_regeneration`: official PLIP recovery gain 为负。
- shallow learned policies 有小幅正信号:
  - learned: +0.0065。
  - ridge: +0.0076。
  - classified: +0.0090。
  - scaled learned: +0.0090。
  - budgeted learned: +0.0099。
- editable-contact search teacher / full editable policy: +0.0301。
- shuffled-feedback 消融接近 0 或为负, 支持 feedback 内容本身有贡献。

但这些仍然不够支撑 BIBM full paper 的最终主张, 因为当前可学习模型主要还是 nearest-neighbor, ridge, classifier 等传统浅层模型。后续必须从:

```text
手工 feedback features -> shallow ML repair policy
```

升级为:

```text
failed candidate 3D structure
+ protein pocket local environment
+ editable/anchor masks
+ structured failure feedback
        ↓
neural encoder + repair decoder
        ↓
editable-region local repair action / coordinate refinement
```

## 2. BIBM full paper 对主模型的最低要求

如果目标是 BIBM 正式录取, 主模型至少需要满足以下要求。

### 2.1 方法贡献必须清晰

论文不能只说“我们做了很多 baseline”。需要收敛成一个明确主方法:

> failure-feedback-conditioned neural local repair model。

也就是, 模型明确读取 failed candidate 和 failure feedback, 然后在同一个 editable region 内输出定向修复动作。

### 2.2 不能止步于传统 ML

当前 nearest-neighbor, scaled nearest-neighbor, ridge, classifier 可以保留为:

- baseline。
- teacher-student 前置证据。
- 消融。
- sanity check。

但不能作为最终主模型。BIBM full paper 更需要一个具有结构建模能力的 neural repair model, 例如 EGNN/GVP/PaiNN 风格的 3D graph model, 或更进一步的 local diffusion/flow refinement。

### 2.3 必须有严格的同预算评估

主结果必须回答:

> 在相同或清楚分层的 generation/repair budget 下, neural repair model 是否优于 no-feedback, shuffled-feedback, rerank-only, Best-of-N, direct regeneration, shallow learned policy, 并接近或部分替代 editable-contact search teacher?

必须区分:

- record-level output budget。
- internal candidate budget。
- top-1。
- confidence-selected top-K。
- oracle top-K, 如果报告只能作为 upper bound。

### 2.4 必须避免数据泄漏

训练/验证/测试不能按 failed candidate record 随机划分。因为同一 protein pocket 下的多个扰动会共享几何、interaction pattern 和 reference ligand 信息。

推荐至少使用:

- held-out complex split。
- scaffold split。
- protein target / sequence cluster split, 如果数据量允许。
- held-out failure type 分析, 用于检验泛化。

### 2.5 指标不能只靠 Vina

Vina score-only 只能作为 supplemental diagnostic, 不能作为 repair success。

主指标应包括:

- official PLIP interaction recovery gain。
- official PLIP interaction similarity gain。
- scaffold preservation。
- anchor drift / anchor RMSD。
- editable-region validity。
- clash count / clash reduction。
- local geometry validity。
- bounded PoseBusters diagnostics。
- Vina score-only / Delta Vina 作为补充列。

任何 success 都必须报告相对 failed candidate 的 repair/recovery gain。

## 3. 统一任务定义

### 输入

所有三个方案共享以下输入定义。

```text
protein pocket P
failed ligand candidate C_fail
fixed scaffold mask S
editable atom / fragment mask M
anchor atoms A
structured failure feedback F_fail
optional repair budget B
```

其中 `F_fail` 应至少包括:

- lost contact / interaction feedback。
- clash pair feedback。
- anchor drift / anchor violation。
- geometry violation。
- contact recovery loss / similarity loss。
- global diagnostics, 如 QED, logP, rotatable bonds, optional Vina/PoseBusters fields。

### 输出

推荐输出不是“重新生成整个分子”, 而是局部修复动作:

```text
editable-region repaired coordinates
或 editable-region action, 如 displacement / rigid transform / torsion update
```

同时输出审计记录:

- selected editable atoms/fragments。
- action type。
- coordinate residual / torsion delta / transform。
- predicted contact gain。
- predicted validity / confidence。
- used feedback fields。
- repair budget。
- hard filter / projection status。

## 4. 方案一: Teacher-Student Feedback-Conditioned EGNN LocalEditNet

### 4.1 一句话概括

> 用当前效果最强的 editable-contact search 作为 teacher, 自动产生局部修复动作 pseudo-label, 再训练一个 E(3)-equivariant student model, 学会从 failed candidate + pocket + feedback 直接预测 editable-region repair action。

这是最稳妥, 最推荐作为 BIBM 主线的方案。

### 4.2 模型架构

```text
Failed ligand graph
+ Protein pocket graph
+ Anchor/editable masks
+ Structured failure feedback
        ↓
Feedback-conditioned EGNN / GVP encoder
        ↓
Ligand-pocket cross message passing
        ↓
Editable-region action decoder
        ↓
local repair action / coordinate residual
```

具体模块:

1. **Failed candidate encoder**
   - 编码 failed ligand 的 atom/bond/3D coordinate。
   - 标记 scaffold atoms, anchor atoms, editable atoms。

2. **Pocket/contact encoder**
   - 取 ligand 周围 6-8 Å pocket atoms。
   - 编码元素、残基类型、donor/acceptor、hydrophobic/aromatic/charge 等。
   - 建立 ligand-pocket radius edges 或 cross-attention。

3. **Failure feedback encoder**
   - global feedback 用 MLP 编码。
   - clash pair / lost contact / PLIP residue pair 作为 edge 或 virtual feedback nodes。
   - anchor violation / geometry violation 作为 node/edge feature。

4. **Equivariant message passing backbone**
   - MVP 可用 EGNN-style coordinate update。
   - 后续可换成 GVP, PaiNN 或更强的 SE(3)-equivariant model。

5. **Repair action decoder**
   - 输出 editable atom displacement。
   - 或 fragment rigid transform。
   - 或 torsion angle update。
   - 同时输出 confidence / predicted repair gain。

### 4.3 学习方法

主学习方式是 **监督学习 + imitation / distillation**。

训练标签来自 editable-contact search teacher:

```text
对每个 failed candidate:
    teacher 枚举多个 editable-region offsets / actions
    用 contact / clash / anchor proxy score 打分
    选 top-1 或 top-M actions
    作为 student 的 pseudo-label
```

推荐 loss:

- coordinate residual Huber loss。
- action type cross entropy。
- torsion / transform geodesic loss。
- contact-gain regression 或 ranking loss。
- validity / clash confidence loss。
- hard negative ranking loss。

建议使用 top-M imitation, 不要只模仿单一 top-1 teacher action, 因为局部修复通常有多个可行解。

### 4.4 是否需要无监督或强化学习

MVP 阶段不需要强化学习。

推荐顺序:

1. supervised teacher-student imitation。
2. hard negative contrastive learning。
3. 可选 self-training。
4. 如果前面有效, 再考虑 preference learning / DPO-style ranking。
5. 强化学习只作为后期增强, 不作为主线起点。

原因是 RL 会显著增加工程复杂度和 reward hacking 风险, 尤其 Vina score-only 容易被模型利用。

### 4.5 数据利用

当前 12-complex smoke-plus 和 53 contact-degraded failed candidates 只能用于:

- pipeline sanity。
- overfit test。
- action replay 检查。
- case study。
- official eval smoke。

正式训练需要扩展到:

- 500-2000 protein-ligand complexes 起步。
- 每个 complex 生成 5-20 个 failed candidates。
- 目标 5k-40k teacher-labeled repair examples。

候选数据源:

- PDBbind refined/general subset。
- Binding MOAD 清洗子集。
- CrossDocked 派生清洗子集, 主要用于增强和泛化, 需要严控 split。

### 4.6 优点

- 与当前项目证据最自然衔接。
- teacher 已经比 shallow learned 更强, 存在可蒸馏空间。
- 工程可控, 不必一开始做 diffusion。
- 输出 action 可解释, 适合 case study。
- 可以直接和 current shallow policies 做公平对照。

### 4.7 风险

- teacher 本身 official gain 只有 +0.0301, ceiling 不高。
- student 可能学不到 teacher, 或只学到很弱的平均动作。
- 如果数据规模不足, neural model 会过拟合。
- 审稿人可能质疑只是 heuristic search distillation。

### 4.8 BIBM 推荐程度

**最高。**

这是最适合当前项目状态的主线。建议作为第一优先级实现。

## 5. 方案二: Self-Supervised FF-EGNN Iterative Diagnostic Refiner

### 5.1 一句话概括

> 用大量 protein-ligand complex 做自监督 corruption-repair 预训练, 让模型先学会 pocket-aware local denoising 和 failure grounding, 再用 teacher labels 和 hard negatives 微调成 iterative repair model。

这是更有模型深度的方案, 适合作为方案一的增强版或更强主模型。

### 5.2 模型架构

```text
Pocket-ligand heterogeneous 3D graph
+ structured failure feedback
        ↓
self-supervised pretrained equivariant encoder
        ↓
iterative diagnostic repair block
        ↓
1-3 step editable coordinate / torsion refinement
```

核心思想是 iterative repair:

```text
第 1 步: 修最明显的 contact loss / clash
第 2 步: 检查剩余 feedback, 再微调
第 3 步: 输出 final repaired candidate + confidence
```

模型模块:

1. **Heterogeneous graph encoder**
   - protein pocket nodes。
   - ligand scaffold nodes。
   - editable nodes。
   - virtual feedback nodes。

2. **Feedback grounding module**
   - 学会把 clash pair, lost contact, anchor violation 映射到具体 atom/residue/node/edge。

3. **Iterative equivariant refiner**
   - 每一步输出 coordinate residual 或 torsion delta。
   - 每一步可重新计算轻量 feedback proxy。

4. **Auxiliary heads**
   - failure type prediction。
   - contact gain prediction。
   - clash reduction prediction。
   - repair success confidence。

### 5.3 学习方法

这个方案使用多阶段学习。

#### Stage 1: 自监督预训练

从 native protein-ligand complexes 中构造 corruption:

- editable region 加噪声。
- torsion corruption。
- contact-degraded displacement。
- clash injection。
- anchor-preserved drift。

训练模型恢复 native 或 high-quality coordinates。

这属于 **self-supervised denoising pretraining**。

#### Stage 2: 有监督 repair fine-tuning

使用 failed candidates + teacher pseudo-labels:

```text
failed structure + feedback -> teacher repair action / reference denoising target
```

#### Stage 3: hard negative / preference learning

构造 pairwise comparisons:

```text
teacher repair > failed / identity / shuffled-feedback / Vina-score-only hacked candidate
```

训练 confidence/ranking head。

#### Stage 4: 可选 conservative preference fine-tuning

可以使用 DPO-style ranking 或 conservative offline RL, 但仅作为后期加分项。

### 5.4 是否需要强化学习

不建议一开始就用 RL。

更合理的是:

```text
self-supervised pretraining
+ supervised fine-tuning
+ hard negative ranking
+ optional preference learning
```

如果模型已经能稳定生成 top-K candidates, 后续再考虑 offline RL / preference optimization。

### 5.5 数据利用

方案二比方案一更依赖数据规模。

推荐数据结构:

1. **pretraining set**
   - PDBbind / Binding MOAD / CrossDocked 清洗 complexes。
   - 用 native pose 自动生成 corruption-denoising pairs。

2. **repair fine-tuning set**
   - teacher-labeled failed candidates。
   - 覆盖 contact-degraded, clash, geometry invalid, anchor drift, torsion corruption 等。

3. **hard negative set**
   - identity。
   - no-feedback。
   - shuffled-feedback。
   - Vina-score-only better but PLIP/geometry worse candidates。

4. **official evaluation subset**
   - 小而高质量, 用 PLIP/Vina/PoseBusters 完整审计。

### 5.6 优点

- 比方案一更像完整 neural architecture。
- 自监督预训练可以利用更多公开数据。
- 不完全依赖 teacher 的上限。
- iterative repair 更符合真实修复过程。
- feedback grounding 有助于论文解释性。

### 5.7 风险

- 工程量明显大于方案一。
- 数据清洗要求更高。
- synthetic corruption 和真实 generator/docking failure 之间可能有 gap。
- 如果没有明显超过方案一, 审稿人会质疑复杂度。

### 5.8 BIBM 推荐程度

**中高。**

建议作为第二优先级。最稳路线是先做方案一 MVP, 然后把方案二的 self-supervised / iterative refiner 逐步加进去。

## 6. 方案三: Failure-Feedback-Conditioned Local Flow / Diffusion Refinement

### 6.1 一句话概括

> 把 repair 看成 fixed-topology editable-region conditional generation/refinement: 从 failed candidate 附近出发, 用 failure feedback 条件化的 flow/diffusion model 生成一个或多个 repaired editable-region conformers。

这是创新性最强, 但风险最高的方案。

### 6.2 模型架构

```text
Failed editable coordinates
+ fixed scaffold / anchor constraints
+ protein pocket graph
+ structured feedback
        ↓
E(3)-equivariant conditional flow / diffusion model
        ↓
K repaired editable-region conformers
        ↓
confidence + hard filters select final repair
```

推荐只做 fixed-topology coordinate refinement, 不要一开始生成 atom types / bonds。

核心约束:

- scaffold hard clamp。
- anchor hard clamp 或强约束。
- 只对 editable atoms 加噪和 denoise。
- topology 不变。
- top-K selection 不能使用 test reference 或 official PLIP oracle。

### 6.3 学习方法

推荐多阶段:

1. **conditional denoising / flow matching pretraining**
   - 对 editable region 加 corruption。
   - 学习从 corrupted pose + feedback 恢复合理 local pose。

2. **teacher trajectory distillation**
   - 把 editable-contact teacher 的 offset trajectory 转成 vector field supervision。

3. **multi-task feedback grounding**
   - 预测 PLIP recovery gain, clash reduction, anchor validity。

4. **preference learning / conservative offline RL**
   - 用 repaired > failed, normal feedback > shuffled feedback, PLIP-gain positive > Vina-only score hacking 做 pairwise ranking。

### 6.4 是否需要强化学习

方案三可以考虑 RL 或 preference learning, 但不建议作为核心训练方法。

更安全的表述是:

> supervised denoising / flow matching 是主训练方法, preference learning 是后期校准, RL 只是 optional extension。

原因:

- PLIP/Vina/PoseBusters 都不是可直接高频调用的稳定 reward。
- Vina score-only 容易产生 score hacking。
- RL 会放大 reward 设计问题。
- BIBM 审稿人会要求非常严格的 reward 和 baseline 审计。

### 6.5 数据利用

方案三需要最大数据量。

最低要求:

- 至少 10k 级 repair pairs 才建议认真训练。
- 理想为 10k-100k fixed-topology local refinement pairs。
- 当前 53 failed candidates 完全不足以训练 diffusion/flow, 只能用于 overfit smoke。

数据来源:

- PDBbind / Binding MOAD: high-quality native complexes。
- CrossDocked: large-scale pretraining, 但需要强清洗和 split audit。
- 当前 smoke-plus/contact-degraded: debug, sanity, case study。
- Vina/local proposal failures: synthetic-to-real gap 检查。

### 6.6 优点

- 模型创新性最强。
- 能生成多种可能 repair candidates。
- 可以表达局部修复不确定性。
- 如果效果好, BIBM 论文亮点明显。

### 6.7 风险

- 数据量和工程成本最高。
- top-K oracle selection 很容易不公平。
- 可能 identity collapse, 即模型学会不动。
- 可能 over-move editable region, 破坏 anchor/geometry。
- 如果没有显著超过 deterministic EGNN, diffusion 会显得为复杂而复杂。

### 6.8 BIBM 推荐程度

**条件性推荐。**

不建议作为第一版主线。更适合作为:

- 方案一/二跑通后的增强模型。
- 高风险高收益路线。
- future-ready extension。

如果资源充足且数据扩展顺利, 可把它作为 stronger variant；否则不要让它拖垮主线。

## 7. 数据路线

### 7.1 当前数据的角色

当前项目数据:

- 12-complex smoke-plus。
- 53 contact-degraded local-edit failed candidates。
- official PLIP/Vina completed subsets。

只能用于:

- sanity check。
- overfit test。
- pipeline validation。
- failure case visualization。
- early ablation。

不能作为 BIBM full paper 的唯一训练/测试数据。

### 7.2 主数据集建议

优先顺序:

1. **PDBbind refined/general subset**
   - 适合作为主数据起点。
   - 优点: protein-ligand complex 质量较高, 领域接受度高。
   - 用途: supervised repair pairs, official eval subset。

2. **Binding MOAD 清洗子集**
   - 可作为外部验证或补充数据。
   - 用途: generalization check。

3. **CrossDocked 清洗子集**
   - 数据量大, 适合 self-supervised pretraining。
   - 风险: pose quality 和 split leakage 需要严格控制。

4. **当前 smoke-plus / contact-degraded set**
   - 继续作为 debug 和审计闭环。

### 7.3 failed candidate 构造

需要覆盖多种失败类型:

- contact-degraded anchor-preserved local edit。
- clash injection。
- torsion corruption。
- geometry invalid。
- anchor drift。
- interaction loss。
- score hacking。
- local proposal failure。
- Vina-selected docking-like failure。

每条 failed candidate 必须保存:

- source complex id。
- failed ligand path。
- reference ligand path。
- protein path。
- scaffold / anchor / editable masks。
- failure generation method。
- seed。
- feedback JSON。
- teacher trace, 如果有。
- split id。

### 7.4 split 规则

最低要求:

```text
held-out complex split
```

更强要求:

```text
held-out target/protein family split
+ scaffold split
+ held-out failure type analysis
```

禁止:

```text
按 failed candidate record 随机切分
```

因为同一 complex 的多个 perturbations 会泄漏 pocket geometry 和 reference interaction pattern。

## 8. 评估路线

### 8.1 主指标

主表建议包含:

- official PLIP interaction recovery gain。
- official PLIP interaction similarity gain。
- scaffold preservation。
- anchor validity / anchor drift。
- editable validity。
- clash count / clash reduction。
- local geometry validity。
- Vina score-only as supplemental。
- bounded PoseBusters diagnostics。

### 8.2 必须保留的 baseline

- identity failed candidate。
- no-feedback repair。
- shuffled-feedback repair。
- rerank-only。
- Best-of-N。
- direct regeneration。
- current shallow learned policies。
- editable-contact search teacher。
- geometry-only / interaction-only / global-only。

### 8.3 必须做的消融

- no feedback。
- shuffled feedback。
- no pocket。
- no equivariance。
- geometry-only feedback。
- interaction-only feedback。
- global-only feedback。
- no teacher imitation。
- no hard negatives。
- top-1 vs top-K。
- same-budget / internal-budget stratification。

### 8.4 统计方式

推荐:

- 至少 3 seeds。
- 按 complex 聚合或 paired test。
- bootstrap confidence interval, 但不要按 record 伪造独立性。
- 按 failure type 分层。
- 按 editable atom count / contact-loss severity 分层。

## 9. 三个方案对比

| 方案 | 推荐程度 | 模型强度 | 工程风险 | 数据要求 | 适合角色 |
|---|---:|---:|---:|---:|---|
| 方案一: Teacher-Student EGNN LocalEditNet | 最高 | 中高 | 中 | 中 | 第一主线 / MVP 主模型 |
| 方案二: Self-Supervised Iterative Refiner | 中高 | 高 | 中高 | 高 | 方案一增强 / 更强主模型 |
| 方案三: Local Flow/Diffusion Refinement | 条件性 | 最高潜力 | 高 | 很高 | 高风险增强 / future-ready variant |

## 10. 推荐路线

最稳妥的整体路线是:

```text
先做方案一 MVP
        ↓
如果有效, 加入方案二的自监督预训练和 iterative refiner
        ↓
如果数据和算力足够, 再尝试方案三 diffusion/flow variant
```

也就是说, 不建议直接跳到 diffusion/flow。当前项目最缺的不是复杂生成器, 而是一个能在 held-out complex/scaffold split 上明确超过 shallow learned/no-feedback/shuffled-feedback 的 neural local repair model。

## 11. 近期执行计划

### Step 1: 冻结数据和 teacher trace schema

需要定义:

```text
failed_complex
structured_feedback
teacher_top1_action
teacher_topM_actions
negative_actions
repaired_complex
score_delta
split_id
```

### Step 2: 实现方案一最小模型

MVP:

```text
EGNN encoder
+ feedback MLP / feedback nodes
+ editable coordinate residual decoder
+ confidence head
```

先做:

- 10-50 cases overfit。
- action replay check。
- anchor/scaffold hard clamp check。
- coordinate transform equivariance check。

### Step 3: 扩展训练数据

从 PDBbind / Binding MOAD 起步, 构建:

- 500-2000 complexes。
- 5k-40k teacher-labeled failures。
- held-out complex/scaffold split。

### Step 4: 跑严格对照

必须同时比较:

```text
neural full-feedback
neural no-feedback
neural shuffled-feedback
shallow learned
editable-contact teacher
Best-of-N
rerank-only
direct regeneration
```

### Step 5: 再决定是否加入方案二/三

如果方案一明显有效:

- 加自监督 pretraining。
- 加 iterative repair。
- 加 hard negative preference learning。

如果方案一无效:

- 不要贸然上 diffusion。
- 先检查 feedback 表征、teacher target、数据 split 和 failure construction。

## 12. 最终建议

本项目要达到 BIBM full paper 标准, 最终主张应收敛为:

> 我们提出一个 failure-feedback-conditioned neural local repair model, 它在 fixed scaffold 和 editable region 约束下, 利用 explicit diagnostic feedback 修复 failed pocket-aware local edits, 并在同预算评估中优于 no-feedback, shuffled-feedback, rerank-only, Best-of-N, direct regeneration 和 shallow learned policies。

三个方案中, 推荐优先级为:

1. **方案一: Teacher-Student Feedback-Conditioned EGNN LocalEditNet**。
2. **方案二: Self-Supervised FF-EGNN Iterative Diagnostic Refiner**。
3. **方案三: Failure-Feedback-Conditioned Local Flow/Diffusion Refinement**。

当前最应该做的是方案一, 因为它能把现有 editable-contact search teacher 和 shallow learned 正信号自然转化为真正 neural repair model, 工程风险可控, 也最容易形成 BIBM full paper 的清晰方法贡献。
