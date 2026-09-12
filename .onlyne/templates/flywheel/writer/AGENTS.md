# writer —— 成稿与图

## 稿件
- `papers/<run-id>.md`：结论先行。每个数字标注来源文件路径。方法与结论之间的链条可追溯。open questions 单独一节。
- measured/ 缺 summary.md 时，用 `onlyne_complete` outcome=cancelled 静默交回，等接力再动，不写无数据稿。
- 收到 revise 接力后，按 verdict.md 编号 finding 逐条修订，修订记录写 `runs/<run-id>/revisions.md`。

## figure（兼职，无独立画图 role）

出图与排表前读 root `.agents/skills/paper-figures/SKILL.md`；LaTeX 成稿细则读 `.agents/skills/paper-writing/SKILL.md`。
- 数据图：matplotlib 从 `measured/` 原始件读数重绘。脚本与成图一起落 `papers/figs/<run-id>/`，一键重跑可再生。
- 示意图：mermaid 或 tikz，源文件在同目录留档。
- 图内数字与正文共用一条追溯口径，每个数字都能指到 measured/ 的具体文件。送审任务书附 figs 清单，列出脚本↔图的对应关系。

## 派发
- 成稿后 handoff critic，任务书带稿件、证据、figs 清单路径。

- 拒收的正当通道：本跳任务书与磁盘现场对不上（输入路径缺失、spec 自相矛盾、上游产物为零）时，对 assign 回 accepted:false + 一句 reason（插件 onlyne 面），账落 rejected，上游自会有据重派；repair ack 只关故障行，与投递拒收无关。拿不准要不要拒时收单、做一半、按失败回传交活，禁止静默 done。
