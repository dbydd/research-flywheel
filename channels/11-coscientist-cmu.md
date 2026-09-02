# 11 — Coscientist (CMU / Emerald Cloud Lab)

| 维度 | 内容 |
|------|------|
| 机构 | Carnegie Mellon University, Gabe Gomes 课题组 + Emerald Cloud Lab (ECL) |
| 论文/发布时间 | Nature 624, 570-578 (2023.12.20) `10.1038/s41586-023-06792-0` |
| 循环形态 | 文献检索 → 合成规划 → 文档查询 → 代码生成 → 云实验室执行 → 数据分析 → 迭代优化 |
| 智能体架构 | 多 LLM 模块化：Planner (GPT-4 主控) + Web Searcher (GPT-4) + Documentation Search (Embedding RAG) + Code Execution (Docker) + Automation (ECL/Opentrons API) |
| 工具链 | Google Search API, Python Docker, ada embedding 向量检索, Opentrons Python API, ECL Symbolic Lab Language (SLL) |
| 度量 | 6 类任务全通过；Suzuki/Sonogashira 钯催化偶联反应优化成功；7 种化合物合成评分中 Web Searcher-GPT-4 达满分 5 分 (4 种)；千次反应/周末 级别的扩展验证 |
| 开源状态 | 代码未开源，论文 + SI 完整披露 prompt 与架构；依赖 ECL 付费云实验室与 GPT-4 API |
| 潜在坑 | API 文档幻觉、加热振荡模块代码错误、纯 LLM 合成规划对非普及分子失败率高 |

## 闭环形态详解

Coscientist 将科学意图翻译为机器可执行工作流。上层用户输入自然语言指令如 "perform multiple Suzuki reactions"，Planner 将其分解为四个命令：GOOGLE、PYTHON、DOCUMENTATION、EXPERIMENT。GOOGLE 调用独立的 Web Searcher LLM 将 prompt 转为搜索 query 并回灌结果；DOCUMENTATION 通过 ada embedding 对 Opentrons 或 ECL SLL 文档做向量检索；PYTHON 在隔离 Docker 中计算实验参数；EXPERIMENT 将生成的代码下发到硬件执行。分析结果后 Planner 再决策下一轮，形成完整闭环。论文验证了从文献合成规划、硬件文档导航、云实验室高层指令执行、低层液体处理精确控制，到多硬件联动与基于历史数据的优化求解共 6 类任务。

## 智能体架构

采用中心化 Planner + 工具子代理模式。Planner 是 GPT-4 ChatCompletion 实例，系统 prompt 模块化定义可用 action space。每个子模块可独立用不同模型：Web Searcher 实测对比 GPT-4/GPT-3.5/Claude 1.3/Falcon-40B，GPT-4 显著领先。PYTHON 与 EXPERIMENT 两个模块不依赖 LLM，直接执行代码或调用硬件 API，Planner 通过观察返回结果决定是否重试或修正。这种分层让推理与执行解耦，便于替不同硬件替换 Documentation 模块。

## 工具链

- **搜索**：Google Search API + LLM 自主 query 构造与网页浏览
- **文档 RAG**：OpenAI ada embedding + 距离检索，将超长 Opentrons/ECL 文档切块召回
- **计算**：Docker 隔离的 Python 执行器，支持修正执行错误后的自修复
- **自动化**：Opentrons OT-2 Python Protocol API（本地液体处理）与 ECL SLL（远程云实验室 HPLC 等）双适配，论文展示通过补充 SLL 文档即可让 GPT-4 学会新 DSL

## 硬件抽象

核心创新是把硬件文档当作可检索知识而非硬编码驱动。Documentation 模块将 API 文档向量化，Planner 通过自然语言描述任务意图，检索到相关函数签名与示例后生成可执行代码。Opentrons 侧生成 Python protocol，ECL 侧生成 SLL 程序。抽象层级分两档：高层 SLL 语义化指令与低层 OT-2 精确移液指令均可生成，验证了对不同抽象粒度的泛化。后续扩展仅需投喂新仪器文档，无需重训。

## 安全约束

Coscientist 未内置独立安全校验层，依赖 GPT-4 自身对危险请求的拒答与 ECL 云端的人工审核。论文讨论部分提及团队参与美国政府 AI 安全行政令咨询，意识到自主化学的双重用途风险。相比 ChemCrow 显式集成安全工具，Coscientist 的安全更多靠云实验室的操作边界与权限控制，而非模型内的 GHS 规则检查。这是可借鉴的反例：安全不应后置于硬件执行侧。

## 调度

调度隐含在 Planner 的 ReAct 循环中，每次只执行一个 COMMAND，根据观察决定下一步。云实验室侧由 ECL 的队列系统承接 SLL 任务，支持 24/7 远程排队。千次反应/周末的吞吐表明其批处理能力来自 ECL 的并行硬件而非单机串行。未披露复杂 DAG 调度或资源争用处理，推断为单线程任务队列。

## 失败处理

最具说服力的案例是加热振荡模块：Planner 首次生成错误代码，执行失败后读取报错信息，重新检索文档、修正脚本并成功执行。PYTHON 模块同样具备错误回显自修复能力。这种 "执行-观测-检索-重写" 循环是其鲁棒性来源。但论文也指出 ibuprofen 等复杂合成仍需引入 Reaxys/SciFinder 等反应数据库或 Chain-of-Thought/Tree-of-Thought 才能提升，说明纯重试对知识缺口无效。

## 度量与评估

6 类任务均设明确通过标准。合成规划任务用 1-5 分人工评分（5 分需详细且化学准确的步骤与用量），Web Searcher-GPT-4 在 7 种化合物中 4 种满分，显著优于无检索基线。硬件任务以代码能否无错运行并产出预期产物为判据。Suzuki-Miyaura 反应优化展示了从文献到实测的端到端优化能力。

## 核心可借鉴点

1. **文档即驱动**：将仪器文档向量化而非手写适配器，新硬件接入成本极低。
2. **Planner + 子 LLM 分工**：搜索任务用独立 LLM 实例，避免主控上下文膨胀。
3. **代码自修复闭环**：把执行报错原文回灌 LLM，结合文档重写，成功率显著提升。
4. **双抽象层验证**：同时打通高层云语言与低层移液 API，证明架构与硬件无关。

## 潜在坑

- 文档质量决定上限，API 文档不全或过时会导致幻觉代码。
- 对非普及分子的合成规划仍 hallucinate，需外挂反应数据库。
- 安全约束后置，真实部署需补显式化学品管控层。
- ECL 依赖导致可复现性受限，本地实验室迁移需重写调度。

## OMP 硬件/仿真 Capability 抽象映射

- 将每台仪器抽象为 `capability: { name: "ot2_pipette", input_schema: {...}, doc_ref: "opentrons_v2.md", executor: "docker|ecl" }`，Documentation 模块即 capability 的检索与 prompt 注入层。
- 仿真与真机同接口：`EXPERIMENT` 命令下同时注册 `sim_ot2` 与 `real_ecl` 两个 capability，调度器根据 `dry_run` flag 路由，仿真相中的错误同样回灌 Planner 做自修复训练。
- 硬件能力声明包含 `safety_tags` 与 `requires_approval` 字段，未通过 GHS 校验的 capability 调用在 OMP 层被拦截，而非依赖 LLM 自觉。

> 来源验证：Nature 论文全文 + CMU 官方新闻稿 + Chemistry World 报道，交叉确认千次反应扩展与架构图 Fig.1。
