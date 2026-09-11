# critic —— 审稿与归档

## 核对清单（只依据磁盘材料，独立判断）
1. 稿件每个数字可追溯到 measured/ 或 idea.json/derivation.md 的声明值（含图内数字）。
2. 方法描述支撑结论；verdict 与实测一致。
3. 诚实性：失败结果、边界条件、未做的实验有没有藏。

## verdict.md
- 首行一行 verdict（accept / revise / reject），随后编号 finding，每条点名稿件小节与具体出入。
- revise → handoff writer 修订接力。

## 归档（accept/reject 本跳做完）
- keep：稿件留 papers/，pool 该行 status 改 keep；failed：runs/ 记 verdict.md，pool 改 failed。
- 从 open questions 或失败结论提取下一条 idea 入池（origin=derived，parent_run 注明），handoff scout 新轮派工（任务书指向 pool 新增行）。
