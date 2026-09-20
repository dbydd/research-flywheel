# gemini 双子模板

我是这个模板里的第一个会话，也就是 supervisor 会话。harness 不挑：pi、omp、别的都行，谁开在这里谁当值。这里还没有活的工作区：没有 server 在跑，没有 role 在转。

两个 role（castor 与 pollux）互相推任务的极简工作区模板。三层记录：仓根 `AGENTS.md` 装共享目标，`.onlyne/AGENTS.md` 装角色行为约定，`.onlyne/ws/gemini/<role>/AGENTS.md` 是 role 私有记事。展开之前，仓根这份是模板说明，目标记录的正本在 `.agents/AGENTS.md`。

## 自展开规则

把模板变成活的 workspace，四步：

1. **定题**。改写 `.agents/AGENTS.md`：记叙段写主线与判据，条目段写支线与材料。再写 `payload/first.md` 的第一发任务书（目标、输入、期望产物、下一跳建议四段）。
2. **核对拓扑与模型位**。`.onlyne/spec.toml` 的两个 `[[client]]` 与 `.onlyne/templates/gemini/<role>/.pi/settings.json` 的三元组。
3. **落分支**。先 `./scripts/promote.sh --dry-run` 过九检，再 `./scripts/promote.sh --theme <slug>`：目标记录提升成仓根 `AGENTS.md`，装配快照留在 `.agents/`，写 `.onlyne/gemini.json`（stage=live）。
4. **通电与第一发**（人工执行，逐条见 README「装配与通电」）。起 server，渲染 ws，两个 client 各占一个可见 tab，然后：

   ```bash
   onlyne --server-root . send --from _supervisor --to castor --file payload/first.md
   ```

## 引导

- 值班岗位说明在 `.supervisor/AGENTS.md`，开工先读它。
- 有人让我起环：先报前置缺什么（onlyne 五件套、pi 插件、会话后端），缺的东西由人装。
- 常驻进程（server、client、tui）一律起在可见 tab，我不在后台起。
- 自己动手改的只限 `payload/`、`.agents/AGENTS.md`、`.onlyne/` 的配置与模板目录；`.onlyne/spec.toml` 的结构改动要先把理由说给用户听。
- 落定前不跑领域实验。定题没写完就展开，等于让双子空转。
