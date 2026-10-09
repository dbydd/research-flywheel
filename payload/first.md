目标：为 AGENTS.md「研究问题与判进标准」一节定下的研究问题做一轮前沿侦察，产出至少一条能过进池硬门的 idea。

背景：这是飞轮的第一发。此前没有任何 runs/ 记录，`pool/ideas.md` 与 `research/frontier-notes.md` 只有框架没有内容，环里的其他角色都等着入池的 idea 才有活干。scout 的检索台账是这个环里一切后续工作的证据起点，先跑通一轮才谈得上闭环。

输入（全部相对 server-root，接收方是全新上下文，只读这里点名的路径）：
- `AGENTS.md` 的「研究问题与判进标准」节：主题、主次度量、阈值、预算、禁区。
- `AGENTS.md` 的「idea 格式」节：四条进池硬门的字段口径。
- `research/frontier-notes.md`：已有检索台账，先翻旧账再查新。
- `research/` 下的本地物料。

期望产物：
- `pool/ideas.md` 新增小节。`evidence`、`evaluation.objectives`、`done_when` 三项非空，headroom 预筛行给出暴露缺口的具体数字或台账行。
- 检索记录追加进 `research/frontier-notes.md`，一行一结论。

自由度：检索围绕研究问题自定查询组；候选 idea 指不出 headroom 数字时，把负证据照记进 `research/frontier-notes.md`；顺手核对「idea 格式」四条硬门的字段在本模板里是否都能照填，填不动的字段记一行说明，供下一轮修订。

下一跳建议：按角色表用 `onlyne_handoff` 交给 model，任务书指向新固化的 `runs/<run-id>/idea.json` 与证据路径；候选全部过不了预筛就写 无，负证据留在台账里等人判。
