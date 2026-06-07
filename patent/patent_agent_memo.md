# 专利代理人备忘录

## 审查结论

当前 `cn_patent_draft.md` 可以作为技术底稿, 但不适合作为直接提交文本。已根据 workflow 审查结论另行生成更收窄的代理人清理版:

- `cn_patent_draft_revised.md`

该清理版的目标是降低与国内外常见 SBDD generation、R-group generation、docking scoring/reranking、molecular optimization 方向的表述相似度。

## 未完成事项

本项目尚未完成法律意义上的专利检索。以下结论不能替代 CNIPA、Google Patents、WIPO、USPTO、EPO 或商业数据库检索:

- 暂未从项目文献矩阵中发现完全覆盖“失败候选输入 + 显式失败诊断反馈 + 固定骨架/锚点/可编辑区域约束 + 同一区域局部修复 + 相对失败候选修复增益选择”的直接公开论文线索。
- 但相邻技术风险仍为中等, 主要来自 pocket-aware generation、scaffold/R-group decoration、structure-based lead optimization、docking score reranking、Best-of-N 和 molecular optimization。

## 建议代理人重点检索关键词

中文关键词:

- 失败候选 分子 修复
- 失败诊断反馈 分子编辑
- 蛋白口袋 局部分子编辑 修复
- 固定骨架 锚点 可编辑区域 分子修复
- 蛋白-配体 相互作用恢复 分子设计
- 对接反馈 分子优化
- R 基团 修复 锚点 蛋白口袋

英文关键词:

- failed candidate molecular repair
- diagnostic feedback molecule repair
- protein pocket local molecular editing
- scaffold anchor editable region repair
- R-group repair protein pocket
- interaction recovery molecular design
- docking feedback molecular optimization
- failed local edit candidate repair

## 最小必要组合

建议正式主权利要求优先保护以下组合, 不要泛化为普通分子生成或打分优化:

1. 输入是已失败的局部编辑候选。
2. 失败候选处在同一 protein pocket, fixed scaffold, anchor, editable region 约束下。
3. 反馈至少包含非单一打分的结构化失败诊断, 如 clash、anchor deviation、contact loss、interaction loss。
4. 修复动作由失败诊断反馈条件化生成。
5. 修复动作施加在同一 editable region 或其与 anchor 连接的预定义局部范围。
6. 固定骨架和锚点映射/约束保持。
7. 目标分子按相对失败候选的 repair/recovery gain 选择。
8. 不能只依赖单一 docking score、Vina score-only、全局排序分数或普通分子性质改善。

## 需要避免的正式文本表述

- 不要声称已经完成专利检索或保证具有新颖性/创造性。
- 不要声称药效、临床效果、真实结合亲和力提升。
- 不要把机制级 smoke evidence 写成大规模泛化验证。
- 不要把 Vina score-only 或任一单一打分指标作为成功证明。
- 不要把 no-feedback / identity 的 basic success 写成修复成功。
- 不要声称所有方法 strict internal same-budget; 当前证据只支持 record-level same candidate coverage 和 internal budget 分层。
- 不要把启发式 editable-search 的强结果归因于 learned policy。

## 当前文件关系

- `technical_disclosure_outline.md`: 技术交底素材, 包含课题脉络和实验支撑。
- `cn_patent_draft.md`: 初版草稿, 内容较全, 含内部说明, 不建议直接提交。
- `cn_patent_draft_revised.md`: 根据 workflow 审查收窄后的清理版, 更适合作为交代理人的正文基础。
- `patent_agent_memo.md`: 本备忘录, 不作为正式专利正文提交。
