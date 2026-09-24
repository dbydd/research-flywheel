---
title: 门控归一化的三选一
slug: gating-normalization
type: concept
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2026-06/moe/spaces-ac-cn/moe-huanyouji-9/moe-huanyouji-9.extracted.md
  - raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-1/moe-huanyouji-1.extracted.md
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3/moe-huanyouji-3.extracted.md
---

# 门控归一化的三选一

MoE（混合专家）把 Transformer 里的 MLP 层换成若干并行的小网络，每个 token 只走其中几个。token 是模型处理文本的最小单位，通常是一小段词或子词；专家指这些小网络中的一个；Router 是从输入预测每个专家模长的小模型，模长记作 ρ；Top-k 指按打分从高到低取前 k 个专家。同一个 ρ 在这里兼两个角色：选 Top-k 时它扮演 Router，乘到专家输出上时它扮演 Gate。Gate 指乘到专家输出上的那份权重，它的作用是在训练时为 Router 提供梯度，这个双重身份的几何来历见 [[router-magnitude-direction|Router 的方向-模长重参数化]]。

## 归一化指什么

归一化指把 Router 的打分做 Softmax，变成非负、总和为一的概率分布。Softmax 把任意一组打分变成这样的分布：每个分量非负，全体分量之和为 1。

打分与权重来自同一份 ρ：Top-k 的选择用它排序，乘到专家输出上的系数也用它。归一化作用在这份系数上，它同时决定 Gate 的取值与 Router 在训练时拿到的梯度，第九篇由此把这件事写成一道三选一的题。

打分的激活函数另有一条自由度。第一篇的几何视角里 ρ 的几何意义是模长，模长不需要按概率分布那样归一化，凡是输出非负的激活函数都可以用。Sigmoid 的输出落在 0 与 1 之间，ReLU 的输出非负，两者都满足这条非负要求。

## 三选一

- 先 Softmax 再选 Top-k：归一化发生在选择之前，选中的专家的权重取自同一个概率分布。
- 先选 Top-k 再 Softmax：这一步叫 Re-Norm，归一化作用在选中的 k 个分量上。
- 不做归一化：打分直接乘到专家输出上。这一条与第一篇的几何视角相容，ρ 的几何意义是模长，模长不需要按概率分布那样归一化。

Re-Norm 让前向数值更稳定，代价是 k 至少大于 1。

已有的选择在这三条上铺开。DeepSeek 为配合 Loss-Free 负载均衡把激活函数改成 Sigmoid，并用于 DeepSeek-V3；ReMoE 用 ReLU；第一篇的几何视角允许任意非负激活函数；Loss-Free 为这一改动给出的理由见 [[loss-free-balancing|Loss-Free 负载均衡：偏置与符号更新]]，DeepSeek 在系列里的位置见 [[deepseekmoe|DeepSeekMoE 与 DeepSeek 路线]]。

## 结论与边界

需要一个自上而下的概率推导时，Router 作为 Gate 应当归一化，并且不应当 Re-Norm。这条结论由门控的概率梯度推导给出：从 k = 1 出发、以 KL 散度为目标得到的那条等效损失，落在先归一化再选择的形式上，推导的每一步见 [[gating-policy-gradient|门控的概率梯度推导]]。

这条推导的适用范围由它自己的起点给出。k = 2 时概率框架给不出精确推导。k 大于 1 的 MoE 可以当作 Max Pooling 的类似物来读，Max Pooling 是局部窗口取最大值的下采样操作；也可以回到第一篇的几何视角，把 ρ 当作模长处理。

第九篇换到梯度一侧讨论门控，前八篇的路线落在偏置与均衡上，两侧合起来构成系列的收尾。这一节的讨论出自《MoE环游记：9、门控归一化之争》。[[moe-huanyouji-9-abstract|MoE环游记：9、门控归一化之争 摘要]] [[moe-huanyouji-reading|MoE环游记 系列精读]]
