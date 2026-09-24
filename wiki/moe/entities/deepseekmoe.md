---
title: DeepSeekMoE 与 DeepSeek 路线
slug: deepseekmoe
type: entity
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3/moe-huanyouji-3.extracted.md
  - raw/2025-05/moe/spaces-ac-cn/moe-huanyouji-5/moe-huanyouji-5.extracted.md
  - raw/2026-06/moe/spaces-ac-cn/moe-huanyouji-9/moe-huanyouji-9.extracted.md
---

# DeepSeekMoE 与 DeepSeek 路线

DeepSeekMoE 出自论文《DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models》（arXiv:2401.06066）。MoE（Mixture of Experts，混合专家）把 Transformer 里的 MLP 层（全连接前馈层）换成若干并行的小网络，每个 token 只走其中几个；token 是模型处理文本的最小单位，通常是一小段词或子词；每个小网络称为一个 Expert。DeepSeek 是提出这套架构的团队与其模型系列，系列里的两份官方配置 DeepSeek-V2 与 DeepSeek-V3 都采用它。

在这条技术线上，DeepSeek 的贡献分三块：架构侧的共享专家与细颗粒度专家，训练侧的 Loss-Free 负载均衡，以及配合 Loss-Free 的 Sigmoid 门控。

## 架构侧的两件改进

共享专家把「n 选 k」改成「n 减 s 选 k 减 s」，另有 s 个专家必然被选中，总专家数与每次激活的专家数不变，参数量与推理成本不变。它把专家之间的共性显式承担下来，让 Routed 侧专心学习残差；这一安排同时让目标负载分布自身不均匀，构成均匀分布最优性的一个具体反例，这条改进的机制与代价记在 [[shared-expert|共享专家与比例因子]]。

细颗粒度专家把每个专家缩小一半、改成 2n 选 2k，总参数与激活参数都不变，可选组合数从 C(n,k) 增到 C(2n,2k)。它用更多、更细的专家覆盖现实世界的非均匀性，代价是专家数越大负载越不均衡、通信与协调成本上升，颗粒度的取舍记在 [[expert-granularity|细颗粒度专家]]。

## 训练侧：Loss-Free 与 Sigmoid 门控

Router 是从输入预测每个专家模长的小模型，ρ 指专家输出的模长分量，也就是输出向量的长度。Loss-Free 负载均衡保留 Router 的打分结果，把分配方式改掉：给每个 Expert 配一个输入无关的偏置 b，用 `argtop_k(ρ + b)` 选专家，乘到专家上的仍是 ρ_i。偏置 b 没有梯度、在训练结束后固定、训练与推理同形，均衡因此只优化这一组新参数，偏置更新规则的来路记在 [[loss-free-balancing|Loss-Free 负载均衡：偏置与符号更新]]。

DeepSeek 为配合 Loss-Free 把门控的激活函数改成 Sigmoid，并用在 DeepSeek-V3 上。门控指乘到专家输出上的那个权重，它在训练时为 Router 提供梯度；Sigmoid 的输出落在 0 与 1 之间，门控归一化的三选一记在 [[gating-normalization|门控归一化的三选一]]。

## 官方配置数字

两份官方 config.json 里的路由缩放因子分别取 16.0（DeepSeek-V2）与 2.5（DeepSeek-V3）。比例因子用来让 Routed 侧权重与共享侧无权相加在初始化阶段模长接近一致，用数值模拟估计同一份配置得到约 16 与约 2.83，两组对照见 [[scaling-factor-across-configs]]。

系列调用比例因子脚本时把共享专家计入专家总数：DeepSeek-V2 记 n = 162、k = 8、s = 2，DeepSeek-V3 记 n = 257、k = 9、s = 1。

## 系列对它的定位

《MoE环游记》把这几件方法接到一条几何与优化的主线上：从 MoE 层的几何分解出发，把「选哪些专家」写成等式约束下的优化问题，再把最优解写成偏置的分位数，也就是把打分按大小排序后按累积比例取出的那个阈值。这条主线上系列给出自己的两个解，Quantile Balancing 处理全局均衡（推导见 [[quantile-balancing|Quantile Balancing：对偶解与分位数]]），Moving Quantile Balancing 把均衡推到序列级（机制见 [[moving-quantile-balancing|Moving Quantile Balancing：序列级均衡]]）。系列全景见 [[moe-huanyouji-reading|MoE环游记 系列精读]]。
