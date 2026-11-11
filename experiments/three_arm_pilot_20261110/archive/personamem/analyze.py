"""Score after execution, using untouched original option-matching function."""
import collections,csv,hashlib,itertools,json,random,statistics,sys
from pathlib import Path
from study import OUT,CONDITIONS,load,save,dumps,digest,nt

def percentile(xs,p):
    xs=sorted(xs);k=(len(xs)-1)*p;a=int(k);return xs[a]+(xs[min(a+1,len(xs)-1)]-xs[a])*(k-a)

def main():
    assert load(OUT/'dev_gate.json')['passed'], 'Do not inspect outcomes to tune a failed interface gate.'
    cases=[x for x in load(OUT/'cases.json') if x['split']=='main']
    refs=load(OUT/'references.json');ns={};exec((OUT/'official_extract_answer.py').read_text(),ns)
    score=ns['extract_answer'];rows=[];bycase={};pairs=collections.defaultdict(list)
    for c in cases:
        bycase[c['case_id']]={};pairs[c['pair_id']].append(c)
        for condition in CONDITIONS:
            p=OUT/'answers'/(c['case_id']+'_'+condition+'.json')
            a=load(p) if p.exists() else {'completed':False,'error':'not_executed','response':''}
            ok,pred=score(None,a.get('response',''),refs[c['case_id']])
            correct=int(ok and a.get('completed',False));bycase[c['case_id']][condition]=correct
            rows.append({**{k:c[k] for k in ['case_id','question_id','persona_id','pair_id','question_type']},'condition':condition,'completed':a.get('completed',False),'correct':correct,'correct_answer':refs[c['case_id']],'predicted_answer':pred,'error':a.get('error'),'response':a.get('response',''),'guidance_tokens':a.get('guidance_tokens'), 'reader_elapsed_s':a.get('elapsed_s'),'reader_call_id':a.get('reader_call_id'),'writer_call_id':a.get('writer_call_id')})
    with (OUT/'scored_results.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    pair_ids=sorted(pairs);assert len(pair_ids)==9 and len(cases)==180
    block={p:{k:statistics.mean(bycase[c['case_id']][k] for c in pairs[p]) for k in CONDITIONS} for p in pair_ids}
    rng=random.Random(20261110);draws=[[rng.choice(pair_ids) for _ in pair_ids] for _ in range(20000)]
    def interval(values):
        bs=[statistics.mean(values[p] for p in draw) for draw in draws]
        return [percentile(bs,.025),percentile(bs,.975)]
    groups={}
    for k in CONDITIONS:
        rr=[r for r in rows if r['condition']==k]
        groups[k]={'questions':len(rr),'correct':sum(r['correct'] for r in rr),'accuracy':statistics.mean(r['correct'] for r in rr),'completed':sum(r['completed'] for r in rr),'failed_or_missing':sum(not r['completed'] for r in rr),'pair_bootstrap_95ci':interval({p:block[p][k] for p in pair_ids}),'mean_guidance_reference_tokens':statistics.mean(r['guidance_tokens'] for r in rr if r['guidance_tokens'] is not None) if any(r['guidance_tokens'] is not None for r in rr) else None}
    comparisons={}
    for name,a,b in [('primary_full_vs_summary','full','mixed_summary'),('source_component','full','no_source'),('scope_version_labels','full','no_scope'),('summary_interference','mixed_summary','clean_summary'),('full_vs_clean_reference','full','clean_summary')]:
        ds={p:block[p][a]-block[p][b] for p in pair_ids};observed=statistics.mean(ds.values())
        null=[statistics.mean(sign*ds[p] for sign,p in zip(signs,pair_ids)) for signs in itertools.product([-1,1],repeat=len(pair_ids))]
        pval=sum(abs(x)>=abs(observed)-1e-12 for x in null)/len(null)
        wins=sum(bycase[c['case_id']][a]>bycase[c['case_id']][b] for c in cases);losses=sum(bycase[c['case_id']][a]<bycase[c['case_id']][b] for c in cases)
        comparisons[name]={'a':a,'b':b,'difference':observed,'difference_percentage_points':observed*100,'pair_bootstrap_95ci':interval(ds),'wins':wins,'losses':losses,'ties':len(cases)-wins-losses,'two_sided_pair_signflip_p':pval,'independent_blocks':len(pair_ids)}
    # Conservative correction across the three method/component comparisons.
    keys=['primary_full_vs_summary','source_component','scope_version_labels'];ordered=sorted(keys,key=lambda k:comparisons[k]['two_sided_pair_signflip_p']);previous=0
    for i,k in enumerate(ordered):
        adj=max(previous,min(1,(len(keys)-i)*comparisons[k]['two_sided_pair_signflip_p']));comparisons[k]['holm_p']=adj;previous=adj
    types={}
    for typ in sorted({c['question_type'] for c in cases}):
        types[typ]={k:{'correct':sum(r['correct'] for r in rows if r['question_type']==typ and r['condition']==k),'n':sum(r['question_type']==typ and r['condition']==k for r in rows)} for k in CONDITIONS}
    calls=[load(p) for p in (OUT/'calls').glob('*/result.json')];usage=collections.Counter()
    for c in calls:usage.update(c.get('usage',{}))
    calls_by_kind={}
    for kind in sorted({c['kind'] for c in calls}):
        cc=[c for c in calls if c['kind']==kind]
        calls_by_kind[kind]={'calls':len(cc),'completed':sum(c['completed'] for c in cc),'elapsed_sum_s':sum(c['elapsed_s'] for c in cc),'median_elapsed_s':statistics.median(c['elapsed_s'] for c in cc)}
    byid={c['call_id']:c for c in calls};configuration_cost={}
    for condition in CONDITIONS:
        wk={'clean_summary':'summary_clean','mixed_summary':'summary_mixed'}.get(condition,'records_mixed')
        writer_ids={'w_'+c['prefix_key']+'_'+wk for c in cases}
        reader_ids={'r_'+c['case_id']+'_'+condition for c in cases}
        included=[byid[i] for i in writer_ids|reader_ids if i in byid];u=collections.Counter()
        for c in included:u.update(c.get('usage',{}))
        configuration_cost[condition]={'unique_writer_calls_present':sum(i in byid for i in writer_ids),'reader_calls_present':sum(i in byid for i in reader_ids),'native_tokens':dict(u),'elapsed_sum_s':sum(c['elapsed_s'] for c in included),'elapsed_amortized_per_question_s':sum(c['elapsed_s'] for c in included)/len(cases),'accounting':'standalone configuration: charge its unique preprocessing and reader calls; shared ledger reused by ablations, so these columns must not be summed as actual paid total'}
    observed_models=collections.Counter();tool_events=collections.Counter();writer_budget_violations=0
    for c in calls:
        if c['kind'].startswith('writer_') and nt(c.get('text',''))>4000:writer_budget_violations+=1
        ep=OUT/'calls'/c['call_id']/'events.jsonl'
        if ep.exists():
            for line in ep.read_text().splitlines():
                e=json.loads(line)
                if e.get('model_name'):observed_models[e['model_name']]+=1
                if str(e.get('type','')).startswith('tool_call.'):tool_events[e.get('type')]+=1
    existing_answers=list((OUT/'answers').glob('*.json'))
    input_diagnostics={}
    for condition in CONDITIONS:
        rendered=[load(OUT/'rendered_inputs'/('r_'+c['case_id']+'_'+condition+'.json')) for c in cases if (OUT/'rendered_inputs'/('r_'+c['case_id']+'_'+condition+'.json')).exists()]
        routed=[x['routing'] for x in rendered if x.get('routing')]
        input_diagnostics[condition]={'rendered_inputs':len(rendered),'empty_guidance':sum(not x['guidance'].strip() for x in rendered),'with_foreign_candidate_in_guidance':sum(x.get('foreign_candidates_included',0)>0 for x in routed),'mean_rendered_records':statistics.mean(x['rendered'] for x in routed) if routed else None,'slots_with_invalid_candidates_dropped':sum(bool(x['invalid_candidates']) for x in routed)}
    complete=len([p for p in existing_answers if any(p.name.startswith(c['case_id']+'_') for c in cases)])==900
    report={'execution_state':('completed' if all(g['failed_or_missing']==0 for g in groups.values()) else 'completed_with_recorded_failures') if complete else 'partial','original_questions':180,'synthetic_personas':18,'independent_donor_pairs':9,'groups':groups,'comparisons':comparisons,'by_question_type':types,'api_calls_total_including_dev':len(calls),'calls_by_kind':calls_by_kind,'standalone_configuration_cost':configuration_cost,'native_tokens_sum':dict(usage),'observed_model_labels':dict(observed_models),'tool_event_counts':dict(tool_events),'writer_instruction_budget_exceeded_calls':writer_budget_violations,'monetary_charge':'no auditable currency bill; not estimated from token prices','all_call_errors':dict(collections.Counter(c.get('error') for c in calls if c.get('error'))),'scored_results_sha256':hashlib.sha256((OUT/'scored_results.csv').read_bytes()).hexdigest()}
    report['actual_input_diagnostics']=input_diagnostics
    save(OUT/'analysis_summary.json',report)
    lines=['# 端到端归因实验: 实际结果','',f'状态: {report["execution_state"]}. 180道原题, 18个合成persona, 9个来源pair. 这是PersonaMem-v1的预先固定干扰条件实验, 不是官方完整589题成绩, 不验证产品内置Memory.', '', '| 条件 | 答对/180 | 正确率 | 执行完成 | 失败/缺失 |','| --- | --- | --- | --- | --- |']
    for k,g in groups.items():lines.append(f'| {k} | {g["correct"]}/180 | {100*g["accuracy"]:.2f}% | {g["completed"]} | {g["failed_or_missing"]} |')
    lines+=['','条件解释: clean_summary只总结目标人物; mixed_summary面对两个人的历史, 仍要求只总结目标人物, 是主要baseline. full使用自动记录、来源/认可筛选和完整结构化标记. no_source关闭来源/认可门禁并去掉结构化来源ID. no_scope保留同一来源筛选, 但只给claim正文, 去掉全部结构化元数据, 包括范围、更新状态、来源ID、证据ID和分组; 它不能单独归因于scope/version. 所有原始条件ID保留以便核对.','','| 预定比较 | 差值(百分点) | pair bootstrap 95%区间(百分点) | 胜/负/平 |','| --- | --- | --- | --- |']
    for k,v in comparisons.items():
        ci=v['pair_bootstrap_95ci'];lines.append(f'| {k} | {v["difference"]*100:+.2f} | [{ci[0]*100:+.2f}, {ci[1]*100:+.2f}] | {v["wins"]}/{v["losses"]}/{v["ties"]} |')
    lines+=['','主比较是full对mixed_summary. 区间按9个独立来源pair重采样, 不把900次回答视为900个独立用户. 失败计0并保留在分母, 同时另列失败数. 完整原始分数、正确选项与实际回答在scored_results.csv, 错误/调用数量在analysis_summary.json.','',f'API请求累计{len(calls)}次(含开发检查), native累计tokens: '+dumps(dict(usage))+'. provider重复计入上下文, 不把tokens当独立任务数. 货币账单未取得, 不填USD0或虚构价格.','']
    lines+=['## 实际输入差异检查','','| 条件 | 已生成答题指导 | 空指导 | 含foreign候选的指导 | 平均记录数 |','| --- | --- | --- | --- | --- |']
    for k,x in input_diagnostics.items():lines.append(f'| {k} | {x["rendered_inputs"]} | {x["empty_guidance"]} | {x["with_foreign_candidate_in_guidance"] if k in {"full","no_source","no_scope"} else "未自动标注prose"} | {x["mean_rendered_records"]} |')
    lines+=['','foreign候选计数来自实际候选记录的来源ID, 不评价prose summary的语义混淆. Full和no_scope的零值由预设来源门禁保证, 只检查处理是否生效, 不能作为方法收益.','']
    lines+=['## 各配置的独立运行开销口径','','| 条件 | 独立writer调用 | reader调用 | 累计input tokens | 累计output tokens | 摊到每题的处理+答题秒数 |','| --- | --- | --- | --- | --- | --- |']
    for k,x in configuration_cost.items():lines.append(f'| {k} | {x["unique_writer_calls_present"]} | {x["reader_calls_present"]} | {x["native_tokens"].get("prompt_tokens",0)} | {x["native_tokens"].get("completion_tokens",0)} | {x["elapsed_amortized_per_question_s"]:.2f} |')
    lines+=['','同一结构化writer被三个消融条件复用, 上表按每个配置单独部署时需要的预处理记账, 不能将五行相加冒充真实账单. 实际已发请求和总usage在上一节. 各组writer指令上限相同, 但该API不提供硬max_tokens; 超过4,000参考tokens的实际writer调用有'+str(writer_budget_violations)+'次. Reader指导实际硬截断/完整记录预算不超过2,000参考tokens. claim-only消融同时移除多类结构化信息并缩短文本, 因此差值不能单独归因于scope/version, 也未排除长度和计算量因素.','']
    pr=comparisons['primary_full_vs_summary'];supported=complete and pr['difference']>0 and pr['pair_bootstrap_95ci'][0]>0 and pr.get('holm_p',1)<.05
    lines+=['## 论文可用结论','']
    if supported:lines.append('本批主要比较支持: 在该公开合成人物、固定预算及配对foreign历史条件下, API级归因框架原型比强普通summary提高原题准确率. 具体差值和区间见上表. 不推广为真实跨expert持久化或平台Memory效果.')
    else:lines.append('本批不能写成已证实主要方法提升: 主要比较尚未同时满足正差值、区间下界大于0及预定统计标准, 或执行未完整. 可据实报告点估计、区间和失败类型; 不更换baseline、挑题或追加有利重复来制造提升.')
    for k in ['source_component','scope_version_labels']:
        x=comparisons[k];supported_component=complete and x['difference']>0 and x['pair_bootstrap_95ci'][0]>0 and x.get('holm_p',1)<.05
        lines.append(f'- {k}'+(' (保留原分析键名; 实际为claim-only全部元数据消融)' if k=='scope_version_labels' else '')+': '+('本批区间及预定检验支持正向增量.' if supported_component else '本批不足以作已证实增量收益的强主张.'))
    lines+=['','## 证据边界','','writer从原历史生成候选, 不读取正确答案或旧手写reusable/applicable标签. Full的foreign门禁诊断不能单独充当贡献; 主贡献检验是原选择题答题效果. no_source是来源门禁与归属标识的联合消融; no_scope保留来源筛选但将指导压成claim正文, 同时移除范围/版本、来源ID、证据ID和其它元数据; 只能解释为整体结构化表示的消融, 不能解释为单独的scope/version算法效果. 普通summary有相同来源身份信息, 明确要求忠实处理更新和一次性例外.','', '没有调用袋袋Memory读写、snapshot、克隆或自动发布. 所有组调用同一个真实Profy expert/model, 但平台内部隐藏上下文/权重版本不是本实验可观测量. 数据是公开合成persona, 只有9个来源block, 不建立真实creator长期忠实度或跨expert授权的结论. OpenReview未提交.']
    (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n')
    paper=f'''## Setup draft\nWe evaluate an API-level attribution prototype on a prespecified 180-question subset of PersonaMem-v1 (32k), covering 18 synthetic personas paired into nine disjoint source blocks. We retain the original questions, options, answers and temporal cutoffs, and add a paired persona's released history as a controlled foreign-source condition. A history writer forms guidance without seeing the question or options; the same hosted expert, with model label GPT-6.1 Sol, then answers each original multiple-choice question under five conditions. The target seed profile is identical across conditions, and downstream guidance is capped at 2,000 reference-tokenizer tokens. We reuse the original answer-matching implementation.\n\n## Results draft (descriptive; strength must follow REPORT.md)\nThe routed condition answers {groups['full']['correct']}/180 questions correctly ({groups['full']['accuracy']*100:.2f}%), compared with {groups['mixed_summary']['correct']}/180 ({groups['mixed_summary']['accuracy']*100:.2f}%) for the target-focused mixed-history summary. The paired difference is {pr['difference']*100:+.2f} percentage points, with a source-pair bootstrap 95% interval of [{pr['pair_bootstrap_95ci'][0]*100:+.2f}, {pr['pair_bootstrap_95ci'][1]*100:+.2f}]. The source-removed and claim-only flattened conditions (the latter retains source gating but removes all structured metadata) score {groups['no_source']['accuracy']*100:.2f}% and {groups['no_scope']['accuracy']*100:.2f}%, respectively. Failed or missing answers remain in the denominator.\n\n## Limitations draft\nThis controlled, synthetic-persona study tests an explicit framework prototype, not the product's native Memory persistence or authorization controls. The interference construction is an adaptation of the released benchmark rather than an official leaderboard setting; nine independent source blocks limit precision.\n'''
    (OUT/'PAPER_UPDATE_DRAFT.md').write_text(paper)
    print(dumps({'state':report['execution_state'],'groups':groups,'comparisons':comparisons,'calls':len(calls)}))

if __name__=='__main__':main()
