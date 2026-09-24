---
title: 位置编码取舍的证据轴：RoPE 与 NoPE 在混合架构上的两种结局
slug: rope-vs-nope-evidence-axes
type: comparison
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/qwen3.8-flash-next.extracted.md
  - raw/2026-07/cs.CL/arXiv/kimi-k3/kimi-k3.extracted.md
  - wiki/attention/nope-position-encoding.md
---

# 位置编码取舍的证据轴：RoPE 与 NoPE 在混合架构上的两种结局

旋转位置编码（RoPE）把查询与键按位置角度旋转，使内积带上相对距离；NoPE 指注意力层不加任何显式位置编码。混合注意力架构把循环层与全注意力层混排（见 [[hybrid-attention-layer-ratio|混合注意力的层间配比]]），位置信息由哪一类层承担成为一处独立决定。Kimi K3 与 Qwen3.8-Flash-Next 在同一个预训练读数上分道，分歧落在评估轴。

## 同一个预训练零读数

两件都在预训练阶段观察到 RoPE 与 NoPE 看不出差别。K3 可以把 RoPE 加回 [[gated-mla|Gated MLA]] 层，加上之后效果看不出变化。Qwen3.8-Flash-Next 的全注意力层保留 RoPE，其 NoPE 变体在预训练指标上同样量不出差别。这一步两家的读数同型。

## 两家的取法

Kimi K3 的 MLA 层全部走 [[nope-position-encoding|NoPE]]，位置敏感与近因感知的序列混合交给 [[kimi-delta-attention|Kimi Delta Attention]]（KDA）。它的机制理由是一项等价推导：正交矩阵的幂可以构建广义旋转位置编码，PaTH（Householder 变换位置编码）在正交情形下可等价写成对查询与键各减一个 DeltaNet 项之后的注意力，KDA 属于更一般的 DeltaNet，混合结构因此自带一种广义旋转位置编码。RoPE 加回去看不出变化，按简洁原则删掉。

Qwen3.8-Flash-Next 在全注意力层保留 RoPE，理由出在后训练：NoPE 变体在后训练之后 endless generation（停不下来的重复生成）率明显升高、更容易不终止。这条差别在预训练指标上量不出，后训练的终止行为把它暴露出来。

## 拆成三个变量

把两件并排，位置编码可省从一个二值判断拆成三个变量。

循环侧的[[gated-deltanet|门控粒度]]是第一个变量。K3 的循环侧用逐通道衰减门，Qwen 的 GDN 用每头一个标量衰减，两者自带的隐式位置信息强度不同。

评估截到哪一段是第二个变量。K3 一侧的账只量到预训练与基准，Qwen 一侧量到后训练与终止行为，两家的证据覆盖面不同。

后训练对终止行为的敏感度是第三个变量。endless generation 只在生成长度不受限的场景里现形，评估协议不含这一档时这条证据不会出现。

这条对质没有输家，它把两件各自结论的适用条件摆了出来。位置编码这一决定与[[three-axis-architecture-eval-protocol|三轴评估协议]]的关系也在这里：预训练轴上的零读数把判断推到了另外两条轴上。
