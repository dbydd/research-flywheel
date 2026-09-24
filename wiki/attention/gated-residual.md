---
title: Gated Residual：四支加宽残差流上的逐元素读门
slug: gated-residual
type: concept
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/qwen3.8-flash-next.extracted.md
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/hf_config.json
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
  - papers/context/qwen3.8-flash-next-context.md
---

# Gated Residual：四支加宽残差流上的逐元素读门

Gated Residual（GR）是 Qwen3.8-Flash-Next 的残差设计，属于 [[wide-residual-stream|加宽残差流]] 一族。它把残差流加宽到 4 支，读用逐元素的数据相关门，写用每支一个标量，支路之间不再混合。这份取法把表达力全部放在读侧，写侧保持低自由度，混合矩阵整个删掉。

## 算子形状

每支先独立归一化，每支一份增益 $\gamma_i\in\mathbb{R}^d$。读门从全部支路预测、逐支逐通道，经一个低秩瓶颈：

$$
\hat{R}_i=\mathrm{RMSNorm}(R_i;\gamma_i),\qquad
G=\mathrm{unvec}\!\left(\sigma\!\left(W_u\,\mathrm{SiLU}\!\left(\tfrac{1}{n_r}W_d\,\mathrm{vec}(\hat{R})\right)\right)\right)\in\mathbb{R}^{n_r\times d},
$$

$$
x=\frac{1}{n_r}\sum_{i=1}^{n_r}G_i\odot\hat{R}_i .
$$

其中 $W_d\in\mathbb{R}^{d_{\text{low}}\times n_r d}$、$W_u\in\mathbb{R}^{n_r d\times d_{\text{low}}}$，瓶颈取 $d_{\text{low}}=d/8$。写是每支一个数据相关标量，权重 $W_w$ 取满形状，低秩瓶颈只在读侧：

$$
s=2\,\sigma\!\left(\tfrac{1}{n_r}W_w\,\mathrm{vec}(\hat{R})\right)\in\mathbb{R}^{n_r},\qquad
R_i'=R_i+s_i y .
$$

读操作顶替块的 pre-normalization，块输入已经归一化并门控，加宽的流不再另设归一化层。静态项无增益，标准随机初始化够用。混合矩阵 $H_{\text{res}}$ 删除之后支路彼此独立：一支只被子层写、只经读操作被读。

## 发布件对账

权重仓库 `config.json` 记 `hc_count=4` 对 $n_r=4$，`hc_lowrank=320` 对 hidden 2560 的 $2560/8$，`output_gate_type=sigmoid`。每层的注意力块与 MLP 块各配一个 GR 模块。

## 消融链

消融在 25B-A3B、560B token 上做，九项基准与 [[hybrid-attention-layer-ratio|混合注意力配比]] 同一套管线：

|残差设计|损失|九项均值|
|---|---|---|
|pre-norm 基线|1.617|50.91|
|静态 mHC（$\lambda_\star=0$，只有宽度与静态读写）|1.596|52.49|
|动态 mHC（读写由状态预测）|1.594|54.47|
|GR（逐元素读门，无 $H_{\text{res}}$）|1.590|54.66|

五条观察定下 GR 的形状：sigmoid 门在损失与稳定性上都好过 tanh，这条结论与 mHC 的结论同向，也与 GDN 与注意力组件里 sigmoid 好过 SiLU 或 tanh 的观察同向；把读从每支一个标量细化到每支每通道有收益，把同样的细化搬到写侧几乎无收益，写保持每支标量；从全部支路预测算子好过只用最后一支或先池化；逐支归一化再加成；读写足够有表达力之后，$n_r\times n_r$ 混合算子带来不了显著提升。

## 与 mHC 的算子级对照

mHC（见 [[wide-residual-stream|加宽残差流]]）的读映射 $\sigma(\cdot)$、写映射 $2\sigma(\cdot)$ 与 GR 的两个门同形。GR 把 mHC 的有界正门整套留下，把混合矩阵扔掉，同时把读粒度从每支标量移到每支逐通道。GR 对动态 mHC 的两项差（逐元素读门、去 $H_{\text{res}}$）换来损失与均值的双胜：损失 1.594→1.590，九项均值 54.47→54.66。

删 $H_{\text{res}}$ 另收两笔红利。每块省一次对完整残差状态的读，解码受内存流量支配，这是加宽流的主要推理成本。省掉一个需要单独约束的算子，报告把约束件明写为潜在失稳源。混合矩阵在更大的支路数配稀疏更新的区间是否重新有价值，是 [[gated-residual-wide-stream-revisit|一条待验的想法]]。

## 与注意力残差的粒度差

Kimi 的 Attention Residuals（见 [[attention-residuals|注意力残差]]）让每层对先前各层输出做 softmax 注意力决定读，块版把层分成大小 $S$ 的块、每块求和成一个表示再对块做注意力。本件在 28 层档复现，$L$ 取 56 个子层（每层注意力块加 MLP 块），$S$ 数子层，粒度比 Kimi 原文的层级块细一档，两处的数字不同网格、不可并排引用：

|残差设计|损失|损失 + GatedNorm|
|---|---|---|
|pre-norm|1.789|1.787（−0.002）|
|Block AttnRes $S=4$|1.773|1.768（−0.005）|
|Block AttnRes $S=2$|1.770|1.766（−0.004）|
|Full AttnRes|1.762|1.758（−0.004）|
|GR（$n_r=4$）|—|1.762|

报告正文说 Full AttnRes 与 GR 持平于 1.762，比的是 Full AttnRes 的未加门值对 GR 的带门值（GR 的读里本来就含门，无门一栏是空）。两列都读时，28 层档 Full AttnRes 加门 1.758 领先 GR 的 1.762 约 0.004；48 层档 Block AttnRes $S=4$ 报 1.711、GR 报 1.707，GR 反超 0.004。加门对 AttnRes 各档降 0.004–0.005、对 pre-norm 基线只降 0.002，报告的读法是子层读到的输入越复杂，门帮得越多。[[gated-normalization|门控归一化]] 是这条门控收益的来源件。

支路之间的信息流在删掉 $H_{\text{res}}$ 之后可以精确分解，这份归因账记在 [[residual-branch-attribution|残差支路归因]]。

## 推理侧的两条试错

稀疏读写（每块只读门值最高的两支，从头稀疏或中途引入）在预训练损失与基准上几乎无损，后训练之后质量明显退化，改变稀疏度也不解决。报告把这处点名为只看预训练指标会做错决定的实例，是 [[three-axis-architecture-eval-protocol|三轴评估协议]] 拦下的三条捷径之一。

FP8 存残差状态可行：GR、门控注意力、GDN 的门把写入幅度约束在窄区间，低精度格式正好匹配，字节数相对 BF16 减半、质量几乎不动。读与写各融成单 kernel，group RMSNorm 折进读侧，加宽的流每块正反各遍历一次。
