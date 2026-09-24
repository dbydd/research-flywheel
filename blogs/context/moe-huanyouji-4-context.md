---
title: MoE环游记：4、难处应当多投入 增强信息
slug: moe-huanyouji-4-context
type: context
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-4/moe-huanyouji-4.extracted.md
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-4/moe-huanyouji-4.html
resource: raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-4
---

# MoE环游记：4、难处应当多投入 增强信息

## 这一篇做了什么

第四篇（2025-03-28，科学空间 10815）把第三篇留下的 Bias 冗余自由度用于动态激活，让每个 Token 激活的 Expert 数目随难度浮动。

- 自由度：`b` 的全体分量加同一个常数不改变 `argtop_k(ρ + b)` 的排序（§优化目标）。作者先把第三篇的更新规则整体去均值，腾出这个自由度（§优化目标，公式 (5)）。
- 激活规则：从 `argtop_k(ρ + b)` 改为 `argwhere(ρ + b > 0)`，每个 Token 激活的 Expert 数目动态，同时免掉排序这一步（§设计思想，公式 (3)）。
- 更新规则：同时推动负载分布逼近均匀、推动平均激活数 `|F̃|` 逼近 `k`（§优化目标，公式 (6)）；只想保证不超过 `k` 的版本去掉一侧推力（公式 (7)）。
- 化简：把「逼近均匀」与「逼近预算」合并为让 `F̃` 逼近 `k/n`，写成一步符号梯度下降（§尝试简化，公式 (9)）；作者实测两个版本效果接近，化简版在训练前期的均衡度与预算抖动都大一些，追求稳定用三段式版本（§尝试简化）。
- 稳定性：用 RMS Norm 替代 `sign` 略稳，幅度有限（§尝试简化）。
- 初始化：在 Router logits 近似正态的假设下用二分法估算 `b`，正文给出可直接运行的脚本（§初始方式）。
- 相关工作梳理：AdaMoE 与 MoE++ 混入空白、复制、常数类低成本 Expert，间接实现动态数目；Top-`p` 的平均预算难以准确控制，需要额外熵损失；Ada-K Routing 另设模块预测激活数并用强化学习训练；DA-MoE 借 Attention 分数识别重要 token；ReMoE 同样基于零阈值，走 Aux Loss 路线（§相关工作）。

## 引用谱系

| 正文指称 | 出处 | 篇内落点 | 核验 |
|---|---|---|---|
| AdaMoE | AdaMoE: Token-Adaptive Routing with Null Experts for Mixture-of-Experts Language Models，arXiv:2406.13233，2024-06-19，Zihao Zeng、Yibo Miao、Hongcheng Gao、Hao Zhang 等 5 位作者，`https://arxiv.org/abs/2406.13233` | §相关工作 | 已核，arXiv API，2026-09-22 |
| MoE++ | MoE++: Accelerating Mixture-of-Experts Methods with Zero-Computation Experts，arXiv:2410.07348，2024-10-09，Peng Jin、Bo Zhu、Li Yuan、Shuicheng Yan，`https://arxiv.org/abs/2410.07348` | §相关工作 | 已核，arXiv API，2026-09-22 |
| 《Harder Tasks Need More Experts: Dynamic Routing in MoE Models》 | arXiv:2403.07652，2024-03-12，Quzhe Huang、Zhenwei An、Nan Zhuang、Mingxu Tao 等 11 位作者，`https://arxiv.org/abs/2403.07652` | §相关工作 | 已核，arXiv API，2026-09-22 |
| Ada-K Routing | Ada-K Routing: Boosting the Efficiency of MoE-based LLMs，arXiv:2410.10456，2024-10-14，Tongtian Yue、Longteng Guo、Jie Cheng、Xuange Gao 等 5 位作者，`https://arxiv.org/abs/2410.10456` | §相关工作 | 已核，arXiv API，2026-09-22 |
| DA-MoE | DA-MoE: Towards Dynamic Expert Allocation for Mixture-of-Experts Models，arXiv:2409.06669，2024-09-10，Maryam Akhavan Aghdam、Hongpeng Jin、Yanzhao Wu，`https://arxiv.org/abs/2409.06669` | §相关工作 | 已核，arXiv API，2026-09-22 |
| ReMoE | ReMoE: Fully Differentiable Mixture-of-Experts with ReLU Routing，arXiv:2412.14711，2024-12-19，Ziteng Wang、Jun Zhu、Jianfei Chen，`https://arxiv.org/abs/2412.14711` | §相关工作 | 已核，arXiv API，2026-09-22 |
| 《MoE环游记：2、不患寡而患不均》 | `https://spaces.ac.cn/archives/10735` | §设计思想 | 站内前篇，原文快照在 `raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-2/` |
| 《MoE环游记：3、换个思路来分配》 | `https://spaces.ac.cn/archives/10757` | §开篇段、§设计思想、§初始方式 | 站内前篇，原文快照在 `raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3/` |

**外部工作在动态激活一支里的位置。** 这一支的目标相同：让不同难度的 Token 使用不同数量的 Expert。实现路径分成四类。第一类混入低成本 Expert（AdaMoE 的空白 Expert、MoE++ 的零计算 Expert），保留 Top-`k` 基建；第二类把 Top-`k` 换成 Top-`p`（Harder Tasks Need More Experts）；第三类另设模块预测激活数并用强化学习训练（Ada-K Routing）或借 Attention 分数识别重要 token（DA-MoE）；第四类基于零阈值选择 Expert（ReMoE）。本篇同属第四类，求解走 Loss-Free，用 `b` 的自由度调控阈值；ReMoE 在这一类里走 Aux Loss 实现负载均匀与预算控制（§相关工作）。

## 建立在前篇之上

- 直接接第三篇 §相关细节 末段留下的 Bias 冗余自由度（§开篇段），把第三篇 §手搓梯度 的 SignSGD 更新式改造成带预算控制的版本。
- 第二篇与第三篇的 Aux Loss、Loss-Free 图景在 §设计思想 被复述一次，作为本篇修改的起点。
- 第七篇 §动态激活 从最优分配的对偶目标重新推出本篇凭直觉设计的 `s − β > 0` 激活规则，并指出两者形式一致；第八篇 §前文回顾 把本篇记作「把 Loss-Free 推广到动态激活数量」的一跳。这两处都指回本页。

## 作者与组

本篇引用块为「苏剑林. (Mar. 28, 2025). 《MoE环游记：4、难处应当多投入》[Blog post]. Retrieved from `https://spaces.ac.cn/archives/10815`」。作者与组的完整背景见 [[moe-huanyouji-1-context|第一篇 增强信息]]。

本篇 §相关工作 的评析带作者立场，源文自己注明是「从个人的审美角度」给出（§相关工作）。这些评析属于作者判断，本页照记并标明归属。

## 关联

- [[moe-huanyouji-4-abstract|MoE环游记：4、难处应当多投入 摘要]]
- [[moe-huanyouji-3-context|第三篇 增强信息]]：Bias 冗余自由度的出处
- [[moe-huanyouji-5-context|第五篇 增强信息]]：系列内下一篇，转入共享专家与细颗粒度
