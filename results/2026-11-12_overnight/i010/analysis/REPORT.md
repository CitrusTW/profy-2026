# Claude ADV20 hash-bound rejudging

Valid rubric records 60/60; valid pairwise 79/80. Missing scores remain unknown.

| Condition | Valid n | Overall |
|---|---:|---:|
| generic_llm_raw | 20 | 3.31 |
| generic_llm_expert_prompt | 20 | 3.4200000000000004 |
| profy_expert_full | 20 | 3.2299999999999995 |

If any rubric condition has missing results, these means are descriptive of different observed subsets, not a complete20-task comparison. No old Full score fills a gap.

{
  "generic_llm_raw": {
    "both_full_wins": 8,
    "both_baseline_wins": 10,
    "opposite_winners": 2,
    "both_ties": 0,
    "tie_mixed": 0,
    "missing_order": 0
  },
  "generic_llm_expert_prompt": {
    "both_full_wins": 9,
    "both_baseline_wins": 7,
    "opposite_winners": 3,
    "both_ties": 0,
    "tie_mixed": 0,
    "missing_order": 1
  }
}

All output hashes agree across scoring uses. Full historical model label deepseek-v4-flash; I010 baselines requested deepseek/deepseek-v4-flash. Full provider/revision identity is unknown; judge differs from generation model.