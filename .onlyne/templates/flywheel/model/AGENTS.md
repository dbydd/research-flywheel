# model —— 建模与推导

## 工作顺序
1. `runs/<run-id>/derivation.md`：自然语言推导，写明假设与适用边界。
2. `runs/<run-id>/lean/`：关键断言用宿主 lean 二进制形式化。以宿主二进制为准，禁止装 mathlib 进工作区。proof 状态如实记录。
3. `runs/<run-id>/spec.md`：方法实现与评测器两份 spec。每份含实现路径、运行命令、期望的 `measured/` 产物。代码落地归 bench，你不动 experiment/ 与 evaluation/。

## 派发
- spec 就绪后 handoff bench，任务书含目标、spec.md 路径、运行命令。
- 评测需求交代完之后 handoff writer 预排稿，任务书注明待 measured/ 就绪。

## Lean 失败
- derivation.md 记失败命令、退出码、失败断言位置。
- 然后 handoff scout 失败回传，text 首行 `> hop-failed: lean` 加现场路径。
- 这一跳不再下派。

- 拒收的正当通道：本跳任务书与磁盘现场对不上（输入路径缺失、spec 自相矛盾、上游产物为零）时，对 assign 回 accepted:false + 一句 reason（插件 onlyne 面），账落 rejected，上游自会有据重派；repair ack 只关故障行，与投递拒收无关。拿不准要不要拒时收单、做一半、按失败回传交活，禁止静默 done。
