"""Test documented user-space image execution on existing cloud compute only."""
import argparse
from profy_cloud_probe import Probe

SCRIPT=r'''import os,sys,json,shutil,subprocess,hashlib,zipfile,re
from pathlib import Path
base=Path.cwd();work=base/'.cgl-user-engine-check';work.mkdir(exist_ok=False)
out=base/'output';out.mkdir(exist_ok=True);delivery=base/'outputs';delivery.mkdir(exist_ok=True)
report={'local_computer_used':False,'new_service_purchased':False,'user_engine_passed':False}
env=dict(os.environ);env['UDOCKER_DIR']=str(work/'store');env['UDOCKER_TMP']=str(work/'tmp');env['PYTHONPATH']=str(work/'tools')
def command(args,timeout):
 p=subprocess.run(args,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
 with (work/'operations.log').open('a') as log:log.write(p.stdout)
 if p.returncode:raise RuntimeError('Command failed '+str(p.returncode)+': '+re.sub(r'https?://S+','[URL]',p.stdout[-2500:]))
 return p.stdout
try:
 assert shutil.disk_usage('.').free>50_000_000_000
 command(['uv','pip','install','--target',str(work/'tools'),'udocker'],120)
 executable=work/'tools/bin/udocker'
 assert executable.exists(),'udocker entry point not installed'
 cli=[str(executable)]
 command(cli+['install'],180)
 command(cli+['pull','alpine:3.20'],180)
 command(cli+['create','--name=cgl-check','alpine:3.20'],60)
 result=command(cli+['run','--user=root','cgl-check','/bin/sh','-c','echo cgl-user-engine-ok'],90)
 assert 'cgl-user-engine-ok' in result
 report['user_engine_passed']=True;report['method']='udocker user-space execution, not native Docker'
except Exception as e:report['error']=str(e)
finally:
 shutil.rmtree(work);report['temporary_engine_data_removed']=not work.exists()
(out/'user_engine_check.json').write_text(json.dumps(report,indent=2))
f=out/'user_engine_check.json';manifest={'input_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'files':{'output/user_engine_check.json':hashlib.sha256(f.read_bytes()).hexdigest()}}
with zipfile.ZipFile(delivery/'deliverables.zip','w') as z:z.write(f,'output/user_engine_check.json');z.writestr('manifest.json',json.dumps(manifest))
print('SBP_NATIVE_ZIP_SHA256:'+hashlib.sha256((delivery/'deliverables.zip').read_bytes()).hexdigest());print('[OUTPUT] outputs/deliverables.zip')
'''

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True);p.add_argument('--keys-file',required=True);p.add_argument('--allow-paid',action='store_true');args=p.parse_args()
    study=Probe(args);folder=study.out/'cloud-user-engine-check';folder.mkdir(exist_ok=False);script=folder/'cloud_user_engine_check.py';script.write_text(SCRIPT);user='cgl-user-engine-check'
    upload=study.transport.upload(script,user);session=study.transport.api('/v1/sessions',{'agent':study.transport.expert_id,'title':'One temporary user-space cloud check'},user)['id']
    body={'agent':{'id':study.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],'input':'Run the attached cloud_user_engine_check.py unchanged with python3, using bash timeout 850. It checks the documented unprivileged udocker tool and removes its own temporary files. Do not modify it, inspect credentials, invoke skills or Memory, purchase anything or ask questions. Return the actual [OUTPUT] outputs/deliverables.zip. This is not a benchmark score.','stream':True,'session_id':session,'attachment_file_ids':[upload['file_id']]}
    row=study.execute(folder,'cloud-user-engine-check','cloud-environment-check',None,True,body,session,user,script)
    if not row['output_received']:raise RuntimeError('Cloud user-space check artifact missing')
    print((folder/'output/user_engine_check.json').read_text())
