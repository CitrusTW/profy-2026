"""Data-bound manuscript copy for I010. Run only after status reports results."""
import argparse,hashlib,json,os,re,shutil
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent;R=O.parent;BASE=R/'cognilife_rev_20261112_draft2_ready';CON=['generic_llm_raw','generic_llm_expert_prompt','profy_expert_full'];DIMS=['completeness','specificity','actionability','coherence','safety_boundary']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--analysis',required=True);p.add_argument('--target',required=True);a=p.parse_args();source=Path(a.analysis);z=json.loads(source.read_text());same=z['same_model_results'];crosspath=R/'adv_i004_analysis_v2/results.json';cross=json.loads(crosspath.read_text());assert z['wording_rule']['complete'];assert (O/'RESULTS_REPORTED_IN_STATUS.json').exists(),'Report to status before paper edits';target=Path(a.target);assert not target.exists();ledger=[]
 def val(cohort,*keys,d=None):
  file=source if cohort=='same' else crosspath;root=z if cohort=='same' else cross;kk=(['same_model_results'] if cohort=='same' else [])+list(keys);v=root
  for k in kk:v=v[k]
  display=str(v) if d is None else f'{v:.{d}f}';ledger.append({'source':str(file),'source_sha256':sha(file),'item':kk,'raw':v,'displayed':display});return display
 n=val('same','planned_tasks');wins=val('same','pairwise',CON[1],'counts','both_full_wins');diff=lambda which:val(which,'full_minus_baseline',CON[1],'overall','mean',d=2);ci=lambda which:'['+val(which,'full_minus_baseline',CON[1],'overall','bootstrap95',0,d=2)+', '+val(which,'full_minus_baseline',CON[1],'overall','bootstrap95',1,d=2)+']'
 supported=z['wording_rule']['same_model_advantage_supported'];text=(BASE/'main.tex').read_text();changes=[]
 # A new copy shares immutable compilation assets; main.tex is newly written.
 target.mkdir()
 for p in BASE.rglob('*'):
  rel=p.relative_to(BASE)
  if p.is_dir():continue
  if rel.parts[0]=='revision_evidence' or rel.name in ['main.tex','submitted_main.tex']:continue
  dest=target/rel;dest.parent.mkdir(parents=True,exist_ok=True);os.link(p,dest)
 fig=target/'figures';plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7,'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
 figdata=[];labs=[];triples=[]
 for cohort,data in [('Cross-model',cross),('Same-label',same)]:
  for c,label in [(CON[1],'Expert Prompt'),(CON[0],'Raw LLM')]:
   co=data['pairwise'][c]['counts'];assert co['missing_order']==0
   values=[co[k] for k in ['both_full_wins','opposite_winners','both_baseline_wins']]+[co['both_ties']+co['tie_mixed']];triples.append(values);labs.append(cohort+' vs '+label);figdata.append({'cohort':cohort,'baseline':c,'counts':values})
 f,ax=plt.subplots(figsize=(3.3,1.62));colors=['#0072B2','#E69F00','#D55E00','#999999']
 for i,values in enumerate(triples):
  left=0
  for j,v in enumerate(values):
   ax.barh(i,v,left=left,color=colors[j],height=.56,label=['Full wins both','Order flips','Baseline wins both','Tie involved'][j] if i==0 and (j<3 or any(v[3] for v in triples)) else None)
   if v:ax.text(left+v/2,i,str(v),ha='center',va='center',color='white' if j!=1 else 'black',fontsize=6.6)
   left+=v
 ax.set_yticks(range(4),labs,fontsize=6.1);ax.invert_yaxis();ax.set_xlim(0,20);ax.set_xticks([0,5,10,15,20]);ax.set_xlabel('Number of ADV tasks',fontsize=7);ax.tick_params(axis='y',length=0);ax.legend(loc='lower center',bbox_to_anchor=(.40,1.04),ncol=2 if any(v[3] for v in triples) else 3,frameon=False,fontsize=5.6,columnspacing=.5,handlelength=.8);f.subplots_adjust(left=.41,right=.98,bottom=.25,top=.80)
 f.savefig(fig/'adv_i010_pairwise.pdf',bbox_inches='tight',pad_inches=.02);f.savefig(fig/'adv_i010_pairwise.png',dpi=180,bbox_inches='tight',pad_inches=.02);plt.close(f)
 # Primary abstract and contribution follow the frozen decision rule.
 old=re.search(r'On 20 advising tasks,.*?A 52-task customs-extraction case study',text,re.S).group()
 if supported:
  claim='With baselines using the same declared base model, the platform-executed configuration retains an overall-score advantage and wins both pairwise orders against Expert Prompt on '+wins+'/'+n+' advising tasks. '
  contribution='With same-declared-model baselines, the deployed configuration retains an overall-score advantage on '+n+' advising tasks and wins both pairwise orders against Expert Prompt on '+wins+'/'+n+' tasks.'
 else:
  claim='On '+n+' advising tasks, the advantage shrinks or is not significant when baselines use the same declared base model; model differences may partly explain the cross-model gap. '
  contribution='On '+n+' advising tasks, the advantage shrinks or is not significant with same-declared-model baselines; model differences may partly explain the cross-model gap.'
 text=text.replace(old,claim+'A 52-task customs-extraction case study',1);st=text.index('\\item \\textbf{Service and workflow analysis.}');en=text.index('\n',st);text=text[:st]+r'\item \textbf{Service and workflow analysis.} '+contribution+' We also examine frozen-skill execution and repeated customs extraction.'+text[en:]
 old='The new judge is';st=text.index(old);en=text.index('\\subsection{Task Utility}',st)
 text=text[:st]+r'''We retain the Moonshot-baseline comparison and add a model-label-matched control: each ADV task receives one new Raw and Expert Prompt answer from \texttt{deepseek/deepseek-v4-flash}, using the original baseline prompts, temperature 0.7, and 4096-token cap. Full is not regenerated; its exact serving revision is unknown. The judge remains \texttt{anthropic/claude-opus-5.5}, with unchanged Listings~\ref{lst:rubric} and~\ref{lst:pairwise}; all three conditions are judged anew within the control batch, with output-hash binding. Overall averages completeness, specificity, actionability, coherence, and safety-boundary adherence; full diagnostics appear in Appendix~\ref{app:robustness}.

'''+text[en:]
 st=text.index('\\subsection{Task Utility}');en=text.index('\\subsection{Runtime and Deployment Observations}',st)
 section=r'''\subsection{Task Utility}

Table~\ref{tab:v1-main-results} reports both comparisons. '''
 section+=('The Full-minus-Expert-Prompt difference remains positive with same-declared-model baselines: '+diff('same')+' (95\\% CI '+ci('same')+').' if supported else 'With same-declared-model baselines, the Full-minus-Expert-Prompt difference is '+diff('same')+' (95\\% CI '+ci('same')+'); the advantage shrinks or is not significant, so model differences may partly explain the cross-model gap.')
 section+='\n\n'+r'\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{3pt}\begin{tabular}{@{}lrrrrl@{}}\toprule Baselines & Raw & Prompt & Full & $\Delta$ & 95\% CI \\\midrule'+'\n'
 for which,name in [('cross','Moonshot'),('same','DeepSeek')]:section+=name+' & '+' & '.join(val(which,'means',c,'overall',d=2) for c in CON)+' & '+diff(which)+' & '+ci(which)+r' \\'+'\n'
 section+=r'\bottomrule\end{tabular}\caption{ADV overall means ($N{=}20$). $\Delta$: Full minus Expert Prompt. Full is rescored within each batch; its saved answers are unchanged.}\label{tab:v1-main-results}\end{table}'+'\n\n'
 section+=r'\subsection{Task and Error Patterns}'+'\n\n'+r'Appendix~\ref{app:robustness} reports all dimensions, variants, and error tags in both comparisons, including negative or tied effects. Model-label matching does not control platform configuration or verify its serving revision.'+'\n\n'+r'\subsection{LLM Preferences}'+'\n\n'
 for which,label in [('cross','Cross-model'),('same','Same-label')]:
  section+=label+' Full wins both orders on '+val(which,'pairwise',CON[1],'counts','both_full_wins')+'/'+n+' tasks versus Expert Prompt and '+val(which,'pairwise',CON[0],'counts','both_full_wins')+'/'+n+' versus Raw. '
 section+='\n\n'+r'''\begin{figure}[t]\centering
\includegraphics[width=\linewidth]{figures/adv_i010_pairwise.pdf}
\caption{Both-order preferences on 20 ADV tasks. Judge: \texttt{anthropic/claude-opus-5.5}; Full label: \texttt{deepseek-v4-flash}; cross-model baselines: \texttt{moonshot-v1-128k}; same-label baselines: \texttt{deepseek/deepseek-v4-flash}. Each output is limited to its first 3000 characters.}\label{fig:adv-counterbalanced}\end{figure}

'''
 text=text[:st]+section+text[en:]
 # Keep I004 appendices intact and append complete I010 diagnostics before protocol listings.
 app=r'\subsection{Model-Label-Matched ADV Control}'+'\n\n'+r'The control uses new DeepSeek baseline responses and unchanged platform Full responses; all are rescored in a single new batch. The exact historical platform model revision is unavailable. The baseline template from the original full-pipeline script includes an uncertainty warning omitted by the standalone script; that choice was frozen before generation. Sampling is temperature 0.7 with a 4096-token cap. No generation input contains checkpoints. Rubric output budget is 4096; pairwise output budget is 1024, with a 3000-character prefix per answer. Parser and judge are unchanged.'+'\n\n'
 app+=r'\begin{table}[H]\centering\scriptsize\begin{tabular}{@{}lrrr@{}}\toprule Dimension & Raw & Prompt & Full \\\midrule'+'\n'
 for d in ['overall']+DIMS+['evidence_grounding','uncertainty_calibration']:app+=d.replace('_',r'\_')+' & '+' & '.join(val('same','means',c,d,d=2) for c in CON)+r' \\'+'\n'
 app+=r'\bottomrule\end{tabular}\caption{I010 same-declared-model ADV means.}\end{table}'+'\n\n'
 app+=r'\begin{table}[H]\centering\scriptsize\begin{tabular}{@{}llrrr@{}}\toprule Baseline / dimension & Mean [95\% CI] & Higher & Lower & Tied \\\midrule'+'\n'
 for c,label in [(CON[0],'Raw'),(CON[1],'Prompt')]:
  for d in ['overall']+DIMS:
   mean=val('same','full_minus_baseline',c,d,'mean',d=2);interval='['+val('same','full_minus_baseline',c,d,'bootstrap95',0,d=2)+', '+val('same','full_minus_baseline',c,d,'bootstrap95',1,d=2)+']';app+=label+'/'+d.replace('_',r'\_')+' & '+mean+' '+interval+' & '+' & '.join(val('same','full_minus_baseline',c,d,k) for k in ['higher','lower','tie'])+r' \\'+'\n'
 app+=r'\bottomrule\end{tabular}\caption{All I010 paired differences, including all five general dimensions.}\end{table}'+'\n\n'
 app+=r'\begin{table}[H]\centering\scriptsize\begin{tabular}{@{}lrrrrr@{}}\toprule Baseline & Full both & Base both & Flip & Ties & A frac. \\\midrule'+'\n'
 for c,label in [(CON[0],'Raw'),(CON[1],'Prompt')]:app+=label+' & '+' & '.join(val('same','pairwise',c,'counts',k) for k in ['both_full_wins','both_baseline_wins','opposite_winners'])+' & '+str(same['pairwise'][c]['counts']['both_ties']+same['pairwise'][c]['counts']['tie_mixed'])+' & '+val('same','pairwise',c,'A_choice_fraction_all',d=3)+r' \\'+'\n'
 app+=r'\bottomrule\end{tabular}\caption{I010 counterbalanced preferences. Ties includes both ties and mixed-tie tasks; complete order counts are preserved.}\end{table}'+'\n\n'
 app+=r'\begin{table}[H]\centering\scriptsize\begin{tabular}{@{}lrrrr@{}}\toprule Variant & N & Raw & Prompt & Full \\\midrule'+'\n'
 for variant,x in z['variant_results'].items():app+=variant.replace('_',r'\_')+' & '+str(x['n_tasks'])+' & '+' & '.join(f'{x["conditions"][c]["overall_mean"]:.2f}' for c in CON)+r' \\'+'\n'
 app+=r'\bottomrule\end{tabular}\caption{I010 ADV variants; missing-information and adversarial cases are retained.}\end{table}'+'\n\n'
 app+=r'\begin{table}[H]\centering\scriptsize\begin{tabular}{@{}lrrr@{}}\toprule Error tag & Raw & Prompt & Full \\\midrule'+'\n'
 tags=sorted(set(t for c in CON for t in same['error_tags'][c]))
 for tag in tags:app+=tag.replace('_',r'\_')+' & '+' & '.join(str(same['error_tags'][c].get(tag,0)) for c in CON)+r' \\'+'\n'
 app+=r'\bottomrule\end{tabular}\caption{All I010 returned error tags.}\end{table}'+'\n\n'
 audit=z['generation_audit'];app+='Generation produced '+str(sum(x['n'] for x in audit.values()))+' saved baseline responses, with '+str(sum(x['empty'] for x in audit.values()))+' empty and '+str(sum(x['length_limited'] for x in audit.values()))+' length-limited outputs; none were regenerated for quality. All raw requests, responses, failures, and output hashes are retained. Temperature for the judge remains omitted (effective value unknown); dates and exact returned model IDs are retained with each call.\n\n'
 text=text.replace('\\section{Evaluation Prompts}',app+'\\section{Evaluation Prompts}',1)
 # New matching addresses model-name difference but not serving/configuration confounds.
 text=text.replace('Full and the baselines use different generation models, and the new Claude judge differs from the original recorded judge;', 'The historical comparison uses different generation models; the new control matches the declared model label without verifying the platform serving revision;')
 text=text.replace('New ADV diagnostics use the hash-bound Claude evaluation of the saved platform responses. No old Full scores are used.', 'The following tables first report the I004 cross-model batch; the model-label-matched I010 batch is presented separately below. Both use hash-bound Claude evaluations; historical proxy scores are excluded.')
 (target/'main.tex').write_text(text);ev=target/'revision_evidence';ev.mkdir();shutil.copyfile(BASE/'revision_evidence/NUMERIC_LEDGER.json',ev/'PRIOR_NUMERIC_LEDGER.json');shutil.copyfile(BASE/'revision_evidence/PROXY85_ARCHIVE_PROVENANCE.json',ev/'PROXY85_ARCHIVE_PROVENANCE.json')
 (ev/'I010_ADDITIONAL_TABLE_SOURCES.json').write_text(json.dumps({'source_results':str(source),'source_sha256':sha(source),'variant_tables':'variant_results','error_tag_tables':'same_model_results.error_tags','generation_counts':'generation_audit','all_raw_numeric_inputs':z},indent=2))
 (ev/'I010_NUMERIC_LEDGER.json').write_text(json.dumps(ledger,indent=2));(ev/'I010_INPUTS.json').write_text(json.dumps({'source_results':str(source),'source_sha256':sha(source),'new_main_sha256':sha(target/'main.tex'),'base_main_sha256':sha(BASE/'main.tex'),'wording_rule':z['wording_rule'],'figure_data':figdata,'full_not_regenerated':True,'original_project_not_modified':True,'scope':'Same-declared-model control; exact historical Full serving revision unknown'},indent=2));print(target)
if __name__=='__main__':main()
