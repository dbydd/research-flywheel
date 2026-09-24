---
title: "DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression 增强信息"
slug: deepseek-v41-flash-context
type: context
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2026-09/cs.CL/arXiv/deepseek-v41-flash/deepseek-v41-flash.extracted.md
  - raw/2026-09/cs.CL/arXiv/deepseek-v41-flash/deepseek-v41-flash.pdf
  - raw/2026-09/cs.CL/arXiv/deepseek-v41-flash/deepseek-v41-flash.html
resource: raw/2026-09/cs.CL/arXiv/deepseek-v41-flash
---

# DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression 增强信息

## 这份资源做了什么

这是一份模型技术报告，作者栏由 DeepSeek-AI 集体署名领衔，2026-09-17 提交到 arXiv 的 cs.CL（arXiv 2609.19969v1，首发日与 abs 页 `citation_date` 一致，`https://arxiv.org/abs/2609.19969`，访问日期 2026-09-22），正文 51 页，六节加两个附录，全文主线是把长上下文服务的 KV 缓存压下来。

- 模型规格：多模态 MoE，552B 骨干参数加 196B Engram 条件记忆参数，每 token 激活 8B（预填充）与 16B（解码），上下文支持到 100 万 token；语言骨干 40 层，分成 20 层 causal encoder 与 20 层 decoder，前两层走滑动窗口注意力，其余走 CSA2；hidden 5120，每层 1 个共享专家加 384 个路由专家，专家隐维 2304，每 token 激活 6 个专家，注意力顶 k 取 512（§2.1、§4.2.1，Table 1 架构行）。权重在 Hugging Face 公开，模型卡标 MIT 许可，48 个 fp8 safetensors 分片合计 510.3 GB（`https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash`，访问日期 2026-09-22）。
- KV 压缩的四件套：CED 让 decoder 的全局 KV 由 encoder 最后一层隐状态投影出来，预填充只跑前一半层数（§2.2，公式 (1)）；CSA2 把 main KV 与 indexer K 沿层复用，并允许层复用 Top-K 索引，Full、Reindex、Reuse 三种模式静态分配（§2.3.1，Figure 4），decoder 第一个 Full 层建候选池供后续层在池内重打分（§2.3.2，Figure 5）；主 KV 缓存改 FP4，取 OCP MXFP4 的 E2M1 配每 16 通道一个 E4M3 缩放，省掉二级全局缩放（§2.4.4）；部署侧用 SWA Bounded Replay 只重放最近一个窗口的 token 近似重建 SWA 状态，SWA KV 不再进持久缓存（§3.2.2）。
- 落点数字：全局 KV 缓存（常驻 HBM）压到每 token 890 字节，约为 DeepSeek-V4-Flash 的四分之一；持久 KV 缓存（驻 SSD 或主机内存）压到约八分之一；上下文从 4K 扩到 1M，单 token 解码 FLOPs 只涨约四分之一；Reuse Mode 层预填充与解码分别只需 15 与 11 个 kernel（§1、§3.2，Figure 1(b)、Figure 2）。
- 三个架构组件各有独立前作，这一版做了改造：Single-Pass mHC 把输入混合系数移位一个 block，配合 Mega-mHC 单 kernel 融合把激活内存流量减半（§2.4.1）；Engram 196B 参数均分两个模块放在第 1、14 层，N-gram 阶取 {2,3,4}，8 个哈希头，每阶嵌入维 2048，每头约 1600 万条表项，嵌入表与投影走 FP8，去掉短因果卷积（§2.4.2）；DSpark 用 3 层草稿器、128 token 的滑窗、一次前向并行出 5 个草稿位，置信头估计接受率，调度器按引擎吞吐曲线选验证长度，放在预训练之后的独立阶段训练（§2.4.3）。嵌入表、词表与预测头用 Sinkhorn 均衡的动量更新替代 Adam（§2.5，Algorithm 1）。
- 预训练与后训练：45T token 多模态语料，文本与多模态 token 比 7:1；从零以 64K 序列长度训稀疏注意力，34T token 处扩到 1M；batch 固定 100.6M token，学习率 2.6e-4 余弦衰减到 2.6e-5（§4.1、§4.2.2）。视觉侧先训 DeepSeek-ViT（约 47B 图文对做对比学习，再接 4B MoE 语言模型做 236B token 的自回归微调），再做语言模型预训练（§2.1.1、§4.2.2）。后训练明说没有算法新意，SFT 加 RL 加 on-policy distillation 三步照旧，全部变化落在数据合成与环境构造管线（§5.1）；沙箱平台 DSec 撑到百万级并发实例（§5.1.3）；推理力度做成一个标量，公开 API 分 max、high、low 三档，对应 100、75、50，2026 年 9 月上线（§5.1.4，Table 2）。
- 评估三位：Base 档与 DeepSeek-V4-Pro-Base 比，用三分之一总参数与四分之一激活参数，在保留评估集上取得 5%–10% 提升，Figure 6 的 BPB 全部最低（§4.3.2，Table 1、Figure 6）；后训练档 Terminal-Bench 2.1 取 90.6、DeepSWE v1.1 取 74.2、CyberGym 取 88.1、Codeforces 评级 3471、MathArena Apex 取 65.6、GPQA Diamond 取 90.9、HLE 取 36.8（纯文本子集 39.1）（Table 3）；scaffold 稳健性上，六个家族八个配置里 Terminal-Bench v2.1 最高是 DeepSeek Harness (Minimal) 的 90.6，DeepSWE v1.1 最高是 mini-SWE 的 74.2（§5.3.4，Table 4）。
- 自报局限：CSA2 的稀疏选择错误与 SWA Bounded Replay 的近似状态重建在未测边界上可能掉能力，压力测试方向列为长上下文稀疏检索与缓存恢复边界（§6）。

![[raw/2026-09/cs.CL/arXiv/deepseek-v41-flash/assets/deepseek-v41-flash-fig1b.png]]

原文 Figure 1(b)：历代 DeepSeek 模型的每 token 全局 KV 缓存字节数——DeepSeek-V1（2023.11）389,120、DeepSeek-V3.2（2025.12）48,068、DeepSeek-V4-Flash（2026.04）3,514、DeepSeek-V4.1-Flash（2026.09）890。

![[raw/2026-09/cs.CL/arXiv/deepseek-v41-flash/assets/deepseek-v41-flash-fig3.png]]

原文 Figure 3：总体架构。左为 causal encoder（20 层），右为 decoder（20 层），CED 箭头表示 decoder 的全局 KV 来自 encoder 末层隐状态，Hierarchical Sparse Indexer 把第一个 Full 层的选择送进 Candidate Pool。

## 立在什么基础上

四组基座，按与本文的距离排。

**一、自家的模型线**。本文把 DeepSeek-V4（arXiv 2606.19348，2026-04-26 首发，cs.CL，319 项作者）当作直接基线，KV 压缩的目标、SWA 加全局注意力的骨架、mHC 与 Engram 与 DSpark 的原始形态都来自这一篇（§1、§2.3、§5.2.4）。更早的自家工作在正文里被逐个点名：DeepSeek-V2（arXiv 2405.04434，2024-05-07）贡献 MLA，把 KV 的 entry 维压成一个小潜变量（§2.3）；DeepSeekMoE（arXiv 2401.06066，2024-01-11，17 位作者）贡献细粒度路由专家与共享专家，本文的每层 1 共享加 384 路由的配置沿用这条线（§2.1）；同一篇里的 DeepSeek-V3（arXiv 2412.19437，2024-12-27）被拿来对照 MTP 模块的做法，本文把 MTP 换成 DSpark 并改到预训练之后单独训练（§2.4.3）；DeepSeek-V3.2（arXiv 2512.02556，2025-12-02）与 V4 一起构成 §1 开篇所述的稀疏注意力前期进展；无辅助损失负载均衡（arXiv 2408.15664，2024-08-28）被扩成按模态分开维护校正偏置的版本（§2.1、§2.1.1）。

**二、沿层维度复用的并行工作**。这是本文架构创新的直接对手与垫脚石，§2.3 一段把四条线并列举出：YOCO（arXiv 2405.05254，2024-05-08，Microsoft Research 与清华大学）让上半的网络直接共享下半网络产出的 KV，CED 明确说受它启发（§2.2）；Brandon 等人的跨层注意力 KV 缩减（NeurIPS 37，2024）给出「部分层复用其它层缓存」这一维度的通用依据；IndexCache（arXiv 2603.12201，2026-03-12，Z.ai 与清华大学）复用 Top-K 索引来砍索引器计算；YOIO（arXiv 2606.06467，2026-06-04，Microsoft Research 与清华大学）把稀疏路由算一次共享给所有层；HySparse（arXiv 2602.03560，2026-02-03，小米 LLM-Core）让稀疏层复用全注意力层的 KV。本文对这批工作的定位写在 §2.3：索引复用单独做省不下主 KV 存储，全局路由共享限制性能，混合设计仍留全注意力层，于是 CSA2 把主 KV、索引器 K、Top-K 索引三样一起沿层复用。解码器的候选池思路则接到 HiSA（arXiv 2603.28458，2026-03-30，北京大学与小红书）的分层索引上（§2.3.2）。SWA 有效感受野远小于理论窗口这个观察引自 PowerAttention（arXiv 2503.03588，2025-03-05，复旦大学 Knowledge Works 实验室与香港大学）（§2.2）。entry 维的两条手段之一是 GQA（arXiv 2305.13245，2023-05-22，Google Research）（§2.3）。

**三、组内三篇组件论文**，这一版把它们各自改造后收进模型：mHC 多流残差（arXiv 2512.24880，arXiv 记录首发 2025-12-31，20 位作者，DeepSeek-AI）升级成 Single-Pass mHC；Engram 条件记忆（arXiv 2601.07372，2026-01-12，北京大学与 DeepSeek-AI）去掉短因果卷积、嵌入更新改走 Sinkhorn 均衡；DSpark 投机解码（arXiv 2607.05147，2026-07-06，北京大学与 DeepSeek-AI，cs.AI）整体收编为解码加速件。全文的引用落点集中在这三篇（§1、§2.1、§2.4.1、§2.4.2、§2.4.3）。

**四、训练配方、量化与工程栈**。优化器沿 DeepSeek-V4 的配置改：Muon（Keller Jordan 2024-12-08 博客与 KellerJordan/Muon 仓库）用于线性变换权重，AdamW（ICLR 2019）用于归一化层与非矩阵参数，Nesterov 动量与解耦权重衰减照旧，Query 与 Key 改成分头 Muon（§2.5、§4.2.2）；Sinkhorn 均衡的更新方式引 SinkGD（NeurIPS 38，2025），并自陈与 Adafactor（PMLR 80，2018）、Adam-mini（ICLR 2025）、Why Transformers Need Adam（NeurIPS 37，2024）等一批轴结构优化器同源（§2.5）。量化三源：QAT（CVPR 2018）用于索引器 query 与 key 的 FP4 训练，OCP MXFP4（arXiv 2310.10537）用于格式选择，NVFP4（NVIDIA 技术博客 2025-06-24）提供 E2M1 配每 16 通道一个 E4M3 缩放的取法（§2.4.4）。视觉件建在 ViT（ICLR 2021）上，配 RMSNorm（NeurIPS 32，2019）与 SwiGLU（arXiv 2002.05202），对比学习用 SigLIP 的 sigmoid 损失（ICCV 2023），数据处理用 SmolVLM（arXiv 2504.05299）做质量打分（§2.1.1、§4.1、§4.2.1、§4.2.2）。训练系统沿用分布式多模态训练的分离式编码器设计（DistTrain，SIGCOMM 2025），并点名同代系统（LongCat-Flash-Omni、Kimi-K2.5）（§3.1.1）。推理栈是把自家仓库拼起来：FlashMLA 的融合 RoPE 注意力 kernel、DeepGEMM 的 Mega-Gate 与 Mega-mHC 与 Mega-MoE kernel、TileKernels 的 kernel、DeepSelect 的 TopK kernel（§3.2）。后训练配方引 MiniLLM（ICLR 2024）与 Thinking Machines 的 on-policy distillation 一文（§5.1）。

**五条待考的联系（猜想）**。以下几处没有原文直接支撑，属我读出的可能关系，标注为猜想：其一，CSA2 的层排布把压缩比 2 的编码器层配成一个 Full 层加五个 Reuse 层、压缩比 1 的解码器层配成 Full 与 Reindex 与 Reuse 混排，这套配比与 YOCO 的「下半编码、上半复用」在动机上同向，两篇对复用粒度的取舍需要各自消融才谈得清（猜想）；其二，候选池尺寸取块级最大分再合并（2048 块乘 8 位置等于 16384 个候选位）这一设定，可能调自长上下文检索的召回与算力折中，原文给了机制说明与「固定池大小则每查询成本与上下文无关」的界，池大小的来源依据未见（猜想）；其三，Engram 减掉短因果卷积的取舍理由写作「收益配不上推理栈复杂度」，与前作里该卷积承担的角色对比起来，属工程口径判断（猜想）；其四，Base 档评估全部在内部框架、对手全是自家前代，与后训练档齐上闭源模型的两套口径拉开的差距，读表时的比较基准不同（猜想）；其五，45T token 里文本与多模态 7:1 的配比、以及 34T token 处才扩到 1M 序列的时机，可能对应长上下文能力与语言能力的权衡，原文只给数字（猜想）。

## 引用落在哪

正文带括号的引用共 68 组，另有若干只出现在表格表头、参考文献里无条目的对照模型。下列四张表收录承担论证的条目，逐条回了一手渠道，访问日期均为 2026-09-22。

**一、自家模型线与架构复用来源**

| 本篇指称 | 一手出处 | 篇内落点 |
|---|---|---|
| DeepSeek-V2 | arXiv 2405.04434，2024-05-07，DeepSeek-AI 集体署名（157 项作者） | §2.3（MLA 压 entry 维） |
| DeepSeekMoE | arXiv 2401.06066，2024-01-11，Damai Dai、Chengqi Deng 等 17 位（DeepSeek-AI 与北京大学） | §2.1（共享与细粒度路由专家） |
| 无辅助损失负载均衡 | arXiv 2408.15664，2024-08-28，Lean Wang、Huazuo Gao 等（DeepSeek-AI 与北京大学） | §2.1、§2.1.1（扩成模态分离的校正偏置） |
| DeepSeek-V3 | arXiv 2412.19437，2024-12-27，DeepSeek-AI 集体署名（200 项作者） | §2.4.3（MTP 做对照） |
| DeepSeek-V3.2 | arXiv 2512.02556，2025-12-02，DeepSeek-AI 集体署名（264 项作者） | §1（稀疏注意力前期进展） |
| DeepSeek-V4 | arXiv 2606.19348，题录首发 2026-04-26，DeepSeek-AI 集体署名（319 项作者） | §1、§2.3、§5.2.4（直接基线） |
| GQA | arXiv 2305.13245，2023-05-22，Joshua Ainslie 等（Google Research） | §2.3 |
| YOCO | arXiv 2405.05254，2024-05-08，Yutao Sun、Li Dong 等（Microsoft Research 与清华大学） | §2.2（CED 的启发源） |
| Brandon 等跨层注意力 KV 缩减 | NeurIPS 37（2024），W. Brandon 等，`https://proceedings.neurips.cc/paper_files/paper/2024/file/9e23d020c18e4c40d81c6a0fc7a46f68-Paper-Conference.pdf` | §2.3 |
| IndexCache | arXiv 2603.12201，2026-03-12，Yushi Bai、Qian Dong 等（Z.ai 与清华大学） | §2.3 |
| YOIO | arXiv 2606.06467，2026-06-04，Yutao Sun、Yanqi Zhang 等（Microsoft Research 与清华大学） | §2.3 |
| HySparse | arXiv 2602.03560，2026-02-03，Yizhao Gao、Jianyu Wei 等（小米 LLM-Core） | §2.3 |
| HiSA | arXiv 2603.28458，2026-03-30，Yufei Xu、Fanxu Meng 等（北京大学与小红书） | §2.3.2（分层索引的前作） |
| PowerAttention | arXiv 2503.03588，2025-03-05，Lida Chen、Dong Xu 等（复旦大学 Knowledge Works 实验室与香港大学） | §2.2（SWA 有效感受野的观察） |
| mHC | arXiv 2512.24880，题录首发 2025-12-31，Zhenda Xie、Yixuan Wei 等 20 位（DeepSeek-AI） | §1、§2.1、§2.4.1 |
| Engram 条件记忆 | arXiv 2601.07372，2026-01-12，Xin Cheng、Rui Tian 等 21 位（北京大学与 DeepSeek-AI）；参考文献另列同题 ACL 2026 正式版 | §2.1、§2.4.2、§4.2.2 |
| DSpark | arXiv 2607.05147，2026-07-06，Xin Cheng、Xingkai Yu 等 33 位（北京大学与 DeepSeek-AI），cs.AI | §1、§2.1、§2.4.3 |

**二、训练配方、优化器与量化**

| 本篇指称 | 一手出处 | 篇内落点 |
|---|---|---|
| Muon 原始出处 | Keller Jordan，2024-12-08，`https://kellerjordan.github.io/posts/muon/`；代码仓 `https://github.com/KellerJordan/Muon`（建仓 2024-11-09） | §2.5、§4.2.2 |
| Muon is Scalable for LLM Training | arXiv 2502.16982，2025-02-24，Jingyuan Liu、Jianlin Su 等 28 位（以 Moonshot AI 为主） | §2.5、§4.2.2（学习率换算的口径） |
| AdamW | ICLR 2019，Loshchilov 与 Hutter，`https://iclr.cc/virtual/2019/poster/935`（arXiv 1711.05101） | §2.5、§4.2.2 |
| Adafactor | ICML 2018，PMLR 80:4596–4604，Shazeer 与 Stern，`https://proceedings.mlr.press/v80/shazeer18a.html` | §2.5（轴结构优化器一族） |
| SinkGD 的梯度多归一化 | NeurIPS 38（2025），Scetbon、Ma、Gong、Meeds，`https://proceedings.neurips.cc/paper_files/paper/2025/hash/3d6235707dbc91acda049a0ccd641a7e-Abstract-Conference.html` | §2.5（Sinkhorn 均衡的来处） |
| Adam-mini | ICLR 2025，Yushun Zhang 等，`https://proceedings.iclr.cc/paper_files/paper/2025/hash/45ae878717399e6f62d57c65f052cd46-Abstract-Conference.html` | §2.5 |
| Why Transformers Need Adam | NeurIPS 37（2024），Yushun Zhang 等，`https://proceedings.neurips.cc/paper_files/paper/2024/hash/ee0e45ff4de76cbfdf07015a7839f339-Abstract-Conference.html` | §2.5 |
| 神经网络优化器原理 | arXiv 2608.16760，2026-08-17，Yushun Zhang | §2.5（分头 Muon 的动机依据） |
| Nesterov 动量 | Nesterov，1983，Soviet Mathematics Doklady 27:372–376 | §2.5 |
| 矩阵轴结构优化器一族 | RMNP arXiv 2603.20527（2026-03-20）；Nora arXiv 2605.03769（2026-05-05）；宽度标度与行列表归一 arXiv 2603.09952（2026-03-10） | §2.5 |
| 行级梯度归一的无状态训练 | Wen 等，2025，题录未寻得（线索 `https://openreview.net/forum?id=BtQLBWr6zI`） | §2.5 |
| QAT | CVPR 2018，Jacob 等，`https://openaccess.thecvf.com/content_cvpr_2018/html/Jacob_Quantization_and_Training_CVPR_2018_paper.html` | §2.4.4 |
| OCP MXFP4 | arXiv 2310.10537，2023-10-16，Bita Darvish Rouhani 等 | §2.4.4 |
| NVFP4 | NVIDIA 技术博客，2025-06-24，`https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/` | §2.4.4 |
| DistTrain | ACM SIGCOMM 2025，Z. Zhang 等 | §3.1.1（分离式编码器设计） |

**三、视觉、数据与后训练配方**

| 本篇指称 | 一手出处 | 篇内落点 |
|---|---|---|
| ViT | ICLR 2021，Dosovitskiy 等，`https://iclr.cc/virtual/2021/poster/3013`（arXiv 2010.11929） | §2.1.1（DeepSeek-ViT 的骨架） |
| RMSNorm | NeurIPS 32（2019），Biao Zhang 与 Rico Sennrich | §2.1.1、§4.2.1 |
| SwiGLU | arXiv 2002.05202，2020-02-12，Noam Shazeer | §2.1.1、§4.2.1 |
| SigLIP 的 sigmoid 对比损失 | ICCV 2023，Zhai 等 | §4.2.2（视觉编码器对比预训练） |
| SwiGLU 截断阈值 | gpt-oss 模型卡，arXiv 2508.10925，2025-08-08 | §4.2.1 |
| SmolVLM | arXiv 2504.05299，2025-04-07，Andrés Marafioti 等 | §4.1（多模态数据质量打分） |
| Cambrian-1 | arXiv 2406.16860，2024-06-28，Shengbang Tong 等 | §4.3.1（多模态评估口径） |
| 同代训练系统 | LongCat-Flash-Omni arXiv 2511.00279；Kimi-K2.5 arXiv 2602.02276，2026-02-02，Moonshot AI | §3.1.1 |
| 后训练配方 | MiniLLM，ICLR 2024，Gu 等；On-Policy Distillation，Thinking Machines Lab，2025 | §5.1 |

**四、自家工程栈与评测夹具**

| 本篇指称 | 一手出处 | 篇内落点 |
|---|---|---|
| FlashMLA | `https://github.com/deepseek-ai/FlashMLA`（建仓 2025-02-21，末次推送 2026-09-15） | §3.2（融合 RoPE 注意力 kernel） |
| DeepGEMM | `https://github.com/deepseek-ai/DeepGEMM`（建仓 2025-02-13，末次推送 2026-09-14） | §3.2（Mega-Gate、Mega-mHC、Mega-MoE kernel） |
| TileKernels | `https://github.com/deepseek-ai/TileKernels`（建仓 2026-04-22） | §3.2（tilelang 写的 kernel 库） |
| DeepSelect | `https://github.com/deepseek-ai/DeepSelect`（建仓 2026-09-09） | §3.2（TopK kernel） |
| deepseek-harness | `https://github.com/deepseek-ai/deepseek-harness`（建仓 2026-08-13，末次推送 2026-09-17） | §5.3.4（评测 scaffold 与 Agent Team 模式） |
| agent 基准 | Terminal-Bench（arXiv 2601.11868）、Terminal-Bench 3.0（`https://www.tbench.ai/news/terminal-bench-3-0`）、Terminal-Bench 4.0（`https://www.tbench.ai/`）、DeepSWE v1.1（`https://deepswe.datacurve.ai/`）、AutomationBench（arXiv 2604.18934）、NL2Repo-Bench（arXiv 2512.12730）、ProgramBench（arXiv 2605.03546）、CyberGym（arXiv 2506.02548，ICLR 2026）、SEC-Bench Pro（arXiv 2605.26548）、Agents' Last Exam（arXiv 2606.05405） | §1、§5.3.1、Table 3、Table 4 |
| 推理与知识基准 | MathArena Apex（`https://matharena.ai/apex/`，2025-08-18）、GPQA（arXiv 2311.12022）、Humanity's Last Exam（arXiv 2501.14249）、MMLU-Pro（arXiv 2406.01574）、SuperGPQA（arXiv 2502.14739）、SimpleQA Verified（arXiv 2509.07968）、MATH（arXiv 2103.03874）、GSM8K（arXiv 2110.14168）、BigCodeBench（arXiv 2406.15877）、BBH（arXiv 2210.09261）与 BBEH（arXiv 2502.19187）、LongBench v2（arXiv 2412.15204） | §4.3.1、§5.3.1、Table 1、Table 3 |
| 多模态基准 | MMMU-Pro（arXiv 2409.02813，ACL 2025）、ZeroBench（arXiv 2502.09696）、Chartography（arXiv 2608.10677）、BabyVision（arXiv 2601.06521）、DocVQA（arXiv 2007.00398）、RefCOCO 系四篇（Kazemzadeh 2014、Mao 2015、Nagaraja 2016、Yu 2016） | §4.3.1、§5.3.1 |
| 评测 scaffold | Claude Code（`https://code.claude.com/docs/en/overview`）、Codex（`https://github.com/openai/codex`）、OpenCode（`https://github.com/anomalyco/opencode`）、Pi（`https://github.com/earendil-works/pi`，论文记作者 M. Zechner）、mini-SWE（SWE-agent，arXiv 2405.15793；实现仓 `https://github.com/SWE-agent/mini-swe-agent`） | §5.3.4、Table 4、附录 B.1 Scaffold Configurations |
| 表头出现的对照模型 | Kimi-K3（arXiv 2607.24653，2026-07-27，Moonshot AI，另有正文引用）；Opus-5（Anthropic，2026-07-24，`https://www.anthropic.com/news/claude-opus-5`）、GPT-5.6 Sol（OpenAI，预览 2026-06-26、开放 2026-07-09，`https://openai.com/index/gpt-5-6/`）、GLM-5.3（`https://z.ai/blog/glm-5.3`，发布 2026-08-14；权重仓 `https://huggingface.co/zai-org/GLM-5.3` 建于 2026-08-25）三者在参考文献里无条目 | Table 3、§6 |

## 谁做的

组织面：DeepSeek-AI（联系邮箱 `research@deepseek.com`），Hugging Face 组织页标为 verified 的公司账号，名下 105 个模型、30 篇论文、2 个数据集、6 个 Space、147,046 位关注者（`https://huggingface.co/api/organizations/deepseek-ai/overview`，访问日期 2026-09-22）。官网自述为「专注于研究世界领先的通用人工智能底层模型与技术」，页脚署「杭州深度求索人工智能基础技术研究有限公司」（`https://www.deepseek.com/`，访问日期 2026-09-22）。

作者面：arXiv 题录的作者栏第一项是组织名 `DeepSeek-AI`，第二项是一个字面的冒号，其后 591 个个人名按名首字母排序（共 593 项，arXiv API 与 abs 页 `citation_author` 一致）。本文附录 A 把作者分成两块：Research & Engineering 465 人，Business & Compliance 126 人，合计 591 人，开篇写明「Authors are listed alphabetically by their first name. Names marked with * denote individuals who have departed from our team.」，带星号的 9 人是 Chengda Lu、Guanting Chen、Haotian Xu、Minghua Zhang、Shiqiang Hu、Tianran Ji、Wenjing Yao、Y.T. Wu、Ying Zhou，全部落在 Research & Engineering 块内。arXiv 提交记录的联系人是 Wenfeng Liang。

本体与去向：模型卡建于 2026-09-10，报告 2026-09-17 上线，权重先于报告公开；许可为 MIT，仓库含 48 个 fp8 分片与一份技术报告 PDF（`https://huggingface.co/api/models/deepseek-ai/DeepSeek-V4.1-Flash`，访问日期 2026-09-22）。同代另有 DeepSeek-V4-Pro、DeepSeek-V4-Flash、DeepSeek-V4-Flash-0731、DeepSeek-V4-Pro-Base 等公开权重；DeepSeek-V4.1-Pro 这个名字下的模型卡在当前渠道不存在。

## 这个组与作者的特点

- **集体署名加字母序，离职留痕**。DeepSeek-V2 起作者栏以 DeepSeek-AI 集体名领衔，个人名按名首字母排列，本篇把这套写法完整摊开：两块职能、591 人、9 处星号标注离职（附录 A）。作者栏规模逐代上升：DeepSeekMoE 17 位个人作者、V2 157 项、V3 200 项、V3.2 264 项、V4 319 项、本篇 593 项（arXiv API，访问日期 2026-09-22）。
- **组件先行、模型后收的节奏**。mHC、Engram、DSpark 各自先成一篇论文，再被下一代模型改造收编；DeepSeekMoE 与无辅助损失负载均衡同理。本篇 §2.4 三节就是三次收编的账：mHC 变 Single-Pass、Engram 去掉短因果卷积、DSpark 换成独立训练阶段。
- **人员连续**。DeepSeekMoE 的 17 位个人作者里有 11 位出现在本篇；六篇模型报告全部在列的 10 人是 Deli Chen、Wangding Zeng、Jiashi Li、Zhenda Xie、Wenfeng Liang、Huazuo Gao、Chenggang Zhao、Panpan Huang、Xingkai Yu、Damai Dai。
- **效率一条主线**。从 V2 的 MLA 到 V3.2 的稀疏注意力到 V4 与 V4.1 的 KV 压缩，每代的压缩成果都落在同一张图里（Figure 1(b)：389,120 字节逐年降到 890 字节），本篇把这条线写进摘要与结论两处。训练与推理的两端同时收窄：预填充激活 8B、解码激活 16B、Reuse Mode 层 15 与 11 个 kernel。
- **工程件与权重同步放出来**。训练侧与推理侧的自研栈都在 GitHub 开源（FlashMLA、DeepGEMM、TileKernels、DeepSelect、deepseek-harness），模型卡点名了额外的 deepseek-recipe Rust 库；TileKernels、DeepSelect 与 deepseek-harness 三个仓库的建仓时间落在 2026-04 到 2026-09，与本代模型的发布节奏咬合。
- **评测口径分层**。Base 档全部在内部框架评估，对手是自家前代（Table 1、Figure 6）；后训练档对齐闭源与开源外部模型（Table 3 的 Opus-5、GPT-5.6 Sol、Kimi-K3、GLM-5.3），并以自家 harness 与外部 scaffold 混搭做稳健性检验（Table 4、Table 5）。跨组引用上也开放：架构借 Microsoft Research、清华大学、Z.ai、小米、北京大学、复旦大学的公开工作，工程上点名同代的 LongCat-Flash-Omni 与 Kimi-K2.5，并把分头 Muon 的实证对照拉到 GLM-5 与 Kimi-K3 两篇报告上。
- **数据管线是后训练的重心**。§5.1 把「没有算法新意」写进正文，把全部变化落在任务合成（problem、environment、verification system 三元组）、环境构造与质检管线上；DSec 沙箱与异步训练基础设施各占一节，多智能体协作只给初步实验（§5.3.5）。

## 核验备注

- 任务书点名的 Llama、GLM-5.2、MiniMax M2.2、Seed-2.1-Pro、Qwen3.6-Max 在本篇正文与参考文献里都未出现。本篇的外部对照模型是 Opus-5、GPT-5.6 Sol、Kimi-K3、GLM-5.3，其中前两者与 GLM-5.3 在参考文献里没有条目（GLM 的条目指向 GLM-5，arXiv 2602.15763）。
- Engram 在参考文献里占两条同题条目：CoRR 预印本（arXiv 2601.07372，标 2026b）与 ACL 2026 正式版（标 2026c）。正文 §2.1 与 §4.2.2 用 2026b，§2.4.2 用 2026c，同一对象两个键。
- mHC 一条本篇记年 2026，arXiv 记录的首次提交日是 2025-12-31，编号月为 2512。DeepSeek-V4 一条的编号月为 2606，题录首次提交日是 2026-04-26。
- Terminal-Bench 一条本篇引作 2.1（`https://arxiv.org/abs/2601.11868`），该条题录与摘要自述为 Terminal-Bench 2.0、89 题；Terminal-Bench 3.0 与 4.0 分列两条，指向 `tbench.ai` 的官方页与榜。
- SRON（Wen 等，2025，行级梯度归一的无状态训练）在一手渠道未寻得题录，只留 OpenReview forum 号 BtQLBWr6zI 一条线索；其余优化器条目都核到。
- 题名差异两处：Scetbon 一文的 arXiv 题名带「Stateless and Scalable」字样，与 NeurIPS 卷上的题名不同；宽度标度一篇的官方题名比本篇引法长。
- 数字口径：Table 1 记 V4-Pro-Base 激活 49B、本篇两档激活 8B（预填充）与 16B（解码），对 49B 分别约为六分之一与三分之一；§1 的说法是总参数三分之一、激活参数四分之一。
- 机构级指标这一跳未取到：OpenAlex 无 key 的共享额度当日用尽（429，`retryAfter` 约 25700 秒），DeepSeek-AI 的机构记录、被引与高产作者前十均未读到。组织面的事实改由 arXiv 题录、Hugging Face API 与官网核对。
- GLM-5.3 的权重公开时间有两说：官方口径 2026-08-28，Hugging Face 仓库创建日 2026-08-25。

## 关联

- [[deepseek-v41-flash-abstract|DeepSeek-V4.1-Flash 摘要]]
- [[deepseek-v41-flash-reading|DeepSeek-V4.1-Flash 精读]]：下游精读报告，与本篇同资源
