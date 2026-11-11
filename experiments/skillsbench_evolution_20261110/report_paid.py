"""Summarize real run receipts without changing outputs or rerunning a grader."""
import argparse
import hashlib
import json
from pathlib import Path

from candidate_check import check_candidate


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize(workspace, run):
    workspace, run = Path(workspace), Path(run)
    target = workspace/'04_项目数据与代码/skillsbench/tasks/threejs-to-obj/environment/skills/threejs/SKILL.md'
    labels = ['dev_original', 'dev_candidate', 'no-skills', 'with-skills', 'with-CogniLife-skills']
    rows = []
    for label in labels:
        path = run/label/'result.json'
        result = json.loads(path.read_text())
        request = json.loads((run/label/'request.json').read_text())
        score = result['score']
        verifier = workspace/'04_项目数据与代码/skillsbench/tasks'/result['task']/'verifier/test_outputs.py'
        assert score['source_sha256'] == sha(verifier), 'Scorer source version changed'
        assert request['agent']['model'] == 'gpt-6.1-sol'
        assert result['native_zip_sha256'] == sha(run/label/'deliverables.zip')
        for name, expected in result['file_hashes'].items():
            assert sha(run/label/name) == expected, 'Output bytes changed'
        rows.append({k: result[k] for k in ['label', 'task', 'completed', 'error', 'elapsed_sec', 'output_received',
                    'native_zip_sha256', 'skill_sha256', 'target_skill_read_verified', 'external_skill_tools_observed',
                    'supplied_benchmark_skills', 'tokens', 'profy_cost_usd', 'score']})
    eligibility = check_candidate(run, target)
    original_pack = json.loads((run/'with-skills/supplied_skill_hashes.json').read_text())
    candidate_pack = json.loads((run/'with-CogniLife-skills/supplied_skill_hashes.json').read_text())
    assert set(original_pack) == set(candidate_pack)
    differences = [name for name in original_pack if original_pack[name] != candidate_pack[name]]
    assert differences == ['bench_skills/threejs/SKILL.md']
    assert json.loads((run/'no-skills/supplied_skill_hashes.json').read_text()) == {}
    generated = json.loads((run/'candidate_generated_receipt.json').read_text())
    assert generated['candidate_sha256'] == sha(run/'evolution/candidate_SKILL.md')
    frozen = json.loads((run/'frozen.json').read_text())
    assert frozen['after_sha256'] == generated['candidate_sha256']
    payloads = [json.loads(p.read_text()) for p in sorted((run/'evolution').glob('request_*.json'))]
    responses = [json.loads(p.read_text()) for p in sorted((run/'evolution').glob('response_*.json'))]
    assert all(p['model'] == 'openai/gpt-6.1-sol' for p in payloads)
    assert all(r.get('model') == 'openai/gpt-6.1-sol' for r in responses)
    serialized = json.dumps(payloads, ensure_ascii=False)
    markers = ['threejs-structure-parser', 'coordinate_diagnostic.json', 'gen_ground_truth.mjs', 'test_outputs.py']
    absence = {name: name not in serialized for name in markers}
    assert all(absence.values()), 'Evaluation marker in evolution request'
    summary = {'client_date': '2026-11-10', 'timezone': 'America/Los_Angeles', 'run_id': run.name,
               'kind': 'real API pilot; previously inspected evaluation task, diagnostic repeat',
               'development_baseline_reused': True, 'new_solver_attempts': 4,
               'solver_model_requested': 'gpt-6.1-sol', 'evolution_model_reported': 'openai/gpt-6.1-sol',
               'evolution': generated, 'candidate_check': eligibility, 'rows': rows,
               'package_differences': differences, 'evolution_request_marker_absence': absence,
               'marker_check_limit': 'String checks supplement the DEV-only input construction; not a general semantic leak detector.',
               'after_evaluation_candidate_edits': False, 'paper_changed': False,
               'profy_total_cost_usd': None,
               'claim_limit': 'One previously inspected task and one attempt per group; not full paper reproduction or independent generalization evidence.'}
    (run/'PAID_RESULTS.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    lines = ['# gpt-6.1-sol新skill小跑结果', '',
             '2026-11-10, America/Los_Angeles. 这是实际API运行和原程序评分. 验证题以前已分析过, 本次是修复后的对照小跑, 不能当新的独立held-out结果.', '',
             '| 运行 | 原测试通过 | strict | 耗时(秒) | tokens | 工具调用 | 目标skill读取核验 |',
             '| --- | --- | --- | --- | --- | --- | --- |']
    for row in rows:
        score = row['score']
        lines.append(f"| {row['label']} | {score['passed']}/{score['tests']} | {score['strict']} | {row['elapsed_sec']} | {row['tokens']['total_tokens']} | {row['tokens']['tool_calls']} | {row['target_skill_read_verified']} |")
    original, candidate = rows[3], rows[4]
    delta = candidate['score']['passed']-original['score']['passed']
    comparison = '多通过'+str(delta)+'项原测试' if delta > 0 else ('少通过'+str(-delta)+'项原测试' if delta < 0 else '通过的原测试数相同')
    token_delta = candidate['tokens']['total_tokens']-original['tokens']['total_tokens']
    seconds_delta = round(candidate['elapsed_sec']-original['elapsed_sec'], 3)
    lines += ['', f"本轮新skill相对原版: {comparison}; reported tokens差值{token_delta:+d}, 耗时差值{seconds_delta:+.3f}秒. 这都是单次观察, 不能据此判断稳定收益.", '',
              f"Evolution由OpenRouter的gpt-6.1-sol完成, {generated['requests']}次请求, {generated['elapsed_sec']}秒, 回报费用${generated['reported_cost_usd']:.6f}. 三组求解由Profy完成. Profy求解和接口诊断没有美元账单, 不编总费用.", '',
              '开发基线复用上一轮真实记录; 其他4次求解为本轮新运行. 后两组提供的文件只有threejs/SKILL.md不同. 候选在验证前冻结, 验证后没有改候选或再进化. 原评分、容差和任务输入未改.', '',
              '进化只使用开发题原材料和真实轨迹, 复用收到的原Evolution workflow与门控. 没有把验证题答案、原verifier或旧失败分析传给进化模型. 自动适用性检查、capability-gap classifier和native promotion仍未完成, 不冒称完整论文方法.', '',
              'Private repo保存本助手写的代码、这份报告和数字/hash. 第三方source、skill正文、原始输入、gold和keys不进repo. 完整原始记录保留在工作区的同名run目录.']
    (run/'PAID_REPORT.md').write_text('\n'.join(lines)+'\n')
    inventory = []
    for path in sorted(run.rglob('*')):
        if path.is_file() and not path.is_symlink() and path.name != 'EVIDENCE_HASHES.json':
            inventory.append({'path': path.relative_to(run).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha(path)})
    (run/'EVIDENCE_HASHES.json').write_text(json.dumps({'run_id': run.name, 'files': inventory,
        'reused_baseline_receipt_sha256': sha(run/'dev_original/result.json'),
        'note': 'Hashes only; original material and derived skill bodies are kept outside the private repo.'}, ensure_ascii=False, indent=2)+'\n')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    result = summarize(args.workspace, args.out)
    print(json.dumps([{'label': r['label'], 'score': r['score'], 'seconds': r['elapsed_sec'], 'tokens': r['tokens']['total_tokens']} for r in result['rows']], ensure_ascii=False, indent=2))
