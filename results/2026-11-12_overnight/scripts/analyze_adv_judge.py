"""Hash-bound Claude ADV analysis; missing scores never filled or counted as ties."""
import argparse,collections,csv,hashlib,json
from pathlib import Path
import numpy as np
CONDS=['generic_llm_raw','generic_llm_expert_prompt','profy_expert_full'];GENERAL=['completeness','specificity','actionability','coherence','safety_boundary'];DIMS=GENERAL+['evidence_grounding','uncertainty_calibration']
def read(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ci(v):
 if not v:return None
 a=np.asarray(v);r=np.random.default_rng(20261112);b=a[r.integers(0,len(a),(10000,len(a)))].mean(axis=1)
 return [float(x) for x in np.quantile(b,[.025,.975])]
def csvout(p,rows):
 if not rows:return
 with p.open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows([{k:'unknown' if v is None else json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in x.items()} for x in rows])
def main(a):
 out=Path(a.out).resolve();out.mkdir(exist_ok=False)
 source=Path(a.rubric_file);pairsource=Path(a.pairwise_file);rr=[x for x in read(source) if x['kind']=='rubric' and x.get('parsed')];pp=[x for x in read(pairsource) if x['kind']=='pairwise' and x.get('parsed')]
 by={(x['task_id'],x['condition']):x for x in rr};assert len(by)==len(rr)
 means={};errors={};overall={}
 for c in CONDS:
  r=[x for x in rr if x['condition']==c];means[c]={'n':len(r),**{d:float(np.mean([x['parsed']['scores'][d] for x in r])) if r else None for d in DIMS}}
  for x in r:overall[x['task_id'],c]=sum(x['parsed']['scores'][d] for d in GENERAL)/5
  means[c]['overall']=float(np.mean([overall[x['task_id'],c] for x in r])) if r else None
  errors[c]=dict(collections.Counter(tag for x in r for tag in x['parsed']['error_tags']))
 differences={}
 for base in CONDS[:2]:
  ids=sorted(t for t,c in by if c==CONDS[2] and (t,base) in by);differences[base]={}
  for d in ['overall']+DIMS:
   vals=[overall[t,CONDS[2]]-overall[t,base] if d=='overall' else by[t,CONDS[2]]['parsed']['scores'][d]-by[t,base]['parsed']['scores'][d] for t in ids]
   differences[base][d]={'n':len(vals),'task_ids':ids,'mean':float(np.mean(vals)) if vals else None,'bootstrap95':ci(vals),'higher':sum(x>1e-12 for x in vals),'lower':sum(x < -1e-12 for x in vals),'tie':sum(abs(x)<=1e-12 for x in vals),'per_task':dict(zip(ids,vals))}
 paired={};pairs_rows=[]
 for base in CONDS[:2]:
  records=[x for x in pp if x['baseline']==base];pb={(x['task_id'],x['order']):x for x in records};assert len(pb)==len(records)
  tally=collections.Counter();detail=[]
  for task in [f'ADV_{n:03d}' for n in range(1,21)]:
   winners=[]
   for order in ['full_A','full_B']:
    r=pb.get((task,order));pref=r['parsed']['preference'] if r else None
    winner=None if r is None else ('tie' if pref=='tie' else r['system_a' if pref=='A' else 'system_b']);winners.append(winner)
   if None in winners:category='missing_order'
   elif winners==[CONDS[2]]*2:category='both_full_wins'
   elif winners==[base]*2:category='both_baseline_wins'
   elif winners==['tie']*2:category='both_ties'
   elif 'tie' in winners:category='tie_mixed'
   else:category='opposite_winners'
   tally[category]+=1;row={'task_id':task,'baseline':base,'full_A_winner':winners[0],'full_B_winner':winners[1],'category':category};detail.append(row);pairs_rows.append(row)
  complete=20-tally['missing_order'];same=tally['both_full_wins']+tally['both_baseline_wins']+tally['both_ties']
  paired[base]={'n_tasks_with_both_orders':complete,'counts':dict(tally),'full_strict_both_order_win_fraction':tally['both_full_wins']/complete if complete else None,'position_consistency_fraction':same/complete if complete else None,'raw_A_count':sum(x['parsed']['preference']=='A' for x in records),'raw_B_count':sum(x['parsed']['preference']=='B' for x in records),'raw_tie_count':sum(x['parsed']['preference']=='tie' for x in records),'A_choice_fraction_all':sum(x['parsed']['preference']=='A' for x in records)/len(records) if records else None,'by_order':{order:dict(collections.Counter(x['parsed']['preference'] for x in records if x['order']==order)) for order in ['full_A','full_B']},'per_task':detail}
 # All uses of the same saved answer must have the identical source hash.
 hashes={}
 for r in rr+pp:
  assert r['judge']=='anthropic/claude-opus-5.5'
  for c,h in r['output_sha256'].items():
   key=(r['task_id'],c)
   if key in hashes:assert hashes[key]==h
   hashes[key]=h
 result={'judge':'anthropic/claude-opus-5.5','planned_tasks':20,'valid_rubric_records':len(rr),'valid_pairwise_records':len(pp),'complete_all_60_rubrics':len(rr)==60,'complete_all_80_pairwise':len(pp)==80,'means':means,'full_minus_baseline':differences,'error_tags':errors,'pairwise':paired,'hash_consistency_verified':True,'n_distinct_output_hash_bindings':len(hashes),'overall_definition':'mean of five general rubric dimensions','bootstrap':{'n':10000,'seed':20261112,'unit':'task'},'analysis_input_sha256':{'rubric_file':sha(source),'pairwise_file':sha(pairsource)},'rubric_source_file':str(source),'pairwise_source_file':str(pairsource),'ranking_full_prompt_raw':bool(all(means[c]['overall'] is not None for c in CONDS) and means[CONDS[2]]['overall']>means[CONDS[1]]['overall']>means[CONDS[0]]['overall']),'incomplete_scores_are_not_imputed':True}
 with (out/'results.json').open('x') as f:json.dump(result,f,indent=2)
 csvout(out/'condition_means.csv',[{'condition':c,**means[c]} for c in CONDS])
 csvout(out/'paired_differences.csv',[{'baseline':c,'dimension':d,**{k:v for k,v in z.items() if k not in ['task_ids','per_task']}} for c,x in differences.items() for d,z in x.items()])
 csvout(out/'pairwise_by_task.csv',pairs_rows)
 report=['# Claude ADV20 hash-bound rejudging','',f'Valid rubric records {len(rr)}/60; valid pairwise {len(pp)}/80. Missing scores remain unknown.','', '| Condition | Valid n | Overall |','|---|---:|---:|']
 report += [f'| {c} | {means[c]["n"]} | {means[c]["overall"]} |' for c in CONDS]
 report += ['','If any rubric condition has missing results, these means are descriptive of different observed subsets, not a complete20-task comparison. No old Full score fills a gap.','',json.dumps({c:paired[c]['counts'] for c in CONDS[:2]},indent=2),'','All output hashes agree across scoring uses. Full generation label deepseek-v4-flash, baselinesmoonshot-v1-128k; judge different from both.']
 (out/'REPORT.md').write_text('\n'.join(report))
 print(json.dumps({'rubric_n':{c:means[c]['n'] for c in CONDS},'pairwise_counts':{c:paired[c]['counts'] for c in CONDS[:2]},'all_complete':len(rr)==60 and len(pp)==80}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--rubric-file',required=True);p.add_argument('--pairwise-file',required=True);p.add_argument('--out',required=True);main(p.parse_args())
