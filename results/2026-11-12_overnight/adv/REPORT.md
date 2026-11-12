# ADV 20题既有分数重新统计

**注意: 这是已有评分记录的统计, 尚不能认作当前平台回答的评分.**
{"by_condition_judge_predates_saved_output": {"generic_llm_raw": 0, "generic_llm_expert_prompt": 0, "profy_expert_full": 20}, "by_condition_pairwise_predates_saved_output": {"generic_llm_raw": 0, "generic_llm_expert_prompt": 0, "profy_expert_full": 20}, "verified_score_output_hash_links": 0, "interpretation": "Saved score summaries only. Current Full platform-labelled outputs cannot be linked to these earlier scores; no causal platform or model comparison is established."}

overall沿用原脚本的5个通用维度平均, 不是7维平均.

| Condition | overall |
|---|---:|
| generic_llm_raw | 3.8800 |
| generic_llm_expert_prompt | 4.0300 |
| profy_expert_full | 4.4300 |

generic_llm_raw
{"mean": 0.5499999999999998, "bootstrap95": [0.32, 0.8099999999999999], "higher": 16, "lower": 0, "tie": 4, "per_task": {"ADV_001": 0.20000000000000018, "ADV_002": 0.6000000000000001, "ADV_003": 0.20000000000000018, "ADV_004": 0.5999999999999996, "ADV_005": 2.3999999999999995, "ADV_006": 0.1999999999999993, "ADV_007": 0.39999999999999947, "ADV_008": 0.7999999999999998, "ADV_009": 0.0, "ADV_010": 0.0, "ADV_011": 1.3999999999999995, "ADV_012": 0.8000000000000003, "ADV_013": 0.0, "ADV_014": 0.6000000000000001, "ADV_015": 0.0, "ADV_016": 0.6000000000000001, "ADV_017": 0.40000000000000036, "ADV_018": 1.1999999999999997, "ADV_019": 0.39999999999999947, "ADV_020": 0.20000000000000018}}

generic_llm_expert_prompt
{"mean": 0.39999999999999997, "bootstrap95": [0.22999999999999993, 0.5999999999999999], "higher": 16, "lower": 1, "tie": 3, "per_task": {"ADV_001": 0.20000000000000018, "ADV_002": 0.20000000000000018, "ADV_003": 0.20000000000000018, "ADV_004": 0.5999999999999996, "ADV_005": 1.5999999999999996, "ADV_006": 0.9999999999999996, "ADV_007": 0.1999999999999993, "ADV_008": 0.5999999999999996, "ADV_009": 0.0, "ADV_010": 0.20000000000000018, "ADV_011": 0.7999999999999998, "ADV_012": 1.0000000000000004, "ADV_013": 0.0, "ADV_014": 0.40000000000000036, "ADV_015": -0.20000000000000018, "ADV_016": 0.20000000000000018, "ADV_017": 0.40000000000000036, "ADV_018": 0.39999999999999947, "ADV_019": 0.0, "ADV_020": 0.20000000000000018}}

Pairwise
{"n": 20, "raw_preference_counts": {"A": 16, "B": 4}, "winner_counts": {"profy_expert_full": 13, "generic_llm_raw": 7}, "A_selection_fraction_all": 0.8, "A_selection_fraction_decisive": 0.8, "system_a_counts": {"profy_expert_full": 9, "generic_llm_raw": 11}, "system_b_counts": {"generic_llm_raw": 9, "profy_expert_full": 11}, "both_orders_available": false}

Error tags
{"generic_llm_raw": {"weak_personalization": 4, "evidence_grounding": 1, "missing_input_not_handled": 4, "overclaiming": 1, "unsafe_boundary": 1}, "generic_llm_expert_prompt": {"evidence_grounding": 1, "missing_input_not_handled": 4, "weak_personalization": 3}, "profy_expert_full": {}}

Model labels
{"generic_llm_raw": {"moonshot-v1-128k": 20}, "generic_llm_expert_prompt": {"moonshot-v1-128k": 20}, "profy_expert_full": {"deepseek-v4-flash": 20}}

No generation or judge calls made. Source hashes and per-task lineage warnings are in results.json and timestamp_and_linkage.csv.