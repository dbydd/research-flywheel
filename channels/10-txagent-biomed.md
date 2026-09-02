# 10 - TxAgent（Harvard Zitnik Lab）：治疗推理智能体

| 字段 | 内容 |
|------|------|
| **机构** | Harvard Medical School / Kempner Institute，Marinka Zitnik Lab；一作 Shanghua Gao 等；关联 ToolUniverse / ToolRAG / ToolGen |
| **论文/发布时间** | arXiv:2503.10970（2025-03-18），TxAgent: An AI Agent for Therapeutic Reasoning Across a Universe of Tools；项目站 zitniklab.hms.harvard.edu/TxAgent；GitHub mims-harvard/TxAgent |
| **用途** | 治疗推理与精准用药：整合 211 个生物医学工具，支持药物机制、相互作用、禁忌症、患者特异性因素的多源证据检索与透明推理，面向药物重定位、个体化治疗推荐、临床决策支持 |
| **验证状态** | 纯计算基准验证，覆盖 3168 个药物推理任务与 456 个个性化场景；无自带湿实验，输出为证据链与推荐，需临床专家复核 |

## 循环形态

TxAgent 采用显式推理-检索-调用-整合的迭代循环：

1. **推理 trace 生成**：专用微调 LLM 产生一步推理陈述，明确当前子目标与所需证据类型。
2. **目标导向工具检索**：ToolRAG 模型根据当前推理状态从 211 工具中检索最相关的候选工具集，按任务目标动态排序。
3. **工具选择与调用**：Agent 从候选集中选择一个工具，构造结构化函数调用参数，执行并获取返回证据。
4. **证据处理与状态更新**：将工具返回的结构化数据与文本证据整合进上下文，评估是否足以支撑结论，不足则回到步骤 1 继续推理。
5. **Finish 终止**：当证据链完整时调用 Finish 工具，输出带引用的治疗建议。

循环强调可解释性，每一步推理与工具调用均持久化，支持审计。该模式区别于一次性 RAG，将检索分散到多步推理中。

## 智能体架构

| 组件 | 功能 |
|------|------|
| ToolUniverse | 211 个专家策展工具的统一集合，涵盖 FDA 药物、Open Targets、HPO 疾病注释等可信源 |
| 专用微调 LLM | 为多步推理与工具执行微调，擅长产生推理 trace 与函数调用 |
| ToolRAG | ML 驱动的工具检索模型，基于任务目标自适应召回工具 |
| ToolGen | 从 API 文档自动生成工具接口的生成器，降低新增工具接入成本 |
| 执行与整合层 | 负责结构化调用、错误处理、证据标准化与最终答案合成 |

架构核心是将工具规模问题转化为检索问题，通过 ToolRAG 将 211 选 1 降为小候选集上的选择。

## 工具/数据库

- **211 工具全集**：含全量 FDA 批准药物（1939 年至今）、Open Targets 临床洞察、HPO 疾病表型、药物-药物相互作用、禁忌症、剂量、适应症等。
- **FDA 药物库**：结构化药物信息、标签、适应症与警告。
- **Open Targets**：靶点-疾病关联、临床证据等级。
- **HPO 与疾病本体**：患者表型到疾病的映射。
- **ML 工具**：部分工具封装机器学习模型（如相互作用预测）。
- **知识更新**：工具对接持续更新的数据源，保证信息新鲜度。

## 度量

- **DrugPC / BrandPC / GenericPC / TreatmentPC / DescriptionPC**：5 套基准共 3168 任务，TxAgent 92.1% 准确率，超越 GPT-4o、DeepSeek-R1 等大模型。
- **个性化场景**：456 个患者特异性场景，评估在合并用药、禁忌、剂量调整等复杂条件下的推理正确性。
- **工具调用质量**：工具选择准确率、调用成功率、证据覆盖度。
- **可解释性**：推理 trace 完整性、引用可追溯性。

## 闭环验证（湿实验/临床）

TxAgent 闭环停留在证据整合与推荐层，无湿实验或临床闭环。验证通过离线基准与专家评审完成，输出建议需经临床医生结合患者具体情况复核。该设计适合作为临床决策支持而非自主处方。

## 开源状态

开源。GitHub mims-harvard/TxAgent 提供代码、ToolUniverse 定义、ToolRAG 与示例；论文与项目站开放；部分数据源需自行申请访问权限。

## 核心可借鉴点

1. **工具规模化的检索解法**：ToolRAG 将大规模工具选择转化为检索问题，适合 OMP 多工具场景。
2. **推理 trace 显性化**：每步推理先于工具调用，证据链可审计，便于错误回溯。
3. **ToolGen 低成本扩展**：从 API 文档自动生成工具接口，新增数据源接入成本低。
4. **持续更新源**：对接 FDA、Open Targets 等活数据源，避免知识过时。
5. **Finish 显式终止**：通过专用工具控制循环结束，避免无限推理。

## 潜在坑

- 211 工具中部分数据源访问受限或需授权，开源复现需处理数据缺口。
- 工具返回异构，标准化与错误处理复杂，单点失败易导致推理中断。
- 微调 LLM 对工具调用格式敏感，迁移到新基座需重新微调或强 prompt 约束。
- 92.1% 准确率为离线基准，真实临床分布外泛化未充分验证。
- 证据整合依赖 LLM 综合，存在选择性引用与过度自信风险。

## 落到 OMP Workspace 的可实现机制

| 借鉴点 | OMP 实现 |
|--------|----------|
| ToolRAG 检索 | 在 `template/tool-registry.json` 上构建 `tool-rag` 子智能体，输入当前推理 trace 输出 Top-K 工具，`channels/10-*` 执行前必经该检索 |
| 显性推理 trace | 约束每轮输出 `reasoning.md` + `tool-call.json` 双产物，`local://txagent/trace-{step}.md` 持久化，`hub` 同步 |
| ToolGen | `tools/toolgen/` 脚本读取 `vault://apis/*.md` 自动生成 tool 定义，新增数据源仅追加文档 |
| 活数据源 | 对 FDA、Open Targets 配置定时 `schedule_prompt` 拉取，更新 `vault://biomed/fda/` 与 `vault://biomed/opentargets/` |
| Finish 门控 | 仅当证据覆盖度阈值达标才允许调用 Finish，未达标自动追加推理轮次，阈值定义在 `WATCHDOG.yml` |

> 来源：arXiv:2503.10970、zitniklab.hms.harvard.edu、Kempner Institute 报道、GitHub mims-harvard/TxAgent；已通过 web_search 与 read 验证。
