"""Frozen I010 protocol. Serial OpenRouter calls, no Profy, no manuscript writes."""
import ast,datetime,decimal,fcntl,hashlib,importlib.util,json,re,sys,time,urllib.request,urllib.error
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parent;B=R.parents[1]/'04_项目数据与代码/Profy-main/knowledge/benchmarks/profybench-v1';D=decimal.Decimal
CONDS=['generic_llm_raw','generic_llm_expert_prompt','profy_expert_full'];GEN='deepseek/deepseek-v4-flash';JUDGE='anthropic/claude-opus-5.5'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(p,x):
 with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2)
def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def append(p,x):
 with p.open('a') as f:f.write(json.dumps(x,ensure_ascii=False)+'\n');f.flush()
def main():
 assert '--allow-paid' in sys.argv
 plan=json.loads((O/'BUDGET_AND_INPUT_PLAN.json').read_text());freeze=json.loads((O/'PREREG_I010_SHA256.json').read_text());assert sha((O/'PREREG_I010.md').read_bytes())==freeze['sha256'];assert sha((O/'BUDGET_AND_INPUT_PLAN.json').read_bytes())==freeze['plan_sha256']
 for p,h in plan['source_sha256'].items():assert sha(Path(p).read_bytes())==h
 assert not (O/'ALL_CALLS.jsonl').exists(),'Never silently rerun a started batch'
 templates=next(ast.literal_eval(n.value) for n in ast.parse((B/'scripts/run_full_pipeline.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='EXPERT_PROMPT_TEMPLATES' for t in n.targets));judge=mod('i010_judge_templates',B/'scripts/llm_judge.py');parse=mod('i010_original_parser',R/'adv_rejudge_i003/run_judge.py').parse
 tasks={x['task_id']:x for x in rows(B/'profybench_v0.jsonl') if x['task_family']=='ADV'};assert sorted(tasks)==plan['tasks'];full={x['task_id']:x for x in rows(B/'results/outputs_profy_expert_full.jsonl') if x['task_id'] in tasks};assert len(full)==20
 catalog={x['id']:x for x in json.loads((O/'OPENROUTER_MODEL_CATALOG.json').read_text())['data']};assert GEN in catalog and JUDGE in catalog
 key=next(x for x in re.findall(r'\bsk-[A-Za-z0-9._-]+',Path('/Users/mac/Desktop/obsidian files/Profy related keys.md').read_text()) if x.startswith('sk-or-'))
 known=D(0);reserved=D(0);unknown=0;count=0;terminal=None;started=time.time();outputs={CONDS[2]:{t:x['output_text'] for t,x in full.items()}};sys.path.insert(0,str(R));from coordination_sync_v12 import sync
 def state(phase,job=None):
  x={'updated_utc':now(),'phase':phase,'last_job':job,'calls':count,'known_actual_usd':str(known),'unknown_cost_calls':unknown,'reserved_unknown_cost_ceiling_usd':str(reserved),'terminal':terminal,'elapsed_seconds':time.time()-started,'full_regenerated':False}
  (O/'STATE.json').write_text(json.dumps(x,indent=2));return x
 def checkpoint(reason):
  state(reason)
  with (R/'coordination_sync.lock').open('a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX);sync('I010 '+reason)
  markers=[int(x.stem.rsplit('-',1)[-1]) for x in R.glob('NEW_INSTRUCTION_I-*.json')]
  if any(x>10 for x in markers):raise RuntimeError('New coordination instruction requires review; pause before next paid call')
 def call(job,body,kind):
  nonlocal known,reserved,unknown,count,terminal
  folder=O/'calls'/job['job_id'];folder.mkdir(parents=True,exist_ok=False);model=body['model'];prices=catalog[model]['pricing'];request=json.dumps(body,ensure_ascii=False).encode();ceiling=D(len(request)+2048)*D(prices['prompt'])+D(body['max_tokens'])*D(prices['completion']);last=None
  for attempt in range(1,4):
   if known+reserved+ceiling>D(10):terminal='budget_ceiling_before_next_call';return None
   (folder/f'request-{attempt}.json').write_bytes(request);start=time.time();raw=b'';response=None;parsed=None;error=None;api_error=False;finish=None;text=None
   try:
    req=urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=request,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=240) as f:raw=f.read()
    (folder/f'response-{attempt}.json').write_bytes(raw);response=json.loads(raw)
    if response.get('error'):api_error=True;raise RuntimeError('API error object')
    ch=response['choices'][0];finish=ch.get('finish_reason');text=ch.get('message',{}).get('content')
    if kind=='generation':
     assert text is None or isinstance(text,str);parsed={'output_text':text or ''}
    else:
     assert finish!='length','length-limited judgment';parsed=parse(text,kind)
   except Exception as exc:
    if isinstance(exc,urllib.error.HTTPError):
     api_error=True;raw=exc.read();(folder/f'http-error-{attempt}.txt').write_bytes(raw)
     if exc.code==402:terminal='api_quota_exhausted'
    elif isinstance(exc,(urllib.error.URLError,TimeoutError,ConnectionError)):api_error=True
    error=(type(exc).__name__+': '+str(exc)).replace(key,'[REDACTED]')
   usage=(response or {}).get('usage') or {};cost=usage.get('cost');count+=1
   if cost is None:unknown+=1;reserved+=ceiling
   else:known+=D(str(cost))
   if known>D(10):terminal='unexpected_receipt_exceeds_budget_stop'
   record={**job,'kind':kind,'judge':JUDGE if kind!='generation' else None,'requested_model':model,'response_model':(response or {}).get('model'),'response_id':(response or {}).get('id'),'started_utc':datetime.datetime.fromtimestamp(start,datetime.timezone.utc).isoformat(),'completed_utc':now(),'attempt':attempt,'request':body,'request_body_sha256':sha(request),'raw_response_text':raw.decode(errors='replace'),'parsed':parsed,'parse_failed':parsed is None,'error':error,'api_error':api_error,'usage':usage,'cost_usd':cost if cost is not None else 'unknown','finish_reason':finish,'elapsed_sec':time.time()-start,'temperature_requested':body.get('temperature','omitted'),'temperature_effective':'unknown','raw_request_path':str(folder/f'request-{attempt}.json')}
   append(O/'ALL_CALLS.jsonl',record);state(kind,job['job_id']);last=record
   print('I010',count,job['job_id'],'parsed',parsed is not None,'usd',str(known),flush=True)
   if parsed is not None:
    if kind!='generation':append(O/'VALID_JUDGMENTS.jsonl',record)
    return record
   if terminal or (kind=='generation' and not api_error):return record
   if attempt<3:time.sleep(1)
  return last
 checkpoint('starting40baseline_generations')
 for t,task in sorted(tasks.items()):
  for c in CONDS[:2]:
   msgs=([{'role':'system','content':templates[task['task_family']]}] if c==CONDS[1] else [])+[{'role':'user','content':task['input']['prompt']}]
   job={'job_id':t+'-generation-'+c,'task_id':t,'condition':c,'prompt_sha256':sha(json.dumps(msgs,ensure_ascii=False).encode())};rec=call(job,{'model':GEN,'messages':msgs,'temperature':0.7,'max_tokens':4096},'generation')
   if rec and rec.get('parsed') is not None:
    text=rec['parsed']['output_text'];outputs.setdefault(c,{})[t]=text
    append(O/'GENERATED_OUTPUTS.jsonl',{'task_id':t,'task_family':'ADV','condition':c,'model':GEN,'response_model':rec['response_model'],'output_text':text,'output_sha256':sha(text.encode()),'finish_reason':rec['finish_reason'],'usage':rec['usage'],'empty_output':not bool(text.strip()),'timestamp':rec['completed_utc']})
   checkpoint('completed_generation_'+job['job_id'])
   if terminal or c not in outputs or t not in outputs[c]:terminal=terminal or 'generation_api_failed_after_retries';break
  with (R/'PROGRESS.md').open('a') as f:f.write('\n'+now()+' I010 baseline task '+t+' processed; calls='+str(count)+', receipt USD='+str(known)+', unknown-cost calls='+str(unknown)+'.\n')
  if terminal:break
 if not terminal:
  assert all(len(outputs[c])==20 for c in CONDS);put(O/'OUTPUT_HASHES.json',{c:{t:sha(x.encode()) for t,x in v.items()} for c,v in outputs.items()});checkpoint('generation_complete_start_new60rubric80pairwise')
  for t,task in sorted(tasks.items()):
   jobs=[]
   for c in CONDS:
    text=outputs[c][t];jobs.append(({'job_id':t+'-rubric-'+c,'task_id':t,'condition':c,'output_sha256':{c:sha(text.encode())}},judge.build_rubric_prompt(task,text),'rubric',4096))
   for base in CONDS[:2]:
    for order in ['full_A','full_B']:
     ca,cb=(CONDS[2],base) if order=='full_A' else (base,CONDS[2]);oa,ob=outputs[ca][t],outputs[cb][t];jobs.append(({'job_id':t+'-pairwise-'+base+'-'+order,'task_id':t,'baseline':base,'order':order,'system_a':ca,'system_b':cb,'output_sha256':{ca:sha(oa.encode()),cb:sha(ob.encode())},'visible_output_sha256':{ca:sha(oa[:3000].encode()),cb:sha(ob[:3000].encode())},'visible_character_limit':3000},judge.build_pairwise_prompt(task,oa,ob),'pairwise',1024))
   for job,prompt,kind,limit in jobs:
    job['prompt_sha256']=sha(prompt.encode());call(job,{'model':JUDGE,'messages':[{'role':'user','content':prompt}],'max_tokens':limit,'response_format':{'type':'json_object'}},kind)
    if terminal:break
   with (R/'PROGRESS.md').open('a') as f:f.write('\n'+now()+' I010 judging task '+t+' processed; calls='+str(count)+', receipt USD='+str(known)+', unknown-cost calls='+str(unknown)+'.\n')
   checkpoint('completed_judging_task_'+t)
   if terminal:break
 terminal=terminal or 'all_jobs_processed';result=state('finished');put(O/'RUN_FINISHED.json',result);checkpoint('finished_'+terminal)
 print('I010_FINISHED',json.dumps(result),flush=True)
if __name__=='__main__':main()
