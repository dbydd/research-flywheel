---
title: MoE环游记：6、最优分配促均衡 增强信息
slug: moe-huanyouji-6-context
type: context
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/moe-huanyouji-6.extracted.md
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/moe-huanyouji-6.html
resource: raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6
---

# MoE环游记：6、最优分配促均衡 增强信息

## 这一篇做了什么

第六篇（2026-02-22，科学空间 11619）把负载均衡写成等式约束下的线性规划来解，得到 Quantile Balancing（QB）。

- 问题：`m` 个 Token、`n` 个 Expert、打分矩阵 `s`，约束为每个 Token 恰好激活 `k` 个、每个 Expert 恰好被激活 `mk/n` 次，目标是总分最高（§线性规划，公式 (1)）。松弛到 `x ∈ [0,1]` 后成为有界区域内的线性规划（公式 (2)）。
- 求解：写成 `max-min` 形式，按 Minimax 定理交换 `max` 与 `min`（§极大极小，公式 (3)、(4)）；`x*` 由 `s_{i,j} − α_i − β_j` 的符号决定（§极大极小）；交换后分裂为 `m` 个独立子问题，交替最小化（§分而治之）。
- 解的形式：每行取 `s − β` 的第 `k+1` 大元素，每列取 `s − α` 的第 `mk/n+1` 大元素；两者都是对应维度的 `1 − k/n` 分位数，方法因此叫 Quantile Balancing（§交替迭代，伪代码框「Quantile Balancing (QB)」）。
- 推理形态：推理只用 `n` 维的 `β`，`α` 的规模是全局 Batch Size，属求解中间量（§交替迭代）。
- 陷阱与实用化：先用旧的 `β` 选出当前批的 Expert、再更新 `β`，否则泄漏未来信息；实际使用从上一步的 `β` 出发、每步只迭代一次，避免过拟合当前批次（§小心陷阱，伪代码框「QB 实际使用形式」）。
- 梯度下降解法：对 `β` 的目标函数可导，梯度为 `mk/n − Σ χ(s_{i,j} − α_i − β_j > 0)`，用 SignSGD 替换 Quantile 更新；在每行第 `k` 大与第 `k+1` 大不相等的条件下，该方案严格等同于 Loss-Free（§梯度下降）。
- 改动点：QB 把 BIP 的不等式约束改成等式约束，去掉了 `α, β ≥ 0` 的截断；作者实测截断拖慢均衡速度，并且常常只能把过载的 Expert 压下去、救不回闲置的 Expert（§相关工作）。
- 演示代码给出 `quantile_bias` 与 `max_min_avg_vio` 两个函数；页内第 1 图是第一层 MoE 的 MaxVio 对比图（§演示代码）。

页内第 1 图：`raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/assets/moe-huanyouji-6-fig1.png`（原文未编号，按正文顺序计为第 1 图）。

## 引用谱系

| 正文指称 | 出处 | 篇内落点 | 核验 |
|---|---|---|---|
| 《BASE Layers: Simplifying Training of Large, Sparse Models》 | arXiv:2103.16716，2021-03-30，Mike Lewis、Shruti Bhosale、Tim Dettmers、Naman Goyal、Luke Zettlemoyer，`https://arxiv.org/abs/2103.16716` | §相关工作 | 已核，arXiv API，2026-09-22 |
| 《Binary-Integer-Programming Based Algorithm for Expert Load Balancing in Mixture-of-Experts Models》（BIP） | arXiv:2502.15451，2025-02-21，Yuan Sun，`https://arxiv.org/abs/2502.15451` | §相关工作 | 已核，arXiv API，2026-09-22 |
| 《Maximum Score Routing For Mixture-of-Experts》 | arXiv:2508.12801，2025-08-18，Bowen Dong、Yilong Fan、Yutao Sun、Zhenyu Li 等 7 位作者，`https://arxiv.org/abs/2508.12801` | §相关工作 | 已核，arXiv API，2026-09-22 |
| 《Selective Sinkhorn Routing for Improved Sparse Mixture of Experts》 | arXiv:2511.08972，2025-11-12，Duc Anh Nguyen、Huu Binh Ta、Nhuan Le Duc、Tan Minh Nguyen 等 5 位作者，`https://arxiv.org/abs/2511.08972` | §相关工作 | 已核，arXiv API，2026-09-22 |
| 《MicroMoE: Fine-Grained Load Balancing for Mixture-of-Experts with Token Scheduling》 | arXiv:2511.16947，2025-11-21（v2 更新 2026-01-15），Chenqi Zhao、Wenfei Wu、Linhai Song、Yuchen Xu 等 5 位作者，`https://arxiv.org/abs/2511.16947` | §相关工作 | 已核，arXiv API，2026-09-22；arXiv 记录现标题为「Fine-grained MoE Load Balancing with Linear Programming」，与源文所引标题存在差异 |
| 《A Theoretical Framework for Auxiliary-Loss-Free Load Balancing of Sparse Mixture-of-Experts in Large-Scale AI Models》 | arXiv:2512.03915，2025-12-03，X. Y. Han、Yuan Zhong，`https://arxiv.org/abs/2512.03915` | §相关工作 | 已核，arXiv API，2026-09-22 |
| 《MoE环游记：2、不患寡而患不均》 | `https://spaces.ac.cn/archives/10735` | §方法回顾 | 站内前篇，原文快照在 `raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-2/` |
| 《MoE环游记：3、换个思路来分配》 | `https://spaces.ac.cn/archives/10757` | §方法回顾 | 站内前篇，原文快照在 `raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3/` |
| STE（Straight-Through Estimator） | 科学空间 `https://spaces.ac.cn/archives/6760#自行设计梯度` | §方法回顾 | 源文内链；站点对自动抓取返回 403 |

**外部工作在最优分配一支里的位置。** 用最优分配视角看 MoE 负载均衡最早见于 BASE Layers（2021），完整的一般解法由 BIP（2025）给出（§相关工作）。QB 改进自 BIP：把不等式约束改成等式约束，去掉非负截断。源文把 QB 比 BIP 之后的四条同向探索一并列出，并说明它们与本篇有重叠而各自不同（§相关工作）。BIP 的做法是先更新 `β` 再选 Top-`k`，作者指出这违反因果法则与训推一致原则；BIP 从最优分配角度所做的完整分析仍具启发意义（§相关工作）。

## 建立在前篇之上

- §方法回顾 复述第二篇的 Aux Loss 与第三篇的 Loss-Free，作为本篇的起点；文中对 Aux Loss 的两个批评（惩罚系数不好调、STE 梯度次优）指回第二篇与第二篇 §直通估计。
- 本篇是系列里 Quantile Balancing 首次出现的地方。第七篇 §一步求解 去掉「每个 Token 恰好激活 `k` 个」这一约束，得到只需一步 Quantile 的动态激活版本；第八篇 §最优之解 与 §滑动分位 在 QB 基础上做序列级 Moving Quantile Balancing；第七篇 §动态激活 还把第四篇凭直觉设计的 `s − β > 0` 激活规则从本篇的对偶目标重新推出。
- 本篇与第五篇之间的间隔是系列里最长的一段：第五篇发布于 2025-05-16（科学空间 10945），本篇发布于 2026-02-22（科学空间 11619），期间没有同系列文章。

## 作者与组

本篇引用块为「苏剑林. (Feb. 22, 2026). 《MoE环游记：6、最优分配促均衡》[Blog post]. Retrieved from `https://spaces.ac.cn/archives/11619`」。作者与组的完整背景见 [[moe-huanyouji-1-context|第一篇 增强信息]]。

## 关联

- [[moe-huanyouji-6-abstract|MoE环游记：6、最优分配促均衡 摘要]]
- [[moe-huanyouji-2-context|第二篇 增强信息]]：Aux Loss 与 STE 的出处
- [[moe-huanyouji-3-context|第三篇 增强信息]]：Loss-Free 的出处
- [[moe-huanyouji-7-context|第七篇 增强信息]]：系列内下一篇，QB 的动态激活一步解
