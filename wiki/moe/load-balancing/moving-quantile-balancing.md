---
title: Moving Quantile Balancing：序列级均衡
slug: moving-quantile-balancing
type: concept
created: 2026-09-22
updated: 2026-09-22
sources:
  - blogs/readings/2026-06/moe/spaces-ac-cn/moe-huanyouji-reading.md
  - raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/moe-huanyouji-8.extracted.md
---

# Moving Quantile Balancing：序列级均衡

Loss-Free 负载均衡引入的偏置在全局共享：给每个专家配一个与输入无关的量，加在 Router 打分上改变专家选择顺序，统计口径是整个训练批里各专家被选中的次数（来路见 [[loss-free-balancing]]）。序列级均衡统计单个序列内部各专家是否被用得均匀，管的是同一条序列里的分布。序列是一段按顺序排列的 token，token 是模型处理文本的最小单位。此前的序列级均衡靠序列级辅助损失（辅助损失的来路见 [[auxiliary-loss]]）。《MoE环游记：8、强制序列级均衡》要找的是序列级均衡的 Loss-Free 对应物，给出的方法叫 Moving Quantile Balancing（MQB）。全局偏置与分位数的关系见 [[quantile-balancing]] 与 [[one-step-quantile-solution]]。

## 站外两条思路的瓶颈

第八篇先对照站外作者 Jonathan Chang 的《Causal Routing Bias for Aux-Loss-Free MoE Training》里的两条思路。第一条是对分数做滑动平均，再用它决定激活，属经验做法。第二条是按测试时训练为每个 token 分配一个偏置并逐 token 更新，测试时训练指在测试阶段也根据当前输入继续更新一部分参数。第二条等价于一个非线性 RNN；RNN 沿序列逐步递推，后一步依赖前一步的状态，逐步更新因此无法并行，序列一长就成为瓶颈。

## 从累积分位数到滑动分位数

MQB 先把逐 token 偏置写成前缀上的分位数，也就是累积分位数，再用固定窗口内的滑动分位数替换，把复杂度从平方级降到线性。

## 把分位数估计换成分布估计

真正解开瓶颈的一步是把分位数的估计转成分布的估计。分数落在 [0,1] 内，Sigmoid 的输出正好在这个区间，可以靠它保证；Sigmoid 是一条把任意实数压进 0 与 1 之间的函数。把 [0,1] 等分成 b 个桶，对分数做 one-hot，one-hot 指向量里恰有一个分量为 1、其余分量为 0。沿序列维度做这种向量的 EMA（指数滑动平均，用一个系数把历史值与当前值加权合并），由累积概率读出 1 − k/n 分位数，作为该 token 的 β。分位数指把样本按大小排序后按累积比例取的位置，累积分布到 1 − k/n 表示这一位置以上的样本占 k/n，正好对应每个专家被激活的目标比例。

EMA 是线性可并行的运算，序列级均衡由此第一次以 Loss-Free 的方式做到。EMA 本质上是 RNN，推理阶段要多存一个 n×b 的 State，也就是沿序列累积的那份路由状态，作者认为 b = 100 已经够用。

![[raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/assets/moe-huanyouji-8-fig1.png]]

图：上图为 Router 分数的局部分布与直方图密度近似，下图为对应的累积分布与阈值读取，标注出分位数阈值 β 约为 0.36。图中的目标概率 0.7 是原理示意的取值；实验配置是 128 选 4，对应的目标概率 1 − k/n 约为 0.97。图取自《MoE环游记：8、强制序列级均衡》。

## Top-k 版本与强度系数 λ

MQB 的 Top-k 版本这样处理：先削平 Router 的局部高峰，再取 Top-k，最后补一步全局 QB 恢复均衡。Top-k 指从高到低取打分最高的 k 个专家。λ 是一个系数，用来削弱序列均衡的强度，做法是把 β 乘以 λ。

## 实验

实验用总参数量约 3B、128 选 4 的 MoE，滑动平均系数 0.99、分桶数 100，用 [[maxvio]] 度量最不均衡的第一层，MaxVio 指各专家负载相对均匀目标的最大偏差。

取 λ 为 1 时，第一层的 MaxVio 全程在 0.2 以下，均衡接近完美，代价是 Loss 比不加序列级均衡时差 0.06；只做全局均衡的 QB 落在 0.7 至 0.9；SignSGD 版 Loss-Free 在一万步前维持在 1.5 至 2。把 λ 调到 0.3 后，第一层的 MaxVio 仍明显低于只做全局均衡的 QB，Loss 基本不掉。第八篇据此给出结论：完美的序列级均衡对效果损伤明显，λ 取 0.3 左右能大致保证效果无损，同时改善每一层的均衡。

![[raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/assets/moe-huanyouji-8-fig2.png]]

![[raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/assets/moe-huanyouji-8-fig3.png]]

图：上图是 λ 为 1 的 MQB、QB 与 SignSGD 三者的第一层 MaxVio 对比；下图是 λ 取 0.3、λ 取 1 与只做全局均衡的 QB 的第一层 MaxVio 对比。两图横轴到 1.6 万步。均取自《MoE环游记：8、强制序列级均衡》。

## 留下的问题

是否需要序列级均衡、需要何种程度、为什么需要，源文都不给标准答案，留作开放问题。分桶方式是 Sigmoid 激活后均匀离散化，更精细的分桶留作实验空间。EMA 是 RNN，推理多一个 n×b 的 State。这三处口子在本仓各有对应的想法页：强度系数按层自适应见 [[layer-wise-routing-strength|序列级均衡强度逐层自适应]]；分桶粒度见 [[quantile-bucketing-schemes|分桶方式实验：分位数字典与 logit 空间分桶]]；推理期多出来的那份 n×b 状态与注意力缓存的合并见 [[moe-routing-state-and-kv-cache|路由 State 与滑窗注意力 KV cache 合并管理]]。

各代方案的差别与超参数账见 [[load-balancing-methods-comparison]]；第八篇的原始论述见 [[moe-huanyouji-8-abstract|MoE环游记：8、强制序列级均衡 摘要]]。
