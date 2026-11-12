"""Retry the documented HTTPS engine location, only on existing Profy compute."""
import argparse
from cloud_user_engine_check import SCRIPT
from profy_cloud_probe import Probe

SCRIPT = SCRIPT.replace("env['PYTHONPATH']=str(work/'tools')", "env['PYTHONPATH']=str(work/'tools');env['UDOCKER_TARBALL']='https://download.a.incd.pt/udocker/udocker-englib-1.2.11.tar.gz'")
SCRIPT = SCRIPT.replace("'udocker'],120)", "'udocker==1.3.17'],120)")
SCRIPT = SCRIPT.replace("finally:\n shutil.rmtree(work)", "finally:\n log=work/'operations.log'\n if log.exists():report['operations_tail']=re.sub(r'https?://\\S+','[URL]',log.read_text(errors='replace')[-6000:])\n shutil.rmtree(work)")
assert 'UDOCKER_TARBALL' in SCRIPT and "report['operations_tail']" in SCRIPT
compile(SCRIPT, '<cloud-only-runtime-check>', 'exec')

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--workspace',required=True);p.add_argument('--out',required=True)
    p.add_argument('--keys-file',required=True);p.add_argument('--allow-paid',action='store_true')
    args=p.parse_args();study=Probe(args)
    folder=study.out/'cloud-user-engine-https-check';folder.mkdir(exist_ok=False)
    script=folder/'cloud_user_engine_check.py';script.write_text(SCRIPT)
    user='cgl-cloud-user-engine-https'
    upload=study.transport.upload(script,user)
    session=study.transport.api('/v1/sessions',{'agent':study.transport.expert_id,'title':'Serial temporary cloud runtime HTTPS check'},user)['id']
    body={'agent':{'id':study.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],
        'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],
        'input':'Run the attached cloud_user_engine_check.py unchanged using python3. Use a foreground bash call with background=false and timeout850. It checks the official HTTPS udocker runtime in this cloud session, keeps the failure diagnostic and removes its own temporary directory. Do not modify the script, invoke skills or Memory, inspect credentials, purchase services or ask questions. Return the actual [OUTPUT] outputs/deliverables.zip. If bash becomes background, await it then touch outputs/deliverables.zip in foreground to deliver it; do not rerun the script. This is an environment check, not a benchmark result.',
        'stream':True,'session_id':session,'attachment_file_ids':[upload['file_id']]}
    row=study.execute(folder,'cloud-user-engine-https-check','environment-check',None,True,body,session,user,script)
    if not row['output_received']:raise RuntimeError('Cloud diagnostic artifact not received; inspect existing events, do not rerun blindly')
    print((folder/'output/user_engine_check.json').read_text())
