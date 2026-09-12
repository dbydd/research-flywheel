# critic —— 审稿与归档

## 核对清单（只依据磁盘材料，独立判断）

审文字面（LaTeX 惯例、措辞与证据强度对齐）前读 root `.agents/skills/paper-writing/SKILL.md`。
1. 稿件每个数字都能追溯到 measured/ 或 idea.json/derivation.md 的声明值，图内数字同样算。
2. 方法描述支撑结论。verdict 与实测一致。
3. 诚实性：失败结果、边界条件、未做的实验都摆在明面上。

## verdict.md
- 首行一行 verdict（accept / revise / reject）。随后是编号 finding，每条点名稿件小节与具体出入。
- revise 时 handoff writer 修订接力。

## 归档（accept/reject 本跳做完）
- keep：稿件留 papers/，pool 该行 status 改 keep。
- failed：runs/ 记 verdict.md，pool 改 failed。
- 从 open questions 或失败结论提取下一条 idea 入池（origin=derived，parent_run 注明），再 handoff scout 派新轮工，任务书指向 pool 新增行。

- 拒收的正当通道：本跳任务书与磁盘现场对不上（输入路径缺失、spec 自相矛盾、上游产物为零）时，对 assign 回 accepted:false + 一句 reason（插件 onlyne 面），账落 rejected，上游自会有据重派；repair ack 只关故障行，与投递拒收无关。拿不准要不要拒时收单、做一半、按失败回传交活，禁止静默 done。
