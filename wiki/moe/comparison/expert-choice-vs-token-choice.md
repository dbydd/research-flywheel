---
title: Expert Choice 与 Token Choice
slug: expert-choice-vs-token-choice
type: comparison
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-7/moe-huanyouji-7.extracted.md
  - raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/moe-huanyouji-8.extracted.md
---

# Expert Choice 与 Token Choice

两种分配方向。Expert Choice 指让专家去挑 token，Token Choice 指让 token 去挑专家。名词先立：token 是模型处理文本的最小单位，通常是一小段词或子词，也是全篇计量的单位；专家是 MoE（混合专家）层里并行小网络中的一个，MoE 把 Transformer 的 MLP 层换成这些并行的小网络；Router 是从输入预测每个专家模长的小模型；Top-k 指按打分从高到低取前 k 个；k 是每个 token 目标激活的专家数，m 是 token 总数，n 是专家总数。

## 朴素 Expert Choice 的两条约束

朴素的 Expert Choice 让每个专家挑 Top-mk/n 个 token，mk/n 是目标负载均匀时每个专家分到的 token 数。这个做法需要沿序列维度比较全体 token，由此同时破坏两条约束。

因果律指算某个位置的输出时看不到它之后的 token。token 一个接一个组成序列，沿整条序列比较会把后面 token 的信息带进前面的激活决策。

训推一致性指同一个输入在训练与推理下算出同一个结果。沿整条序列比较让训练与推理看到的信息不一致。

## 对照表

| 比较项 | 朴素 Expert Choice | Token Choice 的偏置形式 |
|---|---|---|
| 决策方 | 专家挑 token | token 挑专家 |
| 每步选择范围 | 每个专家挑 Top-mk/n 个 token | 每个 token 按阈值挑专家 |
| 需要比较的范围 | 沿序列维度比较全体 token | 当前 token 自己的打分 |
| 因果律 | 激活决策用到了后面的 token | 逐 token 决策，看不到后面的 token |
| 训推一致性 | 训练与推理看到的信息不一致 | 训练与推理同形 |
| 均衡的落点 | 每个专家恰好分到 mk/n 个 token | 偏置 β 承担均衡 |

## 偏置形式怎么修好它

一步分位数解给出修复的第一步：去掉「每个 token 恰好激活 k 个」这条约束之后，对偶问题里只剩偏置 β 一个变量，每一列上 β 的解析解是该列打分的 1 − k/n 分位数，激活规则简化成 `s − β > 0`，无需排序。s 是 token 对专家的打分矩阵；分位数指把打分按大小排序后按累积比例取的位置。这一步本质上是把 Expert Choice 写成 Token Choice，推导见 [[one-step-quantile-solution|一步分位数解与 EMA 平滑]]。

第二步落在更新的时机上。Bias 形式把 β 的更新放到激活决策之后，信息泄漏的入口被关上，前面 token 的决策用不到当前批的全部分位数结果，两步解里的这两个实用点记在 [[quantile-balancing|Quantile Balancing：对偶解与分位数]]。

序列级版本沿用同一方向。Moving Quantile Balancing 把分数落在的 [0,1] 区间等分成 b 个桶做 one-hot（向量里恰有一个分量为 1、其余为 0），沿序列维度做分桶向量的指数滑动平均，指数滑动平均的更新式是新值 = 系数 × 旧值 +（1 − 系数）× 当前值。这个运算是线性可并行的，逐 token 的偏置因此能并行算出，分桶分布估计的完整机制见 [[moving-quantile-balancing|Moving Quantile Balancing：序列级均衡]]。
