---
title: MoE环游记：9、门控归一化之争 增强信息
slug: moe-huanyouji-9-context
type: context
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2026-06/moe/spaces-ac-cn/moe-huanyouji-9/moe-huanyouji-9.extracted.md
  - raw/2026-06/moe/spaces-ac-cn/moe-huanyouji-9/moe-huanyouji-9.html
resource: raw/2026-06/moe/spaces-ac-cn/moe-huanyouji-9
---

# MoE环游记：9、门控归一化之争 增强信息

## 这一篇做了什么

第九篇（2026-06-17，科学空间 11782）从第一性原理追问 Router 打分 `ρ` 兼作 Gate 时该不该归一化，以及归一化放在选 Top-`k` 之前还是之后。问题被写成三选一：先 Softmax 再选 Top-`k`、先选 Top-`k` 再 Softmax（即 Re-Norm），或者不做归一化（§问题描述）。

- 角色分工：`ρ` 用于选 Top-`k` 时是 Router，用于乘到 Expert 上时是 Gate；Gate 的作用是在训练时为 Router 提供梯度（§问题描述）。
- 已有选择：DeepSeek 为配合 Loss-Free 把激活函数改成 Sigmoid，并用于 DeepSeek-V3；ReMoE 用 ReLU；第一篇的几何视角允许任意非负激活函数（§其他选择）。Re-Norm 的收益是前向数值更稳定，代价是 `k` 至少要大于 1，`k = 1` 时 `ρ` 完全收不到梯度（§其他选择）。
- 设计原理：先看 `k = 1`，被激活的 Expert 应当是损失最小的那一个，即 `argmax ρ = argmin [ℓ(e_1),…,ℓ(e_n)]`（§设计原理，公式 (1)）。
- 目标转化：基于损失构造目标分布 `q`，基于 `ρ` 构造预测分布 `p`，最小化两者的 KL；展开后第一项是负熵、第三项与 `θ` 无关，等效损失为 `Σ p_i ℓ(e_i)`（§目标转化）。
- 直通估计：等效损失的梯度是 REINFORCE，噪声偏大（§直通估计）；对减 baseline 的 REINFORCE 做一阶泰勒展开，得到「前向用 1、反向用 `log p_i`」的 STE，前后向不一致。
- 最终形式：把 Expert 从 `e_i` 换成 `p_i e_i`，重复推导后 Stop Gradient 项自动消失，前后向一致，效果天花板随之提高（§最终形式）。
- 结论：如果需要一个自上而下的概率推导，Router 作为 Gate 时应当归一化，且不应当 Re-Norm（§最终形式）。
- 采样与否：`E_{i~p}` 的采样与直接选 Top-`k` 是多样性与稳定性的权衡；折中做法是先选 Top-`(k+c)` 再在 `k+c` 个中随机挑 `k` 个，或者在 logits 上加轻微噪声后再选 Top-`k`（§采样与否）。
- 边界：`k = 2` 时概率框架给不出精确推导，作者建议把 `k > 1` 的 MoE 当作 MaxPooling 的类似物，或者回到第一篇的几何视角理解（§相关工作）。

## 引用谱系

| 正文指称 | 出处 | 篇内落点 | 核验 |
|---|---|---|---|
| Loss-Free 负载均衡 | `https://spaces.ac.cn/archives/10757` | §开篇段 | 站内前篇，原文快照在 `raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3/` |
| DeepSeek-V3 | DeepSeek-V3 Technical Report，arXiv:2412.19437，2024-12-27，DeepSeek-AI 等 200 位作者，`https://arxiv.org/abs/2412.19437` | §其他选择 | 已核，arXiv API，2026-09-22 |
| ReMoE | ReMoE: Fully Differentiable Mixture-of-Experts with ReLU Routing，arXiv:2412.14711，2024-12-19，Ziteng Wang、Jun Zhu、Jianfei Chen，`https://arxiv.org/abs/2412.14711` | §其他选择 | 已核，arXiv API，2026-09-22 |
| 《MoE环游记：1、从几何意义出发》 | `https://spaces.ac.cn/archives/10699` | §其他选择、§相关工作 | 站内前篇，原文快照在 `raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-1/` |
| 《Sparse Backpropagation for MoE Training》 | arXiv:2310.00811，2023-10-01，Liyuan Liu、Jianfeng Gao、Weizhu Chen，`https://arxiv.org/abs/2310.00811` | §相关工作 | 已核，arXiv API，2026-09-22 |
| 《Bridging Discrete and Backpropagation: Straight-Through and Beyond》 | arXiv:2304.08612，2023-04-17，Liyuan Liu、Chengyu Dong、Xiaodong Liu、Bin Yu、Jianfeng Gao，`https://arxiv.org/abs/2304.08612` | §相关工作 | 已核，arXiv API，2026-09-22 |
| 《GRIN: GRadient-INformed MoE》 | arXiv:2409.12136，2024-09-18，Liyuan Liu、Young Jin Kim、Shuohang Wang、Chen Liang、Yelong Shen、Hao Cheng 等 17 位作者，`https://arxiv.org/abs/2409.12136` | §相关工作 | 已核，arXiv API，2026-09-22 |
| 策略梯度与采样的旧文 | 科学空间 `https://spaces.ac.cn/archives/7521`、`https://spaces.ac.cn/archives/7737` | §直通估计 | 源文内链；站点对自动抓取返回 403 |
| DeepSeek-V2/V3 配置数字 | 见 [[moe-huanyouji-5-context|第五篇 增强信息]] 的配置表 | §其他选择（DeepSeek-V3 用 Sigmoid） | 已在第五篇页面核对，2026-09-22 |

## 建立在前篇之上

- §开篇段 接第三篇的 Loss-Free：DeepSeek 为配合 Loss-Free 把激活函数改成 Sigmoid，这条线索的完整记录在第三篇；DeepSeek-V2/V3 的具体配置数字记在第五篇的配置表，本页只引用「DeepSeek-V3 用 Sigmoid」这一事实。
- §其他选择 与 §相关工作 回到第一篇 §为何如此 的几何视角：第一篇指出 `ρ` 的几何意义是模长，激活函数因此没有归一化要求，本页把这个自由度放进 Softmax、Sigmoid、ReLU 并列的候选里讨论。
- 本篇是系列里刘力源三部曲首次出现的地方。第一篇 §为何如此 曾单引其中一篇（Sparse Backpropagation for MoE Training）作为「为何把 `ρ_i` 乘到 Expert 上能让 Router 学会排序」的唯一解释来源；本页把三部曲整体纳入，用作概率框架的统一来源（§相关工作）。这一系列的一般事实都指回本页。
- 本篇是《MoE环游记》系列至 2026-09-22 为止的最后一篇，发布于 2026-06-17，科学空间编号 11782。

## 作者与组

本篇引用块为「苏剑林. (Jun. 17, 2026). 《MoE环游记：9、门控归一化之争》[Blog post]. Retrieved from `https://spaces.ac.cn/archives/11782`」。苏剑林与科学空间的完整背景见 [[moe-huanyouji-1-context|第一篇 增强信息]]。

**刘力源与三部曲（本页首次交代）。** 本篇的推导来自既有工作，作者说明它提炼并修改自刘力源的三篇文章（§相关工作）：

| 篇 | 出处 | 主题 | 核验 |
|---|---|---|---|
| 上篇 | Bridging Discrete and Backpropagation: Straight-Through and Beyond，arXiv:2304.08612，2023-04-17 | 直通估计及其推广 | 已核，arXiv API，2026-09-22 |
| 中篇 | Sparse Backpropagation for MoE Training，arXiv:2310.00811，2023-10-01 | MoE 训练的稀疏反向传播 | 已核，arXiv API，2026-09-22 |
| 下篇 | GRIN: GRadient-INformed MoE，arXiv:2409.12136，2024-09-18 | 梯度信息引导的 MoE | 已核，arXiv API，2026-09-22 |

三部曲共同作者包括微软研究院的 Jianfeng Gao、Weizhu Chen（上篇与中篇）以及 Young Jin Kim、Shuohang Wang、Hao Cheng（下篇，共 17 位作者）（arXiv API，2026-09-22）。作者对三部曲的评价是：它们提供了一个统一的概率框架去为各种离散化操作设计梯度，值得反复阅读；概率框架的局限在于形式化比较严重，操作起来拘束（§相关工作）。这段评价属作者判断。

## 关联

- [[moe-huanyouji-9-abstract|MoE环游记：9、门控归一化之争 摘要]]
- [[moe-huanyouji-1-context|第一篇 增强信息]]：几何视角与作者背景的出处
- [[moe-huanyouji-3-context|第三篇 增强信息]]：Loss-Free 与 Sigmoid 的出处
- [[moe-huanyouji-5-context|第五篇 增强信息]]：DeepSeek-V2/V3 配置数字的出处
- [[moe-huanyouji-8-context|第八篇 增强信息]]：系列内上一篇
