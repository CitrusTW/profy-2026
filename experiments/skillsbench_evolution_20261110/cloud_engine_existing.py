"""Test already unpacked vendor binaries in the same cloud session, without changing package guards."""
import argparse,json
from cloud_engine_retry import SCRIPT
from profy_cloud_probe import Probe

SCRIPT='\n'.join(line for line in SCRIPT.splitlines() if "command(['sudo','-n','apt-get'" not in line and "command(['sudo','-n','mkdir','-p','/var/lib/apt/lists/partial']" not in line)+'\n'
SCRIPT=SCRIPT.replace(" assert shutil.disk_usage('.').free>50_000_000_000,'Insufficient cloud free space'", " assert shutil.disk_usage('.').free>50_000_000_000,'Insufficient cloud free space'\n server=next((p for p in ['/usr/sbin/dockerd','/usr/bin/dockerd'] if Path(p).is_file()),None);client='/usr/bin/docker'\n assert server and Path(client).is_file(),'Vendor binaries not available in this same session'\n report['package_configuration_pending']=True\n report['package_error']='Debian docker.io post-install taint guard rejects PATH; guard was not disabled.'\n report['server_version']=subprocess.run([server,'--version'],stdout=subprocess.PIPE,text=True,check=True).stdout.strip()\n (work/'client-config').mkdir()")
SCRIPT=SCRIPT.replace("['sudo','-n','dockerd',", "['sudo','-n',server,'--group=root',")
SCRIPT=SCRIPT.replace("cli=['sudo','-n','docker','-H',", "cli=['sudo','-n',client,'--config='+str(work/'client-config'),'-H',")
assert "'apt-get'" not in SCRIPT and '--group=root' in SCRIPT
compile(SCRIPT,'<existing-cloud-binaries>','exec')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True);p.add_argument('--keys-file',required=True);p.add_argument('--allow-paid',action='store_true');args=p.parse_args()
    study=Probe(args);folder=study.out/'cloud-native-existing-binaries';folder.mkdir(exist_ok=False)
    previous=json.loads((study.out/'cloud-native-engine-secure-path/request.json').read_text())
    session=previous['session_id'];user='cgl-cloud-engine-secure-path'
    script=folder/'cloud_existing_engine.py';script.write_text(SCRIPT);upload=study.transport.upload(script,user)
    body={'agent':{'id':study.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],
        'input':'Run the attached cloud_existing_engine.py unchanged using foreground bash with background=false and timeout400, in this same existing session. It does not install packages or disable the failing package guard. It tests the already unpacked Docker binaries with a private data directory, root-only socket group, and empty private client config, then removes its own engine data. Do not modify it, inspect credentials, use skills or Memory, buy anything or ask questions. Return [OUTPUT] outputs/deliverables.zip. This is not a benchmark score.',
        'stream':True,'session_id':session,'attachment_file_ids':[upload['file_id']]}
    row=study.execute(folder,'cloud-native-existing-binaries','environment-check',None,True,body,session,user,script)
    if not row['output_received']:raise RuntimeError('Inspect existing events for delivery')
    print((folder/'output/engine_check.json').read_text())
