# Harness Playbook 吸收 — stencil.so/blog/harness-playbook

> 调查证据（本地留存，拉取日期 2026-09-04）：
> - `harness-playbook.html` / `harness-playbook.md` — 原文完整存档（stencil.so，omp² postmortem + playbook）。
> - `pi-mono/` — Pi 框架源码 clone（commit `dd7e816b57dedbe971d159b388f48317a6139079`），playbook 中 "78 个官方 Pi extension 示例" 等论断的验证底座。
> 纯文字转述不构成调查证据；本目录即调查前置条款（M1）的示范执行。

## 概念 → 本工作区改造映射

| Playbook 概念 | 原文要点 | 本工作区落地 |
|---|---|---|
| One authoritative session | 状态必须可从单一日志源推导；两个权威源 = rewind/resume 全部失真 | 飞轮已有单一权威：`traces/` + ledger append-only，runtime 独占终态。保留，并新增"PI 侧 Session 纪律"：agent 的 todo/goal 状态写入文件系统权威位置，不藏在会话内存里（HANDOFF.md 是唯一交接权威） |
| Trusted control plane / dumb executor stub | 宿主持有政策与密钥；沙箱只拿"听话的执行桩" | 子 agent 模板显式声明 `tools`/`acceptanceRole`/`inheritProjectContext: false`——子 agent 起步空白、只拿路径不拿 blob（原条款保留并强化） |
| Bounded work / job primitive | 一切后台物是同一个可取消、可观测、有中央限额的 job | 派遣协议：每个 subagent 任务显式带验收契约（completionGuard / acceptanceRole），并行评审用一次批量派遣；不引入各自的轮询/取消私货 |
| **Directors（反偷懒核心）** | Director 栈拥有 agent loop；候选 yield 被 Plan 拦截，`force_tool("write")` + 有界重试，模型**不写完就不许 yield** | 落地为 pi 原生等价物：agent 模板的 acceptanceRole + 输出契约硬条款（"未写 X 不得返回"）+ workflow 的 stage gate。规则层写入 M2 任务量约束：完成由产出定义，不由耗时定义 |
| Forced tool calls 升级链 | 软提示 → 原生 flag → 有界重试 → 上报失败 | modeler 的 repair 纪律保留（最多一轮修复，第二失败必须结构化上报而非硬撑） |
| 中央限额、一次性截断 | 截断/预算在中央做一次，opt-out 而非 opt-in | report-writing 规则已禁截断 stderr；新增 M4：禁止用环境检查冒充测试 |
| Quirks 是结构化知识 | 兼容性知识单点持有，不散落在分支里 | uv/python 版本契约集中在一个规则文件（python-evidence），其他文件引用不复制 |
| Small permanent tool roster | 23 工具 vs 5 工具：schema 税拖慢每轮 | agents 模板 tools 字段保持最小集（read/grep/find[/bash/write]），不滥发工具 |
| Deep Read / 拉取真实资源 | 调查要 materialize 资源本身，不是读摘要 | **M1 调查前置**：把相关仓库/代码/数据拉到本地留存（本 README 即示范），文字转述不算证据 |
| Debug protocol as verification | 用可检查的协议验证，不信"看起来对" | M4 检查真实性条款：验证 = 对被改行为的断言；reproducibility reviewer 本地重跑实测值的条款保留 |
| Embrace suffering（Ousterhout） | 复杂性下推到单一持有层，别让每个调用者背一份 | 本仓库的对应物：keeper gate / 完整性 / uv 契约全部收在 runtime + 两个规则文件里，agents 模板引用而不复制 |

## 未采纳（及理由）

- 单一 session DOM / ConVar / 组件渲染管线：这些是 harness 引擎（omp²/pi 内核）层的架构，属于 `pi-mono` 的地盘；本仓库是科研飞轮模板，不是引擎。引擎层问题通过升级 pi 本体解决，不在模板里重造。
- Python 扩展运行时 / `@remote` RPC：同上，引擎层能力。

## 一句话总纲

**把"反偷懒"从希望变成结构**：Director 思想的可移植部分 = 在 agent 能 yield 之前，用制度（验收契约 + 硬性产出 gate + 本地证据留存）拦截空手而归；把"调查"从美德变成义务，且义务的计量单位是拉到本地的真实物料，不是写过的字数。
