# supervisor 运维手帐

这一份是 supervisor 的私有手帐（集群侧）。固定口径在 `.supervisor/AGENTS.md` 与 `README.md`；环上内容族的进度与 todo 在仓根 `STATE.md`。

## 集群现状（onlyne 1.4.0 验收期，**已停**）

server 与六 client 全部停止（`onlyne server stop` 收掉 pid 79602，client 逐个精确 pid SIGTERM），`onlyne status` 报无 socket。TUI 板 pid 7912（09-23 17:39 起，`term_d124be86`）仍指向已停的 server——**dev 明示暂停期间不用处理**，解牌后第一件事再收。要复压或读帧，先 `onlyne server start --root .`（读帧不必起 client）。

- 真身在 `/Users/dbydd/Library/CloudStorage/OneDrive-个人/new_document/Alexandria`；`/Users/dbydd/OneDrive` 是同一份的 firmlink（同 inode，非副本）。HEAD `ddf019a`，与 `origin/theme/Alexandria` ahead/behind `0 0`。
- 映像：`onlyne` CLI 12:27、`onlyne-server`/`onlyne-client` 15:14、`onlyne-gateway` 09-23 23:19 ⇒ 本机这套是 **dev 本地构建**，非发布渠道产物（他确认 `~/.cargo/bin` 尚未按发布版重装）。
- 六 client 的 tab↔role 实测映射：scriber `term_b54f9994`、librarian `term_1efa68d1`、astrologer `term_09098506`、master `term_f41cf013`、socrates `term_93262969`、scraper `term_ab0c128d`。
- 重启法：`ps` 按 `--workspace` 认精确 pid 后 SIGTERM（别按名字杀，dev 在同机跑 e2e 会让 `ps` 计数飘），再往同一 tab `orca terminal send` 原启动行；server 用 `onlyne server stop/start --root .`。
- 档案：工作记录 `/tmp/onlyne-bug-141/round4/swap-acceptance.md`（457 行，复验一~九 + 复压七~十二 + 两观察定稿全在）；库备份 `round7-pre/`、`round12/state.db.pre`、旧 schema-3 `swap-backup/schema3/`；脚本 `/tmp/onlyne-bug-141/round7/`。`/tmp/omp-probe-*` 已清 0。

## 暂停牌（dev 挂，2026-09-24 17:30 → 解牌待声明）

crates.io 真实 publish **未开始**（当前只跑 `cargo publish --workspace --dry-run`；他先说「正在执行」后更正）。GitHub/npm 发布他称已完成。我这边**冻结**：集群不起、压测不跑、手册与值班文档的 1.4.0 适配不改。

- **包名事实（dev 给）**：crates.io = `onlyne-cli`（装出 `onlyne` 二进制）+ `onlyne-server` / `onlyne-client` / `onlyne-gateway` / `onlyne-tui` + 其余 workspace crates，统一 **1.4.0**；npm = `pi-onlyne` **1.2.0**（人已手动发）。最终安装命令等他解牌声明，我文档一次写对。
- **我核到的对外事实**：tag `v1.4.0` → `fbd9a23`；`.github/workflows/` 确有 `ci.yml` `release.yml`；`gh release list` **只有 v1.0.0 一条，无 v1.4.0 release**（与他「GitHub 已完成」的说法待他复核）；`gh run list --workflow release.yml` 回 404（默认分支上查不到该 workflow 的运行记录）；`crates.io/api/v1/crates/onlyne` 回 403。这几条只读，已回他。

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
- **他要求的一轮压测（解牌后执行）**：完成 + handoff + 杀 client 形状，期望账落 `acked`、投影 `exited`、两侧 seq 差 0、ghosts 无新行；读数报他。

## 文档口径迁移（注入面与手帐面）

人判「把手帐写进 context 文件是反模式」：注入链每轮整份进 prompt，一写就把前缀缓存打掉。全仓已按此拆开。

- 正本口径：`.onlyne/AGENTS.md` §注入面与手帐面、§我的记事就两段。判据一句：这段文字会不会因某次交付而变——会，它属于 `STATE.md`。
- 注入面（保留固定物）：仓根 `AGENTS.md`（目标、判据、索引表）、`.onlyne/AGENTS.md`（约定）、六份 ws `AGENTS.md`（岗位口径 + 三行指针）、`.omp/AGENTS.md`（指针本）。
- 手帐面：仓根 `STATE.md`、`.supervisor/STATE.md`（本件）、六份 ws `STATE.md`、六份 `.onlyne/templates/<role>/STATE.md`（两行骨架，`generate` 走 `load_tree` 会整棵复制）。**十一份手帐现全部进 git 跟踪**（OneDrive 回滚事件后的处置）。
- 同步改到的文档：`README.md`（15 处）、`STRUCTURE.md`（8 处）、`.agents/skills/wiki-format/SKILL.md`（5 处）、`.agents/skills/scientist-profiles/SKILL.md`（2 处）、`.onlyne/spec.toml`（scraper prose + 一条注释，已 `reload`，`spec_diff` 回 no changes）。
- dev 导出的两件（`.agents/skills/onlyne-role`、`onlyne-supervisor`）待重导：`onlyne skill export --set role --set supervisor --force`（他解牌后跑，手册现在是仓内真文件）。
- 我的 omp 笔记本已降成固定指针本，现场状态一律写本文件。

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
