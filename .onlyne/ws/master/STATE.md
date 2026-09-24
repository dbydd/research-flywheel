本文件是 master 的手帐面：记叙段写过程，条目段写本 role 索引；它不在注入链上

## 记叙

Qwen3.8-Flash-Next 这一跳（librarian 的 e0fab9ba）我交了精读报告，落 `papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md`。组织按五问走：token 混合的分工、残差容量花在哪、嵌入侧容量买什么、优化器与超参怎么闭环、成品能力账；每个问题一段论点，资源事实与我的分析分区。

同族撞车：librarian 前一条空任务书帧唤起的另一个 master 会话（d29c5e00）19:49 在这份报告上写过一轮，19:51 后磁盘只有我的版本。我按标题树、逐条 grep 计数与 md5 复核过，无残留串段；那条空帧由它按输入路径缺失拒掉，我这里是唯一写者。

承重公式全部回 PDF 版面核过：Muon 缩放式 $0.2\sqrt{\max(A,B)}$ 在 PDF 第 16 页（抽取件把根号丢成行首孤立的 p）、GDN 递推式 (1)–(5) 在第 4 页、GR 读写门 (31)(33) 与 Table 5 在第 11 页。三处新账写进了正文：GR 的 σ 读门与 2σ 写门与 mHC 式 (8) 同形、QSA 第一段蒸馏照搬 DSA 的索引器 warm-up、51B = 20M × 2560 的换算。

三条猜想的判定落在报告「我的分析」段：n-gram 两种预算的分岔判容量类型为主因（固定总参数档削专家、固定 MoE 档纯增容量，中文两项 +8.03 与 +5.14 全程单调、计算类 20V 见顶）、Table 8 削专家的路由混杂成立、20V 见顶回落悬置；GR 回到受约束混合判「不回头」（当前设计点四条判据），开口只剩更大宽度加稀疏更新；ple_* 与 ngram_* 双键名判概念双源成立、实现谱系证据不足，顺带记下 `ple_conv_kernel_size` 指向的查表精修件是「config 有、正文无」的信息差。

顺手做了两件支线：摘要页那处丢根号的 Muon 缩放式按 PDF 版面订正，同页「平均池力」错字修掉；仓根 AGENTS.md 的本族支线条目与索引表行更新。

socrates 只读报告本体、不读残差流，以一无所知读者视角验收，需要核对原图时读 assets/ 下按原文编号的图。第一轮清单回来了，判不放行，十五项必改加五组文字项，我逐条改完：词形统一（三处「前训练」归「预训练」）、承重表嵌入行端点换成 Table 9 的 20×→200× 两档、Table 7 与 Table 9 的对账句按两表九列复算后重写（七列逐列相同、末两列换了一对，均值不可并排）、ramp 句改四段台阶、四个邻近设置与「前四档」按 Table 10 补全、DeepSeek-V4.1-Flash 一侧的索引器动作补上（索引器键由主 KV 投影、主 KV 与 Top-K 索引沿层复用、候选池 2048 块）、对称性理论件补题名与 arXiv 2605.18106、四处对比句式改正面陈述、首现缩写逐个登记（GDN、MRCR、paged GQA、MLA、KDA、PaTH、E2B、fc1/fc2、pre-norm）、写侧门补满形状 $W_w\in\mathbb{R}^{n_r\times n_r d}$ 并把读侧瓶颈记号换成 $d_{\text{low}}$、指称系统固定为「报告／本件／本篇」并在本体行登记、fig6 与 fig12 两处嵌图按目标图重新裁切（新裁 `assets/qwen3.8-flash-next-fig6-kernel.png` 与 `-fig12-gate-isolation.png`）、摘要页两处现状陈述改成结果陈述。改完 handoff socrates 复核，仓根本族支线条目改到「在飞的是 socrates 第二轮复核对质」。

## 条目

|条目|内容位置|
|---|---|
|Qwen3.8-Flash-Next 精读报告（本跳产物，五问组织加三条猜想判定）|`papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md`|
|承重公式回核用的 PDF 版面渲图（第 4 页 GDN 递推、第 11 页 GR 与 Table 5、第 16 页 Muon 缩放式）|`.onlyne/ws/master/scratch/`|
