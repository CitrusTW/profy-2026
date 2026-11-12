"""Serial received-method evolution plus separate cloud scoring for the existing 3D task."""
import argparse,json,shutil
from pathlib import Path
from cloud_grade_3d import GradingOnly,prepare
from library_tasks import LibraryStudy
from iterate import evidence
from native_evolution import evolve,require_paid
from run import save,sha

TASK='3d-scan-calc'
SKILL='mesh-analysis'

class CloudStudy(LibraryStudy):
    def input_file(self,task):
        assert task==TASK
        return self.workspace/'01_任务结果/2026-11-11_skillsbench_full_library/library-runs/3d-scan-calc/public_environment.tar.gz','public_environment.tar.gz'

    def grade(self,task,folder):
        root=folder/'cloud-grade';root.mkdir(exist_ok=False)
        archive=prepare(self.workspace,root,solver_folder=folder)
        args=argparse.Namespace(**{**vars(self.args),'out':str(root)})
        grader=GradingOnly(args);user='cgl-isolated-cloud-grade'
        upload=grader.transport.upload(archive,user)
        session=grader.transport.api('/v1/sessions',{'agent':grader.transport.expert_id,'title':'Fixed original 3D grading only'},user)['id']
        command='unzip -o grading_bundle.zip && python3 grade_entry.py'
        body={'agent':{'id':grader.transport.expert_id,'model':'gpt-6.1-sol','tools':[]},'rules':[],'environment':{'type':'profy_hosted','skills':[]},'enable_memory':False,'expert_partner':[],
            'input':'Separate scoring only, never solve or author skills. Use one foreground bash call with background=false and timeout600 to run exactly: '+command+'. Do not edit files, use Memory, invoke skills, inspect credentials or ask questions. Return [OUTPUT] outputs/deliverables.zip. If the tool nevertheless starts a background shell, await it until complete, then use foreground bash to touch outputs/deliverables.zip and print its actual SHA256 prefixed SBP_NATIVE_ZIP_SHA256:. Do not rerun grading.',
            'stream':True,'session_id':session,'attachment_file_ids':[upload['file_id']]}
        row=grader.execute(root,'cloud-grading','grading-only',None,True,body,session,user,archive)
        events=[json.loads(s) for s in (root/'events.jsonl').read_text().splitlines()]
        calls=[e for e in events if e.get('type')=='tool_call.in_progress']
        assert all(e['tool_name'] in ['read','bash','awaitbash'] for e in calls)
        commands=[e['parameters']['command'].strip() for e in calls if e['tool_name']=='bash']
        assert commands and commands[0]==command,'Unexpected grader command'
        assert commands.count(command)==1,'Grading repeated unexpectedly'
        for cmd in commands[1:]:
            assert cmd in ['touch outputs/deliverables.zip && printf SBP_NATIVE_ZIP_SHA256: && sha256sum outputs/deliverables.zip','touch outputs/deliverables.zip; printf SBP_NATIVE_ZIP_SHA256:; sha256sum outputs/deliverables.zip'],'Unexpected follow-up command'
        if row['output_received']:
            receipt=json.loads((root/'output/receipt.json').read_text())
        else:
            # Actual fixed-script stdout is retained if the delivery scanner omitted the ZIP.
            receipts=[]
            for event in events:
                if event.get('type')!='tool_call.result':continue
                for text in grader.strings(event.get('result')):
                    for line in text.splitlines():
                        try:value=json.loads(line)
                        except ValueError:continue
                        if isinstance(value,dict) and value.get('grading_context_only'):receipts.append(value)
            assert receipts,'No actual grading receipt returned'
            receipt=receipts[-1]
        assert receipt['all_static_hashes_before_after_verified'] and receipt['solver_output_unchanged']
        receipt.update({'original_source_sha256':json.loads((root/'GRADING_PROVENANCE.json').read_text())['original_verifier_sha256'],'fixed_grader_command_verified':True,'cloud_only':True,'native_artifact_received':row['output_received']})
        save(root/'ACCEPTED_CLOUD_GRADING.json',receipt);return receipt

def valid(row):
    return row['completed'] and row['error'] is None and row['output_received'] and row['target_skill_read_verified'] and not row['external_skill_tools_observed'] and row['score']['strict']==1

def run(args):
    require_paid(args.allow_paid)
    if not 7<=args.round<=30:raise ValueError('Combined round IDs are capped at 30')
    args.task=TASK
    root=Path(args.out).resolve();root.mkdir(parents=True,exist_ok=True)
    study=CloudStudy(args);original=study.target.read_text()
    baseline=study.workspace/'01_任务结果/2026-11-11_skillsbench_full_library/library-runs/3d-scan-calc/with-skills'
    history=[evidence(baseline,original,TASK,'UNSEEN_FULL_LIBRARY')]
    parent=original;best=history[0][2]['tokens']['total_tokens']
    folder=root/f'round-{args.round:02d}'
    if folder.exists():raise ValueError('Never overwrite an existing round')
    folder.mkdir()
    for old in sorted(root.glob('round-*')):
        if old==folder:continue
        skill=old/'evolution/candidate_SKILL.md';result=old/'development/result.json'
        if not skill.exists() or not result.exists():continue
        try:e=evidence(old/'development',skill.read_text(),TASK,'UNSEEN_FULL_LIBRARY')
        except ValueError:continue
        history.append(e)
        if valid(e[2]) and e[2]['tokens']['total_tokens']<best:parent=skill.read_text();best=e[2]['tokens']['total_tokens']
    shutil.copytree(study.target.parent.parent,folder/'parent_skills')
    target=folder/'parent_skills'/SKILL/'SKILL.md';target.write_text(parent)
    state={'round':args.round,'development_task':TASK,'evaluation_role':'Development on this singleton skill task; not unseen generalization','baseline_tokens':history[0][2]['tokens']['total_tokens'],'minimum_token_reduction_fraction':0.05,'evolution_provider':'OpenRouter owner key','solver_provider':'Profy owner key','serial':True,'local_environment_installed':False}
    save(folder/'STARTED.json',state)
    try:
        candidate,summary=evolve(study.workspace,target,folder/'evolution',[h[0] for h in history][-20:],[h[1] for h in history][-20:],study.transport.evolution_key(),study.transport.scrub,allow_paid=True,
            adapter_contract={'origin':'Execution adapter metadata, not a replacement learning prompt','environment':'Attached public skills are files, not native registered skill IDs. Use only the supplied packages and ordinary file tools.','data_boundary':'Only DEV trajectories and measured run_stats. No verifier, gold, scoring-context history or unseen evaluation answers.'})
    except Exception as exc:
        state.update(status='evolution_exception',error_type=type(exc).__name__,error=study.transport.scrub(str(exc)),requests_started=len(list((folder/'evolution').glob('request_*.json'))),responses_received=len(list((folder/'evolution').glob('response_*.json'))),candidate_available=False,missing_response_usage_unknown=True)
        save(folder/'ROUND.json',state);return
    state['evolution']=summary
    if candidate is None:state['status']='no_proposal';save(folder/'ROUND.json',state);return
    fresh=CloudStudy(argparse.Namespace(**{**vars(args),'out':str(folder)}))
    dev=fresh.solve('development',TASK,candidate);state['development']=dev
    success=False
    if valid(dev) and dev['tokens']['total_tokens']<=0.95*state['baseline_tokens']:
        confirm=fresh.solve('confirmation',TASK,candidate);state['confirmation']=confirm
        success=valid(confirm) and confirm['tokens']['total_tokens']<=0.95*state['baseline_tokens']
    state['status']='small_scope_success_confirmed' if success else 'development_not_improved';state['stop_optimization']=success or args.round==30
    save(folder/'ROUND.json',state);print(json.dumps({'round':args.round,'status':state['status']}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True);p.add_argument('--keys-file',required=True);p.add_argument('--round',required=True,type=int);p.add_argument('--allow-paid',action='store_true');run(p.parse_args())
