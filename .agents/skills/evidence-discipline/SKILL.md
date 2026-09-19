---
name: evidence-discipline
description: 证据与主张纪律。qa 出中期判词/放门前必载；speculator/theorist 落笔前自查，librarian 交引用件前自检，examiner 从此取弹药。管证据等级、断言-许可边界、引用核验阶梯、引用造假分型、数字保真、措辞档位、过程泄漏、入库门禁。用户提到证据纪律、断言对表、引用核验、造假冒充、越依据、措辞越权、hedge、入库门时使用。
---

# 证据与主张纪律

判词写法通例：每条依据 = 缺哪一档证据 + 哪一栏空 + 路径[:行锚]。不写语气评价，不写「建议加强论证」。

## ① 证据等级 L0–L4（定级先于落笔，不是写后标注）

| 等级 | 来源 | 能撑的口气 | 撑不住 |
|---|---|---|---|
| L1 | 全文 / 数据 / measured 实测 / 用户给的原始工件 | 任意主张，含方法细节与确切数字 | 无 |
| L2 | 摘要（用户给或检回） | 研究方向、标题性结论 | 具体数字、方法步骤、实现细节 |
| L3 | 元数据（标题/作者/年/venue） | 「X 等 (年) 就 Y 做了 Z」一句式 | 方法细节、性能数字、局限分析 |
| L0 | 领域常识 | 背景铺垫句 | 含数字/专名/量化比较的任何句子 |
| L4 | 模型记忆（只是「记得」） | **无** | **一切**：它不是证据，不得进证据表 |

- L0 判据两条：删掉这句论证是否变弱 + 这句不含任何数字/专名/量化比较。犹豫一下算不算常识＝不算，去查。
- Evidence Map（写前工作件，段落带引用即先定源）：`ID | 源（文件必须记 path[:行号/表名]）| 等级 | 支撑什么 | **撑不到哪儿（强制列）** | 计划用处 | 风险`。L3 行挂 `metadata-only`。无源主张在规划期就排除，不许写下来再补标签。
- 每条主张分 `Evidence basis`（原始支撑）/ `Interpretation`（更宽综合）两栏。主陈述口气封顶在 basis 直接支撑的最强档；只有指标表时不得升格为训练动态/优化质量的结论。
- 交付正文禁一切方括号占位（`citation needed`/`TBD`/`待作者补`）。缺源只有一条路：检索 → 试 2–3 个关键词变体 → 命中就织进真引用，未命中就改写句子把主张拿掉或整句删。真要人确认的事写在正文之后两三句白话里。
- 五类最易被编造的细节家族（用户没给就不写）：应用场景 / 机制与因果故事 / 量级与规模词 / 流程与实现细节（版本、日期、缺失率）/ 标识符（案号、标准号、arXiv ID）。通则：省略永远比合理的编造安全。

## ② 断言-许可表（加列不换表）

`| Results Unit | 检验的断言 ID | measured/ 路径 | 图表 | Confirmatory Condition | 授权结论句 | Interpretation NOT Allowed |`

- 前两列任一空 = 硬失败，不是提醒。每条贡献至少一行，缺行即「该主张没被测」。一个结果单元映不到任何断言 → 删（filler）或补进 Introduction（未宣告的贡献）。
- `Confirmatory Condition` 挂在断言行上（如「仅在该 held-out 切分 + 同 backbone + 同预算下成立」），条件不写=读者会自行放大。
- `Interpretation NOT Allowed` 强制非空：预先钉死这条读数不许写成什么，防 Discussion 静默放大。
- 与断言清单异轴：清单（泄漏/确定性/预算）管**读数可信**，终点 pass/fail；本表管**措辞不越权**，终点是两栏许可边界。两者并排进 `packs/结题送审包.md` 第①节，不合并。
- 行内 marker 到审计通过才许转成渲染引用：`[claim:C00x] [evidence:E00x]`（或 `[@Exxx]`）与被证句同行；主张台账存文本哈希不存原文；ID 命名空间隔离（skill 自述源 ≠ 稿件源 ≠ measured 读数）。
- 反向提纲是本表的廉价前置检查：主 claim → 每段主题句 → 段内证据点，逐条查两向挂载；挂不上的段落连同其证据一起改写或删除。

## ③ 引用核验阶梯（生成与复核分家）

- 为何必须独立：生成与复核是同一个认知动作、共享同一份错误；凭记忆写出「Smith et al. (2021) proposed X」的模型被要求重查时，只会再查一遍同一份记忆并自我确认。引用层恰是最机械可反验的一类（要么检得到要么检不到），所以只把这一层外包。
- Rung1 fresh-context verifier（首选）：干净上下文，输入只有带引用标的正文 + 参考文献表，**不得**给写作推理。Rung2 仍在同上下文，必须真检索：每条重导自检索响应，绝不重导自记忆，并在交付里说明它比 Rung1 弱。Rung3 无检索：只引用户提供的源，声明「未做独立核验」。纪律永不降级，只有机制降级，降级必须披露。
- 触发分档（互斥四档）：全文/多节稿或 Final → 必走（不论条数）；累计 ≥3 条引用 → 必走；≤2 条的短段 → 可跳，靠行内自查；零引用 → 不触发。阈值取 3，因为 Intro 与 Related Work 立刻越线。
- 每条两次核对：①存在性——至少三种查询式（整标题、作者+关键词+年份、核心关键词），逐字段比标题/作者/年/venue；②引用强度——回到引用句判 citation-level 还是 full-text-level，元数据撑不住数字即 OVERCLAIM。
- `not found` ≠ `could not search`：正常响应且三种查询式全零命中，算 NOT_FOUND；工具报错/超时/限流/系统性空响应 = INCONCLUSIVE。一次基础设施抖动绝不能删掉一条真引用。
- 五档判词：`VERIFIED`（留）/ `METADATA_MISMATCH`（按检索改正；检索后端自身与多源或常识矛盾时挂起交人，不盲信）/ `NOT_FOUND`（删引用连同它撑住的句子，或检索替换，不得留作事实）/ `OVERCLAIM`（降格为 citation-level 措辞）/ `INCONCLUSIVE`（重试，持续则挂起交人）。任何一档都不靠往正文插占位标签解决。
- 收敛条件＝**无未决条目**，不是「全 VERIFIED」：VERIFIED、改正、删除、降级为 citation-level、显式挂给用户，五选一即算已决。未决项只回改受影响句子再复验，不整篇重写。
- 主张忠实度另设一查（存在≠诚实）：逐条判 `SUPPORTED/UNSUPPORTED/AMBIGUOUS/RETRIEVAL_FAILED` + `defect_stage`；付费墙类稳定受限记 `failed`，超时/5xx 记 `audit_tool_failure`，两者不得合并；模糊优先 AMBIGUOUS，不硬判 UNSUPPORTED；绝不模拟检索、绝不谎称读过某篇。
- 诚实边界：抓不到「真引用背后的主张本身是错的」，也抓不到非引用类造假——那是①②⑤的活。

## ④ 引用造假五类 + 三铁律（qa 对表枚举）

| 码 | 型 | 占比 | 查法 |
|---|---|---|---|
| TF | 整条伪造 | ~28% | 标题+作者检不到 |
| PAC | 真学者挂假文 | ~23% | 查该作者真实发文列表 |
| IH | 索引幻觉 | ~19% | 缺 DOI/卷/页等可检字段即深查 |
| PH | 拼贴（多真件混一假） | ~18% | 全字段必须落在**同一篇**上 |
| SH | 语义/字段微改 | ~12% | 逐字段比出版方页 |

- 复合五型：作者冒充 / venue 借用 / 拼贴 / 时间遮蔽（作者话题对、年份或版次错）/ **DOI Misdirection**（DOI 解析到另一篇真文，假 DOI 中占 64%）。最便宜的一手检查先跑：打 DOI——404 即 DOI 本身错，200 则比对返回记录的标题/作者/卷期页。>20 条按 10–15 条一组并行分片。
- **A1 无不确定类**：每条必须落进五类之一或 VERIFIED，禁止「存疑/难以核验」灰区——一条拼贴假引用正是靠这句连逃三轮核验。
- **A2 强制审计轨迹**：逐条记查询串 + URL + 逐字段确认。无轨迹即 `NOT VERIFIED`，**报告本身无效**（不是「结论保守」，是无效件）。
- **A3 幽灵引用双向查**：文献表里的孤儿条目与正文里的悬空引用，两个方向都查。
- 抽样分档（两闸；源仓 Phase D「原文性/查重」档不搬——本仓无查重设施）：中期＝存在性全量 / 上下文 30% / 数据面全量 / 主张按风险分层（HIGH-IMPACT 全量 + 余下随机哨兵 10%，min3 max10，注册总数 <10 则全量）；结题＝上下文 100% / 数据面全量 / 主张全量，且**存在性闸全新重跑全量**——中期可能有漏，不得只复核中期改过的条目；全新重跑仍是同一份错误过程，别把它写成独立复核。
- 顺序硬约束：题录闸未出判词的条目不得进上下文闸；题录判 NOT_FOUND/MISMATCH 的条目直接 FAIL，不看后续。修正后只复验被改条目，最多 3 轮，仍不通过则点名交用户。

## ⑤ 数字保真

- raw/derived 命名铁律：表名声称原表（如 `table3_*`）就必须逐格还原原表题注与内容；只裁子集必须叫 `derived_`/`subset_` 并写明派生自谁；不得把不同原表的行混进同一文件冒充原表；先逐字转录原表再做摘要。`measured/` 里标题带 `summary`/`主结果` 的表必须写派生自哪个 raw 文件。
- 转写数值逐字照抄，不四舍五入、不取近似。
- 规划值与实测值分域：planning 数字只准待在标了 planning 的表/段里，永不进正文当结果。假设段与设计段的预期只准写方向性预期，确切数字只准出现在 `measured/`——防先有结论再编实验。
- Abstract 与 Experiments 的叙述句不得出现未经 `measured/` 支撑的确切数字；结论口气按①档位与⑥阶梯收敛。
- 每个数字入账必备：概念名、单位、分子/分母、分析人群与样本层级、时间点、不确定度、方法/结果 ID 与 evidence ID。缺件＝该数字不入账。
- 七态不得合并、缺失不得填 0：缺失 / 结构不存在 / 未检出 / 低于定量限 / 饱和 / 失败 / 真零各记各的，禁止自动插补；未知量记 `unavailable`（读数器 `environment.json` 的 `null` 与它同义，二者都是状态标记不是数值），绝不当实测 0 聚合（0 会假压有效读数率并误触 stop）。
- 计划值永远独立槽位：`budget_plan.*` 这类计划数不得占用实测槽；预算核验按「计划 / 实测 / 差」三列并排写，缺实测就空着，不许拿计划值顶。
- 数值自洽三律：标题性数字必须能从 Methods 推导；同一指标全篇一个精度并机械交叉核（不凭记忆）；两个不同量恰好同值必须分别命名。
- 正文/表/图互相矛盾：两处都记、不暗选、结论标不确定、并写明什么能消解它。
- 台账装 provenance，正文装科学：正文不得出现 audit 套话。`planned → verified` 的跃迁只能来自 `measured/` 实测，过 checker 不算已验。

## ⑥ 措辞档位（四档 + 受保护 hedge）

| 档 | 触发条件 | 英文 | 中文 |
|---|---|---|---|
| 强 | 多独立研究一致 / meta 分析 / 大规模验证 | demonstrate, establish, confirm | 表明、证实、确立 |
| 中 | 两三篇、条件有界 | suggest, indicate, be consistent with | 提示、与……一致 |
| 弱 | 一两篇，或纯机制论证 | may, appears to | 可能、似乎 |
| 无证据 | 检索后未见 | to our knowledge, no study has examined | 据检索结果，尚无研究考察过 |

- 三类失效：overclaim（`prove` 属于数学；无界 superlative；"the first/only/optimal" 未经彻底核实——正确写法是把范围钉住「在数据集 D 上评测过的方法中，本方法在度量 M 上分数最高」）/ underclaim（hedge 叠罗汉）/ 相关写成因果（无因果识别证据只准 `is associated with`）。另禁以术语密度冒充权威。
- 谓词强度另设门：`demonstrates necessity` 只在有有效干预或消融后允许；`causes` 只在设计支持因果推断时允许；未经外部核实的领域史必须冠 `[Paper-framed; external verification not performed]`；不得因作者自称 first/novel/SOTA 就照写。
- 强度阶梯：`is consistent with` < `is associated with` < `predicts` < `contributes to` < `affects` < `causes / demonstrates / proves`。修订轮里任何一次沿阶梯移动**两个方向都算**，须有一条授权（判词/整改单/任务书），禁止静默升降档。删情态 hedge、删范围限定语、删 null/负结果都算移动。
- 受保护 hedge 三类（删之即改真值承诺，字数压力下删属过度声明，定性为诚信故障而非文风问题）：界定主张的认识级限定（may / preliminary / exploratory / in our sample / under the conditions tested）、立场与角色披露、时间限定（写明年区间；`during this period` 这类指示语本身就是失效形态）。退单理由直接指档位差。
- 新颖性一律有界：绝对优先语断言的是文献**缺席**，任何被引源都撑不起它，引用闸在结构上抓不到这里的越权。默认写法 `To our knowledge, based on searches of [库] through [日期]`／「据对〈库〉截至〈日期〉的检索，未见……」，库名与日期取实际检索记录；缺检索执行日期则该主张记 `UNRESOLVED` 并附「记下 last_searched_at 才能解决」。永不输出「globally verified」式新颖性判决。

## ⑦ 第四面墙（过程泄漏）

- 与三约束的「泄漏」不同轴：那条是训练/评测切分隔离（数据泄漏），本条是稿子叙述自己的写作/评审史（过程泄漏）。两轴分开查，不得互相顶替。
- 读者可见文字里出现规划记号即 BLOCKER：`A → B → C` 式主线、「针对导师/审稿意见本文重新组织」「前期初稿缺少…」「为回应评审建议…」。
- 内容性分析箭链合法（`指代缺失 → 意图漂移 → 错误检索` 这类失效路径/数据流）。判据用**共现正则**（「导师+审阅意见」「本文+重新组织」），不用单词黑名单，避免误伤领域词（如「AI 导师系统」）。
- gates/ 判词、对线记录、整改单编号一律不进 papers/ 正文；要留痕写进 `run-log.md` / `revisions.md`。

## ⑧ 入库与放门清单（qa 向）

1. 结构先于语义：字段缺项直接退单，不进入语义判词。
2. 每条断言两栏许可齐（授权结论句 + NOT Allowed），缺任一栏不放门。
3. 引用层收敛＝无未决条目；A2 轨迹齐；孤儿/悬空双向为零。
4. 数值全部可回指 `measured/` 一个文件；derived 标派生源；缺失记 `unavailable` 而非 0。
5. 结论复用绑内容 hash（含路径）+ 工具版本/模型；版本或模型变更、或超期即全量重跑，不做增量抽验。
6. 先核文件清单再下判词：任何以「存在未披露代码/未披露材料」为前提的结论直接作废；发现先对码（对原文）再判。
7. 不完整的核验不算通过：降级源计数、付费墙跳过数与严重度总量一起复核；「部分放行」必须写成部分放行，不写全清。
8. 误报连同「判它误报的那次检查」一起留档，且允许后续轮推翻；误报登记不得自动抵扣后来的高危结论。
9. 不可达项显式记账并出现在输出里（禁静默 skip），对应送审包「本环境不可复现的部分」。
10. 覆盖检查双向：该有而没有要退，有而无来源（孤儿条目、陈旧断言行）也要清。
11. 沉默不是确认：他角色未回话不构成背书；无定位的意见只算咨询注记，不构成阻塞性 finding（降级，不丢弃）。

## Sources

逐条「机制 → 来源 → license 与处理」。状态/枚举英文字面量为脚本对账所用，一律原样直借，其余全为本仓中文重写。

- L0–L4 表 / Evidence Map 强制列 / 写前溯源 / basis-interp 分离 / 占位禁令 / 五类编造家族 / D0–D5 实验门 → Supervisor-Skills `skills/paper-writer/references/evidence-discipline.md:29-145` → CC BY-NC-SA 4.0：只搬机制，逐条重写。
- 独立核验阶梯（Rung1–3 / 触发分档 / not found vs could not search / 五档判词 / 收敛=无未决）→ Supervisor-Skills `skills/paper-writer/references/verification-ladder.md:20-152` → CC BY-NC-SA 4.0：只取方法，未复制文本。
- 措辞四档 + 三类失效 + 术语密度禁令 → Supervisor-Skills `skills/deep-research/references/hedge-calibration.md:1-62` → CC BY-NC-SA 4.0：改写。
- 造假五类 TF/PAC/IH/PH/SH + 复合五型（DOI Misdirection 64%、Walters 2023）+ 三铁律 + Stage 2.5/4.5 抽样与「存在性闸全新重跑」+ 3 轮修正上限 → academic-research-skills `skills/academic-pipeline/agents/integrity_verification_agent.md` → CC BY-NC 4.0：只搬机制；占比数是它引自外部文献的观测值，本仓当量级参考，不作判据。
- 主张忠实度四值判决 + `defect_stage` + 不模拟检索 → academic-research-skills `skills/academic-pipeline/agents/claim_ref_alignment_audit_agent.md:1-40` → CC BY-NC 4.0：改写。
- 强度阶梯 + 禁静默升降档 + 受保护 hedge 三类 → academic-research-skills `shared/references/claim_strength_ladder.md:20-60`、`shared/references/protected_hedging_phrases.md:1-60` → CC BY-NC 4.0：改写。
- 新颖性检索有界（`SUPPORTED_WITHIN_SEARCH`、缺 `last_searched_at` 退 `UNRESOLVED`）→ academic-research-skills `skills/academic-pipeline/references/claim_verification_protocol.md` E5 节 → CC BY-NC 4.0：改写。
- 断言-许可七列表 + `Interpretation NOT Allowed` + 每贡献至少一行 + 前两列空=硬失败 → PaperSpine `src/skill/references/results-validation.md` → MIT：改写并署名；本仓保留「可重跑」层（源仓无，它的 Result/Evidence 是手抄数）。
- 检索状态分离（`no_hit` 不是「不存在前作」、provider failure 是覆盖率降级、`unavailable` 不记 0、无定位只算咨询意见）→ PaperSpine `references/evidence-grounded-review.md` → MIT：改写并署名。
- 第四面墙 + 共现正则 + 台账/正文分工 → PaperSpine `references/writing-rationale-matrix.md`、`references/motivation-thread-writing.md:15-25`、`src/scripts/integrity_audit.py:357-414` → MIT：改写并署名。
- `[claim:C00x] [evidence:E00x]` 同行 marker + 哈希存主张 + ID 命名空间隔离 + 数字七件 → scientific-agent-skills `skills/scientific-writing/SKILL.md:124-140`、`references/evidence_workflow.md:34-44`、`references/source_ledger.md:10-11`、`references/writing_principles.md:46-61` → MIT：改写并署名。
- claim-evidence map 固定格式与「撑不住就弱化或删主张」→ Research-Paper-Writing-Skills `research-paper-writing/SKILL.md:88,92-99`；反向提纲六步 → 同仓 `references/does-my-writing-flow-source.md:19-29` → MIT：改写并署名。注：蒸馏笔记称 map 为「三态」，原仓实为三栏（Claim/Evidence/Status）、Status 只取 `supported/needs evidence` 两值，本条以原仓为准，未造第三值。
- raw/derived 逐格还原 + 转写不许约 + 设计文档禁确切数 + basis/interpretation → AI-Research-SKILLs `22-agent-native-research-artifact/compiler/SKILL.md:103,114-116,149-152,169-171,229-236` → MIT：改写并署名。
- 七态不合并 / 禁自动插补 → scientific-agent-skills `skills/exploratory-data-analysis/SKILL.md:135-151` → MIT：取两条，余属 runner 面。
- 三档 locator + 五标签溯源 + 谓词强度门 + 矛盾四步 → nature-skills `skills/nature-paper-card/references/evidence-and-provenance.md:7-94`、`skills/nature-paper-card/static/core/output-contract.md:47-62` → 根 Apache-2.0（该仓子包许可混杂，此两目录无独立 LICENSE，按根记）：只搬机制；`figures4papers/`（上游无 LICENSE）一字未取。
- DOI 先查 + 字段级三档 + 并行分片 → nature-skills `skills/nature-ref-verifier/SKILL.md:45-105` → Apache-2.0（同上口径）：改写。
- 入库门禁 1/5/6/7/8/9/10 → scientific-agent-skills `tests/_meta/test_repo_contract.py:72-115`、`AGENTS.md:224-229`、`docs/security-triage.md:3-28,91-92`、`tests/skill-requirements.toml:792-815`（经蒸馏笔记转录，本机未跟踪）→ MIT：改写；剔除 scanner、plugin manifest 等宿主机制。

## 与自家条款的接缝

- 断言清单（`research_project/<项目短名>.md` 设计段 objectives/constraints）是**唯一承诺面**：②表只加列不新增断言；新增断言或改阈值仍走 qa 退单 + `run-log.md` 记账。
- 三约束：⑤与「确定性」重叠，判据不同（约束判「同命令重跑同值」，本节判「数字被如实转述与限定到什么程度」），两票独立记；⑦与「泄漏」不同轴（见该节首条）；⑧第 5 条（复用绑 hash/超期重跑）落在「预算」之外，与既有预算条款冲突时以自家为准。
- 段权（头四段与判词只增不改）：①的写前溯源只约束新段落笔；已冻结段被发现越依据时，处置是追加更正行、在②表把旧行标 stale，不改写原文。
- 判词文件（`gates/中期判定.md`、`gates/结题判定*.md`）：退单理由必须指名 ⑥ 的档位差或 ② 的 `Interpretation NOT Allowed` 栏；referee 越依据 finding 仍按自家既有规则直判 stop 级，本 skill 不另设判决与阈值。
- `measured/` 与 `packs/`：⑤的派生命名与数字七件是 measured 行格式的补充字段；②表并入 packs 第①节右侧，不开新节。librarian 回件落 `research/frontier-notes.md` 行锚，按③④出判词，缺 A2 审计轨迹的行 qa 拒收。
- `paper-writing` 的「主张强度对齐证据」由本 skill ⑥ 提供可查词表与失效分类；examiner 的四类攻击中「不可测」「自相矛盾」的最低证据门槛由 ②③④ 供给弹药。
- 与兄弟 skill 的分工：`measured/environment.json` 与 `self_checks.json` 的键名以 `ml-runbook` 为准（本 skill 只定「什么才算一条有效证据」，不定字段表）；断言行字段（metric/evaluator/direction/epsilon/baseline）以 `experiment-design` 为准，②表只加许可两栏。
