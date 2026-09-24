---
title: 简单谈谈K3的MoE和Attention 增强信息
slug: k3-moe-attention-context
type: context
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2026-08/llm-architecture/spaces-ac-cn/k3-moe-attention/k3-moe-attention.extracted.md
  - raw/2026-08/llm-architecture/spaces-ac-cn/k3-moe-attention/k3-moe-attention.html
resource: raw/2026-08/llm-architecture/spaces-ac-cn/k3-moe-attention
---

# 简单谈谈K3的MoE和Attention 增强信息

## 这一篇做了什么

这是 Kimi K3 的内部视角评注，作者苏剑林，科学空间 2026-08-04 发布（`https://spaces.ac.cn/archives/11848`，站内页面元数据与正文引用块一致，访问日期 2026-09-22），关键词标为线性、attention、位置编码、moe。全篇约五屏，分「写在前面」「混合专家」「注意机制」「文章小结」四节，配一张直方图（`raw/2026-08/llm-architecture/spaces-ac-cn/k3-moe-attention/assets/k3-moe-attention-fig1.png`，原文未编号，按正文顺序计为第 1 图），交代的是设计动机与取舍判断，架构账目留给技术报告。下文落点用该博客自己的小节名。

- 架构总式：K3 = KDA + MLA + Stable LatentMoE + AttnRes，训练优化器沿用 Moonlight 版 Muon，注意力部分的权重改成 Per-Head 形式（§写在前面）。作者自陈这是「集大成」的持续演化，并把 AttnRes 与 KDA 的详细交代指回自己的两篇前作。
- MoE 主线是把 LatentMoE 稳下来（§混合专家）。原版 LatentMoE 先降维到 `d/2`、再做 `2n` 选 `2k` 的稀疏混合、最后升维，四矩阵连乘带来不稳定；Stable 版本做三件事：把门控里的 SiLU 换成带 softcap 的 SiTU（β₁ = 4），给 up 分支也加 softcap（β₂ = 25）形成 SiTU-GLU，用来压住 `W₁` 与输入同向时出现的 `O(‖x‖⁴)` 级异常值；稳定化按最小改动原则只在升维入口留一个 RMSNorm；负载均衡从 Kimi K2 的 SignSGD 式 Loss-Free 更新换成 QB（分位数均衡，Quantile Balancing）。
- QB 的三条工程判据（§QB）：专家总数从设想里的 448 选 8 涨到 896 选 16 之后，SignSGD 式更新不够稳；QB 数学上更合理且无需额外超参；分位数落地走分 bin 直方图，10000 个 bin 相对 1000 个 bin 对负载均衡没有更好增益，分布的可加性让分布信息能跨机、跨梯度累积地以极低通信量聚合。
- RMSNorm 的事后对照（§Norm）：在两侧都加 Norm 的消融里，升维前那个作用最本质；加不加对验证损失影响不大，对某些基准不加会稳定变差；作者给两个可能来源，一是更好地平衡了路由专家与共享专家的比例（加了它之后不再需要额外缩放因子），二是很弱的非线性带来等效深度增加。
- Attention 侧保留 MLA（§MLA）：判据是在固定训练成本与 KV 缓存规模下 MLA 近乎最优，MTP 或推测解码让 MLA 的解码形式（head_dims 512 以上的 MQA）提前消耗算力；文中列出理想 Attention 的四条约束，效果不低于 MLA、训练与前填充成本不超过 MLA、KV 缓存更小、解码算力更小，并给出当前没有简单优雅设计同时满足四条的判断。往小了改（128+128 的 GQA8）效果难打赢 MLA 且 KV 缓存是 MLA 的三倍多，往大了改（256+256 的 MFA）效果能追回而训练成本与预填充成本上升。
- 对 DeepSeek-V4 的读法（§DSV4）：文中把 DSV4 的 Attention 读成 MLA 解码形式的推广（head_dims 512、`K = V` 的 MQA 加 QKVO-RoPE 位置编码），再叠 Sparse 与 Compress 压计算与 KV 缓存，代价落在 Infra 复杂度与激进稀疏的最优性上；结尾给出「Linear+Full 路线与 Sparse 路线究竟谁能走得更远，目前还不得而知」的判断。
- NoPE 的机制（§NoPE）：K3 保留标准 MLA 结构而去掉 RoPE。作者给出推导，任意正交矩阵的幂都能构建广义 RoPE，给 `Q`、`K` 加 DeltaNet 能起到类 RoPE 的位置编码作用，KDA 属更一般的 DeltaNet，所以 KDA 加 MLA 的混合模型自带位置编码。作者另解释 MLA 仍拼接 64 维是为了适配既有基建并控制计算量，K3 已引入 KDA、AttnRes 等新变量，不再往 MLA 加变数。
- 分头 Muon（§写在前面）：这个改动没有效果上的优势，动机是正确性，每个 Head 本就相对独立，不应耦合在一块。

## 引用谱系

正文的外链分两类：站内是作者自己的系列前作，站外是 arXiv 论文，站外链接统一走 `papers.cool`（同一作者的论文阅读站）。逐条核验如下，访问日期均为 2026-09-22。

| 正文指称 | 出处 | 篇内落点 | 核验 |
|---|---|---|---|
| K3 官方博客 | `https://www.kimi.com/blog/kimi-k3` | §写在前面 | 已核，HTTP 200，题名 Kimi K3 Tech Blog: Open Frontier Intelligence |
| 《Attention Residuals 回忆录》 | `https://spaces.ac.cn/archives/11664` | §写在前面 | 站内页对自动抓取返回 JS 跳转页（403，正文 124 字节）；题名经站内检索页「包含关键字 AttnRes 的文章」对上 |
| 《Kimi Linear: An Expressive, Efficient Attention Architecture》 | arXiv 2510.26692，2025-10-30 首发，2025-11-01 更新，cs.CL，60 项作者（`https://papers.cool/arxiv/2510.26692`） | §写在前面、§NoPE | 已核，arXiv API |
| 《LatentMoE: Toward Optimal Accuracy per FLOP and Parameter in Mixture of Experts》 | arXiv 2601.18089，2026-01-26，cs.LG，16 位作者（`https://papers.cool/arxiv/2601.18089`） | §混合专家 | 已核，arXiv API |
| Swish（SiLU 的别名出处） | arXiv 1710.05941，2017-10-16，3 位作者 | §SiTU | 已核，arXiv API |
| GPT-OSS | arXiv 2508.10925，2025-08-08，127 位作者 | §SiTU（硬截断的既有做法） | 已核，arXiv API |
| DeepSeek-V4 | arXiv 2606.19348，题录首发 2026-04-26，cs.CL，319 项作者 | §SiTU（硬截断的既有做法）、§DSV4（整节讨论） | 已核，arXiv API |
| 《MoE环游记：6、最优分配促均衡》 | `https://spaces.ac.cn/archives/11619` | §QB（QB 细节的出处） | 站内页对自动抓取返回 JS 跳转页；题名经站内检索页与本仓 `blogs/context/moe-huanyouji-6-context.md` 对上 |
| 《Loss-Free》（不含额外辅助损失的负载均衡） | `https://spaces.ac.cn/archives/10757` | §QB（K2 所用方案的出处） | 站内页，同上；题名取自链接锚文，系列内第三篇即此篇 |
| 《Transformer升级之路：20、MLA好在哪里?（上）》 | `https://spaces.ac.cn/archives/10907` | §MLA、§DSV4 | 站内页，同上；题名取自链接锚文 |
| 《Transformer升级之路：21、MLA好在哪里?（下）》 | `https://spaces.ac.cn/archives/11111` | §MLA、§DSV4 | 站内页，同上；题名取自链接锚文 |
| MFA（Multi-matrix Factorization Attention） | arXiv 2412.19255，2024-12-26 首发，8 位作者 | §MLA（往大了改的对照） | 已核，arXiv API |
| 《Transformer升级之路：6、旋转位置编码的完备性分析》 | `https://spaces.ac.cn/archives/9403` | §NoPE（广义 RoPE 的推导出处） | 站内页，同上；题名取自链接锚文 |
| QKVO-RoPE（用于位置编码的注意力变体） | `https://spaces.ac.cn/archives/10862` | §DSV4（DeepSeek-V4 的位置编码做法） | 站内页，同上；题名取自链接锚文 |
| PaTH（Householder 变换位置编码） | arXiv 2505.16381，2025-05-22 首发，8 位作者 | §NoPE | 已核，arXiv API |
| 《线性注意力简史：从模仿、创新到反哺》 | `https://spaces.ac.cn/archives/11033` | §NoPE（DeltaNet 等价形式的推导出处） | 站内页，同上；题名取自链接锚文 |

站内八处链接都指向作者自己的科学空间（七篇前作加 QKVO-RoPE 一处），另有一处指向站内 FAQ；站外七篇论文分布在 MoE 稳定化、注意力取舍与位置编码三条线上。

## 建立在前篇之上

- 与前作的关系：本篇把 AttnRes 与 KDA 两块指回两篇前作（《Attention Residuals 回忆录》与 Kimi Linear 技术报告），细节留在前作，本篇的重心是 MoE 与 MLA。
- 与报告的分工：报告给规格、公式与评测读数，本篇给「为什么这么选」。互补后最完整的六处是 SiTU 的取舍理由、一个 RMSNorm 的来处、QB 相对上一代负载均衡的判据、专家数的设想路径（448 选 8 到 896 选 16）、MLA 保留理由与理想注意力的四条约束、NoPE 的机制推导，另有对 DeepSeek-V4 与分头 Muon 的两段判断。这些内容已并进 [[kimi-k3-context|Kimi K3 增强信息]] 的「内部视角」一节。
- 与系列知识点的关系：QB 的完整推导落在第三篇与第六篇，本篇只给工程判据（见 [[quantile-balancing]] 与 [[moe-huanyouji-6-context|MoE环游记：6、最优分配促均衡 增强信息]]）；Loss-Free 的来路见 [[loss-free-balancing]]；共享专家与路由专家的比例问题接 [[shared-expert]]。
- 与 MoE环游记系列的间隔：上一篇 MoE 负载均衡主题的站内博客是《MoE环游记：6、最优分配促均衡》（2026-02-22），该系列此后未见续篇；本篇发布在 2026-08-04，同期站内另有《解构Scaling Law》与《将Softmax Attention线性化为Gated DeltaNet》等篇。

## 作者与组

作者：苏剑林，Kimi 研究员。证据链三条。其一，本篇引用块自署「苏剑林. (Aug. 04, 2026). 《简单谈谈K3的MoE和Attention》[Blog post]. Retrieved from `https://spaces.ac.cn/archives/11848`」，正文用第一人称复数叙述 K3 的发布与设计（「上个月，我们发布了迄今为止最大的开源模型K3」「K3所用的MoE，我们称之为Stable LatentMoE」）。其二，arXiv 题录里 `Jianlin Su` 依次出现在 Kimi K1.5（2501.12599）、Kimi K2（2507.20534）、Kimi Linear（2510.26692）、Kimi K2.5（2602.02276）、Attention Residuals（2603.15031）与 Kimi K3（2607.24653）的作者栏中，访问日期 2026-09-22。其三，Kimi K3 技术报告的参考文献里两条署 `J. Su`，一条是 Muon 优化器指南（`https://kexue.fm/archives/11416`），一条是《MoE环游记：6、最优分配促均衡》（`https://spaces.ac.cn/archives/11619`），分别落在报告的优化器一节与负载均衡一节。

站点：科学空间（Scientific Spaces），作者的个人学术博客，同时挂在 `spaces.ac.cn` 与 `kexue.fm` 两个域名下，文末带转载条款与 BibTeX 引用块，`@online{kexuefm-11848}` 这一键名沿用旧域名。作者名下另有一个 arXiv 论文阅读站 `papers.cool`，本篇的七处站外论文链接都走这个站的中转。

作者与组的特点：主题成系列。同一位作者在同一个站点上连续写 MoE 负载均衡（《MoE环游记》）、注意力与位置编码（《Transformer升级之路》《线性注意力简史》）、优化器与训练（《让炼丹更科学一些》《动量的新理解》）几条线，每篇都把上一阶段的新模型当引子，本篇接的是 K3 上线。文体是先给判据再给结论：理想 Attention 用四条约束定框，QB 用三条工程判据对比上一代，条目成串且可证伪的边界写得明确。引用的组织方式是自引自家站点加外链自家阅读站，本篇八处站内档案链接都指回科学空间，七篇站外论文都经 `papers.cool` 中转。组的层面，核心技术成员在个人博客上公开解释架构取舍，官方技术报告回头把这些博客收进参考文献（Muon 优化器指南与《MoE环游记：6、最优分配促均衡》两条），个人叙述与官方文档互为注释。

## 核验备注

- 站内页面对自动抓取一律返回 JS 跳转页（HTTP 403，正文约 120 字节，页内是 `window.location.href` 一行脚本），八处站内链接都未取到全文。题名与 URL 取自源文链接锚文；《Attention Residuals 回忆录》与《MoE环游记：6、最优分配促均衡》两篇另经站内检索页与仓内上游页面对上。
- 本篇写 10000 个 bin 对负载均衡没有更好的增益，推荐 1000 个 bin；技术报告附录 D 给的是 `B = 1000` 时误差上界为 bin 宽（量级 1e-3）并说明未观察到可测的残余不均衡，两处口径一致，报告多给出误差界。
- 本篇对 DeepSeek-V4 的指称是「DSV4」，对应 arXiv 2606.19348；该条题录的首次提交日 2026-04-26 与编号段 2606 不一致。
- 本篇提到的「原本的设想是 448 选 8」在 Kimi K3 技术报告里没有对应句子，属本篇独有的设计路径说明。
- 本篇说 MFA「本质上是个 MQA」，arXiv 题录的正式题名是 Multi-matrix Factorization Attention，作者与篇名以题录为准。
- 本篇正文里的公式编号由本仓抽取文本保留在 LaTeX 片段里，页内引用按小节名定位，未使用原文的公式序号。

## 关联

- [[k3-moe-attention-abstract|简单谈谈K3的MoE和Attention 摘要]]
- [[kimi-k3-context|Kimi K3: Open Frontier Intelligence 增强信息]]：本篇的内部视角已并进该页
- [[kimi-k3-reading|Kimi K3 精读]]：下游精读报告，与本族同资源
- [[quantile-balancing|Quantile Balancing：对偶解与分位数]]：QB 的完整推导
- [[loss-free-balancing|Loss-Free 负载均衡]]：本篇 QB 的上一代方案
- [[shared-expert|共享专家]]：本篇关于路由专家与共享专家比例的那段
- [[moe-huanyouji-6-context|MoE环游记：6、最优分配促均衡 增强信息]]：本篇引的 QB 出处
