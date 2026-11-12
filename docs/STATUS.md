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

## 正在做什么

冻结第11轮, 串行测试其余8道父版 xlsx SKILL.md 和资源匹配的原题. 使用原题、原附件和原评分, 全程不重新出题或改验收. [自动串行入口](../experiments/skillsbench_cloud_runner_20261111/run_frozen_xlsx.py).

## 还没完成什么

- SkillsBench 全库87题还没跑完. 一份 xlsx skill 不能用于所有不相关任务.
- 当前是 Profy 原生 Linux 文件任务 adapter, 不是官方 Ubuntu Docker image. 环境、软件版本、输入和 source hashes 随题留档. [早期云端环境检查](../results/2026-11-11_skillsbench_cloud_serial/environment-checks/README.md)不计入题目成绩.
- 尚未完整复现 CogniLife 平台. 收到的实现缺少或未接通 capability-gap classifier、通用 semantic applicability check 和 native acceptance/promotion. 本实验只测已明确记录边界的外部适配.

已有原版、采用的进化版、候选历史和每轮来路均保留. 第8轮 OpenRouter SSL 失败未收到候选, 也计入最多30轮. 当前已使用到第11轮. 继续使用已有 API, 不充值或购买服务, 全部串行, 本机不留镜像或大缓存. 论文、Overleaf、OpenReview 未改.

[全部结果](../results/README.md) | [三组 skills](../skills/README.md) | [每轮进化](../skills/evolution-history/README.md)
