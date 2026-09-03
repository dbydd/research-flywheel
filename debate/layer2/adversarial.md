# Layer 2 — 对抗性审查（Adversarial Review）

> 身份：第二层交叉辩论员。输入：`debate/layer1/cs-ml.md`、`bio.md`、`chem-materials.md`、`platform.md`、`physics-crossdomain.md` + `channels/README.md` 全量 46 条索引。任务：逐条找冲突、过度泛化、证据薄弱处、成本与安全盲区。每争议给出 主张 / 支持证据 / 反证或限制 / 裁决条件 / 最小保留原则。输出 8-12 条经反驳后共识原则与 5 条应拒绝的设计冲动。只新增本文件。
> 方法：交叉比对各域可迁移原则的机制、收益、失效模式三列，识别同一维度上相反处方。将来源事实与推断分离复核，弱证据标记原始口径与样本量。成本与安全以物理执行、长时间占用、不可逆操作为判定锚点。裁决条件写成可执行门控而非口号。
> 写入时间：2026-09-02

---

## 争议总表（10 项）

### 争议 1 — 固定 wall-clock 预算赛马可泛化至全域

- **主张**：以单一 wall-clock 预算（如 5 min）+ 单一度量 `val_bpb` 赛马可作为自主科研执行层默认栈，并推广到湿实验与重仿真赛道。
- **支持证据**：`cs-ml.md` 原则 1。Karpathy Autoresearch 固定 5 min wall-clock、git keep/discard、Red Hat 复现 198 实验夜跑 96-100 迭代（来源事实）。`platform.md` 原则 9 的防伪闸门与 `physics-crossdomain.md` 原则 2 coarse-to-fine 均依赖分级预算思想。
- **反证或限制**：`cs-ml.md` 边界 1 自述 H100 5 min ≠ Mac 5 min，单文件锁死跨文件协同失效。`chem-materials.md` 原则 5/10 与 `physics-crossdomain.md` 原则 9：A-Lab 单次烧结 4 h、Toronto Ada 需数小时表征、MatterGen DFT 分支与实验室分支以天周计。`bio.md` 原则 01/08：Virtual Lab 94% 时间在工具计算、Robin 10 周端到端。固定短预算直接外推至湿实验赛道属于跨尺度泛化错误。
- **裁决条件**：预算声明必须携带 `device_info + budget_seconds + cost_type(compute|synthesis|assay)` 指纹。工作区按任务类型切换分层预算：`coarse` 短预算海选（计算侧）、`fine` 长预算复测（精仿/真机），湿实验侧以 `assay_time` 与 `material_cost` 另计预算，未披露指纹的提升不计入 keep。
- **保留的最小原则**：预算分层赛马。保留超时硬截断与指标落盘，丢弃“单一 wall-clock 统一定价”。

### 争议 2 — 自由生成树搜索与多样性采样无条件优于模板约束

- **主张**：去模板自由生成 + 树搜索 + 多样性采样（GFlowNet 按 reward 正比、Elo 锦标赛）天然更优，应作为 idea 层默认。
- **支持证据**：`cs-ml.md` 原则 3 Experiment Manager 树搜索派生多路径、原则 8 GFlowNet 多样性。`bio.md` 原则 06 Elo 锦标赛与 test-time scaling 正相关、原则 07 自博弈辩论提升新颖性。`physics-crossdomain.md` 原则 7-8 图谱锦标赛与按 reward 正比采样。
- **反证或限制**：`cs-ml.md` 边界 3 与原则 2：Sakana v2 自由生成方差与 token 放大、失败率上升，Dolphin 局部修复依赖模板降低回归风险。`bio.md` 边界 03：Co-Scientist Elo 评估仅 15 目标、11 人评，Goodhart 风险与早期偏差放大。`chem-materials.md` 原则 10：网格搜索被主动学习替代的前提是 reward 可建模，稀疏场景采样退化为随机。`platform.md` 边界 3：PaperBench 人类 PhD 41% 显著高于最强 agent 21%，自由探索在长周期研发上仍落后。成本曲线显式劣化：分支数线性推高调用与失败处理开销。
- **裁决条件**：仅在满足三者时启用自由树搜索：(a) `reward_model` 可度量且与外部锚点做过校准；(b) `branch_budget + prune_threshold + early_stop_patience` 三参显式配置；(c) 前置 `compile_check + minimal_run` 门控通过。探索期短预算海选，收敛期切模板约束复测。未达 distinct high-reward modes 阈值不进入执行。
- **保留的最小原则**：有约束的多样性。保留带剪枝与门控的锦标赛，丢弃无预算无校准的自由膨胀。

### 争议 3 — 语义 keeper（模拟分 / VLM 审图 / Elo）可独立裁决 keep/discard

- **主张**：CycleReviewer 模拟分、VLM 图表评审、Elo 分可作为与 `val_bpb` 并列的语义 keeper 独立决定 keep。
- **支持证据**：`cs-ml.md` 原则 4 VLM 像素级审图、原则 6 Reviewer MAE -26.89% 模拟均分 5.36、原则 7 双 keeper 联合裁决。`bio.md` 原则 06 Elo 与 GPQA 正相关。`platform.md` 原则 10 RACE 相对参考评分 PAR 71.33% 超人类互一致。
- **反证或限制**：`cs-ml.md` 边界 2：模拟 5.36 接近 preprint 5.24、距接收 5.69 仍有差距，workshop 超阈值 ≠ 主会接收。`bio.md` 边界 03：Elo 与湿实验成功率不一致，小样本统计效力不足。`chem-materials.md` 边界 3：EvaluatorGPT 偏好流畅但 hallucinate 的回答。`platform.md` 原则 8 FACT 审计显示引用可达性随时间衰减，Bench II 召回显著低于呈现。模拟信号与真实接收/湿实验成功存在系统 gap。
- **裁决条件**：双 keeper 必须分层：`numeric: val_bpb/benchmark/assay_metric` 为硬门，`semantic: reviewer/VLM/Elo` 为软门。语义 keeper 仅在通过校准后计分：与 held-out 人类抽检或湿实验锚点做回归校准，公布校准误差带。冲突时走 PI 裁决，收敛期加 held-out 复测。未校准的模拟分仅用于排序，不用于 discard。
- **保留的最小原则**：双 keeper 有主次与校准。保留语义信号作排序与拦截，丢弃模拟分独立一票否决。

### 争议 4 — 注册表规模化（150-211 工具）零成本复利

- **主张**：统一注册表 + ToolRAG 检索即可支撑百级工具一键编排，新增能力零成本接入。
- **支持证据**：`bio.md` 原则 04 Biomni 150 工具 / TxAgent 211 工具、ToolRAG Top-K 召回、92.1% 离线分数。`platform.md` 原则 1 最小契约注册表、原则 2 三域分面。`chem-materials.md` 原则 1 doc 向量化接入。
- **反证或限制**：`bio.md` 边界 02：检索精度随规模下降，异构返回标准化复杂，105 包版本冲突推高复现成本，E2 污染注册表。`chem-materials.md` 原则 8 MatterSim 覆盖 ≤20 原子外推未知。`platform.md` 原则 1 失效模式：契约粒度过粗致路由歧义，成本声明失真致预算超支。`physics-crossdomain.md` 边界 2：600 sq ft 8 炉 3 臂与 $200M Consortium 证明重资产不可零成本复刻。规模化收益以治理成本为上限。
- **裁决条件**：注册表准入强制最小契约 `I/O Schema + env snapshot + cost + failure_modes + safety_tags`。分层治理：`E1` 稳定轨强校验、`E2` 扩展轨审核合入。路由留痕可回放，成本声明纳入审计，召回未命中时阻断执行而非猜测调用。治理投入未到位前封顶规模。
- **保留的最小原则**：有治理的注册表。保留契约化与检索分面，丢弃无治理无限扩张。

### 争议 5 — 文档即驱动可零代码接入任意硬件/仿真

- **主张**：向量化仪器文档 RAG 注入 prompt 即可让 LLM 学会新 DSL，新硬件零代码接入。
- **支持证据**：`chem-materials.md` 原则 1 Coscientist ada embedding 检索 SLL 文档生成可执行 protocol，补充文档即学会新 DSL。`platform.md` 原则 1 能力契约、`physics-crossdomain.md` 原则 10 PyLabRobot 硬件抽象。
- **反证或限制**：`chem-materials.md` 原则 1/4 失效模式：文档不全过时致幻觉函数签名，召回噪声增幻觉面，知识缺口型失败纯重试无效。`bio.md` 边界 01：Biomni 与 TxAgent 无自带湿实验闭环，物理执行依赖人类。`platform.md` 边界 1：UniLabOS 机器人/表征仪器虚拟化依赖真实硬件抽象与协议约束，纯软件复刻虚假可执行性。`physics-crossdomain.md` 边界 2：跨硬件指纹差异致配方不可复现。
- **裁决条件**：接入流程固化为 `文档→向量化→validate 分支→硬件指纹校准→sim 分支对照` 五步。`validate(procedure)->{valid,errors[]}` 在符号层拦截，`execute` 前强制 `safety pre_filter`。新 capability 必须提供 `doc_ref + doc_version + example_protocols`，缺一不可调度。
- **保留的最小原则**：文档驱动 + 符号校验 + 指纹校准。保留 RAG 加速接入，丢弃零验证直通真机。

### 争议 6 — 安全可由 LLM 自觉或通用拒答覆盖

- **主张**：在 prompt 中呼吁 LLM 自律或依赖模型拒答即可覆盖实验室安全。
- **支持证据**：`chem-materials.md` 原则 3 汇总：Coscientist 依赖 GPT-4 拒答与 ECL 云端人工审核被标记为反例。
- **反证或限制**：`chem-materials.md` 原则 3：ChemCrow 每次合成前强制 GHS 工具评估、A-Lab 源头过滤不稳定目标，两者均为显式工具约束。`bio.md` 原则 11 human-gate、`platform.md` 原则 9 沙盒防伪、`physics-crossdomain.md` 原则 9 design-execute 分离均指向能力层硬约束。`channels/README.md` 潜在坑 2 指出 GHS pre_filter 不可省。训练数据过滤不完整漏过新型危险组合，提示层安全不可审计。
- **裁决条件**：安全作为 capability 的 `pre_filter` 在编排层强制执行：声明 `safety_tags + requires_approval`，`execute` 前必调 `chem.safety.ghs` 等校验，命中阈值进人工确认队列。安全校验结果写入 `tool-call.json` 审计链。无 pre_filter 的链路禁止物理执行。
- **保留的最小原则**：安全是路由层硬门控。保留 pre_filter 与人工确认，丢弃 prompt 自律。

### 争议 7 — 知识图谱 / 世界模型 / pairwise 库可无差别替代

- **主张**：知识图谱、世界模型 `world-model.json`、pairwise 反应库、Elo 谱系可互换，任选其一即获持久记忆复利。
- **支持证据**：`cs-ml.md` 原则 10 三级记忆与 U 标记共识写入。`chem-materials.md` 原则 5 A-Lab pairwise 剪枝 80%、原则 7 SciAgents 图谱共享记忆。`bio.md` 原则 06 假设谱系、`physics-crossdomain.md` 原则 7 Rumi 图谱承载矛盾与演化。
- **反证或限制**：`cs-ml.md` 原则 10 失效：冷启动噪声大、共识过滤筛掉小众新颖发现。`chem-materials.md` 原则 7：图谱构建成本高、膨胀致检索与推理成本飙升、无物理验证时纸面创新。`bio.md` 边界 03：Robin 单案例泛化不足，图谱外推需外部锚点。`physics-crossdomain.md` 原则 6：Rumi 商业服务下线暴露单点依赖。成本与场景不匹配时图谱为负收益。
- **裁决条件**：记忆分层按需选用：短期 `meetings/<round>.md` + 中期 `tree.json`/`elo-board` + 长期 `world-model.json`/`knowledge_graph`。启用图谱需同时满足：(a) 跨运行复用预期 > 单次构建成本；(b) 边强制 `U=0 已验证 / U=1 未验证` 标记，`U=0` 才能作假设前提；(c) ≥2 独立 agent 共识或 XRD/assay 原始数据支撑。否则用轻量 pairwise 表 + 结构化日志。
- **保留的最小原则**：分层记忆 + U 标记 + 共识写入。保留可审计的持久化，丢弃无门槛全量图谱化。

### 争议 8 — 仿真即硬件，`score(structure)` 可替代实验判定成功

- **主张**：MatterSim/DFT 等仿真分数可直接判定材料发现成功，生成器只认统一 `score` 契约。
- **支持证据**：`chem-materials.md` 原则 8 MatterSim MAE 36 meV/atom、0-5000K/0-1000 GPa、快 3-5×、1024 结构批量打分。`physics-crossdomain.md` 原则 1-3 残差与守恒量无监督验证。`platform.md` 原则 9 容器化复现。
- **反证或限制**：`chem-materials.md` 边界 2：预训练 ≤20 原子外推未知、DFT 0K 近似假阳性、A-Lab 63%→67%→70% 校正链显示计算精度直接决定浪费。`chem-materials.md` 原则 8/10：理论稳定但动力学/缺陷致无法合成、非晶化致 XRD 失效。`physics-crossdomain.md` 边界 1：残差小≠解正确、伪守恒、`platform.md` RE-Bench 与 A-Lab correction（Chemistry World 质疑 36-43 新材料多为已知相）指向“成功”需可审计。仿真-实验 gap 持续放大。
- **裁决条件**：分层验证路由 `mattersim(快速阈值) → dft(精确阈值) → lab(合成阈值)`，三层阈值显式配置于 `capability.policy`。仿真仅用于排序与剪枝，成功判定需附 XRD 原始数据 + Rietveld 精修报告或 assay 原始读数。DFT/MatterSim 误差以不确定度通道显式传播。
- **保留的最小原则**：分层验证 + 成功可审计。保留统一 `score` 接口便于调度，丢弃仿真成功等同发现成功。

### 争议 9 — 全自主 7×24 闭环优于人机分叉点介入

- **主张**：端到端无人类闭环吞吐最高，应追求全自主。
- **支持证据**：`chem-materials.md` 原则 6 DigCat 全球联邦异地并行、`platform.md` 原则 9 沙盒无人值守、Biomni 沙盒自检循环。A-Lab 17 天连续运行约 21 实验/天。
- **反证或限制**：`bio.md` 原则 11 与 `chem-materials.md` 边界 1：Virtual Lab 人类仅在分叉点否决追加目标、Robin 物理执行依赖人类实验室，干湿分离明确人机边界。`physics-crossdomain.md` 原则 9 A-Lab 硬件故障占失败大头、粉末堵塞与炉漂需冗余自恢复。`platform.md` 边界 1 真实实验硬件与事务安全边界、边界 2 私域与计费治理边界均要求人工兜底。不可逆/高成本/生物安全操作无人类门控时风险外溢。
- **裁决条件**：默认自治，仅三类操作强制 `human_in_the_loop: true`：(a) 物理执行与外部发布；(b) 资金/合规/生物安全相关；(c) 成本超过 `WATCHDOG.yml` 阈值。门控触发时 PI 议程驱动裁决，执行层自治日志落 `meetings/<round>.md` 与 `artifact://` 可回放。
- **保留的最小原则**：分叉点人机协同。保留自治吞吐，丢弃无门控全自主。

### 争议 10 — 论文与报告向量检索可自举形成研究飞轮

- **主张**：将论文/报告/workflow 向量化后检索复用，可形成跨任务复利与自举评估，无需外部参考。
- **支持证据**：`platform.md` 原则 5 AgentRxiv SentenceTransformer 检索、MATH-500 协作 +13.7%。`bio.md` 原则 06 Elo 自举、`cs-ml.md` 原则 6 DPO 偏好训练。`physics-crossdomain.md` 原则 6 Denario 文献节点复用。
- **反证或限制**：`platform.md` 原则 5 失效：低质内容污染检索库并放大错误、embedding 漂移致召回不稳。`bio.md` 边界 03 与 `cs-ml.md` 边界 2：Elo/模拟分与真实成功/接收不一致，小样本评估统计效力有限。`chem-materials.md` 边界 3：LLM 互评污染、成功认定争议需附原始数据。`platform.md` 原则 8 FACT 揭示召回为短板（Bench II 召回 39.98）、引用衰减。纯自举闭环放大偏差。
- **裁决条件**：检索复利必配质量闸门：(a) 三级溯源 `source→section→claim` 与 FACT 双指标（有效引用数 + 引用准确率）校验；(b) RACE 式相对参考评分，参考报告与 rubric 作者共创；(c) 人类抽检与外部锚点（湿实验、held-out 投稿、human PhD 基线）定期校准。相似度单一排序禁止。
- **保留的最小原则**：有审计的检索复利。保留向量检索与跨任务复用，丢弃无闸门自举。

---

## 经反驳后共识原则（10 条）

> 每条为争议裁决后可直接写入工作区规范的最小可执行原则。推断已折叠为门控参数与落盘契约。

### 共识 1 — 指纹化分层预算执行

- **表述**：所有执行声明 `device_info + budget_seconds + cost_type` 指纹。计算侧用 coarse/fine 两级（粗筛快、细验准），湿实验侧用 `assay_time + material_cost` 另计。超时硬截断，未完成步丢弃并采样已产指标。
- **来源锚点**：Karpathy 5 min 赛马与 Red Hat 198 实验（`cs-ml.md` 原则 1）、AutoNumerics coarse-to-fine（`physics-crossdomain.md` 原则 2）、A-Lab 4 h 烧结与 Robin 10 周（`chem-materials.md`/`bio.md`）。
- **门控**：`writable_allowlist` + `trial_grid/validate_grid` 分级超时 + `channels/<id>/progress.png` 与 `log.md` 落盘。
- **证伪信号**：跨硬件预算不可比时指标虚高；单预算类型下长任务饥饿。

### 共识 2 — 主次双 keeper 与外部校准

- **表述**：数值 keeper（`val_bpb / benchmark / assay`）为主硬门，语义 keeper（reviewer / VLM / Elo）为辅软门。语义信号必经 held-out 人类抽检或湿实验锚点校准后参与排序，冲突走 PI 裁决。
- **来源锚点**：`cs-ml.md` 原则 7 双 keeper、原则 4 VLM、原则 6 模拟分；`bio.md` 原则 06 Elo；`platform.md` 原则 10 RACE/FACT。
- **门控**：`keepers: [numeric, semantic]` 分阈值 + `preference_tuning` 校准带 + held-out 复测。
- **证伪信号**：模拟 5.36 接近 5.24 远离 5.69（`cs-ml.md` 边界 2）、Elo 与湿实验不一致。

### 共识 3 — 契约化注册表与分层治理

- **表述**：每个 capability 声明最小契约 `I/O Schema + env snapshot + cost + failure_modes + safety_tags`，版本化可回放。`E1` 稳定轨强校验，`E2` 扩展轨审核合入，成本与溯源以 capability ID 关联。
- **来源锚点**：Bohrium 注册表（`platform.md` 原则 1）、Biomni 150 / TxAgent 211 工具（`bio.md` 原则 04）、doc 向量化（`chem-materials.md` 原则 1）。
- **门控**：`template/tool-registry.json` 单一真相源 + ToolRAG Top-K 前置检索 + 召回失败阻断。
- **证伪信号**：检索精度下降、105 包冲突、E2 污染。

### 共识 4 — 能力层 validate → execute + 安全 pre_filter 硬门控

- **表述**：安全与可行性在能力编排层强制校验：`validate(procedure)->{valid,errors[]}` 符号拦截，`execute` 前必调 `safety pre_filter`（如 GHS），命中阈值进人工确认。LLM 自觉与拒答不计为安全措施。
- **来源锚点**：ChemCrow GHS 与 A-Lab 源头过滤（`chem-materials.md` 原则 3）、Coscientist 反例、UniLabOS 协议约束（`platform.md` 边界 1）。
- **门控**：`capability` 声明 `safety_tags/requires_approval` + `tool-call.json` 审计链。
- **证伪信号**：校验器不完备漏过不可行配方；Coscientist 类依赖拒答的链路。

### 共识 5 — 结构化错误回灌的局部优先修复

- **表述**：执行失败携带 `exception traceback + stderr + doc_hints` 结构化回灌。修复范围 local-first，`py_compile + quick_run` 烟雾测试后再进全量训练或真机，全局重写为降级路径。
- **来源锚点**：Dolphin traceback 局部修复（`cs-ml.md` 原则 2）、Coscientist/ChemCrow 验证-修正循环（`chem-materials.md` 原则 4）。
- **门控**：`repair_scope: local-first` + `compile_check/minimal_run` 双门 + 失败产物落盘复用。
- **证伪信号**：系统性错误（依赖缺失、管线错配）陷入局部循环；截断噪声致误诊。

### 共识 6 — 分层持久记忆与 U 标记共识写入

- **表述**：三级记忆 `meetings/<round>.md`（短期）+ `tree.json`/`elo-board`（中期）+ `world-model.json`/`knowledge_graph`（长期）。长期边强制 `U=0/U=1` 标记，`U=0` 才能作后续前提，共识需 ≥2 独立 agent 或原始数据支撑。无跨运行复用预期时用轻量 pairwise 表替代图谱。
- **来源锚点**：AI-Supervisor U 标记与共识（`cs-ml.md` 原则 10）、A-Lab pairwise 剪枝 80%（`chem-materials.md` 原则 5）、SciAgents/Rumi 图谱（`chem-materials.md` 原则 7 / `physics-crossdomain.md` 原则 7）、Elo 谱系（`bio.md` 原则 06）。
- **门控**：`memory_store` capability + `gap_discovery.py` 结构化管线 + 版本化落盘。
- **证伪信号**：冷启动噪声、图谱膨胀、单点服务下线（Rumi 2026-07-24）。

### 共识 7 — 仿真分层路由与成功可审计

- **表述**：`mattersim(快) → dft(准) → lab(真)` 三层路由，`score(structure)` 统一契约但阈值分层配置。仿真用于排序剪枝，成功判定必附原始数据与精修报告（XRD + Rietveld / assay 读数），误差以不确定度通道传播。
- **来源锚点**：MatterGen/MatterSim 分层验证（`chem-materials.md` 原则 8-9）、A-Lab XRD 自动解析瓶颈（`chem-materials.md` 原则 10）、AutoNumerics 残差验证（`physics-crossdomain.md` 原则 3）、A-Lab correction 争议（`chem-materials.md` 边界 3）。
- **门控**：`capability.policy: {mattersim,dft,lab}` 三阈值 + `analyze` 能力显式建模资源争用 + 主动学习选点。
- **证伪信号**：DFT 0K 假阳性、≤20 原子外推、非晶化致判读失效、负样本稀缺致乐观偏差。

### 共识 8 — 分叉点人机协同

- **表述**：默认自治，高风险操作强制人类在分叉点介入：物理执行/外部发布/资金合规/生物安全/超阈值成本。人类反馈以自然语言注入 Meta-review，策略对齐在 Team Meeting 层完成，执行层自治。
- **来源锚点**：Virtual Lab PI 会议与 human-gate（`bio.md` 原则 01/11）、Robin 物理依赖人类（`bio.md` 原则 08）、`platform.md` 边界 1 事务安全、`physics-crossdomain.md` 原则 9 设计执行分离。
- **门控**：`WATCHDOG.yml: human-gate/human-feedback` + `hub` 分叉点视图 + 会议纪要落盘。
- **证伪信号**：人类延迟成瓶颈、追加目标与系统探索冲突。

### 共识 9 — 可检验性约束下的多样性采样

- **表述**：idea 层多样性采样以可检验性为前提：reward 可建模且与外部锚点校准，按 reward 正比抗 mode collapse，distinct high-reward modes 未达阈值不晋升执行，多候选并行经 skeptic/critic 评审。
- **来源锚点**：GFlowNet 按 reward 正比（`physics-crossdomain.md` 原则 8）、Elo 锦标赛与自博弈辩论（`bio.md` 原则 06-07）、Experiment Manager 树搜索（`cs-ml.md` 原则 3）、Rumi 锦标赛（`physics-crossdomain.md` 原则 7）。
- **门控**：`num_modes/diversity_weight/reward_model` 参数化 + 分歧度阈值 + 不可证伪拦截。
- **证伪信号**：reward 稀疏噪声致退化为随机、热门文献偏置致局部最优。

### 共识 10 — 三级溯源与沙盒防伪双闸门

- **表述**：检索片段/抽取事实/装配工作流显式链接 `source→section→claim`，报告发布前必过 FACT 双指标（有效引用数 + 引用准确率）与沙盒 anti-fabrication（只读 controller + NaN/Inf + smoke test）。引用不可验证直接阻断发布。
- **来源锚点**：Bohrium 三级溯源与 DeepResearch Bench FACT（`platform.md` 原则 8/10）、Claw/RE-Bench 沙盒（`platform.md` 原则 9）、Denario Docker 隔离（`physics-crossdomain.md` 原则 6）。
- **门控**：`eval` 在隔离 workspace 注入只读 controller + 容器化复现 + 引用审计自动化。
- **证伪信号**：引用可达性衰减、自动化校验误判、沙盒逃逸与资源竞争。

---

## 应拒绝的 5 条设计冲动

### 拒绝 1 — 用 prompt 呼吁替代安全 pre_filter

- **冲动**：在系统提示词中加入安全守则，依赖 LLM 自觉与拒答覆盖合成/生物安全。
- **为何拒绝**：ChemCrow 与 A-Lab 的显式工具约束与源头过滤被验证有效，Coscientist 依赖拒答被标记为反例（`chem-materials.md` 原则 3）。提示层不可审计，新型危险组合易漏过，失败时无拦截证据链。
- **替代**：能力层 `safety pre_filter + requires_approval` 硬门控，审计落 `tool-call.json`。

### 拒绝 2 — 单一 wall-clock（如 5 min）统一定价全域执行

- **冲动**：将 Karpathy 5 min 赛马直接作为湿实验与重仿真赛道的计费与 keep 依据。
- **为何拒绝**：跨硬件不可比、单文件锁死探索、湿实验以小时周计（`cs-ml.md` 边界 1、`chem-materials.md` 原则 5/10、`bio.md` 原则 01）。统一定价导致长任务饥饿与短任务虚高。
- **替代**：共识 1 指纹化分层预算，`coarse/fine/assay` 分池核算。

### 拒绝 3 — 无校准模拟分独立裁决 keep/discard

- **冲动**：以 CycleReviewer 5.36、Elo、VLM 分直接决定论文或假设是否 keep，省去人类抽检与湿实验锚点。
- **为何拒绝**：模拟分与接收分 5.69 有 gap、小样本 Elo 与湿实验不一致、EvaluatorGPT  hallucinate 偏好（`cs-ml.md` 边界 2、`bio.md` 边界 03、`chem-materials.md` 边界 3）。Goodhart 风险显式存在。
- **替代**：共识 2 主次双 keeper + 校准带 + PI 仲裁 + held-out 复测。

### 拒绝 4 — 无治理扩张工具注册表至百级规模

- **冲动**：先追求 150-211 工具接入广度，契约与审核后补。
- **为何拒绝**：`bio.md` 边界 02 与 `platform.md` 原则 1 失效模式显示检索精度下降、异构标准化复杂、105 包冲突、E2 污染、成本声明失真致超支。规模化收益以治理为上限。
- **替代**：共识 3 最小契约 + E1/E2 分层 + 版本化回放，治理未到位前封顶。

### 拒绝 5 — 仿真分数等同实验成功，无需原始数据审计

- **冲动**：MatterSim/DFT 高分即宣布新材料发现，XRD/assay 原始数据与精修报告后补或免除。
- **为何拒绝**：≤20 原子外推、DFT 0K 假阳性、非晶化判读失效、A-Lab correction 新颖性争议（`chem-materials.md` 边界 2-3、`physics-crossdomain.md` 边界 1）。负样本稀缺致乐观偏差，成功口径不可审计。
- **替代**：共识 7 分层路由 + 成功可审计，仿真仅排序，判定必附原始数据。

---

## 对 OMP/PI 工作区的最小落地清单

- `task` Contract 段写入 capability 最小契约与 `safety_tags/requires_approval`，`hub` 按契约路由与鉴权。
- 执行层统一 `validate → safety pre_filter → execute → analyze` 四段，`validate` 符号拦截、`analyze` 显式建模炉与表征资源争用。
- 预算与记忆分层：`trial_grid/validate_grid` 分级超时、`meetings/tree/world-model` 三级落盘、`U` 标记与共识写入。
- 评估双闸：FACT 三级溯源 + 沙盒防伪，RACE 相对参考评分，裁判与 rubric 版本入 trace。
- 人机边界：`WATCHDOG.yml` 定义 `human-gate` 阈值，物理/发布/合规/超成本必经 PI 会议裁决。

---

## 证据与推断分界说明

- 来源事实行均可回溯至 `debate/layer1/*.md` 标注的文件路径与链接：Karpathy 5 min 与 198 实验、`cs-ml.md` 原则 1/6/10；Biomni 150 / TxAgent 211 / Elo 锦标赛、`bio.md` 原则 04/06；ChemCrow GHS / A-Lab pairwise 剪枝 80% / MatterSim 36 meV、`chem-materials.md` 原则 1/3/5/8；Bohrium 注册表 / FACT 90.24% / PAR 71.33%、`platform.md` 原则 1/8/10；AutoNumerics coarse-to-fine / Rumi 图谱 / A-Lab correction、`physics-crossdomain.md` 原则 2/3/7/9。
- 推断部分为跨域综合与工作区落地形态推断，已在争议裁决条件与共识门控中参数化，需在 OMP 实测中以 held-out 与校准误差带验证。

## 产出信息

- 写入：`debate/layer2/adversarial.md`（本文件）
- 未改动：`debate/layer1/*.md`、`channels/*.md`、`channels/README.md`
- 覆盖争议：10 项。共识原则：10 条。拒绝冲动：5 条。
