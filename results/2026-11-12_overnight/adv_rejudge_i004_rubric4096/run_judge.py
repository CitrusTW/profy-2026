"""Uniform I-004 rubric batch. Reuse exact I-003 parser; no answer generation."""
import argparse,datetime,decimal,hashlib,importlib.util,json,re,time,urllib.request,urllib.error
from pathlib import Path
R=Path(__file__).resolve().parent;NIGHT=R.parent;W=NIGHT.parents[1];B=W/'04_项目数据与代码/Profy-main/knowledge/benchmarks/profybench-v1'
D=decimal.Decimal;MODEL='anthropic/claude-opus-5.5';LIMIT=4096;BUDGET=D('15')
def sha(b):return hashlib.sha256(b).hexdigest()
def put(p,j):
 with p.open('x') as f:json.dump(j,f,ensure_ascii=False,indent=2)
def rows(p):return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 p=argparse.ArgumentParser();p.add_argument('--allow-paid',action='store_true');a=p.parse_args();assert a.allow_paid and (NIGHT/'INSTRUCTION_I-004_APPLIED.json').exists()
 budget=json.loads((R/'BUDGET_PLAN.json').read_text());assert budget['model']==MODEL and budget['max_tokens']==LIMIT
 previous=D(budget['previous_batch_actual_cost_usd']);assert previous+D(budget['primary_calls_calculated_cost_ceiling_usd'])<=BUDGET
 parser=module('original_i003_parser',NIGHT/'adv_rejudge_i003/run_judge.py').parse
 source=B/'scripts/llm_judge.py';assert sha(source.read_bytes())==budget['prompt_source_sha256'];templates=module('original_judge_templates',source)
 tasks={x['task_id']:x for x in rows(B/'profybench_v0.jsonl') if x['task_family']=='ADV'};assert len(tasks)==20
 conds=['generic_llm_raw','generic_llm_expert_prompt','profy_expert_full'];outputs={c:{x['task_id']:x for x in rows(B/'results'/('outputs_'+c+'.jsonl')) if x['task_id'] in tasks} for c in conds}
 oldjobs={x['job_id']:x for x in json.loads((NIGHT/'adv_rejudge_i003/JOBS.json').read_text()) if x['kind']=='rubric'};jobs=[]
 for t,task in sorted(tasks.items()):
  for c in conds:
   text=outputs[c][t]['output_text'];job=oldjobs[t+'-rubric-'+c];prompt=templates.build_rubric_prompt(task,text)
   assert sha(prompt.encode())==job['prompt_sha256'] and sha(text.encode())==job['output_sha256'][c]
   x=dict(job,prompt=prompt);expected=budget['jobs'][len(jobs)];assert expected['task_id']==t and expected['condition']==c
   x['calculated_cost_ceiling_usd']=str(D(expected['upper_input_tokens'])*D(budget['input_rate_upper_usd_per_token'])+D(LIMIT)*D(budget['output_rate_usd_per_token']));jobs.append(x)
 assert len(jobs)==60;put(R/'JOBS.json',jobs)
 put(R/'INPUT_PROVENANCE.json',{'parent_batch_input_provenance_sha256':sha((NIGHT/'adv_rejudge_i003/INPUT_PROVENANCE.json').read_bytes()),'all60_prompt_and_output_hashes_equal_parent_batch':True,'model':MODEL,'max_tokens':LIMIT,'new_answers_generated':False})
 key=next(x for x in re.findall(r'\bsk-[A-Za-z0-9._-]+',Path('/Users/mac/Desktop/obsidian files/Profy related keys.md').read_text()) if x.startswith('sk-or-'))
 known=D('0');unknown_reserved=D('0');unknown_calls=0;valid=0;failed=0;terminal=None
 for i,job in enumerate(jobs):
  remaining=sum((D(x['calculated_cost_ceiling_usd']) for x in jobs[i+1:]),D('0'));ceiling=D(job['calculated_cost_ceiling_usd']);folder=R/'calls'/job['job_id'];folder.mkdir(parents=True,exist_ok=False)
  for attempt in [1,2,3]:
   if previous+known+unknown_reserved+ceiling+remaining>BUDGET:terminal='budget_ceiling_reservation';break
   body={'model':MODEL,'messages':[{'role':'user','content':job['prompt']}],'max_tokens':LIMIT,'response_format':{'type':'json_object'}}
   request=json.dumps(body,ensure_ascii=False).encode();(folder/f'request-{attempt}.json').write_bytes(request);start=time.time();raw=b'';response=None;parsed=None;error=None
   try:
    req=urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=request,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=240) as f:raw=f.read()
    (folder/f'response-{attempt}.json').write_bytes(raw);response=json.loads(raw);choice=response['choices'][0];assert choice.get('finish_reason')!='length','length-limited judgment';parsed=parser(choice['message']['content'],'rubric')
   except Exception as exc:
    if isinstance(exc,urllib.error.HTTPError):
     raw=exc.read();(folder/f'http-error-response-{attempt}.txt').write_bytes(raw)
     if exc.code==402:terminal='api_quota_exhausted'
    error=(type(exc).__name__+': '+str(exc)).replace(key,'[REDACTED]')
   usage=(response or {}).get('usage') or {};cost=usage.get('cost')
   if cost is None:unknown_calls+=1;unknown_reserved+=ceiling
   else:known+=D(str(cost))
   assert previous+known<=BUDGET,'Observed expenditure ceiling violated; stop all new calls'
   record={k:v for k,v in job.items() if k!='prompt'};record.update(judge=MODEL,response_model=(response or {}).get('model'),response_id=(response or {}).get('id'),phase='I-004-uniform4096',started_utc=datetime.datetime.fromtimestamp(start,datetime.timezone.utc).isoformat(),completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),attempt=attempt,request=body,request_body_sha256=sha(request),raw_response_text=raw.decode(errors='replace'),parsed=parsed,parse_failed=parsed is None,error=error,usage=usage,cost_usd=cost if cost is not None else 'unknown',elapsed_sec=time.time()-start,temperature_requested='omitted',temperature_effective='unknown')
   with (R/'ALL_CALLS.jsonl').open('a') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
   if parsed is not None:
    with (R/'VALID_JUDGMENTS.jsonl').open('a') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
    valid+=1;break
   failed+=1
   if terminal:break
   if attempt<3:time.sleep(1)
  if (i+1)%10==0 or terminal:
   with (NIGHT/'PROGRESS.md').open('a') as f:f.write(f'\nI004 rubric4096: processed{i+1}/60, valid{valid}, failed_calls{failed}, batch receipt USD{known}, combined known USD{previous+known}, unknown-cost calls{unknown_calls}.\n')
  print('I004_RUBRIC',i+1,job['job_id'],'valid',parsed is not None,'combined_known_usd',str(previous+known),flush=True)
  if terminal:break
 result={'planned_primary_jobs':60,'processed_primary_jobs':i+1,'valid_judgments':valid,'failed_calls':failed,'all_calls':valid+failed,'actual_cost_usd':str(known) if unknown_calls==0 else 'unknown','known_cost_receipts_sum_usd':str(known),'combined_actual_cost_usd':str(previous+known) if unknown_calls==0 else 'unknown','unknown_cost_calls':unknown_calls,'unknown_reserved_ceiling_usd':str(unknown_reserved),'terminal_reason':terminal or 'all_jobs_processed','model':MODEL,'max_tokens':LIMIT,'temperature_effective':'unknown','new_answers_generated':False}
 put(R/'RUN_FINISHED.json',result);print('I004_FINISHED',json.dumps(result),flush=True)
 assert parser('```json\n{"preference":"A","rationale":"ok"}\n```','pairwise')['preference']=='A'
if __name__=='__main__':main()
