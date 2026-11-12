# 运行与分析代码入口

所有模型运行已停止. 这里只索引代码, 不建议为了看结果重新运行脚本. 实验来源和结论先看 [总览](../docs/EXPERIMENTS.md).

| 要查什么 | 代码或说明 | 对应输出 |
| --- | --- | --- |
| ADV跨模型统计 | [analyze_adv_judge_v2.py](../results/2026-11-12_overnight/scripts/analyze_adv_judge_v2.py) | [adv_i004_analysis_v2](../results/2026-11-12_overnight/adv_i004_analysis_v2/) |
| ADV同模型生成与评分 | [run_i010.py](../results/2026-11-12_overnight/i010/run_i010.py)、[预注册](../results/2026-11-12_overnight/i010/PREREG_I010.md) | [i010](../results/2026-11-12_overnight/i010/) |
| ADV同模型分析 | [analyze_i010_v3.py](../results/2026-11-12_overnight/i010/analyze_i010_v3.py) | [I010_RESULTS.json](../results/2026-11-12_overnight/i010/analysis/I010_RESULTS.json) |
| 冻结新题统计 | [analyze_skills_v7.py](../results/2026-11-12_overnight/scripts/analyze_skills_v7.py) | [skills_final](../results/2026-11-12_overnight/skills_final/) |
| 中途离线重算 | [recompute_skills_portable.py](../results/2026-11-12_overnight/scripts/recompute_skills_portable.py)、[对应快照说明](../results/2026-11-12_overnight/PORTABLE_ANALYSIS_README.md) | 只对应11:20UTC中途快照, 不是最终结果 |
| 85题完整性审计 | [audit_85_input_output_20261112.py](paper_judge_audit/audit_85_input_output_20261112.py) | [审计报告](../results/2026-11-12_85task_input_output_audit/REPORT.md) |
| Profy原生Linux文件任务adapter | [skillsbench_cloud_runner_20261111](skillsbench_cloud_runner_20261111/README.md) | [SkillsBench证据](../results/2026-11-12_overnight/skillsbench/) |
| 原方法Evolution外部适配 | [native_evolution.py](skillsbench_evolution_20261110/native_evolution.py) | [各轮实际候选](../skills/evolution-history/README.md) |
| 方法、代码、API缺口 | [METHOD_CODE_API_MAP.md](native_method_feasibility_20261110/METHOD_CODE_API_MAP.md) | 解释哪些未接通, 不冒充完整原生复现 |
| 早期原型/PersonaMem | [three_arm_pilot_20261110](three_arm_pilot_20261110/README.md) | 历史尝试, 不作为论文方法效果证据 |

原始运行会调用API, 分析脚本只读记录. 运行前仍须检查脚本参数和数据版本; 中途说明中的路径与预算不是自动重跑授权. 只读整理不需要key. keys、收到的公司源码、隐藏tests不归档. 本机不新建Docker或下载整套环境.
