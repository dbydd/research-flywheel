---
title: 门控的概率梯度推导
slug: gating-policy-gradient
type: concept
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2026-06/moe/spaces-ac-cn/moe-huanyouji-9/moe-huanyouji-9.extracted.md
---

# 门控的概率梯度推导

本页记第九篇从梯度一侧给出的推导，它回答的是门控要不要归一化。术语先立起来：MoE（混合专家）把 Transformer 里的 MLP 层换成若干并行的小网络，每个 token 走其中几个；token 是模型处理文本的最小单位，通常是一小段词或子词；Router 是从输入预测每个专家模长的小模型，它给出的模长记作 ρ；Gate 是乘到专家输出上的那份权重，作用是在训练时为 Router 提供梯度；专家记作 `e_i`，它对应的损失记作 `L_i`。

概率一侧的术语。KL 散度是衡量两个概率分布差异的量，两个分布越接近取值越小。熵刻画一个分布的分散程度，分布越集中熵越小，负熵是把熵取负号之后的量。策略梯度是用采样得到的回报为概率分布估梯度的思路，REINFORCE 是其中一种，做法是从分布里采一个专家来估计梯度，噪声偏大。baseline 指一个与所选专家无关的基准值，从回报里减掉它不改变梯度的期望，同时把噪声压下去。一阶泰勒展开指在零点附近用一阶导数的线性项近似损失。直通估计的前向指正常算出输出，反向指算梯度。Top-k 指按打分从高到低取前 k 个专家。

## 从 KL 散度到等效损失

推导从 k = 1 出发：每个 token 恰好激活一个专家，被激活的专家应当是损失最小的那一个。先构造一个基于损失的目标分布 q，它把概率集中在损失小的专家上；另有基于 ρ 的预测分布 p。目标是最小化两者的 KL 散度。展开后其中一项是 p 的负熵，负载均衡已经承担了鼓励模型多试不同专家的作用，这一项的活儿由负载均衡那一侧接走；另一项与参数无关，可以省去。由此得到的等效损失是 p 对专家损失的加权和，写作 `Σ_i p_i L_i`。

这条等效损失的梯度正是策略梯度里的 REINFORCE。对减 baseline 的 REINFORCE 做一阶泰勒展开，得到一条直通估计：前向用 1，反向用 `log p_i`。这条估计的两侧算法不一致，前后向不一致。

## 换成 p_i·e_i 之后

关键的改进是把每个专家从 `e_i` 换成 `p_i·e_i`。重复同一推导，停止梯度项自动消失，前后向恢复一致。换过之后，乘到专家输出上的系数带上预测分布 p 的形式，由这条推导读出的归一化结论记在 [[gating-normalization|门控归一化的三选一]]。

这条推导给出两件事：需要一个自上而下的概率推导时，门控应当归一化并且不应当 Re-Norm；Gate 在反向传播里的梯度落在 `log p_i` 这一侧。

## 局限

k = 2 时概率框架给不出精确推导；这条推导走的是 k = 1 的情形，也就是每个 token 恰好激活一个专家。采样与 Top-k 的差异是多样性与稳定性的权衡，文中没有给出采样方案的实验。三部曲的形式化偏重，作者也提到操作上受约束。

## 与最优分配框架的接口

k = 1 处，概率框架给出的归一化门控与最优分配框架给出的偏置阈值指向同一个选择。最优分配框架从等式约束的线性规划对偶解出发，把每一列的 1 − k/n 分位数当作偏置阈值（两步解见 [[quantile-balancing|Quantile Balancing：对偶解与分位数]]，一步解见 [[one-step-quantile-solution|一步分位数解与 EMA 平滑]]）。把两套语言在 k 大于 1 处统一起来是本系列留下的一处空白，本仓把这条空白记成一句待验证的提法 [[unify-gating-and-assignment-frameworks|在 k 大于 1 处统一概率框架与最优分配框架]]。

## 出处

这条推导出自刘力源的三部曲：《Bridging Discrete and Backpropagation: Straight-Through and Beyond》（arXiv:2304.08612）、《Sparse Backpropagation for MoE Training》（arXiv:2310.00811）与《GRIN: GRadient-INformed MoE》（arXiv:2409.12136）。第九篇对三部曲做了提炼与改写，并把它接到本系列的几何视角上。[[moe-huanyouji-9-abstract|MoE环游记：9、门控归一化之争 摘要]] 这条推导在本系列里的位置见 [[moe-huanyouji-reading|MoE环游记 系列精读]]。

直通估计这套前向与反向分离的写法在负载均衡一侧同样被复用，Aux Loss 的推导与偏置更新都落在同一条配方上，配方本身单独成页 [[straight-through-estimator|直通估计与 F 换 P 的配方]]。
