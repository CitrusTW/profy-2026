# 当前状态

更新日期: 2026-11-12. 本页替代旧入口中的“审计后暂停 / 继续进化 / 等待上传”状态; 原说明保存在 [整理前快照](../archive/navigation-before-2026-11-12/).

## 已完成

| 工作 | 当前结果 | 证据 |
| --- | --- | --- |
| ADV 跨模型对照 I-004 | 20题; overall: Raw 2.43 / Expert Prompt 2.63 / Full 3.22. Full−Expert Prompt 0.59, 95% CI [0.30, 0.87] | [最终统计](../results/2026-11-12_overnight/adv_i004_analysis_v2/REPORT.md) |
| ADV 同模型标签对照 I-010 | 20题; overall: Raw 3.31 / Expert Prompt 3.42 / Full 3.23. 差值 -0.19, 95% CI [-0.55, 0.16]. 没有保留 overall 优势 | [结果与异常说明](../results/2026-11-12_overnight/i010/analysis/RESULT_REPORT_ZH.md) |
| SkillsBench held-out | energy-market-pricing、protein-expression-analysis 的第12轮前记录、powerlifting-coef-calc, 每题每组各1次; 三组正确率持平, tokens 因题而异 | [最终记录](../results/2026-11-12_overnight/skills_final/REPORT.md) |
| 85题输入/输出审计 | 255份保存记录按相同标准检查; 原请求或 finish_reason 缺失处是无法核实, 不是正常通过 | [审计报告](../results/2026-11-12_85task_input_output_audit/REPORT.md) |
| 论文修订副本 | 最新 SixLessons PDF, 正文6页 / 总27页; Overleaf修订副本已更新, 原项目和 OpenReview 未修改 | [版本与数字出处](../results/2026-11-12_overnight/paper_rev/README.md) |

## 尚未完成或不能据此证明

- SkillsBench 全库没有跑完. 8道 xlsx 计划题里只有 powerlifting-coef-calc 新增了完整三组有效评分; 不能把中止或平台失败算成完成.
- shock-analysis-demand 的原版组碰到 runner_limit, 没有评分; 同时保留“按失败计”和“整题排除”两种统计, 中止前 tokens 不用于效率比较.
- shock-analysis-supply 只有 no-skills 有评分; reserves-at-risk-calc、xlsx-recover-data、invoice-fraud-detection、pdf-excel-diff、jpg-ocr-stat 未完成. 各次尝试仍保留.
- 同模型 I-010 的 pairwise 有79/80有效顺序, ADV_002 的一个顺序因截断缺失; 不能写成80/80完整.
- Profy Full 的实际上下文注入和服务端模型版本没有记录. 同模型实验只匹配模型标签, 不等于完全控制平台差异.
- 当前 SkillsBench 是收到的 Evolution workflow / gate 的外部适配, 不是完整原生实现. capability-gap classifier、通用适用性检查、native promotion 尚未接通.

## 是否还在跑

全部模型运行和 Profy 探测已停止. 后续没有新进化轮次. 本次仅整理 Git 里的文档和索引, 不改结果、论文或评分, 不产生 API 费用.

最新执行状态见 [coordination/STATUS.md](coordination/STATUS.md); 按实验找记录见 [EXPERIMENTS.md](EXPERIMENTS.md).
