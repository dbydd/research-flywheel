# Research Flywheel 最终设计哲学 v1.1

> 本文记录 Layer 1–3 递归辩论与逐条人机商讨后的现行原则。`debate/` 保留原始提案与证据，本文承担当前规范。

## 1. 原则总表

| 编号 | 原则 | 核心落点 | 证据等级 |
|------|------|----------|----------|
| P01 | 不可变基线与隔离可变面 | Git baseline、`mutable_paths`、integrity manifest、isolation branch | 高 direct |
| P02 | 七阶段研究状态与 runtime 子状态 | 七阶段、lifecycle、完整终态归档 | 高 direct |
| P03 | 分层资源生命周期与成本指纹 | requested/actual cost、checkpoint、fingerprint | 高 direct |
| P04 | OMP 能力发现与研究能力清单 | OMP provider、research manifest、路由记录 | 高 direct |
| P05 | OMP 与工具层最小破坏性防护 | approval policy、bash patterns、工具原生边界 | 高 direct |
| P06 | 实验承诺门控 | idea、exploratory probe、committed experiment | 高 direct |
| P07 | 领域原生评估与按需审查 | native evaluator、primary outcome、milestone review | 中高 direct + supported inference |
| P08 | 领域证据阶梯接口 | evidence tier、escalation、raw evidence | 中高 direct |
| P09 | 过程记录与分域溯源 | append-only trace、claim provenance、profile audit | 高 direct |
| P10 | 四层恢复链与研究账本 | Goal/Todo、Compaction/Hindsight、journal、ledger | 中高 direct + supported inference |
| P11 | 明确授权边界内全自治 | authorization boundary、pending action、resume point | 高 direct |
| P12 | 结果分类、保真错误回灌与双执行边界 | outcome、error envelope、retained/clean runtime | 高 direct |

## 2. 合议设计哲学

### P01 — 不可变基线与隔离可变面

**精确主张**：每轮研究从已提交 Git baseline 派生 disposable merged view。`program.md` 声明 `mutable_paths` 与 `integrity_paths`。modeling agent 在 isolated view 中编辑候选。orchestration 在正式执行前校验 changed paths 与完整性 hash。候选以 isolation branch/commit 进入归并门控，patch 承担可选审计与恢复。

**证据链**：Karpathy autoresearch 提供固定评估资产与 git keep/discard 证据。OMP `runIsolatedSubprocess`、`isoResolve`、`isoStart`、`isoDiff` 与 APFS clonefile/rcopy 后端提供直接执行证据。

**适用边界**：profile 决定可变目录、评估入口、数据边界与工具权限。ML、PDE、材料、实验协议均可使用各自目录形态。Git checkout 与已提交 baseline 是 isolation 前置条件。

**工作区机制**：`.omp/config.yml` 使用 `mode: auto`、`apply: false`、`merge: branch`。`traces/<run_id>/baseline.json` 固化 SHA、profile 与 integrity hashes；`mutation.json` 固化 backend、branch、changed paths 与 gate 结果。

**可观测验收信号**：changed paths 全部匹配 `mutable_paths`；integrity hashes 与 baseline 一致；parent checkout 保持 baseline SHA；keep 记录关联 clean reproduction 与归并结果。

**置信等级**：高 direct。

### P02 — 七阶段研究状态与 runtime 子状态

**精确主张**：研究控制面固定为 `inspiration → modeling → experiment → evaluation → writing → review → archive`。runtime 管理 `active|waiting|paused|resumed|cancelled|completed` 与执行 lifecycle。archive 固化 keep、negative result、inconclusive、execution error 四类科学终态。

**证据链**：Agent Laboratory 的 literature/experiment/writing 分段、AI Scientist 的论文生命周期、Karpathy 的 keep/discard 共同支持阶段化闭环。OMP session、Todo 与 runtime lifecycle 支持恢复和取消。

**适用边界**：七阶段表达科研语义。下载、排队、重试、checkpoint 等执行细节进入 runtime 子状态。领域 profile 复用同一研究拓扑。

**工作区机制**：每个 run 保存阶段 journal 与 lifecycle 事件。`traces.jsonl` 追加 phase、runtime state、outcome 与 artifact refs。archive 记录最终证据包和下一研究入口。

**可观测验收信号**：阶段与 runtime state 可分别查询；每个 started run 具有当前状态；每个终态拥有 archive 记录；按时间排序可回放完整链路。

**置信等级**：高 direct。

### P03 — 分层资源生命周期与成本指纹

**精确主张**：experiment profile 为每个 stage 声明 requested resource、cost type 与可选 deadline。runtime 追加 `started|heartbeat|checkpoint|paused|completed|failed|cancelled` 事件并记录 actual cost。正式比较关联 completed evaluation、device/environment fingerprint 与 actual cost。

**证据链**：Karpathy 固定窗口、PDE coarse-to-fine、A-Lab 小时级烧结与生物实验周级周期共同证明资源尺度依赖领域。OMP runtime 直接提供生命周期和取消边界。

**适用边界**：计算、文献、仿真与 assay profile 使用各自资源字段。通用模板省略统一墙钟值。paused run 关联 checkpoint。未完成执行退出正式比较。

**工作区机制**：`program.md` 保存 stage request。`lifecycle.jsonl` 保存状态事件。`cost.json` 保存 requested/actual。`metrics.json` 保存 execution/evaluation state 与 fingerprint。

**可观测验收信号**：completed run 的 actual cost、device fingerprint、environment fingerprint、evaluation state 齐全；paused run 具有 checkpoint；execution error 与 inconclusive 具有明确归因。

**置信等级**：高 direct。

### P04 — OMP 能力发现与研究能力清单

**精确主张**：OMP runtime 负责发现、合并、启停与刷新 skills、agents、commands、MCP 和工具。飞轮 research manifest 负责研究用途、输入输出、endpoint、审批要求、成本模型、常见失败与文档版本。发现、激活、路由三项决策分别留痕。

**证据链**：Biomni、TxAgent 与 Bohrium 证明能力目录对百级工具路由的价值。OMP capability/provider registry、skills refresh、agent discovery 与 MCP tools-changed 事件提供现成运行基座。

**适用边界**：首期能力清单保持小型。`stable|needs_review` 可表达成熟度。custom tool 文件的 session 级刷新能力低于 MCP；该限制写入 capability 文档。

**工作区机制**：`capabilities/registry.json` 保存研究级 manifest。OMP provider registry 保持运行时真相。`navigator/queries.jsonl` 与 run trace 记录 capability id、version、route reason、call outcome。

**可观测验收信号**：agent 能定位正确能力与文档；输入输出契约可读取；调用关联版本与实际 endpoint；刷新边界清晰；路由失败保留原因。

**置信等级**：高 direct。

### P05 — OMP 与工具层最小破坏性防护

**精确主张**：模型推理与研究角色承担主要行为约束。OMP approval policy、bash command patterns 与工具原生权限边界负责明确破坏性动作。飞轮读取执行结果与必要工具事件。

**证据链**：ChemCrow 与 A-Lab 证明确定性工具约束的价值。OMP approval 决策顺序、工具 tier、per-tool policy 与 bash patterns 已提供统一执行门。

**适用边界**：文件系统、远程服务、真实仪器和账号动作遵守各自工具契约。高影响外部动作遵守 point-of-risk confirmation。研究工作区省略 procedure 级 pre-filter、全量安全标签、自建审批队列和第二安全编排器。

**工作区机制**：`.omp/config.yml` 引用现有 approval 配置。capability manifest 记录 `requires_approval` 与 endpoint，字段承担发现提示。实际批准由 OMP 或工具执行层完成。

**可观测验收信号**：明确破坏性调用产生 allow/prompt/deny 结果；工具原生拒绝完整返回；研究 trace 引用结果 artifact；工作区中不存在平行审批状态机。

**置信等级**：高 direct。

### P06 — 实验承诺门控

**精确主张**：idea 保存观察、来源、问题与不确定性。exploratory probe 保存探索问题、预期信息增益与下一决策。committed experiment 在正式资源分配前保存可证伪主张、观测指标、判定规则、否定条件与 requested resources。result 按预注册规则归类为 support、refute 或 inconclusive。

**证据链**：Google Co-Scientist 的假设演化、AI Scientist 的实验计划与多个系统的负结果回流共同支持资源承诺点上的可证伪纪律。

**适用边界**：开放灵感与弱信号保留探索空间。高成本计算、远程配额、真实仪器和正式结论需要 committed experiment。原始 idea 无全局字段完备要求。

**工作区机制**：`archive/ideas.jsonl` 保存 idea/probe。`runs/<run_id>/commitment.json` 保存正式实验契约。`metrics.json` 与 research ledger 保存预注册规则和观测对照。

**可观测验收信号**：每次正式资源分配引用 commitment；commitment 的 metric、decision rule、negation criterion 与 request 齐全；result 分类可由原始观测复算。

**置信等级**：高 direct。

### P07 — 领域原生评估与按需审查

**精确主张**：每个 channel/profile 声明 native evaluator、primary outcome、baseline comparison 与 raw evidence artifact。客观实验轨依据 evaluator 证据作 keep 决策。探索轨由 PI 依据证据与信息增益选择下一步。Elo、reviewer、VLM 与 FACT 各自服务候选排序、叙事审查、图表审查与引用审计。

**证据链**：Karpathy 指标、Co-Scientist Elo、CycleReviewer、VLM 审图与 DeepResearch FACT 分别来自独立任务环节。现有证据支持分工使用。

**适用边界**：领域原生结果保留原始量纲。语义评分服务对应产物。报告准备、重大路线切换与重要结论触发外部锚点或人工抽检。

**工作区机制**：profile 的 `evaluation` 节声明 evaluator、metric direction、baseline 与 evidence artifact。review 配置声明适用的可选工具和触发里程碑。

**可观测验收信号**：keep 记录引用 native evaluator；exploratory continuation 记录 information gain；语义工具输出关联具体用途；核心 metrics 无通用合成 keeper 分数。

**置信等级**：中高 direct + supported inference。

### P08 — 领域证据阶梯接口

**精确主张**：核心证据层级为 `proxy|modeled|measured|independently_reproduced`。每个 profile 声明 evaluator、升级条件、evidence refs 与成功表述。生成器和验证器使用独立入口。结论措辞匹配已达到的证据层级。

**证据链**：MatterSim→DFT→lab、PDE coarse→invariant→fine、ML smoke→held-out→reproduction 与深度调研 source→claim audit 共同支持领域化阶梯。

**适用边界**：profile 提供具体检查。材料使用 XRD/Rietveld，数值物理使用残差/守恒，ML 使用 benchmark，生物使用 assay，引用报告使用 claim audit。

**工作区机制**：profile 的 `evidence_ladder` 声明 tier、evaluator、escalation 与 required artifacts。`verification.json` 保存 achieved tier、checks、evidence refs 与 claim language。

**可观测验收信号**：每项成功主张具有原始 evidence refs；tier 升级满足 profile 条件；验证器版本独立记录；报告措辞与 achieved tier 一致。

**置信等级**：中高 direct。

### P09 — 过程记录与分域溯源

**精确主张**：每个 run 保存追加式过程记录，字段包含 phase、action summary、inputs、outputs、decision 与 timestamp。研究和报告 channel 保存 claim provenance。计算 profile 保存 execution integrity。引用型 profile 保存 citation audit。图表型 profile 保存 figure review。

**证据链**：TxAgent trace、Bohrium 三级溯源、DeepResearch FACT 与 Claw 执行完整性分别支持对应分域机制。

**适用边界**：过程记录覆盖全部 run。claim provenance 服务有事实主张的产物。execution integrity、citation audit 与 figure review由 profile 触发。

**工作区机制**：`traces.jsonl` 与 `traces/<run_id>/events.jsonl` 追加事件。`navigator/evidence/*.json` 保存 source、locator、quote/raw artifact、tier 与 audit state。journal 保存可恢复的决策摘要和证据引用。

**可观测验收信号**：事件可按时间重放；关键主张可追到 source locator 或 raw artifact；profile 专属审计产物齐全；记录保存决策摘要，隐藏模型推理不进入契约。

**置信等级**：高 direct。

### P10 — 四层恢复链与研究账本

**精确主张**：OMP Goal 与 Todo 构成活跃控制面。Compaction 与 Hindsight 提供启发式上下文连续性。`runs/<run_id>/journal/<phase>.md` 提供确定性阶段恢复点。研究账本跨运行保存 hypothesis、experiment、result、failure 与 claim。派生索引可从账本重建。

**证据链**：OMP Goal/Todo/session/compaction/memory 提供恢复原语。AgentRxiv、A-Lab、SciAgents 与各系统失败库证明跨运行研究记录的复利价值。

**适用边界**：工作区文件与原始 artifact 具有事实优先级。Hindsight 提供检索线索。lineage tree、Elo board、pairwise table、vector index 与 knowledge graph 按 profile 需求启用。

**工作区机制**：ledger record 保存 `epistemic_state`、`evidence_tier`、`scope`、`evidence_refs`、`source_runs`、`supersedes`。journal 保存 state、input/output refs、decisions、uncertainties、next actions 与 resume recipe。

**可观测验收信号**：新 agent 可按 Goal→Todo→active journal→ledger refs→trace→Hindsight 顺序恢复；派生索引删除后可重建；科研事实引用工作区证据。

**置信等级**：中高 direct + supported inference。

### P11 — 明确授权边界内全自治

**精确主张**：Goal 或 run manifest 声明 workspace、tools/endpoints、已有算力或配额、数据访问与外传范围、生命周期 envelope、已授权外部动作及授权来源。边界内研究、计算、修复、写作、归档与续跑全自动进行。越界动作进入 pending action。

**证据链**：Virtual Lab、Agent Laboratory 与 OMP headless task/session resume 支持长链自治。OMP approval 与外部行动确认规则提供执行边界。

**适用边界**：pending action 保存 run、phase、action、target、scope、exact values、reason、required decision 与 resume point。当前 Todo 完成 journal checkpoint 后进入 blocked，其他 runnable Todo 继续。

**工作区机制**：`program.md` 保存 `authorization_boundary`。`runs/<run_id>/pending-actions.jsonl` 保存越界请求。Goal/Todo 保存阻塞与恢复控制。schedule prompt 读取边界和直接授权来源。

**可观测验收信号**：边界内任务无需人工救场；越界任务具有完整 pending action；blocked Todo 可从 journal 恢复；工作区省略 WATCHDOG 与硬件等级总开关。

**置信等级**：高 direct。

### P12 — 结果分类、保真错误回灌与双执行边界

**精确主张**：每次执行先分类为 `execution_error|negative_result|inconclusive`。execution error 保存完整原始输出引用、输入与环境引用、部分产物、failure fingerprint、attempted actions、capability ref、summary 与 failure class。agent 基于因果诊断选择修复范围，并运行 profile 声明的最低成本相关检查。

**证据链**：Dolphin traceback 修复、Coscientist 文档检索修复与 ChemCrow 工具错误回灌支持保真诊断。OMP eval retained state、`reset`、per-call kernel 与独立子 agent runtime 提供双执行边界。

**适用边界**：retained eval 服务探索、缓存与诊断。clean process、per-call kernel 或 reset runtime 服务正式比较、keep、archive 与外部结论。negative result 与 inconclusive 进入研究账本和下一实验设计。

**工作区机制**：`error.json` 保存语言中立信封和 raw refs。`cost.json` 分开记录 repair 与 clean reproduction。profile 声明 compile/smoke 或领域等价检查。keeper 关联 cold-start reproduction。

**可观测验收信号**：三类 outcome 可区分；错误原文可取回；重复 fingerprint 触发新诊断或新方案；repair success 与 clean reproduction success 独立；正式结论具有 clean evidence。

**置信等级**：高 direct。

## 3. 明确拒绝项

1. 飞轮内自建第二套审批与安全编排。
2. 通用模板统一固定墙钟、硬件等级或跨域成本单位。
3. 原始 idea 全量强制伪精确字段。
4. 数值、Elo、reviewer、VLM 与 FACT 合成为通用 keeper 分数。
5. 残差、守恒、MatterSim、XRD 或 FACT 成为全域必检。
6. `U=0/U=1` 二值共识替代领域 evaluator 与原始证据。
7. 固定相似度阈值自动删除研究想法。
8. 自建 Python kernel 守护进程复制 OMP eval runtime。

## 4. 延后扩展

- 真实仪器闭环与跨站点联邦调度：领域 profile、工具原生授权与现场验证齐备后接入。
- GFlowNet、多样性采样和知识图谱：账本规模、重复检索成本与跨任务复用需求形成真实信号后接入。
- 多租户计费与私域融合：出现共享实例与隔离需求后接入。
- 大规模语义评分校准：对外质量声明与稳定产物积累后接入。

## 5. 当前开放问题

1. 首个生产领域 profile 及其 native evaluator。
2. 外部报告和重大路线切换的人工抽检策略。
3. 长周期任务的 checkpoint 粒度与 runtime deadline 设计。
4. 真实远程 endpoint 的数据外传授权表达。
5. 派生索引启用时的维护成本记录。

## 6. 溯源

原始证据位于 `channels/`。Layer 1 领域归纳、Layer 2 交叉辩论与 Layer 3 独立裁决位于 `debate/`。逐条人机商讨形成本文 v1.1。`derived-principles/03-debate-record.md` 保留初始裁决与最终修订的映射。
