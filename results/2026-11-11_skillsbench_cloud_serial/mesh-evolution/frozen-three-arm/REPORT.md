# 3d-scan-calc 三组结果

这道 SkillsBench 题要根据公开3D扫描材料计算物体的质量报告, 输出 mass_report.json. 三组用同一道题和原评分, 只改变是否提供原版或进化版 benchmark skill.

| 条件 | 原测试 | total tokens | 求解耗时 | 模型轮数 / 工具调用 |
| --- | --- | --- | --- | --- |
| no-skills | 2/2 | 127350 | 91.827秒 | 8 / 8 |
| 原版 mesh-analysis | 2/2 | 161063 | 91.882秒 | 10 / 10 |
| 第9轮进化版, 开发 | 2/2 | 125369 | 71.560秒 | 8 / 8 |
| 第9轮同一版, 再次确认 | 2/2 | 127654 | 82.077秒 | 8 / 8 |

2/2是这道题的两项原检查, 不是两道题. 耗时不含独立评分和进化. total tokens 包含输入和输出, 其中有 cache tokens; 不能把降幅直接当成实际费用降幅. Profy 未提供可核对的美元费用, 不填估算金额.

## 说明什么

进化版相对原版少22.16% / 20.74%的 tokens, 两次都保持2/2. 但与 no-skills 基本持平: 开发少1.56%, 确认反而多0.24%. 因此这次只支持“减少原版 skill 带来的额外开销”, 没有观察到正确率提升, 不能声称三组依次更好.

这道题用于生成和选择候选. 再次确认仍是同一道题, 不是独立泛化测试. 单次 no-skills 与原版运行也不能证明稳定的平均提升.

## 过程和证据

- [实际数字](RESULTS.json), 包含三组及确认记录.
- [no-skills 原始结果](no-skills/result.json).
- [no-skills 实际 mass_report.json](no-skills/model_mass_report.json).
- [no-skills 云端原评分回执](no-skills/cloud-grade/ACCEPTED_CLOUD_GRADING.json).
- [第9轮记录](../round-09/ROUND.json)和[冻结记录](../FROZEN.json).
- [进化版完整正文](../../../../skills/with-CogniLife-skills/mesh-analysis/SKILL.md).

no-skills 请求没有附带 benchmark skills, 记录中没有外部 skill 调用. 进化版由实际工具返回的正文核对, 确认读到了提供的候选. 求解与评分在不同会话; 原测试只做路径绑定, 评分时核对测试、输入和实际答案的前后 hash.

第7轮收益不足没采用, 第8轮接口故障未收到候选, 第9轮达到预先记录的开发门槛并确认后冻结. 原方法缺失实现与新增外部适配继续在进化记录里明示. 论文与 OpenReview 未改.
