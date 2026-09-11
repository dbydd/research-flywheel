# 规格：实例工作区物化 + swarm/pi/orca 状态对齐

来源：2026-09-08 Onlyne-Swarm-ARIS 现场排障。第一发投给 scout 后停在 `running` 且会话空闲，
根因链三层，前两层是配置物化缺口，第三层是状态模型缺口。

## 现场事实（可复核）

- 五实例 `.ws/<role>/.onlyne/config.toml` 缺 `[swarm]` 段。模板 `INSTANCE_CONFIG`
  （`src/sync.rs:40-42`）已含 `[swarm] enabled = true`，而 `run_sync` 有条明文规矩
  "已有实例的 config 永不覆写"（`src/sync.rs:57-58`），模板演进对旧实例失效。
  pi-onlyne 侧 `refreshSwarmFlag()` → `readSwarmEnabled(onlyneDir)` 读不到即 false，
  `applyToolSurface()` 按非 swarm 装配，`swarm_complete/swarm_send/...` 不注册。
- 五实例缺 `.pi/onlyne.json`。pi-onlyne `config.js:4` 里 `watch.autoStart` 默认 **false**，
  配置位在 `<cwd>/.pi/onlyne.json`（`config.js:8`）。autoStart 关 ⇒ watch 不起 ⇒
  `swarmReady()` 永不发（`index.js:226`，整段 `try{}catch{}` 静默）。
  对照 marquee：`/Users/dbydd/vibe-agent-working-dir/marquee/.ws/{a..e}/.pi/onlyne.json` 每份都在，
  含 `watch.autoStart: true`、`outbound`、`swarm_prompt.template`。
- 补齐上述两处后同一 payload 立刻跑通：task `d52a0ff9` → scout 会话开始检索与探环境。
- 附带事实：`onlyne client '{"op":"fetch_channel_history",...}'` 在投递成功后查不到正文行，
  `out_cursor = consume` + `markConsumed` 会清已消费行。取证口径要换。

## R1 实例 `.pi` 物化（用户点名要的那条）

`run_sync` 生成/维护实例时，把 supervisor cwd（swarm root）的 `.pi` 物化到 `.ws/<role>/.pi/`：

- 源优先级：`.agents/.schedule/<role>/.pi/**` > `<root>/.pi/**`。`collect_dirs` 的
  dot-dir 过滤（`6476247`）已经把 `.schedule/<role>/.pi` 从 workspace 层里摘出来，
  正好可以当 per-role override 位用。
- 目标：`.ws/<role>/.pi/` 下逐文件写，**copy-if-absent**，与现有 config 不覆写规矩一致。
  手改优先，`--force` 才覆盖。
- 排除：`npm/`、`node_modules/`、`cache/`、`sessions/`、`themes/`（安装产物与缓存，pi 首启自装）。
  `settings.json` 要复制（决定 packages 与 defaultModel）；`hindsight.json` 属 per-role
  语义（bank 分角色），默认不继承，除非 `.schedule/<role>/.pi/` 显式给。
- 必写项：`.pi/onlyne.json` 若最终不存在，scheduler 生成
  `{"watch": {"autoStart": true}}` 并合并已有键（这是 swarm 能跑的前提，属于 scheduler 的职责范围）。
- 已存在实例的迁移：`run` 启动时对缺失项做 additive 补齐（缺文件补文件，缺 `[swarm]` 段追加段），
  永不改已有值。

## R2 `[swarm]` 段的漂移守卫

`INSTANCE_CONFIG` 是唯一真源。对已存在实例，`run_sync` 检查 `.onlyne/config.toml` 是否含
`[swarm] enabled = true`，缺失则追加（纯 additive，正则同 pi-onlyne 的 `readSwarmEnabled` 口径）。
`workspace create` 与 `run` 都走同一函数，守一处。

## R3 健康检查（把这类坑变成可见错误）

`status` / `list_workspaces` 的 health 字段扩展成"swarm-ready 三门"：

1. `.onlyne/config.toml` 有 `[swarm] enabled = true`；
2. `.pi/onlyne.json` 有 `watch.autoStart: true`；
3. `.pi/settings.json` 的 `packages` 含 pi-onlyne。

任一门缺 ⇒ `status` 里该 workspace 标 `not-swarm-ready` 并列缺哪门；`submit` 到该 workspace 时
直接拒绝并打印同一句话。今天的失败模式从"静默挂 12 分钟"变成"提交即报错"。

## R4 状态模型对齐（用户提的那条）

pi 侧有三态：`running`（turn 内）、`idle`（turn 结束等输入）、隐含 `exit`（进程没了）。
orca 侧也看得见：`worktree ps` 的 `agents[].state`、terminal 的 `agentWait`。
swarm 侧只有一个 `TaskState::Running`，把"pane 刚建""会话在启动""空闲等输入""正在干活"
四种现场压成同一个值，于是 liveness 信号丢失。

今天的事故就是这个压值的直接代价：`dispatch()` 建 pane 时就把真实 handle 写进
`terminal`（`sched.rs:161`）并置 `Running`（`:163`），而 `reap_loop` 的 ready-timeout
守卫用 "`terminal` 非 stub 且 state==Running" 判"已投递"（`ipc.rs:220-227`），
于是 120s 超时永远 `continue`，handshake 丢失变成无限挂起，TUI 与 ledger 都看不出来。
守卫应该改用 `running_since`（只在 `write_loopback_in` 成功后插入，`sched.rs:281`）
或显式的 `delivered` 标志。

建议状态与信号源：

| swarm 状态 | 进入条件 | 信号源 | 超时策略 |
|---|---|---|---|
| `Pending` | submit 落库 | 现有 | 队列等待，无超时 |
| `Dispatched` | pane 建好，等 handshake | `dispatch()` | 120s（现有那条要修好守卫） |
| `Ready` | 收到 `swarm_ready`，正文待写 | `events.rs` 现有分支 | 30s 内必须写出，否则失败 |
| `Busy` | 正文已写，agent turn 内 | 新增 `swarm_busy` 或 orca agent state | 长跑上限（role 可配） |
| `Idle` | turn 结束且本轮无 out | 新增 `swarm_idle`（agent_end hook） | 空闲 TTL 到期 ⇒ 判 hop 停滞 |
| `Done/Failed/Cancelled` | out / ack / cancel | 现有 | — |

- 协议增量走 pi-onlyne 现有事件通道（与 `swarm_ready`、`swarm_recycled` 同一形态），
  加 `swarm_busy` / `swarm_idle`，body 带 `{workspace, terminal_handle, task_id}`。
  插件侧数据源是 pi 的 agent 生命周期 hook，无需 orca 轮询。
- 想少改协议也有退路：`sweep_dead_terminals` 顺带读 orca 的 agent state 判 idle。
  代价是轮询与 orca 依赖，好处是零协议变更。倾向选 hook 推送。
- `Idle` 有独立状态后，现在这个 60s TTL 的 `idle` 终端池可以用同一词表表达，
  dispatch 复用空闲 pane 的判据也从"时间到了没"变成"状态是 Idle"。
- TUI 要分得开显示：`Busy` 走粗边，`Idle` 与仅声明的边走细边（对齐 `TUI.md` 既有 weight 语义），
  状态栏显示 hop 在 `Busy/Idle` 上停留多久。今天这类坑在 TUI 上应该一眼可见。

## 验收

- `onlyne-swarm init` + 一个五角色 `.schedule`，实例目录内不手放任何 `.pi/*`：
  `run` 之后三门全绿，`submit` 一发能在 60s 内让 worker 会话开始动作。
- 故意删掉某实例 `.pi/onlyne.json` ⇒ `submit` 到该实例被拒并指出缺 autoStart。
- 用旧模板生成的实例（无 `[swarm]` 段）经一次 `run` 后自动补上段，且不覆写用户改过的其他键。
- 拔掉 handshake（临时让 `swarmReady()` 抛错）⇒ 任务在 120s 被判 `Dispatched` 超时并
  ledger 记行，不再无限 `running`。
- `cargo test` 覆盖：dot-dir、物化 copy-if-absent、`[swarm]` 追加幂等、状态迁移表。

## 版本

R1-R3 是 ARIS 与后续每个 clone 的开路条件，R4 要动协议与 pi-onlyne。建议 R1-R3 + 守卫修正
走 0.6.2，R4 单独一版（0.7.0，含 pi-onlyne 发版与 skill 文档同步）。
