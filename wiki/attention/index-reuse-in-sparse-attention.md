---
title: 稀疏注意力的索引复用：跨层与跨投机步
slug: index-reuse-in-sparse-attention
type: concept
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/qwen3.8-flash-next.extracted.md
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
  - papers/context/qwen3.8-flash-next-context.md
---

# 稀疏注意力的索引复用：跨层与跨投机步

稀疏注意力让索引器为每个查询挑出值得计算的键块。索引器自身有成本，复用已经算出的索引可以省掉其中一部分。这条路上有两根轴：沿层的复用与沿解码步的复用。Qwen Sparse Attention（见 [[qwen-sparse-attention|Qwen Sparse Attention]]）与相邻发布件分别落在两根轴上。

## 跨层复用

跨层复用把层分成跑索引器的层与复用最近一次索引的层。IndexCache（该方法的自名）用训练无关的贪心层搜索加训练感知的多层蒸馏，在 30B 的 DSA 模型上省掉 75% 索引器计算，报前填充最高 1.82 倍、解码最高 1.48 倍加速。「保留几个索引器层」这个旋钮在扫描里记作 Keep $x$。

Qwen3.8-Flash-Next 的报告正文与消融图例把这条对照基线写作 IndexShare，该方法自己的文献题名与报告参考文献表里的条目都是 IndexCache，错位只在本件报告正文一侧。扫描读数上，相对索引器延迟 0.25 处 QSA 追平全注意力，IndexCache 在同一延迟档仍低于基线。

这条路线在混合架构上遇到的门槛与层间相似度有关：跨层共享依赖各层的索引彼此相似，混合架构相邻全注意力层之间夹着三个循环层，层间相似度低。块级压缩的 QSA 在这一点上适配得更好。

## 跨投机步复用

多 token 预测让模型一次生成若干候选 token，多步投机解码对每个候选步各算一次索引。跨投机步复用把同一份 top-k 索引给多个投机步共用，四个投机步下五个域（MT-Bench、GSM8K、MATH、HumanEval、MBPP）的平均接受长度从 4.06 到 4.07，逐档差 0.01 至 0.03，复用无感。

这条机制的出处报告点给 GLM-5，回 GLM-5 全文找不到对应表述，归属按悬空记账，机制本身读作本件自述的实现细节。

## 同代的另一处取法

DeepSeek-V4.1-Flash 与本件同代，两家都把 DSA 的 token 级索引器动过一刀。本件把打分降到块级并压到 4 个索引器头；DeepSeek-V4.1-Flash 让索引器键由主键值投影而来，并把主键值、索引器键与 top-k 索引沿层复用，后层只在首个全注意力层建起的候选池内重打分（候选池 2048 块、每块 8 个位置）。同一条「沿层复用」的想法在两家手里落在不同的复用对象上：一家复用整份索引，一家复用候选池内的索引键。
