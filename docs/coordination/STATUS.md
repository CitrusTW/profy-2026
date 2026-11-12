# STATUS
- Updated (America/Los_Angeles): 2026-11-12T05:38:35.574133-08:00
- Last applied instruction: I-005 (in progress)
- Latest read: I-005; checkpoint: 30min-checkpoint
- Current work: Profy STOPPED (Expert is not published); Claude batch1 finished with incomplete rubrics. Reporting and instruction checks continue.
- Next: await owner restoration of supplied expert and numbered review of uniform rubric repair. No new Profy submissions, key/model bypass, publication or evolution.
- Deadline: 13:30 PST no new run; paper copy then; final report/PDF by15:30 PST.
- ETA: unknown. ADV archive audit complete; fresh judge progress below. Profy USD unknown; no recharge.

## Completed attempts (old setup failures retained)
| Task | Phase | Condition | Rep | Status | Strict | Pass/fail/skip (receipt) | Tokens | Solver seconds |
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
| invoice-fraud-detection | launch-04-i003 | no-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 0 | 2.359 |
| reserves-at-risk-calc | launch-04-i003 | no-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 27292 | 186.075 |
| reserves-at-risk-calc | launch-04-i003 | with-CogniLife-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 0 | 1.835 |
| reserves-at-risk-calc | launch-04-i003 | with-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 0 | 1.99 |
| xlsx-recover-data | launch-04-i003 | no-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 0 | 1.96 |
| xlsx-recover-data | launch-04-i003 | with-CogniLife-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 0 | 3.65 |
| xlsx-recover-data | launch-04-i003 | with-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 0 | 2.455 |
| reserves-at-risk-calc | launch-05-profy-recovery | no-skills | 1 | infrastructure_failure | unknown | unknown/unknown/unknown | 0 | 2.592 |

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

## CONFIRMED UPDATE: Expert is not published
- One bounded original-plan reserve recovery captured the403 JSON body: Expert is not published. Requested expertId/model match the last successfully scored run.
- Further Profy calls STOPPED. This is not a proven quota-exhaustion diagnosis. No recharge, key/model/identity bypass or autonomous expert publication.
- Owner must restore API-callable published state of the supplied expert. See PROFY_BLOCKER_CONFIRMED.md and launch05 recovery evidence.
- New Claude batch1 complete: rubric20/20/12, all80 pairwise valid; uniform60-rubric repair requested. Already received cost3.529044 USD + proposed repair ceiling8.054640 USD =11.583684 USD <=15.

## I-004 update (supersedes previous waiting notes)
- Uniform4096 rubric rerun authorized: all60, same model/prompt/parser; this is the only rubric batch usable in the paper. Prior52 valid rubrics remain audit-only; prior80 complete pairwise retained,3000-character prefix each output.
- New batch calls61, valid60, receipt USD1.412752; combined received USD4.941796. Combined actual budget<=15USD; quota exhausted stops, no recharge.
- Profy: one original-plan next-run probe every30min;403 is not a scientific run. No publishing/key/model/identity change. Resume full serial schedule only if accepted.
- If still403 at12:00PST, start revision copy then; otherwise13:30. Final by15:30.
- Supply B/C skill-read-before-search scope remains unresolved; no answers rewritten and no reruns selected by outcome.
- Reviewer reports stale02:18 status; this executor has pushed later commits to the exact prescribed branch, with receipts. Current STATUS timestamp and branch commit can verify delivery.

## I-005 update
- Assigned supplied SKILL.md reads before/after tool_search are permitted. Offline supply A/B/C checks all pass; B/C original-verifier grading is queued until Profy recovery, no resolving or answer edits.
- The old scope question is resolved; reviewer confirmed status pushes were normal. No Git repair or extra proof is pending.
- ADV paper must retain missing-info tie and lower Full coherence/safety versus Expert Prompt, model confound,3000-character pairwise prefix.
