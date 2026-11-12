"""Repackage existing output bytes for delivery only. Never solve, grade, or change answers."""
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'skillsbench_evolution_20261110'))
from profy_cloud_probe import Probe
SCRIPT=r'''import hashlib,json,zipfile,io
from pathlib import Path
base=Path.cwd();raw=(base/'outputs/deliverables.zip').read_bytes()
assert hashlib.sha256(raw).hexdigest()==EXPECTED_ZIP
with zipfile.ZipFile(io.BytesIO(raw)) as old:
 manifest=json.loads(old.read('manifest.json'));files={n:old.read(n) for n in manifest['files']}
 assert all(hashlib.sha256(b).hexdigest()==manifest['files'][n] for n,b in files.items())
 for n in files:assert n.startswith('output/') and '..' not in Path(n).parts
 files['output/DELIVERY_ORIGIN.json']=json.dumps({'original_zip_sha256':EXPECTED_ZIP,'original_manifest':manifest,'answer_and_score_file_bytes_unchanged':True,'new_solver_run':False,'new_grading_run':False},indent=2).encode()
manifest={'input_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'files':{n:hashlib.sha256(b).hexdigest() for n,b in files.items()}}
with zipfile.ZipFile(base/'deliverables.zip','w',compression=zipfile.ZIP_DEFLATED) as out:
 for n,b in files.items():out.writestr(n,b)
 out.writestr('manifest.json',json.dumps(manifest))
print('SBP_NATIVE_ZIP_SHA256:'+hashlib.sha256((base/'deliverables.zip').read_bytes()).hexdigest());print('[OUTPUT] deliverables.zip')
'''
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for n in ['workspace','out','case','keys-file','expected-zip']:p.add_argument('--'+n,required=True)
 p.add_argument('--allow-paid',action='store_true');a=p.parse_args();assert __import__('re').fullmatch('[0-9a-f]{64}',a.expected_zip)
 previous=json.loads((Path(a.case)/'session.json').read_text());study=Probe(a);folder=study.out/'delivery-only-recovery';folder.mkdir(exist_ok=False)
 script=folder/'recover_delivery.py';script.write_text('EXPECTED_ZIP='+repr(a.expected_zip)+'\n'+SCRIPT)
 upload=study.transport.upload(script,previous['end_user'])
 body={'agent':{'id':study.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],'input':'File delivery only. Run exactly python3 recover_delivery.py unchanged once in foreground bash, background=false, timeout90. It verifies the existing ZIP checksum and original file checksums, and changes only the transport manifest. It prints [OUTPUT] in this foreground call. Do not solve, grade, inspect tests, alter answers, use skills/Memory, buy anything or ask questions. Return [OUTPUT] deliverables.zip.','stream':True,'session_id':previous['id'],'attachment_file_ids':[upload['file_id']]}
 row=study.execute(folder,'delivery-only-recovery','transport-only',None,True,body,previous['id'],previous['end_user'],script)
 print(json.dumps({'actual_existing_files_received':row['output_received'],'file_hashes':row['file_hashes']}))
