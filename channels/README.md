# Research Flywheel — 全量渠道索引（Channels Index）

> 目标：40+ 系统，按学科分类，真实 web_search + read 验证。每行对应 `channels/*.md` 详述。
> 统计口径：单一 `.md` 含多系统的按系统拆行，故行数 > 文件数。当前 **46 个有效条目**，覆盖 CS / 生物医学 / 化学材料 / 物理跨学科 / 平台基础设施 五大类。

## 快速导航

| 汇总文件 | 覆盖范围 |
|----------|----------|
| [`_index-cs.md`](_index-cs.md) | 01-05 CS 自主科研（Karpathy / Sakana / HKUDS / Cycle / Dolphin 系） |
| [`_index-biomed.md`](_index-biomed.md) | 06-10 生物医学（Virtual Lab / Biomni / Co-Scientist / Robin / TxAgent） |
| [`_index-chemmat.md`](_index-chemmat.md) | 11-15 化学/材料/SDL（Coscientist / ChemCrow / SciAgents / A-Lab / MatterGen） |
| [`_index-platform.md`](_index-platform.md) | 16-19 平台与基准（Bohrium / Agent Lab / Deep Research / Benchmarks） |
| [`_index-physics-misc.md`](_index-physics-misc.md) | 20-23 物理/跨学科/新兴（AutoNumerics / Denario-Rumi / Cloud Synthesis / 零散高校） |
| 本文件 `README.md` | 全量 46 条索引总表 |

---

## 全量索引总表（46 条）

| # | 系统 | 机构 / 发布时间 | 领域 | 循环类型 | 开源状态 | 详述文件 |
|---|------|----------------|------|----------|----------|----------|
| 01 | Karpathy Autoresearch | Karpathy 个人 / 2026-03 | CS通用 | 单文件变异→5min赛马→val_bpb keep/discard | MIT 开源 95k★ | `01-karpathy-autoresearch.md` |
| 02 | Sakana AI Scientist v1/v2 | Sakana × UBC/Vector/Oxford / 2024-08 & 2025-04 | CS通用 | idea→tree search→executor→VLM审图→writer | 完全开源 | `02-sakana-ai-scientist.md` |
| 03 | HKUDS AI-Researcher / Novix | 香港科技大学 / 2025-05 | CS通用 | 文献→假设→实现→实验→写作（双轨 Bench） | 主库开源 | `03-ai-researcher-hkuds.md` |
| 04 | CycleResearcher / CycleReviewer | 交大/微软等 / 2024-11 ICLR2025 | CS通用 | 研究↔评审双循环 + DPO 偏好飞轮 | 代码权重全开源 | `04-cycle-researcher.md` |
| 05 | Dolphin | 上科/上海AI Lab / 2025-01 ACL2025 | CS通用 | 思考→实践→反馈闭环，异常局部修复 | 完全开源 | `05-dolphin-virsci.md` |
| 06 | VirSci / Stanford Virtual Lab | Stanford Zou 组 / 2024-11 biorxiv | 生物医学 | PI会议→多学科 agents 共享管线→湿实验回流 | 管线开源 | `05-dolphin-virsci.md` + `06-stanford-virtual-lab.md` |
| 07 | ResearchAgent | KAIST / 2024-04 NAACL2025 | CS通用 | 核心论文→图谱扩展→多 Reviewer 精炼 | 开源 | `05-dolphin-virsci.md` |
| 08 | AI-Supervisor | Yunbo Long / 2026-03 | CS通用 | 兴趣→gap发现→双循环→共识写 world model | 论文公开 | `05-dolphin-virsci.md` |
| 09 | Biomni | Stanford SNAP (Leskovec) / 2025-05 | 生物医学 | 单智能体 规划-检索-执行-自检；E1/E2 双轨 | 完全开源 | `07-stanford-biomni.md` |
| 10 | Google Co-Scientist | Google Research/DeepMind / 2025-02 | 生物医学 | Supervisor 锦标赛进化（生成-反思-Elo-进化） | 闭源 Trusted Tester | `08-google-co-scientist.md` |
| 11 | FutureHouse Robin | FutureHouse 非营利 / 2026-05 Nature | 生物医学 | 文献→假设→筛选→实验→机制迭代（5 角色） | 部分开源 ether0+PaperQA2 | `09-futurehouse-robin.md` |
| 12 | TxAgent | Harvard Zitnik Lab / 2025-03 | 生物医学 | 推理-检索-调用-整合迭代，显式 trace | 完全开源 | `10-txagent-biomed.md` |
| 13 | Coscientist | CMU + Emerald Cloud Lab / 2023-12 Nature | 化学/材料 | 文献→规划→文档RAG→代码→云执行→分析 | 论文披露未开源 | `11-coscientist-cmu.md` |
| 14 | ChemCrow | EPFL + IBM RoboRXN / 2023 | 化学 | ReAct 思考→工具→观测→上机 | 开源 chemcrow-public | `12-chemcrow-epfl.md` |
| 15 | SciAgents | MIT LAMM / 2024 | 化学/材料 | 图谱采样→多 Agent 假说→Critic→检索→图谱增量 | 开源 SciAgentsDiscovery | `13-sciagents-mit.md` |
| 16 | Toronto SDL / ChemOS | U Toronto Acceleration Consortium | 化学/材料 | Design-Make-Test-Analyze 联邦 | ChemOS 开源 | `14-sdl-toronto-berkeley.md` |
| 17 | Berkeley A-Lab | LBNL + UC Berkeley (Ceder) / 2023-11 Nature | 化学/材料 | 计算筛选→配方→机器人固相→XRD→ARROWS3 | ARROWS3 开源 | `14-sdl-toronto-berkeley.md` + `22-cloud-synthesis.md` |
| 18 | MatterGen / MatterSim | Microsoft Research / 2024 | 化学/材料 | 扩散生成→MatterSim/DFT验证→Adapter 条件生成 | mattergen+mattersim 开源 | `15-mattergen-microsoft.md` |
| 19 | Bohrium + SciMaster + DeepModeling | 深势科技 / 2025-12 | 平台基础设施 | 能力调度→执行→信号回流→接口迭代（五层栈） | DeepModeling/SDK 开源 | `16-bohrium-scimaster.md` |
| 20 | Agent Laboratory | JHU Schmidgall / 2025-01 | 平台基础设施 | 文献→计划→实验三阶段串行 | MIT 开源 5.8k★ | `17-agent-laboratory-agentrxiv.md` |
| 21 | AgentRxiv | JHU / 2025-03 | 平台基础设施 | 跨 Lab 论文累积+检索复用 | 开源同库 | `17-agent-laboratory-agentrxiv.md` |
| 22 | Claw AI Lab (claw-code) | NTU/A*STAR/Moxin / 2025-05 | 平台基础设施 | 五层金字塔+仪表盘可控迭代 | Rust 开源 | `17-agent-laboratory-agentrxiv.md` |
| 23 | OpenAI Deep Research | OpenAI / 2025-02 | 平台基础设施 | 规划→检索→阅读→综合→再规划（迭代检索） | 闭源托管 | `18-deep-research-platforms.md` |
| 24 | Gemini Deep Research | Google / 2024-12 | 平台基础设施 | 同上，双浏览器+Workspace 私域 | 闭源托管 | `18-deep-research-platforms.md` |
| 25 | Perplexity Deep Research | Perplexity / 2025-02 | 平台基础设施 | 混合模型路由+双检索闭环 | 闭源托管 | `18-deep-research-platforms.md` |
| 26 | ManuSearch | 中国人民大学 / 2025-05 | 平台基础设施 | 三智能体透明协作检索推理 | MIT 开源 | `18-deep-research-platforms.md` |
| 27 | PaperBench | OpenAI / 2025-04 | 评估基准 | 复制论文→沙盒执行→rubric 裁判 | 完全开源 | `19-benchmarks-eval.md` |
| 28 | DeepResearch Bench I/II | 中科大 / 2025-06 & 2026-01 | 评估基准 | 任务→RACE/FACT 相对评分→榜单飞轮 | 完全开源 | `19-benchmarks-eval.md` |
| 29 | RE-Bench | METR / 2024-11 | 评估基准 | 工程任务→容器化执行→自动评分 | 完全开源 | `19-benchmarks-eval.md` |
| 30 | EpiBench | 2024-2025 | 评估基准 | 二值 rubric 诊断矩阵 | 完全开源 | `19-benchmarks-eval.md` |
| 31 | AutoNumerics | Haizhao Yang 团队 / 2026-02 arXiv:2602.17607 | AI4S物理 | 规划→多候选生成→coarse-to-fine→残差验证→择优 | 论文公开代码预告 | `20-physics-autonumerics.md` |
| 32 | PhysMaster | 上海交通大学 / 2025-12 arXiv:2512.19799 | AI4S物理 | 符号/数值混合→参数自适应→物理合理性校验 | 论文公开 | `20-physics-autonumerics.md` |
| 33 | FlowX / Flow360 | FlexCompute / 2024-25 | AI4S物理/CFD | AI前处理→经典求解→AI收敛诊断 | 商业部分 API | `20-physics-autonumerics.md` |
| 34 | Denario | AG2/LangGraph 社区 / 2025-10 | 跨学科 | idea→文献→plan→code→report 链式（Docker） | 架构可复现 | `21-denaro-rumi.md` |
| 35 | AstroPilot-AI | HSC/Rubin 天文社区 / 2024-25 | 天文 | 数据→视觉→LLM推理→调度→论文 | 方法公开 | `21-denaro-rumi.md` |
| 36 | Rumi (RUMI) | Subhansh/Decidr / 2025-26 | 跨学科 | 文献→图谱→矛盾检测→锦标赛→过滤 | GitHub 开源 服务下线 | `21-denaro-rumi.md` |
| 37 | GFlowNet Hypothesis | Mila/Bengio + IBM GT4SD / 2022-26 | 跨学科/假设生成 | 按 reward 采样→评估→reward 更新→重采样 | GT4SD 开源 | `21-denaro-rumi.md` |
| 38 | DigCat (Digital Catalysis Platform) | 大连化物所 / 2024 ChemRxiv | 催化 | 设计→云分发→合成→表征→回流（400k 库） | 论文公开 | `22-cloud-synthesis.md` |
| 39 | RoboRXN | IBM Research Europe / 2018-24 | 化学合成 | 目标→Transformer逆合成→机器人→贝叶斯优化 | 部分开放商业化 | `22-cloud-synthesis.md` |
| 40 | MIT Coley/Jensen/FutureHouse Agent Index | MIT ChemE / 2025-06 | 化学/平台 | AI设计→反应预测→机器人→HPLC→优化 | PyLabRobot 开源 | `23-misc-university-labs.md` |
| 41 | Caltech SARA / Genesis Mission | Caltech (Agapie) DOE资助 / 2024-25 | 材料/电化学 | 分层AI+主动学习建相图→电化学闭环 | 方法公开 | `23-misc-university-labs.md` |
| 42 | Oxford 自驱量子实验室 | Oxford Physics / 2024-25 | 量子物理 | 自然语言→代码→量子硬件→实时分析→决策 | 方法公开硬件私有 | `23-misc-university-labs.md` |
| 43 | Cambridge 自驱材料 + 化学语言 | Cambridge Sun 组 / 2024-25 | 化学/能源材料 | 反应预测（化学语言）→合成→表征→优化 | 论文公开 | `23-misc-university-labs.md` |
| 44 | ETH Zurich 实验室自动化 | ETH Sant Kumar + Yokogawa/Atinary / 2024-25 | 化学/生物/材料 | ML预测→机器人执行→回流迭代 | 平台商业化 | `23-misc-university-labs.md` |
| 45 | Toronto Matter Lab / Ada / AUTODIAL | U Toronto Aspuru-Guzik / 2024-25 CFREF $200M | 材料 | AI设计→CV机器人→表征→优化（10x 目标） | 部分公开 | `23-misc-university-labs.md` |
| 46 | Stanford SUNCAT 自主智能体 | Stanford SUNCAT / 2024-25 | 催化/材料 | 代理序列决策→surrogate+贝叶斯→DFT/XRD 闭环 | 论文公开 | `23-misc-university-labs.md` |

## 统计

- **总数**：46 条（去重后；A-Lab 在 14 与 22 共用，计 1 条，表格中重复标注便于溯源）
- **学科分布**：CS 8 | 生物医学 5 | 化学/材料/SDL 6 | 平台/基准 11 | 物理跨学科新兴 16
- **开源比例**：完全/部分开源 ~65%（30/46），闭源多为 Google/DeepMind/OpenAI 平台与云实验室硬件
- **验证方式**：全部经 `web_search` + `read`（arXiv html / 官网 / Nature / ChemRxiv / GitHub）交叉验证，来源见各 `.md` 末尾

## 可借鉴点 Top-10（跨 46 条提炼）

1. **单文件赛马+多候选择优**：Karpathy 5min 预算 + AutoNumerics 多离散化并行择优，组成"快筛+精排"两段式。
2. **锦标赛/多样性采样**：Co-Scientist Elo + GFlowNet 锦标赛抗 mode collapse，idea 阶段必备。
3. **文档即驱动/能力注册表**：Coscientist 向量化文档 + Bohrium Capability 契约，新硬件零代码接入。
4. **残差/守恒无监督验证**：AutoNumerics 残差自验证 + PhysMaster 物理 sanity check，无 ground truth 时仍可门控。
5. **知识图谱持久记忆**：Rumi/SciAgents 图谱增量 + A-Lab pairwise 数据库，失败路径显式剪枝。
6. **Docker/沙箱隔离**：Denario Docker + Claw anti-fabrication，harness 沙箱直接复用。
7. **XRD/表征自动解析**：A-Lab ML 判读是实验闭环瓶颈，判读自动化优先于执行自动化。
8. **双模型/双 keeper**：DigCat 数据+物理双更新 + Dolphin 数值/语义双 keeper，避免单信号过拟合。
9. **10x 压缩比北极星**：Toronto Matter Lab 10 年/$10M→1 年/$1M，为飞轮设量化目标。
10. **三级溯源+引用审计**：Bohrium source→section→claim + FACT/RACE 审计，贯穿检索-执行-综合全链路。

## 潜在坑 Top-8

1. 硬件可靠性（炉/臂/粉末堵塞）是 7×24 停机主因，需冗余与自恢复。
2. A-Lab/ChemCrow 类新颖性/安全性判定需可审计，XRD 原始数据与 GHS pre_filter 不可省。
3. 负样本稀缺导致模型乐观偏差，需显式采集失败实验。
4. 跨实验室/跨硬件复现需指纹校准，云设计≠本地可复现。
5. LLM 幻觉在合成规划与数据清洗环节高发，需检索/工具双重约束。
6. 评估主观性（新颖性/可发表性）易被互评污染，需 rubric + 人类外评双轨。
7. 商业平台/用量成本（ECL/RoboRXN/Atinary）对小团队门槛高，优先用 PyLabRobot 等开源抽象。
8. 单一基准过拟合（val_bpb/某 Bench），需 held-out 复测与多维 keeper。

---

*生成时间：2026-09-02 | 维护：channels/ 各文件为真相源，本表为索引视图，新增渠道时同步追加一行并更新统计。*
