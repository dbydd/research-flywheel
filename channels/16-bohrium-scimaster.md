# 16 — DP Bohrium + SciMaster + DeepModeling 科学智能基础设施

| 维度 | 内容 |
|------|------|
| **机构** | 深势科技 DP Technology + AI for Science Institute + 上海交大 / 北大 / 中科院理论所等联合团队 |
| **论文/发布时间** | `Bohrium + SciMaster: Building the Infrastructure and Ecosystem for Agentic Science at Scale` arXiv:2512.20469 (2025-12-23, CC BY 4.0)；Bohrium 平台 https://www.bohrium.com / SciMaster https://scimaster.bohrium.com |
| **开源状态** | **部分开源 / 开放生态**：DeepModeling 社区完全开源 (LGPL-3.0/MIT)，Bohr Agent SDK 开源 (github.com/dptech-corp/bohr-agent-sdk)；Bohrium/SciMaster/UniLabOS/ Science Navigator 为托管服务，模型与能力通过注册表按使用计费 |
| **循环形态** | **平台级闭环 + 多 Master Agent 长周期工作流**：工具/模型/工作流在 Bohrium 上可调度、可观测、可计费；SciMaster 将科学问题编译为 Reading / Computing / Experiment 三域结构化工作流，执行后回流使用信号、失败模式、成本与验证证据，持续优化接口、调度与知识 |
| **核心关键词** | Science-as-a-Service；agent-ready capability；capability registry；Science Navigator / Lebesgue / UniLabOS 三支柱；科学智能基座 (Innovator + SciencePedia + DeepModeling) |

## 1. 平台分层 (5 层逻辑架构)

```
Layer 5  治理与计费层 — 账号、权限、配额、优先级调度、usage-based 计费与订阅
Layer 4  编排层 SciMaster (X-Master 架构) — 推理与规划信号 → 结构化工作流 → 跨域调度
Layer 3  科学智能基座 — Innovator 通用科学基座模型 + SciencePedia 知识基座 + DeepModeling 开源能力供给
Layer 2  能力注册与执行基座 Bohrium — Science Navigator (Reading) / Lebesgue (Computing) / UniLabOS (Experiment)
Layer 1  裸资产层 — 数据集、算力 (云/HPC/加速器)、实验室硬件、科学软件
```

论文明确提出 Bohrium 位于裸资产与上层编排器之间，负责**统一抽象、跨平台调度、异步运行时、平台级日志/监控/鉴权/核算**，将异构资产标准化为具有明确输入输出、复现执行信封与可审计运行记录的 capability。SciMaster 则分离推理规划信号与执行治理，通过 X-Master 将问题转化为工具与智能体工作流并在 Bohrium 基座上执行。

三域可执行服务细节：
- **Reading — Science Navigator**：摄入论文/专利/技术报告，多模态解析 (表格、公式、反应式、分子结构、谱图)，实体/关系/工作流片段抽取，引用与依赖图谱，细粒度语义检索与多跳遍历，段落与断言级溯源。
- **Computing — Lebesgue 调度系统**：统一云 / 自建 HPC / 专用加速器作业提交、资源分配与监控；代码与管线以可复现环境打包，版本/依赖/执行信封入注册表；多租户配额与优先级保障并发可预测。
- **Experiment — UniLabOS 实验室操作系统**：机器人/反应器/表征仪器虚拟化为事务安全基座，实验协议机器可读化，执行轨迹/传感数据/结果结构化落盘，参数边界与协议约束 + 高风险操作人审介入。

## 2. Capability 注册 (Capability & Tool Registry)

这是 Bohrium 对 OMP 最具移植价值的设计：

- **注册对象**：工具、模型 (经典求解器/科学基座模型/领域代理模型)、数据集、工作流、协作产物统一入注册表。
- **最小契约**：`输入/输出 Schema + 可复现环境 + 执行信封 (executable envelope) + 约束/成本/失败模式声明`。论文称为 capability minimal contract。
- **版本与血缘**：注册表记录版本、依赖、输入输出模式与执行信封，支持按约束路由与跨实例复用。
- **标准化打包**：科学代码与管线以可复现环境打包后由 Lebesgue 调度；Bohr Agent SDK 提供本地/云端双模，本地快速迭代、云端 GPU 集群承担生产级计算。
- **三类服务分面**：Reading / Computing / Experiment 能力分面注册，调度器据分面选择后端。

> 可借鉴点：注册表不仅是发现机制，更是**可观测性与可计费性锚点**，后续所有 trace、验证与 flywheel 信号都以 capability ID 为键关联。

## 3. Trace 治理 (可观测、可复现、可审计)

- **平台级可观测性**：Bohrium 提供贯穿作业的 logging / tracing / monitoring，每个调用可追踪、可回放、可审计、可跨候选方案对比。
- **溯源链**：Science Navigator 检索片段/抽取事实/装配工作流元素显式链接回源文档章节与引用上下文，支持 provenance-preserving 复现检查。
- **模型与工作流一等公民**：模型与工作流与工具同等视为可调用、可治理资产，每次调用记录执行信封、资源消耗与验证证据，支撑工作流级而非单次调用级评估。
- **全文 1130 万级执行信号**：论文披露在真实工作流上已沉淀数百万规模的执行锚定信号 (execution-grounded signals)，覆盖成功/失败、耗时、成本、约束满足度与验证证据。
- **安全与回滚**：UniLabOS 实验执行在受控策略与人审下运行，参数边界与协议级约束强制执行。

## 4. Flywheel 机制 (社区级飞轮)

论文 §6 明确将 flywheel 列为四大瓶颈之一的对治核心：

- **使用信号回流**：哪些能力被调用、作业如何调度、何处失败、资源如何消耗，全部通过 Bohrium 日志回流，驱动调度/编排策略、能力上下架与高层抽象演进。
- **验证证据回流**：Science Navigator 的索引/排序/抽取管线随访问模式与成功/失败信号迭代；工作流级验证结果沉淀为 SciencePedia 的长执行链 (long chains of execution) 组成部分。
- **生态供给飞轮**：DeepModeling 开源社区持续贡献可复用引擎/求解器/工作流 (DeePMD-kit、ABACUS、DeePTB、dpnegf、DeepFlame、jax-fem、DP-GEN、dflow、dpdispatcher、APEX、CrystalFormer)，在 Bohrium 治理环境中被调用、比较与改进；SciencePedia 的长思维链 (LCoT) 将结论解压为可验证推理步骤，供后续复用。
- **激励对齐探索**：除既有按量计费与订阅外，团队在探索将使用信号与价值创造、社区贡献奖励更紧密绑定的激励设计，为开放工具/模型/实验室能力的持续供给提供经济闭环。

论文展示的 11 个 Master Agent (PaSaMaster、SurveyMaster、PharmMaster、MatMaster、PDEMaster、FlowXMaster、PhysMaster、OPT-Master、AMTechMaster 等) 在阅读/计算/实验闭环上实现**端到端周期数量级缩短**，是飞轮已转动的实证。

## 5. 智能体架构与工具链

- **科学智能基座三件套**：
  - *Innovator*：通用科学基座模型，负责跨域推理与行动路由，将问题翻译为代码/仿真配置/实验方案，科学感知 (文本/公式/分子图/谱图/图像联合理解) + 科学认知与规划。
  - *SciencePedia* (https://sciencepedia.bohrium.com)：将知识从压缩结论解压为带显式假设与依赖的长思维链，投射为可导航百科，并向长执行链扩展，形成 content-tool 统一知识库。
  - *DeepModeling* (https://deepmodeling.com, https://github.com/deepmodeling/community)：覆盖引擎层/工作流数据层/管线应用层的互操作组件，强调生产级质量与模块化演进。
- **SciMaster 编排**：X-Master 工具增强推理架构，维护科学问题实体的长期状态与记忆，支持多智能体分解、跨域工具调度与长周期协调；约束、资源边界与可验证性为一等约束。
- **Bohr Agent SDK**：双模架构，统一本地与 Bohrium 云端执行，公开 Python SDK。

## 6. 度量体系

- **工作流级指标**：周期时间 (cycle time)、鲁棒性、验证结果为主要度量，替代单模型分数；论文 11 个案例均报告数量级周期缩短。
- **平台级信号**：调用频次、调度效率、失败模式分布、资源消耗、约束满足率、验证证据覆盖率，多百万规模持续累积。
- **科学正确性**：依赖 Science Navigator 的溯源精度、执行轨迹可复现性与实验协议约束满足度，而非仅文本相似度。

## 7. 核心可借鉴点 → OMP 映射

| Bohrium/SciMaster 模式 | OMP 对应构件 | 移植建议 |
|---|---|---|
| Capability Registry 最小契约 | `task` 能力注册 + `skill://` 规范 | 为每个可调用工具/模型/工作流定义 `inputs/outputs/env/constraints/cost/failure` 契约，写入 `task` prompt 的 Contract 段，作为后续 trace 关联键 |
| 三域分面 (Reading/Computing/Experiment) | `task` 角色分工 + `hub` 协调 | 将调研类 task 分为检索、计算、验证三角色，Conductor 在 hub 上按分面路由，减少单体 prompt 过载 |
| Lebesgue 统一调度 + 多租户治理 | `hub` + `schedule_prompt` | 用 `hub` 实现跨 task 资源感知与优先级队列，`schedule_prompt` 承担异步长作业与重试/退避，与 Lebesgue 语义对齐 |
| Science Navigator 细粒度溯源 | `eval` + `channels/*.md` 证据链 | 每个 channel 要求 `source → section → claim` 三级引用，eval 阶段自动校验引用可达性与版本一致性 |
| Innovator 路由决策 vs SciMaster 执行治理分离 | 推理模型 vs `hub`/`eval` 治理分离 | 推理侧只产生计划与假设，执行与审计交由 `hub`/`eval`，避免模型既当裁判又当选手 |
| 平台级 trace 可回放可对比 | `eval` 执行轨迹 + `hub` 日志 | 每次 `task` 执行产生结构化 trace (输入、环境、耗时、成本、验证证据)，存入 `research-flywheel/traces/`，供跨 run 对比与回归检测 |
| 社区飞轮与激励 | `channels/_index-*.md` + 贡献度核算 | 以 channel 被引用次数、验证通过率、复用次数作为贡献信号，未来对接订阅/打赏或积分 |

## 8. 潜在坑

- **托管锁定**：Bohrium/SciMaster 核心为闭源托管服务，Bohr Agent SDK 仅覆盖接口层，底层调度与 UniLabOS 能力无法自托管，移植时需用开源替代 (如 dflow/dpdispatcher + 自建 k8s) 补位。
- **科学解析成本高**：多模态文档解析 (公式/反应式/分子图/谱图) 依赖专用管线，通用 LLM 抽取精度不足，需引入 Uni-Parser 等领域模型。
- **实验硬件耦合**：UniLabOS 的事务安全与人审机制高度依赖真实硬件抽象，纯软件环境复刻价值有限，过度抽象会引入虚假可执行性。
- **激励设计未定型**：论文坦言计费与社区激励仍在探索，直接照搬易产生刷量或价值错配。
- **Innovator 未发布**：作为系统角色描述，尚无稳定模型权重可直接调用，相关能力需用现有大模型 + 领域模型组合近似。

## 参考

- Zhang et al., Bohrium + SciMaster, arXiv:2512.20469v1 (2025-12-23) — https://arxiv.org/html/2512.20469v1 / https://www.alphaxiv.org/abs/2512.20469v1
- Bohrium 官网 https://www.bohrium.com / https://www.dp.tech/en/product/bohrium
- Bohr Agent SDK https://github.com/dptech-corp/bohr-agent-sdk
- DeepModeling https://deepmodeling.com / DeePMD-kit https://pmc.ncbi.nlm.nih.gov/articles/PMC10445636
- SciencePedia https://sciencepedia.bohrium.com
