---
title: 简单谈谈K3的MoE和Attention
slug: k3-moe-attention-abstract
type: abstract
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2026-08/llm-architecture/spaces-ac-cn/k3-moe-attention/k3-moe-attention.extracted.md
  - raw/2026-08/llm-architecture/spaces-ac-cn/k3-moe-attention/k3-moe-attention.html
resource: raw/2026-08/llm-architecture/spaces-ac-cn/k3-moe-attention
---

# 简单谈谈K3的MoE和Attention

> [!quote] 官方摘要
> 上个月，我们发布了迄今为止最大的开源模型K3。……这篇文章，我们来聊聊K3在架构上的一些设计思路。

## 一句话判断

这一篇是 K3 的内部视角说明，作者是 Kimi 研究员苏剑林，逐条交代 MoE 与 Attention 两块的设计动机与取舍，全篇给出的架构总式是 K3 = KDA（Kimi Delta Attention）+ MLA（Multi-head Latent Attention，文中用 Gated MLA 变体）+ Stable LatentMoE + AttnRes（Attention Residuals，用注意力改写残差累加），优化器沿用 Moonlight 版 Muon，注意力权重改成 Per-Head 形式。MoE 侧的主线是把 LatentMoE 稳下来：LatentMoE 先降维到 `d/2`、再做 `2n` 选 `2k` 的稀疏混合、最后升维，四矩阵连乘带来不稳定；作者把 SiLU 换成带 softcap 的 SiTU（Sigmoid Tanh Unit，`β = 4`），又给 up 分支补上 softcap（`β₂ = 25`），形成 SiTU-GLU，用来压住 `W₁` 与输入同向时冒出的 `O(‖x‖⁴)` 级异常值。稳定化按最小改动原则只保留升维入口处的一个 RMS Norm，事后消融显示它除了稳训练还会抬高某些 benchmark 的分数，作者给出两个可能来源：Routed 与 Shared Expert 的比例被平衡，以及很弱的非线性带来的等效深度增加。负载均衡从 K2 的 SignSGD 式 Loss-Free 更新换成 QB（Quantile Balancing），理由是总专家数涨到 896 之后前者不够稳，QB 在数学上更合理且无额外超参；QB 求全局分位数，落地方案是分 bin 直方图估计，作者实测 1000 个 bin 已经够用，分布可加让跨机、跨梯度累积的聚合通信量极低。Attention 侧保留了 MLA，理由是在固定训练成本与 KV cache 规模下它近乎最优，MTP 与推测解码让 MLA 的解码形式（head_dims 512 以上的 MQA）提前消耗算力；作者据此列出理想 Attention 的四条约束——效果不低于 MLA、训练与 Prefill 成本不超过 MLA、KV cache 更小、解码算力更小——并给出当前没有设计能同时满足这四条的判断。K3 用 NoPE，位置编码由 KDA 隐含提供：KDA 属于更一般的 DeltaNet，给 `Q`、`K` 加 DeltaNet 就能起到类 RoPE 的作用，所以去掉 RoPE 之后效果基本不变。文中另有一段对 DeepSeek-V4（文中简称 DSV4）的评论：DSV4 把 Attention 换成 head_dims 512、`K = V` 的 MQA，再加 Sparse 与 Compress 压计算与 KV cache，作者把它读作 MLA 路线的推广与升级，代价落在 Infra 复杂度与激进稀疏的最优性上。

## 本体与去向

- 本体：`raw/2026-08/llm-architecture/spaces-ac-cn/k3-moe-attention/`
- 出处：苏剑林，科学空间，2026-08-04 发布，原文 <https://spaces.ac.cn/archives/11848>
- 图：1 张，`raw/2026-08/llm-architecture/spaces-ac-cn/k3-moe-attention/assets/k3-moe-attention-fig1.png`（直方图近似估计分位数示意图，原文未编号，按正文顺序计为第 1 图）
- 精读：[[kimi-k3-reading|Kimi K3 精读]]
- 关联：[[kimi-k3-abstract|Kimi K3: Open Frontier Intelligence]]
