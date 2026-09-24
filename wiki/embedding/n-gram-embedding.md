---
title: n-gram 嵌入：骨干外的查表容量
slug: n-gram-embedding
type: concept
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/qwen3.8-flash-next.extracted.md
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/hf_config.json
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/hf_model_card.md
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
---

# n-gram 嵌入：骨干外的查表容量

给模型加容量有两条去向：加在骨干里（更多专家、更大隐维），或加在骨干外（一张与内容无关的查表）。n-gram 嵌入走后一条。它以每个 token 结尾的短 n-gram 作键查一张嵌入表，把查得的向量加到对应 token 的表示上。参数量随词表规模涨，每 token 的计算量几乎不动；键由输入直接算出、与内容无关，寻址确定，因此可以异步预取到加速器之外的主机内存。Qwen3.8-Flash-Next 用它加 51B 参数，表挂在第 2 层。

## 50B 级表的换算

查表的规模按行数与嵌入维记。本件取二阶与三阶 n-gram（`ngram_size=3`），基础表 20,000,000 项（`ngram_vocab_size_base=20000000`），8 个哈希头（`heads_per_ngram=8`），嵌入维 2560（`ple_embed_dim=2560`），挂在第 2 层（`ple_layer_ids=[2]`）。模型卡报的 51B n-gram 参数就此闭合：

$$
20{,}000{,}000\times2560=51.2\times10^{9}.
$$

8 个哈希头与阶数折进行空间，等价读法是 160M 行乘 320 维，同一乘积。20M 行对基线词表 250K 是 80 倍，发布件落在[[embedding-vs-expert-capacity|嵌入与专家容量对照]]里 50V 与 100V 两行之间。报告与模型卡都没写这步换算。

发布件另有一个报告正文未提的实现细节：`ple_conv_kernel_size=4`，查得向量过一个长度为 4 的短卷积再并入表示。这是报告正文与发布件之间一处已知的架构信息差。

## 放置消融

放置扫描固定 n-gram 总参数，单层放置扫第 1/2/3/4/10/15/25 层，另测 2+15 与 2+25 双层。基线（无 n-gram）损失 1.585、九项均值 45.44。

|放置层|损失|九项均值|
|---|---|---|
|第 1 层|1.541|47.30|
|第 2 层|1.541|47.94|
|第 3 层|1.543|46.76|
|第 4 层|1.544|46.89|
|第 10 层|1.544|46.62|
|第 15 层|1.543|47.37|
|第 25 层|1.541|47.40|
|2+15|1.541|47.01|
|2+25|1.540|47.75|

三处读数：第 1、2、25 层损失同为 1.541，下游均值差 0.64 分，损失一栏数字相同，放置的差别只出现在下游均值上；同一预算摊到多层没有一致收益；放置排序在 GDN 混合与全注意力下相似，选择与注意力机制基本无关。最终取第 2 层，理由落在工程侧：主机内存预取与第一层计算重叠。

这份放置消融跑在 50V 词表档上：它的无嵌入档损失与固定 MoE 预算那张表的无嵌入档同为 1.585，第 2 层档与 50V 档损失同为 1.541。

## 训练协议

统一实验协议取 300 tokens per active parameter（TPP，训练 token 数与激活参数数之比，本协议取 300）。查询侧的表外还有一套键值投影，报告把 n-gram 的键值投影归入 Muon 的适用范围（见 [[muon-parameter-partitioning|Muon 的参数分工]]），表本体走关掉权重衰减的 Adam。

这条容量路线与外部的对照写在 [[embedding-vs-expert-capacity|嵌入与专家容量对照]]。
