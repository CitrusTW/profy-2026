"""Profy Linux only: prepare an original task environment, with no local Docker work."""
import gzip,hashlib,json,os,re,shutil,subprocess,sys,tarfile,tempfile,time,uuid,zipfile
from pathlib import Path

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def cloud_only():
    if sys.platform!='linux' or not str(Path.cwd()).startswith('/home/user/workspace/'):
        raise RuntimeError('Cloud-only script. Do not run this on the local computer.')

def main():
    cloud_only();base=Path.cwd()
    if (base/'case_context.json').exists():raise RuntimeError('Case already prepared; no duplicate setup')
    meta=json.loads(gzip.decompress((base/'case_config.json.gz').read_bytes()))
    assert digest(base/'task_environment.tar.gz')==meta['input_sha256']
    work=Path(tempfile.mkdtemp(prefix='cgl-task-',dir=str(base)))
    runtime=Path(tempfile.mkdtemp(prefix='cgl-sock-',dir='/tmp'))
    assert shutil.disk_usage(work).free>30_000_000_000,'Insufficient cloud workspace space'
    log=work/'setup.log'
    def command(args,timeout=180,cwd=None,env=None):
        with log.open('a') as stream:p=subprocess.run(args,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=timeout)
        if p.returncode:raise RuntimeError('Setup command failed '+str(p.returncode)+': '+str(args[:2]))
    try:
        vendor=work/'vendor';packages=work/'packages';packages.mkdir()
        # Download and unpack vendor packages without running system installation scripts.
        command(['sudo','-n','apt-get','-o','Acquire::Retries=0','update'],120)
        versions=['docker.io=26.1.5+dfsg1-9+deb13u1','docker-cli=26.1.5+dfsg1-9+deb13u1','containerd=1.7.24~ds1-6+deb13u1','runc=1.1.15+ds1-2+b4','tini=0.19.0-3+b8']
        command(['apt-get','download',*versions],180,cwd=packages)
        package_hashes={p.name:digest(p) for p in packages.glob('*.deb')}
        assert len(package_hashes)==5,'Missing vendor package'
        for p in packages.glob('*.deb'):command(['dpkg-deb','-x',str(p),str(vendor)],60)
        server=vendor/'usr/sbin/dockerd';client=vendor/'usr/bin/docker'
        if not server.is_file():server=vendor/'usr/bin/dockerd'
        assert server.is_file() and client.is_file()
        path=':'.join(str(vendor/p) for p in ['usr/bin','usr/sbin','usr/libexec/docker'])+':/usr/sbin:/usr/bin:/sbin:/bin'
        (work/'client').mkdir();socket=runtime/'d.sock';pidfile=runtime/'d.pid'
        daemon_log=(work/'daemon.log').open('w')
        daemon_args=['sudo','-n','env','PATH='+path,str(server),'--group=root','--data-root='+str(work/'data'),'--exec-root='+str(runtime/'run'),'--pidfile='+str(pidfile),'--host=unix://'+str(socket),'--iptables=false','--bridge=none','--storage-driver=vfs','--registry-mirror=https://mirror.gcr.io','--registry-mirror=https://docker.m.daocloud.io']
        subprocess.Popen(daemon_args,stdout=daemon_log,stderr=subprocess.STDOUT,start_new_session=True)
        cli=['sudo','-n',str(client),'--config='+str(work/'client'),'-H','unix://'+str(socket)]
        for _ in range(40):
            if subprocess.run(cli+['info'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=5).returncode==0:break
            time.sleep(1)
        else:raise RuntimeError('Private Docker engine unavailable')
        context=None
        if meta.get('prebuilt'):
            image=meta['prebuilt']['primary_image']
            assert re.fullmatch(r'ghcr\.io/benchflow-ai/skillsbench-task-env@sha256:[0-9a-f]{64}',image)
            command(cli+['pull',image],600)
        else:
            with tarfile.open(base/'task_environment.tar.gz','r:gz') as archive:archive.extractall(work/'context',filter='data')
            context=work/'context'
            for ref,pin in meta['base_images'].items():
                command(cli+['pull',ref.split(':')[0]+'@'+pin],180)
                command(cli+['tag',ref.split(':')[0]+'@'+pin,ref],30)
            image='cgl-task:'+uuid.uuid4().hex[:12]
            env=dict(os.environ);env['DOCKER_BUILDKIT']='0'
            build_cli=['sudo','-n','env','DOCKER_BUILDKIT=0',str(client),'--config='+str(work/'client'),'-H','unix://'+str(socket)]
            command(build_cli+['build','--network','host','--pull=false','-t',image,str(context)],600,env=env)
        image_id=subprocess.check_output(cli+['image','inspect',image,'--format','{{.Id}}'],text=True).strip()
        (work/'verifier').mkdir();(work/'verifier-logs').mkdir()
        container='cgl-run-'+uuid.uuid4().hex[:12]
        mounts=['--mount','type=bind,src='+str(work/'verifier')+',dst=/verifier,readonly','--mount','type=bind,src='+str(work/'verifier-logs')+',dst=/logs/verifier']
        target_sha=None
        if meta['skills']:
            with zipfile.ZipFile(base/'benchmark_skills.zip') as archive:
                for info in archive.infolist():
                    assert not Path(info.filename).is_absolute() and '..' not in Path(info.filename).parts
                archive.extractall(base)
            for rel,expected in meta['skill_hashes'].items():assert digest(base/rel)==expected
            target_sha=digest(base/'bench_skills'/meta['target_skill']/'SKILL.md')
            for alias in ['/root/bench_skills','/root/.claude/skills','/root/.agents/skills','/root/.codex/skills','/mnt/skills/public']:
                mounts+=['--mount','type=bind,src='+str(base/'bench_skills')+',dst='+alias+',readonly']
        command(cli+['run','-dit','--network','host','--name',container,*mounts,image],60)
        assert subprocess.check_output(cli+['inspect',container,'--format','{{.State.Running}}'],text=True).strip()=='true'
        shell='/bin/bash' if subprocess.run(cli+['exec',container,'/bin/sh','-c','test -x /bin/bash']).returncode==0 else '/bin/sh'
        state={'workspace':str(base),'work':str(work),'runtime':str(runtime),'cli':cli,'container':container,'image_id':image_id,'shell':shell,'input_sha256':meta['input_sha256'],'skill_sha256':target_sha,'package_sha256':package_hashes,'benchmark_pin':meta['benchmark_pin'],'task':meta['task']}
        (base/'case_context.json').write_text(json.dumps(state,indent=2))
        if context is not None:shutil.rmtree(context)
        shutil.rmtree(packages)
        (base/'task_environment.tar.gz').unlink()
        print('CGL_CASE_READY:'+json.dumps(state))
        if target_sha:print('SBP_ACTIVE_SKILL_SHA256:'+target_sha)
    except Exception as exc:
        error={'type':type(exc).__name__,'error':str(exc),'log_tail':log.read_text(errors='replace')[-5000:] if log.exists() else ''}
        try:
            pid=runtime/'d.pid'
            if pid.is_file():
                value=pid.read_text().strip();assert value.isdigit()
                cmdline=Path('/proc/'+value+'/cmdline')
                if cmdline.exists() and ('--data-root='+str(work/'data')).encode() in cmdline.read_bytes():
                    subprocess.run(['sudo','-n','kill','-TERM',value],timeout=10)
                    time.sleep(3)
            result=subprocess.run(['sudo','-n','rm','-rf',str(work),str(runtime)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=90)
            error['cleanup_returncode']=result.returncode
        except Exception as cleanup:error['cleanup_error']=str(cleanup)
        (base/'setup_error.json').write_text(json.dumps(error,indent=2))
        print('CGL_SETUP_ERROR:'+json.dumps(error),flush=True)
        raise

if __name__=='__main__':main()
