# I010 结果: 同模型 ADV20 对照

结论: 使用相同声明模型的基线后, Full 相对 Expert Prompt 的平均差值变为负数, 置信区间包含 0, 没有满足运行前规定的优势保留条件。不能据此声称排除了模型差异这个解释, 也不能断言模型差异是唯一原因。论文未写入这轮结果。

| 对比 | Raw | Expert Prompt | Full | Full − Expert Prompt | Bootstrap95% CI |
|---|---:|---:|---:|---:|---|
| I004: Moonshot基线 | 2.43 | 2.63 | 3.22 | 0.59 | [0.30, 0.87] |
| I010: DeepSeek基线 | 3.31 | 3.42 | 3.23 | -0.19 | [-0.55, 0.16] |

Full 答案未重新生成; I010 对三组统一重新打分, 因而 Full 的平均评分与 I004 略有不同。

| I010 pairwise | 两次Full赢 | 两次基线赢 | 正反不一致 | 缺一个顺序 |
|---|---:|---:|---:|---:|
| Full vs Expert Prompt | 9 | 7 | 3 | 1 |
| Full vs Raw | 8 | 10 | 2 | 0 |

| I010 rubric逐题差值 | 均值 | 95% CI | Full更高 / 更低 / 打平 |
|---|---:|---|---|
| Full − Expert Prompt | -0.19 | [-0.55, 0.16] | 6 / 11 / 3 |
| Full − Raw | -0.08 | [-0.34, 0.18] | 9 / 10 / 1 |

## 异常和边界

- 40/40基线已保存; 60/60rubric有效; 79/80pairwise顺序有效。所有目标均已尝试, 不是全部评分都成功。
- ADV_002 的 Full vs Expert Prompt、Full在A位, 3次均因1024-token评分输出上限截断而失败; 保留缺失, 未补分。
- ADV_004 Raw生成触及原4096-token上限, 非空; 按协议保留, 未重生成。其他基线无空答案。
- 基线使用 deepseek/deepseek-v4-flash, 目录canonical revision为20260423; 历史平台Full只记录deepseek-v4-flash标签, 具体服务版本/provider未知。因此是声明模型匹配, 不是对全部服务细节的控制。
- 原脚本的两个ADV模板相差一句不确定性提醒。运行前固定使用run_full_pipeline.py完整模板, 原样保留; 历史已保存基线没有原始请求, 无法核实当年使用的是哪份模板。
- Judge始终为anthropic/claude-opus-5.5; prompt、解析和预算按预注册执行。没有根据分数更改设置。

费用: OpenRouter实际回执合计 USD 4.0799450879, unknown费用调用 0。共 182次调用, 运行耗时 38.56分钟。未充值、未购买服务、未调用Profy。

## 文件

- analysis/I010_RESULTS.json: 全部统计、子集、维度、费用和缺失计数。
- analysis/results.json: 与I004相同统计代码的基础输出。
- analysis/condition_means.csv、paired_differences.csv、pairwise_by_task.csv: 逐条件和逐题结果。
- INTEGRITY_AUDIT.json: 原脚本参数、prompt、输出hash和原文件未变检查。
- PREREG_I010.md、BUDGET_AND_INPUT_PLAN.json: 运行前冻结的规则。
- ALL_CALLS.jsonl、VALID_JUDGMENTS.jsonl、GENERATED_OUTPUTS.jsonl、calls/: 所有原始请求、返回、失败及生成答案。
- analyze_i010_v3.py、analyze_adv_i010_core.py、audit_i010.py: 可重复运行的统计和核对脚本。

最新用户要求优先: 先报告结果, 不写进论文。既有draft2及原论文未改。
