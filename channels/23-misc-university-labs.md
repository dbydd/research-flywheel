# 23 - 零散高校实验室：MIT / Caltech / Oxford / Cambridge / ETH / Toronto / Stanford 等

> 领域：跨机构、跨学科的零星 autonomous research 工作
> 关键词：self-driving lab、autonomous discovery、human-in-the-loop、Acceleration Consortium

> 本文件为"查漏补缺"汇总，收录前述 01-22 未单独立项、但具代表性的高校实验室工作。每节均含机构、论文/时间、循环形态、工具链、度量、开源状态、可借鉴点与坑。

---

## 23.1 MIT — Coley Lab / Jensen Lab / FutureHouse / Agent Index

- **机构**：MIT Chemical Engineering（Connor Coley, Klavs Jensen）+ MIT spin-out FutureHouse
- **论文/时间**：
  - Coley Lab 自驱化学综述（MIT coley.mit.edu, 持续更新）
  - MIT Agent Index（2025, 盘点 30 个主流 AI agent 的自主能力分级）
  - FutureHouse 自主科研 agent（MIT News 2025-06-30）
  - 多层智能科学实验室架构 Position Paper（arXiv 2506.19613）
- **循环形态**：`AI 分子设计 → 反应预测 → 机器人液体处理 → 在线分析（HPLC/MS）→ 闭环优化`；ASPIRE 等平台打通 design-make-test。FutureHouse 则做 hypothesis→code→robot→analysis→manuscript 端到端。
- **工具链**：PyLabRobot（开源机器人编排）、Open Reaction Database、RXN/retro 模型、HPLC/MS、LangChain/Agents
- **度量**：合成成功率、优化轮次、发现新分子数、agent 自主性分级（Agent Index 的 autonomy level）
- **开源状态**：PyLabRobot 开源，ASPIRE 部分开源，FutureHouse 商业化
- **可借鉴点**：
  1. PyLabRobot 证明"开源硬件抽象层"可大幅降低自驱实验室门槛，harness 可复用其驱动模型。
  2. Agent Index 的自主性分级（从 chat 到 enterprise tool-use）为 harness 设计成熟度路线图提供标尺。
  3. Jensen Lab 的连续流（flow chemistry）+ AI 闭环对反应条件优化极高效，适合催化/合成子循环。
- **坑**：
  - 连续流硬件定制化高，复现成本大。
  - 化学空间巨大，agent 易在局部最优震荡，需 diversity 约束。

## 23.2 Caltech — SARA / Genesis Mission 电化学自驱实验室

- **机构**：Caltech（John Stauffer Professor Theo Agapie 牵头，DOE Genesis Mission 资助）
- **论文/时间**：Genesis Mission 2024-2025 立项；CHESS 报道 SARA；Caltech News 官方发布
- **循环形态**：`AI 代理驱动的电化学合成与表征闭环`：SARA（Scientific Autonomous Reasoning Agent）分层 AI + 主动学习建模加工相图，Genesis 项目在此基础上做"炼厂式"先进化学制造。
- **工具链**：机器人合成+表征、分层主动学习、电化学工作站、相图建模、DOE 资助的自驱实验室硬件
- **度量**：相图覆盖速度、材料发现加速度、加工窗口确定效率
- **开源状态**：方法论文公开，硬件与控制软件未开源
- **可借鉴点**：
  1. "相图驱动"的发现范式：不直接搜材料，而是建相图再选点，harness 可借鉴"先建 landscape 再优化"的两阶段策略。
  2. 分层 AI（高层推理+低层控制）与 harness 的"大脑+执行器"分层一致。
- **坑**：电化学体系对环境敏感，闭环噪声大，reward 需鲁棒设计。

## 23.3 Oxford — 自驱量子实验室

- **机构**：University of Oxford Department of Physics
- **论文/时间**：physics.ox.ac.uk 官方发布（2024-2025），self-driving quantum labs 主题
- **循环形态**：`自然语言指令 → 代码生成 → 超导量子比特硬件控制 → 实时分析 → 自主决策下一步实验`。成功实现量子比特校准与纠缠态制备，性能对标专家。
- **工具链**：LLM 指令转代码、量子硬件控制栈、实时数据分析、量子态层析
- **度量**：量子比特保真度、纠缠保真度、与专家对比的校准时间/精度
- **开源状态**：方法论文公开，量子硬件私有
- **可借鉴点**：
  1. 证明 LLM 可直接操控物理硬件（非仅软件），harness 的"代码即实验"可延伸到仪器控制。
  2. 自然语言→硬件指令的编译链对非量子领域亦有参考（XRD、HPLC 亦可）。
- **坑**：量子硬件稀缺、校准漂移快，闭环需频繁重校准，通用性有限。

## 23.4 Cambridge — 自驱材料实验室（Shijing Sun）+ AI 化学语言

- **机构**：University of Cambridge, Department of Materials Science & Metallurgy（Shijing Sun 组，2024 加入）
- **论文/时间**：cam.ac.uk AI 化学语言报道（>90% 反应预测准确率，超越训练有素化学家）；msm.cam.ac.uk 自驱实验室讲座 2024-2025
- **循环形态**：`AI 分子/材料设计 → 反应预测（化学语言模型）→ 自动合成 → 高通量表征 → 闭环优化`。Sun 组聚焦能源材料（光伏、电池）的高通量机器人+AI 决策。
- **工具链**：化学语言模型（seq2seq 反应预测）、高通量机器人、能源材料表征
- **度量**：反应预测准确率（>90%）、合成路线最优性、材料性能（效率/稳定性）
- **开源状态**：反应预测技术论文公开，部分模型待开源
- **可借鉴点**：
  1. "化学语言"范式（把反应当翻译任务）简洁有效，harness 的 domain LLM 可借鉴序列建模思路。
  2. 能源材料的"性能-稳定性"多目标优化与催化剂场景高度相似。
- **坑**：>90% 准确率在特定数据集上，外推到新反应类型下降明显。

## 23.5 ETH Zurich — 实验室自动化设施（Sant Kumar）

- **机构**：ETH Zurich Laboratory Automation Facility（Sant Kumar, Yokogawa 合作）
- **论文/时间**：活动与报道 2024-2025，Atinary/Yokogawa 联合方案
- **循环形态**：`ML 预测反应结果 → 机器人闭环执行 → 实时数据回流 → 模型迭代`。涵盖化学、生物、材料的模块化自驱平台，近期演示 AI 引导的酶合成与筛选、RL 驱动的材料发现。
- **工具链**：Yokogawa 高内涵成像、Atinary SDLabs、模块化机器人、RL 优化器
- **度量**：实验通量、优化轮次、酶活性/选择性提升
- **开源状态**：平台商业化（Atinary/Yokogawa），方法论文公开
- **可借鉴点**：
  1. 模块化、可扩展的硬件抽象与 Yokogawa 成像的结合，适合生物+化学混合 лаборатория。
  2. Atinary 无代码 AI 平台降低领域专家使用门槛，harness 可提供类似"无代码实验设计"界面。
- **坑**：商业化平台成本高，小实验室难以承担；RL 训练需大量初始数据。

## 23.6 Toronto — Matter Lab / Acceleration Consortium / Project Ada / AUTODIAL

- **机构**：University of Toronto, Matter Lab（Alán Aspuru-Guzik）+ Acceleration Consortium（$200M CFREF 资助）
- **论文/时间**：2024 Project Ada（首个全自动固态无机粉末合成平台）、2025 AUTODIAL（高熵合金/金属玻璃/陶瓷涂层）、持续综述于 matter.toronto.edu
- **循环形态**：`AI 实验设计 → 计算机视觉机器人执行 → 自动表征 → 闭环优化`。目标：将 10 年/$10M 的材料发现压缩 10 倍至 1 年/$1M。Ada 用无机粉末为起点，AUTODIAL 扩展到合金与涂层。
- **工具链**：AI 实验设计、CV 机器人、自动表征、数字孪生、Acceleration Consortium 共享基础设施
- **度量**：发现成本/时间压缩比、通量、材料性能提升
- **开源状态**：部分平台与数据集公开，Consortium 共享
- **可借鉴点**：
  1. 明确的 10x 成本/时间压缩目标为 harness 提供了可量化的北极星指标。
  2. Consortium 模式（多组共享基础设施）对高校资源复用有示范意义。
  3. 自 Ada 到 AUTODIAL 的"平台化演进"（从粉末到合金）展示如何横向扩展自驱实验室。
- **坑**：$200M 级投入不可复制；多组协作的调度与数据标准统一是隐形挑战。

## 23.7 Stanford — SUNCAT / 自主智能体加速材料发现

- **机构**：Stanford SUNCAT Center for Interface Science and Catalysis + Stanford Autonomous Agents Lab
- **论文/时间**：Active Learning 加速 Ir 氧化物多晶型发现（2024-2025）、On-the-fly 闭环材料发现（PMC7686338）、SUNCAT 自治智能体综述
- **循环形态**：`代理序列决策 → 代理模型（surrogate）+ 贝叶斯不确定度 + 物理约束 → 选下一实验（DFT 或 XRD）→ 闭环更新`。支持云端 DFT 大规模并行，覆盖氧化物/磷化物/硫化物/合金等二元/三元体系，可选 human-in-the-loop。
- **工具链**：DFT（VASP 等）、贝叶斯主动学习、替代模型、高通量 XRD、human-in-the-loop 接口
- **度量**：DFT 计算成本节约、发现稳定 Ir 氧化物多晶型数量、相图构建效率、human 干预频率
- **开源状态**：论文与方法公开，部分代码依托开源 DFT 工作流
- **可借鉴点**：
  1. 物理约束+贝叶斯不确定度的"约束主动学习"比纯探索更高效，harness 可直接复用。
  2. human-in-the-loop 的可选设计兼顾自主性与可控性，适合高风险实验。
  3. 云端 DFT 的弹性调度为计算密集型闭环提供了成本模型。
- **坑**：DFT 误差与实验偏差的鸿沟需校准；高维组合空间的主动学习易陷入维度灾难。

---

## 跨校共性总结

| 维度 | 共识 |
|------|------|
| 循环 | 设计→执行→表征→学习，四段式占主导，多为 Bayesian/active learning 驱动 |
| 硬件 | 机器人+高通量表征是标配，差异在 domain（化学/材料/量子/生物） |
| AI 角色 | 实验设计与结果判读是 AI 核心价值，执行层多为确定性控制 |
| 度量 | 吞吐/成本/时间压缩比最受关注，科学新颖性度量仍主观 |
| 开源 | 硬件控制多私有，编排层（PyLabRobot、Atinary）与模型层较开放 |
| 趋势 | 从单实验室闭环向 Consortium/云端网络演进 |

## 可借鉴点（汇总）

1. **开源硬件抽象层（PyLabRobot）** 降低自建门槛。
2. **10x 压缩比** 作为北极星指标。
3. **约束主动学习 + human-in-the-loop** 平衡效率与安全。
4. **平台化演进**（Ada→AUTODIAL）展示横向扩展路径。
5. **Consortium 共享模式** 解决单组资源不足。

## 潜在坑（汇总）

1. 硬件定制化高、复现成本大。
2. 化学/材料空间局部最优陷阱。
3. 跨组数据标准与调度复杂。
4. 商业化平台成本门槛。
5. 科学新颖性评估主观，易夸大。

## 信息来源

- MIT: coley.mit.edu, news.mit.edu FutureHouse, arXiv 2506.19613, MIT Agent Index 2025
- Caltech: caltech.edu Genesis Mission, CHESS SARA
- Oxford: physics.ox.ac.uk self-driving quantum
- Cambridge: cam.ac.uk chemistry language, msm.cam.ac.uk Shijing Sun
- ETH: Yokogawa/Atinary 联合方案, linkedin Nilmani Singh, atinary.com
- Toronto: matter.toronto.edu, Acceleration Consortium, AUTODIAL
- Stanford: suncat.stanford.edu, PMC7686338, The Innovation 2025

---
*调研时间：2026-09-02 | 验证方式：web_search + 官网/论文交叉验证 | 定位：查漏补缺汇总*
