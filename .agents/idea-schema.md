# Idea Schema

每条 idea 是 `.agents/ideas.jsonl` 里的一行 JSON。

## 字段

- `id`: 唯一 id
- `origin`: `user_seed`（用户初始动力）或 `derived`（从上一轮成果衍生）
- `parent_run`: `derived` 时来源轮 id
- `question`: 研究问题
- `hypothesis`: 可证伪假设
- `method`: 方法草案，落在哪块代码
- `evidence`: 证据路径数组，必须非空，指向 `research/` 下真实物料；必须包含 `research/frontier-notes.md`（scout 的联网文献记录，含 URL 与单行结论）
- `evaluation`: 评测契约，见下
- `done_when`: 验收条件，可检查
- `status`: `queued` | `running` | `keep` | `failed` | `manual`

## evaluation 契约

支持多目标和多约束。

```
{
  "objectives": [
    {
      "metric": "指标名",
      "evaluator": "评测器路径",
      "direction": "min" | "max",
      "epsilon": 0.001,
      "baseline": "基线数值或基线产物路径"
    }
  ],
  "constraints": [
    { "check": "可执行命令或断言", "description": "必须满足的硬约束" }
  ],
  "pass_rule": "all" | "any"
}
```

- `objectives` 是优化目标，可多个。
- `constraints` 是硬约束，必须全部满足，不是优化项。
- `pass_rule: all` 要求每个 objective 都朝 direction 方向改进且超过 epsilon；`any` 要求至少一个。
- 评测器代码落在 `evaluation/`，属可改范围。idea 阶段设计评测器，evaluation 站执行。

## 准入

- `evidence` 非空，且路径真实存在。
- `evaluation.objectives` 非空。
- `done_when` 非空。
- 不满足的 idea 停在池外，不调度。
