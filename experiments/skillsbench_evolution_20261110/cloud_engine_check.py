"""Check one temporary engine on authorized Profy compute; install nothing locally."""
import argparse,json
from pathlib import Path
from profy_cloud_probe import Probe
from run import save

SCRIPT=r'''import os,sys,json,shutil,subprocess,time,hashlib,zipfile,re
from pathlib import Path
base=Path.cwd();out=base/'output';out.mkdir(exist_ok=True);delivery=base/'outputs';delivery.mkdir(exist_ok=True)
work=base/'.cgl-engine-check';work.mkdir(exist_ok=False);report={'local_computer_used':False,'new_service_purchased':False,'engine_test_passed':False}
process=None
def command(args,timeout):
 with (work/'operations.log').open('a') as log:
  p=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
 if p.returncode:raise RuntimeError('Command failed: '+args[0]+' '+str(p.returncode))
try:
 assert shutil.disk_usage('.').free>50_000_000_000,'Insufficient cloud free space'
 command(['sudo','-n','apt-get','update'],180)
 command(['sudo','-n','apt-get','install','-y','--no-install-recommends','docker.io'],300)
 socket=work/'engine.sock';pidfile=work/'engine.pid'
 log=(work/'daemon.log').open('w')
 process=subprocess.Popen(['sudo','-n','dockerd','--data-root='+str(work/'data'),'--exec-root='+str(work/'run'),'--pidfile='+str(pidfile),'--host=unix://'+str(socket),'--iptables=false','--bridge=none','--storage-driver=vfs'],stdout=log,stderr=subprocess.STDOUT)
 cli=['sudo','-n','docker','-H','unix://'+str(socket)]
 for i in range(40):
  p=subprocess.run(cli+['info'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=5)
  if p.returncode==0:break
  if process.poll() is not None:raise RuntimeError('Cloud engine could not start')
  time.sleep(1)
 else:raise RuntimeError('Cloud engine startup timeout')
 command(cli+['pull','alpine:3.20'],120)
 command(cli+['run','--rm','--network','none','alpine:3.20','echo','cgl-cloud-engine-ok'],45)
 report['engine_test_passed']=True
except Exception as e:
 report['error']=str(e)
 daemon=work/'daemon.log'
 if daemon.exists():report['daemon_tail']=re.sub(r'https?://\S+','[URL]',daemon.read_text(errors='replace')[-3500:])
finally:
 pidfile=work/'engine.pid'
 if pidfile.exists():
  pid=pidfile.read_text().strip()
  if pid.isdigit():subprocess.run(['sudo','-n','kill','-TERM',pid],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 if process:
  try:process.wait(timeout=20)
  except subprocess.TimeoutExpired:process.terminate()
 assert work.parent==base and work.name=='.cgl-engine-check'
 subprocess.run(['sudo','-n','rm','-rf',str(work)],check=True)
 report['temporary_engine_data_removed']=not work.exists()
(out/'engine_check.json').write_text(json.dumps(report,indent=2))
f=out/'engine_check.json';manifest={'input_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'files':{'output/engine_check.json':hashlib.sha256(f.read_bytes()).hexdigest()}}
with zipfile.ZipFile(delivery/'deliverables.zip','w') as z:z.write(f,'output/engine_check.json');z.writestr('manifest.json',json.dumps(manifest))
print('SBP_NATIVE_ZIP_SHA256:'+hashlib.sha256((delivery/'deliverables.zip').read_bytes()).hexdigest());print('[OUTPUT] outputs/deliverables.zip')
'''

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True);p.add_argument('--keys-file',required=True);p.add_argument('--allow-paid',action='store_true');args=p.parse_args()
    study=Probe(args);folder=study.out/'cloud-engine-check';folder.mkdir(exist_ok=False)
    script=folder/'cloud_engine_check.py';script.write_text(SCRIPT);user='cgl-cloud-engine-check'
    upload=study.transport.upload(script,user);session=study.transport.api('/v1/sessions',{'agent':study.transport.expert_id,'title':'One temporary cloud engine check'},user)['id']
    body={'agent':{'id':study.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],'input':'Run the attached cloud_engine_check.py unchanged using python3. It checks one temporary engine in this cloud session and removes its own generated engine data afterwards. Do not modify the script, inspect credentials, use Memory or skills, buy anything or ask questions. Use timeout 850 for the bash call. Return the generated [OUTPUT] outputs/deliverables.zip. This is not a benchmark score.','stream':True,'session_id':session,'attachment_file_ids':[upload['file_id']]}
    result=study.execute(folder,'cloud-engine-check','cloud-environment-check',None,True,body,session,user,script)
    if not result['output_received']:raise RuntimeError('Cloud engine check artifact missing')
    print((folder/'output/engine_check.json').read_text())
