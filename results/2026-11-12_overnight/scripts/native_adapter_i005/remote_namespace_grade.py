"""Fixed root grading namespace only. Never used for solver execution."""
import json,os,subprocess
from pathlib import Path
from native_support import task_spec

def main():
    base=Path.cwd();state=json.loads((base/'case_context.json').read_text());work=Path(state['work']);runtime=Path(state['runtime'])
    assert base.as_posix().startswith('/home/user/workspace/') and (base/'case_frozen').is_file()
    assert work.parent==base and work.name.startswith('cgl-task-')
    assert runtime.parent==Path('/tmp') and runtime.name.startswith('cgl-sock-')
    assert os.getuid()==0,'Fixed grader requires the isolated namespace, not fake root'
    spec=task_spec(state['task']);assert spec['workdir']==state['workdir']
    subprocess.run(['mount','--make-rprivate','/'],check=True,timeout=10)
    target=runtime/'uv-package'
    subprocess.run(['/usr/local/bin/uv','pip','install','--no-cache','--python','/usr/local/bin/python3','--target',str(target),'uv==0.9.7'],check=True,timeout=150)
    bins=work/'root/.local/bin';bins.mkdir(parents=True,exist_ok=True)
    for name in ['uv','uvx']:
        matches=[p for p in target.rglob(name) if p.is_file() and p.read_bytes()[:4]==b'\x7fELF']
        assert len(matches)==1,'Pinned official binary not uniquely found: '+name
        destination=bins/name
        if destination.is_symlink() or destination.exists():destination.unlink()
        destination.symlink_to(matches[0])
    version=subprocess.check_output([str(bins/'uv'),'--version'],text=True).strip();assert version.split()[:2]==['uv','0.9.7']
    print('CGL_GRADER_UV_VERSION:'+version,flush=True)
    (bins/'env').write_text('export PATH="$HOME/.local/bin:$PATH"\n')
    # Both original logical task roots use fixed mounts. No credentials or host
    # /root contents are copied into either case-owned backing directory.
    mounts=[(work/'root',Path('/root'),False),(work/'app',Path('/app'),False),(work/'verifier',Path('/verifier'),True),(work/'verifier-logs',Path('/logs/verifier'),False)]
    for source,destination,readonly in mounts:
        assert source.is_dir() and not source.is_symlink()
        destination.mkdir(parents=True,exist_ok=True)
        subprocess.run(['mount','--bind',str(source),str(destination)],check=True,timeout=10)
        assert os.stat(source).st_ino==os.stat(destination).st_ino and os.stat(source).st_dev==os.stat(destination).st_dev
        if readonly:subprocess.run(['mount','-o','remount,bind,ro',str(destination)],check=True,timeout=10)
    python=work/'venv/bin/python';assert str(python)==state['task_python'] and python.is_file()
    env=dict(os.environ);env.update(HOME='/root',PATH=str(work/'venv/bin')+':/root/.local/bin:/usr/local/bin:/usr/bin:/bin',VIRTUAL_ENV=str(work/'venv'),TMPDIR=str(work/'tmp'),UV_CACHE_DIR=str(runtime/'uv-cache'),UV_INSTALLER_GITHUB_BASE_URL='https://releases.astral.sh/github')
    env.pop('PYTHONHOME',None);env.pop('PYTHONPATH',None)
    os.chdir(spec['workdir']);os.execvpe('bash',['bash','/verifier/test.sh'],env)

if __name__=='__main__':main()
