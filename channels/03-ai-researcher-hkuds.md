# 03 — HKUDS AI-Researcher / Novix：全流程自治 + Scientist-Bench 基准

## 元信息
- **机构 / 作者**：香港大学 HKUDS 实验室，核心作者 Jiabin Tang, Lianghao Xia, Zhonghang Li, Chao Huang
- **发布时间**：预印 2025-05-24 arXiv:2505.18705，NeurIPS 2025 poster，OpenReview 讨论页同步开放，代码库 hkuds/ai-researcher 活跃更新
- **核心 URL**：
  - 论文：https://arxiv.org/abs/2505.18705 与 HTML 版 https://arxiv.org/html/2505.18705v1
  - 代码：https://github.com/hkuds/ai-researcher
  - NeurIPS 页：https://neurips.cc/virtual/2025/poster/116385
  - OpenReview：https://openreview.net/forum?id=kQWyOYUAC4
  - Novix 预告（PhD-level AI-Scientist 扩展）：https://x.com/huang_chao4969/status/1961120989015937287
  - AlphaXiv 镜像：https://www.alphaxiv.org/abs/2505.18705

## 时间线
- 2025-05：AI-Researcher 预印发布，主张从文献综述到可投稿手稿的零/少人工干预全链路，并发布 Scientist-Bench 评估套件
- 2025-06~09：HKUDS 迭代实现，增加对扩散模型、向量量化、图神经网络、推荐系统等多域覆盖；Novix 作为博士级增强版预告，定位更强的自主探索与跨域泛化
- 2025-11：NeurIPS 2025 poster 展示，Scientist-Bench 被社区用作第三方横评基准之一

## 循环形态（文字图）
```
[ 文献综述 Agent ] ──► [ 假设生成 ] ──► [ 算法实现 Agent ] ──► [ 实验执行 ]
        ▲                      │                    │                │
        │                 Scientist-Bench           │           指标采集
        │                 Level-1 有指令            │                ▼
        │                 Level-2 开放探索     代码仓库          [ 结果分析 ]
        │                      │                    │                │
        └──────────── [ Manuscript Agent ] ◀────────┘                │
                        LaTeX + 引用                  ◄─────────────┘
                              │
                        自检与投稿就绪度打分
```
双轨评测是其设计亮点：Level-1 给显式研究指令测执行力，Level-2 隐去指令测自主选题与探索能力。

## 智能体角色
- **Literature Agent**：检索、聚类、提炼 SOTA 脉络与空白点，输出结构化综述
- **Hypothesis Agent**：基于空白点生成可验证假设与技术路线
- **Implementation Agent**：把路线翻译为算法与代码，处理依赖与超参
- **Experiment Agent**：跑训练/评测、记录日志、做消融
- **Writing Agent**：组装 Introduction / Method / Experiments / Conclusion，管理引用与图表
- **Quality Checker**：对实现成功率与稿件质量做自动打分，决定是否重做某环

Novix 在此之上增强为 PhD-level 自主科学家，强调更长的上下文记忆与跨任务迁移。

## 工具链
- **检索与知识**：学术图谱 + 自建论文库，支持按主题/任务属性排序
- **代码执行**：Python 栈，任务相关框架按 Scientist-Bench 赛道切换（扩散模型、VQ、GNN、RecSys 等）
- **评测**：Scientist-Bench 覆盖引导式与开放式两档，指标含实现成功率、稿件质量分、创新性与可复现性
- **写作**：LaTeX 模板 + 引用管理器，配自动编译与格式检查

## 评测方式
- **Scientist-Bench**：抽取 SOTA 论文构造真题，Level-1 测“按指令做”，Level-2 测“自己找方向做”，两档分数分别报告
- **实现成功率**：代码能否跑通并产出对齐预期的指标
- **稿件接近人类水平度**：人工与模型双评，论文强调“接近人类质量”
- **域泛化**：在 4+ 子领域上重复上述流程，检验跨域稳定性

## 开源与复现成本
- **开源状态**：主库 hkuds/ai-researcher 开源，含文档、benchmark、Slack/Discord 社区入口；Novix 细节以预告为主，代码待发布
- **复现成本**：中等。单赛道需 LLM API + 实验算力，Scientist-Bench 的 Level-2 开放探索成本高于 Level-1；建议先跑 Level-1 单域（如 RecSys）验证链路，再扩至多域。

## 可借鉴点（落地到 harness 机制）
1. **Scientist-Bench 双轨制**：harness 为每个赛道配置 `level: guided | open-ended`，guided 轨给显式指令与参考论文，open 轨只给主题，分别统计成功率；落盘 `channels/<id>/bench.json`。
2. **按域可插拔的工具链**：把扩散/VQ/GNN/RecSys 抽象为 `domain/specs/*.yaml`（数据集、基线、指标），Agent 按 spec 选工具，避免为每个域硬编码。
3. **实现成功率门控**：在“写稿前”设硬门 `impl_success == true`，跑不通的代码不进入写作阶段，节省 token 与人类评审时间；实现为 runner 返回 `exit_code` + `metric_exists` 双校验。
4. **质量自检再投稿**：Writing Agent 后加 Quality Checker，对照 rubric 自评，不达阈值自动回退到 hypothesis 或 implementation 环，形成内循环。
5. **社区与基准共生**：把 benchmark、文档、讨论社区打包发布，降低复现摩擦；harness 可复用其 benchmark 题目作为回归集。

## 坑 / 局限
- **基准题目抽自 SOTA 论文，存在泄露与过拟合风险**：若 LLM 预训练已见过原论文，Level-1 分数虚高；harness 需对题目做时间切分（仅用 cutoff 后论文）。
- **全链路自治的方差大**：任一环节（尤其实现）失败会拖垮全流程，论文报告的“接近人类”多为挑选后结果；harness 需对每环设 `max_retries` 与降级路径（简化假设后重跑）。
- **Novix 尚处预告阶段**：宣称的 PhD-level 能力缺乏可验证产物，引用时需注明为 roadmap 而非已验证结果。

## 复现指引（最小）
```bash
git clone https://github.com/hkuds/ai-researcher && cd ai-researcher
pip install -r requirements.txt
# 按 docs 配置 LLM key 与数据集路径
python -m ai_researcher.run --bench scientist-bench --level 1 --domain recsys
```
