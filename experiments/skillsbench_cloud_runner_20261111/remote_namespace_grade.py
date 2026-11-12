"""Fixed grading only: real private mount namespace and the original pinned uv dependency."""
import json,os,shutil,subprocess
from pathlib import Path

def main():
    base=Path.cwd();state=json.loads((base/'case_context.json').read_text());work=Path(state['work']);runtime=Path(state['runtime'])
    assert base.as_posix().startswith('/home/user/workspace/') and (base/'case_frozen').is_file()
    assert work.parent==base and work.name.startswith('cgl-task-')
    assert runtime.parent==Path('/tmp') and runtime.name.startswith('cgl-sock-')
    assert os.getuid()==0,'Fixed grader requires the isolated namespace, not fake root'
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
    for source,destination,readonly in [(work/'root',Path('/root'),False),(work/'verifier',Path('/verifier'),True),(work/'verifier-logs',Path('/logs/verifier'),False)]:
        destination.mkdir(parents=True,exist_ok=True)
        subprocess.run(['mount','--bind',str(source),str(destination)],check=True,timeout=10)
        if readonly:subprocess.run(['mount','-o','remount,bind,ro',str(destination)],check=True,timeout=10)
    env=dict(os.environ);env.update(HOME='/root',PATH='/root/.local/bin:/usr/local/bin:/usr/bin:/bin',UV_CACHE_DIR=str(runtime/'uv-cache'),UV_INSTALLER_GITHUB_BASE_URL='https://releases.astral.sh/github')
    os.chdir('/root');os.execvpe('bash',['bash','/verifier/test.sh'],env)
if __name__=='__main__':main()
