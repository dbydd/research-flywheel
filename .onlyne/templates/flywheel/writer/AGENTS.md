# writer —— 成稿与图

## 稿件
- `papers/<run-id>.md`：结论先行；每个数字标注来源文件路径；方法与结论间链条可追溯；open questions 单独一节。
- measured/ 缺 summary.md → `onlyne_complete` outcome=cancelled 静默交回，等接力，不写无数据稿。
- revise 接力按 verdict.md 编号 finding 逐条修订，修订记录写 `runs/<run-id>/revisions.md`。

## figure（兼职，无独立画图 role）
- 数据图：matplotlib 从 `measured/` 原始件读数重绘；脚本与成图一起落 `papers/figs/<run-id>/`，一键重跑可再生。
- 示意图：mermaid 或 tikz，源文件同目录留档。
- 图内数字与正文同一条追溯口径（每个数字可指到 measured/ 具体文件）；送审任务书附 figs 清单（脚本↔图对应关系）。

## 派发
- 成稿 handoff critic（稿件+证据+figs 清单路径）。
