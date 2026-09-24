---
title: 注意力残差：把残差搬进深度方向
slug: attention-residuals
type: concept
created: 2026-09-22
updated: 2026-09-22
sources:
  - papers/readings/2026-07/cs.CL/arXiv/kimi-k3-reading.md
  - raw/2026-07/cs.CL/arXiv/kimi-k3/kimi-k3.extracted.md
---

# 注意力残差：把残差搬进深度方向

常规残差连接把之前所有层的信息压进一个状态，每层在这个状态上做一次累加。报告说这在深度方向上像一个随时间递归的循环网络，构成瓶颈：早层写进去的信息要穿过此后每一层的变换才能到达末层。注意力残差（Attention Residuals，AttnRes）是 Kimi K3 三轴信息流里深度方向那一件（见 [[information-flow-three-axes|三轴信息流]]），做法是把注意力机制搬到深度上。

## 深度方向上的注意力

每层有一个可学的伪查询 $\boldsymbol{w}_l$，键与值取嵌入与各前序层的输出，注意力权重用核 $\phi(\boldsymbol{q},\boldsymbol{k})=\exp(\boldsymbol{q}^{\top}\operatorname{RMSNorm}(\boldsymbol{k}))$ 计算，本层输出是这些表示的加权和。RMSNorm 用均方根做归一化，把向量缩放成单位尺度。核里套 RMSNorm 是为了让输出幅度大的层不会独自支配权重。读取集合因此由学习到的查询决定，深层可以直接挑早层的表示，逐层累加这条约束被松开。

## 整版与块版

整版形式对全部前序层取键与值，算术量是层数的平方乘隐维。层数不到一百时这个开销可接受，实际代价是 $O(Ld)$ 的显存与流水线并行（把不同层段放到不同设备上、按流水线喂微批）下的跨级通信，因为要保活所有层的输出（见 [[trillion-scale-parallelism|三万亿级预训练并行]]）。

块版把 L 层分成 N 个块、每块 S 层。块内各层输出先求和成一个块表示，块与块之间只对这 N 个块表示做全注意力；块的第一个层用前面所有块作值，块内后续层额外带上本块的部分和；最后一层聚合全部 N 个块表示。显存与通信从 $O(Ld)$ 降到 $O(Nd)$。块结构还界定了推理时的状态规模，块间可并行而块内按顺序累加，块间的并行结果与块内顺序部分和可以用在线软最大化（流式维护最大值的累加技巧）合并。

## K3 的取法

经验上 N 取 8 上下能收回大部分收益。K3 把层分成 8 个块、每块 12 层，每 12 层里排三组「3 层 KDA 加 1 层 Gated MLA」，8 块共 24 层 Gated MLA（KDA 见 [[kimi-delta-attention|Kimi Delta Attention]]，全局注意力层见 [[gated-mla|Gated MLA]]）。加上嵌入层一共 9 个块，末块不满。
