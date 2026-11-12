"""Client sends serial requests; task execution and original scoring run only in Profy."""
import argparse,gzip,hashlib,json,re,shlex,subprocess,sys,zipfile,io
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'skillsbench_evolution_20261110'))
from library_tasks import LibraryStudy
from profy_cloud_probe import Probe
from cloud_runtime_bridge import MemoryUpload
from run import save,sha
from native_evolution import require_paid
from native_support import archive_rows,choose_target,input_manifest,select_rows,task_spec,transport_pieces

PIN='f860ecf02ef53412a030f8661c83d644b739ff01'
DELIVER_COMMAND="test -f outputs/deliverables.zip && printf SBP_NATIVE_ZIP_SHA256: && sha256sum outputs/deliverables.zip && printf '[OUTPUT] ' && realpath outputs/deliverables.zip"
RUNTIME_FILES=['remote_setup.py','remote_tools.py','remote_native.py','native_support.py','task_specs.json']
GRADE_FILES=['remote_grade.py','remote_native.py','remote_namespace_grade.py','native_support.py','task_specs.json']

def host_command_kind(command):
    command=command.strip()
    if '\n' not in command:
        args=shlex.split(command)
        if len(args)==2 and args[0]=='python3' and Path(args[1]).name=='remote_setup.py':return 'setup'
        return None
    header,body=command.split('\n',1)
    pattern=r'''^python3\s+(?:[^\s]+/)?remote_tools\.py\s+(exec|get)\s*<<\s*(['"])SB_COMMAND\2$'''
    if not re.fullmatch(pattern,header):return None
    lines=body.splitlines()
    if not lines or lines[-1]!='SB_COMMAND' or 'SB_COMMAND' in lines[:-1]:return None
    return 'container'

def tracked_files(bench,task,part):
    prefix='tasks/'+task+'/'+part+'/'
    p=subprocess.run(['git','-C',str(bench),'ls-tree','-rz',PIN,'--',prefix],capture_output=True,check=True)
    rows=[]
    for raw in p.stdout.split(b'\0'):
        if not raw:continue
        header,name=raw.decode().split('\t',1);mode,kind,oid=header.split()
        assert kind=='blob' and mode in ['100644','100755'],'Symlink/submodule input needs explicit review'
        data=(bench/name).read_bytes()
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid,'Local source differs from pinned public blob: '+name
        rows.append((name[len(prefix):],data,0o755 if mode=='100755' else 0o644))
    if not rows:raise ValueError('Pinned task source unavailable')
    return rows

def forbidden_skill_read(event,no_skills,names):
    if event.get('tool_name')!='read':return False
    path=Path((event.get('parameters') or {}).get('file_path',''));parts=path.parts
    if not (path.name=='SKILL.md' or any(x in ['skills','bench_skills'] for x in parts)):return False
    if no_skills or '..' in parts:return True
    return not any(parts[i]=='bench_skills' and i+1<len(parts) and parts[i+1] in names for i in range(len(parts)))

def setup_receipts(events,strings):
    receipts={}
    for event in events:
        if event.get('type')!='tool_call.result':continue
        for text in strings(event.get('result')):
            for line in text.splitlines():
                if line.startswith('CGL_CASE_READY:'):
                    value=json.loads(line.split(':',1)[1]);receipts[json.dumps(value,sort_keys=True)]=value
    return list(receipts.values())

class DockerStudy(LibraryStudy):
    def __init__(self,args):
        super().__init__(args)
        # LibraryStudy selects alphabetically. Override only adapter target state,
        # after its construction; never rewrite a skill or an Evolution source.
        rows=tracked_files(self.bench.parent,args.task,'environment')
        target=getattr(args,'target_skill',None) or self.skill_name
        expected=getattr(args,'expected_parent_md_sha',None)
        if args.task!='weighted-gdp-calc' and not expected:raise ValueError('--expected-parent-md-sha is required for the nine-task registry')
        parent=choose_target(rows,target,expected)
        self.skill_name=target
        self.target=self.bench/args.task/'environment'/'skills'/target/'SKILL.md'
        self.original=parent
        args.skill_name=target;args.target_skill=target
        if target not in self.names:raise ValueError('Requested target missing from LibraryStudy skill inventory')
        self.parent_md_sha=sha(parent.encode())

    def solve(self,label,task,candidate=None,no_skills=False):
        if getattr(self.args,'prebuilt_record',None):raise ValueError('Native file execution does not use prebuilt images')
        spec=task_spec(task,getattr(self.args,'native_specs',None))
        # A supplied registry may relocate the reviewed file, not redefine tasks.
        assert spec==task_spec(task),'Native registry differs from reviewed adapter registry'
        if label=='with-CogniLife-skills' and candidate is None:raise ValueError('Evolved skill missing; no fallback')
        rows=tracked_files(self.bench.parent,task,'environment')
        choose_target(rows,self.skill_name,self.parent_md_sha)
        selected=select_rows(rows,spec)
        data=archive_rows(selected)
        pieces,transport=transport_pieces(data)
        expected_path=getattr(self.args,'expected_input_hashes',None)
        expected=json.loads(Path(expected_path).read_text()) if expected_path else None
        if expected is not None and (not isinstance(expected,dict) or not all(isinstance(k,str) and re.fullmatch('[0-9a-f]{64}',v or '') for k,v in expected.items())):
            raise ValueError('--expected-input-hashes must contain the complete logical-path to SHA256 map from A')
        if task=='pdf-excel-diff' and label in ['no-skills','with-CogniLife-skills'] and expected is None:
            raise ValueError('Comparison groups require --expected-input-hashes from A')
        versions=json.loads(Path(self.args.native_package_versions).read_text()) if getattr(self.args,'native_package_versions',None) else {}
        skill_hashes={};skills=[]
        files=[MemoryUpload(n,b) for n,b in pieces]
        input_file=files[0]
        if not no_skills:
            package=io.BytesIO()
            with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_DEFLATED) as archive:
                for name,raw,mode in rows:
                    if not name.startswith('skills/'):continue
                    rel='bench_skills/'+name[len('skills/'):]
                    if candidate is not None and rel=='bench_skills/'+self.skill_name+'/SKILL.md':raw=candidate.encode()
                    info=zipfile.ZipInfo(rel);info.external_attr=(mode|0o100000)<<16;info.compress_type=zipfile.ZIP_DEFLATED
                    archive.writestr(info,raw);skill_hashes[rel]=sha(raw)
            skills=self.names;files.append(MemoryUpload('benchmark_skills.zip',package.getvalue()))
        config={'task':task,'benchmark_pin':PIN,'input_sha256':sha(data),'transport':transport,'input_manifest':input_manifest(selected),'skills':skills,'target_skill':self.skill_name,'parent_md_sha256':self.parent_md_sha,'skill_hashes':skill_hashes,'native_file_runtime':True,'native_package_versions':versions,'expected_input_hashes':expected}
        files.append(MemoryUpload('case_config.json.gz',gzip.compress(json.dumps(config).encode())))
        files.extend(HERE/n for n in RUNTIME_FILES)
        if any(len(p.read_bytes())>450000 for p in files):raise ValueError('Non-input attachment exceeds upload bound')
        # All validation above precedes reservation, uploads, sessions and model work.
        require_paid(self.args.allow_paid)
        f=self.out/label;f.mkdir(exist_ok=True)
        if (f/'started.json').exists():raise ValueError('Attempt already reserved; do not duplicate')
        source_files=set(RUNTIME_FILES+GRADE_FILES+['study.py'])
        save(f/'started.json',{'task':task,'label':label,'model':'gpt-6.1-sol','adapter':'cloud-native-owned-files-v2','adapter_source_sha256':{n:sha((HERE/n).read_bytes()) for n in sorted(source_files)}})
        save(f/'case_config.json',config)
        user='cgl-native-'+sha(str(f).encode())[:20]
        uploads=[]
        for item in files:uploads.append(self.transport.upload(item,user))
        save(f/'uploads.json',uploads)
        session=self.transport.api('/v1/sessions',{'agent':self.transport.expert_id,'title':'Public task execution'},user)['id']
        save(f/'session.json',{'id':session,'end_user':user})
        tasktext=(self.bench/task/'task.md').read_text().split('---',2)[2].strip()
        skills_text=('Read all supplied benchmark skills in full using read: '+', '.join('bench_skills/'+n+'/SKILL.md' for n in self.names)+'. Follow their relevant instructions. ' if not no_skills else 'No benchmark skills are supplied. Do not discover, read, import or activate any expert/user/builtin skill package. ')
        common="""Execution adapter, identical across conditions: First run exactly python3 remote_setup.py using bash with background=true, then awaitbash on that same job until completion. Do not start setup twice. Do not inspect transport attachments or case_config.json.gz. If setup fails, stop without editing setup code.
After CGL_CASE_READY, use the prepared native Profy host as uid1000, not Docker, PRoot or a solver mount namespace. Original logical /root maps to the receipt's task_roots./root; original logical /app maps to task_roots./app. This mapping is identical in every group. Commands run with cwd mapped from the original WORKDIR, HOME in the owned case root, and the task venv first on PATH. Use those actual owned paths whenever a question or skill mentions absolute /root or /app paths; relative paths are unchanged. No automatic absolute-path interception is performed. Previews accept original logical paths. The harness translates exports and the fixed grader back to original logical paths.
This is not the official Ubuntu image or a security sandbox. Native apt uses --no-install-recommends; the runtime receipt records this adaptation, pre-existing packages, actual versions and omitted blocked requirements. Do not install, import, use or bypass reportlab, fpdf, fpdf2, python-pptx or pptxgenjs; use permitted tools instead. Do not change dependencies or use sudo. Do not access host credentials, control files, other cases, verifier material, Memory or unsupplied skills.
All task shell commands must use this exact quoted heredoc form:
python3 remote_tools.py exec <<'SB_COMMAND'
<ordinary shell commands in the owned task cwd>
SB_COMMAND
For a preview use python3 remote_tools.py get with the same quoted heredoc, whose body is a JSON string containing the original absolute logical file path. It prints an absolute PREVIEW_PATH for read. Do not run task code outside this interface or edit adapter/context files. Do not access /verifier or /logs/verifier and do not attempt scoring. At most48 tool calls and24 model turns. Finish when requested files are ready. The harness freezes and exports actual changed files before exposing the original scorer. Do not create a transport ZIP or extra report."""
        body={'agent':{'id':self.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],'input':tasktext+'\n\n'+common+'\nAfter setup: '+skills_text+'All operations must be sequential; do not delegate.','stream':True,'session_id':session,'attachment_file_ids':[x['file_id'] for x in uploads]}
        row=super().execute(f,label,task,candidate,no_skills,body,session,user,input_file)
        delivered=json.loads((f/'grading-only/result.json').read_text())
        row.update(output_received=delivered['output_received'],native_zip_sha256=delivered['native_zip_sha256'],file_hashes=delivered['file_hashes'],artifact_collection_phase='fixed original grading after solving',grader_same_platform_session=True,condition_valid=not row['external_skill_tools_observed'] and (no_skills or row['target_skill_read_verified']))
        save(f/'result.json',row);return row

    def grade(self,task,folder):
        summary=json.loads((folder/'run_summary.json').read_text())
        if not summary['completed'] or summary['error']:raise RuntimeError('Solver stream incomplete; do not score')
        events=[json.loads(s) for s in (folder/'events.jsonl').read_text().splitlines()]
        config=json.loads((folder/'case_config.json').read_text())
        for e in events:
            if e.get('type')=='tool_call.in_progress' and forbidden_skill_read(e,not config['skills'],self.names):raise RuntimeError('Read of an unsupplied skill')
            if e.get('type')=='tool_call.in_progress' and e.get('tool_name') not in ['read','bash','awaitbash','skills_read']:raise RuntimeError('Unexpected solver tool')
            if e.get('type')=='tool_call.in_progress' and e.get('tool_name')=='bash' and host_command_kind(e['parameters']['command'].strip()) not in ['setup','container']:raise RuntimeError('Unapproved host shell command')
        ready=setup_receipts(events,self.strings)
        if len(ready)!=1:raise RuntimeError('No unique setup receipt; no grading call started')
        state=ready[0];session=json.loads((folder/'session.json').read_text())
        assert state['input_sha256']==config['input_sha256'] and state['task']==task
        if config['expected_input_hashes'] is not None:assert state['original_file_sha256']==config['expected_input_hashes']
        save(folder/'native_input_hashes.json',state['original_file_sha256'])
        root=folder/'grading-only';root.mkdir(exist_ok=False)
        rows=tracked_files(self.bench.parent,task,'verifier');raw=archive_rows(rows)
        if len(raw)>450000:raise ValueError('Verifier attachment exceeds existing grading transport bound')
        payload=MemoryUpload('original_verifier.tar.gz',raw)
        control={'expected_context':state,'verifier_archive_sha256':sha(raw),'source_hashes':{n:sha(b) for n,b,m in rows},'expects_ctrf':any(n=='test.sh' and b'ctrf' in b for n,b,m in rows)}
        grader=Probe(argparse.Namespace(**{**vars(self.args),'out':str(root),'dev_task':task,'skill_name':self.skill_name,'hard_timeout_sec':1200}))
        files=[payload,MemoryUpload('grade_config.json.gz',gzip.compress(json.dumps(control).encode()))]+[HERE/n for n in GRADE_FILES]
        uploads=[]
        for item in files:uploads.append(grader.transport.upload(item,session['end_user']))
        body={'agent':{'id':grader.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[], 'input':'Grading only, no further solving. Run exactly python3 remote_grade.py once using bash with background=true, then awaitbash on that same job until completion. Do not edit answers, scripts, config or tests, inspect the hidden verifier, use skills/Memory, purchase anything or ask questions. The script freezes/exports actual files before exposing the original verifier, runs the original test.sh, preserves source hashes and cleans only this case. After completion, run exactly '+DELIVER_COMMAND+' in one foreground bash call to expose the actual attachment. Return the absolute [OUTPUT] path printed by that command. Do not rerun scoring.','stream':True,'session_id':session['id'],'attachment_file_ids':[x['file_id'] for x in uploads]}
        delivered=grader.execute(root,'grading-only','original-grading',None,True,body,session['id'],session['end_user'],payload)
        grade_events=[json.loads(s) for s in (root/'events.jsonl').read_text().splitlines()]
        commands=[e['parameters']['command'].strip() for e in grade_events if e.get('type')=='tool_call.in_progress' and e.get('tool_name')=='bash']
        assert commands==['python3 remote_grade.py',DELIVER_COMMAND],'Grader command changed or repeated'
        assert delivered['output_received'],'Actual grader artifact not received'
        report=json.loads((root/'output/score_receipt.json').read_text());save(folder/'ORIGINAL_SCORE.json',report)
        if report.get('infrastructure_error'):raise RuntimeError(report['infrastructure_error'])
        assert report['original_source_before_after_verified']
        return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['workspace','out','task','label','keys-file']:p.add_argument('--'+name,required=True)
    for name in ['candidate','prebuilt-record','native-package-versions','native-specs','expected-input-hashes','expected-parent-md-sha']:p.add_argument('--'+name)
    p.add_argument('--target-skill',default='xlsx')
    p.add_argument('--native-file-runtime',action='store_true');p.add_argument('--allow-paid',action='store_true')
    args=p.parse_args();args.hard_timeout_sec=1600
    study=DockerStudy(args)
    candidate=Path(args.candidate).read_text() if args.candidate else None
    if args.label=='with-CogniLife-skills' and candidate is None:raise ValueError('No evolved candidate supplied')
    row=study.solve(args.label,args.task,candidate,args.label=='no-skills')
    print(json.dumps({'task':args.task,'label':args.label,'score':row['score'],'tokens':row['tokens']},ensure_ascii=False))
