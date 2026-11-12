"""Offline audit only. Never import generation scripts, call APIs, or edit source data."""
import argparse
import ast
import collections
import csv
import hashlib
import json
import re
from pathlib import Path

CONDITIONS = {
    'generic_llm_raw': 'Raw',
    'generic_llm_expert_prompt': 'Expert Prompt',
    'profy_expert_full': 'Full',
}
PATTERNS = {
    'runtime_error_text': re.compile(
        r'Traceback \(most recent call last\)|(?:API|HTTP)[ _-]?(?:Error|error|[45]\d\d)'
        r'|JSONDecodeError|RateLimitError|AuthenticationError|context_length_exceeded'
        r'|maximum context length|模型调用失败|接口调用失败', re.I),
    'tool_failure_text': re.compile(
        r'(?:tool|function)[ _-]?(?:call)?[^\n。]{0,40}(?:failed|failure|exception)'
        r'|工具(?:调用|执行)[^\n。]{0,15}(?:失败|出错|异常)', re.I),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def output_check(row):
    text = row.get('output_text')
    text = text if isinstance(text, str) else ''
    return {
        'empty_output': not text.strip(),
        'explicit_error_field': bool(row.get('error')),
        'explicit_partial_flag': row.get('partial') is True,
        'explicit_finish_length': row.get('finish_reason') in ('length', 'max_tokens'),
        'unclosed_code_fence_candidate': len(re.findall(r'^\s*```', text, re.M)) % 2 == 1,
        **{name: bool(pattern.search(text)) for name, pattern in PATTERNS.items()},
    }


def write_csv(path, rows, fields):
    with path.open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    bench = args.workspace / '04_项目数据与代码/Profy-main/knowledge/benchmarks/profybench-v1'
    sources = [bench / 'profybench_v0.jsonl', *[
        bench / 'results' / f'outputs_{condition}.jsonl' for condition in CONDITIONS
    ], *[bench / 'scripts' / name for name in (
        'run_baselines.py', 'run_full_pipeline.py', 'run_profy_invoke.py', 'llm_judge.py'
    )]]
    before = {str(path.relative_to(args.workspace)): digest(path) for path in sources}
    tasks_list = read_rows(sources[0])
    tasks = {row['task_id']: row for row in tasks_list}
    assert len(tasks) == len(tasks_list) == 85

    # Inspect literal templates without importing code or evaluating credentials.
    baseline_text = (bench / 'scripts/run_baselines.py').read_text()
    template_node = next(node.value for node in ast.parse(baseline_text).body
                         if isinstance(node, ast.Assign)
                         and any(isinstance(target, ast.Name)
                                 and target.id == 'EXPERT_PROMPT_TEMPLATES'
                                 for target in node.targets))
    templates = ast.literal_eval(template_node)
    pipeline = (bench / 'scripts/run_full_pipeline.py').read_text()
    generation = next(node for node in ast.parse(pipeline).body
                      if isinstance(node, ast.FunctionDef) and node.name == 'run_baselines')
    generation_text = ast.get_source_segment(pipeline, generation)
    assert 'checkpoints_desc' in generation_text and 'task["checkpoints"]' in generation_text
    assert 'profile' not in generation_text.lower() and 'journal' not in generation_text.lower()

    details, summary, structural = [], [], {}
    for condition, display in CONDITIONS.items():
        path = bench / 'results' / f'outputs_{condition}.jsonl'
        rows = read_rows(path)
        counts = collections.Counter(row.get('task_id') for row in rows)
        ids = set(counts)
        structural[display] = {
            'rows': len(rows), 'missing_task_ids': sorted(tasks.keys() - ids),
            'extra_task_ids': sorted(ids - tasks.keys()),
            'duplicate_task_ids': sorted(key for key, count in counts.items() if count > 1),
        }
        assert ids == tasks.keys() and len(rows) == len(tasks) == 85
        condition_details = []
        for row in sorted(rows, key=lambda value: value['task_id']):
            task = tasks[row['task_id']]
            # The stored outputs have no captured messages/request. Do not treat
            # code-based reconstruction as the request actually sent in the past.
            assert not any(key in row for key in ('messages', 'request', 'raw_request', 'input_messages'))
            usage = row.get('usage') or {}
            source_empty = not task['input']['prompt'].strip()
            role_missing = (condition == 'generic_llm_expert_prompt'
                            and not templates.get(task['task_family'], '').strip())
            live_label = condition == 'profy_expert_full' and row.get('is_proxy') is False
            proxy_label = condition == 'profy_expert_full' and row.get('is_proxy') is True
            tool_calls = row.get('tool_calls')
            tool_failure = (isinstance(tool_calls, list)
                            and any(call.get('status') in ('failed', 'error') or call.get('error')
                                    for call in tool_calls if isinstance(call, dict)))
            item = {
                'task_id': row['task_id'], 'condition': display,
                'condition_key': condition, 'family': task['task_family'],
                'variant': task['variant_type'],
                'output_file': str(path.relative_to(args.workspace)),
                'output_sha256': hashlib.sha256(row['output_text'].encode()).hexdigest(),
                'output_characters': len(row['output_text']),
                'model_label': row.get('model'),
                'generation_request_captured': False,
                'actual_required_context_complete': 'unverifiable',
                'actual_input_empty_or_truncated': 'unverifiable',
                'source_task_prompt_empty': source_empty,
                'source_expert_role_missing': role_missing,
                'context_slots_separately_appended_in_received_code': False,
                'source_only_not_actual_request': True,
                'full_runtime_metadata_workflow_profile_journal': (
                    'unverifiable' if condition == 'profy_expert_full' else 'not_applicable'),
                'proxy_label': proxy_label, 'platform_invoke_label': live_label,
                'recorded_partial_flag': row.get('partial', 'not_saved'),
                'recorded_finish_reason': row.get('finish_reason', 'not_saved'),
                'actual_output_truncation': (
                    'recorded_length_stop' if row.get('finish_reason') in ('length', 'max_tokens')
                    else 'unverifiable_without_finish_reason'),
                'completion_tokens': usage.get('completion_tokens'),
                'actual_max_tokens_saved': False,
                'actual_token_cap_hit': 'unverifiable_without_request_limit',
                'completion_at_or_above_source_cap_4096': (
                    usage['completion_tokens'] >= 4096 if 'completion_tokens' in usage else None),
                'tool_execution_failure_recorded': bool(tool_failure),
                'tool_trace_saved': isinstance(tool_calls, list) and bool(tool_calls),
                'tool_execution_applicable_by_received_route': live_label,
                **output_check(row),
            }
            details.append(item)
            condition_details.append(item)
        categories = {
            '输入原始请求未保存': ('unverifiable', lambda item: not item['generation_request_captured']),
            '实际 context 完整性/空值/截断无法核实': ('unverifiable', lambda item: True),
            'Full 的 metadata/workflow/profile/journal 实际注入无法核实': (
                'unverifiable' if display == 'Full' else 'not_applicable',
                lambda item: display == 'Full'),
            '源题 prompt 为空': ('confirmed_source_issue', lambda item: item['source_task_prompt_empty']),
            'Expert Prompt 源角色模板缺失': (
                'confirmed_source_issue' if display == 'Expert Prompt' else 'not_applicable',
                lambda item: item['source_expert_role_missing']),
            '保存的回答为空': ('confirmed_record_issue', lambda item: item['empty_output']),
            '保存的 error 字段报错': ('confirmed_record_issue', lambda item: item['explicit_error_field']),
            '保存的 partial 标为 true': ('confirmed_record_issue', lambda item: item['explicit_partial_flag']),
            '未保存 partial 字段': ('unverifiable', lambda item: item['recorded_partial_flag'] == 'not_saved'),
            '保存的 finish_reason 标为 length/max_tokens': (
                'confirmed_record_issue', lambda item: item['explicit_finish_length']),
            '回答内有技术报错关键词': ('text_candidate_not_confirmed_failure', lambda item: item['runtime_error_text']),
            '回答内有工具失败关键词': ('text_candidate_not_confirmed_failure', lambda item: item['tool_failure_text']),
            '代码围栏未闭合候选': ('text_candidate_not_confirmed_failure', lambda item: item['unclosed_code_fence_candidate']),
            '工具记录明确报错': ('confirmed_record_issue', lambda item: item['tool_execution_failure_recorded']),
            '未保存 finish_reason, 无法确认输出是否被截断': (
                'unverifiable', lambda item: item['recorded_finish_reason'] == 'not_saved'),
            '未保存实际 max_tokens, 无法确认是否触顶': ('unverifiable', lambda item: True),
            '未保存 completion_tokens': ('unverifiable', lambda item: item['completion_tokens'] is None),
            '已保存 completion_tokens 达到源脚本 4096, 不代表实际限制': (
                'source_limit_comparison_only', lambda item: item['completion_at_or_above_source_cap_4096'] is True),
            '平台调用记录缺少逐次工具日志, 无法排除工具失败': (
                'unverifiable' if display == 'Full' else 'not_applicable_by_received_route',
                lambda item: item['tool_execution_applicable_by_received_route'] and not item['tool_trace_saved']),
            '记录带 proxy 标签': ('record_metadata_not_failure', lambda item: item['proxy_label']),
            '记录带平台调用标签': ('record_metadata_not_failure', lambda item: item['platform_invoke_label']),
        }
        for category, (status, predicate) in categories.items():
            selected = [item['task_id'] for item in condition_details if predicate(item)]
            summary.append({'condition': display, 'category': category, 'status': status,
                            'count': len(selected), 'total': 85, 'task_ids': ';'.join(selected)})
    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.out / '每组每类问题及全部task_id.csv', summary,
              ['condition', 'category', 'status', 'count', 'total', 'task_ids'])
    with (args.out / '逐题完整性记录.jsonl').open('w') as stream:
        for item in details:
            stream.write(json.dumps(item, ensure_ascii=False) + '\n')
    report = {
        'mode': 'offline_read_only_report_no_fixes_no_reruns_no_judging',
        'n_tasks': 85, 'n_condition_outputs': len(details), 'source_sha256': before,
        'structural_checks': structural,
        'criteria_identical_across_conditions': True,
        'unknown_is_not_pass': True,
        'source_code_is_not_a_captured_historical_request': True,
        'source_proxy_branch_injects_checkpoints': True,
        'source_proxy_branch_injects_checkpoints_evidence': 'scripts/run_full_pipeline.py:181-194',
        'source_proxy_branch_profile_journal_loader_present': False,
        'source_proxy_branch_link_to_specific_saved_requests': 'unverified',
        'actual_full_platform_context_injection': 'unverifiable_no_runtime_prompt_snapshot',
        'summary': summary,
        'condition_metadata': {
            condition: {
                'model_labels': dict(collections.Counter(item['model_label'] for item in details
                                                         if item['condition'] == condition)),
                'completion_tokens_recorded_n': sum(item['completion_tokens'] is not None
                                                    for item in details if item['condition'] == condition),
                'completion_tokens_min': min(item['completion_tokens'] for item in details
                                              if item['condition'] == condition and item['completion_tokens'] is not None),
                'completion_tokens_max': max(item['completion_tokens'] for item in details
                                              if item['condition'] == condition and item['completion_tokens'] is not None),
            } for condition in CONDITIONS.values()
        },
    }
    assert before == {str(path.relative_to(args.workspace)): digest(path) for path in sources}
    report['source_files_unchanged_after_audit'] = True
    (args.out / 'audit_results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({'outputs_checked': len(details), 'source_files_unchanged': True,
                      'summary_csv': str(args.out / '每组每类问题及全部task_id.csv')}, ensure_ascii=False))


if __name__ == '__main__':
    assert output_check({'output_text': '  ', 'error': None})['empty_output']
    assert not output_check({'output_text': '完成。#推荐#', 'error': None})['empty_output']
    assert output_check({'output_text': 'Traceback (most recent call last):'})['runtime_error_text']
    assert output_check({'output_text': '```python\nx = 1'})['unclosed_code_fence_candidate']
    main()
