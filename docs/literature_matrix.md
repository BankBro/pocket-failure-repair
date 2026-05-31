# Literature Matrix

> 本文档用于维护文献检索, 撞题分析和 related work 证据. 所有条目必须能追溯到论文, 代码仓库或官方文档. 禁止伪造引用.

## 检索目标

重点确认 failed-candidate-conditioned local molecular repair 是否已有高度重合工作, 并比较 pocket-aware 3D molecular generation, R-group generation, local editing, feedback/guidance, pose/interaction validation 相关方法.

## 第一轮检索结论摘要

日期: 2026-05-31.

1. 未发现同时满足 `failed candidate 作为输入`, `explicit failure feedback`, `pocket-aware 3D local repair`, `same-budget repair vs Best-of-N/rerank-only` 的直接撞题工作.
2. 直接撞题风险暂定为 Low, 但相邻工作风险为 Medium, 尤其是 pocket-aware scaffold decoration, lead optimization, fragment-based generation 和 diffusion-based structure-based drug design.
3. DiffDec, DiffLEOP, DecompDiff, DecompOpt, DecompDPO 与本项目在 pocket-aware / structure-based generation 或 optimization 上相邻, 但第一轮未见其显式把 failed candidate 及其失败诊断作为下一轮修复条件.
4. PoseBusters, PLIP, AutoDock Vina 更适合作为本项目的 feedback / evaluation / scoring 组件, 不是 local molecular repair 方法.
5. AMG 与 MolJO 名称在公开检索中存在歧义或证据不足, 第一轮只保留可核验线索, 不把未确认信息写成事实.
6. 最稳妥的新颖性表述是: 在相同预算下, 利用 failed local candidate 及 clash, interaction loss, anchor invalid 等可解释失败诊断, 进行 pocket-aware 3D local repair, 并对比 direct regeneration, Best-of-N 和 rerank-only.

## 撞题风险总表

| 风险 | 方法 / 方向 | 判断 |
|---|---|---|
| High | 暂无 | 第一轮未找到完全覆盖 failed-candidate-conditioned pocket-aware local repair 的工作. |
| Medium | DiffDec, DiffLEOP, DecompDiff, DecompOpt, DecompDPO, Delete, DeepFrag, D3FG, STRIFE, SLOGEN, BoKDiff | 覆盖 pocket-aware generation, scaffold decoration, lead optimization, preference optimization 或 Best-of-N 相关思想, 但未见完整 failure-feedback repair setting. |
| Low | PoseBusters, PLIP, AutoDock Vina | 主要是验证, interaction profiling 或 docking/scoring 工具, 与本项目互补. |
| 待验证 | AMG, MolJO | 名称或方法归属仍需二轮检索核验. |

## 文献矩阵

| 方法 / 工具 | 年份 | 任务 | 输入条件 | 输出 | 是否 pocket-aware | 是否 local editing | 是否使用 failed candidate | feedback / guidance 类型 | 评价指标 | 代码 / 数据 | 与本项目关系 | 撞题风险 | 备注 |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|
| DiffDec: Structure-Aware Scaffold Decoration with an End-to-End Diffusion Model | 2024 | Structure-aware scaffold decoration / R-group generation | Scaffold, 3D context / pocket-related structure constraints | Decorated molecule / substituents | Yes, structure-aware and pocket-adjacent | Yes, scaffold decoration / local decoration | No evidence in first-round sources | Diffusion generation with structure constraints, not failed-candidate feedback | Molecular validity, docking / structure-aware generation metrics, details待复查原文 | DOI: https://doi.org/10.1021/acs.jcim.3c01466; preprint DOI: https://doi.org/10.1101/2023.10.08.561377 | 强相邻 baseline / related work. 本项目需强调 failed candidate + failure feedback + repair evaluation. | Medium | OpenAlex 确认标题, 年份, 作者和 DOI. 需要二轮读原文补全指标和代码. |
| DiffLEOP / Diffleop: A 3D pocket-aware lead optimization model with knowledge guidance | 2025 | 3D pocket-aware lead optimization | Lead compound, protein pocket, knowledge guidance | Optimized molecule | Yes | Partially, lead optimization | No evidence in first-round sources | Knowledge guidance / affinity or pocket-aware guidance, not explicit failure feedback | Lead optimization metrics待复查原文 | DOI: https://doi.org/10.1093/bib/bbaf345; arXiv线索: https://doi.org/10.48550/arxiv.2504.21065 | 强相邻. 可能是本项目必须讨论的 pocket-aware lead optimization baseline. | Medium | OpenAlex 同时返回正式论文和 arXiv 线索. 方法名 DiffLEOP 需二轮确认大小写和官方仓库. |
| AMG | 2024 | 待核验. 检索线索指向 fragment-based 3D molecular generation for protein pockets | Protein pocket, fragment state, RL interaction agent线索 | Generated 3D molecule / fragment-growing result | Likely yes, but待核验 | Likely fragment-based local generation, but待核验 | No evidence | RL / interaction-agent guidance线索 | 待复查原文 | 可能相关 DOI: https://doi.org/10.1093/bib/bbae531 | 可能是 fragment-based pocket generation 相邻工作, 但名称歧义较大. | 待验证 / Medium if confirmed | OpenAlex 对 `AMG molecular generation protein pocket` 返回 `Deep reinforcement learning as an interaction agent to steer fragment-based 3D molecular generation for protein pockets`. 不能确认 AMG 是否为该方法正式名. |
| MolJO | 2024 | 待核验. 检索线索指向 structure-based molecule optimization with gradient-guided Bayesian flow networks | Protein structure / molecule optimization context线索 | Optimized molecule | Likely yes, but待核验 | Optimization, not necessarily local repair | No evidence | Gradient-guided Bayesian flow / optimization guidance线索 | 待复查原文 | 线索 DOI: https://doi.org/10.48550/arxiv.2411.13280 | 可能是 structure-based optimization 相邻工作. | 待验证 / Medium if confirmed | OpenAlex 对 `MolJO` 返回该论文, 但需二轮确认 MolJO 是否为方法名. |
| DecompDPO: Decomposed Direct Preference Optimization for Structure-Based Drug Design | 2024 | Structure-based drug design preference optimization | Protein-ligand / SBDD samples and preference decomposition线索 | Fine-tuned / optimized generative model outputs | Yes, structure-based | Not specifically local repair in first-round evidence | No evidence | Direct Preference Optimization / decomposed preference, not failed-candidate feedback | Preference / SBDD metrics待复查原文 | arXiv DOI: https://doi.org/10.48550/arxiv.2407.13981 | 相关于用偏好或 reward 改善 SBDD, 可作为 feedback/guidance related work, 但不是 failed candidate repair. | Medium | 需要读原文确认是否可作为 preference baseline. |
| DecompDiff: Diffusion Models with Decomposed Priors for Structure-Based Drug Design | 2024 | Structure-based molecular generation with decomposed priors | Protein pocket / structure context, decomposed priors | Generated molecules | Yes | No evidence of local repair | No evidence | Decomposed prior in diffusion, not explicit failure feedback | SBDD generation metrics待复查原文 | arXiv DOI: https://doi.org/10.48550/arxiv.2403.07902 | 强相关 SBDD diffusion baseline / related work. 本项目应避免只做另一个 pocket generator. | Medium | OpenAlex 确认标题, 年份, 作者和 DOI. |
| DecompOpt: Controllable and Decomposed Diffusion Models for Structure-based Molecular Optimization | 2024 | Structure-based molecular optimization | Protein structure / initial molecule / optimization controls线索 | Optimized molecule | Yes | Optimization, not confirmed local repair | No evidence | Controllable decomposed diffusion / optimization guidance | Optimization metrics待复查原文 | arXiv DOI: https://doi.org/10.48550/arxiv.2403.13829 | 相关于 structure-based optimization, 但第一轮未见 failed candidate diagnostic repair. | Medium | 需要二轮确认输入是否含 initial molecule 和具体控制信号. |
| PoseBusters | 2024 | Pose / molecule validation and plausibility checking | Predicted/generated molecule pose, optional protein and reference ligand | Validation report / per-check pass-fail table | Yes for protein-conditioned checks | No | No, but failed pose can be evaluated as input | Rule-based validation: sanitization, bond lengths, steric clashes, protein-ligand distance/overlap, RMSD等 | Pass/fail checks, pose plausibility, RMSD and geometry checks | Paper: https://doi.org/10.1039/d3sc04185a; arXiv: https://arxiv.org/abs/2308.05777; docs: https://posebusters.readthedocs.io/en/latest/; code: https://github.com/maabuu/posebusters | 可作为 failure taxonomy, geometry feedback 和 evaluation component. | Low | 若项目只做 pose validity benchmark, 与 PoseBusters 接近; 作为组件风险低. |
| PLIP: Protein-Ligand Interaction Profiler | 2015 | Automated protein-ligand interaction profiling | Protein-ligand complex / PDB file | Interaction profile, tables, XML/text, visualization | Yes | No | No, but failed complex can be profiled | Rule-based interaction detection: H-bond, hydrophobic, salt bridge, pi-stacking, pi-cation, halogen, metal等 | Interaction types, residues, atoms, distances, angles | Paper: https://doi.org/10.1093/nar/gkv315; web: https://plip-tool.biotec.tu-dresden.de/plip-web/plip/index; code/docs: https://github.com/pharmai/plip | 可作为 interaction feedback, interaction recovery 和相互作用指纹来源. | Low | 本项目不能只声称 PLIP 打分即为创新, 应把它作为反馈来源之一. |
| AutoDock Vina | 2010 | Docking, pose search and scoring | Receptor PDBQT, ligand PDBQT, search box / maps | Ranked poses and affinity scores | Yes, via receptor and pocket search box | No molecular graph editing; supports pose local optimization | No | Docking score, local search / BFGS pose optimization | Affinity kcal/mol, ranked poses, RMSD bounds, docking success | Paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC3041641/; docs: https://autodock-vina.readthedocs.io/en/latest/; code: https://github.com/ccsb-scripps/AutoDock-Vina | 可作为 docking score, redocking evaluator, Vina / Delta Vina feedback. | Low for tool, Medium if used as only novelty | Vina-guided optimization 很常规, 不能作为唯一创新点. |

## 与本项目核心设定的差异

| 核心轴 | 第一轮观察 | 对本项目的要求 |
|---|---|---|
| failed candidate 作为输入 | 未找到直接覆盖. 相邻方法多用 scaffold, ligand, fragment, pocket 或 preference, 不以失败候选作为下一轮条件. | 输入必须显式包含 failed candidate, 并在 ablation 中比较 no-failed-candidate 或 no-feedback 版本. |
| explicit failure feedback | 相邻工作常用 docking score, preference, knowledge guidance 或 diffusion prior, 但未见基于具体失败原因的 repair feedback loop. | 反馈应包含 clash, interaction loss, anchor violation, PoseBusters/PLIP/Vina 等可解释诊断, 并证明它改变修复分布. |
| pocket-aware 3D local repair | DiffDec / DiffLEOP / DecompOpt 等覆盖 pocket-aware generation/optimization, 但 repair setting 未确认. | 任务表述应坚持 local repair, 不是从零生成, 不是泛化 lead optimization. |
| same-budget evaluation | 未找到直接同题评估. BoKDiff/Best-of-N 方向可作为相邻 baseline. | 主实验必须同预算比较 direct regeneration, Best-of-N, rerank-only 和 repair. |

## 撞题分析问题清单

1. 是否已有方法把 failed candidate 本身作为下一轮生成条件? 第一轮未找到直接证据.
2. 是否已有方法针对 pocket-aware 3D local molecular repair, 而不是 generation 或 optimization? 第一轮发现强相邻 pocket-aware local generation / optimization, 但 repair setting 未确认.
3. 是否已有方法显式利用 clash / interaction loss / anchor invalid 等失败反馈? 第一轮未找到生成式 repair 闭环, PoseBusters / PLIP 可提供诊断信号.
4. 是否已有方法在 same-budget repair setting 下对比 Best-of-N 与 rerank-only? 第一轮未找到.
5. 是否已有 benchmark 专门评估 failed local candidate repair? 第一轮未找到.

## 初步定位

当前项目继续保留差异化切口: failed-candidate-conditioned local molecular repair.

建议论文定位改写为更窄且可防撞的版本:

> We study failure-feedback-conditioned local repair for pocket-aware 3D molecular editing, where a failed local candidate and diagnostic feedback are used as conditions to generate a repaired candidate under the same generation budget.

## 若二轮发现高度重合时的收窄切口

1. 转为 failed local candidate repair benchmark, 强调失败类型, 同预算协议和可复现评估.
2. 收窄到单一失败类型, 如 clash repair, anchor invalid repair 或 PLIP interaction recovery.
3. 收窄到 feedback representation, 比较 global score, geometry feedback, interaction feedback 和 full feedback.
4. 收窄到 plug-in repair module, 接在 DiffDec / DiffLEOP / DecompDiff 等生成器之后.

## 检索记录

| 日期 | 查询 | 工具 | 结果摘要 | 输出 / 证据 |
|---|---|---|---|---|
| 2026-05-31 | DiffDec molecular generation protein pocket diffusion | CCS WebSearch | 搜索服务返回反爬/非结果 HTML, 降级到 OpenAlex 和子 Agent 检索. | 工具错误已记录在会话. |
| 2026-05-31 | DiffLEOP protein ligand molecule diffusion pocket | CCS WebSearch | 搜索服务返回反爬/非结果 HTML, 降级到 OpenAlex 和子 Agent 检索. | 工具错误已记录在会话. |
| 2026-05-31 | DecompDiff protein pocket molecular generation GitHub arXiv | CCS WebSearch | 搜索服务返回反爬/非结果 HTML, 降级到 OpenAlex 和子 Agent 检索. | 工具错误已记录在会话. |
| 2026-05-31 | DiffDec structure aware scaffold decoration | OpenAlex API | 找到 DiffDec JCIM 2024 和 bioRxiv 2023 来源. | https://doi.org/10.1021/acs.jcim.3c01466; https://doi.org/10.1101/2023.10.08.561377 |
| 2026-05-31 | DiffLEOP / A 3D pocket-aware and affinity-guided diffusion model for lead optimization | OpenAlex API | 找到 BIB 2025 正式论文和 arXiv 2025 线索. | https://doi.org/10.1093/bib/bbaf345; https://doi.org/10.48550/arxiv.2504.21065 |
| 2026-05-31 | DecompDPO molecule molecular generation | OpenAlex API | 找到 Decomposed Direct Preference Optimization for Structure-Based Drug Design. | https://doi.org/10.48550/arxiv.2407.13981 |
| 2026-05-31 | DecompDiff protein pocket molecule generation | OpenAlex API | 找到 DecompDiff: Diffusion Models with Decomposed Priors for Structure-Based Drug Design. | https://doi.org/10.48550/arxiv.2403.07902 |
| 2026-05-31 | DecompOpt molecule optimization | OpenAlex API | 找到 DecompOpt: Controllable and Decomposed Diffusion Models for Structure-based Molecular Optimization. | https://doi.org/10.48550/arxiv.2403.13829 |
| 2026-05-31 | AMG molecular generation protein pocket | OpenAlex API | 名称歧义. 最相关线索是 fragment-based 3D molecular generation for protein pockets, 但 AMG 是否为正式方法名待核验. | https://doi.org/10.1093/bib/bbae531 |
| 2026-05-31 | MolJO | OpenAlex API | 名称歧义. 最相关线索是 structure-based molecule optimization with gradient-guided Bayesian flow networks, 但 MolJO 是否为正式方法名待核验. | https://doi.org/10.48550/arxiv.2411.13280 |
| 2026-05-31 | PoseBusters, PLIP, AutoDock Vina | general-purpose research agent | 找到原始论文, 官方文档和代码来源, 判断均为工具组件而非 repair 方法. | PoseBusters: https://doi.org/10.1039/d3sc04185a; PLIP: https://doi.org/10.1093/nar/gkv315; Vina: https://pmc.ncbi.nlm.nih.gov/articles/PMC3041641/ |
| 2026-05-31 | failed candidate molecular repair, failure feedback molecule generation, pocket-aware local molecular editing, same-budget Best-of-N molecular generation | general-purpose research agent + OpenAlex 线索 | 未找到直接撞题. 找到 Delete, DeepFrag, D3FG, STRIFE, ACFIS, SLOGEN, CACM, BoKDiff 等相邻方向. | Delete: https://arxiv.org/abs/2308.02172; DeepFrag: https://doi.org/10.1039/d1sc00163a; D3FG: https://arxiv.org/abs/2306.13769; STRIFE: https://doi.org/10.1021/acs.jcim.1c01311; CACM: https://arxiv.org/abs/2604.09308; BoKDiff: https://arxiv.org/abs/2501.15631 |

## 下一轮需要补查

- 逐篇读 DiffDec, DiffLEOP, DecompDPO, DecompDiff, DecompOpt 的方法和实验部分, 补全数据集, 指标, 官方仓库和 baseline.
- 核验 AMG 与 MolJO 是否为用户所指方法名, 是否存在官方仓库或论文缩写.
- 增补 Delete, DeepFrag, D3FG, STRIFE, ACFIS, SLOGEN, BoKDiff 到扩展 related work 表, 用于论文 related work.
- 若后续发现直接撞题, 立即更新 `docs/method_design.md` 的任务切口.
