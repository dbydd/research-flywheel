---
title: 索引器蒸馏：用块级教师监督稀疏注意力索引器
slug: indexer-distillation
type: concept
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/qwen3.8-flash-next.extracted.md
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
  - papers/context/qwen3.8-flash-next-context.md
---

# 索引器蒸馏：用块级教师监督稀疏注意力索引器

稀疏注意力的索引器负责挑出值得计算的键块，它本身要给出一份逼近全注意力的打分。索引器蒸馏把全注意力的分布压成教师信号，监督索引器的打分。Qwen Sparse Attention（见 [[qwen-sparse-attention|Qwen Sparse Attention]]）的两段协议是一份完整实例。

## 教师信号的构造

教师分布取自全序列 softmax 注意力按教师头求和、L1 归一化，记 $a_i\in\mathbb{R}^n$。按 $r$ 做 max-pool 到块级、再 L1 归一化，得 $\hat a_i\in\mathbb{R}^B$，$B=\lfloor n/r\rfloor$。索引器分数 $I_{i,:}$ 对块级教师做 KL：

$$
L_{KL}=\frac{1}{N}\sum_i D_{KL}\!\left(\hat a_{i,:}\,\|\,\mathrm{Softmax}(I_{i,:})\right).
$$

块级 max-pool 这一步的实证来源要收窄。报告的正文把这一步并写给 SeerAttention 与 ProxyAttn 两件；回一手渠道，把教师注意力分布做 max-pool 到块级做 KL 目标的做法只见于 SeerAttention，ProxyAttn 是 training-free 方法、通篇没有蒸馏损失。

## 两段协议

第一段只训索引器：1,000 步、学习率 $1\times10^{-3}$、每步 8 条 256K 序列、合计约 2B token，损失只算完整键块。第二段骨干与索引器联合训：8,000 步、学习率 $2.5\times10^{-5}$、每步 96 条 256K 序列、合计约 200B token，KL 限制在选中的 $K_B$ 个块上，教师概率在该集合内重归一。

对照路线 DSA（DeepSeek-V3.2 的稀疏注意力）的两段 warm-up 是 1,000 步、学习率 $1\times10^{-3}$、每步 16 条 128K 序列、合计 2.1B token。本件第一段的步数与学习率照搬 DSA 的配置，第二段的序列长度、学习率与预算是自己的配置。

## 消融上的表现

稠密蒸馏初始化之后直接上索引器明显掉分（1M 以内 RULER 约 77–78 对全注意力基线约 86.3），少量联合训练即回到全注意力水平，索引器查询头数 4 头起追平并略超。这条读数把蒸馏初始化与联合训练两段的分工量出来：初始化给出可比起点，联合训练把索引器与骨干的对齐补齐。
