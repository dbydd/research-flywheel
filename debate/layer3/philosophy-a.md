# Layer 3 设计哲学裁决 A — 首席科研系统架构师裁决书

> 身份：首席科研系统架构师，第三层设计哲学裁判 A
> 输入：`debate/layer1/bio.md`、`chem-materials.md`、`cs-ml.md`、`physics-crossdomain.md`、`platform.md` + `debate/layer2/adversarial.md` + `debate/layer2/architecture.md` + `debate/layer2/epistemic.md` + `README.md` + `template/00-spec.md` + `template/01-workspace-layout.md` + `template/02-harness-wiring.md` + `template/03-inspiration-engine.md` + `channels/README.md` 全量 46 系统索引
> 启动条件：Layer 2 三份辩论文件完成后启动
> 输出义务：10-14 条优先级排序的设计哲学，每条含精确主张、证据链、适用边界、工作区机制、可观测验收信号、置信等级；单独列 5 条拒绝项与 5 个待人类决定的开放问题
> 约束：全篇采用直接、加和式陈述，区分来源事实与推断，推断显式标注；保持现有文件不变
> 写作时间：2026-09-02

---

## 0. 裁决方法与优先级依据

裁决对象为 Layer 1 约 54 条候选原则与 15 条领域边界，经 Layer 2 三次辩论收敛为 10 条对抗性共识、10 条架构决议与 11 条认识论护栏。裁决标准三项：跨领域可迁移性、可审计性、可落地性。跨领域指机制在 CS 数值、生物医学、化学材料、平台基建至少两域有独立证据支撑。可审计指产出物具备版本化溯源与可回放性。可落地指机制可映射到 `template/00-spec.md` 定义的七阶段状态机与 `01-workspace-layout.md` 的文件契约。

优先级排序依据：地基先行，执行次之，认知与治理随后，领域扩展居后。`architecture.md` 的 L0/L1/L2/L3 分层为排序骨架，`adversarial.md` 的十项争议裁决为取舍依据，`epistemic.md` 的三阶证据分级为置信标定依据。重复项合并，来源弱且无法观测的口号剔除，口号判定标准为缺乏可观测验收信号或仅依赖单案例宣称。

---

## 1. 设计哲学（12 条，按优先级排序）

### P01 — 单一可变区文件契约与七阶段状态机为地基

**精确主张**：工作区以 `program.md` 冻结目标、`prepare.py` 只读评估、`run.py` 唯一可变、`capabilities/registry.json` 受控变更四文件契约为地基，以 `inspiration → modeling → experiment → evaluation → writing → review → archive` 七阶段与失败直达 `archive` 双终态为状态机。任何 agent 遵守同一权限表，违规在执行前拦截。

**证据链**：
- `template/00-spec.md` §2.1 七阶段定义与 §3.1 文件契约表为直接规范来源
- `template/01-workspace-layout.md` §3-§4 读写权限表与 `hooks/pre-run.sh` 禁写校验为直接实现来源
- `debate/layer1/cs-ml.md` 原则 1 的 `prepare.py` 只读与 `writable_allowlist` 为 CS 域直接证据
- `debate/layer1/chem-materials.md` 原则 1 的 `doc_ref` 与原则 2 的 `validate → execute` 同签名为化学域支撑
- `debate/layer1/platform.md` 原则 4 的角色化分工与分阶段流水线为平台域支撑，`debate/layer2/architecture.md` 决议 01/02 将其归一
- `debate/layer2/epistemic.md` Guardrail 02 将其纳入可复现封存的门控
- `debate/layer2/adversarial.md` 无争议保留该项为最小可执行原则

**适用边界**：全部赛道通用。赛道切换时仅调整 `program.md` Plan DAG 段的准入阈值，文件职责不变。状态机不因任务类型增设状态，写作与审稿合并为 `review` 阶段内小循环。

**工作区机制**：
- 目录落位：`program.md`、`prepare.py`、`run.py`、`capabilities/registry.json`、`navigator/`、`traces/<ts>/`、`reports/`、`archive/`、`bench/`、`orchestration/`、`traces.jsonl`、`status.md`
- 权限执行：`orchestration/hooks/pre-run.sh` 执行 `git diff --name-only` 禁写校验，`prepare.py` 签名固定为 `load_data()` 与 `evaluate(pred,target)->metrics`
- 状态执行：`orchestration/flywheel.py:run_once()` 与 `hooks/post-eval.sh` 实现阶段迁移与双终态归档

**可观测验收信号**：
- `bash orchestration/hooks/pre-run.sh` 对篡改 `prepare.py` 的分支返回非零退出码，日志写入 `traces/<ts>/run.log`
- `traces/<ts>/metrics.json` 含 `keep` 与 `reason` 字段，`traces.jsonl` 每行含 `run_id/idea_id/phase/metric/delta/keep`
- `git tag keep-<id>` 存在性表示成功归档，`archive/discard-<id>/` 存在性表示丢弃归档
- `grep -c "phase" traces.jsonl` 可回放全链路阶段迁移

**置信等级**：高。直接证据。来源为工作区规格原文与多域独立实现验证。

---

### P02 — 指纹化分层预算与 git keep/discard 原子分支

**精确主张**：每轮执行声明 `device_info + budget_seconds + cost_type(compute|synthesis|assay)` 指纹。计算侧采用 `coarse` 粗筛与 `fine` 精验两级墙钟预算，湿实验与重仿真侧以 `assay_time + material_cost` 另计。超时硬截断，未完成步丢弃并采样已产指标，keep/discard 通过 git 分支原子语义实现。

**证据链**：
- `debate/layer1/cs-ml.md` 原则 1 Karpathy 固定 5 min 墙钟、git keep/discard、Red Hat 198 实验夜跑为直接证据，边界 1 指明跨硬件不可比与单文件局限
- `debate/layer1/physics-crossdomain.md` 原则 2 coarse-to-fine 分级执行为物理域直接证据
- `debate/layer1/chem-materials.md` 原则 5/10 的 A-Lab 单次 4 h 烧结与 `debate/layer1/bio.md` 原则 01/08 的 94% 工具耗时与 10 周端到端为跨尺度校正证据
- `debate/layer2/adversarial.md` 争议 1 裁决为指纹化分层预算，`debate/layer2/architecture.md` 决议 03 落地为 `trial_grid/validate_grid` 分级超时，`debate/layer2/epistemic.md` Guardrail 02/09 要求环境指纹与预算分层

**适用边界**：计算密集型任务默认启用两级墙钟。文献调研类任务预算设为 token 预算。湿实验侧不套用墙钟定价。未披露指纹的提升不计入 keep 选举。单机并发 modeling 上限 3，execution 串行或按内核并行。

**工作区机制**：
- 配置落位：`program.md` 声明主度量与 epsilon，`orchestration/flywheel.py` 设 `budget_seconds` 默认 300 可配置 300-900，`schedule_prompt` 夜巡 30-60 分钟触发 `run_once`
- 分支落位：`run/<id>` 分支，keep 时 `git merge --no-ff` 并打 tag，discard 时 `git reset --hard HEAD` 并保留 `traces/<ts>/` 到 `archive/discard-<id>/`

**可观测验收信号**：
- `traces/<ts>/metrics.json` 的 `budget.seconds` 与 `budget.gpu/device_info` 完整
- `traces/<ts>/run.log` 含超时 `SIGKILL` 记录，`traces.jsonl` 的 `delta` 字段可绘制 `progress.png`
- `git log --oneline --graph` 可回放 keep/discard 轨迹，`jq .keep traces/<id>/metrics.json` 可批量审计

**置信等级**：高。直接证据。墙钟赛马与 coarse-to-fine 分级在多系统验证，分层校正经对抗性审查确认。

---

### P03 — 契约化能力注册表与 E1/E2 分层治理

**精确主张**：每个 capability 声明最小契约 `input_schema + output_schema + env_snapshot + cost_model + failure_modes + safety_tags + requires_approval + endpoint(local|remote|sim) + doc_ref`，版本化可回放。注册表采用 `E1` 稳定轨强校验与 `E2` 扩展轨审核合入分层治理，调度先做分面路由再做分面内选择，检索失败阻断执行。

**证据链**：
- `debate/layer1/platform.md` 原则 1 能力最小契约与原则 2 三域分面为平台域直接证据
- `debate/layer1/bio.md` 原则 04 Biomni 150 工具与 TxAgent 211 工具、ToolRAG Top-K 为生物域直接证据，边界 02 指明检索精度下降与 105 包冲突
- `debate/layer1/chem-materials.md` 原则 1 文档向量化接入与原则 8 仿真分层为化学域支撑，`debate/layer2/architecture.md` 决议 06 将四类能力统一注册
- `debate/layer2/adversarial.md` 争议 4 裁决为有治理的注册表，`debate/layer2/epistemic.md` Guardrail 02/06/08 要求契约字段审计与分层权限

**适用边界**：全部工具接入通用。治理投入未到位前封顶规模，避免先扩张后补契约。路由留痕可回放，成本声明纳入审计。新增 capability 需提供 `doc_ref + doc_version + example_protocols`，缺一不可调度。

**工作区机制**：
- 文件落位：`capabilities/registry.json` 单一真相源，`capabilities/tools/*.py` 为包装，`hub` 按契约约束做路由与鉴权，`eval` 按契约校验输入输出
- 分面落位：`Reading` 检索与证据抽取、`Computing` 数值与仿真、`Experiment` 执行与表征；模型侧按概括/判读/推理分面路由
- 治理落位：`registry.json:version` 递增，`E1` 锁定依赖版本并强校验，`E2` 审核合入，变更需人类审批或 `hub` 的 `capability-approval` 频道确认

**可观测验收信号**：
- `capabilities/registry.json` 的 `version` 与 `safety_tags` 覆盖率可统计
- `navigator/queries.jsonl` 含分面路由决策记录，ToolRAG 召回失败时 `validate` 返回阻断而非猜测调用
- `hub` 审计日志含路由留痕与成本核算关联键 `capability ID`

**置信等级**：高。直接证据。Bohrium 数百万执行锚定与 Biomni/TxAgent 百级工具规模为规模化证据，分层治理经对抗性审查确认为必要约束。

---

### P04 — 能力层 validate → execute 同签名与安全 pre_filter 硬门控

**精确主张**：每个 capability 暴露 `validate(procedure)->{valid, errors[]}` 与 `execute(procedure)->observation` 同签名。`execute` 前强制调用 `safety pre_filter`，命中阈值进入人工确认队列。安全在编排层硬执行，提示词自律不计为安全措施。

**证据链**：
- `debate/layer1/chem-materials.md` 原则 2 ChemCrow `validate` 两段式与原则 3 ChemCrow GHS 工具链及 A-Lab 源头过滤为直接证据，Coscientist 缺独立校验被列为反例
- `debate/layer1/platform.md` 原则 9 沙盒防伪与边界 1 UniLabOS 协议约束为平台域支撑
- `debate/layer1/bio.md` 原则 11 human-gate 与 `debate/layer1/physics-crossdomain.md` 原则 5 AI 决策与确定性内核硬边界及原则 9 design-execute 分离为跨域支撑
- `debate/layer2/adversarial.md` 争议 5/6 裁决为文档驱动加符号校验加指纹校准与安全路由层硬门控，`debate/layer2/architecture.md` 决议 06 与 `epistemic.md` Guardrail 06 固化门控

**适用边界**：全部 `execute` 通用。仿真与真机共享同一 `validate` 接口，调度器按 `simulate` 标志路由。校验器不完备时漏过不可行配方属于已知失效模式，执行侧暴露错误后回灌修正。无 pre_filter 的链路禁止物理执行，夜间自治仅允许 `hardware_dependency_level == 0` 任务。

**工作区机制**：
- 契约落位：`capabilities/registry.json` 每项含 `safety_tags`、`requires_approval`、`endpoint`、`hardware_dependency_level`、`pre_filter: {tool: "chem.safety.ghs", policy}`
- 流程落位：`validate → safety pre_filter → execute → analyze` 四段，`validate` 符号拦截，`analyze` 显式建模炉与表征资源争用

**可观测验收信号**：
- `traces/<ts>/run.log` 含 `validate` 返回的 `{valid, errors[]}` 结构化记录
- `tool-call.json` 含 `pre_filter` 判定结果与审计链，`requires_approval == true` 时 `hub` 人工确认队列出现待批记录
- 夜间 `schedule_prompt` 日志中 `hardware_dependency_level > 0` 任务自动跳过记录

**置信等级**：高。直接证据。ChemCrow 每次合成前强制 GHS 评估与 A-Lab 源头过滤为硬门控直接验证。

---

### P05 — 显性推理 trace 与三级溯源及全局追加日志

**精确主张**：每轮实验、每次检索、每份报告产出显性推理链与三级溯源 `source → section → claim`。全局采用 `traces.jsonl` 追加日志与 `traces/<ts>/` 单轮隔离双轨。报告发布前必过 FACT 双指标引用审计与沙盒防伪校验，引用不可验证直接阻断发布。

**证据链**：
- `debate/layer1/bio.md` 原则 09 显性推理 trace 与 Finish 门控，产 `reasoning.md + tool-call.json` 为生物域直接证据
- `debate/layer1/platform.md` 原则 8 三级溯源与 FACT 审计及原则 3 推理与执行治理分离为平台域直接证据，Perplexity Deep Research 引用准确率 90.24% 与 Gemini 有效引用数 111.21 为度量支撑
- `debate/layer1/chem-materials.md` 边界 3 要求 XRD 原始数据与 Rietveld 精修报告可审计为化学域支撑
- `template/02-harness-wiring.md` §4 Trace 治理与 `template/00-spec.md` §3.1 `metrics.json` 契约为工作区直接规范
- `debate/layer2/architecture.md` 决议 09 与 `epistemic.md` Guardrail 03/04 固化溯源字段

**适用边界**：全部阶段通用。每轮必产 trace，每份报告必含三级链接。离线语料与线上语料分别维护引用有效期，引用可达性衰减单独记录，过期标记待复核。

**工作区机制**：
- 单轮落位：`traces/<ts>/run.log`、`metrics.json`、`cost.json`、`git.patch`、`reasoning.md`、`tool-call.json`、`verification.json`
- 全局落位：`traces.jsonl` 每行 `{"ts","run_id","idea_id","phase","metric","value","delta","keep"}` 追加不改历史，`navigator/evidence/*.json` 含溯源片段与 `source_tier(T0-T4)` 及 `citation_audit`
- 审计落位：`eval` 阶段自动执行 FACT 双指标与沙盒只读 controller 的 NaN/Inf 与 smoke test 检测

**可观测验收信号**：
- `traces.jsonl` 可回放全链路，`status.md` 聚合展示最近 3 个失败的 `root_cause`
- `reports/report.md` 每条关键主张附证据编号，缺失三级链接的报告在 `review` 门控被阻断
- `fact_report.json` 含有效引用数与准确率分数，`navigator/evidence/*.json` 的 `source` 可达性可批量校验

**置信等级**：高。直接证据。三级溯源与 FACT 双指标在 Bohrium 与 DeepResearch Bench 有量化验证。

---

### P06 — 可证伪假设门控

**精确主张**：假设进入执行队列前产出可证伪陈述、判定谓词、否定标准三字段。缺失字段直接阻断入队，不可证伪假设标记 `unverified` 不进入 `experiment`，回流到 `next hypotheses`。

**证据链**：
- `debate/layer1/bio.md` 原则 06 假设谱系与 Elo 锦标赛要求假设可比较与可进化、原则 07 自博弈辩论过滤不可证伪假设为生物域直接证据
- `debate/layer1/cs-ml.md` 原则 05 实现成功率硬门控与原则 06/10 的 U 标记验证门控为 CS 域支撑
- `debate/layer1/physics-crossdomain.md` 边界 1 指明检验依赖可形式化不变量为物理域边界证据
- `debate/layer2/epistemic.md` Guardrail 01 为可证伪门控的认识论定义，`debate/layer2/adversarial.md` 争议 9 与 `architecture.md` 决议 07 的 PI 门禁为门控实现

**适用边界**：全部 idea 入队通用。开放式探索任务缺乏不变量时标记探索模式，不进入 L2 表征或外部发布。判定谓词包含阈值与度量，否定标准描述何种观测判定假设被否定。

**工作区机制**：
- 字段落位：`archive/ideas.jsonl` 单条扩展 `hypothesis.falsifiable_statement`、`hypothesis.predicate`、`hypothesis.negation_criterion`、`hypothesis.risk_tags`、`provenance.source_claim: {doc, section, quote}`
- 门控落位：`inspiration → modeling` 准入校验，`review` 环 Critic 校验，`orchestration/hooks/pre-run.sh` 可扩展三字段校验脚本

**可观测验收信号**：
- `jq 'select(.hypothesis.falsifiable_statement==null)' archive/ideas.jsonl` 命中计数为零表示门控生效
- `navigator/evidence/*.json` 保留假设到证据的三级链接，`archive/failed.jsonl` 保留否定案例的完整谓词与观测对照
- `reports/failure.md` 的 `root_cause` 四选一与 `negative_result` 可复用结论完整

**置信等级**：高。直接证据与支持性推断并存。可证伪三字段为直接规范，Goodhart 风险外推为支持性推断。

---

### P07 — 主次双 keeper 联合裁决与外部校准

**精确主张**：每轮评估采用数值 keeper 与语义 keeper 联合裁决。数值 keeper 以 `val_bpb / benchmark / assay_metric` 为主硬门，语义 keeper 以 `reviewer_score / VLM / Elo` 为辅软门。语义信号经过 held-out 人类抽检或外部锚点校准后参与排序，冲突走 PI 裁决，收敛期加 held-out 复测。

**证据链**：
- `debate/layer1/cs-ml.md` 原则 7 双 keeper 联合裁决、原则 4 VLM 图表评审、原则 6 CycleReviewer 模拟分与原则 5 硬门控为 CS 域直接证据
- `debate/layer1/bio.md` 原则 06 Elo 与 GPQA 正相关为生物域支撑，边界 03 指明 Elo 与湿实验不一致及小样本效力不足
- `debate/layer1/platform.md` 原则 10 RACE 相对参考评分与 FACT 审计为平台域支撑
- `debate/layer2/adversarial.md` 争议 3 裁决为双 keeper 有主次与校准，`architecture.md` 决议 08 落地为分阶段启用，`epistemic.md` Guardrail 05/09 要求泄露检测与联合裁决

**适用边界**：`evaluation` 必启用双 keeper，`writing → review` 启用语义 keeper 与可选 VLM/FACT 后置门控。未校准的模拟分仅用于排序，不用于 discard。双阈值过严导致探索停滞时 PI 裁决冲突。

**工作区机制**：
- 配置落位：`orchestration/config` 定义 `keepers: [{name: numeric, metric: val_bpb, threshold: epsilon}, {name: semantic, metric: reviewer_score, threshold}]` 与 `budget_tiers: {explore: 300s, converge: 900s}`
- 执行落位：`prepare.py:evaluate` 产 `metric_main`，`review` 产结构化分数与逐条意见，VLM 产 `chart_feedback.json`，FACT 产 `fact_report.json`

**可观测验收信号**：
- `traces/<ts>/metrics.json` 的 `keeper_votes: {numeric: pass|fail, semantic: pass|fail, conflict: boolean}` 完整
- `reports/review.md` 含分数与 JSON 逐条意见，`bench/scores.jsonl` 含 `numeric/semantic` 双轨分与 `split: held_in|held_out` 及 `leakage_flag`
- 冲突案例单独归档，`hub` 广播 `review-score` 时序可追溯

**置信等级**：中高。直接证据与支持性推断并存。keeper 形态与 MAE 校准数据为直接证据，预算分层增益与校准带设定为支持性推断，需 held-out 实测校准。

---

### P08 — 分级验证关卡与分层仿真路由及成功可审计

**精确主张**：验证采用 L1 自动验证层、L2 领域校验层、L3 人审三级关卡分级执行。仿真采用 `mattersim(快速阈值) → dft(精确阈值) → lab(合成阈值)` 三层路由分层验证。仿真用于排序剪枝，成功判定必附原始数据与精修报告，误差以不确定度通道显式传播。

**证据链**：
- `debate/layer1/physics-crossdomain.md` 原则 3 残差与守恒量无监督验证与原则 4 物理合理性独立校验、原则 1 生成可解释经典求解器及原则 2 分级执行为物理域直接证据
- `debate/layer1/chem-materials.md` 原则 8 仿真即硬件 MatterSim MAE 36 meV/atom 与原则 10 XRD 自动解析瓶颈及边界 2 仿真保真度上限、边界 3 成功认定争议为化学域直接证据
- `debate/layer1/bio.md` 边界 01 干湿分离与 `platform.md` 原则 9 沙盒执行为跨域支撑
- `debate/layer2/adversarial.md` 争议 8 裁决为分层验证与成功可审计，`architecture.md` 决议 10 落地分级关卡，`epistemic.md` Guardrail 10 要求独立验证层

**适用边界**：数值与仿真类任务必启用 L1 三项必检，物理与材料类任务叠加 L2，开放式探索任务在 L2 未覆盖时走 L3 人审。L1 未通过不进入 L2 或人工审查。仿真结论跨域复用时单层结论不外推。`≤20` 原子外推、DFT 0K 近似、非晶化判读失效、负样本稀缺乐观偏差为已知失效模式。

**工作区机制**：
- 验证落位：L1 残差、守恒量、量纲一致性三项必检，验证器与生成器分离部署，检验脚本独立版本管理；L2 `sanity-check` 能力与 `analyze` 能力显式建模炉与表征资源争用
- 路由落位：`capabilities/registry.json:capability.policy: {mattersim, dft, lab}` 三阈值，调度器自动路由，生成器只认 `score(structure)->property`

**可观测验收信号**：
- `traces/<ts>/metrics.json:metric_aux` 含残差与守恒量偏差，`traces/<ts>/verification.json` 含 `L1_gates: [{check, result, evidence}]`
- `reports/review.md` 含 `sanity-check` 二元判定与理由，`traces/<ts>/run.log` 含 `trial_grid` 与 `validate_grid` 两级报告
- 成功判定附 XRD 原始数据与 Rietveld 精修报告或 assay 原始读数，缺失时归档被阻断

**置信等级**：中高。直接证据。残差与守恒量验证及 MatterSim 度量为直接证据，大晶胞外推能力为推测性外推。

---

### P09 — 分层持久记忆与 U 标记共识写入

**精确主张**：记忆采用短期 `meetings/<round>.md`、中期 `tree.json`/`elo-board`、`archive/ideas.jsonl`、长期 `world-model.json`/`knowledge_graph` 三级分层。长期边强制 `U=0 已验证 / U=1 未验证` 标记，`U=0` 才能作为后续假设前提，共识需至少 2 独立 agent 或原始数据支撑。无跨运行复用预期时用轻量 pairwise 表替代图谱。

**证据链**：
- `debate/layer1/cs-ml.md` 原则 10 AI-Supervisor 世界模型 U 标记与共识写入及原则 3 树搜索 `tree.json` 为 CS 域直接证据
- `debate/layer1/chem-materials.md` 原则 5 A-Lab pairwise 剪枝 80% 与原则 7 SciAgents 图谱共享记忆为化学域直接证据
- `debate/layer1/bio.md` 原则 06 假设谱系与 `debate/layer1/physics-crossdomain.md` 原则 6/7 状态图与知识图谱为跨域支撑
- `debate/layer1/platform.md` 原则 5 论文即能力向量检索为平台域补充
- `debate/layer2/adversarial.md` 争议 7 裁决为分层记忆加 U 标记加共识写入，`architecture.md` 决议 07/05 与 `epistemic.md` Guardrail 11 固化分层审计

**适用边界**：首期必选 `archive/failed.jsonl` 与 `archive/ideas.jsonl` 去重，图谱与 world-model 作为可选 L3 扩展。启用图谱需同时满足跨运行复用预期大于构建成本、边含 U 标记、共识或数据支撑三条件。图谱膨胀与冷启动噪声为已知失效模式，Rumi 2026-07-24 商业下线为单点依赖警示。

**工作区机制**：
- 存储落位：`archive/ideas.jsonl` 含 `parent_ids/elo/generation_round`，`channels/<id>/tree.json` 含 `nodes: [{idea_id, parent, score, status}]` 与 `tournament: {elo_board, comparisons[]}`，`world-model.json` 含 `edges: [{claim, U, 验证证据}]`
- 能力落位：`memory_store` capability 固化 pairwise 反应表、合成校验错误、图谱负样本三类记忆，`gap_discovery.py` 按方法→模块→benchmark→gap 分解

**可观测验收信号**：
- `hub` 登记记忆检查点，`channels/elo-board.md` 与 `debate-{round}.md` 保留锦标赛全过程
- `jq 'select(.U==0)' world-model.json` 可统计已验证边占比，缺失 `parent_ids` 的假设标记孤立
- 跨任务检索复用时注入来源版本与血缘标注可验证

**置信等级**：中。支持性推断。形态字段为直接证据，图谱增量对跨轮复利的量化与共识阈值设定需在运行中校准。

---

### P10 — 分叉点人机协同

**精确主张**：默认自治，高风险操作在分叉点强制人类介入。人类反馈以自然语言注入 Meta-review，策略对齐在 Team Meeting 层完成，执行层自治。介入范围、阈值、反馈通道显式配置于 `WATCHDOG.yml`。

**证据链**：
- `debate/layer1/bio.md` 原则 01 双层会议抽象与原则 11 人机分叉点介入及 Virtual Lab 94% 工具耗时为生物域直接证据
- `debate/layer1/chem-materials.md` 原则 3 危险操作人工队列与 `debate/layer1/physics-crossdomain.md` 原则 9/10 人机协同与约束主动学习为化学物理域支撑
- `debate/layer1/platform.md` 边界 1 真实实验硬件与事务安全边界及边界 2 私域与计费治理边界为平台域支撑
- `debate/layer2/adversarial.md` 争议 9 裁决为分叉点人机协同，`architecture.md` 决议 05/08 的 `hub` 分叉点视图与 `epistemic.md` Guardrail 07 固化看板

**适用边界**：三类操作强制介入：物理执行与外部发布、资金合规与生物安全相关、成本超过 `WATCHDOG.yml` 阈值。其余环节自治。人类延迟成为瓶颈与追加目标冲突为已知失效模式，通过 `meetings/<round>.md` 与 `artifact://` 可回放定位。

**工作区机制**：
- 配置落位：`WATCHDOG.yml: {human_gate: {threshold, scope: [publish|hardware|budget|safety]}, human_feedback: "natural-language"}`
- 视图落位：`status.md: {pending_reviews: {run_id, metric_delta, review_score, gate_reason}}`，`hub` 消息 `{type: human_decision, decision: approve|veto|redirect, rationale}`，`meetings/<round>.md` 固化策略对齐记录

**可观测验收信号**：
- `status.md` 顶部展示最近 3 个待复核 keep 的 delta 与最近 2 个 failure 的 `root_cause`
- `hub` 日志含 `human_decision` 时序与 `meeting/trace` 双产物关联存储
- `WATCHDOG.yml` 阈值命中时 `schedule_prompt` 夜间自治跳过高风险任务的日志记录

**置信等级**：高。直接证据。Virtual Lab 分叉点形态与人类 94% 计算侧占比为直接度量支撑。

---

### P11 — 结构化错误回灌的局部优先修复

**精确主张**：执行失败携带 `exception traceback + stderr + doc_hints` 结构化回灌。修复范围 local-first，`py_compile + quick_run` 烟雾测试后再进入全量训练或真机，全局重写作为降级路径。错误回灌保真度决定修正有效性。

**证据链**：
- `debate/layer1/cs-ml.md` 原则 2 Dolphin 异常回溯局部修复与模板机制为 CS 域直接证据
- `debate/layer1/chem-materials.md` 原则 4 Coscientist 加热振荡模块修正与 ChemCrow validation 迭代为化学域直接证据
- `debate/layer1/platform.md` 原则 9 沙盒防伪与 `physics-crossdomain.md` 原则 6 Docker 隔离执行为平台域支撑
- `debate/layer2/architecture.md` 决议 04 与 `adversarial.md` 共识 5、 `epistemic.md` Guardrail 04 固化回灌审计

**适用边界**：全部执行失败通用。系统性错误如依赖缺失与管线错配时局部修复可能陷入循环，校验失败需触发全局重写降级路径。截断噪声导致误诊为已知失效模式。

**工作区机制**：
- 内核落位：`orchestration/kernel.py:hot_run` 常驻 eval 持久内核，热加载 `run.py`，`doc_hints` 来自 `capabilities/registry.json:doc_ref` 检索
- 门控落位：`repair_scope: local-first`，`compile_check` 与 `minimal_run` 双门，失败产物携带 traceback 落盘供下一轮 prompt 直接复用，`execute` 返回值统一含 `stderr + doc_hints`

**可观测验收信号**：
- `traces/<ts>/run.log` 含完整 traceback，`traces/<ts>/cost.json` 含 `compile_check` 与 `minimal_run` 通过标记
- `traces.jsonl` 的 `phase: experiment` 条目含 `repair_scope: local|full`，连续 2 次局部修复失败后出现 `full` 降级记录
- `validator` 报错原文保留于 `tool-call.json`，支持回溯误诊

**置信等级**：高。直接证据。Dolphin traceback 定位与 ChemCrow validation-data 迭代为直接实现验证。

---

### P12 — 可检验性约束下的有约束多样性

**精确主张**：灵感引擎的多样性采样以可检验性为前提。reward 可建模且与外部锚点校准后，按 reward 正比采样抗 mode collapse，`distinct high-reward modes` 未达阈值不晋升执行。多候选并行经 skeptic/critic 评审，锦标赛与辩论提供多样性来源。

**证据链**：
- `debate/layer1/physics-crossdomain.md` 原则 8 GFlowNet 按 reward 正比采样与原则 7 知识图谱锦标赛及 IBM GT4SD 开源库为物理域直接证据
- `debate/layer1/bio.md` 原则 06 Elo 锦标赛与 test-time scaling 正相关及原则 07 自博弈辩论提升新颖性为生物域支撑
- `debate/layer1/cs-ml.md` 原则 3 Experiment Manager 树搜索派生多路径与原则 11 可编程组织为 CS 域支撑
- `debate/layer1/chem-materials.md` 原则 7 生成批判分工与原则 9 小样本 Adapter 为化学域补充
- `debate/layer2/adversarial.md` 争议 2 裁决为有约束的多样性，`architecture.md` 决议 07 的三段式轻量引擎与 `epistemic.md` Guardrail 10 多样性闸门为架构与认识论收敛

**适用边界**：仅在 reward 可度量且与外部锚点校准、分支预算与剪枝阈值显式配置、前置 `compile_check + minimal_run` 门控通过三条件同时满足时启用自由树搜索。探索期短预算海选，收敛期切模板约束复测。reward 稀疏噪声时采样退化为随机，多样性退化为随机性。

**工作区机制**：
- 引擎落位：`template/03-inspiration-engine.md` 三段式 `seed → generation → debate → gating → pool`，单次生成 5 个，一轮 Critic 加权排序 `0.5*score + 0.3*feasibility/5 + 0.2*novelty` 取 top-3，PI 门禁为本地规则
- 参数落位：`program.md` Plan DAG 段配置 `num_modes/diversity_weight/reward_model` 与 `branch_budget/prune_threshold/early_stop_patience`，`archive/ideas.jsonl` 分歧度阈值与不可证伪拦截

**可观测验收信号**：
- `archive/ideas.jsonl` 的 `queued` 计数与 `grep -c queued` 增量，`inspiration.md` 自动更新的 `auto` 时间戳
- `traces/<ts>/verification.json:diversity: {distinct_modes, coverage}` 达标记录，未达阈值时无晋升日志
- `reviews/<round>.json` 含 skeptic 评审记录与 `debate-{round}.md` 产物

**置信等级**：中。支持性推断与推测性外推并存。锦标赛与按 reward 正比采样形态为直接证据，跨域 reward 建模与阈值设定在工作区尚未实测。

---

## 2. 拒绝项（5 条）

### R01 — 用提示词呼吁替代安全 pre_filter

**被拒冲动**：在系统提示词中加入安全守则，依赖 LLM 自觉与模型拒答覆盖合成与生物安全。

**拒绝依据**：`chem-materials.md` 原则 3 汇总 ChemCrow 每次合成前强制 GHS 工具评估与 A-Lab 源头过滤为显式工具约束，Coscientist 依赖 GPT-4 拒答与 ECL 云端人工审核被标记为反例，`platform.md` 边界 1 UniLabOS 协议级约束与 `adversarial.md` 拒绝 1 一致指向提示层不可审计。新型危险组合易漏过，失败时无拦截证据链。

**替代**：P04 能力层 `safety pre_filter + requires_approval` 硬门控，审计落 `tool-call.json`。

---

### R02 — 单一 wall-clock 统一定价全域执行

**被拒冲动**：将 Karpathy 5 min 赛马直接作为湿实验与重仿真赛道的计费与 keep 依据，单一预算覆盖全部类型执行。

**拒绝依据**：`cs-ml.md` 边界 1 自述 H100 5 min 与 Mac 5 min 不可比、单文件锁死跨文件协同失效，`chem-materials.md` 原则 5/10 与 `physics-crossdomain.md` 原则 9 指明 A-Lab 单次烧结 4 h 与 Toronto Ada 数小时表征，`bio.md` 原则 01/08 指明 94% 工具耗时与 10 周端到端，`adversarial.md` 拒绝 2 判定统一定价导致长任务饥饿与短任务虚高。

**替代**：P02 指纹化分层预算，`coarse/fine/assay` 分池核算，未披露指纹的提升不计入 keep。

---

### R03 — 无校准模拟分独立裁决 keep/discard

**被拒冲动**：以 CycleReviewer 5.36、Elo、VLM 分直接决定论文或假设是否 keep，省去人类抽检与外部锚点校准。

**拒绝依据**：`cs-ml.md` 边界 2 指明模拟 5.36 接近 preprint 5.24 距接收 5.69 仍有差距，workshop 超阈值不等同主会接收，`bio.md` 边界 03 指明 Elo 与湿实验不一致及 Goodhart 风险，`chem-materials.md` 边界 3 指明 EvaluatorGPT 偏好流畅但幻觉回答，`adversarial.md` 拒绝 3 判定模拟信号与真实接收存在系统 gap。

**替代**：P07 主次双 keeper 与校准带，语义分仅排序，冲突走 PI 裁决，收敛期加 held-out 复测。

---

### R04 — 无治理扩张工具注册表至百级规模

**被拒冲动**：先追求 150-211 工具接入广度，契约与审核后补，注册表先扩张再治理。

**拒绝依据**：`bio.md` 边界 02 指明检索精度下降、异构返回标准化复杂、105 包版本冲突、E2 污染，`platform.md` 原则 1 失效模式指明契约粒度过粗致路由歧义与成本声明失真，`adversarial.md` 拒绝 4 判定规模化收益以治理为上限。

**替代**：P03 最小契约与 E1/E2 分层及版本化回放，治理未到位前封顶规模，召回失败阻断执行。

---

### R05 — 仿真分数等同实验成功，无需原始数据审计

**被拒冲动**：MatterSim/DFT 高分即宣布新材料发现，XRD/assay 原始数据与精修报告后补或免除，生成器只认统一 `score` 契约即判定成功。

**拒绝依据**：`chem-materials.md` 边界 2 指明预训练限定 20 原子外推未知、DFT 0K 近似假阳性，`chem-materials.md` 原则 10 与 `physics-crossdomain.md` 边界 1 指明非晶化致 XRD 无法识别与残差小不等同解正确、伪守恒，`chem-materials.md` 边界 3 指明 A-Lab 2026-01 correction 新颖性争议与 Chemistry World 质疑 36-43 新材料多为已知相，`adversarial.md` 拒绝 5 判定负样本稀缺致乐观偏差。

**替代**：P08 分层路由与成功可审计，仿真仅排序剪枝，成功判定必附 XRD 原始数据与 Rietveld 精修报告或 assay 原始读数。

---

## 3. 待人类决定的开放问题（5 个）

### Q01 — 首个赛道选择与度量标定

**问题**：首个落地赛道选单 GPU 语言建模、PDE 数值求解、文献调研中的哪一个作为夜间自转基线，`prepare.py:evaluate` 的主度量与 epsilon 阈值如何设定。

**背景**：`README.md` 规格要点列三类赛道均可，`template/00-spec.md` §1.2 要求 30 分钟内看到 metrics 与归档，`architecture.md` L0/L1 要求首期单机可跑通。单 GPU 短预算在 `cs-ml.md` 验证有效，在湿实验链路直接失效。选赛道决定首轮预算分层参数与验证关卡启用范围。

**决策选项**：
- 选项 A：单 GPU 语言建模为首赛道，主度量 `val_bpb`，epsilon 0.01，验证关卡 L1 不启用物理校验
- 选项 B：PDE 数值求解为首赛道，主度量 `rel_L2 + residual + conservation`，启用 L1 三项必检
- 选项 C：文献调研为首赛道，主度量 `FACT 双指标与 RACE 分`，启用三级溯源

**影响**：决定 `program.md` 首版目标陈述、`bench/` 回归集构成、`capabilities/registry.json` 首批能力清单。

---

### Q02 — 语义 keeper 的校准节奏与人类抽检投入

**问题**：CycleReviewer 模拟分、VLM 审图、Elo 排序的校准频率与人类抽检样本量如何配置，校准误差带公布形式如何确定。

**背景**：`epistemic.md` Guardrail 05/09 与 `adversarial.md` 共识 2 要求语义信号必经校准，`cs-ml.md` 边界 2 与 `platform.md` 原则 10 指明模拟分与真实接收存在 gap，Bench II 召回显著低于呈现。校准成本直接影响夜间自治比例。

**决策选项**：
- 选项 A：每 10 轮自动触发一次 held-out 人类抽检，抽检 5 份，误差带写入 `bench/scores.jsonl`
- 选项 B：仅在连续 3 轮 keep 后触发校准，其余时段语义分仅排序
- 选项 C：引入外部湿实验或投稿锚点做前瞻性校准，周期按月

**影响**：决定 `orchestration/config` 的 keeper 阈值与 `reports/review.md` 的 rubric 版本管理策略。

---

### Q03 — 图谱与世界模型的启用时机与投入上限

**问题**：`knowledge_graph` 与 `world-model.json` 何时从可选 L3 扩展转入主干，构建成本与维护投入上限如何设定。

**背景**：`architecture.md` 延后 02 指明 GFlowNet 与图谱因冷启动噪声与一致性维护成本高而延后，激活条件为 `archive/failed.jsonl` 超 50 条且出现 mode collapse；`epistemic.md` 不确定性 03/04 指明规模化拐点与自主性深度权衡尚未量化，Rumi 2026-07-24 下线暴露单点依赖风险。

**决策选项**：
- 选项 A：维持首期轻量 pairwise 表，图谱延后至 50 条失败样本后评估
- 选项 B：首期即引入最小图谱，仅承载假设谱系与证据边，不引入 GFlowNet 采样
- 选项 C：接入 GT4SD 等开源库做多样性采样预研，图谱与采样联动

**影响**：决定 `memory_store` 能力形态与 `hub` 检查点管理复杂度。

---

### Q04 — 硬件在环与联邦调度的接入边界

**问题**：SDL 真机闭环、云端合成异地执行、联邦调度与硬件指纹校准何时接入，接入前仿真分支的验证充分性标准如何界定。

**背景**：`architecture.md` 延后 01/05 指明 SDL 与联邦调度因真实硬件抽象与协议约束而延后，激活条件为 `capabilities/registry.json` 出现 `endpoint: remote` 且仿真分支验证通过；`physics-crossdomain.md` 边界 2 与 `chem-materials.md` 边界 1 指明跨硬件指纹差异与经济边界，小团队自建不经济。

**决策选项**：
- 选项 A：首期纯软件，`endpoint` 仅 `local|sim`，真机接入需独立安全评审
- 选项 B：开放 `remote` 仿真分支，允许 Dry Lab 云端指令分发，物理执行仍需人类确认
- 选项 C：接入 ChemOS 联邦接口做小规模异地并行试点，附硬件指纹校准参数

**影响**：决定 `capabilities/registry.json` 的 `hardware_dependency_level` 分级与 `WATCHDOG.yml` 的夜间自治白名单。

---

### Q05 — 开放式假设生成任务的评估有效性与发布门槛

**问题**：探索型开放课题在缺乏参考答案与可形式化不变量时，rubric 共创、FACT 审计、人类基线的发布门槛如何设定，何种条件下允许发布探索性报告。

**背景**：`epistemic.md` 不确定性 05 与 `platform.md` 边界 3 指明 PaperBench 复制任务人类 PhD 41% 显著高于最强 agent 21%，开放式假设生成评估有效性下降，LLM 互评易被污染，Biomni 开放式假设生成弱于专用系统。`physics-crossdomain.md` 边界 1 指明验证天花板在可形式化不变量。

**决策选项**：
- 选项 A：开放课题标记探索模式，报告仅归档不对外发布，需 L3 人工物理审查后方可发布
- 选项 B：开放课题引入二值诊断矩阵，召回/分析/呈现三维达标后发布，附不确定性声明
- 选项 C：开放课题要求至少 2 独立 agent 共识或原始数据支撑，`U=1` 边不作为发布依据

**影响**：决定 `reports/report.md` 的发布门控与 `reports/domain-gate.md` 的跨域迁移校验强度。

---

## 4. 溯源与方法说明

**输入覆盖**：`debate/layer1` 5 份、`debate/layer2` 3 份、`README.md`、`template` 4 份、`channels/README.md` 46 系统索引全部纳入裁决。Layer 1 约 54 条候选原则与 15 条领域边界参与去重，Layer 2 约 10+10+11 条共识与护栏参与收敛。

**合并处理**：Sakana 广度脑暴、Co-Scientist 六角色 Elo 锦标赛、Virtual Lab PI 会议、Rumi GFlowNet 采样、SciAgents 图谱游走、ResearchAgent 链式文献排序六条灵感路径归一为 P12 有约束多样性；Karpathy git 分支、Claw 隔离 workspace、Denario Docker、Bohrium Lebesgue 调度四条执行隔离路径归一为 P02 指纹化分层执行；Biomni 150 / TxAgent 211 工具集、Bohrium 注册表、doc 向量化、ToolRAG 四条注册表路径归一为 P03 契约化治理。

**剔除标准**：无法观测验收的口号剔除，来源弱且无法落地的宣称剔除，判定标准为缺失可观测信号或仅单案例支撑。R01-R05 为典型剔除项，分别对应零校验安全、单一预算定价、无校准语义裁决、无治理扩张、仿真等同成功五类口号。

**推断标注**：本文件对跨系统归一、层次划分、阈值默认值的综合属于跨系统迁移推断，需在本地工作区实测中校准。推断部分已在每条哲学的工作区机制中参数化，来源事实均可在 `debate/layer1/*.md`、`debate/layer2/*.md`、`template/*.md` 中回溯验证。证据等级遵循 `epistemic.md` 三阶分级：直接证据、支持性推断、推测性外推。

**工作区验证**：

```bash
ls debate/layer1/*.md debate/layer2/*.md template/*.md debate/layer3/philosophy-a.md
grep -c "^### P" debate/layer3/philosophy-a.md  # 期望 12
grep -c "^### R" debate/layer3/philosophy-a.md  # 期望 5
grep -c "^### Q" debate/layer3/philosophy-a.md  # 期望 5
grep -c "可观测验收信号" debate/layer3/philosophy-a.md  # 期望 12
grep -c "置信等级" debate/layer3/philosophy-a.md  # 期望 12
```

---

> 写入：`debate/layer3/philosophy-a.md`（本文件）
> 未改动：`debate/layer1/*.md`、`debate/layer2/*.md`、`channels/*.md`、`template/*.md`、`README.md`
> 覆盖哲学：12 条。拒绝项：5 条。开放问题：5 个。
