---
title: 负载均衡各代方案对照
slug: load-balancing-methods-comparison
type: comparison
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-2/moe-huanyouji-2.extracted.md
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3/moe-huanyouji-3.extracted.md
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/moe-huanyouji-6.extracted.md
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-7/moe-huanyouji-7.extracted.md
  - raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/moe-huanyouji-8.extracted.md
---

# 负载均衡各代方案对照

MoE（混合专家）训练时先按专家分配算力，再把 token 路由过去。token 是模型处理文本的最小单位，通常是一小段词或子词；专家是 MoE 层里并行小网络中的一个；Router 是从输入预测每个专家模长的小模型，模长记作 ρ，每个 token 走其中 k 个专家。分配不均会造出两类浪费：长期闲置的 Dead Expert 与过载丢弃 token 的 Token Drop，两类浪费的成因见 [[load-balancing-problem|负载不均衡的两类浪费]]。

本页用的记号与术语：Top-k 指按打分从高到低取前 k 个；F 是负载分布，也就是 Top-k 指示向量（选中的分量为 1/k、未选中的为 0）在全体 token 上的平均；P 是归一化打分在全体 token 上的平均；Q 是目标负载分布；γ 是偏置更新的学习率；SignSGD 指用符号做梯度下降的更新；直通估计的前向指正常算出输出，反向指算梯度；指数滑动平均的更新式是新值 = 系数 × 旧值 +（1 − 系数）× 当前值；MaxVio 指各专家负载相对均匀目标的最大偏差，是这条路线衡量均衡程度的指标，读数与条件见 [[maxvio|MaxVio：负载偏差的度量]]。

## 对照表

| 方案 | 分配规则 | 更新机制 | 需要调的超参数 | 均衡范围 | 主要缺口 |
|---|---|---|---|---|---|
| 辅助损失 Aux Loss | 打分归一化后按 Top-k 选，训练时加一项负载均衡损失 | 负载分布 F 与归一化打分均值 P 的内积 F·P，实现时用直通估计把不可导的 F 换成可导的 P | 损失权重系数 | 全局 | 权重难调，F·P 承载的是等效梯度，它数值下降与均衡改善是两件事 |
| Loss-Free | `argtop_k(ρ + b)`，b 是每个专家的输入无关偏置，乘到专家上的仍是 ρ | 无梯度偏置加符号更新 `b ← b − γ·sign(F − Q)`，目标分布 Q 均匀时每个分量取 1/n | γ = 0.001，与 Sigmoid 激活绑定 | 全局 | 偏置全局共享，恒定 γ 在分布畸形的层上很难实现均衡 |
| Quantile Balancing | 行偏置 α 与列偏置 β 两步交替：每行取 s 减列偏置后的第 k+1 大元素，每列取 s 减行偏置后的第 mk/n+1 大元素，两者都是 1 − k/n 分位数 | 从等式约束线性规划的对偶解直接读出偏置，推理只用 n 维的列偏置 β | 没有学习率要调 | 全局 | 需跨全体 token 找分位数，m 是全局样本数乘序列长度、一般百万量级；行偏置依赖全局批大小 |
| 一步分位数解 | 激活规则 `s − β > 0`，无需排序 | 每一列 β 的解析解是该列打分的 1 − k/n 分位数，用指数滑动平均平滑历史解 | 指数滑动平均系数 0.9 | 全局 | 一步最优解容易过拟合当前批次，β 的初始化对训练前几步敏感 |
| 序列级 Moving Quantile Balancing | 由分桶分布估计读出逐 token 的 β，Top-k 版本先削平 Router 的局部高峰再取 Top-k | 把 [0,1] 区间等分成 b 个桶做 one-hot，沿序列维度对分桶向量做指数滑动平均，由累积概率读出 1 − k/n 分位数 | 滑动平均系数 0.99、分桶数 100、强度系数 λ | 序列级 | 推理多一个 n×b 的 State；λ 取 1 时 Loss 差 0.06 |

## 超参数账

- Loss-Free 的学习率 γ 取 0.001，这个默认值与 Router 用 Sigmoid 激活绑定，换激活函数需要重调。
- Quantile Balancing 与一步分位数解没有学习率要调。
- 一步分位数解的指数滑动平均系数取 0.9。
- 序列级方案的滑动平均系数取 0.99，分桶数取 100。

## 五代方案的落点

辅助损失的来路与 F·P 的读数条件记在 [[auxiliary-loss]]，它把直通估计这条配方用在负载均衡上；[[straight-through-estimator]] 单独记那条配方。Loss-Free 把均衡交给无梯度的偏置 b，推导与两处改良记在 [[loss-free-balancing]]。Quantile Balancing 从对偶解给出两步交替的行偏置与列偏置，完整的线性规划推导记在 [[quantile-balancing]]。去掉逐 token 约束之后，一步分位数解给出闭式初始化与 EMA 平滑，这一步记在 [[one-step-quantile-solution]]。序列级 Moving Quantile Balancing 把偏置推到单条序列内部，分桶分布估计与强度系数 λ 的取舍记在 [[moving-quantile-balancing]]。

对照表的整体来路见系列精读 [[moe-huanyouji-reading|MoE环游记 系列精读]]。

## 效果与缺口

第一层 MoE 是负载最难均衡的一层，演示集中在这一层。数字上，SignSGD 版 Loss-Free 的 MaxVio 在五千步附近升到 2 左右，带大量尖峰升到 4，一万步后回落到 1 附近；Quantile Balancing 全程稳定在 0.6 至 0.7。用 Quantile Balancing 训练全 MoE 模型时第一层也会变得均衡；对原本 SignSGD 就能均衡的层，它通常没有优势。

序列级方案的实验配置是总参数量约 3B、128 选 4 的 MoE。λ 取 1 时第一层的 MaxVio 全程在 0.2 以下，代价是 Loss 比不加序列级均衡时差 0.06；把 λ 调到 0.3 左右，Loss 基本不掉，均衡仍在改善。

缺口写在明处：关键数字多来自作者自测的小模型（约 3B 一档），系列没有在大规模训练上复现 Quantile Balancing 与 Moving Quantile Balancing 的公开结果，这条缺口记成待做的延伸 [[reproduce-qb-mqb-at-scale|在稍大模型上复现 QB 与 MQB 的均衡收益]]。
