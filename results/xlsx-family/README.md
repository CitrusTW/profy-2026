# Excel 开发题: weighted-gdp-calc

原题要求在 gdp.xlsx 中填查找、统计和加权平均公式, 保留原格式. 题目和评分规则没有改写.

| 组别 | 原得分 | 原检查 | 求解 tokens | 状态 |
| --- | ---: | ---: | ---: | --- |
| no-skills | 1.0 | 27/27 | 155489 | 已完成有效原评分 |
| with-skills | 1.0 | 27/27 | 248816 | 已完成 |
| with-CogniLife-skills 第11轮开发 | 1.0 | 27/27 | 109337 | 达标 |
| 同一新 skill 确认 | 1.0 | 27/27 | 133351 | 达标并固定 |

no-skills 的准备和求解对话共151.985秒, 不包括附件上传和评分, 8个 model turns / 7次工具调用. tokens 包含该组的准备和求解对话, 不包含评分、故障诊断或后续 Evolution; 费用美元数未由 API 返回, 不估算.

## 实际证据

- [最终结果](no-skills-result.json)和[原评分回执](no-skills-original-score.json).
- [原回答 gdp.xlsx](no-skills-gdp.xlsx), SHA256: 7b76971f6fac4c24e3767fe6c622809d9d71ef7d3bfe907f0baa80d0b94ed796.
- [评分修复记录](no-skills-grading-repair-provenance.json)和[实际评分日志](no-skills-original-grading.log).
- [固定软件版本](FROZEN_NATIVE_PACKAGES.json)和[环境来源](NATIVE_RUNTIME_PROVENANCE.json).

第一次评分因 uv 下载和权限问题没有生成 pytest 报告, 那次 reward=0 不是有效答题分数. 修复评分只复用已冻结的同一份 Excel 文件, 没让模型重新答题, 没改 verifier. 有效评分的27项全部通过, 回执确认评分源文件和回答文件都未改变.

环境是 Profy Debian + Gnumeric/LibreOffice Calc, 求解用 PRoot 对应原路径, 评分在私有 kernel mount namespace 中运行原 test.sh, 预装原脚本需要的 uv0.9.7. 这与官方 Ubuntu Docker image 有差别; 三组采用同一方案和软件版本, 单独报告为 Profy 下的外部适配.

这道题用于开发和后续候选选择. 本题已完成三组开发验证和一次候选确认, 另有4道题已有三组记录. 本题不是独立泛化结果; 未参与进化的其他公开题还没有跑完.

## 第10轮与第11轮

第10轮候选27/27, 但291458总tokens高于原版, 未采用, 完整SKILL.md与记录保留在 [round-10](round-10/ROUND.json). 第11轮由原Evolution组件读取原版与第10轮的完整开发求解记录后产生, 没有手工改写技能正文, 没有读取评分历史或隐藏答案. [开发与确认记录](round-11/ROUND.json), [固定版本与边界](FROZEN.json), [完整新SKILL.md](../../skills/with-CogniLife-skills/xlsx/SKILL.md).

第11轮两次比原版少56.06% / 46.41%总tokens, 比no-skills也少29.68% / 14.24%. 这是同一道开发题的选择结果, 需要换题检验. 第10/11轮OpenRouter Evolution费用由API实际返回, 分别0.1345174 / 0.1410002美元; Profy费用没有返回, 不推算.
