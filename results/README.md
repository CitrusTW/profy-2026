# 看实验结果

先打开报告, 它解释题目做什么、三组差在哪、实际数字是什么. 再打开同目录 RESULTS.json 查记录. 正确率、tokens 和耗时分别看, 不把 tokens 直接当成费用.

## 已完成的三组对照

| 实验 | 先读报告 | 适用范围 |
| --- | --- | --- |
| 3d-scan-calc | [三组数字与结论](2026-11-11_skillsbench_cloud_serial/mesh-evolution/frozen-three-arm/REPORT.md) | 第9轮; 同一开发题, 与 no-skills 基本持平 |
| energy-market-pricing | [三组报告](2026-11-11_skillsbench_full_library/network-family/REPORT.md) | 第6轮冻结后评测; 与开发题共享公开电网数据 |
| threejs 两题 | [两题三组报告](run-04-up-to30/full-compatible-two/REPORT.md) | 第5轮; 两题参与过调试 |

## 查失败和旧尝试

| 入口 | 查什么 |
| --- | --- |
| [云端实验记录](2026-11-11_skillsbench_cloud_serial/README.md) | 第7轮、8轮故障、第9轮和原评分接通记录 |
| [第4至5轮进度](run-04-up-to30/PROGRESS.md) | 保留成本没改善的第4轮 |
| [第1至3轮](run-03-iterative/) | 历史运行, 包含输出表示问题 |
| [早期 gpt-6.1-sol 运行](run-02-gpt61/) | 历史失败版 |

文件名含 full_library 只是当时的工作目录名, 不表示87题跑完. 环境检查、评分程序自检、待运行配置也不算完成了模型实验.
