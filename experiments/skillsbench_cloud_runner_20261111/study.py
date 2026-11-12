"""Client sends requests only; all original task environments and scoring run in Profy."""
import argparse,gzip,hashlib,io,json,re,shlex,subprocess,sys,tarfile,urllib.request,zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'skillsbench_evolution_20261110'))
from library_tasks import LibraryStudy
from profy_cloud_probe import Probe
from cloud_runtime_bridge import MemoryUpload
from run import save,sha
from native_evolution import require_paid

PIN='f860ecf02ef53412a030f8661c83d644b739ff01'

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
        path=bench/name;data=path.read_bytes()
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid,'Local source differs from the pinned public blob: '+name
        rows.append((name[len(prefix):],data,0o755 if mode=='100755' else 0o644))
    if not rows:raise ValueError('Pinned task source unavailable')
    return rows

def archive_rows(rows,empty_skills=False):
    out=io.BytesIO()
    with tarfile.open(fileobj=out,mode='w:gz') as archive:
        if empty_skills:
            info=tarfile.TarInfo('skills');info.type=tarfile.DIRTYPE;info.mode=0o755;archive.addfile(info)
        for name,raw,mode in rows:
            if empty_skills and Path(name).parts[0]=='skills':continue
            info=tarfile.TarInfo(name);info.size=len(raw);info.mode=mode;archive.addfile(info,io.BytesIO(raw))
    return out.getvalue()

def primary_pin(reference):
    # Prototype accepts explicit Docker Hub tags; unsupported references fail before a model call.
    assert re.fullmatch(r'[a-z0-9_./-]+:[a-zA-Z0-9_.-]+',reference)
    repo,tag=reference.rsplit(':',1);repo=repo if '/' in repo else 'library/'+repo
    with urllib.request.urlopen('https://auth.docker.io/token?service=registry.docker.io&scope=repository:'+repo+':pull',timeout=30) as r:token=json.load(r)['token']
    headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json, application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json'}
    with urllib.request.urlopen(urllib.request.Request('https://registry-1.docker.io/v2/'+repo+'/manifests/'+tag,headers=headers),timeout=30) as r:raw=r.read(2000000)
    manifest=json.loads(raw)
    if 'manifests' not in manifest:return 'sha256:'+sha(raw)
    selected=[x for x in manifest['manifests'] if x.get('platform',{}).get('os')=='linux' and x.get('platform',{}).get('architecture')=='amd64']
    assert len(selected)==1
    return selected[0]['digest']

class DockerStudy(LibraryStudy):
    def solve(self,label,task,candidate=None,no_skills=False):
        require_paid(self.args.allow_paid)
        if label=='with-CogniLife-skills' and candidate is None:raise ValueError('Evolved skill missing; no fallback to the original')
        f=self.out/label;f.mkdir(exist_ok=True)
        if (f/'started.json').exists():raise ValueError('Attempt already reserved; do not duplicate')
        bench=self.bench.parent;rows=tracked_files(bench,task,'environment')
        data=archive_rows(rows,empty_skills=True);input_file=MemoryUpload('task_environment.tar.gz',data)
        if len(data)>500000:raise ValueError('Prototype source exceeds single-upload bound; no model call started')
        dockerfile=next(raw.decode() for name,raw,mode in rows if name=='Dockerfile')
        refs=re.findall(r'^FROM\s+(\S+)',dockerfile,re.M)
        if len(refs)!=1:raise ValueError('Prototype requires one explicit base image; no model call started')
        pins={ref:primary_pin(ref) for ref in refs}
        skill_hashes={};skills=[];files=[input_file]
        if not no_skills:
            package=io.BytesIO()
            with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_DEFLATED) as archive:
                for name,raw,mode in rows:
                    if not name.startswith('skills/'):continue
                    rel='bench_skills/'+name[len('skills/'):]
                    if candidate is not None and rel=='bench_skills/'+self.skill_name+'/SKILL.md':raw=candidate.encode()
                    archive.writestr(rel,raw);skill_hashes[rel]=sha(raw)
            skills=self.names;files.append(MemoryUpload('benchmark_skills.zip',package.getvalue()))
        config={'task':task,'benchmark_pin':PIN,'input_sha256':sha(data),'skills':skills,'target_skill':self.skill_name,'skill_hashes':skill_hashes,'base_images':pins}
        files.append(MemoryUpload('case_config.json.gz',gzip.compress(json.dumps(config).encode())))
        files += [HERE/'remote_setup.py',HERE/'remote_tools.py']
        if any(len(p.read_bytes())>500000 for p in files):raise ValueError('Prototype upload exceeds bound; no model call started')
        save(f/'started.json',{'task':task,'label':label,'model':'gpt-6.1-sol','adapter':'cloud-original-docker-prototype-v1'})
        save(f/'case_config.json',config)
        user='cgl-native-'+sha(str(f).encode())[:20]
        uploads=[self.transport.upload(p,user) for p in files];save(f/'uploads.json',uploads)
        session=self.transport.api('/v1/sessions',{'agent':self.transport.expert_id,'title':'Public task execution'},user)['id']
        save(f/'session.json',{'id':session,'end_user':user})
        tasktext=(self.bench/task/'task.md').read_text().split('---',2)[2].strip()
        skills_text=('Read all supplied benchmark skills in full using read: '+', '.join('bench_skills/'+n+'/SKILL.md' for n in self.names)+'. Follow their relevant instructions. ' if not no_skills else 'No benchmark skills are supplied. Do not discover, read, import or activate any expert/user/builtin skill package. ')
        common="""Execution adapter, identical across conditions: First run exactly python3 remote_setup.py with foreground bash and timeout850. Do not inspect task_environment.tar.gz or case_config.json.gz. If setup fails, stop and report the failure without editing setup code. After CGL_CASE_READY, solve the original task in its original Docker environment. All task shell commands must use this exact quoted heredoc form:
python3 remote_tools.py exec <<'SB_COMMAND'
<ordinary shell commands running inside the task container>
SB_COMMAND
For a visual/native file preview, use python3 remote_tools.py get with the same quoted heredoc, whose body is a JSON string containing the original absolute file path. It prints PREVIEW_PATH for read. Do not run task code on the host or edit the adapter/context files. Do not access /verifier, /logs/verifier, oracle, reference answers, Memory, other sessions or other skills. Do not attempt scoring. At most48 tool calls and24 model turns. Finish when the requested task files are ready. The harness exports actual changed files and runs the original scorer afterwards; do not create a transport ZIP or extra report."""
        body={'agent':{'id':self.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],'input':tasktext+'\n\n'+common+'\nAfter setup: '+skills_text+'All operations must be sequential; do not delegate.','stream':True,'session_id':session,'attachment_file_ids':[x['file_id'] for x in uploads]}
        row=super().execute(f,label,task,candidate,no_skills,body,session,user,input_file)
        delivered=json.loads((f/'grading-only/result.json').read_text())
        row.update(output_received=delivered['output_received'],native_zip_sha256=delivered['native_zip_sha256'],file_hashes=delivered['file_hashes'],artifact_collection_phase='fixed original grading after solving',grader_same_platform_session=True,condition_valid=not row['external_skill_tools_observed'] and (no_skills or row['target_skill_read_verified']))
        save(f/'result.json',row);return row

    def grade(self,task,folder):
        summary=json.loads((folder/'run_summary.json').read_text())
        if not summary['completed'] or summary['error']:raise RuntimeError('Solver stream incomplete; do not score')
        events=[json.loads(s) for s in (folder/'events.jsonl').read_text().splitlines()]
        ready=[];setup_ids=set()
        for e in events:
            if e.get('type')=='tool_call.in_progress' and e.get('tool_name') not in ['read','bash','awaitbash','skills_read']:
                raise RuntimeError('Unexpected solver tool outside the execution adapter')
            if e.get('type')=='tool_call.in_progress' and e.get('tool_name')=='bash':
                cmd=e['parameters']['command'].strip()
                kind=host_command_kind(cmd)
                if kind=='setup':setup_ids.add(e['tool_call_id'])
                elif kind!='container':
                    raise RuntimeError('Unapproved host shell command: invalid external adapter execution')
            if e.get('type')=='tool_call.result' and e.get('tool_call_id') in setup_ids:
                for text in self.strings(e.get('result')):
                    for line in text.splitlines():
                        if line.startswith('CGL_CASE_READY:'):ready.append(json.loads(line.split(':',1)[1]))
        if len(ready)!=1:raise RuntimeError('No unique actual setup receipt; no grading call started')
        state=ready[0];session=json.loads((folder/'session.json').read_text())
        config=json.loads((folder/'case_config.json').read_text());assert state['input_sha256']==config['input_sha256'] and state['task']==task
        root=folder/'grading-only';root.mkdir(exist_ok=False)
        rows=tracked_files(self.bench.parent,task,'verifier');raw=archive_rows(rows)
        payload=MemoryUpload('original_verifier.tar.gz',raw)
        control={'expected_context':state,'verifier_archive_sha256':sha(raw),'source_hashes':{n:sha(b) for n,b,m in rows},'expects_ctrf':any(n=='test.sh' and b'ctrf' in b for n,b,m in rows)}
        grader=Probe(argparse.Namespace(**{**vars(self.args),'out':str(root),'dev_task':task,'skill_name':self.skill_name,'hard_timeout_sec':1200}))
        files=[payload,MemoryUpload('grade_config.json.gz',gzip.compress(json.dumps(control).encode())),HERE/'remote_grade.py']
        uploads=[grader.transport.upload(p,session['end_user']) for p in files]
        body={'agent':{'id':grader.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],
            'input':'Grading only, no further solving. Run exactly python3 remote_grade.py in one foreground bash call with background=false and timeout1150. Do not edit answers, scripts, config or tests, inspect the hidden verifier, use skills/Memory, purchase anything or ask questions. The script freezes/exports actual files before exposing the original verifier, runs the original test.sh, preserves source hashes and cleans only this case. Return the actual [OUTPUT] outputs/deliverables.zip. Do not rerun scoring.',
            'stream':True,'session_id':session['id'],'attachment_file_ids':[x['file_id'] for x in uploads]}
        delivered=grader.execute(root,'grading-only','original-grading',None,True,body,session['id'],session['end_user'],payload)
        grade_events=[json.loads(s) for s in (root/'events.jsonl').read_text().splitlines()]
        commands=[e['parameters']['command'].strip() for e in grade_events if e.get('type')=='tool_call.in_progress' and e.get('tool_name')=='bash']
        assert commands==['python3 remote_grade.py'],'Grader command changed or repeated'
        assert delivered['output_received'],'Actual grader artifact not received'
        report=json.loads((root/'output/score_receipt.json').read_text())
        save(folder/'ORIGINAL_SCORE.json',report)
        if report.get('infrastructure_error'):raise RuntimeError(report['infrastructure_error'])
        assert report['original_source_before_after_verified']
        return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True);p.add_argument('--task',required=True);p.add_argument('--label',required=True);p.add_argument('--candidate');p.add_argument('--keys-file',required=True);p.add_argument('--allow-paid',action='store_true')
    args=p.parse_args();args.hard_timeout_sec=1600
    study=DockerStudy(args)
    candidate=Path(args.candidate).read_text() if args.candidate else None
    if args.label=='with-CogniLife-skills' and candidate is None:raise ValueError('No evolved candidate supplied; never silently use the original instead')
    row=study.solve(args.label,args.task,candidate,args.label=='no-skills')
    print(json.dumps({'task':args.task,'label':args.label,'score':row['score'],'tokens':row['tokens']},ensure_ascii=False))
