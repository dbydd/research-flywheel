# 自举说明：把本 theme 分支还原成可运行的研究飞轮

框架本体是同仓 `v3-swarm` 分支。不同 theme = 同一框架的不同排布。本分支 `theme/aris` 即其一。

本分支只含运行框架：根约定 `AGENTS.md`、supervisor 指引 `.pi/`、角色模板与拓扑 `.onlyne/`、领域代码面 `experiment/` 与 `evaluation/`、技能文档 `.agents/skills/`。

运行数据留在各自主机，不上网。运行数据包括：runs/、pool/ 内容、research/ 流水、papers/ 成稿、payload/ 历史任务书。

## 前置

- 需要 Rust 工具链与 pi。
- 安装 onlyne 四件套：

  ```bash
  cargo install --locked onlyne-cli onlyne-server onlyne-client onlyne-testkit
  ```

  crate `onlyne-cli` 装出的 bin 叫 `onlyne`。升级＝同一条命令加 `--force` 重跑。兼容判据：`onlyne version` 报 `2.1.1`、`protocol:1`。
- 源码构建备用路（默认分支 main，未发布的 fix 在这儿）：

  ```bash
  git clone https://github.com/dbydd/onlyne && cd onlyne && cargo build --release
  ```

  把 `target/release/onlyne` 放进 PATH。
- 安装 pi 插件：

  ```bash
  pi install npm:pi-onlyne@2.1.0
  ```

  版本号钉住。v2 协议面对旧版插件不兼容。模板 `.pi/settings.json` 的 packages 已写 `npm:pi-onlyne@2.1.0`。
- spec 的 `[server].agent_package` 保持空串。generate 原样保留 npm 路径，产物零绝对路径。
  只有要跟 onlyne 仓未发布 fix 时，才把该字段填成 onlyne checkout 里 `plugins/onlyne-agent-pi` 的绝对路径。generate 会 vendor 进每个 ws。generate 会自动改写 settings。
- 模型配置：pi 的 provider/model 走操作者自己的 pi 默认配置。本树不记录任何 provider/model 名。模板里只保留 per-role thinking 档。按你的算力预算调整。

## 步骤

1. 落树：

   ```bash
   git clone -b theme/aris <本仓> <workspace> && cd <workspace>
   ```

2. 生成 server 身份：先查重端口 `lsof -i :<port>`。

   ```bash
   onlyne server init --root . --listen 127.0.0.1:<port>
   ```

   把打印的 cert_pin 回填进 `.onlyne/spec.toml` 的 `[server]`。

3. 核对插件版本：六个 `templates/aris/<role>/.pi/settings.json` 的 packages 应为 `npm:pi-onlyne@2.1.0`。然后跑一次 `pi install npm:pi-onlyne@2.1.0`。

4. 生成六个 role key：逐 role 跑下面命令。stdout 的 key 行回填 spec.toml 对应 `[[client]]`。

   ```bash
   for r in scout analyzer model bench writer critic; do onlyne client init --workspace .onlyne/ws/aris/$r --role $r --server-root .; done
   ```

5. 调档位：六个 `templates/aris/<role>/.pi/settings.json` 的 `defaultThinkingLevel` 按你的机器与预算调整。分档设计见 AGENTS.md 角色表末列。

6. 渲染六工作区：

   ```bash
   for r in scout analyzer model bench writer critic; do onlyne generate --root . --template aris/$r --role $r --force; done
   ```

   自检 `<ws>/.pi/settings.json` 的 packages 保持 `npm:pi-onlyne@2.1.0`。

7. 起 server：可见前台 tab 跑下面命令（前台常驻）。判活用 `onlyne status --server-root .`。

   ```bash
   onlyne server run --root .
   ```

8. 预检 placement：跑 `onlyne client doctor`。该命令只读打印本机判定。

9. 起六个 client：六个 role 各开一个可见 tab 跑下面命令。

   ```bash
   onlyne client run --workspace .onlyne/ws/aris/<role>
   ```

10. 第一发：写 `payload/first.md`（问题/约束/期望）。然后执行下面命令。

   ```bash
   onlyne --server-root . send --from _supervisor --to scout --file payload/first.md --force --yes-i-am-supervisor-not-other-role
   ```

第一发之后，环在 role 间自转。运维看账用 `onlyne ledger|sessions|faults --server-root .`。

**占位回填（步骤 2 证书与步骤 4 密钥）**：

- 部署必须创建自己的身份。spec.toml 现存的 cert_pin 与各 key 都是 32 字节占位。占位只保 parse 通过。起真集群前逐行回填真值。
- init 与 generate 都要求 spec.toml 全量 parse 通过。
- 回填前 key 位须是合法 32 字节 base64（如 `ed25519/AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQE=`）。非法值全链拒跑。

## 验收自检

通电检查：`onlyne status --server-root .` 答 ok。六个 role connected（6/6），即环点亮。

最小闭环用例：向 scout 投一条自包含任务。session 起。pi 内 `onlyne_complete{outcome:"done"}` 交活。ledger 出现两行：task 结算行与 completion 回 origin 行。faults 为空。

全绿后再投真研究队列。
