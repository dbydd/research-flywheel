# formal-research 大循环 — onlyne v1 公共约定（约定骨架）

主题状态：stage=design，分支 `theme/formal-research`。

这份文件放在 server-root（本仓根目录）。pi 沿父目录自动拼上下文，树内每个 session 都读到同一份约定。

两个词先说清：workspace = role，指该角色的「记忆 + 设定 + 历史文件」；session = 该 role 手头的一件工作，做一跳就结束。

一切信息落文件。每个结论都能回溯到 runs/、papers/ 或台账行（`onlyne ledger --server-root .`）。

## 大循环（formal-research）

模仿高校与工业界正式科研全流程组织本工作区。大循环：开题申报 → 可行性审 → 执行（含中期）→ 验收（中期/末期）→ 新开题。五个域按序接力：D1 申报（pi、librarian）→ D2 开题答辩（examiner）→ D3 执行（theorist、runner、scribe、qa）→ D4 验收（chair、referee）→ D5 立项簿（planner）。域内允许内部循环；跨域边以角色表与 `.onlyne/spec.toml` 的 ACL 为准，两处同源。

三个关口：

- G1 开题批准：examiner 出判词，`pass` → 向 theorist 下开工令，`revise` → 打回 pi 补要素，`fail` → 交 planner 归案。
- G2 中期验收：qa 提包（gate 包落 `pool/themes/<slug>/packs/<tid>-G<n>.md`，含中期报告 + 本轮 `measured/` + constraints 核验），chair 与 referee 合议判 `continue` / `rectify` / `stop`。
- G3 末期验收：chair 依终审报告判 `accept`（结题 → planner 开新题）或 `reject`（终止归档）。

判词落 `pool/themes/<slug>/gates/<tid>-G<n>.decision.md`：判词 + 依据 + 签字 + 时刻。referee 独立意见书落 `pool/themes/<slug>/gates/<tid>-G<n>-referee-<1|2|3>.md`。三个关口默认全自动托管。`human_gate` 条款：主题 `main.md` 可列 `human_gate: [G1,G2,G3 子集]`；被点名关口的主责角色先经 pi-intercom 消息 supervisor 的 omp 会话（地址 `Main`），阻塞等 approve；supervisor 向人类提请批复后代落 gates/ 文件。缺省未列 = 全自动。此条款仅在用户明示的主题生效。

止损条款：qa 对 gate 包判「无有效读数」（valid 率 <0.5 或全部 objective=TBD）连续两次 → chair 直接终止主题 + planner 归案，不再进下一轮。

范围锁首检条款：theorist 与 qa 接单必对 `pool/themes/<slug>/main.md` 的「范围锁」一节逐条核对，任务文件缺 `locked_to:` 摘录即拒收。referee 在 G2/G3 意见书必须含「对照 main.md 范围锁逐条核对」一节，越锁 finding 直接 stop 级。

「什么算进步」分主次两条度量：

- 主度量：端到端跑通轮数。`idea.json`→`derivation.md`→`measured/`→`papers/<run-id>/main.pdf`→`gates/…decision.md` 全链条落盘记一轮。阈值 ≥1 轮完整跑通算推进。
- 次度量：关口 revise 收敛率。rectify→accept 在 3 轮内收敛算健康。

算力与时间预算：本机 pi 会话 + 宿主 lean 二进制 + 按需 GPU 跑批，无固定配额；单主题预算写进 `main.md` 的 `budget` 字段。记账按轮在任务产物里做，配置、种子、耗时进 `measured/`。

禁区四条：不伪造 `measured/` 数值；不改评测器语义迎合结论；不碰外部付费数据集与私有模型权重；theorist 只出 spec，不写 `experiment/` 代码。

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

本树全部人读产物（main.md、tasks/、proposals/、packs/、gates/、derivation.md、measured/summary.md、papers/、verdict.md、revisions.md）按上列八条组织。vault 落库细则见下节写作规范。

## 当前工作模式：training live · 功耗约束（用户 2026-09-09 12:2x 解禁）

- 训练执行解禁：runner 可发起 torch 臂跑批。
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
- 功耗纪律与训练槽协议自旧跑批位细则换绑而来（历史参照：commit f36d3de），条款内容不变。
- 待办挂账（supervisor 13:2x）：`runs/normalized-ssd-branch-003/static-check.md` 标题与 `mode: static-only` 头注属冻结期措辞，已过时——下一位触碰 003 产物面的 role（runner/theorist 按其任务书）顺手更新为 live 期口径，supervisor 不改 domain 文书正文。
- 过期护栏继续有效：`runs/*/DEPRECATED.md` 圈定数字不进稿件/verdict；开工先读本节与台账。

## 工作模型（射后不理）

射后不理 = 发出去就不等回复。

每个 session 的生命周期四步：恢复上下文 → 工作 → 激发下游（可选，若干）→ 交活退出。

session 对下游零等待。下游成果经文件与台账呈现，由接力任务唤醒合适的单位继续。

## 目录

- `pool/themes/registry.json`：主题×任务×run 全局账，`planner` 是唯一写主。
- `pool/themes/<slug>/`：主题池，也是唯一队列。一个主题一个目录：`main.md`（六要素）、`tasks/<tid>.md`、`proposals/`、`packs/`、`gates/`，格式见下两节。旧单文件 `pool/ideas.md` 已废弃。
- `runs/<run-id>/`：一轮任务的全部过程件，含 `idea.json` 快照、`derivation.md`、`lean/`、`measured/`、`verdict.md`。
- `research/`：证据。其中 `frontier-notes.md` 是联网检索记录，格式为 URL + 单行结论，追加式。
- `experiment/`：领域代码。`evaluation/`：评测器。`papers/`：成稿，文件名为 `<run-id>.md`。
- `payload/`：注入给起始 role 的任务书落这里（`payload/first.md` 及后续）。
- `.onlyne/ws/formal/<phase>/<role>/`：generate 渲出的角色工作区（路径随 template 子路径 `formal/<phase>/<role>`，与 server name 无关），内含细则 AGENTS.md、`.pi/` 三元组+插件引用、vendor 的 `.onlyne/agent/onlyne-agent-pi`、运行态。`<phase>` 阶段层：initiation={pi,librarian,examiner}、theory=theorist、experiment=runner、writing=scribe、review={chair,referee,qa}、archive=planner。
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
- 工作面口径：草稿、中间件、探针、staged 代码先落在自己 ws 的 `work/`（私有，不入 git）；定稿产物一次性发布到任务书点名的 root 路径，并在 `runs/<run-id>/run-log.md` 记一行本地→发布映射。
- 追加式台账直写 root：tasks/、frontier-notes.md、run-log.md、measured/ 流件；`pool/themes/registry.json` 例外，只由 planner 写。
- peer 实例的 `../../<peer>/work/`（同一 `.onlyne/ws/formal/<phase>/` 下的兄弟 ws；跨阶段用 `../../../<phase>/<peer>/work/`）可只读翻看；交接与审稿判据是任务书与 root 发布物。
- vault 软链在 root `obsidian/` 下，worker 侧用 `../../../../../obsidian/...` 访问，解析目标是同一 vault。

## Obsidian vault 对接与写作规范（全员遵守）

- vault 根：`~/OneDrive/new_document/humanresources`（vault 根，装配机自定）。root `obsidian/` 下四个软链直达 vault 相应位置：`obsidian/论文`→`论文/`（原文 PDF 归档）、`obsidian/reports`→`reports/`（精读报告）、`obsidian/draft`→`draft/`（日常学习与 idea）、`obsidian/templates`→`templates/`（写作规范与报告模板）。读用软链，写同样经软链落 vault，不在本树里复制 vault 文件。
- 写作规范唯一入口：`obsidian/templates/writing-and-report-guide.md`；精读报告骨架用 `obsidian/templates/paper-report.md`。
- 该规范覆盖所有用户可见文字：`derivation.md`、`measured/summary.md`、`papers/<run-id>/main.tex` 与编译出的 `main.pdf`、`verdict.md`、`revisions.md`、vault 落库的精读报告。
- 规范要点：直接陈述、累加式、结论先行；数字带单位与出处（Table/Figure/公式编号或文件路径）；论文事实与「我的分析」分区；流程用 mermaid；数学用 `$$…$$` 独立公式块；YAML frontmatter 可解析；内部链接与 wikilink 可达。
- 该规范与本机全局写作规则同向（禁转折修辞），冲突时以更严格者为准。
- vault 写入白名单：本工作区只准往 vault 放 PDF 论文与 Markdown 叙事性文件。PDF 只进 `obsidian/论文/原文/<短名>.pdf`，含 supplement 则同名 `-supplemental.pdf`；Markdown 精读报告只进 `obsidian/reports/论文精读/<短名>-精读.md`，并在 `obsidian/reports/论文精读/00-索引.md` 登记（登记动作先读后改、增量更新）。
- 其余一切产物留在本树内，不进 vault，落点用 `papers/`、`runs/`、`presentations/` 这些自建目录，涵盖 pptx、图片资产、代码、日志、快照、Workbook。
- `draft/` 是 idea 源之一：librarian 每跳先读 `obsidian/draft/00-索引.md` 再读相关笔记，把值得开正式链路的判断转为主题或任务（`evidence` 指到 `obsidian/draft/<笔记>.md` 具体章节，`origin` 用 `derived` 并注明来源笔记）。
- 半成品纪律沿用 vault 约定：未核对结论进「证据边界与待核对项」，不直接当 claim 写进稿件。
- 人物画像不归本工作区：不读不写 vault 的 `人物/`、`关系图谱/`；reading/writing 任务保持人物档案创建关闭，已有规范人物页可 wikilink 引用，不新建。
- 精读报告自检跑 vault 校验器（只读调用，不往 vault 写脚本）：`env no_proxy='*' NO_PROXY='*' http_proxy= https_proxy= HTTP_PROXY= HTTPS_PROXY= python3 ~/OneDrive/new_document/humanresources/scripts/validate_reading_report.py <report.md>`，按其报错修 frontmatter、围栏、`$$` 定界符、来源锚点与内部链接。

## runs/<run-id>/ 布局

run-id 形态 `<slug>--<tid>--r<round>`，全局唯一，判据来自 `pool/themes/<slug>/tasks/<tid>.md` 的 round 计数。默认结构（`idea.json`/`derivation.md`/`lean/`/`measured/`/`verdict.md`）保持不变，产物落点：

- `idea.json`：本轮开跑时 `tasks/<tid>.md` 的全字段快照，供评测器与聚合脚本消费；机读字段口径与池面一致。
- `analysis.md`：theorist 出的问题层分析（成因/机制/难点/选型考察点四节；难点=现有方法何处失效+结构性原因，只提问不解答；后续 derivation/spec 的输入约束）。
- `derivation.md`：theorist 出的推导（结论先行，每步给依据；逐条难点给应对与贡献主张）。
- `spec.md`：theorist 出的方法实现 spec 与评测器 spec（theorist 不写 `experiment/` 代码，runner 按此落地跑批）。
- `measured/summary.md`：runner 汇总值与 delta（delta = 相对基线的差值），每个 objective 一个实测值，每个 constraint 一个 pass/fail。
- `revisions.md`：scribe 按关口判词编号 finding 修订的记录。
- `run-log.md`：role 自己的台账（追加式）。`root-log.md` 文件名归 supervisor 专用，role 不自开同名台账。
- `verdict.md`：chair 一行 verdict（continue / rectify / stop / accept / reject）+ 编号 finding。关口判词正本落 `pool/themes/<slug>/gates/`，run 内这份是本轮实测判语。
- `papers/<run-id>/`：scribe 成稿目录，位置在 `papers/` 下（`runs/` 下没有这一层），含 `main.tex`（NeurIPS 2024 风格，模板见 `papers/_template/neurips2024/`）+ `refs.bib` + `figs/`，编译出 `main.pdf`。结论先行，每个数字标注来源文件路径，open questions 单节。

## 评测契约

- objectives：每条 `{metric, evaluator, direction, epsilon, baseline}`。`evaluator` 是 `evaluation/` 下评测器的路径与运行命令；`direction` 取 `higher`/`lower`；`epsilon` 是判定阈值（提升幅度）；`baseline` 来源写清（基线配置、种子、数据切分，缺一视为无效基线）。实测值来自 `measured/`，评测 verdict 与实测一致才 pass。
- constraints：`check` 项含数据泄漏检查（训练/评测切分隔离声明）、随机种子固定声明、时间预算声明；每条 `{check, description}`，qa 在 `measured/summary.md` 核验 pass/fail。
- 基线切分：主度量评测面切一份 held-out（比例写进契约）。lean/measured 迭代只在训练面跑；verdict 用冻结候选在 held-out 跑一次定生死，失败禁回炉再优化（防对评测面调参）。理念源：NVlabs/SoL-Pi 双 split 纪律，见 research/frontier-notes.md。
- pass_rule：`all`（本主题默认全过才 accept；探索性任务可在种子里写 `any` 并说明理由）。

tasks/<tid>.md 的 `evaluation` 按本节字段直接填成字面结论行（池内人读面），字段缺项的任务不进池；`runs/<run-id>/idea.json` 里保留同字段 JSON 形态供评测器与聚合脚本消费。

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

## 任务书四段（handoff/send 的 text）

```text
目标：<一句话，做完算什么>
输入：<必须读的文件路径，runs/ 与 research/ 为准>
期望产物：<写到哪里的什么文件，格式要求>
下一跳建议：<完成后该 handoff 谁、干什么；没有就写 无>
```

输入路径必须真实存在。接收方 session 是全新上下文，任务书里没写的路径它找不到。

## 主题池格式（pool/themes/ 多文件制）

替代单文件 `pool/ideas.md`。形态照契约：

```
pool/themes/registry.json          # 主题×任务×run 全局账，run-id=<slug>--<tid>--r<round> 全局唯一（治撞号）
pool/themes/<slug>/main.md         # 总主题六要素：定位/前因与初衷/目的(observable)/范围锁(正向判据+禁止项)/完成判据/止损线；加 budget、human_gate、status(draft|defended|executing|accepted|closed)、conclude 段
pool/themes/<slug>/tasks/<tid>.md  # 分任务：旧 idea 全字段(origin/hypothesis/method/evidence/evaluation/done_when/conclude/note)+locked_to: <main.md 判据行摘录>；状态机 [ ]→[>]→[x]/[!]
pool/themes/<slug>/proposals/<tid>-{kaoti,zhongqi,jieti}.md   # 开题/中期/结题报告
pool/themes/<slug>/packs/<tid>-G<n>.md                      # qa 提包（G2/G3 gate 包）
pool/themes/<slug>/gates/<tid>-G<n>.decision.md              # 判词+依据+签字+时刻
```

`main.md` 六要素是开题报告的骨架：pi 六要素齐全才可交 examiner，缺格即不出手。`status` 迁移 `draft → defended → executing → accepted → closed`，迁移动作由关口判词驱动，账由 planner 记。

`tasks/<tid>.md` 一条一个文件。池子=人读知识面。合格判据一句话：没参与过该 run 的人，凭这一文件就能看懂它问什么、怎么答的、答案是什么、可信度落点。过程流水、机读清单、核对记录全在 `runs/<run-id>/`（idea.json、run-log.md、verdict.md），池内不复制。

```markdown
## [ ] <tid>
- origin: user_seed|derived | parent_run: <run-id 或 —> | question: <一句话>
- hypothesis: <可检验的假设>
- method: <做法要点，≤3 句>
- evidence: 一条一行、至多 6 条，每条「路径 — 它在这里被用来做什么」。文献引用写 `research/frontier-notes.md:<行号>（一句话主题）`，裸 URL 不入池。
- evaluation: 字面结论多行——每 objective 一行「O<i> <指标>：经 <评测器与运行命令>；不低于/不超过 <阈值(带单位)> 判 pass；baseline：<基线配置、种子、数据切分>」，每约束一行「约束 <check>：<一句话>」，末行「pass_rule=all|any」。
- done_when: <完成的 observable 判据>
- locked_to: <main.md 范围锁判据行摘录>
- conclude: 入池与在途写 `—`。终态分段见下。
- note: 只记状态迁移与知识点增量，一行一条、后来的写上面、每条 ≤80 字。
```

状态机：`[ ]` queued → `[>]` running（取单时改）→ `[x]` keep / `[!]` failed（归档时改）。revise 打回保持 `[>]`（任务在 pi 手里），修订后重交 examiner，不回 `[ ]`；新任务才以 `[ ]` 入册。取单门在 planner 与 theorist。机读口径存于固化的 `runs/<run-id>/idea.json`；池面保持纯人读。

四条进池硬门（entry 门 = pi 写任务时逐条自查）：evidence 为空、objectives 为空、done_when 为空、headroom 预筛不过，任一条命中即不入池。headroom 预筛：写进池子前沿上单行判据——哪个 `measured/` 数字或 frontier-notes 行暴露了缺口、余量多大。指得出数字才占下游 rollout；指不出的候选不写进池，负证据照记进 frontier-notes 一行，下轮检索先翻旧账。

`conclude` 段（ab7d5ae 形态，换绑到多文件制；历史参照 commit ab7d5ae）：入池与在途写 `—`。终态由 chair 在判词落盘时必填成分段：

```markdown
- conclude:
  - 实测: <1-3 条，关键数字+单位+适用范围声明>
  - 意义: <对研究线的一句话>
  - 落点: <papers/<run-id>/main.pdf 与 runs/<run-id>/verdict.md 路径>
```

failed 形态改两子条：死因、负证据（各一句+路径）。conclude 空缺 = 归档未完成，chair 这条交活不算 done。`main.md` 的 conclude 段汇总本主题各 task 的终态，一句一段。

## 角色表（本主题拓扑的唯一事实源）

角色名与 `.onlyne/spec.toml` 的 `[[client]].role` 一一对应；增删 role 同时改这张表、spec 与 `.onlyne/templates/formal/<phase>/<role>/`。

supervisor 代发 `onlyne send --from <role>`、role 侧 `onlyne_send`/`onlyne handoff --to` 的目标名，都查这张表。

`entry` 列标出第一发的注入对象，全表恰好一个 `★`。`relay` 列是任务主下游（spec 的 `relay_required` 单值），与下游列同源。

| role | 职责 | 上游 | 下游 | relay | entry | model |
|---|---|---|---|---|---|---|
| pi | 开题报告六要素作者 | librarian, planner, examiner（revise 打回） | examiner（申报）, librarian（委托检索） | examiner | ★ | axonhub/generic-researcher-powerful/max |
| librarian | 检索与 novelty | pi, theorist, examiner, chair, scribe, planner | pi, theorist, examiner, chair, scribe, planner（检索回件） | pi | | axonhub/supercheap/low |
| examiner | G1 关口主 | pi, librarian, theorist（前提动摇回请） | theorist（pass 开工令）, pi（revise 打回）, planner（fail 归案）, librarian（补检索） | theorist | | axonhub/generic-researcher-powerful/high |
| theorist | 推导+Lean+spec，不写 experiment/ 代码 | examiner, chair（整改经出修订 spec）, librarian, runner（失败回传） | runner, scribe, librarian, examiner（可行性复研） | runner | | axonhub/generic-researcher-powerful/max |
| runner | running_ms=3600000，功耗纪律与训练槽继承旧 bench 细则 | theorist, qa（返工） | qa（送包）, theorist（失败回传）, scribe | qa | | axonhub/supercheap/low |
| qa | 泄漏/确定/预算三约束核验 + 有效读数把关 | runner, scribe, chair（复核委托） | runner（返工）, chair（提包） | chair | | axonhub/supercheap/medium |
| scribe | 旧 writer 细则 | theorist, runner, chair, librarian（检索回件） | chair, librarian, qa（成稿入合规核） | chair | | axonhub/supercheap/high |
| chair | G2/G3 关口主，合议文稿执笔 | qa, scribe, referee, librarian | theorist, scribe, qa, planner, librarian, referee | planner | | axonhub/generic-researcher-powerful/high |
| referee | 意见书独立，提交前彼此不通；只与 chair intercom 交流 | chair | chair | chair | | axonhub/generic-researcher-powerful/high |
| planner | registry.json 唯一维护者；新题发起 | examiner（fail）, chair（accept/reject/stop）, librarian（检索回件） | pi, librarian | pi | | axonhub/generic-researcher-powerful/medium |

`max_sessions` 与契约表同值：runner=2，referee=3，其余=1。职责列抄契约备注原文；「旧 bench / 旧 writer」为历史细则指向（git 参照 f36d3de 六环跑批位与成稿位）。

边义逐条：

- pi→examiner 是开题申报：六要素齐才出手。examiner→pi 是 revise 打回：缺格点名，pi 补后重走 G1。
- pi→librarian 与 examiner→librarian 是检索委托；librarian 把结果回给委托方（含 librarian→scribe、librarian→planner 检索回件）。
- examiner→theorist 是 G1 pass 开工令；theorist→examiner 是前提动摇时回请可行性复研。examiner→planner 是 fail 归案（registry 记一行，主题转 closed）。
- theorist→runner 是按 spec 派跑批；runner→theorist 是失败回传与 spec 疑问。theorist→scribe 是 spec 与 derivation 供成稿；theorist→librarian 是证据缺口委托。
- runner→qa 是送包核验；qa→runner 是返工（constraints fail 或无有效读数）；runner→scribe 是实测就绪可下笔。
- qa→chair 是 G2/G3 提包，包文落 `pool/themes/<slug>/packs/<tid>-G<n>.md`；chair→qa 是复核委托（重开一份 gate 包核）。
- scribe→qa 是验收包文稿入合规核（必须经 qa 入 packs/ 再上 chair）；scribe→chair 是开题申报文稿直发（亦可）；scribe→librarian 是稿件缺证据的补检索委托。relay 仍为 chair。
- chair→referee 是约稿；referee→chair 是独立意见书。chair→theorist 是 rectify 整改令：整改一律经 theorist 出修订 spec 再落 runner/scribe，chair 无直令 runner 边。
- chair→planner 是终局归案（accept 结题 / reject·stop 终止）；planner→pi 是新题发起，任务书必引 G3 open questions 行。

supervisor 不在工作环里：没有任何 role 的上游或下游是 root。supervisor 不注册 [[client]]，admin 面代发除外，签名用持边角色。

supervisor 只做工作区维护，条目为：idle 判定与报告、generate/reload、spec 对表、知识产物 git commit、人机传话。supervisor 不参与工作流转。

三档模型语义：

- `generic-researcher-powerful` 只做纯理论工作，有 agent 能力，不写代码。
- `generic-researcher-weak` 科研能力强，能指导 worker 写代码，必要时自己小写两段。
- `supercheap` 写代码强且便宜，经常思考过度把自己绕晕，不能长时间独立工作。runner 配 low effort（2026-09-09 自 minimal 上调一档，仍为压住它别加戏）。

supervisor 会话档位见根 `.pi/settings.json` 的模型三元组（`generic-researcher-weak` + medium，维护位）。role 档位见 `.onlyne/templates/formal/<phase>/<role>/.pi/settings.json`，改完 `onlyne-server generate --root . --template formal/<phase>/<role> --role <role> --force` 落到该 ws。

## 大循环宏观流（接力闭环，从角色表推导）

接力规则按角色表的 `上游` / `下游` / `relay` 列执行。supervisor 不进工作环，只维护工作区。通用条款五条：

1. planner：从 registry 取一条待开题主题，handoff pi 立题（任务书引上一轮 G3 open questions 行）；pi 写 `pool/themes/<slug>/main.md` 与 `tasks/<tid>.md`，过四条 entry 硬门后 handoff examiner。
2. 关口判定：examiner 判 G1，qa 备 G2/G3 包，chair 合议落 gates/ 判词。判词驱动 status 与 task 状态记号迁移，planner 据此改 registry。
3. 每个 role：完成后按自己的 `下游` 列 `onlyne handoff` 接力任务书，然后 `onlyne_complete` 交活退出。角色零上行边，回执走 origin 自动通道。
4. role 的产物未齐时 `onlyne_complete outcome:"cancelled"`（或不 complete 等 idle 回收）静默交回，等接力唤醒，不写无依据产物。
5. 委托检索的接收面是 librarian：各 role 的补检索任务写清缺哪段文献、要什么来源；librarian 补完 `research/` 后回委托方。

环路在十个 role 之间自转：主环 pi→examiner→theorist→runner→qa→chair→planner→pi；执行环 theorist⇄runner（spec、失败回传与返工）、theorist→scribe→qa→chair（验收包成稿过合规核再送审）；整改环 chair→theorist→runner/scribe；复研环 theorist⇄examiner；合议环 chair⇄referee；委托边 librarian⇄{pi,theorist,examiner,chair,scribe,planner}。人随时可接管任一 session。自激发无熔断，终结靠人 `onlyne control cancel --task <id>` 或会话接管。supervisor（人 + root 会话）只做维护：idle 判定与报告、generate/reload、spec 对表、知识产物 git commit、人机传话。

## 冷启动与第一发

装配完成的瞬间，工作区处于这些事实下：

- `stage=design`，分支 `theme/formal-research`；本行记号在稿件转正后由 supervisor 改 `stage=live`。
- v1 运行时未起：`onlyne-server status` 无 socket，`onlyne-client status --workspace .onlyne/ws/formal/<phase>/<role>` 起不来。通电 = server 一个可见前台 tab 跑 `onlyne-server run --root .`，十个 role client 各占一个可见 tab 跑 `onlyne-client run --workspace .onlyne/ws/formal/<phase>/<role>`（client 侧只有 `run`，`start`/`stop` 自 1.0.1 取消）。
- `tasks` 表 0 行，`runs/` 空，`papers/` 空，`pool/themes/registry.json` 为 `{"themes":[]}`。
- 飞轮是反应式的：没有入站任务就什么都不会发生。`onlyne-server run` 与十个 `onlyne-client run` 属于通电，第一发属于开跑。

启动动作二选一：

1. 用户给方向，supervisor 写 `payload/first.md`（含问题、约束、期望），执行
   `onlyne send --server-root . --from planner --to pi --file payload/first.md`。
2. 用户自己在 CLI 投第一发（同上 admin 面命令），supervisor 事后从 ledger 与 `runs/` 接上下文。

supervisor 只负责把第一发投进 `★` role，不参与后续流转；环成形后自转。

本主题的起始 role 是投第一发时 `--to` 的那个名字（见上表 entry 列，★=pi）。第一发落地后环自转：pi 出六要素申报 examiner，后续每轮的推进靠接力任务，启动只需要一发，supervisor 不参与流转。

## 维护与配置（supervisor 用；版本口径 = 追 latest，条款以 `<onlyne 仓>` main 源码复核）

- 配置唯一入口是 `.onlyne/spec.toml`（拓扑/prose/ACL/timeout/intent/agent_package/cert_pin）与 `.onlyne/templates/formal/<phase>/<role>/`（十套细则+模型三元组）。
- 生效路径：spec 改→reload；模板改→该 role generate --force（`--template formal/<phase>/<role>`）。无 sync/overlay/bootstrap 概念。generate 对两级模板目录的支持未实测，通电首检验证。
- 装役：五件 `onlyne` / `onlyne-server` / `onlyne-client` / `onlyne-gateway` / `onlyne-tui` 装 crates.io latest，插件 `pi install npm:pi-onlyne`（同为 latest）。onlyne 发版频繁，内容基本全是 bug fix，本机长期跑 main 源码构建。策略口径：本树文档与脚本一律不钉版本、不写 tag 名，只设 `protocol=1` 下限。排查工具行为以 `<onlyne 仓>`（本机 onlyne checkout，main）源码与当期 `--help` 为准，role 会话只读。
- server/tui 常驻 = 在 **本主题 worktree 的可见前台 tab** 里跑（`orca terminal create --worktree path:<本树> --command "onlyne-server run --root ."`，tui 同款），关 tab 即停环；禁入任何 agent 后台。client 起 tab 的 worktree 决定会话 spawn 定向（错配案：hub 起 client 继承它方 ORCA_WORKTREE_ID → 会话 cd 进错检出即死）。
- 十角色 client = 各一个可见前台 tab 跑 `onlyne-client run --workspace .onlyne/ws/formal/<phase>/<role>`（60s ready 计时从起表，长活由 running_ms 续；client 侧无 `start`/`stop`）。
- 崩溃残留处理：`onlyne faults --open-only` 看核心检测（intent exhausted 落此），`onlyne repair inspect|retry|close|fail|ack --task <id>` 处置；投递层之外的残影走下面的恢复纪律。
- 恢复运行纪律（0912 补）：client 重挂后、投新任务前，对 `onlyne sessions` 里每条 working 逐个 `onlyne repair inspect --task <id>`；pane 已死而 lifecycle 仍 working 的残影用 `repair close` 收口（faults 只覆盖投递层，running_ms 判定活在 client 侧，client 重启后旧账无人续判；control cancel 属主判定挡 supervisor，close 走 admin 面可用）。语义按源码校准：`close` 记 cancelled、`fail` 记 failed，两者都经 `retire_task_resource` 向属主 client 发 `Command::Cancel`（`<onlyne 仓>/crates/onlyne-server/src/faults.rs:336-368`），pane 一并回收。伴生检查：`ps` 扫 v0 遗留守护进程（ppid=1 且与 runs/ environment.json 端口引用对上的回收，精确 PID）。
- `onlyne-client` 不写 pid 文件（pid 真相在 server 侧 client_registry）。停某个 client 用 `ps` 按 args+cwd 精确匹配该 ws 的 `onlyne-client run` 进程再定点发信号，禁止 pkill 按名杀。
- 清理孤儿进程前先核对身份：`brew services`、launchd、其他 app 拉起的常驻服务不属于 swarm。杀之前查 launchd label / 父进程 / 端口归属，只回收 `.onlyne/run/` pid 文件与 client 注册表里存在的进程。误杀系统服务比留一个孤儿严重得多。
- hindsight bank 重建、hindsight.json 实例面条款：v1 插件无该子系统，实例 `.pi/` 归装机者自管，暂不提供集中重建步骤（需要时按 pi hindsight 扩展原生方式现场配）。

## 纪律

- 范围锁优先：theorist 与 qa 接单必对 `main.md` 范围锁逐条首检，任务缺 `locked_to:` 摘录即拒收；越锁主张在关口判词里点名。
- 有效读数止损：qa 判「无有效读数」（valid 率 <0.5 或全部 objective=TBD）连续两次即上报 chair，chair 终止主题 + planner 归案，不再进下一轮。
- `pool/themes/registry.json` 唯一写主是 planner；其他 role 读账不写账，需改账走 handoff planner。
- worker 交付当场盘验：交活前对任务书点名的每个产物路径实盘一遍（存在、非空、可读、行数对得上），数值产物另落 `measured/self_checks.json`；接收方对不上即拒收。产物写入后交付前必须盘上自验一次。
- 上报与载荷纪律（覆盖全角色）：`onlyne_complete`/`onlyne handoff` 的 text 一行放全（结论+路径清单）；大表、长报告、数字明细一律落盘指路径，禁在单条会话消息里携带 10KB 以上载荷（路由掐流教训）。
- 改 `experiment/`、`evaluation/` 前读 runs/ 里上一轮记录；改动在任务产物里写明。
- 数值只从 measured/ 引，报告只写跑出来的东西。
- 存在 `runs/<run-id>/DEPRECATED.md` 的 run，其废弃范围内数字一律不作证据，只可按该文件口径引用为已废弃 baseline。
- 落点口径：新 run 的实测产物仍落 `runs/<run-id>/measured/`。
- 带 `DEPRECATED.md` 的历史 run，其 `measured/` 已于 2026-09-09 10:32 移出 `runs/`，落 `.archive/deprecated-mlx-20260909/`（路径对照、使用口径与取回命令见该目录 `README.md`）。
- 旧 `runs/<run-id>/measured/` 路径在盘上不再存在，引用前按对照表解析。
- 失败也交活：跑不动的结论写进 runs/，`onlyne_complete outcome:"failed"` 交失败报告（text 首行 `> hop-failed: <原因>` + 现场路径），让下游有据可依。
- `.onlyne.v0-archive/` 里存着 v0 的命名管道（`channels/loopback/in|out`）：对它做任何递归读取（`grep -r`、`find` 后串 read）仍会阻塞在 FIFO 上把会话卡死，整目录只按单文件路径取旧件。
- v1 运行态（`run/`、`store/`、`keys/`、`logs/`）可正常读，任务与账目走 `onlyne ledger|sessions|watch --server-root .`。
