"""One bounded round at a time, enabling a private-repo checkpoint after each."""
import argparse
import collections
import hashlib
import json
import re
import shutil
from pathlib import Path

from iterate import evidence
from native_evolution import evolve, require_paid
from run import Study, DEV, TEST, save


def contract_check(folder):
    rows=[]
    for path in sorted((folder/'output').rglob('*.obj')):
        count=0;refs=[]
        for line in path.read_text().splitlines():
            parts=line.split()
            if not parts:continue
            if parts[0]=='v':count+=1
            elif parts[0]=='f':
                for value in parts[1:]:
                    i=int(value.split('/')[0]);refs.append(i if i>0 else count+i+1)
        uses=collections.Counter(refs)
        passed=bool(count) and len(refs)==count and set(uses)==set(range(1,count+1)) and all(n==1 for n in uses.values())
        rows.append({'file':path.relative_to(folder).as_posix(),'vertices':count,'triangle_corners':len(refs),'public_original_nonindexed_convention':passed})
    return {'passed':bool(rows) and all(r['public_original_nonindexed_convention'] for r in rows),'files':rows,
            'origin':'New compatibility guard derived from original public SKILL.md. No reference geometry used.'}


def valid(row, check):
    s=row['score']
    return (row['completed'] and row['error'] is None and row['output_received'] and row['target_skill_read_verified']
            and not row['external_skill_tools_observed'] and s['strict']==1 and s['tests']>0
            and s['passed']==s['tests'] and s['failed']==0 and s['skipped']==0 and check['passed'])


def run(args):
    require_paid(args.allow_paid)
    workspace,root=Path(args.workspace).resolve(),Path(args.out).resolve()
    if not 4<=args.round<=30:raise ValueError('Total round count, including three completed rounds, is capped at 30')
    prior=workspace/'01_任务结果/2026-11-10_skillsbench_evolution'
    skills=workspace/'04_项目数据与代码/skillsbench/tasks'/DEV/'environment/skills'
    original=(skills/'threejs/SKILL.md').read_text()
    baseline=evidence(prior/'run-01/dev_original',original)
    folder=root/f'round-{args.round:02d}'
    if folder.exists():raise RuntimeError('Do not overwrite or duplicate an existing paid round')
    folder.mkdir(parents=True)
    history=[baseline]
    parent_text=original;parent_tokens=baseline[2]['tokens']['total_tokens']
    # Only previous DEV traces enter the proposer, never target-task answers or grader details.
    indexed=(prior/'run-03-iterative/round-02/evolution/candidate_SKILL.md').read_text()
    history.append(evidence(prior/'run-03-iterative/confirmation/development',indexed))
    for old in sorted(root.glob('round-*')):
        if old==folder:continue
        skill=old/'evolution/candidate_SKILL.md';result=old/'development/result.json'
        if skill.exists() and result.exists():
            try:history.append(evidence(old/'development',skill.read_text()))
            except ValueError:pass
            record=old/'ROUND.json'
            if record.exists():
                previous=json.loads(record.read_text())
                dev=previous.get('development');check=previous.get('development_contract',{'passed':False})
                if dev and valid(dev,check) and dev['tokens']['total_tokens']<parent_tokens:
                    parent_text=skill.read_text();parent_tokens=dev['tokens']['total_tokens']
    history=history[-20:]
    shutil.copytree(skills,folder/'parent_skills')
    target=folder/'parent_skills/threejs/SKILL.md'
    target.write_text(parent_text)
    (folder/'grader_environment').symlink_to(prior/'run-01/grader_environment',target_is_directory=True)
    study=Study(argparse.Namespace(workspace=str(workspace),out=str(folder),keys_file=args.keys_file,allow_paid=True))
    line=next(line.strip() for line in original.splitlines() if re.search(r'if\s*\(.*index.*toNonIndexed\(',line))
    contract={'source':'Original public SkillsBench threejs/SKILL.md, Mesh baking section',
              'source_sha256':hashlib.sha256(original.encode()).hexdigest(),
              'immutable_original_serialization_line':line,
              'constraint':'Retain this original public serialization convention in the proposed skill, with a complete usable code example. Optimize workflow without removing it.',
              'solver_environment':'Benchmark skills are attached files under bench_skills/, not native registered expert skill IDs. Bundled scripts are available through ordinary file/shell tools.',
              'data_boundary':'No target-task outputs, reference coordinates, verifier content or hidden answers are included.'}
    save(folder/'STARTED.json',{'round':args.round,'parent_sha256':hashlib.sha256(parent_text.encode()).hexdigest(),
        'source_contract':'Original public SKILL.md serialization convention; no reference coordinates or target answers'})
    candidate,summary=evolve(workspace,target,folder/'evolution',[r[0] for r in history],[r[1] for r in history],
        study.transport.evolution_key(),study.transport.scrub,allow_paid=True,adapter_contract=contract)
    reference=json.loads((prior/'run-03-iterative/benchmark/with-skills/result.json').read_text())
    assert reference['task']==TEST and reference['score']['strict']==1
    state={'round':args.round,'model':'gpt-6.1-sol','evolution':summary,'new_contract_is_extension':True,
           'inputs':'DEV histories plus original public skill contract, no target answers',
           'baseline_total_tokens':baseline[2]['tokens']['total_tokens']+reference['tokens']['total_tokens']}
    if candidate is None or line not in candidate:
        state['status']='proposal_missing_or_contract_not_preserved';save(folder/'ROUND.json',state);return
    dev=study.solve('development',DEV,candidate);dev_check=contract_check(folder/'development')
    state.update({'development':dev,'development_contract':dev_check})
    if not valid(dev,dev_check):state['status']='development_failed';save(folder/'ROUND.json',state);return
    target_result=study.solve('adaptive-check',TEST,candidate);target_check=contract_check(folder/'adaptive-check')
    state.update({'adaptive_check':target_result,'adaptive_contract':target_check,
                 'target_role':'Adaptive development check on a previously inspected task, not independent held-out evidence.'})
    total=dev['tokens']['total_tokens']+target_result['tokens']['total_tokens'];state['two_task_tokens']=total
    if not valid(target_result,target_check) or total>=state['baseline_total_tokens']:
        state['status']='small_check_not_improved';save(folder/'ROUND.json',state);return
    confirm=root/f'confirmation-{args.round:02d}';confirm.mkdir()
    (confirm/'grader_environment').symlink_to(prior/'run-01/grader_environment',target_is_directory=True)
    study=Study(argparse.Namespace(workspace=str(workspace),out=str(confirm),keys_file=args.keys_file,allow_paid=True))
    confirmed=[]
    for label,task in [('development',DEV),('adaptive-check',TEST)]:
        row=study.solve(label,task,candidate);check=contract_check(confirm/label);confirmed.append({'result':row,'contract':check})
    state['confirmation']=confirmed
    improved=all(valid(x['result'],x['contract']) for x in confirmed) and sum(x['result']['tokens']['total_tokens'] for x in confirmed)<state['baseline_total_tokens']
    state['status']='small_scope_success_confirmed' if improved else 'small_scope_success_not_confirmed'
    state['stop_optimization']=improved or args.round==30
    save(folder/'ROUND.json',state)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True)
    p.add_argument('--round',type=int,required=True);p.add_argument('--keys-file',required=True);p.add_argument('--allow-paid',action='store_true')
    run(p.parse_args())
