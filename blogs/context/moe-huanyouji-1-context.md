---
title: MoE环游记：1、从几何意义出发 增强信息
slug: moe-huanyouji-1-context
type: context
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-1/moe-huanyouji-1.extracted.md
  - raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-1/moe-huanyouji-1.html
resource: raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-1
---

# MoE环游记：1、从几何意义出发 增强信息

## 这一篇做了什么

《MoE环游记》系列的开篇（§开篇段），建立了一条从 Dense 模型逼近出发的 MoE 推导路线。走法六步，作者在 §思路概括 列成小节：

1. 常规 FFN 等价改写为 `n` 个小模型输出向量之和，每个小模型是一个 Expert（§问题定义，公式 (2)）；
2. MoE 的问题被写成「只挑 `k` 个向量之和去逼近 `n` 个向量之和」（§问题定义末引文框）；
3. 在 Expert 两两正交的近似下，最优挑法取模长 `‖v_i‖` 最大的 `k` 个（§模长排序，公式 (5)）；
4. 模长本身要先算出全部 Expert，于是重新设计 Expert：把 `v_i` 归一化为 `e_i`，另设 Router `h(xW^(R))` 预测模长 `ρ_i`（§MoE初现，公式 (6)）；
5. 最终形式为 `y = Σ_{i∈argtop_k ρ} ρ_i e_i`，先算 `ρ` 选前 `k` 个，再去算对应的 `e_i`（§MoE初现，公式 (7)）；
6. 这套形式比通行 MoE 多一步归一化，`ρ` 的几何意义是模长，激活函数因此没有归一化要求，Sigmoid、ReLU 与 Top-`k` 光滑近似都可用（§为何如此）。

## 引用谱系

本页建立的是系列内共享的引用账：后续各篇沿用这里的记录，只补自己那一跳新引的工作。

| 正文指称 | 出处 | 篇内落点 | 核验 |
|---|---|---|---|
| 「Transformer升级之路」系列 | 科学空间站内系列页 `https://spaces.ac.cn/search/Transformer升级之路/` | §开篇段 | 源文内链；站点对自动抓取返回 403 |
| DeepSeek-V3 | DeepSeek-V3 Technical Report，arXiv:2412.19437，2024-12-27，`https://arxiv.org/abs/2412.19437` | §开篇段 | 已核，arXiv API，2026-09-22 |
| 《Mixtral of Experts》 | arXiv:2401.04088，2024-01-08，`https://arxiv.org/abs/2401.04088` | §开篇段 | 已核，arXiv API，2026-09-22 |
| 《低秩近似之路（三）：CR》 | 科学空间 `https://spaces.ac.cn/archives/10427` | §模长排序 | 源文内链；站点对自动抓取返回 403 |
| 《Softmax后传：寻找Top-K的光滑近似》 | 科学空间 `https://spaces.ac.cn/archives/10373` | §为何如此 | 源文内链；站点对自动抓取返回 403 |
| 《Sparse Backpropagation for MoE Training》 | arXiv:2310.00811，2023-10-01，Liyuan Liu、Jianfeng Gao、Weizhu Chen，`https://arxiv.org/abs/2310.00811` | §为何如此 | 已核，arXiv API，2026-09-22 |

源文把上述 arXiv 条目链到 `papers.cool/arxiv/<编号>` 镜像；本页给 arXiv 规范地址，镜像地址与规范地址指向同一记录。

## 建立在前篇之上

这一篇是系列的第一发，没有前篇可沿用。它立下了后续各篇共用的记号与基线形式：

- `y = Σ_{i∈argtop_k ρ} ρ_i e_i` 成为第二篇（§需求分析）、第三篇（§方法大意）、第五篇（§共享专家）与第九篇（§问题描述）反复引用的基线；
- 「`ρ` 是 Router 打分、`e_i` 是 Expert 方向或输出」这一分工在第五篇 §共享专家 被明确回指；
- 「Expert 两两正交」这一假设在第五篇 §多种理解 被当作几何检验的起点，「学习减去均值后的残差，让正交假设更容易成立」正是第五篇解释 Shared Expert 的一条路径。

## 作者与组

**科学空间与苏剑林。** 科学空间是苏剑林维护的个人博客，站点 `spaces.ac.cn`（镜像域名 `kexue.fm`）。系列每篇文末自带引用块，给出作者、日期与文章编号；本篇的引用块为「苏剑林. (Feb. 08, 2025). 《MoE环游记：1、从几何意义出发》[Blog post]. Retrieved from `https://spaces.ac.cn/archives/10699`」。

**这个系列的来路与走向。** MoE环游记承接站内旧系列「Transformer升级之路」的体例（§开篇段），把同一种「自建推导路线、不做系统追根溯源」的写法用在 MoE 上（§问题定义 声明）。全系列九篇的写作顺序与主题：

| 篇 | 发布日 | 科学空间编号 | 主题 |
|---|---|---|---|
| 第一篇 | 2025-02-08 | 10699 | 几何视角推导 MoE 基本形式 |
| 第二篇 | 2025-02-21 | 10735 | Aux Loss 的来路与一般构造配方 |
| 第三篇 | 2025-03-05 | 10757 | DeepSeek 的 Loss-Free 负载均衡 |
| 第四篇 | 2025-03-28 | 10815 | 借 Bias 冗余自由度做动态激活 |
| 第五篇 | 2025-05-16 | 10945 | Shared Expert 与 Fine-Grained Expert |
| 第六篇 | 2026-02-22 | 11619 | 最优分配视角下的 Quantile Balancing |
| 第七篇 | 2026-02-23 | 11626 | 动态激活版 Quantile Balancing 一步解 |
| 第八篇 | 2026-05-22 | 11760 | 序列级均衡 Moving Quantile Balancing |
| 第九篇 | 2026-06-17 | 11782 | 门控归一化的概率推导 |

发布日取自各篇文末引用块。主题走向分两段：2025 年前五篇集中在 MoE 的静态形式与负载均衡，2026 年后四篇转向最优分配与序列级均衡。

**可核到的早期工作。** 苏剑林的公开署名工作在 Transformer 与优化两条线上：

- RoFormer: Enhanced Transformer with Rotary Position Embedding，arXiv:2104.09864，2021-04-20，苏剑林居首作者（`https://arxiv.org/abs/2104.09864`，arXiv API，2026-09-22）；旋转位置编码出自此文。
- Muon is Scalable for LLM Training，arXiv:2502.16982，2025-02-24，苏剑林居第二作者，共 28 位作者（`https://arxiv.org/abs/2502.16982`，arXiv API，2026-09-22）；优化器规模化的两条关键技术记录在摘要中。本系列第五篇 §比例因子 以「我们在《Muon is Scalable for LLM Training》提出」引用该文的比例因子做法。
- Moonshot AI 的 Kimi 系列技术报告作者表中出现同名作者，例如 arXiv:2501.12599（Kimi k1.5，2025-01-22）、arXiv:2507.20534（Kimi K2，2025-07-28）、arXiv:2510.26692（Kimi Linear，2025-10-30）（arXiv API，2026-09-22）。署名关系与任职机构是两个事实，本页只记录署名关系。

## 关联

- [[moe-huanyouji-1-abstract|MoE环游记：1、从几何意义出发 摘要]]
- [[moe-huanyouji-2-context|第二篇 增强信息]]：系列内下一篇
