"""Archive bounded iteration receipts and exact model-produced output bytes."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from iterate import eligible


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize(workspace, root):
    workspace, root = Path(workspace), Path(root)
    state = json.loads((root/'FINAL.json').read_text())
    protocol = json.loads((root/'PROTOCOL.json').read_text())
    rounds = state['rounds']
    for row in rounds:
        if 'development' in row:
            live = json.loads((root/f"round-{row['round']:02d}"/'development/result.json').read_text())
            assert row['development'] == live
            assert live['score']['source_sha256'] == digest(workspace/'04_项目数据与代码/skillsbench/tasks/threejs-to-obj/verifier/test_outputs.py')
    chosen = state.get('best_round')
    if chosen is not None:
        selected = next(row for row in rounds if row['round'] == chosen)
        assert eligible(selected['development'], state['baseline_tokens'])
        assert all(selected['development']['tokens']['total_tokens'] <= row['development']['tokens']['total_tokens']
                   for row in rounds if 'development' in row and eligible(row['development'], state['baseline_tokens']))
    if state['status'] == 'completed':
        assert eligible(state['confirmation'], state['baseline_tokens'])
        assert state['confirmation']['native_zip_sha256'] == digest(root/'confirmation/development/deliverables.zip')
        assert state['confirmation']['skill_sha256'] == digest(root/f'round-{chosen:02d}/evolution/candidate_SKILL.md')
        frozen = json.loads((root/'benchmark/frozen.json').read_text())
        assert frozen['skill_sha256'] == digest(root/f'round-{chosen:02d}/evolution/candidate_SKILL.md') == digest(root/'benchmark/selected_SKILL.md')
        b = json.loads((root/'benchmark/with-skills/supplied_skill_hashes.json').read_text())
        c = json.loads((root/'benchmark/with-CogniLife-skills/supplied_skill_hashes.json').read_text())
        assert set(b) == set(c) and [k for k in b if b[k] != c[k]] == ['bench_skills/threejs/SKILL.md']
        assert c['bench_skills/threejs/SKILL.md'] == frozen['skill_sha256']
        assert b['bench_skills/threejs/SKILL.md'] == digest(workspace/'04_项目数据与代码/skillsbench/tasks/threejs-to-obj/environment/skills/threejs/SKILL.md')
        for row in state['benchmark']:
            folder = root/'benchmark'/row['label']
            assert row == json.loads((folder/'result.json').read_text())
            assert row['native_zip_sha256'] == digest(folder/'deliverables.zip')
            assert row['score']['source_sha256'] == digest(workspace/'04_项目数据与代码/skillsbench/tasks/threejs-structure-parser/verifier/test_outputs.py')
            for name, sha in row['file_hashes'].items():
                assert digest(folder/name) == sha
    total_cost = sum(u.get('cost', 0) for row in rounds for u in row['evolution']['usage'])
    decision = {'candidate_adopted':False,'recommended_version':'original SkillsBench threejs skill'}
    if state.get('benchmark'):
        b = next(row for row in state['benchmark'] if row['label']=='with-skills')
        c = next(row for row in state['benchmark'] if row['label']=='with-CogniLife-skills')
        decision.update({'benchmark_token_change_pct':100*(c['tokens']['total_tokens']/b['tokens']['total_tokens']-1),
                         'benchmark_quality_change_passed_tests':c['score']['passed']-b['score']['passed'],
                         'no_post_benchmark_tuning':True})
        decision['candidate_adopted'] = c['score']['strict']==1 and c['score']['passed']>=b['score']['passed'] and c['tokens']['total_tokens']<b['tokens']['total_tokens']
        if decision['candidate_adopted']:decision['recommended_version']='selected evolved candidate'
    summary = {'client_date':'2026-11-10','timezone':'America/Los_Angeles','state':state,'protocol':protocol,
               'evolution_reported_cost_usd':total_cost,'profy_cost_usd':None,
               'selection_scope':'DEV quality and reported tokens only; no benchmark feedback used to revise or select.',
               'method_scope':'Received original skill-refinement core plus explicitly new external iteration and selection logic.',
               'unimplemented':['capability-gap classifier','general semantic applicability verifier','native creator acceptance/promotion'],
               'conclusion':decision,
               'validation_scope':'Previously inspected task; diagnostic only. No unseen compatible SkillsBench task exists at pinned official main.'}
    (root/'ITERATIVE_RESULTS.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    lines=['# CogniLife路径的多轮skill refinement', '', '2026-11-10, America/Los_Angeles. 所有新求解均为真实Profy API调用, Evolution为OpenRouter的gpt-6.1-sol. 原workflow、门控、run_stats模型和渲染不改; 多次invoke编排和实测选择是本实验新增部分.', '',
           '| 开发记录 | 原测试 | tokens | 耗时(秒) | 工具调用 |', '| --- | --- | --- | --- | --- |',
           '| 复用原版基线 | 3/3 | 152865 | 156.874 | 9 |', '| 复用上一份未选候选 | 3/3 | 287965 | 173.908 | 15 |']
    for row in rounds:
        if 'development' not in row:
            lines.append(f"| 新invoke {row['round']} | 未提出候选 | - | - | - |");continue
        r=row['development'];s=r['score']
        lines.append(f"| 新候选 {row['round']} ({row['status']}) | {s['passed']}/{s['tests']} | {r['tokens']['total_tokens']} | {r['elapsed_sec']} | {r['tokens']['tool_calls']} |")
    if 'confirmation' in state:
        r=state['confirmation'];s=r['score'];lines.append(f"| 选中版本再次确认 | {s['passed']}/{s['tests']} | {r['tokens']['total_tokens']} | {r['elapsed_sec']} | {r['tokens']['tool_calls']} |")
    lines += ['', f"结束状态: {state['status']}. 开发阶段选中round {chosen}. 这是预算内实测最好的候选, 不是全局最优保证.", '']
    if state.get('benchmark'):
        lines += ['| 最后benchmark组别 | 原测试 | tokens | 耗时(秒) | skill读入核验 |','| --- | --- | --- | --- | --- |']
        for r in state['benchmark']:
            s=r['score'];lines.append(f"| {r['label']} | {s['passed']}/{s['tests']} | {r['tokens']['total_tokens']} | {r['elapsed_sec']} | {r['target_skill_read_verified']} |")
    lines += ['', f'Evolution累计返回费用${total_cost:.6f}; Profy没有美元账单, 总美元费用未知.', '',
              '每一轮只输入开发题request/events与各版本的原生run_stats. 未选择的开发尝试也保留并反馈成本; 每次invoke仍最多一条建议. 只有质量保持且实测tokens下降才选择, 最后候选单独确认一次. 验证前冻结, 验证后不改skill.', '',
              '目前只有两道SkillsBench题包含这份threejs skill, 官方main与本地固定commit相同. 最后那道题以前已分析过, 因此结果只能作为diagnostic, 不能当独立泛化证据或完整benchmark成绩. 自动语义适用性检查、能力缺口分类和native promotion仍未完成. 本轮没有修改论文.', '',
              '仓库仅存助手写的代码、数字报告和模型生成的OBJ数据. 原skills、派生skill全文、原输入、第三方源码、gold和keys留在工作区, 不进private repo.']
    lines += ['', f"最终决定: {'采用进化版' if decision['candidate_adopted'] else '不采用进化版, 保留原版'}. 这是本轮全部结果之后的实际决定, 不是修改第三组来追求好看分数."]
    if state.get('benchmark'):
        lines += [f"最后benchmark相对原版, 原测试通过数变化{decision['benchmark_quality_change_passed_tests']:+d}, reported tokens变化{decision['benchmark_token_change_pct']:+.1f}%. 质量与成本都要满足目标, 不能用省tokens抵偿质量退步."]
    if (root/'DEV_REVIEW_NOTES.json').exists():
        summary['independent_dev_review']=json.loads((root/'DEV_REVIEW_NOTES.json').read_text())
        (root/'ITERATIVE_RESULTS.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
        lines += ['', '独立agent仅用DEV复核, 未发现必须停止单OBJ开发检查的严重错误, 但resource路径、skill.execute接口与失败后修复例外仍存在未验证风险. 复核没有输入Evolution, 不能视为通用语义核验通过.']
    (root/'ITERATIVE_REPORT.md').write_text('\n'.join(lines)+'\n')
    with zipfile.ZipFile(root/'MODEL_OUTPUTS_ONLY.zip','w',compression=zipfile.ZIP_DEFLATED) as archive:
        folders = list(root.glob('round-*/development'))
        if (root/'confirmation/development').exists():folders.append(root/'confirmation/development')
        folders += list((root/'benchmark').glob('*-skills')) if (root/'benchmark').exists() else []
        if (root/'benchmark/with-CogniLife-skills').exists() and root/'benchmark/with-CogniLife-skills' not in folders:folders.append(root/'benchmark/with-CogniLife-skills')
        for folder in folders:
            prefix = folder.relative_to(root).as_posix()
            if not (folder/'deliverables.zip').exists():continue
            with zipfile.ZipFile(folder/'deliverables.zip') as native:
                for name in native.namelist():
                    if name.startswith('output/') and name.endswith('.obj'):
                        archive.writestr(prefix+'/'+name,native.read(name))
            for name in ['result.json','usage.json','manifest.json']:
                archive.write(folder/name,prefix+'/'+name)
        archive.write(root/'ITERATIVE_RESULTS.json','ITERATIVE_RESULTS.json')
        archive.write(root/'ITERATIVE_REPORT.md','ITERATIVE_REPORT.md')
    receipt={'bytes':(root/'MODEL_OUTPUTS_ONLY.zip').stat().st_size,'sha256':digest(root/'MODEL_OUTPUTS_ONLY.zip'),
             'contents':'Exact OBJ bytes and assistant-generated metadata only; no third-party code, skill bodies, source inputs, tests or keys.'}
    (root/'OUTPUT_ARCHIVE.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    r=summarize(a.workspace,a.out);print(json.dumps({'status':r['state']['status'],'best_round':r['state']['best_round'],'evolution_cost':r['evolution_reported_cost_usd']}))
