---
title: Expert 正交假设
slug: expert-orthogonality
type: concept
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-1/moe-huanyouji-1.extracted.md
  - raw/2025-05/moe/spaces-ac-cn/moe-huanyouji-5/moe-huanyouji-5.extracted.md
---

# Expert 正交假设

MoE 用 k 个专家的输出之和逼近 n 个专家之和，误差有多大、该挑哪 k 个，第一篇正交假设给出答案。Expert 是 MoE 层里切出来的窄 MLP，一个 token 只走 Router 挑出的 k 个。[[moe-layer|MoE 层：把 MLP 换成并行专家]]

## 假设的内容与结论

假设各 Expert 的输出向量两两正交。正交指两个向量的内积为零，即它们的夹角等于 90 度。在这个近似下得到两条结论：

- 逼近误差等于被丢弃向量的模长平方之和，被丢弃向量就是那 n 减 k 个没被选中的专家输出；
- 最优挑法是保留模长最大的 k 个，这样逐项误差最小。

结论把挑选从「比较方向是否合适」简化成「比较长度」，由此给出可实现的策略：算模长、排序、取前 k。[[router-magnitude-direction|Router 的方向-模长重参数化]]

误差项的形状值得多看一眼。正交时各专家的贡献互不重叠，总输出里每一项各自独立可加，丢掉哪几项，误差就只是那几项模长平方之和。专家之间一旦有重叠，丢掉一项会连带改变其余项的贡献，误差项失去这份干净的形式。

由此也能看出挑选与预测的分工：挑选只需要一个标量排序依据，所以 Router 的任务被压缩成预测每个专家一个模长，无需输出整个向量。这条压缩是整个系列能往下走的前提。

## 正交是一项近似

专家之间存在共性。用几何语言说，任意两个专家输出向量的夹角小于 90 度，正交假设要求这个夹角等于 90 度。训练后期这项假设越难成立：专家之间学到的共性变多，向量之间的夹角随之变小。

第五篇正是从这点质疑均匀分布这个目标本身，它提出的反问是：抛开效率，均匀分布一定导向最好的效果吗。这一节的原始论述见 [[moe-huanyouji-5-abstract|MoE环游记：5、均匀分布的反思 摘要]]。

假设松动之后，先算 ρ、再挑前 k 这套流程照旧可用，变化只落在误差上：夹角越小，丢掉一项带走的连带影响越多，实际误差高出正交情形给出的估计。

## 让 Routed Expert 学习残差

一条让假设更容易成立的做法落在共享专家上。Shared Expert 指必然入选的专家，Routed Expert 指按 Router 挑选激活的专家。把 Shared Expert 视作 Routed Expert 的均值，让 Routed Expert 学习残差之后，共性由均值那一侧承担，被减去均值的各份之间差异更大，正交假设更容易成立。[[shared-expert|共享专家与比例因子]]
