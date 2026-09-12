---
name: paper-writing
description: 论文写作规范与 LaTeX 细则。writer 成稿、critic 文字审时加载：稿件骨架、引用与措辞规则、LaTeX 排版雷区、修订记录。用户提到写论文、改稿、润色、审稿文字面、LaTeX 格式时使用。
---

# 论文写作

细则来源：https://github.com/guanyingc/latex_paper_writing_tips 的 `paper_writing_tips.pdf`（Guanying Chen，CVPR/ECCV 实战总结），加本飞轮自家流程约定。

## 稿件骨架（每节回答一个问题）

- Abstract：问题 → 方法一句话 → 最强结果带数字 → 意义。四到六句，零引用，零缩写未定义先用。
- Introduction：领域地位 → 缺口（现有方法哪里不行，引文献撑住）→ 我们做了什么 → 贡献列表（三条上下，每条可验证）→ 路线图段可选。
- Related Work：按技术线索分组叙述，每组收一句"与本文的关系"。按时间罗列流水账是拒稿常见理由。
- Method：符号先定义后用；一张总览图配数据流叙述；每小节对应一个组件。
- Experiments：先 setup（数据、指标、实现细节、硬件），后主结果，再消融。每张表/图正文必有指涉与结论句，数字与 `measured/` 一致。
- Conclusion：局限写诚实，future work 一句一个。

## LaTeX 排版雷区（PDF §2 逐条）

标点与空格：
- 左括号前留空格：`network (CNN)`，贴写算错。
- 句号、逗号前不留空格。
- 引用前留空格：`problem [1]`。
- 公式末尾要有标点（句子的一部分），全部公式编号，交叉引用才有着落。
- 双引号用 `` `` `` 和 `''`，直引号 `"` 排版出来是错字。
- 句首大写。

引用与指涉：
- Abstract 不放引用。
- 表格指涉永远写全 `Table 1`，句子里 `Tab. 1` 算错。
- 图指涉：句首 `Figure 1`，句中 `Fig. 1`。`Fig.1` 缺空格算错。
- 表题在表上方，图题在图下方。浮动体尽量放页面顶部。
- 高频词定义宏：`\newcommand{\NetName}{...}`，改名一处改完。
- `i.e.`/`e.g.` 用 `\ie`/`\eg` 宏（防句读错断、防换行断坏）。

## 措辞纪律

- 主张强度对齐证据：消融只涨 0.1 就不能写 `significantly outperforms`；`state-of-the-art` 要有对照表撑。
- 全篇时态一致：描述已有工作现在时/过去时二选一，本文实验结果过去时或现在时择一。
- 每个数字出现处，critic 都能指回 `measured/` 一个文件；指不回去的数字删掉。
- 图表未引用的先删，引用的先补指涉句。

## 流程约定（本飞轮）

- 成稿 `papers/<run-id>.md`；LaTeX 工程放 role ws 私有区，定稿一次性发布。
- 每轮修订在稿件头部留一行修订记录：日期、改了什么、响应 critic 哪条。
- critic 打回的文字问题，逐条改，逐条在修订记录里销账。
