"""Diagnose the existing cloud apt failure and capabilities without installing software."""
import argparse
from profy_cloud_probe import Probe

SCRIPT=r'''import json,subprocess,hashlib,zipfile,os,re,shutil
from pathlib import Path
base=Path.cwd();work=base/'.cgl-system-diagnosis';work.mkdir(exist_ok=False)
out=base/'output';out.mkdir(exist_ok=True);delivery=base/'outputs';delivery.mkdir(exist_ok=True)
report={'cloud_only':True,'software_installed':False}
def command(args,timeout):
 try:
  p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
  return {'returncode':p.returncode,'output':re.sub(r'https?://S+','[URL]',p.stdout[-6000:])}
 except Exception as e:return {'error':str(e)}
report['root_capabilities']=command(['sudo','-n','python3','-c',"import os,json;d=dict(s.split(':',1) for s in open('/proc/self/status') if ':' in s);c=int(d['CapEff'].strip(),16);print(json.dumps({'uid':os.getuid(),'cap_sys_admin':bool(c&(1<<21)),'cap_sys_chroot':bool(c&(1<<18))}))"],5)
report['user_namespace']=command(['unshare','-Ur','true'],5)
try:
 report['apt_update']=command(['sudo','-n','apt-get','-o','Acquire::Retries=0','-o','Acquire::http::Timeout=10','-o','Acquire::https::Timeout=10','-o','Dir::State::Lists='+str(work/'lists'),'-o','Dir::Cache='+str(work/'cache'),'update'],45)
finally:
 subprocess.run(['sudo','-n','rm','-rf',str(work)],check=True,timeout=15)
 report['temporary_data_removed']=not work.exists()
f=out/'system_diagnosis.json';f.write_text(json.dumps(report,indent=2))
manifest={'input_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'files':{'output/system_diagnosis.json':hashlib.sha256(f.read_bytes()).hexdigest()}}
with zipfile.ZipFile(delivery/'deliverables.zip','w') as z:z.write(f,'output/system_diagnosis.json');z.writestr('manifest.json',json.dumps(manifest))
print(json.dumps(report));print('SBP_NATIVE_ZIP_SHA256:'+hashlib.sha256((delivery/'deliverables.zip').read_bytes()).hexdigest());print('[OUTPUT] outputs/deliverables.zip')
'''

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True);p.add_argument('--keys-file',required=True);p.add_argument('--allow-paid',action='store_true');args=p.parse_args()
    study=Probe(args);folder=study.out/'cloud-system-diagnosis';folder.mkdir(exist_ok=False)
    script=folder/'cloud_system_diagnosis.py';script.write_text(SCRIPT);user='cgl-cloud-system-diagnosis'
    upload=study.transport.upload(script,user);session=study.transport.api('/v1/sessions',{'agent':study.transport.expert_id,'title':'Diagnose original cloud package-manager failure'},user)['id']
    body={'agent':{'id':study.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],
        'input':'Run the attached cloud_system_diagnosis.py unchanged using one foreground bash call with background=false and timeout100. It checks only this cloud session, diagnoses the existing package-manager failure without installing software, and deletes its own temporary package index directory. Do not modify it, inspect credentials, use skills or Memory, purchase anything or ask questions. Return [OUTPUT] outputs/deliverables.zip. This is not a benchmark result.',
        'stream':True,'session_id':session,'attachment_file_ids':[upload['file_id']]}
    row=study.execute(folder,'cloud-system-diagnosis','environment-check',None,True,body,session,user,script)
    if not row['output_received']:raise RuntimeError('Inspect existing events for delivery')
    print((folder/'output/system_diagnosis.json').read_text())
