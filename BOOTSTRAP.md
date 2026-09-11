# 自举说明：把本 theme 分支还原成可运行的研究飞轮

框架本体是同仓 `v3-swarm` 分支；不同 theme = 同一框架的不同排布，本分支 `theme/aris` 即其一。本分支只含运行框架：根约定 `AGENTS.md`、supervisor 指引 `.pi/`、角色模板与拓扑 `.onlyne/`、领域代码面 `experiment/` 与 `evaluation/`、技能文档 `.agents/skills/`。运行数据（runs/、pool/ 内容、research/ 流水、papers/ 成稿、payload/ 历史任务书）留在各自主机，不上网。文中 `__AGENT_PACKAGE_ABS__` 是哨兵字符串，第 3 步统一替换成你本机的插件绝对路径。

## 前置
- Rust 工具链与 pi（0.85.x 实测）。onlyne 源码取 tag：
  `git clone -b v1.0.0-beta.4 <onlyne 仓> && cd onlyne && cargo build --release`
- `target/release/{onlyne,onlyne-server,onlyne-client,onlyne-gateway}` 进 PATH。macOS 上若是 cp 复制进 PATH，先 `codesign --force --sign -` 每个二进制，否则 exec 收 SIGKILL。
- pi 插件在 onlyne 仓内 `plugins/onlyne-agent-pi`（纯 Node，npm 上的 pi-onlyne 是旧协议，禁装）。

## 步骤
1. 落树：`git clone -b framework <本仓> <workspace> && cd <workspace>`
2. 证书：`onlyne-server init --root . --listen 127.0.0.1:<port>`（端口先查重：`lsof -i :<port>`；参考机 7812/7813 已有他用，7814 起自便）→ 把打印的 cert_pin 填进 `.onlyne/spec.toml` 的 `[server]`。
3. 播种插件路径（macOS 用 `sed -i ''`，Linux 去引号）：
   `ABS=<你的 onlyne 仓>/plugins/onlyne-agent-pi; sed -i '' "s|__AGENT_PACKAGE_ABS__|$ABS|g" .onlyne/spec.toml .onlyne/templates/aris/*/.pi/settings.json`
4. 密钥（逐 role，stdout 的 key 行回填 spec.toml 对应 `[[client]]`）：
   `for r in scout model bench writer critic; do onlyne-client init --workspace .onlyne/ws/aris/$r --role $r --server-root .; done`
   注意：init 与 generate 都要 spec.toml 全量 parse 通过；回填前 key 位须是合法 32 字节 base64（如 `ed25519/AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQE=`），REPLACE_ME 会全链拒跑。
5. 模型档位：五个 `templates/aris/<role>/.pi/settings.json` 的 defaultProvider/defaultModel/defaultThinkingLevel 按你的机器与预算填写（本主题三档设计见 AGENTS.md 角色表）。
6. 渲染五工作区：`for r in scout model bench writer critic; do onlyne-server generate --root . --template aris/$r --role $r --force; done` → 自检 `<ws>/.pi/settings.json` 的 packages 已变 `../.onlyne/agent/onlyne-agent-pi` 且 `.onlyne/agent/` 有货（缺 `../` 前缀 pi 拒载）。
7. 通电：`onlyne-server run --root .` 占一个可见前台终端；随后五角色各 `onlyne client start --workspace .onlyne/ws/aris/<role>`。`onlyne status --server-root .` 到 connected 5/5 即环点亮。
8. 第一发：写 `payload/first.md`（问题/约束/期望），`onlyne send --server-root . --from critic --to scout --file payload/first.md`（supervisor 不注册 [[client]]，签名借 critic→scout 新轮边）。此后环在 role 间自转，运维看账走 `onlyne ledger|sessions|faults --server-root .`。

## 验收自检
最小闭环用例：向 scout 投一条自包含任务 → session 起 → pi 内 onlyne_complete done → ledger 出现 task acked 与 completion 回 origin 两行 → faults 空。绿了再投真研究队列。
