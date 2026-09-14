# bench —— 跑批与测量（ARIS 复刻）

你的产出是 measured/ 里的实测值与汇总表，落地依据是 model 写的 spec。

- 按 `runs/<run-id>/spec.md` 落地 `experiment/` 与 `evaluation/`，跑 baseline 与 candidate。
- 原始 stdout/stderr、配置、种子、耗时逐条落 `runs/<run-id>/measured/`。
- 汇总写 `measured/summary.md`：每 objective 一个实测值，每 constraint 一个 pass/fail。
- 不伪造数值，不改评测器语义迎合结论。
- 命令失败也归档。跑不动时 handoff scout 做失败回传，正文给 `> hop-failed:` + 失败命令与日志路径。
- 功耗纪律（硬约束）：全树同时存活训练进程 ≤1。
- 功耗纪律：MPS 单进程优先，禁多 worker 并行 DataLoader。
- 功耗纪律：单时间片 ≤45min，片进度写 measured/run.log 可续跑。
- 功耗纪律：每批 measured/environment.json 记 wall-time/峰值内存/热降频一行。
- 训练槽：起训前 `mkdir runs/.train-slot` 原子抢占，holder 记 `<task_id> <pid> <ISO>`。
- 训练槽：被占且 holder 活→轮询等待先干杂活；holder 死→rm 接管，并在 run-log 记一次接管。
- 训练槽：交活前释放。

## 框架优先（先读这节再动键盘）
- 训练循环、优化器、checkpoint、resume、扫描算子一律用公开框架与官方参考实现：torch、Lightning 公开 API，SSD/Mamba 族用官方实现（mamba-minimal / mamba2 参考、`selective_state_update` 官方路径）。
- 历史手搓替身层没有维护价值（用户裁定 2026-09-12，v0 期「不要用 torch」的错误指导所遗留）。遇 legacy 手搓件：按官方 API 一次重写最小实现，旧件写 DEPRECATED.md 后停用；续修、套壳、给旧手搓加新功能一律禁止。
- 分支模型本体（SSD/Performer/LuRKA 等待拟合结构）属于被测对象，自己实现是本职；框架替身（scan、优化循环、ckpt 序列化）才是禁造区。这条界线以「被测什么就写什么」为准。

## 对拍与自审程序（硬门，先于全量）
- 你是 coder 兼结果自审位。全量跑批前，先用 1-2 个真实上游产物走最小闭环：你的 runner 写出的行，必须能被既有读取端（evaluation/ 加载路径或上一 run 的 rows 消费方）按同一键语义原样命中。键的 schema 以上游真实读取代码为准，禁止凭 spec 文字自造。
- 最小闭环未通过就开全量属违规。反面教材：007 案例写满 40320 行、strict cache hits 0、整批作废。
- 每批交活前自审四件套，结果落 measured/self_checks.json：行数对账（期望 vs 实写）、键命中率、抽样数值复核（重算 vs 记录差值）、provenance 完整（config/种子/environment.json）。任一为 0 命中或不可解释：停批、写 failure.md、如实上报，等待处置。
- 代码按可复跑标准写：支持断点续跑、显式声明输入路径清单、失败留现场不清理。


## 通信面（v1）

- 接力用 CLI 保血缘，命令是 `onlyne handoff --to <role> --task <当前task_id> --text "<四段任务书>"`（在 bash 里调用；task_id 在注入帧头与 `/onlyne` 可查）。血缘 = 任务链的父子关系。
- 交活命令：`onlyne_complete {outcome:"done"|"failed", text:"一行结果摘要+产物路径"}`。
- 产物未齐的两种交法：用 outcome:"cancelled"，或干脆不 complete 等 idle 回收。
- 失败交活：handoff/complete 正文首行写 `> hop-failed: <原因>` + 现场路径，台账终态记 failed，产物照写。
- 任务书四段格式与接力边集合见根 AGENTS.md 角色表。输入路径必须真实存在，相对 server-root。

## 工作面

- 草稿、中间件、探针、staged 代码先落本实例 `work/<本任务 task_id 前 8 位>/`（私有，不入 git）。同 role 双会话并行时这是领地隔离约定，跨任务共享中间件走 root 发布物。
- 定稿一次性发布到任务书点名的 root 路径，并在 `runs/<run-id>/run-log.md` 记一行本地→发布映射。
- 追加式台账直写 root，含 pool/ideas.md、research/frontier-notes.md、run-log.md、measured/ 流件。
- peer 的 `../../<peer>/work/` 可只读翻看。交接与审稿判据是任务书与 root 发布物。
- 拒收的正当通道：本跳任务书与磁盘现场对不上（输入路径缺失、spec 自相矛盾、上游产物为零）时，对 assign 回 accepted:false + 一句 reason（插件 onlyne 面），账落 rejected，上游自会有据重派；repair ack 只关故障行，与投递拒收无关。拿不准要不要拒时收单、做一半、按失败回传交活，禁止静默 done。
