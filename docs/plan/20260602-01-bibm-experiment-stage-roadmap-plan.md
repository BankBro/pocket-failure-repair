# 面向 BIBM full paper 的实验阶段路线图

版本: 2026-06-02 可读性修订版。  
适用范围: 本文档用于管控 `pocket-failure-repair` 项目从当前诊断性结果, 逐步推进到 BIBM full paper 级主实验候选证据。本文档不表示当前结果已经达到 BIBM full paper 或神经网络主模型水平。

## 1. 一句话结论

当前项目最稳妥的主线是: **先把“失败候选分子 + 结构化失败反馈 + 固定骨架 + 局部可编辑区域”的局部修复任务做扎实, 再训练真正的神经网络修复模型。**

现阶段已有结果能说明: 在一个受控诊断子集上, 使用失败反馈的局部修复策略确实出现了正式 PLIP 指标上的正向信号。但是, 这些结果还只是诊断性证据, 不是完整的 BIBM full paper 主模型结果。

后续最高优先级路线是 **教师-学生式 LocalEditNet**: 先用现有搜索/启发式方法当“教师”, 生成可复核的伪标签, 再训练 EGNN/GVP/PaiNN 风格的三维神经网络学生模型。自监督迭代修复可以作为第二线增强。局部 flow/diffusion 只应作为后期高风险扩展, 不应作为第一版主线。

## 2. 当前证据边界

### 2.1 已验证结果

1. 当前 smoke-plus 数据包含 12 个公开 RCSB 复合物: 1A4W, 3PTB, 1HSG, 1HVR, 2BR1, 3ERT, 1M17, 2HYY, 3G0E, 4DLI, 4ERW, 5P21。当前确定性划分为训练集 6 个, 验证集 3 个, 测试集 3 个。

2. 当前最重要的诊断集是 contact-degraded, anchor-preserved, local-edit 子集。三个随机种子分别产生 19, 17, 17 个失败候选分子, 合计 53 个。这些分子没有 clash, 保留 anchor, 且存在接触恢复损失。

3. 三个种子的关键对照已完成正式 PLIP/Vina 评估: 477/477 条记录, 0 个 PLIP 错误, 0 个 Vina 错误。正式 PLIP recovery gain 为: editable-contact/full search +0.0301, budgeted learned +0.0099, ridge +0.0076, 1-shot learned +0.0065, no-feedback/rerank 0.0, Best-of-N -0.0591, direct regeneration -0.1441。

4. shuffled-feedback 消融已完成 159/159 条正式记录, 0 个 PLIP/Vina 错误。Normal vs shuffled 结果为: learned +0.0065 vs +0.0007, ridge +0.0076 vs -0.0053, budgeted learned +0.0099 vs -0.0012。

5. classified editable-contact policy 已完成 53 条正式记录, 0 个 PLIP/Vina 错误, budget=1 时 PLIP recovery gain 为 +0.0090, similarity gain 为 -0.0108。scaled learned policy 也完成 53 条正式记录, PLIP recovery gain 为 +0.0090, similarity gain 为 -0.0176。

6. 当前只能说“输出覆盖在记录层面对齐”, 不能说“严格内部候选预算完全一致”。也就是说, 相关方法都在同一批 53 个失败候选分子上各输出一条可评估修复结果, coverage 为 1.0, duplicate 为 0。但是, 方法内部使用的候选数量不同, 包括 budget=1, budget=10, budget≈16.1, 以及 7, 16, 17 等不同设置。

7. Vina 分数和 PLIP 接触恢复并不一致。例如 no-feedback/rerank 的 Vina 均值可以接近 editable-contact, 但 PLIP recovery gain 为 0。因此 Vina 只能作为补充诊断指标, 不能作为修复成功的主证据。

8. PoseBusters 只能作为有限的几何诊断。expanded subset35 写出 35/35 summary, 其中 11/35 timeout, 24 条可判定记录 full pass 为 0。这说明 PoseBusters 的 reference consistency 与当前局部编辑任务不完全匹配, 不能作为当前主指标。

9. directional classified 和 directional learned 两类最近蛋白原子方向特征在 fallback contact recovery/similarity 上为负, 已决定不跑正式评估。该负结果必须保留, 不能隐藏。

10. 3ERT seed2 case 可以作为机制展示: feedback repair 能恢复一个 PLIP interaction。但这只是 case study, 不能替代三种子统计结果。

### 2.2 允许主张

当前可以谨慎主张:

- 项目定义了一个窄任务: 在固定骨架和固定可编辑区域内, 根据失败候选分子和结构化失败反馈做三维局部修复。
- 在当前诊断子集上, 使用失败反馈的方法显示出正式 PLIP recovery gain 的正向机制信号。
- shuffled-feedback 消融支持“反馈内容本身有贡献”, 但 learned/ridge/budgeted learned 的绝对提升幅度仍然较小。
- shallow learned policies 只能作为浅层学习对照、消融或神经网络路线的前置证据, 不能作为最终主模型。
- editable-contact/full search 可以作为搜索式教师和伪标签来源, 但不是训练得到的神经网络模型, 也不能放进严格预算匹配的神经网络公平主表。
- 当前文献复核下, direct collision risk 可写为 “Low under current review”, 但 adjacent risk 仍为 Medium, 需要继续维护 literature matrix。

### 2.3 禁止主张

当前不能这样写:

- 不能说当前结果已经达到 BIBM full paper 主模型水平。
- 不能说当前方法已经是完整的 neural repair model。
- 不能把任务泛化成广义 pocket-aware generation, R-group generation, affinity optimization, docking-score optimization 或 diffusion molecular optimization。
- 不能把 Vina 分数写成修复成功、redocking success 或模型选择依据。
- 不能只看正式评估 JSONL 行数。PLIP/Vina 证据必须来自 `pfr-eval-tools`, 并逐条确认 `plip_error` 和 `vina_error` 为空。
- 不能把 PoseBusters full pass 当成当前主指标。
- 不能单独写“same-budget 已成立”。必须写成: 输出覆盖在记录层面对齐, 但严格内部候选预算尚未匹配。
- 不能把 coordinate_rollback, feedback_rule_repair, no_failed_candidate_policy 或 reference-ligand-starting policy 写作公平对照。它们只能作为 sanity check 或 oracle upper bound。
- 不能按 failed-candidate record 随机划分数据。因为同一复合物下多个扰动会泄漏 pocket geometry, reference interaction pattern 和 ligand context。
- 不能隐藏负结果, 包括 full-pose Vina docked failures gain_success 0.0, anchor-preserved Vina local-edit 过于容易, directional feature negative, Vina/PLIP mismatch, PoseBusters mismatch 等。

## 3. 投稿信心等级

这里的“投稿信心”不是录取概率, 而是内部证据成熟度。它只用于判断项目是否可以进入下一阶段, 不应在论文中作为保证性结论。

| 等级 | 含义 | 判定条件 | 当前状态 | 适合论文形态 |
|---|---|---|---|---|
| T0 | 内部技术积累 | 数据、schema 或正式评估还不可靠 | 不作为当前定位 | 内部技术报告或工具积累 |
| T1 | 诊断性机制证据 | 有可复核正式诊断结果, 但没有规模化神经网络模型 | 当前状态 | 诊断协议或机制证据 |
| T2 | 诊断基准候选 | 数据、划分、评估和对照较成熟, 但神经网络主模型不足 | 后续可能 | benchmark/protocol paper |
| T3 | full paper 主实验候选 | 神经网络 full-feedback 模型在 held-out split 和多种子正式指标下稳定超过关键对照 | 尚未达到 | full paper 主实验候选 |
| T4 | 投稿就绪证据链 | T3 结果通过预算、公平对照、统计、局限性和可复现性检查 | 尚未达到 | full paper submission-ready |

当前项目应标注为 **T1: 诊断性机制证据**。只有当真正的神经网络学生模型在 held-out complex/scaffold/family split 上取得多种子、正式 PLIP、几何有效性和预算审计一致正结果后, 才能升级到 T3 或 T4。

## 4. 统一任务定义

统一输入包括:

- 蛋白口袋 `P`。
- 失败候选分子 `C_fail`。
- 固定骨架 mask `S`。
- 可编辑原子或片段 mask `M`。
- anchor atoms `A`。
- 结构化失败反馈 `F_fail`。
- 可选修复预算 `B`。

统一输出不是从零生成完整分子, 而是在同一个可编辑区域内输出局部修复动作或修复后坐标。允许的输出包括:

- 坐标位移。
- 刚体变换。
- 扭转角更新。
- 被选择的原子或片段。
- 动作类型。
- 置信度。
- 预测增益。
- hard-filter / projection 状态。
- 预算审计信息。

模型必须显式读取失败候选分子的三维结构、蛋白口袋局部环境、可编辑区域、anchor mask 和结构化失败反馈。固定骨架和 anchor 必须 hard clamp, 或通过可审计 projection 保持不变。任何输出都必须能追踪到 action, mask, budget, split 和正式评估记录。

模型选择阶段禁止使用 test official PLIP, test reference interaction, Vina-only score, PoseBusters full pass 或任何 test oracle selection。如果使用 top-K 或候选重排, 选择规则必须提前固定, 且不能依赖测试集 reference ligand 或测试集正式指标。

### 4.1 Failed ligand candidate 的三类来源

为了避免任务被质疑为只是在人工扰动上自娱自乐, failed ligand candidate 不应只保留一种来源。推荐分三类来源, 并按阶段使用。

| 来源 | 定义 | 主要用途 | 是否进入训练 |
|---|---|---|---|
| 人工受控扰动失败样本 | 从真实配体出发, 固定 scaffold/anchor, 只扰动 editable region, 构造 contact loss, clash, geometry invalid 或 anchor invalid 等失败 | 主训练、主测试、teacher replay、MVP sanity | 是, 第一版主来源 |
| baseline 失败样本 | 从 Best-of-N, rerank-only, direct regeneration 等对照方法的失败输出中筛选 | hard-case 增强、压力测试、错误分析 | 可以分阶段进入训练, 但只能使用 train split 内样本 |
| 生成/编辑模型失败样本 | 从 pocket-conditioned generation 或 editing model 的输出中筛选失败但可修复的候选 | 真实应用压力测试、外部分布泛化、后期增强 | 第一版不作为主训练来源; 后期可用 train split 内样本增强 |

核心原则是: **人工受控扰动保证严谨性和可复现性, baseline/生成模型失败样本保证真实性和应用说服力。** baseline/生成模型失败样本可以用于训练增强, 但必须严格来自 train split, 禁止 val/test 失败样本反流进训练。

推荐训练集分三档:

| 训练版本 | 训练数据 | 目的 |
|---|---|---|
| Train-A | 只用人工受控扰动失败样本 | 建立最干净、最可控的主模型 baseline |
| Train-B | 人工受控扰动 + train split 内 baseline 失败样本 | 学习更真实的 baseline failure mode |
| Train-C | 人工受控扰动 + train split 内 baseline 失败样本 + train split 内生成/编辑模型失败样本 | 构建更接近真实应用的增强模型 |

推荐测试集分三块:

| 测试集 | 来源 | 作用 |
|---|---|---|
| Test-A | 人工受控扰动失败样本 | 主结果和公平统计 |
| Test-B | baseline 失败样本 | 困难案例压力测试 |
| Test-C | 生成/编辑模型失败样本 | 真实应用泛化测试 |

因此, 主论文不应只依赖人工扰动测试集。更稳妥的写法是: 主结果在 controlled-failure test set 上报告, 同时在 baseline-induced 和 generator-induced failure test sets 上报告压力测试结果。

## 5. Gate 编号说明

本文档中的 Gate 指“阶段验收门槛”。Gate 后面的数字只是编号, 不是分数, 不是优先级, 也不是投稿概率。

Stage 是执行阶段。Gate 是验收条件。一个阶段可以对应多个 Gate, 同一个 Gate 也可能在多个阶段反复使用。

| Gate | 中文名称 | 含义 |
|---|---|---|
| Gate 0 | 主张冻结 | 防止把诊断性证据写成最终神经网络模型或 BIBM-ready result。 |
| Gate 1 | Schema 和 metadata 冻结 | 确保失败候选分子、反馈、mask、动作、预算、split 和评估状态可追踪。 |
| Gate 2 | 教师 trace 和 replay 审计 | 确保教师动作、top-M 候选、hard negatives 和 replay 可复现。 |
| Gate 3 | 神经网络 MVP 前置检查 | 确保小样本过拟合、动作 replay、hard clamp、equivariance 和置信度头通过 sanity check。 |
| Gate 4 | 数据扩展和清洗 | 确保数据规模、数据质量、失败候选覆盖和清洗记录达到主实验最低要求。 |
| Gate 5 | Split 防泄漏 | 禁止 failed-candidate record random split, 确保 held-out complex/scaffold/target split 可审计。 |
| Gate 6 | 正式评估审计 | 确保 PLIP/Vina/PoseBusters 的来源、错误字段、timeout 和 unavailable rate 已报告。 |
| Gate 7 | 预算公平性 | 同时报告输出预算和内部候选预算, 并分离不同预算表。 |
| Gate 8 | 对照和消融完整性 | 确保 no-feedback, shuffled-feedback, rerank-only, Best-of-N, direct regeneration, shallow learned, teacher 和模型消融覆盖。 |
| Gate 9 | 统计稳健性 | 确保多种子、paired/grouped statistics, bootstrap CI 和分层分析合理。 |
| Gate 10 | 方案一推进门槛 | 只有 full-feedback 神经网络学生模型稳定超过 no-feedback/shuffled/shallow learned, 才能升级为主模型候选证据。 |
| Gate 11 | Flow/diffusion 启动门槛 | 只有数据量、top-K 非 oracle 选择、预算审计和 deterministic EGNN baseline 都成熟后, 才启动 flow/diffusion。 |
| Gate 12 | 投稿主张门槛 | 只有神经网络模型在 held-out split、多种子、正式指标、几何有效性和预算审计上闭环, 才能写 full paper 主模型主张。 |

## 6. 十二阶段总览

| 阶段 | 名称 | 主要 Gate | 核心产物 | 不通过时停止条件 | 对 full paper 的贡献 |
|---|---|---|---|---|---|
| 1 | 主张和证据边界冻结 | Gate 0 | Claim control checklist | 出现过度主张 | 防止论文叙事失控 |
| 2 | Schema 和 metadata 冻结 | Gate 1 | Unified repair schema | 记录无法追踪 mask/budget/split/eval | 建立可复现基础 |
| 3 | 正式证据台账和负结果登记 | Gate 6 | Verified evidence ledger | PLIP/Vina error 或 provenance 不清 | 建立可信起点 |
| 4 | 教师 trace 和 replay 审计 | Gate 2 | Teacher action trace dataset | replay 破坏 scaffold/anchor | 把搜索信号转成可学习伪标签 |
| 5 | 数据扩展和清洗 | Gate 4 | 500-2000 complexes 数据池 | 可用复合物不足或清洗失败 | 从 smoke 走向主实验规模 |
| 6 | Split 防泄漏设计 | Gate 5 | held-out complex/family/scaffold split | 使用 record random split | 保证外推评估可信 |
| 7 | 大规模教师标签和 hard negatives | Gate 2/4 | 5k-40k repair examples 目标集 | teacher coverage 过低或 oracle contamination | 提供神经网络监督源 |
| 8 | LocalEditNet MVP 前置检查 | Gate 3 | overfit/equivariance/clamp sanity | 小样本 overfit 或 clamp/equivariance 失败 | 降低大规模训练风险 |
| 9 | 教师-学生 LocalEditNet 主实验 | Gate 10 | held-out neural student results | full-feedback 不超过关键对照 | 形成主模型候选证据 |
| 10 | 对照、消融和预算治理 | Gate 7/8 | budget-stratified fair tables | 内部预算不清或 oracle 混入主表 | 保证胜负关系可信 |
| 11 | 正式评估和统计稳健性 | Gate 6/9 | official metric tables | official errors 或统计口径不合格 | 建立主结果可信度 |
| 12 | 二线路线和投稿形态决策 | Gate 11/12 | go/no-go decision | 未达 T3/T4 却强写 full paper 主模型 | 决定最终论文形态 |

## 7. 逐阶段路线

### 阶段 1. 主张和证据边界冻结

目标是先固定核心叙事: 本项目研究的是“基于失败反馈的蛋白口袋三维局部分子修复”。当前只能写成诊断协议和机制层证据, 不能写成最终神经网络修复模型。

需要完成三件事: 第一, 写清楚允许主张和禁止主张。第二, 所有结果句都标注为“已验证结果”“初步证据”“设计方案”或“待验证假设”。第三, 保证论文贡献句不过度扩大任务范围。

Gate 0 通过标准是: 文档明确写出当前不是 BIBM-ready 主模型结果, shallow policies 不是 neural repair model, Vina 不是修复成功指标, PoseBusters full pass 不是当前主指标, strict same-budget 尚未成立, oracle/reference-starting policies 不进入公平主表。

如果草稿中出现“已经完成 trained neural repair model”“redocking success”“state-of-the-art pocket generation”等表述, 必须先回退措辞, 再推进后续阶段。

### 阶段 2. Schema 和 metadata 冻结

目标是让每一条修复记录都可追踪。至少需要记录 failed complex, structured feedback, teacher top-1 action, teacher top-M actions, negative actions, repaired complex, score delta, split id, mask definitions, seed, output budget, internal candidate budget 和 official eval metadata。

给定任意一条 repair record, 应该能直接回答: 它修复的是哪个失败候选分子, 使用了什么反馈, 编辑了哪些原子或片段, 使用了多少内部候选, 属于哪个 split, 是否包含 oracle/reference access, PLIP/Vina/PoseBusters 是否可判定, error fields 是否为空。

如果 mask, split, budget 或正式评估来源缺失, 这条记录只能降级为 historical diagnostic 或 sanity-only, 不能进入主结果表。

### 阶段 3. 正式证据台账和负结果登记

目标是把当前所有证据按等级登记清楚, 包括正式 PLIP/Vina 结果、shuffled-feedback 消融、classified/scaled learned、PoseBusters 诊断、Vina caveat、same-budget caveat 和负结果。

证据台账必须登记: 477/477 key-baseline official records, 0 PLIP errors, 0 Vina errors; 159/159 shuffled-feedback official records, 0 PLIP/Vina errors; 53-record classified editable-contact 和 scaled learned official records; expanded subset35 PoseBusters 诊断; 输出覆盖在记录层面对齐但严格内部预算未匹配; Vina 只能作为补充诊断。

如果某个 official run 只确认了 JSONL 行数, 没有逐条确认 `plip_error` / `vina_error`, 就不能作为正式证据。如果 PoseBusters timeout/unavailable 未报告, 或 Vina 被写成主成功指标, 也必须先重新审计。

### 阶段 4. 教师 trace 和 replay 审计

editable-contact/full search 在本项目中应定位为“搜索式教师”或“伪标签来源”。它不是训练得到的神经网络模型, 也不是公平预算主表里的主对照。

本阶段要为每个失败候选分子保存教师动作候选、top-1/top-M 动作、评分字段、hard filter 状态、projection 状态、失败原因、replay 状态, 以及动作和修复后 pose 的对应关系。

Gate 2 通过标准是: 每个 teacher-labeled record 至少包含 top-1 action, top-M candidate list, candidate scores, hard filter outcomes, projection outcomes, scaffold/anchor validity, replayed repaired pose, score delta, 以及无有效动作时的 failure reason。

如果 replay 后破坏 scaffold/anchor, teacher action 和 repaired pose 无法对齐, top-M 候选大量不可区分, 或 teacher failure cases 被静默丢弃, 就必须暂停大规模标签生成和神经网络训练。

### 阶段 5. 数据扩展和清洗

目标是从 12-complex smoke 数据扩展到数百至数千个蛋白-配体复合物。主起点建议是 PDBbind refined/general, Binding MOAD 可作为补充或外部验证, CrossDocked 可作为大规模预训练或增强来源。

本阶段需要明确 failed ligand candidate 的三类来源。第一类是人工受控扰动失败样本, 作为主数据来源。第二类是 baseline 失败样本, 用于后续 hard-case 增强和压力测试。第三类是生成/编辑模型失败样本, 用于后期真实应用压力测试和外部分布泛化。第一版主训练不应一开始混合所有来源, 应先保证人工受控扰动来源可控、可追踪、可复现。

起步目标是 500-2000 个 complexes。每个 complex 生成 5-20 个失败候选分子, 形成 5k-40k 条 teacher-labeled repair examples 的候选基础。flow/diffusion 路线至少需要 10k 级 repair pairs 后再考虑。

当前 12-complex/53-candidate set 只能用于 sanity check, 小样本 overfit, case study 和 pipeline debug, 不能承担 BIBM full paper 主实验规模。

如果清洗后可用 complex 数不足数百, 或 receptor cleaning, atom mapping, anchor identification, ligand validity 大规模失败, 就不启动 full neural training。

### 阶段 6. Split 防泄漏设计

目标是禁止 failed-candidate record random split。主结果至少应使用 held-out complex split, 并尽量补充 held-out target/family split, scaffold split 和 held-out failure-type analysis。

每条记录必须绑定 split_id, complex_id, target/family cluster, ligand scaffold cluster, failure type 和 seed。同一 complex 下的所有扰动必须进入同一个 split。

如果同一 complex 的不同 failed candidates 跨 train/test, 或统计时把同一 complex 下多个 perturbations 当成独立样本, 就必须重新 split 和重新统计。

### 阶段 7. 大规模教师标签和 hard negatives

目标是在扩展数据上生成 teacher top-1 actions, teacher top-M actions, hard-negative actions 和 repaired complexes。这些样本要支持 supervised imitation, top-M distillation, ranking loss 和 confidence/gain prediction。

训练数据建议分阶段扩展。Train-A 只使用人工受控扰动失败样本, 用于建立干净可控的主模型。Train-B 在 Train-A 基础上加入 train split 内 baseline 失败样本, 用于学习更真实的 baseline failure mode。Train-C 再加入 train split 内生成/编辑模型失败样本, 用于构建更接近真实应用的增强模型。任何 baseline/生成失败样本都不能从 val/test split 反流进训练。

起步应形成数千级可审计 teacher-labeled examples, 目标推进到 5k-40k repair examples。每条 label 必须有 split_id, budget, top-1/top-M, negative actions, score delta, hard-filter status 和 replay status。

如果 teacher coverage 过低且无法按 failure type 解释, hard negatives 太弱, top-K selection 使用 test reference 或 official PLIP oracle, 就只能先使用 high-confidence subset 训练 MVP, 或回到 teacher scoring/negative mining。

### 阶段 8. LocalEditNet MVP 前置检查

目标是在 10-50 个 case 上验证最小可行神经网络。模型可以采用 EGNN/GVP/PaiNN 风格, 显式读取蛋白口袋、失败候选分子、固定骨架、可编辑区域、anchor 和结构化失败反馈, 输出局部动作或坐标修复。

MVP 必须通过五项检查: 小样本 overfit, action replay, scaffold/anchor hard clamp, 坐标变换一致性或 equivariance, confidence/gain head sanity。初版不建议以强化学习作为起点。

如果模型无法在 10-50 个 case 上 overfit teacher actions 或 repaired coordinates, 或 hard clamp/equivariance/action replay 任一失败, 就不能启动大规模训练。应先检查 schema, mask, coordinate normalization, loss scaling, feedback representation 和 hard negatives。

### 阶段 9. 教师-学生 LocalEditNet 主实验

目标是训练真正的 failure-feedback-conditioned neural local repair model。模型通过教师伪标签学习局部修复动作, 并使用 top-M teacher actions, hard-negative ranking 和 confidence/gain heads 提升非 oracle 选择能力。

主实验建议至少比较三种训练版本: Train-A controlled-only, Train-B controlled + train-split baseline failures, Train-C controlled + train-split baseline failures + train-split generator/editor failures。这样可以回答两个关键问题: 只用人工扰动训练是否足够, 以及加入更真实失败样本后是否提升真实失败测试集表现, 同时不损害人工扰动主测试集表现。

模型选择规则必须提前固定, 不能使用 test official PLIP, test reference interaction, Vina-only score 或 PoseBusters full pass 做 oracle selection。如果使用 top-K, 也不能依赖测试集 reference ligand 或测试集正式指标。

Gate 10 通过标准是: 至少 3 个 seeds; 主结果至少包含 held-out complex split; 每个模型和对照都对同一批 failed candidates 生成可评估输出; 同时报告输出预算和内部候选预算; validation selection 规则预先定义。

成功标准是: full-feedback neural student 在 held-out complex split 上稳定超过 no-feedback neural variant, shuffled-feedback variant, rerank-only, identity/failed candidate 和 shallow learned policies。如果它能在 budget=1 或 budget=10 下接近或部分替代搜索式教师的 recovery gain, 就可以进入 full paper 主实验候选层级。

如果 full-feedback 不超过 no-feedback/shuffled, 或只在 train-like split 有效, 或结果依赖 oracle post-selection / 不公平预算, 就不能进入 self-supervised 或 diffusion 路线。

### 阶段 10. 对照、消融和预算治理

目标是建立公平对照分类、消融矩阵和按预算分层的结果表。当前固定表述仍然是: 输出覆盖在记录层面对齐, 但严格内部候选预算尚未匹配。

主表不能混写 budget=1, budget=10, higher-budget teacher/reference 和 oracle upper bound。每个对照方法的 input access, feedback access, reference access, internal candidate count, selection rule 和 official eval status 都必须写清楚。

Gate 7/8 通过标准是: 所有主表同时给出输出预算和内部候选预算; budget=1, budget=10, higher-budget teacher/reference, oracle sanity 分表展示; coordinate_rollback, feedback_rule_repair, no_failed_candidate_policy, reference-ligand-starting policy 不进入公平胜负表。

如果某个 baseline 的内部预算不清, 或包含 oracle/reference access 但未标注, 该结果只能降级为 supplemental, teacher/reference 或 sanity。

### 阶段 11. 正式评估和统计稳健性

目标是对主模型、对照和消融执行正式 PLIP/Vina/PoseBusters 诊断, 并进行防泄漏统计分析。正式 PLIP/Vina 必须使用 `pfr-eval-tools`, 并逐条报告 `plip_error`, `vina_error`, timeout 和 unavailable rate。

PLIP recovery gain 和 PLIP similarity gain 必须分开报告。Vina 只能作为补充诊断, 不能作为 repair success 或 model selection。PoseBusters 只能作为有限几何诊断, 必须报告 timeout 和可判定记录数。

测试集建议分三块报告。Test-A 是人工受控扰动失败样本, 用于主结果和公平统计。Test-B 是 baseline 失败样本, 用于困难案例压力测试。Test-C 是生成/编辑模型失败样本, 用于真实应用泛化测试。主论文应同时报告 controlled-failure 主测试结果和 realistic-failure 压力测试结果, 以回应“人工扰动是否只是 toy task”的质疑。

Gate 6/9 通过标准是: 每个主结果表都有正式评估来源、错误字段、coverage、duplicate、timeout/unavailable rate; 至少 3 个 seeds; 统计按 complex 聚合或使用 paired test; bootstrap CI 不能把同一 complex 下多个 perturbations 当成独立样本。

如果 PLIP/Vina errors 未处理, official JSONL 行数被当作完成证据, Vina-only 被用于模型选择, 或 record-level 显著但 complex-level 不显著却仍写强结论, 就必须回退到 metric audit 或降低 claim。

### 阶段 12. 二线路线和投稿形态决策

目标是根据阶段 1-11 的结果决定是否进入 self-supervised iterative refiner, local flow/diffusion, 或最终投稿主张冻结。

self-supervised refiner 的进入条件是: 阶段 9 的 neural student 已经在 held-out complex/scaffold split 上稳定超过 no-feedback/shuffled/shallow learned, 并且确实需要进一步改善 low-data generalization 或 feedback grounding。

local flow/diffusion 的进入条件更严格: 至少 10k repair pairs, fixed-topology editable-region coordinate refinement 任务已定义, scaffold/anchor hard clamp 已验证, top-K selection 非 oracle 且 budget audit 可复现, deterministic EGNN baseline 已经足够强。flow/diffusion 不应从一开始生成 atom types 或 bonds, 也不能拖垮主线。

Gate 11/12 通过标准是: 只有真正的神经网络模型, 而不是 shallow policy, 在 held-out split、多种子、正式 PLIP 指标、scaffold/anchor/editable validity 和有限几何诊断上取得一致正结果后, 才能升级为 full paper 主模型主张。

如果阶段 9 未超过 no-feedback/shuffled, 数据未达到 10k repair pairs 却尝试 flow/diffusion, 或最终主张试图把诊断子集写成 full paper 主模型结果, 就必须执行论文形态回退。

## 8. 跨阶段管控清单

| 管控项 | 必须检查的问题 | 不通过时处理 |
|---|---|---|
| 主张控制 | 是否把当前结果写成 final neural model 或 BIBM-ready result | 回到阶段 1, 降级为诊断性叙事 |
| 证据来源 | 正式证据是否来自 `pfr-eval-tools`, 且错误字段为空 | 回到阶段 3/11 重新审计 |
| Schema 完整性 | failed candidate, masks, feedback, action, budget, split, eval status 是否完整 | 缺失记录降级为 historical/sanity-only |
| 教师定位 | editable-contact/full search 是否被标注为搜索式教师, 而不是 trained neural model | 移入 teacher/reference 或 higher-budget 表 |
| 教师 replay | replay 是否保持 scaffold/anchor, trace 是否可复现 | 暂停教师标签和神经网络训练 |
| 数据质量 | 可用 complexes 是否达到数百级, cleaning/exclusion 是否可追踪 | 不启动 full neural training |
| Split 防泄漏 | 是否存在 record random split 或同一 complex 跨 split | 重新 split |
| 预算审计 | 是否同时报告输出预算和内部候选预算 | 不进入公平主表 |
| Oracle access | 是否使用 reference-starting, test reference, official PLIP oracle 或 Vina-only selection | 降级为 oracle sanity 或排除 |
| 对照覆盖 | no-feedback, shuffled, rerank, Best-of-N, direct regeneration, shallow learned, teacher 和关键消融是否覆盖 | 补实验或明确排除理由 |
| 指标解释 | PLIP recovery/similarity 是否分开, Vina/PoseBusters 是否限定解释 | 修订 metric section |
| 统计口径 | 是否 3 seeds, paired/grouped by complex, subgroup analysis | 降低 claim 或补统计 |
| 负结果 | directional feature negative, Vina/PLIP mismatch, PoseBusters mismatch 是否保留 | 加入 negative registry |
| 文献风险 | direct collision Low 是否写成 under current review, adjacent risk Medium 是否维护 | 更新 literature matrix |
| 资源控制 | 主线未过时是否提前启动 self-supervised 或 flow/diffusion | 停止二线路线, 回到主线排查 |

## 9. 对照和消融矩阵

| 类别 | 方法或消融 | 定位 | 表格位置 | 解释边界 |
|---|---|---|---|---|
| Identity | failed candidate / no-op | 不修复起点 | diagnostic baseline | 衡量失败候选本身表现 |
| No-feedback | 不读结构化反馈的方法 | 公平对照 | fair baseline | 测试反馈是否必要 |
| Shuffled-feedback | 读错配反馈的方法 | 公平消融 | fair ablation | 测试反馈内容是否有效 |
| Rerank-only | 不使用有效反馈的重排 | 公平或预算分层对照 | budget table | 当前 PLIP gain 为 0, Vina 不代表成功 |
| Best-of-N | 多候选选择 | 预算分层对照 | budget table | 当前为负, 不应隐藏 |
| Direct regeneration | 直接再生成 | 压力对照 | baseline/stress table | 当前为负, 不能写成主线替代 |
| Shallow learned | nearest-neighbor, ridge, classifier 等 | 浅层学习对照 | shallow baseline table | 只能作为前置证据, 不是 neural repair model |
| 搜索式教师 | editable-contact/full search | 伪标签来源 | teacher/reference table | 不是 trained neural model, 不进严格公平主表 |
| 反馈字段消融 | geometry-only, interaction-only, global-only, full feedback | 反馈有效性检查 | feedback ablation table | 检验 interaction feedback grounding |
| 架构消融 | no pocket, no equivariance, no teacher imitation, no hard negatives 等 | 模型设计检查 | architecture ablation table | 检验神经网络设计必要性 |
| 预算消融 | top-1 vs top-K, budget=1 vs budget=10 | 预算敏感性检查 | budget table | 不得混写 strict same-budget |
| Oracle sanity | coordinate_rollback, reference-ligand-starting 等 | 上界或 sanity | appendix | 不作为公平 baseline |
| 已否定路线 | directional learned/classified | 负结果记录 | negative registry | fallback 为负, 不跑 official |

## 10. 指标和评估清单

### 10.1 主指标

- 正式 PLIP interaction recovery gain。
- 正式 PLIP similarity gain。
- recovery 和 similarity 必须分开报告。
- 所有正式 PLIP 证据必须来自 `pfr-eval-tools`, 并报告 `plip_error` 和 unavailable rate。

### 10.2 局部修复有效性指标

- scaffold preservation。
- anchor drift / anchor validity。
- editable atom/fragment validity。
- local geometry validity。
- clash reduction。
- hard-filter pass rate。
- projection/clamp status。
- action replay validity。

### 10.3 补充诊断

- Vina 只能作为补充诊断, 不能写作 repair success, redocking success 或 model selection criterion。
- PoseBusters 只能作为有限几何诊断, 必须报告 timeout、可判定记录数、full pass 和 submetrics。

### 10.4 正式评估要求

- 不能只看 JSONL 行数。
- 每条 record 都要检查 `plip_error` 和 `vina_error`。
- 记录 timeout, unavailable, duplicate, coverage。
- `pfr` 环境写出的 all-error official 文件必须排除。
- official eval config, receptor/ligand provenance, atom mapping 和 file path 必须可追踪。

### 10.5 预算和覆盖要求

- 固定表述: 输出覆盖在记录层面对齐, 但严格内部候选预算尚未匹配。
- 同时报告 output budget 和 internal candidate budget。
- budget=1, budget=10, higher-budget teacher/reference, oracle sanity 分表。
- 不得把 teacher/search budget 与 budget=1 neural output 混写成 strict same-budget comparison。

### 10.6 统计要求

- 至少 3 个 seeds。
- paired comparison 使用同一批 failed candidates 或同一 complex aggregation。
- bootstrap CI 不能把同一 complex 下多个 perturbations 当成独立样本。
- 按 failure type, editable atom count, contact-loss severity, target/family, scaffold cluster, split type 和 budget 分层。
- 如果 subgroup 为负或不稳定, 必须报告。

### 10.7 模型选择禁令

- 禁止用 test official PLIP 做 selection。
- 禁止用 test reference interaction 做 selection。
- 禁止用 Vina score-only 做 selection。
- 禁止用 PoseBusters full pass 做 oracle selection。
- 禁止用 test reference ligand 或 official test metrics 做 top-K oracle post-selection。

## 11. 风险和回退策略

| 风险 | 触发信号 | 回退策略 |
|---|---|---|
| 主张过度 | 当前结果被写成 BIBM-ready 或 final neural model | 回到诊断协议和机制证据叙事 |
| 教师不可靠 | replay 破坏 scaffold/anchor, trace 不可复现 | 暂停阶段 7/9, 修复 action parameterization 和 hard clamp |
| 数据规模不足 | 清洗后可用 complexes 不足数百 | 不启动 full neural training, 收缩到高质量子集 |
| Split 泄漏 | 同一 complex 的扰动跨 train/test | 重新 split, 禁止 record random split |
| 预算不公平 | internal candidate budget 不清或混表 | 分离预算表, 降级不清记录 |
| 正式评估污染 | error fields 非空或只看 JSONL 行数 | 重新用 `pfr-eval-tools` 评估 |
| Vina/PoseBusters 误读 | Vina 被写成 success, PoseBusters full pass 被写成主指标 | 改为补充诊断或有限几何诊断 |
| 神经网络学生不稳 | full-feedback 不超过 no-feedback/shuffled | 不进入二线路线, 回到 feedback、teacher、negatives、data 排查 |
| 统计不稳 | record-level 为正, complex-level 不显著 | 降级为 preliminary, 补 grouped analysis |
| 文献撞题风险 | adjacent work 出现更接近组合 | 更新 novelty framing, 收窄任务定义 |
| diffusion 拖垮主线 | 未满足 10k repair pairs 或预算审计即启动 | 停止 diffusion, 回到 deterministic LocalEditNet |
| 资源分散 | 多路线并行导致主线延迟 | 优先阶段 1-11, 二线路线条件性启动 |

### 11.1 最终论文形态三档回退

1. **Gate 全部通过: neural local repair full paper。**  
   条件是 full-feedback 神经网络模型在 held-out split、多种子、正式指标、预算分层对照和 grouped statistics 下稳定优于关键对照, 且 validity/geometry 不恶化。

2. **神经网络学生不稳, 但 benchmark/data/eval 成熟: diagnostic benchmark/protocol paper。**  
   重点写任务定义、结构化失败反馈、正式评估协议、公平对照治理、负结果和 teacher-student future route。

3. **数据或正式评估仍不成熟: internal technical report + tooling backlog。**  
   重点保留 cleaning, schema, official eval harness, teacher trace, negative registry 和 literature matrix, 不强行投稿 full paper 主模型。

## 12. 最终优先级

近期最安全的执行顺序是:

1. **先完成阶段 1-3:** 冻结主张、schema 和当前证据台账, 防止过度表述和错误证据污染后续路线。
2. **再完成阶段 4:** 审计教师 trace 和 replay。LocalEditNet 能否成立, 取决于搜索式教师标签是否可 replay、可审计、可学习。
3. **然后推进阶段 5-7:** 扩展数据, 防止 split 泄漏, 构建大规模教师标签和 hard negatives。当前 12-complex/53-candidate set 只能用于 sanity、overfit、case study 和 pipeline debug。
4. **再进入阶段 8-9:** 先做 LocalEditNet MVP, 再做教师-学生主实验。如果小样本 overfit、equivariance 或 clamp 不通过, 不启动大规模训练。
5. **随后完成阶段 10-11:** 做对照、消融、预算治理、正式评估和 grouped statistics。所有正结果都必须经过预算分层和正式工具链审计。
6. **最后才进入阶段 12:** 只有 deterministic LocalEditNet 主线站稳后, 才考虑 self-supervised 或 flow/diffusion。flow/diffusion 必须满足 10k repair pairs、固定拓扑局部坐标修复、非 oracle top-K 选择和可复现预算审计。

一句话总结: **先把诊断证据、教师标签、数据划分和 LocalEditNet 主线做稳, 再谈二线路线和 full paper 主张。如果关键 Gate 未通过, 应回退到 diagnostic-method framing, 而不是放大主模型主张。**
