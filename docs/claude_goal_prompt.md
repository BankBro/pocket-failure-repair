/goal
项目: pocket-failure-repair. 目标会议: IEEE BIBM. 请在本项目内自主完成一个可复现, 可审计, 可投稿的研究闭环: Failure-Feedback-Conditioned Repair for Pocket-Aware 3D Local Molecular Editing. 核心问题: 给定 protein pocket, fixed scaffold, editable region 和一个已经失败的局部编辑候选, 模型能否利用当前失败反馈进行定向局部修复, 并在相同生成预算下比重新采样, Best-of-N, rerank-only, direct regeneration 和普通 affinity/interaction guidance 更可靠.

协作与文本规范: 与用户和仓库内协作型 Agent 交互时始终使用中文. 所有写入文件或终端的文本使用 UTF-8; 中文说明使用英文标点.

当前状态: 目录框架已创建, 原始文档已归位到 docs/, 并已创建 README.md, CLAUDE.md, docs/CLAUDE.md, docs/method_design.md, docs/literature_matrix.md, docs/STATUS.md, docs/EXPERIMENT_LOG.md. 启动后优先阅读 CLAUDE.md, docs/CLAUDE.md, docs/STATUS.md, 基于现有文件继续更新. 已存在文件优先更新, 不重复创建同名或相似文档.

自主推进原则: 用户希望尽量不参与细节决策. 对本地, 可逆, 低风险工作应自主推进, 包括文献检索, 文档更新, 环境检查, 代码实现, smoke test, 结果记录和状态更新. 只有涉及破坏性操作, 外部共享状态, 大额资源消耗, 密钥/认证, 安装不可信插件, git push/force 操作, 或方向性重大取舍时才询问用户.

先做文献与撞题: 必须自主联网检索并维护 docs/literature_matrix.md, 重点比较 DiffDec, Diffleop, AMG, MolJO, DecompDPO, DecompDiff, PoseBusters, PLIP, AutoDock Vina 等. 判断是否撞题; 若高度重合, 基于证据调整到仍有创新性和可做性的细切口, 不能硬做旧工作. 完成第一轮文献矩阵和撞题判断前, 不启动大规模模型实现或长期实验; 只做结构, 环境检查, 文献检索, 方法设计和最小 smoke pipeline 设计.

工具使用: 必须主动使用与本项目相关的 plugin, skill, MCP, subagent, workflow, 而不是只靠普通 shell. 当前已知能力见 docs/STATUS.md 的“可用工具与插件”小节; 启动后先校验, 若环境变化则更新. 文献检索优先用 research-lookup, literature-review, deep-research, paper-lookup, citation-management 或 WebSearch 类 MCP; 分子与科学计算优先考虑 rdkit, datamol, deepchem, molfeat, diffdock, torch-geometric, pytorch-lightning; 代码审查与验证优先用 code-review, verify, run, security-review; 长期轮询用 loop. 盘点能力时以实际可见 skills, MCP, subagent, workflow 和 slash command 为准, 不假设命令一定存在. 插件或 skill 不可用时, 记录原因并降级到本地脚本, 官方 API, curl, git, Python 或手动检索. 安装新插件前说明用途, 来源, 权限风险和替代方案; 不上传密钥, token, 私有路径或未公开数据到不可信服务.

学术底线: 禁止伪造数据, 结果, 引用; 禁止只报最好 seed, 隐藏负结果, 为好看临时改指标定义, 或只用 Vina 证明成功. 所有结论必须追溯到代码, 配置, 数据版本, 日志, 原始指标, 文献来源或实验记录. 失败, 阻塞和负结果也要记录.

项目结构: 保持 configs, data/raw, data/processed, data/splits, src/pfr/{data,chemistry,feedback,models,baselines,evaluation,workflows,utils}, scripts/{setup,data,train,eval,analysis}, experiments/{smoke,main,ablations,baselines}, outputs/{metrics,tables,figures,molecules,logs}, docs, tests, third_party. 用 conda 新建环境并固定 environment.yml. 下载数据或跑 GPU 前先做小样本 smoke; 使用 GPU 时记录设备, 显存, 运行时间和随机种子.

必须维护: docs/STATUS.md 记录当前阶段快照, 最好结果, 最近实验, 计划, 阻塞, 关键路径, 工具与插件, 常用命令, 压缩上下文后优先阅读. docs/EXPERIMENT_LOG.md 追加记录阶段目的, commit, 环境, 数据版本, 命令, 配置, 结果路径, 插件/skill 使用, 结论, 失败原因和下一步. 重要阶段必须更新.

分工: 善用 subagents/workflows; 不支持时按角色模拟. Literature 负责文献和撞题; Repository 负责开源仓库检索, 阅读和复现; Engineering 负责环境, 结构, 测试和 debug; Data 负责数据, R-group 切分和失败候选; Feedback 负责 RDKit/Vina/PLIP/PoseBusters/clash/interaction feedback; Model 负责 no-feedback repair 和 feedback-conditioned repair; Baseline 负责 Best-of-N, rerank-only, direct regeneration, 规则修复和开源 baseline; Evaluation 负责多 seed, 交叉验证和统计; Writing 负责图表和论文.

最小可行任务: single R-group failed-candidate repair. 从公开 protein-ligand complex 数据构造 fixed scaffold, editable R-group, anchor, pocket; 用人工扰动和已有生成器构造失败候选, 包括 clash, interaction loss, anchor invalid, linker too flexible, drug-likeness drop, score hacking. 反馈形式不限, 可用全局数值, 几何场, interaction fingerprint, 历史失败记忆或隐向量; 重点是能被模型吸收并改变下一轮修复分布.

必须实现: 数据校验, 失败候选生成, 反馈提取, baseline, feedback-conditioned repair/refinement, 统一评估, 结果汇总. 指标包括 same-budget success rate, scaffold preservation, editable validity, anchor validity, protein-ligand clash, PoseBusters pass, PLIP interaction recovery/similarity, Vina/Delta Vina, ligand efficiency, QED, SA, logP, rotatable bonds. 至少 3 seeds; 条件允许做 scaffold/protein/pocket split 交叉验证. 消融: no-feedback, global-score-only, geometry-only, interaction-only, rerank-only, Best-of-N, full feedback.

结束标准: 完整代码和测试; environment.yml 可重建; 主要脚本一键可跑; outputs 下有原始 metrics, 表格, 图, 成功/失败案例和分子; docs 下有文献矩阵, 方法设计, STATUS, EXPERIMENT_LOG; 完成 BIBM 风格论文初稿, 含摘要, 引言, 相关工作, 方法, 实验, 结果, 消融, 案例, 局限, 伦理/可复现说明. 最终报告明确哪些结论成立, 不成立, 或只是初步证据. 允许阶段性成果后自动创建本地 git commit, 但不得自动 push; commit 前检查 git status 和 diff, 不提交密钥, token, 私有数据或大文件.
