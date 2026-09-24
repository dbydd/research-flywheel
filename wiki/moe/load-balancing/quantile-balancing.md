---
title: Quantile Balancing：对偶解与分位数
slug: quantile-balancing
type: concept
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/moe-huanyouji-6.extracted.md
  - papers/readings/2026-07/cs.CL/arXiv/kimi-k3-reading.md
  - raw/2026-07/cs.CL/arXiv/kimi-k3/kimi-k3.extracted.md
---

# Quantile Balancing：对偶解与分位数

MoE（Mixture of Experts，混合专家）层把 Transformer 里的 MLP 换成若干并行的小网络，每个 token 只走其中 k 个。token 是模型处理文本的最小单位，通常是一小段词或子词；每个小网络是一个 Expert。基线形式写作 `y = Σ_{i∈argtop_k ρ} ρ_i e_i`，其中 ρ_i 是 Router 预测的模长、e_i 是专家方向，Router 是那个从输入预测各专家模长的小模型（这套形式见 [[router-magnitude-direction]]）。负载分配不均会造出过量丢弃 token 与长期闲置的专家两类浪费（见 [[load-balancing-problem]]）。

## 把均衡写成等式约束下的线性规划

《MoE环游记：6、最优分配促均衡》把负载均衡写成一个分配问题：有 m 个 token、n 个专家，打分矩阵记 s，约定每个 token 恰好激活 k 个专家，每个专家恰好被激活 mk/n 次，在这个约束下求总分最高的分配方案。线性规划指目标函数与约束条件都关于决策变量线性的优化问题。

求解走的是对偶。对偶指给每个约束配一个待定乘子，用乘子把约束并进目标函数，把带约束问题改写成对乘子求极值的问题。第六篇按 token 的乘子记 α、按专家的乘子记 β。乘子乘上约束再加进目标函数后，原问题变成不带约束的极大极小问题；极大极小是一对交换了求极值顺序的问题，线性目标与凸可行集满足极大极小定理的条件，max 与 min 可以交换顺序。

交换后每个分配变量的取值由 s 减去两个乘子之和的符号决定，整个问题分裂成 m 个独立子问题交替最小化。α 与 β 在分配里起的作用是给每个 token 与每个专家各配一个可调修正量，它们就是后文所说的行偏置与列偏置。

## 解落在分位数上

解的形式很干净：每一行取 s 减去列偏置后的第 k+1 大元素，每一列取 s 减去行偏置后的第 mk/n+1 大元素。两者都是对应维度的 1 − k/n 分位数。

分位数指把样本按大小排序后按累积比例取的位置；累积分布到 1 − k/n 表示这一位置以上的样本占 k/n，正好对应每个专家被激活的目标比例。两种取法说的是同一件事：第 k+1 大元素上面恰有 k 个元素，占一行 n 个元素的 k/n；第 mk/n+1 大元素上面恰有 mk/n 个元素，占一列 m 个元素的 k/n。方法因此叫 Quantile Balancing（QB）。

## 推理阶段只用列偏置

推理阶段只用 n 维的列偏置 β。行偏置 α 的规模等于全局批大小，也就是一次训练步里一起处理的全体样本数乘序列长度，属于求解过程的中间量。

两个实用点：先用旧的 β 选出当前批的专家，再更新 β，避免泄漏未来 token 的信息；实际使用从上一步的 β 出发，每步只迭代一次，避免过拟合当前批次。

## K3 的落地形式

Kimi K3 走免辅助损失的路由，负载均衡靠给路由分数加一个专家偏置。路由分数取 `s_i = Sigmoid(W_r x_i)`，按 `s_i + b` 做 Top-k 选择，混合权重 `p_{i,j}` 用原始分数归一化，偏置只调节派发，不改变混合权重，也不进入路由器的梯度优化。

每个 token 在带偏置的分数上把 Top-k 换成 Top-(k+1)，前 k 个是实际走的路由，第 (k+1) 个是 token 要进 Top-k 必须越过的截断值 `α_i`。边缘量指某个 token 的路由分数减去该 token 的截断值，即 `s_{i,j} - α_i`。固定截断值，专家 j 在候选偏置下收到的 token 数随门槛单调下降，把门槛设到目标负载 q 就让第 (q+1) 大的边缘量落在门槛上；目标负载 `q := mk/n` 除以批内 token 数得到比例 `k/n`，离散计数的门槛就是专家 j 这一列边缘量的 `1 − k/n` 分位数。所需偏置 `r_{i,j} := α_i − s_{i,j}` 与边缘量相差一个负号，`r_{:,j}` 的 `k/n` 分位数与负的 `(s_{:,j} − α)` 的 `1 − k/n` 分位数是同一个数。更新写成

$$
\widehat{b}_j^{(t+1)}\leftarrow-\operatorname{quantile}_{1-k/n}\!\left(\boldsymbol{s}_{:,j}-\boldsymbol{\alpha}^{(t)}\right),\qquad \boldsymbol{b}^{(t+1)}\leftarrow\widehat{\boldsymbol{b}}^{(t+1)}-\operatorname{mean}\!\left(\widehat{\boldsymbol{b}}^{(t+1)}\right)\mathbf{1}.
$$

旧偏置只通过截断值进入更新，第二行减掉公共偏移，Top-k 选择不变；更新只在下一步生效，一个批不会用由它自己导出的偏置来路由；推理时偏置冻结。

Kimi K2 走的是 [[loss-free-balancing|Loss-Free 负载均衡]] 里那条符号梯度一步，专家总数涨到 896 之后这条固定步规则不够稳。K3 的这条形式把偏置直接钉到与目标负载匹配的分位数上，没有学习率式超参，在将近一千个专家时仍能在少数几步内收敛。全批分位数要跨数百万 token 聚合，K3 的落地方案是逐专家的分 bin 直方图估计，见 [[quantile-histogram-estimation|分位数均衡的直方图估计]]。

## 谱系与改动

用最优分配视角看负载均衡最早见于 BASE Layers 那篇（arXiv:2103.16716），完整的一般解法由整数规划那篇（arXiv:2502.15451）给出。QB 相对它的改动是把不等式约束换成等式约束，去掉非负截断。作者实测这个截断拖慢均衡速度，并且常常只能把过载的专家压下去，救不回闲置的专家。

这条路线用 [[maxvio]] 度量均衡程度。省去「每个 token 恰好激活 k 个」这条约束得到一步解，见 [[one-step-quantile-solution]]；把偏置从全局推到序列级得到 Moving Quantile Balancing，见 [[moving-quantile-balancing]]。

## 代价

QB 需要跨全体 token 找分位数，m 等于全局样本数乘序列长度，一般是百万量级，精确实现在各种并行策略与梯度累积下难以接受，实际用最大可接受的小批次折中，K3 把这层估计换成逐专家的分 bin 直方图，通信与 token 数解耦，见 [[quantile-histogram-estimation|分位数均衡的直方图估计]]。行偏置 α 依赖全局批大小，不能带进推理。把这条对偶解搬到别的稀疏选择结构上，是本仓记下的一条延伸，见 [[quantile-balancing-beyond-moe|分位数对偶解搬到别的稀疏选择]]。

各代方案的差别与超参数账见 [[load-balancing-methods-comparison]]；第六篇的原始论述见 [[moe-huanyouji-6-abstract|MoE环游记：6、最优分配促均衡 摘要]]，系列全景见 [[moe-huanyouji-reading|MoE环游记 系列精读]]。
