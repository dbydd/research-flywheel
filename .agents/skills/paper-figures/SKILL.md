---
name: paper-figures
description: 论文图表制作规范。writer 画 figs、排表格时加载：matplotlib 脚本一份 conf 一张图、三线表 LaTeX 表格规则、图注与溯源。用户提到论文配图、实验图、表格样式、figs 时使用。
---

# 图表制作

来源三处，都给了出处，改的时候留着：
- 绘图脚本模式：https://github.com/guanyingc/latex_paper_writing_tips （`python_plot_utils/`，CVPR/ECCV 论文实用代码，作者 Guanying Chen）
- 表格与 LaTeX 图规则：同仓库 `paper_writing_tips.pdf`
- 模型结构示意图灵感库：https://github.com/dair-ai/ml-visuals （draw.io 模板，MIT，作者 Omar Sanseviero）

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
- 数据存 json（x 一列、y 一列），画图函数 `json.load` 读入。数字从 `runs/<run-id>/measured/` 来，脚本里零硬编码数值。
- 每张图配一个薄 `plot_<name>.py`：读 conf、逐条 curve 画、存 PDF。多子图用同一套 conf 模式，`subplot_cfg` 里放每格配置。
- 导出矢量 PDF（`savefig(fmt='pdf')`、`bbox_inches='tight'`），进 LaTeX 用 `\includegraphics` 引用。位图截图进论文会糊。
- 线条风格自定，全篇统一：同一份 style 常量（线宽、marker、色板）放公共文件，conf 只管数据与标注。
- 柱状对比用 `multi_bars` 模式（同仓库示例：两组实验并排柱），折线趋势用 `plot_curves`。

## 表格（LaTeX）

三线表规则（PDF §3，论文表格通用底线）：
1. 只用水准线，竖线全部去掉；顶线/表头线/底线用 booktabs 的 `\toprule/\midrule/\bottomrule`。
2. 数字右对齐，文字居中。数字对齐看小数点。
3. 小数位全列统一。精度给到读者能区分名次即可，多余零删掉。
4. 单位放表头（`Size (GB)`、`mAP (\%)`），单元格里不留单位。
5. 本方法那行加粗（`\textbf{Ours}`）或改行名，别用底色。
6. 表名放表格上方，图名放图下方（LaTeX 惯例，题注永远在物体之上/下各自的固定位）。

表格里数字多、列数爆，先想横排换竖排、合并列、拆两张表，最后才缩字号。`\small` 以下审稿人骂人。

## 示意图（模型结构、流程）

要画架构/流程/attention 机制图：
- 先翻 ml-visuals 的 `figures/` 找同型模板（transformer、CNN、RNN、attention、训练流程），draw.io 打开改。署名保留 MIT 来源。
- 模板不够用再手绘。导出 SVG/PDF，文字保持可选中（导出时勾 outline text 关闭）。
- mermaid 源与 tikz 源存 `papers/figs/<run-id>/`，成图同目录，一个图一份源。

## 交付自检

- 每张图：`python3 figs/<run-id>/plot_x.py` 在干净环境重跑一次，产物与提交的 PDF 一致。
- 每个数字能在 `measured/` 找到出处；figs 目录里有 `README.md` 记 图 → measured 文件 映射。
- LaTeX 里 `\ref` 指向的 label 齐全，图不超版心。
