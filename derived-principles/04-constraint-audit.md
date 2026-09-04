# 约束审计 — 2026-09-04

> 触发：连续观察到两类失败。失败 A（调查缺失）：modeler 在对任务、上下文一无所知的情况下，凭空写了一个与任何 idea、任何 profile 都无关的"最小二乘" Python 脚本——18 世纪的基线方法冒充研究成果。失败 B（偷懒拖时间）：agent 规则里的保守套话（"minimal patch" 一类以英文写进模板、再以中文空话形式扩散的措辞）被模型读成"做得越少越好、拖时间费 token 也算完成任务"，甚至用无意义的检查（检查编译器/系统产物）冒充真正的测试。
>
> 结论先行：问题不是"约束太多"或"约束太少"，而是**约束错位**——对正确性、完整性、可复现性的约束很强（keeper gate、append-only、指纹），但对**调查义务、任务量下限、产出真实性**的约束是零，甚至存在反向激励。

## 一、过头 / 反向激励的约束（必须改写）

| # | 位置 | 原文 | 为什么过头 |
|---|---|---|---|
| O1 | `.omp/agents/modeler.md` 工作序 2 | "Implement the idea's `method` as a **minimal patch**" | "minimal" 是对改动方式的修饰，模型读成"产出最小"的直接授权。最小二乘事故的直接温床：写个短脚本最"minimal"。改成：patch 范围由 `mutable_paths` 与预注册 method 界定，**method 必须完整实现**，不以行数论英雄。 |
| O2 | `.omp/rules/task-dispatch.md` + AGENTS.md 派遣协议 | "Skip formatters and project-wide test suites inside subagents; runtime gates are the verification" | 本意是省 token，被读成"不用做测试"。runtime gates 只是**下限**不是全部：改动涉及的行为必须有针对性验证。 |
| O3 | `.omp/agents/idea-generator.md` 规则 2 | "each idea implementable as a patch **under 50 lines**" | 行数上限惩罚一切有实质内容的方法，系统性偏向琐碎改动。改为"单机制、单轮可完成"的范围约束，去掉行数崇拜。 |
| O4 | `.omp/agents/literature-scout.md` | "Read these sources **and nothing else**" | 调查被明文禁止。scout 只许看工作区内 5 个文件，前沿进展在制度上不可达。这是失败 A 的制度根源：整个飞轮没有任何角色被授权（更别说被要求）看外部世界。 |
| O5 | AGENTS.md 会话启动 | "Recalled memory is a search hint, never a fact source" | 合理，但与 O4 叠加后，agent 的信息宇宙只剩工作区内部文件。 |
| O6 | 无任务量约束 | — | 每轮"改善"没有最小实质要求：模型可以写一个 20 行的无关脚本、跑一个无意义检查、宣布完成。token 花了，工作量为零。 |

## 二、缺失的约束（必须新增）

| # | 缺口 | 新条款（落地见 `.pi/rules/` 与 agents 模板） |
|---|---|---|
| M1 | 调查前置 | 任何 idea 生成与建模动手前，必须先调查前沿：文献/开源实现/SOTA 基线。调查结论写入 navigator/，**必须包含拉取到本地的真实证据**（仓库、代码、数据），纯文字转述不算完成。 |
| M2 | 任务量约束 | 每个阶段有明确的最小实质产出定义（method 实现完整、验证覆盖被改行为、证据文件真实存在）。"完成"由产出定义，不由耗时或检查次数定义。 |
| M3 | 反空话 | 产出必须与 idea 的 hypothesis/method 有可追溯联系；与任务无关的产物（示例脚本、无关 demo）按 execution_error 处置。 |
| M4 | 检查真实性 | 禁止用环境检查（编译器版本、系统产物、无断言的命令）冒充测试。验证 = 对被改行为的断言，失败的验证必须留痕。 |
| M5 | 审计人格 | analyst（审计）与 reviewer-skeptic（找茬）模板升级为恶毒反驳 + 激进找茬人格：默认有罪推定，专门找茬，找不到致命问题才允许 pass。 |
| M6 | pi 配置 | 工作区没有任何 pi 配置（agents/rules/workflows/prompts 全部塞在 OMP 的 `.omp/` 里）。按 qwen 工作区结构迁移到 `.pi/`。 |

## 三、保留不动的约束（审计确认正确）

- keeper gate 的确定性条款（RULES.md 1-8）：与本次失败无关，是飞轮的骨架。
- `evaluation/prepare.py` / `program.md` / integrity_paths 冻结：正确。
- uv fresh-process 门控与指纹（package_lock_hash）：正确；qwen 工作区的 python-evidence 是旧版（python3 回退），迁移时以本仓库新版为准。
- append-only 证据纪律：正确。

## 四、OMP/orca 叙事处置

pi 本身运行在 Orca 之上——涉及 Orca 运行时的事实性表述（如"本工作区通过 Orca 打开终端"）**保留**；OMP 产品叙事（`.omp/` 目录、OMP eval 持久内核、`omp/task/<id>` 分支、`xd://` 设备、`@task`/`@smol` 模型别名、OMP 原生发现）**废除**，替换为 pi 原生等价物（`.pi/` agents/rules/workflows、`isolation: "worktree"`、subagent `agent:` 参数、schedule_prompt 扩展）。历史记录（debate/、derived-principles/ 的研究性叙述、archive/）不动——它们是证据，不是活规则。
