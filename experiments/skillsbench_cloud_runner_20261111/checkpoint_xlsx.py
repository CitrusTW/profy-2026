"""Small assistant-authored evidence bundle; never copy received program sources or gold."""
import argparse,difflib,hashlib,json,re,zipfile
from pathlib import Path

def checkpoint(folder,out):
    folder=Path(folder).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    label=folder.name;prefix='results/xlsx-family/native-owned-evolution-v2/'+label
    entries=[];inventory=[]
    def add(path,raw):
        assert not re.search(rb'\bsk-(?:pro|or)-[A-Za-z0-9._-]+',raw),'Credential in checkpoint'
        entries.append({'path':path,'mode':'100644','type':'blob','content':raw.decode()})
    for p in sorted(folder.rglob('*')):
        if p.is_file() and not p.is_symlink():inventory.append({'path':p.relative_to(folder).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    bundle=out/(label+'-evidence.zip')
    with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name in ['ROUND.json','STARTED.json','CANDIDATE_CHECK.json','DEV_RESULT_SOURCES.json','VALIDATION_APT_PACKAGES.json']:
            if (folder/name).exists():z.write(folder/name,name)
        evo=folder/'evolution'
        for p in sorted(evo.glob('*')):
            if p.name.startswith('request') or p.name=='provenance.json' or not p.is_file():continue
            if p.suffix in ['.json','.md']:z.write(p,'evolution/'+p.name)
        provenance=evo/'provenance.json'
        if provenance.exists():
            d=json.loads(provenance.read_text());context=d.pop('context',None)
            d['received_context_record']={'sha256':hashlib.sha256(json.dumps(context,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'note':'Received context stays local; no company source copied.'}
            z.writestr('evolution/provenance.json',json.dumps(d,ensure_ascii=False,indent=2))
        for result in sorted(folder.rglob('run_summary.json')):
            phase=result.parent
            if phase.name=='grading-only':continue
            for name in ['result.json','run_summary.json','SOLVER_RESULT_BEFORE_GRADING.json','case_config.json','started.json','usage.json','native_input_hashes.json','events.jsonl','grading-only/output/score_receipt.json','grading-only/output/dependency_receipt.json']:
                p=phase/name
                if p.exists():
                    raw=p.read_bytes();assert not re.search(rb'\bsk-(?:pro|or)-[A-Za-z0-9._-]+',raw)
                    z.writestr(p.relative_to(folder).as_posix(),raw)
            for name in ['gdp.xlsx','protein_expression.xlsx']:
                p=phase/'grading-only/output/fs/root'/name
                if p.exists():z.write(p,p.relative_to(folder).as_posix())
        z.writestr('ARTIFACT_HASHES.json',json.dumps(inventory,indent=2))
    with zipfile.ZipFile(bundle) as z:
        for name in z.namelist():
            if name.endswith(('.json','.jsonl','.md')):
                assert not re.search(rb'\bsk-(?:pro|or)-[A-Za-z0-9._-]+',z.read(name)),'Credential in evidence bundle'
    assert bundle.stat().st_size<30_000_000,'Checkpoint exceeds small evidence budget'
    state_path=folder/'ROUND.json';state=json.loads(state_path.read_text()) if state_path.exists() else {}
    rows={}
    for name in ['development','confirmation','validation','validation_confirmation']:
        r=state.get(name)
        if r:rows[name]={'task':r['task'],'reward':r['score'].get('original_reward'),'passed':r['score'].get('passed'),'tests':r['score'].get('tests'),'tokens':r['tokens']['total_tokens'],'elapsed_sec':r['elapsed_sec'],'condition_valid':r.get('condition_valid')}
    if not state:
        for p in folder.rglob('result.json'):
            if p.parent.name=='grading-only':continue
            r=json.loads(p.read_text())
            if 'score' in r:rows[p.parent.relative_to(folder).as_posix()]={'task':r['task'],'reward':r['score'].get('original_reward'),'passed':r['score'].get('passed'),'tests':r['score'].get('tests'),'tokens':r['tokens']['total_tokens'],'elapsed_sec':r['elapsed_sec'],'condition_valid':r.get('condition_valid')}
    summary={'round':state.get('round'),'status':state.get('status'),'stop_optimization':state.get('stop_optimization'),'evolution_inputs_development_only':state.get('evolution_inputs_development_only'),'validation_used_for_selection':state.get('validation_used_for_selection'),'results':rows,'artifact_hashes':inventory,'bundle_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest()}
    add(prefix+'/CHECKPOINT.json',json.dumps(summary,ensure_ascii=False,indent=2).encode())
    candidate=folder/'evolution/candidate_SKILL.md';parent=folder/'parent_skills/xlsx/SKILL.md'
    if candidate.exists():
        skill_prefix='skills/evolution-history/xlsx/'+label
        add(skill_prefix+'/SKILL.md',candidate.read_bytes())
        if parent.exists():add(skill_prefix+'/changes_from_parent.diff',''.join(difflib.unified_diff(parent.read_text().splitlines(True),candidate.read_text().splitlines(True),fromfile='parent/SKILL.md',tofile=label+'/SKILL.md')).encode())
        add(skill_prefix+'/EVOLUTION_RECORD.json',json.dumps(summary,ensure_ascii=False,indent=2).encode())
        if state.get('status')=='small_scope_success_confirmed':
            add('skills/with-CogniLife-skills/xlsx/SKILL.md',candidate.read_bytes())
            frozen=folder.parent/'FROZEN.json'
            add('skills/with-CogniLife-skills/xlsx/FROZEN.json',frozen.read_bytes())
            description=f"# xlsx skill 怎么进化的\n\n当前采用第{state['round']}轮. Evolution 使用原始组件和 OpenRouter openai/gpt-6.1-sol, 输入仅含 weighted-gdp-calc 开发轨迹. Profy gpt-6.1-sol 解题.\n\n开发题和 protein-expression-analysis 选版验证题都通过原评分, 两次运行均比各自原版至少少5% solver tokens. 验证题答案、轨迹、评分源码及分数未交给 Evolution; 验证题不再算独立新题证据.\n\n每步实际数字与历史候选见 ../../evolution-history/xlsx/{label}/EVOLUTION_RECORD.json. 这仍是已披露缺失原组件的外部适配, 不冒充完整平台复现.\n"
            add('skills/with-CogniLife-skills/xlsx/HOW_EVOLVED.md',description.encode())
    payload={'text_entries':entries,'binary_entries':[{'local_path':str(bundle),'repo_path':prefix+'/evidence.zip'}],'summary':{k:v for k,v in summary.items() if k!='artifact_hashes'}}
    output=out/(label+'-git.json');output.write_text(json.dumps(payload,ensure_ascii=False));return output

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',required=True);p.add_argument('--out',required=True);a=p.parse_args();print(checkpoint(a.folder,a.out))
