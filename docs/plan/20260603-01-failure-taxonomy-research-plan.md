# 失败样本错误类型与可修复性调研 Prompt

请围绕 pocket-conditioned molecule generation, structure-based drug design, docking/refinement, ligand pose correction, molecular editing, fragment growing/linker design 等相关方向, 调研“失败样本如何定义、分类、判定和统计”, 为 `Failure-Feedback-Conditioned Repair for Pocket-Aware 3D Local Molecular Editing` 课题设计 failure taxonomy 和可修复性边界提供依据。

## 调研目标

本次调研不是复现本地实验, 也不是统计本项目已有样本。目标是从经典和较新以及影响较大的相关工作中梳理:

1. 相关工作如何定义 failed sample / failed molecule / bad pose / invalid output。
2. 是否存在系统的 failure taxonomy, 或者只是零散报告 validity, docking score, clash, interaction, PoseBusters pass rate 等指标。
3. 错误类型有多少种, 每类如何定义, 是否允许一个样本具有多个错误标签。
4. 每类错误使用什么工具、指标或阈值判定, 这些工具和阈值是否有文献或官方依据。
5. 失败样本来自哪里, 包括生成模型、docking/refinement pipeline、人工扰动、传统 baseline、多轮采样或筛选流程中的 rejected/intermediate samples。
6. 相关工作主要关注修复哪些错误, 哪些错误被认为可修复, 哪些被认为不可修复或超出任务范围。
7. 相关工作是否统计失败类型占比, 还是只报告 overall success rate 或 aggregate metrics。

## 必须遵守的原则

- 禁止臆想 taxonomy, 标签定义, 工具阈值或文献结论。
- 每个重要结论必须给出可核验来源, 包括论文、官方工具文档、代码仓库或 benchmark 文档。
- 如果没有发现系统 taxonomy, 请明确说明“未发现系统分类”, 不要强行声称已有标准。
- 请区分“文献已明确提出的错误类型”和“我们根据多个已有指标整理出的 operational category”。
- 请区分“错误类型”, “评价指标”, “筛选规则”和“修复目标”, 不要直接把指标名称等同于错误类别。
- 请优先关注与 protein pocket, ligand 3D pose, pocket interaction, scaffold/anchor constraint, local editing/repair 相关的工作。

## 重点调研问题

### 1. 错误类型和标签体系

请调研相关工作如何对失败样本进行分类。重点回答:

- 是否已有 failure taxonomy?
- 错误标签有哪些?
- 每个标签如何定义?
- 一个样本是否可以有多个错误标签?
- 是否区分 primary failure type 和 secondary failure tags?
- 是否有专门面向 failed ligand repair, pose repair, molecule repair 或 local editing failure 的分类体系?

### 2. 错误类型的判定工具和方法

请调研相关工作如何把“错误”转化为可判定的 operational criteria。不要只列工具名, 要说明判定逻辑、指标含义、阈值来源和适用边界。

重点回答:

- 错误类型是通过规则、benchmark checks、评价指标、人工检查、reference comparison, 还是模型/流程内部状态判定?
- 每类错误对应哪些 observable evidence? 例如 chemical invalidity, 3D geometry violation, pocket clash, interaction loss, docking failure, scaffold mismatch, anchor mismatch, constraint violation。
- 相关工作是否给出明确阈值? 阈值来自工具默认设置、benchmark 标准、论文经验设定, 还是作者自定义 heuristic?
- 判定工具或指标是否被广泛使用? 是否有官方文档、benchmark paper 或代码实现支持?
- 同一错误是否可能被多个工具从不同角度判定? 不同工具结果冲突时, 相关工作如何处理?
- 工具运行失败是否被当作 failure type, 还是单独作为 pipeline/evaluation failure 记录?

可重点关注但不限于:

- chemical validity / sanitization: RDKit 等。
- 3D pose plausibility / geometry checks: PoseBusters 或类似 benchmark checks。
- docking score / docking success / pose quality: Vina, GNINA, redocking RMSD 等。
- protein-ligand interaction: PLIP, interaction fingerprints, contact recovery 等。
- steric clash / pocket overlap: clash check, distance-based violation 等。
- scaffold / anchor / constraint preservation: substructure match, atom mapping, constraint satisfaction 等。
- property constraints: QED, SA, Lipinski, drug-likeness filters 等。

对每种判定方法, 请尽量记录:

- 它判定什么错误。
- 它依赖什么输入。
- 它输出什么指标或布尔结果。
- 阈值或 pass/fail 标准来自哪里。
- 它更适合作为 failure label, secondary tag, filtering criterion, 还是 evaluation metric。

### 3. 失败样本来源和应用场景

请调研失败样本在相关工作中是如何产生和被使用的。不要只按任务名称罗列论文, 要说明样本来源、使用场景、筛选过程和与 repair 任务的关系。

重点回答:

- 失败样本来自模型原始输出、传统方法或 pipeline 输出、人工扰动、benchmark 构造、筛选阶段 rejected samples, 还是多阶段流程中的 intermediate candidates?
- 这些来源分别服务于什么任务场景? 例如 de novo generation, structure-based generation, docking/pose prediction, pose refinement, linker/fragment design, constrained generation, molecular editing, ligand optimization 等。
- 相关工作是否保留和分析失败样本, 还是只报告通过筛选后的 final candidates?
- 失败样本是否接近 near-miss, 即 scaffold/anchor 或主要结构约束基本保留, 但局部几何、pocket contact 或 interaction 不满足?
- 不同来源的失败样本是否具有不同可信度和代表性? 例如模型失败样本、pipeline 失败样本、人工扰动样本各自能说明什么问题。

请主动扩展任务场景和样本来源, 不要只局限于上面的示例。

### 4. 一次性生成与多阶段采样流程

请调研相关工作中候选样本是如何从模型或 pipeline 中产生的, 并分析不同流程对“失败样本”含义的影响。不要只记录流程名称, 要关注每个阶段是否产生、保留、过滤或统计失败样本。

重点回答:

- 样本是 one-shot generation 得到, 还是 multi-sampling / best-of-N / reranking / filtering / docking / refinement / iterative editing 的多阶段产物?
- 相关工作统计的是 raw outputs, filtered outputs, selected candidates, rejected candidates, 还是 intermediate candidates?
- 多阶段流程中, 失败发生在 generation, chemical filtering, docking, reranking, refinement, selection, constraint checking 的哪一环?
- 论文是否报告各阶段的通过率、失败率或筛选条件? 如果没有, 是否只报告最终 aggregate success?
- 对我们的 repair 任务来说, 哪些阶段的失败样本更适合作为可修复对象, 哪些更适合作为背景统计或排除项?

请特别注意: 不要默认所有 rejected samples 都适合 repair。需要结合相关工作证据判断其失败程度、结构约束保留情况和修复可行性。

### 5. 相关工作关注修复什么错误

请调研已有工作实际试图修复、校正、优化或避免哪些错误。不要只列错误名称, 要说明该错误在原文中是 repair target, optimization target, filtering reason, evaluation failure, 还是 out-of-scope condition。

重点回答:

- 相关工作关注的是 molecule-level 问题, pose-level 问题, pocket-interaction 问题, constraint violation, 还是局部 editable-region 问题?
- 对每类错误, 原文是否明确认为它可修复、可优化、可通过 refinement 改善, 还是通常直接过滤/丢弃?
- 修复对象是否保留 scaffold/topology/anchor 等约束? 如果不保留, 与本项目 fixed-scaffold local repair 的关系是什么?
- 是否存在类似 near-miss repair, pose correction, local refinement, constrained editing 的任务设定?
- 哪些错误需要 global regeneration, docking redo, scaffold redesign 或 pipeline fix, 因而不适合作为本项目第一阶段主修复目标?

请把“文献实际修复的错误”和“我们可能想修复的错误”分开记录, 避免把我们的目标倒推成文献结论。

### 6. 是否统计失败占比

请调研相关工作是否系统报告不同错误类型或不同筛选阶段的比例。不要只看论文是否报告某个 metric, 要判断它是否真正给出了 failure prevalence 或 stage-wise attrition。

重点回答:

- 是否报告 invalid rate, docking failure rate, PoseBusters pass/fail, clash/geometry failure, interaction/contact failure, scaffold/anchor preservation failure 等比例?
- 是否报告多标签 failure, 还是每个样本只归入一个互斥类别?
- 是否报告 raw outputs 到 final candidates 的筛选流失过程, 例如 validity filter, property filter, docking filter, interaction filter, constraint filter 的通过率?
- 是否只报告 aggregate metrics, 如 average docking score, success rate, QED/SA, 而没有解释失败样本由哪些错误构成?
- 如果报告比例, 分母是什么? 是 raw generation attempts, valid molecules, docked poses, selected candidates, 还是 benchmark cases?
- 如果没有系统统计, 这种缺口是否可以作为我们后续 failure prevalence audit 的动机?

请把“报告了某项指标”和“系统统计了错误类型占比”区分开。

## 建议检索策略

以下关键词和方向仅作为起点, 不是完整清单, 也不是限制条件。请不要只按这些关键词逐条搜索。调研时必须根据检索结果继续扩展同义词、相关 benchmark、工具论文、综述论文、引用链、被引论文和 related work sections。

优先从以下方向展开:

1. 结构约束分子生成评价。
   - structure-based molecule generation evaluation
   - pocket-conditioned molecule generation benchmark
   - target-aware molecular generation metrics

2. 分子有效性和化学合理性。
   - molecular generation validity
   - chemical validity sanitization
   - molecule generation filtering

3. 3D pose 和 docking 质量。
   - ligand pose quality
   - docking pose plausibility
   - PoseBusters
   - docking success rate

4. protein-ligand interaction 和 pocket clash。
   - protein ligand interaction analysis
   - protein ligand clash
   - PLIP generated molecules

5. constrained generation, editing 和 repair。
   - scaffold constrained molecular generation
   - molecular editing scaffold preservation
   - ligand optimization constraint satisfaction
   - ligand pose refinement
   - molecular conformation refinement

请在检索过程中主动扩展表达方式。例如有些工作不会使用 failure taxonomy 或 repair 这些词, 但可能通过 validity, geometry check, pose plausibility, constraint satisfaction, filtering criteria, success rate 等方式讨论失败样本。

## 期望输出格式

请用中文输出, 保留必要英文术语。请尽量结构化, 但不要编造结论。

调研完成后, 请将结果整理为 Markdown 报告并放入 `docs/report/` 目录。报告命名遵守项目文档规则: `YYYYMMDD-<num>-failure-taxonomy-research-report.md`。如果报告与本计划对应, 只要求中间 slug `failure-taxonomy-research` 保持一致; 日期和 `<num>` 按实际完成日期与当天报告序号确定。

### A. 调研结论摘要

请先用简短段落总结:

- 是否发现已有系统 failure taxonomy。
- 现有工作主要如何定义失败样本。
- 是否普遍支持单样本多错误标签。
- 是否有工作系统统计 failure prevalence 或 stage-wise attrition。
- 哪些错误类型最可能与本项目 fixed-scaffold local repair 相关。

### B. 文献/工作证据表

用于记录论文、benchmark、相关工作。不要把工具细节全部塞入这一张表。

建议按以下字段整理:

| 来源 | 年份 | 任务场景 | 样本来源/流程 | 关注的失败或指标 | 是否统计占比 | 分母是什么 | 是否讨论修复 | 与本项目相关性 | 证据备注 |
|---|---|---|---|---|---|---|---|---|---|

### C. 工具/判定方法证据表

用于单独记录错误判定工具、指标和 operational criteria。

建议按以下字段整理:

| 工具/方法 | 判定对象 | 输入 | 输出 | 阈值/规则来源 | 更适合作为标签/指标/过滤规则 | 局限性 | 来源 |
|---|---|---|---|---|---|---|---|

### D. 候选 failure labels 清单

请整理候选 failure labels。每个标签必须区分“文献明确提出”还是“我们基于已有指标归纳出的 operational category”。

建议按以下字段整理:

| 标签名称 | 定义 | 文献或工具依据 | 判定依据 | 是否文献明确提出 | 证据强度 | primary/secondary 适用性 | 是否可能属于 local repair in-scope |
|---|---|---|---|---|---|---|---|

证据强度可用简洁分级, 例如:

- 强: 多篇论文、benchmark 或官方工具明确支持。
- 中: 单篇代表性论文或常用工具支持。
- 弱: 主要是从多个指标归纳, 需要后续本地审计验证。

### E. 可修复性边界和证据缺口

请总结:

- 哪些错误类型适合本项目的 fixed-scaffold local repair。
- 哪些错误类型可能需要 global regeneration, docking redo, scaffold redesign 或 pipeline fix。
- 哪些错误类型目前证据不足, 需要后续本地审计确认。
- 哪些标签最容易遗漏。
- 相关工作是否已有系统 taxonomy; 如果没有, 我们应如何构建 operational taxonomy。
- 后续本地 failure prevalence audit 前还需要查哪些来源、工具文档或 benchmark 说明。

## 重要提醒

本调研的结论将用于决定后续是否开展本地 failure prevalence audit。请避免直接给出未经证据支持的比例判断。当前阶段只需要调研相关工作和工具依据, 不需要运行本项目代码, 不需要复现实验, 不需要统计本地 outputs。
