"""One bounded retry of the registered unfinished reserve setup, capture403 body."""
import argparse,fcntl,hashlib,json,sys,time,urllib.error,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parents[1]
sys.path.insert(0,str(R));from run_breadth_i003 import FixedStudy

def main():
 root=R/'launch-05-profy-recovery';out=root/'runs/reserves-at-risk-calc/repeat-1';out.mkdir(parents=True,exist_ok=False);folder=out/'no-skills';folder.mkdir()
 real_open=urllib.request.urlopen;counter=0
 def capture(request,*a,**kw):
  nonlocal counter
  try:return real_open(request,*a,**kw)
  except urllib.error.HTTPError as e:
   if getattr(request,'full_url','')=='https://api.profy.cn/v1/agents/run':
    counter+=1;raw=e.read();body=raw.decode(errors='replace');body=__import__('re').sub(r'\bsk-(?:pro|or)-[A-Za-z0-9._-]+','[REDACTED]',body)
    with (root/f'HTTP_ERROR_RESPONSE_{counter}.json').open('x') as f:json.dump({'http_status':e.code,'body':body,'epoch':time.time(),'purpose':'one bounded original-plan reserve recovery after orphaned setup interruption'},f,indent=2)
   raise
 urllib.request.urlopen=capture
 args=argparse.Namespace(workspace=str(W),out=str(out),task='reserves-at-risk-calc',target_skill='xlsx',expected_parent_md_sha='9bdc1fee81f3be9cb34ac49f8890c094a3855d3d0236783d10e0ea6df1515e01',keys_file='/Users/mac/Desktop/obsidian files/Profy related keys.md',allow_paid=True,native_file_runtime=True,hard_timeout_sec=1600,native_package_versions=None,expected_input_hashes=None)
 began=time.time();row=None;error=None
 with (R/'PROFY_SERIAL.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  try:row=FixedStudy(args).solve('no-skills','reserves-at-risk-calc',None,True)
  except Exception as exc:
   error=type(exc).__name__+': '+str(exc)
   row=json.loads((folder/'run_summary.json').read_text()) if (folder/'run_summary.json').exists() else {}
 score=row.get('score') or {};limit=row.get('error') in ['hard_budget_stop','tool_or_turn_cap'];infra=bool(not limit and (error or not row.get('completed') or 'original_reward' not in score))
 result={'task':'reserves-at-risk-calc','repeat':1,'condition':'no-skills','historical_reused':False,'score':{} if limit else score,'runner_limit':limit,'infrastructure_failure':infra,'condition_valid':not infra,'tokens':row.get('tokens'),'solver_elapsed_sec':row.get('elapsed_sec'),'end_to_end_elapsed_sec':time.time()-began,'cost_usd':'unknown','skill_sha256':None,'exception':error,'folder':str(folder),'tokens_comparable':not infra and not limit,'status':'runner_limit' if limit else ('infrastructure_failure' if infra else 'scored'),'adapter_instruction':'I-003','supersedes_setup_attempt':str(R/'launch-04-i003/runs/reserves-at-risk-calc/repeat-1/no-skills'),'completed_epoch':time.time(),'single_bounded_transport_recovery':True}
 with (folder/'NIGHT_RECORD.json').open('x') as f:json.dump(result,f,indent=2)
 with (root/'RECOVERY_FINISHED.json').open('x') as f:json.dump({'status':result['status'],'error':error,'http_error_bodies':counter,'no_further_automatic_retries':True,'epoch':time.time()},f,indent=2)
 with (R/'PROGRESS.md').open('a') as f:f.write('\nOne bounded registered reserve recovery after orphaned setup cancellation: '+json.dumps({'status':result['status'],'strict':score.get('strict'),'http_error_bodies':counter,'cost_usd':'unknown'})+'; no further retry.\n')
 print('BOUNDED_RECOVERY_FINISHED',json.dumps({'status':result['status'],'error':error,'http_error_bodies':counter,'strict':score.get('strict')}),flush=True)
if __name__=='__main__':main()
