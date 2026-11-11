"""Frozen comparison on all two tasks compatible with this particular skill."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
from native_evolution import require_paid
from run import Study, DEV, TEST, save


def run(args):
    require_paid(args.allow_paid)
    root,workspace=Path(args.out).resolve(),Path(args.workspace).resolve()
    record=json.loads(Path(args.success_record).read_text())
    if record['status']!='small_scope_success_confirmed':raise RuntimeError('Small-scope success must be confirmed first')
    selected=Path(args.success_record).parent/'evolution/candidate_SKILL.md'
    text=selected.read_text()
    expected=record['development']['skill_sha256']
    if hashlib.sha256(text.encode()).hexdigest()!=expected:raise ValueError('Frozen skill changed')
    if root.exists():raise RuntimeError('Do not overwrite or duplicate a paid benchmark batch')
    root.mkdir(parents=True)
    save(root/'FROZEN.json',{'scope':'All two compatible SkillsBench tasks, not all 87 tasks',
        'skill_sha256':expected,'selected_round':record['round'],'new_optimization_after_freeze':False,
        'evaluation_role':'Both tasks were used for adaptive development; this is an in-sample frozen comparison, not unseen generalization.'})
    rows=[]
    for task in [DEV,TEST]:
        folder=root/task;folder.mkdir()
        (folder/'grader_environment').symlink_to(workspace/'01_任务结果/2026-11-10_skillsbench_evolution/run-01/grader_environment',target_is_directory=True)
        study=Study(argparse.Namespace(workspace=str(workspace),out=str(folder),keys_file=args.keys_file,allow_paid=True))
        labels=['no-skills','with-skills','with-CogniLife-skills']
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            futures=[pool.submit(study.solve,label,task,text if label==labels[2] else None,label==labels[0]) for label in labels]
            rows.extend(f.result() for f in futures)
        save(root/'FULL_TWO_RESULTS.json',{'scope':'two compatible tasks x three groups','skill_sha256':expected,'rows':rows})
    print(json.dumps([{'task':r['task'],'group':r['label'],'tests':r['score']['passed'],'tokens':r['tokens']['total_tokens']} for r in rows],ensure_ascii=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True)
    p.add_argument('--success-record',required=True);p.add_argument('--keys-file',required=True);p.add_argument('--allow-paid',action='store_true')
    run(p.parse_args())
