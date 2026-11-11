"""Check recorded lineage and DEV execution. Never reads held-out task answers."""
import hashlib
import json
from pathlib import Path

from native_evolution import EVOLUTION_MODEL, EVOLUTION_WIRE_MODEL, EVOLUTION_URL, MISSING_IMPLEMENTATIONS, yaml_module


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def check_candidate(run_dir, target):
    run_dir, target = Path(run_dir), Path(target)
    evo = run_dir/'evolution'
    checks = {}
    def load(path):
        if not path.is_file():
            checks[str(path.relative_to(run_dir))+' exists'] = False
            return {}
        return json.loads(path.read_text())
    summary = load(evo/'summary.json')
    provenance = load(evo/'provenance.json')
    pending = load(evo/'pending.json').get('suggestion_content', {})
    candidate_path = evo/'candidate_SKILL.md'
    raw = candidate_path.read_bytes() if candidate_path.exists() else b''
    before, after = load(run_dir/'dev_original/result.json'), load(run_dir/'dev_candidate/result.json')
    checks['configured_evolver_model'] = summary.get('model') == EVOLUTION_MODEL == provenance.get('model')
    checks['configured_evolver_endpoint'] = summary.get('endpoint') == EVOLUTION_URL == provenance.get('endpoint')
    checks['original_gate_admitted'] = summary.get('accepted_by_original_gate') is True
    checks['parent_version_matches'] = provenance.get('parent_sha256') == digest(target.read_bytes())
    requests = sorted(evo.glob('request_*.json'))
    request_rows = [json.loads(p.read_text()) for p in requests]
    checks['recorded_request_model'] = bool(request_rows) and all(r.get('model') == EVOLUTION_WIRE_MODEL for r in request_rows)
    checks['first_request_matches_provenance'] = bool(request_rows) and provenance.get('request_sha256') == digest(json.dumps(request_rows[0], ensure_ascii=False, sort_keys=True).encode())
    checks['candidate_matches_pending'] = bool(raw) and raw == pending.get('improved_content', '').encode()
    checks['preselected_target_only'] = pending.get('skill_name') == target.parent.name
    checks['candidate_body_size'] = 0 < len(raw.decode()) <= 60000
    # Structure only. This cannot tell whether natural-language advice generalizes.
    yaml = yaml_module()
    try:
        header = raw.decode().split('---', 2)
        meta = yaml.safe_load(header[1]) if len(header) == 3 and not header[0].strip() else {}
        checks['candidate_frontmatter'] = meta.get('name') == target.parent.name and bool(meta.get('description'))
    except (ValueError, AttributeError, yaml.YAMLError):
        checks['candidate_frontmatter'] = False
    for label, row, expected in [('dev_original', before, digest(target.read_bytes())), ('dev_candidate', after, digest(raw))]:
        score = row.get('score', {})
        checks[label+' execution'] = row.get('task') == 'threejs-to-obj' and row.get('completed') is True and row.get('error') is None and row.get('output_received') is True
        checks[label+' skill read'] = row.get('target_skill_read_verified') is True and row.get('skill_sha256') == expected and row.get('external_skill_tools_observed') == []
        checks[label+' scoring complete'] = score.get('tests', 0) > 0 and score.get('skipped') == 0 and score.get('tests') == score.get('passed', 0)+score.get('failed', 0)
        checks[label+' strict consistent'] = score.get('strict') == int(score.get('tests', 0) > 0 and score.get('failed') == 0 and score.get('skipped') == 0 and score.get('original_returncode') == 0)
    b, a = before.get('score', {}), after.get('score', {})
    checks['development_quality_nondegrading'] = b.get('tests', 0) > 0 and a.get('tests') == b.get('tests') and a.get('passed', -1) >= b.get('passed', 0)
    measured = {}
    for key in ['total_tokens', 'tool_calls', 'llm_turns']:
        bv, av = before.get('tokens', {}).get(key), after.get('tokens', {}).get(key)
        measured[key] = {'before': bv, 'after': av, 'delta': av-bv if bv is not None and av is not None else None}
    return {'kind': 'offline structural and DEV evidence check, not semantic verification',
            'checks': checks, 'structural_and_dev_pass': all(checks.values()),
            'failed_checks': [k for k, v in checks.items() if not v],
            'measured_development': measured,
            'measured_efficiency_is_original_gate': False,
            'semantic_applicability_verified': False, 'native_promoted': False,
            'full_paper_method_verified': False, 'missing_implementations': MISSING_IMPLEMENTATIONS,
            'candidate_sha256': digest(raw), 'parent_sha256': digest(target.read_bytes())}
