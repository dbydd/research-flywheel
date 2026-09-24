---
title: "DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression"
slug: deepseek-v41-flash-abstract
type: abstract
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2026-09/cs.CL/arXiv/deepseek-v41-flash/deepseek-v41-flash.extracted.md
  - raw/2026-09/cs.CL/arXiv/deepseek-v41-flash/deepseek-v41-flash.pdf
resource: raw/2026-09/cs.CL/arXiv/deepseek-v41-flash
---

# DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression

> [!quote] 官方摘要
> The widespread adoption of long-horizon agents has made model workloads increasingly input-heavy. …… Together, these compute, storage, and bandwidth demands constitute the primary bottleneck to further lowering deployment costs. To address this challenge, we introduce DeepSeek-V4.1-Flash, a multimodal Mixture-of-Experts (MoE) model with 552B backbone parameters and support for contexts of up to one million tokens. …… To push the limits of KV cache compression, DeepSeek-V4.1-Flash combines cross-layer KV cache reuse in Compressed Sparse Attention 2 (CSA2) with FP4 KV caching. These designs reduce its global KV cache footprint (always in HBM) to 890 bytes per token, roughly 1/4 of the corresponding footprint of DeepSeek-V4-Flash. Further, through a dedicated deployment optimization known as SWA Bounded Replay, DeepSeek-V4.1-Flash reduces its persistent KV cache footprint (always on SSD or in host memory) to roughly 1/8 of that of DeepSeek-V4-Flash. …… In addition, we streamline the DeepSeek-V4 architecture and introduce several efficient architectural extensions. We pretrain DeepSeek-V4.1-Flash on a multimodal corpus comprising 45T tokens and conduct comprehensive post-training, yielding strong performance across diverse text-based and multimodal agentic scenarios. Model checkpoints are available at https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash.

## 一句话判断

这份报告交付一个为长程 agent 负载设计的多模态 MoE 模型 DeepSeek-V4.1-Flash：552B 主干参数加 196B Engram 条件记忆参数，上下文窗口到一百万 token，预训练语料 45T token，解码时每 token 激活 16B 参数，预填充时每 token 激活 8B 参数。KV 缓存压缩是全文主线，机制沿「算得少、存得小、搬得少」三条叠起来：CED 架构把解码器的全局 KV 从编码器最后一层隐状态投影出来，预填充只跑前一半层数；CSA2 把主 KV、索引器 K 与 Top-K 索引沿层复用，Full、Reindex、Reuse 三种模式静态分配给各层，解码器再套一层层次化稀疏索引器，把后续重索引层的打分范围收进首个 Full 模式层建立的候选池；主 KV 缓存走 FP4（E2M1 配每 16 通道一个 E4M3 缩放，去掉二级全局缩放），SWA KV 保持 FP8。落点数字：全局 KV 缓存（常驻 HBM）压到每 token 890 字节，是 DeepSeek-V4-Flash 的四分之一，是首代 DeepSeek-V1 的 1/437；持久 KV 缓存（驻 SSD 或主机内存）压到约八分之一，其中 SWA Bounded Replay 只重放最近一个窗口的 token 来近似重建 SWA 状态，SWA KV 改由主机内存的分布式内存池承载，持久缓存只留全局 KV。计算侧同步收窄：上下文从 4K 拉到 1M，单 token 解码 FLOPs 涨约四分之一；Reuse Mode 层在预填充与解码时分别只需 15 与 11 个 kernel。参数效率的对照落在 DeepSeek-V4-Pro-Base：本模型用三分之一总参数与四分之一激活参数，在保留评估集上取得 5%–10% 的提升。

## 前提背景

这份资源立在长程 agent 带来的输入侧成本问题上。本组自己这条线的前作包括 DeepSeek-V2（MLA 在注意力头之间共享一个小潜变量，arXiv 2405.04434）、DeepSeekMoE（细粒度路由专家，arXiv 2401.06066）、DeepSeek-V3（arXiv 2412.19437）、DeepSeek-V3.2（arXiv 2512.02556），以及本报告的直接基线 DeepSeek-V4（arXiv 2606.19348，2026-06）。DeepSeek-V4 用全局注意力分支配滑动窗口注意力把长序列计算成本压下来，KV 缓存的持久存储与搬运因此浮成主瓶颈，本报告把压缩目标直接定在 KV 缓存本身。

架构侧的直接前作是三条沿层维度复用的并行工作：YOCO（You Only Cache Once，arXiv 2405.05254）让上半个网络直接共享下半个网络产生的 KV；IndexCache（arXiv 2603.12201）复用 Top-K 索引来削减索引器计算；YOIO（You Only Index Once，arXiv 2606.06467）把稀疏路由算一次并共享给所有层；HySparse（arXiv 2602.03560）让稀疏层复用稠密层的 KV 缓存。本文的 CSA2 把主 KV、索引器 K 与 Top-K 索引一起沿层复用，并在解码器里用候选池收窄后续索引层的打分范围。

组内还有三件前作被这一版纳入并各自改造：mHC 多流残差（arXiv 2512.24880）升级成 Single-Pass mHC，配 Mega-mHC 部署 kernel；Engram 条件记忆（arXiv 2601.07372）去掉了短因果卷积，嵌入表改走动量更新加 Sinkhorn 均衡；DSpark 投机解码（arXiv 2607.05147）放到预训练之后的独立阶段训练。

作者与组是 DeepSeek-AI（research@deepseek.com），模型属于 DeepSeek-V4 家族的 Flash 档，权重在 Hugging Face 公开。

## 本体与去向

- 本体：`raw/2026-09/cs.CL/arXiv/deepseek-v41-flash/`
- 图：`assets/` 下按原文编号存放。`deepseek-v41-flash-fig1a.png` 与 `deepseek-v41-flash-fig1b.png` 是 Figure 1 的两个面板（agentic 基准上的表现；历代 DeepSeek 模型每 token 全局 KV 缓存字节数）；`deepseek-v41-flash-fig2.png` 是单 token 解码 FLOPs 随上下文长度的曲线；`deepseek-v41-flash-fig3.png` 是总体架构（编码器 20 层加解码器 20 层，CSA2 的压缩比与模式逐层标注）；`deepseek-v41-flash-fig4.png` 是 CSA2 的三种模式；`deepseek-v41-flash-fig5.png` 是层次化稀疏索引器；`deepseek-v41-flash-fig6.png` 是三个 Base 模型的 BPB 对比；`deepseek-v41-flash-fig7.png` 是 RL 训练规模与代码 agent 基准；`deepseek-v41-flash-fig8.png` 是多版本 Claude Code 与异构 scaffold 的联合 RL；`deepseek-v41-flash-fig9.png` 是推理力度对 Pass@1 与输出长度的作用；`deepseek-v41-flash-fig10.png` 是单 agent 与多 agent 的测试时算力扩展；`deepseek-v41-flash-fig11.png` 是推理力度与轨迹长度；`deepseek-v41-flash-fig12.png` 是八个推理基准上的推理力度曲线。
- 精读：[[deepseek-v41-flash-reading|DeepSeek-V4.1-Flash 精读]]
