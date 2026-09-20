# gemini —— 双子工作区

本工作区是一个二元环：两个 role 互相推任务，没有第三条边，没有中心调度。

workspace 是一个 role 的长期工作区，内容有记忆、设定、历史文件。session 是这个 role 手头的一件工作，一跳即结。所有信息写成文件。结论都能回溯到 `runs/` 与 `onlyne ledger` 的 task 行。

三条本体论：

1. 环 = castor ⇄ pollux，两条互指的边。每条边带一份任务书。
2. 状态全在文件里。会话不继承上下文，接收方只读任务书点名的路径。
3. 一跳一 session：干活 → handoff peer → `onlyne_complete` 交活退出。不等下游，投递后立即返回一行 receipt JSON。

## 角色表

|role|职责|peer|entry|model|
|---|---|---|---|---|
|castor|接任务书干活，产物写 runs/，下一跳任务书 handoff 给 pollux|pollux|★|`axonhub/generic-researcher-powerful`，thinking max|
|pollux|接任务书干活，产物写 runs/，下一跳任务书 handoff 给 castor|castor||`axonhub/supercheap`，thinking max|

表外的 `_supervisor` 是 admin mount：走 `onlyne --server-root .` 值班面，唯一动作是投第一发与人工唤醒，零上行边。它的岗位说明在 `.pi/SYSTEM.md`。

`★` 标第一发的注入对象，全表恰好一个，本主题是 castor。两个 role 职责相同，模型位不同；边的方向决定谁是下一跳。模型位正本在 `.onlyne/templates/gemini/<role>/.pi/settings.json`。

`allowed_targets` 与 `prose` 是 ACL 与身份的机器真相；改动落 `.onlyne/spec.toml` 与模板目录，再 reload 才进 ws。

## 一跳的生命周期

1. 任务书到达：`[onlyne] task <task-id> from role:<sender> (kind task)`，角色 prose 经 welcome 已在上下文。
2. 读任务书四段点名的输入路径，读完再动手。
3. 干活。产物写 `runs/<slug>/`。slug 由任务书给或自取，唯一且可读。
4. 下一跳任务书写成四段，handoff 给 peer（`parent_task` 与 hop+1 血缘自动落账）。
5. `onlyne_complete`：text 一行放结果与产物路径。

任务书的收束判据满足，或任务书写明一跳即止：只 complete，不 handoff。环停在这一跳，等下一次注入或人工唤醒。

## 任务书四段

```text
目标：<一句话，做完算什么>
输入：<必须读的文件路径，runs/ 与 root 文件为准>
期望产物：<写到哪里的什么文件，格式要求>
下一跳建议：<handoff 谁、干什么；没有就写 无>
```

输入路径必须真实存在。接收方 session 是全新上下文，任务书里没写的路径它找不到。

内容按引用交接：text 里给文件路径，接收方读文件。工作区字节从不上总线。

## 文件纪律

- `runs/` 是产物根，一件任务一个子目录 `runs/<slug>/`。本跳产物只写自己这一跳的目录。
- 改动上游文件时，把改了什么与理由写进本跳目录。
- 追加式台账（`runs/` 内的记录、`payload/` 的任务书）直写 root，接力唤醒要求实时。
- 只读面：`.onlyne/`、root `AGENTS.md`、peer 的 ws。
- role 自己的 ws 是私有区：草稿、中间件、探针先落那里。定稿产物一次性发布到任务书点名的 root 路径。

## onlyne 工具面

- `onlyne_send {to, text, kind}`：`kind:"task"` 开新任务族，`kind:"note"`（默认）给在飞任务追加说明；note 不排队，目标离线即 `recipient_offline`。
- `onlyne handoff --to <role> --task <id> --text "<四段>"`：转派下一跳，并记 `parent_task` 与 hop+1 血缘。目标不在本 role 的 `allowed_targets` 里返回 `acl_denied`，账都不落。
- `onlyne_complete {outcome, text}`：`done|failed|cancelled`。text 原样进 ledger 的 `out_head`：单行、200 字符封顶。这是唯一的上行通道，整句答案放这里，写不下就指产物路径。同一 task 只报一次，第二次得 `duplicate`。
- 失败交活：text 首行 `> hop-failed: <环节> <一句话>`，outcome=failed，产物与现场照写。
- 拒绝的正当通道：任务书与磁盘现场对不上（输入路径缺失、判据自相矛盾、上游产物为零）时，对 assign 回 accepted:false + 一句 reason，账落 rejected，上游自有据重派。
- 重试纪律：同一 `op_id` 换内容重发得 `conflict`，重试时原帧重发。断线期照常干活，outgoing receipt 落 intent，重连后按序补投。
- 现场：`onlyne who`、`onlyne watch --follow`。socket 解析次序 `--socket` > `ONLYNE_SOCKET` > cwd 上行查找 `.onlyne/run/s` 或 `.onlyne/run/socket`；client 把它注入它起的 session。
- 细节在 `.agents/skills/onlyne-role/SKILL.md`；值班级词汇在 `.agents/skills/onlyne-supervisor/SKILL.md`。

## 纪律

- 报告只写跑出来的东西，数值只从磁盘文件引。
- 失败也交活：跑不动的结论写进 `runs/`，用 `outcome=failed` 交报告，text 首行带现场路径，让下游有据可依。
- 禁止静默 done。拿不准就收单、做一半、按失败回传。

## 运行面指针

- 集群运维口径：`README.md`。
- supervisor 值班职责：`.pi/SYSTEM.md`。
