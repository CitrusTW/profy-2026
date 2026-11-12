# CogniLife / Profy 实验仓库

这里保存自写实验代码、三组 skills、进化过程、运行结果和论文修订副本. **main 是总入口; 实际实验文件在实验分支.** 点下面的链接即可查看, 不需要先学会切换Git分支.

## 先点哪里

| 想做什么 | 直接打开 |
| --- | --- |
| 看所有实验做了什么、能说明什么 | [实验总览](https://github.com/CitrusTW/profy-2026/blob/codex/three-arm-skill-pilot-20261110/docs/EXPERIMENTS.md) |
| 看现在做完了什么、还有什么没完成 | [当前状态](https://github.com/CitrusTW/profy-2026/blob/codex/three-arm-skill-pilot-20261110/docs/STATUS.md) |
| 看最新论文和完整摘要 | [论文版本说明](https://github.com/CitrusTW/profy-2026/blob/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/paper_rev/README.md) |
| 查每一道题的实际数字和证据 | [实验结果入口](https://github.com/CitrusTW/profy-2026/blob/codex/three-arm-skill-pilot-20261110/results/README.md) |
| 看三组实际使用的skill和每轮进化 | [skills说明](https://github.com/CitrusTW/profy-2026/blob/codex/three-arm-skill-pilot-20261110/skills/README.md) / [全部进化版本](https://github.com/CitrusTW/profy-2026/blob/codex/three-arm-skill-pilot-20261110/skills/evolution-history/README.md) |
| 按文件名找原始记录 | [文件清单CSV](https://github.com/CitrusTW/profy-2026/blob/codex/three-arm-skill-pilot-20261110/docs/records/FILE_INVENTORY.csv) |

## 每个branch是干什么的

branch可以理解成同一仓库里不同用途的工作区. 下面是2026-11-12核对的全部远端分支.

| 分支 | 用途 | 里面有什么 | 怎么使用 |
| --- | --- | --- | --- |
| [main](https://github.com/CitrusTW/profy-2026/tree/main) | 仓库首页 | 当前这份README, 解释去哪看 | 第一次打开repo从这里开始; 实验文件没有复制到main |
| [codex/three-arm-skill-pilot-20261110](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110) | 实验和结果的工作分支 | 自写代码、三组skills、每轮候选、原始记录、统计、失败证据、论文PDF | 日常查实验就用它; 名字虽是pilot, 后续ADV和论文修订也在这里 |
| [coordination](https://github.com/CitrusTW/profy-2026/tree/coordination) | 审核与执行之间传递规则和指令 | PROTOCOL.md、INSTRUCTIONS.md、STATUS_TEMPLATE.md | 查当时要求做什么; 这里不是结果目录, 执行状态写在实验分支的docs/coordination/ |

本次只整理main的README. 实验分支原有路径和证据不搬动; coordination分支不改.

## 实验分支: 每个主要文件夹放什么

以下路径都在 `codex/three-arm-skill-pilot-20261110`, 不是main下的文件夹.

| 文件夹 | 大白话说明 | 入口 |
| --- | --- | --- |
| docs/ | 给人读的状态、实验总览、文件清单和协作记录 | [打开](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/docs) |
| experiments/ | 自写的运行、方法适配、评分调用和分析代码 | [代码说明](https://github.com/CitrusTW/profy-2026/blob/codex/three-arm-skill-pilot-20261110/experiments/README.md) |
| skills/ | no-skills、原版、进化版三组配置和各轮SKILL.md | [skills说明](https://github.com/CitrusTW/profy-2026/blob/codex/three-arm-skill-pilot-20261110/skills/README.md) |
| results/ | 实际运行留下的回答、轨迹、评分、统计与失败记录 | [结果说明](https://github.com/CitrusTW/profy-2026/blob/codex/three-arm-skill-pilot-20261110/results/README.md) |
| archive/ | 历史入口和整理前的说明快照, 方便查当时怎么写的 | [打开](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/archive) |

### docs: 查进度与记录来路

| 路径 | 是什么 |
| --- | --- |
| [docs/EXPERIMENTS.md](https://github.com/CitrusTW/profy-2026/blob/codex/three-arm-skill-pilot-20261110/docs/EXPERIMENTS.md) | 每批实验的目的、边界和证据入口 |
| [docs/STATUS.md](https://github.com/CitrusTW/profy-2026/blob/codex/three-arm-skill-pilot-20261110/docs/STATUS.md) | 现在的完成情况, 不用从旧日志猜 |
| [docs/coordination/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/docs/coordination) | STATUS.md是最新执行状态; STATUS_LOG.md保留过去的状态更新 |
| [docs/records/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/docs/records) | 全文件清单、这次整理改了什么、链接检查结果 |

### experiments: 找程序

| 文件夹 | 是什么 |
| --- | --- |
| [native_method_feasibility_20261110/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/experiments/native_method_feasibility_20261110) | 把论文方法、收到的实现和API能力逐项对照; 说明缺了什么 |
| [skillsbench_evolution_20261110/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/experiments/skillsbench_evolution_20261110) | Evolution外部适配、早期三组执行和候选核验代码 |
| [skillsbench_cloud_runner_20261111/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/experiments/skillsbench_cloud_runner_20261111) | Profy原生Linux文件任务adapter和原verifier接通代码 |
| [paper_judge_audit/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/experiments/paper_judge_audit) | 85题生成输入/输出完整性审计, 不产生新分数 |
| [three_arm_pilot_20261110/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/experiments/three_arm_pilot_20261110) | 更早的三组原型; 里面archive/personamem是PersonaMem尝试, 不作为原论文方法效果证据 |

ADV和夜间统计的自写脚本跟对应数据放在 [results/2026-11-12_overnight/scripts/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/scripts) 和 [i010/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/i010), 不是所有代码都在experiments下.

### skills: 找实际版本, 不只看“最新版”三个字

| 文件夹 | 是什么 |
| --- | --- |
| [no-skills/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/skills/no-skills) | 不提供benchmark skill的条件说明; 不是漏传SKILL.md |
| [with-skills/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/skills/with-skills) | 公开benchmark原版SKILL.md和固定来源记录 |
| [with-CogniLife-skills/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/skills/with-CogniLife-skills) | 采用过的进化版, 按skill分别保存 |
| [evolution-history/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/skills/evolution-history) | 采用和没采用的候选、来源、parent/candidate hash、修改diff |
| [evolution-history/xlsx/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/skills/evolution-history/xlsx) | xlsx第10至13轮相关候选; 本批新题固定用第11轮, 不用后来的候选替换 |

版本按skill区分: threejs第5轮、economic-dispatch第6轮、mesh-analysis第9轮、xlsx新题第11轮. 历史版本不等于都用于最终新题结果; 每一批实际用了什么, 以该批冻结记录为准.

### results: 每批实验放什么

| 文件夹 | 是什么 | 使用时注意 |
| --- | --- | --- |
| [2026-11-12_overnight/](https://github.com/CitrusTW/profy-2026/blob/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/README.md) | 最新ADV对照、冻结skill新题、最终统计和论文副本 | 下面单独解释内部目录 |
| [2026-11-12_85task_input_output_audit/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_85task_input_output_audit) | 85题×3条件的输入/输出审计 | 审计不是新实验得分 |
| [xlsx-family/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/xlsx-family) | weighted-gdp-calc开发、xlsx候选、protein旧记录和原8题批次 | 开发题、后来用于选版的题不能都算独立新题 |
| [2026-11-11_skillsbench_full_library/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-11_skillsbench_full_library) | economic-dispatch开发与energy-market-pricing冻结评测 | full_library只是旧目录名, 不代表全库跑完 |
| [2026-11-11_skillsbench_cloud_serial/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-11_skillsbench_cloud_serial) | mesh-analysis开发、云端环境和原评分接通 | 环境检查不算题目成绩 |
| [run-04-up-to30/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/run-04-up-to30) | threejs后续迭代与两题比较 | 两道题参与过开发/选版 |
| [run-03-iterative/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/run-03-iterative) | threejs早期迭代记录 | 历史尝试 |
| [run-02-gpt61/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/run-02-gpt61) | 早期gpt-6.1-sol运行记录 | 历史尝试 |
| [cloud-runtime/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/cloud-runtime) | 云端执行环境准备和故障记录 | 不是答题结果 |

### 11月12日批次: 最终结果与中间文件分开读

以下路径都以 `results/2026-11-12_overnight/` 开头.

| 文件夹 | 是什么 | 该不该当最新结论 |
| --- | --- | --- |
| [skills_final/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/skills_final) | 最终SkillsBench逐题结果、所有尝试和两种runner_limit口径 | 新题统计看这里 |
| [adv_i004_analysis_v2/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/adv_i004_analysis_v2) | ADV20跨模型最终统计 | 看这里, 同时说明生成模型不同 |
| [i010/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/i010) | ADV20同模型标签对照, 包括新基线、调用、hash和analysis | 同模型结果看这里; Full未重新生成 |
| [adv_rejudge_i003/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/adv_rejudge_i003) | 第一批judge原始调用与失败 | rubric被后续完整批次替代; pairwise仍用于I-004 |
| [adv_rejudge_i004_rubric4096/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/adv_rejudge_i004_rubric4096) | 三组统一4096输出预算的rubric重评 | I-004最终rubric来源 |
| [skillsbench/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/skillsbench) | 实际求解轨迹、交付文件、verifier输出和失败尝试 | 原始证据, 不只看成功记录 |
| [skills/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/skills) | 这批实际冻结的xlsx第11轮正文 | 版本证据 |
| [paper_rev/](https://github.com/CitrusTW/profy-2026/blob/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/paper_rev/README.md) | draft1、draft2和各次final PDF及改动清单 | 最新是SixLessons PDF, 旧final仍保留 |
| [paper_validation/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/paper_validation) | 编译页数、数字核对、摘要文本和上传验证 | 查交付是否对应 |
| [paper_figures/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/paper_figures) | 论文图与数据来源 | 配合论文使用 |
| [scripts/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/scripts) | 本批自写执行和分析代码 | 先看报告, 再查实现 |
| [provenance/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/provenance)、[instructions_received/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/instructions_received) | 来源、规则、收到的指令和修正 | 查来路和为什么改变 |
| [adv/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/adv) | 最初抽取的旧ADV分数 | 只作审计, 不能当平台Full结果 |
| [adv_i004_analysis/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/adv_i004_analysis) | 跨模型旧分析版 | 当前看v2 |
| [adv_i004_context_analysis/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/adv_i004_context_analysis) | family/variant辅助分析 | 不是主表的替代版本 |
| [skills_draft1/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/skills_draft1)、[analysis_snapshots/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/analysis_snapshots) | 初稿和运行途中的统计快照 | 不是最终分母, 不累加为更多实验 |
| [portable_checkpoint_20261112T1120Z/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/portable_checkpoint_20261112T1120Z)、[repro_skills_draft1/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/repro_skills_draft1) | 对应时间点的离线重算与自检 | 只对那一版有效 |
| [run_inventory_checkpoint_v2/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/run_inventory_checkpoint_v2) | 客户端工作与尝试清点 | 不当正确率 |
| [profy_i004_probes/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/results/2026-11-12_overnight/profy_i004_probes) | 平台可用性和403记录 | 不算完成的求解 |

更深一层的重复目录按下面读, 不用把每个task_id当成新的实验设计:

- `round-XX/`: 某一轮候选及它的开发/确认记录; `development/`用来调整, `confirmation/`用于确认.
- `frozen-evaluation/`或`frozen-three-arm/`: 冻结版本后的指定题比较; 是否held-out仍要看该题之前有没有参与开发.
- `runs/<task_id>/repeat-<n>/<condition>/`: 这道题、这一次、这一组的执行证据. `condition`就是no-skills / with-skills / with-CogniLife-skills.
- `calls/`: 每次模型或judge的原始请求、返回与重试; 不等于每个调用都是有效结果.
- `cloud-grade/`: 已保存回答对应的评分回执和来源; `analysis/`是从记录计算出的统计.
- 带时间戳的目录: 当时保存的快照, 不是独立重复实验.

### archive: 保留历史解释

[archive/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/archive)保留早期尝试入口与整理前的说明. [navigation-before-2026-11-12/](https://github.com/CitrusTW/profy-2026/tree/codex/three-arm-skill-pilot-20261110/archive/navigation-before-2026-11-12)是这次整理前的README和状态快照. 里面的相对链接和“运行中”描述保留当时写法, 日常查当前状态用上面的新入口.

## coordination分支里的文件

| 文件 | 是什么 |
| --- | --- |
| [README.md](https://github.com/CitrusTW/profy-2026/blob/coordination/README.md) | 协作入口 |
| [coordination/PROTOCOL.md](https://github.com/CitrusTW/profy-2026/blob/coordination/coordination/PROTOCOL.md) | 多久读一次指令、如何写状态、数据保护规则 |
| [coordination/INSTRUCTIONS.md](https://github.com/CitrusTW/profy-2026/blob/coordination/coordination/INSTRUCTIONS.md) | 按编号追加的任务与审核意见; 同编号的聊天指令需结合日期和内容区分 |
| [coordination/STATUS_TEMPLATE.md](https://github.com/CitrusTW/profy-2026/blob/coordination/coordination/STATUS_TEMPLATE.md) | 写执行状态时的模板 |

看“要求做什么”去coordination; 看“实际做了什么”去实验分支的 [STATUS.md](https://github.com/CitrusTW/profy-2026/blob/codex/three-arm-skill-pilot-20261110/docs/coordination/STATUS.md) 和对应结果.

## 读结果时记住

开发题收益不是新题效果; 没评分不是得0分; runner_limit的失败口径是分析规则, 不是真实verifier回执; tokens不等于费用. 当前SkillsBench是外部适配, 不是完整原生CogniLife复现. 收到的公司源码、key和隐藏评分材料不放进本仓库.

全部模型运行已停止. 本次只整理README, 没有新运行、重算分数或修改论文.
