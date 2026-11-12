"""One serial DEV round using received Evolution components; no verifier feedback or new learning prompt."""
import argparse,json,shutil
from pathlib import Path
from study import DockerStudy
from native_evolution import evolve,require_paid,yaml_module
from candidate_check import check_candidate
from iterate import evidence
from run import save,sha

def valid(row,task):
    score=row.get('score',{})
    return (row.get('task')==task and row.get('completed') and row.get('error') is None
            and row.get('output_received') and row.get('target_skill_read_verified')
            and row.get('condition_valid') and not row.get('external_skill_tools_observed')
            and score.get('strict')==1 and (score.get('tests') or 0)>0
            and score.get('passed')==score.get('tests') and score.get('failed')==0
            and score.get('skipped')==0 and score.get('original_source_before_after_verified'))

def improved(row,baseline,task):
    if not valid(row,task):return False
    return baseline['score']['strict']<1 or row['tokens']['total_tokens']<=.95*baseline['tokens']['total_tokens']

def run(args):
    require_paid(args.allow_paid)
    assert 10<=args.round<=30,'Global rounds1..9 already recorded; no round beyond30'
    root=Path(args.out).resolve();root.mkdir(parents=True,exist_ok=True)
    folder=root/f'round-{args.round:02d}';folder.mkdir(exist_ok=False)
    study=DockerStudy(args);original=study.target.read_text()
    baseline_folder=Path(args.baseline).resolve()
    histories=[evidence(baseline_folder,original,args.task,'UNSEEN_FULL_LIBRARY')]
    baseline=histories[0][2];parent=original;parent_result=baseline;parent_folder=baseline_folder
    for old in sorted(root.glob('round-*')):
        candidate=old/'evolution/candidate_SKILL.md';dev=old/'development/with-CogniLife-skills'
        if not candidate.exists() or not (dev/'result.json').exists():continue
        item=evidence(dev,candidate.read_text(),args.task,'UNSEEN_FULL_LIBRARY');histories.append(item)
        if valid(item[2],args.task) and (not valid(parent_result,args.task) or item[2]['tokens']['total_tokens']<parent_result['tokens']['total_tokens']):
            parent=candidate.read_text();parent_result=item[2];parent_folder=dev
    resources=list(study.target.parent.rglob('*'))
    assert sum(p.stat().st_size for p in resources if p.is_file())<=5_000_000,'Avoid copying a large local skill package'
    target=folder/'parent_skills'/study.skill_name/'SKILL.md'
    shutil.copytree(study.target.parent,target.parent);target.write_text(parent)
    state={'round':args.round,'task':args.task,'development_only':True,'serial':True,'baseline_folder':str(baseline_folder),'parent_execution_folder':str(parent_folder),'parent_sha256':sha(parent.encode()),'evolution_provider':'OpenRouter owner key','solver_provider':'Profy owner key','minimum_token_reduction_fraction':.05,'threshold_is_external_safeguard':True,'hidden_verifier_feedback_used':False}
    save(folder/'STARTED.json',state)
    try:
        candidate,summary=evolve(study.workspace,target,folder/'evolution',[x[0] for x in histories][-20:],[x[1] for x in histories][-20:],study.transport.evolution_key(),study.transport.scrub,allow_paid=True,
            adapter_contract={'origin':'Execution metadata, not a replacement learning prompt','environment':'Original public task runs inside its own cloud container. Supplied skills and their unchanged resources are attached files, not native registered skill IDs.','data_boundary':'Only complete DEV solving records and scalar run_stats. No grader-context history, verifier, gold, unseen task outputs, or validation-answer-derived rules.'})
        state['evolution']=summary
        if candidate is None:
            state['status']='no_proposal';return
        if sha(candidate.encode()) in [sha(original.encode()),sha(parent.encode())]:
            state['status']='unchanged_or_original_candidate';return
        header=candidate.split('---',2)
        meta=yaml_module().safe_load(header[1]) if len(header)==3 and not header[0].strip() else {}
        if not isinstance(meta,dict) or meta.get('name')!=study.skill_name or not meta.get('description'):
            state['status']='invalid_candidate_frontmatter';return
        dev_study=DockerStudy(argparse.Namespace(**{**vars(args),'out':str(folder/'development')}))
        dev=dev_study.solve('with-CogniLife-skills',args.task,candidate)
        save(folder/'dev_original/result.json',parent_result);save(folder/'dev_candidate/result.json',dev)
        save(folder/'DEV_RESULT_SOURCES.json',{'dev_original':str(parent_folder/'result.json'),'dev_candidate':str(folder/'development/with-CogniLife-skills/result.json'),'copied_rows_are_unchanged':True})
        checked=check_candidate(folder,target,args.task);save(folder/'CANDIDATE_CHECK.json',checked)
        state['development']=dev;success=False
        if checked['structural_and_dev_pass'] and improved(dev,baseline,args.task):
            confirmation=DockerStudy(argparse.Namespace(**{**vars(args),'out':str(folder/'confirmation')})).solve('with-CogniLife-skills',args.task,candidate)
            state['confirmation']=confirmation;success=improved(confirmation,baseline,args.task)
        state.update(status='small_scope_success_confirmed' if success else 'development_not_improved',stop_optimization=success or args.round==30)
        if success:
            (root/'SELECTED_SKILL.md').write_text(candidate)
            save(root/'FROZEN.json',{'round':args.round,'task':args.task,'skill_sha256':sha(candidate.encode()),'selection_uses_development_only':True,'native_promoted':False,'semantic_applicability_verified':False,'missing_implementations':summary['missing_implementations']})
    except Exception as exc:
        state.update(status='exception',error_type=type(exc).__name__,error=study.transport.scrub(str(exc)),candidate_available=(folder/'evolution/candidate_SKILL.md').exists())
        raise
    finally:
        save(folder/'ROUND.json',state)
        print(json.dumps({'round':args.round,'status':state.get('status'),'stop_optimization':state.get('stop_optimization',False)}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['workspace','out','task','baseline','keys-file']:p.add_argument('--'+name,required=True)
    p.add_argument('--prebuilt-record');p.add_argument('--native-file-runtime',action='store_true');p.add_argument('--native-package-versions');
    p.add_argument('--round',type=int,required=True);p.add_argument('--allow-paid',action='store_true');a=p.parse_args();a.hard_timeout_sec=1600;run(a)
