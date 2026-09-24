---
title: Muon 的正交化配置：缩放式、迭代步数与系数表
slug: muon-orthogonalization-config
type: concept
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/qwen3.8-flash-next.extracted.md
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
  - papers/context/qwen3.8-flash-next-context.md
---

# Muon 的正交化配置：缩放式、迭代步数与系数表

Muon 把动量矩阵投到近似正交矩阵上，投影用 Newton–Schulz 迭代算。Qwen3.8-Flash-Next 的这套配置由四件定下：动量形式、正交化结果怎么缩放、迭代几步、逐步系数取哪张表。

## 动量与缩放式

Newton–Schulz 迭代跑在 Nesterov 加速动量（$\mu=0.95$）上。正交化结果按矩阵形状缩放，

$$
\gamma(A,B)=0.2\sqrt{\max(A,B)},
$$

使更新的均方根与矩阵形状无关。这一缩放式出自 Moonshot《Muon is Scalable for LLM Training》的式 (4)，动机是把 Muon 更新的均方根配到 AdamW 常见的 0.2–0.4 区间；Muon 自己的参考实现只按长宽比缩放，把更新乘 $(\max(1,A/B))^{0.5}$。

一处版面与抽取件的对账：抽取正文把 $\sqrt{}$ 丢成行首孤立的 `p`，回 PDF 版面核对根号存在，摘要页的同一处已按这一版面订正为 $0.2\sqrt{\max(A,B)}$，两页口径一致。

## 步数与系数表

迭代步数取 8，系数用 Polar Express 的逐步表。Polar Express 的表解的是给定步数预算下的极小极大问题，其主实验用 5 步、消融按损失判优到 6 步封顶。本件取 8 步的理由落在稳定性一侧：压力测试里梯度范数尖峰的幅度与频次都降，与 Polar Express 按损失判优的口径不同档。Frobenius 归一的数值稳定常数取 $10^{-14}$。

这份配置的两端接在别处：缩放式与迭代步数服务于[[muon-parameter-partitioning|Muon 的参数分工]]，8 步的稳定性理由在[[training-stability-stress-test|训练稳定性压力测试]]里兑现。
