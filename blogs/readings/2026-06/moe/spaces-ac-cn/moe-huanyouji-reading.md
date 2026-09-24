---
title: MoE环游记 系列精读
slug: moe-huanyouji-reading
type: reading
created: 2026-09-22
updated: 2026-09-22
sources:
  - raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-1/moe-huanyouji-1.extracted.md
  - raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-1/moe-huanyouji-1.html
  - raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-2/moe-huanyouji-2.extracted.md
  - raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-2/moe-huanyouji-2.html
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3/moe-huanyouji-3.extracted.md
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-3/moe-huanyouji-3.html
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-4/moe-huanyouji-4.extracted.md
  - raw/2025-03/moe/spaces-ac-cn/moe-huanyouji-4/moe-huanyouji-4.html
  - raw/2025-05/moe/spaces-ac-cn/moe-huanyouji-5/moe-huanyouji-5.extracted.md
  - raw/2025-05/moe/spaces-ac-cn/moe-huanyouji-5/moe-huanyouji-5.html
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/moe-huanyouji-6.extracted.md
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/moe-huanyouji-6.html
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-7/moe-huanyouji-7.extracted.md
  - raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-7/moe-huanyouji-7.html
  - raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/moe-huanyouji-8.extracted.md
  - raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/moe-huanyouji-8.html
  - raw/2026-06/moe/spaces-ac-cn/moe-huanyouji-9/moe-huanyouji-9.extracted.md
  - raw/2026-06/moe/spaces-ac-cn/moe-huanyouji-9/moe-huanyouji-9.html
resource: raw/2026-06/moe/spaces-ac-cn/moe-huanyouji-9
---

# MoE环游记 系列精读

- 本体：系列九篇的资源本体分别落在 `raw/2025-02/moe/spaces-ac-cn/moe-huanyouji-1/` 至 `raw/2026-06/moe/spaces-ac-cn/moe-huanyouji-9/` 九个同级目录，本页以第九篇目录为系列主条目
- 原著：苏剑林《MoE环游记》九篇，科学空间（spaces.ac.cn），2025 年 2 月至 2026 年 6 月
- 摘要：九篇摘要页逐篇列在本页「关联」一节

## 问题与做法

MoE（Mixture of Experts，混合专家）的做法是把 Transformer 里的 MLP 层换成若干并行的小网络，每个 token 只走其中几个。MLP 是 Transformer 里的全连接前馈层；token 是模型处理文本的最小单位，通常是一小段词或子词，也是全文计量的单位。参数量随专家总数增长，计算量随实际激活的专家数增长。这套系列共九篇：前四篇处理 MoE 的静态形式与偏置，第五篇反思均匀分布这个目标本身，第六至八篇把负载均衡写成优化问题并一路解到序列级，第九篇换到梯度一侧讨论门控归一化。

**第一篇《MoE环游记：1、从几何意义出发》：把「选哪些专家」写成几何问题。** 常规 MLP 层写成 $y=f(xW^{(A)})W^{(B)}$，其中 $x$ 是输入行向量，$W^{(A)}$、$W^{(B)}$ 是两个参数矩阵，$f$ 是逐元素激活函数，也就是对每个分量独立作用的非线性函数。按参数矩阵的列与行分块，这一层的输出等于 $n$ 个小网络输出之和，每个小网络的中间宽度 $c$ 等于 $D/n$，这里的 $D$ 是原 MLP 层的中间宽度。每个小网络就是一个 Expert。MoE 要回答的问题是：能否只挑 $k$ 个小网络的和来逼近原来 $n$ 个之和，把计算量降到 $k/n$。在 Expert 输出向量两两正交的近似下，逼近误差等于被丢弃向量的模长平方之和，最优挑法是保留模长最大的 $k$ 个。这个挑法带一个循环依赖：算模长要先算全部 Expert。第一篇的解法是把每个 Expert 重新参数化为方向与模长两部分，方向 $e_i$ 由归一化得到，也就是把向量除以其模长、只留方向，模长 $\rho_i$ 交给一个从 $d$ 维到 $n$ 维的线性变换加非负激活来预测，这里的 $d$ 是 token 向量的宽度，这个小模型就是 Router。计算顺序由此变成先算全部 $\rho$、选出前 $k$ 个、再算对应的 $e_i$、乘上 $\rho_i$ 求和，写作 $y=\sum_{i\in\operatorname{argtop}_k\rho}\rho_i e_i$。这条式子是整个系列的基线形式，后面八篇反复回到它。该视角还给出一个副产品：$\rho$ 的几何意义是模长，它不需要按概率分布那样归一化。Sigmoid 的输出落在 0 与 1 之间，ReLU 的输出非负，这类非负激活都可以用。这个自由度在第三篇被 DeepSeek 用上。

**第二篇《MoE环游记：2、不患寡而患不均》：Aux Loss 的来路是一次直通估计。** MoE 训练时先按专家分配算力，再把 token 路由过去。分配不均会造出两类浪费：一部分专家长期闲置，也就是 Dead Expert，等于花了大参数的显存只训出小参数的效果；另一部分专家过载，只能丢弃部分 token，也就是 Token Drop。通行做法是加一个辅助损失 Aux Loss 来推动均衡。第二篇先用记号把这件事写清楚：把打分除以全体打分之和，得到归一化打分 $p$，Top-k 指示向量记 $f$（选中的分量为 $1/k$，未选中的为 0），$P$ 与 $F$ 分别是 $p$、$f$ 在全体 token 上的平均，$F$ 就是当前的负载分布。文献里的 Aux Loss 写作 $F\cdot P$，这里的「·」是内积，把两个同长向量的对应分量相乘再求和，有些文献会多乘一个 $n$。第二篇的贡献是补上这条损失的来路：作者手头的文献与科普多半不加证明地沿用它。他从「让 $F$ 逼近均匀分布」出发写出距离损失，再用直通估计（STE）处理不可导项；STE 的前向指正常算出输出，反向指算梯度，做法是前向保留不可导的 $F$，反向把 $F$ 换成它的可导近似 $P$。求梯度后发现结果恰好落在 $F\cdot P$ 上。由此得到一条一般配方：先按想要的负载分布构造损失，实现时把 $F$ 换成 $P+\operatorname{sg}(F-P)$，其中 $\operatorname{sg}$ 表示停止梯度。作者同时点出读数条件：$F\cdot P$ 承载的是等效梯度的意义，把它代进自动求导得到的梯度与那个可导的距离损失求出的梯度相同，它的数值下降与均衡程度改善是两件事。

**第三篇《MoE环游记：3、换个思路来分配》：用偏置把均衡从损失函数里拿走。** Aux Loss 的麻烦是权重系数要调，调低起不到均衡作用，调高会损害语言模型损失。DeepSeek 在《Auxiliary-Loss-Free Load Balancing Strategy for Mixture-of-Experts》（arXiv:2408.15664）里换了一条路：保留 Router 的打分结果，把分配方式改掉。给每个 Expert 配一个输入无关的偏置 $b$，用 $\operatorname{argtop}_k(\rho+b)$ 选专家，乘到 Expert 上的仍是 $\rho_i$，$b$ 在训练结束后固定，训练与推理同形。第三篇的推进在于：$b$ 没有梯度，作者沿用第二篇的 STE 配方把它的更新规则从 Aux Loss 视角推了出来，得到按负载偏差的符号更新的公式，与原论文取用的符号梯度下降 $b\leftarrow b-\gamma\cdot\operatorname{sign}(F-Q)$ 一致。这里 $Q$ 是目标负载分布，均匀时每个分量取 $1/n$；$\operatorname{sign}$ 取符号，这种用符号做梯度下降的更新叫 SignSGD。两条路线梯度同源。第三篇对 Loss-Free（不用 Aux Loss、改用偏置来做均衡的做法）本质的判断是：新意落在「一个偏置项足以达到负载均衡」这个结论上，均衡只优化新引入的 $b$，语言模型损失优化其余参数，两边的优化参数被隔离开。文中还有两处改良与细节：用 RMS Norm 替代 $\operatorname{sign}$，也就是把向量除以其各分量平方均值的平方根，保留偏差的相对大小，减少已接近均衡的专家来回震荡；把打分的激活拆成两路，加偏置的那一路用 Sigmoid，乘到 Expert 上的门控用别的单调非负激活，这样能继续复用原论文的 $\gamma=0.001$。最后留下一笔：全体 $b$ 分量同加一个常数不影响排序，这个冗余自由度留到下一篇用。

**第四篇《MoE环游记：4、难处应当多投入》：激活数跟着 token 难度浮动。** 第四篇从「每个 token 的难度不同，难的 token 应当多配专家」出发。它接走第三篇留下的冗余自由度：先把更新规则整体去均值腾出这个自由度，再把激活规则从 $\operatorname{argtop}_k(\rho+b)$ 改成 $\operatorname{argwhere}(\rho+b>0)$，也就是把所有满足 $\rho+b>0$ 的专家都选中，每个 token 激活的专家数量随难度浮动，同时免掉排序这一步。更新目标同时管两件事：负载分布逼近均匀，平均激活数逼近 $k$ 作预算控制。作者把两件事合并化简成一步符号梯度；未合并的版本由三段组成，分别是负载均衡项、去均值项与预算控制项，实测它在训练前期的均衡与预算抖动更小，合并成一步的版本抖动更大。初始阶段 $b$ 取零会让每个 token 选满所有专家，造成大量 Token Drop，第四篇给出在 Router logits（Router 输出的未归一化打分）近似正态的假设下用模拟与二分法估计初始 $b$ 的脚本。这一篇还梳理了动态激活一支的相关工作，共同的难题是激活数浮动之后怎么把平均预算管住：AdaMoE 与 MoE++ 在专家中混入空白或零计算专家，用零计算间接削减激活数；把 Top-k 换成 Top-p 的做法难以准确控制平均预算（Top-p 指按打分从高到低累计，到累计概率达到一个阈值为止，把落在其中的专家都选中）；Ada-K Routing 另设模块预测激活数并用强化学习训练；DA-MoE 借 Attention 分数识别重要 token，Attention 是 Transformer 里让每个位置按相关度加权聚合其它位置的层；ReMoE 以零阈值选择专家，用 Aux Loss 实现均衡与预算控制。

**第五篇《MoE环游记：5、均匀分布的反思》：均匀分布要付效果代价。** 第五篇提出一个反问：抛开效率，均匀分布一定导向最好的效果吗？它拿 DeepSeekMoE（《DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models》，arXiv:2401.06066）的两件改进作答。Shared Expert 把 $n$ 选 $k$ 改成 $n-s$ 选 $k-s$，另有 $s$ 个专家必然被选中，总专家数与激活专家数都不变，参数量与推理成本不变。几何理解是：专家之间的共性对应向量夹角小于 90 度，这与第一篇的正交假设冲突；把 Shared Expert 视作 Routed Expert 的均值、让 Routed Expert 学习残差，正交假设更容易成立。Routed 侧的权重 $\rho$ 与 Shared 侧的无权相加容易比例失衡，第五篇给出让两侧在初始化阶段模长接近一致的比例因子 $\lambda$，用数值模拟估计：对 DeepSeek-V2 的配置得到约 16，该配置的 config.json 里 $\lambda$ 取 16.0；对 DeepSeek-V3 的配置得到约 2.83，该配置的 config.json 里 $\lambda$ 取 2.5。Shared Expert 造成的目标负载分布自身不均匀，均匀分布的最优性由此看到了一个具体反例。Fine-Grained Expert 把每个专家缩小一半、改成 $2n$ 选 $2k$，总参数与激活参数都不变，可选组合数从 $\binom{n}{k}$ 增到 $\binom{2n}{2k}$。第五篇另给一条解释，用下面这张图说明：更多、更细的专家能更好地覆盖现实世界的非均匀性。

![[raw/2025-05/moe/spaces-ac-cn/moe-huanyouji-5/assets/moe-huanyouji-5-fig1.png]]

图：左侧是知识的一大一小两团分布，右上用两个总面积相同的大圆覆盖，右下改用八个总面积相同的小圆覆盖，小圆的贴合更细。图取自《MoE环游记：5、均匀分布的反思》正文。

源文也把代价写清了：专家数 $n$ 越大，负载越不均衡，通信与协调成本上升，权衡之下存在一个效果与效率都友好的舒适区间。

**第六篇《MoE环游记：6、最优分配促均衡》：负载均衡是一道等式约束的线性规划。** 第六篇把负载均衡写成等式约束下的线性规划：有 $m$ 个 token、$n$ 个专家，打分矩阵记 $s$，约定每个 token 恰好激活 $k$ 个专家，每个专家恰好被激活 $mk/n$ 次，在这个约束下求总分最高的分配方案。求解走的是对偶：给每个等式约束配一个待定乘子，按 token 的乘子记 $\alpha$、按专家的乘子记 $\beta$，把乘子乘上约束再加进目标函数，带约束的问题就变成不带约束的极大极小问题；这类线性目标与凸可行集满足 Minimax 定理的条件，$\max$ 与 $\min$ 可以交换顺序。交换后每个分配变量的取值由 $s$ 减去两个乘子之和的符号决定，整个问题按行分裂成 $m$ 个独立子问题、按列分裂成 $n$ 个独立子问题，两组交替最小化，$\alpha$ 与 $\beta$ 正是后文的行偏置与列偏置。解的形式很干净：每一行取 $s$ 减去列偏置后的第 $k+1$ 大元素，每一列取 $s$ 减去行偏置后的第 $mk/n+1$ 大元素，两者都是对应维度的 $1-k/n$ 分位数。分位数是把样本按大小排序后按累积比例取的位置；累积分布到 $1-k/n$，意思是该值以上的样本占 $k/n$，正好对应每个专家被激活的目标比例。两种取法说的是同一件事：第 $k+1$ 大元素上面恰有 $k$ 个元素，占一行 $n$ 个元素的 $k/n$；第 $mk/n+1$ 大元素上面恰有 $mk/n$ 个元素，占一列 $m$ 个元素的 $k/n$。方法因此叫 Quantile Balancing（QB）。推理阶段只用 $n$ 维的列偏置 $\beta$，行偏置 $\alpha$ 的规模等于全局批大小，也就是一次训练步里一起处理的全体样本数乘序列长度，属于求解过程的中间量。两个实用点：先用旧的 $\beta$ 选出当前批的专家、再更新 $\beta$，避免泄漏未来 token 的信息；实际使用从上一步的 $\beta$ 出发、每步只迭代一次，避免过拟合当前批次。第六篇也交代了谱系：用最优分配视角看负载均衡最早见于《BASE Layers: Simplifying Training of Large, Sparse Models》（arXiv:2103.16716），完整的一般解法由《Binary-Integer-Programming Based Algorithm for Expert Load Balancing in Mixture-of-Experts Models》（arXiv:2502.15451）给出，QB 相对它的改动是把不等式约束换成等式约束，去掉非负截断。作者实测这个截断拖慢均衡速度，并且常常只能把过载的专家压下去、救不回闲置的专家。这条路线的均衡效果用 MaxVio 度量，指的是各专家负载相对均匀目标的最大偏差。

**第七篇《MoE环游记：7、动态激活极简解》：一步分位数解，顺手修好因果。** 第七篇继续砍约束：把「每个 token 恰好激活 $k$ 个」丢掉，保留「每个专家恰好被激活 $mk/n$ 次」，也就是平均每个 token 激活 $k$ 个。去掉前一条约束后，对偶问题里只剩 $\beta$ 一个变量，每一列上 $\beta$ 的解析解就是该列打分的 $1-k/n$ 分位数，一步分位数直接给出最优解，激活规则也简化成 $s-\beta>0$，无需排序。一步最优解容易过拟合当前批，第七篇用 EMA（指数滑动平均）平滑历史解，更新式是 $\text{新值}=\text{系数}\times\text{旧值}+(1-\text{系数})\times\text{当前值}$，实验中系数取 0.9。它还给出一个漂亮的理解：这本质上是把 Expert Choice 写成 Token Choice。Expert Choice 指让专家去挑 token 的分配方式，Token Choice 指让 token 去挑专家。朴素的 Expert Choice 让每个专家挑 Top-$mk/n$ 个 token，需要沿序列维度比较全体 token；token 一个接一个组成序列，因果律指算某个位置的输出时看不到它之后的 token，训推一致性指同一个输入在训练与推理下算出同一个结果，沿整条序列比较会同时破坏这两条。Bias 形式把 $\beta$ 的更新放到激活决策之后，信息泄漏的入口被关上。初始化也有了闭式，也就是能一笔写出的显式表达式：在 Router 初始 logits 服从正态的假设下，$\beta=\sigma\cdot\Phi^{-1}(1-k/n)$，其中 $\sigma$ 是 logits 的标准差，$\Phi^{-1}$ 是标准正态分布的分位数函数。最后一节说明，如果完全不用分位数，对 $\beta$ 的可导目标做符号梯度下降也行，这条式子正是第四篇凭直觉给出的那一条。

**第八篇《MoE环游记：8、强制序列级均衡》：序列级均衡的 Loss-Free 对应物。** Loss-Free 引入的偏置在全局共享，已有的方案都只能做全局均衡；序列级均衡此前靠序列级 Aux Loss。全局均衡按整个训练批统计各专家被选中的次数，序列级均衡按单个序列内部统计，管的是同一条序列里各专家被用得是否均匀。第八篇要找序列级均衡的 Loss-Free 对应物。它先对照站外作者 Jonathan Chang 的《Causal Routing Bias for Aux-Loss-Free MoE Training》里的两条思路：对分数做滑动平均再用它决定激活，属经验做法；按测试时训练（在测试阶段也根据当前输入继续更新一部分参数）为每个 token 分配一个偏置并逐 token 更新，等价于一个非线性 RNN，序列一长成为瓶颈。RNN 沿序列逐步递推，后一步依赖前一步的状态，逐步更新因此无法并行。第八篇自己的路线叫 Moving Quantile Balancing（MQB）。它先把逐 token 偏置写成前缀上的分位数，也就是累积分位数，再用固定窗口内的滑动分位数替换，把复杂度从平方级降到线性。真正解开瓶颈的一步是把分位数的估计转成分布的估计：分数落在 $[0,1]$ 内，Sigmoid 的输出正好在这个区间，可以靠它保证；把 $[0,1]$ 等分成 $b$ 个桶做 one-hot，one-hot 指向量里恰有一个分量为 1、其余为 0；沿序列维度做这种向量的 EMA，由累积概率读出 $1-k/n$ 分位数作为该 token 的 $\beta$。EMA 只做线性运算，并且可以并行执行，序列级均衡由此第一次以 Loss-Free 的方式做到。EMA 本质上是 RNN，推理阶段要多存一个 $n\times b$ 的 State，作者认为 $b=100$ 已经够用。Top-k 版本的处理是：MQB 把 Router 的局部高峰削平后取 Top-k，再补一步全局 QB 恢复均衡；用 $\lambda$ 削弱序列均衡的强度，即把 $\beta$ 乘以 $\lambda$。实验用总参数量约 3B、128 选 4 的 MoE，滑动平均系数 0.99、分桶数 100，用 MaxVio 度量最不均衡的第一层：$\lambda$ 取 1 时均衡接近完美，代价是 Loss 差 0.06；$\lambda$ 调到 0.3 左右时 Loss 基本不掉，均衡仍在改善。第八篇把「是否需要序列级均衡、需要何种程度、为什么需要」留作开放问题。

**第九篇《MoE环游记：9、门控归一化之争》：Router 当 Gate 用时应当归一化。** 第九篇换到梯度一侧。$\rho$ 兼两个角色：选 Top-k 时充当 Router 打分，乘到专家上时充当 Gate，Gate 的作用是在训练时为 Router 提供梯度。这里的归一化指把 Router 打分做 Softmax 变成概率分布；Softmax 把任意一组打分变成非负、总和为一的概率分布。问题被写成三选一：先 Softmax 再选 Top-k、先选 Top-k 再 Softmax（即 Re-Norm）、不做归一化。已有的选择铺开了：DeepSeek 为配合 Loss-Free 把激活函数改成 Sigmoid 并用于 DeepSeek-V3，ReMoE 用 ReLU，第一篇的几何视角允许任意非负激活函数；Re-Norm 让前向数值更稳定，代价是 $k$ 至少大于 1。第九篇的推导从 $k=1$ 出发：被激活的专家应当是损失最小的那一个。先构造一个基于损失的目标分布 $q$ 与一个基于 $\rho$ 的预测分布 $p$，最小化两者的 KL 散度。KL 散度是衡量两个概率分布差异的量，分布越接近取值越小。展开后一项是负熵，熵刻画一个分布的分散程度，负熵越小分布越集中；负载均衡已经承担了鼓励模型多试不同专家的作用，另一项与参数无关，于是等效损失是 $p$ 对专家损失的加权和。它的梯度正是策略梯度里的 REINFORCE。策略梯度是用采样得到的回报为概率分布估梯度的思路，REINFORCE 是其中一种，做法是从 $p$ 里采一个专家来估计梯度，噪声偏大。对减 baseline 的 REINFORCE 做一阶泰勒展开，baseline 指一个与所选专家无关的基准值，减掉它不改变梯度的期望，同时把噪声压下去；一阶泰勒展开指在零点附近用一阶导数的线性项近似损失。这一步得到前向用 1、反向用 $\log p$ 的直通估计，前后向不一致。关键的改进是把每个专家从 $e_i$ 换成 $p_i\cdot e_i$，重复同一推导后停止梯度项自动消失，前后向恢复一致。结论是：如果需要一个自上而下的概率推导，Router 作为 Gate 时应当归一化，并且不应当 Re-Norm。边界也注明：$k=2$ 时概率框架给不出精确推导，可以把 $k>1$ 的 MoE 当作 Max Pooling 的类似物，Max Pooling 是局部窗口取最大值的下采样操作；也可以回到第一篇的几何视角。这条推导的出处是刘力源的三部曲《Bridging Discrete and Backpropagation: Straight-Through and Beyond》（arXiv:2304.08612）、《Sparse Backpropagation for MoE Training》（arXiv:2310.00811）与《GRIN: GRadient-INformed MoE》（arXiv:2409.12136），第九篇做了提炼与改写。

## 关键证据

**分位数解法在极端不均衡的层上的表现。** 第六篇对比第一层 MoE 的 MaxVio。第一层是负载最难均衡的一层，作者因此把演示集中在这一层。数字上，SignSGD 版的 Loss-Free 在五千步附近升到 1.7 上下，六千步上下到 2 左右，带大量尖峰升到 4，一万步后总体回落，约一万五千步回到 1 附近；QB 前段有一段从 0.2 附近爬升的过程，约五千步后稳定在 0.6 至 0.7，一万两千步与一万四千步附近两次到 0.74。作者据此说 QB 尤其擅长处理极端例子，用它训练一个全 MoE 模型时第一层也会变得均衡；对原本 SignSGD 就能均衡的层，QB 通常没有优势。

![[raw/2026-02/moe/spaces-ac-cn/moe-huanyouji-6/assets/moe-huanyouji-6-fig1.png]]

图：第一层 MoE 的 MaxVio 随训练步数变化，横轴到 1.5 万步，纵轴 0 到 4。图取自《MoE环游记：6、最优分配促均衡》。

**分桶近似分位数的精度。** 第八篇的这张图给出 MQB 的关键一步：直方图近似得到的密度与真实分布贴合，由累积概率读出目标概率 $1-k/n=0.7$ 对应的分位数阈值 $\beta$ 约为 0.36。图是原理示意，横轴为归一到 $[0,1]$ 的 Router 分数，0.7 是该示意取的一组目标概率，与实验配置无关；后文的实验配置是 128 选 4，对应的目标概率 $1-k/n\approx0.97$。

![[raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/assets/moe-huanyouji-8-fig1.png]]

图：上图为 Router 分数的局部分布与直方图密度近似，下图为对应的累积分布与阈值读取，标注出分位数阈值 $\beta$ 约为 0.36。图取自《MoE环游记：8、强制序列级均衡》。

**序列级均衡的强度与代价。** MQB 的实验配置是约 3B 参数的 MoE、128 选 4、滑动平均系数 0.99、分桶数 100。取 $\lambda$ 为 1 时，第一层的 MaxVio 全程稳定在 0.2 上下、峰值约 0.3；只做全局均衡的 QB 在训练后段落在 0.7 至 0.9；SignSGD 版 Loss-Free 约三千五百步起维持在 1.4 至 2.1。这一档的代价是 Loss 比不加序列级均衡时差 0.06。把 $\lambda$ 调到 0.3 后，第一层的 MaxVio 仍明显低于只做全局均衡的 QB，Loss 基本不掉。第八篇据此给出结论：完美的序列级均衡对效果损伤明显，$\lambda$ 取 0.3 左右能大致保证效果无损，并改善每一层的均衡。

![[raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/assets/moe-huanyouji-8-fig2.png]]

![[raw/2026-05/moe/spaces-ac-cn/moe-huanyouji-8/assets/moe-huanyouji-8-fig3.png]]

图：上图是 $\lambda$ 为 1 的 MQB、QB 与 SignSGD 三者的第一层 MaxVio 对比；下图是 $\lambda$ 取 0.3、$\lambda$ 取 1 与只做全局均衡的 QB 的第一层 MaxVio 对比。两图横轴到 1.6 万步。均取自《MoE环游记：8、强制序列级均衡》。

**比例因子的数值校验。** 第五篇的比例因子脚本对 DeepSeek-V2 配置给出约 16，对 DeepSeek-V3 配置给出约 2.83；DeepSeek-V2 官方 config.json 的 routed_scaling_factor 取 16.0，DeepSeek-V3 的取 2.5。前者精确吻合，后者相差约 12%。源文把两个配置的专家数按共享专家计入总数来调用脚本：DeepSeek-V2 记 $n=162$、$k=8$、$s=2$，DeepSeek-V3 记 $n=257$、$k=9$、$s=1$。

**超参数账。** Loss-Free 的学习率 $\gamma$ 取 0.001，这个默认值与 Router 用 Sigmoid 激活绑定，换激活函数需要重调。QB 与第七篇的一步解没有学习率要调。第七篇的 EMA 系数取 0.9，第八篇的滑动平均系数取 0.99、分桶数取 100。

**Fine-Grained 的组合数。** 总参数与激活参数不变的前提下，把每个专家缩小一半、改成 $2n$ 选 $2k$，可选组合数从 $\binom{n}{k}$ 增到 $\binom{2n}{2k}$。第五篇把它列为细颗粒度更优的一条形式化说明。

## 局限与缺口

- 第一篇的正交假设是近似，第五篇指出专家之间必然存在共性，正交假设在训练后期越难成立。
- 第二篇的 Aux Loss 权重难调，STE 给出的梯度是次优的，$F\cdot P$ 的意义落在等效梯度上。这些是第三篇转向 Loss-Free 的直接动因。
- 第三篇的 Loss-Free 仍有 $\gamma$ 要调，$\gamma$ 与激活函数绑定；偏置全局共享，方案只能做全局均衡。第六篇进一步指出恒定 $\gamma$ 在分布畸形的层上很难实现均衡，模型前几层用 MoE 时不均衡尤其常见。
- 第四篇的动态激活在初始化阶段会选满所有专家，可能造成大量 Token Drop；相关工作里 Top-p 难以准确控制平均预算，Ada-K Routing 引入强化学习，DA-MoE 依赖 Attention 分数。
- 第五篇的 Shared Expert 与 Fine-Grained Expert 都带来非均匀与额外的通信、协调成本；$\lambda$ 的取值由数值模拟给出，源文对 DeepSeek-V3 的模拟值与官方取值相差约 12%。
- 第六篇的 QB 需要跨全体 token 找分位数，$m$ 等于全局样本数乘序列长度，一般是百万量级，精确实现在各种并行策略与梯度累积下难以接受，实际用最大可接受的小批次折中。行偏置 $\alpha$ 依赖全局批大小，不能带进推理。
- 第七篇的一步最优解容易过拟合当前批次，EMA 是缓解手段，它不改变一步最优解的性质；$\beta$ 的初始化对训练前几步敏感。这一篇只给了演示代码，没有公开的训练对照。
- 第八篇的 $\lambda$ 取 1 时 Loss 差 0.06；是否需要序列级均衡、需要何种程度、为什么需要，源文都不给标准答案。分桶方式是 Sigmoid 激活后均匀离散化，更精细的分桶留作实验空间。EMA 是 RNN，推理多一个 $n\times b$ 的 State。这一篇的实验规模是约 3B 参数。
- 第九篇的概率框架在 $k=2$ 时给不出精确推导，它证明了归一化门控这条路的可行性；采样与 Top-k 的差异是多样性与稳定性的权衡，文中没有给出采样方案的实验。刘力源三部曲的形式化偏重，作者也提到操作上受约束。
- 全系列的实验规模偏小：除 DeepSeek 官方配置数字外，关键数字多来自作者自测的小模型（约 3B 一档），系列没有在大规模训练上复现 QB、MQB 的公开结果。
- 源文自述走的是自建推导路线，不做系统追根溯源，对 MoE 发展史的覆盖是选择性的。

## 我的分析

以下判断由我给出，源文没有这样组织。

九篇可以读成同一个对象的三次改写。第一次改写把「选哪些专家」从打分排序变成带约束的优化问题，落在第六篇；第二次改写把优化问题的解写成偏置的分位数，落在第七篇；第三次改写把偏置从全局推到局部、从全局约束推到序列约束，落在第八篇。前四篇在造偏置、调偏置，第五篇质疑均匀分布这个目标本身，第六至八篇在把偏置解到极致，第九篇换到梯度一侧收尾。

系列里最干净的一步是第七篇。第四篇凭「难处应当多投入」的直觉设计了 $s-\beta>0$ 这条激活规则，第七篇把它变成对偶解的推论，同时把 QB 从两步交替缩成一步分位数。第六篇的两步交替解推导较繁，第七篇的一步解更简；第八篇的正文交代过这个顺序，按作者写作的先后是先有第六篇再写第七篇，按概念难度讲的时候反了过来，从更简单的第七篇讲起，这一点值得留意。

DeepSeek 在这条线上的位置很清楚：Loss-Free、Shared Expert、Fine-Grained Expert、Sigmoid 门控都是 DeepSeek 提出的，系列的贡献是把它们接到一条几何与优化的主线上，并给出自己的解（QB、MQB）。第三篇对 Loss-Free 的判断，也就是「均衡与语言模型损失各管一部分参数」，是对方法本质的一次提炼。

可延伸的方向有六条。把 QB 的思路搬到其他稀疏选择结构上，因为它的核心只是「约束下的对偶变量等于分位数」，内容路由、检索、稀疏注意力都在射程内。把序列级均衡的 $\lambda$ 做成逐层自适应，源文只做了全局常数 $\lambda$，最不均衡的层恰好在前几层。把分桶方式换成按分位点建表查询或 logit 空间分桶，源文自己说这还留有实验空间。把 MQB 的 State（分桶后沿序列维护的那张分布表）与滑窗注意力的 KV cache（注意力层缓存下来的历史键与值，供后续位置复用）合并考虑，两者都在沿序列做增量状态。给第五篇的比例因子在更多配置上做核验，目前可核的官方数字是两组。把源文的公开代码或演示脚本在一档稍大的模型上跑通，验证 QB 与 MQB 的均衡收益能随规模保持。

一个可以追问的理论问题是：第九篇的概率框架与第六、七篇的最优分配框架是两套语言，前者为门控提供梯度，后者为路由提供偏置，两者在 $k=1$ 处能对上，也就是每行只选一个专家时，概率框架给出的归一化门控与最优分配框架给出的偏置阈值指向同一个选择；在 $k=2$ 处源文明确说概率框架给不出精确推导。把两套语言在 $k>1$ 处统一起来，是这份系列留下的一处空白。

## 关联

- [[moe-huanyouji-1-abstract|MoE环游记：1、从几何意义出发 摘要]]：系列起点，基线形式与正交假设的出处
- [[moe-huanyouji-2-abstract|MoE环游记：2、不患寡而患不均 摘要]]：Aux Loss 与 STE 配方的出处
- [[moe-huanyouji-3-abstract|MoE环游记：3、换个思路来分配 摘要]]：Loss-Free 的出处，本系列均衡路线的分水岭
- [[moe-huanyouji-4-abstract|MoE环游记：4、难处应当多投入 摘要]]：动态激活，Bias 冗余自由度的第一次使用
- [[moe-huanyouji-5-abstract|MoE环游记：5、均匀分布的反思 摘要]]：共享专家、细颗粒度与 DeepSeek 配置数字的出处
- [[moe-huanyouji-6-abstract|MoE环游记：6、最优分配促均衡 摘要]]：Quantile Balancing 的完整推导
- [[moe-huanyouji-7-abstract|MoE环游记：7、动态激活极简解 摘要]]：一步分位数解与 Expert Choice 的因果修复
- [[moe-huanyouji-8-abstract|MoE环游记：8、强制序列级均衡 摘要]]：序列级 Moving Quantile Balancing 及其均衡实验
- [[moe-huanyouji-9-abstract|MoE环游记：9、门控归一化之争 摘要]]：门控归一化的概率推导，系列的收尾
