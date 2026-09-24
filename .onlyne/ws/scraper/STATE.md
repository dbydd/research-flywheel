本文件是 scraper 的手帐面：记叙段写过程，条目段写本 role 索引；它不在注入链上

## 记叙

本跳接 socrates 第二轮放行后的 Qwen3.8-Flash-Next 定稿精读，把它拆成 `wiki/` 知识点页并收敛本族。我先读 wiki-format 正本、定稿报告、增强页与第二轮判决书，按报告的五问切出四域：注意力的十页（混合配比的四层一全注意力、Gated DeltaNet 的递推与参数化、Qwen Sparse Attention 的块级打分、索引器蒸馏的两段协议、跨层与跨投机步的索引复用、加宽残差流的家族、Gated Residual 的算子形状、残差支路归因、RoPE 与 NoPE 的证据轴对照、稀疏注意力的两条路线对照），嵌入的两页（n-gram 嵌入、嵌入与专家容量对照），优化的五页（Muon 参数分工、Muon 正交化配置、批量与学习率重拟合、稳定性压力测试、门控归一化），评测协议与实体各一页，另加一条想法页。切法按知识点不按报告章节：报告的「问题二」把 mHC 家族与 GR 分成两页，两者各自可独立引用；「问题四」把正交化配置与权重分工同理分页。

一处我留下的判断：报告里 Kimi K3 与 DeepSeek-V4.1-Flash 的同题对照不另立汇总页，落到各知识点页的正文与两张对照页（位置编码证据轴、稀疏注意力两条路线），关系名是「对照」而不是「同源」，放进汇总页会造一个话题节点。

一个盘上问题我在 overview 的待补里点名了：先前几族在概览与仓根索引里点名的若干 Kimi K3 页面（下界衰减、满秩输出门、Gated MLA、混合与稀疏对照、系统层三页、后训练三页、评测口径页、实体页）在盘上不存在，从未提交进 git。我这一跳的注意力域有两页指向未建的 `wiki/attention/gated-mla`，与该页一并挂待补。这不是我这一族能一并补的活，留待后续。

收敛动作做完了：仓根 `AGENTS.md` 支线区删掉 Qwen 那条 todo，索引表补了五行承产物落点；`wiki/overview.md` 加了 Qwen 一域的四段知识面、资源层补一条、组织口径补三个新目录、待补补两条。DeepSeek-V4.1-Flash 那条支线不是本族，没动。

嵌图核了一遍：原图里的 fig2、fig3、fig13 三张是整页区域渲染，图面上下带着上一段正文。按 fig6-kernel 与 fig12-gate-isolation 的先例，我把三张按目标图重裁成 `qwen3.8-flash-next-fig2-gdn.png`、`-fig3-qsa.png`、`-fig13-production.png` 三个新件（`raw/` 只增不改，原图留着），三个页面改引新件。fig1、fig7、fig8 原图干净，直接用。

## 条目

|条目|内容位置|
|---|---|
|Qwen3.8-Flash-Next 拆出的注意力域十页|`wiki/attention/hybrid-attention-layer-ratio.md`、`gated-deltanet.md`、`qwen-sparse-attention.md`、`indexer-distillation.md`、`index-reuse-in-sparse-attention.md`、`wide-residual-stream.md`、`gated-residual.md`、`residual-branch-attribution.md`、`rope-vs-nope-evidence-axes.md`、`sparse-attention-route-comparison.md`|
|Qwen3.8-Flash-Next 拆出的嵌入域两页|`wiki/embedding/n-gram-embedding.md`、`embedding-vs-expert-capacity.md`|
|Qwen3.8-Flash-Next 拆出的优化域五页|`wiki/optimization/muon-parameter-partitioning.md`、`muon-orthogonalization-config.md`、`batch-size-and-lr-scaling-refit.md`、`training-stability-stress-test.md`、`gated-normalization.md`|
|Qwen3.8-Flash-Next 的三轴评估协议页与实体页|`wiki/evaluation/three-axis-architecture-eval-protocol.md`、`wiki/entities/qwen3.8-flash-next.md`|
|Qwen3.8-Flash-Next 延伸想法页（大宽度稀疏支路更新下的受约束混合）|`wiki/ideas/gated-residual-wide-stream-revisit.md`|
|本跳的收敛清理落点|`AGENTS.md`、`wiki/overview.md`|
|本跳新增的三张嵌图裁切件（GDN 结构、QSA 总览、生产早期对照）|`raw/2026-09/llm-architecture/github/qwen3.8-flash-next/assets/qwen3.8-flash-next-fig2-gdn.png`、`-fig3-qsa.png`、`-fig13-production.png`|
