# 自举说明：把本分支还原成可运行的科研飞轮

框架本体（onlyne v1）与各渠道最新版同步；本分支只含主题材料：根契约 `AGENTS.md`、11 份角色模板 `.onlyne/templates/formal/`、拓扑 `.onlyne/spec.toml`、领域代码面 `experiment/` 与 `evaluation/`、技能文档 `.agents/skills/`。运行数据（`research_project/` 的在途项目内容、`measured/` 读数、`runs/` 档案、`payload/` 历史任务书）留在各自主机，上网前自查一遍。

## 开场协议（自展开入口）

新人不用手工装配。把树 clone 下来，对你的 agent 会话（pi / omp / claude 皆可）说一句：

> 帮我看看这棵树

会话应当主动完成：读 README 与本文件 → 核 onlyne/pi 装具与版本（`onlyne version` 报 protocol:1）→ 问清你的研究主题、端口、模型供应商与预算档位 → 按下面步骤代你执行装配 → 投第一发。你不碰命令行也能开机。手工装配走同一份文档，逐条照抄即可。

第一发需要的研究方向任务书写进 `payload/first.md`（问题、约束、期望各一段），或由会话代笔经你过目。

## 前置

- Rust 工具链与 pi。onlyne 装 latest，命令里没有版本号，随时发版随时追：
  `cargo install onlyne-cli onlyne-server onlyne-client onlyne-gateway onlyne-tui`（crate `onlyne-cli` 装出的 bin 叫 `onlyne`，其余同名）。
  升级＝同一条命令加 `--force` 重跑。兼容判据是 `onlyne version` 的 `protocol:1`；各 crate 版本号独立前进，别拿一个二进制的号推断另一个。
- 源码构建备用（要跟 main 上尚未发布的 fix）：`git clone https://github.com/dbydd/onlyne && cd onlyne && cargo build --release`，把 `target/release/{onlyne,onlyne-server,onlyne-client,onlyne-gateway,onlyne-tui}` 放进 PATH。macOS 上若是 cp 复制进 PATH，先 `codesign --force --sign -` 每个二进制，否则 exec 收 SIGKILL。后续更新走 `git pull && cargo build --release` 再重跑 cp + codesign。
- pi 插件两条路都取 latest：`pi install npm:pi-onlyne`（relay 守卫与 activity panel 都在最新里），或本机 onlyne checkout 的 `plugins/onlyne-agent-pi`（源码真相）。generate 把包 vendor 进各角色工作区，ws 内副本零 npm 依赖。
- 会话后端需要 `herdr`、`orca` 或 `zellij` 之一。`ONLYNE_BACKEND` 留空或 `auto` 时探测序是 herdr→orca→zellij；`onlyne-client doctor` 只读打印本机判定，探不到时 `onlyne-client run` 退 5 并报 NO_SUPPORTED_HOST。
- pi 的 model/provider 已经配好（本主题默认 axonhub 路由与三档模型，见根 `AGENTS.md` 角色表末列；换供应商改第 5 步的 11 份 settings.json）。

## 步骤

1. 落树：`git clone -b theme/formal-research <本仓> <workspace> && cd <workspace>`。
2. 证书：端口查重（`lsof -i :7820`；本树 spec 定死 `127.0.0.1:7820`，多树并机就改 spec `[server].listen` 再走本步）→ `onlyne-server init --root . --listen 127.0.0.1:7820` → 把打印的 cert_pin 回填 `.onlyne/spec.toml` 的 `[server].cert_pin`（现为 `sha256/REPLACE_ME_after_server_init`，占位值全链拒跑）。
3. 插件路径：11 份 `.onlyne/templates/formal/<phase>/<role>/.pi/settings.json` 的 `packages` 现填装配机字面路径（`/Users/dbydd/Documents/progs/onlyne/plugins/onlyne-agent-pi`）；换机一条 sed 全替：
   `ABS=<你的 onlyne 仓>/plugins/onlyne-agent-pi; sed -i '' "s|/Users/dbydd/Documents/progs/onlyne/plugins/onlyne-agent-pi|$ABS|g" .onlyne/templates/formal/*/*/.pi/settings.json`
   （macOS 用 `sed -i ''`，Linux 去引号。写绝对字面路径是刻意的：generate 认字面路径才触发 vendor 重写，`{{agent_package}}` 模板变量渲出的形态缺 `../` 前缀，pi 拒载。）
4. 密钥：逐 role `onlyne-client init --workspace .onlyne/ws/formal/<phase>/<role> --role <role> --server-root .`，stdout 的 key 行回填 spec 对应 `[[client]].key`。11 个 role 的清单：
   `for p in initiation/pi initiation/examiner common/librarian common/scribe theory/speculator theory/theorist experiment/runner review/qa review/referee review/chair archive/planner; do onlyne-client init --workspace .onlyne/ws/formal/$p --role $(basename $p) --server-root .; done`
   注意：init 与 generate 都要求 spec.toml 全量 parse 通过；回填前 key 位须保持合法 32 字节 base64（现占位 `ed25519/AQEB…` 即合法），改成 REPLACE_ME 会全链拒跑。
5. 模型档位：11 份 settings.json 的 `defaultProvider` / `defaultModel` / `defaultThinkingLevel` 按本机与预算填写。本主题三档设计（powerful/max 理论位、weak 指导位、supercheap 执行位）见根 `AGENTS.md` 角色表；改档不动 packages 行。
6. 渲染 11 工作区：
   `for p in initiation/pi initiation/examiner common/librarian common/scribe theory/speculator theory/theorist experiment/runner review/qa review/referee review/chair archive/planner; do onlyne-server generate --root . --template formal/$p --role $(basename $p) --force; done`
   自检：`<ws>/.pi/settings.json` 的 packages 已变 `../.onlyne/agent/onlyne-agent-pi` 且 `.onlyne/agent/` 有货。
7. 通电：`onlyne-server run --root .` 占一个**可见前台终端 tab**；随后 11 个 role 各开一个可见 tab 跑 `onlyne-client run --workspace .onlyne/ws/formal/<phase>/<role>`。client 侧只有 `run`（前台常驻，后台化交给 tab；`start`/`stop` 自 1.0.1 取消）。server/client 都不进任何 agent 后台，关 tab 即停环。起前 `onlyne-client doctor` 看探测；起后 `onlyne status --server-root .` 到 connected 11/11 即环点亮。观测位可加一个 tab 跑 `onlyne-tui --spacing 2 --server-root .`。
8. 第一发：写 `payload/first.md`（研究方向、约束、期望），`onlyne send --server-root . --from planner --to pi --file payload/first.md`（supervisor 不注册 [[client]]，admin 面签名借 planner→pi 这条持边）。此后环在 role 间自转；看账走 `onlyne ledger|sessions|faults --server-root .`。

## 验收自检

最小闭环用例：向 planner 投一条自包含小任务 → session 起 → pi 内 `onlyne_complete` done → ledger 出现 task acked 与 completion 回 origin 两行 → `onlyne faults --open-only` 空。绿了再投研究方向的第一发。

## 换机速查

要动的：cert_pin（步骤 2）、spec 里 11 个 key（步骤 4）、11 份模板 packages 路径（步骤 3）、模型三元组（步骤 5）。其余文件跨机通用。`.onlyne/run|store|keys|logs|ws/` 全是运行态，不入 git，装机过程自然再生。
