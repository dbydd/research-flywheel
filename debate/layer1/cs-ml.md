# Layer 1 — CS / ML 自主科研系统可迁移设计原则

> 范围：基于 `channels/_index-cs.md` 及 `channels/01-karpathy-autoresearch.md` 至 `channels/05-dolphin-virsci.md` 共 5 个落地文件，覆盖 8 个系统。所有证据行标注系统名、文件路径与来源链接。每条原则区分来源事实与推断。

- 索引文件：`channels/_index-cs.md`
- 源文件：`channels/01-karpathy-autoresearch.md`、`channels/02-sakana-ai-scientist.md`、`channels/03-ai-researcher-hkuds.md`、`channels/04-cycle-researcher.md`、`channels/05-dolphin-virsci.md`
- 写入目标：`debate/layer1/cs-ml.md`（本文件）

---

## 原则 1 — 固定 wall-clock 预算赛马 + git keep/discard 状态机

- **证据**：Karpathy Autoresearch，文件 `channels/01-karpathy-autoresearch.md`，来源 https://github.com/karpathy/autoresearch ， https://developers.redhat.com/articles/2026/04/07/autoresearch-on-red-hat-openshift-ai-198-experiments-zero-intervention
- **机制**：限定可写集合（`train.py` 可变，`prepare.py` 只读），每次迭代 `mutate train.py → uv run train.py 固定 5 min wall-clock → 读 val_bpb → keep 则 commit / discard 则 revert`。外层 runner 设硬超时，超时后立即采样指标，未完成步丢弃。`progress.png` 与 `analysis.ipynb` 构成可视化闭环。
- **收益**：单一度量 `val_bpb` 在同预算下可比，天然 UCB 赛马，单 GPU 夜跑可达 96–100 次迭代。git 状态机提供可回滚与可审计轨迹，零人工干预下完成 198 实验得到 Red Hat 复现验证。
- **失效模式**：跨硬件预算不可比（H100 5 min ≠ Mac 5 min），需记录 `device_info + budget_seconds` 指纹。单文件锁死探索空间，跨文件协同创新被挡在门外。无语义评审时数值噪声易被误判为提升。
- **对 OMP/PI 工作区启示**：harness 设 `writable_allowlist` 与只读校验钩子，runner 统一硬超时与指标采集。每个赛道定义 `METRIC` 与方向，落盘 `channels/<id>/progress.png` 与 `log.md`。
- **事实 / 推断区分**：固定 5 min、git keep/discard、`prepare.py` 只读、Red Hat 198 实验为来源事实。夜跑赛马适合作为执行层默认栈属于推断，已在 `_index-cs.md` 螺旋飞轮建议中被归纳。

## 原则 2 — 异常回溯引导的局部修复

- **证据**：Dolphin（InternScience），文件 `channels/05-dolphin-virsci.md` 05-A 节，来源 https://arxiv.org/abs/2501.03916 ， https://github.com/InternScience/Dolphin
- **机制**：Coder 生成失败时不重写全文件。解析 `exception traceback` 定位局部块，仅修该块后 `py_compile + quick_run` 烟雾测试，再进入完整训练。修复上下文包含异常类型、栈帧与失败输入。
- **收益**：降低 token 成本与回归风险，保留已验证结构，缩短调试轮次。Dolphin 在此机制上实现 thinking→practice→feedback 无人工轮间干预的持续爬升。
- **失效模式**：对系统性错误（依赖缺失、数据管线错配）局部修陷入循环。traceback 指向不准时修错位置。
- **对 OMP/PI 工作区启示**：harness 的 coder 设 `repair_scope: local-first`，全局重写作为降级路径。runner 前置 `compile_check` 与 `minimal_run` 两层门控，失败产物携带 traceback 落盘供下一轮 prompt 直接复用。
- **事实 / 推断区分**：traceback 引导局部修复与模板机制为来源事实。local-first 优于全量重写的成本收益权衡为推断。

## 原则 3 — 显式 Experiment Manager + 树搜索而非线性队列

- **证据**：Sakana AI Scientist v2，文件 `channels/02-sakana-ai-scientist.md`，来源 https://arxiv.org/abs/2504.08066 ， https://github.com/SakanaAI/ai-scientist-v2
- **机制**：引入中心调度者 Experiment Manager，维护 `ideas.jsonl` 树（父子指针、分数、状态）。每轮按 UCB 胜率展开 top-k 节点，控制 `max_children_per_node` 与 `early_stop_patience`，负责去重、优先级与资源分配。v1 线性流水线在 v2 中被树搜索替代。
- **收益**：单 idea 派生多条实验路径，资源向高潜力分支集中，支持跨 domain 泛化。树结构让 `tree.json` 成为中期记忆。
- **失效模式**：自由生成方差增大，剪枝不当浪费预算。token 与调用量随分支数放大。
- **对 OMP/PI 工作区启示**：harness 实现 `channels/<id>/tree.json` 与 UCB 调度器，配置 `branch_budget` 与 `prune_threshold`。探索期用短预算海选，收敛期切长预算复测。
- **事实 / 推断区分**：Experiment Manager 与渐进式 tree search 为 v2 论文事实。UCB 具体实现与预算分层策略为结合 Karpathy 预算思想的推断。

## 原则 4 — VLM 图表语义评审小循环

- **证据**：Sakana AI Scientist v2，文件 `channels/02-sakana-ai-scientist.md`，来源 https://arxiv.org/abs/2504.08066
- **机制**：Writer 产出 LaTeX 与图表初版后，追加 VLM 审图步骤，检查分辨率、图例、坐标标题、信息密度等像素级可读性。不通过则回写修改指令，形成 writer↔reviewer 小循环，再进入编译。
- **收益**：把图表从能跑提升到能发表，补齐纯 LLM 评审的视觉盲区。
- **失效模式**：VLM 对美学偏好引入噪声，过度迭代导致图表美化掩盖方法缺陷。
- **对 OMP/PI 工作区启示**：harness 在写作阶段后插入 `vlm_review` 门控，输出结构化 `chart_feedback.json`。配置 `max_chart_iters` 防止无界打磨。
- **事实 / 推断区分**：VLM 介入图表美化与内容复核为来源事实。将其封装为独立门控属于推断。

## 原则 5 — 实现成功率硬门控置于写作之前

- **证据**：HKUDS AI-Researcher，文件 `channels/03-ai-researcher-hkuds.md`，来源 https://arxiv.org/abs/2505.18705 ， https://github.com/hkuds/ai-researcher
- **机制**：Writing Agent 之前设 `impl_success == true` 硬门。runner 返回 `exit_code + metric_exists` 双校验，跑不通的代码不进入写作。Quality Checker 按 rubric 自评，未达阈值回退至 hypothesis 或 implementation 环，形成内循环。
- **收益**：节省写作 token 与人类评审时间，阻断幻觉稿件外流。Scientist-Bench 双轨（Level-1 guided 测执行力，Level-2 open 测自主探索）让门控效果可度量。
- **失效模式**：门槛过严过滤掉需多轮调试才能跑通的早期探索。全链路方差大时单一环节失败拖垮全流程。
- **对 OMP/PI 工作区启示**：harness 对每环设 `max_retries` 与降级路径（简化假设后重跑）。`bench.json` 分轨统计成功率，guided 与 open 分开报告。
- **事实 / 推断区分**：实现成功率门控与 Scientist-Bench 双轨为来源事实。降级路径与双校验设计为对失效模式的推断补充。

## 原则 6 — 作者-审稿双智能体飞轮 + 真实数据偏好训练

- **证据**：CycleResearcher / CycleReviewer，文件 `channels/04-cycle-researcher.md`，来源 https://arxiv.org/abs/2411.00816 ， https://github.com/zhu-minjun/Researcher
- **机制**：Researcher 产出稿件，Reviewer 模拟多审稿人打分与逐条意见，意见以结构化 JSON 回写驱动修订。Review-5k 与 Research-14k 支撑迭代偏好训练（DPO/RL），MAE 相对单人类审稿人降低 26.89%，模拟均分 5.36。
- **收益**：审稿一致性可训练提升，开源权重即插即用，模拟分可作为与 val_bpb 并列的语义 keeper。
- **失效模式**：模拟分不等于真实接收（距接收稿 5.69 仍有差距），复杂理论与新颖性判断偏弱，易给增量工作高分。数据时间窗口影响跨域泛化。
- **对 OMP/PI 工作区启示**：harness 拆分 `author` 与 `reviewer` 双 agent，共享任务不同 rubric，落盘 `reviews/<round>.json`。设 `preference_tuning: true` 增量训练，模拟分需校准并配人类抽检。
- **事实 / 推断区分**：双循环结构、Review-5k 规模、MAE -26.89%、5.36 模拟分为来源事实。双 keeper 语义与校准抽检为推断。

## 原则 7 — 双 keeper 并行：数值 keeper 与语义 keeper 联合裁决

- **证据**：综合 Karpathy（val_bpb 数值 keeper，`channels/01-karpathy-autoresearch.md`）、HKUDS Quality Checker（`channels/03-ai-researcher-hkuds.md`）、CycleReviewer 模拟分（`channels/04-cycle-researcher.md`），索引归纳见 `channels/_index-cs.md` 螺旋飞轮取舍建议
- **机制**：每轮迭代同时评估 `metric: val_bpb / benchmark` 与 `metric: reviewer_score / rubric`。任一不达标即 discard。数值 keeper 负责可复现性能，语义 keeper 负责方法论与写作质量。
- **收益**：降低单 keeper 过拟合风险，数值提升掩盖方法缺陷的路径被语义闸门拦截。
- **失效模式**：双阈值过严导致探索停滞。两信号冲突时仲裁逻辑不清。
- **对 OMP/PI 工作区启示**：harness 配置 `keepers: [numeric, semantic]` 与各自阈值，冲突时走 PI 裁决。收敛期加 held-out 复测。
- **事实 / 推断区分**：各系统单 keeper 机制为来源事实。双 keeper 并行架构为跨系统综合推断。

## 原则 8 — 链式文献组织 + 双维属性排序检索

- **证据**：ResearchAgent（KAIST），文件 `channels/05-dolphin-virsci.md` 05-C 节，来源 https://arxiv.org/abs/2404.07738 ， https://github.com/JinheonBaek/ResearchAgent ；Dolphin topic/task 排序见同文件 05-A 节
- **机制**：以核心论文为锚，学术图谱扩展引用/被引/共现链，按领域进展链式排序而非扁平堆叠。叠加 Dolphin 的 `topic + task` 双维打分与概念知识库实体增强。多 ReviewingAgents 按人类偏好 rubric 打分驱动 `refine_rounds: 3` 迭代精炼。
- **收益**：降低 LLM 上下文噪声，提升想法的相关性与可追溯性。链式结构让评审反馈有明确锚点。
- **失效模式**：图谱覆盖与时效性直接决定天花板。热门论文偏置易致局部最优，多 reviewer 反馈矛盾需校准。
- **对 OMP/PI 工作区启示**：harness 检索器标配 `chain_sort + dual_score(topic, task)`，输出 `literature_chain.md`。想法生成设固定精炼轮次，每轮必经评审。
- **事实 / 推断区分**：链式文献与多 ReviewingAgents 为来源事实。落盘形态与精炼轮次为推断。

## 原则 9 — PI 制虚拟会议 + 干湿边界门控

- **证据**：VirSci / Virtual Lab（Stanford Zou Group），文件 `channels/05-dolphin-virsci.md` 05-B 节，来源 https://www.biorxiv.org/content/10.1101/2024.11.11.623004v1 ， https://github.com/zou-group/virtual-lab
- **机制**：PI Agent 拆解目标、排期、主持虚拟会议、裁决分歧。领域 Agents（免疫/计算生物/ML）与 Critic Agent 各司其职，共享计算管线（ESM + AlphaFold-Multimer + Rosetta 封装为 tool）。92 候选中 2 强结合的湿实验验证由人类执行，结果回流至 PI。
- **收益**：多学科协作可控，工具链封装让 agent 能力可调用。干湿分离明确人机边界，计算误差不直接外溢为不可逆物理成本。
- **失效模式**：跨学科幻觉需 critic 与人类双重校验。规模化至数千 agent 的通信一致性未验证。
- **对 OMP/PI 工作区启示**：harness 引入 PI agent，会议纪要落盘 `meetings/<round>.md`。对需物理执行、外部发布、资金、生物安全的操作设 `human_in_the_loop: true` 强制确认。工具封装为 `tool: structure_pred` 等可调用接口。
- **事实 / 推断区分**：PI 会议、共享管线、92 选 2 湿实验为来源事实。`human_in_the_loop` 泛化为通用门控为推断。

## 原则 10 — 持久世界模型 + U 标记验证门控 + 共识写入

- **证据**：AI-Supervisor，文件 `channels/05-dolphin-virsci.md` 05-D 节，来源 https://arxiv.org/abs/2603.24402
- **机制**：维护 `world-model.json` 不确定性知识图谱，边标记 `U=0 已验证 / U=1 未验证`。结构化空白发现按方法→模块→benchmark→gap 分解。自纠正发现循环追问为何某模块成败，跨域开发循环靶向失败模块。共识委员会要求 ≥2 独立 agent 复现才提交至图谱。
- **收益**：共享记忆避免重复造轮子，U 标记强制先验证再构建，共识降低单 agent 幻觉污染。
- **失效模式**：冷启动噪声大，共识过滤可能筛掉小众新颖发现。跨域机制迁移适配成本高。
- **对 OMP/PI 工作区启示**：harness 设三级记忆：短期 `meetings/<round>.md`、中期 `tree.json`、长期 `world-model.json`。每条边强制 U 标记，`U=0` 才能作为后续假设前提。`gap_discovery.py` 按结构化管线执行。
- **事实 / 推断区分**：世界模型、U 标记、双自纠正循环、共识机制为来源事实。三级记忆分层为结合 `_index-cs.md` 建议的推断整合。

## 原则 11 — 可编程研究组织与域可插拔 Spec

- **证据**：Karpathy `program.md` 可编程组织（`channels/01-karpathy-autoresearch.md`，来源 https://github.com/karpathy/autoresearch）与 HKUDS 域可插拔 specs（`channels/03-ai-researcher-hkuds.md`）
- **机制**：Karpathy 把 agent 行为从代码抽到 Markdown skill 文件，人改 `program.md` 即可改团队拓扑。HKUDS 把扩散/VQ/GNN/RecSys 抽象为 `domain/specs/*.yaml`（数据集、基线、指标），agent 按 spec 选工具。
- **收益**：组织拓扑与领域能力解耦，换赛道改配置而非改代码。
- **失效模式**：`program.md` 过度抽象导致 agent 行为漂移。spec 覆盖不全时新域接入成本陡增。
- **对 OMP/PI 工作区启示**：harness 提供 `template/program.md` 三档预设（单 agent / 双 agent reviewer / 多 agent swarm）与 `domain/specs/` 目录。PI 按 spec 自动装配工具链。
- **事实 / 推断区分**：`program.md` 与域 specs 为来源事实。三档预设与自动装配为推断。

---

## 领域边界

### 边界 1 — 单 GPU 短预算循环的适用边界

Karpathy 5 min 赛马在 nanochat / TinyStories 等低熵、单文件可表达的任务上验证有效。面向 VirSci 的蛋白管线（ESM/AF/Rosetta + 湿实验）或需跨文件协同的系统级创新，固定短预算与单文件作用域直接失效，需分级解锁与长预算复测。harness 需按任务类型切换预算分层。

### 边界 2 — 模拟评审与真实同行评审的差距边界

CycleReviewer 模拟分 5.36 与 preprint 5.24 接近，距接收稿 5.69 仍有差距。Sakana v2 workshop 超阈值不等同主会接收，HKUDS Scientist-Bench 题目抽自 SOTA 论文存在泄露风险。harness 对外宣传需区分 tier，模拟分仅作内 keeper，外部对齐依赖人类抽检与 held-out 投稿。

### 边界 3 — 自由生成与模板约束的方差边界

Sakana v2 去模板自由生成提升泛化，代价是失败率与成本上升。Dolphin 模板与 ResearchAgent 链式约束降低方差，代价是限制探索空间。HKUDS 全链路方差与 AI-Supervisor 冷启动噪声进一步放大该权衡。harness 需在 `allow_free_codegen` 与模板约束间设可调旋钮，并在 runner 前置强校验门控。

---

## 来源清单

- https://github.com/karpathy/autoresearch
- https://autoresearch.lol
- https://developers.redhat.com/articles/2026/04/07/autoresearch-on-red-hat-openshift-ai-198-experiments-zero-intervention
- https://arxiv.org/abs/2408.06292
- https://arxiv.org/abs/2504.08066
- https://sakana.ai/ai-scientist
- https://github.com/SakanaAI/ai-scientist-v2
- https://arxiv.org/abs/2505.18705
- https://github.com/hkuds/ai-researcher
- https://arxiv.org/abs/2411.00816
- https://github.com/zhu-minjun/Researcher
- https://arxiv.org/abs/2501.03916
- https://github.com/InternScience/Dolphin
- https://www.biorxiv.org/content/10.1101/2024.11.11.623004v1
- https://github.com/zou-group/virtual-lab
- https://arxiv.org/abs/2404.07738
- https://github.com/JinheonBaek/ResearchAgent
- https://arxiv.org/abs/2603.24402

## 方法说明

来源事实来自 5 个 channel 文件及其中引用的 arXiv/GitHub/官网链接，经文件内 URL 验证。推断指跨系统综合、harness 落地形态、参数化建议与边界外推，已在每条原则内单独标注。
