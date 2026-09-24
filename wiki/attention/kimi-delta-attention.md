---
title: Kimi Delta Attention：增量规则与逐通道遗忘门
slug: kimi-delta-attention
type: concept
created: 2026-09-22
updated: 2026-09-22
sources:
  - papers/readings/2026-07/cs.CL/arXiv/kimi-k3-reading.md
  - raw/2026-07/cs.CL/arXiv/kimi-k3/kimi-k3.extracted.md
---

# Kimi Delta Attention：增量规则与逐通道遗忘门

注意力机制里每个位置有一组查询向量、键向量与值向量：查询是当前位置发出的提问，键是各历史位置的索引，值是各历史位置携带的内容。注意力输出用查询与各键的相似度给各值加权求和，权重归一化到总和为一。线性注意力把这件事改成每个位置只保留一个固定大小的循环状态，历史信息压进这个状态，长序列的混合成本因此不随长度增长。

KDA（Kimi Delta Attention，Kimi 增量注意力）把 delta 规则扩展出一个逐通道遗忘门。delta 规则指让记忆状态按预测误差写入的线性注意力规则：先让当前状态对当前值做一次预测，再按这份预测的误差更新状态。

## 状态更新

看单个注意力头。第 t 个位置有查询向量 $\boldsymbol{q}_t$、键向量 $\boldsymbol{k}_t$（都在 $\mathbb{R}^{d_k}$ 里）、值向量 $\boldsymbol{v}_t\in\mathbb{R}^{d_v}$ 与循环状态 $\mathbf{S}_t\in\mathbb{R}^{d_k\times d_v}$。状态按

$$
\mathbf{S}_t=\left(\mathbf{I}-\beta_t\boldsymbol{k}_t\boldsymbol{k}_t^{\top}\right)\operatorname{Diag}(\boldsymbol{\alpha}_t)\mathbf{S}_{t-1}+\beta_t\boldsymbol{k}_t\boldsymbol{v}_t^{\top},\qquad \tilde{\boldsymbol{o}}_t=\mathbf{S}_t^{\top}\boldsymbol{q}_t
$$

更新，输出由状态与查询的内积给出。这里 $\boldsymbol{\alpha}_t\in(0,1)^{d_k}$ 是每通道的一步保留因子，$\beta_t\in(0,1)$ 是写入强度。$\operatorname{Diag}(\boldsymbol{\alpha}_t)$ 先把历史状态按通道衰减；衰减后的状态乘上当前键，就是它对当前值的预测；$\mathbf{I}-\beta_t\boldsymbol{k}_t\boldsymbol{k}_t^{\top}$ 再按当前键方向减掉这份预测；后面的写入项补上真实值。这份动作把记忆写成对值的预测、把误差补进去，是 delta 规则的形状；逐通道的 $\boldsymbol{\alpha}_t$ 是相对 delta 规则多出来的那层遗忘门。

## 参数化

参数化沿用前作 Kimi Linear（arXiv 2510.26692）。查询与键走线性投影，接短卷积（对相邻若干位置做一维卷积，混合局部上下文），接 Swish 激活，再接 L2 归一化。值走短卷积与 Swish。写强度由 Sigmoid 给出。衰减用一个低秩投影加每头偏置产生的衰减对数 $\boldsymbol{z}_t$ 表示。

## 分块并行

训练与前填充按分块形式并行：块内并行，块间串行。块大小记 C，通道累积衰减 $\boldsymbol{\gamma}$ 是块内保留因子的连乘。一个变换把值矩阵折成伪值项，前作称它为 UT 变换；块输出写成两项之和，一项是块间状态通过累积衰减带进来的信息，另一项是块内类似注意力的交互。

分块形式要用累积衰减的倒数去缩放键，这份倒数的数值范围是一处工程关口，处置见 [[bounded-decay-gating|下界衰减]]。

## 在 K3 里的位置

K3 的注意力层按三层 KDA 加一层 [[gated-mla|Gated MLA]] 的配比排布，93 层因此拆成 69 层 KDA 与 24 层 MLA。KDA 承担位置敏感、近因感知的序列混合，MLA 层因此走 [[nope-position-encoding|NoPE]]。KDA 的输出门是输入相关的满秩形式，见 [[full-rank-output-gate|满秩输出门]]。固定大小的循环状态与显卡偏好的宽而均匀的并行相冲突，K3 在算法与系统两侧各做了配套，见 [[kda-system-codesign|KDA 的算法与系统协同]]。这一层改动的坐标是 [[information-flow-three-axes|三轴信息流]] 里的序列轴。
