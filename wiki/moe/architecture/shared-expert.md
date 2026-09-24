---
title: 共享专家与比例因子
slug: shared-expert
type: concept
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2025-05/moe/spaces-ac-cn/moe-huanyouji-5/moe-huanyouji-5.extracted.md
  - papers/readings/2026-07/cs.CL/arXiv/kimi-k3-reading.md
  - raw/2026-07/cs.CL/arXiv/kimi-k3/kimi-k3.extracted.md
  - raw/2026-08/llm-architecture/spaces-ac-cn/k3-moe-attention/k3-moe-attention.extracted.md
---

# 共享专家与比例因子

共享专家出自 DeepSeekMoE（《DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models》，arXiv:2401.06066）。它把专家分成两类：必然入选的那 s 个叫 Shared Expert，按 Router 挑选激活的其余专家叫 Routed Expert。Router 是预测每个专家模长的小模型，模长决定哪些专家被选中。[[moe-layer|MoE 层：把 MLP 换成并行专家]]

## 规则改动

原规则是 n 选 k：共 n 个专家，每个 token 走进 Router 挑出的 k 个。共享专家把规则改成 n 减 s 选 k 减 s，另有 s 个专家必然入选。

改动前后总专家数与激活专家数都不变，参数量与推理成本由此保持不变。换来的是专家的分工方式：算力总量一样，一部分算力固定花在共同的部分上。

## 为什么让共性共享

专家之间存在共性，也就是文档里反复出现的通识部分。共享专家把这份共性显式承担下来，一次算好、每个 token 都摊到；Routed Expert 由此专注于各自的特长。

几何上的对应关系是：让 Shared Expert 充当 Routed Expert 的均值，Routed Expert 学习残差。共性被均值一侧接走，剩下各份之间的差异变大，第一篇的正交假设因此更容易成立。[[expert-orthogonality|Expert 正交假设]]

## 均匀分布最优性的一个反例

共享专家造成的目标负载分布自身不均匀：那 s 个必然入选的专家，负载固定地高于其余专家，平均下来每个专家被等量使用这个目标在这一层里落不了地。均匀分布的最优性由此看到一个具体反例，这一节的原始论述见 [[moe-huanyouji-5-abstract|MoE环游记：5、均匀分布的反思 摘要]]。

## 比例因子 λ

Routed 侧的权重 ρ 与 Shared 侧的无权输出直接相加，两侧的模长量级容易失衡。第五篇给出比例因子 λ，让两侧在初始化阶段的模长接近一致，使训练从量级相当的位置出发。

λ 的取值由数值模拟估计，再与官方配置对照：

| 配置 | 脚本模拟 | 官方 config 取值 |
|---|---|---|
| DeepSeek-V2 | 约 16 | 16.0 |
| DeepSeek-V3 | 约 2.83 | 2.5 |

DeepSeek-V2 一行精确吻合，DeepSeek-V3 一行相差约 12%。脚本按把共享专家计入专家总数的方式调用，DeepSeek-V2 的配置记 n = 162、k = 8、s = 2，DeepSeek-V3 的配置记 n = 257、k = 9、s = 1。两组配置的实体页见 [[deepseekmoe|DeepSeekMoE 与 DeepSeek 路线]]。

## Kimi K3 里的两处相接

Kimi K3 每层放 2 个全宽共享专家，路由专家 896 个、每 token 激活 16 个。共享专家保留全宽路径做通用变换，路由专家在一个宽度为隐维一半的紧凑潜空间里工作，两侧的比例问题因此同时出现在结构里，见 [[latent-moe|潜空间专家]]。

升维入口的 RMSNorm 在这里接上比例问题。博客作者给出两个可能来源：一是它更好地平衡了路由专家与共享专家的比例，实测加了它之后不再需要额外的缩放因子；二是归一化本身是很弱的非线性，加入后无形中增加了等效深度。这条解释给出一组可做的对照：去掉归一化时用缩放因子补偿，与保留归一化让比例自然平衡，两者在验证损失与基准上的差别可以单独量。

## 代价

共享专家与细颗粒度专家都带来额外的通信与协调成本。专家总数越大，负载越不均衡，这两项成本也越高。[[expert-granularity|细颗粒度专家]]
