# 当前做到哪里

## 已完成

| 实验 | 采用版本 | 结果入口 |
| --- | --- | --- |
| threejs 两题三组 | 第5轮 | [报告](../results/run-04-up-to30/full-compatible-two/REPORT.md) |
| energy-market-pricing 三组 | 第6轮 economic-dispatch | [报告](../results/2026-11-11_skillsbench_full_library/network-family/REPORT.md) |
| 3d-scan-calc 三组 | 第9轮 mesh-analysis | [报告](../results/2026-11-11_skillsbench_cloud_serial/mesh-evolution/frozen-three-arm/REPORT.md) |

共4道题完成三组对照. 另外有 grid-dispatch-operator 开发题记录, 不混算为新的独立评测结果.

三组配置、原版 SKILL.md、采用的进化版和10份实际历史候选已归档. 第8轮发生 OpenRouter SSL 传输错误, 未收到候选, 单独保留故障记录并计入30轮上限.

## 第9轮实际结果

3d-scan-calc 三组都通过原评分的2项检查. no-skills 用127350 tokens, 原版161063, 第9轮开发和确认分别125369 / 127654. 进化版比原版少约22.16% / 20.74%, 与 no-skills 基本持平. 这道题用于开发和选择候选, 不能拿它证明独立泛化.

第7轮仅少约0.18%, 没采用. 第9轮两次达到预先记录的至少5%降幅门槛后已冻结. 这个门槛是外部实验的选版规则, 不是原论文方法的一部分, 不修改原评分.

## 还没完成

- SkillsBench 默认全库87题尚未完成.
- 已跑通3D题的独立云端原评分; 全库各题的云端环境和评分链路还未全部验证.
- 尚未完整复现 CogniLife 平台. 收到的代码仍缺少或未接通 capability-gap classifier、通用语义适用性检查和 native promotion. 对照实验测的是已明确记录边界的外部适配.

## 接下来遵守什么

继续使用已有 API, 全部串行, 不在本机搭全库环境或堆缓存. 每轮记录与实际候选上传, 最多30轮. 论文和 OpenReview 未改.

[全部结果](../results/README.md) | [三组 skills](../skills/README.md) | [每轮进化](../skills/evolution-history/README.md)
