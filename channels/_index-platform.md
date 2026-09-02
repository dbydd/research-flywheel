# 平台型与基础设施系统汇总 (16-19)

> 覆盖 Bohrium+SciMaster+DeepModeling、Agent Laboratory+AgentRxiv+Claw AI Lab、Deep Research 平台族、PaperBench+DeepResearch Bench+RE-Bench+EpiBench 四组基础设施。每组经 web_search + arXiv/官网/GitHub read 验证，关键事实带 URL。

## 文件索引

| # | 文件 | 系统 | 一句话定位 |
|---|------|------|-----------|
| 16 | `16-bohrium-scimaster.md` | DP Bohrium + SciMaster + DeepModeling + SciencePedia + Innovator | 五层平台栈 + 三域可执行服务 + 能力注册表的 Science-as-a-Service 基础设施 |
| 17 | `17-agent-laboratory-agentrxiv.md` | Agent Laboratory + AgentRxiv + Claw AI Lab | 三阶段串行 + 跨 Lab 累积 + 五层金字塔仪表盘的协作式研究平台 |
| 18 | `18-deep-research-platforms.md` | OpenAI / Gemini / Perplexity Deep Research + ManuSearch | 迭代检索推理闭环 + 双浏览器 + 混合模型路由的深度研究平台族 |
| 19 | `19-benchmarks-eval.md` | PaperBench + DeepResearch Bench I/II + RE-Bench + EpiBench | 复制 + 调研 + 工程三维覆盖的评估基础设施，rubric 与裁判双层沉淀 |

## 对比总表

| 维度 | 16 Bohrium+SciMaster | 17 Lab/Rxiv/Claw | 18 Deep Research 族 | 19 Benchmarks |
|------|----------------------|-----------------|---------------------|---------------|
| **机构 / 时间** | 深势科技 + AI4S Institute + 交大/北大/中科院, 2025-12 arXiv:2512.20469, https://www.bohrium.com | JHU (Schmidgall) 2025-01 arXiv:2501.04227 + 2025-03 arXiv:2503.18102 + NTU/A*STAR/Moxin 2025-05 arXiv:2605.22662 | OpenAI 2025-02 + Gemini 2024-12 + Perplexity 2025-02 + RUC ManuSearch 2025-05 arXiv:2505.18105 | OpenAI PaperBench 2025-04 + 中科大 Bench I 2025-06 / Bench II 2026-01 + METR RE-Bench 2024-11 |
| **开源状态** | 部分开源：DeepModeling 全开源 LGPL-3.0，Bohr SDK 开源，Bohrium/SciMaster 托管计费 | 完全开源 MIT：Laboratory 5.8k⭐ + Rxiv 同库 + Claw Lab + claw-code Rust | 闭源托管 (OpenAI/Gemini/Perplexity) + ManuSearch MIT 开源 | 全部开源：PaperBench + Bench I/II + RE-Bench + EpiBench |
| **循环形态** | 平台级闭环：能力调度 → 执行 → 使用信号与验证证据回流 → 接口与知识迭代 | 三阶段串行 + 跨 Lab 检索复用 + 五层跨层反馈 + 仪表盘可控迭代 | 单任务迭检索推理闭环：规划→检索→阅读→综合→缺口识别→再规划，多轮自适应 | 评估即锚点：任务定义→执行→细粒度 rubric/裁判评分→人类一致性校验→信号回流 |
| **平台分层要点** | 5 层：裸资产→Bohrium 三域基座→科学智能基座→SciMaster 编排→治理计费 | 3 阶段流水线→Rxiv 累积层→Claw 五层金字塔 + Dashboard/Harness 横切 | o3/Gemini 3 推理层→双浏览器/Workspace/混合路由工具层→迭代检索循环→报告合成层 | 沙盒执行层→rubric 任务层→裁判评分层→榜单飞轮层 + 人类基线横切 |
| **智能体架构** | Innovator 通用基座 + SciencePedia 长思维链 + DeepModeling 引擎族 + SciMaster X-Master 编排 + 11 Master Agents | 角色化 PhD/Postdoc/MLE/Critic + SentenceTransformer 检索 + Claw-Code Harness 沙盒 | o3 ReAct + Gemini 3 plan-execute-refine + Perplexity 混合路由 + ManuSearch 三智能体透明协作 | 隔离执行 + LLM judge / RACE自适应加权 / FACT引用审计 / 自动客观评分 |
| **工具链** | Science Navigator 多模态解析 + Lebesgue 统一调度 + UniLabOS 实验室 OS + Bohr SDK 双模 | arXiv/HF/Python/LaTeX + state_saves 检查点 + dashboard 事件流 + Rust harness | 搜索 API + 网页抓取 + PDF/图像解析 + 视觉浏览器 + Workspace 连接器 | 离线网页语料 10k-100k/任务 + 报告 harness + HF Leaderboard + 容器化工程环境 |
| **度量** | 工作流周期数量级缩短 + 数百万执行信号 + 溯源精度与约束满足度 | MATH-500 +13.7% (Rxiv) + Claw 内部 +15.5~16.5 研究类 / +5.0 复现类 | HLE 21.1% (Perplexity) + Bench I RACE 48.88 Gemini / 46.98 OpenAI + FACT 90.24% Perplexity / 111.21 Gemini | PaperBench 21% vs 人类 41% + Bench I RACE 72.56% 一致性 + Bench II 45.40% + RE-Bench 4倍人类 (2h) |
| **核心可借鉴点** | 能力最小契约 + 三域分面 + 调度与推理分离 + 平台级 trace | 角色分工 + 论文即能力 + 沙盒 anti-fabrication + 仪表盘可观测 | 检索阅读推理闭环 + 能力分面 + 混合路由 + 引用完整性一等 trace | 作者共创 rubric + 参考驱动加权 + 引用审计 + 二值诊断矩阵 |
| **潜在坑** | 托管锁定 + 解析成本高 + 硬件耦合 + 激励未定型 | 协作开销 + 检查点膨胀 + 质量漂移 + 评估主观性 | 闭源黑盒 + 检索偏差 + 路由复杂性 + 单一基准过拟合 | 裁判偏差 + 维护成本高 + 语料时效 + 环境泄露 |

## 基础设施抽象萃取

### 平台分层

- **共性五层模型**：裸资产/语料 → 能力注册与执行基座 → 智能与知识基座 → 编排层 → 治理与评估层。Bohrium 五层栈为最完整实例，Deep Research 族与评测体系为其在文献与评估维度的投影。
- **域分面思想**：Bohrium 按 Reading/Computing/Experiment 分面，Deep Research 按文本抽取/视觉浏览/私域融合分面，评测按复制/调研/工程分面。分面降低单层复杂度，支持按约束路由。
- **推理与执行分离**：Bohrium 显式分离 Innovator 推理信号与 SciMaster 执行治理，Deep Research 分离 o3/Gemini 推理与浏览器执行，Lab/Claw 分离 Idea/Planning 与 Coding/Experiment。该分离提升可审计性。

### Capability 注册

- **最小契约**：输入输出 Schema + 可复现环境 + 执行信封 + 约束/成本/失败模式。Bohrium 提出该契约，ManuSearch 三智能体与 Bench rubric 均遵循同构契约。
- **论文与报告即能力**：AgentRxiv 将论文以 embedding 入库作为可检索能力，Bench 将 rubric 与参考报告作为注册产物。该模式支持跨任务复利。
- **版本与血缘**：Bohrium 注册表记录版本与依赖，Rxiv 记录跨 Lab 血缘，Bench 记录任务版本与裁判版本。血缘支持回放与回归检测。

### Trace 治理

- **三级溯源**：Bohrium 要求 source → section → claim 三级链接，FACT 审计引用准确率，RACE 相对参考报告评分。trace 贯穿检索、执行、综合全链路。
- **可回放可对比**：Bohrium 每次调用记录执行信封与成本，Claw Harness 落盘完整执行日志，Bench 逐条 rubric 评分。三者均支持跨 run 对比与失败定位。
- **沙盒与防伪**：Claw 注入只读 controller 做时间/指标/NaN 检测与 smoke test，RE-Bench 容器化隔离，ManuSearch 结构化日志支持自定义闸门。

### Flywheel 机制

- **使用信号回流**：Bohrium 记录调用频次与失败模式，Deep Research 根据检索效果调整策略，Bench 根据分数差距驱动平台改进。
- **知识沉淀**：DeepModeling 开源供给 + SciencePedia 长思维链 + AgentRxiv 累积 + Bench rubric 增量扩展构成四条知识飞轮，相互叠加。
- **评估驱动**：PaperBench 21% vs 41% 人类差距、Bench I/II 召回短板、RE-Bench 1.3 分未达成均作为定向改进信号，形成制衡飞轮。

## OMP 映射总表 (哪些模式可直接映射到 task/eval/hub/schedule_prompt)

| 基础设施模式 | OMP 构件 | 映射说明 | 来源文件 |
|-------------|----------|----------|----------|
| 能力最小契约注册 | `task` 能力注册 + `skill://` 规范 | 每个工具/模型/工作流定义 inputs/outputs/env/constraints/cost/failure 契约，写入 task Contract 段，作为 trace 关联键 | 16, 18 |
| 三域分面与工具分面 | `task` 角色分工 + `hub` 路由 | 按 Reading/Computing/Experiment 或文本/视觉/私域分面注册，调度器据任务类型路由 | 16, 18 |
| 推理与执行治理分离 | 推理模型 vs `hub`/`eval` | 推理侧产出计划，执行与审计交由 hub/eval，避免既当裁判又当选手 | 16 |
| 角色化分工与多智能体协作 | `task` 角色模板 + `hub` 事件总线 | 定义 PhD/Postdoc/MLE/Critic 或 Planning/Search/Reading 角色，按阶段路由，跨任务通过 hub 协作 | 17, 18 |
| 论文与报告即能力 + 向量检索 | `channels/` 知识库 + 向量检索 | 已沉淀 channels 以 embedding 入库，新任务先做相似度检索，命中即注入上下文 | 17 |
| 迭代检索推理闭环 | `task` 内 ReAct 循环 + `hub` 共享 | 单任务内 plan-act-observe 多轮迭代，跨轮证据经 hub 共享，支持多 task 并发 | 18 |
| 混合模型路由 | `task` 模型路由表 | 维护模型在概括/判读/推理维度的适配度，按子任务动态分发 | 18 |
| 私域与公域融合 | `channels/` 私域能力注册 | 私域文档与公开检索同等注册，统一路由 | 18 |
| 统一调度与多租户治理 | `hub` + `schedule_prompt` | hub 实现资源感知与优先级队列，schedule_prompt 承担异步长作业与重试退避 | 16 |
| 仪表盘可观测与回滚 | `hub` 仪表盘 + `schedule_prompt` 巡检 | hub 暴露事件流与 artifact 巡检，schedule_prompt 定期扫描失败任务并提供回滚入口 | 17 |
| 沙盒执行与防伪 | `eval` 沙盒 + 伪造检测 | 隔离 workspace 执行，注入只读 controller 做时间/指标/NaN 与 smoke test | 17, 19 |
| 细粒度溯源与引用审计 | `eval` 三级引用校验 + FACT 双指标 | 要求 source→section→claim 引用，自动统计有效引用数与准确率，不可验证扣分 | 16, 18, 19 |
| 作者共创 rubric 层级分解 | `eval` rubric 注册 | 为 channels 定义理解/复现/验证三级 rubric，与任务作者共创 | 19 |
| 参考驱动自适应加权评分 | `eval` 报告质量评估 | 引入高质量参考报告，相对评分并按维度动态加权 | 19 |
| 二值专家 rubric 诊断矩阵 | `eval` 细粒度诊断 | 对关键任务引入二值 rubric，形成召回/分析/呈现三维诊断 | 19 |
| LLM 裁判人类一致性标定 | `eval` 裁判选型 | 对裁判模型做 PAR/OPC/FAP/FAS 标定，兼顾一致性与成本 | 19 |
| 人类基线对照 | `eval` 基线管理 | 维护人类 8 小时基线分布，同图展示模型分数 | 19 |
| 榜单与回归检测 | `hub` leaderboard + `schedule_prompt` 定时重跑 | hub 暴露榜单视图，schedule_prompt 定期重跑核心任务做回归检测 | 19 |
| 社区飞轮与激励 | `channels/_index-*.md` + 贡献度核算 | 以被引用次数与验证通过率作为贡献信号，对接后续激励 | 16, 17 |

## 快速决策清单

1. **必做 (高 ROI)**：能力最小契约 + 细粒度溯源 + 分阶段 task 与 hub 路由 + eval 引用审计 + 榜单回归。五项覆盖 Bohrium、ManuSearch、Bench 三方共识，工程成本可控。
2. **次优先**：向量检索复利 (AgentRxiv) + 沙盒防伪 (Claw) + 二值诊断矩阵 (Bench II) + 模型路由表 (Perplexity)。四项依赖前五项落地后增量接入。
3. **延后验证**：私域融合 + 激励对齐 + 多租户计费。三项涉及权限与经济模型，需在 trace 与评估稳定后展开。

## 来源清单

- Zhang et al., Bohrium + SciMaster, arXiv:2512.20469 — https://arxiv.org/html/2512.20469v1
- Bohrium https://www.bohrium.com / SciMaster https://scimaster.bohrium.com / Bohr SDK https://github.com/dptech-corp/bohr-agent-sdk / DeepModeling https://deepmodeling.com / SciencePedia https://sciencepedia.bohrium.com
- Schmidgall et al., Agent Laboratory arXiv:2501.04227 — https://github.com/SamuelSchmidgall/AgentLaboratory
- Schmidgall & Moor, AgentRxiv arXiv:2503.18102 — https://agentrxiv.github.io
- Wu et al., Claw AI Lab arXiv:2605.22662 — https://github.com/Claw-AI-Lab/Claw-AI-Lab / https://github.com/ultraworkers/claw-code
- OpenAI Deep Research https://openai.com/index/introducing-deep-research / Gemini https://gemini.google/overview/deep-research / Perplexity https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research / ManuSearch https://github.com/RUCAIBox/ManuSearch
- PaperBench https://openai.com/index/paperbench / Du et al., DeepResearch Bench https://deepresearch-bench.github.io / https://github.com/Ayanami0730/deep_research_bench / Bench II arXiv:2601.08536 / RE-Bench https://github.com/METR/RE-Bench
