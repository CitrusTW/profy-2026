"""Check only native XLSX dependencies and free space. Installs nothing."""
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'skillsbench_evolution_20261110'))
from profy_cloud_probe import Probe
SCRIPT=r'''import json,subprocess,shutil,hashlib,zipfile,importlib.metadata
from pathlib import Path
base=Path.cwd();out=base/'output';out.mkdir(exist_ok=True)
report={'dependency_check_only':True,'packages_installed':False,'benchmark_solver_run':False,'root_free_bytes':shutil.disk_usage('/').free}
p=subprocess.run(['sudo','-n','apt-get','--assume-no','--no-install-recommends','install','gnumeric','libreoffice-calc'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=90)
report['package_estimate_returncode']=p.returncode;report['package_estimate_output']=p.stdout[-7000:]
report['commands']={x:shutil.which(x) for x in ['ssconvert','libreoffice','python3','uv','proot']}
report['python_versions']={}
for name in ['openpyxl','pytest']:
 try:report['python_versions'][name]=importlib.metadata.version(name)
 except importlib.metadata.PackageNotFoundError:report['python_versions'][name]=None
report['own_prior_workspace_visible']={x:(base.parent/x).is_dir() for x in ['76e679d0-0644-4b5a-a9a6-fe81a70d05b0','e0c573e5-a4f4-4958-a58a-3fa243299329']}
f=out/'native_xlsx_dependencies.json';f.write_text(json.dumps(report,indent=2));manifest={'input_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'files':{'output/native_xlsx_dependencies.json':hashlib.sha256(f.read_bytes()).hexdigest()}}
delivery=base/'outputs';delivery.mkdir(exist_ok=True)
with zipfile.ZipFile(delivery/'deliverables.zip','w') as z:z.write(f,'output/native_xlsx_dependencies.json');z.writestr('manifest.json',json.dumps(manifest))
print(json.dumps(report));print('SBP_NATIVE_ZIP_SHA256:'+hashlib.sha256((delivery/'deliverables.zip').read_bytes()).hexdigest());print('[OUTPUT] '+str(delivery/'deliverables.zip'))
'''
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for n in ['workspace','out','case','keys-file']:p.add_argument('--'+n,required=True)
 p.add_argument('--allow-paid',action='store_true');p.add_argument('--paths-only',action='store_true');p.add_argument('--memory-only',action='store_true');p.add_argument('--full-office',action='store_true');a=p.parse_args()
 if a.paths_only:
  start=SCRIPT.index("p=subprocess.run(['sudo','-n','apt-get'");end=SCRIPT.index("report['commands']",start)
  probe=r'''roots=list(base.glob('cgl-task-*/root'));assert len(roots)==1
root=roots[0]
py="import os,json,hashlib;print(json.dumps({'cwd':os.getcwd(),'uid':os.getuid(),'readable':os.access('/root/gdp.xlsx',os.R_OK),'sha256':hashlib.sha256(open('/root/gdp.xlsx','rb').read()).hexdigest()}))"
commands={'proot':['proot','-0','-b',str(root)+':/root','-w','/root','/usr/local/bin/python3','-c',py],'kernel_namespace':['sudo','-n','unshare','--mount','--propagation','private','/bin/sh','-c','mount --bind "$1" /root && cd /root && /usr/local/bin/python3 -c "$2"','sh',str(root),py]}
report['path_checks']={}
for name,cmd in commands.items():
 p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=20)
 report['path_checks'][name]={'returncode':p.returncode,'stdout':p.stdout[-2000:],'stderr':p.stderr[-2000:]}
'''
  SCRIPT=SCRIPT[:start]+probe+SCRIPT[end:]
 if a.memory_only:
  start=SCRIPT.index("p=subprocess.run(['sudo','-n','apt-get'");end=SCRIPT.index("report['commands']",start)
  probe=r'''report['memory_kib']={k:int(v.split()[0]) for k,v in (line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines()) if k in ['MemTotal','MemAvailable','SwapTotal','SwapFree']}
report['cgroup_membership']=Path('/proc/self/cgroup').read_text()
report['cgroup_memory_limits']={str(p):p.read_text().strip() for p in [Path('/sys/fs/cgroup/memory.max'),Path('/sys/fs/cgroup/memory.high'),Path('/sys/fs/cgroup/memory/memory.limit_in_bytes'),Path('/sys/fs/cgroup/memory/memory.usage_in_bytes')] if p.is_file()}
report['cgroup_mounts']=[line for line in Path('/proc/self/mountinfo').read_text().splitlines() if 'cgroup' in line]
'''
  SCRIPT=SCRIPT[:start]+probe+SCRIPT[end:]
 if a.full_office:SCRIPT=SCRIPT.replace("'libreoffice-calc'","'libreoffice'")
 previous=json.loads((Path(a.case)/'session.json').read_text());study=Probe(a);folder=study.out/('full-office-dependency-check' if a.full_office else 'native-memory-profile' if a.memory_only else 'native-path-check' if a.paths_only else 'native-xlsx-dependency-check');folder.mkdir(exist_ok=False)
 script=folder/'check_native_xlsx.py';script.write_text(SCRIPT);upload=study.transport.upload(script,previous['end_user'])
 body={'agent':{'id':study.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],'input':'Dependency check only. Run exactly python3 check_native_xlsx.py unchanged once using foreground bash with timeout120. It installs nothing and only estimates package size, checks software versions and directory existence. Do not solve, grade, inspect other sessions content, change files, use skills/Memory, purchase anything or ask questions. Return [OUTPUT] outputs/deliverables.zip.','stream':True,'session_id':previous['id'],'attachment_file_ids':[upload['file_id']]}
 row=study.execute(folder,'native-xlsx-dependency-check','environment-check',None,True,body,previous['id'],previous['end_user'],script)
 if not row['output_received']:raise RuntimeError('Inspect native events for delivery')
 print((folder/'output/native_xlsx_dependencies.json').read_text())
