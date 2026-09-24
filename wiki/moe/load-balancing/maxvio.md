---
title: MaxVio：负载偏差的度量
slug: maxvio
type: concept
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/moe-huanyouji-6.extracted.md
---

# MaxVio：负载偏差的度量

MaxVio 指各专家负载相对均匀目标的最大偏差，是分位数这条路线衡量均衡程度的指标。专家是 MoE 层里的并行小网络，MoE 让每个 token 只走其中 k 个，token 是模型处理文本的最小单位（见 [[moe-layer]]）。负载指某个专家在一批 token 里被选中的次数或占比，均匀目标指每个专家被激活的比例都是 k/n。分配不均可造成过量丢弃 token 与长期闲置的专家两类浪费，负载分布与这两类浪费见 [[load-balancing-problem]]。

第一层 MoE 是负载最难均衡的一层，演示因此集中在这一层。

## 第六篇的读数

SignSGD 版 Loss-Free 的 MaxVio 在五千步附近升到 2 左右，带大量尖峰升到 4，一万步后回落到 1 附近。SignSGD 版 Loss-Free 指用符号做梯度下降来更新偏置的方案，更新式是 `b ← b − γ·sign(F − Q)`，其中 F 是当前负载分布、Q 是目标负载分布、γ 是步长（来路见 [[loss-free-balancing]]）。

QB（Quantile Balancing，从对偶解里读出的分位数偏置）全程稳定在 0.6 至 0.7，推导见 [[quantile-balancing]]。

作者据此说 QB 尤其擅长处理极端例子。用 QB 训练一个全 MoE 模型时第一层也会变得均衡；对原本 SignSGD 就能均衡的层，QB 通常没有优势。

![[raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/assets/moe-huanyouji-6-fig1.png]]

图：第一层 MoE 的 MaxVio 随训练步数变化，横轴到 1.5 万步，纵轴 0 到 4。图取自《MoE环游记：6、最优分配促均衡》。

## 读数条件

MaxVio 的数值随层的位置变化，最不均衡的层落在最前面。恒定步长在分布畸形的层上很难实现均衡，模型前几层用 MoE 时不均衡尤其常见。

同一度量在序列级方案上的读数（λ 取 1 时第一层压在 0.2 以下，λ 取 0.3 时仍明显低于只做全局均衡的 QB）见 [[moving-quantile-balancing]]；各代方案在同一度量下的对照见 [[load-balancing-methods-comparison]]。

## 规模边界

关键数字多来自作者自测的小模型，实验规模在约 3B 参数一档，系列没有在大规模训练上复现 QB 与 MQB 的公开结果。

第六篇的原始论述见 [[moe-huanyouji-6-abstract|MoE环游记：6、最优分配促均衡 摘要]]，系列全景见 [[moe-huanyouji-reading|MoE环游记 系列精读]]。
