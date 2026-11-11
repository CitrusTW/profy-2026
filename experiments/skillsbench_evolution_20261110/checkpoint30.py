"""Write a reviewable per-round summary; raw third-party material stays local."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path


def checkpoint(root):
    root=Path(root);rounds=[]
    for folder in sorted(p for p in root.glob('round-*') if p.is_dir()):
        record=folder/'ROUND.json'
        state=json.loads(record.read_text()) if record.exists() else {'round':int(folder.name.split('-')[1]),'status':'running'}
        if not record.exists():
            for label in ['development','adaptive-check']:
                p=folder/label/'result.json'
                if p.exists():state[label.replace('-','_')]=json.loads(p.read_text())
        inventory=[]
        for p in sorted(folder.rglob('*')):
            if p.is_file() and not p.is_symlink() and 'node_modules' not in p.parts:
                inventory.append({'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        payload={'state':state,'artifact_hashes':inventory,
                 'raw_artifacts':'Full local round directory; third-party code, skill bodies, inputs, gold and keys excluded from private repo.'}
        if record.exists():
            bundle=root/(folder.name+'-model-outputs.zip')
            with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED) as z:
                attempts=list(folder.glob('*/result.json'))
                confirmation=root/('confirmation-'+folder.name.split('-')[1])
                if confirmation.exists():attempts+=list(confirmation.glob('*/result.json'))
                for result_file in attempts:
                    attempt=result_file.parent;prefix=attempt.relative_to(root).as_posix()
                    for file in (attempt/'output').rglob('*.obj'):
                        z.write(file,prefix+'/'+file.relative_to(attempt).as_posix())
                    for name in ['result.json','usage.json','manifest.json']:
                        if (attempt/name).exists():z.write(attempt/name,prefix+'/'+name)
                z.write(record,'ROUND.json')
            payload['model_outputs_archive']={'file':bundle.name,'bytes':bundle.stat().st_size,
                'sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),
                'contents':'Exact model-generated OBJ bytes plus assistant metadata; no third-party code, original inputs, gold or keys.'}
        (root/(folder.name+'-checkpoint.json')).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
        rounds.append(state)
    lines=['# 最多30轮的实际进度','','停止条件: 总计30轮, 或小范围质量和tokens改善被再次确认. 前3轮已经完成, 本阶段从第4轮开始.','','| 轮次 | 状态 | 开发测试 | 开发tokens | 另一题测试 | 另一题tokens |','| --- | --- | --- | --- | --- | --- |']
    for r in rounds:
        a=r.get('development',{});b=r.get('adaptive_check',{})
        lines.append(f"| {r['round']} | {r['status']} | {a.get('score',{}).get('passed','-')}/{a.get('score',{}).get('tests','-')} | {a.get('tokens',{}).get('total_tokens','-')} | {b.get('score',{}).get('passed','-')}/{b.get('score',{}).get('tests','-')} | {b.get('tokens',{}).get('total_tokens','-')} |")
    lines+=['','保留官方评分, 不转换旧答案回填得分. 兼容保护来自原公开skill已有的序列化约定, 是新增实验约束. 两题均已用于调试, 不作为独立held-out证据. 论文未改.']
    (root/'PROGRESS.md').write_text('\n'.join(lines)+'\n')
    return rounds


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();print(json.dumps([{'round':r['round'],'status':r['status']} for r in checkpoint(a.out)]))
