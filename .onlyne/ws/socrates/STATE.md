本文件是 socrates 的手帐面：记叙段写过程，条目段写本 role 索引；它不在注入链上

## 记叙

- Qwen3.8-Flash-Next 精读第一轮对质我收了 master 的任务，输入只有报告本体，按角色约定没读残差流，也没开仓里别的上游文件。
- 我把全篇逐句过了一遍，并以一无所知读者自检；报告自己嵌的 assets 图点开八张核了锚点，fig6 与 fig12 两个文件混进了前一幅图的面板，fig1、fig5、fig7、fig8 干净。
- 我判不放行、退回 master：必改十五项（术语混用前训练与预训练、承重表嵌入行端点错位、Table 7 与 Table 9 对账句自相矛盾、ramp 句每步与 524B token 互斥、四个邻近设置只列三项、小一个量级与二点五倍不符、DeepSeek-V4.1-Flash 一侧欠账、四处对比句式、拦在预训练指标之外句义两面、对称性理论工作未冠名、跨层共享索引句读不通、嵌图混面板、Stage 1 描述不一、Table 8 引表与九项口径不符、摘要页现状句与仓根记录冲突），文字与自足另五组。
- 复算过的部分我留了证：GDN 递推合并式、51B 表两法同积、批量三档差值、生产对照 0.058、Table 11 胜负与 2.59、Table 9 走势、判定一的 0.005/0.059，清单「过」一节在。
- 清单全文落 `tools/scratch/qwen3.8-flash-next-socrates-round1-checklist.md`，随 handoff 交给 master。
- 第二轮我收了 master 的回改任务，输入是第一轮清单与回改后的报告本体，同样没读残差流里列的上游文件。
- 二十项逐条现场核对，全部落实；改动处数字复算（Table 9 的 50V 七列和 337.52 与九项和 482.12、47.94×9=431.46、50.66/9=5.63 对 53.57−47.94=5.63；1.585−1.526=0.059；1.76/√2、1.76×√2、8.4M×1.25；2.04/4.86、2.13/5.88），两张新裁图点开核了面板：fig6-kernel 四块延迟面板、fig12-gate-isolation 三块门控面板，各自只含目标图，图注的 (a)(b)(c) 只剩一套候选。
- 判放行，清单落 `tools/scratch/qwen3.8-flash-next-socrates-round2-checklist.md`；两处余留观察（TPP 括注同句重复、本件 Table N 写法并存）注明不构成不放行。
- 交付 scraper 时 `onlyne_handoff` 四次报 `connection lost`、ledger 零落账；改用本工作区点名的 `onlyne_send kind:"task"` 交付成功（ledger 帧 b603a328），客户端把它落成 hop 0 新族 8b367cc6、`parent_task` 为空——血缘断口在 ledger 可见，handoff 工具链路待 supervisor 修。

## 条目

|条目|内容位置|
|---|---|
|Qwen3.8-Flash-Next 精读第一轮对质清单（十五项必改加五组文字项，判不放行退 master）|`tools/scratch/qwen3.8-flash-next-socrates-round1-checklist.md`|
|Qwen3.8-Flash-Next 精读第二轮对质清单（二十项全改、判放行交 scraper）|`tools/scratch/qwen3.8-flash-next-socrates-round2-checklist.md`|
