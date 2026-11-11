"""Repair file extraction from already saved events. No credentials or network."""
import argparse
import json
import shutil
from pathlib import Path
from pilot import CONDITIONS, TEST, OUTPUTS, Pilot, exported_file, save, sha, tool_calls

def recover(workspace, output):
    root = Path(output).resolve()
    summary_file = root/'summary.json'
    original = root/'summary_initial_decoder_failure.json'
    if not original.exists():
        shutil.copy2(summary_file,original)
    summary = json.loads(original.read_text())
    grader = Pilot.__new__(Pilot)
    grader.bench = Path(workspace).resolve()/'04_项目数据与代码/skillsbench/tasks'
    results = []
    for condition in CONDITIONS:
        folder = root/condition
        events = [json.loads(line) for line in (folder/'events.jsonl').read_text().splitlines()]
        raw = exported_file(events)
        if raw is None:
            raise ValueError('No verified bash export for '+condition)
        (folder/OUTPUTS[TEST]).write_bytes(raw)
        completed = any(e.get('type') == 'run.completed' for e in events)
        names = tool_calls(events)
        stamps = [e['timestamp_ms'] for e in events if isinstance(e.get('timestamp_ms'),(int,float))]
        result = {'label':condition,'task':TEST,'completed':completed,'error':None,
                  'elapsed_sec':round((max(stamps)-min(stamps))/1000,3),
                  'timing_basis':'native event span; excludes upload',
                  'output_received':True,'output_sha256':sha(raw),'tool_names':names,
                  'platform_skill_tool_observed':any('skill' in n.lower() for n in names),
                  'money_usd':None,'model_rerun':False,
                  'recovery':'Only this attempt bash exports; exclude prior packet embedded in development-experience read; verify final stated SHA256'}
        result['score'] = grader.grade(folder,TEST)
        save(folder/'result.json',result)
        results.append(result)
    summary['test_results'] = results
    summary['postprocessing_recovery'] = {'new_model_calls':0,'original_summary_preserved':original.name,
          'cause':'Previous experience contained an older export packet, which the original decoder mixed with current output.',
          'answer_or_grading_assertions_changed':False}
    save(summary_file,summary)
    print(json.dumps([{'label':r['label'],'score':r['score'],'elapsed_sec':r['elapsed_sec'],'sha256':r['output_sha256']} for r in results],indent=2))

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--workspace',required=True)
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    recover(args.workspace,args.out)
