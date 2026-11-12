"""Expose an existing immutable transport ZIP with the platform's documented absolute OUTPUT tag."""
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'skillsbench_evolution_20261110'))
from profy_cloud_probe import Probe
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for n in ['workspace','out','case','keys-file','original-input-script']:p.add_argument('--'+n,required=True)
 p.add_argument('--allow-paid',action='store_true');a=p.parse_args()
 prev=json.loads((Path(a.case)/'session.json').read_text());study=Probe(a);folder=study.out/'absolute-delivery-only';folder.mkdir(exist_ok=False)
 command="printf SBP_NATIVE_ZIP_SHA256: && sha256sum deliverables.zip && printf '[OUTPUT] ' && realpath deliverables.zip"
 body={'agent':{'id':study.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],'input':'File delivery only, no solve or scoring. Run exactly the following foreground bash command unchanged once, timeout60: '+command+'. It reads only the already existing ZIP and prints an absolute [OUTPUT] path, as required by the output collector. Do not edit any files, use skills/Memory, inspect tests, ask questions or buy anything.','stream':True,'session_id':prev['id'],'attachment_file_ids':[]}
 row=study.execute(folder,'absolute-delivery-only','transport-only',None,True,body,prev['id'],prev['end_user'],Path(a.original_input_script))
 print(json.dumps({'output_received':row['output_received'],'native_zip_sha256':row['native_zip_sha256'],'file_count':len(row['file_hashes'])}))
