---
title: Loss-Free 负载均衡：偏置与符号更新
slug: loss-free-balancing
type: concept
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3/moe-huanyouji-3.extracted.md
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/moe-huanyouji-6.extracted.md
  - papers/readings/2026-07/cs.CL/arXiv/kimi-k3-reading.md
  - raw/2026-07/cs.CL/arXiv/kimi-k3/kimi-k3.extracted.md
---

# Loss-Free 负载均衡：偏置与符号更新

Loss-Free 指不加额外的辅助损失项，靠改变分配方式本身实现负载均衡。方案出在 DeepSeek 的《Auxiliary-Loss-Free Load Balancing Strategy for Mixture-of-Experts》（arXiv:2408.15664）。

## 做法

保留 Router 的打分结果 `ρ`，给每个 Expert 配一个输入无关的偏置 `b`，用 `argtop_k(ρ + b)` 选专家。`ρ` 是 Router 对专家模长的预测，`b` 只随专家变化、与当前 token 无关；`argtop_k` 指取 `ρ + b` 的前 k 个分量对应的专家编号。

选完之后，乘到专家输出上的仍是 `ρ_i`，偏置只参与挑选，不进入加权求和。`b` 没有梯度，由一条手工更新规则维护，训练结束后固定；推理阶段照同一式子算，训练与推理同形。负载不均衡的两类浪费见[[load-balancing-problem|负载不均衡的两类浪费]]。

## 更新规则的来路

第三篇沿用直通估计的一般配方，把 `b` 的更新规则从辅助损失的视角推了出来，见[[straight-through-estimator|直通估计与 F 换 P 的配方]]。结果是

`b ← b − γ·sign(F − Q)`

`F` 是当前负载分布，`Q` 是目标负载分布，均匀目标下每个分量取 `1/n`；`sign` 取符号，把偏差压成 +1 或 −1；`γ` 是步长，默认取 0.001。这种用符号代替梯度的更新叫 SignSGD（符号梯度下降）。它与原论文取用的符号梯度下降一致，两条路线的梯度同源。

## 两处改良

用 RMS Norm 替代 `sign`：把向量除以其各分量平方均值的平方根，保留偏差的相对大小，减少已经接近均衡的专家来回震荡。

把打分的激活拆成两路：加偏置的那一路用 Sigmoid，乘到专家上的门控用别的单调非负激活。由此可以继续复用原论文的 `γ = 0.001`，这个默认步长与 Sigmoid 激活绑定，换激活函数需要重调。

## 冗余自由度

全体 `b` 分量同加一个常数，不改变 `ρ + b` 的排序，`argtop_k` 的结果因此不变。这条冗余自由度留到第四篇被用上，见[[dynamic-activation|动态激活：按难度浮动激活数]]。

## 本质判断

均衡只优化新引入的 `b`，语言模型损失优化其余参数，两边的优化参数被隔离开。方法的要点落在「一个偏置项足以达到负载均衡」这个结论上。

## 局限

`γ` 要调，且与激活函数绑定。偏置在全局共享，方案只能做全局均衡。恒定步长在分布畸形的层上很难实现均衡，模型前几层用 MoE 时不均衡尤其常见；后续的分位数路线把步长与阈值都换成由数据算出的量，见[[quantile-balancing|Quantile Balancing：对偶解与分位数]]。

Kimi K2 用的就是这条符号梯度更新。专家总数涨到 896 之后它不够稳，Kimi K3 换成 [[quantile-balancing|Quantile Balancing]]。报告把两者接在同一个对偶目标上：专家侧子问题的次梯度正好是目标负载减实际负载，SignSGD 一步只保留这个负载误差的方向，QB 直接跳到同一对偶目标上的精确坐标极小点。这条连续性在博客作者的判据里也出现过，见 [[quantile-histogram-estimation|分位数均衡的直方图估计]]。

出处：系列第三篇[[moe-huanyouji-3-abstract|MoE环游记：3、换个思路来分配 摘要]]；局限一节关于分布畸形层的判断另见第六篇[[moe-huanyouji-6-abstract|MoE环游记：6、最优分配促均衡 摘要]]。
