---
title: Router 的方向-模长重参数化
slug: router-magnitude-direction
type: concept
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-1/moe-huanyouji-1.extracted.md
---

# Router 的方向-模长重参数化

MoE 层里每个 token 只走 k 个专家，挑选依据是各专家的模长：专家输出向量两两正交时，逼近误差等于被丢弃向量的模长平方之和，保留模长最大的 k 个即为最优。[[expert-orthogonality|Expert 正交假设]]

## 循环依赖

模长的计算依赖专家输出向量，而挑选专家这件事要排在计算输出之前。算模长等挑专家、挑专家等算模长，这条循环依赖堵住了直接实现的路。

## 拆成方向与模长

第一篇的解法是把每个 Expert 的输出重新参数化为方向与模长两部分：

- 方向 `e_i` 由归一化得到，做法是把向量除以其模长、只留方向，它的长度固定为 1；
- 模长 `ρ_i` 交给 Router 预测，Router 是一个从 d 维到 n 维的线性变换加一个非负激活，d 是输入维度、n 是专家总数。

计算顺序由此变成三步：先算全部 `ρ`，再选出其中前 k 个，然后只算这 k 个专家对应的方向 `e_i`，乘上 `ρ_i` 求和。整个 MoE 层的输出写作：

```text
y = Σ_{i∈argtop_k ρ} ρ_i e_i
```

`argtop_k ρ` 指 ρ 向量里取值最大的 k 个专家下标，求和只在这些下标上做。

这条式子是整个系列的基线形式，后面八篇反复回到它。这条式子出自 [[moe-huanyouji-1-abstract|MoE环游记：1、从几何意义出发 摘要]]。

## ρ 的几何意义是模长

`ρ` 表示一个向量有多长，它按几何量使用，不需要按概率分布那样归一化。可用的激活函数因此只需满足一条：输出非负。Sigmoid 的输出落在 0 与 1 之间，ReLU 的输出非负，这两类都可以用在 Router 上。

归一化指的是把 Router 打分做 Softmax 变成非负且总和为一的概率分布，它与这里说的几何量是两种不同的解释方式。第九篇把门控归一化写成三选一，其中列出的一条已有选择正是第一篇的几何视角允许任意非负激活函数。[[gating-normalization|门控归一化的三选一]]

## 同一个 ρ 的两个角色

同一个 `ρ` 在流程里出两次场：选 Top-k 时它是 Router，决定哪些专家被选中；乘到专家输出上时它是 Gate，决定选中专家的输出按多大权重加进结果。Gate 的作用是在训练时为 Router 提供梯度，Router 的打分能收到损失回传的信号正是靠这一路。[[gating-policy-gradient|门控的概率梯度推导]]
