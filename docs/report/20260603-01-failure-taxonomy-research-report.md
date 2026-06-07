# 失败样本错误类型与可修复性调研报告

关联计划: `docs/plan/20260603-01-failure-taxonomy-research-plan.md`

本报告围绕 pocket-conditioned molecule generation, structure-based drug design, docking/refinement, ligand pose correction, constrained molecular editing, fragment growing/linker design 等方向, 调研相关工作如何定义、判定和统计 failed sample / failed molecule / bad pose / invalid output, 并为 `Failure-Feedback-Conditioned Repair for Pocket-Aware 3D Local Molecular Editing` 的 failure taxonomy 和可修复性边界提供依据。

调研仅使用论文、benchmark、官方工具文档和代码仓库等公开来源。未运行本项目代码, 未统计本地 outputs, 未复现实验。报告中的比例仅来自引用论文或官方 benchmark, 不代表本项目样本的真实失败占比。

## 调研范围与方法

本次调研从五类来源展开: 结构条件分子生成与 pocket-conditioned generation, docking / redocking / pose prediction / pose plausibility benchmark, protein-ligand interaction 与 clash/contact 分析工具, scaffold/anchor/linker constrained generation 与 molecular editing, 以及 pose refinement / conformation refinement / constrained optimization 等接近 repair 的任务。检索时优先使用原始论文、官方文档、GitHub 仓库、PubMed/PMC/arXiv/OpenReview/RSC/ACM/PMLR 等可核验来源, 并通过相关 benchmark、工具论文和 related work 扩展。

需要特别说明的是, 文献中很少直接使用“failed ligand repair”或“failure taxonomy”这样的术语。多数工作把失败样本拆散到 validity, connectivity, RMSD success, docking score, PoseBusters pass/fail, interaction fingerprint, scaffold/anchor preservation, QED/SA/Lipinski filters 等指标或过滤规则中。因此, 本报告将严格区分三类内容: 文献明确提出的失败类别或检查项, 常用工具/benchmark 可操作化判定的指标, 以及我们为了 fixed-scaffold local repair 需要归纳出的 operational category。

## A. 调研结论摘要

未发现一个被广泛接受、专门面向 failed ligand repair 或 pocket-aware local molecular editing 的统一系统 failure taxonomy。最接近系统分类的是 PoseBusters, 它把生成或 docking 的 ligand pose 拆解为 chemical validity, intramolecular geometry, steric clash, energy, protein/cofactor/water overlap, reference RMSD 等一组 pass/fail checks, 但 PoseBusters 的目标是 pose plausibility benchmark, 不是 failure-conditioned repair taxonomy。DecompDiff 对 incomplete molecule / arm-scaffold disconnected / protein-ligand clash 等失败有更接近生成过程的分类和 guidance, 但范围局限于 decomposed scaffold/arms 的 SBDD 任务。3DLinker, DiffLinker, SyntaLinker, ShapeLinker 等 linker/fragment 生成工作会统计 validity, connectedness, fragment recovery, 2D filters, RMSD, pocket clash 或 constrained embedding failure, 但通常仍是评价或过滤, 不是多标签 repair taxonomy。

现有工作主要通过四种方式定义失败样本。第一类是化学图或输入解析失败, 例如 RDKit parsing/sanitization failure, invalid valence, disconnected fragments, missing input fragments。第二类是 3D pose 或几何失败, 例如 RMSD 未达到 2 Å redocking success, bond length/angle/planarity 异常, internal steric clash, high internal energy, protein-ligand overlap。第三类是约束失败, 例如 scaffold/substructure/anchor/linker 未保留, linker 未成功连接片段, similarity 或 property constraint 不满足。第四类是筛选或 pipeline 阶段失败, 例如 docking run failure, score/reranking 未入选, QED/SA/Lipinski/property filter 未通过。需要注意, docking score 本身通常是排序或优化指标, 不是天然的 failure label; 只有当论文或 benchmark 给出明确阈值或 success definition 时, 才能转化为 pass/fail。

没有发现文献普遍明确支持“一个样本可以有多个 failure labels”的系统 taxonomy。相反, 多数论文报告的是 aggregate metrics 或 stage-wise pass/fail, 例如 validity rate, RMSD < 2 Å success, PoseBusters pass rate, 2D filter pass, recovery rate。PoseBusters 和 PLIP/ProLIF/ODDT/Arpeggio 等工具天然会为同一个样本输出多个检查项或多个 interaction bits, 因而支持我们构建 multi-label operational taxonomy, 但这应被表述为“我们基于多工具检查设计的多标签体系”, 而不是已有文献共识。

系统统计 failure prevalence 或 stage-wise attrition 的工作有限。PoseBusters 是少数明确展示 RMSD-only success 到 RMSD+physical-validity success 之间流失的 benchmark, 例如 Astex 上 DiffDock, TankBind, Uni-Mol 等方法在 RMSD≤2 Å 后仍有大量 pose 不能通过 PoseBusters checks。GNINA, EquiBind, TANKBind, DiffDock 等 docking/pose work 主要统计 RMSD 阈值下的 top-1/top-N success。liGAN, GraphBP, DiffSBDD, DiffLinker, 3DLinker, SyntaLinker, ShapeLinker 等生成工作会统计 validity, connectivity, 2D filters, recovery 或 embedding failure, 但很少把失败样本进一步拆成可修复错误标签并报告多标签占比。

与本项目 fixed-scaffold local repair 最相关的错误类型包括: scaffold/anchor 基本保留但局部 linker/side-chain 几何或连接有问题; 局部 substituent 与 pocket 发生 steric clash / volume overlap; ligand 内部 bond/angle/planarity/energy 异常但分子图仍可解析; 关键 protein-ligand interaction 或 contact fingerprint 缺失; pose 在 pocket 内但局部 orientation / torsion / conformation 不合理。更可能超出第一阶段范围的是: RDKit 无法解析或严重价态错误, scaffold/anchor 已丢失, 分子整体断裂或缺失核心片段, 需要全局重新 docking 或 scaffold redesign 的远离 pocket pose, 以及 docking/evaluation 程序运行失败。

## B. 文献/工作证据表

| 来源 | 年份 | 任务场景 | 样本来源/流程 | 关注的失败或指标 | 是否统计占比 | 分母是什么 | 是否讨论修复 | 与本项目相关性 | 证据备注 |
|---|---:|---|---|---|---|---|---|---|---|
| [AutoDock Vina](https://pmc.ncbi.nlm.nih.gov/articles/PMC3041641/) | 2010 | Redocking / bound pose prediction | 190 protein-ligand complexes, 另有 116 non-PDBbind 检查 | Predicted pose 相对实验 pose 的 RMSD; RMSD < 2 Å 常作为 success | 是 | 190 或 116 complexes | 否, 是 docking/search/score | 支持 pose_accuracy_failure 的 2 Å redocking 依据 | 不报告 clash/geometry taxonomy; score 不等于 failure label |
| [GNINA 1.0](https://doi.org/10.1186/s13321-021-00522-2) | 2021 | Redocking, cross-docking, CNN rescoring/refinement | PDBbind refined set, 过滤后 redocking 4260 pairs, cross-docking 7970 pairs | RMSD < 2 Å good pose, TopN success, CNNscore/CNNaffinity | 是 | Poses / protein-ligand pairs | 部分, 通过 rescoring/refinement 改善 pose ranking | 支持 bad pose 判定和 docking reranking 阶段失败 | 不把 clash/geometry 作为独立 failure taxonomy |
| [EquiBind](https://proceedings.mlr.press/v162/stark22b.html) | 2022 | Geometric DL blind docking | PDBBind v2020 time split, test 363 complexes | L-RMSD, centroid distance, 2 Å/5 Å success; non-intersection loss 防 clash | 是 | 363 test complexes | 部分, point-cloud fitting correction 与 QVina/SMINA fine-tuning | 说明 pose correction 多以 RMSD 改善评价 | 未报告 PB-valid 或 geometry pass/fail 分母 |
| [TANKBind](https://www.proceedings.com/content/068/068431-0525open.pdf) | 2022 | Blind self-docking, distance-map-to-coordinate pose generation | PDBbind v2020 time split, test 363, unseen receptor 142 | Ligand RMSD, centroid distance, 2 Å/5 Å success; local atomic structure loss | 是 | 363 / 142 cases | 部分, 坐标生成与优化 | 支持 pose-level failure 与几何约束分离 | 无独立 clash/PoseBusters 检查 |
| [DiffDock](https://openreview.net/forum?id=kKF8_K-mBbS) | 2023 | Diffusion docking, confidence ranking | PDBBind time split, test 363, holo/apo 设置 | RMSD < 2 Å top-1/top-5 success, confidence ranking | 是 | 363 cases 或 top-N poses | 不是后处理 repair, 是生成/denoising docking | 支持 best-of-N / reranking 对失败含义的影响 | 原论文不审计 PB-valid, clash 或 bond geometry |
| [PoseBusters](https://pubs.rsc.org/en/content/articlehtml/2024/sc/d3sc04185a) | 2024 | Pose plausibility benchmark | Astex Diverse n=85, PoseBusters Benchmark n=308 | RMSD≤2 Å + PB-valid; chemical consistency, bond/angle, internal clash, energy, protein overlap | 是 | 每个 benchmark case / generated pose | 部分, ligand-only minimisation 后处理 | 最强证据: 物理有效性检查可显著改变 success rate | 是 benchmark/check suite, 不是 repair taxonomy |
| [CASF-2016](https://doi.org/10.1021/acs.jcim.8b00545) | 2019 | Scoring function benchmark | 285 protein-ligand complexes | scoring/ranking/docking/screening power | 部分 | 285 complexes | 否 | 支持 score 与 docking/screening 任务应区分 | 摘要不支持 PB-valid 或 clash prevalence |
| [DUD-E](http://dude.docking.org/) | 2012 | Virtual screening / decoy benchmark | 102 targets, 22886 actives, 50 decoys per active | Enrichment/decoy screening, not pose RMSD | 否, 对 pose failure | targets/actives/decoys | 否 | 避免把 screening failure 错写为 bad pose | 非 pose plausibility benchmark |
| [liGAN](https://arxiv.org/abs/2010.14442) | 2020/2022 | Receptor-conditioned 3D molecular generation | Binding-site conditioned density/generation, 后续 UFF/Vina/GNINA 优化 | Validity, uniqueness, RMSD of optimization, predicted affinity; disconnected/steric/geometric problematic structures | 是, aggregate | Generated molecules | 部分, energy minimization 作为评估前处理 | 支持 invalid / geometry-problem 但不是 taxonomy | validity 定义明确, 分类不系统 |
| [DeepLigBuilder / 3D deep generative SBDD](https://pubs.rsc.org/doi/d1sc04444c) | 2021 | Structure-based de novo design | 3D generative model + MCTS | RDKit invalid, non-closed aromatic rings, wrong bond lengths/torsions, QED/SA/smina | 是 | Generated outputs / runs | 部分, local relaxation / MMFF94s | 支持 local geometry defects 可由 relaxation 改善 | 不是 repair task, 是生成质量分析 |
| [3D Generative SBDD](https://arxiv.org/abs/2203.10446) / [repo](https://github.com/luost26/3D-Generative-SBDD) | 2022 | Pocket-conditioned autoregressive generation | 生成后 UFF refine, Vina/QED/SA/diversity | Vina score, QED, SA, high-affinity %, diversity | 是, aggregate | Generated samples | 仅评估前 UFF refine | 说明很多 SBDD 工作只报 aggregate metrics | 不报告 invalid rate 或 failure taxonomy |
| [GraphBP](https://arxiv.org/abs/2204.09410) / [repo](https://github.com/divelab/GraphBP) | 2022 | Graph-based target-conditioned 3D molecule generation | 生成后 UFF/Vina minimization 与 CNN scoring | RDKit validity, binding improvement, bond-length distribution MMD | 是 | Generated molecules | 否, 是 minimization/scoring pipeline | 支持 chemical validity 作为指标 | taxonomy 窄, 基本等于 RDKit validity |
| [Pocket2Mol](https://arxiv.org/abs/2205.07249) / [repo](https://github.com/pengxingang/Pocket2Mol) | 2022 | Pocket-conditioned efficient sampling | Joint atom-bond prediction, RDKit conformer comparison | Bad substructures, distorted benzene rings, excessive three-member rings, angle/dihedral distribution | 是, 部分 | Generated molecules / substructures | 否, 通过 joint atom-bond prediction 预防 | 支持局部几何/坏子结构作为 operational category | 不是完整 taxonomy |
| [TargetDiff](https://arxiv.org/abs/2303.03543) / [repo](https://github.com/guanjq/targetdiff) | 2023 | Target-aware molecule generation | Diffusion generation, Vina Min/Dock evaluation | Vina Dock, high affinity, QED, SA, diversity; Vina parser issue 线索 | 是, aggregate | Valid/generated molecules | 否 | 说明主流 SBDD 多关注最终指标 | 不系统统计 invalid/geometry/clash |
| [DiffSBDD](https://arxiv.org/abs/2210.13695) / [repo](https://github.com/arneschneuing/DiffSBDD) | 2022/2024 | Equivariant diffusion SBDD, inpainting, fragment linking | De novo, inpainting, linking/diversify | Validity, connectivity, docking/property distribution, minor clashes after minimization | 是 | Generated molecules | 部分, local minimization 解决 minor clashes | 支持 connectivity 与 minor clash 作为标签候选 | 仍以评价为主, 非 repair taxonomy |
| [DecompDiff](https://arxiv.org/abs/2403.07902) / [repo](https://github.com/bytedance/DecompDiff) | 2024 | Fragment/scaffold-aware diffusion SBDD | Scaffold/arms decomposed priors, validity guidance | Incomplete molecule, arms-scaffold disconnected, protein-ligand clash, success rate | 是 | Generated cases | 是, sampling-time validity/clash guidance | 与本项目最接近的生成时 failure guidance 证据 | 范围是 decomposed SBDD, 不等同 failed ligand repair |
| [DrugGPS](https://arxiv.org/abs/2305.13997) / [FLAG](https://github.com/zaixizhang/FLAG) | 2023 | Subpocket prototype / motif-based SBDD | Motif attachment enumeration and pruning | Chemically invalid attachment, RDKit sanitization failure, Vina/QED/SA/diversity | 是, aggregate | Generated/pruned candidates | 否, 主要 pruning | 支持 invalid attachment 作为约束失败 | 100% validity 来自过滤, 不代表无失败样本 |
| [DeLinker](https://doi.org/10.1021/acs.jcim.9b01120) | 2020 | 3D fragment linking | 给定两个片段和 3D 约束生成 linker | 3D similarity, fragment incorporation, validity/recovery 类指标 | 部分 | Generated linkers | 否 | 支持 linker/fragment 约束成功定义 | 未见自动修复 constraint violation |
| [SyntaLinker](https://pubs.rsc.org/en/content/articlehtml/2020/sc/d0sc03126g) | 2020 | Conditional transformer fragment linking | 给定片段、linker 长度、药效团限制 | Validity, uniqueness, recovery, novelty, SLBD/pharmacophore match | 是 | ChEMBL/CASF/SLBD generated linkers | 否 | 支持 linker constraint mismatch 作为标签 | 不修复 invalid/mismatch, 而是统计和过滤 |
| [DiffLinker](https://arxiv.org/abs/2210.05274) | 2022/2024 | E(3)-equivariant 3D linker design, pocket-conditioned linker | 多片段连接, pocket-conditioned linker generation | Validity, anchors, 2D filters, recovery, RMSD, SCRDKit, pocket clashes | 是 | Generated linkers / fragment tasks | 否, 主要生成后筛选 | 与 fixed-anchor/local edit 很相关 | Invalid 或 fragment-missing 样本通常排除后再算后续指标 |
| [3DLinker](https://proceedings.mlr.press/v162/huang22d.html) | 2022 | E(3)-equivariant VAE linker design | 两片段, anchor unknown/given | Valid %, recovered %, 2D filters, RMSD, uniqueness, novelty | 是 | Generated molecules | 否 | 支持 connectedness + fragment recovery + anchor 评价 | Invalid molecules discarded for following evaluations |
| [ShapeLinker](https://arxiv.org/abs/2306.08166) | 2023 | PROTAC/linker 3D shape-conditioned optimization | Anchor-warhead fixed, constrained embedding | Validity, uniqueness, novelty, Failed %, constrained embedding failure | 是 | Generated/embedded linkers | 否, 主要 RL scoring + embedding/selection | 支持“嵌入失败/空间连接失败”作为 pipeline-stage failure | 不自动修复失败 embedding |
| [DeepFrag](https://pubs.rsc.org/en/content/articlelanding/2021/sc/d1sc00163a) | 2021 | Structure-based fragment growing | 从 >6500 候选 fragment 中 rank/select | Correct fragment recovery, chemical similarity | 是 | Benchmark deletion cases | 否 | 支持 fragment-growing 中 failure 是未恢复正确片段 | 从有效 fragment 库选择, 非 invalid repair |
| [GCPN](https://arxiv.org/abs/1806.02473) | 2018 | Goal-directed graph generation / constrained optimization | Valency-constrained action space, similarity-constrained optimization | Validity, success, property improvement, similarity constraint | 是 | Optimization tasks / generated molecules | 否, 预防非法动作 | 支持 valency/action 约束与 property failure 区分 | 不接收 invalid molecule 做 post hoc repair |
| [JT-VAE](https://arxiv.org/abs/1802.04364) | 2018 | Junction-tree molecular generation, constrained optimization | Latent optimization, decode and select satisfying candidates | Success rate, property improvement, similarity | 是 | Test molecules / decoded candidates | 否 | 支持 similarity/scaffold-like constraints 的 success/failure | 不满足约束的候选不修复 |
| [MolDQN](https://pmc.ncbi.nlm.nih.gov/articles/PMC6656766/) | 2019 | RL molecular editing / valid-action constrained optimization | Valid editing actions, property/similarity reward | Validity 100%, similarity/property success | 是 | Generated molecules / optimization episodes | 否, 动作空间预防 | 支持把 invalid action 与 property failure 分开 | 不是 failed candidate repair |
| [SELFIES](https://arxiv.org/abs/1905.13741) | 2019/2020 | Robust molecular representation | 字符串表示层约束 | 100% robust validity claim | 是, 表示层 | Generated strings | 否, 是预防 invalid string | 支持 chemical invalidity 可通过表示预防 | 不是 post hoc repair |
| [Torsional Diffusion](https://arxiv.org/abs/2206.01729) | 2022 | Molecular conformer generation | 2D graph -> 3D conformer / torsion diffusion | Conformer RMSD, relaxation, geometry quality | 是, conformer metrics | GEOM-like conformers | 部分, conformation refinement | 支持构象修复与图修复分离 | 不处理 protein pocket 或 scaffold repair |
| [3D pocket-aware lead optimization model](https://academic.oup.com/bib/article/26/4/bbaf345/8193459) | 2025 | 3D target-aware lead optimization / fragment decoration | 生成 500 candidates/site -> filtering/select/synthesis | Affinity, QED, SA, LogP, Lipinski, Vina, RMSD, H-bonds, LE | 是, stage selection | Generated candidates | 否, 多阶段筛选 | 说明真实 lead optimization 多为 generate-filter-select | 没有失败候选诊断 repair |

## C. 工具/判定方法证据表

| 工具/方法 | 判定对象 | 输入 | 输出 | 阈值/规则来源 | 更适合作为标签/指标/过滤规则 | 局限性 | 来源 |
|---|---|---|---|---|---|---|---|
| RDKit `SanitizeMol` | 化学图有效性, valence, kekulization, aromaticity 等 | RDKit Mol | 成功返回 `SANITIZE_NONE/0`; 默认失败抛异常; `catchErrors=True` 返回失败 flag | RDKit 官方 sanitization operations 与 allowed valence 规则 | chemical_invalid 硬标签或基础过滤 | RDKit validity 不是药物合理性; 不检查 pocket pose | [API](https://www.rdkit.org/docs/source/rdkit.Chem.rdmolops.html#rdkit.Chem.rdmolops.SanitizeMol), [Book](https://www.rdkit.org/docs/RDKit_Book.html#molecular-sanitization) |
| RDKit `MolFromSmiles` / `MolFromMolBlock` | 字符串/SDF/MolBlock 解析有效性 | SMILES, MolBlock, SDF | Mol object 或 None; 可选 sanitize | 官方 parser 文档 | parser_failure / sanitization_failure 区分 | 需明确是否开启 sanitize; SDF 3D 几何不一定合理 | [rdmolfiles](https://www.rdkit.org/docs/source/rdkit.Chem.rdmolfiles.html) |
| PoseBusters PB-valid | 生成或 docking pose 的化学身份、内部几何、protein/cofactor overlap、RMSD 等 | Predicted ligand, optional true ligand, conditioned protein | 每项 check 的 pass/fail, summary, CSV/DataFrame | PoseBusters 论文 Methods/Table 4 与官方 config | 3D pose plausibility 硬过滤和多标签来源 | 阈值为 benchmark/工具规则, 不等同实验密度验证; 对输入清洗敏感 | [paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC10901501/), [docs](https://posebusters.readthedocs.io/en/latest/), [repo](https://github.com/maabuu/posebusters) |
| PoseBusters distance/flatness/energy/overlap modules | bond/angle outlier, internal clash, planarity, UFF energy, pocket overlap | Ligand SDF + protein/cofactor/water | Boolean columns 与中间量 | 官方 config 与论文: 例如 DG bounds tolerance, planarity, energy ratio, vdW distance/overlap | geometry_invalid, internal_clash, pocket_overlap, too_far_from_pocket | 需要明确使用 `mol/dock/redock` 哪个 config; 阈值不能随意迁移 | [API](https://posebusters.readthedocs.io/en/latest/api.html), [CLI](https://posebusters.readthedocs.io/en/latest/cli.html), [config](https://raw.githubusercontent.com/maabuu/posebusters/main/posebusters/config/dock.yml) |
| AutoDock Vina output | Docking score / poses / run status | Receptor, ligand, config | mode, affinity, RMSD l.b./u.b. relative to best mode, PDBQT poses | 官方文档; no universal score failure threshold | score/ranking metric; run_failure 记录 | affinity 不是 failure label; relative RMSD 不是 redocking RMSD | [docs](https://autodock-vina.readthedocs.io/en/latest/docking_basic.html), [FAQ](https://autodock-vina.readthedocs.io/en/latest/faq.html) |
| Redocking RMSD < 2 Å | 有参考实验 pose 时的 pose recovery | Predicted pose + crystal/reference pose | RMSD; success/failure | AutoDock Vina, GNINA, Vinardo/Smina 等 redocking 文献常用 | pose_accuracy_failure, 但仅在有 reference 时 | 无 reference 时不可用; 不检查物理合理性 | [Vina](https://pubmed.ncbi.nlm.nih.gov/19499576/), [GNINA](https://doi.org/10.1186/s13321-021-00522-2), [Vinardo](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0155183) |
| GNINA CNNscore/CNNaffinity/Energy | Pose ranking / affinity proxy | Docked poses | CNNscore, CNNaffinity, Energy, output poses | GNINA README 与论文 | ranking metric, reranking/filtering criterion | 不是 repair label; 低分阈值需任务自定义或校准 | [repo](https://github.com/gnina/gnina), [paper](https://doi.org/10.1186/s13321-021-00522-2) |
| PLIP | Protein-ligand noncovalent interactions | PDB/custom complex | Interaction table, XML/text, 2D/3D figures, PyMOL session | PLIP 论文与 `config.py` 默认距离/角度规则 | interaction_loss / key_interaction_missing secondary tag | 对质子化、氢、配体识别和坐标质量敏感; 不是 clash validator | [paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC4489249/), [config](https://raw.githubusercontent.com/pharmai/plip/master/plip/basic/config.py) |
| ProLIF | Protein-ligand interaction fingerprints | RDKit/MDAnalysis complex, poses/trajectory | IFP dict, dataframe, bitvectors, metadata | ProLIF 论文/文档/源码默认 interaction parameters | contact_recovery, IFP similarity, secondary tag | 二值 failure 阈值需标定; alternative interactions 可能等价 | [paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC8466659/), [docs](https://prolif.readthedocs.io/en/latest/) |
| ODDT IFP/SPLIF/PLEC | Residue-level IFP, contact fingerprints | ODDT ligand/protein molecules | NumPy vectors, structured contact hashes, sparse/dense fingerprints | ODDT 文档/源码中的 interaction cutoff | contact_missing, low_contact_recovery, baseline metric | SPLIF/PLEC 化学解释性弱; 不直接给 clash 严重度 | [docs](https://oddt.readthedocs.io/en/latest/rst/oddt.html#module-oddt.fingerprints), [paper](https://doi.org/10.1186/s13321-015-0078-2) |
| BINANA | Protein-ligand interaction characterization | Receptor/ligand PDB/PDBQT | Interaction/contact counts, atom-type pair tallies | 官方 README/INTERACTIONS default cutoff | interaction count drop / close-contact metric | close contact 不等同 steric clash; 依赖 atom typing/charges | [repo](https://github.com/durrantlab/binana), [INTERACTIONS](https://raw.githubusercontent.com/durrantlab/binana/master/INTERACTIONS.md) |
| Arpeggio / pdbe-arpeggio | Interatomic contacts, clash/vdw_clash, noncovalent interactions | mmCIF protein/ligand selection | JSON contacts: clash, vdw, proximal, hbond, ionic, aromatic 等 | CREDO/contact rules, README; proximal within 5 Å | pocket_clash, vdw_clash, interaction contact label | 结构预处理/altloc/missing density 需要统一; 当前工具偏 mmCIF | [repo](https://github.com/PDBeurope/arpeggio) |
| MolProbity / Probe | All-atom clash / contact validation | PDB/mmCIF, 通常 Reduce 加 H | clashscore, serious clash count, contact visualization | MolProbity/Probe 文献: serious clash overlap >0.4 Å per 1000 atoms | steric_clash / pocket_overlap 独立验证 | 需要合理加氢和 ligand parameters; 非完整 ligand geometry validator | [MolProbity](https://pmc.ncbi.nlm.nih.gov/articles/PMC1933162/), [Probe/Reduce](https://pmc.ncbi.nlm.nih.gov/articles/PMC5734394/) |
| HBPLUS / LigPlot+ | H-bond 与 2D interaction diagram | Protein-ligand complex | H-bond list, nearby contacts, 2D plots | HBPLUS manual 几何字段; LigPlot+ 页面 | hbond_missing/hbond_recovered 辅助标签 | 不覆盖全 interaction taxonomy 或 clash; LigPlot+ 页面不应作为 cutoff 来源 | [HBPLUS manual](https://www.ebi.ac.uk/thornton-srv/software/HBPLUS/manual.html), [LigPlot+](https://www.ebi.ac.uk/thornton-srv/software/LigPlus/) |
| RDKit `HasSubstructMatch` / `GetSubstructMatch` | Substructure / motif / anchor preservation | Query SMARTS/Mol + candidate Mol | 是否匹配, atom indices | RDKit API; 阈值来自任务约束 | scaffold/substructure violation 硬规则或审计指标 | 需要定义 canonicalization, tautomer/protonation 和 atom mapping | [API](https://www.rdkit.org/docs/source/rdkit.Chem.rdchem.html#rdkit.Chem.rdchem.Mol.GetSubstructMatch) |
| RDKit MurckoScaffold | Scaffold preservation | Mol/SMILES | Scaffold Mol/SMILES | RDKit scaffold API; 相等/包含关系由任务定义 | scaffold preservation metric/filter | Bemis-Murcko 不等同所有 medicinal scaffold 语义 | [API](https://www.rdkit.org/docs/source/rdkit.Chem.Scaffolds.MurckoScaffold.html) |
| RDKit `ReplaceCore` / `ReplaceSidechains` / atom maps | Core, side-chain, attachment identity | Core query + molecule; atom map labels | Side chains with dummy/attachment labels | RDKit API; task-defined boundary rules | anchor/attachment mismatch 判定与 edit tracing | 不自动证明 3D 坐标合理; 需与 geometry/pose checks 结合 | [rdmolops](https://www.rdkit.org/docs/source/rdkit.Chem.rdmolops.html) |
| RDKit `ConstrainedEmbed` | 3D core-coordinate preservation / constrained conformer generation | Molecule + core coordinates | Constrained embedded Mol | 官方 API; RMSD cutoff 需任务协议定义 | core/anchor coordinate preservation metric | 官方无通用 pass/fail 阈值 | [API](https://www.rdkit.org/docs/source/rdkit.Chem.AllChem.html#rdkit.Chem.AllChem.ConstrainedEmbed) |
| 3DLinker evaluation protocol | Linker validity, connected fragments, recovery, RMSD | Generated linker molecules | Valid %, recovered %, 2D filters, RMSD, SCRDKit | 论文任务定义: obey chemical constraints and link fragments | linker_connection / anchor preservation evaluation | Invalid discarded 后算后续指标, 会影响分母解释 | [paper](https://proceedings.mlr.press/v162/huang22d.html) |
| DiffLinker evaluation protocol | Pocket-conditioned linker quality, pocket clash | Generated linkers + fragments + pocket | Valid, unique, novel, 2D filters, recovery, RMSD, pocket clash counts | 论文定义 pocket clash 为 atom distance 小于 vdW radii sum | local repair 评价维度, clash/filtering criterion | QED/SA 等是指标, 不是 failure taxonomy | [paper](https://arxiv.org/abs/2210.05274) |
| QED / SA / Lipinski | Drug-likeness, synthetic accessibility, oral-likeness heuristic | Molecule | Continuous score or descriptor/rule outputs | QED, SA score, Lipinski 原始论文和 RDKit docs | evaluation metric / property filter / secondary tag | 不应默认当 fixed-scaffold local repair 的硬 failure; PROTAC 等不适合简单套用 | [QED](https://pubmed.ncbi.nlm.nih.gov/22270643/), [SA](https://pubmed.ncbi.nlm.nih.gov/20298526/), [Lipinski](https://pubmed.ncbi.nlm.nih.gov/11259830/), [RDKit QED](https://www.rdkit.org/docs/source/rdkit.Chem.QED.html) |

## D. 候选 failure labels 清单

下表是面向本项目的候选 operational taxonomy。除 PoseBusters 等少数 benchmark 明确给出多项 check 外, 大多数标签不是文献中统一命名的 taxonomy, 而是从已有指标、工具和任务约束中归纳出的可操作类别。

| 标签名称 | 定义 | 文献或工具依据 | 判定依据 | 是否文献明确提出 | 证据强度 | primary/secondary 适用性 | 是否可能属于 local repair in-scope |
|---|---|---|---|---|---|---|---|
| `chemical_invalid` | 分子无法被基础化学规则接受, 如解析失败、价态错误、kekulization/sanitization 失败 | RDKit, liGAN, GraphBP, DiffSBDD, DrugGPS, 3DLinker/DiffLinker | `MolFrom*` 返回 None 或 `SanitizeMol` 失败; 论文 validity 定义 | 文献常明确报告 validity, 但不一定叫 failure label | 强 | 可作为 primary hard failure; 也可拆 secondary cause | 通常不适合作为第一阶段 local repair 主目标, 除非错误极局部且可确定 |
| `identity_or_graph_inconsistent` | 候选 pose 的 molecular formula, bond graph, stereo 与目标/参考不一致 | PoseBusters identity/consistency checks | PoseBusters formula/bonds/stereo pass/fail | PoseBusters 明确 check | 强 | primary, 特别是 pose/docking 输出审计 | 多数不适合, 因为需要分子图或身份修复 |
| `disconnected_or_fragment_missing` | 分子断裂、最大连通分量丢失、linker 未连接片段或 input fragments 未保留 | DiffSBDD connectivity, 3DLinker validity/recovered, DiffLinker fragments, DecompDiff incomplete/disconnected | 连通性检查, fragment/substructure match, linker recovered | 文献明确报告 connectivity/recovery/incomplete | 强 | primary hard failure | 若 scaffold/anchor 缺失通常 out-of-scope; 若只是局部 linker 连接可作为后期 repair |
| `invalid_local_3d_geometry` | 分子图可解析, 但局部 bond length/angle, ring/alkene planarity, torsion 或 conformer geometry 不合理 | PoseBusters, liGAN, DeepLigBuilder, Pocket2Mol, Torsional Diffusion | PoseBusters distance_geometry/flatness checks; RDKit DG bounds; conformer geometry comparison | PoseBusters 明确; 其他文献多以指标/案例讨论 | 强 | 可 primary 或 secondary | 是, 若 scaffold/anchor 保留且错误局限于 editable region 或 conformer |
| `internal_ligand_clash_or_high_energy` | ligand 内部非键合原子过近或 internal energy 异常 | PoseBusters, energy minimisation studies | PoseBusters internal steric clash, UFF energy ratio; force-field minimization change | PoseBusters 明确 | 强 | primary/secondary | 是, 若可通过局部 torsion/coordinate repair 解决 |
| `protein_ligand_steric_clash` | ligand 与 protein/cofactor/water 存在过近接触或体积重叠 | PoseBusters, MolProbity/Probe, Arpeggio, DiffLinker, DecompDiff | vdW distance/overlap, clashscore, volume_overlap, Arpeggio clash/vdw_clash | PoseBusters/MolProbity 明确; 生成文献也报告 pocket clash | 强 | primary, 也可 secondary tag | 是, 是 fixed-scaffold local repair 的核心候选目标 |
| `pose_accuracy_failure` | 有参考晶体 pose 时, 预测 pose 未恢复到阈值内 | Vina, GNINA, EquiBind, TANKBind, DiffDock, PoseBusters | Heavy-atom/symmetry-aware RMSD, 常见 RMSD < 2 Å success | 文献明确使用 | 强 | primary evaluation failure | 条件性 in-scope: 若 scaffold/anchor 保留且局部 pose/torsion 可改; 若整体 docking 错位则 out-of-scope |
| `pocket_detachment_or_too_far` | ligand 不在 pocket 合理接触范围内, 或与 receptor 太远 | PoseBusters max/min intermolecular distance checks | PoseBusters protein-ligand maximum/minimum distance check | PoseBusters 明确 check | 中 | primary/secondary | 通常需要 docking redo 或 global pose correction, 第一阶段应谨慎纳入 |
| `interaction_loss` | 关键 protein-ligand interaction, residue contact 或 interaction fingerprint 未恢复 | PLIP, ProLIF, ODDT, Marcou/Rognan IFP, SILIRID | 与参考/目标 interaction bits 比较; PLIP/ProLIF/ODDT contacts; recall/Tanimoto/Jaccard | 工具明确输出 interactions; “loss”多为我们 operational 定义 | 中 | secondary tag; 若预指定关键 interaction 可 primary | 是, 但需允许等价替代 interaction, 不宜过硬 |
| `scaffold_or_substructure_violation` | 任务要求保留的 scaffold/core/motif 不存在或发生非允许编辑 | RDKit substructure/Murcko, constrained optimization, JT-VAE/GCPN, linker papers | `HasSubstructMatch`, scaffold SMILES equality/containment, protected atom mapping | 文献常报告 constraint/similarity success, 工具支持判定; taxonomy 需自定义 | 中 | primary hard failure | 若 scaffold 不固定则 out-of-scope; 若只是局部编辑边界轻微漂移, 可作为 repair 约束 |
| `anchor_attachment_mismatch` | anchor atom, attachment point, dummy label 或 linker 连接位置不符合约束 | 3DLinker, DiffLinker, SyntaLinker, ShapeLinker, RDKit ReplaceCore/atom map | Atom mapping, attachment dummy labels, linker recovered, fragment contains/all anchors | linker 文献明确处理 anchors/recovery, 但标签命名需 operational | 强, 在 linker 场景 | primary for fixed-anchor tasks | 是, 是 local editing/repair 的核心约束之一 |
| `constraint_filter_failure` | similarity, 2D filters, recovery, SLBD/pharmacophore, shape/color, SCRDKit 等任务约束未通过 | SyntaLinker, DiffLinker, 3DLinker, ShapeLinker, JT-VAE, GCPN | 任务定义的 filter/pass rate | 文献明确统计 success/pass, 但各任务定义不同 | 中 | secondary 或 task-specific primary | 条件性, 只纳入与本项目 scaffold/anchor/local edit 直接相关的约束 |
| `property_constraint_failure` | QED, SA, Lipinski, logP, affinity proxy 等 property 不满足筛选目标 | QED, SA, Lipinski, GCPN, JT-VAE, SBDD papers | 论文/任务定义的 property threshold 或 ranking | 文献常作为 metric/filter, 不作为 repair taxonomy | 中 | secondary metric/filter, 不建议 primary | 通常不作为第一阶段 local repair 主目标, 可作为后续筛选或副指标 |
| `poor_docking_score_or_affinity_proxy` | Docking score/CNN affinity/estimated affinity 不佳 | Vina, GNINA, SBDD papers | Score/ranking, high-affinity threshold if paper-defined | 作为 metric 明确; 作为 failure label 不充分 | 中/弱 | 仅 secondary/ranking, 不建议 primary | 不宜单独作为 repair label; 可配合 pose/clash/interaction 解释 |
| `docking_or_evaluation_run_failure` | Docking/checker 程序无输出、解析失败、报错或输出模式不足 | Vina FAQ, GNINA README, RDKit/PoseBusters CLI | exit status, logs, output file exists/parsable, mode count | 工具文档支持 run status, 不是 molecule error | 中 | pipeline failure 单独记录 | 不属于 molecule local repair, 应排除或单独统计 |

## E. 可修复性边界和证据缺口

### E.1 适合 fixed-scaffold local repair 的错误类型

最适合本项目第一阶段聚焦的是“near-miss”类型失败, 即分子图、scaffold/anchor 和主要 pocket 定位仍基本保留, 但局部 3D geometry, ligand-packet overlap 或 interaction pattern 不满足要求。文献依据主要来自 PoseBusters 对几何、内部 clash、protein overlap 的系统检查, DiffLinker/3DLinker/ShapeLinker 对 linker/anchor/fragment recovery 与 pocket clash 的评价, 以及 PLIP/ProLIF/ODDT/Arpeggio 对 protein-ligand interaction/contact 的可操作输出。

可以优先纳入的 primary labels 包括 `protein_ligand_steric_clash`, `invalid_local_3d_geometry`, `internal_ligand_clash_or_high_energy`, `anchor_attachment_mismatch`, 以及在有参考 pose 或 anchor 约束时的局部 `pose_accuracy_failure`。可以作为 secondary tags 的包括 `interaction_loss`, `poor_docking_score_or_affinity_proxy`, `property_constraint_failure` 和较细粒度的 PoseBusters sub-checks。这样设计的好处是把“修复目标”限制在局部坐标、torsion、linker/side-chain 几何、pocket clash 和 key interaction recovery 上, 避免把全局生成或筛选问题误收为 local repair。

### E.2 更可能需要 global regeneration, docking redo, scaffold redesign 或 pipeline fix 的错误类型

`chemical_invalid`, `identity_or_graph_inconsistent`, 严重 `disconnected_or_fragment_missing`, scaffold/core/anchor 完全丢失, ligand 整体远离 pocket, 以及 docking/evaluation run failure, 都不适合作为第一阶段 fixed-scaffold local repair 的主目标。它们可能需要重新生成分子图、重新指定 scaffold/anchor、重新 docking, 或修复 pipeline/input preparation。将这些样本直接放入 local repair 训练可能会混淆任务, 也可能导致模型被迫解决本不属于局部编辑的问题。

Property 或 affinity proxy 类失败也应谨慎处理。QED, SA, Lipinski, Vina score, CNNaffinity 等在多数论文中是评价指标、筛选规则或优化目标, 不是结构错误标签。除非任务已经定义“局部编辑必须改善某个 property 且保持 scaffold/anchor”, 否则不应把低 QED/SA 或低 docking score 单独当作 primary repair target。

### E.3 目前证据不足, 需要后续本地审计确认的内容

第一, 文献没有给出本项目目标失败类型在真实 baseline/generated failed outputs 中的比例。PoseBusters 能说明 RMSD success 与 physical validity 之间存在显著 attrition, 但不能直接推断本项目 fixed-scaffold local repair 的 near-miss 占比。第二, 多数 SBDD 论文只报告 final aggregate metrics, 很少保存或分析 raw rejected samples, 因而无法仅凭文献判断模型原始输出中 scaffold/anchor-preserved local failures 的比例。第三, interaction loss 的二值化阈值需要本项目标定, 因为不同相互作用可能存在等价替代, 简单按参考 PLIP/ProLIF bit 缺失可能过严。第四, pocket clash 和 geometry checks 的阈值虽然有 PoseBusters/MolProbity 等依据, 但应用到本项目时仍需固定输入清洗、氢处理、cofactor/water 选择、atom typing 和 denominator。

### E.4 容易遗漏的标签

最容易遗漏的不是显眼的 RDKit invalid 或 RMSD failure, 而是中间层的 near-miss 标签: scaffold/anchor 保留但 attachment identity 漂移, linker 成功连接但 3D constrained embedding 失败, ligand 与 pocket 有局部 volume overlap 但 docking score 仍不错, key interaction bit 缺失但产生了替代 contact, 以及程序/工具运行失败被误记为 molecule failure。另一个容易遗漏的问题是分母变化: raw generation attempts, valid molecules, docked poses, top-N selected candidates, PoseBusters-evaluable poses 和 final selected molecules 的失败率不能混在一起比较。

### E.5 建议构建的 operational taxonomy

由于未发现统一的 repair-oriented taxonomy, 后续应把 taxonomy 明确设计为本项目的 operational taxonomy, 并在报告和论文中如实声明其来源。推荐采用 primary failure type + secondary tags 的多标签结构。primary type 用于表示最小可行动作: `pipeline_run_failure`, `chemical_graph_failure`, `scaffold_anchor_constraint_failure`, `local_3d_geometry_failure`, `protein_ligand_clash_failure`, `pose_reference_failure`, `interaction_recovery_failure`, `property_filter_failure`。secondary tags 记录具体工具证据, 例如 RDKit sanitize flag, PoseBusters failed columns, PLIP/ProLIF missing bits, Arpeggio clash type, substructure/anchor mapping status, QED/SA/Lipinski flags。

这种结构能避免两个常见错误。第一, 不把 metric 名称直接等同于 failure label: Vina score, QED, SA, CNNscore 等默认是 metric/filter, 只有在任务协议定义了阈值时才成为 secondary flag。第二, 不把文献中的 aggregate success rate 误写成多标签 prevalence: 多标签占比必须由本项目后续 local audit 在固定分母上统计。

### E.6 后续本地 failure prevalence audit 前还需要补充核查的来源

后续如果进入本地 audit, 还需要进一步核查并固定以下细节: PoseBusters 使用 `mol`, `dock` 还是 `redock` config; RDKit sanitization 是否 catch errors 并记录具体 flags; protein/ligand 加氢、protonation、tautomer、metal/cofactor/water 处理规则; PLIP/ProLIF/Arpeggio 是否使用同一清洗后的结构; scaffold/anchor 的 atom mapping 与 substructure query 如何定义; reference pose/RMSD 是否可用于每个样本; docking run failure 与 molecule failure 如何分开计数。只有这些协议固定后, 才能安全统计本项目 outputs 中各类 failure prevalence。

## 结论对本项目的直接启示

本项目不宜声称“已有文献给出了 failed ligand repair 的标准 taxonomy”。更稳妥的定位是: 现有 SBDD/docking/linker/editing 文献已经提供了许多可核验的失败证据和判定工具, 但这些证据分散在 validity, PoseBusters checks, RMSD success, interaction fingerprints, linker recovery, scaffold/anchor constraints 和 filtering metrics 中。我们的贡献可以是把这些分散指标整理为面向 fixed-scaffold pocket-aware local repair 的 operational multi-label taxonomy, 并在后续 audit 中系统统计每类失败的分母、占比、可修复性和修复效果。

第一阶段建议只把 near-miss local failures 作为主修复目标: scaffold/anchor 基本保留, 分子图可解析, ligand 仍位于 pocket 附近, 但局部 geometry, pocket clash 或 interaction/contact 不满足。严重化学无效、全局 scaffold 丢失、整体 pose 错位、工具运行失败和纯 property filter failure 应单独记录或排除, 不应混入 fixed-scaffold local repair 的核心训练目标。

## 参考来源索引

- AutoDock Vina: https://pmc.ncbi.nlm.nih.gov/articles/PMC3041641/
- GNINA 1.0: https://doi.org/10.1186/s13321-021-00522-2
- EquiBind: https://proceedings.mlr.press/v162/stark22b.html
- TANKBind: https://www.proceedings.com/content/068/068431-0525open.pdf
- DiffDock: https://openreview.net/forum?id=kKF8_K-mBbS
- PoseBusters paper: https://pubs.rsc.org/en/content/articlehtml/2024/sc/d3sc04185a
- PoseBusters docs/repo: https://posebusters.readthedocs.io/en/latest/ ; https://github.com/maabuu/posebusters
- CASF-2016: https://doi.org/10.1021/acs.jcim.8b00545
- DUD-E: http://dude.docking.org/
- liGAN: https://arxiv.org/abs/2010.14442
- DeepLigBuilder / 3D deep generative SBDD: https://pubs.rsc.org/doi/d1sc04444c
- 3D Generative SBDD: https://arxiv.org/abs/2203.10446 ; https://github.com/luost26/3D-Generative-SBDD
- GraphBP: https://arxiv.org/abs/2204.09410 ; https://github.com/divelab/GraphBP
- Pocket2Mol: https://arxiv.org/abs/2205.07249 ; https://github.com/pengxingang/Pocket2Mol
- TargetDiff: https://arxiv.org/abs/2303.03543 ; https://github.com/guanjq/targetdiff
- DiffSBDD: https://arxiv.org/abs/2210.13695 ; https://github.com/arneschneuing/DiffSBDD
- DecompDiff: https://arxiv.org/abs/2403.07902 ; https://github.com/bytedance/DecompDiff
- DrugGPS / FLAG: https://arxiv.org/abs/2305.13997 ; https://github.com/zaixizhang/FLAG
- DeLinker: https://doi.org/10.1021/acs.jcim.9b01120
- SyntaLinker: https://pubs.rsc.org/en/content/articlehtml/2020/sc/d0sc03126g
- DiffLinker: https://arxiv.org/abs/2210.05274
- 3DLinker: https://proceedings.mlr.press/v162/huang22d.html
- ShapeLinker: https://arxiv.org/abs/2306.08166
- DeepFrag: https://pubs.rsc.org/en/content/articlelanding/2021/sc/d1sc00163a
- GCPN: https://arxiv.org/abs/1806.02473
- JT-VAE: https://arxiv.org/abs/1802.04364
- MolDQN: https://pmc.ncbi.nlm.nih.gov/articles/PMC6656766/
- SELFIES: https://arxiv.org/abs/1905.13741
- Torsional Diffusion: https://arxiv.org/abs/2206.01729
- 3D pocket-aware lead optimization model: https://academic.oup.com/bib/article/26/4/bbaf345/8193459
- RDKit sanitization/API: https://www.rdkit.org/docs/source/rdkit.Chem.rdmolops.html#rdkit.Chem.rdmolops.SanitizeMol ; https://www.rdkit.org/docs/RDKit_Book.html#molecular-sanitization
- RDKit substructure/scaffold/constrained embed: https://www.rdkit.org/docs/source/rdkit.Chem.rdchem.html#rdkit.Chem.rdchem.Mol.GetSubstructMatch ; https://www.rdkit.org/docs/source/rdkit.Chem.Scaffolds.MurckoScaffold.html ; https://www.rdkit.org/docs/source/rdkit.Chem.AllChem.html#rdkit.Chem.AllChem.ConstrainedEmbed
- PLIP: https://pmc.ncbi.nlm.nih.gov/articles/PMC4489249/ ; https://raw.githubusercontent.com/pharmai/plip/master/plip/basic/config.py
- ProLIF: https://pmc.ncbi.nlm.nih.gov/articles/PMC8466659/ ; https://prolif.readthedocs.io/en/latest/
- ODDT: https://oddt.readthedocs.io/en/latest/rst/oddt.html#module-oddt.fingerprints ; https://doi.org/10.1186/s13321-015-0078-2
- BINANA: https://github.com/durrantlab/binana ; https://raw.githubusercontent.com/durrantlab/binana/master/INTERACTIONS.md
- Arpeggio: https://github.com/PDBeurope/arpeggio
- MolProbity / Probe: https://pmc.ncbi.nlm.nih.gov/articles/PMC1933162/ ; https://pmc.ncbi.nlm.nih.gov/articles/PMC5734394/
- HBPLUS / LigPlot+: https://www.ebi.ac.uk/thornton-srv/software/HBPLUS/manual.html ; https://www.ebi.ac.uk/thornton-srv/software/LigPlus/
- QED / SA / Lipinski: https://pubmed.ncbi.nlm.nih.gov/22270643/ ; https://pubmed.ncbi.nlm.nih.gov/20298526/ ; https://pubmed.ncbi.nlm.nih.gov/11259830/
