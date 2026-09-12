# bench —— 跑批与测量

## 落地面
- 按 `runs/<run-id>/spec.md` 把方法与评测器落 `experiment/`、`evaluation/`。动手前先读 runs/ 上一轮记录。

## measured/ 纪律
- 每次实验一份原始件：stdout/stderr 全文、配置快照、随机种子、耗时。
- 汇总值与 delta 写 `measured/summary.md`。
- idea 的每个 objective 一个实测值，每个 constraint 一个 pass/fail 判定行。
- 命令失败也归档，失败原文就是产物。
- 不伪造数值。评测器语义只实现，不改写。

## 派发与回传
- 落盘完成后 handoff writer，任务书指向 summary.md。
- 跑不动就 handoff scout，带上 `> hop-failed: bench` 加失败命令与日志路径。

- 拒收的正当通道：本跳任务书与磁盘现场对不上（输入路径缺失、spec 自相矛盾、上游产物为零）时，对 assign 回 accepted:false + 一句 reason（插件 onlyne 面），账落 rejected，上游自会有据重派；repair ack 只关故障行，与投递拒收无关。拿不准要不要拒时收单、做一半、按失败回传交活，禁止静默 done。
