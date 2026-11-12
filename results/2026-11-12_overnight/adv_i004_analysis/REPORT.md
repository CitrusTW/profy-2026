# Claude ADV20 hash-bound rejudging

Valid rubric records 60/60; valid pairwise 80/80. Missing scores remain unknown.

| Condition | Valid n | Overall |
|---|---:|---:|
| generic_llm_raw | 20 | 2.43 |
| generic_llm_expert_prompt | 20 | 2.63 |
| profy_expert_full | 20 | 3.2199999999999998 |

If any rubric condition has missing results, these means are descriptive of different observed subsets, not a complete20-task comparison. No old Full score fills a gap.

{
  "generic_llm_raw": {
    "both_full_wins": 17,
    "opposite_winners": 1,
    "both_baseline_wins": 2
  },
  "generic_llm_expert_prompt": {
    "both_full_wins": 16,
    "both_baseline_wins": 3,
    "opposite_winners": 1
  }
}

All output hashes agree across scoring uses. Full generation label deepseek-v4-flash, baselinesmoonshot-v1-128k; judge different from both.