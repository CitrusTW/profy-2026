# STATUS
- Updated (America/Los_Angeles): 2026-11-12T10:23:13.404860-08:00
- Last applied instruction: I-010 (direct user message; newer than coordination I009).
- Latest read: I-010; checkpoint: I010 completed_judging_task_ADV_009
- Current work: manuscript draft2 per I008/I009, existing evidence only; no more Profy requests.
- Next: restore valid original structure and archive proxy85 numbers unchanged; add clean ADV figure and deployment lessons. Draft2 by12:30PST, final by15:30; no waiting for resubmission.
- ETA: SkillsBench completion unknown because API unavailable; ADV complete; paper state below.
- OpenRouter judge received expense USD4.941796; unknown-cost calls0. Profy USDunknown. No purchase/recharge.

## SkillsBench: all original bookkeeping attempts
- Rows include setup failures/API rejections, not only scientific runs. API403 before model usage is NOT a scored trial. Earlier raw records and superseded failures are preserved.
- Fixed eight tasks, xlsx adopted round11, serial no-skills -> original -> frozen;24-turn cap unchanged. No new evolution.
| Task | Phase | Condition | Rep | Status | Strict | Receipt pass/fail/skip | Observed tokens | Solver sec |
|---|---|---|---:|---|---|---|---:|---:|
| shock-analysis-demand | 01_任务结果 | with-skills | 1 | runner_limit | unknown | unknown/unknown/unknown | 1168850 | 836.448 |
| shock-analysis-demand | 01_任务结果 | no-skills | 1 | scored | 0 | 3/2/0 | 839001 | 760.071 |
| powerlifting-coef-calc | launch-03 | no-skills | 1 | scored | 1 | 11/0/0 | 180811 | 267.007 |
| powerlifting-coef-calc | launch-03 | with-CogniLife-skills | 1 | scored | 1 | 11/0/0 | 230840 | 297.361 |
| powerlifting-coef-calc | launch-03 | with-skills | 1 | scored | 1 | 11/0/0 | 235561 | 275.167 |
| reserves-at-risk-calc | launch-03 | no-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 44468 | 265.677 |
| reserves-at-risk-calc | launch-03 | with-CogniLife-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 44912 | 278.424 |
| reserves-at-risk-calc | launch-03 | with-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 44956 | 276.649 |
| shock-analysis-demand | launch-03 | with-CogniLife-skills | 1 | scored | 0 | 0/5/0 | 885699 | 731.195 |
| shock-analysis-supply | launch-03 | no-skills | 1 | scored(supplement) | 0 | 1/8/0 | 73630 | 182.307 |
| shock-analysis-supply | launch-03 | with-CogniLife-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 100269 | 202.705 |
| shock-analysis-supply | launch-03 | with-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 104019 | 181.555 |
| invoice-fraud-detection | launch-04-i003 | no-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | unknown | 2.359 |
| reserves-at-risk-calc | launch-04-i003 | no-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 27292 | 186.075 |
| reserves-at-risk-calc | launch-04-i003 | with-CogniLife-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | unknown | 1.835 |
| reserves-at-risk-calc | launch-04-i003 | with-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | unknown | 1.99 |
| xlsx-recover-data | launch-04-i003 | no-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | unknown | 1.96 |
| xlsx-recover-data | launch-04-i003 | with-CogniLife-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | unknown | 3.65 |
| xlsx-recover-data | launch-04-i003 | with-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | unknown | 2.455 |
| reserves-at-risk-calc | launch-05-profy-recovery | no-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | unknown | 2.592 |

## Profy state
- Latest next-run probe: 403_rejected_not_a_run; 1794504525.2915342 Unix epoch; scientific_run=False.

## ADV20: current usable evidence
- I004 uniform4096 batch:60 valid rubric judgments; old incomplete52 rubrics are audit-only. I00380 valid counterbalanced pairwise judgments retained,3000-character output prefix. No answers regenerated.
- Judge anthropic/claude-opus-5.5. Full deepseek-v4-flash, baselinesmoonshot-v1-128k; model confound retained. Current results: ADV_CURRENT_RESULTS.md and adv_i004_analysis_v2/results.json.
- Overall Raw2.43 / Expert Prompt2.63 / Full3.22. Full-minus-Prompt0.59,95%CI[0.30,0.87]. Both-order Full wins16/20 versus Prompt,17/20 versus Raw. Missing-info tie and lower Full coherence/safety are reported.
- ALL old Full scores remain proxy-output audit records and do not enter manuscript claims.

## Manuscript copy
- PAPER_DRAFT1_VALIDATION.json: compiled=True, body_pages=6, total_pdf_pages=21.
- Local source copy: /Users/mac/Desktop/naacl 2026.10 - CogniLife/01_任务结果/2026-11-12_night_validation_092503/cognilife_rev_20261112_draft1_anonymous
- PDF in experiment branch: results/2026-11-12_overnight/paper_rev/draft1/CogniLife_revision_draft1.pdf
- Original source, Overleaf and OpenReview unchanged. Numeric-source hashes, original customs values, screenshot anonymization and page count checked.

## Exceptions / decisions
- I003 pin check repaired for actual active interpreter version/location; dependency pins, questions, skills and verifier unchanged. Old setup failures preserved.
- shock-demand receipt/pytest count disagreement retained, strict reward not changed. Runner-limit raw scores stay missing; both requested analysis policies retained.
- Current frozen workflow is an external native-Linux adaptation, not official Docker; classifier, general applicability and native promotion not connected. First historical threejs evolution usedgpt-4.1, current xlsx/solving usegpt-6.1-sol.
- DNS-only and cancelled superseded client launches retained outside protocol comparisons. No hidden-answer skill edits; no selective deletion.
- Interim report delivered08:00. Draft and final are separate immutable deliveries under paper_rev/draft1 and paper_rev/final.

## I007/I008/I009 current decision
- ALL Profy probes stopped by USER DECISION, not by observed performance. Last probe completedUTC 2026-11-12T17:28:45.291534+00:00. No further Profy request will be submitted.
- Three matched held-out tasks only: energy round6, pre-round12 protein/xlsx11, powerlifting/xlsx11; one run/group/task. Shock-demand has both limit policies. Supply B/C unscored/platform unavailable; other incomplete tasks excluded and listed.
- I008: preserve usable original content. Old85 numeric records are archived with checkpoint-prompt-proxy labels only, never as Full/deployment results. Main result is newADV20 with generation-model difference noted next to16/20 in abstract/contributions.
- I009: new single-column stacked pairwise plot includes all three categories; all5 dimension differences/CI retained. Lessons avoid unproven causal claims.
- Latest paper PAPER_DRAFT2_VALIDATION.json: results/2026-11-12_overnight/paper_rev/draft2/CogniLife_revision_draft2.pdf, body_pages=6, total_pdf_pages=25.

## I010 same-declared-model ADV control
- Direct user I010 accepted; PREREG_I010 frozen before paid calls. Exact OpenRouter ID deepseek/deepseek-v4-flash; no substitution. Provider/revision match to historical Full unknown.
- USD10 hard actual-receipt ceiling; initial estimate4.418166196721311USD, not observed expense. All Profy requests remain stopped.
- Latest phase/state: {"updated_utc": "2026-11-12T18:23:12.439145+00:00", "phase": "completed_judging_task_ADV_009", "last_job": null, "calls": 105, "known_actual_usd": "1.9954250879", "unknown_cost_calls": 0, "reserved_unknown_cost_ceiling_usd": "0", "terminal": null, "elapsed_seconds": 1607.3836538791656, "full_regenerated": false}
- Use complete-pipeline ADV template including its uncertainty warning; standalone template differs and historical requests unavailable.40 new baselines,60 fresh rubrics,80counterbalanced pairs. Full unchanged.
