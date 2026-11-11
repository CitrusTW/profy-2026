# gpt-6.1-sol付费小跑

2026-11-10, America/Los_Angeles. 本次已获准付费, 不修改论文或OpenReview.

1. 复用run-01/dev_original的真实gpt-6.1-sol开发记录, 不再花钱重跑同一个开发基线.
2. 进化通过用户已明确允许的OpenRouter入口使用openai/gpt-6.1-sol. Profy plain chat工具请求返回502, 没有换成其他模型. 进化模型只看到threejs-to-obj的原题、原skills和实际开发历史, 通过收到的原Evolution workflow、skill工具和evolution_log生成候选. 验证题的题面、答案、verifier和失败分析不进入进化请求.
3. 新候选先做开发题检查. 查实际读取hash、真实输出、原评分和候选来源, 不只相信自评分. 没通过就不扩大.
4. 冻结候选后, 在threejs-structure-parser上各跑一次no-skills、with-skills、with-CogniLife-skills. 三组使用同一模型、预算和原题, 独立session. 这道题曾经被分析过, 所以标为diagnostic repeat, 不是新的独立held-out证据. 冻结后不把验证结果送回进化.
5. 保存每组原评分、耗时、tokens、工具数、输出hash和错误. 没有账单就不编美元费用. 原始输出留在工作区, private repo保存本助手写的代码、计划、结果报告和可核对的数字/hash, 不收第三方source、skill全文或keys.

最多4次新求解(候选开发1+三组3), Evolution最多8次实际生成请求. 接口诊断单列, 不把失败请求冒称成功生成. 不自动重发可能已经执行的请求.

当前只能复用skill-refinement核心的外部适配. 尚未找到的原capability-gap classifier和语义适用性检查, 以及未接入的native acceptance / promotion, 都继续明示. 如补写代码, 标为本实验新增适配或检查, 不冒称原作者实现, 不通过新学习prompt代替原流程.

状态: 本轮已完成, 结果为negative. 原版3/3, 新skill1/3; 不改论文, 不扩大. 详见[PAID_RESULTS.md](PAID_RESULTS.md).
