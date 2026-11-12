"""Lightweight Profy Linux file-task adapter. Original questions and verifier stay unchanged."""
import gzip,hashlib,json,os,re,shutil,subprocess,tarfile,tempfile,zipfile
from pathlib import Path

def prepare(base,meta):
    assert meta['task']=='weighted-gdp-calc','Only the reviewed single-file prototype is enabled'
    work=Path(tempfile.mkdtemp(prefix='cgl-task-',dir=str(base)))
    runtime=Path(tempfile.mkdtemp(prefix='cgl-sock-',dir='/tmp'))
    log=work/'native_setup.log';cache=runtime/'apt';cache.mkdir();(cache/'partial').mkdir()
    def command(args,timeout=180):
        with log.open('a') as stream:
            p=subprocess.run(args,stdout=stream,stderr=subprocess.STDOUT,timeout=timeout)
        if p.returncode:raise RuntimeError('Native preparation failed: '+log.read_text(errors='replace')[-3000:])
    try:
        assert shutil.disk_usage('/').free>700_000_000,'Cloud system disk too small for the measured dependency set'
        command(['sudo','-n','apt-get','-o','Acquire::Retries=0','update'],120)
        versions=meta.get('native_package_versions') or {}
        names=[n+'='+versions[n] if n in versions else n for n in ['gnumeric','libreoffice-calc','proot']]
        command(['sudo','-n','env','DEBIAN_FRONTEND=noninteractive','apt-get','-o','Dir::Cache::Archives='+str(cache),'-y','--no-install-recommends','install',*names],300)
        subprocess.run(['sudo','-n','rm','-rf',str(cache)],check=True,timeout=30)
        with tarfile.open(base/'task_environment.tar.gz','r:gz') as archive:archive.extractall(work/'source',filter='data')
        root=work/'root';root.mkdir();shutil.copyfile(work/'source/gdp.xlsx',root/'gdp.xlsx')
        inputs={'/root/gdp.xlsx':hashlib.sha256((root/'gdp.xlsx').read_bytes()).hexdigest()}
        for name in ['verifier','verifier-logs','empty-skills']:(work/name).mkdir()
        target_sha=None
        if meta['skills']:
            with zipfile.ZipFile(base/'benchmark_skills.zip') as archive:
                assert all(not Path(i.filename).is_absolute() and '..' not in Path(i.filename).parts for i in archive.infolist())
                archive.extractall(base)
            for rel,h in meta['skill_hashes'].items():assert hashlib.sha256((base/rel).read_bytes()).hexdigest()==h
            target_sha=hashlib.sha256((base/'bench_skills'/meta['target_skill']/'SKILL.md').read_bytes()).hexdigest()
            (root/'bench_skills').symlink_to(base/'bench_skills',target_is_directory=True)
        prefix=['proot','-0','-b',str(root)+':/root','-b',str(work/'verifier')+':/verifier','-b',str(work/'verifier-logs')+':/logs/verifier','-w','/root']
        for alias in ['/mnt/skills/public','/mnt/skills/private']:
            if Path(alias).is_dir():prefix+=['-b',str(base/'bench_skills' if meta['skills'] else work/'empty-skills')+':'+alias]
        # This check uses no task answer or benchmark reference.
        p=subprocess.run(prefix+['/bin/sh','-c','test "$PWD" = /root && test -r /root/gdp.xlsx'],capture_output=True,text=True,timeout=20)
        assert p.returncode==0,p.stderr[-2000:]
        package_versions={n:subprocess.check_output(['dpkg-query','-W','-f=${Version}',n],text=True).strip() for n in ['gnumeric','libreoffice-calc','proot']}
        assert all(package_versions.get(n)==v for n,v in versions.items()),'Native runtime package version differs'
        state={'backend':'native-proot','runtime_difference':'Profy Debian with original task files and unmodified original verifier, not the official Ubuntu Docker image','workspace':str(base),'work':str(work),'runtime':str(runtime),'cli':[],'container':None,'image_id':None,'shell':'/bin/bash','input_sha256':meta['input_sha256'],'original_file_sha256':inputs,'skill_sha256':target_sha,'benchmark_pin':meta['benchmark_pin'],'task':meta['task'],'native_command':prefix,'native_package_versions':package_versions}
        (base/'case_context.json').write_text(json.dumps(state,indent=2))
        shutil.rmtree(work/'source');(base/'task_environment.tar.gz').unlink()
        print('CGL_CASE_READY:'+json.dumps(state),flush=True)
        if target_sha:print('SBP_ACTIVE_SKILL_SHA256:'+target_sha,flush=True)
    except Exception as exc:
        report={'type':type(exc).__name__,'error':str(exc),'log_tail':log.read_text(errors='replace')[-4000:] if log.exists() else ''}
        (base/'setup_error.json').write_text(json.dumps(report,indent=2));print('CGL_SETUP_ERROR:'+json.dumps(report),flush=True)
        raise

def root_file(state,path):
    p=Path(path);assert p.is_absolute() and '..' not in p.parts and len(p.parts)>2 and p.parts[1]=='root'
    root=Path(state['work'])/'root';result=root.joinpath(*p.parts[2:])
    assert result.resolve().is_relative_to(root.resolve()),'Only task files may be exported'
    return result

def execute(base,state,mode,raw):
    if mode=='exec':
        if state['skill_sha256'] is None and any(x in raw for x in ['SKILL.md','/mnt/skills','skills_read']):
            raise RuntimeError('No-skills condition: extra skill access refused')
        return subprocess.run(state['native_command']+[state['shell'],'-lc','cd /root\n'+raw],timeout=480).returncode
    if mode=='get':
        source=root_file(state,json.loads(raw));target=base/'preview'/__import__('uuid').uuid4().hex;target.mkdir(parents=True)
        assert source.is_file();shutil.copyfile(source,target/source.name)
        print('PREVIEW_PATH:'+str(target/source.name));return 0
    raise ValueError('Only exec/get supported')
