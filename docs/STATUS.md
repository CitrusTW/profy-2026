# 当前做到哪里

## 已完成

1. threejs第5轮达到小范围标准并确认. 随后冻结, 完成two-task三组对照: no-skills通过1/2题, with-skills和with-CogniLife-skills均2/2.
2. economic-dispatch第6轮在开发题grid-dispatch-operator上两次6/6. 原版306608 tokens, 候选114602, 确认86932.
3. 冻结第6轮skill后评测energy-market-pricing: no-skills / with-skills / with-CogniLife-skills均4/4, tokens分别204038 / 181580 / 98354.
4. 通用文件传输适配器在3d-scan-calc上完成原版skills单组验证2/2. 这还不是完整三组实验.
5. 已定位并保存8份历史候选, 当前采用threejs第5轮和economic-dispatch第6轮. 原版skills、无skills配置也有独立目录.

## 正在做

迁移到现有Profy云端, 先验证固定模型输出能否由原评分程序在独立会话中评分. 当前仅云端工具检查完成: Linux、Python、Node、pytest、numpy、scipy等可用, 无Docker和LibreOffice. 不把工具检查记为benchmark成绩.

## 没有完成

SkillsBench全库87题尚未完成. 当前有3道题完成完整三组对照; 另有开发题和适配器检查, 不能混算成全库成绩. 还没有完整CogniLife平台复现, 原代码缺少或未接通capability-gap classifier、通用语义适用性检查和native promotion.

## 去哪里看证据

- [电价分析报告](../results/2026-11-11_skillsbench_full_library/network-family/REPORT.md)
- [电价分析原始数字](../results/2026-11-11_skillsbench_full_library/network-family/frozen-evaluation/RESULTS.json)
- [threejs两题报告](../results/run-04-up-to30/full-compatible-two/REPORT.md)
- [完整skill版本索引](../skills/VERSION_INDEX.json)

论文与OpenReview未改. 早期失败成绩不覆盖, 旧解释有修正时另写说明.
