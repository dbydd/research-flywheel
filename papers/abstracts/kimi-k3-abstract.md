---
title: Kimi K3: Open Frontier Intelligence
slug: kimi-k3-abstract
type: abstract
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2026-07/cs.CL/arXiv/kimi-k3/kimi-k3.extracted.md
  - raw/2026-07/cs.CL/arXiv/kimi-k3/kimi-k3.html
  - raw/2026-07/cs.CL/arXiv/kimi-k3/kimi-k3.pdf
resource: raw/2026-07/cs.CL/arXiv/kimi-k3
---

# Kimi K3: Open Frontier Intelligence

> [!quote] 官方摘要
> We introduce Kimi K3, a 2.8T parameter Mixture-of-Experts model with 104 billion activated parameters, native vision capabilities, and a 1-million-token context window. Kimi K3 is built on Kimi Delta Attention and Attention Residuals, which improve information flow across sequence length and model depth. Together with Stable LatentMoE, which effectively activates 16 of 896 routed experts per token, and refined training and data recipes, these advances yield an approximately 2.5× improvement in overall scaling efficiency over Kimi K2. Post-training highlights reinforcement learning across general, agentic, and coding domains and multiple reasoning-effort levels, enabling compositional generalization and robust long-horizon execution. At 2.8T scale, Kimi K3 is supported by infrastructure advances in multiple areas: algorithm-system co-design for KDA, perfectly balanced expert-parallel training with efficient memory management, million-token agentic RL with persistent rollout and sandbox states, and deployment innovations. Extensive evaluations show that Kimi K3 achieves frontier-level performance across long-horizon coding, agentic, knowledge, reasoning, and vision tasks. …… We release the full Kimi K3 model weights to facilitate future research and accelerate the broader deployment and adoption of frontier intelligence.

## 一句话判断

报告给出 Kimi K3：2.8T 总参数、104B 激活参数、896 个路由专家每 token 激活 16 个、原生视觉、100 万 token 上下文的稀疏 MoE，权重全部开放。架构沿序列、深度、宽度三轴同时扩展信息流：序列方向每个块排 3 层 Kimi Delta Attention（KDA）加 1 层 Gated MLA（Multi-head Latent Attention）；深度方向用 Attention Residuals 让每层对嵌入与前序块输出做选择性读取；宽度方向每个注意力层后接 Stable LatentMoE，靠升维入口的 RMS Norm、SiTU-GLU 与 Quantile Balancing 稳住 896 选 16 的极端稀疏训练。这些改动连同数据与训练配方一起，给出相对 Kimi K2 约 2.5 倍的整体 scaling 效率（原文 Table 1 对照两代规格：层数 61→93，总参数 1.04T→2.78T，路由专家 384→896，训练上下文 128K→1M）。评测覆盖长程编码、智能体、知识、推理与视觉，代表性读数有 GPQA Diamond 93.5%、ProgramBench 77.8%、SWE-Marathon 42.0%、BrowseComp 91.2%、Math-Vision 94.3%（配 Python 工具升到 97.8%），整体位置在最强闭源模型 Claude Fable 5 与 GPT-5.6 Sol 之后，领先同一套件内的其余开源与闭源模型。读数条件：多数分数取自最大思考强度配置（max 或 xhigh），部分榜面带日期口径（FrontierSWE 为 2026-07-16），成本对比按每任务推理花费计（BrowseComp 上每任务 2.03 美元）。报告另用大量篇幅写基础设施，含 KDA 的算法-系统协同设计、MoonEP 全均衡专家并行、百万 token 智能体 RL 的外置 KV cache 与可恢复 microVM 沙箱。

## 本体与去向

- 本体：`raw/2026-07/cs.CL/arXiv/kimi-k3/`
- 版本：arXiv 2607.24653v2，首次提交 2026-07-27，本快照取 v2（2026-08-07）
- 作者：Kimi Team（Moonshot AI）
- 图：16 张，`raw/2026-07/cs.CL/arXiv/kimi-k3/assets/kimi-k3-fig1.png` 至 `kimi-k3-fig16.png`（按原文 Figure 编号）
- 精读：[[kimi-k3-reading|Kimi K3 精读]]
- 内部视角：[[k3-moe-attention-abstract|简单谈谈K3的MoE和Attention]]（作者为 Kimi 研究员苏剑林，逐条讲 MoE 与 Attention 的取舍）
