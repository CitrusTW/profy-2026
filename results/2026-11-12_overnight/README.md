# 11月12日批次: 当前该看哪一份

本批包括三件事: 冻结skill的新题验证、ADV20重新评分与同模型对照、论文修订副本. 实验已经停止. 旧报告里的“等待平台恢复 / 等待上传”是当时状态, 现在看本页和仓库当前状态.

## 先看最终输出

| 要看什么 | 文件 | 怎么用 |
| --- | --- | --- |
| SkillsBench三组逐题结果 | [skills_final/REPORT.md](skills_final/REPORT.md)、[task_comparisons.csv](skills_final/task_comparisons.csv) | 3道完整held-out比较, 每组1次; 不能声称准确率或tokens普遍改善 |
| 所有尝试与未完成题 | [all_original_attempts.csv](skills_final/all_original_attempts.csv)、[task_statuses.csv](skills_final/task_statuses.csv) | 包含API/环境失败和runner_limit, 不是只列成功题 |
| ADV跨模型 | [adv_i004_analysis_v2/REPORT.md](adv_i004_analysis_v2/REPORT.md) | rubric用4096上限的完整60份, pairwise沿用I-003有效80份 |
| ADV同模型标签 | [i010/analysis/RESULT_REPORT_ZH.md](i010/analysis/RESULT_REPORT_ZH.md)、[I010_RESULTS.json](i010/analysis/I010_RESULTS.json) | 60份rubric与79份有效pairwise; 一份顺序缺失保留 |
| 最新论文 | [paper_rev/README.md](paper_rev/README.md) | 最新PDF、摘要、编译页数、数字出处 |
| 预先定下的规则 | [PREREG.md](PREREG.md)、[I-010预注册](i010/PREREG_I010.md) | 阅读时注意后续明确记录的修正 |
| 实际改过的决定 | [DECISIONS.md](DECISIONS.md) | 协议修正、平台停止和分析边界 |
| 按时间查进度 | [PROGRESS.md](PROGRESS.md)、[协作状态](../../docs/coordination/STATUS.md) | 旧时间点不能当成当前进度 |

## 原始证据与中间版本

| 目录 | 装的是什么 | 是否作为当前最终统计入口 |
| --- | --- | --- |
| skillsbench/ | 逐次求解、工具轨迹、交付文件、评分和失败记录 | 原始证据; 汇总看skills_final |
| skills/ | 本批冻结的xlsx第11轮SKILL.md | 实际版本证据 |
| adv_rejudge_i003/ | 第一批rubric与pairwise原始请求/返回/重试 | rubric不完整且被替代; pairwise仍用于I-004 |
| adv_rejudge_i004_rubric4096/ | 三条件统一4096预算后的rubric完整重评 | 当前跨模型rubric来源 |
| adv_i004_analysis_v2/ | 当前跨模型统计 | 是 |
| i010/ | 新基线生成、hash绑定、judge、分析和异常 | 当前同模型实验来源 |
| adv/ | 最初抽取的旧分数, 后来发现输出来源不能对应 | 只作审计, 不作平台Full证据 |
| adv_i004_analysis/ | 跨模型旧分析版 | 看v2, 等价证明在provenance |
| adv_i004_context_analysis/ | family / variant辅助分析 | 辅助结果, 不替换主表 |
| skills_draft1/ | 论文初稿时的统计 | 最终看skills_final |
| analysis_snapshots/ | 运行途中保存的统计快照 | 否, 不累加成更多独立实验 |
| portable_checkpoint_20261112T1120Z/、repro_skills_draft1/ | 中途离线重算与自检 | 只对对应时间点有效 |
| run_inventory_checkpoint_v2/ | 客户端工作与运行尝试清点 | 查工作量, 不当正确率 |
| profy_i004_probes/ | 平台可用性探测和403记录 | 不算完成的求解 |
| provenance/、instructions_received/ | 来源、规则、修正、收到的指令 | 查来路与决定 |
| scripts/ | 本批自写运行、统计和论文修改代码 | 不读代码也能先看报告 |
| paper_figures/ | 数据生成的论文图和来源 | 配合论文使用 |
| paper_validation/ | 编译、数字核对、上传记录和摘要文本 | 查最终交付是否对应 |
| paper_rev/ | 各版PDF与改动清单 | 最新版见专门README |

部分旧JSON字段写“complete_with_infrastructure_gap”或旧报告写“I010 incomplete”, 不等于完整三组有效评分或完全没有结果: 应同时读有效数、缺失原因和最终用户决定. 本批SkillsBench最终口径以 `I007_frozen_cohort` 与 skills_final表为准; 同模型I010保留79/80的缺失, 后续按用户I-011写入论文.

这里没有重新生成Full, 没有再进化xlsx. 平台专家的实际上下文与服务端版本未知. [全仓库实验总览](../../docs/EXPERIMENTS.md).
