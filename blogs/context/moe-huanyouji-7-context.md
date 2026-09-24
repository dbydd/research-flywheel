---
title: MoE环游记：7、动态激活极简解 增强信息
slug: moe-huanyouji-7-context
type: context
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-7/moe-huanyouji-7.extracted.md
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-7/moe-huanyouji-7.html
resource: raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-7
---

# MoE环游记：7、动态激活极简解 增强信息

## 这一篇做了什么

第七篇（2026-02-23，科学空间 11626）把第六篇的最优分配问题再砍一刀，得到一个只需一步 Quantile 的动态激活解。

- 简化：去掉「每个 Token 恰好激活 `k` 个 Expert」的约束，只保留「每个 Expert 恰好被激活 `mk/n` 次」（§动态激活，公式 (1)）。作者说明后一条约束足以达成 MoE 的目标（§动态激活）。
- 一步解：对偶问题里只剩 `β` 一个变量，`β_j` 在每一列上有解析解——该列分数的第 `mk/n + 1` 大元素，也就是 `1 − k/n` 分位数（§一步求解，公式 (3) 至 (5)）。
- 激活规则：`s − β > 0` 即激活，免去 Top-`k` 排序（§实践要点）。
- 平滑：一步最优解容易过拟合当前批，用 EMA 平滑历史解，正文实验中取 `λ = 0.9`（§实践要点，伪代码框「Quantile Balancing (QB) 动态激活版」）。
- 理解：这本质上是把 Expert Choice 写成 Token Choice——Expert Choice 要求沿序列维度比较全体 Token，破坏因果律与训推一致性；Bias 形式把更新放到激活决策之后，规避了信息泄漏（§专家选择）。
- 初始化：`β` 的最优解是 `1 − k/n` 分位数，在 Router 初始 Logits 服从正态的假设下，初始化为 `σ·Φ⁻¹(1 − k/n)`；Sigmoid 单调递增，加激活函数即可；Softmax 需要额外处理归一化分母（§初始策略）。`σ` 由 Router 权重初始化方差与输入维度估出，`σ ≈ σ̃√d`（§初始策略）。
- 梯度下降：对 `β` 的可导目标做 SignSGD，成本比全局 Quantile 更低；这条式子正是第四篇从直觉给出的那条公式（§梯度下降）。
- 演示代码给出 `quantile_bias`、`max_min_avg_vio`、`avg_std_active` 三个函数，覆盖无激活、Sigmoid、Softmax 三种情形的初始化验证（§演示代码）。

## 引用谱系

| 正文指称 | 出处 | 篇内落点 | 核验 |
|---|---|---|---|
| 《MoE环游记：6、最优分配促均衡》 | `https://spaces.ac.cn/archives/11619` | §开篇段 | 站内前篇，原文快照在 `raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/` |
| 《MoE环游记：4、难处应当多投入》 | `https://spaces.ac.cn/archives/10815` | §动态激活、§初始策略、§梯度下降 | 站内前篇，原文快照在 `raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-4/` |
| Router 初始化方差估计的经典结果 | 科学空间 `https://spaces.ac.cn/archives/8620` | §初始策略 | 源文内链；站点对自动抓取返回 403 |
| 分位数函数（逆累积分布函数） | `https://en.wikipedia.org/wiki/Cumulative_distribution_function#Inverse_distribution_function_(quantile_function)` | §初始策略 | 维基百科条目，源文内链 |

这一篇没有引入新的外部论文。

## 建立在前篇之上

- 直接接第六篇：把第六篇 §线性规划 的两条等式约束减到一条（§动态激活），对应地把第六篇 §交替迭代 的两步交替减为一步 Quantile（§一步求解）。
- 第四篇的 `argwhere(ρ + b > 0)` 激活规则在这里被重新推出。作者指出这个形式与第四篇的激活规则一致；第四篇的规则来自直觉设计，本篇的规则来自更本质的对偶目标推导（§动态激活）。第四篇 §初始方式 的二分法模拟脚本与本篇 §初始策略 的解析式构成前后呼应，第四篇 §尝试简化 的公式 (9) 与本篇 §梯度下降 的 SignSGD 重合。
- 第八篇 §最优之解 交代写作顺序：第六篇在前、第七篇在后，第七篇在概念与方法上都更简单，所以第八篇从第七篇讲起。第八篇 §滑动分位 与 §分桶估计 在第七篇的 QB 上继续做序列级扩展。

## 作者与组

本篇引用块为「苏剑林. (Feb. 23, 2026). 《MoE环游记：7、动态激活极简解》[Blog post]. Retrieved from `https://spaces.ac.cn/archives/11626`」。作者与组的完整背景见 [[moe-huanyouji-1-context|第一篇 增强信息]]。

第六篇与第七篇的发布日相邻（2026-02-22 与 2026-02-23），两篇构成一组：第六篇给出 Top-`k` 版 QB 的完整推导，第七篇给出动态激活版的一步解。

## 关联

- [[moe-huanyouji-7-abstract|MoE环游记：7、动态激活极简解 摘要]]
- [[moe-huanyouji-6-context|第六篇 增强信息]]：QB 的两步交替解与线性规划框架
- [[moe-huanyouji-4-context|第四篇 增强信息]]：本篇重新推出的动态激活形式与初始化脚本
- [[moe-huanyouji-8-context|第八篇 增强信息]]：系列内下一篇，序列级 Moving Quantile Balancing
