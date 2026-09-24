---
title: 序列级均衡强度逐层自适应
slug: layer-wise-routing-strength
type: idea
status: seed
origin: moe-huanyouji-reading
test: 按层设置 λ，对照常数 λ 看每层 MaxVio 与 Loss
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/moe-huanyouji-8.extracted.md
---

# 序列级均衡强度逐层自适应

## 缺口从哪来

Moving Quantile Balancing 把序列级均衡的强度收在一个全局常数 λ 上：把该 token 的分位数阈值 β 乘以 λ，λ 越小，序列内部各专家被用得越不均匀，语言模型损失受到的扰动越小；λ 取 1 时均衡接近完美，代价是 Loss 差 0.06，λ 调到 0.3 左右时 Loss 基本不掉，均衡仍在改善。序列级均衡指在单条序列内部统计各专家被选中的次数，管的是同一条序列里各专家被用得是否均匀；token 是模型处理文本的最小单位，通常是一小段词或子词；分位数阈值指从打分分布里按 1 − k/n 这个累积比例读出的那个值，k 是每个 token 激活的专家数，n 是专家总数。MQB 的完整机制见 [[moving-quantile-balancing|Moving Quantile Balancing：序列级均衡]]。

这个 λ 对全部层取同一个值。负载最难均衡的层恰好在前几层，第一层 MoE 是其中的极端例子，系列把均衡演示集中在这一层；用 Quantile Balancing（QB）训练全 MoE 模型时第一层也会变得均衡，对原本用符号更新（用符号代替梯度做下降）就能均衡的层，QB 通常没有优势（QB 的推导见 [[quantile-balancing|Quantile Balancing：对偶解与分位数]]，这个读数的定义见 [[maxvio|MaxVio：负载偏差的度量]]）。

## 为什么值得做

均衡手段的收益在层间分布不均：第一层的负载最难均衡，序列级均衡在这里拿到的收益最大；对原本已经能均衡的层，额外的均衡手段收益有限，付出的是同一份 Loss 代价。MaxVio 指各专家负载相对均匀目标的最大偏差，是这条路线衡量均衡程度的指标，这个读数在第一层最能看出差别。把 λ 逐层设置，等于把这份强度预算按层的需要分配，目标是在第一层把 MaxVio 压到低位，同时让总 Loss 代价低于常数 λ 取 1 时的 0.06。

逐层自适应的另一个直接收获是参数账：一份逐层 λ 表本身就是一个可复用的结论，它说明各层各自需要多强的序列级约束，同一份表在结构相近的模型之间可以迁移比较。

## 第一步

按层设置 λ，对照常数 λ 看每层 MaxVio 与 Loss。具体做法：取 Moving Quantile Balancing 现有的实现与约 3B、128 选 4 的实验配置，滑动平均系数 0.99、分桶数 100 保持不动；跑三组对照，第一组 λ 全层取 1，第二组 λ 全层取 0.3，第三组前几层取 1、其余层取 0.3；每组记录逐层的 MaxVio 曲线与 Loss。判据是第三组能在 Loss 接近第二组的同时，把第一层的 MaxVio 压到接近第一组的水平。
