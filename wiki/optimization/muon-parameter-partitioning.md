---
title: Muon 的参数分工：哪些权重走正交化、哪些留 AdamW
slug: muon-parameter-partitioning
type: concept
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/qwen3.8-flash-next.extracted.md
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
  - papers/context/qwen3.8-flash-next-context.md
---

# Muon 的参数分工：哪些权重走正交化、哪些留 AdamW

Muon 对二维权重矩阵做正交化更新（把动量矩阵投到近似正交矩阵上再缩放），逐元素的 AdamW 不做这一步。一条模型里哪些权重走哪条更新是一次设计决定，Qwen3.8-Flash-Next 按权重类别分工。

## 分工清单

走 Muon 的是真正充当线性映射的二维权重：注意力 q/k/v 与输出投影、Gated DeltaNet（见 [[gated-deltanet|Gated DeltaNet]]）的输入与输出投影、路由专家与共享专家的两个前馈线性层（fc1 升到中间维、fc2 降回）、n-gram 的键值投影。走 AdamW 的是输入嵌入、输出头、MoE 路由、[[gated-residual|Gated Residual]] 的两个低秩投影、注意力与 GDN 的输出门。n-gram 表本体走关掉权重衰减的 Adam。

## 逐条理由

路由上 Muon 放大早期训练波动，中后期再上不致失稳、也无明显收益。作者自己把解释写成猜想：路由的每个输出维对应一个专家的分数，维度之间基本独立，没有共享的线性结构给正交化利用。GR 的两个低秩投影因形状过长走 AdamW 更好。输出门上 AdamW 与 Muon 持平或略好。GDN 的衰减与 beta 投影每头出一个标量、是向量，正交化无意义。

这条分工在公开文献里两侧都有位置。Moonshot 在《Muon is Scalable for LLM Training》里把 Muon 用在包括路由在内的矩阵参数上，并报告 Muon 带来的奇异值熵提升在路由权重上更显著。《Symmetry-Compatible Principle for Optimizer Design: Embeddings, LM Heads, SwiGLU MLPs, and MoE Routers》从对称性一侧论证双随机正交更新与路由的置换对称不相容、建议路由离开谱类更新。本件的观察与该文口径同向，报告以自己的猜想收尾。

## 融合矩阵按语义拆开

Megatron 一类框架把注意力 qkv、SwiGLU 的 fc1、GDN 输入投影各存成一个融合矩阵。语义上它们是沿输出维拼接的独立线性算子，对融合矩阵做正交化会把无关子块的奇异方向搅在一起，缩放式也会按拼接后的假形状算。本件把它们按语义拆开再喂 Muon：qkv 与 GDN 输入投影按头拆，损失与下游同升；fc1 拆成 gate 与 up 两半，损失基本不动、下游略升。拆分顺带给出把单个子矩阵排除在 Muon 之外的粒度。

## 分布式实现

正交化要求对每个完整参数矩阵做整体更新，$K$ 步约 $4K\max(A,B)\min(A,B)^2$ FLOPs，与 Megatron 的分片冲突两处：张量并行下没有 rank 持有完整权重；数据并行下代价随短边立方增长，等元素切分留下严重掉队者。Canzona（同组另一篇独立论文，作者表与本件重合）把逻辑优化器分配与物理参数布局解耦：静态分区器搬运整参数（张量内不切）把各数据并行 rank 的估计迭代 FLOPs 拉平，异步 Micro-Group 流水线用融合 All-to-All 跨张量并行重建每个 Muon 所属矩阵，owner 跑的步与单设备 Muon 数学等价，ZeRO-1 的桶几何保留、梯度归约与反向的重叠不丢。它报 1.7B–32B 档 256 卡端到端迭代 1.57 倍加速、优化器步延迟降到约五分之一。

拆完之后一层贡献上百个子矩阵，优化器步成为一长串受 kernel 启动开销约束的小算子，整步用 CUDA graph 捕获。正交化本身怎么配参数记在 [[muon-orthogonalization-config|Muon 的正交化配置]]，分工带来的超参效应记在 [[batch-size-and-lr-scaling-refit|批量与学习率的缩放律重拟合]]。
