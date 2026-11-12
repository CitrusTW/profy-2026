"""Bounded RAM-only relay of public runtime files; no local images or caches."""
import argparse,hashlib,json,urllib.request
from dataclasses import dataclass
from cloud_user_engine_check import SCRIPT as ORIGINAL
from profy_cloud_probe import Probe
from run import save

@dataclass
class MemoryUpload:
    name:str
    data:bytes
    def read_bytes(self):return self.data

def get(url,limit,headers=None):
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers or {}),timeout=60) as response:
        if int(response.headers.get('Content-Length','0'))>limit:raise ValueError('Public download exceeds RAM bound')
        raw=response.read(limit+1)
        if len(raw)>limit:raise ValueError('Public download exceeds RAM bound')
        return raw

def alpine_layer():
    auth=json.loads(get('https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/alpine:pull',100000))['token']
    headers={'Authorization':'Bearer '+auth,'Accept':'application/vnd.oci.image.index.v1+json, application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.list.v2+json, application/vnd.docker.distribution.manifest.v2+json'}
    prefix='https://registry-1.docker.io/v2/library/alpine/'
    manifest=json.loads(get(prefix+'manifests/3.20',2000000,headers))
    if 'manifests' in manifest:
        matches=[m for m in manifest['manifests'] if m.get('platform',{}).get('architecture')=='amd64' and m.get('platform',{}).get('os')=='linux']
        assert len(matches)==1
        pinned=matches[0]['digest'];raw=get(prefix+'manifests/'+pinned,2000000,headers)
        assert 'sha256:'+hashlib.sha256(raw).hexdigest()==pinned
        manifest=json.loads(raw)
    layers=manifest['layers'];assert len(layers)==1,'This small check only accepts a single-layer Alpine rootfs'
    digest=layers[0]['digest'];raw=get(prefix+'blobs/'+digest,15000000,headers)
    assert 'sha256:'+hashlib.sha256(raw).hexdigest()==digest
    return raw,{'image':'alpine:3.20','platform':'linux/amd64','layer_digest':digest,'bytes':len(raw)}

def cloud_script(engine_sha,rootfs_sha):
    text=ORIGINAL.replace("env['PYTHONPATH']=str(work/'tools')", "env['PYTHONPATH']=str(work/'tools');env['UDOCKER_TARBALL']=str(base/'udocker-englib-1.2.11.tar.gz')")
    text=text.replace("'udocker'],120)","'udocker==1.3.17'],120)")
    checks=" assert hashlib.sha256((base/'udocker-englib-1.2.11.tar.gz').read_bytes()).hexdigest()=="+repr(engine_sha)+"\n assert hashlib.sha256((base/'alpine_rootfs.tar.gz').read_bytes()).hexdigest()=="+repr(rootfs_sha)+"\n"
    text=text.replace(" command(cli+['install'],180)",checks+" command(cli+['install'],180)")
    text=text.replace(" command(cli+['pull','alpine:3.20'],180)"," command(cli+['import',str(base/'alpine_rootfs.tar.gz'),'alpine:3.20'],120)")
    text=text.replace("finally:\n shutil.rmtree(work)","finally:\n log=work/'operations.log'\n if log.exists():report['operations_tail']=re.sub(r'https?://\\S+','[URL]',log.read_text(errors='replace')[-6000:])\n shutil.rmtree(work)")
    assert "cli+['pull'" not in text and 'UDOCKER_TARBALL' in text
    compile(text,'<cloud-runtime-bridge>','exec')
    return text

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True)
    p.add_argument('--keys-file',required=True);p.add_argument('--allow-paid',action='store_true');args=p.parse_args()
    study=Probe(args);folder=study.out/'cloud-runtime-memory-bridge';folder.mkdir(exist_ok=False)
    user='cgl-runtime-memory-bridge'
    engine=get('https://download.a.incd.pt/udocker/udocker-englib-1.2.11.tar.gz',50000000)
    engine_sha=hashlib.sha256(engine).hexdigest()
    uploads=[study.transport.upload(MemoryUpload('udocker-englib-1.2.11.tar.gz',engine),user)]
    del engine
    layer,source=alpine_layer();rootfs_sha=hashlib.sha256(layer).hexdigest()
    uploads.append(study.transport.upload(MemoryUpload('alpine_rootfs.tar.gz',layer),user));del layer
    save(folder/'PUBLIC_RUNTIME_SOURCES.json',{'engine_official_url':'https://download.a.incd.pt/udocker/udocker-englib-1.2.11.tar.gz','engine_sha256':engine_sha,'alpine':source,'local_runtime_files_written':False,'new_service_purchased':False})
    script=folder/'cloud_user_engine_check.py';script.write_text(cloud_script(engine_sha,rootfs_sha))
    uploads.append(study.transport.upload(script,user));save(folder/'uploads.json',uploads)
    session=study.transport.api('/v1/sessions',{'agent':study.transport.expert_id,'title':'Serial cloud runtime using bounded RAM relay'},user)['id']
    body={'agent':{'id':study.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],
        'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],
        'input':'Run the attached cloud_user_engine_check.py unchanged with python3 using one foreground bash call with background=false and timeout850. Two public runtime archives are attached; their SHA256 values are checked by the script. It tests a temporary user-space runtime entirely in this cloud session and removes its own temporary folder. Do not modify the script, invoke skills or Memory, inspect credentials, purchase services or ask questions. Return the actual [OUTPUT] outputs/deliverables.zip. If background starts, await it, then touch outputs/deliverables.zip in foreground for delivery without rerunning. This is an environment check, not a benchmark score.',
        'stream':True,'session_id':session,'attachment_file_ids':[u['file_id'] for u in uploads]}
    row=study.execute(folder,'cloud-runtime-memory-bridge','environment-check',None,True,body,session,user,script)
    if not row['output_received']:raise RuntimeError('Inspect existing events for delivery; do not rerun automatically')
    print((folder/'output/user_engine_check.json').read_text())
