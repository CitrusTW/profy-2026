"""Serial evaluation only. Never evolve from evaluation questions or results."""
import argparse,hashlib,json
from pathlib import Path
from study import DockerStudy
from run import save

FROZEN='51ca8a2ff044812e60ca830e9951d17219a66c736004edc99729d157f275cf1a'
PARENT='9bdc1fee81f3be9cb34ac49f8890c094a3855d3d0236783d10e0ea6df1515e01'
TASKS=['shock-analysis-demand','shock-analysis-supply','reserves-at-risk-calc','powerlifting-coef-calc','xlsx-recover-data','invoice-fraud-detection','pdf-excel-diff','jpg-ocr-stat']

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ['workspace','out','candidate','keys-file']:p.add_argument('--'+n,required=True)
    p.add_argument('--allow-paid',action='store_true');a=p.parse_args()
    candidate=Path(a.candidate).read_text();assert hashlib.sha256(candidate.encode()).hexdigest()==FROZEN
    root=Path(a.out).resolve();root.mkdir(parents=True,exist_ok=True)
    for task in TASKS:
        folder=root/task;folder.mkdir(exist_ok=True)
        for label in ['no-skills','with-skills','with-CogniLife-skills']:
            result=folder/label/'result.json'
            if result.exists():
                row=json.loads(result.read_text())
                assert row.get('condition_valid') and not row['score'].get('infrastructure_error')
                if label=='with-CogniLife-skills':assert row['skill_sha256']==FROZEN
                continue
            assert not (folder/label/'started.json').exists(),'Interrupted attempt: inspect it before any new solving'
            pins=folder/'FROZEN_APT_PACKAGES.json'
            args=argparse.Namespace(**{**vars(a),'out':str(folder),'task':task,'target_skill':'xlsx','expected_parent_md_sha':PARENT,'native_file_runtime':True,'hard_timeout_sec':1600,'native_package_versions':str(pins) if pins.exists() else None,'expected_input_hashes':None if label=='no-skills' else str(folder/'no-skills/native_input_hashes.json')})
            study=DockerStudy(args)
            row=study.solve(label,task,candidate if label=='with-CogniLife-skills' else None,label=='no-skills')
            assert row['condition_valid'] and row['score']['original_source_before_after_verified']
            if label=='no-skills':save(pins,row['score']['dependency_receipt']['apt_packages'])
            if label=='with-CogniLife-skills':assert row['skill_sha256']==FROZEN
            print('RESULT',json.dumps({'task':task,'group':label,'reward':row['score']['original_reward'],'tokens':row['tokens']['total_tokens']},ensure_ascii=False),flush=True)
        rows=[json.loads((folder/l/'result.json').read_text()) for l in ['no-skills','with-skills','with-CogniLife-skills']]
        save(folder/'THREE_ARM_SUMMARY.json',[{'group':r['label'],'reward':r['score']['original_reward'],'passed':r['score']['passed'],'tests':r['score']['tests'],'tokens':r['tokens']['total_tokens'],'elapsed_sec':r['elapsed_sec'],'condition_valid':r['condition_valid']} for r in rows])
        print('TASK_COMPLETE',task,flush=True)
