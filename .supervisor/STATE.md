# supervisor 运维手帐

这一份是 supervisor 的私有手帐（集群侧）。固定口径在 `.supervisor/AGENTS.md` 与 `README.md`；环上内容族的进度与 todo 在仓根 `STATE.md`。

## 集群现状（1.4.0 发布后，**现场在隔壁会话手里**）

TUI 板 pid 7912 已收（18:19）。server 现由我 `onlyne server start --root .` 起（pid 11907，ppid 1）；scriber + librarian 两 client 由**隔壁主题的会话**在 10:19:31Z 拉起（其 broker pid 13497，父 omp pid 8119、cwd `orca/workspaces/research-flywheel/theme-formal-research`，任务书里的 orca worktree 标 `theme-gemini`）。**dev 判「保护别人现场、侧向只读做得对，先保持现场不动」**，故两 client 我不碰、不接手压测。要复压或读帧，先确认这两 client 是否仍在别人手里。

- 真身在 `/Users/dbydd/Library/CloudStorage/OneDrive-个人/new_document/Alexandria`；`/Users/dbydd/OneDrive` 是同一份的 firmlink（同 inode，非副本）。它是 git worktree：gitdir 在 `~/vibe-agent-working-dir/research-flywheel/.git/worktrees/…`，**对象库不在同步盘上**。HEAD 到 `f01e8fba`（内容层）+ `f229291`（文档面与手帐），已 push，ahead 0。
- 映像：发布版 `onlyne`、server、client、gateway、tui、testkit 1.4.0 已从 crates.io 重装；npm `pi-onlyne` 1.2.0 已安装。此前 dev 本地构建读数保留在下方验收记录。
- 六 client 的 tab↔role 实测映射：scriber `term_b54f9994`、librarian `term_1efa68d1`、astrologer `term_09098506`、master `term_f41cf013`、socrates `term_93262969`、scraper `term_ab0c128d`。
- 重启法：`ps` 按 `--workspace` 认精确 pid 后 SIGTERM（别按名字杀，dev 在同机跑 e2e 会让 `ps` 计数飘），再往同一 tab `orca terminal send` 原启动行；server 用 `onlyne server stop/start --root .`。
- 档案：工作记录 `/tmp/onlyne-bug-141/round4/swap-acceptance.md`（457 行，复验一~九 + 复压七~十二 + 两观察定稿全在）；库备份 `round7-pre/`、`round12/state.db.pre`、旧 schema-3 `swap-backup/schema3/`；脚本 `/tmp/onlyne-bug-141/round7/`。`/tmp/omp-probe-*` 已清 0。

## 解牌与适配结果

crates.io 真实 publish 已完成。十九个 crate 首次上传成功，Git tag `v1.4.0` 已在远端，npm `pi-onlyne` 为 1.2.0。本机已按发布版重装六个 crate 并重签 binary；role 与 supervisor 手册已用安装 binary 重导，导出结果 unchanged。

- **包名事实**：crates.io = `onlyne-cli`（装出 `onlyne` 二进制）+ `onlyne-server` / `onlyne-client` / `onlyne-gateway` / `onlyne-tui` / `onlyne-testkit` + 其余 workspace crates，统一 **1.4.0**；npm = `pi-onlyne` **1.2.0**。
- **本机核验**：`onlyne version` 返回 `onlyne-cli` 1.4.0、protocol 1 和 `~/.cargo/bin` sibling 路径；`cargo install --list` 列出六个 1.4.0 package。`onlyne skill export --set role --set supervisor --force` 返回 3 个 `unchanged`、0 个 `written`。

**我这边三条核验（含两处自我撤回）**：`~/.cargo/registry/cache` 里 19 个 `onlyne-*-1.4.0.crate` 齐。`~/.cargo/bin` 实有七个 onlyne 系文件：五进制 mtime **18:18:57**（隔壁会话照 dev 命令又跑一次 `cargo install`），`onlyne-agent-fake`/`onlyne-gateway-fake` 是 18:14:20、出自 `onlyne-testkit` 的 `src/bin`。**我先前报「装出 `onlyne` 与 `onlyne-cli` 两个入口」作废** —— 该文件不存在，我把 `onlyne version` 的 JSON 键名当成文件名，发布 crate `onlyne-cli-1.4.0` 的 `[[bin]]` 只有 `name = "onlyne"`，dev 的 (iv) 对。`onlyne-role-payload-v2/` 是导出器认的第三个目标（报 unchanged），「旧残留可清」那条同样作废。

## 复压十三（dev 要的形状已由隔壁会话打出；我只侧向采样）

数据源 = 那一发的活体现场。脚本 `/tmp/onlyne-bug-141/round13/sampler2.py`（只读、14 拍 × 5 秒、有界；首版 `sampler.py` 两处自误：`--task` 要全 uuid、client.db 无 `outcome` 列而是 `delivery_state`/`recovery_substate`）。四判据实测：

- 投影 `exited` ✓ 六条会话全 `public_lifecycle=exited`。
- 两侧 seq 差 0：6 条里 **5 条成立**（`6d983d83` 镜像 seq3/gen2 ｜ 本机 seq3/gen2；`26fc6d60` 4/1 ｜ 4/1）；`d6ba5618` **镜像 5 ｜ 本机 4，差 1，方向是镜像超前** —— 该单收在 `control cancel`（10:26:31 acked、`outcome=cancelled`），client 已死追不上。与复压七「判定不推水位」不同族，已交 dev 判是否设计内。
- `ghosts` 无新行 ✓ `ghost_sweeps` 全程 2 行，`max(swept_at)=2026-09-23T18:19:36Z`（昨天）。
- **账落 `acked` ✗**：六条 `task` 行全收 `rejected` + `reason=session_dead`，同 task 的 `completion` 却 `acked`（`6d983d83` 10:22:31 与 10:23:04 两发，`out_head`="release smoke parent done; handoff child dispatched"；子单 `79a88c4f` 10:23:21；`e1989855` 10:26:06）。每条拒行带 `requeued=1`、`attempt=0`，**账上无第二条行**。`f44c890e` 停在 `queued`（`requeued=1`）＝观察 B 同族，记档不改。

**两条缺陷候选已报他**：(i) 拒了还能完成——`task:rejected` 与 `completion:acked` 并存，只读 task 行会判「没做」，实际产物已落；(ii) `session_dead` 真因是 **orca 单实例墙**：`e1989855` 的 reason 原文 `runtime command failed: orca terminal create --worktree e261f848::…/theme-gemini --title onlyne:e1989855… --command cd '…/Alexandria/.onlyne/ws/librarian' && env … 'pi' --session-id … --session-dir .pi/sessions; exit --json (status 3): [single-instance] Another Orca instance i…`。第一发距 client 启动 6 秒（可算竞态），其后五发在 38 秒～4 分 40 秒之间 ⇒ **排除启动竞态解释**。对本机（人常开 Orca）这是硬约束：orca 后端在「Orca 已运行」下只能走 attach/relay，`terminal create` 必失败。dev 已并行派四个只读调查（账本契约、cancel 后镜像 seq+1、Orca 单实例宿主模型、`onlyne-cli` 别名），结论按 设计/缺陷/歧义 逐条回。

## OneDrive 回滚事件（2026-09-24 17:3x）

本文件 15:30–15:45 的两次追加（复压十一/十二记分、「档案职责」整节）被 OneDrive 换成 13:47 的云版本，mtime 回落、内容丢失。根因是**手帐一直是 git 未跟踪文件**（`?? STATE.md`、`?? .supervisor/STATE.md`），零保护。丢失内容已从本会话逐字复原并在本节记录；此后**手帐必须进 git**（本地提交即时，push 按人判语）。`/tmp` 下的工作记录不受影响（不在同步盘上）——这反过来印证 dev 把它搬进仓（`fd23576`）是对的。

## 验收记分

- 复压七（`42fc685`+`b31b5b3`）：recycle / cancel / done-then-recycle 三形状五条全中；「判定不推水位」有硬证。
- 复压八（`3704b00`）：未通过 —— 修在本机写，镜像停在旧版本；普查给出 10/10 「本机 seq = 镜像 seq + 1」。
- 复压九（`51c23d9`）：普通完成 + recycle 两形全中 —— `agent` running→gone、**两侧 seq 差归 0**、水位与产物照旧。**operator 面与镜像一致性结案，双方无保留意见。**
- 复压十（TUI 12:27 映像）：`--state all` 出 `reason=`、无旗标帧与 `--state active` 逐字节一致；年龄锚定生效——外部断言的正确形式是**去掉页脚那行后逐字节相同**（两次 `--once` 是两个快照，页脚读各自 `refreshed_at`），dev 认他原先那条「同命令两次逐字节相同」是错要求。
- 复压十一（清扫 vs 完成回执 `083fc2b`）定档：**dev 判 1+3 合并**。该合取在 Alexandria 拓扑**不可复现**——pi+orca 在结算后没有第三个心跳源。证据三块：合取之「前」= 修复前 `acp-payload-v2` 的真进程活体；合取之「后」= 服务端用例 `the_sweep_leaves_a_queued_completion_receipt_alone` 确定性钉住（主证据）；我方两发补两件活体事实，复验六的 `1003→1004` 继续作为「谓词成立时清扫仍开火」的独立证据。**我方一处措辞已自我更正**：先前写「活体证据缺失」，准确说法是「缺的是修复后的同一形状」。换 acp 后端复述一遍，dev 判不值得，同一事实他已写进 `docs/operations.md` 清扫节。
- 复压十二（`39408cb` 回执过期预算）：观察 A/B **定稿**——默认 `requeue_ttl_secs=0` 时无 client 的回执**常驻 `queued`、永不自动结掉**（`4b84617` 起的语义），20 秒预算下 20 行按预算过期为 `reason=requeue_ttl`。实验残留：那 20 行**停在 `expired` 不复原**（还原会抹掉承载①②读数的三条任务行），措辞已给 dev 且他认。
- dev 侧 e2e：16/19 → 修两条用例自身不确定性 → 19/19；1100 通过 / 0 失败、69 目标、clippy 与 fmt 清。
- 观察 B：`queued` 的 completion/control 回执 = 收件 role 无 client 时的正常排队，记档不改。停服后只读库实数：completion 11 queued + 1 acked、control 6 queued + 14 acked、`task` 12 acked + 10 rejected；寄给 `_supervisor` 的回执被拒 0 行。

## 档案职责（三层落点）

- `/tmp/onlyne-bug-141/round4/swap-acceptance.md` 是这一轮**所有活体证据的唯一来源**：dev CHANGELOG 引的读数与措辞都出自这里、未另立一套。规矩固定为「他转读数 → 我入档」，两份档案不分叉。**别当临时物清掉。**
- **三层落点**：我的工作记录（`/tmp` 那份，继续往后写）→ dev 仓快照 `/Users/dbydd/Documents/progs/onlyne/docs/live-evidence-1.4.0.md`（`fd23576`，正文逐字保留、他加出处段；只在我扩展之后刷新，一次一次）→ 他的 CHANGELOG 只引不另立。CHANGELOG 1.4.0 段头加了指针，理由是他那句：让证据比采集它的机器活得久。
- **打包一问已结**：`packaging/README.md:53-54` 的发布物是**五个二进制 + `LICENSE` + CLI 自产 shell 补全**，`docs/` 不进包 ⇒ 按我的条件式答复，**打包面一行未改**。证据只活在仓里与 git 历史，维护者按 CHANGELOG 段头指针找得到。任务号笔误只在聊天里，仓里已是 `88d0f5cd`。
- dev 另两笔已入档：`4f4826e`（历史对照 + 等效判据进 CHANGELOG，写明该支需要能重跑已结算任务的后端、指向 e2e 那条 5/5 单槽覆盖）、`bc0a5df`（`repair retry` 的 help 补完，转换表不动：终态无回边就是账本的意义，「重跑已完成的工作等于发新任务」）。
- **待执行的一轮压测**：完成 + handoff + 杀 client 形状，期望账落 `acked`、投影 `exited`、两侧 seq 差 0、ghosts 无新行；读数写入本手帐并报人。

## 文档口径迁移（注入面与手帐面）

人判「把手帐写进 context 文件是反模式」：注入链每轮整份进 prompt，一写就把前缀缓存打掉。全仓已按此拆开。

- 正本口径：`.onlyne/AGENTS.md` §注入面与手帐面、§我的记事就两段。判据一句：这段文字会不会因某次交付而变——会，它属于 `STATE.md`。
- 注入面（保留固定物）：仓根 `AGENTS.md`（目标、判据、索引表）、`.onlyne/AGENTS.md`（约定）、六份 ws `AGENTS.md`（岗位口径 + 三行指针）、`.omp/AGENTS.md`（指针本）。
- 手帐面：仓根 `STATE.md`、`.supervisor/STATE.md`（本件）、六份 ws `STATE.md`、六份 `.onlyne/templates/<role>/STATE.md`（两行骨架，`generate` 走 `load_tree` 会整棵复制）。**十一份手帐现全部进 git 跟踪**（OneDrive 回滚事件后的处置）。
- 同步改到的文档：`README.md`（15 处）、`STRUCTURE.md`（8 处）、`.agents/skills/wiki-format/SKILL.md`（5 处）、`.agents/skills/scientist-profiles/SKILL.md`（2 处）、`.onlyne/spec.toml`（scraper prose + 一条注释，已 `reload`，`spec_diff` 回 no changes）。
- dev 导出的两件已用发布版重导：`onlyne skill export --set role --set supervisor --force` 回 unchanged（内容本就是 1.4.0 版）。
- 我的 omp 笔记本已降成固定指针本，现场状态一律写本文件。
- **本文件现在有两个写者**：同机另一会话（theme-formal-research / theme-gemini）在 §解牌与适配结果 插过整节。它的编辑已保留、我的编辑走定点 hunk，互不覆盖。要并写就先分工，别整份 `write`。

## 挂账

1. **解牌三件已结**：发布版在位（五进制 18:18:57）；手册重导回 unchanged；形状读数已交（见 §复压十三）。**更正我先前一句**：`README.md`/`.onlyne/AGENTS.md`/`.supervisor/AGENTS.md` 的 1.4.0 口径当时是**隔壁会话改的未提交工作树内容**（HEAD `ddf019a` 里还是「各追自己渠道的最新」），不是「已提交零改动」；现随本次布局变更一并提交。
2. 本仓已推：`f229291`（文档面与手帐进跟踪）、`f01e8fba`（内容层 177 文件）、`513ecf08`（复压十三读数），ahead 0。工作树只剩 `.obsidian/`、`.omp/PLAN.md`、`.agents/skills/onlyne-role-payload-v2/`（第三条现为导出器的合法目标，留跟踪与否待人判）。
3. **等 dev 回两问**：(a) 请他重判 (i) —— requeue 是否该排掉「session 已因完成而退出」这条触发；(b) `scriber/client.db` 损坏的定性与他是否要在 operations 写「集群 root 别放同步盘」。在他回之前我不修库。
4. **现场归属待处置**：scriber + librarian 两 client 在隔壁会话手里；`f44c890e` 停在 `queued`（`requeued=1`）；我起的 server pid 11907 归我收。
5. 待人拍板的设计项三条：无 client 的 `queued` 回执要不要就地结掉（`39408cb` 已给出可选预算那半）、claim 语义收成哪一种、操作者能否强制重投已结算任务（dev 依据：现在没有任何入口能造出第二份 verdict，若要即属新增有意能力）。done 判定维持不加第二道闸、只加证据。
6. role 侧 recall-failed 未治；知识层 `.obsidian/` 勿动且**不进提交**；隔壁 lora2/lt formal 集群勿混。

## 口径提醒

- 注入面（`AGENTS.md` 链）只放固定物，进度/todo/过程一律写 `STATE.md`；判据：这段文字会不会因某次交付而变。
- 同步盘上的手帐**必须 git 跟踪**：OneDrive 会用云版本静默换掉本地文件（mtime 一起回退），未跟踪即无痕丢失。
- `onlyne send` 无 `--reason`；`--state` 取值只有 `active`/`all`。
- 脚本一律先 `write` 成文件 + `python3 -m py_compile` 再跑；有界循环写上界，禁 `while True`；`orca terminal read` 的缓冲会留着同一 tab 前一个实例的行，别拿它判 role。

## 取证层（scriber 库损坏，dev 定的处置：只查副本、原库零写入）

副本与 sha256 manifest：`~/.local/share/onlyne-forensics/round13v2-20260924T105536Z/`；脚本 `/tmp/onlyne-bug-141/round13/scene_copy2.py`（首版 `scene_copy.py` 有 bug：六份 `client.db` 同名互相覆盖，那排 ok 作废）。三态对照：

- **A 整套**（主+wal+shm，校验和与原文件一致）→ `integrity_check` **损坏 100 行**（首条 `Tree 21 page 841: btreeInitPage() returns error code 11`），`sessions` 数出 32 行。
- **B 只主文件**（丢 WAL）→ **ok**，17 行，内容止于 `2026-09-23T18:19:14.331Z`、全 `backend=orca`、seq 1003–1024；文件 mtime 却是 09-24 13:47:01。
- **C `backup()` 一致快照**（SQLite 自己回放 WAL）→ **同样损坏 100 行** ⇒ 排除复制撕裂，损坏在**主文件 + WAL 这一对**里，活库读到的就是它。
- 其余六库三态全 ok：`state.db` 整套 28 行 / 只主 22 行；librarian 5/3；astrologer 0、master 3、socrates 2、scraper 1，WAL 皆 0 字节。

两条顺带事实：(1) 今日 8 条会话行 seq 是 **1–4**，主文件昨天的 17 行是 **1003–1024** ⇒ 本机 watermark 今天从 1 重启，**跨天比 seq 无意义**，只有「同 task 镜像行 vs 本机行」可比（正合 dev 的 per-writer 判据）。(2) 今日全部写入都在 WAL、主文件自昨天 18:19 未落盘。**因判我不写死**：网盘换主文件与「13:47 重建那次以 cp 动过 ws 下的库」效果相同，谁在 13:47 碰过这文件我测不出。

**dev 的 SQLite 判定（入档）**：open 只做 `Connection::open` + WAL + foreign_keys + schema marker/DDL，**不跑 quick_check/integrity_check、不修复不隔离**；损坏会在首个 WAL/schema 读写以 sqlite error 让 client/server 启动失败。**操作结论：集群 root 属部署约束，应移出 OneDrive/网盘**（不是「可恢复状态」）。

**上游机制读数（请他重判 (i)）**：本批 8 个 task 信封**无一进过 `acked`**，同 role 的 completion 全 `in_flight→acked`（0.2–0.3 秒）；全库历史对照 `task=acked` 9 条后端全 **orca**、`rejected/session_dead` 6 条后端全 **exec**（第 7 条 `e1989855` 拒因是 orca `terminal create` 失败、会话行却 `backend=exec` —— 谁回落到 exec 待他判）。投影侧：exec 会话 `delivery` **恒 `none`**，orca 起来后写 `delivery=accepted`。⇒ 形状是「**exec 不 ack task 信封 → 60 秒重排到点 → 重投刚退休 slot → 写 `session_dead`**」，活其实已干完（6/6，非竞态）；`requeued` 到 1–2 而 `attempt` 始终 0。另：13/13 信封「事件末态 == 账行现态」，账本无物化滞后（排除一条）。

**待处置**：搬 root 需要 client/server 全停且无进程持库，而那两 client 在隔壁会话手里 ⇒ 等人拍板：让那个会话收工后我全停搬到本地 FS，或就地由我停它起的 client。在他回 (i)/(ii) 之前我不修库。

## 运行时出盘（2026-09-24 20:0x，人判「停那两个 client 并搬」+「mv 后建软链」）

**动作**：现场已自然腾空（我发 SIGTERM 前两 client 与 server 都已退，`lsof` 报无进程持库）。按 dev 的处置「原样搬、只查副本、原库零写入」执行，脚本 `/tmp/onlyne-bug-141/round13/move_runtime{,2}.py`（v1 有两处我的错：`shutil.move` 后又 stat 原路径 → 崩在半路留下「文件走了、链接没建」的空位，v2 改成每步先 mv 立刻补链；v1 还把整个 `ws/` 做目录级软链，导致 git 把六份已跟踪的 ws `STATE.md` 报成删除，v2 退回真目录）。

**最终布局**：真身仍在 `/Users/dbydd/…/OneDrive-个人/new_document/Alexandria`（orca 路径的软链不动，worktree 指针不受影响）；**onlyne 运行时全部落在本地 `~/onlyne-runtime/alexandria/`**，原位留 21 个软链：`state.db{,-wal,-shm}`、`ws/<role>/client.db{,-wal,-shm}` ×6、`run/`、`logs/`、`keys/`、`cache/`。SQLite 顺链解析、边文件落在真身旁边，OneDrive 再摸不到库字节；那 21 条路径全在 gitignore 内，git 完全无感（脏项从 16 回到 10）。损坏的 scriber 主文件与 WAL **成对搬走、未动一刀**。

**功能验证（最小一发）**：`onlyne server start --root .` → pid 96125，`wait-ready` rc 0，`status` 回 `cluster=alexandria`、`event_head=564`（与搬迁前同一库、水位接上）、`role_count=7`；真身 `integrity_check` = ok、`sessions=28`；`server.log` 已落在本地 `~/onlyne-runtime/alexandria/logs/`；`server stop` 干净、停后无 socket 无持库进程。

**dev 的根因确认（`a91c853` 已推 main）**：本地 `onlyne complete` 走 adapter socket 的 `ClientOp::Report(Report::Complete)`，旧代码用 `dispatch.request` 把 raw report 直发 server，**绕过 client 的 `on_plugin_report → on_out`** ⇒ task 行永远 `in_flight`；completion 回执独立 acked 后，session exit 触发 server `release_exited_delivery` 自动 requeue，退休 slot 再写 `session_dead`。focused regression 1 passed（断言本地 task=Done、原 task msg accepted ack、server-facing 只剩投影心跳、无 raw Complete）。operations + supervisor handbook + 两份副本同步，新增五条口径：task/completion 行语义、per-writer seq、terminal `session_dead` 要走新 task、Orca 单实例宿主约束、SQLite 禁放同步盘。**我这轮的执行链读数被他逐条采信。**

**待处置两条**：(1) **scriber 坏库怎么落地**——两条路摆着：从 `~/.local/share/onlyne-forensics/round13v2-*/scriber/client.db.mainonly`（昨天 17 行、干净）恢复，或把坏对改名留证、让 client 首开时按 schema DDL 重建（服务侧账本才是权威，本机库是每 role 缓存）。dev 说「确认后再决定」，我没动。(2) 隔壁会话若再压形状，orca 后端在「Orca 已运行」下仍会撞单实例墙 —— 他那条 `e1989855` 的会话行 `backend=exec` 而拒因是 orca `terminal create` 失败，回落是谁做的仍待 dev 判。

## 事故：本地目录被 Orca 清掉（2026-09-24 20:2x–20:3x）

**经过**：按人的判语做「整仓落本地 + 五项笔记本体留网盘 + overlay 软链」时，我把真身开在 `~/orca/workspaces/research-flywheel/theme-Alexandria`（原为指向网盘的软链），并在同一步**摘掉 git**（删 `.git` 指针 + 把主仓 worktree 注册改名 `.decommissioned`）。几秒后 Orca 的 worktree 清理逻辑把这个「不再是有效 git worktree」的入口整个删除，`.orca-worktree-trash` 空、`~/.Trash` 里只剩一条自指死链 ⇒ **目录被直删，无回收**。我的搬运动作本身没问题，**是我把「无 git」和「住在 Orca 管辖树里」这两件事凑在一起，才让删除无声发生**。

**恢复（已完成，全部有据）**：
- 已跟踪内容自分支 `theme/Alexandria@fd856d9` 全量回来：注册目录改名复原 → 新路径写 `.git` 指针 → `git worktree repair` → `git reset --hard` ⇒ 脏项 0，文档/模板/skills/十一份手帐/`.gitignore` 一字不缺。
- 真身落在 **Orca 树之外**：`~/workspaces/research-flywheel/theme-Alexandria`。
- 运行时自 10:55Z 取证快照恢复：`state.db` 用 SQLite `backup()` 一致快照（`integrity ok`、events 564、sessions 28）；六份 `client.db` 同样用 `.backup`，scriber 用 dev 批准的 `mainonly` 昨天基线（17 行、ok），坏三件套归档在 `.onlyne/archive/scriber-corrupt-20260924T123221Z/`（附 integrity 报告与 PROVENANCE）。dev 那条「恢复后观察新 client.db 写入」在他回信前已实测过一次（当时 18 行、wal 226KB），那一拍的状态随目录一起没了，属可重做。
- 布局终态：网盘 `new_document/Alexandria/` 只放 `blogs papers people raw wiki` 五棵真身（180 文件与 git 副本逐文件 sha256 比对，零差异后才换链）；本地这五棵是软链，并从 git 索引移除 + 写进 `.gitignore`（最后一版快照留在 `fd856d9` 历史里，`origin` 上有）。提交 `1e9af59` 已推。

**净损失（未跟踪、云端也没有，找不回）**：`.obsidian/` 全套配置（图谱、快捷键、主题、插件开关）、`.obsidian_manual_added_resources/` 附件（已核：笔记里无引用，不伤内容）、`.onlyne/keys/` 与六份 ws `.onlyne/keys/` 密钥对、`.onlyne/logs/`、`.onlyne/run/`、各 ws `.pi/sessions/*.jsonl` 角色会话记录、`.omp/PLAN.md`、`.agents/skills/onlyne-role-payload-v2/`（导出器认的目标，重导即回）。

**由此定的两条硬规矩**：其一，**这个仓不能再同时「无 git」且「住在 `~/orca/workspaces/**`」** —— 要么保留 git 注册，要么搬到 Orca 树外（现已在树外，git 我留着：今天两次丢失里唯一把东西捞回来的就是它）。其二，**密钥与运行时与手帐分家存**：手帐与文档进 git，运行时进本地 FS 且已离开同步盘，取证快照另放 `~/.local/share/onlyne-forensics/`（这次的救命稻草，别清）。

**待办一条（起环前必做）**：**密钥重铸**。`cert_pin` 在 `spec.toml` 里活着（跟踪过），但服务端私钥与六份 client 私钥全丢 ⇒ 按 README §通电：`onlyne-server init --root . --listen 127.0.0.1:7812` 取新 `cert_pin` 回填 → 逐 role `onlyne-server generate --root . --role <r>`（ws 存在需 `--force`，会把注入面换回骨架，跑完 `git checkout -- .onlyne/ws/*/AGENTS.md .onlyne/ws/*/STATE.md` 找回手记）→ 六条 `[[client]].key` 粘回 spec → `onlyne reload` + `spec_diff` 回 no changes。这一步要不要现在做，等人一句。

## 密钥重铸完成（2026-09-24 20:4x，环已可用）

脚本 `/tmp/onlyne-bug-141/round13/recast_keys.py`，spec 前态备份 `/tmp/onlyne-bug-141/round13/spec.toml.pre-recast`。按 README §通电走通：`init` 前先把 `spec.toml` 挪开（就位即拒覆盖）→ 新 `cert_pin = sha256/sUsHVxjMb3QgespbCZpdlB6JIvNGbUM1JMZVD1nroi4=`、`.onlyne/keys/server.key` 763B 新生 → 逐 role `generate --force` 六条公钥按 `[[client]].role` 块定位回填（`_supervisor` 的合法占位照旧不动）→ `git checkout -- .onlyne/ws` 找回被 `--force` 换掉的六份手帐（STATE/AGENTS 全在位）。

**验证**：`server start` pid 44485 → `wait-ready` rc 0 → `roles` 7 条（`_supervisor` + 六 agent）→ **`spec_diff` 回 `spec: no changes`** → `status` `cluster=alexandria`、`event_head=564`（与恢复后的同一库）→ `stop` 干净。dev 通报里那句「sessions 28→29」不是这个仓（本机恢复后停在 28、无进程写入），已回他以免他把读数引到 Alexandria 头上。

**当前可跑状态**：密钥、spec、账本、六份 ws 齐；起环只差往各 role 的可见 tab 发 `ONLYNE_BACKEND=orca onlyne client run --workspace <abs>/.onlyne/ws/<role>`。注意 orca 后端在「Orca 已运行」下会撞单实例墙（复压十三②），要压真形状先解决宿主那层，或换 `exec`/fake 后端做投递面验证（代价：exec 不 ack task 信封，那条已被 dev 在 `a91c853` 修掉，可复验）。
