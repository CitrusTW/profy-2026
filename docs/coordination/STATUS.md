# STATUS
- Updated (America/Los_Angeles): 2026-11-12T09:28:47.245638-08:00
- Last applied instruction: I-006 (in progress)
- Latest read: I-009; checkpoint: I004-probe403-not-a-run-no-change-to-model-or-key
- Current work: I006 manuscript revision copy and original-order Profy recovery probes; frozen skills, no new evolution.
- Next: continue one next-planned-run probe every30min; if accepted, resume serial schedule and supplement supply B/C original-verifier grading. Draft1 due11:00PST, reviewer11:15; final15:30; no new run after13:30.
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
- Still blocked:403 Expert is not published. Next same planned run only at registered30min interval; no publication, key/model/identity change. Quota exhaustion is not established.

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
- I005: reads of the assigned skill before/after tool_search are permitted. Supply A/B/C offline scope checks pass; B/C original grading pending API recovery. Environment-limited include/exclude sensitivity retained.
- shock-demand receipt/pytest count disagreement retained, strict reward not changed. Runner-limit raw scores stay missing; both requested analysis policies retained.
- Current frozen workflow is an external native-Linux adaptation, not official Docker; classifier, general applicability and native promotion not connected. First historical threejs evolution usedgpt-4.1, current xlsx/solving usegpt-6.1-sol.
- DNS-only and cancelled superseded client launches retained outside protocol comparisons. No hidden-answer skill edits; no selective deletion.
- Interim report delivered08:00. Draft and final are separate immutable deliveries under paper_rev/draft1 and paper_rev/final.
- 待审核者指令: [REVIEW_QUESTION_CUTOFF_GUARD.md](../../results/2026-11-12_overnight/REVIEW_QUESTION_CUTOFF_GUARD.md)；现有记录保留, 该项等待编号指令。
