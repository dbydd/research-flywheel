---
title: "Kimi K3: Open Frontier Intelligence 增强信息"
slug: kimi-k3-context
type: context
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2026-07/cs.CL/arXiv/kimi-k3/kimi-k3.extracted.md
  - raw/2026-07/cs.CL/arXiv/kimi-k3/kimi-k3.pdf
  - raw/2026-07/cs.CL/arXiv/kimi-k3/kimi-k3.html
resource: raw/2026-07/cs.CL/arXiv/kimi-k3
---

# Kimi K3: Open Frontier Intelligence 增强信息

## 这份资源做了什么

这是一份模型技术报告，作者栏以 Kimi Team 集体署名领衔，arXiv 2607.24653v2，首发 2026-07-27，v2 于 2026-08-07 上线，主分类 cs.CL（`https://arxiv.org/abs/2607.24653`，访问日期 2026-09-22），正文八节加六个附录，全文主线是把一个 3T 级开源 MoE 同时沿序列、深度、宽度三条轴扩到前沿。下文落点用该报告自己的节号与图表号。

- 模型规格：2.78T 总参数、104.2B 激活参数、896 个路由专家每 token 激活 16 个（稀疏度 56）、2 个共享专家、hidden 7168、93 层、96 个注意力头、词表 160K、上下文 1,048,576 token、原生视觉（MoonViT-V2，401M 参数、27 层、patch 14、12 个注意力头）；训练上下文从上一代 128K 扩到 1M（§2、§2.4、Table 1）。权重在 Hugging Face 以 Kimi K3 License 开放，模型卡最后改动 2026-09-02，标 MXFP4 权重与 MXFP8 激活（`https://huggingface.co/moonshotai/Kimi-K3`，访问日期 2026-09-22）。
- 三条扩展轴。序列方向每块排 3 层 KDA（Kimi Delta Attention）加 1 层 Gated MLA，93 层拆成 69 层 KDA 与 24 层 MLA（§2.1，模型卡 `config.json` 的 `linear_attn_config.full_attn_layers` 列了 24 个层号，与 Table 1 的「69 KDA + 24 MLA」对上）；深度方向用 Attention Residuals 让每层对嵌入与前序块输出做选择性读取，按 8 块、每块 12 层划分（§2.2，`attn_res_block_size = 12`）；宽度方向每个注意力层后接 Stable LatentMoE，先把表示降到 3584 维潜空间（0.5 倍 hidden），再做 896 选 16 的稀疏混合，最后升维回 7168（§2.3）。
- KDA 这一版的改动集中在跨块数值范围：把衰减对数改成有下界的缩放 sigmoid（`g_min = -5`），每个保留因子大于 `e^-5`，跨 16 token 的累计对衰减落在 `(-80, 0)`，于是对角块与对角外块都能走稠密 Tensor Core 矩阵乘，省掉逐位置对计算（§2.1.1，公式 (5)，Figure 3）。输出门从低秩参数化换成输入相关的满秩投影（公式 (6)）。
- SiTU-GLU：门控分支用带 softcap 的 SiTU（β₁ = 4），up 分支再加一层 softcap（β₂ = 25），输出上界 `β₁β₂ = 100`（§2.3.2，公式 (12)，Figure 4；附录 B 给局部展开 `z + O(z³/β²)`、极限情形与输出界）。Stable LatentMoE 另在升维入口放一个 RMSNorm（§2.3.1）。
- 负载均衡：分位数均衡（Quantile Balancing，QB）用 Top-(k+1) 路由取到当前 cutoff，再把每个专家的偏置钉到 `1 - k/n` 分位数上，无需学习率式超参；落地走分 bin 直方图，`B = 1000` 时估计误差上界为 bin 宽（量级 1e-3），通信是一次 `nB` 计数的 all-reduce，与 token 数无关（§2.3.3，公式 (14)，Figure 5；附录 C 给最优分配的对偶推导，并把 SignSGD 式偏置更新读成同一对偶目标上的符号梯度一步；附录 D 给直方图估计的准确、便宜、口径正确三条性质）。
- 预训练与长上下文：文本四域（Web Text、Code、Mathematics、Knowledge）加视觉语料，视觉语料按 K2.5 的分类扩到程序化多模态数据（SVG、3D 资产、网页、游戏、CAD）（§3.1）；scaling law 与 Kimi K2 对照给出约 2.5 倍整体 scaling 效率（§3.2，Figure 7、Table 1）；学习率用余弦衰减（§3.2）；四阶段课程把窗口从 8K 推到 64K，再在冷却阶段从 256K 推到 1M（§3.4）。
- 后训练：SFT 冷启，RL 在三个域（通用任务、通用智能体、编码智能体）乘三档推理力度（low、high、max）训出九个专家模型，再用多教师在线策略蒸馏（MOPD）合成一个模型（§4.1，公式 (15)）；MoE 专家权重从 SFT 起走 MXFP4 量化感知训练，激活走 MXFP8（§4.1.4）；预训练的 MTP 层被微调成 EAGLE-3 式草稿模型，草稿训练时展开七步，输入融合第 1、第 4 与最后一个 AttnRes 块的输出（§4.1.4，公式 (16)）；对话模板换成 XTML，用 `[open]`、`[sep]`、`[close]`、`[end_of_msg]` 四个特殊 token 代替尖括号，助手消息分 think、response、tools 三条通道（§4.1.1、附录 F，Figure 16）。
- 基础设施：KDA 侧是 FlashKDA 融合内核加 KDA 上下文并行；三万亿级预训练侧是 MoonEP 全均衡专家并行（每 rank 至多 `E/R` 个冗余专家，附录 E 证明该上界基本紧）、流水线 ZeRO-2 梯度分片与 CPU 卸载、P2P 式 Muon 正交化；百万 token 智能体 RL 侧是外置 KV 缓存池、自动节流调度器与可恢复 microVM 沙箱 AgentENV（检查点 133 ms、恢复 49 ms，等待模型推理占沙箱生命周期的 98%，内存超分至 6.5 倍，全程创建 51,219,741 个沙箱、1,505,678 个镜像）；服务侧是 KDA 感知前缀缓存（6144 token 的物理块内含 512 token 的哈希块，命中边界不要求对齐物理块）、WarpDecode 式解码内核、缓存亲和调度与预算准入（§5.1 至 §5.4，Figure 11、Figure 12）。
- 评测与成本：GPQA Diamond 93.5%、HLE-Full 带工具 56.0% 与不带工具 43.5%、CritPt 23.4%、ProgramBench 77.8%、SWE-Marathon 42.0%、Terminal-Bench 2.1 88.3%、FrontierSWE 81.2%（2026-07-16 口径）、DeepSWE 67.3（mini-SWE-agent 夹具）、BrowseComp 91.2%（关掉上下文压缩后 90.4%）、DeepSearchQA 95.0% F1、MCPMark-Verified 94.5%、Math-Vision 94.3%（配 Python 工具 97.8%）、ZeroBench-main 23.0%（配工具 41.0%）、OmniDocBench 91.1%、WorldVQA 51.0%；整体位置在 Claude Fable 5 与 GPT-5.6 Sol 之后，领先同一套件内的其余开源与闭源模型（§6.1，Table 2）。成本侧 BrowseComp 每任务 2.03 美元，GDPval-AA v2 与 GPT-5.6 Sol 的 Elo 差在 50 以内而成本低 13%（§6.4，Figure 13）。
- 案例研究给出六个自证场景：GPU kernel 优化（AttnRes 时延从 283.6 ms 降到 114.4 ms，KDA 运行时降 73.6%）、GPU 编译器 MiniTriton、48 小时自主跑完的纳米模型推理芯片、复现天体物理 I–Love–Q 关系的编码研究、覆盖 42 年 AI ASIC 产业的知识工作站点、用 56 段素材剪出的解说视频（§7，Figure 14、Figure 15）。
- 自报局限：研究级推理与部分计算机使用基准落后于最强闭源模型，CritPt 落到 23.4%；评测口径里 Claude Fable 5 有 35% 任务触发 fallback，GPT-5.6 Sol 带潜在 cyberguard（§6.1.3、§6.1.4、§8）。

![[raw/2026-07/cs.CL/arXiv/kimi-k3/assets/kimi-k3-fig2.png]]

原文 Figure 2：Kimi K3 总体架构，按 token、通道、层三个方向组织。右上为骨干：每块三层 KDA 加一层 Gated MLA，每个注意力层后接 Stable LatentMoE；Attention Residuals 的伪查询 `w` 与注意力权重 `α` 从嵌入与各前序块取表示。左上为 Stable LatentMoE（共享专家两条，路由专家回传潜空间表示经 RMSNorm 后升维），左下为 KDA 分支，右下为 MoonViT-V2 到 MLP 的视觉通路。

![[raw/2026-07/cs.CL/arXiv/kimi-k3/assets/kimi-k3-fig4.png]]

原文 Figure 4：GLU、SwiGLU 与 SiTU-GLU 的门控分支、up 分支与标量响应曲线。SiTU-GLU 取 β₁ = 4、β₂ = 25，在前原点附近贴合 SwiGLU，大正输入下收敛到 `|f(x)| ≤ β₁β₂ = 100`。

## 立在什么基础上

四组基座，按与本文的距离排。

**一、自家的模型线**。Kimi K2（arXiv 2507.20534，2025-07-28 首发，2026-02-03 更新，cs.LG，200 项作者）是最直接的基线，两代规格对照写在 Table 1，权重裁剪与训练配方沿用（§3.3）；Kimi K2.5（arXiv 2602.02276，2026-02-02，cs.CL，337 项作者）贡献视觉通路、分离式编码器与 RL 算法；Kimi K1.5（arXiv 2501.12599，2025-01-22，cs.AI，96 项作者）贡献同步 RL 框架，本文的部分 rollout 方案建在它上面（§4.1.2）；Kimi Linear（arXiv 2510.26692，2025-10-30，cs.CL，60 项作者）贡献 KDA 与它的 chunkwise 形式，本文的每一条 KDA 改动都是相对这一篇的改动（§2.1.1）；Attention Residuals（arXiv 2603.15031，2026-03-16，cs.CL，37 项作者，官方仓库 `MoonshotAI/Attention-Residuals`）贡献深度轴的注意力残差，报告把它引作无编号的 Kimi Team 预印本（§2.2）；视觉侧接 Kimi-VL（arXiv 2504.07491，2025-04-10，95 项作者）与 K2.5 的 MoonViT-3D 设计（§2.4）。

**二、架构组件的外部来源**。注意力一侧：MLA 出自 DeepSeek-V2（arXiv 2405.04434，2024-05-07，157 项作者），本文的 Gated MLA 在它的潜变量 KV 之上加入满秩输出门（§2.1.2，公式 (7)）；门控注意力的做法引自《Gated Attention for Large Language Models》（arXiv 2505.06708，2025-05-10）；低精度 Flash Attention 的舍入偏差分析（arXiv 2510.04212，2025-10-05）给出把注意力输出保持 FP32 的理由。专家一侧：共享加路由专家的组织沿用 DeepSeekMoE（arXiv 2401.06066，2024-01-11，17 位作者）（§2.3）；潜空间路由出自 LatentMoE（arXiv 2601.18089，2026-01-26，16 位作者）（§2.3）；无辅助损失负载均衡（arXiv 2408.15664，2024-08-28）与其后续 DeepSeek-V3 技术报告（arXiv 2412.19437，2024-12-27，200 项作者）提供 SignSGD 式偏置更新，本文的 QB 在附录 C 里被推成同一对偶目标的精确坐标极小点（§2.3.3、附录 C）；辅助损失一路的代表是 Switch Transformers（Fedus、Zoph、Shazeer，JMLR 23，2022）（§2.3.3）；QB 的最优分配视角接到 BASE Layers（arXiv 2103.16716，2021-03-30），整数规划的近邻是 BIP（arXiv 2502.15451，2025-02-21），排他阈值路由（arXiv 2603.11535，2026-03-12）被明确区分（附录 C）；大规模专家数下路由不均衡的代价引 Step 3.5 Flash（arXiv 2602.10604，2026-02-11，216 项作者）（§2.3.3）。激活与归一化：GLU（Dauphin 等，ICML 2017）、SwiGLU（arXiv 2002.05202，2020-02-12）与 Swish（arXiv 1710.05941，2017-10-16）是 SiTU-GLU 的三件对照，PowLU（arXiv 2605.25704，2026-05-25）是同期的另一条参数化路线（§2.3.2）；RMSNorm（Zhang 与 Sennrich，NeurIPS 32，2019）在本文出现三处（§2.1.1、§2.2、§2.3.1）。线性注意力一线：结构化状态空间对偶（arXiv 2405.21060，2024-05-31）、Gated DeltaNet（Yang、Kautz、Hatamizadeh，ICLR 2025）、DeltaNet 的序列并行（Yang 等，NeurIPS 2024）、门控线性注意力（Yang 等，ICML 2024）、HGRN2（arXiv 2404.07904，2024-04-11）、Griffin（arXiv 2402.19427，2024-02-29）、RWKV-7（arXiv 2503.14456，2025-03-18）共同构成 KDA 的衰减与门控背景（§2.1.1）；YaRN（arXiv 2309.00071，2023-08-31）作为「本文不再需要的位置编码外推件」被点名（§2.1.2、§3.4）。残差与注意力形式：ResNet（arXiv 1512.03385，2015-12-10）、Bahdanau 注意力（arXiv 1409.0473，2014-09-01）、Transformer（Vaswani 等，NeurIPS 2017）、线性注意力（Katharopoulos 等，ICML 2020）与在线 softmax（arXiv 1805.02867，2018-05-08）分别支撑深度轴动机与块间合并（§2.2、§5.4.2）。优化器：Muon（Keller Jordan 博客，2024）；分头 Muon 的实证依据拉到 GLM-5（arXiv 2602.15763，2026-02-17，187 项作者）与 Muon is Scalable（arXiv 2502.16982，2025-02-24，28 项作者，作者含苏剑林）（§2.5、§5.2.2）；报告作者之一苏剑林另有两篇博客进参考文献，Muon 优化器指南与《MoE环游记：6、最优分配促均衡》（§2.5、§2.3.3）。

**三、训练配方、部署件与后训练**。学习率调度用 WSD 作对照，引 MiniCPM（arXiv 2404.06395，2024-04-09）（§3.2）；量化三件：量化感知训练（Jacob 等，CVPR 2018）用于训练期适配，MXFP4 微缩放格式（arXiv 2310.10537，2023-10-16，33 项作者）定格式（§4.1.4）；草稿模型建在 EAGLE-3（arXiv 2503.01840，2025-03-03）上，训练目标换成直接优化接受率的 LK loss（arXiv 2602.23881，2026-02-27）（§4.1.4）；多教师在线策略蒸馏引自 Thinking Machines 的 on-policy distillation 一文，并列同代实践 MiMo-v2-flash（arXiv 2601.02780，2026-01-06，127 项作者）与 DeepSeek-V4（arXiv 2606.19348，题录首发 2026-04-26，cs.CL，319 项作者）（§1、§4.1.3）。

**四、工程栈与评测夹具**。预训练系统引 GPipe（arXiv 1811.06965，2018-11-16）、Megatron-LM（arXiv 1909.08053，2019-09-17）、GShard（arXiv 2006.16668，2020-06-30）、ZeRO（arXiv 1910.02054，2019-10-04）、Ulysses（arXiv 2309.14509，2023-09-25）、Ring Attention（arXiv 2310.01889，2023-10-03）、线性注意力的序列并行 LASP（arXiv 2404.02882，2024-04-03）与 LASP-2（arXiv 2502.07563，2025-02-11）、线性 RNN 的并行化（arXiv 1709.04057，2017-09-12），专家并行的对照是 DeepEP（GitHub 仓库）与 ECHO 所在的 Megatron-Core 报告（arXiv 2603.07685，2026-03-08）、UltraEP（arXiv 2606.04101，2026-06-02）；MoE 反向重写参考 SonicMoE（arXiv 2512.14080，2025-12-16），跨 PP rank 卸载激活用 Mooncake 的传输引擎（arXiv 2407.00079，2024-06-24）（§5.1、§5.2）；沙箱件引 Firecracker（NSDI 2020）、OverlayBD 所属的 DADI（USENIX ATC 2020）与气泡利用的 Optimus（USENIX ATC 2025），AgentENV 由伙伴协作开源（§5.3.2）；编译器与算子引 PyTorch、MLIR（CGO 2021）、Triton（MAPL 2019）、NCCL、cuBLAS 与 Nangate45 标准单元库（§7）；KDA 内核与上下文并行接 FLA 库、FlashKDA 仓库与 DeltaNet 上下文并行笔记（§5.1.1、§5.1.2）；解码侧点名并发工作 ReplaySSM（Dao AI Lab 博客，2026）与 WarpDecode 的 token 中心设计（Cursor 博客）（§5.4.2）；智能体环境与评测夹具列出 Kimi Code、Claude Code、Codex、OpenClaw、Hermes（§4.2.1、§6.1.3）；第三方榜面对接 Artificial Analysis、Vals AI、LMArena 与 Agents' Last Exam 官方榜（§6.1.3、§6.3）。

**四条待考的联系（猜想）**。以下没有原文直接支撑，属我读出的可能关系，标注为猜想：其一，KDA 的下界衰减把逐位置对计算换成稠密矩阵乘，这条改动的动机写在「对角块是块内瓶颈」上，与并发出现的下界门控一族（HGRN2、Griffin、RWKV-7）在思路上同向，报告只给了「closely related」一句（§2.1.1，猜想）。其二，升维入口的 RMSNorm 在消融里同时抬高部分基准分数，报告给「稳定训练」与「一致改善验证损失与下游基准」两句，机制解释留给博客评注里的两个猜想（§2.3.1、博客 §Norm，猜想）。其三，QB 的直方图更新与 DeepSeek 的 SignSGD 式偏置更新共用同一对偶目标，附录 C 把 QB 写成该目标上的精确坐标极小化，把 SignSGD 式更新写成同一目标上的符号梯度一步，两代模型的均衡质量差异可能落在这条步长差异上，报告未给跨模型对照（§2.3.3、附录 C，猜想）。其四，评测里 FrontierSWE 与 SWE-Marathon 走的是自校准分支而非官方 v1.1 终版，报告在 §6.1.3 说明了重校准范围，这两个读数与第三方榜单的官方读数关系需要逐榜核对（§6.1.3，猜想）。

## 引用落在哪

参考文献 152 条，正文与附录的括号引用 233 处，覆盖全部条目；其中约 47 条出现在评测榜与评测夹具清单里。下列四张表收录承担论证的条目，逐条回一手渠道核过，访问日期均为 2026-09-22。报告内部编号在 HTML 版与 PDF 版之间有整体位移（KDA 在 HTML 版是第 57 条，PDF 版是第 64 条），表内用一手题录定位，不跟编号。

**一、自家模型线与深度轴前作**

| 本篇指称 | 一手出处 | 篇内落点 |
|---|---|---|
| Kimi K1.5 | arXiv 2501.12599，2025-01-22 首发，2025-06-03 更新，cs.AI，96 项作者（Kimi Team 领衔） | §1、§4.1.2、§5.3.1 |
| Kimi K2 | arXiv 2507.20534，2025-07-28 首发，2026-02-03 更新，cs.LG，200 项作者 | 摘要、§1、§2.1.2、§3.1、§4.1.1、§4.1.2、§5.2.2、§5.3.1 |
| Kimi K2.5 | arXiv 2602.02276，2026-02-02 首发，2026-08-07 更新，cs.CL，337 项作者 | §1、§2.1.2、§2.4、§3.1、§4.1.1、§4.1.2、§5.2.3 |
| Kimi Linear | arXiv 2510.26692，2025-10-30 首发，2025-11-01 更新，cs.CL，60 项作者 | 摘要、§1、§2.1、§2.1.1、§2.1.2、§7 |
| Attention Residuals | arXiv 2603.15031，2026-03-16 首发，cs.CL，37 项作者，仓库 `MoonshotAI/Attention-Residuals`；报告引作无编号预印本，按题名对上 | 摘要、§1、§2、§2.2、§5.2.2、§5.4.2 |
| Kimi-VL | arXiv 2504.07491，2025-04-10 首发，2025-06-23 更新，95 项作者 | §2.4 |
| Kimi CLI 与 Kimi Code | `https://www.kimi.com/code`；同组另引官方博客 `https://www.kimi.com/blog/kimi-k3`（附录 B 用） | §4.2.1、§6.1.3、附录 B |

**二、架构组件的外部来源**

| 本篇指称 | 一手出处 | 篇内落点 |
|---|---|---|
| MLA（DeepSeek-V2） | arXiv 2405.04434，2024-05-07 首发，157 项作者 | §2.1.2 |
| DeepSeekMoE | arXiv 2401.06066，2024-01-11，17 位作者 | §2.3 |
| LatentMoE | arXiv 2601.18089，2026-01-26，16 位作者 | §2.3 |
| 无辅助损失负载均衡 | arXiv 2408.15664，2024-08-28，5 位作者（Lean Wang、Huazuo Gao 等） | §2.3.3、§5.2.2、附录 C |
| DeepSeek-V3 技术报告 | arXiv 2412.19437，2024-12-27，200 项作者 | §2.3.3、§5.2.2、附录 C |
| Switch Transformers（辅助损失路线） | arXiv 2101.03961，2021-01-11 首发，3 位作者；期刊版 JMLR 23(120):1–39，2022 | §2.3.3 |
| Step 3.5 Flash | arXiv 2602.10604，2026-02-11，216 项作者 | §2.3.3 |
| BASE Layers | arXiv 2103.16716，2021-03-30，5 位作者 | 附录 C |
| BIP 的专家均衡整数规划 | arXiv 2502.15451，2025-02-21，Yuan Sun | 附录 C |
| 排他阈值路由 | arXiv 2603.11535，2026-03-12，4 位作者 | §2.3.3、附录 C |
| GLU | Dauphin、Fan、Auli、Grangier，ICML 2017，PMLR 70:933–941 | §2.3.2、Figure 4 |
| SwiGLU | arXiv 2002.05202，2020-02-12，Noam Shazeer | §2.3.2、Figure 4 |
| Swish | arXiv 1710.05941，2017-10-16，3 位作者 | §2.1.1 |
| PowLU | arXiv 2605.25704，2026-05-25，8 位作者 | §2.3.2 |
| RMSNorm | Zhang 与 Sennrich，NeurIPS 32，2019 | §2.1.1、§2.2、§2.3.1 |
| 门控注意力 | arXiv 2505.06708，2025-05-10，13 位作者 | §2.1.1、§2.1.2 |
| 结构化状态空间对偶 | arXiv 2405.21060，2024-05-31，Dao 与 Gu | §2.1.1 |
| Gated DeltaNet | Yang、Kautz、Hatamizadeh，ICLR 2025 | §2.1.1 |
| DeltaNet 的序列并行 | Yang 等，NeurIPS 2024 | §2.1.1 |
| 门控线性注意力 | Yang 等，ICML 2024 | §2.1.1 |
| HGRN2 | arXiv 2404.07904，2024-04-11，7 位作者 | §2.1.1 |
| Griffin | arXiv 2402.19427，2024-02-29，17 位作者 | §2.1.1 |
| RWKV-7 | arXiv 2503.14456，2025-03-18，18 位作者 | §2.1.1 |
| YaRN | arXiv 2309.00071，2023-08-31 首发，4 位作者 | §2.1.2、§3.4 |
| 低精度 Flash Attention 的舍入偏差 | arXiv 2510.04212，2025-10-05 首发，2 位作者 | §2.1.2 |
| ResNet | arXiv 1512.03385，2015-12-10，4 位作者 | §2.2 |
| Bahdanau 注意力 | arXiv 1409.0473，2014-09-01 | §2.2 |
| Transformer | Vaswani 等，NeurIPS 2017，`https://papers.nips.cc/paper_files/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html` | §2.2 |
| 线性注意力 | Katharopoulos 等，ICML 2020，PMLR 119:5156–5165 | §2.2 |
| 在线 softmax | arXiv 1805.02867，2018-05-08，2 位作者 | §2.2、§5.4.2 |
| Muon | Keller Jordan 博客，`https://kellerjordan.github.io/posts/muon/` | §2.5 |
| Muon is Scalable | arXiv 2502.16982，2025-02-24，28 项作者（含苏剑林） | §5.2.2 |
| GLM-5 | arXiv 2602.15763，2026-02-17，187 项作者 | §1、§2.5、§5.2、§5.2.2 |
| Muon 优化器指南（作者博客） | `https://kexue.fm/archives/11416` | §2.5 |
| MoE环游记：6、最优分配促均衡（作者博客） | `https://spaces.ac.cn/archives/11619` | §2.3.3、附录 C |

**三、训练配方、量化与后训练**

| 本篇指称 | 一手出处 | 篇内落点 |
|---|---|---|
| MiniCPM（WSD 调度对照） | arXiv 2404.06395，2024-04-09 首发，25 项作者 | §3.2 |
| 量化感知训练 | Jacob 等，CVPR 2018 | §4.1.4 |
| MXFP4 微缩放格式 | arXiv 2310.10537，2023-10-16，33 项作者 | §4.1.4 |
| EAGLE-3 | arXiv 2503.01840，2025-03-03 首发，4 位作者 | §4.1.4 |
| LK loss | arXiv 2602.23881，2026-02-27 首发，6 位作者 | §4.1.4 |
| 在线策略蒸馏 | Thinking Machines Lab，`https://thinkingmachines.ai/blog/on-policy-distillation/` | §1、§4.1.3 |
| MiMo-v2-flash | arXiv 2601.02780，2026-01-06 首发，127 项作者 | §1、§4.1.3 |
| DeepSeek-V4 | arXiv 2606.19348，题录首发 2026-04-26，319 项作者 | §1、§4.1.3 |
| ECHO 所在的 Megatron-Core 报告 | arXiv 2603.07685，2026-03-08，45 项作者 | §5.2.1 |
| UltraEP | arXiv 2606.04101，2026-06-02，13 项作者 | §5.2.1 |
| SonicMoE | arXiv 2512.14080，2025-12-16，5 位作者 | §5.2.2 |
| Mooncake 传输引擎 | arXiv 2407.00079，2024-06-24 首发，7 项作者 | §5.2.2 |
| Optimus（流水线气泡） | USENIX ATC 2025，`https://www.usenix.org/conference/atc25/presentation/feng` | §5.2.3 |

**四、工程栈、基准与沙箱**

| 本篇指称 | 一手出处 | 篇内落点 |
|---|---|---|
| GPipe / Megatron-LM / GShard / ZeRO / Ulysses | arXiv 1811.06965（2018-11-16）、arXiv 1909.08053（2019-09-17）、arXiv 2006.16668（2020-06-30）、arXiv 1910.02054（2019-10-04）、arXiv 2309.14509（2023-09-25） | §5.2 |
| Ring Attention / LASP / LASP-2 / 线性 RNN 并行化 | arXiv 2310.01889（2023-10-03）、arXiv 2404.02882（2024-04-03）、arXiv 2502.07563（2025-02-11）、arXiv 1709.04057（2017-09-12） | §5.1.2 |
| DeepEP | `https://github.com/deepseek-ai/DeepEP` | §5.2.1 |
| FLA 库 | `https://github.com/fla-org/flash-linear-attention`（含 DeltaNet 上下文并行合入请求） | §4.2.4、§5.1.1、§5.1.2 |
| FlashKDA | `https://github.com/MoonshotAI/FlashKDA` | §5.1.1（训练与前填充的 chunkwise 内核） |
| DeltaNet 上下文并行笔记 | Yaoyu Wang，`https://yywangcs.notion.site/DeltaNet-2a9fc9f5d8058013a498f34e0b25bd52` | §5.1.1、脚注 |
| MoonEP | `https://github.com/MoonshotAI/MoonEP` | §5.2.1（全均衡专家并行，附录 E 的上界证明） |
| AgentENV | `https://github.com/kvcache-ai/AgentENV` | §5.3.2（microVM 沙箱运行时） |
| ReplaySSM | `https://tridao.me/blog/2026/replayssm/` | §5.4.2（解码期重建 KDA 状态，与本文并发） |
| WarpDecode | `https://cursor.com/blog/warp-decode` | §5.4.2（token 中心的解码内核设计） |
| Firecracker | NSDI 2020，pp. 419–434 | §5.3.2 |
| DADI（OverlayBD 镜像服务） | USENIX ATC 2020，pp. 727–740 | §5.3.2 |
| PyTorch / MLIR / Triton / NCCL / cuBLAS / Nangate45 | `https://pytorch.org`、CGO 2021、MAPL 2019、`https://developer.nvidia.com/nccl`、`https://developer.nvidia.com/cublas`、`https://si2.org/open-cell-library/` | §7 |
| Claude Code / Codex / OpenClaw / Hermes | `https://docs.anthropic.com/en/docs/claude-code`、`https://github.com/openai/codex`、`https://docs.openclaw.ai/`、`https://hermes-agent.nousresearch.com/docs/` | §4.2.1、§6.1.3 |
| 评测榜与夹具（约 47 条） | 四个能力轴：推理与知识（GPQA Diamond、HLE-Full、CritPt）、编码（ProgramBench、SWE-Marathon、Terminal-Bench、DeepSWE、FrontierSWE、PostTrainBench）、智能体（BrowseComp、DeepSearchQA、MCPMark-Verified、OSWorld-Verified、OSWorld 2.0、AutomationBench、τ³-Banking、Harvey Lab、OfficeQA Pro、SpreadsheetBench 2、SaaS-Bench、JobBench）、视觉（Math-Vision、ZeroBench-main、MMMU-Pro、OmniDocBench、WorldVQA、BabyVision、PerceptionBench、Video-MME、MMVU） | §6.1.1 至 §6.1.3、Table 2 |

## 内部视角：并自《简单谈谈K3的MoE和Attention》

同族另有一篇博客评注（苏剑林，科学空间，2026-08-04，`https://spaces.ac.cn/archives/11848`），作者是 Kimi 研究员，逐条交代了 MoE 与 Attention 的设计动机。本篇摘要页列了它的要点，增强信息页落在 `blogs/context/k3-moe-attention-context.md`。与报告互补的六处内部说明如下，落点按报告的节号排。

- SiTU 的取舍理由（§2.3.2）：博客给出原始问题是 `W₁` 的某一行与输入同向时门控与 up 分支同时冒大值，中间出现 `O(‖x‖⁴)` 级异常值；作者先把 SiLU 换成 SiTU，压测后给 up 分支也加上 softcap。报告附录 B 补的是「平滑截断在饱和边界外仍保留非零梯度」，博客补的是「同样界限下 softcap 比硬截断效果好」这条实测判断，同期引用 GPT-OSS 与 DeepSeek-V4 的硬截断做法。
- 一个 RMSNorm 的来处（§2.3.1）：博客说明原始设计在降维之后与升维之前各放一个 RMSNorm，消融显示升维前那个作用最本质，按最小改动原则只保留它；报告写「一致改善验证损失与下游基准」，博客补了两个可能来源，一是更好地平衡了路由专家与共享专家的比例（加了这个 Norm 之后不再需要额外的缩放因子），二是很弱的非线性带来等效深度增加。
- QB 相对上一代的判据（§2.3.3）：博客给出两代负载均衡的连续性，Kimi K2 用 SignSGD 式 Loss-Free 更新，专家总数涨到 896 之后不够稳，QB 数学上更合理且无额外超参；分 bin 实测上，10000 个 bin 相对 1000 个 bin 对负载均衡没有更好增益，分布可加让跨机、跨梯度累积的聚合通信量极低。报告附录 C、附录 D 给的是对偶推导与误差界，博客给的是工程判据。
- 专家数的设想路径（§2.3）：博客写「原本的设想是 448 选 8，引入 LatentMoE 后变成 896 选 16，稀疏度不变」；报告只写 896 选 16 与稀疏度 56，这条设计路径属博客独有。
- MLA 保留的理由与理想注意力的四条约束（§2.1.2）：博客立起四条判据，效果不低于 MLA、训练与前填充成本不超过 MLA、KV 缓存更小、解码算力更小，并给出「当前没有简单设计同时满足四条」的判断；其中 MTP 与推测解码让 MLA 的解码形式（head_dims 512 以上的 MQA）提前消耗算力这一条，是报告 §4.1.4 把 MTP 层改造成 EAGLE-3 式草稿模型的背景。
- NoPE 的机制（§2.1.2、§3.4）：博客给出 KDA 隐含位置编码的推导，给 Q、K 加 DeltaNet 起到类 RoPE 的作用，KDA 属更一般的 DeltaNet，所以去掉 RoPE 之后效果基本不变；报告写「KDA 层提供位置敏感与近因感知的序列混合」，博客补上这条等价形式。博客另解释 MLA 仍拼接 64 维的做法是为了适配既有 MLA 基建并控制计算量。
- 对 DeepSeek-V4 的读法（§1、§2.1.2）：博客把 DeepSeek-V4 的注意力读成 MLA 解码形式的推广（head_dims 512、K = V 的 MQA 加 QKVO-RoPE 位置编码），再叠 Sparse 与 Compress 压计算与 KV 缓存，代价落在 Infra 复杂度与激进稀疏的最优性上，并给出「Linear+Full 路线与 Sparse 路线究竟谁能走得更远目前还不得而知」的开放判断。报告只在 §1 与 §4.1.3 把 DeepSeek-V4 列为同代实践与蒸馏对照。
- 分头 Muon（§2.5）：博客写这个改动没有效果上的优势，动机是正确性，每个 Head 本就相对独立；报告写的是一致性依据与优化器开销下降，两句互补。

## 谁做的

组织面：Kimi Team（Moonshot AI）。Hugging Face 组织页标为 Moonshot AI，名下 19 个模型、3 个数据集、16 篇论文、0 个 Space、18,698 位关注者，许可名 `kimi-k3`（`https://huggingface.co/api/organizations/moonshotai/overview`，访问日期 2026-09-22）。GitHub 组织页列出 30 个公开仓库，与本篇直接相关的有 `Kimi-K3`（描述 Open Frontier Intelligence）、`FlashKDA`、`MoonEP`、`minitriton`、`nano-kpu`、`Attention-Residuals`（`https://github.com/orgs/MoonshotAI/repositories`，访问日期 2026-09-22）。官方发布面同时给出技术博客 `https://www.kimi.com/blog/kimi-k3` 与权重、报告 PDF 三处入口。

作者面：arXiv 题录作者栏首项是组织名 `Kimi Team`，其后 401 个个人名，合计 402 项，与附录 A 的名单长度一致（arXiv API 与 abs 页一致，访问日期 2026-09-22）。附录 A 开篇写明「按姓氏字母序排列」，名单集中在一处，未分研究、工程、职能诸块，也未标离职或核心贡献者。报告正文没有通讯作者标注与联系邮箱。

本体与去向：权重仓库 `moonshotai/Kimi-K3` 最后改动 2026-09-02，标 1,914,251 次下载、11,455 个赞、pipeline 类型 image-text-to-text、MXFP4 权重与 MXFP8 激活（`https://huggingface.co/api/models/moonshotai/Kimi-K3`，访问日期 2026-09-22）；报告 2026-07-27 首发，2026-08-07 出 v2。报告点名的五个自研件都已开源：MoonEP、FlashKDA、minitriton、nano-kpu 与 AgentENV。

## 这个组与作者的特点

- **集体署名加姓氏字母序，模型报告的作者规模逐代抬升**。模型报告的作者栏从 Kimi K1.5 的 96 项、Kimi K2 的 200 项、Kimi K2.5 的 337 项升到本篇的 402 项，组件论文的名单短得多（Kimi Linear 60 项、Attention Residuals 37 项）（arXiv API，访问日期 2026-09-22）；名单只此一份，正文里没有核心贡献者与非核心的区分。
- **上一代成果直接成为下一代的对照表**。Table 1 把 K2 与 K3 的层数、总参数、激活参数、专家数、注意力组成逐行并列，scaling law 图（Figure 7）把 2.5 倍效率增益画成两条拟合曲线，架构改动的账面收益因此可读。
- **组件先成文、再收编**。KDA 与 Attention Residuals 各自先有独立报告与仓库（Kimi Linear 与 `Attention-Residuals`），本篇把它们收进骨架并按百万 token 上下文重做内核与缓存；MoonViT-V2 相对 K2.5 的改动（从零训练替代对比预训练初始化）也以消融读数的形式写进来（§2.4，Figure 6）。
- **组内作者公开写技术博客，报告回头引用自己的博客**。参考文献里两条是作者苏剑林的博客，一条讲 Muon 优化器（kexue.fm），一条讲最优分配促均衡（科学空间），分别落在优化器与负载均衡两节（§2.5、§2.3.3）；同一篇博客里对 SiTU、RMSNorm、QB、MLA、NoPE、DeepSeek-V4 的取舍说明与报告正文互补。
- **基础设施单列一节，且给出可复算的数**。MoonEP 的冗余专家上界带定理与紧性证明（附录 E），AgentENV 给检查点与恢复时延、内存超分比、沙箱与镜像总数，前缀缓存给物理块与哈希块两级粒度（§5.4.1、Figure 12）。这些数在报告里都带单位与场景，便于下游复核。
- **评测同时用自家夹具与第三方榜**。主表用自跑结果并按夹具标注（Kimi Code、Claude Code、Codex 三种混用），另外把 Artificial Analysis、Vals AI、LMArena、Agents' Last Exam 的第三方读数单列（§6.1.3、§6.3），成本效率单独一节比对每任务花费（§6.4，Figure 13）。

## 核验备注

- 报告内部引用编号在两种渲染间不一致：arXiv HTML 版把 KDA 编作第 57 条、Attention Residuals 第 60 条、Kimi K2 第 58 条，PDF 版分别编作第 64、58、59 条，同一张 Figure 4 图片里印的编号又是另一套（GLU 印 26、SwiGLU 印 108）。跨版本对号入座时以题录为准。
- Attention Residuals 一条报告记作「Kimi Team (2026) Attention residuals. Note: Preprint」，无编号；按题名在同一渠道对上 arXiv 2603.15031（2026-03-16 首发，cs.CL，37 项作者，官方仓库 `MoonshotAI/Attention-Residuals`）。这条对应关系是我按题名与作者栏做的匹配，报告本身未给编号。
- DeepSeek-V4 一条的编号段为 2606，arXiv 题录的首次提交日是 2026-04-26，编号月与题录月不一致。
- 模型卡 `config.json` 的 `num_nextn_predict_layers` 为 0，Table 1 的「Number of MTP Layers」记 1 层；§4.1.4 说明 MTP 层被微调成 EAGLE-3 式草稿模型，权重发布件里该字段为 0 属发布包口径这一种解释，报告未就此说明。
- 模型卡 `config.json` 的量化配置只给一组目标为 Linear 的 MXFP4 分组量化（group size 32，对称），报告 §4.1.4 描述专家权重走 MXFP4、激活走 MXFP8、非专家模块保持更高精度，两者粒度不同。
- 作者本人博客在参考文献里用了两个域名：Muon 优化器指南记 `kexue.fm/archives/11416`，MoE环游记第六篇记 `spaces.ac.cn/archives/11619`，两个域名指向同一个博客站。
- 科学空间的站内页面（含本篇引的两篇博客、站内旧文）对自动抓取返回 JS 跳转页（HTTP 403，正文长度约 124 字节），站内引文的题名与 URL 取自源文链接文本与站内检索页，未取全文。
- 评测口径两处要留意：Claude Fable 5 在 SWE-Marathon 与部分任务上触发 fallback（§6.1.3 记 35% 任务），GPT-5.6 Sol 的结果带潜在 cyberguard；FrontierSWE 的读数按 2026-07-16 的重算脚本口径，SWE-Marathon 走 H20 校准分支（2026-07-09 前）。
- 组织级指标这一跳未取 OpenAlex 记录，组织面事实由 arXiv 题录、Hugging Face API、GitHub 组织页与官方博客核对；Hugging Face 组织页的 `isVerified` 字段为 false。

## 关联

- [[kimi-k3-abstract|Kimi K3: Open Frontier Intelligence 摘要]]
- [[k3-moe-attention-context|简单谈谈K3的MoE和Attention 增强信息]]：内部视角评注，与本篇同族
- [[kimi-k3-reading|Kimi K3 精读]]：下游精读报告，与本篇同资源
- [[quantile-balancing|Quantile Balancing]]：本篇 §2.3.3 与附录 C、附录 D 的知识点
- [[kimi-linear|Kimi Linear]]：KDA 的原始出处
