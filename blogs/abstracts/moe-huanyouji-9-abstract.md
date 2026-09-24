---
title: MoE环游记：9、门控归一化之争
slug: moe-huanyouji-9-abstract
type: abstract
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2026-06/moe/spaces-ac-cn/moe-huanyouji-9/moe-huanyouji-9.extracted.md
  - raw/2026-06/moe/spaces-ac-cn/moe-huanyouji-9/moe-huanyouji-9.html
resource: raw/2026-06/moe/spaces-ac-cn/moe-huanyouji-9
---

# MoE环游记：9、门控归一化之争

> [!quote] 官方摘要
> 即便在Softmax内讨论，也有着两种略微不同做法：是先Softmax再选Top- $k$ ，还是先选Top- $k$ 再Softmax呢？后者也可以理解为在选出Top- $k$ 后再做一次归一化，即Re-Norm。那么，Gate的激活函数是否要归一化，要的话是归一化后选Top- $k$ 还是Re-Norm，这便是本文要讨论的主题。

## 一句话判断

这一篇从第一性原理追问 `ρ` 兼作 Router 与 Gate 时该不该归一化，以及归一化放在选 Top-`k` 之前还是之后。推导从 `k = 1` 的期望开始——被激活的 Expert 应当是损失最小的那一个；把这个目标转化成拉近预测分布 `p` 与目标分布 `q`（由各 Expert 的损失做指数归一化得到）的 KL 距离，等效损失是 `Σ p_i ℓ(e_i)`，它的梯度正是 REINFORCE，噪声偏大。关键一步是对减 baseline 的 REINFORCE 做一阶泰勒展开，得到一个“前向用 1、反向用 log p_i”的 STE；把 Expert 从 `e_i` 换成 `p_i e_i` 之后，Stop Gradient 自动消失，前后向一致，效果天花板也随之提高。结论是 Gate 需要归一化，Re-Norm 不做；Re-Norm 还要求 `k ≥ 2`，`k = 1` 时 `ρ` 完全收不到梯度。这套推导提炼自刘力源《Sparse Backpropagation for MoE Training》三部曲；`k = 2` 时概率框架给不出精确推导，作者建议把 `k > 1` 的 MoE 当作 MaxPooling 的类似物，或者回到几何视角理解。文中另有一条实操建议：想要在采样与稳定性之间取中，可以先选出 Top-`k+c` 再在其中随机挑 `k` 个，或者在 logits 上加轻微噪声后再选 Top-`k`。

## 本体与去向

- 本体：`raw/2026-06/moe/spaces-ac-cn/moe-huanyouji-9/`
- 精读：[[moe-huanyouji-reading|MoE环游记系列精读]]
- 系列：上一篇 [[moe-huanyouji-8-abstract|MoE环游记：8、强制序列级均衡]]
