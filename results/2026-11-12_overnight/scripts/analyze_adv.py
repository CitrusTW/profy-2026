"""Read-only ADV reanalysis; hashes, linkage warnings and reproducible paired CI."""
import collections,csv,hashlib,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;W=ROOT.parents[1]
BASE=W/'04_项目数据与代码/Profy-main/knowledge/benchmarks/profybench-v1/results'
GENERAL=['completeness','specificity','actionability','coherence','safety_boundary']
CONDS=['generic_llm_raw','generic_llm_expert_prompt','profy_expert_full']
IDS=[f'ADV_{x:03d}' for x in range(1,21)]

def load(name):return [json.loads(x) for x in (BASE/name).read_text().splitlines() if x.strip()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ci(values):
 values=np.asarray(values,dtype=float);rng=np.random.default_rng(20261112)
 means=values[rng.integers(0,len(values),size=(10000,len(values)))].mean(axis=1)
 return [float(x) for x in np.quantile(means,[.025,.975])]
def writecsv(path,rows):
 with path.open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 out=ROOT/'adv';out.mkdir(exist_ok=False)
 scores=[x for x in load('judge_scores.jsonl') if x['task_id'] in IDS]
 pairs=[x for x in load('pairwise_preferences.jsonl') if x['task_id'] in IDS]
 assert len(scores)==60 and len(pairs)==20
 by={(x['task_id'],x['condition']):x for x in scores};assert len(by)==60
 assert set(by)=={(t,c) for t in IDS for c in CONDS}
 dims=sorted({d for r in scores for d in r['scores']})
 assert all(set(GENERAL)<=r['scores'].keys() for r in scores)
 overall={(t,c):sum(by[t,c]['scores'][d] for d in GENERAL)/len(GENERAL) for t in IDS for c in CONDS}
 means={c:{**{d:float(np.mean([by[t,c]['scores'][d] for t in IDS if d in by[t,c]['scores']])) for d in dims},'overall':float(np.mean([overall[t,c] for t in IDS]))} for c in CONDS}
 differences={}
 for c in CONDS[:2]:
  differences[c]={}
  for d in ['overall']+dims:
   v=[overall[t,CONDS[2]]-overall[t,c] if d=='overall' else by[t,CONDS[2]]['scores'][d]-by[t,c]['scores'][d] for t in IDS]
   differences[c][d]={'mean':float(np.mean(v)),'bootstrap95':ci(v),'higher':sum(x>1e-12 for x in v),'lower':sum(x < -1e-12 for x in v),'tie':sum(abs(x)<=1e-12 for x in v),'per_task':dict(zip(IDS,v))}
 errors={c:dict(collections.Counter(tag for t in IDS for tag in by[t,c].get('error_tags',[]))) for c in CONDS}
 positions=collections.Counter(x.get('raw_preference','unknown') for x in pairs);winners=collections.Counter(x.get('winner','unknown') for x in pairs)
 pair={'n':20,'raw_preference_counts':dict(positions),'winner_counts':dict(winners),'A_selection_fraction_all':positions['A']/20,'A_selection_fraction_decisive':positions['A']/(positions['A']+positions['B']) if positions['A']+positions['B'] else None,'system_a_counts':dict(collections.Counter(x['system_a'] for x in pairs)),'system_b_counts':dict(collections.Counter(x['system_b'] for x in pairs)),'both_orders_available':False}
 chronology=[];models={}
 for c,name in zip(CONDS,['outputs_generic_llm_raw.jsonl','outputs_generic_llm_expert_prompt.jsonl','outputs_profy_expert_full.jsonl']):
  outputs={x['task_id']:x for x in load(name) if x['task_id'] in IDS};assert len(outputs)==20
  models[c]=dict(collections.Counter(x.get('model','unknown') for x in outputs.values()))
  for t in IDS:
   o=outputs[t];j=by[t,c];p=next(x for x in pairs if x['task_id']==t)
   chronology.append({'task_id':t,'condition':c,'output_timestamp':o.get('timestamp'),'judge_timestamp':j.get('timestamp'),'judge_precedes_saved_output':bool(j.get('timestamp') and o.get('timestamp') and j['timestamp']<o['timestamp']),'pairwise_timestamp':p.get('timestamp'),'pairwise_precedes_saved_output':bool(p.get('timestamp') and o.get('timestamp') and p['timestamp']<o['timestamp']),'score_has_output_hash':bool(j.get('output_sha256') or j.get('input_sha256')),'output_model':o.get('model','unknown'),'platform_invoke_label':o.get('invoke_api'),'proxy_label':o.get('is_proxy')})
 files=['judge_scores.jsonl','pairwise_preferences.jsonl','outputs_generic_llm_raw.jsonl','outputs_generic_llm_expert_prompt.jsonl','outputs_profy_expert_full.jsonl']
 linkage={'by_condition_judge_predates_saved_output':{c:sum(r['judge_precedes_saved_output'] for r in chronology if r['condition']==c) for c in CONDS},'by_condition_pairwise_predates_saved_output':{c:sum(r['pairwise_precedes_saved_output'] for r in chronology if r['condition']==c) for c in CONDS},'verified_score_output_hash_links':sum(r['score_has_output_hash'] for r in chronology),'interpretation':'Saved score summaries only. Current Full platform-labelled outputs cannot be linked to these earlier scores; no causal platform or model comparison is established.'}
 result={'n_tasks':20,'overall_definition':'Arithmetic mean of five GENERAL_DIMS, matching received generate_tables.py; family-specific dimensions reported separately','general_dimensions':GENERAL,'means':means,'full_minus_baseline':differences,'error_tags':errors,'pairwise':pair,'models_from_saved_output_labels':models,'judge_models':dict(collections.Counter(x['judge_model'] for x in scores)),'linkage':linkage,'bootstrap':{'replicates':10000,'seed':20261112,'unit':'task','quantiles':[.025,.975],'implementation':'numpy.default_rng percentile'},'source_sha256':{n:sha(BASE/n) for n in files}}
 with (out/'results.json').open('x') as f:json.dump(result,f,indent=2)
 writecsv(out/'condition_means.csv',[{'condition':c,**means[c]} for c in CONDS])
 writecsv(out/'paired_differences.csv',[{'baseline':c,'dimension':d,**{k:v for k,v in x.items() if k not in ['per_task','bootstrap95']},'ci_low':x['bootstrap95'][0],'ci_high':x['bootstrap95'][1]} for c,z in differences.items() for d,x in z.items()])
 writecsv(out/'timestamp_and_linkage.csv',chronology)
 writecsv(out/'task_scores.csv',[{'task_id':t,'condition':c,**by[t,c]['scores'],'overall':overall[t,c],'error_tags':json.dumps(by[t,c].get('error_tags',[]))} for t in IDS for c in CONDS])
 with (out/'selected_score_records.jsonl').open('x') as f:
  for r in scores:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 with (out/'selected_pairwise_records.jsonl').open('x') as f:
  for r in pairs:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 report=['# ADV 20题既有分数重新统计','', '**注意: 这是已有评分记录的统计, 尚不能认作当前平台回答的评分.**',json.dumps(linkage,ensure_ascii=False),'','overall沿用原脚本的5个通用维度平均, 不是7维平均.','', '| Condition | overall |','|---|---:|']
 report += [f'| {c} | {means[c]["overall"]:.4f} |' for c in CONDS]
 for c in CONDS[:2]:report += ['',c, json.dumps(differences[c]['overall'])]
 report += ['','Pairwise',json.dumps(pair),'','Error tags',json.dumps(errors),'','Model labels',json.dumps(models),'','No generation or judge calls made. Source hashes and per-task lineage warnings are in results.json and timestamp_and_linkage.csv.']
 (out/'REPORT.md').write_text('\n'.join(report))
 print(json.dumps({'means':means,'differences':{c:z['overall'] for c,z in differences.items()},'pairwise':pair,'linkage':linkage},ensure_ascii=False,indent=2))
 assert ci([0]*20)==[0,0]
 assert all(sum(z['overall'][k] for k in ['higher','lower','tie'])==20 for z in differences.values())
 assert all(sha(BASE/n)==h for n,h in result['source_sha256'].items())
if __name__=='__main__':main()
