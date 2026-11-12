"""Accept an existing grading artifact by its original tool hash, without rerunning tests."""
import argparse,json,re,hashlib
from pathlib import Path
from run import unpack_output,save

def accept(root):
    root=Path(root)
    original=[json.loads(s) for s in (root/'events.jsonl').read_text().splitlines()]
    delivery=[json.loads(s) for s in (root/'delivery-only/events.jsonl').read_text().splitlines()]
    original_calls=[e for e in original if e.get('type')=='tool_call.in_progress']
    delivery_calls=[e for e in delivery if e.get('type')=='tool_call.in_progress']
    assert [(e['tool_name'],e['parameters'].get('command')) for e in original_calls]==[('bash','unzip -o grading_bundle.zip && python3 grade_entry.py')]
    assert [(e['tool_name'],e['parameters'].get('command')) for e in delivery_calls]==[('bash','mkdir -p outputs && cp deliverables.zip outputs/deliverables.zip && sha256sum outputs/deliverables.zip')]
    text=json.dumps([e for e in original if e.get('type')=='tool_call.result'])
    expected=re.findall(r'SBP_NATIVE_ZIP_SHA256:([0-9a-f]{64})',text)[-1]
    raw=(root/'delivery-only/deliverables.zip').read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
    manifest=unpack_output(raw,root/'delivery-only')
    assert manifest['input_sha256']==hashlib.sha256((root/'grading_bundle.zip').read_bytes()).hexdigest()
    receipt=json.loads((root/'delivery-only/output/receipt.json').read_text())
    assert receipt['all_static_hashes_before_after_verified'] and receipt['solver_output_unchanged']
    receipt.update({'native_zip_sha256':expected,'fixed_grading_command_verified':True,'delivery_only_command_verified':True,'grading_reexecuted_for_delivery':False,'separate_grading_session':True})
    save(root/'ACCEPTED_CLOUD_GRADING.json',receipt);return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);args=p.parse_args();print(json.dumps(accept(args.root)))
