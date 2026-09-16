# research_project/ — 研究项目文件区

一项目一文件、四段生长制。`planner` 是 `registry.json` 唯一写主。替代旧 `pool/`（v0.3.2 起废止，git 参照 4d3601b）。

## 目录布局

```
research_project/
  README.md                        # 本文件
  registry.json                    # 项目×轮次全局账（planner 专写）
  <slug>.md                        # 研究项目文件（生长制正文，结构见下）
  <slug>/
    proposals/{kaoti,zhongqi,jieti}.md   # 开题/中期/结题申报书
    packs/<关口>.md                        # qa 送审包（中期检查/结题验收）
    gates/<关口>.decision.md               # 关口判词（chair 执笔）
    gates/<关口>.referee-<1|2|3>.md        # 独立意见书（席位号由 chair 分发点名）
```

run-id 全局唯一：`<slug>--<轮次>`，账记 registry.json。过程件（lean/、measured/、run-log.md、header-snapshot.md）落 `runs/<run-id>/`。

## registry.json 形状

```json
{"projects":[{"slug":"attn-lowrank","status":"open","stage":"theory","human_gate":false,"rounds":2,"updated":"2026-09-16T12:00:00Z"}]}
```

`status ∈ open|closed|archived`；`stage ∈ initiation|theory|experiment|writing|review|done`；种子为 `{"projects":[]}`。

## 项目文件 `<slug>.md` 结构

头部四段（initiation 组定稿后闭笔）：

1. **问题背景** — pi（难点调研并入 pi）：成因/机制/现有方法何处失效，只提问不解答。
2. **前沿进展—同方向可借鉴设计** — pi 成文，librarian 供行锚：正文摘要 + 调查附件（指 `research/frontier-notes.md` 行号）。
3. **目的** — pi：observable 三成分句「在 <数据/环境> 上，用 <指标> 度量，达到 <数值或行为断言>」。
4. **最终验证依据** — pi：指标+阈值+数据切分写成一句可判真伪的命题。该命题成立即项目完成。

元数据行（头部之后）：`budget:`、`human_gate:`、`status:`、`conclude:` 段。

正文三段，段权=只增不改，revise 打回只许改本阶段段，落笔即在对应 `runs/<run-id>/run-log.md` 记一行：

- **假设段假设与理论论据** — speculator 主笔，theorist 补形式化小节（Lean 文件路径+陈述↔论据对照表）。
- **设计段实验设计与结果** — speculator 写设计，runner 填结果节，qa 核验。
- **结论段结论** — review 组：chair 判词指针 + 逐条回查「最终验证依据」回查表。

## 段内 schema（合格线，缺项即打回）

**假设（五字段）**：陈述句｜预测可观测量(指标+方向+阈值)｜作用范围(体系+数据)｜至少一个竞品假设｜区分性预测(各自预言什么不同读数)。缺预测可观测量=不合格。

**理论论据（四件套）**：机制因果链(每箭头一句)｜文献锚点(frontier-notes 行号)｜≥1 独立推论(可另测，非换皮重述)｜已知边界与反例。

**实验设计（六件套）**：因子矩阵｜对照与baseline(配置+种子+切分，缺切分=无效基线)｜测量协议(evaluation/ 命令原文)｜pass 判据(每 objective 一行 epsilon)｜资源预算与 45min 切片计划｜区分性表(哪两组读数分开 H 与竞品假设)。

**结果（只增五位）**：原始读数表(每数字后缀 measured/ 路径)｜终态断言对表(assertions.json)｜环境行(wall-time/峰值内存/therm)｜有效读数判定(无效格子点名+原因)｜delta vs baseline。

## 关口

- 开题审查（敌意对线）：examiner 持四类攻击（前提崩塌/已被做过/不可测/自相矛盾）与 pi 逐轮攻防，记 `debate.md`；弹药耗尽 `pass`（开工令→theorist），化解不了的实心攻击或致命实锤 `fail`（planner 归案）。攻击必带锚，无锚无效；轮数不设限。
- 中期检查：qa 备齐送审包 `packs/zhongqi.md`，chair+referee×3 合议 `continue|rectify|stop`；stop 凭实据（整改后攻击面未缩小、无可归因进展），不按轮数触发。
- 结题验收：qa 备齐送审包 `packs/jieti.md`（含设计段全部结果节+约束核验+断言对表），chair+referee×3 依结论段判 `accept|reject`；accept→planner 记档开新题。

## pi 交件自查（硬门）

前沿段每条可借鉴设计有行锚；目的句三成分齐；最终验证依据一句可判真伪；写不出 observable 目的的选题不提交。
