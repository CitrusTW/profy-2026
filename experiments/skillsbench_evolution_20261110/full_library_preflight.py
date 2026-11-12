"""Prepare official grading environments, without model calls or exposing reference code."""
import argparse,json,subprocess,time
from pathlib import Path

def run(args):
    tasks=Path(args.tasks).resolve();out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for task in sorted(tasks.iterdir()):
        if not (task/'task.md').exists():continue
        folder=out/task.name;folder.mkdir(exist_ok=True);record=folder/'STATUS.json'
        if record.exists():rows.append(json.loads(record.read_text()));continue
        image='cognilife-sb-full-'+task.name
        state={'task':task.name,'model_calls':0,'reference_material_sent_to_models':False,'status':'preparing'}
        began=time.monotonic();print('PREFLIGHT_START',task.name,flush=True)
        try:
            with (folder/'build.log').open('w') as log:
                p=subprocess.run(['docker','build','-q','-t',image,str(task/'environment')],stdout=log,stderr=subprocess.STDOUT,timeout=1200)
            if p.returncode:raise RuntimeError('Original Dockerfile build failed; inspect local build.log')
            logs=folder/'verifier-logs';logs.mkdir(exist_ok=True)
            command=['docker','run','--rm','--cpus','2','--memory','8g',
                '--mount',f'type=bind,source={task/"oracle"},target=/oracle,readonly',
                '--mount',f'type=bind,source={task/"verifier"},target=/verifier,readonly',
                '--mount',f'type=bind,source={logs},target=/logs/verifier',
                image,'bash','-lc','bash /oracle/solve.sh && bash /verifier/test.sh']
            with (folder/'oracle-environment.log').open('w') as log:
                p=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=1800)
            reward=logs/'reward.txt';state['original_reward']=reward.read_text().strip() if reward.exists() else None
            state['status']='ready' if state['original_reward']=='1' else 'environment_check_failed'
            state['exit_code']=p.returncode
        except Exception as exc:state.update(status='environment_error',error=str(exc))
        state['seconds']=round(time.monotonic()-began,3);record.write_text(json.dumps(state,indent=2)+'\n');rows.append(state)
        (out/'SUMMARY.json').write_text(json.dumps({'model_calls':0,'rows':rows},indent=2)+'\n')
        print('PREFLIGHT_DONE',task.name,state['status'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tasks',required=True);p.add_argument('--out',required=True);run(p.parse_args())
