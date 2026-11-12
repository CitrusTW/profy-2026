"""Export requested skill versions and provenance; exclude company source, keys and gold."""
import difflib,hashlib,json,re
from pathlib import Path

WORKSPACE=Path(__file__).resolve().parents[3]
BENCH=WORKSPACE/'04_项目数据与代码/skillsbench/tasks'
RUNS=WORKSPACE/'01_任务结果/2026-11-10_skillsbench_evolution'
NETWORK=WORKSPACE/'01_任务结果/2026-11-11_skillsbench_full_library/network-family'
PIN='f860ecf02ef53412a030f8661c83d644b739ff01'

def read(path):return json.loads(path.read_text()) if path.exists() else None
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def export():
    entries=[];index=[]
    def add(path,text):entries.append({'path':path,'mode':'100644','type':'blob','content':text})
    def js(path,data):add(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    families={'threejs':'threejs-to-obj','economic-dispatch':'grid-dispatch-operator','mesh-analysis':'3d-scan-calc'}
    resources={}
    for task in ['threejs-to-obj','grid-dispatch-operator','energy-market-pricing','3d-scan-calc']:
        for source in sorted((BENCH/task/'environment/skills').glob('*/SKILL.md')):
            name=source.parent.name
            add('skills/with-skills/'+name+'/SKILL.md',source.read_text()) if name not in resources else None
            resources[name]={'public_source':'https://github.com/benchflow-ai/skillsbench/tree/'+PIN+'/tasks/'+task+'/environment/skills/'+name,
                'skill_sha256':digest(source),'resources':{p.relative_to(source.parent).as_posix():digest(p) for p in source.parent.rglob('*') if p.is_file() and p.name!='SKILL.md'}}
    js('skills/with-skills/SOURCE_MANIFEST.json',resources)
    js('skills/no-skills/CONDITION.json',{'skill_files':[],'environment_skills':[],'enable_memory':False,'meaning':'No benchmark skill is supplied. There is no SKILL.md for this condition.'})
    candidates=[]
    for p in sorted(RUNS.glob('run-*/evolution/candidate_SKILL.md')):candidates.append(('historical-'+p.parents[1].name,'threejs',p,False))
    for number in range(1,6):
        run='run-03-iterative' if number<=3 else 'run-04-up-to30'
        p=RUNS/run/f'round-{number:02d}/evolution/candidate_SKILL.md'
        candidates.append((f'round-{number:02d}','threejs',p,number==5))
    candidates.append(('round-06','economic-dispatch',NETWORK/'round-06/evolution/candidate_SKILL.md',True))
    cloud=WORKSPACE/'01_任务结果/2026-11-11_skillsbench_cloud_serial/mesh-evolution'
    selected_mesh=None
    for p in sorted(cloud.glob('round-*/evolution/candidate_SKILL.md')):
        state=read(p.parent.parent/'ROUND.json') or {}
        selected=state.get('status')=='small_scope_success_confirmed'
        label=p.parent.parent.name
        candidates.append((label,'mesh-analysis',p,selected))
        if selected:selected_mesh=label
    for label,name,skill,selected in candidates:
        if name=='mesh-analysis':selected=label==selected_mesh
        evo=skill.parent;folder=evo.parent;provenance=read(evo/'provenance.json') or {};summary=read(evo/'summary.json') or {}
        tools=[]
        for response in sorted(evo.glob('response_*.json')):
            data=read(response)
            for choice in data.get('choices',[]):
                for c in choice.get('message',{}).get('tool_calls',[]):
                    a=json.loads(c['function']['arguments']);a.pop('improved_content',None)
                    tools.append({'response_file':response.name,'tool':c['function']['name'],'arguments':a})
        metrics={}
        for phase in ['development','confirmation','adaptive-check']:
            result=read(folder/phase/'result.json')
            if result:metrics[phase]=result
        record={'version':label,'skill':name,'model':summary.get('model'),'selected_current':selected,'candidate_sha256':digest(skill),
            'source_artifact':str(skill.relative_to(WORKSPACE)),'original_public_source':resources[name],
            'provenance':provenance,'evolution_summary':summary,'actual_model_tool_calls':tools,'actual_development_results':metrics,
            'data_boundary':'Original Profy context and DEV histories stay in the workspace. Their request hashes and history counts are in provenance. No keys, company source, evaluation answers or verifier are included.',
            'missing_original_implementations':provenance.get('missing_implementations',summary.get('missing_implementations'))}
        target='skills/evolution-history/'+label
        add(target+'/SKILL.md',skill.read_text());js(target+'/EVOLUTION_RECORD.json',record)
        original=BENCH/families[name]/'environment/skills'/name/'SKILL.md'
        parent=folder/'parent_skills'/name/'SKILL.md'
        if not parent.exists() and digest(original)==provenance.get('parent_sha256'):parent=original
        if parent.exists():
            assert digest(parent)==provenance['parent_sha256']
            add(target+'/changes_from_parent.diff',''.join(difflib.unified_diff(parent.read_text().splitlines(True),skill.read_text().splitlines(True),fromfile='parent/SKILL.md',tofile=label+'/SKILL.md')))
        if selected:add('skills/with-CogniLife-skills/'+name+'/SKILL.md',skill.read_text())
        index.append({'version':label,'skill':name,'model':summary.get('model'),'selected':selected,'sha256':digest(skill),'path':target})
    js('skills/VERSION_INDEX.json',index)
    overrides={'threejs':'round-05','economic-dispatch':'round-06'}
    if selected_mesh:overrides['mesh-analysis']=selected_mesh
    js('skills/with-CogniLife-skills/CONDITION.json',{'base':'../with-skills','overrides':overrides,'other_supplied_skills':'Same original files as with-skills; no unrelated threejs skill is added to other tasks.'})
    add('skills/README.md','''# 三组skills和全部进化版本

| 目录 | 是什么 | 先看什么 |
| --- | --- | --- |
| no-skills/ | 不提供benchmark skills | CONDITION.json, 没有虚构SKILL.md |
| with-skills/ | 已跑任务使用的原版公开skills | 各skill的SKILL.md和SOURCE_MANIFEST.json |
| with-CogniLife-skills/ | 最终采用的进化版 | CONDITION.json逐项记录采用哪轮 |
| evolution-history/ | 全部历史候选, 包括未采用版本 | 每版SKILL.md、EVOLUTION_RECORD.json和可核对的parent diff |

三组配置都在这里. 进化历史保留早期候选和后续各轮候选, 不把旧模型或失败版改名当成最新版. VERSION_INDEX.json列出各版模型、hash和是否采用.

原版非SKILL.md脚本、模板和资源不复制进本repo. SOURCE_MANIFEST.json记录它们在固定公开版本中的来源和hash. 运行时应从该来源取得, 再用进化版SKILL.md覆盖同名文件. 这里不是独立打包好的第三方运行环境.

## 怎么进化

1. Profy的gpt-6.1-sol先完成开发题, 留下真实user/assistant/tool执行记录、得分和tokens.
2. 收到的Profy原代码组装Evolution context、workflow、run_stats和工具. OpenRouter模型通过skill工具读取原skills, 再用evolution_log提出修改. 候选正文来自模型响应, 不是本聊天手写.
3. Profy实际读取候选并重新求解开发题, 用原评分检查. 后续轮次只把开发记录送回Evolution, 不把评测题答案补进去.
4. 开发测试全通过、tokens低于原版, 并再次确认后, 才冻结用于评测. 早期历史版的过程以各自记录为准, 不能把今天的完整适配流程套到旧版上.

第4至5轮新增了公开原skill的输出表示兼容保护, 已在provenance.adapter_contract中标明, 不冒充原方法. 原代码中仍缺少或未接通capability-gap classifier、通用语义适用性检查和native promotion, 不能称完整CogniLife平台复现.

每版EVOLUTION_RECORD.json保存实际模型、调用步骤、parent/candidate/request hash、开发记录数量、模型修改说明和实际得分. 只在能核对parent文件时提供diff, 不补造缺失历史.
''')
    assert len({e['path'] for e in entries})==len(entries)
    assert not re.search(r'\bsk-(?:pro|or)-[A-Za-z0-9._-]{20,}',json.dumps(entries))
    Path('/private/tmp/cgl-skill-archive-entries.json').write_text(json.dumps(entries,ensure_ascii=False))
    print(json.dumps({'files':len(entries),'candidate_versions':len(index),'characters':len(Path('/private/tmp/cgl-skill-archive-entries.json').read_text())}))

if __name__=='__main__':export()
