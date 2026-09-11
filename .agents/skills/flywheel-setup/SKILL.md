---
name: flywheel-setup
description: Guide a fresh clone through theme assembly. Use when the user says 装配, bootstrap, 新主题, or clone 了模板接下来怎么配. Step-by-step setup conversation for one-theme-per-flywheel configuration.
---

# flywheel 装配指南

你是这个 clone 的第一个 pi 会话。按 A→G 七个阶段走。每个阶段都包含三件事：问用户什么、写哪个文件、怎么自查。

装配期唯一的机械命令是 `./scripts/promote.sh`，先跑 `--dry-run`。删除动作与 git 动作只许这个脚本执行。

装配前 checkpoint：root `AGENTS.md` 必须是薄入口，即 §5.1 那几行。若它已经是主题约定版，说明本工作区已装配，不要重走本指南。

## A 探询

问用户：研究问题是什么？研究问题用一句话目标加验收它的度量来答。什么算进步？答主度量、次度量、阈值。可跑的评测是什么？算力与时间预算多少？禁区是什么？禁区指不做的事、不碰的数据集/模型。

不写文件。自查：你能一句话说清目标与度量，用户点头。

## B 拓扑

问用户：需要哪些 role？谁唤醒谁，按上游→下游说？哪个模型档位配给哪个 role，按 provider / model / effort 说？需要几个评测器？哪个 role 是第一发的入口？入口恰好一个，记为 entry。

改 `.onlyne/spec.toml` 的 [[client]]，并同步 `.onlyne/templates/flywheel/<role>/`。增删条目与目录。prose 是身份与上报纪律，两处保持一致。`role` 非空。`model` 三字段按主题填写。`back_edges` 按唤醒关系填写。

角色名的唯一事实源是这里的目录名。别处出现的角色名都从这里生成。

自查：每个 role 都有上游和下游；entry 恰好一个。

## C 起草

问用户：术语表、runs/ 结构增补、稿件口径、起始 role 选谁？起始 role 与 B 的 entry 保持一致。

写五个 THEME 槽，都在 `.agents/AGENTS.md`：`research-question`、`runs-layout`、`evaluation-contract`、`role-table`、`entry-role`。角色表的列是 `role | 职责 | 上游 | 下游 | entry | model`。每行对应 spec.toml 一个 [[client]] 与 templates 一个目录。`★` 恰好一个。

同步改 `.pi/SYSTEM.md` 的 supervisor 职责，派工目标名来自角色表，`--to scout` 之类的旧写法按表替换。同步改 `README.md` 的用户面描述。

自查：角色表与 spec.toml 对齐，无多余无缺失；`★` 恰好一个，且与 `entry-role` 槽同名；relay 边双向闭合，A→B 时 B 的 allowed_senders 含 A；无残留 `<!-- THEME:` 标记。

## D 种子

问用户：首批 idea 方向，1–3 个。

写 `pool/ideas.jsonl`，每行一个 JSON：`id/origin/question/hypothesis/method/evidence/evaluation/done_when/status`。`evidence` 是非空数组。`evaluation.objectives` 非空。`done_when` 非空。首批 `origin` 用 `user_seed`，`status` 用 `queued`。

同时写 `research/` 领域锚点文件，含 `frontier-notes.md` 表头与至少一条真实来源记录。

自查：逐行 JSON 可解析；`evidence/evaluation/done_when` 三项缺一就不进池。

## E 校验

不问用户。执行：

```bash
./scripts/promote.sh --dry-run
```

全绿才往下。红项逐条回 C/D 修。常见红项：THEME 残留、`★` 数量不对、角色表与 spec.toml 不一致、seed schema 缺字段、`workspace sync` 报 dangling、`pi-onlyne` 版本下限不够、二进制缺失。

## F 落定

问用户：复述 `./scripts/promote.sh --dry-run` 打印的"将执行动作"与"将删除文件"清单。用户明确确认后执行 `./scripts/promote.sh`，这次不加 `--dry-run`。

脚本会做这些事：建 `theme/<slug>` 分支、把 `.agents/AGENTS.md` 提升为 root `AGENTS.md`、写 `.onlyne/flywheel.json`、用 `workspace create` 生成 `.ws/`、删装配材料、commit、打印三行 idle 提醒。

把那三行原文转述给用户：scheduler 要人另起；这个会话就是 supervisor；飞轮现在全 idle，见 §6.5。

自查：`stage=live`；`theme/<slug>` 分支存在；退场清单文件消失。

## G 第一发

先向用户转述 §6.5 的现场清单：tasks 0 行、`.ws/<role>` 无 session、`runs/` 空、`papers/` 空、pool 里是种子。`onlyne-server run` 与各 `onlyne-client run` 属于通电动作，开跑靠一发注入。

再问：研究方向现在给不给？第一发由谁投？可选方案是 supervisor 写 `payload/first.md` 投，或者用户自己在 CLI 投。

写 `payload/first.md`，内容含问题、约束、期望，然后执行：

```bash
onlyne --server-root . send --from _supervisor --to <entry_role> --file payload/first.md
```

自查：`onlyne ledger` 出现首发 in_flight 行，且起始 role 有 session；随后 `runs/` 或 `research/` 开始有产物。此后环在 role 之间靠接力自转，supervisor 不进环，人工不再推。

常驻推荐 server 前台 tab，用 `onlyne server stop` 收；client 各起一个 tab，或者用 ONLYNE_BACKEND=zellij 归位。
