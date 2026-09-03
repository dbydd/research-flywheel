# Template 映射与处置清单 v1.0

> 定位：`derived-principles/00-design-philosophy.md` 与 `01-principles-registry.md` 到 `template/*.md` 的落地映射。明确每份 template 文档保留、修改或延后的处置，给出最小改动清单与验收锚点。
> 输入：`template/00-spec.md`、`01-workspace-layout.md`、`02-harness-wiring.md`、`03-inspiration-engine.md` 四份现行规格 + 两份 Layer 3 合议结果。
> 约束：保持改动小且可审计，只修改映射中列出的目标位置，不引入新文件或重写整篇。
> 版本：2026-09-02

---

## 0 处置总表

| 模板文件 | 处置 | 关联原则 | 改动幅度 | 验收锚点 |
|---------|------|---------|---------|---------|
| `template/00-spec.md` | 保留并局部修改 | P01, P02, P03, P06, P07, P08, P11, P12 | 中：接入 task isolation、runtime lifecycle、requested/actual cost 与 clean reproduction，保持七阶段拓扑 | baseline/mutation 完整，completed keeper 前置项齐全 |
| `template/01-workspace-layout.md` | 保留并局部修改 | P01, P02, P03, P04, P09, P10, P12 | 中：扩展目录树、profile、权限与候选归并契约 | changed_paths、integrity hash、lifecycle 与 error envelope 可验证 |
| `template/02-harness-wiring.md` | 保留并局部修改 | P01, P02, P03, P04, P11, P12 | 中：使用真实 task isolation、eval 与 schedule_prompt wire shape | branch 候选、eval reset、lifecycle 终态与干净复现可回放 |
| `template/03-inspiration-engine.md` | 保留并局部修改 | P06, P10 | 小：补充去重阈值与多样性闸门，不改三段式形态；约束多样性作为延后扩展，不单列首期原则 | ideas.jsonl 三字段完整，queued 增量可度量 |
| `template` 新增 SDL/GFlowNet/联邦调度章节 | 延后 | 延期 01/02/05 | 零：首期不进入主干，仅保留扩展点占位 | registry.json endpoint 仅 local\|sim |

处置含义：
- 保留：主干机制已获两份 Layer 3 裁决一致肯定，无需结构调整。
- 修改：字段、阈值、门控、验收信号需补齐，以满足合议验收条件。
- 延后：机制有价值但依赖真实硬件、reward 建模或多租户治理，首期不进入主干。

---

## 1 template/00-spec.md — 保留并局部修改

**保留理由**：七阶段状态机、度量契约、失败路径、harness 接线四项为地基。两份 Layer 3 裁决一致以 `00-spec.md` §2.1 状态图为直接规范来源，`architecture.md` 决议 01 已做归一。状态机形态与目录交集正确，无需重构。

**修改清单**：

| 位置 | 现状 | 修改内容 | 关联原则 | 改动行数估计 |
|------|------|---------|---------|-------------|
| §1.2 可度量目标 | 已定义零启动成本与双终态归档 | 增加 baseline、candidate branch、lifecycle、requested/actual cost、fingerprint 与 clean reproduction 审计目标 | P01, P03, P12 | 3 行 |
| §2.1 七阶段状态机表格 | 已定义阶段输入输出与准入契约 | modeling 输出 isolation candidate，experiment 输出 lifecycle/error，evaluation 仅接收 completed execution 与完整指纹 | P01, P03, P07, P12 | 3 行 |
| §3.1 核心文件与 metrics 契约 | 旧版资源与候选元数据粒度不足 | 增加 `.omp/config.yml` isolation 配置、baseline/mutation 文件、stage requested/actual cost、execution/evaluation state 与 fingerprint | P01, P03 | 12 行 |
| §5.1 失败判定 | 已定义五条件 | 在审稿连续 2 轮低分条件后补充 `U=1 假设不进入 L2 表征` 的降级说明 | P06, P08 | 1 行 |
| §5.2 失败报告契约 | 已定义六段结构 | 补充 `hypothesis` 需含三字段 `falsifiable_statement/predicate/negation_criterion` 的引用 | P06 | 1 行 |

**保持项**：七阶段状态图拓扑、与已调研系统的对应关系、双终态知识归档目标持续有效。夜间语义增加 queued/paused 恢复与 lifecycle 归因。

**延后**：SDL 扩展点保持 `template/00-spec.md` §1.3 非目标中已有的“不直接对接物理仪器”表述，不新增硬件章节。

**验收**：scaffold 形成 Git baseline 与 `.omp/config.yml` isolation 配置。首轮证据包含 baseline、mutation、lifecycle、cost，以及 completed metrics 或结构化未完成终态；keeper 关联 clean reproduction。

---

## 2 template/01-workspace-layout.md — 保留并局部修改

**保留理由**：目录树、文件契约、读写边界、git keep/discard 四项为工作区骨架。两份 Layer 3 裁决一致以 `01-workspace-layout.md` §3 权限表为实现来源，单机可跑通首轮 `metrics.json` 的验证标准正确。

**修改清单**：

| 位置 | 现状 | 修改内容 | 关联原则 | 改动行数估计 |
|------|------|---------|---------|-------------|
| §2 完整目录树 | 已含 program/prepare/run/capabilities/navigator/traces/reports/archive/bench/orchestration | 在 trace 包加入 `baseline.json/mutation.json/lifecycle.jsonl/error.json`，将 `git.patch` 标为可选，将项目配置修正为 `.omp/config.yml` | P01, P03, P09, P12 | 6 行 |
| §3 文件职责与读写权限表 | 已定义角色边界 | 使用 `program.md` frontmatter 的 `mutable_paths/integrity_paths`，记录 baseline manifest、candidate metadata 与 runtime lifecycle | P01, P03, P11 | 6 行 |
| §3.3 metrics.json 契约 | 旧版资源字段粒度不足 | 改为 execution requested/actual、stage/state、device/environment fingerprint 与 completed evaluation | P03 | 10 行 |
| §4 Agent 可编辑边界 | 旧版候选写入边界缺少隔离执行语义 | modeling 在 isolated merged view 直接编辑 `mutable_paths`；orchestration 校验 changed paths 与 integrity hash；approval mode 明确为工具调用审批层 | P01, P11 | 8 行 |
| §5 Git 分支与 keep/discard | 已定义 keep/discard 语义 | 补充 `discard` 保留 `traces/<id>/` 到 `archive/discard-<id>/` 前已固化 `verification.json` 的说明 | P02, P08 | 1 行 |

**保持项**：`program.md` 的目标与 plan DAG、目录主干、mermaid 数据流、一键 scaffold 入口持续保留。frontmatter 增加 machine-readable experiment profile。

**延后**：`knowledge_graph` 与 `memory_store` 图谱章节不进入主干目录树，保留为 `archive/failed.jsonl` 轻量 pairwise 表。

**验收**：candidate changed paths 全部匹配 `mutable_paths`，integrity hash 与 baseline 一致，parent checkout 保持 baseline SHA。mutation 记录 resolved backend 与 candidate branch，lifecycle 记录当前状态。

---

## 3 template/02-harness-wiring.md — 保留并局部修改

**保留理由**：task/eval/hub/schedule_prompt/trace 五组件接线正确。两份 Layer 3 裁决一致以 `02-harness-wiring.md` §3 为 Harness 原生能力映射，`schedule_prompt` 30-60 分钟夜巡与 `hub` 三频道 `idea-claimed/keep-decision/review-score` 经双视角校验。

**修改清单**：

| 位置 | 现状 | 修改内容 | 关联原则 | 改动行数估计 |
|------|------|---------|---------|-------------|
| §1 接线总览表 | 已含五组件映射 | task 行接入 `isolated: true` 与 branch capture；eval 行接入 retained exploration、clean gates 与 cold-start reproduction；trace 行加入 lifecycle/cost | P01, P03, P12 | 4 行 |
| §3.1 task 并行探索 | 旧版候选输出缺少 isolation metadata | 配置 `task.isolation.mode: auto/apply: false/merge: branch`，使用真实 task 参数，说明 `runIsolatedSubprocess`、`isoResolve/isoStart/isoDiff` 与 rcopy fallback | P01 | 12 行 |
| §3.2 eval 运行时 | 旧版接线缺少真实工具协议与状态边界 | 使用真实 eval `{language,code,title,timeout,reset}` 参数；定义 clean compile/smoke、retained exploration、cold-start reproduction 与 error envelope | P12 | 24 行 |
| §3.4 候选归并 | 旧版归并缺少 isolation branch metadata | 使用 isolation branch metadata，keeper 前验证 completed execution/evaluation、actual cost、fingerprint 与 clean reproduction | P01, P03, P12 | 8 行 |
| §3.5 schedule_prompt 夜间循环 | 旧版注册形态与实验期限耦合 | 使用 `xd://schedule_prompt` 的 add/list wire shape，恢复 paused checkpoint，实验 deadline 由 stage profile 与 runtime lifecycle 管理 | P03, P11 | 12 行 |

**保持项**：task/eval/hub/schedule_prompt/trace 的组件职责与七阶段业务流保持稳定。图中节点、Trace 事件和 wrapper 伪代码同步新运行契约。

**延后**：联邦调度与多租户计费章节不新增，保持 §1 非目标中已有的扩展点占位。

**验收**：schedule_prompt `action: list` 返回夜间与晨间两项；isolated candidate 留下 branch metadata；eval clean gate 使用 `reset: true`；trace 包含 lifecycle、actual cost、error envelope 或 completed metrics；keeper 关联 cold-start reproduction。

---

## 4 template/03-inspiration-engine.md — 保留并局部修改

**保留理由**：三段式 `seed → generation → debate → gating → pool` 与 Sakana/Co-Scientist/Virtual Lab 三式取舍正确。两份 Layer 3 裁决一致以 `03-inspiration-engine.md` 全篇为灵感引擎直接规范，单次 5 个、2 次 LLM 调用、本地 PI 门禁的成本约束经双视角校验。

**修改清单**：

| 位置 | 现状 | 修改内容 | 关联原则 | 改动行数估计 |
|------|------|---------|---------|-------------|
| §1 目标与约束 | 已定义可执行、可度量、可证伪与 2k tokens 预算 | 在可证伪约束后补充三字段 `falsifiable_statement/predicate/negation_criterion` 缺失阻断入队的显式说明 | P06 | 1 行 |
| §3.1 Seed 来源表 | 已含人类/失败报告/检索 gaps/随机扰动四类 | 在失败报告行补充 `archive/failed.jsonl: next hypotheses` 携带 `parent_failure_id` 回注的说明 | P10 | 1 行 |
| §3.2 Generation 去重 | 已定义 embedding 余弦 0.85 阈值与缺字段丢弃 | 补充去重同时校验 `U` 标记与 `parent_ids` 血缘的说明，缺失 `hypothesis/method/expected_delta` 任一字段直接丢弃不重试 | P06, P10 | 2 行 |
| §3.3 Debate 加权排序 | 已定义 `0.5*score + 0.3*feasibility/5 + 0.2*novelty` 取 top-3 | 补充 `distinct high-reward modes` 未达阈值不晋升执行的闸门说明，Critic 关注 `leakage/unreproducible` 风险 | P06, P08 | 2 行 |
| §3.4 Gating PI 门禁 | 已定义五条本地规则 | 补充与 `WATCHDOG.yml` 的联动：涉及 `publish/hardware/budget/safety` 的 idea 需人工确认 | P11 | 1 行 |

**不改动**：三段式 mermaid、Seed 收集伪代码、产物示例 JSON 形态保持不变。

**延后**：GFlowNet 按 reward 正比采样与知识图谱持续演化章节不进入主干，保留为延后项，激活条件为 `archive/failed.jsonl > 50` 且出现 `mode collapse` 信号。

**验收**：`python orchestration/inspiration.py --once` 在 `archive/ideas.jsonl` 新增 2 行且 `inspiration.md` 被更新，`jq 'select(.hypothesis.falsifiable_statement==null)' archive/ideas.jsonl` 计数为零，`grep -c queued archive/ideas.jsonl` 增量可度量。

---

## 5 延后项与激活条件

以下 5 项在两份 Layer 3 裁决一致延后，首期不修改 template 主干。满足激活条件后以增量文件进入。

| 延后项 | 涉及 template | 激活条件 | 证据等级 |
|-------|-------------|---------|---------|
| SDL 真机闭环与硬件指纹校准 | `02-harness-wiring.md` §1 扩展行、`01-workspace-layout.md` capabilities 行 | `capabilities/registry.json` 出现 `endpoint: remote` 且 `hardware` 分面通过 `validate→execute` 仿真分支验证，`safety_tags` 覆盖率达标 | 高 direct |
| GFlowNet 多样性采样与知识图谱持续演化 | `03-inspiration-engine.md` 扩展章节、`01-workspace-layout.md` 根 `world-model.json` | `archive/failed.jsonl` 累积超 50 条且出现 `mode collapse` 信号，或跨运行复用预期超单次构建成本 | 中 supported inference 到 speculative |
| 多租户计费与私域 Workspace 融合 | `02-harness-wiring.md` 扩展行 | `trace` 与评估稳定且出现多用户共享同一实例需求 | 中 supported inference |
| 人类 8 小时基线对照与作者共创 rubric 大规模校准 | `00-spec.md` §1.2 评估段扩展 | 飞轮在单一赛道连续产出 5 个 keep 且需对外宣称质量分，或语义 keeper 连续触发背离告警 | 高 direct |
| 跨站点联邦调度与硬件指纹差异建模 | `02-harness-wiring.md` §3.3 扩展 | 本地飞轮验证通过且需借用云端能力扩展吞吐，以 `endpoint: remote` + `hardware_fingerprint` 增量接入 | 高 direct |

---

## 6 最小改动执行顺序

1. `template/00-spec.md` 扩展 metrics 契约与失败判定字段
2. `template/01-workspace-layout.md` 扩展目录树与权限表
3. `template/02-harness-wiring.md` 补充 eval 双门控与 hub 分叉点视图
4. `template/03-inspiration-engine.md` 补充三字段门控与多样性闸门

每步改动后执行对应验收命令，改动小且可审计。延后项不阻塞主干，满足激活条件后单独评估。

## 验证命令

```bash
ls template/*.md derived-principles/*.md
grep -c '^| `template/.*` | 保留并局部修改' derived-principles/02-template-mapping.md  # 期望 4
grep -c "延后" derived-principles/02-template-mapping.md  # 期望 >=5
grep -c "验收" derived-principles/02-template-mapping.md  # 期望 4
```
