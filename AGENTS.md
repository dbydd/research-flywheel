# 共享目标记录

本文件在 `AGENTS.md` 注入链上，每一轮都整份进每个会话的 prompt：只放目标、判据与索引这类固定物。进度与进行中的 todo 在 `STATE.md`（手帐面，按需读），运维手帐在 `.supervisor/STATE.md`。

## 主线

《MoE环游记》系列（苏剑林，科学空间，9 篇）完整入库，最终交出一份系列级精读报告。

判据：9 篇原文各落 `raw/<年月>/moe/spaces-ac-cn/moe-huanyouji-<N>/`（网页快照、抽取正文、图），9 页摘要落 `blogs/abstracts/`，9 页增强落 `blogs/context/`，系列级精读落 `blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md`；socrates 判定报告定稿后由 scraper 把知识点拆进 `wiki/`。

各族进度见 `STATE.md`。

## 索引

|条目|内容位置|
|---|---|
|《MoE环游记》系列拆出的知识点页（形式与几何、负载均衡与分位数、架构与门控、两张对照页、七条想法页）|`wiki/moe/`|
|Kimi K3 拆进 MoE 域的三页（潜空间专家 LatentMoE、有界激活 SiTU-GLU、分位数均衡的直方图估计）|`wiki/moe/architecture/latent-moe.md`、`wiki/moe/architecture/situ-glu.md`、`wiki/moe/load-balancing/quantile-histogram-estimation.md`|
|Kimi K3 注意力域的知识点页（三轴信息流、Kimi Delta Attention、下界衰减、满秩输出门、Gated MLA、NoPE、注意力残差、混合与稀疏路线对照）|`wiki/attention/`|
|Kimi K3 系统与基础设施页（MoonEP、KDA 算法与系统协同、前缀缓存两级粒度、AgentENV、三万亿级预训练并行）|`wiki/systems/`|
|Kimi K3 后训练页（多域强化学习与推理力度档、多教师在线策略蒸馏、多 token 预测层改造成投机解码草稿）|`wiki/training/`|
|Kimi K3 评测口径与成本账|`wiki/evaluation/eval-protocol-and-cost.md`|
|Kimi K3 实体页（规格、两代对照、权重发布件口径核对）|`wiki/entities/kimi-k3.md`|
|Kimi K3 延伸想法页（拆解 2.5 倍 scaling 效率增益、分位数均衡与符号梯度更新的正面对照）|`wiki/ideas/`|
|全库活综述（MoE 与注意力知识簇、系统层与资源层现状、待补项）|`wiki/overview.md`|
|DeepSeek-V4.1-Flash 技术报告的原文、抽取正文与 13 张图|`raw/2026-09/cs.CL/arXiv/deepseek-v41-flash/`|
|DeepSeek-V4.1-Flash 摘要页（含前提背景补充段）|`papers/abstracts/deepseek-v41-flash-abstract.md`|
|DeepSeek-V4.1-Flash 的 context 增强信息页（做了什么、立在什么基础上、引用落在哪、谁做的、组与作者特点）|`papers/context/deepseek-v41-flash-context.md`|
|DeepSeek-V4.1-Flash 精读报告（KV 缓存压缩三轴、CED 与 CSA2、FP4 与有界重放、训练与评测账、权重仓库配置核对）|`papers/readings/2026-09/cs.CL/arXiv/deepseek-v41-flash-reading.md`|
|DeepSeek-V4.1-Flash 拆出的知识点落点（稀疏注意力两条路线对照里的检索侧读数、索引沿层复用一页、嵌入与专家容量对照里的 Engram 落点；知识点按内容归页，页名不与报告强关联）|`wiki/attention/sparse-attention-route-comparison.md`、`wiki/attention/index-reuse-in-sparse-attention.md`、`wiki/embedding/embedding-vs-expert-capacity.md`|
|Qwen3.8-Flash-Next 的仓库快照、技术报告两版 PDF、抽取正文与 13 张原文图（另有按目标图重裁的嵌图若干）|`raw/2026-09/llm-architecture/github/qwen3.8-flash-next/`|
|Qwen3.8-Flash-Next 摘要页（规格表、四处架构改动、训练与评测数字）|`papers/abstracts/qwen3.8-flash-next-abstract.md`|
|Qwen3.8-Flash-Next 的 context 增强信息页（五问齐全，附「机制细节与对照账」四段：GDN 与 QSA 的公式形状、GR 与 mHC 与 AttnRes 的对照账、n-gram 两种预算的读数、Muon 分工与缩放律推导链；引用逐条回一手渠道核过，附发布件 config 对齐表）|`papers/context/qwen3.8-flash-next-context.md`|
|Qwen3.8-Flash-Next 精读报告（五问组织：混合与稀疏的粒度选择、GR 的读侧表达力、n-gram 两种预算、Muon 分工与缩放律重拟合、成品能力账；含三条猜想判定与与 Kimi K3 的同题对照）|`papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md`|
|Qwen3.8-Flash-Next 拆出的注意力域知识点页（混合注意力层间配比、Gated DeltaNet、Qwen Sparse Attention、索引器蒸馏、索引复用、加宽残差流、Gated Residual、残差支路归因、RoPE 与 NoPE 证据轴对照、稀疏注意力两条路线对照）|`wiki/attention/`|
|Qwen3.8-Flash-Next 拆出的嵌入域知识点页（n-gram 嵌入、嵌入与专家容量对照）|`wiki/embedding/`|
|Qwen3.8-Flash-Next 拆出的优化域知识点页（Muon 参数分工、Muon 正交化配置、批量与学习率缩放律重拟合、训练稳定性压力测试、门控归一化）|`wiki/optimization/`|
|Qwen3.8-Flash-Next 的三轴架构评估协议页与模型实体页（规格、14 项基座对照、成本与后训练口径）|`wiki/evaluation/three-axis-architecture-eval-protocol.md`、`wiki/entities/qwen3.8-flash-next.md`|
|Qwen3.8-Flash-Next 延伸想法页（大宽度稀疏支路更新下受约束混合是否重新有价值）|`wiki/ideas/gated-residual-wide-stream-revisit.md`|
|Kimi K3 技术报告的原文、抽取正文与 16 张图|`raw/2026-07/cs.CL/arXiv/kimi-k3/`|
|Kimi K3 摘要页（arXiv 2607.24653v2，Kimi Team，2026-07 首次提交）|`papers/abstracts/kimi-k3-abstract.md`|
|苏剑林《简单谈谈K3的MoE和Attention》原文、抽取正文与 1 张图|`raw/2026-08/llm-architecture/spaces-ac-cn/k3-moe-attention/`|
|该博客的摘要页（K3 架构取舍的内部视角）|`blogs/abstracts/k3-moe-attention-abstract.md`|
|Kimi K3 报告的 context 增强信息页（做了什么、立在什么基础上、引用落在哪、谁做的、组与作者特点、核验备注，附内部视角一节）|`papers/context/kimi-k3-context.md`|
|苏剑林博客的 context 增强信息页（引用谱系逐条核验、与前作的关系、作者与组、特点）|`blogs/context/k3-moe-attention-context.md`|
|Kimi K3 精读报告（三轴信息流、KDA 下界衰减、Stable LatentMoE 三件、基础设施与评测成本账，博客的内部视角已并入）|`papers/readings/2026-07/cs.CL/arXiv/kimi-k3-reading.md`|
