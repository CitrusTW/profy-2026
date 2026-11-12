"""Relay only the small official PRoot binary in RAM; execute exclusively in Profy."""
import argparse,gzip,hashlib,io,tarfile,json
from cloud_runtime_bridge import MemoryUpload,get,alpine_layer
from profy_cloud_probe import Probe
from run import save

SCRIPT=r'''import hashlib,json,os,shutil,subprocess,zipfile
from pathlib import Path
base=Path.cwd();work=base/'.cgl-proot-check';work.mkdir(exist_ok=False)
out=base/'output';out.mkdir(exist_ok=True);delivery=base/'outputs';delivery.mkdir(exist_ok=True)
report={'cloud_only':True,'new_service_purchased':False,'runtime_passed':False}
try:
 binary=base/'proot-x86_64';archive=base/'alpine_rootfs.tar.gz'
 assert hashlib.sha256(binary.read_bytes()).hexdigest()==PROOT_SHA
 assert hashlib.sha256(archive.read_bytes()).hexdigest()==ROOTFS_SHA
 binary.chmod(0o700);root=work/'rootfs';root.mkdir()
 subprocess.run(['tar','--no-same-owner','-xzf',str(archive),'-C',str(root)],check=True,timeout=30)
 env=dict(os.environ);env['PROOT_TMP_DIR']=str(work);env['PROOT_NO_SECCOMP']='1'
 command=[str(binary),'-0','-r',str(root),'-b','/dev','-b','/proc','-w','/','/bin/sh','-c','printf cgl-proot-runtime-ok; uname -m']
 p=subprocess.run(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=75)
 report.update(returncode=p.returncode,actual_output=p.stdout[-4000:],runtime_passed=p.returncode==0 and 'cgl-proot-runtime-ok' in p.stdout)
except Exception as e:report['error']=str(e)
finally:
 shutil.rmtree(work);report['temporary_runtime_removed']=not work.exists()
f=out/'runtime_check.json';f.write_text(json.dumps(report,indent=2))
manifest={'input_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'files':{'output/runtime_check.json':hashlib.sha256(f.read_bytes()).hexdigest()}}
with zipfile.ZipFile(delivery/'deliverables.zip','w') as z:z.write(f,'output/runtime_check.json');z.writestr('manifest.json',json.dumps(manifest))
print(json.dumps(report));print('SBP_NATIVE_ZIP_SHA256:'+hashlib.sha256((delivery/'deliverables.zip').read_bytes()).hexdigest());print('[OUTPUT] outputs/deliverables.zip')
'''

def small_binary():
    raw=get('https://download.a.incd.pt/udocker/udocker-englib-1.2.11.tar.gz',50000000)
    archive_sha=hashlib.sha256(raw).hexdigest()
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as t:
        member=t.getmember('udocker_dir/bin/proot-x86_64')
        assert member.isfile() and member.size<5000000
        binary=t.extractfile(member).read()
    return binary,archive_sha

def upload_chunks(study,name,raw,user,folder,uploads,parts):
    chunks=[]
    for offset in range(0,len(raw),500000):
        piece=raw[offset:offset+500000];part=name+'.part%03d'%(offset//500000)
        chunks.append({'name':part,'sha256':hashlib.sha256(piece).hexdigest()})
        uploads.append(study.transport.upload(MemoryUpload(part,piece),user))
        save(folder/'uploads.json',uploads)
        print('PUBLIC_CHUNK_UPLOADED',part,len(piece),flush=True)
    parts[name]=chunks

def reconstruction(parts):
    return '''from pathlib import Path
import gzip,hashlib
PARTS='''+repr(parts)+'''
for name,chunks in PARTS.items():
    payload=[]
    for part in chunks:
        raw=Path(part['name']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==part['sha256']
        payload.append(raw)
    raw=b''.join(payload)
    if name=='proot-x86_64.gz':Path('proot-x86_64').write_bytes(gzip.decompress(raw))
    else:Path(name).write_bytes(raw)
'''

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True)
    p.add_argument('--keys-file',required=True);p.add_argument('--allow-paid',action='store_true');p.add_argument('--chunked',action='store_true');args=p.parse_args()
    study=Probe(args);folder=study.out/('cloud-proot-chunked-memory-check' if args.chunked else 'cloud-proot-small-memory-check');folder.mkdir(exist_ok=False);user='cgl-small-cloud-proot'
    binary,archive_sha=small_binary();binary_sha=hashlib.sha256(binary).hexdigest()
    uploads=[];parts={}
    print('PUBLIC_RUNTIME_MEMBER_READY',len(binary),flush=True)
    if args.chunked:upload_chunks(study,'proot-x86_64.gz',gzip.compress(binary),user,folder,uploads,parts)
    else:uploads.append(study.transport.upload(MemoryUpload('proot-x86_64',binary),user))
    del binary
    layer,source=alpine_layer();rootfs_sha=hashlib.sha256(layer).hexdigest()
    if args.chunked:upload_chunks(study,'alpine_rootfs.tar.gz',layer,user,folder,uploads,parts)
    else:uploads.append(study.transport.upload(MemoryUpload('alpine_rootfs.tar.gz',layer),user))
    del layer
    save(folder/'PUBLIC_RUNTIME_SOURCES.json',{'official_engine_url':'https://download.a.incd.pt/udocker/udocker-englib-1.2.11.tar.gz','engine_archive_sha256':archive_sha,'member':'udocker_dir/bin/proot-x86_64','member_sha256':binary_sha,'alpine':source,'local_binary_or_image_written':False})
    script=folder/'cloud_runtime_check.py';script.write_text((reconstruction(parts) if parts else '')+'PROOT_SHA='+repr(binary_sha)+'\nROOTFS_SHA='+repr(rootfs_sha)+'\n'+SCRIPT)
    uploads.append(study.transport.upload(script,user));save(folder/'uploads.json',uploads)
    session=study.transport.api('/v1/sessions',{'agent':study.transport.expert_id,'title':'Serial small cloud PRoot check'},user)['id']
    body={'agent':{'id':study.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],
        'input':'Run the attached cloud_runtime_check.py unchanged using one foreground bash call with background=false and timeout200. The script verifies the attached public runtime files, tests one temporary Alpine environment entirely in this cloud session, then removes its own temporary directory. Do not modify it, use skills or Memory, inspect credentials, purchase anything or ask questions. Return [OUTPUT] outputs/deliverables.zip. This is an environment check, not a benchmark result.',
        'stream':True,'session_id':session,'attachment_file_ids':[u['file_id'] for u in uploads]}
    row=study.execute(folder,'cloud-proot-small-memory-check','environment-check',None,True,body,session,user,script)
    if not row['output_received']:raise RuntimeError('Inspect existing events; no blind rerun')
    print((folder/'output/runtime_check.json').read_text())
