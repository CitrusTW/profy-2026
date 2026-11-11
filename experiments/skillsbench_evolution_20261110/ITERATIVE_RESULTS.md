# CogniLife路径的多轮skill refinement

2026-11-10, America/Los_Angeles. 所有新求解均为真实Profy API调用, Evolution为OpenRouter的gpt-6.1-sol. 原workflow、门控、run_stats模型和渲染不改; 多次invoke编排和实测选择是本实验新增部分.

| 开发记录 | 原测试 | tokens | 耗时(秒) | 工具调用 |
| --- | --- | --- | --- | --- |
| 复用原版基线 | 3/3 | 152865 | 156.874 | 9 |
| 复用上一份未选候选 | 3/3 | 287965 | 173.908 | 15 |
| 新候选 1 (selected) | 3/3 | 127057 | 128.795 | 9 |
| 新候选 2 (selected) | 3/3 | 108292 | 124.493 | 8 |
| 新候选 3 (not_selected) | 3/3 | 162868 | 131.6 | 10 |
| 选中版本再次确认 | 3/3 | 126712 | 120.155 | 9 |

结束状态: completed. 开发阶段选中round 2. 这是预算内实测最好的候选, 不是全局最优保证.

| 最后benchmark组别 | 原测试 | tokens | 耗时(秒) | skill读入核验 |
| --- | --- | --- | --- | --- |
| no-skills | 1/3 | 83325 | 116.603 | None |
| with-skills | 3/3 | 114718 | 125.708 | True |
| with-CogniLife-skills | 1/3 | 96782 | 136.088 | True |

Evolution累计返回费用$0.519837; Profy没有美元账单, 总美元费用未知.

每一轮只输入开发题request/events与各版本的原生run_stats. 未选择的开发尝试也保留并反馈成本; 每次invoke仍最多一条建议. 只有质量保持且实测tokens下降才选择, 最后候选单独确认一次. 验证前冻结, 验证后不改skill.

目前只有两道SkillsBench题包含这份threejs skill, 官方main与本地固定commit相同. 最后那道题以前已分析过, 因此结果只能作为diagnostic, 不能当独立泛化证据或完整benchmark成绩. 自动语义适用性检查、能力缺口分类和native promotion仍未完成. 本轮没有修改论文.

仓库仅存助手写的代码、数字报告和模型生成的OBJ数据. 原skills、派生skill全文、原输入、第三方源码、gold和keys留在工作区, 不进private repo.

最终决定: 不采用进化版, 保留原版. 这是本轮全部结果之后的实际决定, 不是修改第三组来追求好看分数.
最后benchmark相对原版, 原测试通过数变化-2, reported tokens变化-15.6%. 质量与成本都要满足目标, 不能用省tokens抵偿质量退步.

独立agent仅用DEV复核, 未发现必须停止单OBJ开发检查的严重错误, 但resource路径、skill.execute接口与失败后修复例外仍存在未验证风险. 复核没有输入Evolution, 不能视为通用语义核验通过.
