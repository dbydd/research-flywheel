# 生物医学自主科研渠道汇总（06-10）

> 覆盖 Stanford Virtual Lab、Biomni、Google Co-Scientist、FutureHouse Robin、TxAgent 五个代表性系统；每行对应 `channels/06-10` 详述文件。

| # | 系统 | 机构 | 发布时间 | 循环形态 | 智能体分工 | 工具/数据库 | 湿实验/临床闭环 | 度量 | 开源 | 核心可借鉴点（OMP 映射） | 潜在坑 |
|---|------|------|----------|----------|------------|-------------|------------------|------|------|--------------------------|--------|
| 06 | Virtual Lab | Stanford + CZ Biohub（J. Zou） | 2024-11 bioRxiv | 双层会议：Team Meeting 定策略 + Individual Meeting 执行；计算-湿实验大闭环 | PI + 免疫学/计算/结构专家 + Critic + 人类 high-level 反馈 | ESM、AlphaFold-Multimer、Rosetta、Biopython；湿实验 ELISA/SPR | 是：92 纳米抗体，2 个对 JN.1/KP.3 提升且保留 ancestral 结合 | 结合亲和力、pLDDT、Rosetta 能量、功能性比例 | 论文开放，代码未完整开源 | 双层会议抽象→`local://` 会议纪要；PI+Critic 对偶；工具链声明式 workflow | 角色漂移、工具误差累积、湿实验成本高 |
| 07 | Biomni | Stanford SNAP（Leskovec/Huang） | 2025-05 bioRxiv | 单智能体 规划-检索-执行-自检；E1/E2 双轨生态 | A1 Planner + 检索模块 + 沙盒执行层 + Eval1 基准 | 150 工具 / 59 库 / 105 软件；scanpy、RDKit、PubMed 等 | 否：计算基准与真实任务回放，无自带湿实验 | HLE 17.3%（+402%）、DbQA 74.4%、SeqQA 81.9%、8 真实任务 | 完全开源（snap-stanford/Biomni） | 注册表驱动、代码即计划、E1/E2 双轨、Benchmark 即生态 | 工具选择困难、环境冲突、无湿闭环 |
| 08 | Co-Scientist | Google Research/DeepMind/Cloud | 2025-02 博客+arXiv | Supervisor 异步锦标赛进化：生成-反思-锦标赛-Elo-进化-元复盘；test-time scaling | Supervisor + Generation/Reflection/Ranking/Proximity/Evolution/Meta-review | Gemini 2.0、Web Search、专用模型、Elo 自评 | 是：AML 细胞系、肝类器官、cf-PICI 独立复现 | Elo 与 GPQA 正相关、专家新颖性偏好、剂量响应 p<0.01 | 闭源，Trusted Tester 限量 | 假设谱系+Elo、锦标赛即评估、自博弈辩论、异步扩展 | 供应商锁定、Goodhart、评估样本小 |
| 09 | Robin | FutureHouse（非营利） | 2026-05 Nature | 多智能体端到端：文献→假设→筛选→实验设计→分析→机制迭代 | Crow/Falcon/Owl/Phoenix/Finch + Robin 编排；ether0 化学模型 | PaperQA2、ether0（24B 开放权重）、FDA 库、RPE/RNA-seq 管线 | 是：RPE 吞噬 1.9x、ABCA1 3x，10 周完成 | 生物学效应、时长 10 周、200x 效率、ether0 基准 | 部分开源（PaperQA2+ether0） | 角色分工具、重定位优先、机制实验自动提出、trace 审计 | 物理依赖人类、单案例泛化、编排复杂 |
| 10 | TxAgent | Harvard Zitnik Lab | 2025-03 arXiv | 推理-检索-调用-整合迭代，显式 trace + Finish 门控 | ToolUniverse + 微调 LLM + ToolRAG + ToolGen | 211 工具（FDA 全量、Open Targets、HPO 等） | 否：3168 任务离线基准，需临床复核 | 92.1%（5 基准）、456 个性化场景、工具选择准确率 | 开源（mims-harvard/TxAgent） | ToolRAG 检索、显性 trace、ToolGen、活数据源、Finish 门控 | 数据授权、异构标准化、迁移微调成本 |

## 横向对比要点

- **闭环深度**：Virtual Lab / Co-Scientist / Robin 具备真实湿实验闭环，适合作为飞轮参考的端到端范式；Biomni / TxAgent 停留在计算验证，适合作为干实验与决策支持层。
- **架构范式**：Virtual Lab（会议制）、Biomni（注册表+代码计划）、Co-Scientist（锦标赛进化）、Robin（角色分工具编排）、TxAgent（检索式工具规模化）五种范式互补，可按任务类型路由。
- **开源可用性**：Biomni 与 TxAgent 可直接复用；ether0/PaperQA2 可作为共享锚点；Virtual Lab 与 Co-Scientist 以思路复现为主。
- **度量成熟度**：Biomni 与 TxAgent 基准最完整，Co-Scientist 的 Elo 自评与专家偏好对齐验证为亮点，Robin 的效率宣称需谨慎引用。

## OMP Workspace 统一落地建议

1. **注册表统一**：以 `template/tool-registry.json` 为单一工具真相源，Biomni 的 150 工具分类与 TxAgent 的 ToolRAG 检索叠加使用。
2. **会议与锦标赛双轨**：探索类任务走 Virtual Lab 会议制，假设生成类任务走 Co-Scientist 锦标赛制，通过 `hub` 路由。
3. **重定位优先策略**：复用 Robin 的 FDA 已批准库优先与 TxAgent 的活数据源，降低首轮验证成本。
4. **Trace 审计**：所有渠道强制 `reasoning.md` + `tool-call.json` + `meeting/trace` 三件套，落 `local://` 与 `artifact://`。
5. **基准先行**：在 `research-flywheel/eval/` 建立 10 任务回归集，新增 channel 必须跑分后合入。

> 详述见 `06-stanford-virtual-lab.md`、`07-stanford-biomni.md`、`08-google-co-scientist.md`、`09-futurehouse-robin.md`、`10-txagent-biomed.md`。
