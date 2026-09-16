# pool/themes 格式

多文件主题池。替代单文件 `pool/ideas.md`。`planner` 是 `registry.json` 唯一写主。

## 目录布局

```
pool/themes/registry.json          # 主题×任务×run 全局账
pool/themes/<slug>/main.md         # 总主题
pool/themes/<slug>/tasks/<tid>.md  # 分任务
pool/themes/<slug>/proposals/<tid>-{kaoti,zhongqi,jieti}.md
pool/themes/<slug>/gates/<tid>-G<n>.decision.md   # 关口判词（chair 执笔）
pool/themes/<slug>/gates/<tid>-G<n>-referee-<1|2|3>.md  # 独立意见书，席位号由 chair 分发点名
pool/themes/<slug>/packs/<tid>-G<n>.md            # qa 提包（measured 汇总+三约束核验+无读数计数）
```

## run-id

全局唯一：`<slug>--<tid>--r<round>`。账记在 `registry.json`，用来治撞号。

## registry.json

形状：

```json
{
  "themes": [
    {
      "slug": "<slug>",
      "tasks": [
        {
          "tid": "<tid>",
          "runs": ["<slug>--<tid>--r<round>"]
        }
      ]
    }
  ]
}
```

种子文件本目录 `registry.json` 现为 `{"themes":[]}`。

## main.md 六要素

总主题必含六节：

1. 定位
2. 前因与初衷
3. 目的（observable）
4. 范围锁（正向判据 + 禁止项）
5. 完成判据
6. 止损线

另加字段：

- `budget`
- `human_gate`：`[G1,G2,G3 子集]`。被点名关口的主责角色先经 pi-intercom 消息 supervisor 的 omp 会话（地址 Main），阻塞等 approve；缺省未列 = 全自动。
- `status`：`draft` | `defended` | `executing` | `accepted` | `closed`
- `conclude` 段

## 分任务 `tasks/<tid>.md`

旧 idea 全字段保留：`origin` / `hypothesis` / `method` / `evidence` / `evaluation` / `done_when` / `conclude` / `note`。

加 `locked_to:`，摘录 `main.md` 范围锁判据行。theorist / qa 接单必对 `main.md` 做范围锁首检。

状态机：`[ ]` → `[>]` → `[x]` / `[!]`。

进池硬门换主语继承：entry 门 = pi 写任务时；取单门 = planner / theorist。

## 报告与关口文件命名

- 开题报告：`proposals/<tid>-kaoti.md`
- 中期报告：`proposals/<tid>-zhongqi.md`
- 结题报告：`proposals/<tid>-jieti.md`
- 关口判词：`gates/<tid>-G<n>.decision.md`，内容含判词 + 依据 + 签字 + 时刻。

关口：

- G1 开题批准：examiner 判词 `pass` → theorist 开工令 / `revise` → 打回 pi / `fail` → planner 归案。默认自动。
- G2 中期验收：qa 提包，chair + referee 合议判 `continue` / `rectify` / `stop`。默认自动。
- G3 末期验收：chair 终审报告判 `accept`（结题 → planner 开新题）/ `reject`（终止归档）。默认自动。

止损：qa 对 gate 包判「无有效读数」（valid 率 <0.5 或全部 objective=TBD）连续两次 → chair 直接终止主题 + planner 归案。

referee 在 G2/G3 意见书必须含「对照 main.md 范围锁逐条核对」一节；越锁 finding 直接 stop 级。

## 虚构示例主题树

以下目录树只作格式示意，不入盘。

```
pool/themes/
  registry.json
  attn-lowrank/
    main.md
    tasks/
      t01.md
    proposals/
      t01-kaoti.md
      t01-zhongqi.md
      t01-jieti.md
    gates/
      t01-G1.decision.md
      t01-G2.decision.md
      t01-G2-referee-1.md
      t01-G3.decision.md
    packs/
      t01-G2.md
```

对应账本片段：

```json
{
  "themes": [
    {
      "slug": "attn-lowrank",
      "tasks": [
        {
          "tid": "t01",
          "runs": ["attn-lowrank--t01--r1"]
        }
      ]
    }
  ]
}
```
