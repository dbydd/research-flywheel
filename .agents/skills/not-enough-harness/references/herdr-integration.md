# Herdr 集成 — 拉起 / 监控 / 清理 Worker

> 本文件只在 `HERDR_ENV=1` 时使用。无 herdr 时直接用 `subagent`，见 SKILL.md Phase 2 降级分支。

---

## 0. 前置检查（每次必做）

```bash
test "${HERDR_ENV:-}" = 1 || { echo "not in herdr, fallback to subagent"; exit 0; }

herdr --help | head -n 5          # 确认 CLI 可用
herdr workspace list               # 确认当前 workspace
herdr pane list --workspace "$HERDR_WORKSPACE_ID"  # 看现有 pane
```

不要用裸 `herdr`（会进 TUI），不要省略 `--current` / pane ID。

---

## 1. 拉起 Worker（全新 pane + 全新 agent）

```bash
# 选方向：当前 pane 宽 → right，窄/高 → down；永远 --no-focus 不抢人类焦点
herdr pane split --current --direction right --cwd "$PWD" --no-focus
# 返回 JSON：.result.pane.pane_id 记为 NEW_PANE

# 起 agent：名字带迭代号，避免复用；kind 按 workspace 约定（pi/codex）
herdr agent start harness-worker-3 --kind pi --pane <NEW_PANE> -- --cwd <workspace>
# 返回需等待 agent 就绪（默认 30s 超时）

# 下发任务（prompt 见 references/worker-prompt.md）
herdr agent prompt harness-worker-3 --wait --timeout 600000 "…worker prompt…"
# --wait 会等到 idle/done/blocked 才返回；blocked 表示需要人工介入
```

**铁律：迭代号递增，绝不复用旧 worker 名 / 旧 pane。**

### 常见坑

- `pane split` 后立刻 `agent start`，pane 还没就绪 → 等 1s 或重试一次。
- `agent start` 超时但 agent 其实起来了 → `herdr agent list` 确认后再 prompt。
- workspace 是 git worktree 时 `--cwd` 必须指向 worktree 根，否则读取的 AGENTS.md 是旧的。

---

## 2. 监控 Worker

```bash
# 看状态
herdr agent get harness-worker-3
herdr agent read harness-worker-3 --source recent-unwrapped --lines 200

# 看 pane 原始输出（agent 视图不全时）
herdr pane read <NEW_PANE> --source recent-unwrapped --lines 300

# 等待特定状态
herdr agent wait harness-worker-3 --until blocked --timeout 120000
herdr agent prompt harness-worker-3 --wait --timeout 600000  # 已在上面用过

# 轮询脚本（supervisor 侧，每 15-30s 一次即可，别刷太频）
while true; do
  herdr agent read harness-worker-3 --source recent-unwrapped --lines 80
  sleep 20
done
```

**只读不写**：监控期间不要给 worker 发额外 prompt 干扰任务。

---

## 3. 救场（可选，尽量少做）

worker 进入 `blocked`（需要 approval / 提问）时：

```bash
herdr agent read harness-worker-3 --source recent-unwrapped --lines 200  # 先看问了什么
herdr agent send-keys harness-worker-3 "y"       # 或 esc / ctrl+c
# 更推荐：让 worker 的 AGENTS.md 里写明“遇到提问自行决策并继续”，减少 blocked
```

---

## 4. 清理 / 回收

worker 完成或失败后，**不要复用**，但可以保留 pane 供复盘：

```bash
# 读最终输出归档
herdr agent read harness-worker-3 --source recent-unwrapped --lines 500 > runs/003/worker.log
herdr pane read <NEW_PANE> --source recent-unwrapped --lines 1000 >> runs/003/worker.log

# 可选：关掉 pane（确认不再需要时）
# herdr pane close <NEW_PANE>   # 仅当你创建的 pane，且用户未要求保留
```

**禁止：**

- `herdr server stop` — 会干掉所有 pane
- 关掉 supervisor 自己的 pane
- `pkill` / `killall` 猜名字杀进程（见全局 AGENTS.md 进程管理规范）

---

## 5. 无 Herdr 降级（subagent）

```js
// supervisor 侧
await subagent({
  agent: "delegate",
  cwd: workspace,
  task: workerPrompt,  // 同 worker-prompt.md 模板
})
// 同样每轮新建 subagent，不复用；产物写到 runs/<iter>/ 下
```

---

## 6. 一键自检

```bash
herdr workspace list | python3 -m json.tool
herdr agent list | python3 -m json.tool
herdr pane list --workspace "$HERDR_WORKSPACE_ID" | python3 -m json.tool
```
