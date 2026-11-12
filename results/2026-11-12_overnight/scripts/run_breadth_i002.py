"""User-amended eight-task, serial breadth-first frozen xlsx evaluation."""
import argparse,datetime,hashlib,json,re,sys,time,urllib.error
from pathlib import Path
REPORT=Path(__file__).resolve().parent;ROOT=REPORT/'launch-03';W=REPORT.parents[1]
sys.path.insert(0,str(W/'04_项目数据与代码/辅助代码/skillsbench_cloud_runner_20261111'))
from study import DockerStudy
START=json.loads((ROOT/'START.json').read_text());STOP=json.loads((REPORT/'I002_TIME_WINDOW.json').read_text())['stop_new_epoch']
LABELS=['no-skills','with-skills','with-CogniLife-skills']
FROZEN='51ca8a2ff044812e60ca830e9951d17219a66c736004edc99729d157f275cf1a';PARENT='9bdc1fee81f3be9cb34ac49f8890c094a3855d3d0236783d10e0ea6df1515e01'
def put(path,obj):
 with Path(path).open('x') as f:json.dump(obj,f,indent=2,ensure_ascii=False)
def append(name,text):
 with (REPORT/name).open('a') as f:f.write('\n'+datetime.datetime.now(datetime.timezone.utc).isoformat()+' '+text+'\n')
def quota(text):return bool(re.search(r'insufficient.?balance|insufficient.?credit|quota.exceeded|余额不足|额度耗尽|payment.required|credit.{0,20}exhaust|HTTP Error 402',text,re.I))
class NightStudy(DockerStudy):
 def grade(self,task,folder):
  r=json.loads((folder/'run_summary.json').read_text())
  if r.get('error') in ['tool_or_turn_cap','hard_budget_stop']:raise RuntimeError('runner_limit: no scoring allowed by amendment')
  if time.time()>=STOP:raise RuntimeError('deadline: no new grading invocation')
  return super().grade(task,folder)
def old_records():
 p=REPORT/'historical_inputs/shock-analysis-demand';out=ROOT/'historical_records';out.mkdir(exist_ok=True)
 for label in LABELS[:2]:
  f=p/label;row=json.loads((f/('result.json' if (f/'result.json').exists() else 'run_summary.json')).read_text());score=row.get('score') or {}
  if (f/'ORIGINAL_SCORE.json').exists():score=json.loads((f/'ORIGINAL_SCORE.json').read_text())
  limit=label=='with-skills';record={'task':'shock-analysis-demand','repeat':1,'condition':label,'historical_reused':True,'score':score if not limit else {},'runner_limit':limit,'infrastructure_failure':False,'condition_valid':True,'tokens':row.get('tokens'),'solver_elapsed_sec':row.get('elapsed_sec'),'end_to_end_elapsed_sec':None,'cost_usd':'unknown','skill_sha256':row.get('skill_sha256'),'exception':row.get('error'),'folder':str(f),'tokens_comparable':not limit,'status':'runner_limit' if limit else 'scored','historical_note':'Saved summary says hard_budget_stop; original usage has25 events, exceeding24-turn runner threshold.' if limit else 'Original reward0 preserved; receipt/stdout test-count discrepancy retained.'}
  
  if not (out/(label+'.json')).exists():put(out/(label+'.json'),record)
def main():
 candidate=(ROOT/'frozen_xlsx_round11_SKILL.md').read_text();assert hashlib.sha256(candidate.encode()).hexdigest()==FROZEN
 old_records();items=json.loads((ROOT/'SELECTION_PREFLIGHT.json').read_text());last_cost=time.time();count=0;stop_reason=None
 for repeat in [1,2,3]:
  for item in items:
   task=item['task']
   if repeat==2 and task=='shock-analysis-demand':continue
   directory=ROOT/'runs'/task;directory.mkdir(parents=True,exist_ok=True)
   pins=directory/'APT_PINS.json';expected=directory/'INPUT_HASHES.json'
   if task=='shock-analysis-demand' and not pins.exists():
    old=REPORT/'historical_inputs/shock-analysis-demand';put(pins,json.loads((old/'FROZEN_APT_PACKAGES.json').read_text()))
    if (old/'no-skills/native_input_hashes.json').exists():put(expected,json.loads((old/'no-skills/native_input_hashes.json').read_text()))
   labels=[LABELS[2]] if task=='shock-analysis-demand' else LABELS
   for label in labels:
    if (directory/f'repeat-{repeat}'/label/'NIGHT_RECORD.json').exists():continue
    if (directory/f'repeat-{repeat}'/label/'started.json').exists():
     stop_reason='existing_incomplete_attempt_requires_inspection';break
    if STOP-time.time()<1900:stop_reason='insufficient_time_for_standard_budget_attempt';break
    if sum(p.stat().st_size for p in REPORT.rglob('*') if p.is_file())>500_000_000:stop_reason='500MB_local_evidence_guard';break
    out=directory/f'repeat-{repeat}';out.mkdir(exist_ok=True);f=out/label
    args=argparse.Namespace(workspace=str(W),out=str(out),task=task,target_skill='xlsx',expected_parent_md_sha=PARENT,keys_file='/Users/mac/Desktop/obsidian files/Profy related keys.md',allow_paid=True,native_file_runtime=True,hard_timeout_sec=1600,native_package_versions=str(pins) if pins.exists() else None,expected_input_hashes=str(expected) if expected.exists() else None)
    began=time.time();exception=None;row=None
    try:
     study=NightStudy(args)
     # Report explicit quota exhaustion; never top up or choose another service.
     api=study.transport.api
     def checked_api(*a,**kw):
      try:return api(*a,**kw)
      except urllib.error.HTTPError as exc:
       detail=study.transport.scrub(exc.read(2000).decode(errors='replace'))
       raise RuntimeError('HTTP Error '+str(exc.code)+': '+detail) from None
     study.transport.api=checked_api
     row=study.solve(label,task,candidate if label==LABELS[2] else None,label==LABELS[0])
    except Exception as exc:
     exception=type(exc).__name__+': '+str(exc)
     row=json.loads((f/'run_summary.json').read_text()) if (f/'run_summary.json').exists() else {'label':label,'task':task,'tokens':None,'completed':False,'error':type(exc).__name__}
     if (f/'ORIGINAL_SCORE.json').exists():row['score']=json.loads((f/'ORIGINAL_SCORE.json').read_text())
    limit=row.get('error') in ['tool_or_turn_cap','hard_budget_stop'];score=row.get('score') or {}
    condition=not row.get('external_skill_tools_observed') and (label==LABELS[0] or row.get('target_skill_read_verified') is True)
    infra=bool(not limit and (exception or row.get('error') or score.get('infrastructure_error') or not row.get('completed') or 'original_reward' not in score or not condition))
    if limit:score={} # No score invented. Alternative failure-policy is analysis only.
    record={'task':task,'repeat':repeat,'condition':label,'historical_reused':False,'score':score,'runner_limit':limit,'infrastructure_failure':infra,'condition_valid':condition,'tokens':row.get('tokens'),'solver_elapsed_sec':row.get('elapsed_sec'),'end_to_end_elapsed_sec':time.time()-began,'cost_usd':'unknown','skill_sha256':row.get('skill_sha256'),'exception':exception,'folder':str(f),'tokens_comparable':not limit and not infra,'status':'runner_limit' if limit else ('infrastructure_failure' if infra else 'scored')}
    f.mkdir(parents=True,exist_ok=True);put(f/'NIGHT_RECORD.json',record);count+=1
    receipt=score.get('dependency_receipt') or {}
    if receipt.get('apt_packages') and not pins.exists():put(pins,receipt['apt_packages'])
    if (f/'native_input_hashes.json').exists() and not expected.exists():put(expected,json.loads((f/'native_input_hashes.json').read_text()))
    print('NIGHT_ATTEMPT',task,repeat,label,'reward',score.get('original_reward'),'status',record['status'],flush=True)
    text=exception or ''
    if (f/'exception.json').exists():text+=' '+(f/'exception.json').read_text()
    if (f/'events.jsonl').exists():
     # Search only failure events; ordinary financial tasks can mention balances.
     for line in (f/'events.jsonl').read_text().splitlines():
      e=json.loads(line)
      if e.get('type')=='run.failed':text+=' '+json.dumps(e)
    if quota(text):stop_reason='api_quota_exhausted';append('DECISIONS.md','API quota/balance exhaustion detected; all new requests stopped, no recharge.');break
    if time.time()-last_cost>=7200:append('PROGRESS.md',f'{count} newsolver attempts, Profy cost unknown, OpenRouter newcalls0.');last_cost=time.time()
   records=[json.loads(p.read_text()) for p in directory.glob('repeat-*/*/NIGHT_RECORD.json')]
   append('PROGRESS.md',f'Pass{repeat} task {task}: '+json.dumps([{'condition':r['condition'],'repeat':r['repeat'],'status':r['status'],'reward':r['score'].get('original_reward'),'tokens':(r.get('tokens') or {}).get('total_tokens')} for r in records],ensure_ascii=False)+'; Profy USD unknown; OpenRouter newcalls0.')
   print('TASK_PASS_FINISHED',repeat,task,flush=True)
   if stop_reason:break
  if stop_reason:break
 append('PROGRESS.md',f'I002 continuation stopped: {stop_reason or "both_passes_processed"}; new solver attempts{count}; Profy cost unknown; OpenRouter newcalls0.')
 put(ROOT/'RUNNER_STOPPED_I002.json',{'epoch':time.time(),'new_solver_attempts':count,'reason':stop_reason or 'both_passes_processed','new_openrouter_calls':0})
if __name__=='__main__':main()
