# 任务书：飞轮模板全文档「说人话」重写

## 目标

把 research-flywheel 模板树的全部 agent 面向文档重写为平实白话版本。信息零失真：每条事实、命令、路径、门、语义都必须还在，只换表达方式。

## 重写范围（逐文件）

1. `README.md`
2. `BOOTSTRAP.md`
3. `.agents/AGENTS.md`（约定骨架，最重）
4. `.pi/SYSTEM.md`
5. `AGENTS.md`（root 薄入口，9 行）
6. `.agents/skills/flywheel-setup/SKILL.md`
7. `.onlyne/templates/flywheel/{scout,model,bench,writer,critic,_supervisor}/AGENTS.md` ×6
8. `.onlyne/spec.toml`：仅注释行；`prose` 字段、全部键名与值一字不动
9. `runs/v1-redesign-20260911.md`：轻改（保留 commit 哈希链与数字原样）

## 硬约束（失真红线）

- 命令块（``` 围栏内）、文件路径、TOML/JSON 键名、占位符（`__AGENT_PACKAGE_ABS__`、`{{agent_package}}`、`REPLACE_ME`）、探测序 `orca→zellij→fake`、数值（timeout、端口、tag 号 `v1.0.0-beta.4 = 2666ede`、`base64(32×0x01)=AQEBAQ…`）、错误码词表（acl_denied / recipient_offline / conflict / exit 2 / exit 4 / SIGKILL+codesign）、`../.onlyne/agent/onlyne-agent-pi` 渲染形态说明：一律原样保留。
- `<!-- THEME:xxx -->` 槽标记五个，名称与位置不动，槽内说明文字可白话化。
- 机器核过的语义不许松动：零上行边（`_supervisor` 不在 allowed_targets）、completion-to-origin 豁免、F1 定稿链顺序、F4 三态合法性、promote 九检每一项的检查内容、动词面（瘦入口 vs onlyne-server 子命令划分）、`socket_present` 判活。
- 表达改法：长定语句拆短句；文言词（收官、落盘、知会、勘误、放行进闸）换日常词；紧凑名词堆叠换成「谁做什么」句式；一句只说一件事。删掉修辞性强调，保留全部信息量。
- 禁用修辞（全局规则）：「不是…而是…」及一切转折反诘句式，中英文都禁。平铺直叙，additive 连接。

## 工作流

1. 逐文件：先完整读原文 → 列该文件的事实清单（每条命令/数字/路径/规则一项）→ 重写 → 对照清单逐条打勾，缺一条补一条。
2. `_supervisor` 模板与 spec prose 的边界：prose 不动，模板 AGENTS.md 可改。
3. 全部改完后跑验证：
   - `bash -n scripts/promote.sh`
   - `/tmp/fwtpl` 夹具：同步 `.onlyne/templates` 与 spec 后 `PATH=/tmp/v1shim:$PATH bash scripts/promote.sh --dry-run` 须 `9/9 PASS`
   - `git diff` 通读：删掉的行里出现的每个技术 token 都要能在新行里找到（可用 grep 抽点对账）。
4. 提交：单 commit，message 说明「plain-language rewrite, zero token loss」，不 push（push 归 supervisor）。

## 交付

回报一行：改动文件数、九检结果、对账中发现并补回的失真点列表（如有）。
