"""Serial uid1000 execution in the prepared owned task filesystem."""
import json,sys
from pathlib import Path
from remote_setup import cloud_only
from remote_native import execute

def main():
    cloud_only();base=Path.cwd()
    if (base/'case_frozen').exists():raise RuntimeError('Solving is finished; no answer changes allowed')
    state=json.loads((base/'case_context.json').read_text())
    if state.get('backend')!='native-owned':raise RuntimeError('Unsupported runtime backend')
    raise SystemExit(execute(base,state,sys.argv[1],sys.stdin.read()))

if __name__=='__main__':main()
