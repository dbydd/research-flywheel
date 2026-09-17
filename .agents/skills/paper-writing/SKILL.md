---
name: paper-writing
description: 论文写作规范与 LaTeX 细则。writer 成稿、critic 文字审时加载：稿件骨架、主线映射与动笔前五问、反向提纲、段落四问、Method 三件套、反模式、文字审计（七锚点/七类缺陷/浅改比率）、修订三维台账、返修回复与 cover letter、LaTeX 排版雷区。用户提到写论文、改稿、润色、逐点回复、审稿文字面、LaTeX 格式时使用。
---

# 论文写作

细则来源：https://github.com/guanyingc/latex_paper_writing_tips 的 `paper_writing_tips.pdf`（Guanying Chen，CVPR/ECCV 实战总结），加本飞轮自家流程约定。外部蒸馏部件的逐条出处见文末 `## Sources`，一律改写成本飞轮口径，状态枚举保留英文原串。

## 稿件骨架（每节回答一个问题）

- Abstract：问题 → 方法一句话 → 最强结果带数字 → 意义。四到六句，零引用，零缩写未定义先用。
- Introduction：领域地位 → 缺口（现有方法哪里不行，引文献撑住）→ 我们做了什么 → 贡献列表（三条上下，每条可验证）→ 路线图段可选。
- Related Work：按技术线索分组叙述，每组收一句"与本文的关系"。按时间罗列流水账是拒稿常见理由。
- Method：符号先定义后用；一张总览图配数据流叙述；每小节对应一个组件。
- Experiments：先 setup（数据、指标、实现细节、硬件），后主结果，再消融。每张表/图正文必有指涉与结论句，数字与 `measured/` 一致。
- Conclusion：局限写诚实，future work 一句一个。

## 动笔前五问（倒序思考、正序写作）

- 倒序先答五问：①解决什么技术问题 ②**为什么没有成熟解法**（防「把已有做法当创新」的闸，最重要）③我们的技术贡献是什么 ④本质上为什么可行 ⑤给出的技术优势与新洞察是什么。
- 正序才落笔：任务 → 借前人方法引出我们要解决的那个挑战 → 贡献若干条 → 贡献的技术优势并明写洞察。
- Abstract 用同五问的压缩版，不另起一套问题集。五问答不上来 = 稿子还没到能动笔的时候，回设计段补。

## 主线映射：论证链 → 落笔段

- 论证链七格，逐格填一句：L1 在解什么任务 / L2 这个任务该看哪些指标 / L3 SOTA 达不到哪条指标 / L4 失败背后的根因技术问题 / L5 我们的解法与 pipeline / L6 为什么有效 / L7 附加贡献。
- 落笔段五格：R1 任务应用与目标指标 / R2 SOTA 失效与根因 / R3 我们的方案与为何有效 / R4 附加贡献与影响 / R5 实验。
- 两条硬判据：任一 R 段找不到对应 L 节点 = 空转段，删或改写；任一 L 节点没有 R 承接 = 漏讲，补段。
- 两张表随稿件存 `papers/<项目短名>/`，收包时按表点段；填不出表就不要开写。

## 反向提纲六步（交稿前自查，也是判词第一步）

六步：①写下主 claim ②写下每段主题句 ③写下每段内的证据/解释点 ④逐条查主题句是否挂到主 claim ⑤逐条查证据是否支撑本段主题句且**充分** ⑥挂不上的段落连同其证据一起改写或删除。

- 诊断尺：能轻松写出反向提纲说明组织得好；写不出来，说明主 claim 与主题句本身就不清楚。
- 产出三列可核对表（主 claim | 主题句 | 段内证据）进送审包；进不了表的段落 = 判词里的删除项。

## 段落四问（逐段返工的最小单元）

- 四问：①一段只承载一个信息 ②首句就说出本段要干什么 ③关键名词自足，新词先定义再复用 ④句与句之间必须有可指认的关系：因果 / 对比 / 推论 / 细化 / 举例，五类之外不算关系。
- 四问任一未过即整段重写，不做句级打磨。「一段塞多信息」是中文稿件通病。

## Method 三件套（先设计后回填）

- 动笔前枚举模块，每模块答三问并先整理成表：怎么跑 / 为何需要 / **为何有效**。「为何有效」不许空着开写。
- 写作顺序：画 pipeline 草图 → 用草图切小节 → 每小节规划动机·设计·技术优势 → **先写模块设计搭骨架，再回填动机与优势**（避免先抒情后技术）。
- 模块设计分两半：数据结构（`We represent ... with ...`）与前向过程（`Given [input], we first ... then ... finally ...`，严格按执行顺序），末句落到输出解释。
- 技术优势尽可能挂到可测行为上；挂不上的记为待测，进断言清单，不进正文当结论。
- 三级自检：逻辑级（写完把 Method 的写作逻辑重新摘要一遍看顺不顺）/ 段落级（首句即可懂、一段一信息）/ 句子级（每句动机显式：读者任何时刻都要清楚「为什么需要这句话」；句间流、术语一致）。

## 反模式四条（命中即退单）

- 禁「先摆朴素方案再改它」：不要先给一个 naive 解法再写我们的改进，**工作确实是增量式的也不要这样写**。理由：抹掉读者好奇心，让想法显得「理所当然」，把工作读成低分补丁。
- 禁 Intro 只讲抽象洞察、藏起具体设计：把**步骤**写成新的，**真洞察**没写成新的；引入大量新词，机制不讲 = novelty illusion，审稿人读成浅/增量。
- 禁 Related Work 堆引文 / 藏最强 baseline：先列直接竞品与近年 baseline，按技术主题分组不按年份；差异必须用技术语（机制、假设、失效模式），营销语不算。
- 禁把技术缺陷写成范围限制，也禁把可修瑕疵当结论主题：Technical defect = 关键指标不及强 baseline，或带来不可接受的权衡；Scope limitation = 受当前任务边界约束；边界内在当前 SOTA 里仍有竞争力。结论只围绕后者；判词里「这是局限」与「这是缺陷」按此二分，不许互替。

## 文字审计三件（referee 文字席与文稿合规核）

- 七锚点血缘测试：抽出七句原文，只读这七句：①Abstract 动机句 ②Introduction 首个问题句 ③主 gap 句 ④Intro 末条贡献/路线图句 ⑤Methods 首个 rationale 句 ⑥Results 首条 headline finding ⑦Discussion 首条回答句。七句应自己构成一条连贯的 problem→solution→evidence→resolution 弧；弧断在哪个锚点就去改对应节的设计，**先别打磨语言**。锚点定位天然满足「攻击必锚到段+句+证据，无锚无效」。
- 七类缺陷命名（finding 共享词表，便于合议聚类）：`background-stack`（背景罗列不收口到必要性）/ `gap-vague`（gap 存在、不可测）/ `method-recipe`（只列部件不讲设计需要）/ `metric-dump`（报数不解释它在测哪条承诺）/ `claim-leap`（解读超出证据）/ `discussion-repeat`（Discussion 复述 Results 不解动机）/ `latex-driven`（改版式不动论证）。
- 浅改比率审计：收文字整改单回件、结题修订回件时，对上一版与本版做归一化（tex/md）后逐段最相似比对，记 `near_identical_ratio`（保旧文太多）/ `addition_heavy`（以追加为主）两项进台账；两项同高 = 本轮无实质修订，退回。配套四条警告各记 Observed?/Evidence/Required Fix：段落顺序未变只做句级打磨、无证据库支撑的新主张、Results 仍是 metric-dump、排版工作挤掉了写作逻辑。

## 修订三维台账（替旧「稿件头部一行修订记录」）

- 一件修订一行，落 `research_project/<项目短名>/revisions.md`，追加式只增不改；行首键 = `gates/` 判词里的 finding 编号（`中期判定.md`、`结题判定.md`、`结题判定-评审<甲|乙|丙>.md`）。
- 三条正交轴各占一列，不许互相代填：
  - `action`（回应方式）：`ACCEPT_TEXT` / `ACCEPT_ANALYSIS` / `ACCEPT_EXPERIMENT` / `ACCEPT_FIGURE` / `CLARIFY_EXISTING` / `ADD_CITATION` / `SOFTEN_CLAIM` / `PARTIAL` / `DISAGREE` / `OUT_OF_SCOPE` / `AUTHOR_INPUT_NEEDED` / `BLOCKING`。
  - `work_status`（进度与可核验性）：`VERIFIED_DONE` / `REPORTED_DONE_UNVERIFIED` / `TODO_TEXT` / `TODO_ANALYSIS` / `TODO_EXPERIMENT` / `TODO_AUTHOR_CONFIRM` / `NOT_FEASIBLE` / `PROPOSED_DISAGREEMENT`。
  - `readiness`（整包）：`ready_to_submit` / `draft_with_placeholders` / `needs_author_input` / `blocked`。
- 每行另带四个控制字段：`required_input` / `expected_output` / `verification_evidence` / `blocks_finalization`。
- 完成红线：有可查验工件（稿面 diff、新文件、`measured/` 路径）才准 `VERIFIED_DONE`；责任角色只口头说「改完了」→ `REPORTED_DONE_UNVERIFIED`；说加了实验、没给工件 → 同样永远不给 `VERIFIED_DONE`。草稿回复存在不是手稿已改的证据。
- `ready_to_submit` 保守推导：零 `blocks_finalization`、零未解占位、所有已完成项皆 `VERIFIED_DONE` 三者齐才成立；任一行处于 `TODO_AUTHOR_CONFIRM` 或 `REPORTED_DONE_UNVERIFIED`，整包至多 `needs_author_input`。
- 轴义分明：`action` 说回应策略，`work_status` 报进度与核验状态，两者不得互相代填。台账过宽放不下时改成逐条块状，字段一个不减，尤其不得丢掉 `work_status`、`expected_output`、`blocks_finalization`。
- 稿件头部只放一行指向 `revisions.md` 对应行的锚，不再逐轮堆修订散文。

## 返修回复与 cover letter 结构（minor revise 回件用）

- 出件顺序：内部策略摘要（标注 not reviewer-facing）→ 逐条台账（上节字段）→ 每席独立逐点回复 → cover letter（被点名或交齐包时才写）→ 标红改动段 → 交付清单与缺料点名。
- 逐点回复一份一席：`**评审意见**`（原话全引，不改写）→ `**回复**`（先直接答，再写「为此我们做了 X，见 节/页/行/图表号」）→ `**修改后的正文**`（引修改段原文，与稿源逐字一致）。本席之外的事不出现在本席文件里：不提别的席位、不引别的席的意见或编号；同一 concern 多席提出，各文件重复完整回答。
- 对外文件用本地中性编号（`Comment 1`、`E.1` 给程序性指令），不泄内部 finding 全局编号；跨席重复与冲突只记在内部台账。
- cover letter 短于逐点回复，四段：致谢 + 稿件号 → 本轮三件主要改动 → 各化解了哪三条主 concern → 指向逐点回复与「现稿更清楚、更有支撑」。
- 引文即承诺：回复里每段引文必须逐字出现在展开后的手稿源里；正文删了一行，回查信里是否还在描述它（删除有涟漪）。禁写「新增两句/三条新文献」这类会过期的计数，改写成「下面引用的这段」。
- 标红必须有基线：基线是归档的上一版源文件，不是「感觉新」。为省事复述**已有**文字时，用另一种不标红的样式并在信首声明，用同款标红样式即失真。

## 样例格式（本 skill 的条款载体）

- 每条写作规程配两件：填空骨架（`We represent ... with ...` 一类句位，中英双注，便于直接落英文稿）+ 一个带逐段角色标签的实例。
- 实例只写骨架与角色标签（`Module design: data structure` / `Module design: forward process` / `Motivation of this module` / `Technical advantages`），正文用本项目语言。
- 不抄已发表论文正文，不整段搬第三方样例；复用的是句逻辑不是措辞；引用外部样例时给原论文题录。

## 措辞纪律

- 主张强度对齐证据：消融只涨 0.1 就不能写 `significantly outperforms`；`state-of-the-art` 要有对照表撑。
- 全篇时态一致：描述已有工作现在时/过去时二选一，本文实验结果过去时或现在时择一。
- 每个数字出现处，critic 都能指回 `measured/` 一个文件；指不回去的数字删掉。
- 图表未引用的先删，引用的先补指涉句。
- 限定语（hedge）不许在字数压力下删：删 hedge 是诚信故障，不是文风问题；词表与判定归 `evidence-discipline`（hedge 校准节）。
- 过程泄漏（第四面墙）：读者可见文字里不出现写作/评审史与规划记号（「为回应评审建议…」「前期初稿缺少…」）；正则表与正本条款归 `evidence-discipline`，本处只留禁令。

## LaTeX 排版雷区（PDF §2 逐条）

标点与空格：
- 左括号前留空格：`network (CNN)`，贴写算错。
- 句号、逗号前不留空格。
- 引用前留空格：`problem [1]`。
- 公式末尾要有标点（句子的一部分），全部公式编号，交叉引用才有着落。
- 双引号用 `` `` `` 和 `''`，直引号 `"` 排版出来是错字。
- 句首大写。

引用与指涉：
- Abstract 不放引用。
- 表格指涉永远写全 `Table 1`，句子里 `Tab. 1` 算错。
- 图指涉：句首 `Figure 1`，句中 `Fig. 1`。`Fig.1` 缺空格算错。
- 表题在表上方，图题在图下方。浮动体尽量放页面顶部。
- 高频词定义宏：`\newcommand{\NetName}{...}`，改名一处改完。
- `i.e.`/`e.g.` 用 `\ie`/`\eg` 宏（防句读错断、防换行断坏）。

## 流程约定（本飞轮）

- 成稿目录 `papers/<项目短名>/`：`main.tex`（NeurIPS 2024 风格，模板 `papers/_template/neurips2024/`）+ `refs.bib` + `figs/`，编译出 `main.pdf`。草稿与中间件先落 role ws 的 `work/`（私有、不入 git），定稿一次性发布到 root 路径，并在 `research_project/<项目短名>/run-log.md` 记一行本地→发布映射。
- 每轮修订记进 `research_project/<项目短名>/revisions.md` 的三维台账（键为 `gates/` finding 编号）；critic 打回的文字问题逐条改，逐条把 `work_status` 推到 `VERIFIED_DONE` 并填 `verification_evidence` 销账。
- scribe 挂起中：`papers/` 文稿由责任角色自书（结题整改期的文字整改归 speculator，送审包由 qa 自书），本 skill 是它们的下笔规范。

## Sources

- 动笔前五问 → Research-Paper-Writing-Skills/`references/introduction.md:50-65` + `references/abstract.md:11-19` → MIT，改写为五问 + 正序落笔序。
- 主线映射 L1–L7/R1–R5 → 同上仓库 `references/introduction.md:11-48` → MIT，双列投影图改写成两张表 + 两条硬判据。
- 反向提纲六步 → 同上 `references/does-my-writing-flow-source.md:19-29` → MIT，六步与诊断尺改写；判词挂载点为本仓自定。
- 段落四问 → 同上 `SKILL.md:21-31,33-48` → MIT，四类句间关系词保留。
- Method 三件套与三级自检 → 同上 `references/method.md:11-61,82-100,116-133` → MIT，改写为顺序规程；原仓「写作常见病」断链占位未搬，按 `method.md:116-133` 自建。
- 反模式四条 → 同上 `references/introduction.md:177-182,376-381`、`references/related-work.md:29-34`、`references/conclusion.md:25-28` → MIT，改写；`Version 1/2/3` 编号命名不采用。
- 样例双联格式（骨架 + 逐段角色标签）→ 同上 `references/examples/method/*` → MIT，只取骨架与标签；原仓所抄 Neural Body/Instant-NGP 等论文正文属第三方版权，一字未取。
- 修订三维台账（`action` × `work_status` × `readiness` 与 `REPORTED_DONE_UNVERIFIED` 等枚举）→ nature-skills/`skills/nature-response/references/action-mapping.md:19-31,65-75,93-105` + `static/core/stance.md:38-39` → 根 Apache-2.0（该子技能无独立许可），机制改写、枚举原样保留英文；作者/评审人称谓改成本飞轮的责任角色与 `gates/` finding。
- 返修回复与 cover letter 结构、耦合工件涟漪检查 → nature-skills/`skills/nature-response/references/response-structure.md`、`package-consistency-audit.md:23-32,70-85,87-92,105-112` → 根 Apache-2.0，结构直借并改写措辞；期刊专属字段（manuscript ID、journal name）按投稿场景自填。
- 七锚点血缘 + 七类缺陷命名 + 浅改六警告 → PaperSpine/`src/skill/references/logic-transfer-audit.md`（`### 4`、`### 1`、`## Shallow Patch Check`）→ MIT，改写并挂到本飞轮 referee 文字席；attribution：PaperSpine contributors。
- `near_identical_ratio` / `addition_heavy` 比率口径 → PaperSpine/`src/scripts/revision_audit.py` + `references/rewrite-matrix.md:Step 8` → MIT，只搬口径与判据，脚本不搬。
- 第四面墙（过程泄漏）与 protected hedges → 分别见 PaperSpine/`references/writing-rationale-matrix.md`、academic-research-skills/`shared/references/protected_hedging_phrases.md` → MIT / CC BY-NC 4.0 → 本文件只留一句禁令与指针，正本归 `evidence-discipline`，未复制其条文与词表。
- 原有骨架/LaTeX/表格条款 → guanyingc/latex_paper_writing_tips `paper_writing_tips.pdf`（保留原出处行）。

## 与自家条款的接缝

- 解释文八条（仓根 AGENTS.md）优先于本文件任何措辞与样例取向：结论先行、直接陈述、禁转折修辞、术语按依赖序展开、数字带单位与出处。冲突时以八条为准，本文件只补细则。
- 数字只从 `research_project/<项目短名>/measured/` 引；正文任何数字都要指回一个文件，指不回即删。禁伪造 `measured/` 数值（禁区四条）。预算类数字按「计划 / 实测 / 差」三列口径落表（键名与分列规则正本在 `ml-runbook`），计划值不得在稿中呈现为已观察证据。
- 段权：`research_project/<项目短名>.md` 头四段与 `gates/` 判词、台账只增不改；`papers/` 稿件不受只增不改约束（整段重写合法，git 历史承担冻结），浅改比率审计就是为补「改得有实质」这一面。
- finding 编号正本在 `gates/`（判词、意见书），本文件的台账只是按编号回销；放门与结题判据走断言清单三约束（泄漏 / 确定性 / 预算），本文件不新增关口，也不给分数。
- 覆盖类检查（主 claim ≤ 验证实验数、模块 ≤ 消融数）归 `experiment-design`；引用核验、hedge 校准、过程泄漏正则归 `evidence-discipline`；约稿与合议规程归 `review-discipline`。
- `papers/` 挂起期由责任角色自书：成稿与文字整改是 speculator，送审包是 qa，referee 不用代笔（意见书独立性条款）。本 skill 在挂起期照常是下笔规范，落点目录仍是 `papers/<项目短名>/`。
