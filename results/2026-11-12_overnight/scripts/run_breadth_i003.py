"""I-003 adapter repair; frozen skill and benchmark unchanged, serial all Profy work."""
import argparse,datetime,fcntl,hashlib,json,re,sys,time,urllib.error
from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parents[1];ROOT=R/'launch-04-i003';STOP=json.loads((R/'I002_TIME_WINDOW.json').read_text())['stop_new_epoch']
sys.path.insert(0,str(R/'native_adapter_i003'))
from study import DockerStudy
LABELS=['no-skills','with-skills','with-CogniLife-skills'];TASKS=['shock-analysis-demand','shock-analysis-supply','reserves-at-risk-calc','powerlifting-coef-calc','xlsx-recover-data','invoice-fraud-detection','pdf-excel-diff','jpg-ocr-stat']
FROZEN='51ca8a2ff044812e60ca830e9951d17219a66c736004edc99729d157f275cf1a';PARENT='9bdc1fee81f3be9cb34ac49f8890c094a3855d3d0236783d10e0ea6df1515e01'
def put(p,j):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(j,f,indent=2,ensure_ascii=False)
def append(n,s):
 with (R/n).open('a') as f:f.write('\n'+datetime.datetime.now(datetime.timezone.utc).isoformat()+' '+s+'\n')
def pending():return [p for p in R.glob('NEW_INSTRUCTION_I-*.json') if int(p.stem.split('I-')[1])>3 and not (R/(p.stem.replace('NEW_INSTRUCTION_','INSTRUCTION_')+'_APPLIED.json')).exists()]
def wait_instructions():
 while pending():
  if time.time()>=STOP:return False
  time.sleep(2)
 return True
class FixedStudy(DockerStudy):
 def grade(self,task,folder):
  row=json.loads((folder/'run_summary.json').read_text())
  if row.get('error') in ['hard_budget_stop','tool_or_turn_cap']:raise RuntimeError('runner_limit: no scoring')
  if time.time()>=STOP:raise RuntimeError('deadline: no new grading calls')
  return super().grade(task,folder)
def main():
 ROOT.mkdir(exist_ok=False);put(ROOT/'CONTROLLER_STARTED.json',{'pid':__import__('os').getpid(),'epoch':time.time(),'instruction':'I-003','adapter':'native_adapter_i003','all_profy_work_serial_lock':True})
 candidate=(R/'frozen_xlsx_round11_SKILL.md').read_text();assert hashlib.sha256(candidate.encode()).hexdigest()==FROZEN
 legacy={}
 for p in (R/'launch-03/runs').glob('*/repeat-*/*/NIGHT_RECORD.json'):
  x=json.loads(p.read_text());legacy[x['task'],x['repeat'],x['condition']]=x
 count=0;reason=None
 for repeat in [1,2,3]:
  for task in TASKS:
   if task=='shock-analysis-demand':continue # old baselines+new frozen r1 retained; no more solves
   directory=ROOT/'runs'/task;directory.mkdir(parents=True,exist_ok=True)
   pins=directory/'APT_PINS.json';expected=directory/'INPUT_HASHES.json'
   old=R/'launch-03/runs'/task
   if (old/'APT_PINS.json').exists() and not pins.exists():put(pins,json.loads((old/'APT_PINS.json').read_text()))
   if (old/'INPUT_HASHES.json').exists() and not expected.exists():put(expected,json.loads((old/'INPUT_HASHES.json').read_text()))
   for label in LABELS:
    if not wait_instructions():reason='deadline_pending_instruction';break
    previous=legacy.get((task,repeat,label));rerun_setup=False
    if previous:
     folder=Path(previous['folder']);events=folder/'events.jsonl'
     rerun_setup=previous['status']=='infrastructure_failure' and events.exists() and 'Declared pip pin not active' in events.read_text()
     if not rerun_setup:
      put(ROOT/'reused'/task/f'repeat-{repeat}'/(label+'.json'),{'original_record':str(folder/'NIGHT_RECORD.json'),'sha256':hashlib.sha256((folder/'NIGHT_RECORD.json').read_bytes()).hexdigest(),'reason':'preserve previous scored/limit/unscored trace; no repeat solving'})
      continue
    if STOP-time.time()<1900:reason='insufficient_time_for_standard_budget';break
    if sum(p.stat().st_size for p in R.rglob('*') if p.is_file())>500_000_000:reason='local500MB_guard';break
    out=directory/f'repeat-{repeat}';out.mkdir(exist_ok=True);folder=out/label
    args=argparse.Namespace(workspace=str(W),out=str(out),task=task,target_skill='xlsx',expected_parent_md_sha=PARENT,keys_file='/Users/mac/Desktop/obsidian files/Profy related keys.md',allow_paid=True,native_file_runtime=True,hard_timeout_sec=1600,native_package_versions=str(pins) if pins.exists() else None,expected_input_hashes=str(expected) if expected.exists() else None)
    began=time.time();exc_text=None;row=None
    with (R/'PROFY_SERIAL.lock').open('a') as lock:
     fcntl.flock(lock,fcntl.LOCK_EX)
     try:
      study=FixedStudy(args);api=study.transport.api
      def checked(*a,**kw):
       try:return api(*a,**kw)
       except urllib.error.HTTPError as e:raise RuntimeError('HTTP Error '+str(e.code)+': '+study.transport.scrub(e.read(2000).decode(errors='replace'))) from None
      study.transport.api=checked
      row=study.solve(label,task,candidate if label==LABELS[2] else None,label==LABELS[0])
     except Exception as e:
      exc_text=type(e).__name__+': '+str(e)
      row=json.loads((folder/'run_summary.json').read_text()) if (folder/'run_summary.json').exists() else {'tokens':None,'completed':False,'error':type(e).__name__}
      if (folder/'ORIGINAL_SCORE.json').exists():row['score']=json.loads((folder/'ORIGINAL_SCORE.json').read_text())
    score=row.get('score') or {};limit=row.get('error') in ['hard_budget_stop','tool_or_turn_cap'];valid=not row.get('external_skill_tools_observed') and (label==LABELS[0] or row.get('target_skill_read_verified') is True)
    infra=bool(not limit and (exc_text or row.get('error') or score.get('infrastructure_error') or not row.get('completed') or 'original_reward' not in score or not valid))
    if limit:score={}
    record={'task':task,'repeat':repeat,'condition':label,'historical_reused':False,'score':score,'runner_limit':limit,'infrastructure_failure':infra,'condition_valid':valid,'tokens':row.get('tokens'),'solver_elapsed_sec':row.get('elapsed_sec'),'end_to_end_elapsed_sec':time.time()-began,'cost_usd':'unknown','skill_sha256':row.get('skill_sha256'),'exception':exc_text,'folder':str(folder),'tokens_comparable':not limit and not infra,'status':'runner_limit' if limit else ('infrastructure_failure' if infra else 'scored'),'adapter_instruction':'I-003','completed_epoch':time.time(),'supersedes_setup_attempt':previous['folder'] if rerun_setup else None}
    put(folder/'NIGHT_RECORD.json',record);count+=1
    receipt=score.get('dependency_receipt') or {}
    if receipt.get('apt_packages') and not pins.exists():put(pins,receipt['apt_packages'])
    if (folder/'native_input_hashes.json').exists() and not expected.exists():put(expected,json.loads((folder/'native_input_hashes.json').read_text()))
    print('I003_ATTEMPT',task,repeat,label,record['status'],'reward',score.get('original_reward'),flush=True)
    append('PROGRESS.md',json.dumps({k:record[k] for k in ['task','repeat','condition','status','cost_usd','completed_epoch','adapter_instruction']})+'; strict='+str(score.get('strict'))+'; total_tokens='+str((row.get('tokens') or {}).get('total_tokens')))
    text=exc_text or ''
    if (folder/'exception.json').exists():text+=' '+(folder/'exception.json').read_text()
    if (folder/'events.jsonl').exists():
     for s in (folder/'events.jsonl').read_text().splitlines():
      e=json.loads(s)
      if e.get('type')=='run.failed':text+=' '+json.dumps(e)
    if re.search(r'insufficient.?balance|insufficient.?credit|quota.exceeded|余额不足|额度耗尽|payment.required|HTTP Error 402',text,re.I):reason='api_quota_exhausted';break
    # Let the independent watcher read instructions and publish before next call;
    # any new numbered instruction blocks new solves until applied by the agent.
    time.sleep(3)
   append('PROGRESS.md',f'I003 task pass finished: {task}, repeat{repeat}, Profy USDunknown; fixed order retained.')
   if reason:break
  if reason:break
 put(ROOT/'RUNNER_STOPPED.json',{'reason':reason or 'all_three_passes_processed','epoch':time.time(),'new_solver_attempts':count,'instruction':'I-003'})
 print('I003_CONTROLLER_STOPPED',reason or 'all_three_passes_processed',count,flush=True)
if __name__=='__main__':main()
