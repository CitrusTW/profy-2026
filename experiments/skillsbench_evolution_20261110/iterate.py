"""Bounded DEV-only iterations around received original Evolution functions."""
import argparse
import concurrent.futures
import hashlib
import json
import shutil
from pathlib import Path

from native_evolution import evolve, require_paid
from run import Study, DEV, TEST, save


def evidence(folder, text, dev_task=DEV, test_task=TEST):
    row = json.loads((folder/'result.json').read_text())
    if row['task'] != dev_task:
        raise ValueError('Only DEV records may enter evolution')
    if not (row['completed'] and row['output_received'] and row['target_skill_read_verified'] and row['error'] is None and not row['external_skill_tools_observed']):
        raise ValueError('Incomplete or contaminated DEV attempt')
    if row['skill_sha256'] != hashlib.sha256(text.encode()).hexdigest():
        raise ValueError('DEV skill version does not match its actual trace')
    history = {'request': json.loads((folder/'request.json').read_text()),
               'events': [json.loads(s) for s in (folder/'events.jsonl').read_text().splitlines()]}
    payload = json.dumps(history, ensure_ascii=False)
    if any(marker in payload for marker in [test_task, 'coordinate_diagnostic.json', 'gen_ground_truth.mjs', 'test_outputs.py']):
        raise ValueError('Evaluation/scoring marker in DEV evidence')
    metrics = {**row['tokens'], 'strict': row['score']['strict'], 'skill_chars': len(text),
               'skill_version_note': 'DEV skill sha256='+row['skill_sha256'][:20]}
    return history, metrics, row


def eligible(row, baseline_tokens):
    return (row['task'] == DEV and row['score']['strict'] == 1 and row['score']['tests'] > 0
            and row['score']['passed'] == row['score']['tests'] and row['score']['failed'] == 0
            and row['score']['original_returncode'] == 0 and not row['score']['skipped']
            and row['completed'] and row['output_received'] and row['error'] is None and row['target_skill_read_verified']
            and not row['external_skill_tools_observed'] and 0 < row['tokens']['total_tokens'] < baseline_tokens)


def run(args):
    require_paid(args.allow_paid)
    root, workspace = Path(args.out).resolve(), Path(args.workspace).resolve()
    if root.exists():
        raise RuntimeError('Use a new run directory; never overwrite or duplicate paid attempts')
    root.mkdir(parents=True)
    previous = workspace/'01_任务结果/2026-11-10_skillsbench_evolution'
    environment = workspace/'04_项目数据与代码/skillsbench/tasks'/DEV/'environment'
    original = (environment/'skills/threejs/SKILL.md').read_text()
    bad = (previous/'run-02-gpt61/evolution/candidate_SKILL.md').read_text()
    records = [evidence(previous/'run-01/dev_original', original), evidence(previous/'run-02-gpt61/dev_candidate', bad)]
    baseline_tokens = records[0][2]['tokens']['total_tokens']
    best_text, best_tokens, best_round = original, baseline_tokens, None
    rows = []; stalls = 0
    save(root/'PROTOCOL.json', {'client_date':'2026-11-10', 'timezone':'America/Los_Angeles',
        'objective':'Original workflow proposals; choose lowest measured DEV tokens with full original DEV tests, then confirm once.',
        'max_new_invocations':3, 'max_new_dev_solves':4, 'final_benchmark_solves':3,
        'stopping':'Three proposals or two consecutive non-improvements; no candidate means stop.',
        'selection':'DEV-only, no validation outcomes in evolution or version selection; original remains fallback and is never renamed evolved.',
        'evaluation_scope':'Previously inspected threejs-structure-parser, diagnostic repeat, not independent held-out evidence.',
        'extensions':'Bounded iterative orchestration, empirical DEV selection and confirmation; not received native promotion or full paper method.',
        'missing':'Capability-gap classifier, general semantic-applicability verifier and native acceptance/promotion remain absent.'})
    for index in range(1,4):
        folder = root/f'round-{index:02d}'; folder.mkdir()
        shutil.copytree(environment/'skills', folder/'parent_skills')
        target = folder/'parent_skills/threejs/SKILL.md'; target.write_text(best_text)
        (folder/'grader_environment').symlink_to(previous/'run-01/grader_environment', target_is_directory=True)
        study = Study(argparse.Namespace(workspace=str(workspace), out=str(folder), keys_file=args.keys_file, allow_paid=True))
        candidate, summary = evolve(workspace, target, folder/'evolution', [r[0] for r in records], [r[1] for r in records],
                                    study.transport.evolution_key(), study.transport.scrub, allow_paid=True)
        if candidate is None:
            rows.append({'round':index,'status':'no_proposal','evolution':summary}); break
        result = study.solve('development', DEV, candidate)
        valid = eligible(result, best_tokens)
        rows.append({'round':index,'status':'selected' if valid else 'not_selected', 'parent_sha256':hashlib.sha256(best_text.encode()).hexdigest(),
                     'candidate_sha256':hashlib.sha256(candidate.encode()).hexdigest(), 'development':result, 'evolution':summary})
        try:
            records.append(evidence(folder/'development', candidate))
        except ValueError:
            save(folder/'feedback_excluded.json', {'reason':'Execution incomplete or skill identity invalid; no invented history added'})
        if valid:
            best_text, best_tokens, best_round = candidate, result['tokens']['total_tokens'], index; stalls = 0
        else:
            stalls += 1
        save(root/'SELECTION.json', {'rounds':rows,'best_round':best_round,'best_tokens':best_tokens,'baseline_tokens':baseline_tokens})
        if stalls >= 2:
            break
    state = {'rounds':rows,'best_round':best_round,'baseline_tokens':baseline_tokens,'best_tokens':best_tokens}
    if best_round is None:
        state['status']='no_empirically_better_candidate'; save(root/'FINAL.json',state); return
    confirm_dir = root/'confirmation'
    confirm_dir.mkdir(); (confirm_dir/'grader_environment').symlink_to(previous/'run-01/grader_environment', target_is_directory=True)
    study = Study(argparse.Namespace(workspace=str(workspace),out=str(confirm_dir),keys_file=args.keys_file,allow_paid=True))
    confirmation = study.solve('development', DEV, best_text)
    state['confirmation']=confirmation
    if not eligible(confirmation, baseline_tokens):
        state['status']='best_candidate_not_confirmed';save(root/'FINAL.json',state);return
    benchmark = root/'benchmark';benchmark.mkdir()
    (benchmark/'grader_environment').symlink_to(previous/'run-01/grader_environment', target_is_directory=True)
    (benchmark/'selected_SKILL.md').write_text(best_text)
    save(benchmark/'frozen.json',{'selected_round':best_round,'skill_sha256':hashlib.sha256(best_text.encode()).hexdigest(),
         'selection_used':'DEV records only','validation_feedback_used':False,'claim_scope':'diagnostic repeat, not full native method'})
    study = Study(argparse.Namespace(workspace=str(workspace),out=str(benchmark),keys_file=args.keys_file,allow_paid=True))
    labels=['no-skills','with-skills','with-CogniLife-skills']
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(study.solve,label,TEST,best_text if label==labels[2] else None,label==labels[0]) for label in labels]
        state['benchmark']=[f.result() for f in futures]
    state['status']='completed'; save(root/'FINAL.json',state)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--workspace',required=True);parser.add_argument('--out',required=True)
    parser.add_argument('--keys-file',required=True);parser.add_argument('--allow-paid',action='store_true')
    run(parser.parse_args())
