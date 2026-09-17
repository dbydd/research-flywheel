---
name: paper-figures
description: 论文图表制作规范。writer 画 figs、排表格时加载：matplotlib 脚本一份 conf 一张图、图型决策、8pt/双通道/灰度无障碍、诚实轴与 Ours 不高亮、面板推理角色与必要性三问、逐面板 QA 表、渲染后视觉复检环、三线表 LaTeX 表格规则、图注与溯源。用户提到论文配图、实验图、图表审阅、表格样式、figs 时使用。
---

# 图表制作

来源三处，都给了出处，改的时候留着：
- 绘图脚本模式：https://github.com/guanyingc/latex_paper_writing_tips （`python_plot_utils/`，CVPR/ECCV 论文实用代码，作者 Guanying Chen）
- 表格与 LaTeX 图规则：同仓库 `paper_writing_tips.pdf`
- 模型结构示意图灵感库：https://github.com/dair-ai/ml-visuals （draw.io 模板，MIT，作者 Omar Sanseviero）

外部蒸馏部件的逐条出处与许可见文末 `## Sources`；一律改写为本飞轮口径，状态枚举与角色名保留英文原串。

## 实验图（matplotlib）

一份 conf 文件配一张图。图的数据、标题、轴、图例全在 conf 里，画图函数不认识具体内容。重跑一个脚本就能复现整张图，改数据只动 conf。

conf 长这样（py dict，命名 `<figure-name>.conf.py`）：

```python
cfg = {
    'title': '',                   # 空串 = 不画标题，论文图一般不要标题
    'xlabel': 'Epochs', 'ylabel': 'Error rate (%)',
    'xlim': [0, 15], 'ylim': [0, 30],
    'legend': ['Ours', 'Prior method A', 'Prior method B'],
    'legend_pos': 'upper right',   # 图例放到曲线不挡头的角
    'curves': [
        {'data_x': 'ours_x.json',   'data_y': 'ours_y.json'},
        {'data_x': 'a_x.json',      'data_y': 'a_y.json'},
        {'data_x': 'b_x.json',      'data_y': 'b_y.json'},
    ],
}
```

要点（来自该仓库的实战风格）：
- 数据存 json（x 一列、y 一列），画图函数 `json.load` 读入。数字从 `research_project/<项目短名>/measured/` 来，脚本里零硬编码数值。
- 每张图配一个薄 `plot_<name>.py`：读 conf、逐条 curve 画、存 PDF。多子图用同一套 conf 模式，`subplot_cfg` 里放每格配置。
- 导出矢量 PDF（`savefig(fmt='pdf')`、`bbox_inches='tight'`），进 LaTeX 用 `\includegraphics` 引用。位图截图进论文会糊。
- 线条风格自定，全篇统一：同一份 style 常量（线宽、marker、色板）放公共文件，conf 只管数据与标注。项目早期就建这份公共文件，全文视觉一致会被审稿人下意识读成专业度。
- 柱状对比用 `multi_bars` 模式（同仓库示例：两组实验并排柱），折线趋势用 `plot_curves`。

## 图型选择（先定图型再写脚本）

| 数据形态 | 图型 | 备注 |
|---|---|---|
| 随步数/时间变化的趋势 | 折线 | 训练曲线、scaling law |
| N 方法 × M 基准 | 分组柱 | 主结果、消融 |
| 单指标多方法排名 | 水平条形 | leaderboard 式比较 |
| 分数分布 | 箱线 / 小提琴 | 方法间散布 |
| 两量相关 | 散点 | 指标相关性、embedding 分析 |
| 矩阵值 | 热力图 | 混淆矩阵、注意力图 |
| 构成占比 | 堆叠柱 | ML 论文不用饼图 |

- 故事匹配不上任何一种图型时，退回去问实验本身设计得好不好：没有合适图表的故事往往意味着没有清晰结论。图审因此是实验设计的探针，不是排版工序。

## 无障碍与可读性硬条

- 矢量 only：PDF/SVG 进 LaTeX，PNG/JPG 是「业余」的第一处 tell；确需位图（照片、显微类）取 300 DPI 以上并给比例尺。
- 最终印刷尺寸下每处文字 ≥8pt。Matplotlib 用小画布（约 150×100 pt）配正常字号，不用大画布配小字。
- 双通道编码：颜色之外必带线型/标记/直标，禁 rainbow 色图，禁红绿作唯一编码。
- 灰度自检（出图前跑一遍）：转灰度打印还分得清每条曲线吗？每个 glyph 都 ≥8pt 吗（mathtext 上标常被缩到父字号 0.7，7pt 的 `$R^2$` 会渲染出 4.9pt；改用 Unicode `R²` 或加大父字号并复核 PDF）？长标签按最终栏宽量过渲染 bbox 吗（别只看源码字号）？
- caption 自含（不读正文也能懂这张图在说什么）；轴名带单位；命名一律具体，禁 `Module A/X/Y`；图例能共享就别逐面板重复。

## 诚实读数条

- Y 轴起点必须诚实：不靠截断基线制造陡峭，跨度要让读者读得出量级。
- Ours 不占优时不要人为高亮某个方法：让读者看见持平。加粗、描边、底色都不许用来制造优势感。
- 不得因为结果是负的、或不利于排版，就藏起会改结论的观测。
- 加了误差棒/区间之后，删掉同样表达这个差的箭头、括号、填充：同一几何不双写同一件事。

## 面板推理角色（多子图先分角色再画）

- 十种角色，逐面板标一个：`setup`（设定/数据）/ `representative`（定性代表例）/ `primary quantitative`（主读数）/ `baseline-control`（对照）/ `decomposition`（分解/残差）/ `stratification`（分层切片）/ `orthogonal validation`（另一条独立证据线）/ `perturbation-stress`（扰动/压力测试）/ `boundary-failure`（边界与失效例）/ `mechanistic`（机制）。
- 弱式反例：`a: R²` → `b: R² 两两比较` → `c: MAPE` → `d: MAPE 两两比较`，四个面板往往归为两种推理角色。强式序列：扰动设计 → 决定性对照 → 全分布或残差 → 分解或边界。
- 必要性三问（逐面板答）：①删掉这块会失去哪一条唯一推论？②那条推论是在确立/推进/限定/框定整图主张中的哪一种？③它是独立证据角色，还是同一结果换了指标/估计器/种子/阈值/视觉编码？
- 四去向：主图（决定性证据、必要对照、中央证伪、会改结论的边界）/ 补充材料（安心件、溯源细节、次级指标、不改解读的稳健性）/ 挪去另一张图（确属另一条主 claim）/ 删并（无独立推论增益）。

## 逐面板 QA 表（交付前逐格填，不许整页扫一眼放行）

| 面板 | 唯一 claim | 中心统计 | 散布/区间 | 重复单元 | 显示标签 | 对齐组/结果 | 碰撞检查 | Pass |
|---|---|---|---|---|---|---|---|---|
| a | 这块专门回答的那个问题 | mean/median/raw | SD/SE/CI/none + 理由 | seeds/folds/slices/subjects | 最终显示标签 | 行列分组、偏差或豁免 | 审计发现 + 数据与误差极值 + 文字 bbox | yes/no |

- 先在最终物理尺寸下逐面板看，再看装配图，Pass 只准 yes/no；重复面板并排比对术语、不确定度定义、轴、色映射是否一致，邀请直接比较的面板必须同 `n`、同分母、同尺度，否则明写豁免。
- 可脚本化的三项：PDF 里每个 glyph ≥8pt、多面板渲染后 plot-area 矩形共享边/宽/高/标签锚/重复 gutter 在 1.5pt 内、碰撞审计无 FAIL。
- 逐面板心算一遍「拿掉这块论点是否仍完整」，完整就合并或删除该面板。

## 渲染后视觉复检环（出码之后、交付之前）

- 步骤：渲染成图 → 渲染图 + 源数据 + 清单一起过视觉复检 → 命中 FAIL 就点名具体问题 → 改画图代码 → 重渲染再复检，最多 2 轮（含首轮共 3 次渲染）。
- 十条清单：值与源数据目视一致（标注 45% 的柱应约占轴程 45%）；所有序列都在，无缺类缺组；误差棒/区间尺度对；两轴都带描述与单位；图例齐全可读；字号在付印尺寸可读、无 <8pt 文字；文字无截断/重叠/出界；两系列颜色不撞；无 chart junk（3D、阴影、无谓网格）；标题与记号格式统一。
- 两轮后仍残留：停手，把残留问题写进图注 `Note:`，并在台账点名待复核；禁继续循环、禁删检项、禁把 FAIL 写成过检。复检状态只准四值：`PASS` / `PASS_WITH_NOTES` / `NEEDS_REVIEW` / `SKIPPED`；无视觉能力时显式记 `SKIPPED`，不假装过检。
- 边界：视觉复检只回答「渲染是否与源数据一致」，不回答「图注的解释是否从数据推出、正文引用它是否撑得住该主张」。后者由溯源映射与 `paper-writing` 的反向提纲负责。

## 表格（LaTeX）

三线表规则（PDF §3，论文表格通用底线）：
1. 只用水准线，竖线全部去掉；顶线/表头线/底线用 booktabs 的 `\toprule/\midrule/\bottomrule`。
2. 数字右对齐，文字居中。数字对齐看小数点。
3. 小数位全列统一。精度给到读者能区分名次即可，多余零删掉。
4. 单位放表头（`Size (GB)`、`mAP (\%)`），单元格里不留单位。
5. 本方法那行加粗（`\textbf{Ours}`）或改行名，别用底色。
6. 表名放表格上方，图名放图下方（LaTeX 惯例，题注永远在物体之上/下各自的固定位）。

增量四条：
7. 表头标指标方向：`PSNR ↑`、`LPIPS ↓`，必要时同处带单位。
8. 同一指标列内小数位一致，baseline 与 Ours 混排时不许各写各的精度；精度下限 = 读者能据此分出名次。
9. 双栏排版下，栏下单图/单表优先放右栏，让读者从左上正文进入不断流。
10. caption 只写协议与记号，不做讨论与解释；细节少时在正文用一句话总结主结果。
11. 一表一信息；消融与属性显式写进行名或属性列；多数据集分组用 `\multicolumn` + `\cmidrule`，不用竖线。

表格里数字多、列数爆，先想横排换竖排、合并列、拆两张表，最后才缩字号。`\small` 以下审稿人骂人。

## 示意图（模型结构、流程）

要画架构/流程/attention 机制图：
- 先翻 ml-visuals 的 `figures/` 找同型模板（transformer、CNN、RNN、attention、训练流程），draw.io 打开改。署名保留 MIT 来源。
- 模板不够用再手绘。导出 SVG/PDF，文字保持可选中（导出时勾 outline text 关闭）。
- 结构性/关系图起手用文本源（mermaid 或 tikz），成图可重生、可 git diff；mermaid 源与 tikz 源存 `papers/<项目短名>/figs/`，成图同目录，一个图一份源，文本源永不为出图而删。

## 交付自检

- 每张图：`python3 papers/<项目短名>/figs/plot_x.py` 在干净环境重跑一次，产物与提交的 PDF 一致。
- 每个数字能在 `research_project/<项目短名>/measured/` 找到出处；figs 目录里有 `README.md` 记 图 → measured 文件 映射。
- LaTeX 里 `\ref` 指向的 label 齐全，图不超版心。
- 脚本绿 ≠ 图对：脚本能跑、PDF 能开、审计器无 FAIL 只证明技术有效。完成要求在全尺寸/最终印刷尺寸下逐项目视比对（图例挡线、标签截断、刻度误读、面板未对齐只在目视里露头）；近似字体、近似面板在参考有具体风格时就是缺陷。同一条适用于 runner 的读数核验。内部诊断工件不冒充交付物：碰撞审计标出的标记 PDF 是 QA 工件，绝不可代替投稿文件。

## Sources

- 图型决策表 → AI-Research-SKILLs/`20-ml-paper-writing/academic-plotting/SKILL.md:314-324` → MIT，改写为七行；其 Gemini 生图链与 `GEMINI_API_KEY` 依赖不搬。
- 色盲安全与灰度/无障碍自检 → 同上 `SKILL.md:163,187`、`references/style-guide.md:8-12,63,296-303` → MIT，改写为三问；其 7pt 底线按本仓 CS venue 口径提到 8pt。
- ≥8pt/小画布、双通道编码、诚实轴与「Ours 不占优不高亮」、命名具体、公共 style 常量、图审当实验设计探针 → Supervisor-Skills/`skills/figure-designer/references/experimental-results.md:24-26,66-69,95-105` 与 `references/design-rules.md` → 该技能 frontmatter CC BY 4.0（仓库根 CC BY-NC-SA 4.0），只取判据中文重写，未复制文本。
- 「脚本绿≠图画对」的保真契约与「内部诊断工件不冒充交付物」→ Supervisor-Skills/`skills/drawio-reconstruction/SKILL.md:16-29` → 该件自带 MIT LICENSE（VCG-Bench Authors）；`.drawio` 导出链与 worker 编排不搬。
- 十种面板推理角色 + 镜面对照弱式 + 必要性三问与四去向 + 不藏负观测 → nature-skills/`skills/nature-figure/references/multipanel-evidence-architecture.md:67-79,84-97,217-237`；逐面板一行表、三项可脚本化、glyph 底线与 mathtext 上标 0.7 坑、1.5pt 对齐、标记 PDF 仅 QA 工件 → 同仓库 `skills/nature-figure/references/qa-contract.md:40-64,258-280` 与 `SKILL.md:117-118` → 根 Apache-2.0（该子技能无独立许可），角色名保留英文、字段直借并中文化；期刊专属项（89/183mm 版心、显微比例尺、image-integrity、export bundle）不取。
- 渲染后视觉复检环（十条、FAIL→改码→最多 2 轮→残留写图注 `Note`、四值状态、与解释正确性的边界）→ academic-research-skills/`academic-paper/references/vlm_figure_verification.md` → 仓库整仓 CC BY-NC 4.0（非开源许可），只搬流程与判据，未复制清单原文；APA 7.0 项按 CS venue 改写。
- 表格增量四条（方向箭头、同列小数位、双栏右栏、caption 分工）与「无合适图型即回问实验」 → Research-Paper-Writing-Skills/`references/experiments.md:55-88` → MIT，改写；其 booktabs/禁竖线/禁双线与我们三线表重复，未再抄。
- 原有绘图脚本、三线表、ml-visuals 条款 → guanyingc/latex_paper_writing_tips 与 dair-ai/ml-visuals（MIT），保留上方出处行。
- 未取：nature-skills/`skills/nature-figure/assets/figures4papers/`（上游无 LICENSE 的第三方留档），一字一图未取其样式。

## 与自家条款的接缝

- 数字只从 `research_project/<项目短名>/measured/` 引：`measured/` 由 runner 落账（CSVLogger 主账），figs 脚本只读产物、零硬编码、不为出图另起长跑；指不回文件的数字删掉。预算类读数按「计划 / 实测 / 差」三列口径呈现（键名与分列规则正本在 `ml-runbook`），计划值不得画成实测曲线（禁区四条：不伪造 `measured/`）。
- 解释文八条优先于外部图注与表格细则：结论先行、对象先行、术语按依赖序、数字带单位与量级。阈值、效应、噪声同轴并报，读者能自行判断哪条结论到分辨极限。
- 三约束在图面的投影：确定性 = 重复单元与误差定义逐面板写清（seed/fold/slice，缺项回问 runner 用一句短事实问句，不许含糊）；泄漏 = held-out 与训练面读数不得同面板混画而不标注；预算 = 复检环最多 2 轮，超限记 `NEEDS_REVIEW` 交 qa。
- 覆盖类判据（每主 claim 一个验证实验、每模块一个消融、消融包构成）归 `experiment-design`；本 skill 只管已定实验怎么画。评审席对图的攻击写法与 severity 判级归 `review-discipline`；引用核验与数字保真分级归 `evidence-discipline`。
- 文件即真相：conf、`plot_<name>.py`、源数据、`README.md` 映射一起进 git，发布位在 `papers/<项目短名>/figs/`，草稿落 role ws 的 `work/`。出图角色目视复核后自报 `PASS`；qa 放门只认工件与台账行，口头「图画好了」至多记 `REPORTED_DONE_UNVERIFIED`（口径见 `paper-writing` 的修订三维台账）。
- 段权与追加式：`papers/<项目短名>/figs/` 下的 conf、脚本、`README.md` 映射行进 git 后按追加式处理（改面板就在 README 追加一行新映射，不回改历史行；旧版靠 git 取回）。正文里的图指涉句属自书角色的段落，别的角色不代改，referee 意见书更不碰稿面。
- 表格美学冲突裁决：外部「最佳/次佳可用克制底色」与我们「本方法行只用加粗或改行名、不用底色」冲突，以自家为准；底色最多用于表头分组行。
- scribe 挂起中：图的正文指涉句与结论句由画它的自书角色补（结题整改期文字归 speculator，送审包归 qa），figs 不设代笔位。
