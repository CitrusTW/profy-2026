"""Saved ADV metadata, variant diagnostics and billing; no model calls."""
import argparse,collections,csv,hashlib,json,statistics
from decimal import Decimal
from pathlib import Path
GENERAL=['completeness','specificity','actionability','coherence','safety_boundary'];CONDS=['generic_llm_raw','generic_llm_expert_prompt','profy_expert_full']
def rows(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main(a):
 out=Path(a.out);out.mkdir(exist_ok=False);meta=json.loads(Path(a.metadata).read_text());tasks=meta['tasks'];rubric=rows(a.rubric);by={(x['task_id'],x['condition']):x for x in rubric if x.get('parsed') and x['kind']=='rubric'}
 variants={}
 for variant in sorted({x['variant_type'] for x in tasks.values()}):
  ids=sorted(t for t,v in tasks.items() if v['variant_type']==variant);z={'task_ids':ids,'n_tasks':len(ids),'conditions':{}}
  for c in CONDS:
   valid=[by[t,c] for t in ids if (t,c) in by];v=[sum(x['parsed']['scores'][d] for d in GENERAL)/5 for x in valid];z['conditions'][c]={'n_valid':len(valid),'overall_mean':statistics.mean(v) if v else None}
  variants[variant]=z
 timing=[x['elapsed_sec'] for x in meta['full_output_metadata'].values() if x.get('elapsed_sec') is not None];batches={};total=Decimal(0);unknown=0
 for source in a.calls:
  calls=rows(source);known=sum((Decimal(str(x['cost_usd'])) for x in calls if x.get('cost_usd') not in [None,'unknown']),Decimal(0));u=sum(x.get('cost_usd') in [None,'unknown'] for x in calls);total+=known;unknown+=u
  batches[Path(source).parent.name]={'all_calls':len(calls),'valid_calls':sum(x.get('parsed') is not None for x in calls),'failed_calls':sum(x.get('parsed') is None for x in calls),'valid_by_kind':dict(collections.Counter(x['kind'] for x in calls if x.get('parsed'))),'failed_by_condition':dict(collections.Counter(x.get('condition',x.get('baseline','unknown')) for x in calls if not x.get('parsed'))),'known_cost_receipts_sum_usd':str(known),'unknown_cost_calls':u,'models_requested':dict(collections.Counter(x['judge'] for x in calls)),'models_returned':dict(collections.Counter(str(x.get('response_model')) for x in calls)),'max_tokens':dict(collections.Counter(str(x['request']['max_tokens']) for x in calls)),'temperature_requested':dict(collections.Counter(x['temperature_requested'] for x in calls)),'temperature_effective':dict(collections.Counter(x['temperature_effective'] for x in calls)),'first_call_utc':min((x['started_utc'] for x in calls),default=None),'last_call_utc':max((x['completed_utc'] for x in calls),default=None),'sha256':sha(source)}
 result={'variant_results':variants,'platform_full_timing':{'n':len(timing),'mean_seconds':statistics.mean(timing) if timing else None,'median_seconds':statistics.median(timing) if timing else None,'baseline_timing_comparable':False},'judge_batches':batches,'actual_cost_usd':str(total) if unknown==0 else 'unknown','known_cost_receipts_sum_usd':str(total),'unknown_cost_calls':unknown,'metadata_sha256':sha(a.metadata),'rubric_sha256':sha(a.rubric),'old_full_scores_used':False,'is_causal_method_comparison':False}
 with (out/'results.json').open('x') as f:json.dump(result,f,indent=2)
 flat=[{'variant':v,'n_tasks':x['n_tasks'],'condition':c,**r} for v,x in variants.items() for c,r in x['conditions'].items()]
 with (out/'variant_means.csv').open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(flat[0]),lineterminator='\n');w.writeheader();w.writerows(flat)
 print(json.dumps({'fresh_rubric_count':len(by),'actual_judge_usd':result['actual_cost_usd'],'platform_full_timing':result['platform_full_timing']}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--metadata',required=True);p.add_argument('--rubric',required=True);p.add_argument('--calls',nargs='+',required=True);p.add_argument('--out',required=True);main(p.parse_args())
