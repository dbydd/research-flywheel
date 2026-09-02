# CS 自主科研渠道总览（对比表）

> 覆盖 8+ 系统，拆至 5 个落地文件。每个系统均经 web_search + arXiv/GitHub/官网 read 验证，关键事实带 URL。

## 文件索引
| # | 文件 | 系统 | 一句话定位 |
|---|------|------|-----------|
| 01 | `01-karpathy-autoresearch.md` | Karpathy Autoresearch | 单文件 + 5 分钟硬预算的极简赛马机 |
| 02 | `02-sakana-ai-scientist.md` | Sakana AI Scientist v1/v2 | 端到端论文工厂，tree search + VLM 审图 |
| 03 | `03-ai-researcher-hkuds.md` | HKUDS AI-Researcher / Novix | 全流程自治 + Scientist-Bench 双轨评测 |
| 04 | `04-cycle-researcher.md` | CycleResearcher / CycleReviewer | 研究-评审双循环 + 偏好训练飞轮 |
| 05 | `05-dolphin-virsci.md` | Dolphin / VirSci / ResearchAgent / AI-Supervisor | 闭环三段式 + PI 制虚拟实验室 + 文献链精炼 + 持久世界模型 |

## 对比总表

| 维度 | 01 Karpathy | 02 Sakana v1/v2 | 03 HKUDS | 04 Cycle | 05-A Dolphin | 05-B VirSci | 05-C ResearchAgent | 05-D AI-Supervisor |
|------|-------------|-----------------|----------|----------|--------------|-------------|--------------------|--------------------|
| **机构 / 时间** | Karpathy 个人, 2026-03, https://github.com/karpathy/autoresearch | Sakana AI × UBC/Vector/Oxford, v1 2024-08 arXiv:2408.06292, v2 2025-04 arXiv:2504.08066, https://sakana.ai/ai-scientist | HKUDS, 2025-05 arXiv:2505.18705, https://github.com/hkuds/ai-researcher | 交大/微软等, 2024-10 arXiv:2411.00816 ICLR2025, https://github.com/zhu-minjun/Researcher | 上科/上海AI Lab, 2025-01 arXiv:2501.03916 ACL2025, https://github.com/InternScience/Dolphin | Stanford Zou, 2024-11 biorxiv 2024.11.11.623004, https://github.com/zou-group/virtual-lab | KAIST, 2024-04 arXiv:2404.07738 NAACL2025, https://github.com/JinheonBaek/ResearchAgent | Yunbo Long, 2026-03 arXiv:2603.24402 |
| **循环形态** | 单循环：mutate train.py → 5min 跑 → val_bpb keep/discard | 线性→树：idea → experiment-manager tree search → executor → VLM reviewer → writer → 投稿 | 文献→假设→实现→实验→写作，Level-1/2 双轨 | 双循环：Researcher 产出 ↔ Reviewer 审稿，偏好信号 RL 迭代 | 思考→实践→反馈 闭环，异常回溯局部修复 | PI 拆解→多学科 agents 会议→共享管线 ESM/AF/Rosetta→湿实验回流 | 核心论文→图谱扩展→链式文献→多 Reviewer 迭代精炼 | 兴趣→文献合成→结构化 gap→自纠正发现/开发双循环→共识写入 World Model |
| **智能体角色** | 单 Agent（program.md 定义），人管组织 Agent 管实验 | Ideator / Exp Manager / Executor / Analyzer / Writer / LLM+VLM Reviewer | Literature / Hypothesis / Implementation / Experiment / Writing / Quality Checker；Novix 增强记忆与迁移 | CycleResearcher（作者） + CycleReviewer（审稿团） + 偏好训练协调器 | Idea / Coder-Debugger / Executor / Analyzer | PI + 免疫/计算生物/ML/Critic + 人类湿实验 | ResearchAgent + 多 ReviewingAgents（人类偏好对齐） | Synthesizer / Gap Discoverer / Discovery Prober / Mechanism Searcher / Consensus Committee |
| **工具链** | PyTorch 单 GPU, uv, val_bpb, git, progress.png | LLM 自由代码生成, VLM 审图, LaTeX, Semantic Scholar | 学术图谱, 多域 specs（扩散/VQ/GNN/RecSys）, LaTeX | 开源 LLM 后训练, Review-5k/Research-14k, MAE 评测, 权重发布 | dolphin_utils, launch_dolphin, topic/task 排序检索, MLE-bench | ESM + AlphaFold-Multimer + Rosetta, LLM 会议, 云+湿实验 | 学术图 + 概念知识库, 偏好对齐 rubric | 不确定性知识图谱 (U=0/1), 结构化 gap pipeline, 跨域机制库 |
| **评测方式** | 在线 val_bpb keep/discard + analysis.ipynb 离线 + Red Hat 198 实验稳定性 | LLM/VLM 内评 + ICLR workshop 人类外评（v2 一篇超阈值）+ 第三方 arXiv:2502.14297 | Scientist-Bench 双轨（guided/open）+ 实现成功率 + 稿件质量 + 域泛化 | Reviewer MAE -26.89% vs 人类单审 + 模拟均分 5.36 vs preprint 5.24 vs 接收 5.69 | 多 topic 爬升曲线 + MLE-bench 子集 + 与 SOTA 对标 | 计算打分排序 + 92 设计湿实验验证（2 强结合） | 人类+模型双评（新颖/清晰/有效） + 跨域泛化 | 图谱覆盖/准确/收敛 + gap 精确率 + 与人类 supervisor 对比 |
| **开源与复现成本** | MIT 95k★ 13k fork, 单 H100 夜跑 100 次, Mac fork 可用 | v1/v2 均开源, 单篇数十迭代 中高成本 | 主库开源 Novix 待发布, 中等 | 代码+数据+权重全开源, 推理单卡 训练多卡 | 完全开源 低-中 | 管线开源 成本高（含湿实验） | 开源 低成本 | 论文为主 代码待发布 中高 |
| **可借鉴点（harness）** | 单文件变异+git keep/discard；固定 5min 预算；program.md 可编程组织；单一度量；夜跑可视化 | Exp Manager tree search；去模板自由生成+门控；VLM 审图；真实投稿外评；provenance 水印 | 双轨 bench；域可插拔 specs；实现成功门控；自检阈值回退；benchmark 社区打包 | 作者↔审稿双 agent；偏好 DPO 迭代；5k 真实审稿数据；模拟分 keeper；开源权重即插 | 异常回溯局部修；topic/task 双维检索；反馈即 prompt | PI 会议纪要；tool 封装 ESM/AF；干湿边界门控 | 链式文献排序；多 reviewer rubric；想法 refine 3 轮 | 持久 world-model.json；U 标记验证门控；结构化 gap；共识 ≥2 复现才写入 |
| **坑 / 局限** | 跨硬件不可比；单文件锁死探索；易过拟合 val_bpb | 幻觉与统计不严谨；自由生成方差大；workshop≠主会 | SOTA 题目泄露；全链路方差大；Novix 仅预告 | 模拟≠真实评审；开源模型天花板；数据偏见 | 模板瓶颈；检索偏热门；缺独立评审 | 跨学科幻觉；管线误差传导；规模化未验证 | 增量式新颖；图谱时效；reviewer 不一致 | 冷启动噪声；共识过滤新颖；跨域适配成本 |

## 螺旋飞轮取舍建议（给 research-flywheel harness）

1. **默认栈**：Karpathy 的 5min 赛马（执行层） + Dolphin 的局部修复 + ResearchAgent 的链式检索 + CycleReviewer 的模拟评审 + HKUDS 的实现门控 + AI-Supervisor 的 world model 记忆。六件套覆盖“快、准、稳、记”。
2. **预算分层**：探索期用 5min 短预算快速海选，收敛期切长预算做 held-out 复测，避免 val_bpb 过拟合。
3. **双 keeper**：数值 keeper（val_bpb / benchmark）与语义 keeper（reviewer_score / rubric）并行，任一不达标即 discard。
4. **人机边界**：VirSci 的干湿分离思想泛化为 `human_in_the_loop` 标签，凡涉及外部发布、资金、生物安全的操作强制人工确认。
5. **记忆分级**：短期 `meetings/<round>.md`（PI 会议）+ 中期 `tree.json`（Sakana 树）+ 长期 `world-model.json`（AI-Supervisor 图谱），三级落盘避免上下文丢失。

## 来源清单（关键事实 URL）
- https://github.com/karpathy/autoresearch / https://autoresearch.lol / https://developers.redhat.com/articles/2026/04/07/autoresearch-on-red-hat-openshift-ai-198-experiments-zero-intervention
- https://arxiv.org/abs/2408.06292 / https://arxiv.org/abs/2504.08066 / https://sakana.ai/ai-scientist / https://github.com/SakanaAI/ai-scientist-v2
- https://arxiv.org/abs/2505.18705 / https://github.com/hkuds/ai-researcher / https://neurips.cc/virtual/2025/poster/116385
- https://arxiv.org/abs/2411.00816 / https://github.com/zhu-minjun/Researcher / https://wengsyx.github.io/Researcher/
- https://arxiv.org/abs/2501.03916 / https://github.com/InternScience/Dolphin / https://aclanthology.org/2025.acl-long.1056
- https://www.biorxiv.org/content/10.1101/2024.11.11.623004v1 / https://github.com/zou-group/virtual-lab
- https://arxiv.org/abs/2404.07738 / https://github.com/JinheonBaek/ResearchAgent
- https://arxiv.org/abs/2603.24402 / https://arxiv.org/html/2603.24402v1
