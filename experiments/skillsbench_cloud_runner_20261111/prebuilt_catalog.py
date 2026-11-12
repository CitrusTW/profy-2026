"""Compare public image tags and environment Git trees; never download image layers."""
import argparse,json,subprocess,urllib.request
from pathlib import Path
PIN='f860ecf02ef53412a030f8661c83d644b739ff01'
BUILDER='12ebd8653093e0734c7902835cb20c054196026c'
REPO='benchflow-ai/skillsbench-task-env'
def get(url,headers=None):
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers or {'User-Agent':'CogniLife-source-check'}),timeout=30) as r:return json.load(r)
def catalog(bench):
    remote=get('https://api.github.com/repos/benchflow-ai/skillsbench/git/trees/'+BUILDER+'?recursive=1')
    assert not remote.get('truncated'),'Incomplete source tree'
    trees={x['path']:x['sha'] for x in remote['tree'] if x['type']=='tree'}
    token=get('https://ghcr.io/token?service=ghcr.io&scope=repository:'+REPO+':pull')['token']
    tags=get('https://ghcr.io/v2/'+REPO+'/tags/list?n=1000',{'Authorization':'Bearer '+token})['tags']
    assert len(tags)<1000,'Pagination required; do not claim complete catalog'
    rows=[]
    for task in sorted(bench.joinpath('tasks').iterdir()):
        if not (task/'task.md').exists():continue
        rel='tasks/'+task.name+'/environment'
        local=subprocess.check_output(['git','-C',str(bench),'rev-parse',PIN+':'+rel],text=True).strip()
        tag='skillsbench-v1.1-'+task.name+'-'+BUILDER[:12]
        rows.append({'task':task.name,'environment_tree_sha':local,'builder_environment_tree_sha':trees.get(rel),'environment_tree_exact_match':local==trees.get(rel),'tag':tag,'tag_exists':tag in tags})
    return {'benchmark_pin':PIN,'builder_commit':BUILDER,'image_repository':'ghcr.io/'+REPO,'image_layers_downloaded':False,'model_calls':0,'tasks':rows,'matching_and_available':sum(x['environment_tree_exact_match'] and x['tag_exists'] for x in rows)}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bench',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    report=catalog(Path(a.bench));Path(a.out).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'tasks':len(report['tasks']),'matching_and_available':report['matching_and_available']}))
