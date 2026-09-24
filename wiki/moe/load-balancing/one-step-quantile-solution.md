---
title: 一步分位数解与 EMA 平滑
slug: one-step-quantile-solution
type: concept
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-7/moe-huanyouji-7.extracted.md
---

# 一步分位数解与 EMA 平滑

Quantile Balancing（QB）把负载均衡写成等式约束下的分配问题，用行偏置与列偏置两个乘子交替最小化求解（见 [[quantile-balancing]]）。《MoE环游记：7、动态激活极简解》砍掉其中一条约束，把解压到一步。这里的 token 是模型处理文本的最小单位，专家是 MoE 层里并行小网络中的一个，MoE 让每个 token 只走其中 k 个（见 [[moe-layer]]）。

## 省去逐 token 约束后只剩一个变量

约束「每个 token 恰好激活 k 个专家」在训练与推理里都可以省去，真正需要的是每个专家恰好被激活 mk/n 次，也就是平均每个 token 激活 k 个。

省去前一条约束后，对偶问题里只剩列偏置 β 一个变量，每一列上 β 的解析解就是该列打分的 1 − k/n 分位数。对偶指给每个约束配一个待定乘子、用乘子把约束并进目标函数来求解的办法；分位数指把样本按大小排序后按累积比例取的位置，累积分布到 1 − k/n 表示这一位置以上的样本占 k/n，正好对应每个专家被激活的目标比例。一步分位数直接给出最优解，激活规则也简化成 `s − β > 0`，无需排序。

## 用指数滑动平均压住批间抖动

一步最优解容易过拟合当前批，第七篇用 EMA（指数滑动平均）平滑历史解。指数滑动平均指用一个系数把历史值与当前值加权合并，更新式是 `新值 = 系数 × 旧值 +（1 − 系数）× 当前值`，实验中系数取 0.9。这个平滑手段改变的是解的稳定性，一步最优解本身的性质保持不变。

## 闭式初始化

初始化有闭式，也就是能一笔写出的显式表达式：在 Router 初始打分服从正态分布的假设下，β 取 `σ·Φ⁻¹(1 − k/n)`，其中 Router 是那个给每个专家预测模长的小模型，σ 是打分的标准差，Φ⁻¹ 是标准正态分布的分位数函数。正态分布是一条钟形曲线，标准差衡量它的宽窄。β 的取值对训练前几步敏感。

## 与 Expert Choice 的关系

第七篇给出一个概念上的理解：这条一步解本质上是把 Expert Choice 写成 Token Choice。Expert Choice 指让专家去挑 token，Token Choice 指让 token 去挑专家；朴素的 Expert Choice 让每个专家挑 Top-mk/n 个 token，需要沿序列维度比较全体 token，会破坏因果律与训推一致性。偏置形式把 β 的更新放到激活决策之后，信息泄漏的入口被关上（两条约束的细节见 [[expert-choice-vs-token-choice]]）。

## 与两步解的关系

QB 用行偏置与列偏置两个乘子交替最小化，分位数的计算跨全体 token 进行；一步解只留列偏置一个变量，每一列独立求分位数即可。推理阶段两者都用同一个 n 维偏置向量（见 [[quantile-balancing]]）。

## 退回到符号梯度下降

完全不用分位数时，对 β 的可导目标做符号梯度下降也行。符号梯度下降指每步只取梯度的符号来决定更新方向，这种用符号做梯度下降的更新在 Loss-Free 那一篇里叫 SignSGD（见 [[loss-free-balancing]]）。这条式子正是第四篇凭直觉给出的那一条。

第七篇只给了演示代码，没有公开的训练对照。序列级方案见 [[moving-quantile-balancing]]，各代方案的差别与超参数账见 [[load-balancing-methods-comparison]]；第七篇的原始论述见 [[moe-huanyouji-7-abstract|MoE环游记：7、动态激活极简解 摘要]]。
