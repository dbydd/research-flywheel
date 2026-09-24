---
title: MoE环游记：5、均匀分布的反思 增强信息
slug: moe-huanyouji-5-context
type: context
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2025-05/moe/spaces-ac-cn/moe-huanyouji-5/moe-huanyouji-5.extracted.md
  - raw/2025-05/moe/spaces-ac-cn/moe-huanyouji-5/moe-huanyouji-5.html
resource: raw/2025-05/moe/spaces-ac-cn/moe-huanyouji-5
---

# MoE环游记：5、均匀分布的反思 增强信息

## 这一篇做了什么

第五篇（2025-05-16，科学空间 10945）对「均匀分布就是最好的方向」提出反问，并拿 Shared Expert 与 Fine-Grained Expert 两件 DeepSeek 的改进作答（§开篇段）。

- Shared Expert：把 `n` 选 `k` 改成 `(n − s)` 选 `(k − s)`，另有 `s` 个 Expert 必然被选中（§共享专家，公式 (1)）。开启前后总 Expert 数与激活 Expert 数都不变，参数量与推理成本不变，DeepSeekMoE 与本组实验显示效果有提升（§共享专家）。
- 三种理解：残差视角（学习减去 Shared Expert 后的残差，降低学习难度）；把 Routed Expert 类比成学科老师、Shared Expert 类比成班主任；几何视角（Expert 之间的共性对应夹角小于 90 度，与第一篇的正交假设冲突，把 Shared Expert 视作 Routed Expert 的均值能让正交假设更容易成立）（§多种理解）。
- 比例因子 `λ`：让 Shared 与 Routed 在初始化阶段模长接近一致，用数值模拟估计；脚本对 DeepSeek-V2 配置给出约 16，对 DeepSeek-V3 配置给出约 2.83（§比例因子，正文脚本 `scaling_factor`）。
- 非均匀性：Shared Expert 造成的均衡目标分布是 `F = [1,…,1,1/(n−s),…]/(s+1)`，均匀分布作为最优方向这一点，由此看到一个具体反例（§非均匀性）；引 Zipf 定律说明现实世界的非均匀性普遍存在。
- Fine-Grained Expert：每个 Expert 缩小一半、改成 `2n` 选 `2k`，总参数与激活参数不变，组合数 `C(n,k) ≪ C(2n,2k)`（§细颗粒度）；作者另给一条解释——更多、更细的 Expert 能更好地覆盖现实世界的非均匀性，页内第 1 图用大小圆覆盖对比说明。
- 代价：`n` 增大后 Expert 之间的负载更不均衡，通信与协调成本上升，存在一个效果与效率都友好的舒适区间（§细颗粒度）。

页内第 1 图：`raw/2025-05/moe/spaces-ac-cn/moe-huanyouji-5/assets/moe-huanyouji-5-fig1.png`（原文未编号，按正文顺序计为第 1 图，大小圆覆盖对比）。

## DeepSeek 配置数字（本页首次交代，第九篇指回本页）

第五篇 §比例因子 用到两组配置。两组数字在 Hugging Face 官方 `config.json` 上核对如下（`https://huggingface.co/deepseek-ai/DeepSeek-V2/raw/main/config.json`、`https://huggingface.co/deepseek-ai/DeepSeek-V3/raw/main/config.json`，访问日期 2026-09-22）：

| 字段 | DeepSeek-V2 | DeepSeek-V3 |
|---|---|---|
| `n_routed_experts` 路由专家数 | 160 | 256 |
| `n_shared_experts` 共享专家数 | 2 | 1 |
| `num_experts_per_tok` 每 token 路由数 | 6 | 8 |
| `routed_scaling_factor` 比例因子 `λ` | 16.0 | 2.5 |
| `scoring_func` 打分激活 | `softmax` | `sigmoid` |
| `norm_topk_prob` 重归一化 | `false` | `true` |

源文把共享专家计入总数：DeepSeek-V2 记 `n = 162, k = 8, s = 2`（160 + 2 = 162，6 + 2 = 8），DeepSeek-V3 记 `n = 257, k = 9, s = 1`（256 + 1 = 257，8 + 1 = 9），脚本调用写作 `scaling_factor(162, 8, 2, 'softmax', False)` 与 `scaling_factor(257, 9, 1, 'sigmoid', True)`（§比例因子）。模拟对 DeepSeek-V2 给出约 16，与该配置的 `routed_scaling_factor = 16.0` 吻合；对 DeepSeek-V3 给出约 2.83，该配置实际取 2.5。

## 引用谱系

| 正文指称 | 出处 | 篇内落点 | 核验 |
|---|---|---|---|
| DeepSeekMoE | DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models，arXiv:2401.06066，2024-01-11，Damai Dai、Chengqi Deng、Chenggang Zhao、R. X. Xu、Huazuo Gao 等 17 位作者，`https://arxiv.org/abs/2401.06066` | §共享专家、§细颗粒度 | 已核，arXiv API，2026-09-22 |
| 《Muon is Scalable for LLM Training》 | arXiv:2502.16982，2025-02-24，Jingyuan Liu、Jianlin Su 等 28 位作者，`https://arxiv.org/abs/2502.16982` | §比例因子 | 已核，arXiv API，2026-09-22 |
| DeepSeek-V2 配置 | `https://huggingface.co/deepseek-ai/DeepSeek-V2/raw/main/config.json`（源文链 `blob/main/config.json#L48`） | §比例因子 | 已核，Hugging Face，2026-09-22 |
| DeepSeek-V3 配置 | `https://huggingface.co/deepseek-ai/DeepSeek-V3/raw/main/config.json`（源文链 `blob/main/config.json#L57`） | §比例因子 | 已核，Hugging Face，2026-09-22 |
| Zipf定律 | 科学空间 `https://spaces.ac.cn/archives/9607#Zipf定律` | §非均匀性 | 源文内链；站点对自动抓取返回 403 |
| 《MoE环游记：1、从几何意义出发》 | `https://spaces.ac.cn/archives/10699` | §多种理解 | 站内前篇，原文快照在 `raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-1/` |
| 《MoE环游记：3、换个思路来分配》 | `https://spaces.ac.cn/archives/10757` | §开篇段、§共享专家 | 站内前篇，原文快照在 `raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3/` |
| 《MoE环游记：4、难处应当多投入》 | `https://spaces.ac.cn/archives/10815` | §共享专家 | 站内前篇，原文快照在 `raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-4/` |

## 建立在前篇之上

- §共享专家 明确说明第三篇的 Loss-Free 替换与第四篇的动态激活「跟 Shared Expert 技巧都是正交的，因此接下来只以最基本的形式为例」，基线回到第一篇的 `y = Σ_{i∈argtop_k ρ} ρ_i e_i`。
- §多种理解 拿第一篇 §模长排序 的「Expert 两两正交」假设做几何检验：Expert 之间的共性对应夹角小于 90 度，Shared Expert 可以理解为 Routed Expert 的均值，学习残差让正交假设更容易成立。
- 开篇段把这之前的三篇归到负载均衡一条线上，本篇转入「均匀分布是否最优」这个问题，并给出「非均匀分布普遍存在」这个新方向。
- 第五篇是系列里 DeepSeek-V2/V3 配置数字首次出现的地方。第九篇 §其他选择 引用 DeepSeek-V3 的 Sigmoid 激活作为非 Softmax 路线的证据时，指回本页的配置表。

## 作者与组

本篇引用块为「苏剑林. (May. 16, 2025). 《MoE环游记：5、均匀分布的反思》[Blog post]. Retrieved from `https://spaces.ac.cn/archives/10945`」。作者与组的完整背景见 [[moe-huanyouji-1-context|第一篇 增强信息]]。

本篇是系列里作者自身工作在技术上被直接引用的第一篇：§比例因子 以「我们在《Muon is Scalable for LLM Training》提出」引用比例因子的量纲条件（Shared 与 Routed 在初始化阶段模长接近一致）。该文的 28 位作者中苏剑林居第二（arXiv API，2026-09-22），属 Moonshot AI 的规模化工作。

## 关联

- [[moe-huanyouji-5-abstract|MoE环游记：5、均匀分布的反思 摘要]]
- [[moe-huanyouji-1-context|第一篇 增强信息]]：基线形式与正交假设的出处
- [[moe-huanyouji-6-context|第六篇 增强信息]]：系列内下一篇，转入最优分配
