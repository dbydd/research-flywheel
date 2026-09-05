# Research Flywheel

全自动科研飞轮模板。一个 idea 进，一篇论文或一份失败结论出，然后从结果自动衍生下一个 idea。

Pi 是唯一控制面，Orca 是多 agent 执行体。每个 worker 在独立 Orca worktree 里跑 Pi。

## 前置

- Pi：`pi --version`
- Orca：`orca status --json`
- Lean：仅 modeling 站需要，宿主自装，模板不装

## 快速开始

1. 打开模板：`cd research-flywheel && pi`
2. 运行 `/bootstrap`，按提示输入研究领域、第一个问题、已知约束
3. scout 派发后写入第一条 idea，运行 `/flywheel <idea-id>` 逐站推进
4. 成稿进 `papers/`，失败进 `.agents/archive/`

## 生产链

scout → modeling → experiment → evaluation → writing → review → archive

| 站 | 产出 |
| --- | --- |
| scout | 拉证据到 `research/`，写 idea 进 `.agents/ideas.jsonl` |
| modeling | 自然语言推导 + Lean 形式化 + 实现 + 评测器 |
| experiment | 跑 baseline 和 candidate，记值和 delta |
| evaluation | 按评测契约出 verdict |
| writing | 写带溯源的 report |
| review | 内容审查，verdict + 编号 finding |
| archive | keep 进 `papers/`，失败进 `.agents/archive/`，写台账 |

## 命令

- `/bootstrap [方向]`：交互式派发 scout；带参则直接派发
- `/flywheel <idea-id>`：报告 idea 的下一站和前置产物

## 目录

- `.agents/`：调度器私有状态（ideas、ledger、runs、archive、roles）
- `research/`：证据
- `experiment/`：领域代码
- `evaluation/`：评测器
- `papers/`：论文成稿

## 动力源

初次启动靠用户给的 seed（方向 + 问题）。之后每轮结束，从上一轮论文或失败结论提取 open question，自动生成下一条 idea。idea 必须带非空 evidence 和评测契约，否则不进池。
