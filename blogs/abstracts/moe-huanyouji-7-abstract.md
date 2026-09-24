---
title: MoE环游记：7、动态激活极简解
slug: moe-huanyouji-7-abstract
type: abstract
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-7/moe-huanyouji-7.extracted.md
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-7/moe-huanyouji-7.html
resource: raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-7
---

# MoE环游记：7、动态激活极简解

> [!quote] 官方摘要
> 上一篇文章《MoE环游记：6、最优分配促均衡》中，我们通过求解如下最优分配问题来实现负载均衡
> $$ \begin{equation}\max_{x_{i,j}\in\{0,1\}} \sum_{i,j} x_{i,j}s_{i,j} \qquad\text{s.t.}\qquad \sum_j x_{i,j} = k,\quad \sum_i x_{i,j} = \frac{mk}{n}\end{equation} $$
> 其中 $\sum_j x_{i,j} = k$ 表示每个Token恰好激活 $k$ 个Expert，而 $\sum_i x_{i,j} = mk/n$ 表示每个Expert恰好被激活 $mk/n$ 次。……注意，现在待求变量只有 $\boldsymbol{\beta}$，所以就没有交替迭代的步骤了，直接一步Quantile就得到了绝对均衡的最优解！

## 一句话判断

这一篇把上一篇的最优分配问题再砍一刀，得到一个极简解。做法是去掉“每个 token 恰好激活 `k` 个”的约束，只保留“每个 Expert 恰好被激活 `mk/n` 次”，对偶问题里只剩 `β` 一个变量，而它在每一列上有解析解——该列分数的 `1 − k/n` 分位数。于是不再需要交替迭代，一步 Quantile 就得到绝对均衡的最优解。激活规则相应变成 `s − β > 0` 即激活，免去了 Top-`k` 排序这一步；这个形式本质上把 Expert Choice 写成了 Token Choice，并把 `β` 的更新放到激活决策之后，因此不破坏因果性，也不依赖 Batch Size。实践中一步最优解容易过拟合当前批，处理办法是用 EMA 平滑历史解，文中取衰减率 0.9；初始化可以在 Router logits 近似正态的假设下取 `σ·Φ⁻¹(1 − k/n)`，Sigmoid 与 Softmax 版本各有对应的换算，`σ` 由 Router 权重初始化方差与输入维度估出。完全不想做 Quantile 时，可以对这个可导目标做符号梯度下降，成本更低，这条式子正是上一篇从直觉给出的那条公式。

## 本体与去向

- 本体：`raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-7/`
- 精读：[[moe-huanyouji-reading|MoE环游记系列精读]]
- 系列：上一篇 [[moe-huanyouji-6-abstract|MoE环游记：6、最优分配促均衡]]；下一篇 [[moe-huanyouji-8-abstract|MoE环游记：8、强制序列级均衡]]
