# 可用于修订副本的ADV20结果 (I-004)

唯一rubric来源是I004统一4096批次, 不是旧Full评分或I003不完整rubric. Pairwise使用I003的80次有效正反序评分. 没有重新生成回答.

| Condition | n | Overall |
|---|---:|---:|
| generic_llm_raw | 20 | 2.43 |
| generic_llm_expert_prompt | 20 | 2.63 |
| profy_expert_full | 20 | 3.22 |

Full减generic_llm_raw: 0.79, bootstrap95%CI [0.46, 1.11], 高/低/平 18/2/0. 正反都Full赢/都基线赢/反转: 17/2/1. A位选择比例 0.525.

Full减generic_llm_expert_prompt: 0.59, bootstrap95%CI [0.30, 0.87], 高/低/平 15/3/2. 正反都Full赢/都基线赢/反转: 16/3/1. A位选择比例 0.525.

必须保留的边界: missing_info子集Full与Expert Prompt overall均值相同; Full coherence和safety低于Expert Prompt. 不能沿用原稿“missing-information差距最大”或“各维度均更好”的说法. Full模型deepseek-v4-flash, 两个基线moonshot-v1-128k; 新judge anthropic/claude-opus-5.5. 这支持有模型差异的配置级输出比较, 不是进化效果归因. Pairwise每份回答只用前3000字符, 与原函数一致.

费用: 两批全部回执合计USD4.941796. I004有1次JSON解析失败后按规则重试成功, 无缺失; 原始失败保留.

数字出处: adv_i004_analysis/results.json 和 adv_i004_context_analysis/results.json; 脚本scripts/analyze_adv_judge.py和scripts/analyze_adv_context.py. 旧Full审计仅在adv/保留, 不进入论文数字. 本文数值由脚本输出格式化, 原始精度在JSON中保存.
