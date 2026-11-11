"""Inspect saved calls; optionally replay reviewed local solvers. No model/API calls."""
import argparse
import ast
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from pilot import CONDITIONS, INPUTS, SKILL, TEST, exported_file, sha

ALLOWED_IMPORTS={'pathlib','csv','json','re','unicodedata','hashlib','gzip','base64',
                 'decimal','difflib','collections','openpyxl','pypdf','pandas'}


def audit(workspace, result_dir, replay=False):
    workspace=Path(workspace).resolve(); root=Path(result_dir).resolve()
    output=root/'diagnosis_v2'; output.mkdir(exist_ok=True)
    records=[]
    for label in CONDITIONS:
        folder=root/label
        events=[json.loads(x) for x in (folder/'events.jsonl').read_text().splitlines()]
        candidates=[]
        for event in events:
            if event.get('type')!='tool_call.result' or event.get('tool_name')!='bash':
                continue
            message=(event.get('result') or {}).get('message','')
            match=re.search(r"cat > work/analyze_invoices\.py <<'PY'\n(.*?)\nPY",message,re.S)
            if match:
                candidates.append((event,match[1]+'\n'))
        assert len(candidates)==1, 'Expected one reviewed solver per arm'
        event,code=candidates[0]
        tree=ast.parse(code)
        imports={node.module.split('.')[0] for node in ast.walk(tree) if isinstance(node,ast.ImportFrom)}
        imports.update(alias.name.split('.')[0] for node in ast.walk(tree) if isinstance(node,ast.Import) for alias in node.names)
        assert imports <= ALLOWED_IMPORTS, 'Unexpected import; inspect before replay'
        raw=exported_file(events)
        assert raw is not None and raw==(folder/'fraud_report.json').read_bytes()
        final=''.join(e.get('delta') or '' for e in events if e.get('type')=='output.text.delta')
        record={'condition':label,'solver_sha256':sha(code.encode()),'solver_tool_call_id':event['tool_call_id'],
                'solver_native_event_seq':event['seq'],'output_sha256':sha(raw),
                'native_export_matches_local_file':True,'final_text_contains_same_hash':sha(raw) in final,
                'session_sha256':sha(json.loads((folder/'session.json').read_text())['id'].encode()),
                'raw_answer_literal_present_in_solver':raw.decode().strip() in code,
                'imports':sorted(imports)}
        stage=output/'replay'/label
        if replay:
            # These exact three programs were reviewed before enabling this local replay.
            stage.mkdir(parents=True,exist_ok=True)
            (stage/'outputs').mkdir(exist_ok=True); (stage/'work').mkdir(exist_ok=True)
            for name in INPUTS[TEST]:
                shutil.copy2(workspace/'04_项目数据与代码/skillsbench/tasks'/TEST/'environment'/name,stage/name)
            (stage/'solver.py').write_text(code)
            run=subprocess.run([sys.executable,'solver.py'],cwd=stage,capture_output=True,text=True,timeout=120)
            (stage/'stdout.log').write_text(run.stdout); (stage/'stderr.log').write_text(run.stderr)
            assert run.returncode==0, 'Local replay failed for '+label
            generated=stage/'outputs/fraud_report.json'
            assert generated.exists()
            record['local_replay_sha256']=sha(generated.read_bytes())
            record['local_replay_matches_native_output']=generated.read_bytes()==raw
            record['native_style_root_output_created_by_solver']=(stage/'fraud_report.json').exists()
        elif (stage/'solver.py').exists() and (stage/'outputs/fraud_report.json').exists():
            assert (stage/'solver.py').read_text()==code, 'Saved replay source differs'
            generated=stage/'outputs/fraud_report.json'
            record['local_replay_sha256']=sha(generated.read_bytes())
            record['local_replay_matches_native_output']=generated.read_bytes()==raw
            record['native_style_root_output_created_by_solver']=(stage/'fraud_report.json').exists()
            record['replay_record_reused_without_execution']=True
        records.append(record)
    original=(workspace/'04_项目数据与代码/experts/01-财务报销管家'/SKILL).read_bytes()
    updated=(root/'candidate_SKILL.md').read_bytes()
    source=workspace/'04_项目数据与代码/Profy-main/services/agent-runtime/src/plugins/builtin/evolution/tools/evolution_log.py'
    tree=ast.parse(source.read_text()); nodes=[]
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in {'_FOOTPRINT_FULL_SCORE_CHARS','_FOOTPRINT_ZERO_SCORE_CHARS'} for t in node.targets):
            nodes.append(node)
        if isinstance(node,ast.FunctionDef) and node.name=='_context_footprint_score':
            nodes.append(node)
    # Only the reviewed pure scoring function and its two numeric constants.
    namespace={}; exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),namespace)
    footprint={'source_file':str(source.relative_to(workspace)),'source_sha256':sha(source.read_bytes()),
               'score_computed_from_exact_local_source_function':True,
               'original_chars':len(original.decode()),'updated_chars':len(updated.decode()),
               'original_context_footprint_score':namespace['_context_footprint_score'](len(original.decode())),
               'updated_context_footprint_score':namespace['_context_footprint_score'](len(updated.decode())),
               'production_deployment_version_verified':False}
    (output/'ORIGINAL_FOOTPRINT_CHECK.json').write_text(json.dumps(footprint,ensure_ascii=False,indent=2))
    paper=workspace/' naacl 2027 提交版.pdf'
    report={'new_model_calls':0,'network_calls':0,'records':records,
            'distinct_solver_count':len({r['solver_sha256'] for r in records}),
            'distinct_session_count':len({r['session_sha256'] for r in records}),
            'distinct_output_count':len({r['output_sha256'] for r in records}),
            'all_transport_hashes_verified':all(r['native_export_matches_local_file'] and r['final_text_contains_same_hash'] for r in records),
            'all_reviewed_local_replays_match':all(r.get('local_replay_matches_native_output',False) for r in records) if all('local_replay_matches_native_output' in r for r in records) else None,
            'original_skill':{'sha256':sha(original),'utf8_bytes':len(original),'characters':len(original.decode())},
            'updated_skill':{'sha256':sha(updated),'utf8_bytes':len(updated),'characters':len(updated.decode())},
            'submitted_paper':{'filename':paper.name,'sha256':sha(paper.read_bytes()),'method_page':4},
            'original_scorer_or_answers_modified':False}
    (output/'AUDIT_FACTS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='records'},ensure_ascii=False,indent=2))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--workspace',required=True)
    parser.add_argument('--result-dir',required=True)
    parser.add_argument('--replay-reviewed-local-solvers',action='store_true')
    args=parser.parse_args()
    audit(args.workspace,args.result_dir,args.replay_reviewed_local_solvers)
