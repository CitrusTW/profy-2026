# STATUS
- Updated (America/Los_Angeles): 2026-11-12T03:12:24.944820-08:00
- Last applied instruction: I-003 (in progress)
- Latest read: I-003; checkpoint: Profy403-confirmed-expert-not-published-stop-no-recharge
- Current work: frozen xlsx round11, fixed eight-task order, all Profy solving/grading serial; I003 Claude ADV rejudge may run alongside Profy.
- Next: retain completed runs; rerun only the I003-authorized failed setup; at most three passes. No new evolution.
- Deadline: 13:30 PST no new run; paper copy then; final report/PDF by15:30 PST.
- ETA: unknown. ADV archive audit complete; fresh judge progress below. Profy USD unknown; no recharge.

## Completed attempts (old setup failures retained)
| Task | Condition | Rep | Status | Strict | Pass/fail/skip (receipt) | Tokens | Solver seconds |
|---|---|---:|---|---|---|---:|---:|
| shock-analysis-demand | with-skills | 1 | runner_limit | unknown | unknown/unknown/unknown | 1168850 | 836.448 |
| shock-analysis-demand | no-skills | 1 | scored | 0 | 3/2/0 | 839001 | 760.071 |
| powerlifting-coef-calc | no-skills | 1 | scored | 1 | 11/0/0 | 180811 | 267.007 |
| powerlifting-coef-calc | with-CogniLife-skills | 1 | scored | 1 | 11/0/0 | 230840 | 297.361 |
| powerlifting-coef-calc | with-skills | 1 | scored | 1 | 11/0/0 | 235561 | 275.167 |
| reserves-at-risk-calc | no-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 44468 | 265.677 |
| reserves-at-risk-calc | with-CogniLife-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 44912 | 278.424 |
| reserves-at-risk-calc | with-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 44956 | 276.649 |
| shock-analysis-demand | with-CogniLife-skills | 1 | scored | 0 | 0/5/0 | 885699 | 731.195 |
| shock-analysis-supply | no-skills | 1 | scored(supplement) | 0 | 1/8/0 | 73630 | 182.307 |
| shock-analysis-supply | with-CogniLife-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 100269 | 202.705 |
| shock-analysis-supply | with-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 104019 | 181.555 |
| invoice-fraud-detection | no-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 0 | 2.359 |
| reserves-at-risk-calc | no-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 27292 | 186.075 |
| reserves-at-risk-calc | with-CogniLife-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 0 | 1.835 |
| reserves-at-risk-calc | with-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 0 | 1.99 |
| xlsx-recover-data | no-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 0 | 1.96 |
| xlsx-recover-data | with-CogniLife-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 0 | 3.65 |
| xlsx-recover-data | with-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 0 | 2.455 |

## ADV20: I003 supersedes use of old Full scores
- Old Full rubric/pairwise scores are proxy-output audit records. They will not support ANY revised-paper Full conclusion.
- New judge: anthropic/claude-opus-5.5; original Listing1/2; hashes bind actual saved outputs to every request/response; no regenerated answers.
- Primary jobs observed: 140/140; calls: 159; failed calls: 27. Received cost USD3.529044; unknown-cost calls0.
- Registered primary-call conservative ceiling11.200208 USD, total ceiling15 USD. A ceiling is not an observed bill.
- Some Full rubric calls hit1024 output tokens (including reasoning); no partial JSON scores used. Uniform rubric repair requested, no unapproved parameter change.

## Paper revision copy
- Not created yet; original project/Overleaf/OpenReview untouched. Start per I002 at13:30 PST.
- I003: use only successful fresh-judge data; if incomplete/omitted, remove Full judge-comparison claims and flag user decision. Never fill gaps with old scores.
- Deliver only PDF and change ledger under results/2026-11-12_overnight/paper_rev; no LaTeX in Git.

## Exceptions and decisions
- I003 pin fix queries active distribution version/location in the same task Python. Pins, dependencies, skills,24-turn cap and original verifier unchanged. Old failed setups remain in the evidence.
- Existing powerlifting three-arm first pass finished before the safe controller boundary. No active solving/grading was killed.
- Supply A had pure tool_search with no skill read: original verifier supplemented without solving/answer changes. B/C supplied-skill reads before discovery await scope clarification.
- Original receipt/pytest counts disagree on shock-demand; both retained, reward unchanged. See count-audit sidecars.
- Capability-gap classifier, general applicability and native promotion not connected. Native Linux adapter is not official Docker. Historical first threejs evolution usedgpt-4.1; current xlsx11/solving usegpt-6.1-sol.
- Earlier DNS-only submissions created no model sessions; one superseded baseline interrupted on direct user amendment, excluded from results, observed466072 tokens retained. USDunknown.
- New adapter and judge questions below are sent to the authorized reviewer; all original artifacts preserved.

## URGENT: Profy execution paused after repeated403
- Repaired reserve setup stream ended without run.completed; following agents/run requests return403 with zero usage. No scores invented.
- All NEW Profy model submissions are paused; no recharge/key rotation. Read-only session query succeeds200, so quota exhaustion is not established. Reason remains unknown.
- Owned incomplete setup activity was interrupted through its existing session; no scorer was active. OpenRouter ADV judge continues independently within15USD.
- See PROFY_403_READONLY_DIAGNOSTIC.json and PROFY_ABANDONED_SETUP_INTERRUPT.json. Await explicit diagnostic/resume direction; other reporting continues.

## CONFIRMED UPDATE: Expert is not published
- One bounded original-plan reserve recovery captured the403 JSON body: Expert is not published. Requested expertId/model match the last successfully scored run.
- Further Profy calls STOPPED. This is not a proven quota-exhaustion diagnosis. No recharge, key/model/identity bypass or autonomous expert publication.
- Owner must restore API-callable published state of the supplied expert. See PROFY_BLOCKER_CONFIRMED.md and launch05 recovery evidence.
- New Claude batch1 complete: rubric20/20/12, all80 pairwise valid; uniform60-rubric repair requested. Already received cost3.529044 USD + proposed repair ceiling8.054640 USD =11.583684 USD <=15.
- 待审核者指令: [REVIEW_QUESTION_I003_judge_output_limit.md](../../results/2026-11-12_overnight/REVIEW_QUESTION_I003_judge_output_limit.md)；现有原始记录保留, 尚未改adapter。
- 待审核者指令: [REVIEW_QUESTION_I003_tool_search_scope.md](../../results/2026-11-12_overnight/REVIEW_QUESTION_I003_tool_search_scope.md)；现有原始记录保留, 尚未改adapter。
- 待审核者指令: [REVIEW_QUESTION_pip_pin_check.md](../../results/2026-11-12_overnight/REVIEW_QUESTION_pip_pin_check.md)；现有原始记录保留, 尚未改adapter。
- 待审核者指令: [REVIEW_QUESTION_profy_403.md](../../results/2026-11-12_overnight/REVIEW_QUESTION_profy_403.md)；现有原始记录保留, 尚未改adapter。
- 待审核者指令: [REVIEW_QUESTION_tool_search.md](../../results/2026-11-12_overnight/REVIEW_QUESTION_tool_search.md)；现有原始记录保留, 尚未改adapter。
