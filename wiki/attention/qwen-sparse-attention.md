---
title: Qwen Sparse Attention：块级打分与轻量索引器
slug: qwen-sparse-attention
type: concept
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/qwen3.8-flash-next.extracted.md
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/hf_config.json
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
---

# Qwen Sparse Attention：块级打分与轻量索引器

全注意力对每个查询与全部历史键打分，成本随序列长度的平方增长，键值缓存随长度线性增长。稀疏注意力替全注意力挑出少数键，让核心注意力只在被选中的块上算。Qwen Sparse Attention（QSA）是 Qwen3.8-Flash-Next 继续预训练阶段替换全注意力层的件，路线沿 DeepSeek-V3.2 的 DSA（轻量索引器产生稀疏掩码），改动落在打分粒度：DSA 在 token 级打分，QSA 在 $r$ 个 token 组成的块级打分。

## 压缩索引器

索引器是 MQA 结构（多查询头共享一个键头）：$H=4$ 个查询头加 1 个共享键头，查询侧带 RMSNorm、键侧不带，

$$
q_i^{h}=\mathrm{RMSNorm}(W_Q^{h}x_i),\qquad k_i=W_K x_i .
$$

键按 $r$ 个 token 非重叠分块做平均池化压缩，位置编码在池化之后施加——每头 128 维里旋转 64 维，块取块首位置、查询保留 token 位置。这样做的理由是避免把不同旋转相位的 token 表示平均在一起。

$$
\bar k_b=\mathrm{RMSNorm}\!\left(\mathrm{AvgPool}(k_{p_b:p_b+r-1})\right),\qquad
I_{ib}=\sum_{h=1}^{H}\mathrm{ReLU}\left\langle q_i^{h},\bar k_b\right\rangle .
$$

打分受块因果约束：满足 $p_b+r-1\le i$（块内最后一个 token 不晚于查询位置）的块可被该查询打分，其余记 $-\infty$。给定 token 预算 $K$，块预算 $K_B=\lceil K/r\rceil$；选中的块展开成 token 下标，末尾不完整块的 token 恒包含。生产配置取 $K=2048$、$r=4$、$K_B=512$，索引器复杂度从 $O(n^2)$ 降到 $O(n^2/r)$。

![[raw/2026-09/llm-architecture/github/qwen3.8-flash-next/assets/qwen3.8-flash-next-fig3-qsa.png]]

> **QSA 总览图**（技术报告 Figure 3）左侧压缩轻量索引器用压缩因果掩码给键块打分、选 top-k 块下标；右侧稀疏核心注意力把块下标展开成稀疏掩码计算。

## 索引器怎么学

索引器由 [[indexer-distillation|索引器蒸馏]] 的两段协议监督：第一段只训索引器，第二段骨干与索引器联合训。这段监督是 QSA 与 DSA 在协议上的共同处，细节记在那一页。

## 消融读数

训练代价上，换 QSA 后损失曲线与全注意力基线高度一致，继续预训练末段逐步差在 $10^{-4}$ 量级。能力读数分两档。八项短上下文基准（MMLU-Pro、SuperGPQA、MATH、GSM8K、BBH、MMMLU、EvalPlus、MultiPL-E）均值 75.9→76.8，八项里七项持平或更好，唯一回落的 MMMLU 差 0.7 分。长上下文检索的收益集中到 512K 以上：RULER 512K–1M 档 90.08→93.00；8-needle MRCR（长上下文多针检索基准）在 512K 从 30.66 到 40.53、1M 从 20.71 到 26.44；128K 以内两档基本持平（RULER ≤128K 99.84→99.89），MRCR 的 128K、256K 两档各回落 1.2 分。

效率读数以 FlashInfer 的 paged GQA（分组查询注意力，键值缓存按页管理）为基线，取 kernel 级对比。1M 上下文处索引器自身快 3.8 倍（前填充）与 4.4 倍（解码），含索引器的注意力模块整体快 7.6 倍与 4.9 倍。前填充按 16K chunk、batch 1，解码 batch 4、next_n=4（对应三个多 token 预测步）。

![[raw/2026-09/llm-architecture/github/qwen3.8-flash-next/assets/qwen3.8-flash-next-fig6-kernel.png]]

> **kernel 延迟图**（技术报告 Figure 6）(a)(b) 索引器在前填充与解码的延迟随上下文长度，压缩比 4 对 1 的加速标注 3.8× 与 4.4×；(c)(d) 注意力模块整体对稠密 GQA 基线，1M 处 7.6× 与 4.9×。

## 两个结构选择

索引器头数扫描在 35B-A3B 档做，指标取 1M 以内 RULER，模型取第二段稀疏训练之后的继续预训练件。稠密蒸馏初始化之后直接上索引器明显掉分（RULER 约 77–78 对基线约 86.3），少量联合训练即回到全注意力水平，4 头起追平并略超，最终取 4 头。

跨层共享索引这条路线也被纳入扫描。相对索引器延迟（索引器延迟相对全注意力层延迟）0.25 处，QSA 追平全注意力基线；对照方法一路到 0.5（每两个全注意力层共享一份索引，中间隔三个 GDN 层）仍低于基线。报告把这条对照读作块级压缩对混合架构的适配优势：跨层共享依赖层间索引相似，混合架构相邻全注意力层之间夹着三个循环层，层间相似度低。这条路线与跨投机步复用的机制记在 [[index-reuse-in-sparse-attention|稀疏注意力的索引复用]]。

## 发布件对账

权重仓库 `config.json` 与这套形状逐项对齐：`indexer_budget=2048`、`indexer_compress_ratio=4`、`indexer_n_heads=4`、`indexer_kv_heads=1`、`indexer_head_dim=128`。核心注意力 `head_dim=256` 配 `partial_rotary_factor=0.25` 给出 $256\times0.25=64$ 个旋转维，与索引器每头旋转的 64 维相等。

同一代的另一条稀疏路线（压缩缓存的省字节路线）与本件的省算力路线的分工见 [[sparse-attention-route-comparison|稀疏注意力的两条路线]]。
