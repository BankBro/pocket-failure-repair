# Literature Matrix

> 本文档用于维护文献检索、撞题分析和 related work 证据。所有条目必须能追溯到论文、代码仓库或官方文档。禁止伪造引用。

## 检索目标

重点确认 failed-candidate-conditioned local molecular repair 是否已有高度重合工作，并比较 pocket-aware 3D molecular generation、R-group generation、local editing、feedback/guidance、pose/interaction validation 相关方法。

## 待重点检索方法

- DiffDec
- Diffleop
- AMG
- MolJO
- DecompDPO
- DecompDiff
- DecompOpt
- PoseBusters
- PLIP
- AutoDock Vina

## 文献矩阵

| 方法 / 工具 | 年份 | 任务 | 输入条件 | 输出 | 是否 pocket-aware | 是否 local editing | 是否使用 failed candidate | feedback / guidance 类型 | 评价指标 | 代码 / 数据 | 与本项目关系 | 撞题风险 | 备注 |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|
| DiffDec | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | 待检索 |
| Diffleop | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | 待检索 |
| AMG | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | 待检索 |
| MolJO | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | 待检索 |
| DecompDPO | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | 待检索 |
| DecompDiff | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | 待检索 |
| DecompOpt | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | 待检索 |
| PoseBusters | TBD | Pose / molecule validation | TBD | Validation report | Yes/No | No | No | Rule-based validation | Validity / pose quality | TBD | Evaluation tool | Low | 待检索 |
| PLIP | TBD | Protein-ligand interaction profiling | Protein-ligand complex | Interaction profile | Yes | No | No | Interaction detection | Interaction types | TBD | Feedback extraction | Low | 待检索 |
| AutoDock Vina | TBD | Docking / scoring | Protein + ligand | Pose / score | Yes | No | No | Docking score | Vina score | TBD | Scoring baseline / feedback | Low | 待检索 |

## 撞题分析问题清单

1. 是否已有方法把 failed candidate 本身作为下一轮生成条件？
2. 是否已有方法针对 pocket-aware 3D local molecular repair，而不是 generation 或 optimization？
3. 是否已有方法显式利用 clash / interaction loss / anchor invalid 等失败反馈？
4. 是否已有方法在 same-budget repair setting 下对比 Best-of-N 与 rerank-only？
5. 是否已有 benchmark 专门评估 failed local candidate repair？

## 初步定位

当前项目暂定差异化切口：failed-candidate-conditioned local molecular repair。最终定位需在完成文献检索后更新。

## 检索记录

| 日期 | 查询 | 工具 | 结果摘要 | 输出 / 证据 |
|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD |
