from pathlib import Path
import os,re,json,hashlib,datetime
R=Path('/Users/mac/Desktop/naacl 2026.10 - CogniLife/01_任务结果/2026-11-12_night_validation_092503');B=R/'cognilife_rev_20261112_i011_final';P=R/'cognilife_rev_20261112_match_models';assert not P.exists();P.mkdir();old=(B/'main.tex').read_text();s=old;changes=[]
a=json.loads((R/'i010/analysis/I010_RESULTS.json').read_text())['same_model_results'];c=json.loads((R/'adv_i004_analysis_v2/results.json').read_text());assert c['pairwise']['generic_llm_expert_prompt']['counts']['both_full_wins']==16;delta=a['full_minus_baseline']['generic_llm_expert_prompt']['overall'];assert abs(delta['mean']+.19)<1e-12;assert all(abs(x-y)<1e-12 for x,y in zip(delta['bootstrap95'],[-.55,.16]))
lesson=r'\textbf{Match base models.} A configuration advantage that appeared against baselines on a different model (both-order wins on 16/20 tasks) was not retained with model-label-matched baselines (Full $-$ Expert Prompt: $-$0.19, 95\% CI [$-$0.55, 0.16]); configuration-level comparisons should hold the base model fixed.'
needle=r'\paragraph{Lessons from deployment.}'+'\n';assert s.count(needle)==1;s=s.replace(needle,needle+lesson+'\n',1);changes.append({'item':'First deployment lesson','before':needle.strip(),'after':needle+lesson})
# Preserve code listings and all existing math spans; format only signed numbers in prose/tables.
parts=re.split(r'(\\begin\{lstlisting\}.*?\\end\{lstlisting\}|\$[^$]*\$|\\\(.*?\\\)|\\\[.*?\\\])',s,flags=re.S);negatives=[]
for i,part in enumerate(parts):
 if i%2:continue
 def fix(m):
  negatives.append({'before':m.group(0),'after':'$-$'+m.group(0)[1:]});return '$-$'+m.group(0)[1:]
 parts[i]=re.sub(r'(?<![A-Za-z0-9_\\\-−])[-−]\d+(?:\.\d+)?',fix,part)
s=''.join(parts)
for p in B.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(B)
 if rel.name=='main.tex':continue
 dest=P/rel;dest.parent.mkdir(parents=True,exist_ok=True);os.link(p,dest)
(P/'main.tex').write_text(s);report={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_project':str(B),'new_project':str(P),'base_main_sha256':hashlib.sha256((B/'main.tex').read_bytes()).hexdigest(),'main_sha256':hashlib.sha256((P/'main.tex').read_bytes()).hexdigest(),'lesson':lesson,'lesson_values_verified_against_I004_I010':True,'negative_sign_replacements':negatives,'count':len(negatives),'changes':changes,'runtime_paragraph_not_yet_shortened':True,'all_other_files_unchanged':True};(P/'revision_evidence/MATCH_MODELS_CHANGES.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('Created copy; numeric minus replacements:',len(negatives))
