# 物理 / 跨学科 / 新兴渠道汇总（20-23）

> 覆盖 AI4S 物理求解（AutoNumerics/PhysMaster/FlowX）、跨学科假设生成（Denario/AstroPilot/Rumi/GFlowNet）、催化/材料云端闭环（DigCat/A-Lab/RoboRXN）、零散高校实验室（MIT/Caltech/Oxford/Cambridge/ETH/Toronto/Stanford）四组。每组经 web_search + arXiv/官网/Nature/ChemRxiv 交叉验证。

## 文件索引

| # | 文件 | 系统 | 一句话定位 |
|---|------|------|-----------|
| 20 | `20-physics-autonumerics.md` | AutoNumerics / PhysMaster / FlowX | PDE-agnostic 经典求解器生成 + 物理合理性校验 + AI 编排 CFD |
| 21 | `21-denaro-rumi.md` | Denario / AstroPilot-AI / Rumi / GFlowNet | 端到端助理 + 天文闭环 + 终端知识图谱 + 多样性采样假设生成 |
| 22 | `22-cloud-synthesis.md` | DigCat / A-Lab / RoboRXN | 云端催化剂设计 + 无机粉末自主合成 + 有机 retrosynthesis 云执行 |
| 23 | `23-misc-university-labs.md` | MIT/Caltech/Oxford/Cambridge/ETH/Toronto/Stanford | 七校自驱动实验室查漏补缺：化学/材料/量子/电化学/生物 |

## 对比总表

| 维度 | 20-A AutoNumerics | 20-B PhysMaster | 20-C FlowX | 21-A Denario | 21-B AstroPilot | 21-C Rumi | 21-D GFlowNet | 22-A DigCat | 22-B A-Lab | 22-C RoboRXN | 23 众实验室 |
|------|-------------------|-----------------|------------|--------------|-----------------|-----------|---------------|-------------|------------|--------------|-------------|
| **机构/时间** | Haizhao Yang 2026-02 arXiv:2602.17607 | 上交 2025-12 arXiv:2512.19799 | FlexCompute 2024-25 产品 | AG2/LangGraph 2025-10 arXiv:2510.26887 | HSC/Rubin 2024-25 综述 | Subhansh/Decidr 2025-26 GitHub | Mila/Bengio 2022+IBM GT4SD | 大连化物所 2024 ChemRxiv | LBNL/Berkeley 2023 Nature 624 | IBM Research 2018-24 | 7 校 2024-26 |
| **循环形态** | 规划→多候选生成→coarse-to-fine→残差验证→择优 | 推理→符号/数值混合→参数自适应→物理校验 | AI 前处理→经典求解→AI 收敛诊断 | idea→文献→plan→code→report 链式 | 数据→视觉→LLM 推理→调度→论文 | 文献→图谱→矛盾检测→锦标赛→过滤 | 采样→评估→reward 更新→重采样 | 设计→云分发→合成→表征→回流 | 文献+GNoME→配方→机器人→XRD→主动学习 | 目标→Transformer 逆合成→机器人→优化 | 设计→执行→表征→学习（各域实例化） |
| **智能体架构** | Planner/Coder/Debugger/Verifier/Ranker 多 Agent | 单 LLM + 符号数值工具 | AI 编排+经典内核 | AG2+LangGraph 状态图多 Agent | LLM+Vision+调度三层 | Terminal + 图谱 + 锦标赛 | 生成器+闭环控制器 | 云 Agent+分布式执行器 | 自动化+ML 决策+ARROWS3 | Transformer+机器人+云编排 | PI 会议/分层主动学习/量子控制等 |
| **工具链** | NumPy/SciPy/残差/CFL | Julia/DifferentialEquations.jl | 自研 CFD/RANS/LES | AG2/LangGraph/Docker/FRED | HSC/LSST/分割/红移 | 图数据库/GFlowNet/skeptic | GT4SD/PyTorch/DFT | 400k 催化剂库/GHS | 3 臂8 炉XRD | RXN/Chemspeed/SDLabs | PyLabRobot/Echo/DFT/成像等 |
| **度量** | L2 误差/residual/守恒/时间 | 成功率/数值误差/物理一致 | 残差/网格无关/实验对照 | 完成度/可运行率/发表评分 | 准确率+5-10%/周→小时 | 新颖性/可检验/多样性 | mode coverage/效率 | 转化率/周期/泛化 | 63-71%/20-25/天 | top-N/成功率/成本 | 吞吐/成本/时间压缩比 |
| **开源** | 论文公开代码预告 | 论文公开 | 商业部分 API | 架构可复现 | 方法公开 | GitHub 开源服务下线 | GT4SD 开源 | 论文公开 | 方法公开控制私有 | 部分开放商业化 | PyLabRobot 等部分开源 |
| **可借鉴点** | 经典求解器生成+残差自验证+多候选择优 | 物理 sanity check 独立 | AI 决策+确定性执行边界 | 状态图编排+Docker 隔离 | 感知推理解耦+开放数据 | 图谱记忆+锦标赛多样性 | 多样性采样 | 异地设计执行分离+双模型更新 | XRD 自动解析+主动学习 | 预测即指令+多云调度 | 开源硬件抽象+10x 目标+约束主动学习 |
| **坑** | CFL/边界遗漏/评估成本 | 环境漂移/复现度 | 黑盒/日志 | 助理退化/幻觉 | TB/夜吞吐 | 收购下线/reward 稀疏 | reward 设计难 | 负样本偏差/跨硬件复现 | 新颖性争议/硬件故障 | 成本/硬件门槛 | 定制化/局部最优/标准不一 |

## 跨组共性与差异

- **验证信号**：20 系用残差/守恒量做无监督验证；21 系用多样性与可检验性；22 系用 XRD/性能实测；23 各校以吞吐与成本压缩为北极星。四者互补构成"数值-假设-物理-工程"全谱验证。
- **多样性机制**：GFlowNet 锦标赛（21）、多候选择优（20）、Consortium 并行（23）、DigCat 多实验室（22）均显式抗 mode collapse，harness idea 阶段应强制多样性。
- **硬件边界**：20 的 FlowX 与 23 的量子/电化学证明 AI 不必替代求解器/仪器，做好编排与判读即可；22 的 A-Lab/RoboRXN 则证明执行自动化价值在 XRD 解析等判读环节。
- **开源光谱**：纯软件（AutoNumerics/Rumi/GFlowNet）最易复用；重硬件（A-Lab/RoboRXN/各校 SDL）需依赖 PyLabRobot/Atinary 等抽象层。

## OMP Harness 统一可借鉴方案

1. **数值-假设-执行三飞轮**：20 的"生成经典求解器+残差验证"作为计算飞轮，21 的"图谱+锦标赛"作为假设飞轮，22 的"云设计+本地执行"作为实验飞轮，三者通过统一 capability 注册表对接。
2. **验证分级**：L1 残差/守恒（自动）→ L2 XRD/性能（半自动）→ L3 人工物理审查（PhysMaster sanity check），逐级门控。
3. **多样性闸门**：idea 阶段强制 GFlowNet/锦标赛采样，执行阶段多候选并行，结果阶段按 Pareto 排序，避免早熟收敛。
4. **硬件即能力**：复用 PyLabRobot/ChemOS 抽象，仪器文档向量化，`validate→execute` 双接口，`safety pre_filter` 显式阻断。
5. **记忆图谱化**：Rumi 知识图谱 + SciAgents 图谱增量 + A-Lab pairwise 数据库统一为 `memory_store`，支撑跨轮剪枝与复利。

> 详述见 `20-physics-autonumerics.md`、`21-denaro-rumi.md`、`22-cloud-synthesis.md`、`23-misc-university-labs.md`，每文件均含机构、时间、循环、架构、工具链、度量、开源、可借鉴点、坑、来源。
