# 8题广度优先验证 + 2道此前held-out结果

{"complete_valid_tasks": 2, "quality_counts": {"tie": 2}, "tokens_counts": {"unknown_variation": 2}, "can_claim_accuracy_improved": false, "can_claim_tokens_reduced": false, "permitted_wording": "效果因任务而异", "policies": {"a_count_limits_as_failure": {"n_compared_tasks": 3, "tasks": ["shock-analysis-demand", "energy-market-pricing", "protein-expression-analysis"], "quality_counts": {"tie": 3}, "tokens_counts": {"unknown_variation": 2}, "observed_token_directions": {"decrease": 1, "increase": 1}, "n_token_comparable_tasks": 2, "bootstrap_tokens_percent": null, "can_claim_accuracy_improved": false, "can_claim_tokens_reduced": false}, "b_exclude_tasks_with_any_limit": {"n_compared_tasks": 2, "tasks": ["energy-market-pricing", "protein-expression-analysis"], "quality_counts": {"tie": 2}, "tokens_counts": {"unknown_variation": 2}, "observed_token_directions": {"decrease": 1, "increase": 1}, "n_token_comparable_tasks": 2, "bootstrap_tokens_percent": null, "can_claim_accuracy_improved": false, "can_claim_tokens_reduced": false}}, "includes_two_prior_heldout_results": true, "newly_completed_eight_task_comparisons": 1, "versions_are_skill_specific": true}

注意: runner_limit没有原评分. 仅口径(a)分析时当失败; 口径(b)整题排除. 中止tokens不参与完成运行效率比较. n=1的标准差unknown, 不填0.

| Task | Skill/round | Group | n/scored | strict mean | Policy(a) mean | completed tokens mean ± SD |
|---|---|---|---:|---:|---:|---|
| shock-analysis-demand | xlsx/11 | no-skills | 1/1 | 0 | 0 | 839001 ± None |
| shock-analysis-demand | xlsx/11 | with-skills | 1/0 | None | 0 | None ± None |
| shock-analysis-demand | xlsx/11 | with-CogniLife-skills | 1/1 | 0 | 0 | 885699 ± None |
| shock-analysis-supply | xlsx/11 | no-skills | 1/0 | None | None | None ± None |
| shock-analysis-supply | xlsx/11 | with-skills | 1/0 | None | None | None ± None |
| energy-market-pricing | economic-dispatch/6 | no-skills | 1/1 | 1 | 1 | 204038 ± None |
| energy-market-pricing | economic-dispatch/6 | with-skills | 1/1 | 1 | 1 | 181580 ± None |
| energy-market-pricing | economic-dispatch/6 | with-CogniLife-skills | 1/1 | 1 | 1 | 98354 ± None |
| protein-expression-analysis | xlsx/11 | no-skills | 1/1 | 1 | 1 | 183191 ± None |
| protein-expression-analysis | xlsx/11 | with-skills | 1/1 | 1 | 1 | 187869 ± None |
| protein-expression-analysis | xlsx/11 | with-CogniLife-skills | 1/1 | 1 | 1 | 264808 ± None |

## 任务状态
| Task | Status | Note |
|---|---|---|
| shock-analysis-demand | complete_with_runner_limit | Prior partial attempts reused; frozen only added tonight |
| shock-analysis-supply | partial | Prespecified frozen-version test |
| reserves-at-risk-calc | not_started | Prespecified frozen-version test |
| powerlifting-coef-calc | not_started | Prespecified frozen-version test |
| xlsx-recover-data | not_started | Prespecified frozen-version test |
| invoice-fraud-detection | not_started | Prespecified frozen-version test |
| pdf-excel-diff | not_started | Prespecified frozen-version test |
| jpg-ocr-stat | not_started | Prespecified frozen-version test |
| energy-market-pricing | complete | Earlier held-out result, no new runs tonight |
| protein-expression-analysis | complete | Initially held-out for round11; used in selection after round12, not independent of that later selection |

## 门控预测与实际执行
{"prediction_type": "model-estimated efficiency rubric, not predicted task tokens", "before": 13.85, "after": 26.12, "predicted_token_reduction_percent": "unknown", "xlsx_heldout_observed_token_changes": {"shock-analysis-demand": null, "protein-expression-analysis": 40.95353677296414}, "economic_dispatch_round6_reported_separately": true}

原始轨迹/附件/verifier输出在historical_inputs和launch-03/runs. 上一版启动失败和中断另存, 不作为新题成绩.