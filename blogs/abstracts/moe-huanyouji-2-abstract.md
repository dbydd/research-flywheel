---
title: MoE环游记：2、不患寡而患不均
slug: moe-huanyouji-2-abstract
type: abstract
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-2/moe-huanyouji-2.extracted.md
  - raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-2/moe-huanyouji-2.html
resource: raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-2
---

# MoE环游记：2、不患寡而患不均

> [!quote] 官方摘要
> 负载均衡，即“不患寡而患不均”，说白了就是让每个Expert都在干活，并且都在干尽可能一样多的活，避免某些Expert浪费算力。负载均衡既是充分利用训练算力的需求，也是尽可能发挥MoE大参数量潜力的需求。

## 一句话判断

这一篇讲负载均衡里的 Aux Loss，主要贡献是把这个沿用已久的损失函数补上来路。记号上先设 `p = ρ/Σρ` 为归一化的 Router 打分、`f` 为 Top-`k` 指示向量除以 `k`，再取全体样本全体 Token 的平均，得到 `P = E[p]`（`F` 的光滑近似）与 `F = E[f]`（当前负载分布），于是文献里通用的写法是 `L_aux = F·P`。作者指出这条损失在既有文献与科普里被反复引用，来路却没有交代，于是自己补了一版推导：从“让 `F` 逼近均匀分布 `Q`”出发，用 STE 把不可导的 `F` 替换成 `P + sg[F − P]`，求梯度后恰好落在 `F·P` 上。由此得到构造 Aux Loss 的一般配方——先按想要的 `F` 写损失，实现时做同一个替换；把目标换成熵的相反数，就能得到另一条可直接写进代码的 Aux Loss。读数条件是：`F·P` 本身不是可以单调下降的目标，当 `F = P` 时它等于 `1/n`，它的值还能更小，所以训练中它的数值下降与均衡程度改善是两件事。

## 本体与去向

- 本体：`raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-2/`
- 精读：[[moe-huanyouji-reading|MoE环游记系列精读]]
- 系列：上一篇 [[moe-huanyouji-1-abstract|MoE环游记：1、从几何意义出发]]；下一篇 [[moe-huanyouji-3-abstract|MoE环游记：3、换个思路来分配]]
