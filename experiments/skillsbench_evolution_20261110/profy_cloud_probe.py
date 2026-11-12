"""One serial cloud capability check; no local runtime installation or benchmark score."""
import argparse,json
from pathlib import Path
from run import Study,save

SCRIPT='''import os,sys,json,shutil,importlib.util,hashlib,zipfile,subprocess,platform
from pathlib import Path
p=Path('output');p.mkdir(exist_ok=True)
d={'uid':os.getuid(),'platform':sys.platform,'root_writable':os.access('/root',os.W_OK),'free_bytes':shutil.disk_usage('.').free,'commands':{k:shutil.which(k) for k in ['python3','node','npm','apt-get','sudo','libreoffice','ssconvert','docker','uv','git']},'modules':{k:bool(importlib.util.find_spec(k)) for k in ['pytest','numpy','scipy','pandas','openpyxl','cvxpy','fitz']}}
d['machine']=platform.machine()
d['sudo_noninteractive']=subprocess.run(['sudo','-n','true'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=5).returncode==0 if shutil.which('sudo') else False
d['userspace_tools']={k:shutil.which(k) for k in ['proot','skopeo','umoci','unshare','busybox']}
f=p/'capabilities.json';f.write_text(json.dumps(d,indent=2))
m={'input_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest()}}
with zipfile.ZipFile('deliverables.zip','w') as z:z.write(f,str(f));z.writestr('manifest.json',json.dumps(m))
print('SBP_NATIVE_ZIP_SHA256:'+hashlib.sha256(Path('deliverables.zip').read_bytes()).hexdigest())
print('[OUTPUT] deliverables.zip')
'''

class Probe(Study):
    def grade(self,task,folder):
        return {'strict':0,'tests':0,'passed':0,'failed':0,'skipped':0,'environment_probe_only':True,'not_a_benchmark_result':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True);p.add_argument('--keys-file',required=True);p.add_argument('--allow-paid',action='store_true');args=p.parse_args()
    study=Probe(args);f=study.out/'cloud-capabilities';f.mkdir(exist_ok=False)
    script=f/'cloud_probe.py';script.write_text(SCRIPT)
    user='cgl-cloud-grader-probe';upload=study.transport.upload(script,user)
    session=study.transport.api('/v1/sessions',{'agent':study.transport.expert_id,'title':'Cloud grader capability check'},user)['id']
    body={'agent':{'id':study.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],'input':'Run the attached cloud_probe.py unchanged once using bash and Python. Do not install anything, inspect credentials, use Memory, discover other skills or ask questions. Return the actual generated file using [OUTPUT] deliverables.zip. This is only an execution capability check, not a benchmark answer.','stream':True,'session_id':session,'attachment_file_ids':[upload['file_id']]}
    row=study.execute(f,'cloud-capabilities','environment-probe',None,True,body,session,user,script)
    if not row['completed'] or not row['output_received']:raise RuntimeError('Cloud environment check incomplete')
    print((f/'output/capabilities.json').read_text())
