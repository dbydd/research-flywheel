# 第二层认识论护栏与审计框架（Epistemic Guardrails）

> 定位：第二层科学方法与审计辩论员
> 输入：`debate/layer1/*.md` 五份、`channels/README.md`、各文件来源节与链接、`template/00-spec.md` 工作区规格
> 输出义务：审计可证伪性、可复现性、来源层级、负结果、评估污染、自动化权限、人类复核、跨域迁移风险；每项原则标注证据等级；定义工作区可落地的审计字段、门控、回放要求；给出 8-12 条 guardrails 与 5 条明确不确定性
> 约束：保持现有文件不变，只新增本文件与必要目录

---

## 1. 审计范围与方法

审计对象为五份 Layer 1 证据分析：`bio.md`、`physics-crossdomain.md`、`chem-materials.md`、`cs-ml.md`、`platform.md`。审计输入包含 46 个系统的 `channels/*.md` 溯源链与 `_index-*.md` 横向对比。审计方法采用三阶证据分级，逐条回溯来源事实与推断边界，映射到 `template/00-spec.md` 定义的七阶段状态机与目录契约。

统计锚点：`channels/README.md` 登记 46 条系统，开源比例约 65%，物理跨域新增 16 条（含 AutoNumerics、PhysMaster、FlowX、Denario、Rumi、GFlowNet、DigCat、A-Lab 等）。Layer 1 共沉淀约 54 条可迁移原则与 15 条领域边界。本层在其上做认识论收敛。

---

## 2. 证据等级定义

| 等级 | 标记 | 判定标准 |
|------|------|----------|
| 直接证据 | direct | 来源论文、官方文档、开源代码、运行日志中可定位的原始陈述或度量，具备可复核链接 |
| 支持性推断 | supported inference | 跨 2 个以上系统的机制归纳，逻辑链完整，具备可检验预测，尚未在目标工作区实测 |
| 推测性外推 | speculative | 单案例类比或跨域外推，缺乏直接度量支撑，需前瞻性验证或外部锚点校准 |

使用规范：每条 guardrail 标注主等级，涉及多源时附加子项等级分解。

---

## 3. 认识论护栏（11 条）

### Guardrail 01 — 可证伪假设门控

**原则**：假设进入执行队列前，产出可证伪陈述、判定谓词、否定标准。

**来源审计**：
- `bio.md` 原则 06/07：假设谱系与 Elo 锦标赛要求假设可比较、可进化，Elo 与 GPQA 正相关，存在 Goodhart 风险。`cs-ml.md` 原则 05 要求 `impl_success == true` 硬门控。`chem-materials.md` 原则 07 要求 Critic 挑错。`physics-crossdomain.md` 边界 1 指明检验依赖可形式化不变量。
- 等级：direct（Elo 机制、硬门控存在性）；supported inference（Goodhart 风险外推到工作区）

**工作区落地审计字段**：
```
archive/ideas.jsonl 单条扩展字段：
  hypothesis.falsifiable_statement: string（单句可证伪陈述）
  hypothesis.predicate: string（判定谓词，含阈值与度量）
  hypothesis.negation_criterion: string（何种观测判定假设被否定）
  hypothesis.risk_tags: string[]（Goodhart / 小样本 / 单域深度不足）
  provenance.source_claim: { doc: string, section: string, quote: string }
```

**门控**：
- `inspiration` 到 `modeling` 准入：缺失三字段直接阻断入队
- `review` 环 Critic 校验：不可证伪假设标记 `unverified`，不进入 `experiment`，回流到 `ideas.jsonl` 的 `next hypotheses`

**回放要求**：
- `navigator/evidence/*.json` 保留假设到证据的 `source → section → claim` 三级链接
- `traces/<ts>/reasoning.md` 记录判定谓词的满足度计算过程
- `archive/failed.jsonl` 对否定案例保留完整谓词与观测对照

---

### Guardrail 02 — 可复现执行封存

**原则**：执行结果具备可复跑性，环境、代码、数据、度量同版本封存。

**来源审计**：
- `platform.md` 原则 01/09：能力最小契约与沙盒执行，要求输入输出 Schema、环境快照、执行信封、NaN/Inf 检测。`cs-ml.md` 原则 01 要求 `prepare.py` 只读与 git keep/discard 状态机。`chem-materials.md` 原则 08 要求 MatterSim/DFT/实验室三路分层验证。`physics-crossdomain.md` 原则 02 要求 coarse-to-fine 分级与超时隔离。
- 等级：direct（契约字段、只读校验、沙盒形态）；supported inference（分层验证降低仿真-实验鸿沟的外推）

**工作区落地审计字段**：
```
traces/<ts>/metrics.json 扩展：
  budget: { seconds, gpu, device_info }
  env_fingerprint: { image_digest, python_version, package_lock_hash }
  code_ref: { patch_hash, parent_run, branch }
  data_ref: { dataset_version, prepare_py_hash }
  metric_main / metric_aux / keep / reason 同 template/00-spec.md §3.1
traces/<ts>/cost.json：耗时、token、费用
capabilities/registry.json：每个 capability 的输入输出 Schema、约束、成本、失败模式
```

**门控**：
- `modeling` 到 `experiment`：`prepare.py` 篡改检测失败阻断
- `experiment` 到 `evaluation`：缺失 `env_fingerprint` 或 `device_info` 的运行标记不可比，不参与 keep 选举
- `evaluation` 的 keep 判定显式记录 `device_info + budget_seconds` 指纹

**回放要求**：
- `reproduce.sh` 一键复跑最新 keep，依赖 lock 文件与镜像 digest 完整
- `git` 分支保留 discard 路径的 `traces/<ts>/run.log` 与 `git.patch`，支持断点续跑
- `eval` 持久内核与 `hub` 协调的并发执行保留资源隔离日志

---

### Guardrail 03 — 来源层级与三级溯源

**原则**：区分证据强度，强制三级溯源，量化引用审计。

**来源审计**：
- `platform.md` 原则 08 要求 source → section → claim 三级溯源，FACT 双指标审计引用准确率，Bench II 诊断召回短板。`bio.md` 原则 08/10 强调活数据源与开放锚点。`chem-materials.md` 边界 3 要求 XRD 原始数据与精修报告可审计。
- 等级：direct（FACT 90.24% 准确率、Bench II 三维度评分结构）；supported inference（开放锚点复用降低重复建设）

**工作区落地审计字段**：
```
navigator/evidence/*.json 单条：
  source_tier: T0_原始数据 | T1_同行评审论文 | T2_预印本/技术报告 | T3_解读/博客 | T4_LLM生成
  provenance: { source_url, section_id, claim_span, retrieval_time, access_status }
  citation_audit: { valid_refs, accuracy, recall_proxy }
capabilities/registry.json：数据源 capability 标注更新频率与授权状态
```

**门控**：
- `navigator` 到 `modeling`：T3/T4 证据占比超过阈值触发缺口再检索
- `writing` 到 `review`：引用条目缺失三级链接或 FACT 校验失败阻断发布
- `archive` 固化时写入 `citation_audit`，支撑跨 run 对比

**回放要求**：
- 引用链路版本化存储于 `hub`，支持离线语料与线上复测的差异对比
- 引用可达性衰减单独记录有效期，过期引用标记待复核
- 写作产物 `reports/report.md` 每条关键主张附证据编号

---

### Guardrail 04 — 负结果强制归档与再利用

**原则**：失败为一等产物，具备固定结构与再利用路径。

**来源审计**：
- `template/00-spec.md` §5 定义失败判定五条件与 `reports/failure.md` + `archive/failed.jsonl` 双归档。`chem-materials.md` 原则 05 要求 pairwise 反应数据库与图谱负样本持久化，`bio.md` 边界 01 强调干湿分离的度量不可外推。`cs-ml.md` 原则 05 要求失败产物携带 traceback。
- 等级：direct（失败报告结构、五判定条件）；supported inference（负样本剪枝 80% 搜索空间的外推需校准）

**工作区落地审计字段**：
```
reports/failure.md 固定字段：idea_id, runs[], hypothesis, evidence, root_cause{假设|实现|数据|评估}, negative_result, next_hypotheses[]
archive/failed.jsonl：每行含 run_id, idea_id, outcome: failure, metrics, trace_ref
memory_store（pairwise 反应表 / 合成校验错误 / 图谱负样本）：key, negative_evidence, first_seen_run
```

**门控**：
- 连续 3 轮无提升、2 次崩溃、审稿 2 轮低分、预算耗尽任一触发失败归档，不再重试该 idea
- `next hypotheses` 自动回注入 `archive/ideas.jsonl`，注入时携带 `parent_failure_id`

**回放要求**：
- `status.md` 顶部展示最近 3 个失败报告的 `root_cause` 与 `next hypotheses`
- `traces.jsonl` 全局追踪中 `outcome: failure` 可过滤回放
- 失败分支归档前已固化 `traces/<id>/`，`git branch -D` 不丢失证据

---

### Guardrail 05 — 评估污染隔离

**原则**：度量与评估的污染路径显式隔离，复测与抽检并行。

**来源审计**：
- `cs-ml.md` 边界 02：模拟分 5.36 接近 preprint 5.24，距接收稿 5.69 仍有差距，AI Scientist workshop 超阈值不等同主会接收，Scientist-Bench 题目抽自 SOTA 存在泄露风险。`platform.md` 原则 10 与边界 3：PaperBench 人类 PhD 41% 高于最强 agent 21%，Bench II 召回显著低于呈现，RE-Bench 基线揭示长周期瓶颈。`bio.md` 边界 03：Elo 自评 Goodhart 与小样本效力不足。
- 等级：direct（分数差距、泄露风险记载）；supported inference（held-out 与人类抽检的缓解效力）

**工作区落地审计字段**：
```
bench/scores.jsonl：{ task_id, split: held_in | held_out, metric, leakage_flag }
traces/<ts>/metrics.json：{ leakage_check: { overlapping_ids, near_duplicate_score }, judge_model, rubric_version }
reports/review.md：{ reviewer_score, rubric_version, human_spot_check: { sampled, agreement } }
```

**门控**：
- `evaluation` 前置泄露检测，命中 held-out 重叠直接标记 `leakage_flag`，不参与 keep 选举
- 数值 keeper 与语义 keeper 联合裁决，模拟分仅作内 keeper，外部对齐依赖人类抽检
- 针对单一指标优化触发偏科告警，要求多维 keeper 同步展示

**回放要求**：
- `rubric_version` 与 `judge_model` 写入 trace，支撑跨版本回归检测
- 核心任务维护人类 8 小时基线分布，模型分数与基线同图展示
- 离线语料与线上复测分别记录，时效漂移可追溯

---

### Guardrail 06 — 自动化权限分级与安全互锁

**原则**：能力按风险分级，权限在编排层强制执行。

**来源审计**：
- `chem-materials.md` 原则 02/03：validate → execute 两段式与 GHS pre_filter 显式阻断，Coscientist 缺失独立校验被列为反例。`physics-crossdomain.md` 原则 05 强调 AI 决策与确定性内核硬边界。`platform.md` 边界 01 要求真实实验硬件依赖显式标注。`template/00-spec.md` 保留 SDL 扩展点，不直接对接物理仪器。
- 等级：direct（validate 返回 `{valid, errors[]}`、GHS 工具链、UniLabOS 协议约束）；supported inference（分级权限映射到软件工作区的通用性）

**工作区落地审计字段**：
```
capabilities/registry.json 扩展：
  safety_tags: string[]
  requires_approval: boolean
  endpoint: local | remote | sim
  hardware_dependency_level: 0_纯软件 | 1_需仿真校准 | 2_需硬件在环
  pre_filter: { tool: "chem.safety.ghs", policy }
orchestration/config：human_gate 阈值与重试上限
```

**门控**：
- 任何 `execute` 前强制 `validate`，`valid == false` 触发结构化错误回灌，不进入物理或高成本分支
- `requires_approval == true` 的操作进入人工确认队列，需显式批准
- `schedule_prompt` 夜间自治仅允许 `hardware_dependency_level == 0` 的任务自动执行

**回放要求**：
- `pre_filter` 判定结果与 `errors[]` 完整落盘，关联到 `traces/<ts>/reasoning.md`
- 跨站点执行的远程指令保留多级互锁日志与硬件指纹校准参数
- 安全工具输出错误单独审计，避免级联误判进入推理层

---

### Guardrail 07 — 人类复核点与分叉裁决

**原则**：人类在高层分叉点行使否决与追加，执行层自治。

**来源审计**：
- `bio.md` 原则 11：Virtual Lab 人类仅在分叉点否决或追加目标，计算侧占 94%。`cs-ml.md` 原则 09 要求 `human_in_the_loop: true` 对物理执行、外部发布、资金、生物安全强制确认。`chem-materials.md` 原则 03 要求危险操作进入人工队列。`platform.md` 边界 02 要求私域融合与计费激励延后验证。
- 等级：direct（分叉点介入形态、94% 工具耗时）；supported inference（阈值门控对带宽释放的具体数值）

**工作区落地审计字段**：
```
WATCHDOG.yml：{ human_gate: { threshold, scope: [publish|hardware|budget|safety] }, human_feedback: "natural-language" }
status.md：{ pending_reviews: { run_id, metric_delta, review_score, gate_reason } }
hub 消息：{ type: human_decision, decision: approve | veto | redirect, rationale }
```

**门控**：
- `evaluation` 到 `writing`：主度量 delta 超 epsilon 自动 keep，低于阈值但接近边界的 keep 进入待复核队列
- `review` 到 `archive`：分数阈值以下回退到 `modeling`，连续 2 轮低分触发人类复核
- `schedule_prompt` 晨间复盘生成 `status.md`，人类一键 retain 新假设或关闭队列

**回放要求**：
- 人类决策与 `meeting/trace` 双产物关联存储
- 分叉点视图保留策略与执行的分离日志，支持责任定位
- 人类反馈直通 Meta-review，下一轮生成方向可追溯

---

### Guardrail 08 — 跨域迁移显式边界校验

**原则**：跨域迁移前显式校验领域边界，不变量缺失时降级为探索模式。

**来源审计**：
- `physics-crossdomain.md` 边界 1/2/3：可形式化不变量边界、经济与可复现性边界、自主性与深度权衡边界。`chem-materials.md` 边界 1/2：固相与液相物理不可迁移性、仿真规模与保真度上限。`bio.md` 边界 02：工具规模化与环境复现成本边界。`cs-ml.md` 边界 01：单 GPU 短预算循环的适用边界。
- 等级：direct（三组边界的事实依据）；supported inference（"云端借用+硬件指纹校准"的经济性权衡）

**工作区落地审计字段**：
```
capabilities/registry.json：{ domain: cs | bio | chem | physics | platform, transferability: { invariants[], known_gaps[] } }
program.md：{ scope_constraints: string[], out_of_scope: string[] }
traces/<ts>/metrics.json：{ domain_gate: { passed, failed_checks[] } }
```

**门控**：
- 跨域能力调用前校验不变量清单，缺失可形式化不变量时标记探索模式，不进入 L2 表征或外部发布
- 仿真结论跨域复用时强制分层验证（快速仿真 → 精确仿真 → 实验），单层结论不外推
- 通用助理跨 8 域场景需显式取舍，单域深度不足时触发专家 Critic 增强

**回放要求**：
- 领域边界检查报告落盘为 `reports/domain-gate.md`
- 跨域迁移的假设谱系保留 `parent_ids` 与域标签，支持谱系回溯
- 开放式探索任务引入 L3 人工物理审查记录

---

### Guardrail 09 — 双 keeper 联合裁决与预算分层

**原则**：数值性能与语义质量双阈值联合裁决，预算按探索与收敛分层。

**来源审计**：
- `cs-ml.md` 原则 07/01/06：双 keeper 架构成熟于 Karpathy val_bpb + CycleReviewer 语义分，wall-clock 固定预算赛马支撑 UCB 资源分配。`platform.md` 原则 09 要求防伪闸门与 smoke test。`physics-crossdomain.md` 原则 02/03 要求分级熔断与残差自验证。
- 等级：direct（双 keeper 形态、5 min 预算、MAE -26.89% 校准数据）；supported inference（预算分层对收敛期的增益）

**工作区落地审计字段**：
```
orchestration/config：{ keepers: [{name: numeric, metric: val_bpb, threshold: epsilon}, {name: semantic, metric: reviewer_score, threshold}], budget_tiers: { explore: 300s, converge: 900s } }
traces/<ts>/metrics.json：{ keeper_votes: { numeric: pass|fail, semantic: pass|fail, conflict: boolean } }
```

**门控**：
- 任一 keeper 不达标即 discard，冲突时走 PI 裁决，收敛期加 held-out 复测
- 探索期短预算海选，收敛期长预算复测，超阈值自动切换 tier
- `eval` 前置 `compile_check` 与 `minimal_run` 两层烟雾测试

**回放要求**：
- 每轮 `keeper_votes` 与阈值写入 `traces.jsonl`，支持 keeper 敏感度分析
- 冲突案例单独归档，关联到 `reports/review.md` 的逐条意见
- 预算指纹与 keeper 结果同图展示，支撑成本效益审计

---

### Guardrail 10 — 独立验证层与多样性闸门

**原则**：生成与验证分离部署，检验信号独立于生成信号。

**来源审计**：
- `physics-crossdomain.md` 原则 03/04：残差与守恒量无监督验证，物理合理性独立检查；`bio.md` 原则 02/03：Critic 独立部署与确定性 workflow；`cs-ml.md` 原则 02/10：异常回溯局部修复与 U 标记验证门控；`platform.md` 原则 03：推理与执行治理分离。
- 等级：direct（残差/守恒三项必检、Critic 独立 prompt、U=0/1 标记）；supported inference（多样性采样抗 mode collapse 的阈值设定）

**工作区落地审计字段**：
```
capabilities/registry.json：{ verifier: { type: residual | conservation | dimensional | physical_sanity | critic, version } }
traces/<ts>/verification.json：{ L1_gates: [{check, result, evidence}], diversity: { distinct_modes, coverage } }
world-model.json：{ edges: [{ claim, U: 0|1,验证证据 }] }
```

**门控**：
- 计算任务强制 L1 三项必检（残差、守恒量、量纲），未通过不进入 L2 表征或人工审查
- 验证器与生成器分离版本管理，同源偏差单独告警
- idea 到 plan 阶段设置多样性闸门，`distinct_modes` 未达阈值不进入执行

**回放要求**：
- 验证脚本独立版本落盘，检验日志与生成日志分文件存储
- `world-model.json` 仅 `U=0` 边可作为后续假设前提，`U=1` 需先验证再构建
- 失败验证案例触发 `gap_discovery.py` 结构化空白发现

---

### Guardrail 11 — 版本化记忆与锦标赛审计

**原则**：记忆分层版本化，锦标赛过程可审计。

**来源审计**：
- `physics-crossdomain.md` 原则 06/07：状态图编排与 Docker 隔离、知识图谱记忆与锦标赛。`bio.md` 原则 06/10：假设谱系与 Elo 锦标赛、双轨环境。`cs-ml.md` 原则 03/10：树搜索与三级记忆。`platform.md` 原则 05：论文即能力与向量检索复利。
- 等级：direct（状态图、Elo 更新、tree.json、world-model.json 形态）；supported inference（图谱增量对跨轮复利的量化）

**工作区落地审计字段**：
```
memory_store：{ graph_nodes: [{id, type: 文献矛盾|假设谱系|实验结果, version}], edges: [{from, to, relation}] }
channels/<id>/tree.json：{ nodes: [{idea_id, parent, score, status}], tournament: {elo_board, comparisons[]} }
archive/ideas.jsonl：{ idea_id, parent_ids, elo, generation_round }
```

**门控**：
- 假设谱系通过 `read` 继承，缺失 `parent_ids` 的假设标记孤立，需补充溯源
- 锦标赛采样按 reward 正比，多样性不足时触发重采样
- 低质内容污染检索库时触发质量闸门，引用次数与验证通过率加权排序

**回放要求**：
- 记忆读写纳入版本化落盘，`hub` 登记检查点，支持中断恢复与回溯修正
- `channels/elo-board.md` 与 `debate-{round}.md` 保留锦标赛全过程
- 跨任务检索复用时注入来源版本与血缘标注

---

## 4. 横向不确定性（5 条）

### 不确定性 01 — Elo 自评与湿实验成功率的外推鸿沟

Co-Scientist 的 Elo 与 GPQA 正相关建立在 15 目标小样本与 11 人评上，`bio.md` 边界 03 与 `platform.md` 边界 03 共同指向 Goodhart 风险。Elo 在计算基准上的提升外推到湿实验成功率缺乏直接校准。工作区在引入 `elo-tournament` 时，Elo 仅作为内排序信号，外部发布前需湿实验锚点或 held-out 前瞻性验证。等级：supported inference。

### 不确定性 02 — 仿真-实验鸿沟的保真度上限

MatterGen 预训练限定 ≤20 原子体系，DFT 0K 近似与 MatterSim 误差随体系复杂度上升，`chem-materials.md` 边界 02 与 `physics-crossdomain.md` 边界 1 共同表明仿真结论的理论稳定不等同可合成。生成器只认 `score(structure)` 的统一契约在多约束 Pareto 冲突下可能掩盖动力学与缺陷。工作区分层验证可缓解，无法消除该鸿沟。等级：direct（MAE 36 meV/atom、0K 近似记载）与 speculative（大晶胞外推能力）并存。

### 不确定性 03 — 工具规模化与检索精度的权衡拐点

Biomni 150 工具与 TxAgent 211 工具验证了注册表驱动的规模化，`bio.md` 边界 02 与 `chem-materials.md` 原则 04 指明检索精度下降、描述不规范、异构返回标准化的成本拐点尚未量化。ToolRAG Top-K 过滤在 300+ 规模下的召回稳定性缺少实测。工作区需在 `capabilities/registry.json` 上配套强校验与统一 schema，拐点需在运行中实测标定。等级：supported inference。

### 不确定性 04 — 自主性与领域深度的取舍

Denario 通用指令退化为被动助手、Rumi 跨 8 域通用但单域深度不足、Agent Index 自主性分级共同指向通用与专用的张力，`physics-crossdomain.md` 边界 3 明确天文因数据开放最顺滑，化学因硬件异构最难泛化。工作区在 `program.md` 中做显式取舍时，取舍阈值的普适性缺乏跨域对照。等级：supported inference。

### 不确定性 05 — 开放式假设生成的评估有效性

Biomni 开放式假设生成弱于专用系统，PaperBench 复制任务人类 41% 显著高于 agent 21%，Bench II 召回短板揭示评估本身在缺乏参考答案的探索性任务上适用性下降，`platform.md` 边界 03 与 `cs-ml.md` 边界 02 共同表明 LLM 互评易被污染。工作区对高度开放任务的 rubric 需依赖人类一致性标定，标定成本与时效构成持续不确定性。等级：direct（41% vs 21% 差距）与 speculative（新颖性度量的主观性）并存。

---

## 5. 工作区实施清单

| 实施项 | 落位文件 | 关联 Guardrail |
|--------|----------|----------------|
| 假设三字段校验脚本 | `orchestration/hooks/pre-run.sh` | GR01 |
| 环境指纹与设备指纹采集 | `traces/<ts>/metrics.json` + `cost.json` | GR02 |
| 三级溯源与 FACT 校验 | `navigator/evidence/*.json` + `eval` | GR03 |
| 失败双归档与回注 | `reports/failure.md` + `archive/failed.jsonl` | GR04 |
| 泄露检测与 held-out 复测 | `bench/scores.jsonl` + `hub` 广播 | GR05 |
| validate→execute 与 GHS pre_filter | `capabilities/registry.json` | GR06 |
| 人类分叉点看板 | `WATCHDOG.yml` + `status.md` | GR07 |
| 域边界校验器 | `program.md` + `reports/domain-gate.md` | GR08 |
| 双 keeper 与预算分层 | `orchestration/config` | GR09 |
| L1 独立验证层 | `traces/<ts>/verification.json` | GR10 |
| 版本化记忆与锦标赛 | `world-model.json` + `tree.json` + `elo-board.md` | GR11 |

验证标准：任一 `traces/<ts>/` 缺失审计字段即判定该轮不可回放；任一门控绕过即阻断下游阶段；所有 guardrails 的审计字段纳入 `traces.jsonl` 全局追踪。

---

## 6. 来源索引

- Layer 1 五份：`debate/layer1/bio.md`、`debate/layer1/physics-crossdomain.md`、`debate/layer1/chem-materials.md`、`debate/layer1/cs-ml.md`、`debate/layer1/platform.md`
- 渠道索引：`channels/README.md`（46 条全量索引）
- 工作区规格：`template/00-spec.md`（七阶段状态机与文件契约）
- 渠道详述：`channels/06-stanford-virtual-lab.md`、`07-stanford-biomni.md`、`08-google-co-scientist.md`、`09-futurehouse-robin.md`、`10-txagent-biomed.md`、`11-coscientist-cmu.md`、`12-chemcrow-epfl.md`、`13-sciagents-mit.md`、`14-sdl-toronto-berkeley.md`、`15-mattergen-microsoft.md`、`16-bohrium-scimaster.md`、`17-agent-laboratory-agentrxiv.md`、`18-deep-research-platforms.md`、`19-benchmarks-eval.md`、`20-physics-autonumerics.md`、`21-denaro-rumi.md`、`22-cloud-synthesis.md`、`23-misc-university-labs.md` 及其汇总 `_index-*.md`

> 写作约束：全篇采用直接、加和式陈述，证据等级显式标注，推断边界单独说明，落地字段可直接映射到工作区目录与门控脚本。
