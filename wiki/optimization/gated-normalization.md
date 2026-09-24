---
title: 门控归一化：零中心 RMSNorm 与带门读
slug: gated-normalization
type: concept
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/qwen3.8-flash-next.extracted.md
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
---

# 门控归一化：零中心 RMSNorm 与带门读

归一化层的权重幅度与激活幅度共同决定训练稳定性。Qwen3.8-Flash-Next 在这两处各取一件：全模型的 RMSNorm 走零中心形式，残差块的读操作自带一道门。

## 零中心 RMSNorm

零中心 RMSNorm 把归一化权重零初始化，前向乘 $(1+w)$。这一形式限制归一化权重的增长，出自 Qwen3-Next 一线。全模型所有 RMSNorm 统一此式，包括 [[gated-deltanet|Gated DeltaNet]] 的头输出归一化。

## GatedNorm 与带门读

GatedNorm 是 RMSNorm 之后接一个低秩瓶颈自门的结构，用途是给激活幅度提供重标定。它在 [[gated-residual|Gated Residual]] 里折进块自身的归一化位置，读操作因此同时完成归一化与门控。这一件的出处是 Qiu 等《A Unified View of Attention and Residual Sinks: Outlier-Driven Rescaling is Essential for Transformer Training》。

## 隔离读数

单变量隔离实验固定 AdamW 与结构、取 3 倍学习率，只开关 GatedNorm：损失尖峰从每万步 32.0 降到 3.2，裁剪阈值穿越从 256 降到 20。无门基线的学习率阶梯显示残差最大激活随学习率近似线性增长、尖峰率涨得更快；带门 run 在最高学习率的激活水平低于无门基线在最低学习率的水平。

报告的机制读法把这条读数接到重标定上：高学习率训练需要一个重标定机制，无门网络靠养大激活 outlier 来间接完成、因此脆弱，乘性门直接把重标定供给出来。这套读数支撑[[training-stability-stress-test|压力测试]]里带门配置在 2 倍与 4 倍学习率下的零阈值穿越。
