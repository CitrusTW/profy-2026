# 当前做到哪里

| 已完成三组的题 | 版本 | 看结果 |
| --- | --- | --- |
| Threejs 两题 | 第5轮 | [报告](../results/run-04-up-to30/full-compatible-two/REPORT.md) |
| energy-market-pricing | 第6轮 | [报告](../results/2026-11-11_skillsbench_full_library/network-family/REPORT.md) |
| 3d-scan-calc, 开发题 | 第9轮 | [报告](../results/2026-11-11_skillsbench_cloud_serial/mesh-evolution/frozen-three-arm/REPORT.md) |
| weighted-gdp-calc, 开发题 | 第11轮 | [报告](../results/xlsx-family/README.md) |
| protein-expression-analysis, 未参与进化 | 冻结第11轮 | [报告和实际 Excel](../results/xlsx-family/heldout/protein-expression-analysis/REPORT.md) |

共6道题完成三组, 其中开发题用于改 skill 和选版, 不能一起算成独立泛化结果. 另有 grid-dispatch-operator 开发记录.

## 最新数字意味着什么

weighted-gdp-calc 三组都27/27. no-skills 用155489 solver tokens, 原版248816. 第10轮291458, 未采用. 第11轮两次109337 / 133351, 比原版少56.06% / 46.41%, 已冻结.

但第一道未参与进化的 protein-expression-analysis, 三组虽都6/6, 第11轮却用264808 tokens, 原版187869, no-skills183191. 进化版比原版多40.95%, 这道题没有显示质量或效率提升. 不把开发题的收益写成普遍收益, 不用这道题答案回改 skill.

## 正在继续进化 xlsx

从第12轮继续, 最多到第30轮. 只把 weighted-gdp-calc 开发轨迹交给原 Evolution 组件; 纠正旧 PRoot 环境描述. 用 protein-expression-analysis 做候选选版检查, 不把它的答案、轨迹、评分源码或分数交给 Evolution. 后续这题不再算独立新题证据. 开发和验证都要保持原评分全过, 并两次比原版至少少5% solver tokens, 才采用. [完整计划](../results/xlsx-family/native-owned-evolution-v2/PLAN.md).

现有第11版和先前不理想的结果均保留. 当前先取得同一 native-owned 环境的开发题原版与第11版记录. 论文未改.

## 上轮8题批次已停止

这8题中0题完成三组, 1题部分完成, 7题未开始. shock-analysis-demand 的 no-skills 原 reward0, 使用839001 solver tokens. 原版 skill 组在25次 usage记录超过runner的24轮限制后中止, 已使用1168850 tokens, 没有有效评分. 进化版尚未运行. 不是仍在后台运行, 不把未完成的组算为0分.

原 no-skills 评分回执的计数与 pytest stdout 不一致, 两种计数和原始 reward均保留并标注. [本批完整进度、实际数字与停止证据](../results/xlsx-family/heldout/BATCH_REPORT.md).

本次只复查已有记录并上传证据, 没有付费重跑、修改 skill 或修改论文. 原串行入口仍保留, 未改为自动跳过中止记录.

## 还没完成什么

- SkillsBench 全库87题还没跑完. 一份 xlsx skill 不能用于所有不相关任务.
- 当前是 Profy 原生 Linux 文件任务 adapter, 不是官方 Ubuntu Docker image. 环境、软件版本、输入和 source hashes 随题留档. [早期云端环境检查](../results/2026-11-11_skillsbench_cloud_serial/environment-checks/README.md)不计入题目成绩.
- 尚未完整复现 CogniLife 平台. 收到的实现缺少或未接通 capability-gap classifier、通用 semantic applicability check 和 native acceptance/promotion. 本实验只测已明确记录边界的外部适配.

已有原版、采用的进化版、候选历史和每轮来路均保留. 第8轮 OpenRouter SSL 失败未收到候选, 也计入最多30轮. 当前已使用到第11轮. 继续使用已有 API, 不充值或购买服务, 全部串行, 本机不留镜像或大缓存. 论文、Overleaf、OpenReview 未改.

[全部结果](../results/README.md) | [三组 skills](../skills/README.md) | [每轮进化](../skills/evolution-history/README.md)
