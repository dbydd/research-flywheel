---
title: "NoPE：位置编码由 KDA 隐式提供"
slug: nope-position-encoding
type: concept
created: 2026-09-22
updated: 2026-09-22
sources:
  - papers/readings/2026-07/cs.CL/arXiv/kimi-k3-reading.md
  - raw/2026-07/cs.CL/arXiv/kimi-k3/kimi-k3.extracted.md
  - raw/2026-08/llm-architecture/spaces-ac-cn/k3-moe-attention/k3-moe-attention.extracted.md
---

# NoPE：位置编码由 KDA 隐式提供

NoPE（No Position Encoding）指注意力层在查询与键上不施加任何显式位置编码。注意力按查询与键的相似度给各值加权求和，本身不读位置下标。常规做法是在查询与键上叠加旋转位置编码（RoPE，把向量按位置角度旋转，使不同位置的向量内积带上相对距离），顺序信息由此进入模型。

Kimi K3 的 MLA 层全部走 NoPE。MLA（Multi-head Latent Attention，多头潜在注意力）把每个 token 的键值表示压成一个低维潜变量缓存起来，注意力计算时用学到的上投影重建内容键与内容值，全局的 token 到 token 注意力因此保留下来（结构见 [[gated-mla|Gated MLA]]）。这批层不加位置编码，提供不受位置限制的全局内容交互。位置敏感与近因感知的序列混合由中间的 KDA 层提供，KDA 是 Kimi 增量注意力，每个位置只保留一个固定大小的循环状态（见 [[kimi-delta-attention|Kimi Delta Attention]]）。两段分工合起来，序列混合与内容交互各由一类层承担。

## 扩上下文时省掉的动作

报告说这条分工省掉了扩上下文时改位置编码参数的动作，例如重调旋转位置编码的频率基，或施加 YaRN 一类外推（把位置角度的频率按缩放因子拉长，让训练期没见过的长位置落在已学过的范围内）。K3 因此直接外推到 100 万 token。

## 博客补充的机制理由

博客作者（Kimi 研究员苏剑林）对这一段给出了机制层的补充。K3 可以把旋转位置编码加回去，加上之后效果看不出变化，按最简洁的原则就不加了。一个全 MLA 的模型（例如 Kimi K2）去掉旋转位置编码会明显变差。K3 能用 NoPE，靠的是 KDA 与 MLA 的混合结构。

理由是一项等价推导。任意正交矩阵的幂都能用来构建广义的旋转位置编码：正交矩阵把向量做长度不变的旋转或反射，取它的幂次就得到随位置变化的旋转角度。常见做法选简单的旋转矩阵，PaTH 一类工作选 Householder 矩阵（一种由一个向量确定的反射矩阵）。在正交情形下，PaTH 可以等价地写成对查询与键各减去一个 DeltaNet 项之后的软最大化注意力；softmax 把一片分数变成一组总和为一的权重，DeltaNet 指让记忆状态按预测误差写入的线性注意力规则。这项等价表明，给查询与键加上 DeltaNet 就能起到类似位置编码的作用。KDA 属于更一般的 DeltaNet，KDA 与 MLA 混合的模型因此自带一种广义旋转位置编码。博客作者把这一点总结为 K3 的位置编码由 KDA 隐含提供。

## MLA 拼接维度的取舍

K3 的 MLA 保留拼接 64 维的做法，理由落在既有的 MLA 基础设施复用与计算量控制上。直接投影出 576 维潜变量再分出键与值的做法更简洁，代价是计算增加，效果收益很小；K3 已经引入 KDA 与注意力残差等新变量，MLA 上就不再动结构。博客作者把保留 MLA 的理由归成四条约束：效果不低于 MLA，训练与前填充成本不超过 MLA，KV 缓存比 MLA 小，解码算力比 MLA 小。他给出当前没有简单优雅的注意力设计能同时满足这四条的判断。
