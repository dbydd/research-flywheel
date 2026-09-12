# Research Flywheel v3 — swarm 公共约定（约定骨架）

这份文件放在 swarm root。pi 沿父目录自动拼上下文，树内每个 session 都读到同一份约定。

两个词先说清：workspace = role，指该角色的「记忆 + 设定 + 历史文件」；session = 该 role 手头的一件工作，做一跳就结束。

一切信息落文件。每个结论都能回溯到 runs/、papers/ 或 .onlyne/ledger.jsonl 的路径。

## 研究问题（ARIS 复刻）

本主题用 onlyne 五角色飞轮复刻 ARIS（https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep）的全自动科研环，环的形态是：文献→idea 发现→实验→跨模型评审循环→论文写作→同行评审 rebuttal。

ARIS 是一套 Markdown-only skills 的自主 ML 研究系统。本飞轮把它的 workflow 映射成 scout/model/bench/writer/critic 五跳：`/research-pipeline` 全链装进飞轮宏观流本身，`/research-wiki` 的持久记忆装进 hindsight bank（跨会话的长期记忆库）。证据锚点见 `research/aris-workflow-summary.md`。

「什么算进步」分主次两条度量：

- 主度量：端到端跑通轮数。`idea.json`→`derivation.md`→`measured/`→`papers/<run-id>/main.pdf`→`verdict.md` 全链条落盘记一轮。阈值 ≥1 轮完整跑通算推进。
- 次度量：critic accept 率与 revise 收敛轮数。revise→accept 在 3 轮内收敛算健康。

算力与时间预算：本机 pi 会话 + 宿主 lean 二进制 + 按需 GPU 跑批，无固定配额。记账按轮在任务产物里做，配置、种子、耗时进 `measured/`。

禁区四条：不伪造 `measured/` 数值；不改评测器语义迎合结论；不碰外部付费数据集与私有模型权重；model 只出 spec 不写 `experiment/` 代码。

## 当前工作模式：training live · 功耗约束（用户 2026-09-09 12:2x 解禁）

- 训练执行解禁：bench 可发起 torch 臂跑批。
- measured 新产物一律落 `runs/<run-id>/measured/`。禁写 `.archive/`，那里只存废弃历史。
- 功耗纪律（用户硬约束）：本树任意时刻同时存活的训练/拟合进程 ≤1，批内串行，跨配置矩阵也串行。
- 功耗纪律细则：优先 MPS 单进程；禁多 worker 并行 DataLoader。
- 功耗纪律细则：长跑批切时间片，单片 ≤45 min，片间让机散热；片进度写 `measured/run.log` 可续跑。
- 功耗纪律细则：每批在 `measured/environment.json` 记 wall-time、峰值内存与观察到的热/降频迹象，`pmset -g therm` 采样一行即可。
- 调度冲突时宁可晚出数，不许并发轰功率。
- 训练槽协议（spec §15「取得训练槽」的执行定义）：发起任何训练/拟合命令前 `mkdir runs/.train-slot` 原子抢占（原子 = 抢占动作一步完成，两个进程只会有一个成功）。
- 训练槽协议：抢占成功即 `echo "<task_id> <pid> <ISO>" > runs/.train-slot/holder`。
- 训练槽协议：槽已存在则读 holder——pid 活着就等待，5-10 min 轮询一次，等待期间先干不需槽的活；pid 死了 `rm -r` 接管，并在 run-log 记一次接管。
- 训练槽协议：交活/退出前 `rm -r runs/.train-slot` 释放。
- 待办挂账（supervisor 13:2x）：`runs/normalized-ssd-branch-003/static-check.md` 标题与 `mode: static-only` 头注属冻结期措辞，已过时——下一位触碰 003 产物面的 role（bench/model 按其任务书）顺手更新为 live 期口径，supervisor 不改 domain 文书正文。
- 过期护栏继续有效：`runs/*/DEPRECATED.md` 圈定数字不进稿件/verdict；开工先读本节与台账。

## 工作模型（射后不理）

射后不理 = 发出去就不等回复。

每个 session 的生命周期四步：恢复上下文 → 工作 → 激发下游（可选，若干）→ 交活退出。

session 对下游零等待。下游成果经文件与台账呈现，由接力任务唤醒合适的单位继续。

## 目录

- `pool/ideas.md`：idea 池，也是唯一队列，一条 idea 一个小节，checkbox 状态机 + note 追加行，格式见下。scout 取单消费，critic/scout 写终态与新行。
- `runs/<run-id>/`：一轮 idea 的全部过程件，含 `idea.json` 快照、`derivation.md`、`lean/`、`measured/`、`verdict.md`。
- `research/`：证据。其中 `frontier-notes.md` 是联网检索记录，格式为 URL + 单行结论，追加式。
- `experiment/`：领域代码。`evaluation/`：评测器。`papers/`：成稿，文件名为 `<run-id>.md`。
- `payload/`：注入给起始 role 的任务书落这里（`payload/first.md` 及后续）。
- `.onlyne/ws/aris/<role>/`：generate 渲出的角色工作区，内含细则 AGENTS.md、`.pi/` 三元组+插件引用、vendor 的 `.onlyne/agent/onlyne-agent-pi`、运行态。
- 改 role 上下文的做法：改 `.onlyne/templates/aris/<role>/`，再跑 `onlyne-server generate --root . --template aris/<role> --role <role> --force`。
- 模板 settings 的 packages 须写 agent_package 的字面绝对路径，generate 才触发 vendor 重写；写 `{{agent_package}}` 渲出形态缺 `../` 前缀，pi 不加载。
- `.onlyne/`：v1 集群面。跟踪的模板真相是 `spec.toml` 与 `templates/aris/<role>/`（AGENTS.md+`.pi/settings.json`）。
- 运行时禁入 git 的目录：`run/` socket、`store/` db、`keys/`、`logs/`、`ws/`（generate 渲出的角色工作区，产物零绝对路径）。
- v0 遗物冻结在 `.onlyne.v0-archive/`，内含旧 FIFO，勿递归读。
- 台账：v1 账本在 server store，用 `onlyne ledger --server-root .` pull 式读；v0 流水冻结导出 `runs/v0-ledger.csv`。
- `.agents/skills/`：预制领域 skill，随树分发（pi 沿父目录链发现）。现有两个：`paper-figures`（matplotlib conf 驱动绘图 + LaTeX 三线表与图规则，源自 guanyingc/latex_paper_writing_tips 与 dair-ai/ml-visuals）、`paper-writing`（稿件骨架 + LaTeX 细则 + 措辞纪律）。writer 出图出稿前、critic 审文字面时先读对应 skill。
- 主题状态：stage/entry_role 记在本文件（角色表 ★ 行与冷启动节），v1 无 flywheel.json。

路径约定：本文件与一切任务书里的路径都相对 swarm root。配套四条：

- worker session 的 cwd 在 `.ws/<name>/`，root 即 `../../`。读写知识文件用这个锚点；发现文件不存在先 `pwd` 确认站位。
- 工作面口径：草稿、中间件、探针、staged 代码先落在自己实例的 `work/`（私有，不入 git）；定稿产物一次性发布到任务书点名的 root 路径，并在 `runs/<run-id>/run-log.md` 记一行本地→发布映射。
- 追加式台账直写 root：pool/ideas.md、frontier-notes.md、run-log.md、measured/ 流件。
- peer 实例的 `../../<peer>/work/` 可只读翻看；交接与审稿判据是任务书与 root 发布物。
- vault 软链在 root `obsidian/` 下，worker 侧用 `../../obsidian/...` 访问，解析目标是同一 vault。

## Obsidian vault 对接与写作规范（全员遵守）

- vault 根：`~/OneDrive/new_document/humanresources`（vault 根，装配机自定）。root `obsidian/` 下四个软链直达 vault 相应位置：`obsidian/论文`→`论文/`（原文 PDF 归档）、`obsidian/reports`→`reports/`（精读报告）、`obsidian/draft`→`draft/`（日常学习与 idea）、`obsidian/templates`→`templates/`（写作规范与报告模板）。读用软链，写同样经软链落 vault，不在 ARIS 树里复制 vault 文件。
- 写作规范唯一入口：`obsidian/templates/writing-and-report-guide.md`；精读报告骨架用 `obsidian/templates/paper-report.md`。
- 该规范覆盖所有用户可见文字：`derivation.md`、`measured/summary.md`、`papers/<run-id>/main.tex` 与编译出的 `main.pdf`、`verdict.md`、`revisions.md`、vault 落库的精读报告。
- 规范要点：直接陈述、累加式、结论先行；数字带单位与出处（Table/Figure/公式编号或文件路径）；论文事实与「我的分析」分区；流程用 mermaid；数学用 `$$…$$` 独立公式块；YAML frontmatter 可解析；内部链接与 wikilink 可达。
- 该规范与本机全局写作规则同向（禁转折修辞），冲突时以更严格者为准。
- vault 写入白名单：本工作区只准往 vault 放 PDF 论文与 Markdown 叙事性文件。PDF 只进 `obsidian/论文/原文/<短名>.pdf`，含 supplement 则同名 `-supplemental.pdf`；Markdown 精读报告只进 `obsidian/reports/论文精读/<短名>-精读.md`，并在 `obsidian/reports/论文精读/00-索引.md` 登记（登记动作先读后改、增量更新）。
- 其余一切产物留在 ARIS 树内，不进 vault，落点用 `papers/`、`runs/`、`presentations/` 这些自建目录，涵盖 pptx、图片资产、代码、日志、快照、Workbook。
- `draft/` 是 idea 源之一：scout 每跳先读 `obsidian/draft/00-索引.md` 再读相关笔记，把值得开正式链路的判断转为 pool idea（`evidence` 指到 `obsidian/draft/<笔记>.md` 具体章节，`origin` 用 `derived` 并注明来源笔记）。
- 半成品纪律沿用 vault 约定：未核对结论进「证据边界与待核对项」，不直接当 claim 写进稿件。
- 人物画像不归本工作区：不读不写 vault 的 `人物/`、`关系图谱/`；reading/writing 任务保持人物档案创建关闭，已有规范人物页可 wikilink 引用，不新建。
- 精读报告自检跑 vault 校验器（只读调用，不往 vault 写脚本）：`env no_proxy='*' NO_PROXY='*' http_proxy= https_proxy= HTTP_PROXY= HTTPS_PROXY= python3 ~/OneDrive/new_document/humanresources/scripts/validate_reading_report.py <report.md>`，按其报错修 frontmatter、围栏、`$$` 定界符、来源锚点与内部链接。

## runs/<run-id>/ 布局（ARIS 主题增补）

默认结构（`idea.json`/`derivation.md`/`lean/`/`measured/`/`verdict.md`）保持不变。ARIS 映射产物按以下落点：

- `spec.md`：model 出的方法实现 spec 与评测器 spec（model 不写 `experiment/` 代码，bench 按此落地跑批）。
- `measured/summary.md`：bench 汇总值与 delta（delta = 相对基线的差值），每个 objective 一个实测值，每个 constraint 一个 pass/fail。
- `revisions.md`：writer 按 critic verdict 编号 finding 修订的记录。
- `run-log.md`：role 自己的台账（追加式）。`root-log.md` 文件名归 supervisor 专用，role 不自开同名台账。
- `verdict.md`：critic 一行 verdict（accept / revise / reject）+ 编号 finding。
- `papers/<run-id>/`：writer 成稿目录，位置在 `papers/` 下（`runs/` 下没有这一层），含 `main.tex`（NeurIPS 2024 风格，模板见 `papers/_template/neurips2024/`）+ `refs.bib` + `figs/`，编译出 `main.pdf`。结论先行，每个数字标注来源文件路径，open questions 单节。

## 评测契约（ARIS 复刻）

- objectives：每条 `{metric, evaluator, direction, epsilon, baseline}`。`evaluator` 是 `evaluation/` 下评测器的路径与运行命令；`direction` 取 `higher`/`lower`；`epsilon` 是判定阈值（提升幅度）；`baseline` 来源写清（基线配置、种子、数据切分，缺一视为无效基线）。实测值来自 `measured/`，评测 verdict 与实测一致才 pass。
- constraints：`check` 项含数据泄漏检查（训练/评测切分隔离声明）、随机种子固定声明、时间预算声明；每条 `{check, description}`，bench 在 `measured/summary.md` 给 pass/fail。
- 基线切分：主度量评测面切一份 held-out（比例写进契约）。lean/measured 迭代只在训练面跑；verdict 用冻结候选在 held-out 跑一次定生死，失败禁回炉再优化（防对评测面调参）。理念源：NVlabs/SoL-Pi 双 split 纪律，见 research/frontier-notes.md。
- pass_rule：`all`（ARIS 主题默认全过才 accept；探索性 idea 可在种子里写 `any` 并说明理由）。

idea 的 `evaluation` 字段按本节直接填写，缺项的 idea 不进池。

## onlyne v1 工具面（v1.0.0 GA + CLI 热补 main@ae429d2，两树同闸）

- 集群真相 = `.onlyne/spec.toml`（[server]+[[client]]，deny_unknown_fields，报错 `spec.toml:<行>: <msg>`）；改完 `onlyne server reload --server-root .`（--dry-run 配 spec-diff 预览），运行期零回写。
- role 在 pi 内的通信：`onlyne_send {to, text, kind:"task"|"note"}`（note 不建 session 不排队，离线 recipient_offline）；`onlyne_complete {outcome:"done"|"failed", text}` 交活。
- 接力派下一跳用 bash `onlyne handoff --to <role> --task <当前task_id> --text "<任务书>"`（parent_task+hop 血缘顺链；task_id 在注入帧头、`/onlyne` 或 receipt JSON 里查）。
- 失败交活用 complete outcome=failed，或 handoff 正文首行 `> hop-failed: <原因>`。
- 产物未齐用 outcome=cancelled，或干脆不 complete 等 idle 回收（回收 = 换一个全新 session id，旧档案留 .pi/sessions 可查）。
- 观测命令：`onlyne status|roles|sessions|ledger|faults|watch|history --server-root .`；pi 内 `/onlyne`。op_id 换体重发 conflict，重试原帧重发。
- supervisor 不注册 [[client]]：cwd=server-root 走 admin 面。第一发 `onlyne send --server-root . --from critic --to scout --file payload/first.md`（--from 须已注册持边角色，落账 admin=true）。
- 角色零上行边：completion 走 origin 免 ACL 特例自动回账，进来源 role 收件箱（queued 行，pull 式），反边不用声明。
- control：`onlyne control cancel|recycle|probe|snapshot --task <id>`（属主或 admin 角色署名）。backend：ONLYNE_BACKEND=zellij|orca|fake，探测序 orca→zellij→fake（omp 勘误 2026-09-11，实现推翻 v1-PLAN 旧序）。
- 调度参数承接：per-role `[client.timeout]{ready_ms,running_ms,idle_ms}`（bench running_ms=3600000 承接旧 busy_secs）+ `[client.intent]{attempts=100000, backoff 六档}`（attempts=0 表示首次失败即 exhausted，已弃用）。

## 任务书四段（handoff/send 的 text）

```text
目标：<一句话，做完算什么>
输入：<必须读的文件路径，runs/ 与 research/ 为准>
期望产物：<写到哪里的什么文件，格式要求>
下一跳建议：<完成后该 handoff 谁、干什么；没有就写 无>
```

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

状态机：`[ ]` queued → `[>]` running（scout 取单时改）→ `[x]` keep / `[!]` failed（critic 归档时改）。`evaluation` 行保持 JSON 内联，字段口径与历史 `.archive/ideas-v1.jsonl` 一致。

四条进池硬门：evidence 为空、objectives 为空、done_when 为空、headroom 预筛不过，任一条命中即不进节。headroom 预筛：写进池子前沿上单行判据——哪个 measured/ 数字或 frontier-notes 行暴露了缺口、余量多大。指得出数字才占下游 rollout；指不出的候选不写进节，负证据照记进 frontier-notes 一行，下轮检索先翻旧账。

## 角色表（本主题拓扑的唯一事实源）

角色名与 `.agents/.schedule/<目录名>` 一一对应；增删 role 同时改这张表和这些目录。

supervisor 代发 `onlyne send --from <role>`、role 侧 `onlyne_send`/`onlyne handoff --to` 的目标名，都查这张表。

`entry` 列标出第一发的注入对象，全表恰好一个 `★`。

| role | 职责 | 上游 | 下游 | entry | model |
|---|---|---|---|---|---|
| scout | 前沿检索与 idea 入池 + 取 queued 派工（ARIS `/idea-discovery`：research-lit→idea-creator→novelty-check） | critic, model/bench（失败回传）, writer（补检索） | model | ★ | axonhub/supercheap/low |
| model | 推导 + Lean 形式化 + 出 spec（ARIS `/experiment-bridge` 前半：plan→spec；不写 `experiment/` 代码） | scout, critic（revise-理论） | bench, writer, scout（失败回传/补检索） | | axonhub/generic-researcher-powerful/max |
| bench | 跑批与测量，按 model spec 落地并落 `measured/`（ARIS `/experiment-bridge` 后半：deploy→collect） | model | writer, scout（失败回传） | | axonhub/supercheap/minimal |
| writer | 成稿（ARIS `/paper-writing`：plan→figure→write→compile；初稿与修订稿） | model, bench, critic（revise-文字） | critic, scout（补检索） | | axonhub/supercheap/high |
| critic | 审稿 verdict + 归档 + 提下一条 idea（ARIS `/auto-review-loop` 4 轮评审 + cross-model jury + `/rebuttal` 语义：revise 循环或 accept/reject 终局） | writer | writer（revise-文字）/ model（revise-理论）/ scout（accept/reject 开新轮） | | axonhub/generic-researcher-powerful/high |

四条边各自含义：

- critic→model 是 revise-理论：推导或 spec 有缺陷，重推。
- critic→writer 是 revise-文字：文字、claim、结构修订，不动推导。
- writer→scout 是补检索：稿件缺证据，要文献。
- model→scout 是失败回传与补检索：Lean 失败带现场路径；证据缺口写清要什么来源。

supervisor 不在工作环里：没有任何 role 的上游或下游是 root。supervisor 不注册 [[client]]，admin 面代发除外，签名用持边角色。

supervisor 只做工作区维护，条目为：idle 判定与报告、generate/reload、spec 对表、知识产物 git commit、人机传话。supervisor 不参与工作流转。

接力闭环在五个 role 之间：

- 主环 scout→model→bench→writer→critic→scout（accept/reject 开新轮）。
- 修订环 critic→writer（revise-文字）/ critic→model（revise-理论）。
- 回传边 model→scout、bench→scout、writer→scout。

三档模型语义：

- `generic-researcher-powerful` 只做纯理论工作，有 agent 能力，不写代码。
- `generic-researcher-weak` 科研能力强，能指导 worker 写代码，必要时自己小写两段。
- `supercheap` 写代码强且便宜，经常思考过度把自己绕晕，不能长时间独立工作。bench 配 low effort，2026-09-09 自 minimal 上调一档，仍为压住它别加戏。

supervisor 会话档位见根 `.onlyne/swarm.workspace.jsonc`（`generic-researcher-weak` + medium，维护位）。

scout

本名字同时是 admin 面 `onlyne send --to scout` 与 role 侧 `onlyne_send {to:"scout"}` 的目标参数。

## 飞轮宏观流（接力闭环，从角色表推导）

接力规则按角色表的 `上游` / `下游` 列执行。supervisor 不进工作环，只维护工作区。通用条款五条：

1. scout：从 pool 取 queued idea，固化 `runs/<run-id>/idea.json`（status 改 running），派给 model；同时承担检索与新 idea 入池。
2. 每个 role：完成后按自己的 `下游` 列 `onlyne handoff` 接力任务书，然后 `onlyne_complete` 交活退出。角色零上行边，回执走 origin 自动通道。
3. role 的产物未齐时 `onlyne_complete outcome:"cancelled"`（或不 complete 等 idle 回收）静默交回，等接力唤醒，不写无依据产物。
4. critic 闭环：revise-文字则 handoff writer 修订接力；revise-理论（推导或 spec 有缺陷）则 handoff model 重推接力；accept/reject 则归档（keep 留 papers/ 并把 idea 状态改 keep，failed 记 verdict.md 并改 failed），从 open questions 或失败结论提取下一条 idea 入池，再 handoff scout 开新轮。
5. 回传 scout 的任务共三种：
   - model 的失败回传（Lean 失败，接力正文首行 `> hop-failed` + 现场路径）与补检索（证据缺口，写清缺哪段文献、要什么来源）。
   - bench 的失败回传（跑不动，接力正文首行 `> hop-failed` + 现场路径 + 失败命令与日志路径）。
   - writer 的补检索（稿件哪一节缺什么证据、要什么来源）。
   scout 处理完后走正常派工跳（取 queued 派给 model）。

环路在五个 role 之间自转：主环 scout→model→bench→writer→critic→scout（新轮）；修订环 critic→writer（文字）/ critic→model（理论）；回传边 model→scout、bench→scout、writer→scout。人随时可接管任一 session。自激发无熔断，终结靠人 `onlyne control cancel --task <id>` 或会话接管。supervisor（人 + root 会话）只做维护：idle 判定与报告、generate/reload、spec 对表、知识产物 git commit、人机传话。

## 冷启动与第一发

装配完成的瞬间，工作区处于这些事实下：

- `stage=live`，`theme/<slug>` 分支已建，装配材料已消失。
- server 未跑（装配不起常驻进程）；`onlyne-server run --root .` 通电后逐 role `onlyne client start` 挂载。
- `tasks` 表 0 行，`.ws/<role>` 下无 session，`runs/` 空，`papers/` 空，`pool/ideas.md` 只有种子或空。
- 飞轮是反应式的：没有入站任务就什么都不会发生。`server run`+`client start` 属于通电，属于开跑。

启动动作二选一：

1. 用户给方向，supervisor 写 `payload/first.md`（含问题、约束、期望），执行
   `onlyne send --server-root . --from critic --to <entry_role> --file payload/first.md`。
2. 用户自己在 CLI 投第一发（同上 admin 面命令），supervisor 事后从 ledger 与 `runs/` 接上下文。

supervisor 只负责把第一发投进 `★` role，不参与后续流转；环成形后自转。

本主题的起始 role 是投第一发时 `--to` 的那个名字（见上表 entry 列，★=scout）。第一发落地后环自转：起始 role 取 queued 固化 idea.json 派 model，后续每轮的推进靠接力任务，启动只需要一发，supervisor 不参与流转。

## 维护与配置（supervisor 用，2026-09-12 按 v1.0.0 GA 对表；beta.3 期条款已就地更新）

- 配置唯一入口是 `.onlyne/spec.toml`（拓扑/prose/ACL/timeout/intent/agent_package/cert_pin）与 `.onlyne/templates/aris/`（细则+模型三元组）。
- 生效路径：spec 改→reload；模板改→该 role generate --force。无 sync/overlay/bootstrap 概念。
- 装役：现役 = redesign worktree 构建、`~/.cargo/bin` 五件（onlyne 1.0.0 + server/client/tui/gateway），热补单 main@ae429d2 已含；crates.io 发布中（6/18），全绿后统一写 `cargo install onlyne-cli onlyne-server onlyne-client onlyne-gateway onlyne-tui` 与 `pi install npm:pi-onlyne`。插件 canonical = redesign worktree 的 `plugins/onlyne-agent-pi`（仓库 b810f1d 已删 integrations/pi-onlyne 旧孪生=无守卫过期码），spec `agent_package` 与五模板 settings 的 packages 均指该绝对路径；v1.0.0 tag 后增量（cli socket 修复/spec alias/tui 岛剪枝/manifest 钉版）随下次 build 带上。
- server/tui 常驻 = 在 **ARIS worktree 的可见前台 tab** 里跑（`orca terminal create --worktree path:<本树> --command "onlyne-server run --root ."`，tui 同款），关 tab 即停环；禁入任何 agent 后台。client 起 tab 的 worktree 决定会话 spawn 定向（错配案：hub 起 client 继承它方 ORCA_WORKTREE_ID → 会话 cd 进错检出即死）。
- 五角色 client = `onlyne client start --workspace .onlyne/ws/aris/<role>` 守护态（pid/socket 在 ws 运行面）；重启环后逐个 start，或 `client run` 进各自 tab。
- 崩溃残留处理：`onlyne server repair`（清 running delivery 类残留在 v1 的对应物），再用 `onlyne faults` 看故障队列（intent exhausted 落此，`repair retry` 人工续
- 恢复运行纪律（0912 补）：client 重挂后、投新任务前，对 `onlyne sessions` 里每条 working 逐个 `onlyne server repair inspect --task <id>`；pane 已死而 lifecycle 仍 working 的残影用 `repair close` 收口（faults 只覆盖投递层，running_ms 判定活在 client 侧，client 重启后旧账无人续判；control cancel 属主判定挡 supervisor，close 走 admin 面可用）。伴生检查：`ps` 扫 v0 遗留守护进程（ppid=1 且与 runs/ environment.json 端口引用对上的回收，精确 PID）。
- 杀单个 client 用其 ws pid 文件精确 PID，禁止 pkill 按名杀。
- 清理孤儿进程前先核对身份：`brew services`、launchd、其他 app 拉起的常驻服务不属于 swarm。杀之前查 launchd label / 父进程 / 端口归属，只回收 `.onlyne/run/` pid 文件与 client 注册表里存在的进程。误杀系统服务比留一个孤儿严重得多。
- hindsight bank 重建、hindsight.json 实例面条款：v1 插件无该子系统，实例 `.pi/` 归装机者自管，暂不提供集中重建步骤（需要时按 pi hindsight 扩展原生方式现场配）。

## 纪律

- 改 `experiment/`、`evaluation/` 前读 runs/ 里上一轮记录；改动在任务产物里写明。
- 数值只从 measured/ 引，报告只写跑出来的东西。
- 存在 `runs/<run-id>/DEPRECATED.md` 的 run，其废弃范围内数字一律不作证据，只可按该文件口径引用为已废弃 baseline。
- 落点口径：新 run 的实测产物仍落 `runs/<run-id>/measured/`。
- 带 `DEPRECATED.md` 的历史 run，其 `measured/` 已于 2026-09-09 10:32 移出 `runs/`，落 `.archive/deprecated-mlx-20260909/`（路径对照、使用口径与取回命令见该目录 `README.md`）。
- 旧 `runs/<run-id>/measured/` 路径在盘上不再存在，引用前按对照表解析。
- 失败也交活：跑不动的结论写进 runs/，`onlyne_complete outcome:"failed"` 交失败报告（text 首行 `> hop-failed: <原因>` + 现场路径），让下游有据可依。
- `.onlyne.v0-archive/` 里存着 v0 的命名管道（`channels/loopback/in|out`）：对它做任何递归读取（`grep -r`、`find` 后串 read）仍会阻塞在 FIFO 上把会话卡死，整目录只按单文件路径取旧件。
- v1 运行态（`run/`、`store/`、`keys/`、`logs/`）可正常读，任务与账目走 `onlyne ledger|sessions|watch --server-root .`。
