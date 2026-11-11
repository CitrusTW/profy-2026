"""Reuse Profy transport and received Evolution; original Docker verifier stays private."""
import argparse
import concurrent.futures
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from iterate import evidence
from native_evolution import evolve, require_paid
from run import Study, save, sha

DEV='grid-dispatch-operator'
TEST='energy-market-pricing'
SKILL='economic-dispatch'
IMAGE='cognilife-sb-grid-grader-20261111'


class NetworkStudy(Study):
    def __init__(self,args):
        args.dev_task=DEV;args.skill_name=SKILL
        super().__init__(args)

    def input_file(self,task):
        if task not in [DEV,TEST]:raise ValueError('Task not in frozen family')
        return self.bench/task/'environment/network.json','network.json'

    def instructions(self,task,no_skills):
        names=sorted(p.parent.name for p in (self.bench/task/'environment/skills').glob('*/SKILL.md'))
        setup=('No benchmark skills are supplied. Solve with ordinary code/file tools. Do not discover or activate any other expert/user/builtin skill packages. ' if no_skills else
            'Unzip benchmark_skills.zip into this session. Use read to load all supplied SKILL.md files in full: '+', '.join('bench_skills/'+n+'/SKILL.md' for n in names)+'. Follow relevant supplied instructions and references. Compute and print SBP_ACTIVE_SKILL_SHA256:<computed hash> of bench_skills/economic-dispatch/SKILL.md with bash. ')
        common='''
Execution adapter instructions (same in all groups): Unzip task_input.zip into this session directory, where network.json is the original input. Paths /root/ mean this session directory. Preserve network.json unchanged. Ordinary Python and file tools are available; install mathematical dependencies if needed. No web search, Memory, delegation, other sessions, benchmark tests, oracle or reference answers. Do not ask questions. Use at most 48 tool calls and 24 model turns.
Write the original requested report.json. After solving, use Python zipfile to package its exact bytes into deliverables.zip with archive path output/report.json. Include manifest.json at ZIP root containing {"input_sha256":"computed SHA256 of network.json","files":{"output/report.json":"computed SHA256 of report.json"}}. This archive path is file transport only; do not change the report content to package it. Print [OUTPUT] deliverables.zip and SBP_NATIVE_ZIP_SHA256:<computed SHA256 of deliverables.zip>. Final response briefly names the output file.
'''
        return setup,common

    def grade(self,task,folder,oracle=False):
        source=self.bench/task
        assert self.input_file(task)[0].read_bytes()==self.input_file(DEV)[0].read_bytes(), 'Shared grader image must contain the exact task input'
        scoring=folder/'scoring_only';scoring.mkdir(parents=True,exist_ok=True)
        output=folder/'output';output.mkdir(exist_ok=True)
        args=['docker','run','--rm','--network','none','--cpus','2','--memory','4g',
            '--mount',f'type=bind,source={source/"verifier"},target=/verifier,readonly',
            '--mount',f'type=bind,source={scoring},target=/logs/verifier',
            '--mount',f'type=bind,source={output},target=/model_output,readonly']
        command='if [ -f /model_output/report.json ]; then cp /model_output/report.json /root/report.json; fi; bash /verifier/test.sh'
        if oracle:
            args+=['--mount',f'type=bind,source={source/"oracle"},target=/oracle,readonly']
            command='bash /oracle/solve.sh && bash /verifier/test.sh'
        args += [IMAGE,'bash','-lc',command]
        p=subprocess.run(args,capture_output=True,text=True,timeout=900)
        (scoring/'docker.log').write_text(p.stdout+p.stderr)
        ctrf=scoring/'ctrf.json';reward=scoring/'reward.txt'
        if not ctrf.exists() or not reward.exists():raise RuntimeError('Original verifier did not produce scores; inspect local docker.log before any more paid calls')
        result=json.loads(ctrf.read_text())['results'];summary=result['summary']
        score={'tests':summary['tests'],'passed':summary['passed'],'failed':summary['failed'],
            'skipped':summary.get('skipped',0),'strict':int(reward.read_text().strip()=='1'),
            'original_returncode':p.returncode,'source_sha256':sha((source/'verifier/test_outputs.py').read_bytes()),
            'original_test_script_sha256':sha((source/'verifier/test.sh').read_bytes()),
            'verifier_unmodified':True,'grader_image':IMAGE,'oracle_environment_check':oracle}
        save(scoring/'receipt.json',score);return score


def valid(row):
    s=row['score']
    return row['completed'] and row['error'] is None and row['output_received'] and row['target_skill_read_verified'] and not row['external_skill_tools_observed'] and s['strict']==1 and s['passed']==s['tests'] and not s['skipped']


def run(args):
    root=Path(args.out).resolve();root.mkdir(parents=True,exist_ok=True)
    study=NetworkStudy(args)
    if args.phase=='preflight':
        scores={t:study.grade(t,root/'environment-check'/t,oracle=True) for t in [DEV,TEST]}
        if not all(s['strict']==1 and s['tests']>0 for s in scores.values()):raise RuntimeError('Official oracle environment check failed; no paid calls permitted')
        save(root/'ENVIRONMENT_READY.json',{'scores':scores,'model_calls':0,'oracle_never_sent_to_evolution':True});return
    require_paid(args.allow_paid)
    if not (root/'ENVIRONMENT_READY.json').exists():raise ValueError('Original scoring environment must pass first')
    if args.phase=='baseline':
        row=study.solve('dev-original',DEV);save(root/'BASELINE.json',row);return
    if args.phase=='evaluate':
        records=[p for p in sorted(root.glob('round-*/ROUND.json')) if json.loads(p.read_text())['status']=='small_scope_success_confirmed']
        if not records:raise ValueError('Confirmed development success required before evaluation')
        selected=records[-1];candidate=(selected.parent/'evolution/candidate_SKILL.md').read_text()
        frozen=root/'frozen-evaluation'
        if frozen.exists():raise ValueError('Never overwrite evaluation')
        frozen.mkdir();save(frozen/'FROZEN.json',{'selected_round':json.loads(selected.read_text())['round'],'skill_sha256':sha(candidate.encode()),'development':DEV,'evaluation':TEST})
        fresh=NetworkStudy(argparse.Namespace(**{**vars(args),'out':str(frozen)}))
        labels=['no-skills','with-skills','with-CogniLife-skills']
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            futures=[pool.submit(fresh.solve,label,TEST,candidate if label==labels[2] else None,label==labels[0]) for label in labels]
            rows=[f.result() for f in futures]
        save(frozen/'RESULTS.json',{'rows':rows,'paper_changed':False});return
    if args.phase!='round':raise ValueError('Unsupported phase')
    if not 6<=args.round<=30:raise ValueError('Combined round IDs capped at 30, including the five threejs rounds')
    folder=root/f'round-{args.round:02d}'
    if folder.exists():raise ValueError('Preserve prior paid attempts')
    folder.mkdir();original=study.target.read_text()
    history=[evidence(root/'dev-original',original,DEV,TEST)]
    parent=original;best_tokens=history[0][2]['tokens']['total_tokens']
    for old in sorted(root.glob('round-*')):
        skill=old/'evolution/candidate_SKILL.md';record=old/'development/result.json'
        if not skill.exists() or not record.exists():continue
        text=skill.read_text()
        try:e=evidence(old/'development',text,DEV,TEST)
        except ValueError:continue
        history.append(e)
        if valid(e[2]) and e[2]['tokens']['total_tokens']<best_tokens:parent=text;best_tokens=e[2]['tokens']['total_tokens']
    shutil.copytree(study.target.parent.parent,folder/'parent_skills')
    target=folder/'parent_skills'/SKILL/'SKILL.md';target.write_text(parent)
    contract={'origin':'New external execution adapter information, not a replacement Evolution algorithm',
        'environment':'Public benchmark skills are files under bench_skills/, not registered native skill IDs. Use ordinary file/Python tools for their resources.',
        'invariants':'Keep the original public skill generalizable and preserve original task requirements. No evaluation task, verifier, oracle, target outputs or gold is included.'}
    candidate,summary=evolve(study.workspace,target,folder/'evolution',[e[0] for e in history][-20:],[e[1] for e in history][-20:],study.transport.evolution_key(),study.transport.scrub,allow_paid=True,adapter_contract=contract)
    state={'round':args.round,'development_task':DEV,'unseen_evaluation_task':TEST,'evolution':summary,'evolution_provider':'OpenRouter owner key','candidate_authored_by_chat':False,'baseline_tokens':history[0][2]['tokens']['total_tokens']}
    if candidate is None:state['status']='no_proposal';save(folder/'ROUND.json',state);return
    fresh=NetworkStudy(argparse.Namespace(**{**vars(args),'out':str(folder)}))
    dev=fresh.solve('development',DEV,candidate);state['development']=dev
    if valid(dev) and dev['tokens']['total_tokens']<state['baseline_tokens']:
        confirm=fresh.solve('confirmation',DEV,candidate);state['confirmation']=confirm
        success=valid(confirm) and confirm['tokens']['total_tokens']<state['baseline_tokens']
    else:success=False
    state['status']='small_scope_success_confirmed' if success else 'development_not_improved'
    state['stop_optimization']=success or args.round==30
    save(folder/'ROUND.json',state)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['preflight','baseline','round','evaluate'])
    p.add_argument('--workspace',required=True);p.add_argument('--out',required=True)
    p.add_argument('--keys-file');p.add_argument('--allow-paid',action='store_true');p.add_argument('--round',type=int)
    run(p.parse_args())
