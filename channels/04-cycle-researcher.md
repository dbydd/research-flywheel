# 04 — CycleResearcher / CycleReviewer：研究-评审双循环与偏好训练

## 元信息
- **机构 / 作者**：Yixuan Weng, Minjun Zhu, Guangsheng Bao, Hongbo Zhang, Jindong Wang, Yue Zhang, Linyi Yang 等，关联机构含上海交通、微软研究院等
- **发布时间**：预印 2024-10-28 arXiv:2411.00816，ICLR 2025 接收，含 v2/v3 迭代（2025-03-05 / 2025-03-08）
- **核心 URL**：
  - 论文：https://arxiv.org/abs/2411.00816 与 HuggingFace 镜像 https://huggingface.co/papers/2411.00816
  - AlphaXiv：https://www.alphaxiv.org/overview/2411.00816
  - 代码与权重：https://github.com/zhu-minjun/Researcher 与 https://wengsyx.github.io/Researcher/
  - 相关 DeepReview 扩展：arXiv:2503.08569

## 时间线
- 2024-10：CycleResearcher/CycleReviewer 预印，主张用开源后训练 LLM 同时做作者与审稿人，闭环迭代
- 2024-12~2025-03：发布 Review-5k 与 Research-14k 两个训练集，做迭代偏好训练（iterative preference training / RL）
- 2025-03：ICLR 2025 接收，报告 CycleReviewer 相对单个人类审稿人 MAE 降低 26.89%，CycleResearcher 生成稿件模拟评审均分 5.36（人类 preprint 5.24，接收稿 5.69）

## 循环形态（文字图）
```
外循环（研究侧）：
[ 文献回顾 ] ──► [ 选题与提纲 ] ──► [ 撰写初稿 ] ──► [ 提交至 CycleReviewer ]
                                                        │
内循环（评审侧）：                                         ▼
                                   [ CycleReviewer 模拟多审稿人打分 + 意见 ]
                                                        │
                                   [ 偏好训练信号 ] ◄────┘
                                                        │
                                                        ▼
                                   [ 根据意见修订稿件 ] ──► [ 再审 ] ──► 收敛
```
双模型协同：CycleResearcher 负责产出，CycleReviewer 负责打分与建议，二者通过强化学习的偏好信号互相提升，形成“越审越会写、越写越会审”的飞轮。

## 智能体角色
- **CycleResearcher（作者智能体）**：基于开源 LLM 后训练，执行文献综述、稿件撰写、按评审意见修订
- **CycleReviewer（审稿智能体）**：模拟审稿人小组，给出分数与逐条意见，支持平均分与最高/最低分的细粒度预测
- **训练协调器**：用 Review-5k / Research-14k 做迭代偏好训练（类似 RLHF/RLAIF），对齐人类评审分布
- **数据集构建器**：从真实 ML 审稿数据提炼 Review-5k（评审意见）与 Research-14k（研究任务）

## 工具链
- **模型底座**：开源 LLM（非闭源 API 依赖），通过后训练与偏好优化获得审稿与写作能力
- **数据集**：Review-5k（真实审稿意见）、Research-14k（研究任务全集），用于训练与评测
- **评测脚本**：MAE 等回归指标衡量审稿分数预测，模拟评审分数量化写作质量
- **部署**：GitHub 提供权重与推理脚本，支持本地复现审稿与写作

## 评测方式
- **审稿侧**：MAE 衡量分数预测与人类审稿人的一致性，报告降低 26.89% 相对单人类审稿人
- **写作侧**：模拟评审均分 5.36，对照人类 preprint 5.24 与接收稿 5.69，证明在模拟器内具备 preprint 竞争力
- **消融**：迭代偏好训练轮次与数据规模对分数的影响，验证飞轮效应

## 开源与复现成本
- **开源状态**：代码、数据集、模型权重均发布于 GitHub 与项目页，可本地复现
- **复现成本**：低至中等。审稿与写作推理可在单机 GPU 完成；若复现偏好训练则需多卡与 Review-5k/Research-14k 全量训练。适合作为 harness 的“评审子系统”直接集成。

## 可借鉴点（落地到 harness 机制）
1. **双智能体对抗式飞轮**：harness 将“作者”与“审稿人”拆为两个独立 agent，共享同一任务但不同 prompt 与 rubric，审稿意见作为结构化 JSON 回写给作者，形成 `author → reviewer → revision` 内循环；落盘 `reviews/<round>.json`。
2. **偏好训练而非一次性 prompt**：用收集的审稿偏好对做 DPO/RL 迭代，提升审稿一致性；harness 可对 reviewer 设 `preference_tuning: true` 并定期用新收集的 `human_vs_model` 对增量训练。
3. **真实审稿数据驱动**：Review-5k 的构造方法可复用——从本团队历史审稿记录中抽取 5k 条意见，清洗后作为 reviewer 的 few-shot 与微调数据。
4. **模拟分数作为 keeper**：把 CycleReviewer 的平均分当作与 val_bpb 并列的 keeper 信号，harness 中支持 `metric: reviewer_score` 与 `metric: val_bpb` 双轨 keeper。
5. **开源权重即插即用**：直接引入 CycleReviewer 权重作为 harness 的默认 reviewer，比纯 prompt 评审更稳定。

## 坑 / 局限
- **模拟评审≠真实评审**：5.36 的模拟分不代表能过真实同行评审，论文也承认距接收稿 5.69 仍有差距；harness 需对模拟分做校准（calibration）并以人类抽检为准。
- **开源模型能力天花板**：对复杂理论证明与新颖性判断仍弱，易给“看似合理但实则增量”的稿件高分；需配人类 senior reviewer 抽检。
- **数据污染与偏见**：Review-5k 来源与时间窗口影响模型对新领域的泛化，跨域复用需重新采样与再训练。

## 复现指引（最小）
```bash
git clone https://github.com/zhu-minjun/Researcher && cd Researcher
pip install -r requirements.txt
# 下载 Review-5k / Research-14k 与权重
python reviewer.py --paper draft.pdf --out reviews.json
python researcher.py --topic "diffusion acceleration" --review reviews.json
```
