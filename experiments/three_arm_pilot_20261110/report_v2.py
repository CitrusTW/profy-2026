"""Report saved v2 results without model calls or copying third-party source."""
import argparse
import collections
import json
import zipfile
from pathlib import Path
from pilot import CONDITIONS, INPUTS, SKILL, TEST, sha, tool_calls


def load(path):
    return json.loads(path.read_text())


def invoice_diagnostic(folder):
    output = folder/'fraud_report.json'
    reference = folder/'scoring_only/ground_truth.json'
    if not output.exists() or not reference.exists():
        return None
    actual = load(output)
    gold = load(reference)
    expected = {x['invoice_page_number']:x for x in gold if x['reason'] != 'Clean'}
    predicted = {x['invoice_page_number']:x for x in actual}
    differences = collections.Counter()
    examples = []
    for page in sorted(expected.keys() & predicted.keys()):
        for field in sorted(expected[page].keys() | predicted[page].keys()):
            if expected[page].get(field) != predicted[page].get(field):
                differences[field] += 1
                if len(examples)<1:
                    examples.append({'page':page,'field':field,'expected':expected[page].get(field),'actual':predicted[page].get(field)})
    return {'reference_pages':len(gold),'expected_fraud_pages':len(expected),
            'predicted_fraud_pages':len(predicted),'duplicate_output_pages':len(actual)-len(predicted),
            'missed_pages':len(expected.keys()-predicted.keys()),
            'extra_pages':len(predicted.keys()-expected.keys()),
            'exact_field_differences':dict(differences),
            'difference_example':examples[0] if examples else None,
            'note':'Offline exact JSON diagnostic only; original grader score unchanged.'}


def package_hashes(path):
    with zipfile.ZipFile(path) as archive:
        return {name:sha(archive.read(name)) for name in archive.namelist()}


def summarize(root, source_commit):
    root = Path(root)
    study = load(root/'summary.json')
    assert study['protocol']['protocol_version'] == 2, 'This report is only for v2'
    runs = []
    for label in ['dev_before','dev_candidate','dev_candidate_revised']+CONDITIONS:
        folder = root/label
        if not (folder/'result.json').exists():
            continue
        result = load(folder/'result.json')
        events = [json.loads(x) for x in (folder/'events.jsonl').read_text().splitlines()]
        usage = [e for e in events if e.get('type') == 'usage.token']
        stamps = [e['timestamp_ms'] for e in events if isinstance(e.get('timestamp_ms'),(int,float))]
        names = tool_calls(events)
        record = {k:result.get(k) for k in ['task','completed','error','elapsed_sec','output_received','output_sha256','score','active_skill_evidence']}
        record.update({'condition':label,'native_event_span_sec':round((max(stamps)-min(stamps))/1000,3) if stamps else None,
                       'tool_calls':len(names),'tool_names':dict(collections.Counter(names)),
                       'usage_event_sums':{k:sum(e.get(k,0) or 0 for e in usage) for k in ['prompt_tokens','completion_tokens','total_tokens','cache_read_tokens','cache_write_tokens']},
                       'usage_event_count':len(usage),'profy_cost_usd':None})
        if label in CONDITIONS:
            record['invoice_diagnostic'] = invoice_diagnostic(folder)
        runs.append(record)
    by_label = {r['condition']:r for r in runs}
    audits = {}
    allowed = {'task','public_task','run_completed','error','elapsed_sec','tools','output_received'}
    experience = load(root/'development_experience.json')
    audits['shared_experience_allowlist_only'] = set(experience) == allowed
    audits['common_experience_has_no_raw_tool_result_field'] = 'observed_tool_results' not in experience
    test_folders = [root/c for c in CONDITIONS]
    audits['all_three_test_outputs_scored'] = all(by_label.get(c,{}).get('score',{}).get('status')=='scored' for c in CONDITIONS)
    a=root/CONDITIONS[0]
    if (a/'uploads.json').exists():
        audits['no_skills_no_expert_zip_uploaded'] = all(r['filename']!='expert.zip' for r in load(a/'uploads.json'))
        events=[json.loads(x) for x in (a/'events.jsonl').read_text().splitlines()]
        audits['no_skills_no_skill_tool_call'] = not any('skill' in n.lower() for n in tool_calls(events))
        read_paths=[e.get('result',{}).get('file_path') or '' for e in events if e.get('type')=='tool_call.result' and e.get('tool_name')=='read' and isinstance(e.get('result'),dict)]
        audits['no_skills_no_skill_file_read'] = not any('/expert/' in p or '/skills/' in p or p.endswith('SKILL.md') for p in read_paths)
    if all((f/'development_experience.json').exists() for f in test_folders):
        hashes=[sha((f/'development_experience.json').read_bytes()) for f in test_folders]
        audits['same_public_only_experience_for_three_arms'] = len(set(hashes))==1
    if all((f/'uploads.json').exists() for f in test_folders):
        attachments=[{r['filename']:r['sha256'] for r in load(f/'uploads.json') if r['filename'] in INPUTS[TEST]} for f in test_folders]
        audits['same_original_task_files_in_three_arms'] = all(set(a)==set(INPUTS[TEST]) for a in attachments) and all(a==attachments[0] for a in attachments)
    b,c = root/CONDITIONS[1],root/CONDITIONS[2]
    if (b/'expert.zip').exists() and (c/'expert.zip').exists():
        initial,updated=package_hashes(b/'expert.zip'),package_hashes(c/'expert.zip')
        changed=[name for name in initial.keys() | updated.keys() if initial.get(name)!=updated.get(name)]
        audits['only_target_skill_changed_in_bundle'] = changed==['expert/'+SKILL]
        audits['updated_skill_hash_differs'] = initial.get('expert/'+SKILL)!=updated.get('expert/'+SKILL)
    audits['update_accepted_before_test'] = bool(study['gate'].get('accepted'))
    audits['with_skills_initial_skill_read_and_hash_verified'] = bool(by_label.get(CONDITIONS[1],{}).get('active_skill_evidence',{}).get('verified'))
    audits['third_arm_updated_skill_read_and_hash_verified'] = bool(by_label.get(CONDITIONS[2],{}).get('active_skill_evidence',{}).get('verified'))
    sessions=[load(f/'session.json')['id'] for f in root.iterdir() if f.is_dir() and (f/'session.json').exists()]
    audits['sessions_unique'] = len(sessions)==len(set(sessions))
    required=['shared_experience_allowlist_only','common_experience_has_no_raw_tool_result_field',
              'all_three_test_outputs_scored','no_skills_no_expert_zip_uploaded','no_skills_no_skill_tool_call',
              'no_skills_no_skill_file_read','same_public_only_experience_for_three_arms','same_original_task_files_in_three_arms',
              'only_target_skill_changed_in_bundle','updated_skill_hash_differs',
              'update_accepted_before_test','with_skills_initial_skill_read_and_hash_verified',
              'third_arm_updated_skill_read_and_hash_verified','sessions_unique']
    complete=all(audits.get(k,False) for k in required)
    writer_responses=[load(p) for p in sorted(root.glob('writer_response*.json'))]
    costs=[r.get('usage',{}).get('cost') for r in writer_responses]
    report={'run_id':root.name,'source_commit':source_commit,'driver_sha256':study['protocol']['driver_sha256'],
            'initial_source_commit':study['protocol'].get('initial_source_commit',source_commit),
            'model':study['protocol']['model'],'updater_model':study['protocol']['updater_model'],
            'tasks':{'development':study['protocol']['development_task'],'test':study['protocol']['heldout_task']},
            'gate':study['gate'],'runs':runs,'audits':audits,'three_arm_execution_verified':complete,
            'profy_invocations':study['profy_model_invocations_reserved'],'openrouter_requests':len(writer_responses),
            'openrouter_reported_cost_usd':round(sum(costs),10) if costs and all(isinstance(x,(int,float)) for x in costs) else None,
            'profy_cost_usd':None,'scope':'One development task, one previously seen test task, one attempt per arm. New procedural-update prototype, not native Profy evolution or cross-expert attribution.',
            'paper_modified':False,'openreview_submitted':False}
    (root/'RESULTS_V2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    lines=['# 修正版三组小实验: 实际结果','',
           '三组执行检查: '+('通过' if complete else '未全部通过, 不能把本轮叫作有效三组对照')+'.',
           '开发题是SkillsBench的pdf-excel-diff: 核对员工PDF和Excel. 测试题是invoice-fraud-detection: 核对发票、供应商和采购订单. 三组用同一个Profy gpt-6.1-sol, 各自使用独立session.',
           '这是本助手新增的skill更新研究原型. 不是袋袋原生evolution, 也没有测试跨expert归因. 测试题此前已经跑过, 不称全新未见任务; 更新器不接收测试答案或评分反馈.','',
           '| 阶段/组别 | 原整题strict | 原pytest通过/总数 | 客户端秒数 | 工具调用 |',
           '| --- | --- | --- | --- | --- |']
    stage_names={'dev_before':'开发题: 原skill','dev_candidate':'开发题: 首个候选(弃用)',
                 'dev_candidate_revised':'开发题: 通用候选(采用)'}
    for r in runs:
        score=r['score']
        lines.append(f'| {stage_names.get(r["condition"],r["condition"])} | {score["strict"]} | {score.get("passed",0)}/{score.get("tests",0)} | {r["elapsed_sec"]:.3f} | {r["tool_calls"]} |')
    lines += ['', '整题strict是整份输出通过=1、没通过=0. pytest包含文件存在和整份内容等测试, 通过项比例不是字段准确率. 客户端秒数含任务运行和文件回传, 不含上传.', '',
              '## 新版skill有没有真的进入第三组','',
              '采用检查结果: '+('通过, 新版已在测试前冻结.' if study['gate'].get('accepted') else '未通过, 不应启动第三组测试.'),
              '新版是根据公开开发题和开发运行统计生成的一份通用记录核对说明, 替换expense-record-reconciliation/SKILL.md. 更新器没有阅读私有原skill正文; 原skill只在本地用于体积比较. 因此这里测的是有开发检查的候选替换原型, 不能称为袋袋原生完整学习机制.',
              '表中的首个候选在开发阶段弃用: 它写入了开发题专用文件名, 因而不进入正式测试. 通用候选才是纠正后做开发复测并采用的版本. 原skill没有因此重跑. 纠正在测试启动前完成, 未向更新器提供测试反馈.',
              '检查同时核对了上传包里只改目标skill、与旧版哈希不同、原生read返回包含新版全文、bash计算的实际文件SHA256一致. 它能证明新版被加载和读取, 不能单独证明模型每一步都遵循它.', '',
              '## no-skills有没有夹带skill','',
              '共用经验只保留公开开发题面和运行统计. 检查附件中没有expert.zip, 原生调用中没有skill工具或skill文件读取. 这表示没有提供本项目expert包或片段; 平台基础指令仍存在, 不把它叫作完全没有任何平台基础skill的裸模型.', '',
              '## 原输出哪里没通过','',
              '以下只对保存下来的JSON作离线诊断, 没改答案、没放宽原评分.','']
    for label in CONDITIONS:
        d=by_label.get(label,{}).get('invoice_diagnostic')
        if d:
            lines.append(f'- {label}: 参考答案标记{d["expected_fraud_pages"]}页有问题, 输出{d["predicted_fraud_pages"]}页, 漏报{d["missed_pages"]}页, 多报{d["extra_pages"]}页; 全字段精确比对差异计数为{json.dumps(d["exact_field_differences"],ensure_ascii=False)}.')
    example=(by_label.get(CONDITIONS[0],{}).get('invoice_diagnostic') or {}).get('difference_example')
    if example:
        lines += ['',f'差异例子: 第{example["page"]}页的{example["field"]}, 输出是{json.dumps(example["actual"],ensure_ascii=False)}, 参考答案是{json.dumps(example["expected"],ensure_ascii=False)}. po_number就是采购订单号.']
    lines += ['', '## 这次实际说明什么','']
    if complete:
        a_run,b_run,c_run=[by_label[c] for c in CONDITIONS]
        lines.append(f'原整题strict: no-skills={a_run["score"]["strict"]}, with-skills={b_run["score"]["strict"]}, with-skills-cognilife-method={c_run["score"]["strict"]}.')
        if c_run['score']['strict'] > b_run['score']['strict']:
            lines.append('在这一个测试任务上, 更新后组通过、初始skill组未通过. 这是单任务观察, 还不能说方法普遍提高成功率.')
        elif c_run['score']['strict'] < b_run['score']['strict']:
            lines.append('在这一个测试任务上, 更新后组未通过、初始skill组通过. 本轮没有补到方法提升的证据, 反而提示开发题检查没有保证这道测试题的表现.')
        else:
            lines.append('更新后组与初始skill组的整题通过情况相同. 本题没有观察到整题得分提升, 不把新版加载成功写成方法效果提升.')
        if len({r['output_sha256'] for r in [a_run,b_run,c_run]})==1:
            lines.append('三组输出的SHA256完全相同, 即交付JSON的字节也相同.')
        lines.append(f'测试任务客户端耗时: 初始skill组{b_run["elapsed_sec"]:.3f}秒、更新后组{c_run["elapsed_sec"]:.3f}秒. 本次更新后组耗时'+('更长' if c_run['elapsed_sec']>b_run['elapsed_sec'] else '更短或持平')+', 只报告这一次观察, 不据此推广为稳定性能差异.')
        gate=study['gate']
        lines.append(f'开发题原测试通过数没有下降; skill文档从{gate["before_utf8_bytes"]}减至{gate["after_utf8_bytes"]} UTF-8字节, 减少{(1-gate["after_utf8_bytes"]/gate["before_utf8_bytes"])*100:.1f}%. 这是文档体积变化, 不是已证明的调用费用或执行效率提升.')
    else:
        lines.append('执行检查没有全部通过, 因此不把本轮称为完成的三组方法效果对照. 具体缺项见检查明细.')
    lines += ['', '## 费用和调用量','',
              f'Profy任务{report["profy_invocations"]}次, OpenRouter请求{report["openrouter_requests"]}次. OpenRouter返回费用合计{report["openrouter_reported_cost_usd"]} USD. Profy货币账单未知, 不填0.', '',
              '| 阶段/组别 | prompt tokens事件合计 | completion tokens事件合计 |',
              '| --- | --- | --- |']
    for r in runs:
        u=r['usage_event_sums']
        lines.append(f'| {r["condition"]} | {u["prompt_tokens"]} | {u["completion_tokens"]} |')
    lines += ['', 'token数是原生usage.token事件逐项求和, 不是已核对的货币账单. 完整运行日志、原始输出和原grader保存在本地, 代码仓库只保存本助手代码、说明和不含原文的数字摘要.', '',
              '## 怎么下结论','',
              '这轮只比较同一道测试题的三次运行. 即使有分差, 也只能报告这个任务的观察, 不能推出普遍提升、长期学习或跨expert有效. 三组得分相同也不能证明方法普遍无效. 是否值得扩大任务量要按真实结果判断.', '',
              '没有修改论文或提交OpenReview.', '',
              '## 执行检查明细','']
    lines.extend('- '+key+': '+str(value) for key,value in audits.items())
    lines += ['', '初始开发与弃用候选的执行commit: '+report['initial_source_commit']+'.',
              '纠正后执行代码commit: '+source_commit+'.', '纠正后pilot.py SHA256: '+report['driver_sha256']+'.']
    (root/'RESULTS_V2.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'run_id':root.name,'three_arm_execution_verified':complete,'scores':[{k:r[k] for k in ['condition','score','elapsed_sec']} for r in runs]},ensure_ascii=False))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('result_dir')
    parser.add_argument('--source-commit',required=True)
    args=parser.parse_args()
    summarize(args.result_dir,args.source_commit)
