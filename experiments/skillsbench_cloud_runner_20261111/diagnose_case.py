"""Read only this case's setup status after the foreground tool timeout; never solve or score."""
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'skillsbench_evolution_20261110'))
from profy_cloud_probe import Probe

SCRIPT=r'''import json,hashlib,zipfile,subprocess,shutil
from pathlib import Path
base=Path.cwd();report={'diagnosis_only':True,'new_solver_run':False,'new_scoring_run':False}
report['paths']={str(p):{'free_bytes':shutil.disk_usage(p).free,'filesystem':subprocess.run(['stat','-f','-c','%T',str(p)],capture_output=True,text=True).stdout.strip()} for p in [base,Path('/'),Path('/tmp'),Path('/var/tmp')]}
for name in ['case_context.json','setup_error.json']:
 p=base/name
 if p.exists():report[name]=json.loads(p.read_text())
report['setup_logs']={str(p):p.read_text(errors='replace')[-6000:] for p in base.glob('cgl-task-*/setup.log')}
report['daemon_logs']={str(p):p.read_text(errors='replace')[-1800:] for p in base.glob('cgl-task-*/daemon.log')}
out=base/'diagnostic_output';out.mkdir(exist_ok=True);f=out/'diagnostic.json';f.write_text(json.dumps(report,indent=2))
manifest={'input_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'files':{'output/diagnostic.json':hashlib.sha256(f.read_bytes()).hexdigest()}}
delivery=base/'outputs';delivery.mkdir(exist_ok=True)
with zipfile.ZipFile(delivery/'deliverables.zip','w') as z:z.write(f,'output/diagnostic.json');z.writestr('manifest.json',json.dumps(manifest))
print('SBP_NATIVE_ZIP_SHA256:'+hashlib.sha256((delivery/'deliverables.zip').read_bytes()).hexdigest());print('[OUTPUT] outputs/deliverables.zip')
'''

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True);p.add_argument('--case',required=True);p.add_argument('--keys-file',required=True);p.add_argument('--allow-paid',action='store_true');args=p.parse_args()
    previous=json.loads((Path(args.case)/'session.json').read_text())
    study=Probe(args);folder=study.out/'diagnose-foreground-timeout';folder.mkdir(exist_ok=False)
    script=folder/'diagnose_case.py';script.write_text(SCRIPT);user=previous['end_user']
    upload=study.transport.upload(script,user)
    body={'agent':{'id':study.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],'input':'Diagnostic only. Run exactly python3 diagnose_case.py using foreground bash with timeout90. Do not solve, grade, edit files, start another setup, inspect credentials, use skills/Memory, purchase anything or ask questions. It reads only this case own setup logs and filesystem metadata. Return the generated [OUTPUT] outputs/deliverables.zip.','stream':True,'session_id':previous['id'],'attachment_file_ids':[upload['file_id']]}
    row=study.execute(folder,'diagnose-foreground-timeout','environment-check',None,True,body,previous['id'],user,script)
    if not row['output_received']:raise RuntimeError('Inspect native events for delivery')
    print((folder/'output/diagnostic.json').read_text())
