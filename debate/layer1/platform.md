# Layer 1 平台基建证据分析：可迁移设计原则（16-19）

> 来源文件：`channels/_index-platform.md`、`channels/16-bohrium-scimaster.md`、`channels/17-agent-laboratory-agentrxiv.md`、`channels/18-deep-research-platforms.md`、`channels/19-benchmarks-eval.md`
> 证据范围：Bohrium+SciMaster+DeepModeling+SciencePedia+Innovator、Agent Laboratory+AgentRxiv+Claw AI Lab、Deep Research 平台族（OpenAI/Gemini/Perplexity/ManuSearch）、PaperBench+DeepResearch Bench I/II+RE-Bench+EpiBench
> 写作约束：区分来源事实与推断，推断显式标注 [推断]

---

## 原则 1 — 能力最小契约注册表

**证据**
- 系统：DP Bohrium 能力注册表；SciMaster X-Master 调度
- 文件路径：`channels/16-bohrium-scimaster.md` §2、`channels/_index-platform.md` §基础设施抽象萃取-Capability注册
- 来源链接：Zhang et al. arXiv:2512.20469 https://arxiv.org/html/2512.20469v1 ；Bohrium https://www.bohrium.com ；Bohr SDK https://github.com/dptech-corp/bohr-agent-sdk

**来源事实**
Bohrium 将工具、模型、数据集、工作流、协作产物统一入注册表。最小契约定义为输入输出 Schema + 可复现环境 + 执行信封 + 约束/成本/失败模式声明。注册表记录版本、依赖、输入输出模式与执行信封，支持按约束路由与跨实例复用。科学代码与管线以可复现环境打包后由 Lebesgue 调度。论文披露已沉淀数百万规模执行锚定信号，覆盖成功/失败、耗时、成本、约束满足度与验证证据。

**机制**
每个可调用单元在注册时声明结构化契约，包含输入输出类型、环境快照、资源约束、成本模型、已知失败模式。调度器依据任务约束做匹配路由，执行时绑定契约版本，落盘执行信封。

**收益**
调度可解释，执行可回放，成本可核算。trace、验证、计费均以 capability ID 为关联键，支持跨运行对比与回归定位。

**失效模式**
契约粒度过粗导致路由歧义。环境快照缺失导致复现失败。成本声明失真导致预算超支。注册表膨胀后检索延迟上升。

**对 OMP/PI 工作区的启示**
在 `task` prompt Contract 段为每个工具/模型/工作流写入最小契约。`skill://` 规范承载可复用契约模板。`hub` 按契约约束做路由。`eval` 按契约校验输入输出。需配套契约版本化与淘汰机制。

---

## 原则 2 — 三域分面与工具分面注册

**证据**
- 系统：Bohrium 三域服务（Reading/Computing/Experiment）；Deep Research 双浏览器与 Workspace 分面；评测体系复制/调研/工程分面
- 文件路径：`channels/16-bohrium-scimaster.md` §1-§2、`channels/18-deep-research-platforms.md` §1-§2、`channels/_index-platform.md` §平台分层
- 来源链接：Bohrium https://www.bohrium.com ；OpenAI Deep Research https://openai.com/index/introducing-deep-research ；Gemini https://gemini.google/overview/deep-research ；Perplexity https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research

**来源事实**
Bohrium 按 Reading（Science Navigator 多模态解析）、Computing（Lebesgue 统一调度）、Experiment（UniLabOS 实验室 OS）三域分面。OpenAI 双浏览器分为文本浏览器与视觉交互浏览器。Gemini 增加 Workspace 私域连接器分面。Perplexity 按概括/判读/推理分工做模型分面。评测体系按复制/调研/工程分面组织任务与评分器。

**机制**
将能力按领域语义分面注册，分面之间接口隔离。调度器先做分面路由，再做分面内细粒度选择。分面降低单层复杂度，支持按资源与约束独立演进。

**收益**
单体 prompt 与单体调度器负载下降。分面内可独立优化工具链与成本模型。新增分面无需改动既有分面。

**失效模式**
分面边界划分不当导致跨域任务频繁跨分面协调。分面间重复注册造成一致性漂移。调度器分面误判放大至下游质量损失。

**对 OMP/PI 工作区的启示**
`task` 按 Reading/Computing/Experiment 或文本抽取/视觉浏览/私域融合分面注册。`hub` 维护分面路由表。调研类任务拆为检索、计算、验证三角色，Conductor 按分面分发。[推断] PI 工作区可将 `channels/` 私域能力与公开检索能力同表注册，统一参与路由。

---

## 原则 3 — 推理与执行治理分离

**证据**
- 系统：SciMaster X-Master vs Bohrium 执行治理；OpenAI o3 推理 vs 双浏览器执行；Lab Idea/Planning vs Coding/Experiment
- 文件路径：`channels/16-bohrium-scimaster.md` §1§5、`channels/18-deep-research-platforms.md` §1§5、`channels/_index-platform.md` §基础设施抽象萃取-平台分层
- 来源链接：arXiv:2512.20469；OpenAI https://openai.com/index/introducing-deep-research ；ByteByteGo https://blog.bytebytego.com/p/how-openai-gemini-and-claude-use

**来源事实**
Bohrium 论文明确分离 Innovator 推理信号与 SciMaster 执行治理，SciMaster 将问题编译为结构化工作流后在 Bohrium 基座执行。OpenAI 以 o3 负责 ReAct 规划，浏览器负责网页交互与文档解析。Agent Laboratory 将 Idea/Planning 与 Coding/Experiment 分阶段由不同角色承担。

**机制**
推理侧产出计划、假设、资源诉求，执行侧负责调度、鉴权、监控、核算、审计。两层之间通过结构化工作流与执行信封衔接，审计方独立于推理方。

**收益**
可审计性提升，推理偏差可在执行层被约束拦截。评估时可独立度量规划质量与执行质量。

**失效模式**
接口契约不完整导致推理侧假设在执行侧不可兑现。执行层过度约束抑制推理侧探索。分离引入额外序列化开销。

**对 OMP/PI 工作区的启示**
推理模型只产出计划与假设，执行与审计交由 `hub`/`eval` 治理。`hub` 承担鉴权与资源感知，`eval` 承担可复现性与合规校验。需定义推理-执行之间的工作流 Schema，避免自由文本传递。

---

## 原则 4 — 角色化分工与分阶段流水线

**证据**
- 系统：Agent Laboratory 角色化协作；Claw 五层金字塔；Bohrium 11 Master Agents
- 文件路径：`channels/17-agent-laboratory-agentrxiv.md` §1§2§5、`channels/16-bohrium-scimaster.md` §4
- 来源链接：Schmidgall et al. arXiv:2501.04227 https://github.com/SamuelSchmidgall/AgentLaboratory ；Wu et al. arXiv:2605.22662 https://github.com/Claw-AI-Lab/Claw-AI-Lab ；arXiv:2512.20469

**来源事实**
Agent Laboratory 定义 PhD / Postdoc / MLEngineer / Professor 角色，每角色绑定职责与 prompt 模板，按 Literature Review → Experimentation → Report Writing 三阶段调度。Claw 重构为 Idea → Planning → Coding → Experiment → Writing 五层金字塔，支持下游异常回跳上游重修。Bohrium 展示 11 个 Master Agent 在阅读/计算/实验闭环上实现端到端周期数量级缩短。

**机制**
将长周期研究分解为阶段，每阶段绑定角色职责与产物契约。阶段产物落盘为可复用 artifact，阶段间通过结构化接口传递。异常触发跨层反馈而非线性重试。

**收益**
职责清晰，prompt 过载下降，产物可独立评估与复用。跨层反馈支持早期纠偏，减少无效实验投入。

**失效模式**
角色协作开销随阶段线性增长。阶段接口过窄导致信息丢失。回跳机制无收敛控制导致震荡。

**对 OMP/PI 工作区的启示**
为 `task` 定义角色枚举与职责契约，Conductor 按阶段路由至对应角色 prompt。将长研究拆为三至五阶段 `task`，每阶段产物写入 `channels/` 并在 `hub` 登记检查点。用 `task` DAG 描述 Idea→Planning→Coding→Experiment→Writing 依赖，层间失败通过 `hub` 事件回跳。[推断] 需配套阶段级预算与重试上限，避免协作开销失控。

---

## 原则 5 — 论文与报告即能力，向量检索驱动跨任务复利

**证据**
- 系统：AgentRxiv 预印本服务器；ManuSearch 透明协作；DeepModeling 开源供给
- 文件路径：`channels/17-agent-laboratory-agentrxiv.md` §1§2§4、`channels/18-deep-research-platforms.md` §4、`channels/16-bohrium-scimaster.md` §4
- 来源链接：Schmidgall & Moor arXiv:2503.18102 https://agentrxiv.github.io ；RUCAIBox ManuSearch https://github.com/RUCAIBox/ManuSearch ；DeepModeling https://deepmodeling.com

**来源事实**
AgentRxiv 以 SentenceTransformer 编码论文，相似度搜索返回相关工作，下游 Lab 将检索结果作为 Literature Review 输入。论文报告 MATH-500 上协作相对隔离基线提升 13.7%。ManuSearch 三智能体协作全程结构化日志可检索。DeepModeling 社区持续贡献引擎与工作流，在 Bohrium 治理环境中被调用与比较。

**机制**
将论文、报告、工作流沉淀为 embedding 可检索的能力单元。新任务启动时先做相似度检索，命中则注入上下文或作为起点二次改进，形成检索-复用-再发布循环。

**收益**
跨任务知识复利，已验证方法快速扩散。检索即组合，降低重复探索成本。

**失效模式**
低质内容污染检索库并放大后续错误。相似度排序掩盖质量差异。embedding 漂移导致召回稳定性下降。检索结果注入过长导致上下文稀释。

**对 OMP/PI 工作区的启示**
将 `channels/*.md` 以 embedding 入库，新任务 Literature Review 阶段前置向量检索。检索 API 作为 Lab 文献工具暴露，命中结果以结构化上下文注入。需配套质量闸门与引用次数/验证通过率加权，避免相似度单一排序。[推断] PI 工作区可为检索结果增加版本与血缘标注，支持复现链路追溯。

---

## 原则 6 — 迭代检索推理闭环与缺口驱动再规划

**证据**
- 系统：OpenAI/Gemini/Perplexity 迭代检索循环；ManuSearch 三智能体闭环；Gemini plan-execute-refine
- 文件路径：`channels/18-deep-research-platforms.md` §1§4、`channels/_index-platform.md` §对比总表-循环形态
- 来源链接：OpenAI https://openai.com/index/introducing-deep-research ；Gemini https://gemini.google/overview/deep-research ；ManuSearch arXiv:2505.18105 https://github.com/RUCAIBox/ManuSearch

**来源事实**
四平台共同呈现规划 → 检索 → 阅读 → 综合 → 缺口识别 → 再规划的多轮自适应闭环。ManuSearch 将闭环显式拆为 Solution Planning / Internet Search / Webpage Reading 三智能体。Gemini 采用重复 plan-execute-refine 并保持长任务上下文。Perplexity 基于新发现洞察持续调整检索策略。Humanity's Last Exam 上 Perplexity Deep Research 达到 21.1%。

**机制**
单任务内维护 ReAct 循环，综合阶段显式识别证据缺口，缺口驱动下一轮子查询生成。每轮新证据精化后续检索策略，直至满足停止条件后合成报告。

**收益**
报告覆盖度与深度随轮次提升，证据链完整性可度量。缺口显式化减少遗漏。

**失效模式**
检索偏差传导至报告，缺乏对抗性检索验证时产生系统性偏见。轮次无预算控制导致成本线性增长。弱模型下子查询质量下降，闭环收益衰减。

**对 OMP/PI 工作区的启示**
每个深度研究 `task` 内实现 plan-act-observe 循环，跨轮证据通过 `hub` 共享。ManuSearch 三智能体模式可拆为 Planning / Search / Reading 三个子 `task`，通过 `hub` 消息协作，产物独立落盘与评估。需设定轮次上限与缺口收敛阈值。[推断] PI 工作区可将缺口识别作为独立评估维度纳入 rubric。

---

## 原则 7 — 混合模型路由与能力分面调度

**证据**
- 系统：Perplexity 混合多模型路由；ManuSearch 任意 LLM 后端；Agent Laboratory 多后端插拔
- 文件路径：`channels/18-deep-research-platforms.md` §1§2§5、`channels/17-agent-laboratory-agentrxiv.md` §5
- 来源链接：Perplexity https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research ；ManuSearch https://github.com/RUCAIBox/ManuSearch ；AgentLaboratory https://github.com/SamuelSchmidgall/AgentLaboratory

**来源事实**
Perplexity 按子任务动态选择最适配模型，注册表记录模型在概括、检索结果判读、推理等维度的适配度。ManuSearch 支持接入任意 LLM 与搜索引擎实现，三智能体可独立替换后端。Agent Laboratory 支持 OpenAI o1/o3-mini/gpt-4o、DeepSeek-V3 可插拔。

**机制**
维护模型能力注册表，按子任务类型做动态路由。路由决策留痕，便于对比不同模型在同一子任务上的表现并持续优化选择策略。

**收益**
任务与模型能力精细匹配，综合性价比提升。模型演进可增量接入，无需重构主流程。

**失效模式**
路由错误放大至报告质量。路由表陈旧导致次优选择。路由复杂度增加调度延迟与可解释性负担。

**对 OMP/PI 工作区的启示**
在 `task` 侧维护模型路由表，按概括/判读/推理分工分发。路由决策写入 trace，支持离线对比。ManuSearch 模式提供参考：每个 agent 暴露清晰接口，外部可替换实现，新增 agent 类型无需改动主循环。[推断] 需配套路由准确率监控与回退策略，避免路由失败导致任务整体失败。

---

## 原则 8 — 三级溯源与引用审计

**证据**
- 系统：Bohrium Science Navigator 溯源链；Deep Research 引用完整性；FACT 审计框架
- 文件路径：`channels/16-bohrium-scimaster.md` §3、`channels/18-deep-research-platforms.md` §3、`channels/19-benchmarks-eval.md` §3
- 来源链接：arXiv:2512.20469；Du et al. DeepResearch Bench https://deepresearch-bench.github.io ；arXiv:2506.11763

**来源事实**
Bohrium 要求检索片段/抽取事实/装配工作流元素显式链接回源文档章节与引用上下文，支持 provenance-preserving 复现检查。Deep Research 平台每份报告附数百来源引用，支持溯源验证。DeepResearch Bench FACT 框架审计有效引用数与引用准确率，Perplexity Deep Research 引用准确率 90.24% 居首，Gemini-2.5-Pro Deep Research 有效引用数 111.21 领先。Bench II 呈现分数普遍高于召回分数，揭示召回为短板。

**机制**
要求 source → section → claim 三级链接，执行时记录引用链路，评估时自动统计有效引用数与引用准确率，不可验证引用直接扣分。

**收益**
证据链可验证，研究结论可复现。引用审计区分信息广度与溯源精度，避免堆引用数而忽略精度的偏科。

**失效模式**
溯源粒度过细导致标注成本激增。引用可达性随时间衰减，离线语料与线上复测背离。自动化引用校验误判导致误扣分。

**对 OMP/PI 工作区的启示**
每个 `channels/*.md` 要求三级引用，`eval` 阶段自动执行 FACT 双指标校验。`hub` 记录引用链路版本，支持跨 run 对比。需为离线语料与线上语料分别维护引用有效期。[推断] PI 工作区可将引用审计作为 Deep Research 类任务的必检闸门，不可验证直接阻断报告发布。

---

## 原则 9 — 沙盒执行与防伪闸门

**证据**
- 系统：Claw-Code Harness 沙盒；RE-Bench 容器化环境；Agent Laboratory 隔离执行
- 文件路径：`channels/17-agent-laboratory-agentrxiv.md` §2§3、`channels/19-benchmarks-eval.md` §1§5、`channels/_index-platform.md` §Trace治理-沙盒与防伪
- 来源链接：Claw-Code https://github.com/ultraworkers/claw-code ；RE-Bench https://github.com/METR/RE-Bench ；PaperBench https://github.com/openai/paperbench

**来源事实**
Claw-Code Harness 将本地代码库、数据集、checkpoint 抽象为可调度能力，注入只读 Python controller 负责时间预算、指标上报、结果固化与 NaN/Inf 检测，支持 smoke test 与 anti-fabrication 检查，执行在隔离 workspace。RE-Bench 提供 7 个容器化工程环境，每个环境提供参考解与自动评分。PaperBench 要求从论文文本出发重建完整实验管线，LLM judge 逐条 rubric 评分。

**机制**
代码与实验在隔离 workspace 执行，注入只读 controller 做时间/指标/NaN 与 smoke test 检测，结果不一致直接阻断下游报告生成。容器化保障可复现与公平对比。

**收益**
虚假指标与占位实现被自动拦截，实验结果可信度提升。隔离执行支持并发与资源配额。

**失效模式**
沙盒逃逸与文件系统/GPU 资源竞争。只读 controller 覆盖不全导致伪造漏检。容器镜像过大导致启动延迟，超长训练任务需外部调度器补充。

**对 OMP/PI 工作区的启示**
`eval` 阶段在隔离 workspace 执行代码，注入只读 controller 做时间/指标/NaN 检测与 smoke test。`hub` 承担资源感知与优先级队列，`schedule_prompt` 承担长作业重试与退避。多项目并发时需严格配额隔离。[推断] PI 工作区对高风险操作补充人审介入，与 UniLabOS 协议级约束对齐。

---

## 原则 10 — 作者共创 rubric 与参考驱动自适应加权评估

**证据**
- 系统：PaperBench 作者共创 rubric；DeepResearch Bench RACE/FACT；Bench II 二值诊断矩阵；LLM judge 人类一致性标定
- 文件路径：`channels/19-benchmarks-eval.md` §2§3§6、`channels/_index-platform.md` §评测体系分层
- 来源链接：Starace et al. arXiv:2504.01848 https://openai.com/index/paperbench ；Du et al. arXiv:2506.11763 / arXiv:2601.08536 https://deepresearch-bench.github.io

**来源事实**
PaperBench 与 20 篇 ICML 2024 Spotlight/Oral 原作者共创 8,316 项原子 rubric，层级分解为理解贡献、编写完整代码库、复现实验与结果匹配。DeepResearch Bench I 引入 RACE 参考驱动自适应准则与动态加权，相对高质量参考报告评分，人类一致性实验显示 RACE Full 整体 72.56% 显著高于 vanilla prompt 60.46%，PAR 71.33% 超过人类互一致 68.44%，OPC 99.54%。Bench II 扩展至 132 任务与 9,430 条二值专家 rubric，覆盖召回/分析/呈现三维度，GPT-o3 DR 整体 45.40%（召回 39.98 / 分析 49.85 / 呈现 89.16）。RE-Bench 提供 71 人次人类 8 小时基线，Claude 3.5 Sonnet 在 2 小时预算下达到约 4 倍人类分数。

**机制**
rubric 与任务作者共创确保真实性与可客观判分。引入高质量参考报告做相对评分，按维度动态加权。对关键任务增加二值 rubric 形成诊断矩阵，定位召回/分析/呈现短板。裁判模型做 PAR/OPC/FAP/FAS 标定，兼顾一致性与成本。

**收益**
评估可解释，短板可定位，分数区分度提升。人类基线对照避免分数虚高，榜单与回归检测驱动平台迭代。

**失效模式**
rubric 维护成本高，新增任务需原作者协同。LLM judge 与被评模型同源时存在偏好偏差。离线语料时效导致线上复测背离。针对单一指标优化产生偏科。

**对 OMP/PI 工作区的启示**
为 `channels/*.md` 定义理解/复现/验证三级 rubric，与任务作者共创后在 `eval` 注册。引入参考报告做 RACE 式相对评分，按维度动态加权。`eval` 自动执行 FACT 双指标与二值诊断矩阵。`eval` 裁判选型参考 Bench I 方法做一致性与成本标定。为核心任务维护人类 8 小时基线分布，模型分数与基线同图展示。[推断] PI 工作区可将 rubric 版本与裁判版本一并写入 trace，支撑跨版本回归检测。

---

## 领域边界

**边界 1 — 真实实验硬件与事务安全边界**
Bohrium UniLabOS 的机器人/反应器/表征仪器虚拟化依赖真实硬件抽象与协议级约束，纯软件环境复刻虚假可执行性增益有限。OMP/PI 为软件工作区时，实验域能力注册需标注硬件依赖等级，避免将不可兑现的实验协议纳入调度。[事实依据：`channels/16-bohrium-scimaster.md` §1 Experiment-UniLabOS §8 潜在坑]

**边界 2 — 私域融合与计费激励的治理边界**
Bohrium 的按量计费与社区激励仍在探索，Gemini Workspace 私域融合涉及权限与隐私，AgentRxiv 质量漂移风险随开放供给放大。OMP/PI 在 trace 与评估稳定前，私域融合、多租户计费、贡献度激励三项需延后验证，优先落地契约、溯源、评估三件套。[事实依据：`channels/16-bohrium-scimaster.md` §4§8、`channels/18-deep-research-platforms.md` §8、`channels/17-agent-laboratory-agentrxiv.md` §8]

**边界 3 — 自动化评估的适用性边界**
PaperBench 复制任务人类 PhD 41% 显著高于最强 agent 21%，Bench II 召回显著低于呈现，RE-Bench 1.3 分目标未达成，三者表明长周期研发与信息召回为当前瓶颈。作者共创 rubric 与 LLM judge 依赖高质量参考与人类一致性标定，在高度开放、缺乏参考答案的探索性任务上适用性下降，评估本身需评估。[事实依据：`channels/19-benchmarks-eval.md` §3§4§6]

---

## 来源清单

- Zhang et al., Bohrium + SciMaster, arXiv:2512.20469 https://arxiv.org/html/2512.20469v1
- Bohrium https://www.bohrium.com / SciMaster https://scimaster.bohrium.com / Bohr SDK https://github.com/dptech-corp/bohr-agent-sdk / DeepModeling https://deepmodeling.com / SciencePedia https://sciencepedia.bohrium.com
- Schmidgall et al., Agent Laboratory, arXiv:2501.04227 https://github.com/SamuelSchmidgall/AgentLaboratory
- Schmidgall & Moor, AgentRxiv, arXiv:2503.18102 https://agentrxiv.github.io
- Wu et al., Claw AI Lab, arXiv:2605.22662 https://github.com/Claw-AI-Lab/Claw-AI-Lab / Claw-Code https://github.com/ultraworkers/claw-code
- OpenAI Deep Research https://openai.com/index/introducing-deep-research / Gemini https://gemini.google/overview/deep-research / Perplexity https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research / ManuSearch arXiv:2505.18105 https://github.com/RUCAIBox/ManuSearch
- PaperBench arXiv:2504.01848 https://openai.com/index/paperbench / DeepResearch Bench arXiv:2506.11763 https://deepresearch-bench.github.io / Bench II arXiv:2601.08536 https://agentresearchlab.com/benchmarks/deepresearch-bench-ii/ / RE-Bench arXiv:2411.15114 https://github.com/METR/RE-Bench / EpiBench arXiv:2604.05557
