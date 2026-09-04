# Handoff

## 当前真实状态（2026-09-04 重构后）

本仓库是**模板仓库**：给其他科研工作区当初始化模版用（`bash orchestration/scaffold.sh` 即可 scaffold 一个新工作区）。仓库内没有需要保护的实验产物；`runs/`、`traces/`、`archive/` 里是参考 profile 的历史验证记录，保持只读。

本工作区通过 pi（pi coding harness）驱动，pi 运行在 Orca 之上（Orca 负责工作区/终端编排，这是运行时事实，不属于飞轮逻辑）。

## 2026-09-04 重构记录（本次 handoff 的由来）

触发：连续两类失败（详见 `derived-principles/04-constraint-audit.md`）。
- 失败 A：modeler 对任务与上下文一无所知，凭空写了一个与任何 idea 无关的最小二乘脚本——调查流程在制度上缺失甚至被禁止（literature-scout 原规则明文"只读工作区内部"）。
- 失败 B：`"minimal patch"`、`"skip tests"` 等保守空话被模型读成偷懒授权，任务量无约束。

本次重构内容：
1. 约束审计：`derived-principles/04-constraint-audit.md`（过头/缺失/保留三清单）。
2. 调查机制落地：`literature-scout` 升级为强制前置角色——调查前沿 + **把仓库/代码/论文拉到本地 `research/` 留存**（示范：`research/harness-playbook/`，含 stencil.so harness-playbook 原文存档与 pi-mono clone）。
3. 反偷懒条款：RULES.md 硬约束新增 9-13（调查前置、无中生有禁令、任务量下限、真实检查、诚实升级）；`modeler` 模板改为"完整实现 method，不以行数论英雄"，输出契约新增 `behavior_checks`；`idea-generator` 去掉 50 行上限、要求证据引用。
4. 审计人格：`analyst`（恶毒审计官，有罪推定）与 `reviewer-skeptic`（攻击犬人格）模板重写。
5. pi 配置迁移：`.omp/` 已删除；`.pi/`（agents×9、rules×5、workflows×3、prompts、settings.json、hindsight.json）按 qwen38-27b-sft-workspace 的 pi 结构迁移，规则内容以本仓库较新版本为准（qwen 的 python-evidence 是旧版）。`orchestration/scaffold.sh` 改为从本模板仓库复制 `.pi/` 树。
6. OMP 叙事清除：活文档（AGENTS/RULES/README/QUEST/HANDOFF/template/orchestration/.pi）中的 OMP 产品叙事（eval 持久内核、`omp/task/*` 分支、`xd://` 设备、`@task`/`@smol`、`hub`、merged view）已替换为 pi 原生等价物；Orca 运行时事实保留。历史记录（debate/、derived-principles/00-03、archive/）按证据纪律不动。
7. `template/` 规格文档同步更新为 pi 接线。

## 下一步（新会话从这继续）

1. **验证迁移**：`uv sync --frozen` 后跑 `bash orchestration/scaffold.sh` 到一个临时目录，确认新工作区带完整 `.pi/` 树并能通过 `sh -n` 与 `py_compile` 检查。
2. **首轮带调查的完整飞轮验证**：跑一轮 reference profile 的 run loop，重点观察 literature-scout 是否产出 `research/` 本地证据、modeler 是否在无证据时报告 `investigation_missing`。
3. **qwen 工作区回灌**：qwen38-27b-sft-workspace 仍持旧版 `.pi/`（含 "minimal patch" 措辞）；本次重构的 agents/rules 应回灌到该工作区（或由它重新从本模板 scaffold）。
4. 观察点：夜间自转是否还出现"无调查直接开干"；reviewer-skeptic 的 strongest_attack 是否真的有杀伤力。

## 硬约束提醒

`RULES.md` 1-8（测量完整性）不变；新增 9-13（调查前置/任务量下限/真实检查）同样 sticky。
