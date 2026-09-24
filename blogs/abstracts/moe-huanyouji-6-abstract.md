---
title: MoE环游记：6、最优分配促均衡
slug: moe-huanyouji-6-abstract
type: abstract
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/moe-huanyouji-6.extracted.md
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/moe-huanyouji-6.html
resource: raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6
---

# MoE环游记：6、最优分配促均衡

> [!quote] 官方摘要
> 我们知道，负载均衡（Load Balance）是MoE架构中基本且关键的一环，直接影响模型的效率和性能。本系列已经有两篇文章介绍了两种实现负载均衡的主流思路，分别是《MoE环游记：2、不患寡而患不均》介绍的经典方案Aux Loss，以及《MoE环游记：3、换个思路来分配》中的由DeepSeek提出的Loss-Free方案。……本文将探讨第三种思路：最优分配，它将负载均衡视为等式约束下的线性规划问题。

## 一句话判断

这一篇把负载均衡写成等式约束下的线性规划来解。约束有两项：每个 token 恰好激活 `k` 个 Expert，每个 Expert 恰好被激活 `mk/n` 次；在两项约束下最大化 Router 打分之和。松弛后交换 `max` 与 `min` 的顺序，交替最小化给出的解是——每行取 `s − β` 的第 `k+1` 大，每列取 `s − α` 的第 `mk/n+1` 大，两者都是对应维度上的 `1 − k/n` 分位数，方法因此叫 Quantile Balancing（QB）。推理阶段只保留 `n` 维的 `β`，`α` 的规模是全局 Batch Size，属于求解过程的中间量。QB 没有学习率一类的超参数要调，比 SignSGD 更稳更准，适用任意值域的 Router 分数，对第一层 MoE 这种最不均衡的层尤其快。文中的陷阱提示是：先用旧的 `β` 选出当前批的 Expert、再更新 `β`，否则会泄漏未来信息；实际使用形式从上一步的 `β` 出发、每步只迭代一次，避免过拟合当前批次。作者另附一段梯度下降的解法，在分数矩阵每行第 `k` 大与第 `k+1` 大不相等的条件下，它严格等同于 Loss-Free 的 SignSGD。与在先的 BIP 相比，QB 把不等式约束改成等式约束，去掉了 `α, β ≥ 0` 的截断操作；作者实测截断拖慢均衡速度，并且常常只能把过载的 Expert 压下去，救不回闲置的 Expert。

## 本体与去向

- 本体：`raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/`
- 图：`raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/assets/moe-huanyouji-6-fig1.png`（第一层 MoE 的 MaxVio 对比图，原文未编号，按正文顺序计为第 1 图）
- 精读：[[moe-huanyouji-reading|MoE环游记系列精读]]
- 系列：上一篇 [[moe-huanyouji-5-abstract|MoE环游记：5、均匀分布的反思]]；下一篇 [[moe-huanyouji-7-abstract|MoE环游记：7、动态激活极简解]]
