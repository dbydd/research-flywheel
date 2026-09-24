---
title: KDA 的算法与系统协同
slug: kda-system-codesign
type: concept
created: 2026-09-22
updated: 2026-09-22
sources:
  - papers/readings/2026-07/cs.CL/arXiv/kimi-k3-reading.md
  - raw/2026-07/cs.CL/arXiv/kimi-k3/kimi-k3.extracted.md
---

# KDA 的算法与系统协同

KDA（Kimi Delta Attention，Kimi 增量注意力）用固定大小的循环状态替换随序列长度增长的 KV 缓存（键值缓存，生成时避免重算历史注意力而存下的中间量），长序列的混合成本不再随长度增长。状态的更新逐步串行，GPU 偏好宽而均匀的并行，两者冲突，冲突在训练、前填充与跨设备三种执行场景里表现为三种不同的瓶颈。《Kimi K3》技术报告为这三种场景各配了一套内核与并行方案。算法侧见 [[kimi-delta-attention|Kimi Delta Attention]]。

## 训练与前填充：FlashKDA

KDA 的分块形式块内并行、块间串行。朴素执行时两段交替，块间串行的那一段让 SM（显卡上的计算单元）空转。FlashKDA 是基于 CUTLASS（一个显卡矩阵乘模板库）的分块 GPU 内核（kernel，在显卡上执行的一段函数），把块内计算与跨块状态传播重叠起来，把工作拆成 token 并行阶段与 head 并行递归，两个阶段各自调度调优。它的性能明显好过 Triton 参考实现，并作为 flash-linear-attention 的后端自动派发。

## 单机长上下文前填充：SM 级上下文并行

张量并行（把同一层的矩阵按头或通道切开放到不同设备上）按头切分，递归长度从不因此缩短。在只持有少数头的 rank 上做超长序列前填充，多数 SM 处于空闲。关键观察是每段的状态转移可以独立于入态求值，求完之后精确复合。规划器因此把序列分到单机的各 SM 上并行求段转移，再合并结果，恢复每段的精确初始状态，整个过程在设备内完成，没有跨设备通信。这套切分由规划器自动完成。

## 跨设备：KDA 上下文并行

软最大化注意力要求在 rank 之间交换随序列长度增长的键值块；线性注意力把前文装进固定大小的循环状态里。既有方法利用可加递归，在各 rank 上从零态求本地状态，再在之前的 rank 上求和恢复入态。直接求和对 KDA 不够用：delta 规则先用一个 token 相关的矩阵

$$
\mathbf{M}_t=(\mathbf{I}-\beta_t\boldsymbol{k}_t\boldsymbol{k}_t^{\top})\operatorname{Diag}(\boldsymbol{\alpha}_t)
$$

作用在入态上，再加上当前的写入，本地序列段的效应依赖进入该段的状态。

KDA 上下文并行（KCP）把每段的效应分解成两个本地可算的量：一个作用在入态上的累积转移，一个从零态本地生成的状态。rank 级的更新可以结合地复合，每段的入态由一个前缀扫描恢复。每个 rank 本地算累积转移与零态状态，两者各用一次 all-gather（各副本把自己持有的那片发给所有副本）交换；之后 rank i+1 按顺序处理前序片段，重建自己的入态。KCP 的状态同步只需要一次固定大小的 all-gather，计算随规模线性扩展。

循环状态在服务侧的落点见 [[prefix-cache-two-level|前缀缓存两级粒度]]，那里把状态检查点放进与 MLA KV 缓存同一个分页块池。训练时的并行组合见 [[trillion-scale-parallelism|三万亿级预训练并行]]。
