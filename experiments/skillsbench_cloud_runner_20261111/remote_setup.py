"""Profy native setup only; no images, builds, Docker daemon or solver launcher."""
import gzip,hashlib,json,sys
from pathlib import Path

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def cloud_only():
    if sys.platform!='linux' or not str(Path.cwd()).startswith('/home/user/workspace/'):
        raise RuntimeError('Cloud-only script. Do not run this on the local computer.')

def main():
    cloud_only();base=Path.cwd()
    # Atomic reservation also blocks duplicate background setup while preparation runs.
    (base/'case_setup_reserved').touch(exist_ok=False)
    if (base/'case_context.json').exists():raise RuntimeError('Case already prepared')
    meta=json.loads(gzip.decompress((base/'case_config.json.gz').read_bytes()))
    from native_support import read_transport
    from remote_native import prepare
    with read_transport(base,meta) as buffer:prepare(base,meta,buffer)

if __name__=='__main__':main()
