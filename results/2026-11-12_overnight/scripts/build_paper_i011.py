"""User I011: evidence-bound final copy; no API calls and no original edits."""
from pathlib import Path
import os,json,re,hashlib,datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;BASE=R/'cognilife_rev_20261112_final_verified';TARGET=R/'cognilife_rev_20261112_i011';S=R/'i010/analysis/I010_RESULTS.json';C=R/'adv_i004_analysis_v2/results.json';CONDS=['generic_llm_raw','generic_llm_expert_prompt','profy_expert_full'];DIMS=['completeness','specificity','actionability','coherence','safety_boundary'];LEDGER=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not TARGET.exists();TARGET.mkdir();z=json.loads(S.read_text());s=z['same_model_results'];c=json.loads(C.read_text());assert s['complete_all_60_rubrics'];assert z['wording_rule']['same_model_advantage_supported'] is False
 def num(which,*keys,d=None):
  src=S if which=='s' else C;v=z if which=='s' else c;path=(['same_model_results'] if which=='s' else [])+list(keys)
  for k in path:v=v[k]
  out=str(v) if d is None else f'{v:.{d}f}';LEDGER.append({'source':str(src),'source_sha256':sha(src),'item':path,'raw':v,'displayed':out});return out
 def mean(c,dim):return num('s','means',c,dim,d=2)
 def count(c,tag):
  # An unobserved returned tag has count0; absence is not a missing judgment.
  if tag not in s['error_tags'][c]:return '0'
  return num('s','error_tags',c,tag)
 n=num('s','planned_tasks');text=(BASE/'main.tex').read_text();original=text
 # Copy only immutable compilation assets; never mutate shared links.
 for p in BASE.rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(BASE)
  if rel.parts[0]=='revision_evidence' or rel.name in ['main.tex','submitted_main.tex']:continue
  dst=TARGET/rel;dst.parent.mkdir(parents=True,exist_ok=True);os.link(p,dst)
 # Reframe empirical claims, preserving the framework and customs account.
 start=text.index('On 20 advising tasks, the platform-executed');end=text.index('A 52-task customs-extraction case study',start)
 text=text[:start]+('An evaluation of '+n+' advising tasks finds that the overall-score advantage over Expert Prompt is not retained with baselines using the same declared model; deployment observations identify evaluation, tool-execution, and promotion failure modes. ')+text[end:]
 # Describe framework+implemented controls and lessons without changing its scope.
 text=text.replace('We introduce \\system{}, a framework for continuous cognitive distillation in multi-expert agent marketplaces.','We introduce \\system{}, a framework for continuous cognitive distillation in multi-expert agent marketplaces, and examine its implemented controls and deployment lessons.',1)
 a=text.index('\\item \\textbf{Service and workflow analysis.}');b=text.index('\n',a)
 text=text[:a]+r'\item \textbf{Deployment evaluation and lessons.} We compare saved platform responses with cross-model and model-label-matched baselines on '+n+' advising tasks; the latter does not retain an overall-score advantage over Expert Prompt. Frozen-skill execution and repeated customs extraction inform evaluation and promotion practice.'+text[b:]
 # Main protocol; legacy85 construction stays, detailed family focus moves unchanged to appendix.
 p0='The expert-service task set contains 85 instances across five production task families (Table~\\ref{tab:taskset-composition}), built from privacy-filtered public replay seeds or controlled internal tests. Each instance records its input and context slots, family, variant, source category, risk level, checkpoints, and evaluation dimensions. Checkpoints specify expected response components. Complete, missing-information, and adversarial variants probe deliverable quality, omitted constraints, fragmented inputs, and unsafe overconfidence.'
 p1='The expert-service task set contains 85 instances across five production families, built from privacy-filtered public replay seeds or controlled internal tests (Table~\\ref{tab:taskset-composition}). Records contain input/context slots, family, variant, source category, risk level, checkpoints, and dimensions. Checkpoints define expected components; complete, missing-information, and adversarial variants probe deliverable quality, omitted constraints, fragmented inputs, and unsafe overconfidence.'
 assert p0 in text;text=text.replace(p0,p1)
 cap=re.search(r'\\caption\{Composition of the expert-service task set:.*?\}\n\\label\{tab:taskset-composition\}',text,re.S).group();focus=cap[cap.index('Evaluation focus by family'):cap.index('}\n\\label')]
 text=text.replace(cap,r'\caption{Composition of the 85-instance expert-service task set across five families and three variants (Complete / Missing-information / Adversarial). Family-specific evaluation focus appears in Appendix~\ref{app:robustness}.}\label{tab:taskset-composition}')
 st=text.index('We compare request-only \\textbf{Raw LLM}');en=text.index('\\subsection{Task Utility}',st)
 protocol=r'''We compare request-only \textbf{Raw LLM}, role-conditioned \textbf{Expert Prompt}, and \textbf{Full}: 20 saved ADV responses from a deployed expert called through the platform API, labelled \texttt{deepseek-v4-flash}. The platform assembles its configured context; injected contents were not logged. The other 65 Full-labelled responses are checkpoint-conditioned prompt-proxy outputs, excluded from this deployment comparison.

We retain the \texttt{moonshot-v1-128k} baselines and generate one new answer per baseline/task with \texttt{deepseek/deepseek-v4-flash}, using the original full-pipeline prompts, temperature 0.7 and a 4096-token cap. Full is unchanged; its exact serving revision is unknown. Both batches use \texttt{anthropic/claude-opus-5.5} and unchanged Listings~\ref{lst:rubric} and~\ref{lst:pairwise}, with output-hash binding; all three conditions are rescored within each batch. Overall averages five general dimensions. Appendix~\ref{app:robustness} gives full diagnostics and protocol details.

'''
 text=text[:st]+protocol+text[en:]
 st=text.index('\\subsection{Task Utility}');en=text.index('\\subsection{Runtime and Deployment Observations}',st)
 delta=num('s','full_minus_baseline',CONDS[1],'overall','mean',d=2);ci='['+num('s','full_minus_baseline',CONDS[1],'overall','bootstrap95',0,d=2)+', '+num('s','full_minus_baseline',CONDS[1],'overall','bootstrap95',1,d=2)+']'
 mainsec=r'\subsection{Task Utility}'+'\n\n'+r'Table~\ref{tab:v1-main-results} reports both batches. With model-label-matched baselines, Full minus Expert Prompt is '+delta+' (95\\% CI '+ci+'); the overall-score advantage is not retained. Model differences may partly explain the cross-model gap.\n\n'
 mainsec+=r'\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{3pt}\begin{tabular}{@{}lrrrrl@{}}\toprule Baselines & Raw & Prompt & Full & $\Delta$ & 95\% CI \\\midrule'+'\n'
 for w,label in [('c','Cross-model'),('s','Same-label')]:
  mainsec+=label+' & '+' & '.join(num(w,'means',x,'overall',d=2) for x in CONDS)+' & '+num(w,'full_minus_baseline',CONDS[1],'overall','mean',d=2)+' & ['+', '.join(num(w,'full_minus_baseline',CONDS[1],'overall','bootstrap95',i,d=2) for i in [0,1])+r'] \\'+'\n'
 mainsec+=r'\bottomrule\end{tabular}\caption{ADV overall means ($N{=}20$); $\Delta$: Full minus Expert Prompt. Unchanged Full responses are scored within each batch.}\label{tab:v1-main-results}\end{table}'+'\n\n'+r'\subsection{Task and Error Patterns}'+'\n\n'
 mainsec+='In the model-label-matched batch, Full has slightly higher descriptive means for safety ('+mean(CONDS[2],'safety_boundary')+' vs.\ '+mean(CONDS[1],'safety_boundary')+'/'+mean(CONDS[0],'safety_boundary')+') and evidence grounding ('+mean(CONDS[2],'evidence_grounding')+' vs.\ '+mean(CONDS[1],'evidence_grounding')+'/'+mean(CONDS[0],'evidence_grounding')+'), and fewer overclaiming ('+count(CONDS[2],'overclaiming')+' vs.\ '+count(CONDS[1],'overclaiming')+'/'+count(CONDS[0],'overclaiming')+') and hallucinated-evidence tags ('+count(CONDS[2],'hallucinated_evidence')+' vs.\ '+count(CONDS[1],'hallucinated_evidence')+'/'+count(CONDS[0],'hallucinated_evidence')+'); comparisons are against Expert Prompt/Raw, respectively. Completeness and actionability are lower. These are descriptive differences on '+n+r' tasks with limited sample size; all dimensions and tags appear in Appendix~\ref{app:robustness}.'+'\n\n'+r'\subsection{LLM Preferences}'+'\n\n'
 pw=s['pairwise'][CONDS[1]]['counts'];mainsec+='Against same-label Expert Prompt, both orders favor Full on '+num('s','pairwise',CONDS[1],'counts','both_full_wins')+' tasks and the baseline on '+num('s','pairwise',CONDS[1],'counts','both_baseline_wins')+'; '+num('s','pairwise',CONDS[1],'counts','opposite_winners')+' flip, and '+num('s','pairwise',CONDS[1],'counts','missing_order')+r' lacks an order (Figure~\ref{fig:adv-counterbalanced}).'+'\n\n'
 mainsec+=r'''\begin{figure}[t]\centering
\includegraphics[width=\linewidth]{figures/adv_i011_matched_pairwise.pdf}
\caption{Same-label ADV preferences ($n{=}20$). Judge: \texttt{anthropic/claude-opus-5.5}; Full label: \texttt{deepseek-v4-flash}; baselines: \texttt{deepseek/deepseek-v4-flash}. Each output is limited to its first 3000 characters.}\label{fig:adv-counterbalanced}\end{figure}

'''
 text=text[:st]+mainsec+text[en:]
 # New operational lesson is anchored to same-model batch, not the old scores.
 needle='The design lesson is to separate observation, revision, and release:'
 lesson=r'\textbf{Record tool failures separately.} The judge assigns \texttt{tool\_failure} to '+count(CONDS[2],'tool_failure')+'/'+n+' platform Full responses; deployment evaluation should separately log and report tool-execution failures.\n'
 assert text.count(needle)==1;text=text.replace(needle,lesson+needle,1)
 oldlim='Full and the baselines use different generation models, and the new Claude judge differs from the original recorded judge; these scores cannot isolate memory or evolution effects.'
 newlim='The historical comparison uses different generation models; model-label matching cannot verify the platform serving revision or control its context and generation settings. The earlier baseline requests are unavailable, and the two source scripts differ by an uncertainty warning; we freeze the full-pipeline template before generation. These comparisons cannot isolate memory or evolution effects.'
 assert oldlim in text;text=text.replace(oldlim,newlim)
 text=text.replace('Pairwise judges see only output prefixes.','Pairwise judges see only output prefixes; one matched-baseline order remains missing after registered retries.',1)
 # Preserve old diagnostics verbatim but identify their batch; add all general dimensions.
 text=text.replace('New ADV diagnostics use the hash-bound Claude evaluation of the saved platform responses. No old Full scores are used.', 'The first tables report the cross-model batch; the model-label-matched batch is reported separately below. Both use hash-bound Claude evaluation of the saved platform responses. No historical proxy scores enter these comparisons. '+focus,1)
 def table(headers,rows,caption,label=None):
  body=r'\begin{table}[H]\centering\scriptsize\begin{tabular}{@{}'+'l'+'r'*(len(headers)-1)+r'@{}}\toprule '+' & '.join(headers)+r' \\\midrule'+'\n'
  body+='\n'.join(' & '.join(row)+r' \\' for row in rows)+'\n'+r'\bottomrule\end{tabular}\caption{'+caption+'}'+(r'\label{'+label+'}' if label else '')+r'\end{table}'+'\n\n';return body
 # All cross-model five general dimensions were previously in main table; retained here.
 app=table(['Dimension','Raw','Prompt','Full'],[[d.replace('_',r'\_')]+[num('c','means',x,d,d=2) for x in CONDS] for d in DIMS],'Cross-model batch: all five general dimensions.')
 app+=r'\subsection{Model-Label-Matched ADV Control}'+'\n\n'
 app+=r'''The requested baseline model is \texttt{deepseek/deepseek-v4-flash}, catalog revision \texttt{deepseek-v4-flash-20260423}. The historical platform records contain only \texttt{deepseek-v4-flash}; its revision and provider are unknown. Each baseline has one new response per task, using the original full-pipeline template, temperature 0.7 and max\_tokens 4096. That template adds an uncertainty warning omitted by the standalone script; historical request logs cannot resolve which template generated the earlier Moonshot baselines. Generator inputs contain no checkpoints. The existing Full outputs are unchanged.

All conditions use the same unchanged judge templates and parser. Rubric max\_tokens is 4096; pairwise is 1024 with the first 3000 characters per answer. Only an outer JSON code fence is removed; judge temperature is omitted because unsupported, and its effective value is unknown. Every judgment is bound to its output hash. Paired-task bootstrap uses 10000 resamples with seed 20261112. Missing judgments are not imputed.

'''
 app+=table(['Dimension','Raw','Prompt','Full'],[[d.replace('_',r'\_')]+[num('s','means',x,d,d=2) for x in CONDS] for d in ['overall']+DIMS+['evidence_grounding','uncertainty_calibration']],'Model-label-matched batch: overall and every rubric dimension.','tab:i011-matched-dimensions')
 tags=sorted(set(t for x in CONDS for t in s['error_tags'][x]));app+=table(['Error tag','Raw','Prompt','Full'],[[t.replace('_',r'\_')]+[count(x,t) for x in CONDS] for t in tags],'Model-label-matched batch: every returned error tag; zero means not observed.','tab:i011-matched-tags')
 paired=[]
 for b,label in [(CONDS[0],'Raw'),(CONDS[1],'Prompt')]:
  for d in ['overall']+DIMS:
   paired.append([label+'/'+d.replace('_',r'\_'),num('s','full_minus_baseline',b,d,'mean',d=2),'['+', '.join(num('s','full_minus_baseline',b,d,'bootstrap95',i,d=2) for i in [0,1])+']']+[num('s','full_minus_baseline',b,d,k) for k in ['higher','lower','tie']])
 # String-bearing CI column uses l instead of r for predictable width.
 app+=table(['Base/dimension','Mean','95\% CI','Higher','Lower','Tied'],paired,'All model-label-matched Full-minus-baseline paired differences; all five general dimensions retained.')
 variants=[]
 for v,x in z['variant_results'].items():variants.append([v.replace('_',r'\_'),str(x['n_tasks'])]+[f'{x["conditions"][c]["overall_mean"]:.2f}' for c in CONDS])
 app+=table(['Variant','N','Raw','Prompt','Full'],variants,'Model-label-matched ADV overall means by input variant, including missing-information and adversarial tasks.')
 pairs=[]
 for w,data in [('Cross',c),('Matched',s)]:
  for b,label in [(CONDS[0],'Raw'),(CONDS[1],'Prompt')]:
   q=data['pairwise'][b];co=q['counts'];pairs.append([w+'/'+label]+[str(co[k]) for k in ['both_full_wins','both_baseline_wins','opposite_winners','missing_order']]+[f'{q["A_choice_fraction_all"]:.3f}',f'{q["position_consistency_fraction"]:.3f}'])
 app+=table(['Batch/base','Full','Base','Flip','Missing','A frac.','Consist.'],pairs,'Both-order counts, observed A-choice fractions and winner-identity consistency. No tied preferences occurred; missing orders stay unknown.')
 audit=json.loads((R/'i010/INTEGRITY_AUDIT.json').read_text());calls=[json.loads(x) for x in (R/'i010/ALL_CALLS.jsonl').read_text().splitlines()];judges=[x for x in calls if x['kind']!='generation'];dates=[x['started_utc'] for x in judges]
 app+='The batch has '+str(audit['valid_records_by_kind']['generation'])+' saved baseline responses, '+str(audit['valid_records_by_kind']['rubric'])+' valid rubric judgments and '+str(audit['valid_records_by_kind']['pairwise'])+' valid pairwise orders. ADV\\_002, Full versus Expert Prompt with Full in A, failed all '+str(sum(x['parse_failed'] for x in judges))+' allowed attempts through length-limited judge output; the order remains missing. ADV\\_004 Raw is nonempty but reached its original generation cap; it was not regenerated. The requested and returned judge model is \\texttt{anthropic/claude-opus-5.5}; calls span '+min(dates)+' to '+max(x['completed_utc'] for x in judges)+'. All raw requests, responses, failures and hashes are retained.\n\n'
 app+=r'\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figures/adv_i011_both_batches_pairwise.pdf}\caption{Both batches, with all outcome categories and missing orders shown. Each batch contains 20 ADV tasks, judged by \texttt{anthropic/claude-opus-5.5} on output prefixes of 3000 characters.}\end{figure}'+'\n\n'
 text=text.replace('\\section{Evaluation Prompts}',app+'\\section{Evaluation Prompts}',1)
 # Generate plots directly from counts; missing is its own category, never a loss.
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7,'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False});plotdata=[]
 for matched_only,name in [(True,'adv_i011_matched_pairwise'),(False,'adv_i011_both_batches_pairwise')]:
  datasets=[('Matched',s)] if matched_only else [('Cross-model',c),('Matched',s)];labels=[];values=[]
  for label,data in datasets:
   for b,title in [(CONDS[1],'Expert Prompt'),(CONDS[0],'Raw LLM')]:
    co=data['pairwise'][b]['counts'];assert co['both_ties']==co['tie_mixed']==0;v=[co[k] for k in ['both_full_wins','opposite_winners','both_baseline_wins','missing_order']];values.append(v);labels.append(('vs '+title) if matched_only else label+' vs '+title);plotdata.append({'plot':name,'batch':label,'baseline':b,'counts':v})
  f,ax=plt.subplots(figsize=(3.3,1.32 if matched_only else 1.85));colors=['#0072B2','#E69F00','#D55E00','#999999']
  for i,v in enumerate(values):
   left=0
   for j,x in enumerate(v):
    ax.barh(i,x,left=left,height=.55,color=colors[j],label=['Full wins both','Order flips','Baseline wins both','Missing order'][j] if i==0 else None)
    if x:ax.text(left+x/2,i,str(x),ha='center',va='center',fontsize=6.5,color='black' if j==1 else 'white')
    left+=x
  ax.set_yticks(range(len(labels)),labels,fontsize=6.2);ax.invert_yaxis();ax.set_xlim(0,20);ax.set_xticks([0,5,10,15,20]);ax.set_xlabel('Number of ADV tasks');ax.tick_params(axis='y',length=0);ax.legend(loc='lower center',bbox_to_anchor=(.35,1.02),ncol=2,frameon=False,fontsize=5.9,columnspacing=.8,handlelength=.9);f.subplots_adjust(left=.29 if matched_only else .43,right=.98,bottom=.28 if matched_only else .21,top=.68 if matched_only else .76);f.savefig(TARGET/'figures'/(name+'.pdf'),bbox_inches='tight',pad_inches=.02);f.savefig(TARGET/'figures'/(name+'.png'),dpi=180,bbox_inches='tight',pad_inches=.02);plt.close(f)
 (TARGET/'main.tex').write_text(text);ev=TARGET/'revision_evidence';ev.mkdir();(ev/'NUMERIC_LEDGER_I011.json').write_text(json.dumps(LEDGER,indent=2));(ev/'INPUTS_I011.json').write_text(json.dumps({'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_project':str(BASE),'base_sha256':sha(BASE/'main.tex'),'main_sha256':sha(TARGET/'main.tex'),'source_results':{str(S):sha(S),str(C):sha(C)},'all_additional_table_data':z,'plot_data':plotdata,'framework_and_customs_preserved':True,'negative_same_model_result_integrated':True,'no_new_paid_calls':True,'draft2_review_textfixes_retained':True},ensure_ascii=False,indent=2))
 print('I011_SOURCE_READY',TARGET)
if __name__=='__main__':main()
