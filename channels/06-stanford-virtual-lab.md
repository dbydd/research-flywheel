# 06 - Stanford Virtual Lab：跨学科虚拟实验室

| 字段 | 内容 |
|------|------|
| **机构** | Stanford University + Chan Zuckerberg Biohub San Francisco，James Zou 团队；一作 Kyle Swanson 等，协作者 John Pak（湿实验） |
| **论文/发布时间** | bioRxiv 2024.11.11.623004（2024-11-12 预印），The Virtual Lab: AI Agents Design New SARS-CoV-2 Nanobodies with Experimental Validation；2025-07-29 Nature 报道延伸 |
| **用途** | 用 LLM 智能体团队替代传统跨学科课题组，解决需要生物学、计算、化学、结构生物学协同的开放式难题；首个案例为针对 SARS-CoV-2 新变体（JN.1 / KP.3 等）设计纳米抗体 |
| **验证状态** | 已完成湿实验验证：92 个全新纳米抗体设计，CZ Biohub 湿实验室表达与结合实验，其中 2 个对 JN.1 / KP.3 结合力显著提升且保留对 ancestral spike 的结合 |

## 循环形态

Virtual Lab 采用双层循环嵌套会议机制：

1. **外层 Team Meeting 循环**：PI Agent 召集全体专家 Agent 围绕科学议程讨论，确定本周期的设计策略、突变空间和计算 pipeline 步骤。人类研究员以 high-level feedback 介入，纠正方向但不写代码。
2. **内层 Individual Meeting 循环**：每个专家 Agent 在独立上下文中完成分配任务（如突变打分、结构预测、能量最小化），产出归档后回到 Team Meeting 汇总。
3. **计算-湿实验大闭环**：计算端批量产出候选序列后，进入人类主导的湿实验表达、纯化、ELISA/SPR 结合测定，结果回灌为下一轮计算筛选的约束条件。

单轮计算迭代约数小时，94% 时间花在工具调用与结构计算，人机交互仅在策略节点。整体从立项到 92 个设计完成约数周，远快于传统 6-12 月的抗体工程周期。

## 智能体架构

| 角色 | 职责 | 基座模型 |
|------|------|----------|
| PI Agent | 议程管理、任务分解、跨领域协调、冲突裁决 | GPT-4 级 LLM，system prompt 赋予 PI 人设 |
| 免疫学专家 Agent | 纳米抗体生物学可行性、表位选择、变体逃逸分析 | 同上，注入免疫学文献上下文 |
| 计算生物学 Agent | 序列突变策略、ESM 打分、AlphaFold 流程编排 | 同上，注入计算生物学工具手册 |
| 结构生物学/化学 Agent | 结构精修、Rosetta 能量评估、成药性检查 | 同上 |
| Critic Agent | 全流程挑错、证伪、提出反例，强制团队自检 | 同上，对抗式 prompt |
| 人类研究员 | 战略反馈、在关键分叉点否决或追加目标，不参与执行细节 | 真人 |

架构要点：所有 Agent 共享同一 LLM 基座，通过角色 prompt 与私有记忆隔离实现分工；PI 与 Critic 形成生成-批判对偶，提升鲁棒性；会议记录以结构化 markdown 持久化，支持断点续跑。

## 工具/数据库

- **ESM（Evolutionary Scale Modeling）蛋白语言模型**：计算点突变的 log-likelihood ratio，筛选高概率突变。
- **AlphaFold-Multimer**：预测纳米抗体-抗原复合物 3D 结构，评估结合界面。
- **Rosetta**：结构精修与能量最小化，给出 ΔG 近似与稳定性分数。
- **Python bioinformatics 栈**：Biopython、PyMOL 脚本、序列比对与聚类。
- **文献与数据库隐式调用**：Agent 通过 LLM 内部知识与检索补充 SARS-CoV-2 变体序列与表位信息。
- **湿实验工具链**：大肠杆菌/哺乳动物细胞表达、纯化、ELISA、SPR（在人类实验室侧完成）。

## 度量

- **计算侧**：ESM 突变打分分布、AlphaFold pLDDT / pTM、Rosetta 能量、结合界面 RMSD。
- **湿实验侧**：结合亲和力（KD / EC50）、中和活性、跨变体广谱性（ancestral vs JN.1 vs KP.3）、表达可溶性与稳定性。
- **系统侧**：设计成功率（92 设计中功能性比例）、人类反馈次数、计算成本/设计。

论文报告功能性纳米抗体比例显著高于随机突变基线，2 个突出候选在 JN.1/KP.3 上结合力提升且不牺牲 ancestral 结合，证明跨学科推理有效。

## 闭环验证（湿实验/临床）

湿实验在 CZ Biohub 由 John Pak 团队执行：基因合成、质粒构建、蛋白表达纯化、ELISA 初筛、SPR 精确测定。验证流程与真实抗体发现管线一致，非纯计算自评。该模式证明 AI 虚拟实验室可产出可直接进入下游成药评估的实体分子。

## 开源状态

- 论文与补充材料开放（bioRxiv CC-BY-NC）。
- 代码未以完整一键复现形式开源，部分 pipeline 描述与 prompt 策略见论文附录。
- 依赖的 ESM、AlphaFold、Rosetta 均为开源或可申请使用，复现门槛主要在 LLM 编排与湿实验室。

## 核心可借鉴点

1. **双层会议抽象**：Team Meeting 做策略对齐，Individual Meeting 做执行隔离，天然适合映射到 OMP 的 supervisor/worker 协作与 `local://` 会议纪要。
2. **PI + Critic 双角色**：生成与批判分离，显著降低幻觉导致的错误突变。
3. **工具链即 pipeline**：将 ESM-AlphaFold-Rosetta 串成声明式 workflow，Agent 只负责参数与阈值决策，执行交由确定性工具。
4. **人类只在分叉点介入**：避免人类成为瓶颈，同时保留对高风险决策的否决权。

## 潜在坑

- 角色 prompt 漂移：多轮会议后专家人设弱化，需定期重注角色指令。
- 工具误差累积：ESM 分数与真实结合力相关性有限，AlphaFold 对新表位预测误差大，过度依赖计算分会漏掉湿实验表现好的候选。
- 评估偏乐观：92 设计中仅少数强结合，论文突出头部案例，平均成功率需谨慎解读。
- 湿实验成本高：每轮合成表达需数千美元与数周，闭环频率受限。

## 落到 OMP Workspace 的可实现机制

| 借鉴点 | OMP 实现 |
|--------|----------|
| PI 议程驱动 | `research-flywheel/template/virtual-lab-pi.md` 定义 PI 系统 prompt，Supervisor Agent 按议程分发任务到 `channels/06-*` 对应 worker |
| Critic 对抗 | 独立 `critic` 子智能体，配置与主 worker 相同工具但 prompt 为证伪视角，每轮产出 `critique.md` 阻塞下一轮 |
| ESM-AlphaFold-Rosetta 链 | 封装为 `tools/bio-pipeline/` 三个可复用 tool，输入序列输出分数与结构，Agent 通过 `tool` 调用而非自由文本编排 |
| 会议持久化 | 每次 Team/Individual 会议写入 `local://virtual-lab/meeting-{n}.md`，`hub` 消息同步议程，支持断点续跑 |
| 人机分叉点 | 在 `WATCHDOG.yml` 定义 `human-gate: binding-threshold`，仅当结合分数分歧超过阈值时触发人工复核 |

> 来源：bioRxiv 2024.11.11.623004、Chan Zuckerberg Biohub 报道、Stanford HAI 解读；已通过 web_search + read 验证正文结构。
