# 原则注册表 v1.0 — 可审计、可落地、可回放

> 定位：`derived-principles/00-design-philosophy.md` 的注册形态。每条原则具备独立编号、机制、证据来源、边界、失败信号、落地位置、验收条件六要素，可直接映射到文件、权限、门控、回放、调度脚本。推断部分需在工作区实测中以 held-out 与校准误差带验证。
> 输入：`debate/layer3/philosophy-a.md` 12 哲学与 `debate/layer3/operating-model.md` 12 运行决议合议结果。
> 数量：12 条编号原则，覆盖 L0 地基至 L3 扩展首期必选。
> 版本：2026-09-02

---

## 总表

| 编号 | 原则名称 | 证据等级 | 落地文件 | 验收信号 |
|------|---------|---------|---------|---------|
| P01 | 不可变基线与隔离可变面 | 高 direct | `program.md` / `.omp/config.yml` / `traces/<ts>/baseline.json` / `mutation.json` | changed_paths 属于 mutable_paths，完整性 hash 一致，parent SHA 不变 |
| P02 | 七阶段状态机与双终态归档 | 高 direct | `orchestration/flywheel.py:run_once()` / `orchestration/hooks/post-eval.sh` / `archive/` | keep/discard 原子性，traces.jsonl 回放 |
| P03 | 分层资源生命周期与成本指纹 | 高 direct | `program.md` / `lifecycle.jsonl` / `cost.json` / `metrics.json` | lifecycle 终态、requested/actual cost、fingerprint 完整 |
| P04 | 契约化能力注册表与分层治理 | 高 direct | `capabilities/registry.json` / `capabilities/tools/*.py` | version 覆盖率，路由留痕 |
| P05 | validate→execute 同签名与安全 pre_filter 硬门控 | 高 direct | `capabilities/registry.json` / `traces/<ts>/run.log` / `tool-call.json` | validate 结构化返回，pre_filter 审计链 |
| P06 | 可证伪假设门控 | 高 direct | `archive/ideas.jsonl` / `navigator/evidence/*.json` | 三字段完整性，unverified 阻断 |
| P07 | 主次双 keeper 联合裁决与分阶段启用 | 中高 direct + supported inference | `prepare.py:evaluate` / `reports/review.md` / `bench/scores.jsonl` | keeper_votes 完整，双轨分趋势 |
| P08 | 分级验证关卡与分层仿真路由及成功可审计 | 中高 direct | `capabilities/registry.json:policy` / `traces/<ts>/verification.json` | L1_gates 通过率，XRD 原始数据附带 |
| P09 | 显性推理 trace 与三级溯源及全局追加日志 | 高 direct | `traces/<ts>/` / `traces.jsonl` / `navigator/evidence/*.json` | 三级链接完整，FACT 双指标达标 |
| P10 | 分层持久记忆与 U 标记共识写入 | 中 supported inference | `archive/ideas.jsonl` / `archive/failed.jsonl` / `world-model.json` | U=0 占比，parent_ids 完整 |
| P11 | 分叉点人机协同与夜间自治边界 | 高 direct | `WATCHDOG.yml` / `status.md` / `hub` | pending_reviews 队列，human_decision 时延 |
| P12 | 结构化错误回灌、局部优先修复与干净复现 | 高 direct | `traces/<ts>/error.json` / `cost.json` / OMP `eval` | error envelope 完整，clean gates 与 reproduction 分开记录 |

---

## P01 — 不可变基线与隔离可变面

**机制**：每轮从已提交 Git baseline 派生 isolated merged view。`program.md` frontmatter 声明 `mutable_paths` 与 `integrity_paths`。modeling agent 在 merged view 中直接编辑跨文件候选。`program.md`、`prepare.py` 与 `capabilities/registry.json` 的 hash 进入 baseline manifest。成功候选保留为 isolation branch，orchestration 在归并前执行 changed-path 与完整性门控。

**证据来源**：原始四文件契约和 `writable_allowlist` 提供评估资产完整性目标。OMP `settings-schema.ts:task.isolation.*`、`task/isolation-runner.ts:runIsolatedSubprocess`、`task/worktree.ts:ensureIsolation` 与 pi-iso `isoResolve/isoStart/isoDiff` 提供直接实现证据。APFS backend 的 `clonefile` 路径证明 macOS CoW 语义。

**边界**：isolated task 要求 Git checkout 与已提交 baseline。`task.isolation.mode: auto` 依据宿主能力解析后端，`rcopy` 提供最终降级。approval mode 管理工具调用审批；文件级完整性由 baseline manifest、mutation gate 与归并控制执行。

**失败信号**：changed path 超出 `mutable_paths` 仍进入 full run。integrity hash 漂移后仍使用 baseline evaluator。候选执行期间 parent checkout SHA 或工作树变化。task isolation fallback 与 branch metadata 缺少记录。

**落地位置**：`.omp/config.yml` 设置 isolation `mode: auto`、`apply: false`、`merge: branch`。`program.md` 保存 profile。`traces/<ts>/baseline.json` 保存 SHA、hash 与 profile snapshot；`mutation.json` 保存 resolved backend、fallback reason、candidate branch、changed paths 与 gate 结果。`git.patch` 为可选审计产物。

**验收条件**：mutation gate 证明 changed paths 全部匹配 `mutable_paths`，三个 integrity path 的 hash 与 baseline 一致，parent checkout 保持 baseline SHA。成功候选生成 `omp/task/<id>`。keep 发生在 clean reproduction 后，并留有候选归并记录。

---

## P02 — 七阶段状态机与双终态归档

**机制**：七阶段 `inspiration → modeling → experiment → evaluation → writing → review → archive` 为唯一控制平面。成功路径经 `review` 归档到 `archive/papers/`，失败路径从 `evaluation` 或 `review` 直达 `archive`，产物为 `reports/failure.md` 与 `archive/failed.jsonl`。`orchestration/flywheel.py:run_once()` 为状态机落地，`schedule_prompt` 每 30-60 分钟触发一轮，空闲进入 Sleep。

**证据来源**：`template/00-spec.md` §2.1 状态图与阶段契约表为直接规范。`template/02-harness-wiring.md` §3.5 夜巡状态机与 `debate/layer2/architecture.md` 决议 01 为实现来源。`debate/layer2/adversarial.md` 共识 1 与 `epistemic.md` Guardrail 04 为收敛依据。两份 Layer 3 裁决在 P01/P02 与决议 01 一致。

**边界**：全部赛道通用。写作与审稿合并为 `review` 阶段内小循环，不增设状态。失败直达路径在任意 `evaluation` 或 `review` 节点可触发，产物结构遵循 `template/00-spec.md` §5.2 六段契约。

**失败信号**：`traces.jsonl` 缺失 `phase` 字段导致全链路不可回放。`git tag keep-<id>` 存在性与 `archive/papers/` 固化产物不一致。`archive/failed.jsonl` 未记录 `next hypotheses` 导致失败知识未回注。

**落地位置**：`orchestration/flywheel.py:run_once()` 状态机函数，`orchestration/hooks/post-eval.sh` keep/discard 分支逻辑，`archive/ideas.jsonl` 每行 `status: queued|running|keep|discard|failure`，`traces.jsonl` 全局追加日志，`reports/failure.md` 六段结构化失败报告。

**验收条件**：`traces/<ts>/metrics.json:keep` 布尔值与 `reason` 字段完整。`traces.jsonl` 每行含 `run_id/idea_id/phase/metric/delta/keep`，按 `ts` 排序可回放全链路。`git tag keep-<id>` 存在性表示成功归档，`archive/discard-<id>/` 存在性表示丢弃归档。`status.md` 顶部展示最近 3 个失败的 `root_cause`。

---

## P03 — 分层资源生命周期与成本指纹

**机制**：experiment profile 为 coarse、fine、assay 等 stage 声明 requested resource、cost type 与可选 deadline。runtime 追加 `started|heartbeat|checkpoint|paused|completed|failed|cancelled` 事件并记录 actual cost。coarse/fine 表达保真度与阶段路由。keeper 读取 completed execution、completed evaluation、device/environment fingerprint 与 actual cost。

**证据来源**：Karpathy 固定 5 min 墙钟提供单一计算赛道证据。物理 coarse-to-fine、A-Lab 4 h 烧结、10 周端到端与生物工具耗时提供跨尺度校正。追加运行时校准采用 stage profile、lifecycle 与 requested/actual 分离，保留真实成本与可恢复状态。

**边界**：计算、文献、仿真与 assay 使用各自资源字段。具体 stage 可声明 deadline。通用工作区省略统一墙钟截止值。paused run 保留 checkpoint。`failed|cancelled` 归类 execution_error，clean reproduction 未完成归类 inconclusive。未完成运行不参与 keeper。

**失败信号**：started 后缺失当前 lifecycle state。completed run 缺 actual cost、device/environment fingerprint 或 completed evaluation。paused run 缺 checkpoint。未完成 metrics 进入 keeper。requested 与 actual 字段混写导致成本回放失真。

**落地位置**：`program.md` experiment profile 保存 stage request。`traces/<ts>/lifecycle.jsonl` 保存状态事件，`cost.json` 保存 requested/actual cost，`metrics.json` 保存 execution/evaluation state 与 fingerprint，`traces.jsonl` 聚合终态、delta 与成本。`schedule_prompt` 检查 queued/paused run。

**验收条件**：每个 run 具有 started 与当前 lifecycle state。completed run 的 actual cost、device fingerprint、environment fingerprint 与 evaluation state 完整。heartbeat/checkpoint 可关联。inconclusive 与 execution_error 具有明确归因。keep 记录只引用 completed evaluation。

---

## P04 — 契约化能力注册表与分层治理

**机制**：每个 capability 声明最小契约 `input_schema + output_schema + env_snapshot + cost_model + failure_modes + safety_tags + requires_approval + endpoint(local|remote|sim) + doc_ref + doc_version` 并版本化可回放。注册表采用 `E1` 稳定轨强校验与 `E2` 扩展轨审核合入分层治理，按 `Reading/Computing/Experiment` 三域分面路由，调度先分面后分面内选择，检索失败阻断执行。

**证据来源**：`debate/layer1/platform.md` 原则 1 能力最小契约与原则 2 三域分面为直接证据。`debate/layer1/bio.md` 原则 04 Biomni 150 工具与 TxAgent 211 工具、ToolRAG Top-K 为直接证据。`debate/layer1/chem-materials.md` 原则 1 文档向量化为支撑。`debate/layer2/adversarial.md` 争议 4 与 `architecture.md` 决议 06 为裁决来源。Bohrium 数百万执行锚定为规模化证据。

**边界**：全部工具接入通用。治理投入未到位前封顶规模，避免先扩张后补契约。新增 capability 需提供 `doc_ref + doc_version + example_protocols`，缺一不可调度。路由留痕可回放，成本声明纳入审计。

**失败信号**：检索精度随规模下降，异构返回标准化复杂，105 包版本冲突，E2 污染注册表。契约粒度过粗致路由歧义，成本声明失真致预算超支。召回未命中时猜测调用而非阻断。

**落地位置**：`capabilities/registry.json` 单一真相源，每项含 `version/safety_tags/requires_approval/endpoint/hardware_dependency_level/pre_filter`。`capabilities/tools/*.py` 为工具包装，`hub` 按契约约束做路由与鉴权，`navigator/queries.jsonl` 记录分面路由决策。

**验收条件**：`capabilities/registry.json:version` 递增可统计，`safety_tags` 覆盖率可审计。`navigator/queries.jsonl` 含分面路由决策记录。ToolRAG 召回失败时 `validate` 返回阻断而非猜测调用。`E1` 锁定依赖版本并强校验，`E2` 审核合入需人类审批或 `hub:capability-approval` 确认。

---

## P05 — 能力层 validate→execute 同签名与安全 pre_filter 硬门控

**机制**：每个 capability 暴露 `validate(procedure)->{valid, errors[]}` 与 `execute(procedure)->observation` 同签名。`execute` 前强制调用 `safety pre_filter`，命中阈值进入人工确认队列。安全在编排层硬执行，提示词自律不计为安全措施。仿真与真机共享同一 `validate` 接口，调度器按 `simulate` 标志路由。

**证据来源**：`debate/layer1/chem-materials.md` 原则 2 ChemCrow `validate` 两段式与原则 3 ChemCrow GHS 工具链及 A-Lab 源头过滤为直接证据，Coscientist 缺独立校验被列为反例。`debate/layer1/platform.md` 原则 9 沙盒防伪与 `physics-crossdomain.md` 原则 5 AI 决策与确定性内核硬边界为跨域支撑。`debate/layer2/adversarial.md` 争议 5/6 为裁决来源。

**边界**：全部 `execute` 通用。校验器不完备时漏过不可行配方属于已知失效模式，执行侧暴露错误后回灌修正。无 pre_filter 的链路禁止物理执行，夜间自治仅允许 `hardware_dependency_level == 0` 任务。

**失败信号**：校验器不完备漏过不可行配方。提示层安全在新型危险组合上失效且无拦截证据链。`pre_filter` 判定结果未写入 `tool-call.json` 审计链。

**落地位置**：`capabilities/registry.json` 每项含 `safety_tags`、`requires_approval`、`endpoint`、`hardware_dependency_level`、`pre_filter: {tool: "chem.safety.ghs", policy}`。流程 `validate → safety pre_filter → execute → analyze` 四段，`validate` 符号拦截，`analyze` 显式建模炉与表征资源争用。

**验收条件**：`traces/<ts>/run.log` 含 `validate` 返回的 `{valid, errors[]}` 结构化记录。`tool-call.json` 含 `pre_filter` 判定结果与审计链。`requires_approval == true` 时 `hub` 人工确认队列出现待批记录。夜间 `schedule_prompt` 日志中 `hardware_dependency_level > 0` 任务自动跳过记录完整。

---

## P06 — 可证伪假设门控

**机制**：假设进入执行队列前产出三字段 `falsifiable_statement/predicate/negation_criterion`，分别对应可证伪陈述、判定谓词、否定标准。缺失字段直接阻断入队，不可证伪假设标记 `unverified` 不进入 `experiment`，回流到 `next hypotheses`。判定谓词包含阈值与度量，否定标准描述何种观测判定假设被否定。

**证据来源**：`debate/layer1/bio.md` 原则 06 假设谱系与 Elo 锦标赛、原则 07 自博弈辩论为直接证据。`debate/layer1/cs-ml.md` 原则 05 硬门控与原则 06/10 的 U 标记为支撑。`debate/layer2/epistemic.md` Guardrail 01 为认识论定义，`architecture.md` 决议 07 的 PI 门禁为实现。两份 Layer 3 裁决在可证伪性上一致。

**边界**：全部 idea 入队通用。开放式探索任务缺乏不变量时标记探索模式，不进入 L2 表征或外部发布。`risk_tags` 标注 `Goodhart/小样本/单域深度不足` 等风险。

**失败信号**：开放式任务在缺乏可形式化不变量时被误判为可证伪并进入 L2 表征。`archive/failed.jsonl` 缺失谓词与观测对照导致否定案例不可复用。Goodhart 风险下单指标优化触发偏科但未告警。

**落地位置**：`archive/ideas.jsonl` 单条扩展 `hypothesis.falsifiable_statement`、`hypothesis.predicate`、`hypothesis.negation_criterion`、`hypothesis.risk_tags`、`provenance.source_claim: {doc, section, quote}`。门控落位 `inspiration→modeling` 准入校验与 `review` 环 Critic 校验，`orchestration/hooks/pre-run.sh` 可扩展三字段校验脚本。

**验收条件**：`jq 'select(.hypothesis.falsifiable_statement==null)' archive/ideas.jsonl` 命中计数为零。`navigator/evidence/*.json` 保留假设到证据的三级链接。`archive/failed.jsonl` 对否定案例保留完整谓词与观测对照。`reports/failure.md:root_cause` 四选一与 `negative_result` 可复用结论完整。

---

## P07 — 主次双 keeper 联合裁决与分阶段启用

**机制**：数值 keeper 以 `val_bpb/benchmark/assay_metric` 为主硬门，语义 keeper 以 `reviewer_score/VLM/Elo` 为辅软门。数值 keeper 每轮必检，语义 keeper 在 `writing→review` 启用，VLM 审图与 FACT 引用审计作为写作后置门控。语义信号经过 held-out 人类抽检或外部锚点校准后参与排序，冲突走 PI 裁决，收敛期加 held-out 复测。

**证据来源**：`debate/layer1/cs-ml.md` 原则 7 双 keeper、原则 4 VLM 图表评审、原则 6 CycleReviewer 模拟分为直接证据。`debate/layer1/platform.md` 原则 10 RACE 相对参考评分与 FACT 审计为支撑。`debate/layer2/adversarial.md` 争议 3 与 `architecture.md` 决议 08、 `epistemic.md` Guardrail 05/09 为裁决来源。

**边界**：`evaluation` 必启用数值 keeper，`writing→review` 启用语义 keeper与可选 VLM/FACT 后置门控。未校准的模拟分仅用于排序，不用于 discard。双阈值过严导致探索停滞时 PI 裁决冲突。

**失败信号**：模拟 5.36 接近 5.24 远离 5.69 但被独立计为 keep。Elo 与湿实验成功率不一致但未触发冲突告警。单一指标优化触发偏科但未要求多维 keeper 同步展示。`FACT: citation_audit: accuracy < 0.8` 但仍自动合并到 main。

**落地位置**：`orchestration/config` 定义 `keepers: [{name: numeric, metric: val_bpb, threshold: epsilon}, {name: semantic, metric: reviewer_score, threshold: 6.0}]`，experiment profile 定义 stage requested resources、cost type 与可选 deadline。`prepare.py:evaluate` 产 `metric_main`，`review` 产结构化分数与逐条意见，VLM 产 `chart_feedback.json`，FACT 产 `fact_report.json`。配置 `max_chart_iters` 防止无界打磨。

**验收条件**：`traces/<ts>/metrics.json:keeper_votes: {numeric: pass|fail, semantic: pass|fail, conflict: boolean}` 完整。`reports/review.md` 含分数与 JSON 逐条意见。`bench/scores.jsonl` 含 `numeric/semantic` 双轨分与 `split: held_in|held_out` 及 `leakage_flag`。冲突案例单独归档，`hub:review-score` 时序可追溯。

---

## P08 — 分级验证关卡与分层仿真路由及成功可审计

**机制**：验证采用 L1 自动验证层、L2 领域校验层、L3 人审三级关卡分级执行。L1 对数值与仿真任务必检残差、守恒量、量纲一致性，验证器与生成器分离部署，检验脚本独立版本管理。仿真采用 `mattersim(快速阈值) → dft(精确阈值) → lab(合成阈值)` 三层路由分层验证，仿真用于排序剪枝，成功判定必附原始数据与精修报告。

**证据来源**：`debate/layer1/physics-crossdomain.md` 原则 3 残差与守恒量无监督验证与原则 4 物理合理性独立校验为直接证据。`debate/layer1/chem-materials.md` 原则 8 仿真即硬件 MatterSim MAE 36 meV/atom 与原则 10 XRD 自动解析瓶颈为直接证据。`debate/layer2/adversarial.md` 争议 8 与 `architecture.md` 决议 10、 `epistemic.md` Guardrail 10 为裁决来源。

**边界**：数值与仿真类任务必启用 L1 三项必检，物理与材料类任务叠加 L2，开放式探索任务在 L2 未覆盖时走 L3 人审。L1 未通过不进入 L2 或人工审查。仿真结论跨域复用时单层结论不外推。`≤20` 原子外推、DFT 0K 近似、非晶化判读失效、负样本稀缺乐观偏差为已知失效模式。

**失败信号**：残差小但解不正确，伪守恒未被独立校验捕获。DFT 0K 假阳性致仿真高分但真机无法合成。≤20 原子预训练外推到大晶胞能力未知但被直接外推。XRD 非晶化致自动解析失效但未触发多模态回退。

**落地位置**：`capabilities/registry.json:capability.policy: {mattersim, dft, lab}` 三阈值与 `verifier: {type: residual|conservation|dimensional|physical_sanity|critic, version}`。`traces/<ts>/verification.json: {L1_gates: [{check, result, evidence}], diversity: {distinct_modes, coverage}}`，`traces/<ts>/metrics.json:metric_aux{residual,conservation}`，`reports/review.md:sanity-check` 二元判定。

**验收条件**：`traces/<ts>/metrics.json:metric_aux` 含残差与守恒量偏差。`traces/<ts>/verification.json: L1_gates` 含三项必检结果与证据。成功判定附 XRD 原始数据与 Rietveld 精修报告或 assay 原始读数，缺失时归档被阻断。`trial_grid` 粗网格失败不进入 `validate_grid` 细网格验证。

---

## P09 — 显性推理 trace 与三级溯源及全局追加日志

**机制**：每轮实验、每次检索、每份报告产出显性推理链与三级溯源 `source → section → claim`。全局采用 `traces.jsonl` 追加日志与 `traces/<ts>/` 单轮隔离双轨。报告发布前必过 FACT 双指标引用审计与沙盒防伪校验，引用不可验证直接阻断发布。离线语料与线上语料分别维护引用有效期，引用可达性衰减单独记录。

**证据来源**：`debate/layer1/bio.md` 原则 09 显性推理 trace 与 Finish 门控为直接证据。`debate/layer1/platform.md` 原则 8 三级溯源与 FACT 审计及原则 3 推理与执行治理分离为直接证据。`template/02-harness-wiring.md` §4 Trace 治理为工作区直接规范。两份 Layer 3 裁决在 P05/决议 09 一致。

**边界**：全部阶段通用。每轮必产 trace，每份报告必含三级链接。推断部分需在工作区实测中以 held-out 与校准误差带验证。`navigator` 到 `modeling` 时 `T3/T4` 证据占比超阈值触发缺口再检索。

**失败信号**：引用可达性衰减但过期引用未标记待复核。自动化校验误判或沙盒逃逸与资源竞争。写作产物关键主张缺失证据编号但仍通过 `review` 门控。

**落地位置**：单轮 `traces/<ts>/baseline.json`、`mutation.json`、`lifecycle.jsonl`、`run.log`、`metrics.json`、`cost.json`、`reasoning.md`、`tool-call.json`、`verification.json`，失败时增加 `error.json`，审计策略启用时增加 `git.patch`。全局 `traces.jsonl` 追加 lifecycle、metric、actual cost 与 keeper 事件。`navigator/evidence/*.json` 含溯源片段、`source_tier(T0-T4)` 与 `citation_audit`，`reports/fact_report.json` 含审计报告。

**验收条件**：`traces.jsonl` 按 `ts` 排序可回放全链路，`status.md` 聚合展示最近 3 个失败的 `root_cause`。`reports/report.md` 每条关键主张附证据编号，缺失三级链接的报告在 `review` 门控被阻断。`fact_report.json: {valid_refs, accuracy}` 双指标可批量校验，`navigator/evidence/*.json:source` 可达性可统计。

---

## P10 — 分层持久记忆与 U 标记共识写入

**机制**：记忆采用短期 `meetings/<round>.md`、中期 `tree.json`/`elo-board`、`archive/ideas.jsonl`、长期 `world-model.json`/`knowledge_graph` 三级分层。长期边强制 `U=0 已验证 / U=1 未验证` 标记，`U=0` 才能作为后续假设前提，共识需至少 2 独立 agent 或原始数据支撑。无跨运行复用预期时用轻量 pairwise 表替代图谱。`archive/failed.jsonl` 负样本显式过滤与去重阈值 0.85。

**证据来源**：`debate/layer1/cs-ml.md` 原则 10 AI-Supervisor 世界模型 U 标记与共识写入为直接证据。`debate/layer1/chem-materials.md` 原则 5 A-Lab pairwise 剪枝 80% 与原则 7 SciAgents 图谱共享记忆为直接证据。`debate/layer2/adversarial.md` 争议 7 与 `architecture.md` 延后策略为裁决来源。Rumi 2026-07-24 商业下线为单点依赖警示。

**边界**：首期必选 `archive/failed.jsonl` 与 `archive/ideas.jsonl` 去重，图谱与 world-model 作为可选 L3 扩展。启用图谱需同时满足跨运行复用预期大于构建成本、边含 U 标记、共识或数据支撑三条件。图谱膨胀与冷启动噪声为已知失效模式，投入上限需在 Q03 中决策。

**失败信号**：图谱膨胀致检索与推理成本飙升。冷启动噪声大，共识过滤筛掉小众新颖发现。无物理验证时纸面创新被写入 `U=0`。`parent_ids` 缺失的假设标记孤立但仍被作为前提使用。

**落地位置**：`archive/ideas.jsonl` 每行 `parent_ids/elo/generation_round`，`archive/failed.jsonl` 每行 `negative_evidence/first_seen_run`，`channels/<id>/tree.json` 含 `nodes: [{idea_id, parent, score, status}]` 与 `tournament: {elo_board, comparisons[]}`，`world-model.json` 含 `edges: [{claim, U, 验证证据}]`。`memory_store` capability 固化三类记忆。

**验收条件**：`hub` 登记记忆检查点，`channels/elo-board.md` 与 `debate-{round}.md` 保留锦标赛全过程。`jq 'select(.U==0)' world-model.json` 可统计已验证边占比，缺失 `parent_ids` 的假设标记孤立。跨任务检索复用时注入来源版本与血缘标注可验证。`grep -c queued archive/ideas.jsonl` 增量与 `inspiration.md: auto` 时间戳可审计灵感引擎产出。

---

## P11 — 分叉点人机协同与夜间自治边界

**机制**：默认自治，高风险操作在分叉点强制人类介入。人类反馈以自然语言注入 Meta-review，策略对齐在 Team Meeting 层完成，执行层自治。介入范围、阈值、反馈通道显式配置于 `WATCHDOG.yml`。`schedule_prompt` 夜间自治仅允许 `hardware_dependency_level == 0` 任务自动执行。

**证据来源**：`debate/layer1/bio.md` 原则 01 双层会议抽象与原则 11 人机分叉点介入及 Virtual Lab 94% 工具耗时为直接证据。`debate/layer1/chem-materials.md` 原则 3 危险操作人工队列与 `physics-crossdomain.md` 原则 9 人机协同为支撑。`debate/layer2/adversarial.md` 争议 9 与 `epistemic.md` Guardrail 07 为裁决来源。

**边界**：三类操作强制介入：物理执行与外部发布、资金合规与生物安全相关、成本超过 `WATCHDOG.yml` 阈值。其余环节自治。人类延迟成为瓶颈与追加目标冲突为已知失效模式，通过 `meetings/<round>.md` 与 `artifact://` 可回放定位。

**失败信号**：人类延迟成瓶颈但未触发限流告警。`hardware_dependency_level > 0` 任务在夜间被自动执行。`WATCHDOG.yml` 阈值命中但 `schedule_prompt` 未跳过高风险任务。追加目标与系统探索冲突但未记录于会议纪要。

**落地位置**：`WATCHDOG.yml: {human_gate: {threshold, scope: [publish|hardware|budget|safety]}, human_feedback: "natural-language"}`。`status.md: {pending_reviews: {run_id, metric_delta, review_score, gate_reason}}` 看板视图。`hub` 消息 `{type: human_decision, decision: approve|veto|redirect, rationale}`。`meetings/<round>.md` 固化策略对齐记录。

**验收条件**：`status.md` 顶部展示最近 3 个待复核 keep 的 delta 与最近 2 个 failure 的 `root_cause`。`hub` 日志含 `human_decision` 时序与 `meeting/trace` 双产物关联存储。`WATCHDOG.yml` 阈值命中时 `schedule_prompt` 夜间自治跳过高风险任务的日志记录完整。`pending_reviews` 队列长度与 `human_decision` 时延可度量。

---

## P12 — 结构化错误回灌、局部优先修复与干净复现

**机制**：执行失败写入 `{error_class,message,frames:[{file,line,symbol}],stderr_tail,stage}` 语言中立信封。局部优先修复读取 frames 与原始日志。compile/smoke 使用 clean runtime，exploratory full run 可复用 retained runtime，keeper 候选使用 cold-start clean reproduction。repair success 与 clean reproduction success 分开记录。

**证据来源**：Dolphin 异常回溯局部修复与 Coscientist 模块修正提供修复证据。OMP `docs/tools/eval.md`、`tools/eval.ts` 与 eval runtime 直接定义单 cell、retained state、`reset` 和 per-call kernel。`template/02-harness-wiring.md` §3.2 给出真实 eval 参数与 error envelope。

**边界**：`error_class` 枚举 `syntax|import|runtime|timeout|resource|assert`，`stage` 枚举 `compile|smoke|full`。系统性依赖或管线错误可升级到 full-scope repair。retained runtime 服务探索效率，clean reproduction 作为 keeper 证据。

**失败信号**：错误信封字段或枚举缺失。frame 指向完整性路径。compile 失败后仍进入 smoke，smoke 失败后仍进入 full。`repair_passed` 被当作 reproduction 成功。探索 cache/state 未记录。keeper 缺 cold-start 结果。

**落地位置**：compile/smoke eval 调用使用 `reset: true` 或 `python.kernelMode: per-call`。探索首格重建 runtime，后续格复用并写 `exploration_state_manifest`。`traces/<ts>/error.json` 保存错误信封；`cost.json` 保存 `compile_clean_passed`、`smoke_clean_passed`、`repair_scope`、`repair_passed` 与 `clean_reproduction_passed`。

**验收条件**：error envelope 字段完整且 frames 可定位候选代码。compile/smoke/full 门控顺序可回放。`repair_passed` 与 `clean_reproduction_passed` 可独立查询。keeper 关联 cold-start reproduction、完整 fingerprint 和 completed evaluation。

---

## 延期与未决对照

本注册表仅收敛首期必选 12 条。以下 5 项为两份 Layer 3 裁决一致延后，需满足激活条件后评估：SDL 真机闭环与硬件指纹校准、GFlowNet 多样性采样与知识图谱持续演化、多租户计费与私域 Workspace 融合、人类 8 小时基线对照与作者共创 rubric 大规模校准、跨站点联邦调度与硬件指纹差异建模。详见 `00-design-philosophy.md` §4 与 `operating-model.md` 延期清单。

## 验证命令

```bash
grep -c "^## P" derived-principles/01-principles-registry.md  # 期望 12
grep -c '^\*\*证据来源' derived-principles/01-principles-registry.md  # 期望 12
grep -c '^\*\*失败信号' derived-principles/01-principles-registry.md  # 期望 12
grep -c '^\*\*落地位置' derived-principles/01-principles-registry.md  # 期望 12
grep -c '^\*\*验收条件' derived-principles/01-principles-registry.md  # 期望 12
```
