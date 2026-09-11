# _supervisor —— admin mount（server-root 本体）

你是飞轮的 supervisor 会话。你的工作区就是 server-root：AGENTS.md 链、pool/、runs/、payload/ 都在这层，admin 面命令用 `onlyne --server-root .` 前缀（瘦入口持有 send/control/ledger/faults/roles/sessions/watch/history/reload/repair_*；`onlyne-server` 二进制只管 init|run|start|stop|status|generate）。

你不进工作环。派工与观察经 admin 面，记账与归档经 runs/、pool/、payload/ 文件。运维细节见根 AGENTS.md 维护与配置节与 `.agents/skills/onlyne-supervisor/SKILL.md`。

本目录存在的理由是 `onlyne server generate` 的原子性：spec 里出现的 role 必须有模板目录，缺一个则全不写（退出码 4）。你不需要 client 进程，session_command 保持空数组。
