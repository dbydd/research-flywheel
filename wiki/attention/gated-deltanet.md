---
title: Gated DeltaNet：带全局衰减与增量规则的循环注意力
slug: gated-deltanet
type: concept
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/qwen3.8-flash-next.extracted.md
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/hf_config.json
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
---

# Gated DeltaNet：带全局衰减与增量规则的循环注意力

Kimi Delta Attention 一族（见 [[kimi-delta-attention|Kimi Delta Attention]]）与 Gated DeltaNet 同属 delta 规则线性注意力：每个位置只保留一个固定大小的循环状态，历史信息压进状态，逐位置的更新按预测误差写入。Gated DeltaNet（下称 GDN）是 Qwen3.8-Flash-Next 循环侧采用的件，也是 [[hybrid-attention-layer-ratio|混合注意力层间配比]] 里承担历史压缩的那一层。

## 状态递推

看单个注意力头。第 $t$ 个位置有查询 $q_t$、键 $k_t$（都在 $\mathbb{R}^{d_k}$ 里）、值 $v_t\in\mathbb{R}^{d_v}$ 与状态 $S_t\in\mathbb{R}^{d_k\times d_v}$。约定写出：

$$
\widetilde{S}_{t-1}=\alpha_t S_{t-1},\qquad
e_t=v_t-\widetilde{S}_{t-1}^{\top}k_t,\qquad
S_t=\widetilde{S}_{t-1}+\beta_t k_t e_t^{\top},\qquad
y_t=S_t^{\top}q_t,
$$

合并成

$$
S_t=\alpha_t\left(I-\beta_t k_t k_t^{\top}\right)S_{t-1}+\beta_t k_t v_t^{\top}.
$$

衰减 $\alpha_t\in(0,1)$ 是每一步的保留因子，全局控制旧状态的寿命。delta 项先估计当前键 $k_t$ 已经关联的值，只把残差 $e_t$ 写回去，重复或相近的键因此更新既有关联、积累不起无界的外积。这一份状态几何沿用原论文约定的转置。

## 参数化

查询与键走短因果卷积（对相邻若干位置做一维卷积，混合局部上下文）加 SiLU 激活，再接 L2 归一化；L2 归一化把 q/k 幅度封住，稳住秩一 delta 转移。值走卷积加 SiLU。写入强度与衰减由输入投影给出：

$$
\beta_t=\sigma(W_\beta x_t),\qquad
\alpha_t=\exp\left[-\exp(A)\,\mathrm{softplus}(W_\alpha x_t+b_\alpha)\right],
$$

头输出由输出门调制：

$$
o_t=W_o\left[\sigma(W_z x_t)\odot \mathrm{RMSNorm}(y_t)\right].
$$

输出门取有界 sigmoid 形式，归一化取 [[gated-normalization|零中心 RMSNorm]]。

## 两处带账的改动

输出门是相对原论文的一处改动。原论文用 SiLU 门，本件换成有界 sigmoid 门，并在全部实验里观察到一致提升；原论文自己的消融表里去掉输出门把困惑度从 27.35 推到 29.12，输出门在原始配方里就是承重件。归一化沿用 Qwen3-Next 的零中心 RMSNorm，全模型所有 RMSNorm 统一此式。

## 发布件对账

权重仓库 `config.json` 记 GDN 线性注意力的 V 头 48、QK 头 16、head_dim 128、短卷积核 4（`linear_conv_kernel_dim=4`）。同族的门控粒度对照：Kimi K3 的循环侧用逐通道衰减门，本件用每头一个标量衰减，两处的机制差异记在 [[kimi-delta-attention|Kimi Delta Attention]]。

![[raw/2026-09/llm-architecture/github/qwen3.8-flash-next/assets/qwen3.8-flash-next-fig2-gdn.png]]

> **GDN token mixer 结构图**（技术报告 Figure 2）q/k 走短卷积、SiLU 与 L2 归一化，v 走卷积与 SiLU，状态递推由衰减与写入强度驱动，头输出经归一化与有界门调制。
