"""Exercise the received gate function locally. No models, network or copied source."""
import argparse
import ast
import asyncio
import hashlib
import json
import os
import typing
from pathlib import Path
from types import SimpleNamespace


class NullLog:
    def __getattr__(self,name):
        return lambda *args,**kwargs:None


class CaptureStore:
    def __init__(self):
        self.rows=[]

    async def create_evolution_suggestion(self,**kwargs):
        self.rows.append(kwargs)
        return 'local-fixture-'+str(len(self.rows))


class FileSkill:
    def get_enabled_skill_metas(self):
        return [SimpleNamespace(name='expert/xlsx')]

    async def fetch_skill_content(self,**kwargs):
        return SimpleNamespace(content='x'*4000)


async def check(workspace,output):
    workspace=Path(workspace).resolve(); output=Path(output)
    source=workspace/'04_项目数据与代码/Profy-main/services/agent-runtime/src/plugins/builtin/evolution/tools/evolution_log.py'
    tree=ast.parse(source.read_text())
    selected=[]
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            node.decorator_list=[]
            selected.append(node)
        elif isinstance(node,ast.Assign):
            selected.append(node)
    store=CaptureStore()
    # Replace only framework decoration and remote storage. Gate bodies stay original.
    namespace={'os':os,'Literal':typing.Literal,'RunnableConfig':dict,'logger':NullLog(),
               'get_core_client':lambda:store}
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(source),'exec'),namespace)
    assert namespace['_active_rubric']()=='quality_eff', 'Unexpected rubric; do not silently override it'
    dimensions=list(namespace['QUALITY_DIMENSIONS'])+['step_economy','exploration_replacement']
    baseline={name:50 for name in dimensions}
    config={'configurable':{'expert_identifier':'fixture-expert','user_id':'fixture-owner','skill_context':FileSkill()}}
    cases=[]
    async def one(name,after,expected_accept,content='y'*4000,skill_name='xlsx'):
        count=len(store.rows)
        message=await namespace['evolution_log'](action='suggest_skill_improvement',skill_name=skill_name,
             summary='Local fixture',diff_summary='Local fixture only',improved_content=content,
             before_scores=dict(baseline),after_scores=after,improved_dimensions='step_economy',config=config)
        accepted=len(store.rows)>count
        assert accepted==expected_accept,(name,message)
        cases.append({'case':name,'expected_accept':expected_accept,'actual_accept':accepted,'pass':True,'message':message})
    improved=dict(baseline,step_economy=90)
    await one('quality_same_efficiency_increases',improved,True)
    await one('quality_drops_even_with_efficiency_gain',dict(improved,workflow_clarity=0),False)
    await one('quality_improves_but_efficiency_flat',dict(baseline,workflow_clarity=90),False)
    await one('all_scores_flat',dict(baseline),False)
    await one('missing_score_dimension',{},False)
    await one('non_expert_target',improved,False,skill_name='not-owned')
    await one('qualified_name_rejected',improved,False,skill_name='expert/xlsx')
    await one('model_cannot_fake_document_footprint',dict(baseline,context_footprint=100),False,content='y'*30000)
    registry=workspace/'04_项目数据与代码/Profy-main/services/agent-runtime/src/plugins/registry.py'
    t=ast.parse(registry.read_text())
    fn=next(n for c in t.body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name=='_check_activation')
    env={'PluginManifest':object,'ActivationContext':object}
    exec(compile(ast.Module(body=[fn],type_ignores=[]),str(registry),'exec'),env)
    manifest=SimpleNamespace(id='profy-evolution',activation=SimpleNamespace(user_selectable=False,requires={'is_internal_invoke':True},conditions={}))
    for internal in [False,True]:
        ctx=SimpleNamespace(is_internal_invoke=internal,enabled_plugins=['profy-evolution'])
        active=env['_check_activation'](None,manifest,ctx)
        assert active==internal
        cases.append({'case':'evolution_activation_internal_'+str(internal),'expected_active':internal,'actual_active':active,'pass':True})
    report={'status':'offline_source_checks_passed','new_model_calls':0,'network_calls':0,
            'test_count':len(cases),'passed':sum(c['pass'] for c in cases),'cases':cases,
            'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'registry_sha256':hashlib.sha256(registry.read_bytes()).hexdigest(),
            'limits':'Local fixture only. No real candidate, real expert state, production authentication, authority, promotion or benchmark effectiveness tested.'}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:report[k] for k in ['status','new_model_calls','test_count','passed']}))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--workspace',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    asyncio.run(check(args.workspace,args.output))
