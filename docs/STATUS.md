# 当前做到哪里

## 已完成

1. threejs第5轮达到小范围标准并确认. 随后冻结, 完成two-task三组对照: no-skills通过1/2题, with-skills和with-CogniLife-skills均2/2.
2. economic-dispatch第6轮在开发题grid-dispatch-operator上两次6/6. 原版306608 tokens, 候选114602, 确认86932.
3. 冻结第6轮skill后评测energy-market-pricing: no-skills / with-skills / with-CogniLife-skills均4/4, tokens分别204038 / 181580 / 98354.
4. 通用文件传输适配器在3d-scan-calc上完成原版skills单组验证2/2. 这还不是完整三组实验.
5. 已定位并保存9份历史候选, 当前采用threejs第5轮和economic-dispatch第6轮. 原版skills、无skills配置也有独立目录.

## 第8轮接口故障

OpenRouter收到第一份响应后, 后续请求出现SSL传输错误, 未收到候选skill. 已保留请求hash和已收到的usage, 未收到响应的费用未知. 不记为方法效果失败, 但计入30轮上限. 接下来从第9轮继续, 全部串行.

## 正在做

已在独立Profy会话用原评分验证固定3D答案2/2, 核对原测试路径绑定、答案和数据的前后hash. 第7轮候选也在云端评分2/2, 使用新skill的实际文件正文已核实; tokens为160781, 对比原版161063仅少约0.18%, 不采用为成功版, 继续调. 后续本例要求至少5%降幅并再次确认, 这是开发阶段门槛, 不修改原评分. 云端完整系统环境仍未验证, 不能据此标记全库可跑. 全部串行, 不再构建本机环境.

## 没有完成

SkillsBench全库87题尚未完成. 当前有3道题完成完整三组对照; 另有开发题和适配器检查, 不能混算成全库成绩. 还没有完整CogniLife平台复现, 原代码缺少或未接通capability-gap classifier、通用语义适用性检查和native promotion.

## 去哪里看证据

- [电价分析报告](../results/2026-11-11_skillsbench_full_library/network-family/REPORT.md)
- [电价分析原始数字](../results/2026-11-11_skillsbench_full_library/network-family/frozen-evaluation/RESULTS.json)
- [threejs两题报告](../results/run-04-up-to30/full-compatible-two/REPORT.md)
- [完整skill版本索引](../skills/VERSION_INDEX.json)

论文与OpenReview未改. 早期失败成绩不覆盖, 旧解释有修正时另写说明.
