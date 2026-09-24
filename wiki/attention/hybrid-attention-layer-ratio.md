---
title: 混合注意力的层间配比：每四层一个全注意力
slug: hybrid-attention-layer-ratio
type: concept
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/qwen3.8-flash-next.extracted.md
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/hf_config.json
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
---

# 混合注意力的层间配比：每四层一个全注意力

注意力层负责把当前 token 与历史 token 混合。全注意力让每个位置对全部历史位置打分，逐 token 的直接检索能力完整，代价是序列长度的二次计算与随长度线性增长的键值缓存。线性注意力把前缀压进一个固定大小的循环状态，混合成本随长度线性增长，状态容量固定。混合架构把两种层按固定间隔排布。Qwen3.8-Flash-Next 取每四层一个全注意力层，其余三层走 [[gated-deltanet|Gated DeltaNet]]（下称 GDN）循环层。

## 配比与它回答的问题

报告给的理由是任何有限状态循环记忆都精确复现不了逐 token 的检索能力，全注意力层因此按固定间隔保留。48 层模型里每第四层是全注意力槽位，其余是 GDN 层；继续预训练阶段把这些全注意力槽位换成 [[qwen-sparse-attention|Qwen Sparse Attention]]。发布件 `config.json` 与这条排布对齐：`full_attention_interval=4`，`layer_types` 每第四项写作 `full_attention`。模型卡把每第四个槽位标成 Qwen Sparse Attention，两者同属「全注意力那一档」。

这个配比同时定下两件事的边界：留多少层做逐 token 检索由上层的层数比例回答，全注意力本身怎么变便宜由 QSA 那一件回答。

## 三方消融

配比的取值有一条同规模对照，在 28 层 25B-A3B 稀疏 MoE（总参数 25B、每 token 激活 3B）上做，结构底座是 Qwen3.5 架构，先 4K 上下文训 400B token，再 32K 上下文训 80B token。九项基准是知识类 MMLU、MMLU-Pro、SuperGPQA，数学类 MATH、GSM8K，推理类 BBH，多语类 MMMLU，代码类 EvalPlus、MultiPL-E。

|混合方案|九项均值|
|---|---|
|全注意力|49.87|
|滑动窗口混合（窗口 128）|51.15|
|GDN 混合|53.81|

滑动窗口混合让每层只看最近 128 个 token。GDN 混合在九项里赢全注意力八项、赢滑动窗口七项，拿下九项里七项的单列最高与全场最高平均；MMLU 与 EvalPlus 两项的单列最高归滑动窗口档。

![[raw/2026-09/llm-architecture/github/qwen3.8-flash-next/assets/qwen3.8-flash-next-fig1.png]]

> **总体架构图**（技术报告 Figure 1）每四层排三个 GDN 层加一个 QSA 层；每个子层经加宽残差流读写；n-gram 嵌入层只挂第 2 层；多 token 预测模块在投机解码步间复用 QSA 索引。

## 同一量级的另一处取法

Kimi K3 采用三比一配比，93 层里排 69 层 [[kimi-delta-attention|Kimi Delta Attention]] 与 24 层 Gated MLA，循环侧的门控粒度与全局注意力侧的键值压缩路线记在那一页。两件都把逐 token 检索留在少数层、把历史压缩交给多数层。位置编码在两类层上的分配是这处配比的连带决定，两家的取舍见 [[rope-vs-nope-evidence-axes|位置编码取舍的证据轴]]。
