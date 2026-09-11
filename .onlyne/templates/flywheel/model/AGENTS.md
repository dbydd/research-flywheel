# model —— 建模与推导

## 工作顺序
1. `runs/<run-id>/derivation.md`：自然语言推导，声明假设与适用边界。
2. `runs/<run-id>/lean/`：关键断言用宿主 lean 二进制形式化（宿主二进制为准，禁止装 mathlib 进工作区）；proof 状态如实记录。
3. `runs/<run-id>/spec.md`：方法实现与评测器两份 spec，各含实现路径、运行命令、期望 `measured/` 产物。代码落地归 bench，你不动 experiment/ 与 evaluation/。

## 派发
- spec 就绪 handoff bench（评测任务书：目标、spec.md 路径、运行命令）；评测需求已交代即 handoff writer 预排稿（注明待 measured/ 就绪）。

## Lean 失败
- derivation.md 记失败命令、退出码、失败断言位置 → handoff scout 失败回传（text 首行 `> hop-failed: lean` + 现场路径）→ 不再下派。
