"""I009: clean ADV plots directly from frozen analysis JSON, no API calls."""
import argparse,hashlib,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def main(a):
 source=Path(a.results).resolve();x=json.loads(source.read_text());out=Path(a.out).resolve();out.mkdir(exist_ok=False)
 assert x['complete_all_60_rubrics'] and x['complete_all_80_pairwise'];n=x['planned_tasks'];bases=['generic_llm_expert_prompt','generic_llm_raw'];rows=[]
 for base in bases:
  z=x['pairwise'][base]['counts'];assert z['both_ties']==z['tie_mixed']==z['missing_order']==0
  values=[z['both_full_wins'],z['opposite_winners'],z['both_baseline_wins']];assert sum(values)==n
  rows.append({'baseline':base,'counts':values,'fields':['both_full_wins','opposite_winners','both_baseline_wins']})
 dims=['completeness','specificity','actionability','coherence','safety_boundary'];effects=[{'dimension':d,**x['full_minus_baseline']['generic_llm_expert_prompt'][d]} for d in dims];assert len(effects)==5
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':8,'legend.fontsize':6.8,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42,'savefig.dpi':300})
 fig,ax=plt.subplots(figsize=(3.3,1.38));fig.subplots_adjust(left=.34,right=.965,bottom=.27,top=.72);left=np.zeros(2);colors=['#0072B2','#E69F00','#D55E00'];labels=['Full wins both','Order flips','Baseline wins both']
 for i,(color,label) in enumerate(zip(colors,labels)):
  widths=np.array([r['counts'][i] for r in rows]);bars=ax.barh(np.arange(2),widths,left=left,height=.5,color=color,edgecolor='white',linewidth=.45,label=label)
  for y,(v,l) in enumerate(zip(widths,left)):ax.text(l+v/2,y,str(v),ha='center',va='center',color='black' if i==1 else 'white',fontsize=8)
  left+=widths
 ax.set_yticks([0,1],['vs Expert Prompt','vs Raw LLM']);ax.invert_yaxis();ax.set_xlim(0,n);ax.set_xticks(np.linspace(0,n,5));ax.set_xlabel('Number of ADV tasks');ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False);ax.grid(axis='x',alpha=.12);ax.set_axisbelow(True);fig.legend(*ax.get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.51,1.015),ncol=3,columnspacing=.65,handlelength=.8,handletextpad=.35,frameon=False)
 for ext in ['pdf','png']:fig.savefig(out/f'adv_counterbalanced_pairwise.{ext}',bbox_inches='tight',pad_inches=.02,metadata={'Author':'','Title':'Counterbalanced ADV preferences'} if ext=='pdf' else None)
 plt.close(fig)
 fig,ax=plt.subplots(figsize=(3.3,2.0));fig.subplots_adjust(left=.34,right=.98,bottom=.25,top=.97);means=np.array([d['mean'] for d in effects]);lo=np.array([d['bootstrap95'][0] for d in effects]);hi=np.array([d['bootstrap95'][1] for d in effects]);ax.axvline(0,color='#555555',linewidth=.8,linestyle='--');ax.errorbar(means,np.arange(5),xerr=np.vstack([means-lo,hi-means]),fmt='o',color='#0072B2',markersize=3.8,capsize=2,linewidth=1.1);ax.set_yticks(range(5),['Completeness','Specificity','Actionability','Coherence','Safety']);ax.invert_yaxis();ax.set_xlabel('Full minus Expert Prompt');ax.set_xlim(min(lo)-.15,max(hi)+.15);ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True);ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False)
 for ext in ['pdf','png']:fig.savefig(out/f'adv_all_dimensions.{ext}',bbox_inches='tight',pad_inches=.02,metadata={'Author':'','Title':'All five ADV dimension differences'} if ext=='pdf' else None)
 plt.close(fig)
 with (out/'PLOT_DATA.json').open('x') as f:json.dump({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'n_tasks':n,'pairwise_category_order':labels,'pairwise_rows':rows,'all_five_dimension_effects':effects,'judge':x['judge'],'no_category_or_dimension_omitted':True,'API_calls':0},f,indent=2)
 print(json.dumps({'out':str(out),'pairwise_counts':[r['counts'] for r in rows],'dimension_means':means.tolist()}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--results',required=True);p.add_argument('--out',required=True);main(p.parse_args())
