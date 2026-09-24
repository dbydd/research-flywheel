---
title: 大宽度加稀疏支路更新下，受约束混合是否重新有价值
slug: gated-residual-wide-stream-revisit
type: idea
status: seed
origin: gated-residual
test: 在 $n_r=16$ 稠密读写与 $n_r=16$ 每步只更新 4 支两种配置下各加与不加双随机混合矩阵，比较损失、下游与支路份额分布
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
---

# 大宽度加稀疏支路更新下，受约束混合是否重新有价值

[[gated-residual|Gated Residual]] 在 $n_r=4$ 的稠密读写下把支路间混合矩阵删掉，损失与下游双胜带约束混合的动态 mHC，支路分解显示网络自己学出「一支长程、三支局部」的分工（见 [[wide-residual-stream|加宽残差流]]）。混合矩阵原本要防的支路趋同与容量闲置，在这个宽度上没有出现。

开口落在宽度上。支路一多、每步写者一稀疏，支路饿死这类模式才可能出现。xHC 的稀疏支路更新走的是大 $n_r$ 路线（16 支更新 4 支），报告点名后以内存开销为由不跟进。这条猜想要验的东西是：支路数推到 16 上下、写侧只更新少数支时，双随机约束的混合矩阵是否从「无增益」翻成「有增益」。

可行的验证把四个格子并排：$n_r=16$ 稠密读写加与不加混合矩阵、$n_r=16$ 每步更新 4 支加与不加混合矩阵。读数除了损失与下游，还要看支路份额分布是否出现饿死（份额长期贴零的支路条数）。这条想法在 Qwen 这条线上的先验低：报告的轨迹方向是去约束（删混合、删特殊初始化、稳定性押在有界门上），回归的形态更可能是大宽度加稀疏更新，回到 mHC 式双随机约束的概率排在它后面。
