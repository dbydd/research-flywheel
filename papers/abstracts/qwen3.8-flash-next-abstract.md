---
title: "Qwen3.8-Flash-Next（架构预览：GDN + QSA、Gated Residual、N-gram Embedding、Muon）"
slug: qwen3.8-flash-next-abstract
type: abstract
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

# Qwen3.8-Flash-Next（架构预览：GDN + QSA、Gated Residual、N-gram Embedding、Muon）

> [!quote] 官方摘要
> We describe the architecture and ablations of Qwen3.8-Flash-Next, a sparse mixture-of-experts model with 125B parameters, 6B activated per token, and additional 51B parameters of n-gram embedding tables held off the accelerator. On fourteen pre-training benchmarks the model leads the 397B-A17B predecessor on eight and trails it on the rest by at most 2.6 points, at 1/3 the activated parameters, 1/3 the training tokens, and roughly 1/9 the training FLOPs. Token mixing uses a layer-wise hybrid of Gated DeltaNet (GDN) and global attention, with one full-attention layer in every four; at continued-pretraining time those full-attention layers are replaced by Qwen Sparse Attention (QSA), which scores context at micro-block granularity with a compressed lightweight indexer. The residual stream is widened to four branches and read through an elementwise gate, a design we call the Gated Residual (GR). Capacity is added outside the backbone by a single n-gram embedding layer whose tables are prefetched from host memory. We evaluate every candidate change along three axes: loss together with downstream benchmarks; the cost of the change in training, prefill and decode; and its effect on the optimal hyperparameters and training stability. Loss and downstream accuracy do not always move together: enlarging the n-gram vocabulary lowers loss monotonically while downstream accuracy saturates. The architecture and the Muon optimizer together shift the optimal learning rate and batch size upwards, render batch-size warmup unnecessary, and substantially improve stability under stress tests. Loss, benchmarks, efficiency and stability form one design problem. Solved jointly, they yield a recipe that is simultaneously more efficient, more capable and more stable.
>
> —— 技术报告《On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability》摘要，2026-08-26；arXiv 同题条目 2608.30320v1（2026-08-31 提交，cs.CL）

## 一句话判断

这份资源交付一个「架构预览件」：Qwen3.8-Flash-Next 是 125B 总参数、每 token 激活 6B 的多模态稀疏 MoE，另有 51B n-gram 嵌入表放在加速器外的主机内存、4B MTP 参数，官方定位是 Qwen4 架构的首次开源验证件，角色等同于 Qwen3-Next 之于 Qwen3.5——把 Gated DeltaNet 加门控注意力的混合设计提前放出来给社区检验。承重改动四处：注意力用 GDN 与 Qwen Sparse Attention 的混合，每四层一个全注意力层，继续预训练时把全注意力层换成按 micro-block（r=4 token 压缩、K=2048 token 预算）打分的轻量索引器；残差流加宽到 4 支并用逐元素数据相关门控读写（Gated Residual）；容量加在骨干之外的一层 n-gram 嵌入（放在第 2 层，主机内存异步预取）；优化器换成按权重类别分工的 Muon 加 AdamW，并为新架构重拟合了缩放律。效率账落在同一张对照表上：14 个预训练基准里，它压过 397B-A17B 前代（Qwen3.7-Plus-Base）8 项，落后的 6 项最多差 2.6 分，代价是三分之一激活参数、三分之一训练 token、约九分之一训练 FLOPs。读这些数字要带的条件：架构消融全在 25B-A3B/28 层的中小规模上做，QSA 的长上下文收益在 512K 以上才显著，n-gram 词表扩大的 loss 收益与下游精度饱和这一处分歧被作者明确写进摘要。

## 规格（模型卡与 config.json 口径）

|项|取值|
|---|---|
|类型|带视觉编码器的因果语言模型（Hugging Face pipeline_tag 为 image-text-to-text）|
|参数|125B 总量、每 token 激活 6B；另加 51B n-gram 嵌入与 4B MTP|
|层数与排布|48 层，12 × (3 × (Gated DeltaNet → MoE) → 1 × (Qwen Sparse Attention → MoE))，即每四层一个稀疏注意力层|
|hidden / 词表|hidden 2560；token embedding 248320（padded）|
|GDN 线性注意力|V 头 48、QK 头 16，head_dim 128，短因果卷积核 4|
|QSA|Q 头 24、KV 头 2，head_dim 256，RoPE 维 64；索引器为 MQA，4 个查询头加 1 个共享键头，索引器 head_dim 128，压缩比 4，预算 512 块（2048 token）|
|MoE|512 个路由专家，每 token 激活 10 个路由加 1 个共享，专家隐维 640（共享专家同为 640）|
|Gated Residual|4 条残差支路，低秩瓶颈 rank 320，输出门类型 sigmoid|
|N-gram 嵌入|三阶（bigram/trigram），基础表 20,000,000 项，8 个哈希头，只挂在第 2 层|
|MTP|1 层，多步训练|
|上下文|原生 262,144，可外推到 1,000,000（YaRN，factor 4.0，rope_theta 1e7）|
|视觉侧|hidden 1152、16 头，输出投影到 2560|
|架构类名|`Qwen4ExpForConditionalGeneration`，model_type `qwen4_exp`|
|许可 / 权重|Qwen Community License 1.0；Hugging Face 与 ModelScope 公开，仓库 144 个文件|

## 架构要点

- **GDN 混合**。线性注意力把前缀压成固定尺寸状态、代价线性，全注意力层保留逐 token 的直接检索，比例取每四层一个。GDN 的 q/k 先过短因果卷积与 SiLU 再做 L2 归一化，写入强度 $\beta_t=\sigma(W_\beta x_t)$、衰减 $\alpha_t=\exp[-\exp(A)\,\mathrm{softplus}(W_\alpha x_t+b_\alpha)]$，头输出走 RMSNorm 后由有界 sigmoid 门调制（原论文用 SiLU 门，这里换掉并在全部实验中观察到一致提升），归一化沿用 Qwen3-Next 的 zero-centered RMSNorm。同规模的三方对照（28 层 25B-A3B MoE，400B token 的 4K 预训练加 80B token 的 32K 扩展）：全注意力九项均值 49.87、滑动窗口混合 51.15、GDN 混合 53.81，GDN 混合在九项里赢八项。
- **Qwen Sparse Attention**。走的是 DeepSeek-V3.2 的 DSA 路线，改动在打分粒度：键按 r 个 token 分块、平均池化加 RMSNorm 压成块键，索引器用 MQA 对块做 block-causal 打分（ReLU 相似度按头求和），选中的块展开成 token 下标再截到预算 K。取 K=2048、r=4 时每查询最多选 512 个完整块并带上末尾不完整块的尾巴。索引器自身的开销随序列长度下降，这是相对 DSA 的 O(n²) 索引器的主要差别。QSA 在 256K 序列的继续预训练阶段引入：先只训索引器 1,000 步（lr 1e-3，约 2B token），再骨干与索引器联合训 8,000 步（lr 2.5e-5，约 200B token），监督信号是教师注意力分布按头求和、L1 归一、max-pool 到块级后的 KL 散度。效果：8 项短上下文基准均值从 75.9 到 76.8（八项里七项持平或更好）；RULER 在 512K–1M 档从 90.08 到 93.00，8-needle MRCR 在 512K 从 30.66 到 40.53、1M 从 20.71 到 26.44；kernel 级在 1M 上下文下 prefill 快 7.6 倍、decode 快 4.9 倍；MTP 的平均接受长度基本不动（3.44→3.47 一档）。与 IndexShare 的对照里，QSA 在相对索引器延迟 0.25 处追平全注意力。
- **Gated Residual**。残差流加宽成 4 支，读用逐元素的数据相关权重（每支每通道一个权重），写用每支一个标量，配 group-RMSNorm，去掉支路间混合矩阵。消融链（25B-A3B，560B token）：pre-norm 损失 1.617、九项均值 50.91；静态加宽的 mHC 1.596/52.49；动态 mHC 1.594/54.47；GR 1.590/54.66。这里有一处被点名写出的分歧：静态到动态只再降 0.002 损失，同一步的平均精度涨 1.98 分（基线到静态涨 1.58 分）。GR 同时把 GatedNorm（RMSNorm 后接低秩瓶颈自门）折进块自身的归一化位置，训练稳定性收益在 §3.3 的压力测试里单独量化。
- **N-gram 嵌入**。一层、放第 2 层，用局部上下文查表，参数量随词表扩大而涨、每 token 计算量几乎不动，寻址确定因此可异步预取到主机内存。两种预算下的结论不同：固定总参数（削专家数补嵌入）时损失在 10× 词表（占 25%）处最低且下游无明确改善；固定 MoE 预算、词表从 20V 扩到 200V 时损失单调下降（1.585→1.526），下游精度饱和或波动，中文基准（C-Eval 66.91→74.94、CMMLU 68.10→73.24）随词表一致改善。词表压缩、非均匀阶数分配、按频次分槽都试过，无一致收益。
- **Muon 与超参**。Muon 用 Newton–Schulz 正交化（8 步，Polar Express 的逐步系数表，Nesterov 动量 0.95，更新按 $0.2\sqrt{\max(A,B)}$ 缩放——原页此处曾误作 0.2·max(A,B)，根号按技术报告 PDF 第 16 页版面订正；Frobenius 归一常数 1e-14），只用在真正充当线性映射的二维权重上（注意力 q/k/v 与输出投影、GDN 输入输出投影、路由与共享专家的 fc1/fc2、n-gram 的键值投影）；嵌入、归一化增益、GR 的两个低秩投影、注意力与 GDN 的输出门走 AdamW。Megatron 融合的 qkv、SwiGLU fc1、GDN 输入投影按语义拆开再喂给 Muon。重拟合缩放律把最优点推高：批量从 12.6M 提到 25.2M token（4T token 预算、10.8B-A0.89B 模型）比旧配方低 7.2e-3 损失，再放大 1.5 倍只亏 4.3e-4；批量 warmup 被判定不必要——两条 ramp 曲线落在 run-to-run 方差内、还多花 18.8% 优化步。学习率预测在 48 层 156B-A7B、419B token 上检验，预测最优 (B=8.4M, η=1.76e-3)，旧配方高 7.8e-3，最优点周围至少在 ±2 倍学习率与 +25% 批量的范围内是平的。
- **稳定性**。把学习率固定在最优值的若干倍、绕过衰减来复现大规模失稳：2 倍时 AdamW 基线每万步 4.3 次尖峰、两种 Muon 配置 0.2 次；4 倍时 AdamW 每万步 183 次尖峰、19,932 步里 213 次撞裁剪阈值（0.5），差异变成量级上的分离。单变量隔离 GatedNorm（固定 AdamW 与结构，3 倍学习率）：尖峰 32.0→3.2 每万步，阈值穿越 256→20。生产学习率下前 276B token 的三段对照：加 GR 降 0.026，整套 Flash-Next 配方再降 0.032，合计 0.058；GR 让每层残差最大激活一致下降，因此不需要 qk-clip 或 SwiGLU-clip 这类显式激活控制。

## 训练与评测数字

- 预训练基座对照（技术报告 Table 11，14 项）：Qwen3.8-Flash-Next-Base 全面压过 Qwen3.8-27B-Base；对 397B-A17B 的 Qwen3.7-Plus-Base 赢 8 项，输的 6 项最大差 2.6 分。抽样读数：MMLU 90.36（对手 90.43）、MMLU-Pro 73.23（70.90）、SuperGPQA 51.36（48.42）、BBH 90.87（89.41）、GPQA 51.42（51.52）、GSM8K 93.29（92.95）、MATH 72.78（74.38）、EvalPlus 78.76（78.06）、MultiPL-E 79.09（81.68）、SWEBench-Pretrain 50.99（49.24）、MGSM 89.33（85.42）、MMMLU 84.86（84.53）、INCLUDE 78.40（78.90）。成本口径：约三分之一激活参数、三分之一训练 token、约九分之一训练 FLOPs。
- 后训练件（模型卡自述，与 DeepSeek-V4-Flash-0731、Claude-Opus-4.6 (Max)、Qwen3.8-27B、Qwen3.7-Plus 并列对照）：DeepSWE 1.1 取 58.7（Qwen3.7-Plus 16.5）、SWE-bench Pro 62.5、SWE-bench Multilingual 81.0、CoWorkBench 73.9、JobBench 55.7、Toolathlon Verified 73.5、IFBench 81.3、GPQA Diamond 91.7、LiveCodeBench v6 91.9、HLE 35.9、Agents' Last Exam pass@1 24.3。多模态侧：AndroidWorld 84.5、OSWorld 2.0 二值 19.4/部分 52.3、Vision2Web 64.0、RecreationBench 49.9、ClawEval-MM pass@3 64.4、MathVision 无 CI 90.6、CharXiv (RQ) 无 CI 84.6、LVBench 76.6、RealWorldQA 88.5、ERQA 72.3。模型卡自报训练与推理成本相对 Qwen3.7-Plus 约降到九分之一。
- 口径提示：模型卡数字是自述，评测 harness 与温度写进脚注（temp=1.0、top_p=0.95、256K 窗口、Claude Code 与 mini-SWE-agent 两套 harness 取最高）；CoWorkBench、RecreationBench、NL2Repo-Bench、ClawEval-MM 是自建基准；技术报告的 14 项是 Base 档内部评估管线。

## 前提背景

这份资源立在四条线上，逐条回一手渠道的核对见增强信息页。自家线：Qwen3-Next 首次给出 Gated DeltaNet 加门控注意力的混合设计（官方博客，无 arXiv 论文），该设计此后贯穿 Qwen3.5、3.6、3.7、3.8 系列；本件是 Qwen4 架构的提前发布。对手线：稀疏注意力的 micro-block 打分沿 DeepSeek-V3.2 的 DSA（arXiv 2512.02556），残差加宽沿 Hyper-Connections（arXiv 2409.19606）、AltUp（arXiv 2301.13310）、mHC（arXiv 2512.24880）与 Kimi 的 Attention Residuals（arXiv 2603.15031），嵌入侧容量沿 Gemma 3n 与 RWKV-V8 DeepEmbed 一族的 offload 做法，以及 N-Grammer（arXiv 2207.06366）、L3、STEM（arXiv 2601.10639）、Scaling Embeddings Outperforms Scaling Experts（arXiv 2601.21204）。优化器线：Muon（Keller Jordan 2024 博客）与 Muon is Scalable for LLM Training（arXiv 2502.16982）、Polar Express 系数表（arXiv 2505.16932）、Essential AI 的预训练实测（arXiv 2505.02222）、分布式实现 Canzona（arXiv 2602.06079）。组内前作：门控注意力（arXiv 2505.06708）与注意力/残差流的 outlier 重标定（arXiv 2601.22966）由同一批作者先写过，GatedNorm 与 sigmoid 输出门这两件直接来自它们。

## 本体与去向

- 本体：`raw/2026-09/llm-architecture/github/qwen3.8-flash-next/`
- 本体件：`README.md`（仓库快照，commit 6988587）、`tech_report.pdf`（28 页，仓库内原件）、`tech_report_arxiv_2608.30320v1.pdf`（arXiv 同号件，28 页，字节与仓库版不同）、`qwen3.8-flash-next.extracted.md`（抽取正文）、`hf_model_card.md` 与 `hf_config.json`（权重仓库件）
- 图：`assets/` 下按原文编号存放。`qwen3.8-flash-next-fig1.png` 总体架构（三层 GDN 配一层 QSA，展开残差与 GR 读写、第 2 层 n-gram 嵌入、MTP 与预测头）；`fig2.png` GDN token mixer 内部结构；`fig3.png` QSA 总览（压缩索引器加稀疏核心注意力）；`fig4.png` 有无 QSA 的训练损失曲线；`fig5.png` QSA 在 RULER 上的架构消融（块大小、索引器头数）；`fig6.png` QSA 的 kernel 级延迟随上下文长度（prefill 与 decode）；`fig7.png` GR 增加的跨层路径矩阵；`fig8.png` 4T token 预算下的批量扫描；`fig9.png` 419B token 预算下的学习率扫描；`fig10.png` 压力测试下的训练损失；`fig11.png` 压力测试下的梯度范数与激活；`fig12.png` 单变量隔离 GatedNorm 的效果；`fig13.png` 生产学习率下前 276B token 的三段对照。`qwen3.8-flash-next-architecture.png` 是仓库 README 与模型卡共用的原始架构图（2885×2930）。
- 精读：[[qwen3.8-flash-next-reading|Qwen3.8-Flash-Next 精读]]
