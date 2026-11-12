"""Validate separate cloud grading using a frozen output, never a new solve."""
import argparse,ast,hashlib,json,tarfile,zipfile
from pathlib import Path
from run import Study,save,sha

RUNNER='''import os,sys,json,hashlib,subprocess,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
root=Path.cwd();expected=json.loads(Path('STATIC_HASHES.json').read_text())
def verify():
 for name,digest in expected.items():
  assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
verify()
subprocess.run(['uv','pip','install','--target','cloud_grader_deps','pytest==8.4.1','pytest-json-ctrf==0.3.5'],check=True)
out=Path('output');out.mkdir(exist_ok=True)
env=dict(os.environ);env['PYTHONPATH']=str(root/'cloud_grader_deps')
p=subprocess.run([sys.executable,'-m','pytest','bound_verifier/test_outputs.py','-rA','-v','-p','no:cacheprovider','--ctrf',str(root/'output/ctrf.json'),'--junitxml='+str(root/'output/junit.xml')],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
(out/'pytest.log').write_text(p.stdout);verify()
cases=ET.parse(out/'junit.xml').findall('.//testcase');failed=sum(c.find('failure') is not None or c.find('error') is not None for c in cases);skipped=sum(c.find('skipped') is not None for c in cases)
r={'original_returncode':p.returncode,'strict':int(p.returncode==0 and bool(cases) and skipped==0),'tests':len(cases),'passed':len(cases)-failed-skipped,'failed':failed,'skipped':skipped,'all_static_hashes_before_after_verified':True,'solver_output_unchanged':True,'grading_context_only':True}
(out/'receipt.json').write_text(json.dumps(r,indent=2))
files={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.iterdir() if f.is_file()}
m={'input_sha256':hashlib.sha256(Path('grading_bundle.zip').read_bytes()).hexdigest(),'files':files}
Path('outputs').mkdir(exist_ok=True)
with zipfile.ZipFile('outputs/deliverables.zip','w') as z:
 for name in files:z.write(name,name)
 z.writestr('manifest.json',json.dumps(m))
print(json.dumps(r));print('SBP_NATIVE_ZIP_SHA256:'+hashlib.sha256(Path('outputs/deliverables.zip').read_bytes()).hexdigest());print('[OUTPUT] outputs/deliverables.zip')
'''

class GradingOnly(Study):
    def grade(self,task,folder):
        return {'strict':0,'tests':0,'passed':0,'failed':0,'skipped':0,'separate_grading_transport_only':True}

def prepare(workspace,out,solver_folder=None):
    source=workspace/'04_项目数据与代码/skillsbench/tasks/3d-scan-calc/verifier/test_outputs.py'
    frozen=workspace/'01_任务结果/2026-11-11_skillsbench_full_library/library-runs/3d-scan-calc'
    original=source.read_text();tree=ast.parse(original);count=sum(isinstance(n,ast.Assert) for n in ast.walk(tree))
    changes=[]
    class Bind(ast.NodeTransformer):
        def visit_Constant(self,node):
            if isinstance(node.value,str) and (node.value=='/root' or node.value.startswith('/root/')):
                replacement='fs'+node.value;changes.append({'from':node.value,'to':replacement})
                return ast.copy_location(ast.Constant(replacement),node)
            return node
    bound=Bind().visit(tree);assert count==sum(isinstance(n,ast.Assert) for n in ast.walk(bound))
    # Only original path constants change; no tolerance, expected value or assertion is edited.
    for change in changes:assert change['to']=='fs'+change['from']
    files={'bound_verifier/test_outputs.py':(ast.unparse(bound)+'\n').encode()}
    with tarfile.open(frozen/'public_environment.tar.gz') as tar:
        for name in ['fs/root/scan_data.stl','fs/root/material_density_table.md']:
            files[name]=tar.extractfile(name).read()
    result_folder=Path(solver_folder) if solver_folder is not None else frozen/'with-skills'
    files['fs/root/mass_report.json']=(result_folder/'output/fs/root/mass_report.json').read_bytes()
    hashes={name:hashlib.sha256(raw).hexdigest() for name,raw in files.items()}
    files['STATIC_HASHES.json']=json.dumps(hashes).encode();files['grade_entry.py']=RUNNER.encode()
    archive=out/'grading_bundle.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name,raw in files.items():z.writestr(name,raw)
    save(out/'GRADING_PROVENANCE.json',{'original_verifier_sha256':sha(source.read_bytes()),'assertions_preserved':count,'path_bindings_only':changes,'static_hashes':hashes,'bundle_sha256':sha(archive.read_bytes()),'not_solver_or_evolution_input':True})
    return archive

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True);p.add_argument('--keys-file',required=True);p.add_argument('--allow-paid',action='store_true');args=p.parse_args()
    study=GradingOnly(args);folder=study.out/'grading-3d-frozen';folder.mkdir(exist_ok=False);archive=prepare(study.workspace,folder)
    user='cgl-separate-grading-check';upload=study.transport.upload(archive,user)
    session=study.transport.api('/v1/sessions',{'agent':study.transport.expert_id,'title':'Separate frozen-output grading'},user)['id']
    command='unzip -o grading_bundle.zip && python3 grade_entry.py'
    body={'agent':{'id':study.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],
        'input':'This is a separate grading session, never a task-solving or skill-authoring session. Run exactly one bash command: '+command+'. Do not edit any file, inspect credentials, use Memory, invoke skills or ask questions. The fixed script runs the original tests with path bindings, checks all static hashes before and after, and packages actual results. Return [OUTPUT] deliverables.zip. Do not interpret or repair the candidate answer.',
        'stream':True,'session_id':session,'attachment_file_ids':[upload['file_id']]}
    result=study.execute(folder,'separate-grading','frozen-output-grading',None,True,body,session,user,archive)
    if not result['completed'] or not result['output_received']:raise RuntimeError('Cloud grading incomplete')
    events=[json.loads(s) for s in (folder/'events.jsonl').read_text().splitlines()]
    commands=[e['parameters']['command'].strip() for e in events if e.get('type')=='tool_call.in_progress' and e.get('tool_name')=='bash']
    assert commands==[command], 'Unexpected grading commands; do not accept score'
    receipt=json.loads((folder/'output/receipt.json').read_text());assert receipt['all_static_hashes_before_after_verified']
    save(folder/'ACCEPTED_CLOUD_GRADING.json',receipt);print(json.dumps(receipt))
