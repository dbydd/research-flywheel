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

**我这边另两条核验**：`~/.cargo/registry/cache` 里 19 个 `onlyne-*-1.4.0.crate` 齐；五进制 + `onlyne-testkit`/`onlyne-gateway-fake` 时间戳 18:14:20、签名在。`onlyne-cli` 这个包会同时装出 `onlyne` 与 `onlyne-cli` 两个同尺寸入口，已问 dev 是否有意留的别名。`onlyne-role-payload-v2/` 是**导出器认的第三个目标**（它也报 unchanged），我先前判它「旧残留可清」判错，已撤回。

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

1. **解牌后三件**：走正常渠道装 1.4.0（`cargo install onlyne-cli …` 还是 brew，等他给最终命令）→ `onlyne skill export --set role --set supervisor --force` 重导手册 → 收 TUI 7912 后压「完成 + handoff + 杀 client」形状并报读数；再把 1.4.0 口径（七动词裸调用 exit 2 且不碰 socket、`onlyne_handoff` 插件、家族元信息 family/hop_budget/origin/deadline/labels、`requeue_ttl_secs`、`--once --state active|all`）落进 README / 值班文档。
2. 本仓 push：已 commit 到位（见 §OneDrive 回滚事件的处置），**push 等解牌或人一句话**；工作树里内容族产物（`blogs/`、`papers/`、`wiki/`、`raw/`）与文档面分开提交。
3. 待人拍板的设计项三条：无 client 的 `queued` 回执要不要就地结掉（`39408cb` 已给出可选预算那半）、claim 语义收成哪一种、操作者能否强制重投已结算任务（dev 依据：现在没有任何入口能造出第二份 verdict，若要即属新增有意能力）。done 判定维持不加第二道闸、只加证据。
4. role 侧 recall-failed 未治；知识层 `.obsidian/` 勿动且**不进提交**；隔壁 lora2/lt formal 集群勿混。

## 口径提醒

- 注入面（`AGENTS.md` 链）只放固定物，进度/todo/过程一律写 `STATE.md`；判据：这段文字会不会因某次交付而变。
- 同步盘上的手帐**必须 git 跟踪**：OneDrive 会用云版本静默换掉本地文件（mtime 一起回退），未跟踪即无痕丢失。
- `onlyne send` 无 `--reason`；`--state` 取值只有 `active`/`all`。
- 脚本一律先 `write` 成文件 + `python3 -m py_compile` 再跑；有界循环写上界，禁 `while True`；`orca terminal read` 的缓冲会留着同一 tab 前一个实例的行，别拿它判 role。
