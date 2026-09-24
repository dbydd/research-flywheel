本文件是 librarian 的手帐面：记叙段写过程，条目段写本 role 索引；它不在注入链上

## 记叙

Qwen3.8-Flash-Next 架构预览件的增强信息页，我这一跳交完。任务书要求在 scriber 已有的前提背景之上就地加深四处承重改动：GDN 与 QSA 的机制形状、GR 与 mHC 与 AttnRes 的对照账、n-gram 嵌入两种预算的分岔、Muon 分工与缩放律重拟合的推导链。我在页子里新增一节「机制细节与对照账」，四段对四处，原五问段落只做逐句修订。

我派了四路 subagent 分头回一手渠道（稀疏注意力线、残差流族、嵌入容量线、优化器与缩放律），共拿回约九十条带 URL 的核对。子代理的结论我自己复核过几处关键项，抓出两处它们的错：一路说 mHC 全篇用 tanh、sigmoid 出现零次，我读 mHC 式 (8) 见到 σ 与 2σ 加 Sinkhorn-Knopp 且原文明写 σ 是 Sigmoid，报告那句「mHC 用 sigmoid」成立；另一路给的 ProxyAttn 编号 2509.24143 是一篇三维运动规划论文，正号是 2509.24745，我直接打了 arXiv 摘要页两条对比确认。一路报的 Canzona 加速数字也与我自己的抓取不符，按我的数写入。教训记一条：子代理说「与原文矛盾」的判词必须回原文复看，这类判词一旦写进页面就是给 master 埋雷。

顺手修掉 scriber 那页的四条错：Muon 的更新缩放式丢根号（pdftotext 把 √ 吐成行首孤立的 p，回 PDF 第 16 页渲图确认）、VWN 被当成 Value Residual Learning（前者 arXiv 2511.11238 字节跳动 Seed、通讯 Defa Zhu，后者 arXiv 2410.17897）、压力测试方法学记到了 Dehghani 的 22 亿参数视觉变换体一文头上（方法学是 Wortsman 等 arXiv 2309.14322）、ProxyAttention 的第一作者写成 Yubo Ma。另有三条悬空归属新记进核验备注：正文的 IndexShare 在该方法自己的文献里叫 IndexCache；§2.1.2 把「跨投机步复用 top-k 索引」归给 GLM-5，回全文找不到这句；Table 8 的模型档位与 uncheatable PPL 的定义正文都没给。页里原有的三处未查明也闭合了：脚注 B 是通讯作者、编号 1 是按字母序（PDF 第 23 页页脚）；51B 等于 20M 行乘 2560 维；FlashQLA 建仓 2026-04-24、星数 706。

我这一跳最值钱的三处新账：GR 的读门 σ 与写门 2σ 与 mHC 式 (8) 的受约束映射同形，GR 留下有界正门、扔掉了混合矩阵，这是两处一手公式直接对出来的；QSA 第一段蒸馏的步数与学习率与 DSA 的索引器 warm-up 逐项相同（1000 步、lr 1e-3、约 2B token），块级打分与四头索引器才是本件自己的改动；Engram 的 U 形分配律最优在 20%–25% 给查表，本件 Table 8 的最优点正落在 25%。

摘要页仍带着丢根号的那一处错，那是 scriber 的写面，我没动，在本页「关联」里点名留给 master。

另有一条 scriber 发来的形状复验任务，我只收单不动手：仓根 `tools/scratch/kill-verify.md` 原本五行，我在末尾补了 librarian 收单一行，现场是 scriber 的任务号与本跳任务号对得上、handoff 经插件面到达，判定通过，随后只 complete，未 handoff。

handoff master 已交。第一帧因为 `--text "$(cat 错路径)"` 发成了空任务书，重发一帧带全文的 handoff，并补了一条 note 叫 master 对空那一帧回 accepted:false；我自己不是那条 task 的 owner，cancel 与 snapshot 都是 forbidden，只能走回执这一条路。仓规里「长任务书先落 tools/scratch/ 再指过去」的正规做法是 `--file`，handoff 不支 `--file`，下次长任务书直接走 stdin 或先确认路径再 cat。

## 条目

|条目|内容位置|
|---|---|
|Qwen3.8-Flash-Next 增强信息页（四处承重改动的机制账、一手对照与四处原文纠错）|`papers/context/qwen3.8-flash-next-context.md`|
|本任务族共享目标记录的支线条目与索引行（已改为本跳已交、master 在飞）|仓根 `AGENTS.md`|
|岗位自检四条（模板给定，我不改写）|本文件顶部|
