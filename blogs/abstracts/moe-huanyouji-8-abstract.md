---
title: MoE环游记：8、强制序列级均衡
slug: moe-huanyouji-8-abstract
type: abstract
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/moe-huanyouji-8.extracted.md
  - raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/moe-huanyouji-8.html
resource: raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8
---

# MoE环游记：8、强制序列级均衡

> [!quote] 官方摘要
> 到目前为止，“MoE环游记”系列已经写了7篇文章，其中5篇都是围绕着MoE的路由和负载均衡展开的。……如果我们相信每个Aux-Loss方案都有对应的Loss-Free版本，那么序列级的Loss-Free均衡，又应该怎么实现呢？这便是文本要探讨的主题。

## 一句话判断

这一篇把 QB 从全局均衡推到序列级均衡。背景是 Loss-Free 引入的偏置全局共享，已有的 Loss-Free 方案都只能做全局均衡，而序列级均衡此前的两条路子各有难处：对分数做滑动平均是经验做法，作者实测在极不均衡的层上帮助有限；测试时训练式的逐 token 偏置更新等价于非线性 RNN，序列一长就成为瓶颈。本文的路线是先设窗口 `w` 求滑动分位数，得到 Moving Quantile Balancing（MQB）的雏型；关键改进在于把分位数的估计转成分布的估计——把 `[0,1]` 内的分数分 `b` 个桶做 one-hot，沿序列做 EMA（这一步线性、可并行），再由累积概率读出 `1 − k/n` 分位数，作为逐 token 的 `β`。Top-`k` 版 MoE 则在 MQB 之后补一步全局 QB，并用 `λ` 削弱序列均衡的强度。实验配置为约 3B 总参数、128 选 4 的 MoE，滑动平均系数 0.99、分桶数 100，用 MaxVio 度量最不均衡的第一层：`λ = 1` 时均衡非常完美，代价是 Loss 差 0.06，`λ` 调到 0.3 左右时 Loss 基本不掉，均衡状况继续改善。推理要多存一个 `n × b` 的 State，文中认为 `b = 100` 已经够用；分桶方式目前是 Sigmoid 激活后均匀离散化，更精细的分桶还是开放问题。

## 本体与去向

- 本体：`raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/`
- 图：原文未编号，按正文顺序三张依次为 `raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/assets/moe-huanyouji-8-fig1.png`（直方图近似估计分位数示意图）、`raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/assets/moe-huanyouji-8-fig2.png`（MQB(λ=1) 与 QB、SignSGD 的效果比较）、`raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/assets/moe-huanyouji-8-fig3.png`（不同的 λ 对应的负载均衡情况）
- 精读：[[moe-huanyouji-reading|MoE环游记系列精读]]
- 系列：上一篇 [[moe-huanyouji-7-abstract|MoE环游记：7、动态激活极简解]]；下一篇 [[moe-huanyouji-9-abstract|MoE环游记：9、门控归一化之争]]
