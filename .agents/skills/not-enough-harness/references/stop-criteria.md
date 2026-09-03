# 停止标准 — “好使”的感性判定

> 本 harness 的迭代停止不靠阈值，靠人的体感。机器无法替你决定“好使”。

---

## 30 秒自检清单（全部 ✅ 再停）

- [ ] 不读代码，只看 `AGENTS.md` 就能让全新 worker 跑通一次完整任务
- [ ] 连续 2 轮 worker 无需人工救场（无 blocked、无手动补输入）
- [ ] 没有“每次都要手动…”的步骤（改 prompt、搬文件、补 key 等）
- [ ] 你愿意把这个 workspace 发给同事而不觉得丢人

---

## “还不好使”的信号

| 信号 | 对应要改的层 |
| ------ | -------------- |
| worker 每次都要问同一个问题 | `AGENTS.md` / skill 里把答案写死 |
| worker 手写了第二遍相同脚本 | 抽成 `scripts/` 或 skill |
| worker 因历史对话做出错误假设 | 本轮 worker 已污染，下轮全新 worker + prompt 显式约束 |
| 人类需要手动搬运文件/填参数 | 加 `Makefile` / `inbox→outbox` 约定 / 默认值 |
| 换个输入就挂 | `QUEST.md` 的链路示例不够，或 AGENTS.md 约束不完整 |

---

## 演示脚本（给人看的 1 分钟演示）

```bash
# 在全新目录/全新 worker 里跑通一次
cat QUEST.md          # 一句话目标
cat AGENTS.md         # 工作区约定
ls .agents/skills/    # 有哪些能力
ls scripts/           # 沉淀了哪些工具
cat harness-log.md    # 迭代过程

# 拉起全新 worker 跑回归输入
# → 观察：是否无需人工干预就产出 runs/<latest>/output/
ls runs/*/output/
```

如果演示时你需要解释“这里要手动…”，说明还没“好使”，再磨一轮。

---

## supervisor 的话术

- 完成一轮后问人：**“这一轮 worker 在 ___ 卡住了，我打算把 ___ 沉淀到 ___。你觉得这算是‘好使’了吗？还是再磨一轮？”**
- 人说“好使了” → 停，输出 `harness-log.md` 总结 + 演示脚本。
- 人说“再磨一轮” → 继续 Phase 1→2。
- 人不确定 → 跑一轮回归，让结果说话。

永远不要让 supervisor 自行宣布“已完成”，决定权在人。
