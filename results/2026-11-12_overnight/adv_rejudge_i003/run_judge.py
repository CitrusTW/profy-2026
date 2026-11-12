"""I-003: hash-bound rejudging, one frozen Claude model, no answer generation."""
import argparse,datetime,decimal,hashlib,importlib.util,json,re,time,urllib.request,urllib.error
from pathlib import Path
R=Path(__file__).resolve().parent;NIGHT=R.parent;W=NIGHT.parents[1];B=W/'04_项目数据与代码/Profy-main/knowledge/benchmarks/profybench-v1'
MODEL='anthropic/claude-opus-5.5';D=decimal.Decimal;BUDGET=D('15')
def sha(b):return hashlib.sha256(b).hexdigest()
def put(p,j):
 with p.open('x') as f:json.dump(j,f,ensure_ascii=False,indent=2)
def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def parse(s,kind):
 text=s.strip();m=re.fullmatch(r'```(?:json)?\s*\n?(.*?)\n?```',text,re.S|re.I)
 if m:text=m.group(1).strip()
 j=json.loads(text)
 if kind=='rubric':
  dims=['completeness','specificity','actionability','coherence','safety_boundary','evidence_grounding','uncertainty_calibration']
  assert all(type(j['scores'][d]) is int and 1<=j['scores'][d]<=5 for d in dims)
  assert isinstance(j['error_tags'],list) and all(isinstance(x,str) for x in j['error_tags'])
 else:assert j['preference'] in ['A','B','tie']
 assert isinstance(j.get('rationale'),str)
 return j

def main():
 p=argparse.ArgumentParser();p.add_argument('--allow-paid',action='store_true');a=p.parse_args();assert a.allow_paid
 budget=json.loads((NIGHT/'I003_ADV_BUDGET_PLAN.json').read_text());assert budget['model']==MODEL and D(budget['primary_calls_calculated_cost_ceiling_usd'])<=BUDGET
 source=B/'scripts/llm_judge.py';assert sha(source.read_bytes())==budget['prompt_source_sha256']
 spec=importlib.util.spec_from_file_location('original_judge_templates',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 tasks={x['task_id']:x for x in rows(B/'profybench_v0.jsonl') if x['task_family']=='ADV'}
 conditions=['generic_llm_raw','generic_llm_expert_prompt','profy_expert_full'];outputs={c:{x['task_id']:x for x in rows(B/'results'/('outputs_'+c+'.jsonl')) if x['task_id'] in tasks} for c in conditions}
 assert len(tasks)==20 and all(len(v)==20 for v in outputs.values())
 jobs=[]
 for t,task in sorted(tasks.items()):
  for c in conditions:
   text=outputs[c][t]['output_text'];jobs.append({'kind':'rubric','task_id':t,'condition':c,'prompt':m.build_rubric_prompt(task,text),'output_sha256':{c:sha(text.encode())}})
  for baseline in conditions[:2]:
   for order in ['full_A','full_B']:
    ca,cb=(conditions[2],baseline) if order=='full_A' else (baseline,conditions[2]);oa=outputs[ca][t]['output_text'];ob=outputs[cb][t]['output_text']
    jobs.append({'kind':'pairwise','task_id':t,'baseline':baseline,'order':order,'system_a':ca,'system_b':cb,'prompt':m.build_pairwise_prompt(task,oa,ob),'output_sha256':{ca:sha(oa.encode()),cb:sha(ob.encode())},'visible_output_sha256':{ca:sha(oa[:3000].encode()),cb:sha(ob[:3000].encode())},'visible_character_limit':3000})
 rate=D(budget['input_rate_upper_usd_per_token']);out_rate=D(budget['output_rate_usd_per_token']);limit=budget['max_tokens']
 for x,expected in zip(jobs,budget['jobs']):
  assert x['task_id']==expected['task_id'] and x['kind']==expected['kind'] and len(x['prompt'].encode())==expected['prompt_bytes']
  x['calculated_cost_ceiling_usd']=str(D(expected['upper_input_tokens'])*rate+D(limit)*out_rate)
  x['job_id']=x['task_id']+'-'+x['kind']+'-'+(x.get('condition') or x['baseline']+'-'+x['order'])
  x['prompt_sha256']=sha(x['prompt'].encode())
 put(R/'JOBS.json',jobs)
 source_names=['profybench_v0.jsonl','scripts/llm_judge.py']+['results/outputs_'+c+'.jsonl' for c in conditions]
 put(R/'INPUT_PROVENANCE.json',{'source_sha256':{n:sha((B/n).read_bytes()) for n in source_names},'model':MODEL,'new_answers_generated':False,'output_model_labels':{c:sorted({x['model'] for x in v.values()}) for c,v in outputs.items()},'source_folder':str(B)})
 # Credentials remain outside this folder and are never saved in requests.
 key=next(x for x in re.findall(r'\bsk-[A-Za-z0-9._-]+',Path('/Users/mac/Desktop/obsidian files/Profy related keys.md').read_text()) if x.startswith('sk-or-'))
 spent=D('0');known_cost=D('0');unknown_costs=0;valid=0;failed=0;terminal=None
 for i,job in enumerate(jobs):
  remaining=sum(D(x['calculated_cost_ceiling_usd']) for x in jobs[i+1:]);ceiling=D(job['calculated_cost_ceiling_usd']);folder=R/'calls'/job['job_id'];folder.mkdir(parents=True,exist_ok=False)
  for attempt in [1,2,3]:
   if spent+ceiling+remaining>BUDGET:terminal='budget_ceiling_reservation';break
   body={'model':MODEL,'messages':[{'role':'user','content':job['prompt']}],'max_tokens':limit,'response_format':{'type':'json_object'}}
   raw_request=json.dumps(body,ensure_ascii=False).encode();(folder/f'request-{attempt}.json').write_bytes(raw_request)
   start=time.time();raw=b'';response=None;parsed=None;error=None
   try:
    req=urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=raw_request,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=180) as f:raw=f.read()
    (folder/f'response-{attempt}.json').write_bytes(raw);response=json.loads(raw)
    choice=response['choices'][0]
    assert choice.get('finish_reason')!='length','length-limited judgment'
    parsed=parse(choice['message']['content'],job['kind'])
   except Exception as exc:
    if isinstance(exc,urllib.error.HTTPError):
     raw=exc.read();(folder/f'http-error-response-{attempt}.txt').write_bytes(raw)
     if exc.code==402:terminal='api_quota_exhausted'
    error=(type(exc).__name__+': '+str(exc)).replace(key,'[REDACTED]')
   spent+=ceiling
   usage=(response or {}).get('usage') or {};cost=usage.get('cost')
   if cost is None:unknown_costs+=1
   else:known_cost+=D(str(cost))
   record={k:v for k,v in job.items() if k!='prompt'}
   record.update(judge=MODEL,response_model=(response or {}).get('model'),response_id=(response or {}).get('id'),started_utc=datetime.datetime.fromtimestamp(start,datetime.timezone.utc).isoformat(),completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),attempt=attempt,request=body,request_body_sha256=sha(raw_request),raw_response_text=raw.decode(errors='replace'),parsed=parsed,parse_failed=parsed is None,error=error,usage=usage,cost_usd=cost if cost is not None else 'unknown',elapsed_sec=time.time()-start,temperature_requested='omitted',temperature_effective='unknown')
   with (R/'ALL_CALLS.jsonl').open('a') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
   if parsed is not None:
    with (R/'VALID_JUDGMENTS.jsonl').open('a') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
    valid+=1;break
   failed+=1
   if terminal:break
   if attempt<3:time.sleep(1)
  if (i+1)%10==0 or terminal:
   with (NIGHT/'PROGRESS.md').open('a') as f:f.write(f'\nI003 ADV judge: primary jobs processed{i+1}/140, valid{valid}, failed calls{failed}, received-cost sum USD{known_cost}, unknown-cost calls{unknown_costs}, conservative reserved spent ceiling USD{spent}; not an observed expense estimate.\n')
  print('I003_JUDGE',i+1,job['job_id'],'valid',parsed is not None,'cost_receipts',str(known_cost),flush=True)
  if terminal:break
 result={'planned_primary_jobs':140,'processed_primary_jobs':i+1,'valid_judgments':valid,'failed_calls':failed,'all_calls':valid+failed,'actual_cost_usd':str(known_cost) if unknown_costs==0 else 'unknown','known_cost_receipts_sum_usd':str(known_cost),'unknown_cost_calls':unknown_costs,'conservative_spent_ceiling_usd':str(spent),'terminal_reason':terminal or 'all_jobs_processed','model':MODEL,'max_tokens':limit,'temperature_effective':'unknown','new_answers_generated':False}
 put(R/'RUN_FINISHED.json',result)
 assert parse('```json\n{"preference":"A","rationale":"ok"}\n```','pairwise')['preference']=='A'
 print('I003_FINISHED',json.dumps(result),flush=True)
if __name__=='__main__':main()
