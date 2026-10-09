# Research Flywheel v3 — onlyne 2.1.1 公共约定

本文件是 ARIS 主题的公共约定骨架，放在 server-root（本仓根目录）。pi 沿父目录拼上下文，树内每个 session 读到同一份约定。

## 术语

- workspace = role 的工作区：该角色的细则、配置与运行态文件，落在 `.onlyne/ws/aris/<role>/`。
- session：role 手头的一件工作。session 何时关闭由工作区 `[client.session] scope` 决定：默认 `oneshot` 一跳一关；`task` 一个任务族共用；`role` 常驻池复用。本主题用默认 `oneshot`。

## 落盘纪律

一切信息落文件。每个结论都能回溯到 runs/、papers/ 或 ledger 行。账本用 `onlyne ledger --server-root .` 读。

## 研究问题（ARIS 复刻）

本主题用 onlyne 六角色飞轮复刻 ARIS 的全自动科研环。ARIS 是公开的 Markdown-only skills 自主 ML 研究系统，仓库见 https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep。它的环形态：文献 → idea 发现 → 实验 → 跨模型评审循环 → 论文写作 → 同行评审 rebuttal。

技能到飞轮的映射：

- `/idea-discovery` → scout（检索与入池）+ analyzer（问题层分析深化位）。
- `/experiment-bridge` → model（plan→spec）+ bench（deploy→collect）。
- `/auto-review-loop` → critic 的 verdict 修订环。
- `/research-pipeline` 全链 → 飞轮宏观流本身。
- `/research-wiki` 持久记忆 → 文件台账（runs/、pool/、ledger）。

ARIS 上游技能事实以公开仓库 `skills/` 目录为准（main 分支）。

## 进步度量

- 主度量：端到端跑通轮数。`idea.json`→`analysis.md`→`derivation.md`→`measured/`→`papers/<run-id>/main.pdf`→`verdict.md` 全链条落盘记一轮。≥1 轮完整跑通算推进。
- 次度量：critic accept 率与 revise 收敛轮数。revise→accept 在 3 轮内收敛算健康。

算力与时间预算无固定配额：本机 pi 会话 + 宿主 lean 二进制 + 按需 GPU 跑批。记账按轮在任务产物里做。配置、种子、耗时进 `measured/`。

## 禁区

- 不伪造 `measured/` 数值。
- 不改评测器语义迎合结论。
- 不碰外部付费数据集与私有模型权重。
- model 只出 spec，不写 `experiment/` 代码。

## 工作模式：training live · 功耗约束

- bench 可发起 torch 臂跑批。
- measured 新产物一律落 `runs/<run-id>/measured/`。废弃产物按 DEPRECATED.md 口径标注。

功耗纪律：

- 全树任意时刻同时存活的训练/拟合进程 ≤1。批内串行，跨配置矩阵也串行。
- 优先本机加速器后端单进程（CUDA/MPS/CPU 按可用取）。禁多 worker 并行 DataLoader。
- 长跑批切时间片。单片 ≤45 min，片间让机散热。片进度写 `measured/run.log`，可续跑。
- 每批在 `measured/environment.json` 记 wall-time、峰值内存、热/降频迹象。热节流读数按平台取：macOS 用 `pmset -g therm`，Linux 用 sensors 或 `/sys/class/thermal`。取不到记 unavailable。
- 调度冲突时宁可晚出数，不许并发轰功率。

训练槽协议：

1. 发起任何训练/拟合命令前，先 `mkdir runs/.train-slot` 原子抢占。原子抢占 = 抢占动作一步完成，两个进程只会有一个成功。
2. 抢占成功后写 holder：`echo "<task_id> <pid> <ISO>" > runs/.train-slot/holder`。
3. 槽已存在则读 holder。pid 活着：等待，5-10 min 轮询一次，等待期间先干不需槽的活。
4. pid 死了：`rm -r` 接管，并在 run-log 记一次接管。
5. 交活/退出前 `rm -r runs/.train-slot` 释放。

过期护栏：`runs/*/DEPRECATED.md` 圈定的数字不进稿件与 verdict。开工先读本节与台账。

## 工作模型（射后不理）

射后不理 = 发出去就不等回复。

每个 session 的动作序列：

1. 恢复上下文。
2. 工作。
3. 用 `onlyne_handoff` 激发下游（可选，可多个）。
4. `onlyne_complete` 交活退出。

session 不等下游。投递后立即收到一行 receipt JSON。后续进展看 ledger 与 client intent。下游成果经文件与 ledger 呈现。接力任务唤醒合适的角色。

## 目录

- `pool/ideas.md`：idea 池，也是唯一队列。一条 idea 一个小节，checkbox 状态机 + note 追加行。scout 取单消费，critic/scout 写终态与新行。
- `runs/<run-id>/`：一轮 idea 的全部过程件：`idea.json` 快照、`analysis.md`、`derivation.md`、`lean/`、`measured/`、`verdict.md`。
- `research/frontier-notes.md`：联网检索记录。格式为 URL + 单行结论，追加式。
- `experiment/`：领域代码。`evaluation/`：评测器。`papers/`：成稿，落 `papers/<run-id>/`。
- `payload/`：注入给起始 role 的任务书（`payload/first.md` 及后续）。
- `.onlyne/spec.toml`：集群配置真相。
- `.onlyne/templates/aris/<role>/`：角色模板真相（AGENTS.md + `.pi/settings.json`）。
- `.onlyne/ws/aris/<role>/`：generate 渲出的角色工作区。运行时禁入 git 的目录：`run/`、`store/`、`keys/`、`logs/`、`ws/`。
- `.agents/skills/`：随树分发的技能。领域两件：`paper-figures`（绘图与表格规则）、`paper-writing`（稿件骨架与措辞纪律）。平台两件：`onlyne-supervisor`（集群运维面）、`onlyne-role`（role 会话侧通信纪律）。writer 出图出稿前、critic 审文字面时先读对应领域技能。supervisor 与 role 会话开工前先读 onlyne-* 对应那篇。

改 role 上下文：改 `.onlyne/templates/aris/<role>/`。再跑 `onlyne generate --root . --template aris/<role> --role <role> --force`。

主题状态：stage 与 entry role 记在角色表（★ 行）与冷启动节。

### 路径约定

本文件与一切任务书里的路径都相对 server-root。

- role session 的 cwd 在 `.onlyne/ws/aris/<role>/`，root 即 `../../../../`。发现文件不存在先 `pwd` 确认站位。
- 草稿、中间件、探针、staged 代码先落在自己 ws 的 `work/`（私有，不入 git）。定稿产物一次性发布到任务书点名的 root 路径，并在 `runs/<run-id>/run-log.md` 记一行本地→发布映射。
- 追加式台账直写 root：pool/ideas.md、frontier-notes.md、run-log.md、measured/ 流件。
- peer 实例的 `../../<peer>/work/` 可只读翻看。交接与审稿判据是任务书与 root 发布物。

### Obsidian vault 对接（全员遵守）

- vault 根由本机仓根 obsidian/ 软链给出。装配机自定，仓内不记录绝对路径。
- root `obsidian/` 下四个软链：`obsidian/论文`→`论文/`（原文 PDF 归档）、`obsidian/reports`→`reports/`（精读报告）、`obsidian/draft`→`draft/`（日常学习与 idea）、`obsidian/templates`→`templates/`（写作规范与报告模板）。读写都经软链，不在 ARIS 树里复制 vault 文件。
- 写作规范唯一入口：`obsidian/templates/writing-and-report-guide.md`。精读报告骨架：`obsidian/templates/paper-report.md`。
- 规范覆盖所有用户可见文字：`derivation.md`、`measured/summary.md`、`papers/<run-id>/main.tex` 与 `main.pdf`、`verdict.md`、`revisions.md`、vault 落库的精读报告。
- 规范要点：直接陈述、累加式、结论先行；数字带单位与出处；论文事实与「我的分析」分区；流程用 mermaid；数学用 `$$…$$` 独立公式块；YAML frontmatter 可解析；内部链接与 wikilink 可达。
- vault 写入白名单：PDF 论文只进 `obsidian/论文/原文/<短名>.pdf`（含 supplement 则同名 `-supplemental.pdf`）。Markdown 精读报告只进 `obsidian/reports/论文精读/<短名>-精读.md`，并在 `obsidian/reports/论文精读/00-索引.md` 登记。登记动作先读后改、增量更新。
- 其余一切产物留在 ARIS 树内，落点用 `papers/`、`runs/`、`presentations/`。
- `draft/` 是 idea 源之一。scout 每跳先读 `obsidian/draft/00-索引.md`，再读相关笔记。值得开正式链路的判断转为 pool idea：`evidence` 指到笔记具体章节，`origin` 用 `derived` 并注明来源笔记。
- 未核对结论进「证据边界与待核对项」，不直接当 claim 写进稿件。
- 人物画像不归本工作区：不读不写 vault 的 `人物/`、`关系图谱/`。已有规范人物页可 wikilink 引用，不新建。

## runs/<run-id>/ 布局

- `analysis.md`：analyzer 出的问题层分析。四节：成因/机制/难点/选型考察点。难点只提问；应对与贡献由 model 给出。
- `spec.md`：model 出的方法实现 spec 与评测器 spec。bench 按此落地跑批。
- `measured/summary.md`：bench 汇总值与 delta。每个 objective 一个实测值，每个 constraint 一个 pass/fail。
- `revisions.md`：writer 按 critic verdict 编号 finding 修订的记录。
- `run-log.md`：role 自己的追加式台账。`root-log.md` 文件名归 supervisor 专用，role 不自开同名台账。
- `verdict.md`：critic 一行 verdict（accept / revise / reject）+ 编号 finding。
- `papers/<run-id>/`：writer 成稿目录：`main.tex`（NeurIPS 2024 风格，模板 `papers/_template/neurips2024/`）+ `refs.bib` + `figs/`，编译出 `main.pdf`。结论先行，每个数字标注来源文件路径，open questions 单节。

## 评测契约

objectives 每条 `{metric, evaluator, direction, epsilon, baseline}`：

- `evaluator` 是 `evaluation/` 下评测器的路径与运行命令。
- `direction` 取 `higher` / `lower`。
- `epsilon` 是判定阈值（提升幅度）。
- `baseline` 写清来源：基线配置、种子、数据切分。缺任一项视为无效基线。

实测值来自 `measured/`。评测 verdict 与实测一致才 pass。

constraints 每条 `{check, description}`。

`check` 项含三类：

- 数据泄漏检查：声明训练/评测切分隔离。
- 随机种子固定声明。
- 时间预算声明。

bench 在 `measured/summary.md` 给每条 pass/fail。

基线切分：主度量评测面切一份 held-out，比例写进契约。lean/measured 迭代只在训练面跑。verdict 用冻结候选在 held-out 跑一次定生死。失败即终局，禁回炉再优化。这条防对评测面调参。

pass_rule 默认 `all`。探索性 idea 可在种子里写 `any` 并说明理由。

idea 的 `evaluation` 字段按本节填写。缺项的 idea 不进池。

## onlyne 2.1.1 工具面

### 装具

- 四件套：`cargo install --locked onlyne-cli onlyne-server onlyne-client onlyne-testkit`。crate `onlyne-cli` 装出的 bin 叫 `onlyne`。
- 插件：`pi install npm:pi-onlyne@2.1.0`。版本号钉住：v2 协议面对旧版插件不兼容。
- 兼容判据：`onlyne version` 报 `2.1.1`、`protocol:1`。
- `onlyne-gateway` 与 `onlyne-tui` 两个独立二进制已不存在。TUI 收成 `onlyne tui --server-root .`。gateway 能力收成 `onlyne gateway status`。

### 配置

- 集群唯一配置真相 = `.onlyne/spec.toml`。改完跑 `onlyne reload --server-root .`。运行期零回写。
- `reload` 无 `--dry-run`。看待应用差异用只读动词 `onlyne spec_diff --server-root .`，拼作 `spec-diff` 同样有效。
- spec 键分三档：未知键只 warn 后忽略；值错误报 `spec.toml:<行>: <msg>` 并拒跑；`backend` 与 v1 的 relay 三键按名硬拒（`BACKEND_IS_GONE` / `RELAY_IS_GONE`）。
- 键集全貌看 `onlyne schema spec`。

### role 通信三件（pi 插件内）

- `onlyne_handoff{to, text, image}`：接力并延续任务族，记录 parent_task 与 hop 血缘。ledger 顺链可查整条任务族。
- `onlyne_send{to, text, kind, image}`：`kind:"task"` 开新任务族；`kind:"note"`（默认）追加 note。note 不建 session。目标离线即 `recipient_offline`。本 spec `note_queue = false`。
- `onlyne_complete{outcome, summary, details, files}`：交活结项。`outcome` 取 `done|failed|cancelled|blocked`。

### 上报纪律

- `summary` 进 ledger 的 `out_head`：单行、200 字符封顶。它是展示行。
- 全文走 `details`，产物路径走 `files`。details 与 files 同样是结果的一部分，进 ledger 可查。上游不靠 summary 单通道收货。
- 同一 task 第二次 complete 只回 `reported <outcome>`。
- 完成守卫：报终态前，session 必须已向 `allowed_targets` 里列出的每个下游角色投递。欠投的 `onlyne_complete` 被拒并点名欠谁。这道守卫由 `allowed_targets` 一个列表承担。
- 失败交活：`onlyne_handoff` 的 text 或 `onlyne_complete` 的 summary 首行写 `> hop-failed: <环节> <一句话>`，并带 `outcome=failed`。这只是正文习惯：2.x 没有任何解析方读这一行，接收角色靠人读。
- 产物未齐：`onlyne_complete{outcome:"blocked", summary:"<缺什么>"}` 交回，等接力唤醒，不写无依据产物。

### shell 显式接口

- role-speaking 动词：`send` / `reply` / `handoff` / `complete` / `ack` / `reject` / `control`。七个动词都要求同时带 `--force` 与 `--yes-i-am-supervisor-not-other-role`。
- `repair` 族不带这两个旗标。
- mounted pi role 不走这条 shell 接口。

### 观测

- 只读命令：`onlyne status|roles|sessions|ledger|faults|watch|history --server-root .`。
- 看板：`onlyne tui --server-root .`。
- 机器级清单：`onlyne ls`。SOCKET 与 ALIVE 两列分开读。
- socket 固定在 `/tmp/onlyne-<uid>/<digest>.sock`。树内 `.onlyne/run/s` 只是打印拼写。

### supervisor

- supervisor 是 `_supervisor` admin mount：`command = []`、`admin = true`，不进工作环。
- 第一发：`onlyne --server-root . send --from _supervisor --to scout --file payload/first.md --force --yes-i-am-supervisor-not-other-role`。
- 角色的 completion 回执自动回流 origin（origin==收件方时免 ACL），进来源收件箱，pull 式取。

### placement 与调度

- placement 是机器属性，值域 `orca|zellij|tern|headless|external`，写在各 role 工作区 `.onlyne/config.toml` 的 `placement` 键。
- 缺失时探测序：tern → orca → zellij → headless。非空 `ONLYNE_BACKEND` 优先。
- `drive = "acp"` 要求 `placement = "headless"`。
- `onlyne client doctor` 只读打印本机判定。
- session scope 三档见「术语」节。本主题用默认 `oneshot`。
- 调度参数：per-role `[client.timeout]{ready_ms, idle_ms}`，默认 30000/60000。`[client.intent]{attempts, backoff_ms}`，默认 attempts=3、backoff 三档。v1 的 running 键已删。

## 任务书六段（handoff/send 的 text）

```text
目标：<一句话，做完算什么>
背景：<为什么做这件事：上游发现了什么、卡在哪、这个任务在整体里处于什么位置；两三句；没有就写 无>
输入：<必须读的文件路径，一条一行，括号里写清这份文件是什么；runs/ 与 research/ 为准>
期望产物：<写到哪里的什么文件，格式要求>
自由度：<除点名产物外鼓励顺手做什么：补检索、修断链、记负证据、建索引页；或写 按角色表惯例>
下一跳建议：<完成后用 onlyne_handoff 交给谁、干什么；没有就写 无>
```

六段标题字面固定，接收方与校验器按标题找段。段内自由行文；`输入` 保持一条一行。`背景` 与 `自由度` 允许写「无」；写「无」时接收方按角色表与根约定自主判断。接收方带着上下文干活：先读背景，再决定怎么干；点名产物是硬契约，工作路径自己判断。
输入路径必须真实存在。接收方 session 是全新上下文，任务书里没写的路径它找不到。

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

状态机：

- `[ ]` queued → `[>]` running。scout 取单时改。
- `[>]` → `[x]` keep / `[!]` failed。critic 归档时改。

`evaluation` 行保持 JSON 内联。

进池硬门四条，任一条命中即不进节：

1. `evidence` 为空。
2. `objectives` 为空。
3. `done_when` 为空。
4. headroom 预筛不过：写不出「哪个 measured/ 数字或 frontier-notes 行暴露了缺口、余量多大」的单行判据。

指得出数字才占下游 rollout。指不出的候选不写进节，负证据照记进 frontier-notes 一行，下轮检索先翻旧账。

## 角色表（本主题拓扑的唯一事实源）

角色名与 `.onlyne/templates/aris/<目录名>` 一一对应。增删 role 时同时改三处：这张表、spec 的 `[[client]]`、模板目录。

`entry` 列标出第一发的注入对象。全表恰好一个 `★`。

thinking 档是模板 `.pi/settings.json` 里的 `defaultThinkingLevel`。pi 的 provider/model 由操作者自己的 pi 配置给默认。本树不记录。

| role | 职责 | 上游 | 下游 | entry | thinking |
|---|---|---|---|---|---|
| scout | 前沿检索与 idea 入池 + 取 queued 派工 | _supervisor、critic、analyzer、model、bench、writer | analyzer | ★ | low |
| analyzer | 问题层分析，出 `runs/<run-id>/analysis.md`。难点只提问，应对与贡献归 model | scout、model（补分析回请） | model、scout（失败回传/补检索） | | high |
| model | 推导 + Lean 形式化 + 出 spec。不写 `experiment/` 代码 | analyzer、critic（revise-理论） | bench、writer、analyzer（补分析回请）、scout（失败回传/补检索） | | max |
| bench | 跑批与测量，按 spec 落地并落 `measured/` | model | writer、scout（失败回传） | | low |
| writer | 成稿（初稿与修订稿） | model、bench、critic（revise-文字） | critic、scout（补检索） | | high |
| critic | 审稿 verdict + 归档 + 提下一条 idea | writer | writer（revise-文字）/ model（revise-理论）/ scout（accept/reject 开新轮） | | high |

`★` 标第一发的注入对象，本主题是 scout。

`下游` 列与每个 `[[client]]` 的 `allowed_targets` 逐行对齐。`上游` 列与 `allowed_senders` 对齐。

`allowed_targets` 与 `prose` 是 ACL 与身份的机器真相。改动落 `.onlyne/spec.toml` 与模板目录，再 reload 才进 ws。

表外的 `_supervisor` 是 admin mount：走 `onlyne --server-root .` 值班面。它唯一出边是向 scout 投第一发，零上行边。岗位说明在 `.pi/SYSTEM.md`。

### 七条边的含义

- critic→model：revise-理论。推导或 spec 有缺陷，重推。
- critic→writer：revise-文字。文字、claim、结构修订，不动推导。
- writer→scout：补检索。稿件缺证据，要文献。
- model→analyzer：补分析回请。analysis.md 的难点或机制段撑不起推导时退回补析，写清缺哪一节。analyzer→model 正常下派，构成一小环，两轮封顶。
- analyzer→scout：失败回传与补检索。证据不足以判别机制时列「无法判别」段，写清缺什么证据、要什么来源。
- model→scout：失败回传与补检索。Lean 失败带现场路径。证据缺口写清要什么来源。
- bench→scout：失败回传。跑不动时带现场路径。

### 闭环

supervisor 不在工作环里：没有任何 role 的上游或下游是 root。

supervisor 只做工作区维护。条目为：idle 判定与报告、generate/reload、spec 对表、知识产物 git commit、人机传话。

接力闭环在六个 role 之间：

- 主环：scout→analyzer→model→bench→writer→critic→scout（accept/reject 开新轮）。
- 修订环：critic→writer（revise-文字）/ critic→model（revise-理论）。
- 补析环：model→analyzer（回请补析）→model（重下派）。
- 回传边：analyzer→scout、model→scout、bench→scout、writer→scout。

supervisor 会话档位见根 `.pi/settings.json`（medium，维护位）。role 档位见 `.onlyne/templates/aris/<role>/.pi/settings.json`。改完跑 `onlyne generate --root . --template aris/<role> --role <role> --force`，落到该 ws。

## 飞轮宏观流（从角色表推导）

接力规则按角色表的 `上游` / `下游` 列执行。supervisor 不进工作环。

各跳职责：

1. scout：从 pool 取 queued idea，固化 `runs/<run-id>/idea.json`（status 改 running），用 `onlyne_handoff` 派给 analyzer（任务书交代先立 analysis.md）。同时承担检索与新 idea 入池。
2. analyzer：读 idea.json 与 evidence，写 `analysis.md` 四节，handoff model。按 model 回请补析，两轮封顶。
3. model：读 analysis.md 逐难点给应对，出 `derivation.md` 与 `spec.md`，handoff bench。评测器就绪后 handoff writer。
4. bench：按 spec 落地 `experiment/` 与 `evaluation/`，跑批落 `measured/`，汇总后 handoff writer。跑不动则 handoff scout 失败回传。
5. writer：读 runs/ 全产物成稿 `papers/<run-id>/`，handoff critic 送审。稿件缺证据则 handoff scout 补检索。
6. critic：按闭环规则收尾（见下）。

通用条款：

- 每个 role 完成后按自己的 `下游` 列 `onlyne_handoff` 接力任务书，然后 `onlyne_complete` 交活退出。角色零上行边，回执走 origin 自动通道。
- 产物未齐时 `onlyne_complete{outcome:"blocked"}` 交回，等接力唤醒，不写无依据产物。

critic 闭环：

- revise-文字：handoff writer 修订接力。
- revise-理论：handoff model 重推接力。
- accept/reject：归档。keep 留 papers/ 并把 idea 状态改 keep。failed 记 verdict.md 并改 failed。
- 归档后从 open questions 或失败结论提取下一条 idea 入池，再 handoff scout 开新轮。

回传 scout 的任务共四种：analyzer 的失败回传与补检索、model 的失败回传与补检索、bench 的失败回传、writer 的补检索。scout 处理完后走正常派工跳。

环路在六个 role 之间自转。人随时可接管任一 session。自激发无熔断，终结靠人跑带 gate 的命令，或用 TUI：

```bash
onlyne --server-root . control cancel --task <id> --from _supervisor --reason "..." --force --yes-i-am-supervisor-not-other-role
```

## 冷启动与第一发

装配完成的瞬间，工作区处于这些事实下：

- `stage=live`，`theme/<slug>` 分支已建，装配材料已消失。
- 运行时未起：`onlyne status --server-root .` 无 socket。
- `tasks` 表 0 行，`runs/` 空，`papers/` 空，`pool/ideas.md` 只有种子或空。

飞轮是反应式的：没有入站任务就什么都不会发生。

通电 = server 一个可见前台 tab 跑 `onlyne server run --root .`。六个 role client 各占一个可见 tab，跑 `onlyne client run --workspace .onlyne/ws/aris/<role>`。

第一发属于开跑。

启动动作二选一：

1. 用户给方向：supervisor 写 `payload/first.md`（问题、约束、期望），执行第一发命令。`--to` 的对象是角色表 `★` 行，本主题 scout。
2. 用户自己在 CLI 投第一发（同上 admin 面命令），supervisor 事后从 ledger 与 `runs/` 接上下文。

supervisor 只负责把第一发投进 `★` role，不参与后续流转。环成形后自转。

## 维护与配置（supervisor 用）

- 配置唯一入口：`.onlyne/spec.toml`（拓扑/prose/ACL/timeout/intent/agent_package/cert_pin）与 `.onlyne/templates/aris/`（细则 + thinking 档）。
- 生效路径：spec 改 → reload；模板改 → 该 role generate --force。无 sync/overlay/bootstrap 概念。
- 装役判据：`onlyne version` 报 `2.1.1`。
- server 与 TUI 常驻 = 在本 ARIS worktree 的可见前台 tab 里跑，关 tab 即停环，禁入任何 agent 后台。client 起 tab 的 worktree 决定会话 spawn 定向。
- 六 role client = 各一个可见前台 tab 跑 `onlyne client run --workspace .onlyne/ws/aris/<role>`。
- 崩溃残留：`onlyne faults --open-only` 看核心检测（intent exhausted 落此）。`onlyne repair inspect|retry|close|fail|ack --task <id>` 处置。`onlyne ghosts --limit 20` 看 ghost sweep 审计。pane 已死而 lifecycle 仍 working 的残影用 `repair close` 收口。
- client 不写 pid 文件，pid 真相在 server 侧 client_registry。停某个 client 用 `ps` 按 args+cwd 精确匹配该 ws 的 `onlyne client run` 进程，再定点发信号。禁止 pkill 按名杀。
- 清理孤儿进程前先核对身份：`brew services`、launchd、其他 app 拉起的常驻服务不属于 swarm。杀之前查父进程与端口归属，只回收 client 注册表里存在的进程。误杀系统服务比留一个孤儿严重得多。

## 纪律

- 改 `experiment/`、`evaluation/` 前读 runs/ 里上一轮记录。改动在任务产物里写明。
- 数值只从 measured/ 引。报告只写跑出来的东西。
- 存在 `runs/<run-id>/DEPRECATED.md` 的 run：其废弃范围内数字一律不作证据，只可按该文件口径引用为已废弃 baseline。
- 新 run 的实测产物仍落 `runs/<run-id>/measured/`。
- 失败也交活：跑不动的结论写进 runs/，`onlyne_complete{outcome:"failed"}` 交失败报告（summary 首行 `> hop-failed: <原因>` + 现场路径），让下游有据可依。
