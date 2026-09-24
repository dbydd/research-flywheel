---
title: 动态激活：按难度浮动激活数
slug: dynamic-activation
type: concept
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-4/moe-huanyouji-4.extracted.md
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-7/moe-huanyouji-7.extracted.md
---

# 动态激活：按难度浮动激活数

出发点：每个 token 的难度不同，难的 token 应当多配专家。激活数从全局固定的 k 变成逐 token 浮动的整数，负载均衡与预算控制在同一次更新里管住。token 是模型处理文本的最小单位，k 是此前固定的激活专家数。

## 继承来的自由度

更新规则先从偏置路线接过来，见[[loss-free-balancing|Loss-Free 负载均衡：偏置与符号更新]]。做法是先把更新规则整体去均值，腾出「全体偏置同加一个常数不影响排序」这条冗余自由度。偏置的绝对大小由此空出来，可以承载别的信息，激活数就是其中一项。

## 激活规则

挑选规则从 `argtop_k(ρ + b)` 改成 `argwhere(ρ + b > 0)`：`ρ` 是 Router 打分，`b` 是专家偏置，`ρ + b` 为正的专家全部选中，为负的全部跳过。`argtop_k` 取打分加偏置的前 k 个分量对应的专家编号，数量固定为 k；`argwhere` 取出所有满足条件的专家编号，数量随 token 浮动。每个 token 激活的专家数量随其难度浮动，排序这一步同时被免掉。

## 更新目标

更新规则同时管两件事：

- 负载分布逼近均匀。
- 平均激活数逼近 k，作预算控制。预算控制指把每层每个 token 的平均激活数压在 k 附近，算力开销因此与原方案持平。

两项都由偏差的符号驱动：符号梯度用偏差的符号代替偏差本身，把更新幅度固定成一个步长。作者把两件事合并化简成一步符号梯度。未合并的版本由三段组成，分别是负载均衡项、去均值项与预算控制项。实测它在训练前期的均衡与预算抖动更小，合并成一步的版本抖动更大。

## 初始化

初始阶段 `b` 取零会让每个 token 选满所有专家，造成大量 Token Drop，见[[load-balancing-problem|负载不均衡的两类浪费]]。选满所有专家意味着这一层退化成全量计算，过载的专家装不下分给它的 token，只能丢弃一部分。第四篇给出一个脚本，在 Router logits 近似正态分布的假设下用模拟与二分法估计初始 `b`。Router logits 指 Router 输出的未归一化打分；正态分布是由均值与标准差确定的钟形分布；二分法是反复折半搜索区间、逐步逼近目标值的数值方法。

## 后续

第七篇把这条凭直觉给出的激活规则变成对偶解的推论，激活条件写成打分减阈值大于零，见[[one-step-quantile-solution|一步分位数解与 EMA 平滑]]。同一支的其它做法见[[sparse-routing-alternatives|稀疏路由的替代路线]]。

出处：系列第四篇[[moe-huanyouji-4-abstract|MoE环游记：4、难处应当多投入 摘要]]，后续一节另参第七篇[[moe-huanyouji-7-abstract|MoE环游记：7、动态激活极简解 摘要]]。
