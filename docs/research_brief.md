# pocket-failure-repair 研究简报

## 研究题目

**Failure-Feedback-Conditioned Repair for Pocket-Aware 3D Local Molecular Editing**

中文表述：

**面向蛋白口袋约束 3D 局部分子编辑的失败反馈条件化修复方法**

## 核心问题

现有 pocket-aware 3D 分子生成方法已经能够在蛋白口袋约束下生成整分子、R-group、linker 或 scaffold decoration 结果，但很多方法仍偏向一次性生成、多采样后重排序、用 Vina / affinity / interaction score 做通用 guidance。它们通常没有把“当前失败候选本身”作为下一轮修复的条件。

本项目聚焦一个更窄、更有差异化的问题：

> 给定 protein pocket、fixed scaffold、editable region 和一个已经失败的局部编辑候选，模型能否利用当前失败反馈，对这个具体候选进行局部修复，并在相同生成预算下比 Best-of-N、rerank-only、direct regeneration 和普通 guidance 更可靠？

## 差异化定位

本项目不主打泛泛的 pocket-aware molecular generation，也不主打普通 R-group generation。更准确的定位是：

> **failed-candidate-conditioned local molecular repair**

即：

- 不是从零生成整分子；
- 不是单纯固定 scaffold 生成 R-group；
- 不是只用 affinity / interaction 做通用引导；
- 不是只做 Best-of-N 重排序；
- 而是把当前失败候选及其失败反馈重新注入修复模型，让模型在同一 editable region 内进行定向修复。

## 主要假设

1. 当前失败候选中包含有价值的局部几何和化学上下文，直接丢弃并重新采样会浪费信息。
2. 失败反馈不一定需要人工结构化成标签，只要能被模型吸收并改变下一轮生成分布即可。
3. 几何反馈、相互作用反馈和全局性质反馈的组合，可能比单一 Vina / affinity guidance 更能提升可靠性。
4. 在相同生成预算下，反馈条件化修复应优于 Best-of-N 和 rerank-only。

## 最小可行任务

**Single R-group failed-candidate repair**

输入：

- protein pocket；
- original ligand；
- fixed scaffold；
- editable R-group mask；
- anchor atoms；
- failed candidate；
- feedback features。

输出：

- repaired local molecule / repaired editable region。

## 目标贡献

1. 定义 failed-candidate local repair 任务。
2. 构建反馈条件化局部修复模型。
3. 构建可靠性导向评价体系，避免只看 Vina。
4. 证明在相同预算下，反馈修复比 Best-of-N、rerank-only、direct regeneration 更可靠。
