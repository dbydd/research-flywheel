---
name: paper-figures
description: 论文图表制作规范。writer 画 figs、排表格时加载：matplotlib 脚本一份 conf 一张图、三线表 LaTeX 表格规则、图注与溯源。用户提到论文配图、实验图、表格样式、figs 时使用。
---

# 图表制作

本规范覆盖 matplotlib 实验图、LaTeX 表格、模型示意图、交付自检。

## 来源

本规范整合三处外部资料。修改本文件时，保留全部出处。

- 绘图脚本模式：https://github.com/guanyingc/latex_paper_writing_tips （`python_plot_utils/`，CVPR/ECCV 论文实用代码，作者 Guanying Chen）
- 表格与 LaTeX 图规则：同仓库 `paper_writing_tips.pdf`
- 模型结构示意图灵感库：https://github.com/dair-ai/ml-visuals （draw.io 模板，MIT 许可证，作者 Omar Sanseviero）

## 实验图（matplotlib）

实验图用 matplotlib 画。一份 conf 文件对应一张图。

conf 保存图的全部信息：数据、标题、轴、图例。画图函数读 conf，函数体不含具体内容。重跑同一个脚本，复现整张图。改数据时只改 conf。

conf 文件是一个 py dict，文件名格式为 `<figure-name>.conf.py`：

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

下列要点来自该仓库的实战风格：

- 数据存成 json 文件，x 一列，y 一列。画图函数用 `json.load` 读入。
- 数值全部来自 `runs/<run-id>/measured/`。脚本里零硬编码数值。
- 每张图配一个薄脚本 `plot_<name>.py`。脚本读 conf，逐条 curve 画线，存成 PDF。
- 多子图沿用同一套 conf 模式。每格配置放在 `subplot_cfg`。
- 导出矢量 PDF：`savefig(fmt='pdf')` 加 `bbox_inches='tight'`。LaTeX 里用 `\includegraphics` 引用。位图截图进论文会糊。
- 线条风格全篇统一。线宽、marker、色板写成同一份 style 常量，放公共文件。conf 只管数据与标注。
- 柱状对比用 `multi_bars` 模式，同仓库示例是两组实验并排柱。折线趋势用 `plot_curves`。

## 表格（LaTeX）

三线表规则来自 PDF §3。这些规则是论文表格的通用底线。

1. 表格只用水平线。竖线全部删除。顶线、表头线、底线用 booktabs 的 `\toprule/\midrule/\bottomrule`。
2. 数字右对齐，文字居中。数字按小数点对齐。
3. 同一列的小数位统一。精度到读者能区分名次即可。多余的零删除。
4. 单位放表头，如 `Size (GB)`、`mAP (\%)`。单元格内零单位。
5. 本方法那一行加粗（`\textbf{Ours}`），或改行名。行底色保持默认。
6. 表题放表格上方，图题放图下方。这两个位置是 LaTeX 固定惯例。

表格装不下全部列时，按顺序处理：横排换竖排、合并列、拆成两张表。缩字号排在最后一步。字号最低用到 `\small`。再小的字号会招审稿人批评。

## 示意图（模型结构、流程）

示意图覆盖模型结构、系统流程、attention 机制。

- 先翻 ml-visuals 的 `figures/` 目录，找同型模板：transformer、CNN、RNN、attention、训练流程。找到模板后用 draw.io 打开修改。署名保留 MIT 来源。
- 如果模板不够用，则手绘。导出 SVG 或 PDF。导出时取消勾选 outline text，文字保持可选中。
- mermaid 源与 tikz 源存 `papers/<run-id>/figs/`。成图放同一目录。一张图对应一份源。

## 交付自检

交付前逐项检查。

- 每张图：在干净环境重跑一次 `python3 figs/<run-id>/plot_x.py`。重跑产物与提交的 PDF 一致。
- 每个数字能在 `measured/` 里找到出处。`figs/` 目录里有 `README.md`，记录「图 → measured 文件」映射。
- LaTeX 里 `\ref` 指向的 label 全部存在。图不超版心。
