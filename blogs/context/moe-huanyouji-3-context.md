---
title: MoE环游记：3、换个思路来分配 增强信息
slug: moe-huanyouji-3-context
type: context
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3/moe-huanyouji-3.extracted.md
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3/moe-huanyouji-3.html
resource: raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3
---

# MoE环游记：3、换个思路来分配 增强信息

## 这一篇做了什么

第三篇（2025-03-05，科学空间 10757）介绍 DeepSeek 的 Loss-Free 负载均衡，并把这条更新规则接回第二篇的 Aux Loss 推导。

- 做法：保留 Router 打分结果，改掉分配方式，把 `argtop_k ρ` 换成 `argtop_k(ρ + b)`，乘到 Expert 上的是 `ρ_i`（§方法大意，公式 (1)）。`b` 输入无关、不参与 MoE 前向计算、训练完成后固定，训练与推理形式一致。
- 更新规则：`b` 没有梯度，作者按第二篇的记号定义 `F`，照 STE 配方把优化参数换成 `b`（因为「增大 `b_i`，`i` 被选中的概率就更高」），推出梯度 `F − Q`，原论文最终取符号梯度下降 `b ← b − γ sign(F − Q)`（§手搓梯度，公式 (2) 至 (6)）。
- 结论：Loss-Free 的更新规则可以从 Aux Loss 视角得到，两条路线一脉相承（§一脉相承）。作者对 Loss-Free 本质的判断是：创新点落在「一个偏置项足以达到负载均衡」这一事实，因此把均衡与语言模型损失的优化参数隔离开，两者互不牵制（§一脉相承）。
- 两处改良：用 RMS Norm 替代 `sign`，保留 `F_i − Q_i` 的相对大小，减少已接近均衡的 Expert 来回震荡（§改良版本）；把加 `b` 的那路打分解耦为 Sigmoid、乘 Expert 的门控换别的单调非负激活，这样能继续复用 `γ = 0.001`（§相关细节）。
- 使用顺序：先用语言模型损失更新模型参数，再用新统计量更新 `b`，避免泄漏未来 token 的信息（§相关细节）。
- 遗留：`b` 的全体分量加同一个常数不改变排序，这个冗余自由度留到第四篇使用（§相关细节末段）。
- 延伸：同样的思路可用于 VQ-VQE 的编码表坍缩，并给出用梯度下降求解线性指派问题的一般图景（§延伸思考）。

## 引用谱系

| 正文指称 | 出处 | 篇内落点 | 核验 |
|---|---|---|---|
| 《Auxiliary-Loss-Free Load Balancing Strategy for Mixture-of-Experts》 | arXiv:2408.15664，2024-08-28，Lean Wang、Huazuo Gao、Chenggang Zhao、Xu Sun、Damai Dai，`https://arxiv.org/abs/2408.15664` | §方法大意 | 已核，arXiv API，2026-09-22 |
| BASE Layer | BASE Layers: Simplifying Training of Large, Sparse Models，arXiv:2103.16716，2021-03-30，Mike Lewis、Shruti Bhosale、Tim Dettmers、Naman Goyal、Luke Zettlemoyer，`https://arxiv.org/abs/2103.16716` | §方法大意 | 已核，arXiv API，2026-09-22 |
| 线性指派问题与匈牙利算法 | `https://en.wikipedia.org/wiki/Assignment_problem`、`https://en.wikipedia.org/wiki/Hungarian_algorithm` | §方法大意、§延伸思考 | 维基百科条目，源文内链 |
| 《MoE环游记：2、不患寡而患不均》 | `https://spaces.ac.cn/archives/10735` | §开篇段 | 站内前篇，原文快照在 `raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-2/` |
| 「旋转技巧」 | 科学空间 `https://spaces.ac.cn/archives/10489` | §延伸思考 | 源文内链；站点对自动抓取返回 403 |
| 「线性变换技巧」 | 科学空间 `https://spaces.ac.cn/archives/10519` | §延伸思考 | 源文内链；站点对自动抓取返回 403 |

**外部工作的谱系位置。** 在负载均衡的三条路线里，BASE Layer（2021）属于「最优分配」一支的早期尝试：把 Expert 分配视为线性指派问题，以负载均衡为约束求 Router 总打分最高的分配，可用匈牙利算法求解（§方法大意）。它的限制是求解需要全体 Token 的打分，因此只适用于训练，推理仍回到 `argtop_k ρ`，训练与推理形式不一，并且当时的求解算法只支持 `k = 1`（§方法大意）。DeepSeek 的 Loss-Free（2024）属于「Loss-Free」一支：不改 Router 打分，改排序方式，训练与推理同形（§方法大意）。第六篇把这两支合并到最优分配的框架里继续推进。

## 建立在前篇之上

- 沿用第二篇 §辅助损失 的记号 `F`、`F = E[f]` 与均匀分布 `Q`，也沿用第二篇 §直通估计 的 STE 配方。本篇的推进点是：第二篇用配方构造 Aux Loss，本篇用同一配方把 `b` 的更新规则从 Aux Loss 推出来，得到「两条路线梯度同源」的结论（§一脉相承）。
- 第二篇指出 Aux Loss 权重不好调（调低不促均衡、调高损害语言模型损失），本篇据此转入 Loss-Free 路线（§开篇段）；本篇同时指出 Loss-Free 也留了一个 `γ` 要调（§一脉相承）。
- 本页是系列里 Loss-Free 首次出现的地方。第五篇 §共享专家 说明 Loss-Free 的 `argtop_k ρ + b` 与 Shared Expert 正交；第八篇 §前文回顾 把 Loss-Free 拆成 DeepSeek 的 SignSGD 与本系列第六、七篇的 Quantile Balancing 两类。这些 Loss-Free 的一般事实都指回本页。

## 作者与组

本篇引用块为「苏剑林. (Mar. 05, 2025). 《MoE环游记：3、换个思路来分配》[Blog post]. Retrieved from `https://spaces.ac.cn/archives/10757`」。作者与组的完整背景见 [[moe-huanyouji-1-context|第一篇 增强信息]]。

本篇出现一处作者对该工作的评价，按判断记录：「潜在的学术影响力可能远超其他工作」（§方法大意）；理由在 §延伸思考 交代，落在 Loss-Free 思路的普适性上。

## 关联

- [[moe-huanyouji-3-abstract|MoE环游记：3、换个思路来分配 摘要]]
- [[moe-huanyouji-2-context|第二篇 增强信息]]：Aux Loss 与 STE 配方的出处
- [[moe-huanyouji-4-context|第四篇 增强信息]]：系列内下一篇，接走本页留下的 Bias 冗余自由度
