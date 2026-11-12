"""Fix the observed Debian post-install PATH failure, using cloud compute only."""
import argparse
from cloud_engine_retry import SCRIPT
from profy_cloud_probe import Probe

SCRIPT=SCRIPT.replace("['sudo','-n','apt-get','install','-y','--no-install-recommends','docker.io']", "['sudo','-n','env','PATH=/usr/sbin:/usr/bin:/sbin:/bin','DEBIAN_FRONTEND=noninteractive','apt-get','install','-y','--no-install-recommends','docker.io','docker-cli']")
assert 'DEBIAN_FRONTEND=noninteractive' in SCRIPT and "'docker-cli'" in SCRIPT
compile(SCRIPT,'<cloud-engine-secure-path>','exec')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True);p.add_argument('--keys-file',required=True);p.add_argument('--allow-paid',action='store_true');args=p.parse_args()
    study=Probe(args);folder=study.out/'cloud-native-engine-secure-path';folder.mkdir(exist_ok=False)
    script=folder/'cloud_engine_check.py';script.write_text(SCRIPT);user='cgl-cloud-engine-secure-path'
    upload=study.transport.upload(script,user);session=study.transport.api('/v1/sessions',{'agent':study.transport.expert_id,'title':'Fix observed cloud package installation PATH failure'},user)['id']
    body={'agent':{'id':study.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],
        'input':'Run the attached cloud_engine_check.py unchanged with python3 using one foreground bash call with background=false and timeout850. The exact observed Debian package post-install failure is an insecure inherited PATH. This script uses the trusted system PATH for package installation, includes the separate Docker CLI package, tests its own temporary private engine, and removes that engine data. Do not modify it, inspect credentials, use skills or Memory, buy anything or ask questions. Return [OUTPUT] outputs/deliverables.zip. If background starts, await it then touch outputs/deliverables.zip in foreground without rerunning. This is an environment check, not a benchmark score.',
        'stream':True,'session_id':session,'attachment_file_ids':[upload['file_id']]}
    row=study.execute(folder,'cloud-native-engine-secure-path','environment-check',None,True,body,session,user,script)
    if not row['output_received']:raise RuntimeError('Inspect existing events for delivery')
    print((folder/'output/engine_check.json').read_text())
