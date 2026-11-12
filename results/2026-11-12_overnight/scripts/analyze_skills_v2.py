"""Amended breadth-first analysis, with both runner-limit policies and actual n."""
import argparse,collections,csv,json,statistics
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;W=R.parents[1]
LABELS=['no-skills','with-skills','with-CogniLife-skills']
TASKS=['shock-analysis-demand','shock-analysis-supply','reserves-at-risk-calc','powerlifting-coef-calc','xlsx-recover-data','invoice-fraud-detection','pdf-excel-diff','jpg-ocr-stat']
def load(p):return json.loads(p.read_text())
def csvwrite(p,rows):
 if not rows:return
 with p.open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def historical():
 records=[]
 for task,skill,version,folder in [('energy-market-pricing','economic-dispatch',6,'energy-market-pricing'),('protein-expression-analysis','xlsx',11,'protein-expression-analysis')]:
  for l in LABELS:
   p=R/'historical_inputs'/folder/l;r=load(p/'result.json')
   records.append({'task':task,'repeat':1,'condition':l,'historical_reused':True,'score':r['score'],'runner_limit':False,'infrastructure_failure':False,'condition_valid':True,'tokens':r['tokens'],'solver_elapsed_sec':r['elapsed_sec'],'end_to_end_elapsed_sec':None,'cost_usd':'unknown','skill_sha256':r.get('skill_sha256'),'exception':None,'folder':str(p),'tokens_comparable':True,'status':'scored','skill_family':skill,'version':version})
 return records

def bootstrap(values):
 if len(values)<5:return None
 v=np.asarray(values);rng=np.random.default_rng(20261112);m=v[rng.integers(0,len(v),(10000,len(v)))].mean(axis=1)
 return {'mean_percent':float(v.mean()),'ci95':[float(x) for x in np.quantile(m,[.025,.975])],'n_tasks':len(v),'unit':'task','resamples':10000,'seed':20261112}
def mean(v):return statistics.mean(v) if v else None
def main(out):
 out.mkdir(exist_ok=False)
 records=[load(p) for p in sorted((R/'launch-03/runs').glob('*/repeat-*/*/NIGHT_RECORD.json'))]
 records += [load(p) for p in sorted((R/'launch-03/historical_records').glob('*.json'))]+historical()
 for r in records:
  r.setdefault('skill_family','xlsx');r.setdefault('version',11)
 assert len({(x['task'],x['repeat'],x['condition']) for x in records})==len(records)
 tasks=TASKS+['energy-market-pricing','protein-expression-analysis'];groups=[];comps=[];statuses=[]
 for t in tasks:
  rr=[x for x in records if x['task']==t];stats={}
  invalid=any(sum(x['infrastructure_failure'] for x in rr if x['condition']==l)>=2 for l in LABELS)
  all_present=all(any(x['condition']==l for x in rr) for l in LABELS)
  any_limit=any(x['runner_limit'] for x in rr)
  any_infra=any(x['infrastructure_failure'] for x in rr)
  status='invalid_infrastructure' if invalid else ('complete_with_runner_limit' if all_present and any_limit else ('complete_with_infrastructure_gap' if all_present and any_infra else ('complete' if all_present else ('partial' if rr else 'not_started'))))
  statuses.append({'task':t,'skill_family':rr[0]['skill_family'] if rr else 'xlsx','version':rr[0]['version'] if rr else 11,'status':status,'new_attempts':sum(not x['historical_reused'] for x in rr),'historical_attempts_reused':sum(x['historical_reused'] for x in rr),'runner_limit_count':sum(x['runner_limit'] for x in rr),'infrastructure_failure_count':sum(x['infrastructure_failure'] for x in rr),'all_groups_present':all_present,'historical_note':'Prior partial attempts reused; frozen only added tonight' if t=='shock-analysis-demand' else ('Initially held-out for round11; used in selection after round12, not independent of that later selection' if t=='protein-expression-analysis' else ('Earlier held-out result, no new runs tonight' if t=='energy-market-pricing' else 'Prespecified frozen-version test'))})
  for l in LABELS:
   a=[x for x in rr if x['condition']==l]
   if not a:continue
   scored=[x for x in a if x['status']=='scored' and not x['infrastructure_failure']]
   completed_tokens=[x['tokens']['total_tokens'] for x in scored if x.get('tokens') and x['tokens'].get('total_tokens') is not None]
   raw_rewards=[x['score'].get('strict') for x in scored]
   policy_a=[0 if x['runner_limit'] else x['score'].get('strict') for x in a if not x['infrastructure_failure']]
   seconds=[x['solver_elapsed_sec'] for x in scored if x.get('solver_elapsed_sec') is not None]
   stat={'task':t,'skill_family':a[0]['skill_family'],'version':a[0]['version'],'condition':l,'n_attempts':len(a),'n_scored':len(scored),'runner_limit_count':sum(x['runner_limit'] for x in a),'infrastructure_failure_count':sum(x['infrastructure_failure'] for x in a),'strict_reward_values':raw_rewards,'strict_reward_mean':mean(raw_rewards),'policy_a_failure_reward_mean':mean(policy_a),'policy_a_reward_values':policy_a,'tokens_completed_values':completed_tokens,'tokens_mean':mean(completed_tokens),'tokens_sd_sample':statistics.stdev(completed_tokens) if len(completed_tokens)>=2 else None,'tokens_all_attempts_values':[(x.get('tokens') or {}).get('total_tokens') for x in a],'solver_completed_seconds_values':seconds,'solver_seconds_mean':mean(seconds),'tool_calls_all_values':[(x.get('tokens') or {}).get('tool_calls') for x in a],'cost_usd':'unknown','task_invalid':invalid}
   groups.append(stat);stats[l]=stat
  if all_present and not invalid and all(stats.get(l,{}).get('policy_a_failure_reward_mean') is not None for l in LABELS):
   b=stats[LABELS[1]];c=stats[LABELS[2]];delta=c['policy_a_failure_reward_mean']-b['policy_a_failure_reward_mean']
   token_ok=not any_limit and not any_infra and b['tokens_mean'] is not None and c['tokens_mean'] is not None
   td=c['tokens_mean']-b['tokens_mean'] if token_ok else None;sd=b['tokens_sd_sample'] if token_ok else None
   direction='unknown_variation' if td is not None and sd is None else ('unavailable' if td is None else ('within_variation' if abs(td)<=sd else ('decrease' if td<0 else 'increase')))
   comps.append({'task':t,'skill_family':stats[LABELS[2]]['skill_family'],'version':stats[LABELS[2]]['version'],'policy_a_strict_reward_delta':delta,'policy_b_included':not any_limit and not any_infra,'policy_b_strict_reward_delta':delta if not any_limit and not any_infra else None,'quality_direction':'tie' if abs(delta)<1e-12 else ('increase' if delta>0 else 'decrease'),'token_comparable':token_ok,'token_delta':td,'token_delta_percent':100*td/b['tokens_mean'] if token_ok else None,'original_tokens_sample_sd':sd,'exceeds_original_sd':abs(td)>sd if td is not None and sd is not None else None,'token_direction':direction,'observed_token_direction':None if td is None else ('decrease' if td<0 else ('increase' if td>0 else 'tie')),'baseline_tokens_mean':b['tokens_mean'] if token_ok else None,'candidate_tokens_mean':c['tokens_mean'] if token_ok else None,'n_original':b['n_attempts'],'n_frozen':c['n_attempts']})
 policies={}
 for name,items in [('a_count_limits_as_failure',comps),('b_exclude_tasks_with_any_limit',[x for x in comps if x['policy_b_included']])]:
  q=dict(collections.Counter(x['quality_direction'] for x in items));tok=[x for x in items if x['token_comparable']];tc=dict(collections.Counter(x['token_direction'] for x in tok));obs=dict(collections.Counter(x['observed_token_direction'] for x in tok))
  policies[name]={'n_compared_tasks':len(items),'tasks':[x['task'] for x in items],'quality_counts':q,'tokens_counts':tc,'observed_token_directions':obs,'n_token_comparable_tasks':len(tok),'bootstrap_tokens_percent':bootstrap([x['token_delta_percent'] for x in tok]),'can_claim_accuracy_improved':q.get('increase',0)>0 and q.get('decrease',0)==0,'can_claim_tokens_reduced':tc.get('decrease',0)>=tc.get('increase',0)+2}
 a=policies['a_count_limits_as_failure'];b=policies['b_exclude_tasks_with_any_limit']
 quality=a['can_claim_accuracy_improved'] and b['can_claim_accuracy_improved'];eff=a['can_claim_tokens_reduced'] and b['can_claim_tokens_reduced']
 # New-task conclusions must hold under both explicitly requested policies.
 fresh_summary={'complete_valid_tasks':b['n_compared_tasks'],'quality_counts':b['quality_counts'],'tokens_counts':b['tokens_counts'],'can_claim_accuracy_improved':quality,'can_claim_tokens_reduced':eff,'permitted_wording':'提高正确率' if quality else ('降低 token 消耗' if eff else '效果因任务而异'),'policies':policies,'includes_two_prior_heldout_results':True,'newly_completed_eight_task_comparisons':sum(x['task'] in TASKS for x in comps),'versions_are_skill_specific':True}
 pending=W/'01_任务结果/2026-11-11_skillsbench_cloud_serial/xlsx-family/native-proot-v2/evolution/round-11/evolution/pending.json';gate=load(pending)['suggestion_content']['rubric_totals']
 gate_comparison={'prediction_type':'model-estimated efficiency rubric, not predicted task tokens','before':gate['before']['efficiency'],'after':gate['after']['efficiency'],'predicted_token_reduction_percent':'unknown','xlsx_heldout_observed_token_changes':{x['task']:x['token_delta_percent'] for x in comps if x['skill_family']=='xlsx'},'economic_dispatch_round6_reported_separately':True}
 result={'attempts':records,'task_statuses':statuses,'group_statistics':groups,'task_comparisons':comps,'fresh_summary':fresh_summary,'gate_vs_execution':gate_comparison,'cost_usd':'unknown','new_evolution_calls':0,'solver_model_label':'gpt-6.1-sol','n_new_solver_attempts':sum(not x['historical_reused'] for x in records),'counts':{'all_recorded_attempts_including_reused':len(records),'complete_scored_tasks':sum(x['status']=='complete' for x in statuses),'complete_limit_tasks':sum(x['status']=='complete_with_runner_limit' for x in statuses),'infrastructure_invalid_tasks':sum(x['status']=='invalid_infrastructure' for x in statuses)},'protocol':'PREREG_AMENDMENT_01.md','client_failed_launch_excluded':'launch01 no API sessions, launch02 one interrupted superseded baseline; raw evidence retained but not experimental comparisons','model_scope_note':'round11 xlsx evolution and all current solving use gpt-6.1-sol; first historical threejs counterexample evolved with gpt-4.1 and must not be relabelled'}
 with (out/'results.json').open('x') as f:json.dump(result,f,indent=2,ensure_ascii=False)
 csvwrite(out/'task_statuses.csv',statuses);csvwrite(out/'task_comparisons.csv',comps)
 csvwrite(out/'group_statistics.csv',[{k:json.dumps(v) if isinstance(v,list) else v for k,v in x.items()} for x in groups])
 csvwrite(out/'attempts.csv',[{'task':x['task'],'skill':x['skill_family'],'version':x['version'],'condition':x['condition'],'repeat':x['repeat'],'historical_reused':x['historical_reused'],'strict_reward':x['score'].get('strict'),'policy_a_reward':0 if x['runner_limit'] else x['score'].get('strict'),'policy_b_include':next((c['policy_b_included'] for c in comps if c['task']==x['task']),False),'status':x['status'],'passed':x['score'].get('passed'),'failed':x['score'].get('failed'),'skipped':x['score'].get('skipped'),'tokens':(x.get('tokens') or {}).get('total_tokens'),'tokens_comparable':x['tokens_comparable'],'tool_calls':(x.get('tokens') or {}).get('tool_calls'),'solver_seconds':x['solver_elapsed_sec'],'cost_usd':'unknown'} for x in records])
 report=['# 8题广度优先验证 + 2道此前held-out结果','',json.dumps(fresh_summary,ensure_ascii=False),'','注意: runner_limit没有原评分. 仅口径(a)分析时当失败; 口径(b)整题排除. 中止tokens不参与完成运行效率比较. n=1的标准差unknown, 不填0.','', '| Task | Skill/round | Group | n/scored | strict mean | Policy(a) mean | completed tokens mean ± SD |','|---|---|---|---:|---:|---:|---|']
 for x in groups:report.append(f"| {x['task']} | {x['skill_family']}/{x['version']} | {x['condition']} | {x['n_attempts']}/{x['n_scored']} | {x['strict_reward_mean']} | {x['policy_a_failure_reward_mean']} | {x['tokens_mean']} ± {x['tokens_sd_sample']} |")
 report+=['','## 任务状态','| Task | Status | Note |','|---|---|---|']+[f"| {x['task']} | {x['status']} | {x['historical_note']} |" for x in statuses]
 report+=['','## 门控预测与实际执行',json.dumps(gate_comparison,ensure_ascii=False),'','原始轨迹/附件/verifier输出在historical_inputs和launch-03/runs. 上一版启动失败和中断另存, 不作为新题成绩.']
 (out/'REPORT.md').write_text('\n'.join(report))
 print(json.dumps(fresh_summary,ensure_ascii=False))
 assert all(x['score']=={} for x in records if x['runner_limit'])
 assert all(x['token_delta_percent'] is None for x in comps if not x['token_comparable'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();main(Path(a.out).resolve())
