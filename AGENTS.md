# 这棵树还没装配 —— 你是 clone 后的第一个会话

判据：`scripts/bootstrap.sh --check` 未全绿，且本文件首行仍是这个标题。两条同时成立 = 未装配。装配收尾的 `--promote` 会把 `.agents/AGENTS.md`（11 角色公共约定正本）复制为仓根 `AGENTS.md`，本文件的使命到此完成。

你（pi / omp / claude 任一接手本树的会话）的活是引导用户把这棵模板树装配成他机器上可通电的 onlyne 集群。照 `BOOTSTRAP.md` 走，顺序如下：

1. 读 `BOOTSTRAP.md` 的「开场协议」节：向用户自我介绍，一次问全四件——装在哪台机器与用哪个终端后端（herdr / orca / zellij 之一）、`[server].listen` 端口、pi 的模型供应商与三档路由、有无 Obsidian vault 与算力功耗边界。
2. 装依赖：onlyne 五件套 + `pi install npm:pi-onlyne`，全追渠道 latest，兼容判据 `onlyne version` 报 `protocol:1`。
3. 跑 `scripts/bootstrap.sh --assemble`（把用户答复换成对应 flag）：证书初始化与 `cert_pin` 回填、11 个 role 密钥与 `key` 回填、模型档位写入、11 份角色工作区渲染、vault 软链，全幂等。
4. 跑 `scripts/bootstrap.sh --check`：门禁全绿才准 `--promote`。
5. 通电与第一发：server 与 11 个 role client 各占一个**用户可见的前台终端 tab** 起（脚本不起守护进程），第一发按 `BOOTSTRAP.md` 第 8 步投给角色表 ★ entry role（pi）。

红线：装配完成前不起 server/client、不跑领域实验、不动 `.onlyne/spec.toml` 与 `.onlyne/templates/` 的结构、不动 `.agents/skills/onlyne-{supervisor,role}`。

想先浏览不动手：读 `README.md` 的「这套系统长什么样」，停在原地，零文件改动。

各层读者与文件的对应关系（装配后依然成立）：role 会话读仓根 `AGENTS.md`（= `.agents/AGENTS.md` 的副本）+ 自己 ws 的角色细则；supervisor 值班读 `.pi/SYSTEM.md`；换机重装读 `BOOTSTRAP.md`；领域方法论读 `.agents/skills/`。
