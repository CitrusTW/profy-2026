# 8道 xlsx 原题: 实际进度与已完成数字

## 先看结论

这8道题没有新增完成三组的题. 批次已经停止, 不是仍在后台运行. 第1题 shock-analysis-demand 的 no-skills 已完成原评分; 原版 skill 组超过 runner 的24轮模型调用限制后被中止. 串行程序随后退出, 进化版和后面7题没有开始. 不把未运行或未完成的组算成0分.

这次只查已有记录和归档, 没有付费重跑, 没有改 skill、原题、评分规则或论文.

## 已完成的三组比较: 此前那道 protein-expression-analysis

它不属于这次剩余8题, 单独列出, 防止把旧结果当作本批新增结果.

| 组别 | 原评分 | Solver total_tokens | 准备环境加解题, 秒 |
| --- | --- | ---: | ---: |
| no-skills | 6/6, reward1.0 | 183191 | 282.754 |
| with-skills, 原版 xlsx | 6/6, reward1.0 | 187869 | 309.261 |
| with-CogniLife-skills, 冻结第11轮 | 6/6, reward1.0 | 264808 | 336.866 |

进化版与原版相比, 正确率没有提高, tokens 多40.95%, 这次记录的耗时多8.93%. 目前没有在这道未参与进化的题上看到提升. 一次运行不能证明所有任务都这样, 但不能把开发题上的收益说成新题上的收益.

tokens 是 API 返回的用量, 不是美元费用. 耗时包含环境准备和解题, 不包含评分、附件上传或回传. A组曾补取被截断的环境记录; B/C 使用同一修复后格式. 具体边界、实际 Excel、逐步运行记录和原评分见[该题完整报告](protein-expression-analysis/REPORT.md).

## 这8道题的实际进度

| 原题 task ID | no-skills | with-skills | with-CogniLife-skills |
| --- | --- | --- | --- |
| shock-analysis-demand | 已评分, reward0; 839001 tokens, 760.071秒 | 中止, 未评分; 1168850 tokens, 836.448秒 | 未开始 |
| shock-analysis-supply | 未开始 | 未开始 | 未开始 |
| reserves-at-risk-calc | 未开始 | 未开始 | 未开始 |
| powerlifting-coef-calc | 未开始 | 未开始 | 未开始 |
| xlsx-recover-data | 未开始 | 未开始 | 未开始 |
| invoice-fraud-detection | 未开始 | 未开始 | 未开始 |
| pdf-excel-diff | 未开始 | 未开始 | 未开始 |
| jpg-ocr-stat | 未开始 | 未开始 | 未开始 |

shock-analysis-demand 的原版组确实读到了原版 xlsx SKILL.md; 25次 usage 记录超过自定的24轮限制. 这不是 Profy 返回的600秒上限, 也不是有效评分为0. 该组的1168850 tokens 是中止前已经发生的用量, 不能当成完成解题的用量比较.

## 评分记录中必须保留的差异

shock-analysis-demand 的 no-skills 原回执写 tests5 / passed3 / failed2, 但原 pytest stdout 的最终摘要写5 passed / 2 failed, 即7个实际执行结果. 两处计数不一致. 原 reward.txt 对应的 reward0不变; 不把任一计数改写成无争议的准确率, 不改原评分.

原始 score_receipt.json 照存. ORIGINAL_SCORE_AUDIT.json 另外保存两种计数、完整 stdout 的 SHA256 和摘要. 上传的 original_verifier_summary.log 只保留原日志的最终结果段; 不复制日志中展开的第三方测试源码或参考答案. 完整 stdout 保留在原本的本地证据目录, 没有用于 skill 进化.

## 证据在哪里

- [本批状态](BATCH_STATUS.json): 0题完成三组、1题部分完成、7题未开始.
- shock-analysis-demand/no-skills/: 实际交回的 test_demand.xlsx、result.json、原回执、评分摘要与审计.
- shock-analysis-demand/with-skills/: 中止前的 run_summary.json、usage.json、完整求解事件记录的压缩版. 没有评分文件, 因为没有运行评分.
- 每组 events.jsonl.gz 是原求解记录的压缩副本; 解压后可查看, 不含之后的 hidden verifier 执行记录.
- [runner预算中止条件](../../../experiments/skillsbench_evolution_20261110/run.py)及[串行入口](../../../experiments/skillsbench_cloud_runner_20261111/run_frozen_xlsx.py)已经在同一分支归档.

目前没有新增论文结果, 没有改论文、Overleaf 或 OpenReview.
