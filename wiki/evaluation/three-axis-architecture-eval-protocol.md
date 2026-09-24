---
title: 三轴架构评估协议：损失、三段成本、超参与稳定性
slug: three-axis-architecture-eval-protocol
type: concept
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/qwen3.8-flash-next.extracted.md
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
---

# 三轴架构评估协议：损失、三段成本、超参与稳定性

一个架构改动的价值由多条量共同决定。损失单看会漏掉能力退化，基准单看会漏掉效率代价，效率单看会漏掉训练稳定性。三轴架构评估协议把每个候选改动同时放上三条轴读，是 Qwen3.8-Flash-Next 技术报告的方法论主张。

## 三条轴

第一条轴是损失与下游基准一起看。第二条轴是改动在训练、前填充（把整段输入一次性算进模型）、解码（逐 token 生成）三段的成本分开看。第三条轴是改动对最优超参与训练稳定性的影响单独看。报告全文的叙事单元是「一处改动加三轴读数」。

## 被协议拦下的三条捷径

作者把这些轴互相矛盾之处写进报告正文：损失与下游精度分道扬镳的地方、预训练指标干净而后训练才退化的地方、白花优化步的惯例。结论一节把拦下的三条看似无害的捷径列成清单。

第一条是只在预训练无损的稀疏读写。[[gated-residual|Gated Residual]] 的稀疏读写变体（每块只读门值最高的两支）在预训练损失与基准上几乎无损，后训练之后质量明显退化，改变稀疏度也不解决。

第二条是在预训练看不出差别的位置编码删除。[[rope-vs-nope-evidence-axes|RoPE 与 NoPE]] 在预训练阶段读数同型，NoPE 变体在后训练之后 endless generation 率明显升高、更容易不终止。

第三条是多花 18.8% 优化步的批量 warmup。两条 ramp 曲线落在 run-to-run 方差内，[[batch-size-and-lr-scaling-refit|缩放律重拟合]]之后判废。

## 一条同轴的读法

损失与下游分道扬镳在[[wide-residual-stream|加宽残差流]]的静态到动态一步也现形：损失只再降 0.002，九项均值涨 1.98 分。损失单独看会低估这步改动的价值，这条读法正是协议第一条轴要拦的东西。

## 作者给下一步定的瓶颈

报告展望点名的瓶颈在评估侧：一个能可靠预测后训练排序的更便宜中规模探针会让设计空间更好搜。这份报告的可复用产出对做架构的人是那几张消融表的数字，对做流程的人是这套协议。
