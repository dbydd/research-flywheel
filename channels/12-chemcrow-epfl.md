# 12 — ChemCrow (EPFL / IBM RoboRXN)

| 维度 | 内容 |
|------|------|
| 机构 | EPFL, NCCR Catalysis, Philippe Schwaller 课题组 + IBM Research RoboRXN + WhiteLab (U Rochester) |
| 论文/发布时间 | arXiv 2304.05376 (2023.04) → Nature Machine Intelligence 6, 525-535 (2024.05.08) `10.1038/s42256-024-00832-8` |
| 循环形态 | 自然语言任务 → ReAct 思考 → 工具调用 → 观测 → 再思考 → 终答/上机合成 → 人机协作验证 |
| 智能体架构 | 单 GPT-4 ReAct Agent + 18 专家工具 + LangChain 编排 + RoboRXN 云机器人执行 |
| 工具链 | 分5类18工具：反应/分子/安全/搜索/标准；底层含 RXN4Chemistry、OPSIN、PubChem、GHS 安全评估、文献检索等 |
| 度量 | 14 个化学用例；自主合成 DEET + 3 种硫脲有机催化剂 + 新 chromophore (目标 369nm→实测336nm)；专家评分在复杂任务上显著优于纯 GPT-4 |
| 开源状态 | 开源 `ur-whitelab/chemcrow-public` (Zenodo v0.3.24) + `chemcrow-runs` 全量执行轨迹 |
| 潜在坑 | 工具输出错误会误导推理；合成引擎无效动作 (not enough solvent / invalid purify)；推理质量受限于 GPT-4 本身 |

## 闭环形态详解

ChemCrow 把 LLM 从"超自信的错误信息源"转为"推理引擎"。用户输入如 "Plan and execute the synthesis of an insect repellent"，LLM 按 Thought→Action→Action Input→Observation 的 ReAct 循环迭代：先思考当前状态与目标关联，再选工具并给参，暂停生成等待工具返回 Observation，再回到 Thought 直至终答。验证闭环分两段：前 4 个分子在 IBM RoboRXN 全自动合成，后 1 个 chromophore 为人机协作——ChemCrow 负责数据清洗、随机森林训练与候选推荐，人类负责合成与光谱验证。

## 智能体架构

单 Agent 多工具架构，GPT-4 为唯一推理核心，18 工具通过 LangChain 暴露为统一函数签名 (name, description, input/output spec)。论文刻意让模型优先用工具而非内部知识，以凸显工具增益。近期衍生的 ChemAgent 在此基础上扩展到 137 工具并引入层次化进化 MCTS，将 planning 与 execution 解耦，并用自维护记忆库持续进化，属于 ChemCrow 架构的规模化演进。

## 工具链

5 类划分清晰可复用：
- **Reaction**：Transformer 反应预测、RXN4Chemistry 路线规划
- **Molecule**：OPSIN IUPAC→结构、SMILES 转换、性质计算
- **Safety**：GHS 分类、危险评估，执行前强制检查
- **Search**：文献/网络检索、分子数据库查询
- **Standard**：计算器、代码执行等通用工具
工具设计要求文档完备、代码精炼，便于 LLM 准确选型与填参。ChemToolBench 数据集即为评估工具选择与参数填充能力而建。

## 硬件抽象

通过 IBM RoboRXN 平台实现硬件抽象。ChemCrow 生成标准化合成步骤，RoboRXN 提供 `synthesize` 与 `validate` 两类 API：前者接收步骤 JSON 执行合成，后者返回可执行性校验 (如溶剂不足、纯化步骤非法)。抽象层不暴露底层机械臂指令，只暴露化学语义级别的合成原语，LLM 无需理解流体力学即可操控。这与 Coscientist 的 SLL 思路一致，但更聚焦有机合成的标准化流程。

## 安全约束

显式集成安全工具是 ChemCrow 的关键差异。每次合成前调用 Safety 类工具评估 GHS 危险等级与操作风险，并可拒止高危请求。论文特别强调"缓解实验室安全顾虑，自适应机器人平台特定条件"。失效分析显示，若安全工具返回不准确，Agent 会得出错误结论，因此安全能力与工具质量强绑定。

## 调度

ReAct 循环本身即调度器，串行执行工具调用。RoboRXN 侧为云队列，支持多合成任务排队。ChemCrow 在合成验证失败时自主迭代修正 (如增加溶剂量)，无需人工介入，体现了"验证-修正"内循环调度。未涉及复杂并行 DAG，但架构上支持并发多用户任务由 RoboRXN 侧调度。

## 失败处理

典型失败是合成步骤未通过 RoboRXN 的验证器。ChemCrow 的处理是查询 validation data，定位无效动作，迭代调整参数直至 fully valid。论文指出预测流程并非总可直接执行，但 Agent 能自主适配。另一种失败是工具返回错误信息导致推理偏离，缓解手段是 ChemToolBench 上的层次化 MCTS 与记忆库，或简单重试。评估显示纯 GPT-4 在无工具时系统性 hallucinate，而 ChemCrow 的失败更多可追溯到工具链而非 LLM 幻觉。

## 度量与评估

14 个用例覆盖药物合成规划、相似作用分子设计、反应机理阐释等。评估采用双轨：EvaluatorGPT (让 LLM 扮教师打分) 与专家化学家三维评分 (化学正确性、推理质量、任务完成度)。Expert 评估显示复杂任务上 ChemCrow 显著领先，简单记忆型任务 (DEET, paracetamol) 上纯 GPT-4 略优。实验验证 4/4 RoboRXN 合成成功，chromophore 吸收峰误差约 9% (336 vs 369nm)。

## 核心可借鉴点

1. **工具分类学**：5 类 18 工具的划分可直接映射为 OMP capability 的命名空间。
2. **强制工具优先**：prompt 显式要求优先调工具而非内部记忆，显著降低幻觉。
3. **Validation Adapter**：硬件侧返回结构化校验错误，Agent 侧迭代修正，无需人介入。
4. **人机协作模式**：复杂发现任务中让人负责最后物理验证，LLM 负责数据与模型，形成可控边界。

## 潜在坑

- 工具越多选型越难，137 工具的 ChemAgent 已需 MCTS 辅助，18 工具是平衡点。
- 底层合成引擎质量决定上限，引擎改进比 Agent 技巧更重要。
- EvaluatorGPT 偏好流畅但 hallucinate 的纯 GPT-4 回答，自动评估需谨慎。
- 工具错误会级联，缺乏独立的工具输出校验层。

## OMP 硬件/仿真 Capability 抽象映射

- 按 ChemCrow 五类划分 OMP capability 命名空间：`chem.reaction.predict`, `chem.molecule.convert`, `chem.safety.ghs`, `chem.search.pubchem`, `std.calc`，每个 capability 声明 `description + input_schema + output_schema + cost`，LLM 通过统一注册表选型。
- 硬件抽象为 `RoboRXN`-like 的两阶段接口：`capability.validate(procedure) -> {valid, errors[]}` 与 `capability.execute(procedure) -> observation`，仿真环境实现相同接口，调度器先走 `validate` 仿真分支，失败则触发 Agent 修正循环，成功后再路由到真机。
- 安全 capability 设为 `pre_filter`：任何 `execute` 前 OMP 强制调用 `chem.safety.ghs`，返回高风险时阻断并要求人工确认，对应 OMP 的 `requires_approval: true` 策略。

> 来源验证：Nature MI 论文全文 + EPFL 官方新闻 + IBM RoboRXN 文档 + chemcrow-public GitHub，交叉核对 18 工具清单与 4+1 合成验证。
