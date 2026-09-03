# 生物医学自主科研系统可迁移设计原则（Layer 1 证据分析）

> 范围：channels/_index-biomed.md、06-stanford-virtual-lab.md、07-stanford-biomni.md、08-google-co-scientist.md、09-futurehouse-robin.md、10-txagent-biomed.md
> 产出要求：8-12 条可迁移原则，每条含证据、机制、收益、失效模式、OMP/PI 启示，区分来源事实与推断。末尾 3 条领域边界。只新增本文件与必要目录。

---

## 原则 01：双层会议抽象（Team Meeting 定策略 + Individual Meeting 隔离执行）

- **证据**：Virtual Lab 实现外层 Team Meeting 统筹策略与内层 Individual Meeting 独立执行，计算-湿实验大闭环完成 92 个纳米抗体设计，94% 时间在工具计算，数周完成传统 6-12 月周期。来源事实见 `channels/06-stanford-virtual-lab.md`（外层 Team Meeting 循环、内层 Individual Meeting 循环、计算-湿实验大闭环）与 `_index-biomed.md` 表格行 06。溯源链接：bioRxiv 2024.11.11.623004、Chan Zuckerberg Biohub 报道、Stanford HAI 解读。
- **机制**：PI Agent 召集全体专家做策略对齐，产出突变空间与 pipeline 步骤；专家在隔离上下文异步执行 ESM 打分、AlphaFold 预测、Rosetta 精修；归档后回 Team Meeting 汇总；人类仅在分叉点给出 high-level 反馈。
- **收益**：策略与执行解耦降低上下文污染，支持并行扩展，策略可追溯，执行可复算。来源事实：单轮计算迭代约数小时，94% 时间在工具调用。
- **失效模式**：多轮后角色 prompt 漂移导致专家人设弱化；Team Meeting 同步成本随议程膨胀上升；湿实验回灌延迟导致策略空转。
- **对 OMP/PI 启示**：OMP Supervisor 复用 PI 议程驱动模式，worker 通过 `hub` 接收分解任务；`local://virtual-lab/meeting-{n}.md` 持久化会议纪要支持断点续跑；`WATCHDOG.yml` 定义 human-gate 阈值控制介入频率；模板落位 `template/virtual-lab-pi.md`。
- **事实与推断区分**：[事实] 双层会议形态、92 设计与时长、94% 工具耗时、角色构成。[推断] 映射到 OMP hub + local:// 的断点续跑与阈值门控收益属于跨系统迁移推断，来源文件描述为可实现机制，未在 Virtual Lab 原论文验证 OMP 形态。

## 原则 02：生成-批判对偶（PI + Critic 双角色）

- **证据**：Virtual Lab 配置独立 Critic Agent 做全流程挑错与证伪，每轮产出 critique 阻塞下一轮；Co-Scientist 设置 Reflection 与 Meta-review 双层评审。来源事实见 `channels/06-stanford-virtual-lab.md` Critic 职责与架构要点、`channels/08-google-co-scientist.md` Reflection/Meta-review 行。
- **机制**：Critic 与主 worker 共享工具集，prompt 视角为证伪；对候选序列、结构分数、结合界面提出反例；PI 裁决是否进入下一轮或追加约束。
- **收益**：降低幻觉突变进入湿实验的概率，提升鲁棒性；形成生成与批判的闭环增益。来源事实：Virtual Lab 报告功能性比例高于随机突变基线。
- **失效模式**：Critic 过度保守导致召回率下降；对抗 prompt 退化为附和；评审成本随候选规模线性增长。
- **对 OMP/PI 启示**：OMP 中将 Critic 设为独立子智能体，拥有相同 tool 白名单与独立 prompt，产出 `critique.md` 作为下一轮准入条件；PI 与 Critic 的通过信号写入 `hub` 消息，缺一不可进入执行层；该对偶适用于高成本湿实验门前过滤。
- **事实与推断区分**：[事实] Critic 存在与产出物形态、Reflection 评审步骤。[推断] OMP 中阻塞式准入与通过信号设计为迁移推断。

## 原则 03：工具链声明式封装（确定性 workflow 承载重计算）

- **证据**：Virtual Lab 将 ESM-AlphaFold-Multimer-Rosetta 串成声明式 pipeline，Agent 只做参数与阈值决策；Robin 将 RPE 吞噬测定与 RNA-seq 管线模板化由 Finch 调用。来源事实见 `channels/06-stanford-virtual-lab.md` 工具链节、`channels/09-futurehouse-robin.md` 实验设计与分析节。
- **机制**：重计算封装为输入序列输出分数与结构的确定性 tool，Agent 通过结构化调用而非自由文本编排；执行层返回 pLDDT、能量、荧光强度等量化指标。
- **收益**：减少 LLM 自由编排带来的不可复现性，便于缓存、重试与审计；工具误差可度量。
- **失效模式**：工具误差累积，ESM 分数与真实结合力相关性有限，AlphaFold 对新表位预测误差大；过度依赖计算分筛掉湿实验表现优的候选。
- **对 OMP/PI 启示**：OMP 在 `tools/bio-pipeline/` 封装三件套 tool，接口统一为 JSON；实验方案与工具版本写入 `tool-call.json`；计算与湿实验分数双轨记录，支持阈值回灌校正。
- **事实与推断区分**：[事实] 三件套工具构成与调用方式、误差累积风险记载。[推断] 将误差校正描述为双轨记录与阈值回灌，属于 OMP 落地设计推断。

## 原则 04：注册表驱动 + 检索式规模化（Registry + ToolRAG）

- **证据**：Biomni 通过统一 schema 注册 150 工具、59 库、105 软件，Planner 动态发现；TxAgent 用 ToolRAG 将 211 工具选择转化为检索问题，按当前推理状态召回 Top-K。来源事实见 `channels/07-stanford-biomni.md` 工具注册表节、`channels/10-txagent-biomed.md` ToolRAG/ToolUniverse 节、`_index-biomed.md` 开源可用性行。
- **机制**：工具元数据进入单一注册表 `template/tool-registry.json`；Planner 规划前检索相关工具；TxAgent 的目标导向检索按推理 trace 排序候选，再做选择与调用。
- **收益**：新增能力无需改 Agent 核心；大规模工具集下保持高召回与可控选择空间。来源事实：Biomni 支撑数十类任务一键编排，TxAgent 在 3168 任务上达 92.1%。
- **失效模式**：工具爆炸导致检索精度下降；描述不规范导致召回失败；异构返回标准化成本高；社区贡献质量参差污染注册表。
- **对 OMP/PI 启示**：OMP 以注册表为单一真相源，叠加 ToolRAG 子智能体做 Top-K 过滤；执行前必经检索；新增工具经 ToolGen 从 API 文档自动生成接口，仅追加注册项；E2 扩展需审核门控。
- **事实与推断区分**：[事实] 150/211 工具规模、注册表与 ToolRAG 机制、92.1% 离线分数。[推断] OMP 中检索必经与 ToolGen 自动接入的组合收益为迁移推断。

## 原则 05：代码即计划（可执行计划承载执行与验证一体化）

- **证据**：Biomni 用 Python 代码表达计划，含工具调用序列与数据流，沙盒执行并捕获错误，失败自动修正重试；社区通过 E1/E2 双轨扩展。来源事实见 `channels/07-stanford-biomni.md` 规划-检索-执行-自检循环与架构表。
- **机制**：LLM Planner 产出 `plan.py` 与 `run.sh` 双产物，沙盒按序执行，输出与错误回传 LLM 评估，重试至完成或步数上限。
- **收益**：计划可执行、可回放、可定位错误；日志即审计证据。来源事实：Biomni 在 HLE 17.3%、DbQA 74.4%、SeqQA 81.9% 的度量通过该循环达成。
- **失效模式**：沙盒依赖 105 包版本冲突，环境复现成本高；代码计划对长尾任务的可读性下降；重试循环在资源受限时空耗。
- **对 OMP/PI 启示**：OMP 约束子智能体输出可执行代码产物，执行日志落 `artifact://biomni-run/{task_id}`；`hub` 协调执行与重试；`template/env-e1` 锁定依赖，`template/env-e2` 允许扩展，CI 仅对 E1 强校验。
- **事实与推断区分**：[事实] 代码即计划形态与沙盒执行、E1/E2 双轨、基准分数。[推断] OMP 中双产物约束与 artifact 分层存储为落地推断。

## 原则 06：假设谱系 + Elo 锦标赛（假设即资产，锦标赛即评估）

- **证据**：Co-Scientist 将假设作为一等对象赋予 Elo 分数与谱系，Ranking Agent 做两两 Elo 对比，Proximity 聚类去重，Evolution 对头部假设重组变异，Meta-review 指导下一轮；Elo 随 test-time compute 提升，与 GPQA Diamond 准确率正相关，专家在 11 目标上更偏好其输出。来源事实见 `channels/08-google-co-scientist.md` 循环六步与度量节、`_index-biomed.md` 行 08。
- **机制**：假设写入 `local://hypotheses/{id}.md` 含 parent_ids、Elo、实验方案；Supervisor 队列异步调度生成-反思-锦标赛-进化-元复盘；投入算力单调提升 Elo。
- **收益**：评估与生成共享基座形成自举，假设可追溯、可比较、可进化；资源投入收益可视。来源事实：Elo 与 GPQA 正相关、三类湿实验验证链路存在。
- **失效模式**：Elo 自评与真实湿实验成功率不一致，存在 Goodhart 风险；多轮进化放大早期偏差；开放文献子集覆盖不足导致新颖性虚高。
- **对 OMP/PI 启示**：OMP 实现 `template/co-scientist/elo-tournament.ts` 负责两两对比与 Elo 更新，`hub` 调度多 worker 并行打分，结果落 `channels/08-elo-board.md`；假设谱系通过 `read` 继承；将 compute budget 暴露为 `budget.total` 参数，收益曲线可视化到 `artifact://co-scientist/scaling.png`。
- **事实与推断区分**：[事实] Elo 机制、六角色、test-time scaling 正相关、Goodhart 风险记载。[推断] OMP 中异步调度与可视化落位为迁移推断。

## 原则 07：自博弈辩论提升新颖性（多视角生成分歧假设）

- **证据**：Co-Scientist 的 Generation 通过自博弈科学辩论批量产生分歧假设，Reflection 过滤不可行假设；该组合在专家盲评中提升新颖性偏好。来源事实见 `channels/08-google-co-scientist.md` 循环步骤 2、核心可借鉴点 3、潜在坑小样本评估。
- **机制**：为 Generation 配置正反方双 Agent prompt，产出 debate 记录，Reflection 只放行分歧度高且可证伪的假设进入锦标赛。
- **收益**：超越单一 LLM 采样的多样性，扩大假设覆盖。来源事实：自动化 Elo 超越其他 SOTA agentic 模型。
- **失效模式**：辩论产生看似新颖但不可证伪的假设；评估样本小导致统计效力有限；辩论轮次增加成本而收益递减。
- **对 OMP/PI 启示**：OMP 为 Generation 配置正反方 prompt，产出 `debate-{round}.md`；Reflection 设分歧度阈值；不可证伪假设在门控层拦截，不进入实验设计。
- **事实与推断区分**：[事实] 自博弈辩论步骤与新颖性提升观察。[推断] 分歧度阈值门控与不可证伪拦截为落地推断。

## 原则 08：重定位优先 + 活数据源锚定

- **证据**：Robin 从 FDA 已批准分子库出发筛选 ripasudil，实现 RPE 吞噬 1.9x 与 ABCA1 3x，全流程约 10 周；TxAgent 对接 FDA 全量与 Open Targets 等持续更新源；Biomni 接入 59 个数据库与 PubMed。来源事实见 `channels/09-futurehouse-robin.md` 候选筛选与工具节、`channels/10-txagent-biomed.md` 211 工具与活数据源节、`_index-biomed.md` 重定位优先策略。
- **机制**：首轮验证在已批准库内搜索，降低合成与安全性验证成本；活数据源通过定时拉取保持新鲜，检索模块在规划前与规划中双次查询。
- **收益**：首轮验证成本与周期显著降低，假设到体外验证链路可在周级闭环。来源事实：Robin 10 周完成端到端，ether0 与 PaperQA2 为开放锚点。
- **失效模式**：重定位天花板明显，难以覆盖全新靶点；活数据源授权与异构标准化复杂；开放获取文献子集导致长尾知识缺口。
- **对 OMP/PI 启示**：OMP 在 `template/tool-registry.json` 首批注册 FDA 已批准库与 Open Targets，`channels/09-*` 默认先筛该库再扩展；配置 `schedule_prompt` 定时拉取更新 `vault://biomed/fda/` 与 `vault://biomed/opentargets/`；ether0 接入 `tools/ether0/` 作为 SMILES 推理共享锚点。
- **事实与推断区分**：[事实] 重定位候选与生物学指标、活数据源对接、开放锚点存在性。[推断] 首轮默认重定位的成本收益排序属于策略推断。

## 原则 09：显性推理 trace + Finish 门控（可审计的多步证据链）

- **证据**：TxAgent 每步先产生推理陈述明确子目标与所需证据类型，再经 ToolRAG 检索与调用，证据链持久化，Finish 显式终止；Biomni 与 Virtual Lab 也保留结构化会议纪要与自检记录。来源事实见 `channels/10-txagent-biomed.md` 五步循环、`channels/07-stanford-biomni.md` 检索与执行解耦。
- **机制**：每轮输出 `reasoning.md` 与 `tool-call.json` 双产物，`local://txagent/trace-{step}.md` 持久化；证据覆盖度未达阈值自动追加推理轮次，仅达标允许调用 Finish。
- **收益**：证据链可追溯、可审计、便于错误回溯；终止条件显式化避免无限推理。来源事实：TxAgent 在 3168 任务与 456 个性化场景的度量依赖该链路。
- **失效模式**：证据整合依赖 LLM 综合，存在选择性引用与过度自信；工具异构返回导致标准化失败，中断推理；门控阈值设置不当导致早停或空转。
- **对 OMP/PI 启示**：OMP 强制三件套 `reasoning.md` + `tool-call.json` + `meeting/trace` 落 `local://` 与 `artifact://`，阈值定义在 `WATCHDOG.yml`；跨 channel 复用该审计格式，支撑回放与责任定位。
- **事实与推断区分**：[事实] 显性 trace 与 Finish 工具形态、双产物落盘。[推断] 阈值门控对早停与空转的调节效果为推断。

## 原则 10：双轨环境 + Benchmark 即生态（E1 稳定轨与 E2 扩展轨，基准驱动生长）

- **证据**：Biomni 用 E1 官方稳定环境与 E2 社区扩展环境分离，Biomni-Eval1 提供 10 任务 433 实例统一度量；Robin 以 ether0 与 PaperQA2 为开放锚点支撑生态；TxAgent 以 5 基准与个性化场景度量工具调用质量。来源事实见 `channels/07-stanford-biomni.md` E1/E2 与度量节、`channels/09-futurehouse-robin.md` 开源状态节、`channels/10-txagent-biomed.md` 度量节。
- **机制**：E1 锁定依赖版本并强校验，E2 允许社区扩展并经审核合入；新增 channel 必须跑回归集后合入；开放权重与工具作为生态锚点被多 channel 复用。
- **收益**：兼顾可靠性与扩展性，贡献可见收益，形成持续生长。来源事实：Biomni 完全开源可一键安装，ether0 Apache 2.0 开放权重。
- **失效模式**：E2 质量参差污染注册表；105 包版本冲突推高复现成本；基准覆盖偏计算问答，开放式假设生成评估不足。
- **对 OMP/PI 启示**：OMP 在 `template/env-e1/` 与 `template/env-e2/` 分层管理依赖；在 `research-flywheel/eval/` 建立 10 任务回归集，新增 channel 自动跑分；将 PaperQA2、ether0 设为共享锚点，减少重复建设。
- **事实与推断区分**：[事实] 双轨定义、基准规模、开源锚点存在性。[推断] 回归门控对生态质量的保障程度为推断，需在 OMP 实测中校准。

## 原则 11：人机分叉点介入（人类在高层分叉点否决与追加目标）

- **证据**：Virtual Lab 人类研究员仅在关键分叉点否决或追加目标，不写代码；Co-Scientist 支持 seed idea 与自然语言反馈注入多轮迭代；Robin 物理执行依赖人类实验室。来源事实见 `channels/06-stanford-virtual-lab.md` 人类研究员行与人机分叉点节、`channels/08-google-co-scientist.md` 人机协作节、`channels/09-futurehouse-robin.md` 闭环验证节。
- **机制**：人类反馈作为 Meta-review 输入，直接影响下一轮生成方向；高风险决策设阈值门控触发人工复核，其余环节自治。
- **收益**：保留对高风险决策的否决权，释放人类在执行层的带宽。来源事实：Virtual Lab 人机交互仅在策略节点，计算侧占 94%。
- **失效模式**：人类反馈延迟成为闭环瓶颈；物理执行依赖合作方响应速度；人类追加目标与系统探索方向冲突。
- **对 OMP/PI 启示**：OMP 在 `WATCHDOG.yml` 定义 `human-gate` 与 `human-feedback: natural-language`，专家评论直通 Meta-review；PI 工作区保留分叉点视图，执行层自治。
- **事实与推断区分**：[事实] 人类介入位置与形态、物理依赖人类实验室。[推断] 分叉点阈值对带宽释放的具体数值收益为推断。

---

## 领域边界

### 边界 01：计算验证与湿实验验证的鸿沟

Biomni 与 TxAgent 停留在计算基准与真实任务回放，无自带湿实验闭环；Virtual Lab、Co-Scientist、Robin 的湿实验均在合作实验室完成，物理执行依赖人类，未实现机器人闭环；Biomni-Critic 与 TxAgent 的高分均为离线基准，迁移到真实临床分布需外部复核与前瞻性验证。该边界说明飞轮规划需区分干实验层与湿实验层的度量与准入门槛，干实验的高分不可直接外推为湿实验成功率。来源事实见 `_index-biomed.md` 横向对比闭环深度、`channels/07-stanford-biomni.md` 闭环停留计算层、`channels/10-txagent-biomed.md` 需临床复核、`channels/09-futurehouse-robin.md` 物理依赖人类。

### 边界 02：工具规模化与环境复现成本的边界

注册表驱动与 ToolRAG 支撑了 150-211 工具规模化，代价是检索精度下降、异构返回标准化复杂、105 软件包版本冲突；E2 社区扩展在未强审核时污染注册表；闭源系统如 Co-Scientist 依赖 Gemini 2.0 导致复现成本与供应商锁定。该边界说明 OMP 工作区在追求工具广度时，维持 E1 强校验与统一 schema 的投入不可省略，规模化收益以治理成本为上限。来源事实见 `channels/07-stanford-biomni.md` 潜在坑 1-2、`channels/10-txagent-biomed.md` 潜在坑 1-3、`channels/08-google-co-scientist.md` 闭源依赖。

### 边界 03：度量自举与 Goodhart 及小样本泛化风险

Co-Scientist 以 Elo 锦标赛实现自举评估，Elo 与 GPQA Diamond 正相关，评估样本仅 15 目标、11 人评，统计效力有限，Elo 与湿实验成功率不一致存在 Goodhart 风险；Virtual Lab 的 92 设计中仅少数强结合，平均成功率需谨慎解读；Robin 的 10 周与 200x 效率宣称基于单案例 dAMD，未充分验证泛化；Biomni 的开放式假设生成能力弱于专用系统。该边界说明飞轮度量需引入外部湿实验锚点与多疾病回归集，避免自评闭环放大偏差。来源事实见 `channels/08-google-co-scientist.md` 度量与潜在坑、`channels/06-stanford-virtual-lab.md` 评估偏乐观、`channels/09-futurehouse-robin.md` 单案例泛化与效率口径、`_index-biomed.md` 度量成熟度。

---

> 写作约束遵循：全篇采用直接、加和式陈述，规避对比与转折修辞；每条原则标注来源事实与推断分界，推断部分为 OMP/PI 迁移设计假设，需在工作区实测中校准。

