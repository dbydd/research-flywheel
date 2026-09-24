---
title: 加宽残差流：从 AltUp 到 Hyper-Connections 一族
slug: wide-residual-stream
type: concept
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/qwen3.8-flash-next.extracted.md
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
  - papers/context/qwen3.8-flash-next-context.md
---

# 加宽残差流：从 AltUp 到 Hyper-Connections 一族

常规残差连接让每个子层在同一个累加流上做一次加法，深层读到的信号被此前各层的累加稀释。加宽残差流把这条单流换成若干支并行状态，子层从多支读、往多支写。Qwen3.8-Flash-Next 的 [[gated-residual|Gated Residual]] 是这一族里的一个设计点，它前面的家族成员给出了宽度与读写算子的取值空间。

## 宽度本身

隔离宽度收益的对照用一个适配 pre-norm（把归一化放在每个子层输入端、残差主干上不再加归一化层的结构）的简化 AltUp（Alternating Updates 的变体）：$n_r$ 支残差流，每块持 $n_r$ 个可学习标量做加权读，块输出按深度轮转写回单支。

$$
x^{(\ell)}=\sum_{i=1}^{n_r} h_i R_i^{(\ell)},\qquad
R_i^{(\ell+1)}=R_i^{(\ell)}+\mathbf{1}[i=\ell \bmod n_r]\, y^{(\ell)} .
$$

每块只加 $n_r$ 个参数、零矩阵乘，额外代价是携带多支状态的内存流量。在 25B-A3B 上训 400B token 降约 0.01 损失。宽度本身值钱，接下来的问题是在加宽的流上再叠多少读写机器。

## 三个算子

Hyper-Connections（HC）一族把读写推广成三个算子：读算子 $H_{\text{mix}}$ 形成块输入，写算子 $H_{\text{combine}}$ 把块输出分发到各支，混合算子 $H_{\text{res}}$ 在支路之间交换信息。每个算子都是静态项加数据相关项。mHC（DeepSeek 的流形约束版本）把三个算子分别约束为 sigmoid、两倍 sigmoid、Sinkhorn-Knopp 投影到双随机矩阵。双随机矩阵是行列和均为 1 的矩阵流形，谱范数不超过 1、乘法闭合，Sinkhorn-Knopp 的迭代上限取 20 次。

同族方向上，xHC（小红书与上海交通大学的扩展件）在写回侧加多尺度因果卷积与稀疏支路更新，$N=16$ 支里每步只更新 $k=4$ 支；Virtual Width Networks 把隐向量均分 $m$ 段逐段做宽度与深度方向的连接，HC 与 AltUp 是它的简化特例。

## 静态与动态的门控账

读写算子取静态项还是由状态预测，两条消融给出一步被点名的分歧。在 25B-A3B、560B token 上，九项基准同一套管线：

|残差设计|损失|九项均值|
|---|---|---|
|pre-norm 基线|1.617|50.91|
|静态 mHC（只有宽度与静态读写）|1.596|52.49|
|动态 mHC（读写由状态预测）|1.594|54.47|

静态到动态这一步损失只再降 0.002，平均精度涨 1.98 分（基线到静态涨 1.58 分）。损失单独看会低估这步改动的价值，这条分歧是 [[three-axis-architecture-eval-protocol|三轴评估协议]] 的实例。读写足够有表达力之后，$n_r\times n_r$ 的混合算子带来不了显著提升，这条读数直接指向 [[gated-residual|Gated Residual]] 把混合矩阵删掉的取法。
