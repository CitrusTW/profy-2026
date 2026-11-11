"""Offline diagnosis of existing OBJ bytes. No API, answer edits or score replacement."""
import argparse
import hashlib
import json
import runpy
import sys
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_obj(path, np):
    vertices, faces = [], []
    for line in path.read_text().splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] == 'v':
            vertices.append([float(v) for v in fields[1:4]])
        elif fields[0] == 'f':
            if len(fields) != 4:
                raise ValueError('This existing task exports triangles; unexpected face arity')
            face = []
            for ref in fields[1:]:
                index = int(ref.split('/')[0])
                if index == 0:
                    raise ValueError('Invalid OBJ vertex index 0')
                index = index - 1 if index > 0 else len(vertices) + index
                if not 0 <= index < len(vertices):
                    raise ValueError('Face references an unavailable vertex')
                face.append(index)
            faces.extend(face)
    return np.array(vertices, dtype=np.float64), np.array(faces, dtype=np.int64)


def diagnose(workspace, run):
    sys.path.extend(['/private/tmp/cognilife-e2e-env/lib/python3.12/site-packages', '/private/tmp/cgl-expert-preflight-deps'])
    import numpy as np
    workspace, run = Path(workspace).resolve(), Path(run).resolve()
    benchmark = run/'benchmark'
    gt = run.parent/'run-01/grader_environment/threejs-structure-parser/ground_truth'
    scorer = workspace/'04_项目数据与代码/skillsbench/tasks/threejs-structure-parser/verifier/test_outputs.py'
    original = workspace/'04_项目数据与代码/skillsbench/tasks/threejs-to-obj/environment/skills/threejs/SKILL.md'
    candidate = run/'round-02/evolution/candidate_SKILL.md'
    protected = [original, candidate, run/'benchmark/selected_SKILL.md', scorer]
    for label in ['with-skills', 'with-CogniLife-skills']:
        protected += [benchmark/label/name for name in ['request.json','result.json','manifest.json','deliverables.zip','supplied_skill_hashes.json']]
        protected += list((benchmark/label/'output').rglob('*.obj'))
    before = {str(p): sha(p) for p in protected}
    native = runpy.run_path(str(scorer))
    cd = native['chamfer_distance']
    rows = []
    expected_files = {p.relative_to(gt).as_posix() for p in gt.rglob('*.obj')}
    for label in ['with-skills','with-CogniLife-skills']:
        actual = {p.relative_to(benchmark/label/'output').as_posix() for p in (benchmark/label/'output').rglob('*.obj')}
        assert actual == expected_files, 'File structure mismatch'
    for name in sorted(expected_files):
        g64, gf = read_obj(gt/name, np)
        b64, bf = read_obj(benchmark/'with-skills/output'/name, np)
        c64, cf = read_obj(benchmark/'with-CogniLife-skills/output'/name, np)
        g, b, c = [v.astype(np.float32) for v in [g64,b64,c64]]
        expanded = c[cf]
        same_shape = expanded.shape == g.shape
        unique_c, unique_g = np.unique(c,axis=0), np.unique(g,axis=0)
        sample_c = native['downsample_points'](native['canonicalize_points'](c))
        sample_g = native['downsample_points'](native['canonicalize_points'](g))
        rows.append({'file':name,'reference_vertices':len(g),'original_vertices':len(b),'candidate_vertices':len(c),
            'reference_triangles':len(gf)//3,'original_triangles':len(bf)//3,'candidate_triangles':len(cf)//3,
            'reference_unique_vertices_float32':len(unique_g),'candidate_unique_vertices_float32':len(unique_c),
            'unique_position_sets_exactly_equal_float32':bool(np.array_equal(unique_c,unique_g)),
            'face_expanded_positions_equal_reference_rows_float32':bool(same_shape and np.array_equal(expanded,g)),
            'face_expanded_float64_max_coordinate_difference':float(np.max(np.abs(c64[cf]-g64))) if same_shape else None,
            'official_metric_original_raw':cd(b,g),'official_metric_candidate_raw':cd(c,g),
            'diagnostic_metric_face_expanded_candidate':cd(expanded,g),
            'diagnostic_metric_deduplicated_both':cd(unique_c,unique_g),
            'overlap_between_two_300_sample_point_sets':len(set(map(tuple,sample_c)) & set(map(tuple,sample_g)))})
    a = json.loads((benchmark/'with-skills/request.json').read_text())
    b = json.loads((benchmark/'with-CogniLife-skills/request.json').read_text())
    for request in [a,b]:
        for field in ['session_id','attachment_file_ids']:
            request.pop(field,None)
    packs = [json.loads((benchmark/label/'supplied_skill_hashes.json').read_text()) for label in ['with-skills','with-CogniLife-skills']]
    assert packs[0].keys() == packs[1].keys()
    changed_pack = [key for key in packs[0] if packs[0][key] != packs[1][key]]
    events = [json.loads(s) for s in (benchmark/'with-CogniLife-skills/events.jsonl').read_text().splitlines()]
    commands = [e['parameters'].get('command','') for e in events if e.get('type') == 'tool_call.in_progress' and e.get('tool_name') == 'bash']
    protected_unchanged = all(sha(Path(p)) == h for p,h in before.items())
    assert protected_unchanged
    result = {'kind':'Offline diagnosis using existing outputs; diagnostic metrics do not replace official rewards.',
        'client_date':'2026-11-10','timezone':'America/Los_Angeles','model_calls':0,'new_solver_runs':0,
        'file_pairs_checked':len(rows),'original_raw_metric_failures':sum(r['official_metric_original_raw'] >= native['CD_THRESHOLD'] for r in rows),
        'candidate_raw_metric_failures':sum(r['official_metric_candidate_raw'] >= native['CD_THRESHOLD'] for r in rows),
        'diagnostic_face_expansion_failures':sum(r['diagnostic_metric_face_expanded_candidate'] >= native['CD_THRESHOLD'] for r in rows),
        'all_unique_position_sets_equal_float32':all(r['unique_position_sets_exactly_equal_float32'] for r in rows),
        'all_face_expanded_rows_equal_float32':all(r['face_expanded_positions_equal_reference_rows_float32'] for r in rows),
        'max_float64_coordinate_difference':max(r['face_expanded_float64_max_coordinate_difference'] or 0 for r in rows),
        'request_bodies_equal_except_session_and_attachment_ids':a==b,'changed_pack_files':changed_pack,
        'candidate_installed_task_pinned_version':any('three@0.170.0' in c for c in commands),
        'candidate_solver_calls_toNonIndexed':any('toNonIndexed(' in c for c in commands),
        'original_score_unchanged':{'with-skills':json.loads((benchmark/'with-skills/result.json').read_text())['score'],
                                    'with-CogniLife-skills':json.loads((benchmark/'with-CogniLife-skills/result.json').read_text())['score']},
        'protected_artifacts_unchanged':protected_unchanged,'protected_files_checked':len(protected),
        'candidate_sha256':sha(candidate),'scorer_sha256':sha(scorer),'rows':rows,
        'limit':'Float32 position/triangle equivalence for these files only; not a claim about UVs, normals, other tasks, or full CogniLife.'}
    out = run/'diagnosis_20261110';out.mkdir(exist_ok=True)
    (out/'DIAGNOSIS_FACTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    result=diagnose(a.workspace,a.out)
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},ensure_ascii=False,indent=2))
