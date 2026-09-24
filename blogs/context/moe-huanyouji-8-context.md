---
title: MoE环游记：8、强制序列级均衡 增强信息
slug: moe-huanyouji-8-context
type: context
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/moe-huanyouji-8.extracted.md
  - raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/moe-huanyouji-8.html
resource: raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8
---

# MoE环游记：8、强制序列级均衡 增强信息

## 这一篇做了什么

第八篇（2026-05-22，科学空间 11760）把 Quantile Balancing 从全局均衡推到序列级均衡，给出 Moving Quantile Balancing（MQB）。

- 问题来源：Loss-Free 引入的偏置全局共享，已有的 Loss-Free 方案都只能做全局均衡；序列级均衡此前靠序列级 Aux Loss 实现，本篇要找它的 Loss-Free 对应物（§开篇段）。
- 两条先例：对分数做滑动平均再用它决定激活（站外作者的第一种思路，属经验做法，作者实测在极不均衡的层上帮助有限）（§局部中心）；按测试时训练为每个 Token 分配一个偏置并逐 Token 更新（第二种思路，等价于非线性 RNN，序列一长成为瓶颈）（§测试训练）。
- CQB 到 MQB 雏型：先设 `β_i = quantile(s_{[:i]}, 1 − k/n)`（Cumulative Quantile，复杂度平方级），再改为固定窗口 `w` 内的滑动分位数 `β_i = quantile(s_{[i−w:i]}, 1 − k/n)`，得到 Moving Quantile Balancing 的雏型（§滑动分位）。
- 分桶估计：把分位数的估计转成分布的估计——分数落在 `[0,1]` 内，等分 `b` 个桶做 one-hot，沿序列做 EMA，再由累积概率读出 `1 − k/n` 分位数作为逐 token 的 `β`（§分桶估计，伪代码框「Moving Quantile Balancing (MQB)」，页内第 1 图）。
- Top-`k` 版：MQB 削平 Router 的局部高峰后，对 `s_i − β_i` 取 Top-`k`，再补一步全局 QB 恢复均衡；用 `λ` 削弱序列均衡强度，`λ( s_i − β_i ) + (1 − λ) s_i = s_i − λ β_i`（§一般情况）。
- 实验：总参数量约 3B、128 选 4 的 MoE，滑动平均系数 0.99、分桶数 100，用 MaxVio 度量最不均衡的第一层；`λ = 1` 时均衡非常完美，代价是 Loss 差 0.06；`λ` 调到 0.3 左右时 Loss 基本不掉，均衡状况继续改善（§实验结果，页内第 2、3 图）。
- 推理成本：EMA 本质是 RNN，推理要多存一个 `n × b` 的 State，文中认为 `b = 100` 已经够用（§其他细节）。
- 开放问题：是否需要序列级均衡、需要何种程度，文中不给出标准答案；分桶方式目前是 Sigmoid 激活后均匀离散化，更精细的分桶留待实验（§延伸思考、§其他细节）。

页内图：`raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/assets/moe-huanyouji-8-fig1.png`（直方图近似估计分位数示意图）、`.../moe-huanyouji-8-fig2.png`（MQB(λ=1) 与 QB、SignSGD 的效果比较）、`.../moe-huanyouji-8-fig3.png`（不同的 λ 对应的负载均衡情况）。三张原文均未编号，按正文顺序计为第 1 至 3 图。

## 引用谱系

| 正文指称 | 出处 | 篇内落点 | 核验 |
|---|---|---|---|
| 《Causal Routing Bias for Aux-Loss-Free MoE Training》 | Jonathan Chang 的博客，发布于 2026-03-17，`https://jonathanc.net/blog/causal-routing-bias` | §局部中心、§测试训练 | 已核，页面元数据，2026-09-22 |
| 同一作者在 X 上的帖子 | `https://x.com/ChangJonathanC/status/2033942835951767612` | §局部中心、§测试训练 | 源文内链；站点对自动抓取受限 |
| Hash Routing | Hash Layers For Large Sparse Models，arXiv:2106.04426，2021-06-08，Stephen Roller、Sainbayar Sukhbaatar、Arthur Szlam、Jason Weston，`https://arxiv.org/abs/2106.04426` | §延伸思考 | 已核，arXiv API，2026-09-22 |
| 《DeepSeek V4的tid2eid是怎么来的？》 | 科学空间 `https://spaces.ac.cn/archives/11750` | §延伸思考 | 源文内链；站点对自动抓取返回 403 |
| 测试时训练（TTT） | 科学空间 `https://spaces.ac.cn/archives/11033#测试时训练` | §测试训练 | 源文内链；站点对自动抓取返回 403 |
| 《MoE环游记：2、不患寡而患不均》 | `https://spaces.ac.cn/archives/10735` | §前文回顾 | 站内前篇，原文快照在 `raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-2/` |
| 《MoE环游记：3、换个思路来分配》 | `https://spaces.ac.cn/archives/10757` | §前文回顾、§测试训练 | 站内前篇，原文快照在 `raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3/` |
| 《MoE环游记：4、难处应当多投入》 | `https://spaces.ac.cn/archives/10815` | §前文回顾 | 站内前篇，原文快照在 `raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-4/` |
| 《MoE环游记：6、最优分配促均衡》 | `https://spaces.ac.cn/archives/11619` | §前文回顾 | 站内前篇，原文快照在 `raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/` |
| 《MoE环游记：7、动态激活极简解》 | `https://spaces.ac.cn/archives/11626` | §前文回顾 | 站内前篇，原文快照在 `raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-7/` |

## 建立在前篇之上

- §前文回顾 把系列前七篇按负载均衡路线整理一遍：第二篇的 Aux Loss、第三篇起的 Loss-Free、第四篇的动态激活推广、第六篇的最优分配 QB、第七篇的动态版 QB（§前文回顾）。这是系列里第一次集中复述全部前篇的路线图。
- §最优之解 交代写作顺序：第六篇在先、第七篇在后，第七篇更简单，所以第八篇从第七篇讲起，再进入序列化（§最优之解、§滑动分位）。
- 本篇是系列里序列级均衡首次出现的地方。它把第二篇的 Aux Loss 序列级能力（第二篇 §一般形式 与第八篇 §前文回顾 记载 Aux Loss 可按序列、分组或全局调节颗粒度）与 Loss-Free 的偏置形式接起来，并给出这个问题的第一个 Loss-Free 答案。
- 篇内引入的两条先例来自站外作者 Jonathan Chang 的博客；作者用「我们后面自己的思路」与其对照（§局部中心），并在 §其他细节 指出 MQB 与其中第一种方案都落到 EMA 上，EMA 的对象各有不同。

## 作者与组

本篇引用块为「苏剑林. (May. 22, 2026). 《MoE环游记：8、强制序列级均衡》[Blog post]. Retrieved from `https://spaces.ac.cn/archives/11760`」。作者与组的完整背景见 [[moe-huanyouji-1-context|第一篇 增强信息]]。

本篇是系列里唯一以站外作者工作为对照对象的一篇。作者对 MQB 的位置有一段自评：它兼容常规的 MoE 形式，把「调节 Aux Loss 的系数」转化成「调节一个可解释的局部偏置项」，只影响 Router 决策而不注入梯度（§延伸思考）。这段属作者判断。

## 关联

- [[moe-huanyouji-8-abstract|MoE环游记：8、强制序列级均衡 摘要]]
- [[moe-huanyouji-6-context|第六篇 增强信息]]：QB 的出处
- [[moe-huanyouji-7-context|第七篇 增强信息]]：动态版 QB 一步解
- [[moe-huanyouji-9-context|第九篇 增强信息]]：系列内下一篇，转入门控归一化
