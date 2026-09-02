# 02 — Sakana AI Scientist v1 / v2：端到端论文工厂

## 元信息
- **机构 / 作者**：Sakana AI（Tokyo）× UBC / Vector Institute / Oxford，v1 作者 Chris Lu, Cong Lu, Robert Tjarko Lange, Jakob Foerster, Jeff Clune, David Ha；v2 新增 Yutaro Yamada, Shengran Hu 等
- **发布时间**：v1 预印 2024-08-12 arXiv:2408.06292，v2 预印 2025-04-10 arXiv:2504.08066，Nature 扩展版 2026 年刊出 Nature 651, 914–919
- **核心 URL**：
  - v1 论文：https://arxiv.org/abs/2408.06292
  - v2 论文：https://arxiv.org/abs/2504.08066 与 HuggingFace 镜像 https://huggingface.co/papers/2504.08066
  - 官网解读：https://sakana.ai/ai-scientist 与 https://sakana.ai/ai-scientist-nature
  - v1 代码：https://github.com/SakanaAI/ai-scientist
  - v2 代码：https://github.com/SakanaAI/ai-scientist-v2
  - Nature 评述：https://www.nature.com/articles/d41586-026-00899-w

## 时间线
- 2024-08：v1 发布，首次展示 LLM 驱动的 idea → 文献检索 → 实验规划/执行 → 画图 → 写稿 → 评审的全链路闭环
- 2025-04：v2 发布，移除对人工手写代码模板的依赖，引入渐进式 agentic tree search 与 experiment-manager，VLM 介入图表美化与内容复核；三篇全自治稿件投向 ICLR workshop，其中一篇超过人类平均接收阈值，宣称首篇完全由 AI 生成且通过人工同行评审的 workshop 论文
- 2025-08：外部独立复现评估 arXiv:2502.14297 对 v1/v2 的主张做成色检验，指出有效性参差但方向可行
- 2026：Nature 刊出整合版，补充规模化结果与安全讨论

## 循环形态（文字图）
```
[ Idea Generator ] ──► [ Experiment Manager ] ──► [ Executor ]
        ▲                        │                     │
        │              渐进式 tree search              ▼
        │              按节点展开/剪枝        批量跑实验 + 日志
        │                        │                     │
        └──────── [ VLM Reviewer + LLM Reviewer ] ◀────┘
                             │         │
                    语义/视觉反馈      评分与修改建议
                             ▼
                    [ Manuscript Writer ] ──► [ LaTeX 编译 + 图表迭代 ]
                             │
                    workshop 投稿 → 人类 peer review
```
v1 为线性流水线 + 模板填充，v2 改为树搜索：一个 idea 节点可派生多条实验路径，experiment-manager 负责调度、去重、资源分配，评审侧用 VLM 对图表做像素级反馈。

## 智能体角色
- **Ideator**：基于文献与已有结果生成假设，v2 中不再依赖人工模板，完全由 LLM 自由生成
- **Experiment Manager**：v2 新增的中心调度者，管理 tree search 的展开、优先级、失败重试与资源预算
- **Executor / Coder**：把假设翻译为可运行代码并执行，采集指标与产物
- **Analyzer**：汇总结果、做统计检验、生成图表初版
- **Writer**：拼接 LaTeX 稿件，调用模板与引用库
- **Reviewer**：LLM 评审 + VLM 视觉评审，外层人类 workshop 评审为最终关卡

## 工具链
- **LLM 底座**：兼容多家 foundation model，未绑定单一供应商；代码生成与写作均经 LLM
- **实验执行**：Python 科学栈 + 任务相关框架（ML 领域为主），v2 强调跨 domain 泛化
- **图表与排版**：matplotlib / LaTeX，VLM 负责“图是否清晰、坐标轴是否可读”等美学与信息密度反馈
- **检索**：Semantic Scholar 等学术图谱用于文献与引用
- **版本与产物**：git 管理稿件迭代，artifacts 包含代码、日志、图表、PDF

## 评测方式
- **内部**：LLM reviewer 打分 + VLM 图表反馈的迭代收敛度
- **外部黄金标准**：真实投稿至 ICLR workshop 的人类同行评审分数，v2 报告一篇稿件超过平均接收阈值（workshop-level）
- **第三方对照**：arXiv:2502.14297 设对照组与能量/量化等推荐系统子任务，评估复现率与 novelty 区分度

## 开源与复现成本
- **开源状态**：v1 与 v2 均开源（GitHub 上 SakanaAI 组织），含代码、prompt、LaTeX 模板与示例稿件；Nature 版提供复现指南与安全说明
- **复现成本**：中等偏高。单篇稿件需数十次实验迭代，依赖 LLM API 调用与 LaTeX 编译链；v2 的 tree search 会放大调用量。社区报告在 8–16 GPU 时或等价 API 预算下可在一两天内复现单赛道。非 ML 领域需自备数据集与评测脚本。

## 可借鉴点（落地到 harness 机制）
1. **Experiment Manager + Tree Search**：harness 引入显式的 manager 角色，维护 `ideas.jsonl` 树（父子指针 + 分数 + 状态），每轮按 UCB 胜率展开 top-k 节点，而非线性队列；落盘为 `channels/<id>/tree.json`。
2. **模板消除**：v2 证明可去掉人工 code template，改由 LLM 自由生成但配强校验（静态检查 + 最小可运行冒烟测试）；harness 可设 `allow_free_codegen: true` 并在 runner 前加 `py_compile` + `quick_run` 门控。
3. **VLM 图表闭环**：把图表从“能跑”提升到“能发表”，harness 在 writer 阶段后加一步 VLM 审图（分辨率、图例、坐标标题），不通过则回写修改指令，形成 writer ↔ reviewer 小循环。
4. **真实投稿作为外评**：把 workshop 投稿分数当作 hold-out metric，避免自评自嗨；harness 可配置 `external_review: workshop` 与人类评审分数对齐日志。
5. **安全与声明机制**：Nature 版强调 AI 生成稿件的披露与伦理审查，harness 应对 AI 生成产物打水印与 provenance 记录（`generated_by`, `model`, `timestamp`）。

## 坑 / 局限
- **幻觉与统计不严谨风险高**：评审模型对方法 novelty 与统计显著性判断不稳定，v2 仍需人类把关；harness 需加 `stat_check` 与 `citation_verify` 两个硬门控。
- **模板移除后方差增大**：自由生成代码的失败率与 token 成本上升，tree search 剪枝策略不当会浪费预算；建议设 `max_children_per_node` 与 `early_stop_patience`。
- **Workshop 阈值不等同会议主会**：首篇接收的含金量被外部评估认为更多是 workshop-level，harness 对外宣传需区分 tier，避免误导。

## 复现指引（最小）
```bash
git clone https://github.com/SakanaAI/ai-scientist-v2 && cd ai-scientist-v2
pip install -r requirements.txt
# 按 README 配置 LLM API key 与 LaTeX 环境
python run.py --idea "adaptive dropout for ViT" --workshop-mode
```
