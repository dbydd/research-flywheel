---
title: 全库综述
slug: overview
type: overview
created: 2026-09-22
updated: 2026-09-23
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - papers/readings/2026-09/cs.CL/arXiv/deepseek-v41-flash-reading.md
  - papers/readings/2026-07/cs.CL/arXiv/kimi-k3-reading.md
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
---

# 全库综述

本仓的知识层是 `wiki/`，一页装一个知识点。资源层两棵树——`papers/` 与 `blogs/`——各存摘要、增强与精读；知识点的溯源写在页面 frontmatter 的 `sources` 里，知识点之间的关系写在正文里。本页是全库的人工活综述，随每份新资源进来改写。

## 现有的知识面

**MoE 的路由与负载均衡。** 《MoE环游记》九篇（苏剑林，科学空间）从一个几何问题出发，把「哪些专家接这个 token」一路写成带约束的优化问题。系列级精读见 [[moe-huanyouji-reading|MoE环游记 系列精读]]，拆出的知识点分四类落位：

- 形式与几何（`wiki/moe/foundations/`）：[[moe-layer]] 给出 MoE 层的基本形式与参数量、计算量的解耦；[[router-magnitude-direction]] 给出系列的基线形式与「先算模长、再算方向」的计算顺序；正交近似与它的边界单独成页。
- 均衡问题与偏置路线（`wiki/moe/load-balancing/`）：[[load-balancing-problem]] 立起闲置与丢弃两类浪费；辅助损失、直通估计、无梯度偏置与动态激活四页连成一条链；[[quantile-balancing]] 与 [[one-step-quantile-solution]] 把均衡解成分位数；[[moving-quantile-balancing]] 把偏置推到序列级，偏差度量单独成页；[[quantile-histogram-estimation]] 记分位数均衡在将近一千个专家上的直方图落地。
- 架构与门控（`wiki/moe/architecture/`、`wiki/moe/gating/`）：共享专家与细颗粒度专家两页记 DeepSeek 的两件改进；[[latent-moe]] 记把模型宽度与专家宽度拆开的潜空间专家；[[situ-glu]] 记有界激活；[[gating-normalization]] 与门控的概率梯度推导两页记第九篇换到梯度一侧的推导。
- 对照与想法（`wiki/moe/comparison/`、`wiki/moe/ideas/`）：[[load-balancing-methods-comparison]] 把五代方案并列；想法页记本仓的延伸方向。

**注意力的三条扩展轴。** Kimi K3 这一族把「一个 token 能看见多少信息」沿序列、深度、宽度三个方向各自松开，系列级精读见 [[kimi-k3-reading|Kimi K3 精读]]，拆出的知识点分四域落位：

- 注意力域（`wiki/attention/`）：[[information-flow-three-axes]] 给出三轴骨架；序列轴的 [[kimi-delta-attention]] 配 [[bounded-decay-gating]] 与 [[full-rank-output-gate]] 两页；全局注意力层由 [[gated-mla]] 与 [[nope-position-encoding]] 两页承载；[[attention-residuals]] 记深度轴；[[hybrid-vs-sparse-attention]] 把混合注意力路线与全层稀疏注意力路线并列。
- 系统与基础设施（`wiki/systems/`）：[[moonep]] 记全均衡专家并行；[[kda-system-codesign]] 记 KDA 的算法与系统协同；[[prefix-cache-two-level]] 记混合架构的前缀缓存两级粒度；[[agentenv]] 记可恢复微虚拟机沙箱；[[trillion-scale-parallelism]] 记三万亿级预训练的并行与显存手法。
- 后训练（`wiki/training/`）：[[moe-rl-multi-domain]] 记多域强化学习与推理力度档；[[multi-teacher-on-policy-distillation]] 记把九个专家合成一个模型；[[mtp-eagle-draft]] 记多 token 预测层改造成投机解码草稿。
- 评测与实体（`wiki/evaluation/`、`wiki/entities/`）：[[eval-protocol-and-cost]] 记评测口径与每任务成本账；[[kimi-k3]] 是模型实体页，含两代规格对照与权重发布件口径核对。

**Qwen3.8-Flash-Next 的架构预览。** 这一件把 Qwen4 的架构草稿提前放出，四处承重改动各对一个瓶颈，拆出的知识点分四域落位：

- 注意力域（`wiki/attention/`）：[[hybrid-attention-layer-ratio]] 给出循环层与全注意力层的三比一配比；[[gated-deltanet]] 记循环侧的状态递推与参数化；[[qwen-sparse-attention]] 与 [[indexer-distillation]] 两页记块级打分的索引器与它的监督协议；[[index-reuse-in-sparse-attention]] 记跨层与跨投机步的索引复用；[[wide-residual-stream]] 与 [[gated-residual]] 两页记加宽残差流的家族与 GR 的取法，[[residual-branch-attribution]] 记它的跨层路径归因；[[rope-vs-nope-evidence-axes]] 与 [[sparse-attention-route-comparison]] 两页记与 Kimi K3、DeepSeek 一族的同题对照。
- 嵌入域（`wiki/embedding/`）：[[n-gram-embedding]] 记骨干外一层查表容量；[[embedding-vs-expert-capacity]] 记两种预算下嵌入与专家的分岔。
- 优化域（`wiki/optimization/`）：[[muon-parameter-partitioning]] 与 [[muon-orthogonalization-config]] 两页记 Muon 的权重分工与正交化配置；[[batch-size-and-lr-scaling-refit]] 记批量与学习率的重拟合；[[training-stability-stress-test]] 与 [[gated-normalization]] 两页记稳定性证据与门控归一化。
- 评测与实体（`wiki/evaluation/`、`wiki/entities/`）：[[three-axis-architecture-eval-protocol]] 记三轴协议与它拦下的三条捷径；[[qwen3.8-flash-next]] 是模型实体页，含规格、14 项基座对照与成本口径。

**资源层。** `blogs/` 树现有《MoE环游记》九篇与《k3-moe-attention》；`papers/` 树有 Kimi K3、DeepSeek-V4.1-Flash 与 Qwen3.8-Flash-Next 三份摘要，各有增强页与精读报告（[[kimi-k3-reading|Kimi K3 精读]]、[[deepseek-v41-flash-reading|DeepSeek-V4.1-Flash 技术报告 精读]]、[[qwen3.8-flash-next-reading|Qwen3.8-Flash-Next 精读]]）。

## 组织口径

知识层级由目录表达：`wiki/moe/` 下按 foundations、architecture、load-balancing、gating、comparison、entities、ideas 分域，`wiki/attention/`、`wiki/systems/`、`wiki/training/`、`wiki/evaluation/`、`wiki/entities/`、`wiki/embedding/`、`wiki/optimization/`、`wiki/ideas/` 按同一规则组织，目录随知识点归类变化。一条链只写一种真实关系，链接目标落在仓里真实存在的页面，待建的页面以未解析链接占位并收进本页待补；`tags` 非要求不写；全库不设目录页，找页靠图谱、反链与搜索，本页是人读的入口。**知识点按内容归页：一页可以收多份资源的同一条知识，页名与源资源不要求同名或强关联，判断某份资源拆没拆过要查页面正文与 `sources`。**

## 待补

- Kimi K3 一族在本页与仓根索引里点名的若干页在盘上未建：`wiki/attention/` 的下界衰减、满秩输出门、Gated MLA、混合与稀疏路线对照，`wiki/systems/` 的前缀缓存两级粒度、AgentENV、三万亿级并行，`wiki/training/` 的三页，`wiki/evaluation/` 的评测口径与成本账，`wiki/entities/kimi-k3`。这些名字以未解析链接入图，待补。
- Qwen3.8-Flash-Next 注意力域两页指向未建的 `wiki/attention/gated-mla`，与该页一并待补。
- `people/` 目前是空的，系列作者与被引作者的画像未建。
- 想法页全部处于 `seed` 状态，还没有一条跑出验证结果。
