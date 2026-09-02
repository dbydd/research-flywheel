# 05 — Dolphin / VirSci Virtual Lab / ResearchAgent / AI-Supervisor：一组互补的闭环与世界模型

> 本文件按任务要求打包四条相关但形态各异的 CS 闭环，供 harness 按需取用。Dolphin 与 VirSci 同源互补，ResearchAgent 聚焦想法的迭代精炼，AI-Supervisor 提供持久世界模型与自纠正编排。

---

## 05-A — Dolphin：思考-实践-反馈的闭环

### 元信息
- **机构 / 作者**：上海人工智能实验室 InternScience 团队，Jiakang Yuan, Xiangchao Yan, Shiyang Feng, Bo Zhang, Tao Chen, Botian Shi, Wanli Ouyang, Yu Qiao, Lei Bai, Bowen Zhou
- **发布时间**：预印 2025-01-07 arXiv:2501.03916，ACL 2025 主会接收（ACL Anthology 2025.acl-long.1056）
- **核心 URL**：
  - 论文：https://arxiv.org/abs/2501.03916 与 HTML 版 https://arxiv.org/html/2501.03916v3
  - 代码：https://github.com/InternScience/Dolphin
  - 项目页：https://alpha-innovator.github.io/Dolphin-project-page
  - ACL 版本：https://aclanthology.org/2025.acl-long.1056

### 时间线
- 2025-01：首次预印，提出 thinking → practice → feedback 三段闭环
- 2025-03~05：发布 dolphin_utils、launch_dolphin.py/sh 与 docs，支持按 topic/task 属性检索与过滤文献
- 2025-07：ACL 2025 发表，报告在 3D 点云分类等任务上自动提出的方法可比肩 SOTA，并在 MLE-bench 子集上验证持续提升

### 循环形态（文字图）
```
[ 文献检索与排序（topic/task 属性） ] ──► [ 想法生成（基于上一轮结果 + 相关论文） ]
                                              │
                                              ▼
                                    [ 代码生成（模板 + 异常回溯引导的局部结构） ]
                                              │
                                              ▼
                                    [ 自动调试（exception traceback guided fix） ]
                                              │
                                              ▼
                                    [ 实验执行与结果分析 ] ──► [ 反馈至下一轮想法 ]
                                              │
                                              └──── 闭环持续提升，无需人工在轮间干预
```

### 智能体角色
- **Idea Generator**：按反馈与检索论文生成新假设
- **Coder / Debugger**：用精炼模板生成实验代码，异常回溯定位到局部结构，迭代修复直至可运行
- **Executor**：批量执行，采集指标
- **Analyzer**：自动分析结果并写反馈，供下一轮检索与生成使用
- 单一主循环，无独立 reviewer 角色，评审由指标与反馈隐式承担

### 工具链
- **检索**：按主题与任务属性对文献排序与过滤
- **代码**：`dolphin_utils` 封装的模板与调试器，`launch_dolphin.py` 一键启动
- **执行**：Python 科学栈，适配 MLE-bench 等 benchmark
- **依赖**：`requirements.txt` 明示，结构轻量

### 评测方式
- 多 topic benchmark 上的性能爬升曲线，验证闭环是否单调提升
- MLE-bench 子集上的端到端成绩
- 与 SOTA 对比，特别是 3D 点分类等任务上“自动提出方法 ≈ SOTA”的案例

### 开源与复现成本
- **开源**：GitHub 完整开源，含 examples 与 docs
- **成本**：低至中等，单机可跑，闭环轮数与检索量决定 API 与算力开销

### 可借鉴点
1. **异常回溯引导的局部修复**：harness 的 coder 失败时不重写全文件，只修 traceback 指向的局部块，显著降低 token 与回归风险。
2. **按属性排序的文献检索**：harness 检索器支持 `topic` + `task` 双维打分，而非纯关键词，提升想法与任务的相关性。
3. **闭环反馈即 prompt**：上一轮的指标与失败原因直接拼入下一轮想法生成的上下文，形成最简记忆。

### 坑 / 局限
- 模板仍是瓶颈，过度依赖初始模板会限制创新空间
- 检索排序若偏向热门论文，易陷入局部最优
- 缺独立评审，数值提升可能掩盖方法论缺陷

---

## 05-B — VirSci / Virtual Lab（Stanford Zou Group）：多学科 PI 制虚拟实验室

### 元信息
- **机构 / 作者**：Stanford James Zou 团队，含 Zou Group 多名博后与学生，协作实验团队
- **发布时间**：bioRxiv 预印 2024-11-11（2024.11.11.623004），Nature 相关报道 2025-07，GitHub zou-group/virtual-lab 同步
- **核心 URL**：
  - 预印：https://www.biorxiv.org/content/10.1101/2024.11.11.623004v1 与 PubMed https://pubmed.ncbi.nlm.nih.gov/40730228
  - 代码：https://github.com/zou-group/virtual-lab
  - 医学院报道：https://med.stanford.edu/news/all-news/2025/07/virtual-scientist.html 与 https://med.stanford.edu/cancer/about/news/inside-the-virtual-lab--how-ai-scientists-are-accelerating-disco.html
  - 访谈：https://www.youtube.com/watch?v=H87hC_5uQtc

### 时间线
- 2024-11：bioRxiv 预印，提出 PI 统筹的多智能体虚拟实验室
- 2025-02~07：以 SARS-CoV-2 纳米抗体设计为示范，计算管线产出 92 个候选，其中 2 个对 JN.1/KP.3 等新变体结合更强且保留对祖先株亲和力，成果被多家媒体与期刊关注
- 2025 至今：向“虚拟生物技术公司”扩展，目标数千智能体规模

### 循环形态（文字图）
```
[ 人类给出研究问题 ] ──► [ PI Agent 拆解目标 + 开会拉齐 ]
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
         [ 免疫学 Agent ] [ 计算生物 Agent ] [ 机器学习 Agent ] [ 批判 Agent ]
               │               │               │               │
               └──────► [ 共享计算管线：ESM + AlphaFold-Multimer + Rosetta ] ◄──────┘
                                      │
                                      ▼
                              [ 候选设计与排序 ]
                                      │
                              [ 湿实验验证（人类执行） ]
                                      │
                              [ 结果回流至 PI，迭代下一轮 ]
```

### 智能体角色
- **PI Agent**：定目标、排期、主持虚拟会议、裁决分歧
- **领域科学家 Agents**：免疫、计算生物、机器学习等，各自负责假设与代码/管线
- **Critic Agent**：审查逻辑一致性与实验有效性
- **人类协作者**：提供问题、执行湿实验、把关安全与可解释性

### 工具链
- **蛋白建模**：ESM（序列表示）、AlphaFold-Multimer（结构预测）、Rosetta（设计与能量评估）
- **LLM 协作**：多 Agent 会议与文献引用
- **实验**：云端计算 + 线下湿实验闭环

### 评测方式
- 计算指标：结合亲和力、稳定性等打分排序
- 湿实验验证：92 个设计中 2 个强结合新变体，超越已有抗体，报告于预印与媒体
- 过程指标：跨学科推理的完整度与可追溯性

### 开源与复现成本
- **开源**：virtual-lab 仓库含管线代码与示例
- **成本**：高。需蛋白模型权重、结构预测算力与湿实验条件，纯计算复现门槛亦高于纯 ML 闭环

### 可借鉴点
1. **PI 制与虚拟会议**：harness 引入 PI agent 做任务分解与冲突裁决，会议纪要落盘为 `meetings/<round>.md`，比扁平多 agent 更可控。
2. **工具链即智能体能力**：把 ESM/AlphaFold/Rosetta 封装为 agent 可调用的 tool，而非外部脚本，harness 可类比封装 `tool: docking` / `tool: structure_pred`。
3. **干湿闭环接口**：明确划分 AI 负责计算、人负责实验的边界，harness 对需物理执行的任务设 `human_in_the_loop: true` 门控。

### 坑 / 局限
- 跨学科幻觉风险高，需 critic 与人类双重校验
- 计算管线误差会传导至湿实验，成本高且不可逆
- 规模化至数千 agent 的通信与一致性尚未验证

---

## 05-C — ResearchAgent：基于文献图的迭代想法精炼

### 元信息
- **机构 / 作者**：Jinheon Baek, Sujay Kumar Jauhar, Silviu Cucerzan, Sung Ju Hwang（KAIST 等）
- **发布时间**：预印 2024-04-11 arXiv:2404.07738，NAACL 2025 接收
- **核心 URL**：
  - 论文：https://arxiv.org/abs/2404.07738
  - 代码：https://github.com/JinheonBaek/ResearchAgent
  - 讨论：https://news.ycombinator.com/item?id=40047152

### 时间线
- 2024-04：预印发布，提出以核心论文为锚、学术图谱扩展、知识库实体增强的想法规整
- 2025：NAACL 发表，验证在多学科上生成想法的新颖性、清晰度与有效性

### 循环形态（文字图）
```
[ 核心论文 ] ──► [ 学术图谱扩展（引用/被引/共现） ] ──► [ 链式文献组织（按领域进展排序） ]
        │                        │                              │
        │              知识库实体增强（跨论文概念挖掘）              ▼
        └──────────────► [ 多 ReviewingAgents 评分（新颖/可行/影响力） ] ──► [ 迭代改写想法 ]
                                      ▲                                    │
                                      └────────────── 反馈精炼 ◄─────────────┘
```

### 智能体角色
- **ResearchAgent（主）**：定义问题、提方法、设计实验
- **ReviewingAgents（多）**：按人类偏好对齐的评审标准打分，给出可操作修改建议，驱动迭代

### 工具链
- **检索**：学术图谱（Semantic Scholar 等）+ 自建概念知识库
- **评审对齐**：从人类判断中抽取的评审准则，经 prompt 注入 ReviewingAgents
- **写作**：结构化的问题/方法/实验三段式产出

### 评测方式
- 人类与模型双评：新颖性、清晰度、有效性
- 跨学科泛化：多领域论文集上的想法质量对比
- 与基线方法对比，验证链式文献组织优于扁平检索

### 开源与复现成本
- **开源**：GitHub 提供核心实现
- **成本**：低。主要为 LLM 调用与图谱检索，无需重型训练

### 可借鉴点
1. **链式文献组织**：harness 检索后不堆文献，而是按“领域进展链”排序，降低 LLM 上下文噪声。
2. **多 ReviewingAgents 的偏好对齐**：把人类评审偏好显式编码为 rubric，harness 可复用为 `rubric/reviewer.yaml`。
3. **想法精炼而非一次性生成**：harness 对想法设 `refine_rounds: 3`，每轮必经评审，降低一次性幻觉。

### 坑 / 局限
- 想法易“看似新颖实则增量”，缺乏实验验证难以证伪
- 图谱覆盖度与知识库时效性直接影响天花板
- 多 reviewer 的一致性需校准，否则反馈矛盾

---

## 05-D — AI-Supervisor / Persistent Research World Model：带记忆与自纠正的编排

### 元信息
- **机构 / 作者**：Yunbo Long 等，独立研究团队
- **发布时间**：预印 2026-03-25 arXiv:2603.24402
- **核心 URL**：
  - 论文：https://arxiv.org/abs/2603.24402 与 HTML 版 https://arxiv.org/html/2603.24402v1
  - 镜像：https://theresanaiforthat.com/paper/ai-supervisor-autonomous-ai-research-supervision-via-a-persistent-research-world-model

### 时间线
- 2026-03：预印发布，提出 Research World Model + 结构化空白发现 + 自纠正发现/开发双循环 + 共识提交

### 循环形态（文字图）
```
[ 人类兴趣（自然语言） ] ──► [ 文献阅读与合成 ] ──► [ 结构化空白发现（方法→模块→benchmark→gap） ]
        ▲                              │                        │
        │                     [ Research World Model（知识图谱，U=0 已验证 / U=1 未验证） ]
        │                              │                        │
        │                              ▼                        ▼
        │                    [ 自纠正发现循环（为何某模块在某类问题上成/败） ]
        │                              │                        │
        │                    [ 自改进开发循环（跨域机制搜索，靶向失败模块） ]
        │                              │                        │
        │                    [ 多 Agent 共识：独立发现互证后才提交至图谱 ]
        │                              │                        │
        └──────────── [ 评估、论文写作、图谱更新 ] ◀─────────────┘
```

### 智能体角色
- **Literature Synthesizer**：读论文并抽取方法、模块、benchmark、gap
- **Gap Discoverer**：把方法拆为核心模块，验证其在各 benchmark 上的表现，映射 gap
- **Discovery Prober**：追问“为何在此类问题上成功/失败、benchmark 是否有偏、评测协议是否过时”
- **Mechanism Searcher**：跨域搜索可迁移机制，靶向失败模块
- **Consensus Committee**：多 agent 独立验证，达成共识才写入 World Model

### 工具链
- **World Model**：不确定性标注的知识图谱（U 标记），作为共享记忆与编排骨架
- **检索与合成**：结构化抽取管线
- **跨域搜索**：跨学科机制库
- **写作与评估**：基于图谱的论文生成与验证

### 评测方式
- 图谱的覆盖度、准确度与自纠正收敛速度
- 空白发现的精确率与可验证性
- 生成稿件的完整度与与人类 supervisor 输出的对比

### 开源与复现成本
- **开源**：论文为主，代码待发布（截至 2026-03）
- **成本**：中高。图谱维护与多 agent 共识的调用量大，但可增量构建

### 可借鉴点
1. **持久世界模型而非无状态流水线**：harness 维护 `world-model.json`（方法/模块/benchmark/gap/U 标记），所有 agent 共享读写，避免重复造轮子。
2. **U 标记的验证门控**：harness 对图谱每条边设 `U=0/1`，只有 `U=0` 才能作为后续假设的前提，强制“先验证再构建”。
3. **结构化空白发现**：把“找空白”从自由生成变为“方法→模块→benchmark→gap”的结构化分解，harness 可落地为 `gap_discovery.py`。
4. **共识提交**：harness 要求同一发现由 ≥2 个独立 agent 复现才写入 world model，降低单 agent 幻觉污染。

### 坑 / 局限
- 图谱构建的冷启动成本高，初期噪声大
- 共识机制可能过滤掉真正新颖但小众的发现
- 跨域机制迁移的适配成本被低估

---

## 跨系统可直接复用的 harness 机制清单
- 异常回溯的局部修复（Dolphin） + 单文件变异（Karpathy）组合：先局部修，再整文件赛马
- 链式文献 + 属性排序检索（ResearchAgent + Dolphin）：harness 检索器标配
- PI 会议纪要 + 共识写入（VirSci + AI-Supervisor）：harness 的两级记忆（短期会议 + 长期图谱）
- 多 Reviewer 偏好对齐（ResearchAgent + CycleReviewer）：harness 的默认 reviewer 栈
