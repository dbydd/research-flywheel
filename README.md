# ARIS Flywheel（onlyne v1 复刻 ARIS 全自动科研环）

本工作区用 `onlyne` v1 五角色飞轮复刻 [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) 的全自动科研工作流。

ARIS 是一套 Markdown-only skills 的自主 ML 研究系统，流程为：文献→idea 发现→实验→跨模型评审循环→论文写作→同行评审 rebuttal。

ARIS 各技能到本飞轮的映射：

- `/idea-discovery` → scout
- `/experiment-bridge` → model + bench
- `/auto-review-loop`（4 轮评审、cross-model jury）→ critic 的 verdict 修订环
- `/research-pipeline` 全链 → 飞轮宏观流本身
- `/research-wiki` 持久记忆 → 文件台账（`runs/`、`pool/ideas.md`、`.onlyne/store/`）

主题证据锚点见 `research/aris-workflow-summary.md`。

三个词先说清：workspace = role，指该角色的「记忆+设定+历史文件」；session = 手头一件工作；任务 = session = 一跳。

工作模型是射后不理，即发出去就不等回复。一轮 session 的动作序列：恢复上下文 → 工作 → `onlyne handoff` 激发下游（可选，若干）→ 落文件 → `onlyne_complete` 退出。

session 对下游零等待。结果经文件与账本（`onlyne ledger --server-root .`）呈现，接力任务唤醒下一个单位。环路开放，靠人闭合。

## 前置

- onlyne v1.0.0 五件套：`cargo install onlyne-cli onlyne-server onlyne-client onlyne-gateway onlyne-tui`（crate `onlyne-cli` 装出的 bin 叫 `onlyne`，其余四个 crate 名=bin 名）；备用路 `git clone -b v1.0.0` + `cargo build --release`
- pi + 插件：`pi install npm:pi-onlyne`（latest=1.0.0，含接力守卫）；找代码认仓库 `plugins/onlyne-agent-pi`，装包认 `pi-onlyne`
- `orca`（含 `orca` CLI）与已配置的 pi model/provider
- 拓扑纪律：server/tui 跑在**本 worktree 的可见前台 tab**（关 tab 即停环），不进任何 agent 后台；client 用 `onlyne client start` 守护态，且必须从本 worktree 的 tab 起（client 起 tab 的 worktree 决定会话 spawn 定向）

## 起飞

集群真相是 `.onlyne/spec.toml`（拓扑/ACL/timeout/relay 策略）与 `.onlyne/templates/aris/<role>/`（细则+模型三元组），装配材料已退役（框架本体与自举见模板树 v3-swarm 的 BOOTSTRAP.md）。重建运行时：

```bash
# 1. 生成五角色工作区（模板改后用 --force）
onlyne server generate --root . --template aris/<role> --role <role> --force

# 2. 起 server：本 worktree 可见 tab 前台
orca terminal create --worktree path:$PWD --title onlyne-server --command "onlyne-server run --root ."

# 3. 起五角色 client（守护态，pid/socket 在各自 ws 运行面）
for r in scout model bench writer critic; do
  onlyne client start --workspace .onlyne/ws/aris/$r
done

# 4. 观测位：可见 tab 跑 tui（力导布局）
orca terminal create --worktree path:$PWD --title onlyne-tui --command "onlyne-tui --spacing 2 --server-root ."

# 5. 第一发（admin 面署名持边角色 critic，注入 ★ entry role scout）
onlyne send --server-root . --from critic --to scout --file payload/first.md
```

## 角色树

```text
.        supervisor（root 会话）：只做工作区维护与第一发，不进工作环
├─ scout   检索+证据+idea 入池+派工（★ entry）→ model
├─ model   推导+Lean 形式化+出 spec（不写 experiment/ 代码）→ bench / writer / scout
├─ bench   跑评测落 measured/ → writer / scout
├─ writer  成稿（带溯源数字）→ critic / scout
└─ critic  对照证据审稿 → verdict.md → writer（revise-文字）/ model（revise-理论）/ scout（accept/reject 开新轮）
```

接力闭环：主环 scout→model→bench→writer→critic→scout；修订环 critic→writer / critic→model；回传边 model→scout、bench→scout、writer→scout。拓扑唯一事实源=根 `AGENTS.md` 角色表与 `.onlyne/spec.toml`，每个 session 自动继承前者。守卫：spec 的 `relay_required`/`relay_count` 经 client 注入会话环境，未接力不许静默交活（force 豁免带 reason 落账）。

## 动力源

seed 由人给（方向+问题）。之后每轮收尾，critic 从论文 open questions 或失败结论提取下一条 idea 入池。idea 无证据或无评测契约不进池。

自激发无熔断，终结靠人：`onlyne control --from <owner> --task <id> cancel --server-root . --reason "..."`（admin 面）或会话接管。收口 bench 类任务补一步进程树扫荡：账本结算杀不到 setsid 出去的 detached 子树。
