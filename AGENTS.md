# formal-research 大循环 — onlyne v1 公共约定（约定骨架）

主题状态：stage=design，分支 `theme/formal-research`。

这份文件放在 server-root（本仓根目录）。pi 沿父目录自动拼上下文，树内每个 session 都读到同一份约定。

本体论先说清：运行时 + 工作区（数据、记录、上下文文件）才是 agent 的本体；workspace = role，指该角色的「记忆 + 设定 + 历史文件」；session = 该 role 手头的一件工作，做一跳就回收，来消息拉新 session。一切值得写入持久状态的信息应写尽写，不落文件的等于没发生。

一切信息落文件。每个结论都能回溯到项目目录、papers/ 或台账行（`onlyne ledger --server-root .`）。

## 设计哲学（用户裁定 0916 深夜，凌驾全部细则）

- 造的是有向有环图。theory ⇄ experiment ⇄ 中期检查天然成环，实践中理论-实验-理论反复迭代属常态；角色沿角色表的边自由往返，关口是环上节点。
- 少约束，多自纠。错误出现时先由环上的边裁决（对线、联名上报、revise、rectify），禁止为个例失败新增兜底条款。
- 抛弃状态机。状态行、轮次计数、枚举态全部废止：多任务同时在飞轮中跑、单 role 多 session、单闭环多 session 都是常态。全部真相 = 文件 + git + onlyne 台账。
- 版本交给 git。段落只增不改，冻结与回查靠提交历史，存底/快照类文书废止。

## 大循环（formal-research）

模仿高校与工业界正式科研全流程组织本工作区。大循环：开题黑盒（pi 负责，产出头四段）→ 开题对线（examiner 攻不破才放行）→ 执行（含中期）→ 验收（中期检查/结题验收）→ 新开题。域按序接力：initiation（pi、examiner）→ theory（speculator、theorist）→ experiment（runner）→ review（chair、referee、qa）→ archive（planner）。common 层跨全部阶段常驻：librarian（检索）与 scribe（代笔）为公共资源，任何 role 任何时点可点单；referee 不用代笔（意见书独立性条款）。域内允许内部循环；跨域边以角色表与 `.onlyne/spec.toml` 的 ACL 为准，两处同源。

三个关口（口径与 `research_project/README.md`「关口」节同源）：

- 开题审查=敌意对线：examiner（powerful/max，职责让项目死掉）持四类攻击（前提崩塌/已被做过/不可测/自相矛盾）与 pi 逐轮攻防，记录追加 `research_project/<项目短名>/对线记录.md`。弹药耗尽 → `pass`（开工令 → theorist 先形式化头部四段命题 → speculator 带陈述出假设与方案）；存在化解不了的实心攻击或致命实锤 → `fail`（planner 归案）。攻击必锚到段+句+证据，无锚无效。轮数不设限、不作终止条件，判据只看弹药与证据。
- 中期检查：qa 备齐送审包 `research_project/<项目短名>/packs/中期送审包.md`，chair + referee×3 合议 `continue` / `rectify` / `stop`。stop 判据是实据：整改后攻击面未缩小、measured/ 无可归因进展。rectify 轮数不设限。
- 结题验收：qa 备齐送审包 `research_project/<项目短名>/packs/结题送审包.md`（含设计段全部结果节 + 约束核验 + 断言对表），chair + referee×3 依结论段判 `accept` / `reject`。accept → planner 记档开新题。

判词落 `research_project/<项目短名>/gates/<关口>判定.md`：判词 + 依据 + 签字 + 时刻。referee 独立意见书落 `research_project/<项目短名>/gates/<关口>判定-评审<甲|乙|丙>.md`。三个关口默认全自动托管，planner 产出照例不待批——这就是全自动飞轮的意义。`human_gate` 条款：用户对特定主线开放请示时通知 supervisor/planner，项目文件头以 `human_gate:` 点名哪些关口可请求；被点名关口的主责角色经 pi-intercom 发 supervisor 的 omp 会话（地址 `Main`），阻塞等 approve，supervisor 向人开 ask 批复后代落 gates/ 判词。人不在场=有事，阻塞即正确状态，不设降级兜底。缺省未列 = 全自动。此条款仅在用户明示的主题生效。

关口防护四条（项目级范围锁/止损线已废止，防护由关口规则承担）：

- referee 意见书逐条回查「最终验证依据」；越依据 finding 直接 stop 级。
- qa 三约束（泄漏 / 确定性 / 预算）原样保留在送审包。
- 中期检查 stop 凭实据（攻击面未缩、无进展），不凭 rectify 计数。
- qa 连续 2 包无有效读数（valid 率 <0.5 或全部 objective=TBD）→ chair 必停 + planner 归案。

「什么算进步」分主次两条度量：

- 主度量：端到端跑通轮数。`research_project/<项目短名>.md` 头定稿 → 假设段（假设/论据/形式化）→ 设计段（设计/结果 + `measured/`）→ `papers/<项目短名>/main.pdf` → `gates/结题判定.md` 全链条落盘记一轮。阈值 ≥1 轮完整跑通算推进。
- 次度量：关口 revise/rectify 收敛情况，按台账如实计数，不设健康上限。

算力与时间预算：本机 pi 会话 + 宿主 lean 二进制 + 按需 GPU 跑批，无固定配额；单项目预算写进 `<项目短名>.md` 的 `budget` 字段。记账按轮在任务产物里做，配置、种子、耗时进 `measured/`。

禁区四条：不伪造 `measured/` 数值；不改评测器语义迎合结论；不碰外部付费数据集与私有模型权重；speculator 出假设与实验设计、theorist 出形式化，两者都不写 `experiment/` 代码。`spec.md` 独立文书废止，runner 唯一输入 = 设计段实验设计段 + 断言清单。

### 解释文规范

凡向人解释研究、实验、系统状态的正文（答复、报告、`derivation.md`、`verdict.md`、精读报告、论文 intro 类文字），按下面阶梯组织。代码、命令、行内注释按本节精神从简执行。

1. 对象先行：第一段说清在比什么、要回答什么问题、答案是什么形态。读者无需读过任何仓库文件即可进入。
2. 测量先于过程：给出量的物理含义、单位、一个可感的换算锚点（多少算大、多少算小），再谈流程。
3. 实验环境落地：硬件、软件栈、规模、一次几个进程、数据是什么。
4. 术语依赖序展开：每个术语首次出现就用日常语言给物理定义，此后才可引用。定义链禁止回环（用 seed 解释 seed、用 delta 解释 delta 即违例）；记号（`O1`、`K=3`、`L₁`、缩写）先有对应白话对象才可出现。
5. 数字带单位与量级：阈值、效应、噪声同轴并报，读者能自行判断哪个结论可辨、哪个到分辨极限。
6. 比喻限两处以下：只用于第 4 条物理定义完成之后的加速理解；技术定义句内禁比喻。
7. 结尾回指问题：用本正文词汇表重述一遍结论，一两句，零新术语。
8. 发送前自检：扫一遍正文，任何词的解释出现在使用位置之后即重排或删词。

本树全部人读产物（`research_project/<项目短名>.md`、proposals/、packs/、gates/、measured/summary.md、papers/、revisions.md）按上列八条组织。vault 落库细则见下节写作规范。

## 当前工作模式：training live · 功耗约束（用户 2026-09-09 12:2x 解禁）

- 训练执行解禁：runner 可发起 torch 臂跑批。
- measured 新产物一律落 `research_project/<项目短名>/measured/`。禁写 `.archive/`，那里只存废弃历史。
- 功耗纪律（用户硬约束）：本树任意时刻同时存活的训练/拟合进程 ≤1，批内串行，跨配置矩阵也串行。
- 功耗纪律细则：优先 MPS 单进程；禁多 worker 并行 DataLoader。
- 功耗纪律细则：长跑批切时间片，单片 ≤45 min，片间让机散热；片进度写 `measured/run.log` 可续跑。
- 功耗纪律细则：每批在 `measured/environment.json` 记 wall-time、峰值内存与观察到的热/降频迹象，`pmset -g therm` 采样一行即可。
- 调度冲突时宁可晚出数，不许并发轰功率。
- 训练槽协议（训练槽协议的执行定义）：发起任何训练/拟合命令前 `mkdir .train-slot`（仓根，跨项目全局串行锁）原子抢占（原子 = 抢占动作一步完成，两个进程只会有一个成功）。
- 训练槽协议：抢占成功即 `echo "<task_id> <pid> <ISO>" > .train-slot/holder`。
- 训练槽协议：槽已存在则读 holder——pid 活着就等待，5-10 min 轮询一次，等待期间先干不需槽的活；pid 死了 `rm -r` 接管，并在 run-log 记一次接管。
- 训练槽协议：交活/退出前 `rm -r .train-slot` 释放。
- 功耗纪律与训练槽协议自旧跑批位细则换绑而来（历史参照：commit f36d3de），条款内容不变。
- 过期护栏继续有效：`research_project/<项目短名>/DEPRECATED.md` 圈定数字不进稿件/判词；开工先读本节与台账。

## 工作模型（射后不理）

射后不理 = 发出去就不等回复。

每个 session 的生命周期四步：恢复上下文 → 工作 → 激发下游（可选，若干）→ 交活退出。

session 对下游零等待。下游成果经文件与台账呈现，由接力任务唤醒合适的单位继续。

## 目录

- `research_project/<项目短名>.md`：研究项目文件（一项目一文件，头四段生长制）。过程件目录见下条，细则见 `research_project/README.md`。旧 `pool/` 废止。
- `research_project/<项目短名>/`：项目过程件（`dispatch.md`、`对线记录.md`、`run-log.md`、`revisions.md`、`lean/`、`measured/`、`data/`、proposals/packs/gates/），追加式只增不改，版本靠 git。旧 `runs/<run-id>/` 制与开题存底文书废止（runs/ 仅存 aris 历史档案）。
- `research/`：证据。其中 `frontier-notes.md` 是联网检索记录，格式为 URL + 单行结论，追加式。
- `experiment/`：领域代码。`evaluation/`：评测器。`papers/`：成稿，目录名 `<项目短名>/`。
- `payload/`：注入给起始 role 的任务书落这里（`payload/first.md` 及后续）。
- `.onlyne/ws/formal/<phase>/<role>/`：generate 渲出的角色工作区（路径随 template 子路径 `formal/<phase>/<role>`，与 server name 无关），内含细则 AGENTS.md、`.pi/` 三元组+插件引用、vendor 的 `.onlyne/agent/onlyne-agent-pi`、运行态。`<phase>` 阶段层：initiation={pi,examiner}、common={librarian,scribe}（公共资源层）、theory={speculator,theorist}、experiment=runner、review={chair,referee,qa}、archive=planner。
- 改 role 上下文的做法：改 `.onlyne/templates/formal/<phase>/<role>/`，再跑 `onlyne-server generate --root . --template formal/<phase>/<role> --role <role> --force`。
- 模板 settings 的 packages 须写 agent_package 的字面绝对路径，generate 才触发 vendor 重写；写 `{{agent_package}}` 渲出形态缺 `../` 前缀，pi 不加载。
- `.onlyne/`：v1 集群面。跟踪的模板真相是 `spec.toml` 与 `templates/formal/<phase>/<role>/`（AGENTS.md+`.pi/settings.json`）。
- 运行时禁入 git 的目录：`run/` socket、`store/` db、`keys/`、`logs/`、`ws/`（generate 渲出的角色工作区，产物零绝对路径）。
- v0 遗物冻结在 `.onlyne.v0-archive/`，内含旧 FIFO，勿递归读。
- 台账：v1 账本在 server store，用 `onlyne ledger --server-root .` pull 式读；v0 流水冻结导出 `runs/v0-ledger.csv`。
- `.agents/skills/`：预制领域 skill，随树分发（pi 沿父目录链发现，与本文件同机制）。现有四个：`paper-figures`（matplotlib conf 驱动绘图 + LaTeX 三线表与图规则，源自 guanyingc/latex_paper_writing_tips 与 dair-ai/ml-visuals）、`paper-writing`（稿件骨架 + LaTeX 细则 + 措辞纪律）、`onlyne-supervisor`（集群运维面：通电、派工、看账、repair）、`onlyne-role`（role 会话侧 handoff/complete 纪律）。scribe 出图出稿前、chair 与 referee 审文字面时先读对应 skill；supervisor 与 role 会话开工前读 onlyne-* 对应那篇。
- 主题状态：stage/entry_role 记在本文件（标题下行、角色表 ★ 行与冷启动节），v1 无 flywheel.json。

路径约定：本文件与一切任务书里的路径都相对 server-root。配套五条：

- role session 的 cwd 在 `.onlyne/ws/formal/<phase>/<role>/`，root 即 `../../../../../`。读写知识文件用这个锚点；发现文件不存在先 `pwd` 确认站位。
- 工作面口径：草稿、中间件、探针、staged 代码先落在自己 ws 的 `work/`（私有，不入 git）；定稿产物一次性发布到任务书点名的 root 路径，并在 `research_project/<项目短名>/run-log.md` 记一行本地→发布映射。
- 追加式台账直写 root：`research_project/<项目短名>.md`、frontier-notes.md、run-log.md、measured/ 流件。无中心账本，也无状态登记：状态隐含在飞轮中，全部真相 = 文件 + git + onlyne 台账；终局 conclude 段归 planner。
- peer 实例的 `../../<peer>/work/`（同一 `.onlyne/ws/formal/<phase>/` 下的兄弟 ws；跨阶段用 `../../../<phase>/<peer>/work/`）可只读翻看；交接与审稿判据是任务书与 root 发布物。
- vault 软链在 root `obsidian/` 下，worker 侧用 `../../../../../obsidian/...` 访问，解析目标是同一 vault。

## Obsidian vault 对接与写作规范（全员遵守）

- vault 根：`~/OneDrive/new_document/humanresources`（vault 根，装配机自定）。root `obsidian/` 下四个软链直达 vault 相应位置：`obsidian/论文`→`论文/`（原文 PDF 归档）、`obsidian/reports`→`reports/`（精读报告）、`obsidian/draft`→`draft/`（日常学习与 idea）、`obsidian/templates`→`templates/`（写作规范与报告模板）。读用软链，写同样经软链落 vault，不在本树里复制 vault 文件。
- 写作规范唯一入口：`obsidian/templates/writing-and-report-guide.md`；精读报告骨架用 `obsidian/templates/paper-report.md`。
- 该规范覆盖所有用户可见文字：`derivation.md`、`measured/summary.md`、`papers/<项目短名>/main.tex` 与编译出的 `main.pdf`、`revisions.md`、gates/ 判词、vault 落库的精读报告。
- 规范要点：直接陈述、累加式、结论先行；数字带单位与出处（Table/Figure/公式编号或文件路径）；论文事实与「我的分析」分区；流程用 mermaid；数学用 `$$…$$` 独立公式块；YAML frontmatter 可解析；内部链接与 wikilink 可达。
- 该规范与本机全局写作规则同向（禁转折修辞），冲突时以更严格者为准。
- vault 写入白名单：本工作区只准往 vault 放 PDF 论文与 Markdown 叙事性文件。PDF 只进 `obsidian/论文/原文/<短名>.pdf`，含 supplement 则同名 `-supplemental.pdf`；Markdown 精读报告只进 `obsidian/reports/论文精读/<短名>-精读.md`，并在 `obsidian/reports/论文精读/00-索引.md` 登记（登记动作先读后改、增量更新）。
- 其余一切产物留在本树内，不进 vault，落点用 `papers/`、项目目录、`presentations/` 这些自建目录，涵盖 pptx、图片资产、代码、日志、快照、Workbook。
- `draft/` 是 idea 源之一：librarian 每跳先读 `obsidian/draft/00-索引.md` 再读相关笔记，把值得开正式链路的判断转为研究项目（`evidence` 指到 `obsidian/draft/<笔记>.md` 具体章节，`origin` 用 `derived` 并注明来源笔记）。
- 半成品纪律沿用 vault 约定：未核对结论进「证据边界与待核对项」，不直接当 claim 写进稿件。
- 人物画像不归本工作区：不读不写 vault 的 `人物/`、`关系图谱/`；reading/writing 任务保持人物档案创建关闭，已有规范人物页可 wikilink 引用，不新建。
- 精读报告自检跑 vault 校验器（只读调用，不往 vault 写脚本）：`env no_proxy='*' NO_PROXY='*' http_proxy= https_proxy= HTTP_PROXY= HTTPS_PROXY= python3 ~/OneDrive/new_document/humanresources/scripts/validate_reading_report.py <report.md>`，按其报错修 frontmatter、围栏、`$$` 定界符、来源锚点与内部链接。

## 项目附件目录布局（research_project/<项目短名>/）

追加式、只增不改、版本交给 git；run-id、轮次与开题存底文书废止（`idea.json` 同废）。过程件落点：

- `lean/`：theorist 形式化产物（编译过的可行性推导链 + 陈述↔论据对照表），指针挂 `<项目短名>.md` 假设段形式化段。
- `measured/summary.md`：runner 汇总值与 delta（delta = 相对基线的差值），每个 objective 一个实测值，每个 constraint 一个 pass/fail。
- `revisions.md`：scribe 按关口判词编号 finding 修订的记录。
- `run-log.md`：role 自己的台账（追加式）；每段落笔记一行。`root-log.md` 文件名归 supervisor 专用，role 不自开同名台账。
- 关口判词（chair 一行 verdict：continue / rectify / stop / accept / reject + 编号 finding）正本落 `gates/`，另存 run 内副本的做法随轮次制同废。
- `papers/<项目短名>/`：scribe 成稿目录，位置在 `papers/` 下（项目目录里没有这一层），含 `main.tex`（NeurIPS 2024 风格，模板见 `papers/_template/neurips2024/`）+ `refs.bib` + `figs/`，编译出 `main.pdf`。结论先行，每个数字标注来源文件路径，open questions 单节。
- 问题层分析并入 `<项目短名>.md` 头部「问题背景」（pi 主笔，只提问不解答）。`spec.md` 独立文书废止。

## 评测契约

- objectives：每条 `{metric, evaluator, direction, epsilon, baseline}`。`evaluator` 是 `evaluation/` 下评测器的路径与运行命令；`direction` 取 `higher`/`lower`；`epsilon` 是判定阈值（提升幅度）；`baseline` 来源写清（基线配置、种子、数据切分，缺一视为无效基线）。实测值来自 `measured/`，评测 verdict 与实测一致才 pass。
- constraints：`check` 项含数据泄漏检查（训练/评测切分隔离声明）、随机种子固定声明、时间预算声明；每条 `{check, description}`，qa 在 `measured/summary.md` 核验 pass/fail。
- 基线切分：主度量评测面切一份 held-out（比例写进契约）。lean/measured 迭代只在训练面跑；verdict 用冻结候选在 held-out 跑一次定生死，失败禁回炉再优化（防对评测面调参）。理念源：NVlabs/SoL-Pi 双 split 纪律，见 research/frontier-notes.md。
- pass_rule：`all`（本主题默认全过才 accept；探索性任务可在种子里写 `any` 并说明理由）。

`<项目短名>.md` 设计段实验设计的 pass 判据按本节字段直接填成字面结论行，字段缺项不交 runner；头四段（含最终验证依据）由只增不改段权+git 历史冻结，供评测器与关口回查。

## 运行时能力面（每个 role 都是 pi coding agent 会话）

- 各 role 放开用 pi 本体的一切工具：文件读写、检索、eval、subagent 系统——预算无上限，数量与深度不设配额。能拆的活拆给 subagent 并行干，主会话做判断与整合；会话回收只回收内存，工具与 subagent 每次会话都在。
- 自带 web_search 与 librarian 的分工：web_search 是自用裸检索——快、散、查完即弃，不落档、不经排队，看个新现象顺手查它。librarian 是专职文献官——除了同样会 web_search，她还整理分类、对照本工作区历史文件、当前任务与文献存档（`research/frontier-notes.md` 行锚、obsidian draft 索引），产出可被引用与回查的归档行。要「谁做过什么、撞不撞车、证据链」这种判断，派单给她；只要「这东西是什么」，自己搜。

## onlyne v1 工具面（版本口径：追 latest，闸只设 protocol=1 下限）

- 装具与插件各追自己渠道的最新，命令里没有版本号：升级 `cargo install --force onlyne-cli onlyne-server onlyne-client onlyne-gateway onlyne-tui` + `pi install npm:pi-onlyne`。onlyne 随时发版，每个小版本装进来的都是 bug fix；`onlyne version` 的 `protocol:1` 是兼容判据，各 crate 版本号独立前进。工具面事实以 `<onlyne 仓>`（本机 onlyne checkout，main 分支）源码与当期 `--help` 为准，本树只读它。
- 集群真相 = `.onlyne/spec.toml`（[server]+[[client]]，deny_unknown_fields，报错 `spec.toml:<行>: <msg>`）；改完 `onlyne reload --server-root .`（`reload` 无 `--dry-run`，看待应用差异用只读动词 `onlyne spec_diff --server-root .`，别名 `spec-diff` 同解），运行期零回写。
- role 在 pi 内的通信：`onlyne_send {to, text, kind:"task"|"note"}`；note 骑在对方已活的 session 上，目标离线或在线无 working session 都直接 `recipient_offline`（本 spec `note_queue = false`；要排队先把该键设 true 并带 `--ttl`，到点记 expired）。`onlyne_complete {outcome:"done"|"failed"|"cancelled", text}` 交活。
- 接力派下一跳用 bash `onlyne handoff --to <role> --task <当前task_id> --text "<任务书>"`（parent_task+hop 血缘顺链；task_id 在注入帧头、`/onlyne` 或 receipt JSON 里查）。
- 失败交活用 complete outcome=failed，或 handoff 正文首行 `> hop-failed: <原因>`。
- 产物未齐用 outcome=cancelled（bash 面 `onlyne complete --task <id> --outcome cancelled --head-from local --text "<说明>"`；`--head-from` 必填，`local` 用本行 text 当 head，`ledger` 回读已存 head），或干脆不 complete 等 idle 回收（回收 = 换一个全新 session id，旧档案留 .pi/sessions 可查）。
- 观测命令：`onlyne status|roles|sessions|ledger|faults|watch|history --server-root .`；pi 内 `/onlyne`。op_id 换体重发 conflict，重试原帧重发。
- supervisor 不注册 [[client]]：cwd=server-root 走 admin 面。第一发 `onlyne send --server-root . --from planner --to pi --file payload/first.md`（--from 须已注册持边角色，落账 admin=true）。
- 角色零上行边：completion 走 origin 免 ACL 特例自动回账，进来源 role 收件箱（queued 行，pull 式），反边不用声明。
- control：`onlyne control cancel|recycle|probe|snapshot|focus --task <id>`（属主或 admin 角色署名；`--from`/`--task` 是全局 flag，子命令前后都认）。backend：`ONLYNE_BACKEND` 取 `herdr|orca|zellij|exec|fake|auto`，留空或 `auto` 时探测序 herdr→orca→zellij，`exec`/`fake` 只认点名，探不到 `onlyne-client run` 退 5 并报 NO_SUPPORTED_HOST（判定在 `<onlyne 仓>/crates/onlyne-session/src/backend/mod.rs::select_backend_from_env`）；`onlyne-client doctor` 只读打印本机判定，恒退 0。
- 调度参数承接：per-role `[client.timeout]{ready_ms,running_ms,idle_ms}`（默认 30000/120000/60000，runner running_ms=3600000 承接旧 busy_secs）+ `[client.intent]{attempts, backoff_ms}`（默认 attempts=3、backoff 三档；本主题用 attempts=100000 + 六档长跑）。
- `relay_required`（任务主下游，单值）与角色表 `relay` 列同源；ACL 终表双边互认，边成立需两端都列。

## 任务书三段（handoff/send 的 text）

```text
目标：<一句话，做完算什么>
输入：<必须读的文件路径，项目目录与 research/ 为准>
期望产物：<写到哪里的什么文件，格式要求>
```

输入路径必须真实存在。接收方 session 是全新上下文，任务书里没写的路径它找不到。不设「下一跳建议」段——下游由角色表的边决定，写进任务书反而带偏。任务书发出前由发信方全文追加进所涉项目的 `research_project/<项目名>/dispatch.md`（一节一封：发信角色+时刻+正文），消息里放正文或路径；一切 relay 任务书同此存档，examiner 与评审回查可翻。

## 研究项目文件（research_project/）

旧 `pool/` 与 `registry.json` 废止（v0.4 全盘 md 化）。一项目一文件、生长制、全人读文档。完整口径见 `research_project/README.md`。本节只给摘要。

```
research_project/立项规划.md                            # planner 大课题笔记（自由格式）
research_project/<项目短名>.md                             # 研究项目文件（头四段 + 假设段/设计段/结论段）
research_project/<项目短名>/dispatch.md                        # 任务书存档（每轮追加，一节一封）
research_project/<项目短名>/proposals/{开题申报,中期报告,结题报告}.md
research_project/<项目短名>/packs/<关口>送审包.md                  # qa 送审包
research_project/<项目短名>/gates/<关口>判定.md         # 关口判词
research_project/<项目短名>/gates/<关口>判定-评审<甲|乙|丙>.md  # 独立意见书
```

项目头元数据只 `budget:` 与 `human_gate:`。状态行、轮次、枚举态全部废止——状态隐含在飞轮中：多任务并发在环、单 role 多 session 都是常态，全部真相 = 文件 + git + 台账。

头部四段（initiation 组定稿后闭笔；pi 主笔，librarian 供行锚）：

1. 问题背景 — 成因/机制/现有方法何处失效，只提问不解答。
2. 前沿进展—同方向可借鉴设计 — 正文摘要 + 调查附件（指 `research/frontier-notes.md` 行号）。
3. 目的 — observable 三成分句「在 <数据/环境> 上，用 <指标> 度量，达到 <数值或行为断言>」。
4. 最终验证依据 — 指标+阈值+数据切分写成一句可判真伪的命题。该命题成立即项目完成。

元数据行：`budget:`、`human_gate:`、`conclude:` 段。pi 头四段齐全才可交 examiner，缺格即不出手。写不出 observable 目的的选题不提交。

正文三段，段权=只增不改，revise 打回只许改本阶段段，落笔即在 `<项目短名>/run-log.md` 记一行：

- 假设段假设与理论论据 — speculator 主笔，theorist 补形式化小节。
- 设计段实验设计与结果 — speculator 写设计，runner 填结果节，qa 核验。
- 结论段结论 — review 组：chair 判词指针 + 逐条回查「最终验证依据」回查表。

开题对线中 revise 保持进行中（pi 手里），修后回环继续攻防；fail 只凭化解不了的实心攻击或致命实锤，与轮数无关。新项目才新开 `<项目短名>.md`。

`conclude` 段（ab7d5ae 形态）：在途写 `—`。终态由 chair 在判词落盘时必填成分段：

```markdown
- conclude:
  - 实测: <1-3 条，关键数字+单位+适用范围声明>
  - 意义: <对研究线的一句话>
  - 落点: <papers/<项目短名>/main.pdf 与 gates/结题判定.md 路径>
```

failed 形态改两子条：死因、负证据（各一句+路径）。conclude 空缺 = 归档未完成，chair 这条交活不算 done。

## 角色表（本主题拓扑的唯一事实源）

角色名与 `.onlyne/spec.toml` 的 `[[client]].role` 一一对应；增删 role 同时改这张表、spec 与 `.onlyne/templates/formal/<phase>/<role>/`。

supervisor 代发 `onlyne send --from <role>`、role 侧 `onlyne_send`/`onlyne handoff --to` 的目标名，都查这张表。

`entry` 列标出第一发的注入对象，全表恰好一个 `★`。`relay` 列是任务主下游（spec 的 `relay_required` 单值），与下游列同源。

| role | 职责 | 上游 | 下游 | relay | entry | model |
|---|---|---|---|---|---|---|
| pi | 开题黑盒唯一负责人；头四段作者；对线辩方 | librarian, planner, examiner（攻击/revise）, scribe（成稿回件） | examiner（申报/回应）, librarian（委托检索）, scribe（委托代笔） | examiner | ★ | axonhub/generic-researcher-powerful/max |
| librarian | 公共检索资源（常驻所有阶段外侧） | pi, examiner, theorist, speculator, scribe, chair, planner | pi, examiner, theorist, speculator, scribe, chair, planner | pi | | axonhub/supercheap/low |
| examiner | 敌意评审官：开题对线主，四类攻击，攻不破才放行；可点单请示人工 | pi（申报/回应）, theorist, speculator, librarian, scribe | pi（攻击/revise）, theorist（pass 开工令）, planner（fail 归案）, librarian, scribe | theorist | | axonhub/generic-researcher-powerful/max |
| speculator | 假设/方案/假设段主笔/设计段设计主笔 | theorist, runner（失败回传）, chair, examiner, librarian | theorist（对线）, runner, scribe, examiner（僵局上报）, librarian | runner | | axonhub/generic-researcher-powerful/max |
| theorist | 形式化（Lean/推导，挂假设段形式化段+附件） | examiner, speculator, chair, librarian, scribe | speculator（带陈述出假设）, examiner（复研）, librarian, scribe（委托代笔） | speculator | | axonhub/generic-researcher-powerful/max |
| runner | running_ms=3600000，功耗纪律与训练槽继承旧 bench 细则 | speculator, qa（返工） | qa（交核验）, speculator（失败回传） | qa | | axonhub/supercheap/low |
| qa | 泄漏/确定/预算三约束核验 + 有效读数把关 | runner, scribe, chair（复核委托） | runner（返工）, chair（送审包） | chair | | axonhub/supercheap/medium |
| scribe | 公共代笔位：跨阶段成文（申报书/papers/文稿），为贵档角色省 token | pi, examiner, theorist, speculator, planner, chair, librarian | 各委托方（成稿回件）, qa（合规核）, librarian | chair | | axonhub/supercheap/high |
| chair | 中期检查/结题验收关口主，合议文稿执笔 | qa, scribe, referee, librarian | theorist, speculator, scribe, qa, planner, librarian, referee | planner | | axonhub/generic-researcher-powerful/high |
| referee | 意见书独立，提交前彼此不通；只与 chair intercom 交流 | chair | chair | chair | | axonhub/generic-researcher-powerful/high |
| planner | 立项策划位：全局翻项目文件头、大课题策划（立项规划.md）、派题与归案 | examiner（fail）, chair（accept/reject/stop）, librarian, scribe | pi, librarian, scribe（任务书代笔） | pi | | axonhub/generic-researcher-powerful/medium |

theory 域两员：speculator + theorist，历史名「旧 model 拆二」（git 参照 f36d3de 六环推导位）。`max_sessions`：runner=2，referee=3，librarian=2、scribe=2（公共位接单并发），其余=1。职责列「旧 bench / 旧 writer」为历史细则指向。

边义逐条：

- pi⇄examiner 是开题对线：pi 头四段齐才出手；examiner 逐轮发实心攻击（四类弹药，必带锚），pi 修文或驳锚，同记 对线记录.md。弹药耗尽=pass；化解不了的实心攻击或致命实锤=fail；轮数不设限。
- examiner→theorist 是开题审查 pass 开工令（先形式化头部四段命题）。theorist→speculator 是带陈述出假设与方案。examiner→planner 是 fail 归案。
- speculator⇄theorist 是对线环：假设/论据与形式化互校，自由往返；任一方认定分歧超出本职权限（根前提动摇、可行性存疑）→ 联名上报 examiner 复研，不设轮数门槛。
- speculator→runner 是按设计段实验设计派跑批；runner→speculator 是失败回传与设计疑问。
- speculator→scribe 是假设段/设计段供成稿。speculator→examiner 是对线僵局上报。
- runner→qa 是送核验；qa→runner 是返工（三约束 fail 或无有效读数）。
- qa→chair 是中期检查/结题验收送审包，包落 `research_project/<项目短名>/packs/<关口>送审包.md`；chair→qa 是复核委托。
- scribe 是公共代笔位：委托边=pi/examiner/theorist/speculator/planner/chair（→scribe），成稿回件回到委托方；验收包文稿必经 qa 入 packs/ 再上 chair。referee 不用代笔（意见书独立成文）。relay 仍为 chair。
- chair→referee 是约稿；referee→chair 是独立意见书（逐条回查最终验证依据）。chair→speculator / chair→theorist 是 rectify 整改令：整改经 theory 组，chair 无直令 runner 边。
- chair→planner 是终局归案；planner→pi 是新题发起，任务书必引结题验收 open questions 行。
- librarian 回件面 = 全部委托方（pi、examiner、theorist、speculator、scribe、chair、planner）。

supervisor 不在工作环里：没有任何 role 的上游或下游是 root。supervisor 不注册 [[client]]，admin 面代发除外，签名用持边角色。

例外边（唯一人工请示通道）：examiner 在特定开题任务上可经 pi-intercom 向 `Main` 发请示（题目价值存疑、资源取舍超出判据时），supervisor 向人开 ask 提请批复，批结果回 examiner 后代落 gates/。阻塞等批；此边只服务开题裁量，日常攻防不触发。

supervisor 只做工作区维护，条目为：idle 判定与报告、generate/reload、spec 对表、知识产物 git commit、人机传话。supervisor 不参与工作流转。

三档模型语义：

- `generic-researcher-powerful` 只做纯理论工作，有 agent 能力，不写代码。
- `generic-researcher-weak` 科研能力强，能指导 worker 写代码，必要时自己小写两段。
- `supercheap` 写代码强且便宜，经常思考过度把自己绕晕，不能长时间独立工作。runner 配 low effort（2026-09-09 自 minimal 上调一档，仍为压住它别加戏）。

supervisor 会话档位见根 `.pi/settings.json` 的模型三元组（`generic-researcher-weak` + medium，维护位）。role 档位见 `.onlyne/templates/formal/<phase>/<role>/.pi/settings.json`，改完 `onlyne-server generate --root . --template formal/<phase>/<role> --role <role> --force` 落到该 ws。

## 大循环宏观流（接力闭环，从角色表推导）

接力规则按角色表的 `上游` / `下游` / `relay` 列执行。supervisor 不进工作环，只维护工作区。通用条款五条：

1. planner：翻项目文件与立项规划.md 定向，委托 librarian 摸同行切法，出立项任务书 handoff pi（新题引上一轮结题验收 open questions 或大课题节）；pi 黑盒作业（与 librarian 内部自由分工），头四段+自证断言出手交 examiner；开题对线逐轮 对线记录.md，弹药耗尽 examiner 落 pass 开工令。
2. 关口判定：examiner 判开题审查，qa 备中期检查/结题验收包，chair 合议落 gates/ 判词。落判词者顺手同步项目文件结论段，planner 终局写 conclude。
3. 每个 role：完成后按自己的 `下游` 列 `onlyne handoff` 接力任务书，然后 `onlyne_complete` 交活退出。角色零上行边，回执走 origin 自动通道。
4. role 的产物未齐时 `onlyne_complete outcome:"cancelled"`（或不 complete 等 idle 回收）静默交回，等接力唤醒，不写无依据产物。
5. 委托检索的接收面是 librarian：各 role 的补检索任务写清缺哪段文献、要什么来源；librarian 补完 `research/` 后回委托方。

环路自转：主环 pi→examiner→theorist→speculator→runner→qa→chair→planner→pi；对线环 speculator⇄theorist；执行环 speculator⇄runner（设计段设计与失败回传）、speculator→scribe→qa→chair（验收包成稿过合规核再送审）；整改环 chair→speculator/theorist；复研环 theory 组⇄examiner；合议环 chair⇄referee；委托边 librarian 回全部委托方。人随时可接管任一 session。自激发无熔断，终结靠人 `onlyne control cancel --task <id>` 或会话接管。supervisor（人 + root 会话）只做维护：idle 判定与报告、generate/reload、spec 对表、知识产物 git commit、人机传话。

## 冷启动与第一发

装配完成的瞬间，工作区处于这些事实下：

- `stage=design`，分支 `theme/formal-research`；本行记号在稿件转正后由 supervisor 改 `stage=live`。
- v1 运行时未起：`onlyne-server status` 无 socket，`onlyne-client status --workspace .onlyne/ws/formal/<phase>/<role>` 起不来。通电 = server 一个可见前台 tab 跑 `onlyne-server run --root .`，十一个 role client 各占一个可见 tab 跑 `onlyne-client run --workspace .onlyne/ws/formal/<phase>/<role>`（client 侧只有 `run`，`start`/`stop` 自 1.0.1 取消）。
- `tasks` 表 0 行，`papers/` 空，`research_project/` 只有 README.md（formal 项目目录尚未产生）。
- 飞轮是反应式的：没有入站任务就什么都不会发生。`onlyne-server run` 与十一个 `onlyne-client run` 属于通电，第一发属于开跑。

启动动作二选一：

1. 用户给方向，supervisor 写 `payload/first.md`（含问题、约束、期望），执行
   `onlyne send --server-root . --from planner --to pi --file payload/first.md`。
2. 用户自己在 CLI 投第一发（同上 admin 面命令），supervisor 事后从 ledger 与项目目录接上下文。

supervisor 只负责把第一发投进 `★` role，不参与后续流转；环成形后自转。

本主题的起始 role 是投第一发时 `--to` 的那个名字（见上表 entry 列，★=pi）。第一发落地后环自转：pi 出头四段申报 examiner，后续每轮的推进靠接力任务，启动只需要一发，supervisor 不参与流转。

## 维护与配置（supervisor 用；版本口径 = 追 latest，条款以 `<onlyne 仓>` main 源码复核）

- 配置唯一入口是 `.onlyne/spec.toml`（拓扑/prose/ACL/timeout/intent/agent_package/cert_pin）与 `.onlyne/templates/formal/<phase>/<role>/`（十一套细则+模型三元组）。
- 生效路径：spec 改→reload；模板改→该 role generate --force（`--template formal/<phase>/<role>`）。无 sync/overlay/bootstrap 概念。generate 对两级模板目录的支持未实测，通电首检验证。
- 装役：五件 `onlyne` / `onlyne-server` / `onlyne-client` / `onlyne-gateway` / `onlyne-tui` 装 crates.io latest，插件 `pi install npm:pi-onlyne`（同为 latest）。onlyne 发版频繁，内容基本全是 bug fix，本机长期跑 main 源码构建。策略口径：本树文档与脚本一律不钉版本、不写 tag 名，只设 `protocol=1` 下限。排查工具行为以 `<onlyne 仓>`（本机 onlyne checkout，main）源码与当期 `--help` 为准，role 会话只读。
- server/tui 常驻 = 在 **本主题 worktree 的可见前台 tab** 里跑（`orca terminal create --worktree path:<本树> --command "onlyne-server run --root ."`，tui 同款），关 tab 即停环；禁入任何 agent 后台。client 起 tab 的 worktree 决定会话 spawn 定向（错配案：hub 起 client 继承它方 ORCA_WORKTREE_ID → 会话 cd 进错检出即死）。
- 十一角色 client = 各一个可见前台 tab 跑 `onlyne-client run --workspace .onlyne/ws/formal/<phase>/<role>`（60s ready 计时从起表，长活由 running_ms 续；client 侧无 `start`/`stop`）。
- 崩溃残留处理：`onlyne faults --open-only` 看核心检测（intent exhausted 落此），`onlyne repair inspect|retry|close|fail|ack --task <id>` 处置；投递层之外的残影走下面的恢复纪律。
- 恢复运行纪律（0912 补）：client 重挂后、投新任务前，对 `onlyne sessions` 里每条 working 逐个 `onlyne repair inspect --task <id>`；pane 已死而 lifecycle 仍 working 的残影用 `repair close` 收口（faults 只覆盖投递层，running_ms 判定活在 client 侧，client 重启后旧账无人续判；control cancel 属主判定挡 supervisor，close 走 admin 面可用）。语义按源码校准：`close` 记 cancelled、`fail` 记 failed，两者都经 `retire_task_resource` 向属主 client 发 `Command::Cancel`（`<onlyne 仓>/crates/onlyne-server/src/faults.rs:336-368`），pane 一并回收。伴生检查：`ps` 扫 v0 遗留守护进程（ppid=1 且与 runs/ environment.json 端口引用对上的回收，精确 PID）。
- `onlyne-client` 不写 pid 文件（pid 真相在 server 侧 client_registry）。停某个 client 用 `ps` 按 args+cwd 精确匹配该 ws 的 `onlyne-client run` 进程再定点发信号，禁止 pkill 按名杀。
- 清理孤儿进程前先核对身份：`brew services`、launchd、其他 app 拉起的常驻服务不属于 swarm。杀之前查 launchd label / 父进程 / 端口归属，只回收 `.onlyne/run/` pid 文件与 client 注册表里存在的进程。误杀系统服务比留一个孤儿严重得多。
- hindsight bank 重建、hindsight.json 实例面条款：v1 插件无该子系统，实例 `.pi/` 归装机者自管，暂不提供集中重建步骤（需要时按 pi hindsight 扩展原生方式现场配）。

## 纪律

- 终局 conclude 段与立项规划.md 只归 planner；项目不设状态行（状态隐含在飞轮，全部真相 = 文件 + git + 台账）。
- worker 交付当场盘验：交活前对任务书点名的每个产物路径实盘一遍（存在、非空、可读、行数对得上），数值产物另落 `measured/self_checks.json`；接收方对不上即拒收。产物写入后交付前必须盘上自验一次。
- 过程必落文件（覆盖全角色）：决策、攻防、核验、账目先写文件再上报；`onlyne_complete`/`onlyne handoff` 的 text 放结论+路径清单，消息体量不设限（pi 与 provider 已配无限重试，旧「10KB 禁令」系路由掐流时期的误报，废止）。角色间本就互翻文件，指针即通达。
- 改 `experiment/`、`evaluation/` 前先读项目目录 run-log.md 与 measured/ 里的上一手记录；改动在任务产物里写明。
- 数值只从 measured/ 引，报告只写跑出来的东西。
- 存在 `<项目短名>/DEPRECATED.md` 的项目，其废弃范围内数字一律不作证据，只可按该文件口径引用为已废弃 baseline。
- 带 `DEPRECATED.md` 的历史 run，其 `measured/` 已于 2026-09-09 10:32 移出 `runs/`，落 `.archive/deprecated-mlx-20260909/`（路径对照、使用口径与取回命令见该目录 `README.md`）。
- 旧 `runs/<run-id>/measured/` 路径在盘上不再存在，引用前按对照表解析。
- 失败也交活：跑不动的结论写进项目目录（run-log.md 记节），`onlyne_complete outcome:"failed"` 交失败报告（text 首行 `> hop-failed: <原因>` + 现场路径），让下游有据可依。
- `.onlyne.v0-archive/` 里存着 v0 的命名管道（`channels/loopback/in|out`）：对它做任何递归读取（`grep -r`、`find` 后串 read）仍会阻塞在 FIFO 上把会话卡死，整目录只按单文件路径取旧件。
- v1 运行态（`run/`、`store/`、`keys/`、`logs/`）可正常读，任务与账目走 `onlyne ledger|sessions|watch --server-root .`。
