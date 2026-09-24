---
title: 训练稳定性压力测试：小模型抬学习率复现大规模失稳
slug: training-stability-stress-test
type: concept
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/qwen3.8-flash-next.extracted.md
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
  - papers/context/qwen3.8-flash-next-context.md
---

# 训练稳定性压力测试：小模型抬学习率复现大规模失稳

大规模训练的失稳难以在目标规模上反复触发。压力测试用一条方法学绕开这一点：在中小模型上把学习率抬高，把失稳提前暴露。Qwen3.8-Flash-Next 用它验证新配方在同等压力下至少和已成功规模化的旧代一样稳。

## 压力测试读数

模型取 28 层 25B-A3B，学习率固定在最优值的 2 倍与 4 倍、绕过衰减。尖峰的定义是损失超过 201 步滚动中位数 0.1 以上。

2 倍处 AdamW 基线每万步 4.3 次尖峰，两种 Muon 配置 0.2 次。4 倍处 AdamW 每万步 183 次、19,932 步里 213 次撞 0.5 的裁剪阈值、裁剪器近乎常开，两条 Muon run 一次未撞阈值，带 [[gated-residual|Gated Residual]] 的配置零损失尖峰。差异在 4 倍这一档变成量级上的分离。

## 门的单变量隔离

单变量隔离实验固定 AdamW 与结构、取 3 倍学习率，只开关 [[gated-normalization|GatedNorm]]：尖峰从每万步 32.0 降到 3.2，阈值穿越从 256 降到 20。

无门基线的学习率阶梯显示激活 outlier 随学习率近似线性增长、尖峰率涨得更快；带门 run 在最高学习率的 outlier 水平低于无门基线在最低学习率的水平。报告的机制读法：高学习率训练需要一个重标定机制，无门网络靠养大激活 outlier 来间接完成、因此脆弱，乘性门直接把重标定供给出来。

![[raw/2026-09/llm-architecture/github/qwen3.8-flash-next/assets/qwen3.8-flash-next-fig12-gate-isolation.png]]

> **门控单变量隔离图**（技术报告 Figure 12）(a)(b) 3 倍学习率下 GatedNorm 开关对损失与未裁剪梯度范数；(c) 无门基线在 1×、2×、3× 学习率的残差最大激活阶梯与带门对照。

## 生产规模验证

前 276B token、同数据序、同学率日程、同优化器的三件对照：Qwen3.5 结构加 Muon 为基线，加 GR 降 0.026，整套 Flash-Next 配方再降 0.032，合计 0.058。梯度范数上纯 Muon 的中位数约为两条带门 run 的两倍、p99.9 是 4.2 倍（0.097/0.298 对 0.053/0.071 与 0.043/0.066），且是唯一撞过裁剪阈值的；带门 run 在 1000 步窗内的标准差低 4.3–4.7 倍。残差最大激活加 GR 后全网一致下降、各探测深度同形：无 GR 的 Muon 基线冲到约 4300，Flash-Next 约 800–900，加 GR 的 Qwen3.5 约 300–400。报告猜「把残差读与 LM 头前最后一次归一化融成一个带门读操作」是 Flash-Next 对 Muon 加 GR 差值的主贡献者，标注为猜想。

![[raw/2026-09/llm-architecture/github/qwen3.8-flash-next/assets/qwen3.8-flash-next-fig13-production.png]]

> **生产早期对照图**（技术报告 Figure 13）(a) 三件 run 的损失随消耗 token，插图放大 160B–270B 段；(b) 未裁剪梯度范数与 1000 步滚动窗标准差；(c) 残差最大激活。

整训全程零损失尖峰、零梯度范数异常，未用 qk-clip 或 SwiGLU-clip 这类显式激活控制。压力测试的结论在 8 倍模型规模与生产学习率下复现，这条余量是[[batch-size-and-lr-scaling-refit|缩放律重拟合]]把超参推高的前提。

方法学出自 Wortsman 等《Small-scale proxies for large-scale transformer training instabilities》，做法是在小模型上抬学习率复现大模型失稳。
