# 实验总览: 做过什么, 哪些能用于论文

读法: 先看这一页的批次表, 再点具体报告. 每份旧报告描述的是当时状态; 最终使用版本单独标出. “检查通过数”是同一道题内部的 verifier 检查数, 不是题目数量.

## 1. 论文现在使用的结果

| 实验 | 回答什么问题 | 实际记录与边界 | 先看哪里 |
| --- | --- | --- | --- |
| ADV 跨模型对照 I-004 | 平台专家输出和原来两组基线相比怎样? | 20题; Full 是平台输出, 基线用不同模型. 只能说明这个配置对比, 不能分离模型作用 | [最终跨模型统计](../results/2026-11-12_overnight/adv_i004_analysis_v2/REPORT.md) |
| ADV 同模型标签对照 I-010 | 两组基线也用 Full 的模型标签后, 优势还在吗? | 40份新基线输出, Full不重新生成; 60份 rubric 有效, 79/80份 pairwise顺序有效. overall优势未保留 | [中文结果](../results/2026-11-12_overnight/i010/analysis/RESULT_REPORT_ZH.md)、[原始汇总](../results/2026-11-12_overnight/i010/analysis/I010_RESULTS.json) |
| SkillsBench 冻结版新题 | 在不继续调skill的题上, 原版和进化版做得怎样? | 3道完整可比较 held-out 题, 每组各1次, 正确率持平; tokens因题而异. xlsx用第11轮, economic-dispatch用第6轮 | [最终SkillsBench报告](../results/2026-11-12_overnight/skills_final/REPORT.md) |
| 早期 threejs 门控反例 | 通过候选门控是否保证执行变好? | 第一个早期候选用gpt-4.1进化, threejs-structure-parser检查由3/3降为1/3; 与后来的第5轮版本分开 | [历史候选](../skills/evolution-history/historical-run-01/)、[最终论文数字来源](../results/2026-11-12_overnight/paper_rev/final/NUMERIC_SOURCES_I011.json) |
| customs 案例 | 结构化文件提取的重复运行怎样? | 论文保留收到的52题案例. 不是本repo这轮新增的配对三组实验, 不能把它当SkillsBench分数 | [论文来源说明](../results/2026-11-12_overnight/paper_rev/final/CHANGELOG_I011.md) |

### SkillsBench 的新题、开发题要分开

- 新题比较: energy-market-pricing / economic-dispatch第6轮; protein-expression-analysis / xlsx第11轮且在第12轮之前的那次; powerlifting-coef-calc / xlsx第11轮.
- 开发或选版: threejs-to-obj、threejs-structure-parser、3d-scan-calc、weighted-gdp-calc. protein-expression-analysis 后来参与选版, 后来的记录不能继续算独立新题.
- shock-analysis-demand 有 runner_limit, 单列两种口径; 不能拿它中止的 tokens 与完成运行比较.
- supply 和其余未完成题也要看, 不只列成功记录. [全部尝试](../results/2026-11-12_overnight/skills_final/all_original_attempts.csv) / [最终任务状态](../results/2026-11-12_overnight/skills_final/task_statuses.csv).

## 2. 开发、选版与环境排错

| 批次或目录 | 实际用途 | 记录入口 |
| --- | --- | --- |
| threejs 第1至5轮 | 调整外部适配、原版输出兼容, 最后在参与过开发的两题上验证 | [迭代过程](../results/run-04-up-to30/PROGRESS.md)、[两题结果](../results/run-04-up-to30/full-compatible-two/REPORT.md) |
| economic-dispatch 第6轮 | 先开发, 再冻结到 energy-market-pricing | [任务与运行结果](../results/2026-11-11_skillsbench_full_library/network-family/REPORT.md) |
| mesh-analysis 第7至9轮 | 开发题3d-scan-calc; 第8轮传输失败没有候选 | [云端批次](../results/2026-11-11_skillsbench_cloud_serial/README.md)、[第9轮三组](../results/2026-11-11_skillsbench_cloud_serial/mesh-evolution/frozen-three-arm/REPORT.md) |
| xlsx 第10至11轮 | weighted-gdp-calc 开发与确认, 第11轮冻结 | [开发结果](../results/xlsx-family/README.md)、[冻结记录](../results/xlsx-family/FROZEN.json) |
| xlsx 第12至13轮 | 后续native-owned候选/选版尝试, 不用于本次第11轮冻结评测 | [当时计划与记录](../results/xlsx-family/native-owned-evolution-v2/PROGRESS.md)、[候选正文](../skills/evolution-history/xlsx/) |
| Linux / Docker / 评分接通 | 环境可行性、原verifier接通、失败排查; 不算题目效果 | [环境检查](../results/2026-11-11_skillsbench_cloud_serial/environment-checks/README.md)、[运行时状态](../results/cloud-runtime/STATUS.md) |

## 3. 审计和已被替代的记录

| 记录 | 为什么保留 | 为什么不能当最新结论 |
| --- | --- | --- |
| [85题完整性审计](../results/2026-11-12_85task_input_output_audit/REPORT.md) | 检查输入/输出缺失和来源 | 是审计, 不产生新得分 |
| [ADV旧分数抽取](../results/2026-11-12_overnight/adv/AUDIT_ONLY_I003.md) | 暴露旧分数与后来的平台输出不能对应 | 不能拿来证明真实Full效果 |
| [I-003第一批judge](../results/2026-11-12_overnight/adv_rejudge_i003/COVERAGE_AND_FAILURES.json) | 保留截断、重试与每次原始返回 | rubric不完整, 被统一4096预算的I-004取代; 这批pairwise仍被使用 |
| [I-004旧分析目录](../results/2026-11-12_overnight/adv_i004_analysis/) | 保留分析历史 | 当前入口为v2; [等价检查](../results/2026-11-12_overnight/provenance/ADV_ANALYSIS_V2_EQUIVALENCE.json) |
| [中途统计快照](../results/2026-11-12_overnight/analysis_snapshots/) | 保存当时进展, 不能删除失败记录 | 不是最终分母; 当前SkillsBench看skills_final |
| [PersonaMem与早期三组原型](../experiments/three_arm_pilot_20261110/README.md) | 保留自写prompt等原型及问题诊断 | 不作为原论文方法实现或效果证据 |
| [第11轮前的8题状态](../results/xlsx-family/heldout/BATCH_REPORT.md) | 原来的部分运行仍被复用 | 它描述夜间补跑前的状态, 现在看最终报告 |

## 4. 一个结论怎么查到证据

1. 从最新报告找到对应实验和 task_id.
2. 用该目录的 results.json / I010_RESULTS.json 查统计, 用 CSV 查逐题值.
3. 查原始请求、返回、score receipt、verifier输出和输出hash. 失败调用也保留.
4. 如果涉及进化, 查冻结的 SKILL.md、parent/candidate hash、Evolution记录和开发题使用情况.
5. 论文里的数字再对 [数字来源清单](../results/2026-11-12_overnight/paper_rev/final/NUMERIC_SOURCES_I011.json). 本次摘要替换不改变实验数字.

[I-004原始rubric](../results/2026-11-12_overnight/adv_rejudge_i004_rubric4096/) / [I-003原始pairwise](../results/2026-11-12_overnight/adv_rejudge_i003/) / [I-010调用、输出、hash与统计](../results/2026-11-12_overnight/i010/) / [SkillsBench运行目录](../results/2026-11-12_overnight/skillsbench/).

按单个文件查找可用 [FILE_INVENTORY.csv](records/FILE_INVENTORY.csv). 其中 git_blob 是Git对象标识, 不是文件SHA256; 输出SHA256仍以各实验原记录为准.
