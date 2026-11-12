"""Resume only a grading infrastructure failure, with the original frozen answer bytes."""
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'skillsbench_evolution_20261110'))
from profy_cloud_probe import Probe
from run import save,sha
SCRIPT=r'''import gzip,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
base=Path.cwd();old=json.loads((base/'output/score_receipt.json').read_text())
assert old.get('infrastructure_error') and old.get('tests') is None,'Only an infrastructure failure may be resumed'
answer=base/'output/fs/root/gdp.xlsx'
assert hashlib.sha256(answer.read_bytes()).hexdigest()==EXPECTED_ANSWER==old['pre_grade_file_hashes']['/root/gdp.xlsx'],'Answer changed after freezing'
control=json.loads(gzip.decompress((base/'grade_config.json.gz').read_bytes()))
assert hashlib.sha256((base/'original_verifier.tar.gz').read_bytes()).hexdigest()==control['verifier_archive_sha256']==EXPECTED_VERIFIER
previous=json.loads((base/'case_context.json').read_text())
for n,v in previous['native_package_versions'].items():assert subprocess.check_output(['dpkg-query','-W','-f=${Version}',n],text=True).strip()==v
repair=base/'grading-repair-v1';repair.mkdir(exist_ok=False)
work=Path(tempfile.mkdtemp(prefix='cgl-task-',dir=str(repair)));runtime=Path(tempfile.mkdtemp(prefix='cgl-sock-',dir='/tmp'))
for name in ['root','verifier','verifier-logs']:(work/name).mkdir()
shutil.copyfile(answer,work/'root/gdp.xlsx');shutil.copyfile(base/'original_verifier.tar.gz',repair/'original_verifier.tar.gz')
if (base/'bench_skills').is_dir():(repair/'bench_skills').symlink_to(base/'bench_skills',target_is_directory=True)
state={**previous,'workspace':str(repair),'work':str(work),'runtime':str(runtime),'native_command':[],'grading_only_repair':True,'frozen_solver_answer_sha256':EXPECTED_ANSWER}
(repair/'case_context.json').write_text(json.dumps(state));control['expected_context']=state
(repair/'grade_config.json.gz').write_bytes(gzip.compress(json.dumps(control).encode()))
subprocess.run([sys.executable,str(base/'remote_grade.py')],cwd=repair,check=True,timeout=1100)
print('REPAIR_COMPLETED_WITHOUT_NEW_SOLVING')
'''
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for n in ['workspace','out','case','keys-file','original-delivery']:p.add_argument('--'+n,required=True)
 p.add_argument('--allow-paid',action='store_true');a=p.parse_args();case=Path(a.case)
 previous=json.loads((case/'session.json').read_text());delivery=Path(a.original_delivery)
 old=json.loads((delivery/'output/score_receipt.json').read_text());origin=json.loads((delivery/'output/DELIVERY_ORIGIN.json').read_text())
 assert old.get('infrastructure_error') and old.get('tests') is None
 expected=old['pre_grade_file_hashes']['/root/gdp.xlsx'];archive_hash=origin['original_manifest']['input_sha256']
 a.expected_input_sha256=archive_hash;a.hard_timeout_sec=1300
 study=Probe(a);folder=study.out/'grading-repair-v1';folder.mkdir(exist_ok=False)
 script=folder/'repair_native_grading.py';script.write_text('EXPECTED_ANSWER='+repr(expected)+'\nEXPECTED_VERIFIER='+repr(archive_hash)+'\n'+SCRIPT)
 files=[script,HERE/'remote_grade.py',HERE/'remote_namespace_grade.py'];uploads=[study.transport.upload(x,previous['end_user']) for x in files]
 command="printf SBP_NATIVE_ZIP_SHA256: && sha256sum grading-repair-v1/outputs/deliverables.zip && printf '[OUTPUT] ' && realpath grading-repair-v1/outputs/deliverables.zip"
 body={'agent':{'id':study.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],'input':'Fixed grading repair only, never solve again. Run exactly python3 repair_native_grading.py once using background=true; await that same job until it ends. It permits only an infrastructure failure with no test report, verifies unchanged original answer and verifier hashes, and runs the unchanged original scorer in a private kernel namespace with pinned uv dependency. Do not edit any answer, tests, scripts, config or rules, use skills/Memory, ask questions or buy anything. After completion, run this exact foreground delivery command once: '+command+'. Do not rerun grading.','stream':True,'session_id':previous['id'],'attachment_file_ids':[x['file_id'] for x in uploads]}
 row=study.execute(folder,'grading-repair-v1','original-grading-repair',None,True,body,previous['id'],previous['end_user'],script)
 assert row['output_received'],'Inspect existing events for delivery; never solve again'
 report=json.loads((folder/'output/score_receipt.json').read_text())
 assert report['pre_grade_file_hashes']['/root/gdp.xlsx']==expected
 save(folder/'GRADING_REPAIR_PROVENANCE.json',{'frozen_answer_sha256':expected,'original_invalid_receipt':old,'new_solver_run':False,'original_verifier_archive_sha256':archive_hash})
 assert not report.get('infrastructure_error'),report.get('infrastructure_error')
 assert report['original_source_before_after_verified'] and report['answer_files_unchanged_by_grader']
 result=json.loads((case/'SOLVER_RESULT_BEFORE_GRADING.json').read_text())
 no_skills=not json.loads((case/'case_config.json').read_text())['skills']
 result.update(score=report,output_received=True,native_zip_sha256=row['native_zip_sha256'],file_hashes=row['file_hashes'],grading_repair=True,new_solver_run_for_repair=False,condition_valid=not result['external_skill_tools_observed'] and (no_skills or result['target_skill_read_verified']))
 save(case/'ORIGINAL_SCORE.json',report);save(case/'result.json',result)
 print(json.dumps({'score':report,'solver_tokens':result['tokens']}))
