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
    validation_path=getattr(args,'validation_baseline',None)
    validation_folder=Path(validation_path).resolve() if validation_path else None
    validation_baseline=json.loads((validation_folder/'result.json').read_text()) if validation_folder else None
    excluded_task=validation_baseline['task'] if validation_baseline else 'UNSEEN_FULL_LIBRARY'
    if validation_baseline:
        assert excluded_task!=args.task and valid(validation_baseline,excluded_task),'Validation baseline must be complete and separate from DEV'
        a=json.loads((baseline_folder/'case_config.json').read_text())['skill_hashes']
        b=json.loads((validation_folder/'case_config.json').read_text())['skill_hashes']
        prefix='bench_skills/'+study.skill_name+'/'
        assert {k:v for k,v in a.items() if k.startswith(prefix)}=={k:v for k,v in b.items() if k.startswith(prefix)},'Validation target resources differ'
    histories=[evidence(baseline_folder,original,args.task,excluded_task)]
    baseline=histories[0][2];parent=original;parent_result=baseline;parent_folder=baseline_folder
    seed_path=getattr(args,'seed',None)
    if seed_path:
        seed=Path(seed_path).resolve();text=(seed/'SKILL.md').read_text()
        item=evidence(seed/'with-CogniLife-skills',text,args.task,excluded_task);histories.append(item)
        if valid(item[2],args.task) and item[2]['tokens']['total_tokens']<parent_result['tokens']['total_tokens']:
            parent=text;parent_result=item[2];parent_folder=seed/'with-CogniLife-skills'
    for old in sorted(root.glob('round-*')):
        candidate=old/'evolution/candidate_SKILL.md';dev=old/'development/with-CogniLife-skills'
        if not candidate.exists() or not (dev/'result.json').exists():continue
        item=evidence(dev,candidate.read_text(),args.task,excluded_task);histories.append(item)
        if valid(item[2],args.task) and (not valid(parent_result,args.task) or item[2]['tokens']['total_tokens']<parent_result['tokens']['total_tokens']):
            parent=candidate.read_text();parent_result=item[2];parent_folder=dev
    resources=list(study.target.parent.rglob('*'))
    assert sum(p.stat().st_size for p in resources if p.is_file())<=5_000_000,'Avoid copying a large local skill package'
    target=folder/'parent_skills'/study.skill_name/'SKILL.md'
    shutil.copytree(study.target.parent,target.parent);target.write_text(parent)
    state={'round':args.round,'task':args.task,'evolution_inputs_development_only':True,'validation_used_for_selection':bool(validation_baseline),'validation_task':excluded_task if validation_baseline else None,'validation_baseline_folder':str(validation_folder) if validation_folder else None,'serial':True,'baseline_folder':str(baseline_folder),'parent_execution_folder':str(parent_folder),'parent_sha256':sha(parent.encode()),'evolution_provider':'OpenRouter owner key','solver_provider':'Profy owner key','minimum_token_reduction_fraction':.05,'threshold_is_external_safeguard':True,'hidden_verifier_feedback_used':False}
    save(folder/'STARTED.json',state)
    try:
        candidate,summary=evolve(study.workspace,target,folder/'evolution',[x[0] for x in histories][-20:],[x[1] for x in histories][-20:],study.transport.evolution_key(),study.transport.scrub,allow_paid=True,
            adapter_contract={'origin':'Execution metadata, not a replacement learning prompt','environment':'Current runtime is native-owned Profy Linux uid1000, not Docker or PRoot. Logical /root and /app paths map to owned task directories. Commands run from the mapped task cwd. Supplied skills and unchanged resources are attached files, not native registered skill IDs. Historical PRoot failures do not describe this runtime.','data_boundary':'Only complete DEV solving records and DEV scalar run_stats. No validation trajectories, validation answers, validation scores, grader-context history, verifier, gold, or unseen task outputs.'})
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
        if success and validation_baseline:
            pins=folder/'VALIDATION_APT_PACKAGES.json'
            save(pins,validation_baseline['score']['dependency_receipt']['apt_packages'])
            validation_args={**vars(args),'task':excluded_task,'target_skill':study.skill_name,'expected_parent_md_sha':sha(original.encode()),'native_package_versions':str(pins),'expected_input_hashes':str(validation_folder/'native_input_hashes.json')}
            first=DockerStudy(argparse.Namespace(**{**validation_args,'out':str(folder/'validation')})).solve('with-CogniLife-skills',excluded_task,candidate)
            state['validation']=first;success=improved(first,validation_baseline,excluded_task)
            if success:
                second=DockerStudy(argparse.Namespace(**{**validation_args,'out':str(folder/'validation-confirmation')})).solve('with-CogniLife-skills',excluded_task,candidate)
                state['validation_confirmation']=second;success=improved(second,validation_baseline,excluded_task)
            state['validation_failed_selection']=not success
        state.update(status='small_scope_success_confirmed' if success else 'development_not_improved',stop_optimization=success or args.round==30)
        if state.get('validation_failed_selection'):state['status']='validation_not_improved'
        if success:
            (root/'SELECTED_SKILL.md').write_text(candidate)
            save(root/'FROZEN.json',{'round':args.round,'task':args.task,'skill_sha256':sha(candidate.encode()),'selection_uses_development_only':not bool(validation_baseline),'validation_task':excluded_task if validation_baseline else None,'validation_is_not_independent_test_evidence':bool(validation_baseline),'native_promoted':False,'semantic_applicability_verified':False,'missing_implementations':summary['missing_implementations']})
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
    p.add_argument('--seed');p.add_argument('--validation-baseline')
    p.add_argument('--round',type=int,required=True);p.add_argument('--allow-paid',action='store_true');a=p.parse_args();a.hard_timeout_sec=1600;run(a)
