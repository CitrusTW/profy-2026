# Excel 开发题: weighted-gdp-calc

原题要求在 gdp.xlsx 中填查找、统计和加权平均公式, 保留原格式. 题目和评分规则没有改写.

| 组别 | 原得分 | 原检查 | 求解 tokens | 状态 |
| --- | ---: | ---: | ---: | --- |
| no-skills | 1.0 | 27/27 | 155489 | 已完成有效原评分 |
| with-skills | 待返回 | 待返回 | 待返回 | 原版 xlsx skill 运行中 |
| with-CogniLife-skills | 待运行 | 待运行 | 待运行 | 第10轮尚未开始 |

no-skills 的准备和求解对话共151.985秒, 不包括附件上传和评分, 8个 model turns / 7次工具调用. tokens 包含该组的准备和求解对话, 不包含评分、故障诊断或后续 Evolution; 费用美元数未由 API 返回, 不估算.

## 实际证据

- [最终结果](no-skills-result.json)和[原评分回执](no-skills-original-score.json).
- [原回答 gdp.xlsx](no-skills-gdp.xlsx), SHA256: 7b76971f6fac4c24e3767fe6c622809d9d71ef7d3bfe907f0baa80d0b94ed796.
- [评分修复记录](no-skills-grading-repair-provenance.json)和[实际评分日志](no-skills-original-grading.log).
- [固定软件版本](FROZEN_NATIVE_PACKAGES.json)和[环境来源](NATIVE_RUNTIME_PROVENANCE.json).

第一次评分因 uv 下载和权限问题没有生成 pytest 报告, 那次 reward=0 不是有效答题分数. 修复评分只复用已冻结的同一份 Excel 文件, 没让模型重新答题, 没改 verifier. 有效评分的27项全部通过, 回执确认评分源文件和回答文件都未改变.

环境是 Profy Debian + Gnumeric/LibreOffice Calc, 求解用 PRoot 对应原路径, 评分在私有 kernel mount namespace 中运行原 test.sh, 预装原脚本需要的 uv0.9.7. 这与官方 Ubuntu Docker image 有差别; 三组采用同一方案和软件版本, 单独报告为 Profy 下的外部适配.

这道题用于开发和后续候选选择. 目前没有三组结果, 也没有新的泛化结论. 另有4道题已完成三组, 不把本题第一组混算成第5道三组完成.
