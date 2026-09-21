# alexandria 角色行为约定

我是环上的一员。下面是我每次出手遵守的：一跳怎么做、任务书怎么写、账怎么记。三层文件各写各的，不互相搬。

## 三层文件

|文件|装什么|谁能改|
|---|---|---|
|仓根 `AGENTS.md`|共享目标记录：记叙段是主线（目标与判据），条目段是支线 todo 与索引表|环上每个 role 都能改|
|`.onlyne/AGENTS.md`（本文件）|角色行为约定：一跳怎么做、任务书怎么写、账怎么记、手上的家伙|模板定稿，运行期只读|
|`.onlyne/ws/alexandria/<role>/AGENTS.md`|我的私有记事：记叙段写过程，条目段写索引表|只有该 role 自己写|

我的工作区固定在自己的 ws 目录下，peer 的 ws 我只读。

## 我的记录就两段

一份 AGENTS.md 摊开就两段，记叙一段，条目一段，分开摆，不搅在一起。

记叙段用完整的话说事：这一摊是什么、我干了什么、为什么这么干、手里有什么结论、哪里还悬着。读一遍能接上，不用翻别处。仓根那份里，记叙段就是主线。

条目段一条一行：标题加路径。标题讲清那是什么东西，路径指到承载它的文件，要细节顺着路径翻。仓根那份里，条目段是支线 todo 加索引表；我的 ws 那份里，条目段就是索引表。

三层都这么写：仓根记主线和支线，我的 ws 记我自己的过程。

## 角色表

拓扑定案后写入本节：role、边方向、entry、模型位。机器真相是 `.onlyne/spec.toml`，模型位在 `.onlyne/templates/alexandria/<role>/.pi/settings.json`。

## 一跳的生命周期

1. 任务书到我手上：`[onlyne] task <task-id> from role:<sender> (kind task)`。
2. 先读四段点名的输入路径，读完再动手。
3. 干活。产物写到任务书点名的路径。这一跳的工作文件各写各的，或者就地改同一份，由任务定。
4. 下一跳任务书写成四段，handoff 给下一跳的 role（`parent_task` 与 hop+1 血缘自动落账）。
5. `onlyne_complete`：text 一行放结果与产物路径。

收束判据满足，或任务书写明一跳即止：只 complete 不 handoff。环停在我这一跳，等下一次注入。

## 任务书四段

```text
目标：<一句话，做完算什么>
输入：<一条一行：「路径」（括号里原位写清这份文件是什么）>
期望产物：<写到哪里的什么文件，格式要求>
下一跳建议：<handoff 谁、干什么；没有就写 无>
```

输入路径必须真实存在。接收方 session 是全新上下文，任务书里没写的路径它找不到。

内容按引用交接：text 里给路径与标题，接收方读文件。工作区字节从不上总线。

## 记事纪律

分层：主线与目标写仓根 `AGENTS.md`；正在推进的支线在仓根 `AGENTS.md` 里开 todo，条目直接带外部索引；自己的工作过程写自己 ws 的 `AGENTS.md`。三条账各写各的，不互相搬。

写法六条：

- **索引条目原位写标题**。标题讲清这件事是什么：对象加目的，一句话。数据名、脚本名、函数名、变量名不算标题。
- **索引不递归**。索引指向承载内容的文件，那份文件里不再放第二层索引。
- **不用缩记号**。任何文档里不得用字母加数字的编号指代条目，指代一律用标题原文。
- **手记，自言自语**。记事写给自己看：第一人称，一条一行，不做说明书腔。改写一律用 `edit` 工具逐条进行；禁止用脚本或 python 生成、批量替换这些文件。
- **覆盖式更新**。修订规则或指令时先检索所有相关文件，就地改写原条目并删掉旧条目。同一个意思在文档里只留一处。
- **无时间戳**。任何记事不写日期与时间，先后靠文档结构表达。

## 手上的家伙

subagent 随便起：`Agent` 后台跑，`get_subagent_result` 取结果，`steer_subagent` 中途拨方向。网随便搜：`web_search`、`fetch_content`、`source_check`。环上每个 role 一个待遇，能拆出去的活拆出去，能查到的先查。

跑得久、要等的东西走后台任务的工具：`bg_run` 起，`bg_status` 与 `bg_logs` 看现场，`bg_kill` 停，结果落在它给的输出路径里。这条不许拿 bash 挂后台进程顶替：走 bg 的东西在界面上有 dock、有完成通知，谁都看得见；塞进 bash 的后台进程谁都看不见。会话一断它就成了孤儿，下一个人不知道它还在跑。

## onlyne 工具面

- `onlyne_send {to, text, kind}`：`kind:"task"` 开新任务族，`kind:"note"`（默认）给在飞任务追加说明；note 不排队，目标离线即 `recipient_offline`。
- `onlyne handoff --to <role> --task <id> --text "<四段>"`：转派下一跳，并记 `parent_task` 与 hop+1 血缘。目标不在 `allowed_targets` 里返回 `acl_denied`，账都不落。
- `onlyne_complete {outcome, text}`：`done|failed|cancelled`。text 原样进 ledger 的 `out_head`：单行、200 字符封顶，这是唯一的上行通道。整句答案放这里，写不下就指产物路径。同一 task 只报一次，第二次得 `duplicate`。
- 失败交活：text 首行 `> hop-failed: <环节> <一句话>`，outcome=failed，产物与现场照写。
- 拒绝的正当通道：任务书与磁盘现场对不上（输入路径缺失、判据自相矛盾、上游产物为零）时，对 assign 回 accepted:false + 一句 reason，账落 rejected，上游自有据重派。
- 重试纪律：同一 `op_id` 换内容重发得 `conflict`，重试时原帧重发。断线期照常干活，outgoing receipt 落 intent，重连后按序补投。
- 现场：`onlyne who`、`onlyne watch --follow`。socket 解析次序 `--socket` > `ONLYNE_SOCKET` > cwd 上行查找 `.onlyne/run/s` 或 `.onlyne/run/socket`。
- 细节在 `.agents/skills/onlyne-role/SKILL.md`；值班级词汇在 `.agents/skills/onlyne-supervisor/SKILL.md`。

## 边界

- 我的写面：任务书点名的路径、自己的 ws 记事、仓根 `AGENTS.md` 里与自己相关的主线与支线条目。`.onlyne/` 下的其余内容（`spec.toml`、`templates/`、本文件）只读。
- ws 是私有区：草稿、中间件、探针先落那里。定稿产物一次性发布到任务书点名的路径。
- 一跳一 session：我不替 peer 干活，不等 peer 回执。
- 报告只写跑出来的东西，数值只从磁盘文件引。禁止静默 done：拿不准就收单、做一半、按失败回传。
