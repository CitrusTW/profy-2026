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
    summary={'round':state.get('round'),'status':state.get('status'),'stop_optimization':state.get('stop_optimization'),'evolution_inputs_development_only':state.get('evolution_inputs_development_only'),'validation_used_for_selection':state.get('validation_used_for_selection'),'parent_sha256':state.get('parent_sha256'),'evolution_model':state.get('evolution',{}).get('wire_model'),'missing_implementations':state.get('evolution',{}).get('missing_implementations'),'results':rows,'artifact_hashes':inventory,'bundle_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest()}
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
    if state.get('round'):
        lines=['# xlsx 第12到30轮的实际进度','','只把开发题记录交给 Evolution. 蛋白题用于选版, 不再算独立新题证据. 两题均须原评分全过, 且两次都比原版至少少5% tokens, 才采用. 未运行的格子写 -, 不记作0分.','','每格依次写通过的检查数 / 总检查数, solver tokens. 开发题是 weighted-gdp-calc, 蛋白题是 protein-expression-analysis.','','| 轮次 | 开发第1次 | 开发第2次 | 蛋白第1次 | 蛋白第2次 | 状态 |','| --- | --- | --- | --- | --- | --- |']
        for p in sorted(folder.parent.glob('round-*/ROUND.json')):
            r=json.loads(p.read_text());cells=[]
            for phase in ['development','confirmation','validation','validation_confirmation']:
                row=r.get(phase)
                cells.append(str(row['score']['passed'])+'/'+str(row['score']['tests'])+', '+str(row['tokens']['total_tokens']) if row else '-')
            human={'small_scope_success_confirmed':'通过, 已采用','validation_not_improved':'验证未达门槛, 未采用','development_not_improved':'开发检查未达门槛, 未采用','no_proposal':'没有候选','exception':'运行错误, 待查'}.get(r.get('status'),r.get('status','未完成'))
            version='round-'+str(r['round']).zfill(2)
            lines.append('| '+str(r['round'])+' | '+' | '.join(cells)+' | '+human+' [证据]('+version+'/evidence.zip) |')
        lines+=['','每轮完整候选和 parent diff 在 skills/evolution-history/xlsx/ 对应轮次. 实际 Excel、逐步求解记录、模型回复和原评分在对应 round-XX/evidence.zip. 原始请求及收到的公司程序不复制进 Git, 只记录指纹. 论文未改.']
        add('results/xlsx-family/native-owned-evolution-v2/PROGRESS.md','\n'.join(lines).encode())
    add('experiments/skillsbench_cloud_runner_20261111/checkpoint_xlsx.py',Path(__file__).read_bytes())
    payload={'text_entries':entries,'binary_entries':[{'local_path':str(bundle),'repo_path':prefix+'/evidence.zip'}],'summary':{k:v for k,v in summary.items() if k!='artifact_hashes'}}
    output=out/(label+'-git.json');output.write_text(json.dumps(payload,ensure_ascii=False));return output

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',required=True);p.add_argument('--out',required=True);a=p.parse_args();print(checkpoint(a.folder,a.out))
