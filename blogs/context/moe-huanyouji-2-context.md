---
title: MoE环游记：2、不患寡而患不均 增强信息
slug: moe-huanyouji-2-context
type: context
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-2/moe-huanyouji-2.extracted.md
  - raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-2/moe-huanyouji-2.html
resource: raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-2
---

# MoE环游记：2、不患寡而患不均 增强信息

## 这一篇做了什么

第二篇（2025-02-21，科学空间 10735）讨论负载均衡的第一条主流路线 Aux Loss，主要贡献是给这条沿用已久的损失补上来路。

- 需求侧：训练时先给每个 Expert 分配算力、再把 Token 路由过去，分配不均会造出 Dead Expert 与 Token Drop，两者都直接损失参数量与算力（§需求分析）。
- 记号：`p = ρ/Σρ` 为归一化 Router 打分，`f` 为 Top-`k` 指示向量的取值（选中为 `1/k`，未选中为 `0`），`P = E[p]`、`F = E[f]`（§辅助损失，公式 (1)）；
- 文献通用形式：`L_aux = F·P`，一般文献多乘一个 `n`（§辅助损失，公式 (2)）；
- 本篇补的推导：从「让 `F` 逼近均匀分布 `Q`」出发写 `½‖F − Q‖²`，用直通估计把不可导的 `F` 替换成 `P + sg[F − P]`，求梯度后恰好落在 `F·P` 上（§直通估计，公式 (3) 至 (5)）；
- 一般配方：先按想要的 `F` 构建损失，实现时做同一个替换；把目标换成熵的负值即可得到另一条可直接写进代码的 Aux Loss（§一般形式）；
- 读数条件：`F·P` 的意义落在等效梯度上，`F = P` 时它等于 `1/n`，还能构造出更小的值，训练中它数值下降与均衡程度改善是两件事（§直通估计末段）。

## 引用谱系

| 正文指称 | 出处 | 篇内落点 | 核验 |
|---|---|---|---|
| 《GShard: Scaling Giant Models with Conditional Computation and Automatic Sharding》 | arXiv:2006.16668，2020-06-30，Dmitry Lepikhin 等 9 位作者，`https://arxiv.org/abs/2006.16668` | §辅助损失 | 已核，arXiv API，2026-09-22 |
| STE（Straight-Through Estimator） | 科学空间 `https://spaces.ac.cn/archives/6760#自行设计梯度` | §直通估计 | 源文内链；站点对自动抓取返回 403 |
| 《MoE环游记：1、从几何意义出发》 | `https://spaces.ac.cn/archives/10699` | §开篇段、§需求分析 | 站内前篇，原文快照在 `raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-1/` |

**Aux Loss 的出处（本页首次交代，后续各篇指回本页）。** 主流使用的 Aux Loss 形式最早可追溯到 2020 年的 GShard（§辅助损失原文用语）。作者同时指出，既有文献与科普对这条损失的引用多为不加证明地沿用，他到手的资料里未见推导（§直通估计开篇段）。

## 建立在前篇之上

- 基线形式沿用第一篇（§需求分析 开头引用 `y = Σ_{i∈argtop_k ρ} ρ_i e_i`），并明确通用 MoE 与几何 MoE 只是理解视角的差别（§需求分析）。
- 本篇把负载均衡写成分布逼近问题，为系列后面几篇留下三个落点：第三篇 §手搓梯度 用同一套 STE 配方把 Loss-Free 的 SignSGD 更新规则从 Aux Loss 推出来；第六篇 §方法回顾 把 STE 取作 Aux Loss 梯度次优的论据；第八篇 §前文回顾 指出 Aux Loss 可以按序列、分组或全局层次调节均衡颗粒度。这些 Aux Loss 的一般事实都指回本页。

## 作者与组

本篇引用块为「苏剑林. (Feb. 21, 2025). 《MoE环游记：2、不患寡而患不均》[Blog post]. Retrieved from `https://spaces.ac.cn/archives/10735`」。作者与组的完整背景见 [[moe-huanyouji-1-context|第一篇 增强信息]] 的「作者与组」一节。本篇的写法特征是作者对通行结论提出疑问并自行补上证明：正文直言「对 Aux Loss 的引用都是不加证明的」，「反正笔者是没看出来」，随后给出自己的构造（§直通估计）。

## 关联

- [[moe-huanyouji-2-abstract|MoE环游记：2、不患寡而患不均 摘要]]
- [[moe-huanyouji-1-context|第一篇 增强信息]]：系列内上一篇，共用记号与作者背景的出处
- [[moe-huanyouji-3-context|第三篇 增强信息]]：系列内下一篇，Loss-Free 的 STE 推导接在本页
