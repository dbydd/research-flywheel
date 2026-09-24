---
title: MoE环游记：1、从几何意义出发
slug: moe-huanyouji-1-abstract
type: abstract
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-1/moe-huanyouji-1.extracted.md
  - raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-1/moe-huanyouji-1.html
resource: raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-1
---

# MoE环游记：1、从几何意义出发

> [!quote] 官方摘要
> 前两年福至心灵之下，开了一个“Transformer升级之路”系列，陆续分享了主流Transformer架构的一些改进工作和个人思考，得到了部份读者的认可。这篇文章开始，我们沿着同样的风格，介绍当前另一个主流架构MoE（Mixture of Experts）。

## 一句话判断

这一篇从几何逼近的角度给出一条自洽的 MoE 推导路线。起点是：单个 FFN 可以等价改写成 `n` 个 Expert 向量之和 `Σ v_i`，于是 MoE 的问题变成“只用其中 `k` 个之和去逼近原本 `n` 个之和”。在 Expert 两两正交的近似下，最优挑法是取模长 `‖v_i‖` 最大的 `k` 个。这条规则本身不省算力，因为算出模长就要先算出全部 Expert；绕开的办法是把每个 Expert 重参数化为 `ρ_i e_i`，让低成本的 Router 先预测模长 `ρ_i`，方向 `e_i` 做归一化，于是 `y = Σ_{i∈argtop_k ρ} ρ_i e_i`，先算 `ρ` 选前 `k` 个、再去算对应的 `e_i`。这样推出来的 MoE 比常见形式多一步归一化。读数上要注意 `ρ` 在这里的几何意义是模长，激活函数因此没有归一化要求，Sigmoid、ReLU 以及 Top-`k` 光滑近似都可以用；实现里 L2 Normalize 可以换成 gamma 恒等于 1 的 RMS Norm。

## 本体与去向

- 本体：`raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-1/`
- 精读：[[moe-huanyouji-reading|MoE环游记系列精读]]
- 系列：下一篇 [[moe-huanyouji-2-abstract|MoE环游记：2、不患寡而患不均]]
