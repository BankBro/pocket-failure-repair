# BIBM 执行说明

## 投稿目标

目标会议：IEEE BIBM。

本项目按 BIBM 论文目标推进，但必须以真实实验为准。如果结果不足以支撑投稿，不得强行包装。

## 论文主线建议

论文主线应围绕：

> Failed-candidate-conditioned repair for pocket-aware 3D local molecular editing.

不要写成泛泛的：

- pocket-aware generation；
- 3D molecule generation；
- R-group generation；
- affinity-guided molecular optimization；
- RL-guided generation。

这些方向已有大量工作，容易撞题。

## 最小投稿版本

最小投稿版本应至少包含：

1. 文献矩阵和撞题分析；
2. failed-candidate local repair 任务定义；
3. 数据构造流程；
4. 失败候选构造；
5. feedback extraction；
6. no-feedback repair baseline；
7. feedback-conditioned repair；
8. Best-of-N / rerank-only / direct regeneration baseline；
9. 至少 3 seeds；
10. 至少一个 split 的交叉验证；
11. 消融实验；
12. 失败案例和成功案例；
13. 论文初稿。

## 推荐图表

- Figure 1：任务示意图，展示 original ligand、fixed scaffold、editable region、failed candidate、feedback extraction、repaired candidate。
- Figure 2：方法框架，展示 pocket encoder、scaffold / editable mask、failed candidate encoder、feedback encoder、local repair decoder / diffusion refinement。
- Figure 3：iteration success curve，对比 direct regeneration、Best-of-N、rerank-only、no-feedback repair、full feedback repair。
- Table 1：与 DiffDec、Diffleop、AMG、MolJO、DecompDPO 和本方法的对比。
- Table 2：主实验结果。
- Table 3：消融实验。
- Figure 4：成功案例和失败案例可视化。

## 论文初稿章节

1. Abstract
2. Introduction
3. Related Work
4. Problem Definition
5. Method
6. Experiments
7. Results
8. Ablation Study
9. Case Study
10. Limitations
11. Ethics and Reproducibility
12. Conclusion

## 判断是否值得继续投稿

如果 full feedback repair 在相同预算下不能稳定超过 Best-of-N 或 rerank-only，则不要强行声称方法有效。应转向：

- 更强 feedback encoder；
- 更合理 failed candidate 数据构造；
- 更窄任务，例如 clash repair 或 interaction recovery；
- 将方法定位为 diagnostic benchmark / repair benchmark，而不是生成模型。
