---
title: 稀疏注意力的两条路线：检索省算力与压缩缓存省字节
slug: sparse-attention-route-comparison
type: comparison
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/qwen3.8-flash-next.extracted.md
  - raw/2026-07/cs.CL/arXiv/kimi-k3/kimi-k3.extracted.md
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
---

# 稀疏注意力的两条路线：检索省算力与压缩缓存省字节

长上下文把全注意力的成本推到两处：序列长度的二次计算量，与随长度线性增长的键值缓存。稀疏注意力这一族给出两条不同的省钱路线，落点一个在算力、一个在字节。

## 检索路线

检索路线让每个查询只对少数键块算注意力，省掉的是计算量。Qwen Sparse Attention（见 [[qwen-sparse-attention|Qwen Sparse Attention]]）是这条路的实例：轻量索引器按 $r$ 个 token 的块打分、选 top-k 块，核心注意力只在被选中的 token 上计算，索引器复杂度从 $O(n^2)$ 降到 $O(n^2/r)$。索引器自身仍随长度平方增长，只是常数被 $r$ 压住。

## 压缩缓存路线

压缩缓存路线把每个 token 的键值压成低维潜变量再缓存，省掉的是缓存字节。Kimi K3 的 Gated MLA 走这条路，注意力计算时用学到的上投影重建内容键与内容值，全局的 token 到 token 注意力保留下来，缓存占用按压缩率下降。这条路线的代表页记在 [[gated-mla|Gated MLA]]。

## 同代对 DSA 索引器的两处改动

DeepSeek-V3.2 的 DSA 是检索路线的先行件，token 级打分、64 个索引器查询头、每个查询选 2048 个键值 token。同代两件各自动了它一刀。Qwen3.8-Flash-Next 把打分从 token 级移到块级，索引器头数从 64 降到 4，token 预算同为 2048，省的是索引器自身与核心注意力的计算。DeepSeek-V4.1-Flash 让索引器键由主键值投影而来，并把主键值、索引器键与 top-k 索引沿层复用，后层只在首个全注意力层建起的候选池内重打分（候选池 2048 块、每块 8 个位置），省的是索引器键的构造与重复打分。两处改动与跨层复用的机制见 [[index-reuse-in-sparse-attention|稀疏注意力的索引复用]]。

## 检索路线的天花板

检索路线把索引器留在计算路径上，索引器自己成为瓶颈的那一点决定这条路能推到多长。Qwen3.8-Flash-Next 的 kernel 读数已经露出这条天花板：1M 上下文处索引器自身相对稠密基线快 3.8 倍（前填充）与 4.4 倍（解码），含索引器的注意力模块整体快 7.6 倍与 4.9 倍，索引器延迟在模块里占相当份额。
