---
title: "Qwen3.8-Flash-Next 增强信息"
slug: qwen3.8-flash-next-context
type: context
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/README.md
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/qwen3.8-flash-next.extracted.md
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/hf_model_card.md
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/hf_config.json
resource: raw/2026-09/llm-architecture/github/qwen3.8-flash-next
---

# Qwen3.8-Flash-Next 增强信息

## 这份资源做了什么

资源本体是一份 GitHub 仓库加仓库内随附的技术报告。仓库 `QwenLM/Qwen3.8-Flash-Next`（`https://github.com/QwenLM/Qwen3.8-Flash-Next`，快照 commit `69885871a64393807d988b27b1b5e380e8f28526`，提交时间 2026-08-27T15:29:26+08:00，访问日期 2026-09-23）只有两件内容物：`README.md` 与 `tech_report.pdf`，没有 docs/ 目录、没有独立 release notes 文件，News 一节单条记录 2026-08-26 发布。技术报告 28 页，A4，LaTeX 与 pdfTeX-1.40.27 生成，PDF 元数据的创建与修改时间都是 2026-08-26 16:44 CST，标题《On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability》，作者栏集体署名 Qwen Team，仓库 README 的 BibTeX 把机构写为 Alibaba Group、月份写为 August、年份 2026。同一份报告在 arXiv 有正式条目 2608.30320v1，主分类 cs.CL，首次提交 2026-08-31T06:35:07Z，作者栏展开为 36 个个人名，正文 28 页，PDF 字节与仓库版不同（仓库版 MD5 `1ce2ae8699fc0f6b05d96f5735bc10b1`，arXiv 版 `faac29b990085c855e447652c90d9466`），摘要文字与仓库版逐字一致（arXiv API，访问日期 2026-09-23）。

工作的性质是架构验证件的公开说明。README 开篇写明这一版开放的是 Qwen3.8-Flash-Next 的权重，它是同时充当 Qwen4 所用架构的早期预览，作用是重演 Qwen3-Next 之于 Qwen3.5 的角色——那次引入的 Gated DeltaNet 加 Gated Attention 混合设计此后贯穿 Qwen3.5、Qwen3.6、Qwen3.7、Qwen3.8 四个系列，官方选择再次提前放出架构改动，让社区在完整 Qwen4 家族建在它上面之前先检验（README Introduction 一节）。报告的写法与常规模型技术报告有差别：全文的主语是「一处架构改动」加「三条评估轴」，作者把方法论写在摘要里——每个候选改动同时看损失与下游基准、看它在训练/预填充/解码三段的成本、看它对最优超参与训练稳定性的影响，并专门报告三轴互相矛盾之处（技术报告摘要，§1）。

四处承重改动与它们的量化落点：

- **注意力**。层排布取每四层一个全注意力层，其余为 Gated DeltaNet 循环层；继续预训练阶段把全注意力层换成 Qwen Sparse Attention（QSA）。QSA 沿用 DeepSeek-V3.2 的 DSA 路线，改动在打分粒度：键按 r 个 token 分块、平均池力压缩，索引器（MQA，4 查询头加 1 共享键头）做 block-causal 打分，选中的块展开为 token 下标后截到预算 K。生产配置 K=2048、r=4（技术报告 §2.1.2；权重仓库 `config.json` 的 `indexer_budget` 与 `indexer_compress_ratio` 同为 2048 与 4）。同规模消融：28 层 25B-A3B MoE，400B token 的 4K 段加 80B token 的 32K 段，全注意力九项均值 49.87、滑动窗口混合 51.15、GDN 混合 53.81（技术报告 Table 1）。QSA 换掉全注意力后的读数：8 项短上下文均值 75.9→76.8，RULER 512K–1M 档 90.08→93.00，8-needle MRCR 在 512K 30.66→40.53、1M 20.71→26.44（Table 2、Table 3）；kernel 级在 1M 上下文 prefill 快 7.6 倍、decode 快 4.9 倍（§2.1.2 与 Figure 6）。
- **残差**。残差流加宽到 4 支，读用逐元素数据相关权重、写用每支一个标量，配 group-RMSNorm，并去掉支路间混合矩阵，作者命名 Gated Residual（GR）。消融链在 25B-A3B、560B token 上：pre-norm 损失 1.617 与九项均值 50.91、静态 mHC 1.596 与 52.49、动态 mHC 1.594 与 54.47、GR 1.590 与 54.66（Table 5）。被点名写出的分歧：静态到动态损失只再降 0.002，平均精度涨 1.98 分，而基线到静态涨 1.58 分（§2.2）。
- **嵌入**。骨干外加一层 n-gram 嵌入，放在第 2 层，表放主机内存、异步预取与第一层计算重叠。51B 参数、三阶、基础表 20,000,000 项、8 个哈希头（README；`config.json` 的 `ngram_vocab_size_base`、`ngram_size`、`heads_per_ngram`、`ple_layer_ids=[2]`）。两种预算的结论分岔：固定总参数（削专家补嵌入）时损失在 10× 词表处最低（1.197）且下游无明确改善；固定 MoE 预算、词表 20V→200V 时损失单调降到 1.526、下游饱和或波动、中文基准 C-Eval 66.91→74.94 与 CMMLU 68.10→73.24 一致改善（Table 8、Table 9）。
- **优化与超参**。Muon 配 Newton–Schulz 正交化 8 步、Polar Express 系数表、Nesterov 动量 0.95、更新按 $\gamma(A,B)=0.2\sqrt{\max(A,B)}$ 缩放（这一缩放式的出处是 Moonshot 一文的式 (4)，见「机制细节与对照账」第四段），只用在真正充当线性映射的二维权重上，其余（嵌入、归一化增益、GR 的两个低秩投影、注意力与 GDN 的输出门）走 AdamW；Megatron 融合的 qkv、SwiGLU fc1、GDN 输入投影按语义拆开再喂 Muon（§3.1）。重拟合缩放律把最优点推高：批量 12.6M→25.2M token 比旧配方低 7.2e-3 损失，再放大 1.5 倍只亏 4.3e-4；批量 warmup 判定不必要，两条 ramp 落在 run-to-run 方差内且多花 18.8% 优化步；学习率预测在 48 层 156B-A7B、419B token 上检验，预测最优 (B=8.4M, η=1.76e-3)，旧配方高 7.8e-3，最优点周围在至少 ±2 倍学习率与 +25% 批量内是平的（§3.2，Figure 8、Figure 9）。
- **稳定性证据**。绕过衰减、把学习率固定在最优值的倍数上来复现大规模失稳：2 倍时 AdamW 基线每万步 4.3 次尖峰、两种 Muon 配置 0.2 次；4 倍时 AdamW 每万步 183 次、19,932 步里 213 次撞 0.5 的裁剪阈值（§3.3，Figure 10、Figure 11）。单变量隔离 GatedNorm（固定 AdamW 与结构、3 倍学习率）：尖峰 32.0→3.2 每万步、阈值穿越 256→20（Figure 12）。生产学习率下前 276B token 三段对照：加 GR 降 0.026，整套配方再降 0.032，合计 0.058（Figure 13）。

自报的边界与下一步写在结论里：作者称验证策略是「在完整评估预算仍可承受的规模上测每一条主张」，压力测试与缩放律检验各自放在最敏感的区域；前训练指标一致而后期评估分岔的情况被联合协议拦在生产之前；展望点名的瓶颈是评估吞吐——一个能可靠预测后训练排序的更便宜中规模探针会让设计空间更好搜（§5）。报告没有给训练算力、GPU 时数、语料量与数据配比的绝对数字，成本一律以相对量表达（约三分之一激活参数、三分之一训练 token、约九分之一训练 FLOPs，对照对象是 397B-A17B 的 Qwen3.7-Plus）。

## 立在什么基础上

四条基座，按与本件的距离排。

**一、自家的模型线与「预览件」这个体裁**。README 把体裁说得直接：本件相对 Qwen4 的位置，就是 Qwen3-Next 相对 Qwen3.5 的位置，那次引入的 Gated DeltaNet 加 Gated Attention 混合设计此后贯穿 Qwen3.5 到 Qwen3.8 四个系列（README Introduction）。Qwen3-Next 本身只有官方博客（`https://qwen.ai/blog?id=qwen3-next`），arXiv 上以「Qwen3-Next」为题检索不到对应论文，命中的是无关条目（arXiv API 标题检索，访问日期 2026-09-23）；阿里云的开发者的博客把它描述为「新一代超高效模型架构」（`https://www.alibabacloud.com/blog/qwen3-next-a-new-generation-of-ultra-efficient-model-architecture-unveiled_602536`，访问日期 2026-09-23），Hugging Face Transformers 文档里 `qwen3_next` 是独立的模型类型条目。报告正文里被当作既有基线点名的自家工作有两件：Qwen3.5（官方博客 2026-02，`https://qwen.ai/blog?id=qwen3.5`，被引作 Qwen Team, 2026，是消融所用 28 层 25B-A3B MoE 的结构底座，也是 n-gram 词表缩放里 V 的取值来源）与 Qwen2.5 技术报告（arXiv 2412.15115，2024-12-19，44 位作者，集体署名 Qwen）。更早的 Qwen3 技术报告（arXiv 2505.09388v1）在参考文献里占一条。zero-centered RMSNorm、RoPE、GQA/MQA、SwiGLU 这些件在正文里被当作既有标准直接采用（§2.1.1、§2.1.2）。

**二、稀疏注意力这条线**。QSA 的路线归属写在正文：沿 DSA（Liu et al., 2025a，即 DeepSeek-V3.2，arXiv 2512.02556，2025-12-02，DeepSeek-AI 集体署名 264 项作者）的路子，用轻量索引器产生稀疏掩码，本文的改动是把打分从 token 级移到 micro-block 级，理由是 DSA 的 O(n²) 索引器在长序列下开销不可忽略（§2.1.2）。同一节的对照基线报告写作 IndexShare（arXiv 2603.12201，2026-03-12，Yushi Bai、Qian Dong 等 8 位，Z.ai 与清华大学），该方法的自名是 IndexCache，报告的参考文献条目题名也是 IndexCache，错位只在正文与图例；做法是跨层复用索引来省索引器计算，自报在 30B 的 DSA 模型上省掉 75% 索引器计算、prefill 最高 1.82 倍与 decode 最高 1.48 倍；本文报出的对比是 QSA 在相对索引器延迟 0.25 处追平全注意力，IndexCache 在同延迟下追不平（§2.1.2）。这条线上更早的学术工作在参考文献里排着：SeerAttention（arXiv 2410.13276，2024-10-17，Yizhao Gao 等 11 位）学内在稀疏注意力，ProxyAttn（arXiv 2509.24745，2025-09-29 首发，Yixuan Wang 等 7 位，哈工大与字节跳动，ICLR 2026）用代表性头引导稀疏、本身是 training-free 方法；本文 §2.1.2 把两件并列为块级 max-pool 对齐的来源，回一手渠道，把教师注意力分布做 max-pool 到块级这一步只见于 SeerAttention。MTP 段的索引复用（跨投机步复用 top-k 下标）点名跟的是 GLM（GLM-5，arXiv 2602.15763，2026），本跳回 GLM-5 全文未找到该表述，归属存疑（详「机制细节与对照账」第一段）。

**三、残差加宽与门控这条线**。§2.2 一段把三条并行工作并列举出作为直接前作：稠密跨层连接 DenseNet（arXiv 1608.06993）、给注意力值开一条额外残差路的 Value Residual Learning（arXiv 2410.17897，2024-10-23，Zhanchao Zhou 等 5 位）、跨层复用缓存状态的 YOCO 一族（Sun et al., 2024）；加宽流这一支引 Alternating Updates（arXiv 2301.13310，2023-01-30，Cenk Baykal 等 6 位，Google）与 Hyper-Connections（arXiv 2409.19606，2024-09-29，Defa Zhu 等 8 位），门控读写这一支引 Highway Networks（arXiv 1505.00387）。本文的 GR 定位写得很清楚：它和 HC、mHC、VWN 同族，差别在 GR 把块的 pre-normalization 替换掉、前面不再加归一化层（§2.2）。mHC（arXiv 2512.24880v2，首发 2025-12-31，Zhenda Xie、Yixuan Wei 等 20 位，DeepSeek-AI）是消融表里的直接对手，本文报出 GR 在同预算下损失与均值双胜（Table 5）；xHC（arXiv 2607.14530，2026-07-16，Xiangdong Zhang 等 13 位）与 Kimi Team 的 Attention Residuals（arXiv 2603.15031，2026-03-16，集体署名 37 项作者）也在对照里，后者在 Table 6 上与 GR 同预算比损失（AttnRes S=4 为 1.773/1.768，pre-norm 为 1.789/1.787）。GatedNorm 这一件的出处是组内另一篇：Qiu et al., 2026《A Unified View of Attention and Residual Sinks: Outlier-Driven Rescaling is Essential for Transformer Training》（arXiv 2601.22966，2026-01-30，19 位作者，Zihan Qiu 领衔），正文写「在另一项工作中我们发现……」（§2.2）。sigmoid 门优于 SiLU/tanh 这一观察，正文同时接在 GDN 输出门与 mHC 的结论上（§2.1.1、§2.2），本跳核对 mHC 原文式 (8)：其读映射与写映射确实分别是 $\sigma(\cdot)$ 与 $2\sigma(\cdot)$、文中明写 $\sigma$ 是 Sigmoid，本件这一句接得实；GR 的门形式与 mHC 同形，差别在粒度与混合矩阵（详「机制细节与对照账」第二段）。门控注意力本身的实证来自组内的 Gated Attention 一文（arXiv 2505.06708，2025-05-10，Zihan Qiu 等 13 位）。

**四、嵌入侧容量与优化器**。n-gram 嵌入这一支的谱系在 §2.3 一段摊开：概念前作 N-Grammer（arXiv 2207.06366，2022-07-13，Aurko Roy 等 16 位，它查的是潜空间码本离散出的 latent n-gram、表可训练）、L3（Large Lookup Layers，arXiv 2601.21461，Tseng 与 De Sa，ICML 2026）、STEM（arXiv 2601.10639，2026-01-15，Ranajoy Sadhukhan 等 8 位，CMU 与 Meta AI）、Engram（报告里写作 Cheng et al., 2026，arXiv 2601.07372，2026-01-12 首发，Xin Cheng 等 21 位，北京大学与 DeepSeek-AI）与本库已有账目的 [[deepseek-v41-flash-context|DeepSeek-V4.1-Flash 增强信息]]；「嵌入表可放大并放到加速器外」的工程口径引 Google DeepMind 的 Gemma 3n 模型概览（2025）与 RWKV-V8 的 DeepEmbed（`https://wiki.rwkv.com/basic/architecture.html#rwkv-v8-s-deepembed`，报告标注访问日期 2026-08-20）；把嵌入继续放大的判断来自《Scaling Embeddings Outperforms Scaling Experts in Language Models》（arXiv 2601.21204，2026-01-29，Hong Liu 等 16 位，美团 LongCat 一线），本文的固定总参数消融正是为了检验这一判断，结论落在「N-gram 嵌入与 MoE 专家在扩容上扮演不同角色」（§2.3.2，Table 8）；词表压缩与分配策略的对照引 X-GRAM（arXiv 2604.21724，2026-04-23，Yilong Chen 等 13 位，中科院信工所、国科大、北京大学与 IQuest Research）与 Engram（同上的 Cheng et al., 2026，它的词表压缩是 NFKC 与小写化把 128K 词表的等效规模降 23%），正文称试过同类做法、在本配方里无一致收益；n-gram 查表的参数量与卸载开销在 Engram 一边有可直接对照的账：它的 U 形分配律最优在 20%–25% 给查表记忆，本件 Table 8 的最优点在 25%；它的 100B 表 CPU 卸载代价是吞吐降 2.8% 以内，本件没给同口径的吞吐数字（详「机制细节与对照账」第三段）。优化器一支：Muon 原始出处是 Keller Jordan 2024-12 的博客与仓库（`https://kellerjordan.github.io/posts/muon/`），规模化依据引 Moonshot AI 的《Muon is Scalable for LLM Training》（arXiv 2502.16982，2025-02-24，Jingyuan Liu、Jianlin Su 等 28 位，本文 §3.1 的 $0.2\sqrt{\max(A,B)}$ 缩放即出自该文式 (4)）与 Essential AI 的《Practical Efficiency of Muon for Pretraining》（arXiv 2505.02222，2025-05-04，它的实测主张是 Muon 在远超临界批量的大批量下比 AdamW 更能保住数据效率，模型做到 4B），正交化系数表引 Polar Express（arXiv 2505.16932v5，2025-05-22，Noah Amsel 等 4 位），张量并行下的实现与 Canzona（arXiv 2602.06079，2026-02-04，Liangyu Wang 等 10 位，作者表里的 Liangyu Wang 是本件 Contributors 之一）同题；批量与学习率的缩放律依据引 Kaplan 等（arXiv 2001.08361）、McCandlish 等的临界批量模型（arXiv 1812.06162）与《How does critical batch size scale in pre-training?》（arXiv 2410.21676）；压力测试的方法学来自 Wortsman 等《Small-scale proxies for large-scale transformer training instabilities》（arXiv 2309.14322，2023-09-25，ICLR 2024，做法是在小模型上抬学习率复现大模型失稳）；同节开篇举的大规模失稳例子是 Dehghani 等的 22 亿参数视觉变换体一文（arXiv 2302.05442，2023-02-10）与 PaLM（arXiv 2204.02311），两件在本件里承担的是背景例子、方法学一条归 Wortsman 等；梯度裁剪阈值 0.5 引 Pascanu 等（arXiv 1211.5063）；不用 qk-clip 与 SwiGLU-clip 这两件分别点名 Kimi Team 2025（arXiv 2507.20534，Kimi K2）与 Agarwal 等 2025（gpt-oss 模型卡，arXiv 2508.10925）。GDN 本身的出处是 Yang et al., 2024《Gated Delta Networks: Improving Mamba2 with Delta Rule》（arXiv 2412.06464v3，2024-12-09）；线性注意力当快权重记忆的解读引 Schlag et al.（arXiv 2108.07732 之外的 Transformer Circuits 一文与 Schlag 2021）。

**五、四条待考的联系（猜想）**。以下几处没有原文直接支撑，属我读出的可能关系，标明为猜想。其一，发布件 `config.json` 同时带着 `indexer_n_heads=4`、`indexer_compress_ratio=4`、`indexer_budget=2048` 与 `mtp.layer_types=["full_attention"]`，模型卡的 Hidden Layout 又把每第四个槽位直接写作 Qwen Sparse Attention，两处合起来支持「骨干与 MTP 的每四层一个全注意力槽位在 CPT 里换成 QSA、槽位名沿用层类型枚举」这一读法；`partial_rotary_factor=0.25` 与核心注意力 `head_dim=256` 给出 64 个旋转维，与索引器每头 128 维里旋转 64 维对得上（见「机制细节与对照账」第一段）。报告没有写出「哪些原始全注意力权重被丢弃、哪些被继承」，这处空缺属未查明。其二，GR 去掉支路间混合矩阵 Hres 的理由写作「需要单独约束、是潜在失稳源」；mHC 那一路给 Hres 加的是 doubly stochastic 流形约束（Sinkhorn-Knopp，本跳核到迭代上限 20 次），同一类工作里两种处置并存，两篇的稳定性结论各自建立在自己的压力测试协议上（猜想）。本跳另外核到一处同形：mHC 的读映射 $\sigma(\cdot)$ 与写映射 $2\sigma(\cdot)$ 与 GR 的两个门同形，GR 把 mHC 的有界正门留下、把混合矩阵扔掉，粒度从每支标量移到每支逐通道。其三，n-gram 表放第 2 层的理由是与第一层计算重叠预取，与 Gemma 3n 的早层插入是否同一动机，原文未比（猜想）。其四，QSA 的教师是注意力分布的块级 max-pool，蒸馏目标与检索指标（RULER、MRCR）同时上升，这一处的因果方向（索引器学得好导致检索变强，或者长上下文训练本身导致）原文没有拆开（猜想）。

## 机制细节与对照账

本节把四处承重改动补到公式、协议与一手对照的层面，供精读直接取用。落点用技术报告自身的节号、公式号与表号，外部件一律冠名；访问日期均为 2026-09-23。报告内部的数字来自仓库版 PDF 的原页与图，外部数字来自各件一手渠道。

### 一、GDN 混合与 QSA：块级打分与蒸馏监督的完整形状

**GDN 的递推形状**。§2.1.1 公式 (1)–(5)：状态 $S_t\in\mathbb{R}^{d_k\times d_v}$，先衰减 $\hat S_t=\alpha_t S_{t-1}$，再取残差 $\tilde v_t=v_t-\hat S_{t-1}^{\top}k_t$，写回 $S_t=\hat S_{t-1}+\beta_t k_t\tilde v_t^{\top}$，读出 $y_t=S_t^{\top}q_t$；合并形式 $S_t=\alpha_t(I-\beta_t k_tk_t^{\top})S_{t-1}+\beta_t k_tv_t^{\top}$。报告自陈这个状态形状是原论文约定的转置，核对结果对得上：《Gated Delta Networks》（arXiv 2412.06464v3，NVIDIA 的 Songlin Yang、Jan Kautz、Ali Hatamizadeh）原文写作 $S_t=S_{t-1}+v_tk_t^{\top}\in\mathbb{R}^{d_v\times d_k}$、读出 $o_t=S_tq_t$（§3、§4，`https://arxiv.org/html/2412.06464v3`）。同篇的模块描述写明输出门是 linear proj. with SiLU，其消融表里 "w/o. Output Gate" 一行把困惑度从 27.35 推到 29.12，输出门在原始配方里是承重件；本件 §2.1.1 换有界 sigmoid 门的对照点就在这里。

**GDN 的参数化与归一化**。q/k 走短因果卷积加 SiLU 再加 L2 归一化，v 走卷积加 SiLU，写入强度 $\beta_t=\sigma(W_\beta x_t)$，衰减 $\alpha_t=\exp[-\exp(A)\,\mathrm{softplus}(W_\alpha x_t+b_\alpha)]$，头输出 $o_t=W_o[\sigma(W_zx_t)\odot\mathrm{RMSNorm}(y_t)]$（公式 (6)–(11)）。zero-centered RMSNorm 的出处经 Hugging Face Transformers 源码核对：`Qwen3NextRMSNorm` 继承 `Gemma3RMSNorm`，前向算 `output * (1.0 + weight)`、权重零初始化，同处 `full_attention_interval` 默认 4、层类型按 `(i + 1) % 4 == 0` 判全注意力（`https://github.com/huggingface/transformers`，main 分支）。本件 `config.json` 的 `full_attention_interval=4` 与 `layer_types` 每第四项 `full_attention` 与这条排布规则同形。

**QSA 的块级打分形状**。索引器是 MQA，$H=4$ 查询头加 1 共享键头，查询侧带 RMSNorm、键侧不带（公式 (12)）；键按 $r$ 个 token 非重叠分块，块键 $\bar k_b=\mathrm{RMSNorm}(\mathrm{AvgPool}(k_{p_b:p_b+r-1}))$（公式 (13)）；位置编码在池化之后施加，每头 128 维里旋转 64 维，块取块首位置 $p_b$、查询保留 token 位置 $i$（公式 (14)），报告给的理由是避免把不同旋转相位的 token 表示平均在一起；打分 $I_{ib}=\sum_h\mathrm{ReLU}\langle q_i^h,\bar k_b\rangle$，块因果条件 $p_b+r-1\le i$，不满足记 $-\infty$（公式 (15)）；块预算 $K_B=\lceil K/r\rceil$（公式 (16)），选中块展开成 token 下标，末尾不完整块的 token 恒包含（公式 (19)）。生产档 $K=2048$、$r=4$、$K_B=512$，索引器复杂度从 $O(n^2)$ 降到 $O(n^2/r)$（§2.1.2 Efficiency Analysis）。发布件与这套形状逐项对齐：`indexer_n_heads=4`、`indexer_kv_heads=1`、`indexer_head_dim=128`、`indexer_compress_ratio=4`、`indexer_budget=2048`；核心注意力 `head_dim=256` 配 `partial_rotary_factor=0.25`，旋转维数 $256\times0.25=64$，与索引器每头旋转的 64 维相等，正文「matching the rotary dimension used in the core attention module」这句话在发布件里成立。

**与 DSA 的对照账**。DeepSeek-V3.2（arXiv 2512.02556）的 lightning indexer 是 token 级打分 $I_{t,s}=\sum_j w_{t,j}\,\mathrm{ReLU}(q_{t,j}k_s)$，稀疏阶段明写「select 2048 key-value tokens for each query token」，发布件 `config.json` 记 `index_n_heads=64`、`index_head_dim=128`、`index_topk=2048`（`https://huggingface.co/deepseek-ai/DeepSeek-V3.2/raw/main/config.json`）。三处相同：token 预算同为 2048、都用 ReLU 相似度按头求和、都靠少头实现省算力。两处是本件的改动：打分从 token 级移到 $r$ token 块级，索引器头数从 64 降到 4。DSA 原文 §2.3 自陈「the lightning indexer still has a complexity of $O(L^2)$」，靠头数少与 FP8 压常数，本件 §2.1.2 的动机句与这一自陈对得上，$O(n^2/r)$ 是本件自己的改动。

**蒸馏监督的两段形状**。教师分布是全序列 softmax 注意力按教师头求和再 L1 归一化，$a_i\in\mathbb{R}^n$；按 $r$ 做 max-pool 到块级、再 L1 归一化得 $\hat a_i\in\mathbb{R}^B$，$B=\lfloor n/r\rfloor$（公式 (17)）；第一段损失 $L_{KL}=\frac1N\sum_i D_{KL}(\hat a_{i,:}\,\|\,\mathrm{Softmax}(I_{i,:}))$，只算完整键块，索引器单独训 1,000 步、lr $1\times10^{-3}$、每步 8 条 256K 序列、合计约 2B token；第二段 KL 限制在选中的 $K_B$ 块上、教师概率在该集合内重归一（公式 (20)），骨干与索引器联合训 8,000 步、lr $2.5\times10^{-5}$、每步 96 条 256K 序列、合计约 200B token。DSA 原文 §2.1.1 的两段与本件几乎同参：warm-up 段 lr $10^{-3}$、1,000 步、每步 16 条 128K、合计 2.1B token，稀疏段 lr $7.3\times10^{-6}$、15,000 步、每步 480 条 128K、合计 943.7B token。本件第一段的步数与学习率照搬，第二段换了序列长度、学习率与预算。

**块级 max-pool 教师的实名**。§2.1.2 写「Following prior work (Gao et al., 2024; Wang et al., 2026b)」。SeerAttention（arXiv 2410.13276v4，Yizhao Gao 等 11 位）的 §3.2 与附录 A.1 确实是把注意力图做二维 max-pool 当 KL 教师、并实现带 2D-MaxPooling 的 FlashAttention。被并列引的第二件需要修正题名与作者：正确题名 "ProxyAttn: Guided Sparse Attention via Representative Heads"，arXiv 2509.24745（首发 2025-09-29，v2 标 ICLR 2026 camera-ready），作者 Yixuan Wang、Huang He、Siqi Bao、Hua Wu、Haifeng Wang、Qingfu Zhu、Wanxiang Che（哈工大与字节跳动），方法是 training-free 的代表头池化打分加块级动态预算，通篇没有蒸馏损失，也没有把教师分布 max-pool 成块级目标这一步（`https://arxiv.org/html/2509.24745v2`）。块级教师这一步的实证来源是 SeerAttention 一件。本件核心贡献者里的 Yixuan Wang 与 ProxyAttn 第一作者同名，两条记录分属阿里巴巴与哈工大/字节跳动，是否同一人未查明。

**IndexShare 的实名与账**。§2.1.2 与 Figure 5(a) 图例把对照基线叫 IndexShare，其参考文献条目的题名是 "IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse"（arXiv 2603.12201，Yushi Bai、Qian Dong、Ting Jiang、Xin Lv 在 Z.ai，Zhengxiao Du、Aohan Zeng、Jie Tang、Juanzi Li 在清华大学与 Z.ai）；该文自名 IndexCache，通篇不见 IndexShare 一词。它的机制是把层分成跑索引器的 Full 层与复用最近 Full 层 top-k 索引的 Shared 层，训练无关的贪心层搜索加训练感知的多层蒸馏，在 30B 的 DSA 模型上省掉 75% 索引器计算，报 prefill 最高 1.82 倍、decode 最高 1.48 倍（`https://arxiv.org/html/2603.12201v1`）。Figure 5(a) 图例里的 "Keep x" 就是保留 $x$ 个索引器层，与 IndexCache 的 Full/Shared 划分对得上。

**MTP 索引复用那条归属未证实**。§2.1.2 写「we follow GLM (GLM-5-Team, 2026) and reuse the top-k indices across speculative decoding steps」。回 GLM-5（arXiv 2602.15763v2）原文，它记的是采用 DSA、索引器 warm-up 与联合训练的两段消融（GLM-4.7-Flash 上 1000 步 / 150B token）、MTP 三层参数共享（接受长度 2.76 对 2.55）、RL 侧的 indexer replay 与确定性 top-k 实现；「跨投机步复用 top-k 索引」这句话在该文里找不到（`https://arxiv.org/html/2602.15763v2`）。这条归属按悬空记账，机制本身是本件自述的实现细节。

**QSA 的消融规模与图读数**。压缩比与索引器头数的消融在 35B-A3B 档做（§2.1.2 Architecture Ablation），指标是 1M 以内 RULER，模型取第二段稀疏训练之后的 CPT 件。Figure 5(a) 扫 Block 2/4/8/16 与 IndexCache 的 Keep 3/4/5，本件在相对索引器延迟 0.25 处追平全注意力，IndexCache 在 0.5 处仍低于基线（0.5 表示每两个全注意力层共享一份索引、中间隔三个 GDN 层）。Figure 5(b) 扫索引器查询头数 1/2/4/16，读数是稠密初始化之后直接上索引器明显掉分、少量联合训练即回到全注意力水平，最终取 4 头。Figure 6 的 kernel 账：基线是 FlashInfer 的 paged GQA，prefill 用 16K chunk、batch 1，decode 用 batch 4、next_n=4（三个 MTP 步），1M 处索引器自身 3.8 倍（prefill）与 4.4 倍（decode），含索引器的注意力模块整体 7.6 倍与 4.9 倍。Table 4 的 MTP 平均接受长度在 MT-Bench、GSM8K、MATH、HumanEval、MBPP 上从 4.06 到 4.07，逐档差 0.01 至 0.03。

**FlashQLA 的建仓与热度已补上**。GitHub API 直取成功（HTTP 200）：`QwenLM/FlashQLA` 语言 Python，星数 706，建仓 2026-04-24，末次推送 2026-09-18，描述是 TileLang 写的高性能线性注意力 kernel 库；README 报 GDN chunked-prefill 前向对 FLA Triton kernel 2–3 倍、反向约 2 倍，v0.1.2（2026-07）同时作为 flash-linear-attention 的 GDN 后端，另有官方博客 `https://qwen.ai/blog?id=flashqla`（`https://api.github.com/repos/QwenLM/FlashQLA`，访问日期 2026-09-23）。

### 二、GR 与 mHC、AttnRes 的对照账

**GR 的算子形状**。§2.2 公式 (30)–(34)：每支独立归一化 $\hat R_i=\mathrm{RMSNorm}(R_i;\gamma_i)$，增益 $\gamma_i\in\mathbb{R}^d$ 每支一份；读门 $G=\mathrm{unvec}\big(\sigma(W_u\,\mathrm{SiLU}(n_rW_d\,\mathrm{vec}(\hat R)))\big)\in\mathbb{R}^{n_r\times d}$，$W_d\in\mathbb{R}^{r\times n_rd}$、$W_u\in\mathbb{R}^{n_rd\times r}$、瓶颈秩 $r=d/8$；块输入 $x=\frac1{n_r}\sum_i G_i\odot\hat R_i$；写标量 $s=2\sigma\big(\frac1{n_r}W_w\,\mathrm{vec}(\hat R)\big)\in\mathbb{R}^{n_r}$，$W_w\in\mathbb{R}^{n_r\times n_rd}$，写回 $R_i'=R_i+s_iy$。hidden 2560 时瓶颈秩 $2560/8=320$，与发布件 `hc_lowrank=320` 对齐，`hc_count=4` 对 $n_r=4$。每层的注意力块与 MLP 块各配一个 GR 模块，静态项无增益、标准随机初始化够用，读操作顶替块的 pre-normalization，去掉 $H_{res}$ 之后支路彼此独立。

**与 mHC 的门形式对照**。mHC（arXiv 2512.24880v2，§4.2）先按 HC 的写法算出静态项加动态项的原始系数，再施加约束：读映射 $\mathcal{H}^{pre}=\sigma(\tilde{\mathcal{H}}^{pre})$、写映射 $\mathcal{H}^{post}=2\sigma(\tilde{\mathcal{H}}^{post})$、混合矩阵 $\mathcal{H}^{res}=\text{Sinkhorn-Knopp}(\tilde{\mathcal{H}}^{res})$，文中明写 $\sigma(\cdot)$ 是 Sigmoid；Sinkhorn-Knopp 先取指数保正、再交替归一行列，迭代上限 $t_{max}=20$，投到双随机矩阵流形（Birkhoff polytope，行列和为 1、谱范数不超过 1、乘法闭合）。本件 GR 的读门 $\sigma(\cdot)$ 与写门 $2\sigma(\cdot)$ 与 mHC 的两个约束同形，GR 保留有界正门、去掉混合矩阵，同时把读从每支一个标量细化到每支每通道一个权重。mHC 自己的账：门控因子初始化 $\alpha=0.01$（该文附录 A.1 配置表，HC 与 mHC 同值；HC v3 正文只写「较小的初始可学习因子」，0.01 这个数出自 mHC 的复现表），$n=4$ 时训练额外时间开销 6.7%，27B 档相对 HC 涨 BBH 2.1 分、DROP 2.3 分，HC 的 Amax 增益峰值可达约 3000、mHC 压到约 1.6，实验规模是 DeepSeek-V3 式 MoE 的 3B/9B/27B 加 3B 跑 1T token（`https://arxiv.org/html/2512.24880v2`）。本件 Table 5 的链（25B-A3B、560B token）：pre-norm 1.617/50.91、静态 mHC 1.596/52.49、动态 mHC 1.594/54.47、GR 1.590/54.66；GR 与动态 mHC 的差落在逐通道读门与去掉 $H_{res}$ 两处。

**宽度本身的账**。§2.2 先用一个适配 pre-norm 的简化 AltUp（公式 (21)–(22)）隔离宽度：$n_r$ 支、每块 $n_r$ 个可学习标量做读、块输出按深度轮转写回单支，加 $n_r$ 个参数、零矩阵乘，25B-A3B 在 400B token 上降约 0.01 损失。原论文（arXiv 2301.13310v2，Google Research 的 Cenk Baykal 等）的机制是把 token 嵌入加宽到 $Kd$、每层只在 $\ell\bmod K$ 那个子块上计算、其余子块走 predict-and-correct 更新，主战场是 T5 在 SuperGLUE 与 SQuAD 上的微调，等精度下最高 87% 加速（`https://arxiv.org/html/2301.13310v2`）。本件的简化版与原论文在「谁被计算、谁被修正」这一处不同，读 Table 5 时把宽度收益归到本件自己的变体上。

**与 AttnRes 的粒度差**。Kimi 的 Attention Residuals（arXiv 2603.15031）把 PreNorm 的等权累加换成对先前各层输出的 softmax 注意力，每层一个学习伪查询；Block AttnRes 把层分成大小 $S$ 的块、每块求和成一个表示再对块做注意力，内存从 $O(Ld)$ 降到 $O(Nd)$；该文的单位是层，正文不见 sublayer，消融在 16 层模型上做（Full 即 $S{=}1$ 最优，验证损失 1.737），旗舰件集成在 Kimi Linear（48B 总 / 3B 激活、1.4T token），自报推理延迟开销低于 2%（`https://arxiv.org/abs/2603.15031`）。本件 Table 6 的复现把 $L$ 定义成 56 个子层（28 层），$S$ 数的是子层，粒度比 Kimi 原文细一档，两处的数字不同网格、不可并排引用。本件 Table 6 的读数：pre-norm 1.789、Block AttnRes $S{=}4$ 1.773、$S{=}2$ 1.770、Full AttnRes 1.762、GR（$n_r{=}4$）1.762；加 GatedNorm 一列依次 1.787、1.768、1.766、1.758，GR 只有带门的一栏。正文写 Full AttnRes 与 GR 持平于 1.762，比的是 Full AttnRes 的未加门值对 GR 的带门值；两列都读时，28 层档 Full AttnRes 加门 1.758 领先 GR 的 1.762 约 0.004，48 层档 Block AttnRes $S{=}4$ 是 1.711、GR 是 1.707，GR 反超 0.004。本件给的读法是「子层读到的输入越复杂，门帮得越多」，加门对 AttnRes 各档降 0.004–0.005、对 pre-norm 基线只降 0.002。本库知识层的 [[attention-residuals|注意力残差]] 页记的是 Kimi K3 自己的取法（8 块 × 12 层），与本件 Table 6 的子层粒度是同一机制的两种离散化。

**VWN 与 xHC 两处对照**。Virtual Width Networks（arXiv 2511.11238v2，ByteDance Seed 集体署名 119 项作者，通讯作者 Defa Zhu，同时是 Hyper-Connections 的第一作者）的机制是 Over-Width Embedding 把表示宽度与骨干宽度解耦，广义 Hyper-Connections 把隐向量均分 $m$ 段 $\boldsymbol{h}_k\in\mathbb{R}^{D/m}$、逐段做宽度与深度方向的连接，HC 与 AltUp 是它的简化特例；3.3B 激活的 MoE 上 8 倍宽展开对 next-token 吞吐超过 2 倍、next-2-token 约 3 倍，虚拟宽度对损失近似对数线性（`https://arxiv.org/html/2511.11238v2`）。本件 §2.2 给 VWN 的定位（保留每支标量、改把 token 嵌入加宽切段）与原文一致。xHC（arXiv 2607.14530v1，Xiangdong Zhang 等 13 位，上海交通大学人工智能学院与小红书 Dots Studio，另有中科大与北大）的实际机制是给写回做多尺度因果卷积的时间特征增强，配稀疏支路架构在 $N=16$ 支里只更新 $k=4$ 支、读路径保持稠密；18B/28B MoE 档对 mHC 平均下游涨 4.0 分，vanilla 与 mHC 要追平它的损失分别需要 1.50 倍与 1.19 倍的算力（`https://arxiv.org/html/2607.14530v1`）。本件 §2.2 那句「xHC 探索用更大的 $n_r$ 让稀疏支路更新更容易」方向一致、细节以原文为准：$N$ 放大与稀疏更新在原文里互为条件。

**GR 的支路用途账**。§2.2 的分解是精确的：块 $u$ 对块 $v$ 输入的贡献 $a_{u\to v}=\frac1{n_r}\sum_c G_c^{(v)}\odot\gamma_c\odot\frac{s_c^{(u)}y^{(u)}}{\mathrm{rms}(R_c^{(v)})}$（公式 (36)），归一化份额 $\pi_{uv}=\|a_{u\to v}\|\big/\sum_{u'<v}\|a_{u'\to v}\|$（公式 (37)），每个读者的份额之和与 1 的偏差在 $3\times10^{-8}$ 以内。对照件是 20 层 MoE 加 GR 对同配方同数据同优化器同步数的无 GR 参照，统计量 $\Delta_{uv}=\pi^{\text{GR}}_{uv}-\pi^{\text{ref}}_{uv}$。Figure 7 画 780 个有序对里 $\Delta_{uv}\ge0.05$ 且跳层至少 1 层的 21 条路径；标定句是第 15 层有 30 个写者、均分各约 0.03、份额 0.13 是它的四倍。五个 GR checkpoint 各有一条长程支路，典型跳层 10.9，其余支路 3.4–3.9。三条样例：第 0 层 GDN 到第 15 层注意力的份额从 0.020 涨到 0.138，在第 10 到 19 层的每个读者身上保持 0.072–0.138；第 10 层 GDN 到第 11 层注意力 $\Delta_{uv}=0.117$；第 0 层 MLP 同时走长程（0.008→0.058）与局部（0.139→0.192）两条支路。按跳层分组求和：跳 1 层共涨 0.96，跳 12 层以上共涨 0.91，跳 2–12 层共跌 3.21，加权平均跳层 3.97 对 3.91。读 GR 支路最重的子层集中在 softmax 注意力层。早层跨深度保留这一处，报告接的是 Elhage 等的 Transformer Circuits 框架与 Men 等的 ShortGPT（arXiv 2403.03853）。

**推理侧的两条试错**。稀疏读写（每块只读门值最高的两支）在预训练损失与基准上几乎无损，后训练之后质量明显退化，变稀疏度也不解决，报告把这处点名为「只看预训练指标会做错决定」的例子。FP8 存残差状态可行，GR 与门控注意力、GDN 的门把写入幅度约束在窄区间，字节数相对 BF16 减半，质量几乎不动。读（公式 (30)–(32)）与写（公式 (33)–(34)）各融成单 kernel，group RMSNorm 折进读侧，加宽的流每块正反各遍历一次。

### 三、n-gram 嵌入：两种预算与分岔的位置

**协议与形状**。§2.3 的统一协议是 300 tokens per active parameter（TPP）。一层 n-gram 嵌入挂第 2 层，阶取 2 与 3，短 n-gram 作键查表，查得的向量增强对应 token 表示，参数量随词表涨、每 token 计算量几乎不动，寻址确定因此可异步预取。发布件的对齐：`ngram_size=3`、`ngram_vocab_size_base=20000000`、`heads_per_ngram=8`、`ple_layer_ids=[2]`、`ple_embed_dim=2560`、`ple_conv_kernel_size=4`、`split_ngram_parts=128`、`make_ngram_vocab_size_divisible_by=128`。

**51B 的换算闭合**。$20{,}000{,}000\times2560=51.2\times10^{9}$，模型卡与 README 的 51B 就是这张 20M 行、每行 2560 维的表；8 个哈希头与阶数折进行数（等价读法 160M 行 × 320 维，同一乘积）。20M 行对基线词表 250K 是 80 倍，即发布件落在 Table 9 的 50V 与 100V 两行之间。表之外的键值投影另计（§3.1 把 n-gram 的键值投影列为 Muon 参数、表本体走关掉权重衰减的 Adam）。

**放置消融（Table 7）**。固定 n-gram 总参数，单层放置扫第 1/2/3/4/10/15/25 层，另测 2+15 与 2+25：无 n-gram 基线损失 1.585、九项均值 45.44；第 1 层 1.541/47.30，第 2 层 1.541/47.94，第 3 层 1.543/46.76，第 4 层 1.544/46.89，第 10 层 1.544/46.62，第 15 层 1.543/47.37，第 25 层 1.541/47.40，2+15 是 1.541/47.01，2+25 是 1.540/47.75。第 1、2、25 层损失同为 1.541、下游均值差 0.64 分；同一预算摊到多层没有一致收益。Table 7 的 w/o 行与 Table 9 的 None 行同为 1.585、第 2 层行与 Table 9 的 50V 行损失与各列逐项相同，说明放置消融跑在 50V 档上。

**固定总参数（Table 8）**。词表按基线 250K 的倍数记，括注 n-gram 占总参数的比例，专家数相应削减：None 损失 1.202、uncheatable PPL 5.55、C-Eval 70.78、CMMLU 73.01、MMMLU 58.32；5×(10%) 1.200/5.54/70.93/73.44/57.49；10×(25%) 1.197/5.55/70.71/73.31/56.22；30×(50%) 1.201/5.59/72.49/73.28/56.66。损失非单调、最低点在 10×(25%)，域外 PPL 全程 5.54–5.59，九项下游对无嵌入基线没有一致改善，MMMLU 一路走低（58.32→56.22，30× 处 56.66）。Table 8 的模型档位与 token 预算在正文与表题里都没写，基线损失 1.202 与 Table 7/9 的 1.585 差 0.38，两表的绝对损失不可并排。

**固定 MoE 预算（Table 9）**。词表 20V→200V，总参数随之外涨：损失 None 1.585、20V 1.553、50V 1.541、100V 1.534、200V 1.526，单调下降。下游分三类：MMLU 62.78→64.85 缓涨，MMLU-Pro 与 SuperGPQA 见顶于 100V（35.87、21.93）；MATH 32.52→37.38（20V）→35.34、GSM8K 59.21→65.09（20V）→62.96、BBH 53.40→57.56（50V）→56.23 都是先涨后回落；中文两项 C-Eval 66.91→71.75→72.12→73.75→74.94 与 CMMLU 68.10→72.29→72.48→72.73→73.24 全程单调。

**报告写到的解释与没写到的**。报告写到的两处：固定总参数档的「同一最优点在别的评估上不成立、域外 uncheatable PPL 各预算间变化很小、下游对纯 MoE 基线无明确改善」，据此得出「n-gram 嵌入与 MoE 专家在扩容上扮演不同角色」，于是改用固定 MoE 预算重测；固定 MoE 档的「损失单调下降而下游不跟同样的趋势、部分基准饱和或波动、中文基准随词表一致改善」。报告没有给分岔的机制解释，uncheatable PPL 这一列在正文与表题里都没有定义（全文只出现在 Table 8 表头与 §2.3.2 一句里）。以下几条是候选解释方向，报告未写，标明为猜想：其一，300 TPP 的短预算下容量尚未吃满，静态表的额外容量先落在损失的低频可预测部分，中文分词与形态覆盖正是词表敏感项，与中文基准单调上升相容，推理与数学类任务要的是计算侧容量；其二，固定总参数档里削专家补表会同时改变路由粒度，Table 8 的读数混着两件事；其三，MATH 与 GSM8K 在 20V 见顶后回落，与「表已够覆盖局部共现、再扩只稀释专家」相容。三条都要更长预算或分任务类型的损失分解才能判。

**对照的外部账**。Engram 一条补齐：Cheng et al. 的 "Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models" 预印本编号 arXiv 2601.07372（2026-01-12 首发，Xin Cheng、Rui Tian、Wangding Zeng、Damai Dai、…、Huishuai Zhang、Dongyan Zhao、Wenfeng Liang 共 21 位，机构写北京大学与 DeepSeek-AI），方法名 Engram，机制是后缀 n-gram 经多头哈希（每阶 $K$ 个头、表大小取素数）做 $O(1)$ 查表、配 tokenizer 压缩与上下文化门控，表卸载到主机内存运行时预取。它的分配账是一条 U 形：定义 $\rho$ 为分给 MoE 专家的不活跃参数比例，两个算力档（$2\times10^{20}$ 与 $6\times10^{20}$ FLOPs）都在 $\rho\approx80\%$（稳定区间 75%–80%）见最优，也就是 20%–25% 给查表记忆；卸载账是 4B 稠密基线 9,031.62 token/s 加 100B Engram 后 8,858.28、8B 基线 6,315.52 加 100B 后 6,140.02，惩罚峰值 2.8%；词表压缩用 NFKC 与小写化把 128K 词表的等效规模降 23%（`https://arxiv.org/html/2601.07372v2`）。本件 Table 8 的 10×(25%) 点位与 Engram 的 20%–25% 甜点同区间，报告那句「consistent with the allocation sweet spots reported in prior work (Liu et al., 2026; Cheng et al., 2026)」正是这一处。本库的 [[deepseek-v41-flash-context|DeepSeek-V4.1-Flash 增强信息]] 页已把 Engram 记为该模型 196B 条件记忆件的出处，n-gram 查表这一支在同代两家的权重里都已落地。

《Scaling Embeddings Outperforms Scaling Experts in Language Models》（arXiv 2601.21204，2026-01-29，Hong Liu 等 16 位，通讯邮箱 @meituan.com，美团 LongCat 一线）的被检验对象是一元嵌入表（$d_{\text{model}}\times N$），落地件 LongCat-Flash-Lite 68.5B 总 / 约 3B 激活、30B 以上给嵌入，摘要主张固定预算下嵌入侧的 Pareto 前沿优于专家侧、尤其在 agentic 与 coding 域（`https://arxiv.org/abs/2601.21204`）。本件 Table 8 把这条判断从一元表搬到 n-gram 表上检验，读数落在「两种容量扮演不同角色」。X-GRAM（arXiv 2604.21724v1，Yilong Chen 等 13 位，中科院信工所、国科大、北京大学与 IQuest Research，Bryan Dai 在列）做的是频率感知的动态 token 注入：混合哈希加别名混排压 Zipf 长尾、归一化 SwiGLU ShortConv 精修查得向量、深度感知门控接进注意力值流与层间残差，0.73B/1.15B 档对基座平均涨 4.4 分（`https://arxiv.org/html/2604.21724v1`）。N-Grammer（arXiv 2207.06366，Aurko Roy 等 16 位，Google）的 n-gram 是潜空间的：一元嵌入经 PQ 码本离散成 latent bigram id、再哈希进一张可训练的 bigram 表，它加参数，与本件表面 n-gram 哈希表的差别在构造对象是码本 id 对 token id（`https://arxiv.org/html/2207.06366`）。STEM（arXiv 2601.10639，Ranajoy Sadhukhan 等 8 位，CMU 与 Meta AI）把 FFN 的 up-projection 换成层内静态 token 索引查表、gate 与 down 保持稠密，去掉运行时路由、支持 CPU 卸载与异步预取，约省三分之一 FFN 参数。L3（Tseng 与 De Sa，arXiv 2601.21461，ICML 2026，PMLR 300:61557–61579）把嵌入表推广成解码器层里的静态 token 路由查表，配 CPU 卸载推理与信息论的分配界，做到 2.6B 激活。《Over-tokenized Transformer: Vocabulary is Generally Worth Scaling》（arXiv 2501.16975，Hongzhi Huang、Defa Zhu 等 7 位，ICML 2025，PMLR 267:24111–24129，开源名 over-tok）把输入输出词表解耦、输入侧用 multi-gram 放大，损失对输入词表近似对数线性。Yu et al.《Scaling Embedding Layers in Language Models》（arXiv 2502.01637，Da Yu、Edith Cohen、Badih Ghazi、Yangsibo Huang、Pritish Kamath、Ravi Kumar、Daogao Liu、Chiyuan Zhang，NeurIPS 2025）的 SCONE 把 n-gram 嵌入放在加速器外，固定加速器预算下沿嵌入大小与 n-gram 度两条轴放大，1B 加速器常驻件对 1.9B 基线约一半 FLOPs 与内存取胜。Gemma 3n 的官方概览页把参数分成文本/视觉/音频/每层嵌入（PLE）四组，PLE 表缓存在本地快速存储、E2B 有效加载约 1.91B 参数，页内不见 Medusa 一名（`https://ai.google.dev/gemma/docs/gemma-3n`）；Gemma 4 技术报告（arXiv 2607.02770，Gemma Team 323 项作者）Table 1 与 §2 写明 E2B 与 E4B 沿用 Gemma 3n 的 per-layer embeddings。RWKV-V8 的 DeepEmbed 是给词表每个 token 在每层 FFN 里训一个可学习高维向量、推理期存 RAM/SSD，明写「不占显存甚至不占内存」的边端稀疏设计（`https://wiki.rwkv.com/basic/architecture.html`）。本件发布件里 `ple_layer_ids`、`ple_embed_dim`、`ple_conv_kernel_size` 三个键名走 Gemma 3n 的 per-layer embeddings 叫法，`ngram_*` 五个键名走 Engram 的哈希表叫法，两套命名在同一份 config 里并存（猜想：实现谱系同时接这两条线，键名是可见的痕迹）。

### 四、Muon 分工与缩放律重拟合的推导链

**分工清单**。Muon 侧：注意力 q/k/v 与输出投影、GDN 输入与输出投影、路由专家与共享专家的 fc1/fc2、n-gram 的键值投影。AdamW 侧：输入嵌入、输出头、MoE 路由、GR 的两个低秩投影、注意力与 GDN 的输出门。Adam（关权重衰减）侧：n-gram 表本体。报告给的理由逐条：路由上 Muon 放大早期训练波动，中后期再上不致失稳也无明显收益，作者猜「路由每个输出维对应一个专家的分数、维度间基本独立、没有共享线性结构给正交化利用」；GR 的两个低秩投影因形状过长走 AdamW 更好；输出门上 AdamW 与 Muon 持平或略好；GDN 的衰减与 beta 投影每头出一个标量、是向量，正交化无意义。融合矩阵按语义拆开再喂 Muon：qkv 与 GDN 输入投影按头拆（损失与下游同升），SwiGLU fc1 拆成 gate 与 up 两半（损失基本不动、下游略升），拆分同时给出把单个子矩阵排除在 Muon 之外的粒度。

**缩放式的实名**。$0.2\sqrt{\max(A,B)}$ 出自 Moonshot 的式 (4)：$W_t=W_{t-1}-\eta_t\big(0.2\cdot O_t\cdot\sqrt{\max(A,B)}+\lambda W_{t-1}\big)$，动机是 AdamW 的更新 RMS 常在 0.2 到 0.4 之间、把 Muon 的更新 RMS 配到这个区间（`https://arxiv.org/html/2502.16982v1`）。Muon 自己的参考实现只按长宽比缩放，`update *= max(1, update.size(-2)/update.size(-1))**0.5`（`https://github.com/KellerJordan/Muon/blob/master/muon.py`）。本件 §3.1 把该缩放式引向 Liu et al., 2025b，指向正确；Nesterov 动量则是 Muon 原文的默认（博客原话「using Nesterov-style momentum for Muon works a bit better than normal SGD-momentum in every case we have tested」，仓库默认 `beta=0.95, ns_steps=5, nesterov=True`）。

**Newton–Schulz 的步数账**。本件取 8 步、Polar Express 逐步系数、Nesterov 动量 0.95、Frobenius 归一常数 $10^{-14}$。Polar Express（arXiv 2505.16932v5，Noah Amsel、David Persson、Christopher Musco、Robert M. Gower）的逐步系数解的是给定步数预算下的极小极大问题，主实验用 5 步，消融写「2 或 3 步差于 5 或 6 步，再往上（甚至用 SVD 精确算）不改善优化质量」，并给出固定系数的 Newton–Schulz 前 17 步几乎无进展、Jordan 的调好在 11 步后停在约 0.3 误差（`https://arxiv.org/html/2505.16932v5`）。本件取 8 步的理由是「比少步更准的正交化、并降低压力测试里梯度范数尖峰的幅度与频次」，落点在稳定性一侧，与 Polar Express 按损失判优的口径不同档。

**NS 的成本与分布式实现**。NS 迭代要求对每个完整参数矩阵做整体更新，$K$ 步约 $4K\max(A,B)\min(A,B)^2$ FLOPs，与 Megatron 的分片冲突两处：TP 下没有 rank 持有完整权重，DP 下代价随短边立方、等元素切分留下严重掉队者。Canzona（arXiv 2602.06079v1，2026-02-04，Liangyu Wang、Siqi Zhang、Junjie Wang、Yiming Dong、Bo Zheng、Zihan Qiu、Shengkun Tang、Di Wang、Rui Men、Dayiheng Liu；机构记 KAUST、阿里巴巴、北京大学、MBZUAI，脚注写明三位作者是阿里巴巴实习生）把逻辑优化器分配与物理参数布局解耦：$\alpha$-balanced 静态分区器搬运整参数（张量内不切）把各 DP rank 的估计 NS FLOPs 拉平，异步 Micro-Group 流水线用融合 All-to-All 跨 TP 重建每个 Muon 所属矩阵，owner 跑的步与单设备 Muon 数学等价，ZeRO-1 的桶几何保留、Reduce-Scatter 与反向的重叠不丢；报 Qwen3 家族 1.7B–32B、256 卡上端到端迭代 1.57 倍加速、优化器步延迟降到 1/5.8，不均衡比从 3.24 倍（FLOPs）与 2.46 倍（内存）压到 1.43 与 1.11（`https://arxiv.org/html/2602.06079v1`）。第二处工程账：拆完之后一层贡献上百个子矩阵，优化器步成为一长串受启动开销约束的小 kernel，整步用 CUDA graph 捕获。

**缩放律的推导链**。报告的链条是六步：新架构与新优化器在压力测试里明显更稳（§3.3）→ 稳定性余量意味着更激进的超参可用（§3.2 动机段）→ 重拟合 Kaplan 一路的批量与学习率律 → 预测点向更大批量与更高学习率移动、学习率随模型变大的衰减变慢 → 两条预测各自放到最敏感的区间验：批量放在小模型长训（20 层 10.8B-A0.89B、4T token），学习率放在大模型短训（48 层 156B-A7B、419B token）→ 结果：批量账 1.5774（旧配方 12.6M）对 1.5702（25.2M）对 1.5707（37.7M），预测点下方陡升、上方近平；学习率账旧配方高 $7.8\times10^{-3}$、四个邻近设置彼此差在 $7\times10^{-4}$ 内、$B\times1.25$ 名义最好领先 $3\times10^{-4}$，Table 10 的七项均值 60.55 对旧配方 56.41，五 run 在 warmup 之后裁剪器一次未触发、预测最优点最大未裁剪梯度范数只到阈值的 28%、旧配方 51%。报告自己给 Table 10 的排序加了限定：单次评估、前四档差距小、这些差异大概落在评估噪声里，读数按观察量处理。报告没有写出重拟合后的函数形式与拟合数据点，只给出预测值与检验值，两处预测各自的公式与拟合区间在正文里不可复算。

**批量能放大的三条依据**。Muon 在大批量下保住数据效率（Essential AI，arXiv 2505.02222v4，摘要原话是 Muon 比 AdamW 更能保住远超临界批量的大批量下的数据效率，实验做到 4B 参数，`https://arxiv.org/abs/2505.02222`）；低于预测点比高于预测点更伤（自家扫描，Figure 8a）；MoE 大批量让每个专家每步拿到足量多样 token 信号（引 arXiv 2501.11873）。第三条的原文口径要收窄：那篇《Demons in the detail》研究的是负载均衡损失的聚合范围，标准框架在 micro-batch 内算损失会强制每条序列均匀路由、抑制专家专门化，改在全局批次上算可促进语料级均衡、显著提升专家领域专门化（做到 42.8B 参数、400B token），它的自变量是均衡损失的聚合批，与吞吐批量大小是两回事。

**批量 warmup 的判词与机制**。两条 ramp 从 6.3M 起、每次加 6.3M、到 524B token 处达 25.2M，一条保持常数批量最优的峰值学习率、一条下调峰值学习率配早期小批量；两条都落在 run-to-run 方差内、分别比常数基线差 $2.5\times10^{-4}$ 与 $3.5\times10^{-4}$，还多花 18.8% 优化步。机制叙述：爬升期同学习率下小批量带来更高梯度噪声、损失更高；批量到位后短暂领先来自早期攒下的更多优化步；学习率衰减、接近收敛时步数优势被中和，常数批量最终胜出。稳定性无碍：没有哪一步损失超局部中位数 0.1，p99.9 未裁剪梯度范数 0.088–0.190，阈值 0.5。临界批量的传统依据两条：McCandlish 等（arXiv 1812.06162）给的是临界批量随损失下降而增长的实测模型；Zhang 等（arXiv 2410.21676，85M–1.2B 模型、C4）的实测主张是临界批量主要随数据量增长、随模型规模基本不涨（`https://arxiv.org/abs/2410.21676`），第二条与「按模型大小放大批量」这一路不同向，读 §3.2 那段时把两条的分量分开。

**压力测试的方法学与两条对照**。方法学引 Wortsman 等（arXiv 2309.14322，ICLR 2024）：注意力 logit 增长与 logit/对数概率发散两类失稳在小模型高学习率下同样出现，大规模的缓解手段在那里同样有效；该文的旋钮有两把，抬学习率与缩短归一化长度，本件只用抬学习率这一把（`https://arxiv.org/abs/2309.14322`）。Dehghani 等（arXiv 2302.05442，22B ViT）在 §3.3 开篇承担的是大规模失稳的例子。两条对照件：qk-clip 在 Kimi K2（arXiv 2507.20534v2）的 MuonClip 一节，机制是最大 logit 超过阈值时按 $\gamma_h=\min(1,\tau/S_{\max}^h)$ 逐头缩放 q/k 投影权重，K2 以 15.5T token 训完零损失尖峰（`https://arxiv.org/html/2507.20534v2`）；SwiGLU 截断在 gpt-oss 模型卡（arXiv 2508.10925v1）里只有一条脚注「Our SwiGLU implementation is unconventional, including clamping and a residual connection」，全文不见 SwiGLU-clip 这个术语、也没给截断公式与稳定性动机（`https://arxiv.org/html/2508.10925v1`）。本件 §3.3 说「不需要 qk-clip 与 SwiGLU-clip 这类显式激活控制」，两条引用的支撑强度不同档：K2 一条给的是可复述的机制，gpt-oss 一条给的是脚注级的存在性。

**路由分工的外部位置**。本件把路由留在 AdamW 并给出猜想式解释，这条判断在公开文献里两侧都有位置：Moonshot（arXiv 2502.16982）把 Muon 用在包括路由在内的矩阵参数上，并报 Muon 带来的 SVD 熵提升在路由权重上更显著、据此说 MoE 更能吃到 Muon 的好处；《Symmetry-Compatible Principle for Optimizer Design: Embeddings, LM Heads, SwiGLU MLPs, and MoE Routers》（arXiv 2605.18106）从对称性一侧论证双随机正交更新与路由的置换及共享平移对称不相容，给路由与嵌入配单边谱、行范数类更新（`https://arxiv.org/abs/2605.18106`）。本件这条经验观察与后者的理论口径同向，Moonshot 的实践口径把路由放在 Muon 一侧，报告自己把本件的解释写成「One possible explanation」。

**稳定性收益的三段账**（Figure 13 与 §3.3）：生产学习率下前 276B token、同数据序同学率日程同优化器的三件对照，Qwen3.5 结构加 Muon 为基线，加 GR 降 0.026，整套 Flash-Next 配方再降 0.032，合计 0.058；梯度范数上纯 Muon 的中位数约为两条带门 run 的两倍、p99.9 是 4.2 倍（0.097/0.298 对 0.053/0.071 与 0.043/0.066），且是唯一撞过裁剪阈值的；带门 run 在 1000 步窗内的标准差低 4.3–4.7 倍；把残差读与 LM 头前的最后一次归一化融成一个带门读操作进一步降梯度范数，报告猜这是 Flash-Next 与 Muon+GR 差值的主因；激活侧加 GR 后每层残差最大激活一致下降，各探测深度一致。

## 引用落在哪

技术报告参考文献共约 180 条。下表收录承担论证的条目，逐条回一手渠道（arXiv API 与 Hugging Face API），访问日期均为 2026-09-23。落点用报告自身的节号与表号，外指他文一律冠名。

**一、架构组件的直接前作与对手**

| 本篇指称 | 一手出处 | 篇内落点 |
|---|---|---|
| Gated DeltaNet（GDN） | arXiv 2412.06464v3，2024-12-09，Songlin Yang 等 | §2.1.1（循环层机制）、§3.1（GDN 投影的优化器分工） |
| DSA / DeepSeek-V3.2 | arXiv 2512.02556，2025-12-02，DeepSeek-AI 集体署名（264 项作者） | §2.1.2（QSA 的路线归属与索引器开销的对照） |
| IndexCache（IndexShare） | arXiv 2603.12201，2026-03-12，Yushi Bai、Qian Dong 等 8 位（Z.ai 与清华大学） | §2.1.2（相对索引器延迟 0.25 的对照基线） |
| SeerAttention | arXiv 2410.13276v4，2024-10-17，Yizhao Gao 等 11 位 | §2.1.2（内在稀疏注意力一路） |
| ProxyAttn | arXiv 2509.24745，2025-09-29 首发，Yixuan Wang、Huang He、Siqi Bao、Hua Wu、Haifeng Wang、Qingfu Zhu、Wanxiang Che（哈工大与字节跳动），ICLR 2026，pp. 18603–18617 | §2.1.2（代表头引导稀疏一路；块级 max-pool 教师的实打实来源是上一行的 SeerAttention） |
| GLM-5 | arXiv 2602.15763，2026 | §2.1.2（MTP 段跨投机步复用 top-k 索引） |
| Hyper-Connections（HC） | arXiv 2409.19606v3，2024-09-29，Defa Zhu 等 8 位 | §2.2（加宽残差流的来源） |
| mHC | arXiv 2512.24880v2，首发 2025-12-31，Zhenda Xie、Yixuan Wei 等 20 位（DeepSeek-AI） | §2.2（静态与动态门控的对照、Table 5 的对手） |
| xHC | arXiv 2607.14530，2026-07-16，Xiangdong Zhang 等 13 位 | §2.2（同族加宽工作） |
| Alternating Updates（AltUp） | arXiv 2301.13310v2，2023-01-30，Cenk Baykal 等 6 位 | §2.2（简化版 AltUp 用来隔离「宽度本身」的收益） |
| Value Residual Learning | arXiv 2410.17897v5，2024-10-23，Zhanchao Zhou 等 5 位 | §2.2（给注意力值开额外残差路；ResFormer 与 SVFormer） |
| Virtual Width Networks（VWN） | arXiv 2511.11238v2，2025-11-14，ByteDance Seed 集体署名（119 项作者），通讯作者 Defa Zhu | §2.2（同族对照：Over-Width Embedding 把隐向量切成 $m$ 段做逐段读写） |
| Attention Residuals（AttnRes） | arXiv 2603.15031，2026-03-16，Kimi Team 集体署名（37 项作者） | §2.2（Table 6 的对照） |
| Highway Networks | arXiv 1505.00387，2015-05-03，Srivastava、Greff、Schmidhuber | §2.2（逐层读写门控的早期形态） |
| DenseNet | arXiv 1608.06993，2016-08-25，Gao Huang 等 | §2.2（稠密跨层连接） |
| Gated Attention | arXiv 2505.06708，2025-05-10，Zihan Qiu 等 13 位 | §2.1.1（输出门一族）、§3.3（门控与稳定性） |
| 注意力与残差流的 outlier 重标定 | arXiv 2601.22966，2026-01-30，Zihan Qiu 等 19 位 | §2.2（GatedNorm 的出处）、§3.3 |
| zero-centered RMSNorm、RoPE、GQA/MQA、SwiGLU | arXiv 2412.15115 与 arXiv 2505.09388 谱系下的既有标准件 | §2.1.1、§2.1.2 |

**二、嵌入侧容量**

| 本篇指称 | 一手出处 | 篇内落点 |
|---|---|---|
| N-Grammer | arXiv 2207.06366，2022-07-13，Aurko Roy 等 16 位 | §2.3（潜在 n-gram 增广 Transformer） |
| L3: Large Lookup Layers | arXiv 2601.21461，2026-01-29 首发，Albert Tseng 与 Christopher De Sa，ICML 2026（第四十三届），PMLR 300:61557–61579 | §2.3（查表扩容） |
| Engram（报告里写作 Cheng et al., 2026） | arXiv 2601.07372，2026-01-12 首发，Xin Cheng、Rui Tian、Wangding Zeng、Damai Dai 等 21 位（北京大学与 DeepSeek-AI），《Conditional Memory via Scalable Lookup》，ACL 2026 正式版同题 | §2.3（n-gram 条件化、确定性寻址可卸载、分配甜点位、token 归一做词表压缩） |
| Over-tokenized Transformer | arXiv 2501.16975v2，2025-01-28 首发，Hongzhi Huang、Defa Zhu 等 7 位，ICML 2025，PMLR 267:24111–24129 | §2.3（词表本身值得放大） |
| Scaling Embedding Layers（SCONE） | arXiv 2502.01637v3，2025-02-03 首发，Da Yu、Edith Cohen、Badih Ghazi、Yangsibo Huang、Pritish Kamath、Ravi Kumar、Daogao Liu、Chiyuan Zhang（Google Research），NeurIPS 2025 camera-ready | §2.3（加速器外 n-gram 嵌入、固定常驻预算下放大） |
| STEM | arXiv 2601.10639，2026-01-15，Ranajoy Sadhukhan 等 8 位 | §2.3（嵌入模块扩容） |
| Scaling Embeddings Outperforms Scaling Experts | arXiv 2601.21204v2，首发 2026-01-29，Hong Liu 等 16 位 | §2.3.2（固定总参数消融要检验的判断） |
| X-GRAM | arXiv 2604.21724v2，2026-04-23，Yilong Chen 等 13 位 | §2.3.2（词表压缩与 token 归一，本文称无一致收益） |
| Gemma 3n | Google DeepMind，2025，模型概览页 | §2.3（加速器外嵌入表的可卸载性） |
| RWKV-V8 DeepEmbed | `https://wiki.rwkv.com/basic/architecture.html#rwkv-v8-s-deepembed`，报告自标访问日期 2026-08-20 | §2.3（同族做法） |

**三、优化器、缩放律与稳定性方法学**

| 本篇指称 | 一手出处 | 篇内落点 |
|---|---|---|
| Muon | Keller Jordan，2024-12-08，`https://kellerjordan.github.io/posts/muon/`（博客与代码仓库） | §3.1（正交化更新方向） |
| Muon is Scalable for LLM Training | arXiv 2502.16982，2025-02-24，Jingyuan Liu、Jianlin Su 等 28 位（以 Moonshot AI 为主） | §3.1（$0.2\sqrt{\max(A,B)}$ 缩放的出处，该文式 (4)）、§3.2（学习率换算口径） |
| Practical Efficiency of Muon for Pretraining | arXiv 2505.02222v4，2025-05-04，Essential AI 集体署名 25 项 | §3.1、§3.2（批量下的数据效率） |
| Polar Express | arXiv 2505.16932v5，2025-05-22，Noah Amsel、David Persson、Christopher Musco、Robert M. Gower | §3.1（Newton–Schulz 逐步系数表） |
| Canzona | arXiv 2602.06079，2026-02-04，Liangyu Wang、Siqi Zhang、Junjie Wang、Yiming Dong、Bo Zheng、Zihan Qiu、Rui Men、Dayiheng Liu 等 10 位 | §3.1（张量并行与 ZeRO-1 下的等价实现） |
| 缩放律 | arXiv 2001.08361，2020-01-23，Kaplan 等 | §3.2（重拟合的对象） |
| 临界批量的经验模型 | arXiv 1812.06162，2018-12-14，McCandlish 等 | §3.2（批量 warmup 的传统依据） |
| 预训练中临界批量如何缩放 | arXiv 2410.21676v4，2024-10-29，Hanlin Zhang 等 | §3.2 |
| 小规模复现大规模失稳 | arXiv 2309.14322，2023-09-25，Mitchell Wortsman 等 17 位（ICLR 2024） | §3.3（压力测试方法学：抬高学习率复现失稳） |
| 大规模失稳的例子 | arXiv 2302.05442，2023-02-10，Mostafa Dehghani 等 42 位（Scaling Vision Transformers to 22B） | §3.3 开篇（大规模才出现的稳定性问题） |
| 层冗余与早层的重要性 | arXiv 2403.03853，2024-03-06，Xin Men 等；Elhage 等《A Mathematical Framework for Transformer Circuits》，Transformer Circuits Thread，2021 | §2.2（GR 支路分解的旁证：早层输出跨深度保留） |
| 梯度裁剪 | arXiv 1211.5063v2，2012-11-21，Pascanu、Mikolov、Bengio | §3.3（阈值 0.5） |
| qk-clip | arXiv 2507.20534v2，首发 2025-07-28，Kimi Team（Kimi K2，200 项作者） | §3.3（本文称不需要显式激活控制） |
| SwiGLU-clip | arXiv 2508.10925，2025-08-08，gpt-oss-120b/20b 模型卡 | §3.3（同上） |
| 训练系统底座 | arXiv 1909.08053v4，2019-09-17，Shoeybi 等（Megatron-LM）；Yang & Zhang，2024 的 FLA Triton kernel | §2.1.1（FlashQLA 的对照）、§3.1（融合矩阵的拆分） |
| 无辅助损失负载均衡与 MoE 专门化 | arXiv 2501.11873v2，2025-01-21，Zihan Qiu 等 10 位 | §3.2（大批量对专家信号的作用） |
| 路由与谱更新不相容的对称性论证 | arXiv 2605.18106，《Symmetry-Compatible Principle for Optimizer Design: Embeddings, LM Heads, SwiGLU MLPs, and MoE Routers》（报告未引，外部对照件） | 本节「路由分工的外部位置」 |
| 评估夹具 | MMLU（Hendrycks 等，ICLR 2021）、MMLU-Pro（Wang 等，NeurIPS 37:95266–95290，2024）、MMLU-Redux（Gema 等《Are we done with MMLU?》，CoRR abs/2406.04127，2024）、SuperGPQA（arXiv 2502.14739，首发 2025-02-20）、BBH（Suzgun 等，Findings of ACL 2023，pp. 13003–13051）、GPQA（Rein 等，First Conference on Language Modeling，2024）、GSM8K（arXiv 2110.14168）、MATH（arXiv 2103.03874）、EvalPlus（arXiv 2305.01210）、MultiPL-E（Cassano 等，2023）、SWE-bench（arXiv 2310.06770）、MGSM（Shi 等，2022）、MMMLU（OpenAI，2024，数据集页）、INCLUDE（arXiv 2411.19799）、RULER（arXiv 2404.06654）、MRCR（OpenAI，2025）——以上逐条对回报告参考文献列表（抽取正文的 References 一节），列表只给会议名的条目照原样记录 | §2.1.1、§2.1.2、§4（各表的评估口径） |

**四、报告之外、承重数字还在的两件发布件**

| 件 | 一手出处 | 用途 |
|---|---|---|
| Hugging Face 模型卡 | `https://huggingface.co/Qwen/Qwen3.8-Flash-Next`，仓库创建于 2026-08-24T08:24:59Z，末次改动 2026-08-27T05:03:36Z，144 个文件，月度下载 807,550、点赞 5,624，pipeline_tag 为 image-text-to-text，许可 `qwen-community-1.0`（Hugging Face API，访问日期 2026-09-23） | 层排布、头数、专家数、n-gram 表大小、MTP 参数量、上下文窗口、后训练档基准数字的唯一来源 |
| 权重仓库 `config.json` | `https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/config.json`（访问日期 2026-09-23） | 与模型卡逐项对齐：`num_hidden_layers=48`、`full_attention_interval=4`、`hidden_size=2560`、`num_experts=512`、`num_experts_per_tok=10`、`indexer_budget=2048`、`indexer_compress_ratio=4`、`indexer_n_heads=4`、`indexer_kv_heads=1`、`ngram_size=3`、`ngram_vocab_size_base=20000000`、`heads_per_ngram=8`、`ple_layer_ids=[2]`、`hc_lowrank=320`、`output_gate_type=sigmoid`、`mtp_num_hidden_layers=1`、`vocab_size=248320`；架构类名 `Qwen4ExpForConditionalGeneration`、model_type `qwen4_exp` |

## 谁做的

组织面：作者栏集体署名 Qwen Team，机构由仓库 README 的 BibTeX 写为 Alibaba Group（`@techreport{qwen2026design, institution = {Alibaba Group}, month = {August}, year = {2026}}`）。发布渠道三处：GitHub 组织 `QwenLM`、Hugging Face 组织 `Qwen`、ModelScope 组织 `qwen`（README Models 一节）。Hugging Face 组织页名为 Qwen，名下模型数超过 100 个（API 分页首页即 100 条，访问日期 2026-09-23）。

人的名单：报告 §6 分两档。Core Contributors 10 人，Zihan Qiu、Zekun Wang、Xiao Li、Yanpeng Li、Yang Xu、Yixuan Wang、Huaqing Zhang、Rui Men、Bo Zheng、Dayiheng Liu，末两位带 B 上标标记（PDF 里 B 为上标，正文与页脚未见标记含义的图例）。Contributors 26 人，Bochao Mao、Chengruidong Zhang、Fan Zhou、Hao Luo、Haofeng Huang、Haoran Lian、Haoyan Huang、Hongqing Chen、Jianwei Zhang、Jing Xu、Junjie Wang、Langshi Chen、Liangyu Wang、Linlang Jiang、Man Yuan、Minmin Sun、Peng Jin、Siqi Zhang、Siyu Wang、Xingzhang Ren、Yakai Wang、Yi Zhang、Yiming Dong、Yizhong Cao、Yubo Ma、Yunfei Mao，带编号脚注标记。arXiv 条目 2608.30320v1 的作者栏把 36 人逐个列出，顺序为 8 位核心贡献者、26 位贡献者、Bo Zheng、Dayiheng Liu（arXiv API，访问日期 2026-09-23）。

领衔者的可查线索：第一作者 Zihan Qiu 是本件三处关键件的前序论文第一作者——门控注意力（arXiv 2505.06708）、注意力与残差流的 outlier 重标定即 GatedNorm 的出处（arXiv 2601.22966）、MoE 负载均衡损失的实现细节（arXiv 2501.11873），同时也是本件引用的分布式矩阵优化器框架 Canzona（arXiv 2602.06079）的合著者之一，那条的作者表里还有 Liangyu Wang、Siqi Zhang、Junjie Wang、Yiming Dong、Bo Zheng、Rui Men、Dayiheng Liu，与本件 Contributors 与 Core Contributors 高度重合（arXiv API，访问日期 2026-09-23）。这条线索说明本件的架构件与优化器件各有组内前作垫底。

发布件的时间线：Hugging Face 权重仓库 2026-08-24 创建；技术报告 PDF 元数据与 README 的 News 都落在 2026-08-26；README 快照的 commit 时间 2026-08-27；模型卡末次改动 2026-08-27；arXiv 提交 2026-08-31。权重先于报告、报告先于 arXiv 挂出（各来源同上一条与下一表，访问日期 2026-09-23）。

## 这个组与作者的特点

- **同代三件并行发布，本件是架构档**。Hugging Face 上 Qwen3.8 一代的公开权重按创建日排：Qwen3.8-27B（2026-08-05）、Qwen3.8-2.4T-A95B（2026-08-08）、Qwen3.8-Flash-Next（2026-08-24），另有 27B 与 Flash-Next 的 FP8 版同日挂出（Hugging Face API，访问日期 2026-09-23）。月度下载量 27B 一档 6,912,469、Flash-Next 一档 807,550，旗舰 2.4T-A95B 一档 54,427。本件在家族里的位置是「小激活参数加新架构」的验证档，README 与模型卡都把它指向 Qwen4 的前身。
- **预览件这个体裁是重复动作**。README 自己把它排在 Qwen3-Next 之后：同一类混合架构改动当年先出 Qwen3-Next、后贯穿 Qwen3.5 到 Qwen3.8 四个系列，这次以同样的方式先出 Flash-Next。权重仓库的架构类名直接叫 `Qwen4ExpForConditionalGeneration`、model_type 叫 `qwen4_exp`，发布件里就带着「实验性架构」的标记。
- **报告体裁是消融集**。全文 28 页里 13 张图、11 张表，绝大多数是消融；训练数据量、算力、GPU 时数、语料配比一个绝对数字都没给，成本一律以相对 Qwen3.7-Plus 的比例表达。评估协议本身被当成贡献来写：三轴（损失与下游、三段成本、超参与稳定性）在摘要、§1、§5 三处反复申明，结论一节把「哪三处看似无害的捷径被这套协议拦下」列成清单（稀疏写会在后训练后退化、位置编码在前训练看着可省、批量 warmup 白花优化步）。
- **消融规模与生产规模分层**。所有机制级消融在 28 层 25B-A3B、20 层 10.8B-A0.89B、48 层 156B-A7B 这三档中小模型上做，token 预算 400B 到 4T；生产件 125B-A6B 只出现在最终对照表（Table 11）与早期段对照（Figure 13）。这套分层被作者写成显式的预算判断：每条主张在「完整评估预算仍可承受」的规模上测。
- **对同代对手的引用密度高、口径直**。DeepSeek（V3.2 与 mHC）、Kimi（K2、Attention Residuals、qk-clip）、GLM-5、Google DeepMind（Gemma 3n、Gemma 4）、OpenAI（gpt-oss、MRCR）、美团 LongCat 一族的嵌入扩容一文、Essential AI、Moonshot、Z.ai 都在承重位置被点名，模型卡的后训练对照表里直接并列 DeepSeek-V4-Flash-0731 与 Claude-Opus-4.6 (Max)（Hugging Face 模型卡 Benchmark Results 一节）。
- **作者层连续、领导层换过**。长期担任 Qwen 技术负责人的 Junyang Lin（林俊旸）不出现在本件任何一档作者名单里；公开报道记录他于 2026 年 3 月正式离开阿里巴巴，随后在上海创办新的 AI 实验室并获投资（Wikipedia 条目 `Junyang_Lin`，引 36Kr 2026-09-19、China Daily 2026-08-13、The Information 2026-05-13、Bloomberg 2026-08-12，访问日期 2026-09-23）。本件的核心贡献者一档由 Zihan Qiu 领衔，Rui Men、Dayiheng Liu、Bo Zheng 这几位从 Qwen2.5 与 Qwen3 技术报告一路在列的作者仍在名单里（arXiv 2412.15115 与 2505.09388 作者表比对，访问日期 2026-09-23）。
- **工程件与权重同步放出的习惯**。GDN kernel 库 FlashQLA 在正文里点名开源（`https://github.com/QwenLM/FlashQLA`，TileLang 写的融合线性注意力 kernel，报告称相对 FLA 的 Triton kernel 有 2–3 倍前向与约 2 倍反向加速，§2.1.1）。本跳重取 GitHub API 成功（前次限流，访问日期 2026-09-23）：语言 Python，星数 706，建仓 2026-04-24，末次推送 2026-09-18，v0.1.2（2026-07）同时作为 flash-linear-attention 的 GDN 后端，另有同名博客 `https://qwen.ai/blog?id=flashqla`。

## 核验备注

- 任务书点名的 `docs/` 目录与独立 release notes 文件在仓库里不存在；仓库只有 `README.md` 与 `tech_report.pdf` 两件，News 一节单条。README 全文 180 行已整件快照入库。
- 技术报告的 arXiv 条目 2608.30320v1 由本跳独立检索发现（仓库 README 与模型卡都只指向仓库内的 PDF 与官方博客，未给 arXiv 链接）。两版 PDF 均 28 页、摘要逐字一致、字节不同；本目录同时保留两件，抽取正文以仓库版为准。
- 官方发布说明页 `https://qwen.ai/blog?id=qwen3.8-flash-next` 与 `https://qwen.ai/blog?id=qwen3-next`、`https://qwen.ai/blog?id=qwen3.5` 为前端渲染，静态抓取判为「内容依赖 JavaScript 加载」，本次未取到正文（fetch 工具返回，访问日期 2026-09-23）。README 与模型卡都把基准细节指向博客，本库里的评测数字因此全部来自仓库 PDF 与 Hugging Face 模型卡两处可静态获取的一手件。
- 报告 §6 的作者标记含义已查明（本跳回 PDF 第 23 页页脚核对）：上标 B 的图例是「Corresponding authors.」，上标 1 的图例是「Alphabetical order.」。Bo Zheng 与 Dayiheng Liu 是通讯作者，Contributors 一档按字母序排列。前版「未见图例」的记录作废。
- 模型卡的 51B n-gram 参数已闭合：$20{,}000{,}000\times2560=51.2\times10^{9}$，行数取 `ngram_vocab_size_base`、嵌入维取 `ple_embed_dim`，哈希头与阶数折进行空间；20M 行对 250K 基线词表是 80 倍，发布件落在 Table 9 的 50V 与 100V 两行之间。报告与模型卡都未写这步换算，本跳算出。
- 模型卡的规格与 `config.json` 逐项对齐通过（见「引用落在哪」第四表）。两处口径提示：模型卡把 n-gram 嵌入写作「20,000,000（bigrams/trigrams at layer 2）」，`config.json` 的对应键是 `ngram_vocab_size_base=20000000` 与 `ngram_size=3`、`ple_layer_ids=[2]`；模型卡的 51B n-gram 参数与 20M 表项的关系需要按嵌入维与阶数换算，报告与模型卡都没给换算过程。
- 报告的 Table 1、Table 5、Table 7、Table 8、Table 9、Table 10 的评估管线统一写作「§2.1.1 的基准与评估管线」，即 28 层 25B-A3B MoE 在 400B 加 80B token 的 checkpoint 上跑九项；Table 2、Table 3、Table 11 用的是生产件 125B-A6B，两套九项均值的绝对水平不可跨表比较。
- 抽取正文的落点：`qwen3.8-flash-next.extracted.md` 由 `pdftotext -layout` 产出并做了轻量结构化（节号转标题、Figure/Table 行转引用块），公式与表格线有失真；承重数字全部回 PDF 原页与图核对过，图 13 张按原文编号整页区域渲染入库。本跳新增一处失真案例：§3.1 的 $\gamma(A,B)=0.2\sqrt{\max(A,B)}$ 在抽取文本里丢了根号（pdftotext 把 √ 吐成下一行行首的孤立 `p`），摘要页沿用了丢根号的写法；本跳回 PDF 第 16 页把该公式区域渲成图核对，根号存在。后续跳里凡公式系数一律回版面，不吃抽取件。
- 报告自身的两处印刷错误（PDF 原页即如此，非转换失真）：第 21 页把一个优化器名印成「AdmaW」；Figure 12 图例里 (c) 标号重复一次。两处不影响数字。
- Table 8 的模型档位与 token 预算正文未写：它的 None 基线损失 1.202，与共用 1.585 基线的 Table 7 与 Table 9 不同档，三表绝对损失不可并排；Table 7 的 2nd 行与 Table 9 的 50V 行逐列相同，说明放置消融跑在 50V 词表上。「uncheatable PPL」这一列名在全文没给定义，只出现在 Table 8 表头与 §2.3.2 一句里。§3.2 的重拟合只给预测值与检验值，没写函数形式、拟合点与生产件的实际批量与学习率。
- 报告正文里出现的 `Qwen Team, 2026` 一条同时承担两个所指：Qwen3.5 官方博客（消融底座与 n-gram 词表基准 V）与「上一代 397B-A17B 旗舰」的引用；§1 与 §4 用后者，§2.1.1 与 §2.3.2 用前者。
- 机构级指标（OpenAlex 的作者与机构记录）本次未取到：`raw_author_name.search` 过滤返回空计数、`authors?search` 端点在本次调用中未返回记录（Hugging Face 与 OpenAlex API，访问日期 2026-09-23），作者面的事实改由 arXiv 题录、报告 §6 名单与 Wikipedia 条目支撑。
- Qwen3-Next 的论文形态：arXiv 标题检索「Qwen3-Next」命中的三条均与本件无关（Memory-Sovereign Inference、Provably Shorter Scratchpads in Hybrid DeltaNet-Attention Decoders、Bloom-Aligned Educational Control），其中第二条标题直接研究 Hybrid DeltaNet-Attention 解码器，是第三方对这条架构线的后续分析（arXiv API，访问日期 2026-09-23）。
- 本跳新添的两处待核：正文与 Figure 5(a) 写作 IndexShare，该方法自己的文献题名是 IndexCache（报告参考文献条目也用 IndexCache），名字错位只在本件正文；§2.1.2 把「跨投机步复用 top-k 索引」归给 GLM-5，回该文全文未找到对应表述，归属按悬空记账。两处细节均在「机制细节与对照账」第一段。
- Engram 的发布件在本次核对时点没有可公开的权重仓库：Hugging Face 按作者 deepseek-ai 与关键词 Engram 检索返回空集、常见型号名的 `raw/main/config.json` 取不到（访问日期 2026-09-23），官方代码仓库 `https://github.com/deepseek-ai/Engram` 的 README 里没有 n-gram 配置键样例。本件发布件的 `ngram_*` 键与 Engram 的对应关系存为猜想，不作实现谱线的断言。

## 关联

- [[qwen3.8-flash-next-abstract|Qwen3.8-Flash-Next 摘要页]]：本页服务的对象的摘要。摘要页的优化一段仍写着丢根号的 `0.2·max(A,B)`，正确式子是 $0.2\sqrt{\max(A,B)}$，精读时以本页为准。
- [[qwen3.8-flash-next-reading|Qwen3.8-Flash-Next 精读报告]]（待写）：本页的机制账与对照账供该件取用。
- [[deepseek-v41-flash-context|DeepSeek-V4.1-Flash 增强信息]]：同一批外部件（Engram 条件记忆、mHC）在邻家发布件里的落点。
- [[attention-residuals|注意力残差]]：本件 Table 6 的对照机制的知识层页，那里记的是层级块粒度，本件的复现是子层粒度。
- [[kimi-delta-attention|Kimi Delta Attention]]：与本件 GDN 同属 delta 规则一族的循环注意力件，两家的门控粒度不同。
- [[nope-position-encoding|NoPE 位置编码]]：本件 §2.1.1 报出全注意力层去掉 RoPE 会推高后训练 endless generation 率，是该结论在另一条路线上的反面对照。
