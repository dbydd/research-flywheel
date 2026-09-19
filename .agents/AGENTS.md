# Research Flywheel v3 — onlyne v1 公共约定

本文件在 server-root。pi 沿父目录链把它拼进树内每个 role 会话的上下文。

workspace 就是一个 role，内容有记忆、设定、历史文件。session 是这个 role 手头的一件工作，一跳即结。所有信息写成文件。所有结论都能回溯到 runs/、papers/ 以及 `onlyne ledger/history` 的 task 行。

## 研究问题与判进标准

本主题研究问题由本飞轮的 owner 定，写进本节后即是全环的唯一口径。

主度量与次度量、各自的判定阈值、算力与时间预算、禁区都写在这里。每条要具体到能判断某一轮实验是否推进了它。禁区指不做的事、不碰的数据集与模型。

一轮的推进判据：`runs/<run-id>/` 的 `verdict.md` 首行为 accept，且该轮的 measured/ 汇总给出了主度量的实测值。

## 工作模型（射后不理）

每个 session 的生命周期：恢复上下文 → 工作 → 激发下游（handoff，可选若干）→ `onlyne_complete` 交活退出。

session 不等下游。投递后立即返回一行 receipt JSON。后续进展都在 ledger 与 client intent 里。下游成果经文件与 ledger 呈现。接力任务唤醒合适的单位继续。

## 目录

- `.agents/skills/`：预制技能，随树分发（pi 沿父目录链发现，与本文件同机制）。领域两件：`paper-figures`（matplotlib conf 驱动绘图 + LaTeX 三线表与图规则，源自 guanyingc/latex_paper_writing_tips 与 dair-ai/ml-visuals）、`paper-writing`（稿件骨架 + LaTeX 细则 + 措辞纪律），读者是 writer 与 critic，出图出稿前、审文字面时先读对应一件。平台两件：`onlyne-role`（角色协同纪律，读者是每个 role 会话）、`onlyne-supervisor`（值班与运维纪律，读者是 supervisor 会话）。
- `.onlyne/spec.toml`：拓扑唯一真相。[server] 一节加每 role 一个 [[client]]，含 prose、ACL、timeout、intent。
- `.onlyne/templates/flywheel/<role>/`：role 细则（AGENTS.md）与 `.pi/settings.json` 模型位的正本，渲进 `.onlyne/ws/`。
- `pool/ideas.md`：idea 池，也是唯一队列。一条 idea 一个小节，checkbox 状态机 + note 追加行，格式见下。scout 追加并自取消费。supervisor 不碰队列。
- `runs/<run-id>/`：一轮 idea 的全部过程件。里面有 `idea.json` 快照、`derivation.md`、`lean/`、`measured/`、`verdict.md`。
- `papers/`：成稿（`<run-id>.md`）与 `figs/<run-id>/`。figs 里放绘图脚本、成图、mermaid/tikz 源。图随稿件走，critic 的追溯锚点保持单一。figure 由 writer 兼职制作，没有独立的画图 role。
- `research/`：证据。`frontier-notes.md` 是联网检索记录，格式为 URL 加单行结论，追加式。
- `experiment/`：领域代码。`evaluation/`：评测器。
- `payload/`：注入给 entry role 的任务书落这里，例如 `payload/first.md` 及后续文件。

路径约定：本文件与一切任务书里的路径都相对 server-root。role session 的 cwd 在其 ws 目录。读写知识文件时用任务书里的 root 相对路径。文件不存在就先 `pwd` 确认站位。内容按引用交接：text 里给文件路径，接收方读文件。工作区字节从不上总线。

## runs/<run-id>/ 目录约定

- `idea.json`：入池小节的字段快照，`status` 由 scout 取单时改 `running`。
- `derivation.md`：model 的推导记录。关键断言与形式化的失败命令都写在这里。
- `lean/`：Lean 形式化源与编译现场。
- `measured/`：原始 stdout/stderr、配置、种子、耗时。汇总与 delta 写 `measured/summary.md`，每个 objective 一个实测值，每个 constraint 一个 pass/fail。
- `verdict.md`：critic 的判词。首行 accept / revise / reject，随后编号 finding。
- `spec.md`：model 的方法与评测器 spec，bench 的唯一输入。
- `run-log.md`：本地→发布的映射行，追加式。
- `revisions.md`：writer 按 verdict 编号 finding 的修订记录。

## 评测契约

`objectives` 每条四项：metric（指标）、evaluator（评测器）、direction（方向）、epsilon（判定余量）。基线来源写进同一行。`constraints` 每条两项：check 与 description，覆盖数据泄漏、随机种子、时间预算这类硬项。`pass_rule` 取 `all` 或 `any`。

基线切分：主度量评测面切一份 held-out，比例写进契约。lean/measured 迭代只在训练面跑；verdict 用冻结候选在 held-out 跑一次定生死，失败禁回炉再优化，防对评测面调参。理念源：NVlabs/SoL-Pi 双 split 纪律，见 research/frontier-notes.md。

idea 的 `evaluation` 字段必须能按本节直接填写。缺项的 idea 不进池。

## onlyne 工具（v1 pi 插件在 role 会话提供）

- `onlyne_send {to, text, kind}`：激发新任务族用 kind:"task"。给在飞任务追加 note 用 kind:"note"，这也是默认值。note 不建 session：目标离线、或者在线但手头没有 working session，都直接得 `recipient_offline`（server 侧 `note_queue = true` 才排队，排队后到 `ttl_ms` 记 expired）。to 必须在本 role 的 `allowed_targets` 里，否则返回 `acl_denied`，行都不落。
- `onlyne_complete {outcome, text}`：交活结项。`outcome: done|failed|cancelled`（`cancelled` 表示这一跳体面交回、产物未齐）。CLI 同面：`onlyne complete --task <id> --outcome <o> --head-from local --text "..."`（`--head-from` 必填，`local` 用本行 text 当 head，`ledger` 回读已存 head）。text 原样进 ledger 的 `out_head`：单行、200 字符封顶。这是唯一的上行通道，整句答案放这里，写不下就指产物路径。同一 task 第二次 complete 会被拒，只喊一次。onlyne-client 1.2.1 起，结清时没有结果行也会落一条正文为空的 `completion` 收据，等这张收据的下一跳能继续。ACP 结项报告（往 `<ws>/.onlyne/out/<task-id>.md` 写 `hop-done:` / `hop-failed:` 一行）只在 `backend = "acp"` 时生效；本模板 `session_command` 是 pi 插件路径，结项走 `onlyne_complete`。
- CLI 同面（shell 里跑）：`onlyne handoff --to <role> --task <id> --text "..."` 表示转派新任务，并记 `parent_task` 与 hop+1 血缘。`onlyne send --to <role> --text|--file ...` 开新任务族。`onlyne reply --to <msg-id> --text "..."` 回执。`onlyne control recycle|probe|snapshot|cancel|focus --task <id>` 管任务（`--from`/`--task` 全局，子命令前后都认）。
- 接力一律用 handoff。ledger 顺 `parent_task` 链能查出整条科研链路，追溯成本为零。
- 失败交活：handoff/complete 的 text 首行写 `> hop-failed: <环节> <一句话>`，并带 `outcome=failed`。产物与现场照写。
- 重试纪律：同一 `op_id` 换内容重发得到 `conflict`。重试时原帧重发。断线期照常干活：outgoing receipt 落 intent，重连后按序补投。
- role 会话查现场：`onlyne who`、`onlyne watch --follow`。socket 解析次序 `--socket` > `ONLYNE_SOCKET` > cwd 上行查找 `.onlyne/run/s` 或 `.onlyne/run/socket`。pi 内用 `/onlyne` 命令看连接与 task 统计。

## 任务书四段（send/handoff 的 text）

```text
目标：<一句话，做完算什么>
输入：<必须读的文件路径，runs/ 与 research/ 为准>
期望产物：<写到哪里的什么文件，格式要求>
下一跳建议：<完成后 handoff 谁、干什么；没有就写 无>
```

输入路径必须真实存在。接收方 session 是全新上下文。任务书里没写的路径它找不到。

## idea 格式（pool/ideas.md 一条一个小节）

```markdown
## [ ] <id>
- origin: user_seed|derived | parent_run: <run-id 或 —> | question: <一句话>
- hypothesis: <可检验的假设>
- method: <做法要点>
- evidence: <非空路径数组，逗号分隔，含 research/frontier-notes.md>
- evaluation: {"objectives":[{metric,evaluator,direction,epsilon,baseline}], "constraints":[{check,description}], "pass_rule":"all"|"any"}
- done_when: <完成的 observable 判据>
- note: <追加式备注，一行一条，后来的写上面>
```

状态机：`[ ]` queued → `[>]` running（scout 取单时改）→ `[x]` keep / `[!]` failed（critic 归档时改）。`evaluation` 行保持 JSON 内联。四条进池硬门：evidence 为空、objectives 为空、done_when 为空、headroom 预筛不过，任一条命中即不进节。headroom 预筛：入池前沿上单行判据——哪个 measured/ 数字或 frontier-notes 行暴露了缺口、余量多大；指得出数字才占下游 rollout，指不出的候选负证据记 frontier-notes 一行即可。

## 角色表（本主题拓扑的唯一事实源）

| role | 职责 | 上游 | 下游 | entry | model |
|---|---|---|---|---|---|
| scout | 前沿侦察：检索、证据入池、取单固化 idea.json | _supervisor、critic、model、bench、writer | model | ★ | `templates/flywheel/scout/.pi/settings.json` |
| model | 建模：推导、Lean 形式化、方法与评测器 spec | scout、critic | bench、writer、scout | | `templates/flywheel/model/.pi/settings.json` |
| bench | 跑批与测量：实验与评测器落地、measured/ 汇总 | model | writer、scout | | `templates/flywheel/bench/.pi/settings.json` |
| writer | 成稿与图：papers/ 稿件、溯源数字、figs 脚本 | model、bench、critic | critic、scout | | `templates/flywheel/writer/.pi/settings.json` |
| critic | 审稿与归档：verdict.md、keep/failed 归档、提新轮 idea | writer | writer、scout、model | | `templates/flywheel/critic/.pi/settings.json` |

表外的 `_supervisor` 是 admin mount：走 `onlyne --server-root .` 值班面，唯一出边是向 scout 投第一发，零上行边。它的岗位说明在 `.pi/SYSTEM.md`。

`★` 标第一发的注入对象，全表恰好一个，本主题是 scout。`下游` 列与每个 [[client]] 的 `allowed_targets` 逐行对齐。`上游` 列与 `allowed_senders` 对齐。模型三档写在 `.onlyne/templates/flywheel/<role>/.pi/settings.json`。

`allowed_targets` 与 `prose` 是 ACL 与身份的机器真相；改动落 `.onlyne/spec.toml` 与模板目录，再 reload 才进 ws。

## 飞轮宏观流（接力闭环）

1. scout：产出入池后自取一条 queued idea，把 `runs/<run-id>/idea.json` 固化（status 改 running），再 `handoff model` 交建模任务。supervisor 不进环。
2. 每个 role：完成后按角色表自己那行的 `下游` 发 `handoff` 接力任务书，然后 `onlyne_complete {outcome:"done"}` 交活退出。
3. 产物未齐的跳：用 `onlyne_complete {outcome:"cancelled", text:"等待条件说明"}` 体面交回，也可以静默终止，由 idle 回收兜底。等接力唤醒再动，不写无依据产物。
4. 闭环回到 scout：critic 的 accept/reject 本跳自归档，keep 的稿件留 papers/，pool 该行改 keep；failed 的记 verdict.md，pool 改 failed。随后提取下一条 idea 入池（origin=derived），`handoff scout` 开新一轮。
5. 回执自动回 origin，离线也排队。role 的 `allowed_targets` 从不含 `_supervisor`，上行零常驻边。

环路全在 role 之间自转：scout→model→{bench,writer}→writer→critic→{writer 修订、model 理论级修订、scout 换题}。人通过 supervisor 或 TUI 观察现场。自激发有账：ledger 每跳一行，`onlyne ledger --task <id>` 顺链可查。终结靠人跑 `onlyne control cancel --task <id>`，或者用 TUI。

## 运行面指针

本文只定角色与流程约定。运维与值班各有正本：

- supervisor 值班职责（账目读取、残影恢复、idle 判定、对人报告、权限边界）：`.pi/SYSTEM.md`。
- 集群的运维操作口径：`README.md`。
- 飞轮的反应式性质：没有入站任务时环不动。第一发之后，推进全靠角色表的接力边自转，supervisor 不进气泡。

## 纪律

- 改 `experiment/`、`evaluation/` 前先读 runs/ 里上一轮记录。改动在任务产物里写明。
- 数值只从 measured/ 引。报告只写跑出来的东西。
- 失败也交活：跑不动的结论写进 runs/，用 `onlyne_complete {outcome:"failed"}` 交失败报告。text 首行写 `> hop-failed: <原因>` 加现场路径，让下游有据可依。
- 发布面/工作面边界：草稿、中间件、探针、staged 代码先落 role 自己的 ws（私有区）。定稿产物一次性发布到任务书点名的 root 路径，并在 `runs/<run-id>/run-log.md` 记一行本地→发布映射。追加式台账（pool/ideas.md、frontier-notes.md、run-log.md、measured/ 流件）直写 root，接力唤醒要求实时。peer 的 ws 可以只读翻看。交接与审稿判据仍是任务书与 root 发布物。
