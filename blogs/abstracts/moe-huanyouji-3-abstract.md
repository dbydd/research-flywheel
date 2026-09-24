---
title: MoE环游记：3、换个思路来分配
slug: moe-huanyouji-3-abstract
type: abstract
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3/moe-huanyouji-3.extracted.md
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3/moe-huanyouji-3.html
resource: raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3
---

# MoE环游记：3、换个思路来分配

> [!quote] 官方摘要
> 这篇文章我们继续探讨MoE的负载均衡问题。在上一篇文章《MoE环游记：2、不患寡而患不均》中，我们主要讨论了通过Aux Loss来促进负载均衡的思路。……本文要分享的是名为“Loss-Free”的方案，由DeepSeek在《Auxiliary-Loss-Free Load Balancing Strategy for Mixture-of-Experts》提出。

## 一句话判断

这一篇介绍 DeepSeek 的 Loss-Free 负载均衡。做法是保留 Router 的打分结果，改掉分配方式：把 `argtop_k ρ` 换成 `argtop_k(ρ + b)`，`b` 是输入无关的偏置向量，只在分配阶段参与，乘到 Expert 上的是 `ρ_i`。`b` 没有梯度，于是单独定制更新规则：统计当前负载分布 `F`，做符号梯度下降 `b ← b − γ·sign(F − Q)`，原论文给出的默认值是 `γ = 0.001`。作者接着用上一篇的 STE 配方把这条规则从 Aux Loss 推出来，说明两条路线在梯度上同源。他对 Loss-Free 本质的判断是：创新点在于“一个偏置项足以达到负载均衡”这一事实，由此把均衡与语言模型损失的优化参数隔离开，让两者的优化方向互不牵制。本文还提了两处改良，一是用 RMS Norm 代替 sign，保留偏离幅度的相对大小，减少已接近均衡的 Expert 来回震荡；二是把加 `b` 的那路打分固定用 Sigmoid、乘 Expert 的门控换别的单调非负激活，这样就能继续复用 `γ = 0.001`。使用时要注意顺序：先用语言模型损失更新模型参数，再用新统计量更新 `b`，这样才不泄漏未来 token 的信息。

## 本体与去向

- 本体：`raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3/`
- 精读：[[moe-huanyouji-reading|MoE环游记系列精读]]
- 系列：上一篇 [[moe-huanyouji-2-abstract|MoE环游记：2、不患寡而患不均]]；下一篇 [[moe-huanyouji-4-abstract|MoE环游记：4、难处应当多投入]]
