# 这棵树还没装配 —— 你是 clone 后的第一个会话

装配动作全部跑完后，`scripts/bootstrap.sh --promote` 会用 `.agents/AGENTS.md`（11 角色公共约定正本）原样覆盖本文件，这份引导就地消失。判据：本文件首行仍是上面这个标题 = 未装配；首行是「formal-research 大循环 — onlyne v1 公共约定」= 已装配，本文件不再对任何人有效，别再装配。

你（pi / omp / claude 任一接手本树的会话）的活是引导用户把这棵模板树装成他机器上可通电的 onlyne 集群。手册是 `README.md` 的「装配与通电」节，顺序照它走：

1. 「装机前四条确认」：向用户自我介绍，一次问全四件——终端宿主（herdr / orca / zellij 之一）、`[server].listen` 端口、模型供应商与两档路由、有无 Obsidian vault 与功耗边界。
2. 「前置」：onlyne 五件套 + `pi install npm:pi-onlyne`，全追渠道 latest，兼容判据 `onlyne version` 报 `protocol:1`。
3. 「装配」：`scripts/bootstrap.sh --assemble`（用户答复换成对应 flag）——证书与 `cert_pin`、11 个 role 密钥与 `key`、模型档位、11 份工作区渲染、vault 软链，全幂等。
4. 收尾自动跑 `--check`，全绿才 `--promote`。
5. 「通电」与「第一发与验收」：server 与 11 个 client 各占一个用户可见的前台终端 tab（脚本不起守护进程），第一发投给角色表 ★ entry role（pi）。

红线：装配完成前不起 server/client、不跑领域实验、不动 `.onlyne/spec.toml` 与 `.onlyne/templates/` 的结构、不动 `.agents/skills/onlyne-{supervisor,role}`。

只想浏览不动手：读 `README.md` 的「这套系统长什么样」，停在原地，零文件改动。

各层读者与文件的对应关系（装配后依然成立）：role 会话读仓根 `AGENTS.md`（= `.agents/AGENTS.md` 的副本）+ 自己 ws 的角色细则；supervisor 值班读 `.pi/SYSTEM.md`；换机重装读 `README.md`「装配与通电」节；领域方法论读 `.agents/skills/`。
