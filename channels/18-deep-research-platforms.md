# 18 — Deep Research 平台族：OpenAI / Gemini / Perplexity + ManuSearch

| 维度 | 内容 |
|------|------|
| **机构** | OpenAI (Deep Research, 2025-02-02 发布, 2025-07 视觉代理升级)；Google Gemini (Deep Research, 2024-12-11 发布, Gemini 3 驱动)；Perplexity (Deep Research, 2025-02-14 发布)；ManuSearch (中国人民大学 RUCAIBox, Huang 等 7 人, arXiv:2505.18105, Findings of EMNLP 2025) |
| **发布时间** | OpenAI https://openai.com/index/introducing-deep-research；Gemini https://gemini.google/overview/deep-research；Perplexity https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research；ManuSearch https://github.com/RUCAIBox/ManuSearch |
| **开源状态** | OpenAI/Gemini/Perplexity **闭源托管服务**，通过 ChatGPT/Gemini/Perplexity 前端与 API 暴露；ManuSearch **完全开源 (MIT)**，https://github.com/RUCAIBox/ManuSearch，可本地部署，支持任意 LLM 后端 |
| **循环形态** | **迭代检索-推理闭环**：规划 → 检索 → 阅读 → 综合 → 发现缺口 → 再规划，多轮自适应直至生成引用完备的分析师级报告；ManuSearch 将该闭环显式拆为三智能体协作 |
| **核心关键词** | Agentic deep research；dual-browser；hybrid multi-model；iterative retrieval loop；transparent modular multi-agent |

## 1. 平台分层

### OpenAI Deep Research
```
Layer 4  报告合成层 — 数百来源综合为结构化长报告，含引用与推理链展示
Layer 3  推理规划层 — o3 专用推理模型 (o1 推理训练范式 + RL 强化微调)，ReAct 循环：Plan → Act → Observe → Re-plan
Layer 2  工具执行层 — 双浏览器架构：文本浏览器 (搜索/API/文档抽取/PDF/图像) + 视觉交互浏览器 (点击/填表/多步导航，2025-07 新增)
Layer 1  检索基座 — Bing/Google 搜索 API + 网页抓取清洗 + PDF/图像解析
  横切  安全与风控 — o3 中等风险评级，web hazard 缓解，来源可追溯
```

### Gemini Deep Research
```
Layer 4  报告合成层 — 多页报告，自动评估发现、识别缺口、再综合
Layer 3  规划-执行-精化循环 — Gemini 3 驱动的重复 plan-execute-refine，保持长任务上下文
Layer 2  检索与 Workspace 融合层 — 数百网页扫描 + Gmail/Drive/Chat 私域内容自动接入
Layer 1  搜索基座 — Google 搜索 + Workspace 索引
```

### Perplexity Deep Research
```
Layer 4  报告合成层 — 推理驱动的深度报告
Layer 3  混合模型路由层 — 按子任务动态选择最适配模型 (概括 vs 检索结果判读等)
Layer 2  迭代检索循环 — 基于新发现洞察持续调整检索策略，非单轮搜索
Layer 1  检索基座 — Perplexity 搜索引擎 + 多模型推理
```

### ManuSearch (开源可复刻参考)
```
Layer 3  Solution Planning Agent — 迭代生成与精化子查询，产出结构化研究计划
Layer 2  Internet Search Agent — 实时 web 检索，执行子查询
Layer 1  Webpage Reading Agent — 结构化抽取与证据综合，返回关键证据
  底座  任意 LLM 后端 + 搜索引擎 API + 网页解析
  特性  三智能体协作透明可解释，模块化可扩展，无需私有工具链
```

四者共同抽象：**规划层与执行层分离，检索-阅读-推理形成可观测闭环，报告层对证据链负责**。该分层与 Bohrium 的 Reading/Computing/Experiment 以及 SciMaster 的推理-执行分离同构，规模更聚焦于文献与网络证据。

## 2. Capability 注册

- **OpenAI**：工具以 function calling 契约注册，包含 search、scrape、pdf_extract、image_understand、visual_browse 等；每个工具声明输入输出 schema 与失败模式，o3 控制器按 ReAct 轨迹路由。商业版通过 ChatGPT Agent Mode 暴露，支持用户侧一键触发。
- **Gemini**：能力注册与 Workspace 深度绑定，Gmail/Drive/Chat 作为私有 capability 与公开网页检索同等注册，调度器据任务类型选择公域或私域来源，体现 capability 分面思想。
- **Perplexity**：混合模型即 capability 路由 — 不同子任务绑定不同模型能力，注册表记录模型在概括、检索判读、推理等维度的适配度，运行时动态分发。
- **ManuSearch**：三智能体本身即能力注册单元，每个 agent 暴露清晰接口 (输入子查询/输出证据/输出计划)，外部可替换任意 LLM 或搜索引擎实现；`manusearch/` 模块化代码使新增 agent 类型无需改动主循环，符合最小契约原则。

> 共同模式：能力以显式契约注册，调度器据任务上下文路由，执行结果携带来源与成本元数据，为后续 trace 关联提供键。

## 3. Trace 治理

- **OpenAI**：展示详细推理步骤与搜索进展，用户可回溯每一步检索与综合依据；每份报告附数百来源引用，支持溯源验证；视觉浏览器操作留痕，处理高风险 web 内容时有风控审计。
- **Gemini**：自动评估发现并识别缺口的过程显式记录，多轮精化轨迹可巡检；Workspace 私域访问留痕，区分公域与私域证据来源；长任务上下文保持使跨轮证据链可追溯。
- **Perplexity**：迭代检索轨迹记录每次策略调整的依据，新发现洞察与后续检索的因果链可观测；混合模型路由决策留痕，便于对比不同模型在同一子任务上的表现。
- **ManuSearch**：三智能体协作全程透明，每次子查询生成、检索执行、证据抽取均有结构化日志；开源实现使 trace 可完整落盘与回放，支持自定义验证闸门接入。

该族平台的 trace 核心是**引用完整性与证据链可验证性**，与 DeepResearch Bench 的 FACT 维度直接对应。

## 4. Flywheel 机制

- **单任务内飞轮**：规划 → 检索 → 阅读 → 综合 → 缺口识别 → 再规划构成任务内闭环，每轮新证据精化后续检索策略，报告质量随轮次提升。
- **跨任务飞轮**：Perplexity 的混合模型路由根据历史子任务表现持续优化模型选择；Gemini 的 Workspace 记忆使跨任务私域知识沉淀；ManuSearch 开源社区通过 issue/PR 持续贡献新 agent 与检索策略，形成与 DeepModeling 类似的开放供给循环。
- **评估驱动飞轮**：Humanity's Last Exam 等基准显示 Perplexity Deep Research 达 21.1% 准确率，显著高于 Gemini Thinking / o3-mini / o1 / DeepSeek-R1 等基线，该信号回流至检索与路由策略优化；ManuSearch 在 EMNLP Findings 论文中以可复现实验验证模块化增益，社区复现信号持续精化三智能体分工。
- **平台演进飞轮**：OpenAI 从纯文本浏览器扩展至视觉交互浏览器，Gemini 从公域检索扩展至 Workspace 私域，体现能力注册表随使用信号横向扩展的演进路径，与 Bohrium 的 living infrastructure 理念一致。

## 5. 智能体架构与工具链

- **OpenAI**：o3 推理模型 + RL 训练 + ReAct agent loop + 双浏览器工具链；控制器负责长链推理与工具协调，执行层负责网页交互与文档解析。
- **Gemini**：Gemini 3 统一驱动，agentic 能力原生集成，工具链覆盖搜索、文档理解、Workspace 连接器。
- **Perplexity**：多模型协作架构，任务路由器 + 迭代检索引擎 + 推理综合器，强调模型能力与任务类型的精细匹配。
- **ManuSearch**：三智能体协作框架，Solution Planning / Internet Search / Webpage Reading 各司其职，通过显式消息传递协作；支持接入任意 LLM (GPT、Claude、开源模型) 与搜索引擎，代码库提供完整可运行示例与评估脚本。

## 6. 度量体系

- **OpenAI/Gemini/Perplexity 官方与第三方对比**：Humanity's Last Exam 综合基准上 Perplexity Deep Research 21.1%，高于多数前沿模型；DeepResearch Bench 上 Gemini-2.5-Pro Deep Research RACE Overall 48.88 领先，OpenAI Deep Research 46.98 紧随，Perplexity Deep Research 42.25 (详见 19-benchmarks-eval.md)。
- **FACT 维度**：Perplexity Deep Research 引用准确率 90.24% 居首，Gemini-2.5-Pro Deep Research 有效引用数 111.21 显著领先，体现不同平台在信息广度与引用精度上的权衡。
- **ManuSearch**：论文在多跳问答与长文档综合任务上验证透明多智能体相对单体检索的增益，强调可解释性与可扩展性作为附加度量。

## 7. 核心可借鉴点 → OMP 映射

| Deep Research 模式 | OMP 对应构件 | 移植建议 |
|---|---|---|
| ReAct 规划-执行-观测闭环 | `task` 内 ReAct 循环 + `hub` 事件总线 | 每个深度研究 `task` 内实现 plan-act-observe 循环，跨轮证据通过 `hub` 共享，支持多 task 并发协作 |
| 双浏览器 (文本 + 视觉) | `task` 工具分面 | 将检索工具按文本抽取与交互式浏览分面注册，调度器据任务类型选择，降低单工具复杂度 |
| 混合模型路由 | `task` 模型路由表 | 维护模型能力注册表 (概括/判读/推理分工)，据子任务类型动态选择模型，类似 Perplexity 策略 |
| 三智能体透明协作 (ManuSearch) | `task` 多智能体分解 | 将深度研究拆为 Planning / Search / Reading 三个子 `task`，通过 `hub` 消息协作，每个子任务产物独立落盘与评估 |
| Workspace 私域融合 (Gemini) | `channels/` 私域知识库 | 将用户私域文档与公开检索同等注册为 capability，检索时统一路由，实现公私域证据融合 |
| 引用完整性为一等 trace | `eval` FACT 校验 | `eval` 阶段自动执行 FACT 评估：有效引用数与引用准确率双指标，引用不可验证直接扣分 |

## 8. 潜在坑

- **闭源黑盒**：OpenAI/Gemini/Perplexity 核心模型与检索链路不开放，trace 仅展示摘要，难以深度审计与定制；成本与延迟随检索轮次线性增长，长任务易超预算。
- **检索偏差**：搜索引擎排序偏差会传导至报告，缺乏对抗性检索验证时易产生系统性偏见；视觉浏览器对动态网页的鲁棒性仍有限。
- **混合路由复杂性**：Perplexity 式多模型路由增加调度复杂度，路由错误会放大至报告质量，需配套路由准确率监控。
- **ManuSearch 工程门槛**：三智能体协作虽透明，协调开销与消息一致性保障需自行实现；对 LLM 推理能力依赖度高，弱模型下子查询质量下降明显。
- **评估单一化风险**：Humanity's Last Exam 等单一基准易被针对性优化，需结合 RACE/FACT 多维评估避免过拟合。

## 参考

- OpenAI Introducing Deep Research https://openai.com/index/introducing-deep-research
- Gemini Deep Research https://gemini.google/overview/deep-research
- Perplexity Introducing Deep Research https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research (Humanity's Last Exam 21.1%)
- ManuSearch: Democratizing Deep Search, arXiv:2505.18105 — https://github.com/RUCAIBox/ManuSearch / https://aclanthology.org/2025.findings-emnlp.130
- ByteByteGo Deep Research 架构解析 https://blog.bytebytego.com/p/how-openai-gemini-and-claude-use
- DeepResearch Bench  leaderboard  https://deepresearch-bench.github.io (RACE/FACT 结果)
