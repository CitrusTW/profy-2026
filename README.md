# profy-2026

这里保存三组 SkillsBench 实验的代码、skills 和实际结果. 先看结果, 想了解怎么做的再往下找.

## 2026-11-12: 85 题完整性审计已完成

[先看审计报告](results/2026-11-12_85task_input_output_audit/REPORT.md). Raw / Expert Prompt / Full 共255份保存记录按同一标准检查. 原始生成请求和 finish_reason 缺失的地方标为无法核实, 不算通过. 新 judge 和 SkillsBench 进化均暂停, 等待审计确认; 本轮没有修复、重跑或改论文.

## 从哪里开始

| 想知道什么 | 点这里 |
| --- | --- |
| 现在做完了什么, 还缺什么 | [当前状态](docs/STATUS.md) |
| 三组分别用了哪些 skills | [skills 目录说明](skills/README.md) |
| 每一轮改了什么, 为什么采用或没采用 | [进化记录](skills/evolution-history/README.md) |
| 实际回答、得分、tokens 和耗时 | [实验结果](results/README.md) |
| 运行代码在哪里 | [代码目录说明](experiments/README.md) |
| 以前试过什么 | [历史入口](archive/README.md) |

## 文件夹怎么分

```text
docs/         当前进度和说明
skills/       三组配置、原版 skills、采用的进化版和每轮记录
results/      实际结果; 每个实验从 REPORT.md 开始看
experiments/  运行与分析代码
archive/      旧尝试的入口和整理前的状态快照
```

每个实验通常先看 REPORT.md, 再查 RESULTS.json 的数字. SKILL.md 是实际给模型读的操作说明; EVOLUTION_RECORD.json 记录它怎么生成; changes_from_parent.diff 显示相对上一版改了哪些文字. 没收到候选的轮次不会伪造 SKILL.md.

## 已完成的三组对照

| SkillsBench 题目范围 | no-skills | 原版 skills | 进化版 skills | 能说明什么 |
| --- | --- | --- | --- | --- |
| threejs 两题 | 1/2题通过 | 2/2题通过, 237638 tokens | 2/2题通过, 217326 tokens | 相比原版合计少8.55%; 两题参与过调试 |
| energy-market-pricing | 4/4检查, 204038 tokens | 4/4检查, 181580 tokens | 4/4检查, 98354 tokens | 相比原版少45.83%; 未用于生成 skill, 与开发题共享公开电网数据 |
| 3d-scan-calc | 2/2检查, 127350 tokens | 2/2检查, 161063 tokens | 两次2/2检查, 125369 / 127654 tokens | 相比原版少22.16% / 20.74%, 与 no-skills 基本持平; 这是开发题 |

这里共4道题完成三组对照. 2/2、4/4检查是单题内部测试数, 不是题目数. 这些结果不能当成87题全库成绩, tokens 也不等于实际费用.

## 执行约定

- 进化走已有 OpenRouter key, 求解走已有 Profy key, 使用 gpt-6.1-sol.
- 全部串行. 本机不搭全库环境, 不堆 Docker 镜像或大缓存, 不额外购买服务.
- 每轮保留候选、来源、修改过程和实际结果. 开发题可用于调整, 评测题答案不送进进化.
- 收到的原方法代码仍有缺失或未接通部分, [当前状态](docs/STATUS.md)明确说明. 不把外部适配说成完整平台复现.
- 不上传 keys、收到的 Profy 公司源码、隐藏评分材料或无关第三方代码. 原版和进化版 SKILL.md 按要求归档; 其他公开资源只记录固定来源和 hash.
- 论文与 OpenReview 未改.

旧路径保留, 以前的链接仍可用. archive 是查旧记录的入口, 不是把重复文件再存一份.
