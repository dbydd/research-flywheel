---
name: review-discipline
description: 评审关口纪律。chair 约稿与合议、referee 独立意见书、examiner 敌意对线、qa 中期判词与放门时加载：盲段承诺与符合性检查、意见书三节、concern 账本、非补偿合议、评审红线、断言类型→证据形状硬表。用户提到审稿纪律、约稿、合议、非补偿、concern 账本、评审包冻结、拒稿信号、判词格式、评审档位时使用。
---

# 评审纪律

服务四方：referee 独立意见书 → chair 合议判词；examiner 开题对线；qa 中期判词与放门。关口五步规程与判词文件格式以仓根 `AGENTS.md` 为准，本文件只管评审纪律面。

## ① 约稿与盲段纪律（先立约后看稿）

- 约稿任务书按仓根只含两样：送审包路径 + 席位号。零倾向语句——对稿件好坏的任何措辞都不许出现；referee 亦不回问倾向，材料说话。轴面透镜是 chair 的可选程序面：要在约稿前定死并写进任务书，须先按仓根改动流程扩该条；未扩时三席读同一份准则、各自声明 `applicability` 与排除项。
- 轴面透镜是工作透镜不是人设：允许「技术失效面 / 原创与重要性面 / 跨读者可读性面」三档。禁止造身份（「统计学审稿人」「资深临床肿瘤学家」），禁止写入资历、地域、机构、与领域的私人关系；席位人设不出现在意见书正文。
- 承诺先行：读稿前先落「判据承诺」节，每面四行 `看什么 / 什么触发 reject / 什么触发 revise / 什么触发 accept`，四串两两互异；只依据任务书信封字段（题目、包路径、席位号、字数）。此节即本席标尺，标尺不因见稿而换。
- 字节子串符合性：见稿后每条批评必须带回它所属承诺行的逐字子串（`trigger:` 串）。带不回 = 读完稿再回头合理化标准，该条无效：删除，或另立承诺行、下一轮生效。单次见稿调用最多改一面的承诺；改两面以上 = 本席作废，退回重写承诺节。
- 盲段自证：承诺节里不得出现送审包正文的连续 12 词片段（whitespace 归一 + 大小写折叠后做字面搜索）。命中即该席承诺节判无效；唯一豁免是同一片段同时出现在任务书信封字段值里。豁免只由本条检查定义，不留解释余地。
- 派发形状：单上下文里"一人模拟整面板"已被证实会把稿件内容漏进"盲"的承诺节，属无效测量条件。每席各自独立 session，盲段落笔前不接触稿件；一席失败不拖别席。
- 见稿后的调用不重试（读过稿的第二次调用已被污染）。承诺节可重试一次，二次失败本席作废，不代填。

## ② 意见书三节结构（落 `gates/结题判定-评审<甲|乙|丙>.md`）

三节固定，与仓根结题规程同构；禁止追加共识/overlap/综合节——那是 chair 的活。

1. 依据逐条核对：对照 `<项目短名>.md` 头四段「最终验证依据」，每条 `hit / miss` + 依据路径（`measured/` 文件或送审包节号）。
2. 四类攻击点：前提崩塌 / 已被做过 / 不可测 / 自相矛盾，每条带锚（段+句+证据路径）。无锚无效，不发。
3. 建议档位：`accept / minor revise / reject` + 一段理由。越依据的 finding 直接标 reject 级。

逐条 finding 的写法：
- 指认"在场"的问题必须逐字引子串（`evidence_span`）；只有关于"缺席"的判断才可免引，且必须写查证范围（查过哪几节、哪几个 `measured/` 文件）。
- prose 互证不算支撑：支撑只能走 断言 → `measured/` 路径。"文稿三处都这么写"不是证据。
- 措辞：写「可能质疑分析把错误的独立单元当作 n」，不写「这是假显著性 / 作者操纵」。未拿到原始材料只准 `not assessable / potential risk / requires author confirmation`。
- severity 看对中央结论的影响，不看语气、难度、成本、口味：`major+blocking`（现证据撑不起中央结论）/ `major+non-blocking`（实质削弱但不废全案）/ `minor`（局部，不改中央解释）。缺细节只有阻断中央结果复现时才算 major；图与统计问题不天然 minor；写作歧义改变主 claim 才算 major。
- 空档写 `None identified from the supplied material`。绝不为配额、为"看起来认真"造意见。
- 只列问题的意见书不是好意见书：附一行「站得住之处」。此项不抵依据逐条的缺项。

## ③ concern 账本（席位私有，11 字段）

| 字段 | 含义 | 约束 |
|---|---|---|
| `issue_key` | 归一化键 | 席位本地，专供事后判重 |
| `axis` | 主轴一选 | `novelty-significance / mechanism-evidence / experimental-design / statistical-rigor / reproducibility / clinical-validity / ethical-governance / data-resource-quality / figures-and-tables / writing-clarity / claim-moderation / causal-vs-correlative` |
| `applicability` | `applicable / not applicable / not assessable` | `not assessable` 不得当成缺陷 |
| `severity` | `major / minor` | 只按对中央结论的影响定档，赋号后不改 |
| `blocking` | `yes / no` | 只有 major 可 `yes`；minor 恒 `no` |
| `severity_rationale` | 一句话：对本案中央结论的影响 | |
| `claim_pointer` | 被质疑主张的忠实单句转述 | 不是引文 |
| `evidence_pointer` | 节标题/表号/图号等可核位置 | 核不上写 `location not provided`，绝不编位置 |
| `evidence_status` | `located / location_missing / not_assessable` | |
| `concern` | 可见证据为何尚不支撑 | |
| `resolution_test` | 什么证据/分析/澄清/claim 收窄能关掉它 | 必填；缺此栏本条无效 |

席位号由文件名承载，不入账。意见分型九类：`misunderstanding / evidence_gap / novelty / baseline_fairness / scope_claim / writing_clarity / theory / efficiency / other`，逐条记化解去向（补证据 / 改措辞 / 收 claim / 换基线 / 文字澄清 / 越界不办），去向表交 chair 归案。Weakness 与 Question 分开：W 必须给证据+行动，Q 只答 2–4 句并给节/表指针——常见错法是 Q 过度解释、W 只解释不行动。

账本与包的纪律：
- 不可变评审包（chair 供件）：必放 = 送审包与项目文件原文、已核实锚点、评估边界与缺件清单、共同准则与报告骨架、本席轴面透镜；禁放 = 别席意见书或账本、已抽出的 concern 清单、共享的 claim-evidence 解读、任何 overlap/consensus/综合提示。
- 账本私有：别席不得读本席账本；对外只出示意见书正文里可追溯的字段。
- 冻结不回灌：意见书落盘即冻结。chair 综合阶段绝不回灌给任何 referee；以"换个角度/再补差异"为由退回复核即违此条。
- 自然的重复与分歧本身就是独立性的证据。事后只做描述性 overlap 统计（几席独立提出同一底层关切），严禁为凑重复率或凑多样性增删改 concern 或改分配。
- 共识门槛：≥2 席独立提出同一底层关切才叫共识条目；单席关切照留，按准则与锚定证据评估，不因缺共识而丢。

## ④ 合议规则（非补偿四则）

- 则一 拆后计数：复合意见先拆原子子主张再数——四席各说"部分支持"被当成多数支持，是合议里最大宗的正确性错误。只拆席位真说过的；chair 绝不代造新条。
- 则二 分母恒为 4：referee 三席 + chair 执笔席。缺席、撤回、未表态都不从分母扣；`not-mentioned` 既不是同意也不是反对，不得升格为同意；一席独提是 1/4 条目，不是共识。
- 则三 冲突压多数：任一子主张上 `conflict ≥ 1` → `SPLIT`，优先级高过所有多数标签（3 同意 1 反对是 SPLIT，不是带脚注的 CONSENSUS-3）。SPLIT 由 chair 逐条仲裁并给 binding 结论；作者收到的是仲裁后的结论，不是原始分歧。
- 则四 敌意条目独立追踪：examiner 未销的实心攻击与 qa 的无效读数/stop 记录，在本环承担 `DA-CRITICAL` 的角色。它们不进 4 席计数，但每条必须进判词，带四样：论点、有无席位附议、chair 效力评估、要求的整改。VALIDATED 或未决者阻断沉默 Accept——判 accept 必须逐条写化解依据。chair 驳回某条须写理由：未获支持的负面主张与正面主张承担同等证据负担。
- 不加权：意见书里的自评信心（1-5 或任何标尺）只是不确定性申报，永不用于求和、平均、投票、排除条目。高信心绝不压过低信心的相反意见，低信心的条目绝不在账上消失。
- severity 只搬运不重推：chair 引用席位档位，绝不静默改档；要改档另开一条并给依据。
- 衔接自家条款：判词与多数意见书建议相悖时判词必须写理由（仓根规程 ④）。则二说明"多数本身不是判据"，写理由是最低义务，不是把多数当默认答案。
- 收敛判据是"无未决"，不是"全绿"：仍有未解 `blocking: yes` 时不许写 accept/ready 级措辞；一屏 minor 而漏掉唯一致命问题 = 给飞轮假信心，把口味抬成 CRITICAL = 摧毁信任，两头都算判词失效。

## ⑤ 评审红线

- 门的性质：程序核验只验声明、不验真伪——`It validates declarations, not their truth.` 六节齐 + 抽跑一致只支持"申报完整且自洽"这句，绝不写成"内容已核实为真"。真伪归 referee/qa 的锚定证据与当场重跑。
- 代理指标禁令：IF 与刊级指标、h 指数、发文与引用数、altmetrics、期刊/会议/机构/地域声望、作者职衔与人脉，一律不作质量证据；判据里出现即无效，删。描述性提及必须同时记：用途、来源、覆盖、领域与时间效应、不确定、缺失、可被博弈的风险、它为何不直接度量质量。绝不把指标塞进不透明综合分。
- 人事打分禁令：评审面绝不产出招聘、晋升、tenure、录取、经费、奖项、处分类结论；不给人排名；不把人化约为综合分；有人签字不解除此禁令。planner 派题触及对人的评价即触线，改出「只对该作品的发展性意见」或「只走程序面审计」。
- 弃 0-100：判据档绑准则，不换算点数、不加权、不求和、不出百分比、不做潜排序，绝不把总分或标签计数机械映射到 `accept / minor revise / reject`。校准状态默认 `NOT_CALIBRATED`；没有与当前域、文型、准则版本、席位配置匹配且可重放的实测剖面，不许写"已校准"；也绝不声称档位在跨项目、跨 session、跨模型版本上一致。
- 每面必须写档位锚定句（最高档/中间档/最低档各自"长什么样"的可观察描述），禁止只有档位名。校准句：像样的产物本该落中间档，最高档是"确实出色"而不是"没挑出错"；挑不出错先回 ⑥ 复核证据形状齐不齐。
- 未检到 ≠ 假、≠ 新颖：`not_found` 只能报成「在这些关键词下未检到直接重叠工作」。`missing` 与 `not_applicable` 不得编码为 0、不得合并。
- 席位不越权：referee 的档位是建议，判词与结论段归 chair；referee 不得写"已结题 / 应归档 / 转下一步"。chair 不得代 referee 出意见，也不得代其拆条造新关切。
- 私密边界：未结题稿件、送审包、评审材料不外传，这是「泄漏」约束的外部形态。

## ⑥ 断言类型 → 证据形状硬表

| 断言类型（措辞线索） | 必需证据形状 | 缺形状的判词用语 |
|---|---|---|
| 因果 `causes / leads to / enables / is driven by` | 隔离消融或干预：remove / replace / disable 变体 + 对完整模型的 delta；模块耦合处做交互消融 | 「因果断言缺隔离消融」 |
| 泛化 `robust / across / generalizes / 任意·所有` | 异构测试条件：不同数据集、规模、域、种子，各自独立 | 「泛化断言只有同分布单条件」 |
| 改进 `outperforms / better / improves` | 公平协议下的强且近年基线：同 split、同预处理、同评估设置 | 「改进断言缺同协议强基线」 |
| 描述 `accounts for / pattern / distribution` | 代表性采样或全量枚举 + 采样口径声明 | 「描述断言未声明采样代表性」 |
| 定界 `when / under conditions / limited to` | 边界声明 + 边界外的失效例 | 「定界断言未给边界与失效例」 |

用法：结论段与送审包每条断言先归类、再问形状在场否。缺形状是 referee「不可测 / 自相矛盾」席位的实心弹药，属证据问题不是措辞问题。范围校核双向：过 claim（写 `all models` 而证据只覆盖窄条件）与 under-claim（`measured/` 有结果没被任何断言收走）都各记一条。

可伪证三判（「不可测」攻击的判据）：可操作性——独立复研者能跑，测什么、阈值多少、什么条件下三样齐；非重言——「方法不 work 就错了」算零分，「在同一批 77 篇上重评且名次不再居首」才算；范围匹配 + 独立性——检验式覆盖的范围与主张一致，且不依赖作者私有数据或系统。

拒稿五面（席位分工与攻击面枚举，不打分）：①贡献不足（目标失效例太常见 / 所用技术已被充分探索、增益可预期）②写作不清（缺技术细节不可复现 / 模块无明确动机）③效果弱（仅边际提升 / 赢了但绝对性能仍不够强）④评估不全（缺消融 / 缺重要基线或指标 / 数据集太简单）⑤方法设计有问题（setting 不真实 / 有技术缺陷 / 靠逐场景调参才稳 / 新设计的限制超过收益，净值为负）。chair 若启用分面：甲管贡献+方法设计、乙管写作+图表、丙管效果+评估完整性，同面不重复占席；未启用（缺省）则三席读同一准则、各自声明 `applicability`，席间重复照 ③ 只做描述性统计。

可查落点：形状在场否只看 `measured/` 文件——断言行取 `measured/assertions.json`（字段定义归 experiment-design），环境、切片与探针自检取 `measured/environment.json` 与 `measured/self_checks.json`（键名归 ml-runbook）。本文件不定义任何字段名。

三值标记：每条核对问句标 `pass / needs revision / needs new experiment`，对应自家三去向——入账 / 整改单（只动文字与结构、数据断言原样）/ 放门前补实验（qa 直发 runner，走断言清单与三约束）。qa 判词循环体：按怀疑者通读 → 每问只用论文内证据作答 → 标记 → 改主张或缩范围 → 反复直到无主要拒稿风险。接收三条作合议议程口径：贡献足量、公平对照下经验性能优于近年强基线、比较与消融足量；任一不满足记一条未决，不许用别面高分抵消。

## Sources

- 承诺先行 + 字节子串符合性 + 12 词 shingle + 见稿不重试 → academic-research-skills `academic-paper-reviewer/references/sprint_contract_protocol.md:18,25-36,68,89-95`、`docs/design/2026-07-25-574-spec-a-role-scoped-scoring-decision-contract-spec.md:694-697`、`evals/heldout/reviewer_seeded_defects/README.md:64-71` → CC BY-NC 4.0，只搬机制、全篇改写、已修改。
- 非补偿合议（拆子主张 / 分母 4 / 未提及≠同意 / SPLIT 压多数 / DA-CRITICAL 独立追踪 / confidence 不加权 / severity 只搬运）+ 弃 0-100 与 `NOT_CALIBRATED` → 同仓 `academic-paper-reviewer/agents/editorial_synthesizer_agent.md:106-200`、`references/quality_rubrics.md:11-21,36-38,76` → CC BY-NC 4.0，改写；枚举英文字面量直借。
- 不可变评审包 + emphasis brief 先定 + 冻结不回灌 + 不为多样性编辑 + 禁造人设 → nature-skills `skills/nature-reviewer/references/reviewer-workflow.md:17-33,51-64,91-97`、`role-boundaries.md:5-10,14-29,45-47`、`qa-checklist.md:82-87` → 该子包无独立 LICENSE，受根 Apache-2.0 约束，改写并署出处。注：三互盲与 12 轴是该仓实现选择，不是 Nature 官方准则（`source-basis.md:62-85`），本文件同此标注。
- concern 账本 11 字段 + `resolution_test` + 三态 applicability + severity/blocking 校准 + 空档句 → nature-skills `technical-concern-taxonomy.md:22-69`、`report-structure.md:57-88` → Apache-2.0，改写。
- 断言类型→证据形状硬表 + 逐字 `evidence_span` + 可伪证三判 + 中间档校准句 + 「prose 互证不算证据」 → AI-Research-SKILLs `22-agent-native-research-artifact/rigor-reviewer/SKILL.md:31-44,97-135,302-316` → MIT，改写；其数值判级映射（`SKILL.md:227-238`）与弃 0-100 冲突，不迁。
- 拒稿五面 + 接收三条 + 三值标记 → Research-Paper-Writing-Skills `research-paper-writing/references/paper-review.md:11-34,80-86` → MIT，改写并署名（方法论底本为彭思达公开笔记，见其 `README.md:5-11` 归属声明）。
- 「只验声明不验真伪」 → scientific-agent-skills `skills/peer-review/SKILL.md:54-75` → MIT，字面量直借。
- 代理指标与人事打分禁令 + `missing`/`not_applicable` 不得编码为 0 → scientific-agent-skills `skills/scholar-evaluation/SKILL.md:27-44,63-78,158-165` → MIT，改写；其"不下 accept/reject 判断"限于 rubric 认证语境，与本环 referee 档位不同轴。
- 七信号分型（只借结构）+ concern 九分类 + severity honesty 双向 + "无未决"收敛 → Supervisor-Skills `skills/rebuttal-guidance/references/concern-classification.md`、`mindset-matching-heuristics.md:5-16`、`pre-submission-reviewer/SKILL.md:239-258`、`paper-writer/references/verification-ladder.md §7` → CC BY-NC-SA 4.0，只搬枚举，涨分率与 Cohen's d 数值一条不迁（私有数据集产物）。

## 与自家条款的接缝

- 三约束：本文件的评审动作不替代 qa 核验。「缺件清单 + `not assessable`」是「泄漏」的合法出口——缺什么就声明什么，不猜也不外求。判据与承诺节同构于「rubric 永不进生成上下文」：判据先于稿件进入上下文。
- 断言清单与断言对表：⑥ 硬表是对 `measured/assertions.json` 每条断言的分类动作；三值标记落在 `gates/中期判定.md` 的判词条目上，不是项目状态。
- 段权：承诺节、意见书、账本、判词一律只增不改；退回复核走追加核对节；`trigger:` 子串对应关系靠 git 历史回查。落笔各记一行 `run-log.md`。
- 判词文件：⑤ 只约束措辞与红线，「判词 + 依据 + 签字 + 时刻」四件套归仓根；本文件不引入轮次计数、状态行、枚举态（抛弃状态机条款）。
- 冲突以自家为准：0-100 与均值判级不迁；上游的 `Dimension Scores / Review Body` 分节不迁（三节结构归仓根）；examiner 无「作者回复」环节，rebuttal 策略与涨分目标一律不迁，关口只求真伪与归因。
- 字段归属：本文件只判"形状在场否"与"证据可指否"，不定义台账字段。断言行 schema 归 `experiment-design`；`measured/environment.json` 与 `measured/self_checks.json` 的键名归 `ml-runbook`；`gates/` 四件套格式归仓根 `AGENTS.md`。
- nature-response 的 action×work_status×package_readiness 状态机（含 `REPORTED_DONE_UNVERIFIED`）本体归 `paper-writing`，此处只留一句：作者自称做完而无工件可查，评审面永记 `VERIFIED_DONE`。
