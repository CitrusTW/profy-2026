"""Read-only request, output and budget integrity audit; no API calls."""
import ast,collections,decimal,hashlib,importlib.util,json
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parent;B=R.parents[1]/'04_项目数据与代码/Profy-main/knowledge/benchmarks/profybench-v1';sha=lambda b:hashlib.sha256(b).hexdigest()
def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def main():
 calls=rows(O/'ALL_CALLS.jsonl');plan=json.loads((O/'BUDGET_AND_INPUT_PLAN.json').read_text());freeze=json.loads((O/'PREREG_I010_SHA256.json').read_text());assert sha((O/'PREREG_I010.md').read_bytes())==freeze['sha256'];assert sha((O/'BUDGET_AND_INPUT_PLAN.json').read_bytes())==freeze['plan_sha256']
 for p,h in plan['source_sha256'].items():assert sha(Path(p).read_bytes())==h,p
 tasks={x['task_id']:x for x in rows(B/'profybench_v0.jsonl') if x['task_family']=='ADV'};templates=next(ast.literal_eval(n.value) for n in ast.parse((B/'scripts/run_full_pipeline.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='EXPERT_PROMPT_TEMPLATES' for t in n.targets));spec=importlib.util.spec_from_file_location('original_i010_judge',B/'scripts/llm_judge.py');judge=importlib.util.module_from_spec(spec);spec.loader.exec_module(judge)
 outputs={'profy_expert_full':{x['task_id']:x['output_text'] for x in rows(B/'results/outputs_profy_expert_full.jsonl') if x['task_id'] in tasks}}
 generated=rows(O/'GENERATED_OUTPUTS.jsonl');count=collections.Counter((x['task_id'],x['condition']) for x in generated);assert all(v==1 for v in count.values())
 for x in generated:assert x['output_sha256']==sha(x['output_text'].encode());outputs.setdefault(x['condition'],{})[x['task_id']]=x['output_text']
 valid=collections.Counter();cost=decimal.Decimal(0);unknown=0
 for x in calls:
  t=tasks[x['task_id']];req=x['request'];assert sha(json.dumps(req,ensure_ascii=False).encode())==x['request_body_sha256'];assert Path(x['raw_request_path']).read_bytes()==json.dumps(req,ensure_ascii=False).encode()
  if x['kind']=='generation':
   msgs=([{'role':'system','content':templates['ADV']}] if x['condition']=='generic_llm_expert_prompt' else [])+[{'role':'user','content':t['input']['prompt']}];assert req=={'model':'deepseek/deepseek-v4-flash','messages':msgs,'temperature':0.7,'max_tokens':4096}
  else:
   if x['kind']=='rubric':prompt=judge.build_rubric_prompt(t,outputs[x['condition']][x['task_id']]);limit=4096
   else:prompt=judge.build_pairwise_prompt(t,outputs[x['system_a']][x['task_id']],outputs[x['system_b']][x['task_id']]);limit=1024
   assert req=={'model':'anthropic/claude-opus-5.5','messages':[{'role':'user','content':prompt}],'max_tokens':limit,'response_format':{'type':'json_object'}}
   for c,h in x['output_sha256'].items():assert h==sha(outputs[c][x['task_id']].encode())
  if x.get('parsed') is not None:valid[x['kind']]+=1
  if x['cost_usd']=='unknown':unknown+=1
  else:cost+=decimal.Decimal(str(x['cost_usd']))
  assert x['attempt']<=3
 assert cost<=10
 report={'prereg_and_plan_unchanged':True,'all_original_source_hashes_unchanged':True,'original_messages_and_parameters_exact':True,'no_duplicate_successful_generation':True,'all_judge_templates_and_parameters_exact':True,'all_scored_output_hashes_verified':True,'full_not_regenerated_or_modified':True,'valid_records_by_kind':dict(valid),'observed_actual_receipt_sum_usd':str(cost),'unknown_cost_calls':unknown,'within10usd_observed':True,'generation_empty_outputs':sum(x['empty_output'] for x in generated),'generation_length_limited':sum(x['finish_reason']=='length' for x in generated),'all_records_preserved':len(calls),'no_api_calls_from_audit':True}
 out=O/'INTEGRITY_AUDIT.json'
 with out.open('x') as f:json.dump(report,f,indent=2)
 print(json.dumps(report))
if __name__=='__main__':main()
