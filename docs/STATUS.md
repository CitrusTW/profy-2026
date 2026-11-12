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

## 环境补充

已在 Profy 云端实际运行临时 Alpine Linux, [回执与排错记录](../results/2026-11-11_skillsbench_cloud_serial/environment-checks/README.md)单独保存. 公开工具通过内存分片中转, 本机没有保存镜像或运行环境. 原 benchmark Dockerfile 的云端流程仍未跑通; 不把环境检查计入题目成绩.

原生 Docker 已在云端实际拉取并运行固定 SHA256 的公开 Alpine image, [实际记录与未解决的清理项](../results/2026-11-11_skillsbench_cloud_serial/environment-checks/NATIVE_DOCKER.md)已留档. 新的原题 runner 放在独立目录, [从这里看](../experiments/skillsbench_cloud_runner_20261111/README.md). 先验证 weighted-gdp-calc, 不提前算作三组完成. 原方法共享代码36项检查、新云端原型3项检查通过; 这不是benchmark题数.

## Excel 开发题的最新进展

weighted-gdp-calc 的 no-skills 已完成有效原评分: 27/27, reward1.0, 155489求解 tokens. 原版 xlsx skill 组正在串行运行, 新的第10轮 Evolution 尚未开始. [实际数字、原回答及评分修复证据](../results/xlsx-family/README.md).

官方 image 的镜像文件已经下完, 但云端解压超时. 当前改用已验证的轻量 Profy Debian 文件任务环境; 与官方 Ubuntu image 的差别、实际软件版本和原评分源文件指纹均留档. 仍是4道题完成完整三组, 87题全库未完成.
