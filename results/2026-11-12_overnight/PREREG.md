# 当前有效预注册: I-001 + I-002

完整旧版与用户第一次修正保留在provenance. 本文件在I-001/I-002接管后冻结, 不根据新题成绩改变规则.

- 仅8道xlsx held-out题, 顺序: shock-analysis-demand, shock-analysis-supply, reserves-at-risk-calc, powerlifting-coef-calc, xlsx-recover-data, invoice-fraud-detection, pdf-excel-diff, jpg-ocr-stat. 不另外选题.
- xlsx冻结第11轮, SHA256 51ca8a2ff044812e60ca830e9951d17219a66c736004edc99729d157f275cf1a. 所有其他原skill资源原样保留, 不进化不修改skill/门控/流程.
- 全串行、广度优先, 每题依次no-skills/original/frozen各一次, 8题完成后才补第二遍, 再有时间补第三遍. 最多3次/组/题. shock-demand沿用已有A/B, 本夜只补一次冻结组; 不重跑旧基线.
- 24模型轮/48工具调用/1600秒solver上限, 三组完全相同, 不因结果变更. 沿用Profy原生native-owned文件adapter与原verifier, 不是官方Docker. 模型label gpt-6.1-sol; 这次xlsx候选历史进化也是gpt-6.1-sol, 本夜无新OpenRouter/Evolution调用.
- runner_limit无原评分, 不把中止tokens与完成运行相比. 同时(a)在分析中计失败0,(b)整题排除配对比较. infra_fail单列unknown, 不自动当答错, 同一组至少2次基础设施失败则整题标invalid, 全部记录保留. 不依据某组结果跳题.
- 每题每组逐次列strict reward、passed/failed/skipped、同源solver total_tokens、工具次数、耗时、费用unknown. 有至少2次完成运行才报告tokens样本SD和min/max; 单次波动unknown. 任务有runner_limit或infra缺口时不作该题完整tokens比较.
- held-out汇总纳入之前economic-dispatch第6轮的energy-market-pricing、xlsx第11轮的protein第一次测试(第12轮前), 以及这8题, 共固定10个题目位置. 版本按skill分开. protein后来的选版记录另表, 不覆盖它第一次测试的身份.
- 质量措辞须存在提升且无任何下降, 并在两种runner-limit口径下都成立. tokens措辞须多数固定held-out题(超过10题位置的一半)同时有下降和已估计波动, 并超出原版自身波动; 操作定义同时报告: 绝对均值差>原版样本SD、冻结均值是否低于原版观测min(或高于max), 最终降低消耗措辞要求下降同时满足这两项. 单次题不能计明显下降. 不满足就写效果因任务而异. 这是预先写明的保守操作化, 非显著性检验.
- 至少5道可比较题才对tokens百分比变化按题bootstrap10000次, seed20261112, percentile95%CI. 不把重复次数当独立题. 质量差、tokens差、失败和missing的分母完整给出. 不声称泛化或稳定有效.
- ADV仅从既有两份评分文件抽取20题, 不再生成/评分, overall沿用5个通用维度. 已发现无回答hash绑定与时间字段对应问题, 如实披露, 不把档案评分冒称当前平台回答的已验证成绩.
- 历史首threejs候选通过门控而验证从3/3降为1/3必须保留; 该历史Evolution模型为gpt-4.1, 与xlsx11/gpt-6.1-sol分清. 缺classifier、通用semantic applicability、native promotion如实写明.
- I-002: 2026-11-12 08:00 PST写INTERIM_REPORT; 13:30 PST后不启动新run, 开始论文副本; 15:30 PST前全部报告与PDF推实验分支. 不动原论文、不上传Overleaf/OpenReview. 不充值, 额度耗尽停止.
- 每完成一个run和每30分钟读取coordination新指令、推docs/coordination状态; 只写实验分支, coordination分支只读. 状态/进度管理文件按协议更新, 原数据结果不可覆盖.
