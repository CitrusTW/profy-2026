# 实验结果入口

[先看实验总览](../docs/EXPERIMENTS.md). 这里按用途找目录, 不把中途快照当最终结果.

## 当前论文使用的批次

| 内容 | 最新入口 | 注意 |
| --- | --- | --- |
| ADV20跨模型 | [I-004最终统计](2026-11-12_overnight/adv_i004_analysis_v2/REPORT.md) | Full与基线生成模型不同 |
| ADV20同模型标签 | [I-010中文结果](2026-11-12_overnight/i010/analysis/RESULT_REPORT_ZH.md) | 不支持overall优势; 一处pairwise顺序缺失 |
| SkillsBench held-out | [最终报告](2026-11-12_overnight/skills_final/REPORT.md) | 3道完整可比较题, 每题每组1次; 未完成题也保留 |
| 论文和数字出处 | [版本说明](2026-11-12_overnight/paper_rev/README.md) | SixLessons为最新PDF |

## 所有历史批次

| 原目录 | 里面是什么 | 先看哪里 |
| --- | --- | --- |
| 2026-11-12_overnight | 夜间补跑、ADV重评、同模型对照、最终统计、论文副本 | [目录说明](2026-11-12_overnight/README.md) |
| 2026-11-12_85task_input_output_audit | 三组255份记录的完整性审计 | [REPORT.md](2026-11-12_85task_input_output_audit/REPORT.md) |
| xlsx-family | weighted-gdp开发、10至13轮相关记录、先前protein和8题批次 | [开发结果](xlsx-family/README.md)、[旧8题批次](xlsx-family/heldout/BATCH_REPORT.md) |
| 2026-11-11_skillsbench_full_library | economic-dispatch与energy-market-pricing, 不是全库成绩 | [network-family报告](2026-11-11_skillsbench_full_library/network-family/REPORT.md) |
| 2026-11-11_skillsbench_cloud_serial | mesh开发、云端环境和原评分接通 | [README.md](2026-11-11_skillsbench_cloud_serial/README.md) |
| run-04-up-to30 | threejs后续轮次和两题冻结版 | [PROGRESS.md](run-04-up-to30/PROGRESS.md)、[两题报告](run-04-up-to30/full-compatible-two/REPORT.md) |
| run-03-iterative | threejs早期迭代 | [原目录](run-03-iterative/) |
| run-02-gpt61 | 早期gpt-6.1-sol候选尝试 | [原目录](run-02-gpt61/) |
| cloud-runtime | 云端环境准备与故障记录, 不是答题结果 | [STATUS.md](cloud-runtime/STATUS.md) |

无评分、触发runner_limit、API拒绝和环境检查都不能写成“完成一道实验题”. 原目录和原分数不改. [文件清单](../docs/records/FILE_INVENTORY.csv)列出所有已归档路径.
