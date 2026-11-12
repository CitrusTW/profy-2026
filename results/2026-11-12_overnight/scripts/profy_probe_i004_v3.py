"""I004: one next-planned reserve/A attempt each30min;403 is not a scored run."""
import argparse,fcntl,hashlib,json,re,sys,time,urllib.error,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parents[1];sys.path.insert(0,str(R));sys.path.insert(0,str(R/'native_adapter_i005'));from study import DockerStudy
class FixedStudy(DockerStudy):
 def grade(self,task,folder):
  row=json.loads((folder/'run_summary.json').read_text())
  if row.get('error') in ['hard_budget_stop','tool_or_turn_cap']:raise RuntimeError('runner_limit: no scoring')
  if time.time()>=STOP:raise RuntimeError('deadline: no new grading calls')
  return super().grade(task,folder)
STOP=json.loads((R/'I002_TIME_WINDOW.json').read_text())['stop_new_epoch']
def put(p,j):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(j,f,indent=2,ensure_ascii=False)
def pending():return [p for p in R.glob('NEW_INSTRUCTION_I-*.json') if not (R/(p.stem.replace('NEW_INSTRUCTION_','INSTRUCTION_')+'_APPLIED.json')).exists()]
def sync(reason):
 import coordination_sync_v10 as c
 with (R/'coordination_sync.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);c.sync(reason)
def main():
 assert (R/'INSTRUCTION_I-004_APPLIED.json').exists();base=R/'profy_i004_probes';base.mkdir(exist_ok=True);last=max((json.loads(p.read_text())['started_epoch'] for p in base.glob('*/PROBE_STATUS.json')),default=None)
 real_open=urllib.request.urlopen
 while STOP-time.time()>=1900:
  if last is not None and time.time()-last<1800:time.sleep(min(10,1800-(time.time()-last)));continue
  if pending():time.sleep(2);continue
  last=time.time();root=base/str(int(last));out=root/'runs/reserves-at-risk-calc/repeat-1';out.mkdir(parents=True,exist_ok=False);folder=out/'no-skills';http=[]
  def capture(request,*a,**kw):
   try:return real_open(request,*a,**kw)
   except urllib.error.HTTPError as e:
    if getattr(request,'full_url','')=='https://api.profy.cn/v1/agents/run':
     body=re.sub(r'\bsk-(?:pro|or)-[A-Za-z0-9._-]+','[REDACTED]',e.read().decode(errors='replace'));http.append({'http_status':e.code,'body':body,'epoch':time.time()})
     if not (root/'HTTP_ERROR_RESPONSE.json').exists():put(root/'HTTP_ERROR_RESPONSE.json',http[-1])
    raise
  urllib.request.urlopen=capture
  old=R/'launch-03/runs/reserves-at-risk-calc';pins=old/'APT_PINS.json';expected=old/'INPUT_HASHES.json'
  args=argparse.Namespace(workspace=str(W),out=str(out),task='reserves-at-risk-calc',target_skill='xlsx',expected_parent_md_sha='9bdc1fee81f3be9cb34ac49f8890c094a3855d3d0236783d10e0ea6df1515e01',keys_file='/Users/mac/Desktop/obsidian files/Profy related keys.md',allow_paid=True,native_file_runtime=True,hard_timeout_sec=1600,native_package_versions=str(pins) if pins.exists() else None,expected_input_hashes=str(expected) if expected.exists() else None)
  began=time.time();row=None;error=None
  with (R/'PROFY_SERIAL.lock').open('a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX)
   try:row=FixedStudy(args).solve('no-skills','reserves-at-risk-calc',None,True)
   except Exception as exc:
    error=type(exc).__name__+': '+str(exc);row=json.loads((folder/'run_summary.json').read_text()) if (folder/'run_summary.json').exists() else {}
  urllib.request.urlopen=real_open
  tokens=row.get('tokens') or {};rejected=any(x['http_status']==403 for x in http) and not tokens.get('llm_turns')
  status={'instruction':'I-004','started_epoch':last,'completed_epoch':time.time(),'task':'reserves-at-risk-calc','condition':'no-skills','repeat':1,'http_errors':http,'error':error,'no_usage_events':not tokens.get('llm_turns'),'scientific_run':not rejected,'result_folder':str(folder),'cost_usd':'unknown','status':'403_rejected_not_a_run' if rejected else 'accepted_or_non403_requires_review','next_probe_not_before_epoch':last+1800}
  put(root/'PROBE_STATUS.json',status)
  with (R/'PROGRESS.md').open('a') as f:f.write('\nI004 original-order next-run probe: '+json.dumps(status,ensure_ascii=False)+'\n')
  print('I004_PROBE',json.dumps(status,ensure_ascii=False),flush=True)
  if not rejected:
   if not any(x['http_status']==402 for x in http):put(R/'PROFY_RECOVERED_I004.json',{'epoch':time.time(),'probe':str(root),'status':'API no longer403; inspect saved original attempt before resuming','row_saved':(folder/'run_summary.json').exists()})
   put(root/'ACCEPTED_RESULT.json',row)
   sync('I004-probe-non403-inspect-before-continuation');break
  sync('I004-probe403-not-a-run-no-change-to-model-or-key')
  if sum(p.stat().st_size for p in R.rglob('*') if p.is_file())>500000000:put(base/'STOPPED.json',{'reason':'500MB_local_guard','epoch':time.time()});break
 else:put(base/'STOPPED.json',{'reason':'deadline_reserve_required_for_standard_run','epoch':time.time()})
if __name__=='__main__':main()
