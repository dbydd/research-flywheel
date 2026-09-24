---
title: MoE环游记：5、均匀分布的反思
slug: moe-huanyouji-5-abstract
type: abstract
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2025-05/moe/spaces-ac-cn/moe-huanyouji-5/moe-huanyouji-5.extracted.md
  - raw/2025-05/moe/spaces-ac-cn/moe-huanyouji-5/moe-huanyouji-5.html
resource: raw/2025-05/moe/spaces-ac-cn/moe-huanyouji-5
---

# MoE环游记：5、均匀分布的反思

> [!quote] 官方摘要
> 说到负载均衡，它无疑是MoE一个极为重要的目标，本系列的第2～4篇，可以说都在围绕着它展开。……抛开效率上的需求不谈，均匀分布就一定是效果最好的方向吗？本文就带着这个疑问，去理解Shared Expert、Fine-Grained Expert。

## 一句话判断

这一篇对“均匀分布就是最好的方向”提出反问，并拿 Shared Expert 与 Fine-Grained Expert 两件 DeepSeek 的改进来作答。Shared Expert 把 `n` 选 `k` 改成 `(n−s)` 选 `(k−s)`，另外 `s` 个 Expert 必然被选中，总参数量与激活量都保持不变，效果也有提升；这个技巧可以从残差视角、班主任类比、几何正交假设三个角度理解。Routed 与 Shared 之间的比例因子 `λ` 由“初始化阶段两者模长接近一致”数值模拟得到，脚本结果与 DeepSeek-V2 的 `λ = 16` 吻合；对 DeepSeek-V3 的配置，模拟给出约 2.83，实际取 2.5。Fine-Grained Expert 把每个 Expert 缩小一半、改成 `2n` 选 `2k`，组合数 `C(n,k)` 远小于 `C(2n,2k)`，作者另给一个解释——更细的颗粒度能更好地覆盖现实世界的非均匀性，文中用一张大小圆覆盖示意图说明。代价也很明显：`n` 增大后 Expert 之间的负载往往更不均衡，通信与协调成本也随之上升，所以存在一个效果与效率都友好的舒适区间。

## 本体与去向

- 本体：`raw/2025-05/moe/spaces-ac-cn/moe-huanyouji-5/`
- 图：`raw/2025-05/moe/spaces-ac-cn/moe-huanyouji-5/assets/moe-huanyouji-5-fig1.png`（大小圆覆盖对比示意图，原文未编号，按正文顺序计为第 1 图）
- 精读：[[moe-huanyouji-reading|MoE环游记系列精读]]
- 系列：上一篇 [[moe-huanyouji-4-abstract|MoE环游记：4、难处应当多投入]]；下一篇 [[moe-huanyouji-6-abstract|MoE环游记：6、最优分配促均衡]]
