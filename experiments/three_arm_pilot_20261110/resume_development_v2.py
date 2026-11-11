"""Finish the same v2 run after a pre-test, development-only correction."""
import argparse
import concurrent.futures
import json
import shutil
from pathlib import Path
from pilot import CONDITIONS, DEV, SKILL, TEST, Pilot, proposal_gate, save, sha


def resume(args):
    pilot=Pilot(args)
    out=pilot.out
    protocol=json.loads((out/'protocol.json').read_text())
    assert protocol['protocol_version']==2
    assert (out/'dev_before/result.json').exists() and (out/'dev_candidate/result.json').exists()
    assert not (out/'development_resume_started.json').exists(), 'Do not resume twice'
    for condition in CONDITIONS:
        folder=out/condition
        assert not (folder/'request.json').exists(), 'A test model request already exists; do not rerun it'
        if folder.exists():
            cancelled=out/'cancelled_before_model_request'; cancelled.mkdir(exist_ok=True)
            shutil.move(str(folder),str(cancelled/condition))
    save(out/'development_resume_started.json',{'reason':'First candidate contained development-only employee terminology and output filename; rejected before test model calls.',
         'baseline_reused':True,'max_total_profy_invocations':6,'max_total_writer_invocations':2})
    shutil.copy2(out/'protocol.json',out/'protocol_before_development_correction.json')
    shutil.copy2(out/'candidate_SKILL.md',out/'discarded_candidate_SKILL.md')
    if (out/'frozen_test_configuration.json').exists():
        shutil.move(str(out/'frozen_test_configuration.json'),str(out/'discarded_frozen_configuration.json'))
    if (out/'gate.json').exists(): shutil.copy2(out/'gate.json',out/'discarded_gate.json')
    pilot.reservations=2
    pilot.max_profy_invocations=6
    protocol.update({'driver_sha256':sha(Path(__file__).with_name('pilot.py').read_bytes()),
                     'initial_source_commit':'0d9d8754e1f3bb7681ddea85a0cbbc5d489269c2',
                     'resume_driver_sha256':sha(Path(__file__).read_bytes()),'max_profy_invocations':6,
                     'development_correction':'Reject development filenames and employee/HR-specific workflow before test. Reuse initial development; one additional candidate validation allowed. Test feedback not supplied to updater.'})
    save(out/'protocol.json',protocol)
    before=json.loads((out/'dev_before/result.json').read_text())
    experience=json.loads((out/'development_experience.json').read_text())
    old=(pilot.expert/SKILL).read_text()
    candidate=pilot.propose(before,old,experience,start_attempt=2)
    after=pilot.solve('dev_candidate_revised',DEV,candidate)
    gate=proposal_gate(before['score'],after['score'],old,candidate)
    gate['initial_skill_read_verified']=before.get('active_skill_evidence',{}).get('verified',False)
    gate['updated_skill_read_verified']=after.get('active_skill_evidence',{}).get('verified',False)
    gate['accepted']=gate['accepted'] and gate['initial_skill_read_verified'] and gate['updated_skill_read_verified']
    save(out/'gate.json',gate)
    summary={'protocol':protocol,'gate':gate,'development_before':before,'development_candidate':after,
             'discarded_development_attempt':'dev_candidate','test_results':[],
             'scope':'One initial development task, one discarded development candidate, one corrected candidate, one previously seen test task. New prototype; no native evolution or cross-expert claim.'}
    if gate['accepted']:
        save(out/'frozen_test_configuration.json',{'candidate_accepted':True,'active_skill_sha256':sha(candidate.encode()),
             'original_skill_sha256':sha(old.encode()),'experience_sha256':sha((out/'development_experience.json').read_bytes()),
             'test_answers_or_scores_used_for_update':False})
        def one(condition):
            return pilot.solve(condition,TEST,candidate if condition==CONDITIONS[2] else None,
                               experience=experience,use_expert=condition!=CONDITIONS[0])
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            pending={pool.submit(one,c):c for c in CONDITIONS}
            for future in concurrent.futures.as_completed(pending):
                try: summary['test_results'].append(future.result())
                except Exception as exc:
                    summary['test_results'].append({'label':pending[future],'error_type':type(exc).__name__,
                                                    'score':{'strict':0,'status':'failed_attempt'}})
        summary['test_results'].sort(key=lambda r:CONDITIONS.index(r['label']))
    else:
        summary['status']='stopped_before_heldout_test'
    summary['profy_model_invocations_reserved']=pilot.reservations
    save(out/'summary.json',summary)
    print('RESUMED_PILOT_FINISHED',json.dumps({'gate':gate,'scores':[{k:r.get(k) for k in ['label','score','elapsed_sec']} for r in summary['test_results']]}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--workspace',required=True)
    parser.add_argument('--out',required=True)
    parser.add_argument('--dev-inputs',required=True)
    parser.add_argument('--keys-file',required=True)
    resume(parser.parse_args())
