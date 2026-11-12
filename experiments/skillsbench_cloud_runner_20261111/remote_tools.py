"""Run solver commands in the prepared task container; export previews when needed."""
import json,subprocess,sys,uuid
from pathlib import Path
from remote_setup import cloud_only

def main():
    cloud_only();base=Path.cwd();state=json.loads((base/'case_context.json').read_text())
    if (base/'case_frozen').exists():raise RuntimeError('Solving is finished; no answer changes allowed')
    mode=sys.argv[1];raw=sys.stdin.read();cli=state['cli'];container=state['container']
    if mode=='exec':
        p=subprocess.run(cli+['exec','-i',container,state['shell'],'-lc',raw],timeout=480)
        raise SystemExit(p.returncode)
    if mode=='get':
        path=Path(json.loads(raw))
        assert path.is_absolute() and '..' not in path.parts
        assert path.parts[1] not in ['verifier','logs','etc','usr','proc','sys','dev']
        target=base/'preview'/uuid.uuid4().hex;target.mkdir(parents=True)
        subprocess.run(cli+['cp',container+':'+str(path),str(target)],check=True,timeout=60)
        subprocess.run(['sudo','-n','chown','-R',str(__import__('os').getuid())+':'+str(__import__('os').getgid()),str(target)],check=True)
        print('PREVIEW_PATH:'+str(target/path.name));return
    raise ValueError('Only exec and get are supported')

if __name__=='__main__':main()
