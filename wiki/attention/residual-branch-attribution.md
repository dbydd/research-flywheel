---
title: 残差支路归因：把跨层信息流拆成份额
slug: residual-branch-attribution
type: concept
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/qwen3.8-flash-next.extracted.md
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
---

# 残差支路归因：把跨层信息流拆成份额

[[gated-residual|Gated Residual]] 删掉支路间混合矩阵之后，每支残差流成为一个纯累加器，块之间的信息流可以精确算出。这份归因把「加宽流上到底谁读到谁」从直觉变成可读的量。

## 分解与统计量

块 $u$ 对块 $v$ 输入的贡献是

$$
a_{u\to v}=\frac{1}{n_r}\sum_{c=1}^{n_r}G_c^{(v)}\odot\gamma_c\odot\frac{s_c^{(u)}y^{(u)}}{\mathrm{rms}(R_c^{(v)})},
$$

归一化份额

$$
\pi_{uv}=\frac{\lVert a_{u\to v}\rVert}{\sum_{u'<v}\lVert a_{u'\to v}\rVert}.
$$

每个读者的份额之和与 1 的偏差在 $3\times10^{-8}$ 以内。对照件是 20 层 MoE 加 GR 对同配方、同数据、同优化器、同步数的无 GR 参照，统计量取份额差 $\Delta_{uv}$，减掉参照是为了剥掉「近邻写者支配」这条所有残差网络共有的模式。

![[raw/2026-09/llm-architecture/github/qwen3.8-flash-next/assets/qwen3.8-flash-next-fig7.png]]

> **GR 跨层路径图**（技术报告 Figure 7）四行对应四条残差支路，连线从写者子层指向读者子层，线宽与透明度编码 $\Delta_{uv}$，阴影列是每四层一个的 softmax 注意力层；b0 行整条长程支路都从第 0 层出发、落在第 10 层之后。

## 读数

图里画 780 个有序对里 $\Delta_{uv}\ge0.05$ 且跳层至少 1 层的 21 条路径。标尺：第 15 层有 30 个写者、均分各约 0.03，份额 0.13 是均分的四倍。五个 GR checkpoint 各有一条长程支路，典型跳层 10.9，其余三支 3.4–3.9。

三条样例给出分工的形状。第 0 层 GDN 输出到第 15 层注意力的份额从 0.020 涨到 0.138，且在第 10 到 19 层的每个读者身上保持 0.072–0.138、无衰减趋势。第 10 层 GDN 到第 11 层注意力 $\Delta_{uv}=0.117$，单层跳同样强化，GR 同时加强短程。第 0 层 MLP 同时走长程（0.008→0.058）与局部（0.139→0.192）两条支路，同一份输出以不同强度到达近读者与远读者；单流网络每个写者只有一种衰减率、表达不出这种分层。

按跳层分组求和：跳 1 层共涨 0.96，跳 12 层以上共涨 0.91，跳 2–12 层共跌 3.21；加权平均跳层 3.97 对 3.91。跨层信息总量近似守恒，变的是分布——GR 选中少数路径放大，资金来源是中程。读 GR 支路最重的子层集中在 softmax 注意力层，报告的读法是全局注意力承担整合的角色：它把 [[gated-deltanet|GDN]] 压缩掉的显式长程历史重新整合进残差流。
