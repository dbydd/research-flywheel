---
title: MoE环游记：4、难处应当多投入
slug: moe-huanyouji-4-abstract
type: abstract
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-4/moe-huanyouji-4.extracted.md
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-4/moe-huanyouji-4.html
resource: raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-4
---

# MoE环游记：4、难处应当多投入

> [!quote] 官方摘要
> 前两篇文章我们都在讨论负载均衡，其中在《MoE环游记：3、换个思路来分配》介绍Loss-Free方案时，笔者留了一个悬念：它引入的Bias项有一个冗余的自由度，这个自由度可以用来做另外有趣的事情。这篇文章我们就来讨论这件事。

## 一句话判断

这一篇把上一篇里 `b` 的冗余自由度拿去实现动态激活。`b` 的全体分量加同一个常数不改变排序，所以先把更新规则整体去均值，腾出来的这个自由度用于预算控制；激活规则从 `argtop_k(ρ + b)` 改为 `argwhere(ρ + b > 0)`，每个 token 激活的 Expert 数目随难度浮动，免掉了排序这一步。更新式同时做两件事：把负载分布拉向均匀，把平均激活数推向 `k`；只想保证不超过 `k` 的版本可以去掉一侧的推力。作者还试了化简，把“逼近均匀”与“逼近预算”合并成让 `F̃` 逼近 `k/n`，可以写成一步符号梯度下降，代价是训练前期的均衡度与预算抖动变大，追求稳定就用三段式的版本。其余细节包括：用 RMS Norm 替代 sign 略微更稳；`b` 的初始化可以在 Router logits 近似正态的假设下用二分法估算，文中给了可直接运行的脚本。相关工作一节梳理了 AdaMoE 与 MoE++（混入空白、复制、常数类低成本 Expert，间接实现动态数目）、Top-`p`（平均预算难以准确控制，需要额外熵损失）、Ada-K Routing（另设模块预测激活数，用强化学习训练）、DA-MoE（借 Attention 分数识别重要 token）与 ReMoE（同样基于零阈值，走 Aux Loss 路线）。

## 本体与去向

- 本体：`raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-4/`
- 精读：[[moe-huanyouji-reading|MoE环游记系列精读]]
- 系列：上一篇 [[moe-huanyouji-3-abstract|MoE环游记：3、换个思路来分配]]；下一篇 [[moe-huanyouji-5-abstract|MoE环游记：5、均匀分布的反思]]
