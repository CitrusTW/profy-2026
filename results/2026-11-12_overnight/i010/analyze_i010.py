"""Repeatable I010 statistics, all conditions and fixed wording. No API calls."""
import argparse,collections,datetime,hashlib,importlib.util,json,statistics,sys
from pathlib import Path
import numpy as np
O=Path(__file__).resolve().parent;R=O.parent;CONDS=['generic_llm_raw','generic_llm_expert_prompt','profy_expert_full'];DIMS=['completeness','specificity','actionability','coherence','safety_boundary']
def rows(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def ci(vals):
 if not vals:return None
 v=np.asarray(vals);rng=np.random.default_rng(20261112);return [float(x) for x in np.quantile(v[rng.integers(0,len(v),(10000,len(v)))].mean(axis=1),[.025,.975])]
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();out=Path(a.out);assert not out.exists();allcalls=rows(O/'ALL_CALLS.jsonl');validpath=O/'VALID_JUDGMENTS.jsonl';valid=rows(validpath)
 core=mod('i010_same_statistics',R/'analyze_adv_judge_v2.py');core.main(argparse.Namespace(out=str(out),rubric_file=str(validpath),pairwise_file=str(validpath)))
 results=json.loads((out/'results.json').read_text());cross=json.loads((R/'adv_i004_analysis_v2/results.json').read_text());meta=json.loads((R/'ADV_METADATA_INPUT.json').read_text());rubric={(x['task_id'],x['condition']):x for x in valid if x['kind']=='rubric'};variants={}
 for variant in sorted({x['variant_type'] for x in meta['tasks'].values()}):
  ids=sorted(t for t,v in meta['tasks'].items() if v['variant_type']==variant);z={'task_ids':ids,'n_tasks':len(ids),'conditions':{},'full_minus_baseline':{}}
  for c in CONDS:
   vals=[sum(rubric[t,c]['parsed']['scores'][d] for d in DIMS)/5 for t in ids if (t,c) in rubric];z['conditions'][c]={'n':len(vals),'overall_mean':statistics.mean(vals) if vals else None}
  for base in CONDS[:2]:
   zz={}
   for d in ['overall']+DIMS:
    vals=[]
    for t in ids:
     if (t,base) not in rubric or (t,CONDS[2]) not in rubric:continue
     b,f=[rubric[t,c]['parsed']['scores'] for c in [base,CONDS[2]]];vals.append((sum(f[x]-b[x] for x in DIMS)/5) if d=='overall' else f[d]-b[d])
    zz[d]={'n':len(vals),'mean':statistics.mean(vals) if vals else None,'bootstrap95':ci(vals),'higher':sum(x>1e-12 for x in vals),'lower':sum(x< -1e-12 for x in vals),'tie':sum(abs(x)<=1e-12 for x in vals)}
   z['full_minus_baseline'][base]=zz
  variants[variant]=z
 generated=rows(O/'GENERATED_OUTPUTS.jsonl');audit={c:{'n':sum(x['condition']==c for x in generated),'empty':sum(x['condition']==c and x['empty_output'] for x in generated),'length_limited':sum(x['condition']==c and x['finish_reason']=='length' for x in generated),'returned_model_counts':dict(collections.Counter(x['response_model'] for x in generated if x['condition']==c))} for c in CONDS[:2]};cost=sum(float(x['cost_usd']) for x in allcalls if x['cost_usd']!='unknown');unknown=sum(x['cost_usd']=='unknown' for x in allcalls)
 diff=results['full_minus_baseline'][CONDS[1]]['overall'];pw=results['pairwise'][CONDS[1]]['counts'];complete=results['complete_all_60_rubrics'] and results['complete_all_80_pairwise'];support=complete and diff['bootstrap95'][0]>0 and pw['both_full_wins']>pw['both_baseline_wins']
 text='With baselines using the same declared base-model label, the advantage remains.' if support else ('With baselines using the same declared base-model label, the advantage shrinks or is not significant; model differences may account for part of the cross-model gap.' if complete else 'I010 incomplete; no complete same-model conclusion is supported.')
 supplement={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'same_model_results':results,'cross_model_results_file':str(R/'adv_i004_analysis_v2/results.json'),'cross_model_results_sha256':hashlib.sha256((R/'adv_i004_analysis_v2/results.json').read_bytes()).hexdigest(),'variant_results':variants,'generation_audit':audit,'billing':{'known_receipt_sum_usd':cost,'unknown_cost_calls':unknown,'actual_cost_usd':cost if unknown==0 else 'unknown','calls':len(allcalls),'failed_calls':sum(x['parse_failed'] for x in allcalls)},'wording_rule':{'complete':complete,'ci_strictly_positive':bool(diff['bootstrap95'] and diff['bootstrap95'][0]>0),'both_order_full_more_than_baseline':pw['both_full_wins']>pw['both_baseline_wins'],'same_model_advantage_supported':support,'manuscript_wording':text},'generation_model_requested':'deepseek/deepseek-v4-flash','generation_model_catalog_revision':'deepseek/deepseek-v4-flash-20260423','historical_platform_full_model_revision':'unknown','full_outputs_regenerated':False,'cannot_isolate_memory_or_evolution_causally':True,'all_calls_sha256':hashlib.sha256((O/'ALL_CALLS.jsonl').read_bytes()).hexdigest()}
 # New derivative files, never overwrite core results.json.
 (out/'I010_RESULTS.json').write_text(json.dumps(supplement,ensure_ascii=False,indent=2))
 report=['# I010: 同模型 ADV20 对照','',text,'','| 对比 | Raw overall | Expert Prompt overall | Full overall | Full−Expert Prompt | 95% CI | 两次Full赢 / 不一致 / 两次基线赢 |','|---|---:|---:|---:|---:|---|---|']
 for label,res in [('I004: Moonshot基线',cross),('I010: DeepSeek基线',results)]:
  d=res['full_minus_baseline'][CONDS[1]]['overall'];w=res['pairwise'][CONDS[1]]['counts'];report.append('| '+' | '.join([label]+[str(res['means'][c]['overall']) for c in CONDS]+[str(d['mean']),str(d['bootstrap95']),str([w['both_full_wins'],w['opposite_winners'],w['both_baseline_wins']])])+' |')
 report+=['','Full未重新生成。I010的Full重新评分, 和I004评分分别报告。历史平台Full仅有模型标签, 未核实实际服务版本; 不声称已控制服务端全部差异。','', '完整子集、维度差值、费用、截断和空输出计数: I010_RESULTS.json。']
 (out/'I010_REPORT.md').write_text('\n'.join(report));print(json.dumps({'complete':complete,'wording':supplement['wording_rule'],'cost':supplement['billing']},ensure_ascii=False))
if __name__=='__main__':main()
