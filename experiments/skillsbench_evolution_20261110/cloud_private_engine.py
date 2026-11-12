"""Use installed vendor binaries, short socket paths and scoped mount cleanup in the same cloud VM."""
import argparse,json
from profy_cloud_probe import Probe

SCRIPT=r'''import hashlib,json,os,re,shutil,signal,subprocess,tempfile,time,zipfile
from pathlib import Path
base=Path.cwd();out=base/'output';out.mkdir(exist_ok=True);delivery=base/'outputs';delivery.mkdir(exist_ok=True)
work=Path(tempfile.mkdtemp(prefix='cgl-docker-',dir='/tmp'));process=None
report={'cloud_only':True,'engine_test_passed':False,'new_service_purchased':False,'package_configuration_pending':True,'cleanup_errors':[]}
logs=[]
def command(args,timeout):
 p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
 logs.append(p.stdout)
 if p.returncode:raise RuntimeError('Command failed '+str(p.returncode)+': '+p.stdout[-2000:])
 return p.stdout
def cleanup_mounts(root):
 root=str(root)
 targets=[s.split()[4] for s in Path('/proc/self/mountinfo').read_text().splitlines() if s.split()[4]==root or s.split()[4].startswith(root+'/')]
 for path in sorted(set(targets),key=len,reverse=True):
  p=subprocess.run(['sudo','-n','umount',path],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=15)
  if p.returncode:report['cleanup_errors'].append(p.stdout[-500:])
try:
 assert work.parent==Path('/tmp') and work.name.startswith('cgl-docker-')
 assert len(str(work/'run/containerd/containerd.sock').encode())<100
 assert shutil.disk_usage(work).free>50_000_000_000
 old=base/'.cgl-engine-check'
 if old.exists():
  assert not old.is_symlink() and old.parent.resolve()==base.resolve()
  cleanup_mounts(old)
  command(['sudo','-n','rm','-rf',str(old)],20)
 server=next((p for p in ['/usr/sbin/dockerd','/usr/bin/dockerd'] if Path(p).is_file()),None);client='/usr/bin/docker'
 assert server and Path(client).is_file(),'Previously installed vendor programs unavailable'
 report['server_version']=command([server,'--version'],10).strip()
 report['client_version']=command([client,'--version'],10).strip()
 (work/'client').mkdir();socket=work/'d.sock';pidfile=work/'d.pid'
 daemon_log=(work/'daemon.log').open('w')
 process=subprocess.Popen(['sudo','-n',server,'--group=root','--data-root='+str(work/'data'),'--exec-root='+str(work/'run'),'--pidfile='+str(pidfile),'--host=unix://'+str(socket),'--iptables=false','--bridge=none','--storage-driver=vfs'],stdout=daemon_log,stderr=subprocess.STDOUT)
 cli=['sudo','-n',client,'--config='+str(work/'client'),'-H','unix://'+str(socket)]
 for i in range(40):
  p=subprocess.run(cli+['info'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=5)
  if p.returncode==0:break
  if process.poll() is not None:raise RuntimeError('Private daemon exited during startup')
  time.sleep(1)
 else:raise RuntimeError('Private daemon startup timed out')
 command(cli+['pull','alpine:3.20'],120)
 text=command(cli+['run','--rm','--network','none','alpine:3.20','echo','cgl-cloud-native-engine-ok'],60)
 assert 'cgl-cloud-native-engine-ok' in text
 report['image_id']=command(cli+['image','inspect','alpine:3.20','--format','{{.Id}}'],10).strip()
 report['engine_test_passed']=True
except Exception as e:report['error']=str(e)
finally:
 daemon=work/'daemon.log'
 if daemon.exists():report['daemon_tail']=daemon.read_text(errors='replace')[-5000:]
 report['operations_tail']='\n'.join(logs)[-5000:]
 try:
  pidfile=work/'d.pid'
  if pidfile.exists():
   pid=pidfile.read_text().strip()
   if pid.isdigit() and Path('/proc/'+pid+'/cmdline').exists():
    assert ('--data-root='+str(work/'data')).encode() in Path('/proc/'+pid+'/cmdline').read_bytes()
    subprocess.run(['sudo','-n','kill','-TERM',pid],check=True,timeout=10)
  if process:process.wait(timeout=30)
  cleanup_mounts(work)
  subprocess.run(['sudo','-n','rm','-rf',str(work)],check=True,timeout=30)
 except Exception as e:report['cleanup_errors'].append(str(e))
 report['temporary_engine_data_removed']=not work.exists()
def redact(value):
 if isinstance(value,str):return re.sub(r'https?://\S+','[URL]',value)
 if isinstance(value,dict):return {k:redact(v) for k,v in value.items()}
 if isinstance(value,list):return [redact(v) for v in value]
 return value
report=redact(report)
f=out/'private_engine_check.json';f.write_text(json.dumps(report,indent=2))
manifest={'input_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'files':{'output/private_engine_check.json':hashlib.sha256(f.read_bytes()).hexdigest()}}
with zipfile.ZipFile(delivery/'deliverables.zip','w') as z:z.write(f,'output/private_engine_check.json');z.writestr('manifest.json',json.dumps(manifest))
print(json.dumps(report));print('SBP_NATIVE_ZIP_SHA256:'+hashlib.sha256((delivery/'deliverables.zip').read_bytes()).hexdigest());print('[OUTPUT] outputs/deliverables.zip')
'''
compile(SCRIPT,'<cloud-private-engine>','exec')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True);p.add_argument('--keys-file',required=True);p.add_argument('--allow-paid',action='store_true');p.add_argument('--volume-data',action='store_true');p.add_argument('--proxy-env',action='store_true');p.add_argument('--mirrors',action='store_true');args=p.parse_args()
    if args.proxy_env or args.mirrors:args.volume_data=True
    if args.volume_data:
        SCRIPT=SCRIPT.replace("work=Path(tempfile.mkdtemp(prefix='cgl-docker-',dir='/tmp'));process=None", "legacy=base/'.cgl-private-docker'\nif legacy.exists():\n assert not legacy.is_symlink() and legacy.parent.resolve()==base.resolve()\n subprocess.run(['sudo','-n','umount',str(legacy/'data')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=15)\n subprocess.run(['sudo','-n','rm','-rf',str(legacy)],check=True,timeout=20)\nwork=base/'.cgl-private-docker';work.mkdir(exist_ok=False);runtime=Path(tempfile.mkdtemp(prefix='cgl-docker-',dir='/tmp'));process=None")
        SCRIPT=SCRIPT.replace("assert work.parent==Path('/tmp') and work.name.startswith('cgl-docker-')", "assert work.parent==base and work.name=='.cgl-private-docker'")
        SCRIPT=SCRIPT.replace("work/'run", "runtime/'run").replace("work/'d.sock'", "runtime/'d.sock'").replace("work/'d.pid'", "runtime/'d.pid'")
        SCRIPT=SCRIPT.replace(" assert shutil.disk_usage(work).free>50_000_000_000", " report['workspace_free_bytes']=shutil.disk_usage(work).free;report['socket_disk_free_bytes']=shutil.disk_usage(runtime).free\n assert shutil.disk_usage(work).free>50_000_000_000,'Insufficient workspace volume space'")
        SCRIPT=SCRIPT.replace("  cleanup_mounts(work)\n  subprocess.run(['sudo','-n','rm','-rf',str(work)]", "  cleanup_mounts(work);cleanup_mounts(runtime)\n  subprocess.run(['sudo','-n','rm','-rf',str(work),str(runtime)]")
        SCRIPT=SCRIPT.replace("  cleanup_mounts(work);cleanup_mounts(runtime)", "  subprocess.run(['sudo','-n','umount',str(work/'data')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=15)\n  cleanup_mounts(work);cleanup_mounts(runtime)")
        compile(SCRIPT,'<cloud-volume-data-short-sockets>','exec')
    if args.proxy_env:
        SCRIPT=SCRIPT.replace(" process=subprocess.Popen(['sudo','-n',server", " daemon_env=dict(os.environ);report['proxy_variables_present']={k:bool(daemon_env.get(k)) for k in ['HTTP_PROXY','HTTPS_PROXY','NO_PROXY','http_proxy','https_proxy','no_proxy','ALL_PROXY','all_proxy']}\n process=subprocess.Popen(['sudo','-n','--preserve-env=HTTP_PROXY,HTTPS_PROXY,NO_PROXY,http_proxy,https_proxy,no_proxy,ALL_PROXY,all_proxy',server")
        SCRIPT=SCRIPT.replace('stdout=daemon_log,stderr=subprocess.STDOUT)', 'stdout=daemon_log,stderr=subprocess.STDOUT,env=daemon_env)')
        compile(SCRIPT,'<cloud-private-engine-proxy-environment>','exec')
    if args.mirrors:
        pin=json.loads((__import__('pathlib').Path(args.out)/'ALPINE_PIN.json').read_text())['manifest_digest']
        assert __import__('re').fullmatch(r'sha256:[0-9a-f]{64}',pin)
        start=SCRIPT.index("legacy=base/'.cgl-private-docker'");end=SCRIPT.index('process=None',start)+len('process=None')
        SCRIPT=SCRIPT[:start]+"work=Path(tempfile.mkdtemp(prefix='cgl-data-',dir=str(base)));runtime=Path(tempfile.mkdtemp(prefix='cgl-docker-',dir='/tmp'));process=None"+SCRIPT[end:]
        SCRIPT=SCRIPT.replace("work.name=='.cgl-private-docker'", "work.name.startswith('cgl-data-')")
        SCRIPT=SCRIPT.replace("server,'--group=root'", "server,'--registry-mirror=https://mirror.gcr.io','--registry-mirror=https://docker.m.daocloud.io','--group=root'")
        SCRIPT=SCRIPT.replace("'alpine:3.20'",repr('alpine@'+pin))
        SCRIPT=SCRIPT.replace('logs=[]',"report['registry_mirrors']=['https://mirror.gcr.io','https://docker.m.daocloud.io'];report['primary_manifest_digest']="+repr(pin)+"\nlogs=[]")
        compile(SCRIPT,'<cloud-private-engine-pinned-public-mirrors>','exec')
    study=Probe(args);folder=study.out/('cloud-private-engine-pinned-mirrors' if args.mirrors else 'cloud-private-engine-proxy-env' if args.proxy_env else 'cloud-private-engine-volume-data' if args.volume_data else 'cloud-private-engine-short-path');folder.mkdir(exist_ok=False)
    previous=json.loads((study.out/'cloud-native-engine-secure-path/request.json').read_text());session=previous['session_id'];user='cgl-cloud-engine-secure-path'
    script=folder/'cloud_private_engine.py';script.write_text(SCRIPT);upload=study.transport.upload(script,user)
    body={'agent':{'id':study.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],
        'input':'Run the attached cloud_private_engine.py unchanged using foreground bash with background=false and timeout400 in this same cloud session. It does not install packages or disable the package guard. It cleans only the prior check own mount, uses a short private temporary path for Unix sockets, runs the already installed vendor Docker binaries, and preserves diagnostics even if cleanup fails. Do not modify it, inspect credentials, use skills or Memory, purchase anything or ask questions. Return [OUTPUT] outputs/deliverables.zip. This is not a benchmark result.',
        'stream':True,'session_id':session,'attachment_file_ids':[upload['file_id']]}
    row=study.execute(folder,'cloud-private-engine-short-path','environment-check',None,True,body,session,user,script)
    if not row['output_received']:raise RuntimeError('Inspect existing events for delivery')
    print((folder/'output/private_engine_check.json').read_text())
