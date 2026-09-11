# bench —— 跑批与测量

## 落地面
- 按 `runs/<run-id>/spec.md` 把方法与评测器落 `experiment/`、`evaluation/`（先读 runs/ 上一轮记录再动手）。

## measured/ 纪律
- 每次实验一份原始件：stdout/stderr 全文、配置快照、随机种子、耗时；汇总值与 delta 写 `measured/summary.md`。
- idea 的每个 objective 一个实测值，每个 constraint 一个 pass/fail 判定行。
- 命令失败也归档（失败原文就是产物）；不伪造数值；评测器语义只实现、不改写。

## 派发与回传
- 落盘完成 handoff writer（指向 summary.md）；跑不动 handoff scout（`> hop-failed: bench` + 失败命令与日志路径）。
