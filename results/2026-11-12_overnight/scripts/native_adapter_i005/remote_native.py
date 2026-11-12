"""Owned native filesystem runner. Kernel namespaces are reserved for grading only."""
import hashlib,json,os,re,shutil,subprocess,tempfile,zipfile
from pathlib import Path
from native_support import BLOCKED,copy_targets,extract_inputs,select_rows,task_spec

EXCLUDED={'.cache','.git','.npm','.local','.venv','node_modules','__pycache__','.pytest_cache','bench_skills','.claude','.agents','.codex','.bash_history','.config','.fonts','.gnupg'}

def file_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def root_file(state,path):
    p=Path(path)
    assert p.is_absolute() and '..' not in p.parts and len(p.parts)>2 and p.parts[1] in ['root','app'],'Only logical task paths are supported'
    root=Path(state['work'])/p.parts[1];result=root.joinpath(*p.parts[2:])
    assert result.resolve().is_relative_to(root.resolve()),'Only task files may be exported'
    assert not any(x in EXCLUDED for x in p.parts[2:]),'Adapter/cache/skill paths cannot be exported'
    return result

def task_directory(work,path):
    p=Path(path)
    assert p.is_absolute() and '..' not in p.parts and len(p.parts)>=2 and p.parts[1] in ['root','app']
    result=work/p.parts[1]
    if len(p.parts)>2:result=result.joinpath(*p.parts[2:])
    assert result.resolve().is_relative_to((work/p.parts[1]).resolve())
    return result

def changed_files(state):
    paths=[]
    for name in ['root','app']:
        root=Path(state['work'])/name
        for item in root.rglob('*'):
            rel=item.relative_to(root)
            if any(x in EXCLUDED for x in rel.parts) or item.is_symlink() or not item.is_file():continue
            logical='/'+name+'/'+rel.as_posix()
            if root_file(state,logical)!=item:raise RuntimeError('Export mapping mismatch')
            if file_sha(item)!=state['original_file_sha256'].get(logical):paths.append(logical)
    return sorted(paths)

def prepare(base,meta,buffer):
    assert os.getuid()==1000,'Native solver preparation must run as existing uid1000'
    spec=task_spec(meta['task'])
    work=Path(tempfile.mkdtemp(prefix='cgl-task-',dir=str(base)))
    runtime=Path(tempfile.mkdtemp(prefix='cgl-sock-',dir='/tmp'))
    log=work/'native_setup.log';cache=work/'apt-downloads';cache.mkdir();(cache/'partial').mkdir()
    def command(args,timeout=300,env=None):
        p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout,env=env)
        with log.open('a') as stream:stream.write(p.stdout)
        if p.returncode:raise RuntimeError('Native preparation failed: '+p.stdout[-3000:])
        return p.stdout
    try:
        source=work/'source';source.mkdir();extract_inputs(buffer,source,meta['input_manifest'])
        rows=[(n,(source/n).read_bytes(),v['mode']) for n,v in meta['input_manifest'].items()]
        assert {n for n,b,m in select_rows(rows,spec)}==set(meta['input_manifest'])
        for name in ['root','app','verifier','verifier-logs','empty-skills','tmp']:(work/name).mkdir()
        (work/'verifier').chmod(0o000);(work/'verifier-logs').chmod(0o000)
        for directory in spec.get('directories',[]):task_directory(work,directory).mkdir(parents=True,exist_ok=True)
        cwd=task_directory(work,spec['workdir']);cwd.mkdir(parents=True,exist_ok=True)
        inputs={}
        for name,logical in copy_targets(spec,meta['input_manifest']).items():
            target=task_directory(work,logical);target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source/name,target);target.chmod(meta['input_manifest'][name]['mode'])
            inputs[logical]=file_sha(target)
        # Only the two reviewed original public URLs are executed, with wget's
        # original -O behavior; never run arbitrary Dockerfile shell bodies.
        for url,logical in spec.get('downloads',[]):
            target=task_directory(work,logical);target.parent.mkdir(parents=True,exist_ok=True)
            command(['wget','-O',str(target),url],180)
            if not target.stat().st_size:raise RuntimeError('Empty public download')
            inputs[logical]=file_sha(target)
        expected=meta.get('expected_input_hashes')
        if expected is not None and inputs!=expected:raise RuntimeError('Inputs do not match condition A')
        versions=meta.get('native_package_versions') or {}
        if set(versions)-set(spec['apt']):raise ValueError('Package pins include undeclared apt packages')
        names=[n+'='+versions[n] if n in versions else n for n in spec['apt']]
        aptenv=dict(os.environ,LC_ALL='C',LANG='C')
        command(['sudo','-n','apt-get','-o','Acquire::Retries=0','update'],180,aptenv)
        apt=['sudo','-n','env','LC_ALL=C','DEBIAN_FRONTEND=noninteractive','apt-get','-o','Dir::Cache::Archives='+str(cache),'--no-install-recommends']
        simulation=command(apt+['--simulate','install',*names],180,aptenv)
        (work/'apt-simulation.txt').write_text(simulation)
        planned=[]
        for line in simulation.splitlines():
            match=re.match(r'^Inst (\S+)(?: \[[^]]+\])? \((\S+)',line)
            if match:planned.append(match.groups())
        installed_bytes=download_bytes=0
        for package,version in planned:
            info=command(['apt-cache','show','--no-all-versions',package+'='+version],60,aptenv)
            size=re.search(r'^Installed-Size: (\d+)$',info,re.M);download=re.search(r'^Size: (\d+)$',info,re.M)
            if not size or not download:raise RuntimeError('Cannot budget apt transaction')
            installed_bytes+=int(size[1])*1024;download_bytes+=int(download[1])
        # Conservative: count full installed sizes, including upgraded packages,
        # plus archives when workspace and system disk share a filesystem.
        same_disk=os.stat(cache).st_dev==os.stat('/usr').st_dev
        required=installed_bytes+120_000_000+(download_bytes if same_disk else 0)
        system_free=shutil.disk_usage('/usr').free;workspace_free=shutil.disk_usage(work).free
        if system_free<required or workspace_free<download_bytes+100_000_000:raise RuntimeError('Insufficient disk for simulated apt transaction')
        guard={'installed_bytes_upper_bound':installed_bytes,'archive_bytes':download_bytes,'system_free':system_free,'workspace_free':workspace_free,'same_filesystem':same_disk}
        try:command(apt+['-y','install',*names],900,aptenv)
        finally:subprocess.run(['sudo','-n','rm','-rf',str(cache)],check=True,timeout=60)
        uv=shutil.which('uv')
        if not uv:raise RuntimeError('Existing platform uv is required; no bootstrap installer is permitted')
        host_python=shutil.which('python3')
        venv=work/'venv'
        command([uv,'venv','--system-site-packages','--python',host_python,str(venv)],120)
        python=venv/'bin/python'
        omitted=[];requirements=[]
        for requirement in spec['pip']:
            name=requirement.split('==')[0].lower().replace('_','-')
            if name in BLOCKED:omitted.append(requirement)
            else:
                if '==' not in requirement:raise ValueError('Unpinned pip requirement')
                requirements.append(requirement)
        if requirements:command([uv,'pip','install','--no-cache','--python',str(python),*requirements],600)
        pip_receipt=json.loads(command([str(python),'-c','import importlib.metadata,json;print(json.dumps(sorted([(d.metadata["Name"],d.version) for d in importlib.metadata.distributions()])))'],60))
        # I-003: distributions() includes hidden system-site versions. Query the
        # active task interpreter's metadata resolution, retain the full inventory.
        requested_names=[x.split('==')[0] for x in requirements]
        active_code='import importlib.metadata as m,json,sys; names=json.loads(sys.argv[1]); print(json.dumps({n.lower().replace("_","-"):{"version":m.version(n),"location":str(m.distribution(n).locate_file(""))} for n in names}))'
        active_distributions=json.loads(command([str(python),'-c',active_code,json.dumps(requested_names)],60))
        resolved={n:v['version'] for n,v in active_distributions.items()}
        for requirement in requirements:
            n,v=requirement.split('==');assert resolved.get(n.lower().replace('_','-'))==v,'Declared pip pin not active'
        apt_receipt=command(['dpkg-query','-W','-f=${binary:Package}\t${Version}\n'],60)
        package_versions={n:command(['dpkg-query','-W','-f=${Version}',n],60).strip() for n in spec['apt']}
        assert all(package_versions[n]==v for n,v in versions.items()),'Native apt pin mismatch'
        target_sha=None
        if meta['skills']:
            with zipfile.ZipFile(base/'benchmark_skills.zip') as archive:
                infos=archive.infolist()
                assert len(infos)==len(meta['skill_hashes']) and {i.filename for i in infos}==set(meta['skill_hashes'])
                for info in infos:
                    p=Path(info.filename)
                    assert not p.is_absolute() and '..' not in p.parts and p.parts[0]=='bench_skills'
                    assert info.file_size<=50_000_000
                    raw=archive.read(info)
                    assert hashlib.sha256(raw).hexdigest()==meta['skill_hashes'][info.filename]
                    target=base/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
                    target.chmod(((info.external_attr>>16)&0o111)|0o444)
            target_sha=file_sha(base/'bench_skills'/meta['target_skill']/'SKILL.md')
            (work/'root/bench_skills').symlink_to(base/'bench_skills',target_is_directory=True)
        receipt={'apt_packages':package_versions,'all_installed_apt':apt_receipt,'python_distributions':pip_receipt,'active_python_distributions':active_distributions,'python':str(python),'host_python':host_python,'uv':command([uv,'--version'],30).strip(),'declared_pip':spec['pip'],'omitted_blocked_pip':omitted,'apt_space_guard':guard}
        (work/'dependency_receipt.json').write_text(json.dumps(receipt,indent=2))
        state={'backend':'native-owned','runtime_difference':'Native Profy host, not the official Ubuntu image. Solver uses uid1000 without path interception or mount namespaces. All apt installs use --no-install-recommends as a disclosed native adaptation. Host system-site-packages and pre-existing apt packages remain visible. Blocked declared packages are omitted and may not be used. Existing platform uv replaces Dockerfile uv installers. This runner is not a security sandbox.','workspace':str(base),'work':str(work),'runtime':str(runtime),'cli':[],'container':None,'image_id':None,'shell':'/bin/bash','input_sha256':meta['input_sha256'],'original_file_sha256':inputs,'skill_sha256':target_sha,'benchmark_pin':meta['benchmark_pin'],'task':meta['task'],'workdir':spec['workdir'],'cwd':str(cwd),'task_roots':{'/root':str(work/'root'),'/app':str(work/'app')},'task_python':str(python),'task_path':str(venv/'bin')+':'+os.environ.get('PATH','/usr/local/bin:/usr/bin:/bin'),'native_package_versions':package_versions,'dependency_receipt':receipt,'runtime_adaptations':spec.get('adaptations',[]),'supplied_skill_hashes':meta['skill_hashes']}
        assert all(file_sha(task_directory(work,p))==h for p,h in inputs.items())
        # Keep the setup receipt below the tool output limit; retain full dependencies as a file.
        state['dependency_receipt']={'file':'dependency_receipt.json','sha256':file_sha(work/'dependency_receipt.json')}
        (base/'case_context.json').write_text(json.dumps(state,indent=2))
        shutil.rmtree(source)
        for entry in meta['transport']:(base/entry['name']).unlink()
        if (base/'benchmark_skills.zip').exists():(base/'benchmark_skills.zip').unlink()
        print('CGL_CASE_READY:'+json.dumps(state),flush=True)
        if target_sha:print('SBP_ACTIVE_SKILL_SHA256:'+target_sha,flush=True)
    except Exception as exc:
        if cache.exists():subprocess.run(['sudo','-n','rm','-rf',str(cache)],timeout=60)
        report={'type':type(exc).__name__,'error':str(exc),'log_tail':log.read_text(errors='replace')[-4000:] if log.exists() else ''}
        (base/'setup_error.json').write_text(json.dumps(report,indent=2));print('CGL_SETUP_ERROR:'+json.dumps(report),flush=True)
        raise

def execute(base,state,mode,raw):
    if mode=='exec':
        if state['skill_sha256'] is None and any(x in raw for x in ['SKILL.md','/mnt/skills','skills_read']):raise RuntimeError('No-skills condition: extra skill access refused')
        assert os.getuid()==1000 and os.getgid()==1000,'Solver must be existing uid1000/gid1000'
        work=Path(state['work']);cwd=task_directory(work,state['workdir'])
        assert str(cwd)==state['cwd']
        env=dict(os.environ,HOME=str(work/'root'),PATH=state['task_path'],TMPDIR=str(work/'tmp'),VIRTUAL_ENV=str(work/'venv'))
        env.pop('PYTHONHOME',None);env.pop('PYTHONPATH',None)
        return subprocess.run([state['shell'],'--noprofile','--norc','-c',raw],cwd=cwd,env=env,timeout=480).returncode
    if mode=='get':
        source=root_file(state,json.loads(raw));target=base/'preview'/__import__('uuid').uuid4().hex;target.mkdir(parents=True)
        assert source.is_file() and not source.is_symlink();shutil.copyfile(source,target/source.name)
        print('PREVIEW_PATH:'+str((target/source.name).resolve()));return 0
    raise ValueError('Only exec/get supported')
