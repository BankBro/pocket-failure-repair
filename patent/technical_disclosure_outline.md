# 失败反馈条件化的蛋白口袋约束 3D 局部分子编辑修复方法

## 1. 拟定名称

一种基于失败诊断反馈的蛋白口袋约束三维局部分子编辑修复方法、系统及存储介质。

可选名称:

- 一种面向蛋白口袋三维分子编辑失败候选的诊断反馈修复方法。
- 一种利用蛋白-配体相互作用损失反馈的局部分子结构修复方法。
- 一种在固定骨架和锚点约束下的失败分子候选局部修复方法。

## 2. 技术领域

本技术涉及计算机辅助药物设计、结构生物信息学、三维分子生成、蛋白-配体相互作用建模和分子结构优化领域。更具体地, 涉及在蛋白口袋约束下, 对已经失败的三维局部分子编辑候选进行基于失败诊断反馈的局部修复。

## 3. 背景问题

在结构基础药物设计中, 常见任务包括 pocket-aware molecule generation、R-group generation、lead optimization、docking-based scoring 和分子重采样。这些方法通常关注从头生成或优化候选分子, 但在实际局部分子编辑过程中, 经常出现如下失败候选:

- editable region 与蛋白口袋发生空间冲突。
- 固定 scaffold 或 anchor atoms 被破坏。
- 原本需要保留或恢复的蛋白-配体相互作用丢失。
- 分子几何或局部构象不合理。
- Vina score、PLIP interaction、PoseBusters checks 或其他诊断指标显示候选不可靠。

传统处理方式通常是重新采样、Best-of-N、rerank-only 或全局打分筛选。这些方法的问题是:

1. 没有显式利用已经失败的候选结构本身。
2. 没有把具体失败原因作为下一次修复的条件。
3. 容易把“原地不动但基本合法”的候选误判为修复成功。
4. 在生成预算不受控时, Best-of-N 或 direct regeneration 可能因内部候选数更多而产生不公平比较。
5. 单独使用 docking score 或 Vina score-only 不能说明蛋白-配体相互作用是否真正恢复。

因此, 需要一种针对失败局部编辑候选的、能够利用结构化失败反馈并在相同 editable region 内进行定向修复的方法。

## 4. 要解决的技术问题

本技术希望解决以下问题:

- 如何将已经失败的局部编辑候选作为修复输入, 而不是简单丢弃并重新生成。
- 如何把 clash、anchor violation、interaction/contact loss、PLIP interaction recovery、Vina score-only、PoseBusters checks 等诊断信息编码为修复反馈。
- 如何在 fixed scaffold、anchor atoms 和 editable region 约束下只修复局部区域。
- 如何通过 repair/recovery gain 判断修复是否真的改善失败候选, 避免 identity/no-feedback 被误判为成功。
- 如何在 same-budget 或分层预算条件下比较反馈修复、no-feedback、rerank-only、Best-of-N 和 direct regeneration。

## 5. 核心技术方案

### 5.1 输入

方法输入可以包括:

1. 蛋白口袋结构。
2. 原始或参考配体结构。
3. 固定 scaffold。
4. editable region 或 R-group mask。
5. anchor atoms 或 anchor constraints。
6. 一个已经失败的局部编辑候选分子。
7. 与失败候选相关的诊断反馈特征。

诊断反馈特征可包括但不限于:

- 分子有效性、scaffold preservation、editable validity。
- anchor distance error 或 anchor validity。
- protein-ligand clash count 或最小距离。
- contact fingerprint similarity / recovery。
- PLIP interaction fingerprint, residue-level interaction recovery / similarity。
- Vina score-only 或 delta score。
- PoseBusters checks。
- QED、SA、logP、rotatable bonds 等药物化学属性。
- failure type embedding, 例如 clash、interaction loss、anchor invalid、geometry invalid 等。

### 5.2 输出

方法输出为:

- repaired editable region。
- repaired local molecule。
- repaired 3D coordinates。
- 可选 confidence、ranking score 或修复诊断报告。

### 5.3 方法流程

一个可实施流程如下:

1. 从蛋白-配体复合物中提取 pocket、reference ligand、fixed scaffold、editable region 和 anchor atoms。
2. 生成或接收失败局部编辑候选。
3. 对失败候选进行诊断, 得到结构化 feedback features。
4. 根据 fixed scaffold 和 anchor constraints 限定可编辑原子集合。
5. 根据 feedback features 生成一个或多个 editable-region repair actions。
6. 将 repair actions 应用于 failed candidate, 仅修改 editable region 或其局部三维坐标。
7. 对候选 repaired molecules 进行评估或重排序, 可使用 geometry、contact、PLIP、Vina、PoseBusters 或组合指标。
8. 输出得分最高或满足修复条件的 repaired candidate。
9. 计算相对 failed candidate 的 repair/recovery gain, 判断是否真正修复。

## 6. 可选实现方式

### 6.1 规则型或启发式 editable-contact 修复

在 fixed scaffold 和 anchor atoms 不变的前提下, 对 editable atoms 应用小范围三维偏移。候选偏移由 contact recovery、clash penalty、anchor penalty 等 oracle-free proxy 评分选择。

该实现可作为可解释的 upper-bound 或启发式 baseline。

### 6.2 learned editable-contact policy

基于其他 protein complexes 或训练样本, 从失败候选的 feedback features 中学习 editable offset 或 repair action。

可选模型包括:

- 最近邻 feedback-to-offset policy。
- ridge regression / kernel regression。
- kNN 或 small MLP。
- 等变图神经网络 local repair policy。
- diffusion-based local refinement。
- interaction-aware conditional R-group decoder。

### 6.3 budgeted learned policy

为 learned policy 分配多个内部候选预算。例如以预测 offset 为中心生成 10 个扰动候选, 再用相同的 editable-contact scoring 选择最优 repaired molecule。

该设计用于公平比较 1-shot learned policy、budgeted learned policy 和 editable-search fallback。

### 6.4 消融设置

为了证明诊断反馈的作用, 可设置如下消融:

- no-feedback。
- rerank-only。
- direct regeneration。
- Best-of-N。
- global-score-only。
- geometry-only。
- interaction-only。
- full feedback。
- shuffled-feedback。
- no-failed-candidate。

## 7. 评价指标

### 7.1 基础合法性指标

- molecule validity。
- scaffold preservation。
- editable validity。
- anchor validity。
- clash-free。

### 7.2 修复增益指标

为避免“原地不动”被误判为修复成功, 应计算 repaired candidate 相对 failed candidate 的增益, 包括:

- contact recovery gain。
- contact fingerprint similarity gain。
- PLIP interaction recovery gain。
- PLIP interaction similarity gain。
- anchor error reduction。
- clash count reduction。
- Vina-like proxy gain。

可定义 `repair_gain_success`: 在满足基础合法性条件下, 至少一个核心修复增益为正。

### 7.3 官方或外部诊断指标

- PLIP interaction profiling。
- AutoDock Vina score-only 或 docking score。
- PoseBusters checks。

注意: Vina score-only 只能作为辅助分数, 不能单独证明修复成功。

## 8. 当前实验支撑材料

当前项目中已经形成如下机制级证据:

### 8.1 contact-degraded local-edit 诊断集

- seeds 0/1/2 分别得到 19/17/17 个 failed candidates。
- 合计 53 个 contact-degraded, anchor-preserved local-edit failed candidates。
- 该集合固定 scaffold 和 anchor, 主要制造 interaction/contact loss。

### 8.2 三 seed fallback / same-budget 结果

- 22 baselines。
- 1166 evaluated records。
- record-level same-budget audit 通过: 所有 baseline 覆盖同一 53 candidates, coverage 1.0, duplicate 0。
- strict internal candidate budget 不成立, 需要按 budget type 分层报告。

关键结果:

| 方法 | internal budget | fallback gain_success | contact recovery gain |
|---|---:|---:|---:|
| no_feedback / rerank | 1 | 0.0000 | 0.0000 |
| 1-shot learned editable-contact | 1 | 0.2642 | 0.0156 |
| budgeted learned editable-contact | 10 | 0.3189 | 0.0330 |
| editable-contact / full editable search | 10 | 0.6047 | 0.0627 |
| Best-of-N | 16-17 | 0.0000 | -0.0027 |
| direct regeneration | 16-17 | 0.0588 | -0.0243 |

### 8.3 official PLIP/Vina 结果

三 seed key-baseline official PLIP/Vina:

- 477/477 records。
- PLIP 0 error。
- Vina 0 error。

official PLIP recovery gain:

| 方法 | PLIP recovery gain |
|---|---:|
| no-feedback / rerank | 0.0000 |
| 1-shot learned editable-contact | +0.0065 |
| budgeted learned editable-contact | +0.0099 |
| full editable | +0.0301 |

结论: feedback-based repair 在 official PLIP interaction recovery 上存在弱正向信号, 但幅度小, 仍属于机制级 smoke evidence。

## 9. 可作为专利创新点的方向

可考虑围绕以下技术点撰写权利要求:

1. 将失败局部编辑候选和失败诊断反馈共同作为分子修复输入。
2. 在 fixed scaffold / anchor atoms / editable region 约束下进行局部三维修复。
3. 使用 structured failure feedback 驱动 repair action, 而不是仅用全局 score rerank。
4. 使用相对 failed candidate 的 repair/recovery gain 作为修复成功判断。
5. 将 PLIP/contact interaction loss 用于生成或选择 repair actions。
6. 对 learned policy 使用 budgeted editable-offset proposal, 并在同一候选预算下进行选择。
7. 对 no-feedback、geometry-only、interaction-only、full feedback 等进行同预算或分层预算的修复比较。
8. 输出 repaired molecule 的同时输出可解释失败-修复诊断报告。

## 10. 潜在独立权利要求草案方向

### 方法权利要求方向

一种基于失败诊断反馈的蛋白口袋约束三维局部分子编辑修复方法, 包括:

1. 获取蛋白口袋结构、参考配体结构、固定分子骨架、可编辑区域、锚点原子和失败局部编辑候选分子。
2. 对失败局部编辑候选分子进行诊断, 得到至少包括几何冲突、锚点偏差或蛋白-配体相互作用损失之一的失败反馈特征。
3. 基于所述失败反馈特征和所述可编辑区域生成一个或多个局部修复动作。
4. 在保持固定分子骨架和锚点约束的条件下, 将所述局部修复动作施加于失败局部编辑候选分子的可编辑区域, 得到一个或多个修复候选分子。
5. 基于至少一个修复增益指标对所述修复候选分子进行选择, 输出修复后的三维分子结构。

### 系统权利要求方向

一种分子局部修复系统, 包括:

- 数据解析模块。
- 失败候选诊断模块。
- 反馈特征编码模块。
- 局部修复动作生成模块。
- scaffold/anchor 约束施加模块。
- 修复候选评估与选择模块。
- 修复增益报告模块。

### 存储介质权利要求方向

一种计算机可读存储介质, 其上存储有程序, 所述程序被处理器执行时实现上述方法。

## 11. 当前不能夸大的内容

后续写专利或论文时应避免以下表述:

- 不应声称已经获得 BIBM 级最终模型性能。
- 不应声称 Vina score-only 等同于真实 docking success 或结合能力提升。
- 不应把 PoseBusters full pass 作为唯一主指标。
- 不应把 identity/no-feedback 的 basic success 说成修复成功。
- 不应声称所有方法 proposal-level strict same-budget, 目前只能说 record-level same-budget 通过, internal budget 需分层。
- 不应把 handcrafted editable-search fallback 的强结果归因于 learned policy。
- 不应引用 cache 串用修复前的旧 geometry/residual 结果。
- 不应引用曾经因环境误用导致 all-error 的 official evaluation 文件。

## 12. 后续补充建议

为了让专利材料更完整, 后续可补充:

1. 系统流程图。
2. feedback feature 表。
3. repair action 示例图。
4. failed candidate -> repaired candidate 的案例对比。
5. 与 Best-of-N / rerank-only / no-feedback 的效果对比图。
6. 可选模型结构图, 如 feedback encoder + editable action decoder。
7. 更一般化的实施例, 覆盖规则型、机器学习型和深度学习型修复器。
8. 专利代理人要求的技术效果和实施例数据表。
