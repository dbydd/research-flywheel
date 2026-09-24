---
title: 负载不均衡的两类浪费
slug: load-balancing-problem
type: concept
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-2/moe-huanyouji-2.extracted.md
---

# 负载不均衡的两类浪费

MoE（Mixture of Experts，混合专家）把 Transformer 的 MLP 层换成若干并行的小网络，每个 token 只走其中几个。MLP 是 Transformer 里的全连接前馈层；token 是模型处理文本的最小单位，通常是一小段词或子词；每个小网络就是一个 Expert；Router 是预测每个专家模长的小模型，输出一个与专家数同长的打分向量。这套结构的计算顺序是先按专家分配算力，再把 token 路由过去。这层结构与分配顺序的完整来历见 [[moe-layer|MoE 层：把 MLP 换成并行专家]]。

## 两类浪费

**Dead Expert。** 长期闲置的专家等于花了大参数的显存，只训出小参数的效果。它占着总参数量的份额，训练中拿到的 token 一再稀少，学到的能力停在很小的规模上。

**Token Drop。** 过载的专家装不下分给它的 token，只能丢弃其中一部分。被丢的 token 在这一层少一次计算，输入到输出的关系因此随负载波动。

两类浪费由同一次分配产生：算力事先按专家切好，token 按 Router 的打分流向少数几个热门专家，闲置与过载同时出现。

## 记号

把负载写成一组平均量，后来的辅助损失与偏置更新都在这组记号上做。

- 打分 `ρ`：Router 为每个 token 给出的 n 维输出，第 i 个分量是第 i 个专家的模长预测。
- 归一化打分 `p`：把一条 token 的打分除以这条 token 的全体打分之和，得到各分量之和为 1 的分布。
- Top-k 指示向量 `f`：长度为 n，被选中的 k 个分量取 `1/k`，未被选中的分量取 0。Top-k 指按打分从高到低取前 k 个。
- `P`：`p` 在全体 token 上的平均。
- `F`：`f` 在全体 token 上的平均。`F` 就是当前的负载分布，第 i 个分量是第 i 个专家平均被分配到的份额。

均匀目标是每个专家的份额都等于 `1/n`。`F` 里远大于 `1/n` 的分量对应过载的专家，远小于 `1/n` 的分量对应闲置的专家。这些份额与均匀目标之间的最大偏差由 [[maxvio|MaxVio：负载偏差的度量]]给出一个数字化的读数。

## 两条应对路线

通行的做法是加一个辅助损失项，推动 `F` 靠近均匀分布，见[[auxiliary-loss|Aux Loss 与 F·P 的来路]]。DeepSeek 换了一条路：保留 Router 的打分，给每个专家配一个可调偏置来改变分配，见[[loss-free-balancing|Loss-Free 负载均衡：偏置与符号更新]]。两条路线的记号与优化目标都落在上面这组平均量上。

出处：系列第二篇[[moe-huanyouji-2-abstract|MoE环游记：2、不患寡而患不均 摘要]]给出了两类浪费与这组记号的原始表述。
