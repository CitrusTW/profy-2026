# 先小跑, 有信号再扩大

日期: 2026-11-10, America/Los_Angeles.

**当前状态: 方案候选已写清楚, 原方法接线仍未完成, 还不能启动付费小跑. 本轮模型调用0次.** 10项离线函数检查不是效果实验. 下面的任务、规模和继续条件是建议, 不是已经完成的工作.

## 这次到底想回答什么

给同一个模型一本操作说明, 让它先做一道公开任务. 再用论文已有的Evolution流程, 根据这次实际操作改这本说明. 最后用另外的公开任务检查: 改后的说明有没有让模型做得更准, 或在做对的前提下少花tokens.

这里的操作说明是expert skill. 研究对象是收到的02-员工服务助手中的xlsx/SKILL.md, 不是重新编一个故意很差的skill. 选它是因为公开表格任务有真实附件和程序验收, 收到的xlsx skill也有现成操作内容. 这只测试skill refinement, 不证明员工服务身份、跨expert归因、Memory或长期creator fidelity.

**这条实验若接通并出现改善, 可以补“skill更新有没有实际收益”的一个小案例. 它不能补上整篇论文的所有缺口, 也不是完整SkillsBench结果.** 当前还不能承诺11/13前完成: 主要未知数是原生链路何时可用, 不是18次任务需要多少时间.

## 先补哪几个接线问题, 才能开始花钱

| 检查 | 需要看到什么 | 目前是什么情况 |
| --- | --- | --- |
| 正确的原版本 | 提交稿§3.4所述capability-gap分类, 以及Appendix F所述候选、比较和promotion的对应文件/版本 | 收到的Evolution核心齐全; 对应分类实现没找到; 收到的Core采纳路径直接覆盖skill, 与稿中版本有差异 |
| 目标skill确实注册 | 原生skill discover/activate能找到expert/xlsx, 激活正文hash与收到的原skill一致 | ZIP中的文件已获得; 尚未验证平台expert/*注册. 把ZIP上传sandbox不能自动证明这一步 |
| 原生Evolution可以触发 | 一个当前能用的原runner、原job或已授权creator运行入口, 能把实际轨迹送进原Evolution模式 | 官方机制说明和收到源码的入口是内部调用. 已知SEA-Eval桥接脚本在原实验者外部目录, 当前包没有 |
| 三组不会串版本 | 三份独立测试expert, 或实际可用的不可变skill版本; 能确认原skill、候选skill和活动版本 | 同一个expert id的三个sandbox只隔离文件/会话, 不能推定它们隔离数据库skill内容 |
| baseline没有同类skill | no-target-xlsx组的库发现、自动注入和工具轨迹能确认没有同名或等价xlsx skill; 其他通用工具三组相同 | 公开API说明builtin工具持续存在, expert技能也可能自动注入. 不能只用environment.skills=[]宣称no-skills |
| 原任务能验收 | 正确依赖、真实指定路径的输出文件、原verifier可以运行; 失败/skip不会被隐藏 | 输入、题面、verifier已在SkillsBench副本; 新文件型Profy接线尚未做 |

没有第一至第五项, 就不启动“原方法效果”实验. 这不是要求拿内部secret或开发新接口, 是要求用已有且可授权的链路和对应代码版本. 也不把普通agents/run里选择evolution扩展, 当成内部独占模式已经启动的证明.

理论上可以在平台外忠实移植原算法, 再用Profy求解任务. 但这仍要补工具接线、状态保存和对应版本缺失, 并明确标为外部复现; 当前离线函数fixture不是这个实现. 本轮不临时改写一套更新算法来绕过缺口.

## 公开原题怎么分工

统一来源: [benchflow-ai/skillsbench](https://github.com/benchflow-ai/skillsbench), 本地副本commit为f860ecf02ef53412a030f8661c83d644b739ff01. 不改题面、参考答案或验收规则. 表里列的是本次候选子集, 不是让skill读取的学习答案.

| 阶段 | 原task id | 模型获得的原附件 | 要交什么 | 为什么用它 / 回答什么 |
| --- | --- | --- | --- | --- |
| 开发, 唯一学习任务 | xlsx-recover-data | nasa_budget_incomplete.xlsx | nasa_budget_recovered.xlsx | 补回跨工作表缺失数据. 从实际工具操作里找可复用步骤; 只准用这一阶段的轨迹学习 |
| 小跑验证 | financial-modeling-qa | data.xlsx, background.pdf | answer.txt | 结合表格和背景材料得出数值答案. 看改后的skill离开开发题以后, 是否还有收益 |
| 冻结后的测试1 | sales-pivot-analysis | population.pdf, income.xlsx | demographic_analysis.xlsx | 按原题合并人口/收入信息并制作实际Excel pivot tables. 看新skill能否用于另一类表格操作 |
| 冻结后的测试2 | exceltable-in-ppt | input.pptx | results.pptx | 更新PPT里的嵌入Excel表格, 保持其他内容符合原验收. 看收益会不会只限于普通xlsx文件 |

附件只按上表白名单上传. 特别是xlsx-recover-data/environment目录含groundtruth/answers.txt和生成程序, **不能整目录上传**. oracle、verifier、参考输出和隐藏答案都不进入求解、轨迹学习或skill正文. 本地评分程序可以读取它们, 但不会把答案回传给更新模型.

以上任务名称、输入完整性和评分结构已检查, 还没有对候选skill跑过结果. 两道冻结测试题的分数不能用于继续改skill. 这组任务是否足够难、是否出现天花板, 需要小跑回答, 不预先保证.

## 三组到底差什么

| 组 | 使用的目标xlsx skill | 用来比较什么 |
| --- | --- | --- |
| no-target-xlsx | 没有目标xlsx skill或等价替代品; 保留三组相同的PDF/PPT支持和基础工具 | 这类任务是否真的需要目标skill. 其他支持仍存在, 所以不笼统叫绝对no-skills |
| original-skill | 收到的原xlsx skill, 内容冻结 | 原skill的起点 |
| native-evolved-skill | 用原Evolution流程得到并通过原门控/评估的一个冻结版本 | 只改目标skill有没有新增收益 |

三组固定同一模型与实际可用的同一版本、参数、任务指令、文件、资源、依赖和预算. 拟沿用之前可调用的gpt-6.1-sol标签, 正式记录平台返回的实际标识; 不宣称平台标签等于底层权重版本. 每次运行新建会话与sandbox, 不带上一题输出和Memory. 如果平台自动注入无法控制, 先解决控制问题, 不把污染组记成baseline.

## 怎么跑, 每步留下什么

| 步骤 | 做什么 | 产出 / 继续条件 |
| --- | --- | --- |
| 0. 接通并确认 | 完成上面的原版本、注册、触发、隔离、baseline和验收检查 | 原版本索引、实际发现/激活记录、调用入口和原verifier环境. 没接通就停在这里 |
| 1. 用原skill做开发题 | 跑xlsx-recover-data一次, 保存实际工具参数/结果、用量、原生输出和原verifier结果 | 一条真实轨迹. 环境或任务指令问题先修接线, 不把它当expert能力不足. 如果原策略判定没有可更新的gap, 不强制生成候选 |
| 2. 原Evolution提建议 | 原EVOLUTION.md、原builtin/evolution workflow、原expert工具作用域和原10维rubric/ratchet原样使用; 输入步骤1轨迹和原run_stats | 至多一条原生pending建议. 保存父skill hash、候选hash、9项模型估计、代码计算的context_footprint、双门控结果和suggestion id. 允许没有建议 |
| 3. 比较并冻结 | 原skill和候选在同一开发题、相同条件下得到实际reward, 走对应版本的权限/目标/版本检查, 比较后再promotion | 分开的before/after评估记录、promotion回执和活动版本. 门控估计分不能冒充真实任务分; 当前缺对应版本时不能跳过这一步后宣称完整链路 |
| 4. 小跑三组 | financial-modeling-qa每组一次. 取回平台实际输出, 用原verifier评分 | 三组实际分、tokens、耗时、工具次数、成功/失败/skip. 先判断实现是否正确, 再判断有没有收益 |
| 5. 有信号再扩大 | 冻结S0/S1, 两道测试题各跑三组, 每组3次独立尝试, 共18次求解. 运行顺序交错 | 原评分结果表、逐次原生输出、方法/任务版本和实际用量. 全部有效尝试都报告, 不挑最高分 |
| 6. 判断论文能补什么 | 只按冻结测试结果判断质量和效率, 把Evolution本身消耗单独列出 | 一张小案例表和一段结论. 有收益就报告收益; 无收益就如实记录, 不改原85题准确率/评分数字 |

新代码只允许做传输、原记录接线、原函数调用和结果汇总. 不另写候选生成prompt、评分rubric或benchmark. 不额外加human evaluation、LLM judge或新的公开数据集.

## “效果好/不好”怎么决定

- **先看跑得对不对.** 原库版本不对、baseline夹带skill、候选没激活、缺依赖、输出取错、原评分异常, 都是实现问题. 修好后重试对应开发/小跑步骤, 不据此评价方法.
- **再看小跑信号.** native-evolved-skill比original-skill原评分更高, 或原评分不降且实际求解tokens至少减少15%, 才扩大到18次测试. 15%只是在单次噪声下避免为很小变化大批付费的筛选线, 不是原ratchet的一部分, 也不是显著性证据. tokens缺失时不以工具数假充tokens.
- **不好时有限调整.** 最多再做一次原生候选更新, 只用开发轨迹; 再跑候选的开发评估和小跑验证. 不改原rubric、不删难题、不降低验收、不根据最终测试答案改skill. 两轮仍无信号就结束, 保留负结果.
- **不能只保留好看的结果.** 即使扩大的结果变差, 也保留全部运行与本次先筛选再测试的流程. 两个测试任务上的重复运行只能描述这两个任务的波动, 不能当18个不同任务推断整个benchmark.

最初一轮约6个逻辑调用: 原skill开发1次、Evolution1次、候选开发1次、小跑三组3次. 如果再调整一次候选, 额外约3个逻辑调用: Evolution、候选开发、候选小跑各1次. 再扩大18次, 合计最多约27个逻辑调用. 单次逻辑调用可包含多轮模型请求; 不把27次说成27个模型request或固定费用. 无新候选、异常中止或未通过原promotion时不会用满.

## 在哪里执行, 需要什么资源

求解在Profy hosted环境执行; 本机只做调度、取回文件和程序评分, 不在本机部署大模型, 不新增GPU平台. key从既有私密配置读取, 不进入仓库/Drive/日志. OpenRouter key不用于代替原Evolution写skill, 也不增加一个付费judge.

原verifier在有相应依赖的隔离评分环境运行. 固定Python及文件处理库版本, 按各任务Dockerfile/test.sh确认依赖; 在正式调用前确认不能跳过关键测试. 平台环境与官方BenchFlow环境的差异要记录, 结果写成“原SkillsBench任务在固定Profy执行环境上的案例”, 不冒充官方harness排行榜.

每个attempt保存task commit、输入hash、组别、expert/skill版本、会话id、平台实际输出及hash、原verifier命令与返回码、逐项评分、tokens/cache字段、工具次数、求解耗时和Evolution消耗. Profy账单金额没返回就写unknown, 不拿OpenRouter价格估算成真实Profy费用. 学习开销和后续求解开销分开, 如计算回本次数也标明是按观测值推算.

## 现在只需补的具体材料

收到的Profy-main、6个expert包和公开SkillsBench附件不需要再提供. 需要的是: **与提交稿对应的capability-gap分类/候选比较/promotion代码版本, 以及一个已授权、当前能运行原生Evolution的测试expert入口或现成runner/job.** 还需确认能给三份互不串skill版本的测试expert或等价版本隔离, 以及原skill的expert/*注册记录. 如果这些只能在creator页面操作, 提供该入口和现成操作步骤即可; 不需要内部secret.

在这些缺口解决前, 状态保持“原方法接线未完成”, 不能标记小跑完成或方法无效. 证据和逐项核对见[METHOD_CODE_API_MAP.md](METHOD_CODE_API_MAP.md).
