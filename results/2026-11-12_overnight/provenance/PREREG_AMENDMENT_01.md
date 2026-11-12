# 优先级更高的修正, 2026-11-12收到后、launch-03付费运行前冻结

原PREREG保留作历史. 冲突部分全部按本修正, 不属于看完新结果后的选题调整.

1. 只跑既定8道xlsx题, 顺序与BATCH_REPORT一致. 唯一候选为xlsx第11轮, hash不变. 不选第二批, 不进化. 全串行.
2. 广度优先: 第一轮依次每题 no-skills -> original -> frozen 各一次, 8题处理完有时间才同顺序补第二次. 不要求3次. shock-analysis-demand 的旧no-skills reward0及原版中止原样保留; 本夜只补一次frozen, 不重跑其基线或补第二次.
3. 模型24轮/48工具上限不改. 触发上限runner_limit, 无评分, strict reward原始值unknown. 同时输出(a)分析时计失败0,(b)该题任何组触发上限则整题配对比较排除. 上限中止tokens只列消耗, 不与完整运行比较效率. 非上限基础设施失败单列unknown, 达到原约定至少2次/组则整题无效. 不自动把基础设施错误算错题.
4. 汇总本轮8题和此前energy-market-pricing(economic-dispatch第6轮)、protein-expression-analysis(xlsx第11轮,第12轮之前首次测试). 保留它们在当时确为未用于该冻结版开发的状态. 同时明确protein后来参与第12轮以后选版, 不称这次新跑/完全未观察过. 所有开发/选版测量另列. shock-demand已部分查看过, 仍按本次明确要求纳入held-out任务集合, 另外标记previously attempted, 不称首次未见.
5. 各组各题实际次数如实报告, 样本SD仅n>=2可计算, n=1记unknown. 不把旧单次当3次. 无重复波动估计的任务不能支撑超出波动的token收益表述. bootstrap以可完成且无runner-limit的题为单位, >=5题才做10000次, seed不变; 两种口径均保留.
6. 复用收到的Evolution workflow和门控的外部适配, 不是完整平台/官方Docker. 这次xlsx候选的进化和求解均gpt-6.1-sol, OpenRouter负责历史进化, Profy负责求解; 本夜OpenRouter新调用0. capability-gap classifier、通用语义适用性检查、native promotion没接通. 第一份threejs反例历史进化为gpt-4.1, 必须另外标明, 不伪称也是gpt-6.1-sol.
7. 额度/余额耗尽立即停止所有新请求, 保留记录, 不充值不买服务. 一般上传网络失败不据此换题或把0分塞进去. 已发生的修正前重复基线被中止, 单独存档, 不混进结果.
8. 09:25:03 UTC起6.5小时停止新请求、7小时完成交付, 计时不重启. 所有新目录和append-only日志, 原论文不动.
