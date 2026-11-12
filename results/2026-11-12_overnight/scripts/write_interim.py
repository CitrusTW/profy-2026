"""Half-page checkpoint from completed records, without performance conclusions."""
import datetime,json,time
from pathlib import Path
R=Path(__file__).resolve().parent
def main():
 assert time.time()>=json.loads((R/'I002_TIME_WINDOW.json').read_text())['interim_report_epoch']
 p=R/'INTERIM_REPORT.md'
 if p.exists():return
 paths=sorted((R/'analysis_snapshots').glob('*/results.json'));s=json.loads(paths[-1].read_text());a=json.loads((R/'adv_i004_analysis_v2/results.json').read_text());c=json.loads((R/'adv_i004_context_analysis/results.json').read_text());rows=[x for x in s['attempts'] if not x['historical_reused']]
 fresh=[x for x in s['task_statuses'] if x['task'] not in ['energy-market-pricing','protein-expression-analysis']];n=sum(x['status']=='complete' for x in fresh);scored=sum(x['status']=='scored' for x in rows)
 text='# 08:00中期报告 (只报初步数字)\n\n截至'+datetime.datetime.now(datetime.timezone.utc).isoformat()+', 预选8题中有'+str(n)+'道完成三组完整评分; 新有效评分记录'+str(scored)+'份. 旧shock-demand两组和此前energy/protein结果保留, 没有重新求解. 各次失败、上限和未开跑记录另列, 不填成已完成.\n\n'
 text+='| 组别 | 新有效评分份数 |\n|---|---:|\n'
 for label in ['no-skills','with-skills','with-CogniLife-skills']:text+='| '+label+' | '+str(sum(x['condition']==label and x['status']=='scored' for x in rows))+' |\n'
 means=a['means'];cs=['generic_llm_raw','generic_llm_expert_prompt','profy_expert_full'];d=a['full_minus_baseline'][cs[1]]['overall']
 text+='\nADV20: 新Claude评分三组overall依次为'+ '/'.join(f'{means[k]["overall"]:.2f}' for k in cs)+'; Full减Expert Prompt为'+f'{d["mean"]:.2f}, 95%CI[{d["bootstrap95"][0]:.2f},{d["bootstrap95"][1]:.2f}]'+'. 正反都Full赢: 对Expert Prompt '+str(a['pairwise'][cs[1]]['counts']['both_full_wins'])+'/20, 对Raw '+str(a['pairwise'][cs[0]]['counts']['both_full_wins'])+'/20. 生成模型不同, 此处不作机制收益结论.\n'
 if not (R/'PROFY_RECOVERED_I004.json').exists():text+='\nProfy仍因Expert is not published受阻, 按I004每30分钟只探测原顺序下一次运行. 403不计实验次数. '
 else:text+='\nProfy已出现非403返回, 状态和后续串行运行见STATUS. '
 text+='OpenRouter新评分实付合计USD'+c['actual_cost_usd']+'; Profy费用unknown. 未充值/购买. 继续执行, 原论文未改.\n'
 with p.open('x') as f:f.write(text)
 assert len(text)<1800,'Interim should stay compact'
if __name__=='__main__':main()
