"""Offline public task/skill inventory; never read oracle, verifier, gold or keys."""
import argparse
import hashlib
import json
from pathlib import Path


def inventory(tasks):
    rows=[]
    for task in sorted(Path(tasks).iterdir()):
        if not task.is_dir() or not (task/'task.md').exists():continue
        env=task/'environment';skills=[]
        for path in sorted((env/'skills').glob('*/SKILL.md')):
            text=path.read_text();licenses=[p for p in path.parent.iterdir() if p.is_file() and p.name.lower().startswith('license')]
            prohibition=any('Create derivative works' in p.read_text(errors='replace') for p in licenses)
            skills.append({'name':path.parent.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'body_bytes':path.stat().st_size,'declares_proprietary':'license: Proprietary' in text,
                'bundled_license_explicit_derivative_prohibition':prohibition,
                'license_files':[p.relative_to(env).as_posix() for p in licenses]})
        public=[p for p in env.rglob('*') if p.is_file() and 'skills' not in p.relative_to(env).parts]
        rows.append({'task':task.name,'task_sha256':hashlib.sha256((task/'task.md').read_bytes()).hexdigest(),
            'public_environment_bytes':sum(p.stat().st_size for p in public),'public_environment_file_count':len(public),
            'dockerfile_exists':(env/'Dockerfile').exists(),'skills':skills,
            'requires_license_review_before_derivation':any(s['declares_proprietary'] or s['bundled_license_explicit_derivative_prohibition'] for s in skills)})
    return {'task_count':len(rows),'paid_calls':0,'keys_read':False,'scoring_or_oracle_read':False,
        'tasks_with_license_review_flag':sum(r['requires_license_review_before_derivation'] for r in rows),
        'scope':'Static source inventory, not executed benchmark results or a legal clearance', 'rows':rows}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tasks',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    data=inventory(a.tasks)
    assert data['task_count']==87,'Unexpected benchmark version; do not silently change the study scope'
    Path(a.out).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in data.items() if k!='rows'}))
