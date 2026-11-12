"""Retry native cloud Docker with retained diagnostics; no local runtime operations."""
import argparse
from cloud_engine_check import SCRIPT
from profy_cloud_probe import Probe

SCRIPT=SCRIPT.replace(" command(['sudo','-n','apt-get','update'],180)"," command(['sudo','-n','mkdir','-p','/var/lib/apt/lists/partial'],15)\n command(['sudo','-n','apt-get','-o','Acquire::Retries=0','-o','Acquire::http::Timeout=15','-o','Acquire::https::Timeout=15','update'],120)")
SCRIPT=SCRIPT.replace("finally:\n pidfile=work/'engine.pid'", "finally:\n operations=work/'operations.log'\n if operations.exists():report['operations_tail']=re.sub(r'https?://\\S+','[URL]',operations.read_text(errors='replace')[-7000:])\n pidfile=work/'engine.pid'")
assert "report['operations_tail']" in SCRIPT
compile(SCRIPT,'<cloud-native-engine-retry>','exec')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True);p.add_argument('--keys-file',required=True);p.add_argument('--allow-paid',action='store_true');args=p.parse_args()
    study=Probe(args);folder=study.out/'cloud-native-engine-retry';folder.mkdir(exist_ok=False)
    script=folder/'cloud_engine_check.py';script.write_text(SCRIPT);user='cgl-native-cloud-engine-retry'
    upload=study.transport.upload(script,user);session=study.transport.api('/v1/sessions',{'agent':study.transport.expert_id,'title':'Native cloud engine with retained error output'},user)['id']
    body={'agent':{'id':study.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],
        'input':'Run the attached cloud_engine_check.py unchanged with python3 using one foreground bash call with background=false and timeout850. Cloud root capabilities have already been checked. This script retains the package-manager error, tests a private temporary Docker engine with network bridge and iptables changes disabled, then removes its own engine data. Do not edit the script, inspect credentials, use skills or Memory, buy anything or ask questions. Return [OUTPUT] outputs/deliverables.zip. If bash becomes background, await it then touch outputs/deliverables.zip in foreground without rerunning. This is an environment check, not a benchmark result.',
        'stream':True,'session_id':session,'attachment_file_ids':[upload['file_id']]}
    row=study.execute(folder,'cloud-native-engine-retry','environment-check',None,True,body,session,user,script)
    if not row['output_received']:raise RuntimeError('Inspect existing events for delivery')
    print((folder/'output/engine_check.json').read_text())
