"""Separate client reservations, API rejection, started model work and scored trials."""
import argparse,csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def main(out):
 out.mkdir(exist_ok=False);rows=[]
 paths=[p for phase in ['launch-03','launch-04-i003','launch-05-profy-recovery'] for p in (R/phase/'runs').glob('*/repeat-*/*/NIGHT_RECORD.json')]
 for p in sorted(paths):
  x=read(p);folder=p.parent;events=folder/'events.jsonl';text=(events.read_text() if events.exists() else '')+((folder/'exception.json').read_text() if (folder/'exception.json').exists() else '');tokens=x.get('tokens') or {};turns=tokens.get('llm_turns');started=turns>0 if turns is not None else None
  rejected=started is False and ('HTTP Error 403' in text or 'Expert is not published' in text)
  receipts=list(folder.parents[3].glob('HTTP_ERROR_RESPONSE*.json')) if len(folder.parents)>3 else []
  if started is False and any(read(y).get('http_status')==403 for y in receipts):rejected=True
  rows.append({'task':x['task'],'condition':x['condition'],'repeat':x['repeat'],'client_attempt_id':str(p.relative_to(R)),'record_type':'original_attempt','bookkeeping_status':x['status'],'confirmed_model_usage_events':turns,'model_work_started':started,'api403_rejected_before_model':rejected,'score_available_original':bool(x.get('score')),'strict_reward_original':(x.get('score') or {}).get('strict'),'tokens_observed_if_model_work':tokens.get('total_tokens') if started else None,'runner_limit':x['runner_limit'],'raw_record_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'note':'Raw zero usage counters are not a measured completed-run token consumption; failures are not scores.'})
 for p in sorted((R/'profy_i004_probes').glob('*/PROBE_STATUS.json')):
  x=read(p);rows.append({'task':x['task'],'condition':x['condition'],'repeat':x['repeat'],'client_attempt_id':str(p.relative_to(R)),'record_type':'I004_probe','bookkeeping_status':x['status'],'confirmed_model_usage_events':0 if x['no_usage_events'] else None,'model_work_started':not x['no_usage_events'],'api403_rejected_before_model':x['status']=='403_rejected_not_a_run','score_available_original':False,'strict_reward_original':None,'tokens_observed_if_model_work':None,'runner_limit':False,'raw_record_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'note':'I004 explicitly excludes403 rejection from scientific-run counts; raw request/session evidence remains local.'})
 result={'client_attempt_records':len(rows),'confirmed_model_started_records':sum(x['model_work_started'] is True for x in rows),'confirmed_api403_no_model_records':sum(x['api403_rejected_before_model'] for x in rows),'score_bearing_original_records':sum(x['score_available_original'] for x in rows),'rows':rows,'scope':'Original new attempts/probes only. Effective supplemented scores and historical reused trials remain in the main statistical results. No scientific score is recalculated here.','unknown_semantics':'JSON null and human-readable unknown; zero recorded usage events do not establish a billed cost or a completed solve.'}
 with (out/'results.json').open('x') as f:json.dump(result,f,indent=2)
 with (out/'client_and_model_work.csv').open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows([{k:'unknown' if v is None else v for k,v in x.items()} for x in rows])
 assert all(x['tokens_observed_if_model_work'] is None for x in rows if x['api403_rejected_before_model'])
 print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();main(Path(a.out))
