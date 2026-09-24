---
title: 稀疏路由的替代路线
slug: sparse-routing-alternatives
type: concept
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-4/moe-huanyouji-4.extracted.md
---

# 稀疏路由的替代路线

动态激活把「每个 token 激活几个专家」从固定 k 改成逐 token 浮动，见[[dynamic-activation|动态激活：按难度浮动激活数]]。同一题下另有一批做法，各自用不同的信号决定激活数量或激活名单。本页逐个交代它们的机制与代价。token 是模型处理文本的最小单位，专家指 MLP 层切分后的并行小网络。

## 在专家池里混入零计算专家

AdaMoE 与 MoE++ 在专家中混入空白或零计算专家。挑选规则保持不变，被选中的专家里有一部分不产生计算，实际消耗的算力因此减少，平均激活数间接下降。

## 按累计打分取阈值

Top-p 把 Top-k 换成另一种取法：按打分从高到低累计，累到概率和达到 p 为止，把落在其中的专家全部选中。它的问题在于难以准确控制平均预算，每个 token 实际选中的专家数随打分分布波动。

## 单独预测激活数

Ada-K Routing 另设一个模块预测每个 token 的激活数，用强化学习训练这个预测。强化学习指按奖励信号调整策略的训练方式，这里的奖励与后续的语言模型损失挂钩。

## 借用注意力分数

DA-MoE 借 Attention 分数识别重要 token。Attention 是 Transformer 里让每个位置按相关度加权聚合其它位置的层，它的分数刻画了各位置的重要程度，DA-MoE 用它决定哪些 token 值得多配专家。

## 零阈值加辅助损失

ReMoE 同样基于零阈值，走辅助损失路线：打分加阈值后大于零的专家被激活，阈值的更新交给辅助损失，见[[auxiliary-loss|Aux Loss 与 F·P 的来路]]。

## 与动态激活的分工

动态激活一支关心的是激活数随难度浮动，同时把平均激活数压回预算 k；上面这些做法分别在挑选规则、激活数预测、重要性识别与阈值来源上给出替代。分歧点落在「激活数由谁决定」：由打分阈值决定的做法免掉排序，由额外模块决定的做法把这件事交给一个专门的预测器。

出处：系列第四篇[[moe-huanyouji-4-abstract|MoE环游记：4、难处应当多投入 摘要]]，本页清单取自该篇对动态激活一支的梳理。
