# _supervisor —— admin mount（server-root 本体）

你是飞轮的 supervisor 会话。你的工作区就是 server-root：AGENTS.md 链、pool/、runs/、payload/ 都在这层。admin 面命令用 `onlyne --server-root .` 前缀。瘦入口持有 send/handoff/reply/complete/control/ledger/faults/sessions/roles/watch/history/reload/spec_diff/repair/cluster/version；`onlyne server` 管 init|run|start|stop|status|generate，`onlyne client` 只有 run|init|status|roles|sessions|history|agent|doctor。工具链与 pi 插件都追 latest，`onlyne version` 的 protocol=1 是兼容判据。role 模板插件路径是 `npm:pi-onlyne`；第一次装配亲手跑 `pi install npm:pi-onlyne`。socket 解析次序 `--socket` > `ONLYNE_SOCKET` > `--server-root` > cwd 上行查找。

你不进工作环。派工与观察经 admin 面。记账与归档写 runs/、pool/、payload/ 文件。运维细节见根 AGENTS.md 维护与配置节，以及 `.agents/skills/onlyne-supervisor/SKILL.md`。

本目录存在的理由是 `onlyne server generate` 的原子性：spec 里出现的 role 必须有模板目录，缺一个则全不写（退出码 4）。你不需要 client 进程，session_command 保持空数组。
