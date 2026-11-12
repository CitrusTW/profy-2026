# CogniLife 实验记录

先看 [实验总览](docs/EXPERIMENTS.md). 这里说明每批做了什么、实际得到什么、哪些结果进入论文、证据在哪里.

| 想查什么 | 从这里开始 |
| --- | --- |
| 最新结果和未完成的部分 | [当前状态](docs/STATUS.md) |
| 每批实验怎么区分 | [实验总览与证据入口](docs/EXPERIMENTS.md) |
| ADV 20题、SkillsBench 新题的最终记录 | [11月12日批次说明](results/2026-11-12_overnight/README.md) |
| 最新论文、完整摘要和数字出处 | [论文版本说明](results/2026-11-12_overnight/paper_rev/README.md) |
| no-skills / 原版 / 进化版实际用了什么 | [三组 skills](skills/README.md) |
| 每轮怎么进化、有没有采用 | [进化版本记录](skills/evolution-history/README.md) |
| 开发、失败、审计和早期尝试 | [全部实验目录](results/README.md) |
| 运行和分析代码 | [代码入口](experiments/README.md) |
| 按文件名找全部记录 | [文件清单 CSV](docs/records/FILE_INVENTORY.csv) |

**当前结论:** ADV 的跨模型对照有优势, 换成相同模型标签的基线后, overall 优势没有保留. SkillsBench 可比较的3道 held-out 题正确率持平, tokens 有增有减. 这些边界已经写进论文, 不把开发题收益当作新题效果.

本仓库的完整记录在 `codex/three-arm-skill-pilot-20261110` 分支; `coordination` 只传递协作指令. 全部模型运行已停止, 本次整理没有调用模型或重跑实验.

## 目录怎么读

- `results/`: 每次实际运行、原始返回、评分、统计与失败记录.
- `skills/`: 三组配置、公开原版 SKILL.md、实际候选和进化过程.
- `experiments/`: 自写运行、适配与分析代码. 收到的公司源码和隐藏评分材料不放进来.
- `docs/`: 当前状态、实验总览、文件清单和协作状态.
- `archive/`: 历史入口及整理前的说明快照.

旧结果和路径保留. 报告中的“运行中”可能是当时的快照, 现在是否还在运行以当前状态为准. `full_library` 是旧目录名, 不代表 SkillsBench 全库跑完; tokens 不是美元费用.
