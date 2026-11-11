"""Summarize native events and original grader results; contains no benchmark code."""
import argparse
import collections
import json
from pathlib import Path
from pilot import SKILL_HEADER, tool_calls

def diagnostics(root):
    request = json.loads((root/'writer_request.json').read_text())
    evidence = json.loads(request['messages'][0]['content'].rsplit('\n',1)[1])
    response = json.loads((root/'writer_response.json').read_text())
    body = json.loads(response['choices'][0]['message']['content'])['body']
    experience = json.loads((root/'development_experience.json').read_text())
    excerpts = experience.get('observed_tool_results',[])
    # Diagnostic comparison only. Does not alter the submitted output or official score.
    actual = json.loads((root/'no-skills/fraud_report.json').read_text())
    reference = json.loads((root/'no-skills/scoring_only/ground_truth.json').read_text())
    expected = {x['invoice_page_number']:x for x in reference if x['reason'] != 'Clean'}
    predicted = {x['invoice_page_number']:x for x in actual}
    differences = collections.Counter()
    for page in expected.keys() & predicted.keys():
        for field in expected[page].keys() | predicted[page].keys():
            if expected[page].get(field) != predicted[page].get(field):
                differences[field] += 1
    return {'candidate_utf8_bytes':len((SKILL_HEADER+body).encode()),
            'original_utf8_bytes_derived_from_recorded_budget':evidence['max_body_utf8_bytes']+len(SKILL_HEADER.encode())+1,
            'development_candidate_executed':(root/'dev_candidate/result.json').exists(),
            'shared_experience_expert_excerpt_count':sum('/expert/' in text for text in excerpts),
            'shared_experience_old_export_count':sum('PILOT_PART' in text for text in excerpts),
            'clean_no_skills_control':not any('/expert/' in text for text in excerpts),
            'test_diagnostic':{'reference_pages':len(reference),'expected_fraud_pages':len(expected),
                 'predicted_fraud_pages':len(predicted),'missed_pages':len(expected.keys()-predicted.keys()),
                 'extra_pages':len(predicted.keys()-expected.keys()),'exact_value_differences':dict(differences),
                 'scope':'Offline exact JSON comparison of no-skills output; all three output hashes match. Not a replacement official metric.'}}

def summarize(root):
    root = Path(root)
    study = json.loads((root/'summary.json').read_text())
    runs = []
    for group in ['dev_before','dev_candidate'] + study['protocol']['conditions']:
        folder = root/group
        if not (folder/'result.json').exists():
            continue
        result = json.loads((folder/'result.json').read_text())
        events = [json.loads(line) for line in (folder/'events.jsonl').read_text().splitlines()]
        usage = [e for e in events if e.get('type') == 'usage.token']
        tools = tool_calls(events)
        totals = {key:sum(e.get(key,0) or 0 for e in usage)
                  for key in ['prompt_tokens','completion_tokens','total_tokens','cache_read_tokens','cache_write_tokens']}
        stamps = [e['timestamp_ms'] for e in events if isinstance(e.get('timestamp_ms'),(int,float))]
        runs.append({'condition':group,'task':result['task'],'completed':result['completed'],
                     'output_received':result['output_received'],'score':result['score'],
                     'elapsed_sec':result['elapsed_sec'],'tool_calls':len(tools),
                     'native_event_span_sec':round((max(stamps)-min(stamps))/1000,3),
                     'timing_basis':result.get('timing_basis','Client task duration; excludes upload'),
                     'output_sha256':result['output_sha256'],
                     'tool_names':dict(collections.Counter(tools)),
                     'native_token_totals':totals,'usage_event_count':len(usage),
                     'profy_cost_usd':None})
    writer = root/'writer_response.json'
    response = json.loads(writer.read_text()) if writer.exists() else {}
    report = {'runs':runs,'gate':study['gate'],'diagnostics':diagnostics(root),
              'valid_method_effect_comparison':False,
              'validity_note':'Rejected update fell back to original skill; no-skills received an expert skill excerpt in shared experience. Not evidence for or against CogniLife effectiveness.',
              'updater_model':study['protocol']['updater_model'],
              'openrouter_reported_cost_usd':response.get('usage',{}).get('cost'),
              'profy_cost_note':'Currency bill unavailable; not reported as zero or inferred from tokens.',
              'executed_code_commit':'e68a13ba60bc2ccf7b19a6cb3a0fc01a0203d950',
              'scope':study['scope'],
              'event_counter_note':'Native tools emit in_progress. Tool totals here are deduplicated from actual event IDs; the first driver version counted created events only. Original outputs and grader scores are unchanged.'}
    (root/'RESULTS_SUMMARY.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    lines = ['# 三组小实验: 实际结果','',
             '**本轮已执行并评分, 但没有形成有效的三组方法对照, 不能写成CogniLife提升证据.**',
             '本轮是新写的skill更新研究原型, 不是袋袋原生evolution, 也没有测跨expert归因.',
             '练习是员工PDF/Excel记录差异核对, 考试是另一道发票核对原题. 每组只有一次考试尝试.','',
             '| 阶段/组别 | 原strict通过 | 原pytest通过/总数 | 秒 | 工具调用 |',
             '| --- | --- | --- | --- | --- |']
    for run in runs:
        score = run['score']
        lines.append(f'| {run["condition"]} | {score["strict"]} | {score.get("passed",0)}/{score.get("tests",0)} | {run["native_event_span_sec"]:.3f} | {run["tool_calls"]} |')
    gate = study['gate']
    diag = report['diagnostics']
    lines += ['', '秒数统一按原生events的首尾时间差统计, 不含附件上传. 开发任务客户端另记249.492秒. 工具调用按tool_call_id去重.',
              '', '## 第三组有没有真的采用更新','',
              '采用新版: '+('是' if gate['accepted'] else '否, 按规则保留初始版')+'.',
              f'初始skill为{diag["original_utf8_bytes_derived_from_recorded_budget"]} UTF-8字节, 候选为{diag["candidate_utf8_bytes"]}字节. 预先规则要求变短, 所以候选在再次做开发题之前就被拒绝. 本轮没有执行dev_candidate.',
              '因此第三组实际使用的expert包与with-skills相同. 两组相同的分数不能用来判断skill更新有效或无效.',
              '采用记录: '+json.dumps(gate,ensure_ascii=False), '',
              '## no-skills也有一个输入问题','',
              '首版代码把开发运行的工具输出片段作为共同经验给了三组. 其中夹带了读取expert/skills/xlsx/SKILL.md的内容, 所以no-skills虽然没收到expert.zip, 仍间接收到了一部分skill. 它不是干净的无skill组. 这是本次实现问题, 不能归因于论文方法.',
              '当前代码已改成只共享公开开发题面和运行统计, 并加了检查. 这是执行后的修复, 没有用修复版付费重跑, 也没有改写本轮原输入.', '',
              '## 为什么三组都是0','',
              '三份fraud_report.json的SHA256完全相同. 原评分包含文件存在检查和整份内容检查; 三组都是文件存在通过、内容检查失败, 所以原strict均为0, pytest均为1/2. 这不表示发票识别准确率只有50%.',
              '原评分首先停在第4页的po_number: 返回PO-INVALID, 参考答案要求null. 只用已经保存的文件继续做离线诊断, 发现53页中50页被参考答案标为有问题; 三组都找齐这50页, 没多报或漏报. 对照JSON的全部字段, 有5处po_number不一致, 其他字段值相同. 这是额外诊断, 没有替代或放宽原评分.', '',
              '## 怎么理解','',
              '原strict是整题通过=1、未通过=0. pytest通过项不是字段准确率. 一道考试原task、三次运行不能当成三个独立任务, 也不足以说明普遍提升或做显著性结论.',
              '本轮只完成了运行和排错记录. 由于第三组没有采用更新、no-skills又夹带skill内容, 不能拿它补论文里的方法效果或跨expert缺口, 也不能说原论文方法没用. 不把这组结果加入论文主结果.', '',
              '## 实际调用和token记录','',
              '本轮共4次Profy任务调用: 1次初始开发题、3次测试题; 另有1次OpenRouter请求. 没有额外付费答题或重试.', '',
              '| 阶段/组别 | prompt tokens事件合计 | completion tokens事件合计 |',
              '| --- | --- | --- |']
    for run in runs:
        totals=run['native_token_totals']
        lines.append(f'| {run["condition"]} | {totals["prompt_tokens"]} | {totals["completion_tokens"]} |')
    lines += ['', 'token数按usage.token原生事件逐项求和, 不是已经核对过的货币账单.', '',
              '## 费用与数据','',
              'Profy货币账单未取得, 因此费用写未知, 不填0或虚构估计. OpenRouter返回费用: '+str(report['openrouter_reported_cost_usd'])+' USD.',
              'OpenRouter只收到公开题面和数值统计, 不收到私有expert原文、工具结果原文或答案. expert包只用于Profy任务执行.',
              '原始文件、模型输出、第三方grader和完整日志留在本地, 不提交到代码仓库.', '',
              '## 实现记录','',
              '实际执行代码commit: '+report['executed_code_commit']+'.',
              '首版driver漏识别了in_progress形式的工具计数; 上表已从原始event ID重新统计. 开发期writer实际收到的tool_call_count为0, 这个历史输入保留不改.',
              '首版回传解析混入了开发经验中的旧编码片段. recover_outputs.py只从各次任务自己的bash返回中恢复文件, 检查字节数与SHA256, 再调用原评分. 没有重新请求模型, 没有改回答或评分断言. 初版解析失败摘要保留为summary_initial_decoder_failure.json.',
              '没有修改论文或提交OpenReview.']
    (root/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'runs':len(runs),'candidate_accepted':gate['accepted']},ensure_ascii=False))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('result_dir')
    args = parser.parse_args()
    summarize(args.result_dir)
