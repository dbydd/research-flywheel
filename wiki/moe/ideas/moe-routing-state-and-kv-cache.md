---
title: 路由 State 与滑窗注意力 KV cache 合并管理
slug: moe-routing-state-and-kv-cache
type: idea
status: seed
origin: moe-huanyouji-reading
test: 给出合并后的单次前向更新式，测内存与吞吐
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/moe-huanyouji-8.extracted.md
---

# 路由 State 与滑窗注意力 KV cache 合并管理

## 缺口从哪来

Moving Quantile Balancing 在推理阶段多出一样东西：一个 n×b 的 State。n 是专家数，b 是分桶数，把 [0,1] 等分成 b 个桶，b 取 100 已经够用。这个 State 存的是沿序列做指数滑动平均得到的分数分布估计，指数滑动平均的更新式是新值 = 系数 × 旧值 +（1 − 系数）× 当前值；每个解码步用当前 token 的 Router 分数更新一次，再由累积概率读出该 token 的分位数阈值 β。Router 是从输入预测每个专家模长的小模型；token 是模型处理文本的最小单位，通常是一小段词或子词。分位数阈值指把样本按大小排序后按累积比例取的位置，β 就是落在 1 − k/n 这个累积比例上的那个值。这份状态的来路见 [[moving-quantile-balancing|Moving Quantile Balancing：序列级均衡]]。

自回归解码（一个 token 一个 token 依次生成）还有另一份沿序列累积的状态：KV cache。它是每个位置的注意力键与值，缓存下来供后续步复用，省掉对整条序列的重算；滑窗注意力指每个位置只关注最近一段窗口内的位置。两份状态都在每个解码步增长或更新，都按序列位置顺序推进；系列精读的分析一节由此提出把它们合并考虑，作为一条延伸方向，这一节的出处见 [[moe-huanyouji-reading|MoE环游记 系列精读]]。

## 为什么值得做

两份状态住在同一块推理缓存里，各自占用一份读写带宽，各自的更新各遍历一次缓存结构。合并的价值在于让一个解码步内的缓存访问合并成一次，同时让显存预算有一个统一的账，省掉两份结构各自的对齐与填充开销。n×b 这一份的规模随专家数增长，在专家数上千的配置里它占的份额上升，统一记账的收益跟着上升。

收益可以直接量化：峰值显存与每 token 吞吐，两个数在合并不合并之间对照即可得出一份差，这份差随 b 与专家数的变化就是这条路的适用边界。

## 第一步

给出合并后的单次前向更新式，测内存与吞吐。具体做法：先写出一个解码步里两份状态更新各自依赖的输入——State 的更新依赖当前 token 的 Router 分数与指数滑动平均系数，KV cache 的追加依赖当前 token 的注意力键与值；再把这一个解码步里的两次缓存遍历写成一遍遍历的更新式，两份状态共用一次读写；然后在同一份实现下测峰值显存与每 token 吞吐，对照分开管理的版本，并扫一遍 b 取 100 附近与专家数取现有配置附近的取值，看收益随规模的变化方向。
