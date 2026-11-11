"""Validate and report the frozen two-task comparison without replacing scores."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from continue30 import contract_check


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def report(root):
    root=Path(root);full=root/'full-compatible-two'
    data=json.loads((full/'FULL_TWO_RESULTS.json').read_text());rows=data['rows']
    assert len(rows)==6
    assert {(r['task'],r['label']) for r in rows}=={
        (task,label) for task in ['threejs-to-obj','threejs-structure-parser']
        for label in ['no-skills','with-skills','with-CogniLife-skills']}
    frozen=json.loads((full/'FROZEN.json').read_text());aggregates={}
    for row in rows:
        folder=full/row['task']/row['label']
        assert row==json.loads((folder/'result.json').read_text())
        assert sha(folder/'deliverables.zip')==row['native_zip_sha256']
        for name,expected in row['file_hashes'].items():assert sha(folder/name)==expected
        if row['label']=='with-CogniLife-skills':
            assert row['skill_sha256']==frozen['skill_sha256'] and row['target_skill_read_verified']
            assert contract_check(folder)['passed']
        agg=aggregates.setdefault(row['label'],{'tokens':0,'seconds':0,'tasks_passed':0})
        agg['tokens']+=row['tokens']['total_tokens'];agg['seconds']+=row['elapsed_sec'];agg['tasks_passed']+=row['score']['strict']
    for task in sorted({r['task'] for r in rows}):
        packs=[json.loads((full/task/label/'supplied_skill_hashes.json').read_text()) for label in ['with-skills','with-CogniLife-skills']]
        assert packs[0].keys()==packs[1].keys()
        assert [k for k in packs[0] if packs[0][k]!=packs[1][k]]==['bench_skills/threejs/SKILL.md']
    base=aggregates['with-skills'];candidate=aggregates['with-CogniLife-skills']
    passed=candidate['tasks_passed']==2 and candidate['tasks_passed']>=base['tasks_passed'] and candidate['tokens']<base['tokens']
    cost=sum(u.get('cost',0) for p in root.glob('round-*/evolution/summary.json') for u in json.loads(p.read_text())['usage'])
    result={'completion_date':'2026-11-11','timezone':'America/Los_Angeles','scope':'all two tasks compatible with this threejs skill, not all 87 SkillsBench tasks',
        'rows':rows,'aggregates':aggregates,'frozen':frozen,'full_comparison_goal_met':passed,
        'aggregate_token_change_pct':100*(candidate['tokens']/base['tokens']-1),
        'evolution_cost_usd_rounds_4_5':cost,'profy_dollar_cost':None,
        'method_variant':'Received original Evolution core plus explicit new compatibility protection, empirical iteration/selection/confirmation.',
        'evaluation_limit':'Both tasks used during development; frozen in-sample comparison, not independent generalization or complete original CogniLife reproduction.',
        'old_scores_unchanged':True,'paper_changed':False,'native_promotion_called':False}
    (full/'FINAL_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    lines=['# 第5轮冻结版本的两题三组完整对照','','2026-11-11完成. 这里的完整范围是同一threejs skill全部2道配套题, 不是SkillsBench全库87题. 共6次新Profy求解, 全部使用gpt-6.1-sol标签, 原评分程序不改, 没有输出后处理补分.','','| 任务 | 组别 | 原测试通过数 | reported tokens | 耗时(秒) |','| --- | --- | --- | --- | --- |']
    for task in ['threejs-to-obj','threejs-structure-parser']:
        for label in ['no-skills','with-skills','with-CogniLife-skills']:
            r=next(x for x in rows if x['task']==task and x['label']==label);s=r['score']
            lines.append(f"| {task} | {label} | {s['passed']}/{s['tests']} | {r['tokens']['total_tokens']} | {r['elapsed_sec']} |")
    lines+=['',f"原版两题合计{base['tokens']} tokens, 进化版{candidate['tokens']} tokens, 本次合计减少{100*(1-candidate['tokens']/base['tokens']):.2f}%. 两组均两题全部原测试通过. 每题3项检查, 不是每组3道题或全库准确率.",'',
            '收益不均匀: 单OBJ题tokens少约26.7%, 分部件题反而多约18.2%. 不能写成每项任务都更省. 本次只支持这两个已用于开发的任务上的观察, 不支持稳定收益、显著性或独立泛化结论. 汇总耗时也仅列实际观察, 不替代token指标.', '',
            f'第4至5轮Evolution实际返回美元费用共${cost:.6f}. Profy未提供美元账单, 不能给出完整实验美元总费用, 也不能把执行tokens的降幅当成完整实验费用降幅. 生成和调试成本不包含在上面的单次执行tokens比较里.', '',
            '停止决定: 第5轮小范围两题均3/3, 两次合计tokens均低于预定原版基线; 冻结后两题三组对照也保住质量和合计tokens优势, 因此在第5轮停止, 不继续烧到30轮. 若后续扩展其他skills/任务, 属于另外的范围.', '',
            '兼容保护明确属于本实验新增: 保留原公开skill原本的non-indexed输出惯例. 旧1/3官方分数不改, 但它已被离线定位为等价OBJ表示与原verifier抽样交互, 不能直接解释为几何失败. 新运行由模型重新生成并导出, 不转换旧答案刷分.', '',
            '原workflow、门控、run_stats模型和渲染仍从收到的Profy源码调用. 通用语义适用性检查、capability-gap classifier和native creator accept/promotion没有完成, 不能称完整CogniLife平台复现. 两题均已用于适应性调试, 最后对照也不是独立held-out. 论文和OpenReview未改.', '',
            '每轮的指标、hash和模型OBJ输出分别存档; 第4轮成本未改善的记录保留. repo不收第三方代码、原/派生skill全文、原输入、gold或keys.']
    (full/'REPORT.md').write_text('\n'.join(lines)+'\n')
    with zipfile.ZipFile(full/'MODEL_OUTPUTS_ONLY.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
        for r in rows:
            folder=full/r['task']/r['label'];prefix=r['task']+'/'+r['label']
            for p in sorted((folder/'output').rglob('*.obj')):z.write(p,prefix+'/'+p.relative_to(folder).as_posix())
            for name in ['result.json','usage.json','manifest.json']:z.write(folder/name,prefix+'/'+name)
        z.write(full/'REPORT.md','REPORT.md');z.write(full/'FINAL_RESULTS.json','FINAL_RESULTS.json')
    (full/'OUTPUT_ARCHIVE.json').write_text(json.dumps({'bytes':(full/'MODEL_OUTPUTS_ONLY.zip').stat().st_size,
        'sha256':sha(full/'MODEL_OUTPUTS_ONLY.zip'),'contents':'Exact model-generated OBJ data and assistant result metadata only.'},indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();r=report(a.out)
    print(json.dumps({'goal_met':r['full_comparison_goal_met'],'aggregates':r['aggregates'],'token_change_pct':r['aggregate_token_change_pct']}))
