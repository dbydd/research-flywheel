---
title: 在稍大模型上复现 QB 与 MQB 的均衡收益
slug: reproduce-qb-mqb-at-scale
type: idea
status: seed
origin: moe-huanyouji-reading
test: 在更大一档的模型上跑 QB 与 MQB，看均衡收益是否随规模保持
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/moe-huanyouji-6.extracted.md
  - raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/moe-huanyouji-8.extracted.md
---

# 在稍大模型上复现 QB 与 MQB 的均衡收益

## 缺口从哪来

全系列的实验规模偏小：除 DeepSeek 官方配置数字外，关键数字多来自作者自测的约 3B 一档的模型，系列没有在大规模训练上复现 QB 与 MQB 的公开结果。QB 指 Quantile Balancing，把负载均衡解成分位数阈值；MQB 指 Moving Quantile Balancing，把同一套阈值推到序列级。五代方案的对照见 [[load-balancing-methods-comparison|负载均衡各代方案对照]]。

已经跑出来的数字集中在小档，读数都取自负载最难均衡的第一层的 MaxVio，也就是各专家负载相对均匀目标的最大偏差。QB 训练时第一层 MoE 的 MaxVio 全程稳定在 0.6 至 0.7；同组的符号更新版 Loss-Free 在五千步附近升到 2 左右，带大量尖峰升到 4，一万步后回落到 1 附近。MQB 的实验配置是约 3B、128 选 4，滑动平均系数 0.99、分桶数 100；λ 取 1 时第一层 MaxVio 全程在 0.2 以下，只做全局均衡的 QB 落在 0.7 至 0.9，符号更新版 Loss-Free（用符号代替梯度做下降）在一万步前维持在 1.5 至 2，代价是 Loss 差 0.06（两个方案的推导见 [[quantile-balancing|Quantile Balancing：对偶解与分位数]] 与 [[moving-quantile-balancing|Moving Quantile Balancing：序列级均衡]]，读数的定义见 [[maxvio|MaxVio：负载偏差的度量]]）。

## 为什么值得做

均衡收益随规模的变化决定这条路线在真实训练里的位置。模型变大时专家数、每层宽度与批内 token 数一起变，token 是模型处理文本的最小单位，小档的三组数字回答不了这一点，需要同构的更大一档配置。一组同构配置上的三档对照能回答两件事：均衡收益是否保持量级，以及 λ 的最优位置是否随规模移动。前者决定方法能不能直接用，后者决定超参数要不要重扫。

这份复现同时给这条路线补一份可公开比对的账。系列给出的关键数字目前都出自一档自测规模，把它抬一档并公开配置与曲线，后来者能在这条线上继续叠加。

## 第一步

在更大一档的模型上跑 QB 与 MQB，看均衡收益是否随规模保持。具体做法：选一档大于 3B 的 MoE，专家数与激活专家数按同一比例放大，k/n 比保持 128 选 4 这一档的水平；以符号更新版 Loss-Free 为基线，跑 QB 与 MQB 两组，MQB 的 λ 取 1 与 0.3 两个点，滑动平均系数 0.99、分桶数 100 不动；同一份数据、同一训练步数下记录第一层 MaxVio 曲线与 Loss，与小档的数字并排看。判据是均衡收益的量级在小档与大一档之间保持，λ 取 0.3 这一档继续维持 Loss 基本不掉的读数。
