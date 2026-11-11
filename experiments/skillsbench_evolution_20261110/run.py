"""Small public-task experiment. Only transport/glue; no new learning prompt or grader."""
import argparse
import ast
import concurrent.futures
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from native_evolution import evolve

DEV = 'threejs-to-obj'
TEST = 'threejs-structure-parser'
MODEL = 'gpt-6.1-sol'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def load_own_transport(workspace):
    p = Path(workspace)/'04_项目数据与代码/辅助代码/three_arm_skill_pilot_20261110/pilot.py'
    if not p.exists():
        p = Path(__file__).resolve().parents[1]/'three_arm_pilot_20261110/pilot.py'
    spec = importlib.util.spec_from_file_location('previous_own_transport', p)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def unpack_output(raw, folder):
    """Extract only native output bytes; never create a missing expected answer."""
    import io
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names = z.namelist()
        assert len(names) <= 1000 and sum(f.file_size for f in z.infolist()) <= 30_000_000
        assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in names)
        assert all(n == 'manifest.json' or n.startswith('output/') for n in names), names
        z.extractall(folder)
    manifest = json.loads((folder/'manifest.json').read_text())
    for name, expected in manifest['files'].items():
        assert name.startswith('output/') and sha((folder/name).read_bytes()) == expected
    actual = {p.relative_to(folder).as_posix() for p in (folder/'output').rglob('*') if p.is_file()} if (folder/'output').exists() else set()
    assert actual == set(manifest['files']), 'Native manifest/output mismatch'
    return manifest


class Study:
    def __init__(self, args):
        self.workspace = Path(args.workspace).resolve(); self.out = Path(args.out).resolve()
        self.out.mkdir(parents=True, exist_ok=True)
        self.bench = self.workspace/'04_项目数据与代码/skillsbench/tasks'
        old = load_own_transport(self.workspace)
        self.strings = old.strings
        self.transport = old.Pilot(argparse.Namespace(workspace=str(self.workspace), out=str(self.out), dev_inputs=str(self.bench/DEV/'environment'), keys_file=args.keys_file))
        self.target = self.bench/DEV/'environment/skills/threejs/SKILL.md'
        assert self.target.read_bytes() == (self.bench/TEST/'environment/skills/threejs/SKILL.md').read_bytes()

    def setup_grader(self, task):
        dest = self.out/'grader_environment'/task
        if (dest/'ready.json').exists():
            return dest
        (dest/'data').mkdir(parents=True, exist_ok=True)
        shutil.copyfile(self.bench/task/'environment/data/object.js', dest/'data/object.js')
        (dest/'package.json').write_text('{"private":true,"type":"module"}\n')
        version = '0.175.0' if task == DEV else '0.170.0'
        p = subprocess.run(['npm', 'install', '--ignore-scripts', '--no-audit', '--no-fund', 'three@'+version], cwd=dest, capture_output=True, text=True, timeout=180)
        (dest/'npm.log').write_text(p.stdout+p.stderr)
        if p.returncode:
            raise RuntimeError('Scoring npm dependency install failed; no model should run')
        code = (self.bench/task/'verifier/gen_ground_truth.mjs').read_text()
        bound = code.replace('/root/', dest.as_posix()+'/')
        (dest/'generate_reference.mjs').write_text(bound)
        p = subprocess.run(['node', 'generate_reference.mjs'], cwd=dest, capture_output=True, text=True, timeout=120)
        (dest/'reference_generation.log').write_text(p.stdout+p.stderr)
        if p.returncode:
            raise RuntimeError('Original scoring reference generation failed')
        save(dest/'ready.json', {'original_generator_sha256': sha(code.encode()), 'binding': '/root/ only', 'three_version': version, 'never_uploaded': True})
        return dest

    def grade(self, task, folder):
        gt = self.setup_grader(task)
        src = self.bench/task/'verifier/test_outputs.py'
        tree = ast.parse(src.read_text()); before = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
        class BindPaths(ast.NodeTransformer):
            def visit_Constant(self, node):
                if isinstance(node.value, str) and node.value.startswith('/root/'):
                    suffix = node.value[len('/root/'):]
                    base = gt if suffix.startswith('ground_truth') else folder
                    return ast.copy_location(ast.Constant(str(base/suffix)), node)
                return node
        tree = BindPaths().visit(tree)
        assert before == sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
        scoring = folder/'scoring_only'; scoring.mkdir(exist_ok=True)
        (scoring/'test_outputs.py').write_text(ast.unparse(tree)+'\n')
        bootstrap = "import sys;sys.path.extend(['/private/tmp/cognilife-e2e-env/lib/python3.12/site-packages','/private/tmp/cgl-expert-preflight-deps']);import pytest;raise SystemExit(pytest.main(sys.argv[1:]))"
        p = subprocess.run([sys.executable, '-c', bootstrap, str(scoring/'test_outputs.py'), '-q', '-p', 'no:cacheprovider', '--junitxml='+str(scoring/'junit.xml')], cwd=folder, capture_output=True, text=True, timeout=240)
        (scoring/'pytest.log').write_text(p.stdout+p.stderr)
        cases = ET.parse(scoring/'junit.xml').findall('.//testcase')
        failed = sum(c.find('failure') is not None or c.find('error') is not None for c in cases)
        skipped = sum(c.find('skipped') is not None for c in cases)
        result = {'tests': len(cases), 'passed': len(cases)-failed-skipped, 'failed': failed, 'skipped': skipped, 'strict': int(p.returncode == 0 and bool(cases) and not skipped), 'original_returncode': p.returncode, 'source_sha256': sha(src.read_bytes()), 'assertions_unchanged': before}
        save(scoring/'receipt.json', result)
        return result

    def solve(self, label, task, candidate=None, no_skills=False):
        f = self.out/label; f.mkdir(exist_ok=True)
        assert not (f/'started.json').exists(), 'Do not duplicate a paid attempt'
        assert len(list(self.out.glob('*/started.json'))) < 5, 'Paid solve cap'
        save(f/'started.json', {'task': task, 'model': MODEL, 'label': label})
        user = 'sb-evo-'+self.out.name+'-'+label
        source = self.bench/task/'environment'
        with zipfile.ZipFile(f/'task_input.zip', 'w', compression=zipfile.ZIP_DEFLATED) as z:
            z.write(source/'data/object.js', 'data/object.js')
        files = [f/'task_input.zip']
        expected = {}
        if not no_skills:
            with zipfile.ZipFile(f/'benchmark_skills.zip', 'w', compression=zipfile.ZIP_DEFLATED) as z:
                for p in sorted((source/'skills').rglob('*')):
                    if p.is_file() and not p.name.startswith('.'):
                        rel = p.relative_to(source/'skills').as_posix()
                        raw = candidate.encode() if candidate is not None and rel == 'threejs/SKILL.md' else p.read_bytes()
                        z.writestr('bench_skills/'+rel, raw)
                        expected['bench_skills/'+rel] = sha(raw)
            files.append(f/'benchmark_skills.zip')
        receipts = [self.transport.upload(p, user) for p in files]
        save(f/'uploads.json', receipts); save(f/'supplied_skill_hashes.json', expected)
        session = self.transport.api('/v1/sessions', {'agent': self.transport.expert_id, 'title': 'SkillsBench '+label}, user)['id']
        save(f/'session.json', {'id': session})
        tasktext = (self.bench/task/'task.md').read_text().split('---', 2)[2].strip()
        version = '0.175.0' if task == DEV else '0.170.0'
        setup = ('Unzip benchmark_skills.zip into this session. Use read to load bench_skills/threejs/SKILL.md and bench_skills/obj-exporter/SKILL.md in full before solving; follow relevant supplied instructions and references. Compute and print SBP_ACTIVE_SKILL_SHA256:<computed hash> of bench_skills/threejs/SKILL.md with bash. '
                 if not no_skills else 'No benchmark skills are supplied. Solve with ordinary code/file tools. Do not discover or activate any other expert/user/builtin skill packages. ')
        common = '''
Execution adapter instructions (same in all groups): Unzip task_input.zip into this session directory, so data/object.js exists. Paths /root/ in the original task mean this session directory. Preserve that input unchanged. Node.js/npm are available; use the task-pinned three@VERSION if installation is needed. No web search, Memory, delegation, other sessions, benchmark tests, oracle or reference answers. Do not ask questions; produce the best supported original deliverables. Use at most 48 tool calls and 24 model turns.
After writing the original requested outputs under output/, package only those actual files into deliverables.zip. Include manifest.json at ZIP root containing {"input_sha256": "computed SHA256 of data/object.js", "files": {"output/path.obj": "computed SHA256 of those exact bytes", ...}}. Use Python zipfile to put the actual output/ files and manifest.json into deliverables.zip, without altering/reformatting the output bytes. Print [OUTPUT] deliverables.zip and SBP_NATIVE_ZIP_SHA256:<computed SHA256 of deliverables.zip>. This is only file transport after solving, not a new deliverable requirement for the original grader. Final response briefly names the output file(s).
'''.replace('VERSION', version)
        body = {'agent': {'id': self.transport.expert_id, 'model': MODEL, 'tools': []}, 'rules': [], 'environment': {'type': 'profy_hosted', 'skills': []}, 'enable_memory': False, 'expert_partner': [], 'input': tasktext+'\n\n'+setup+common, 'stream': True, 'session_id': session, 'attachment_file_ids': [r['file_id'] for r in receipts]}
        save(f/'request.json', body)
        stop = threading.Event()
        def interrupt():
            if stop.is_set(): return
            stop.set()
            try: self.transport.api('/v1/sessions/'+session+'/interrupt', {}, user)
            except Exception: pass
        timer = threading.Timer(900, interrupt); timer.daemon = True; timer.start()
        began = time.monotonic(); events = []; calls = {}; usages = []; error = None; completed = False; archive = None
        print('START', label, flush=True)
        try:
            req = urllib.request.Request('https://api.profy.cn/v1/agents/run', data=json.dumps(body).encode(), headers={'Authorization': 'Bearer '+self.transport.key, 'Content-Type': 'application/json', 'X-Profy-End-User-Id': user, 'Accept': 'text/event-stream'}, method='POST')
            with urllib.request.urlopen(req, timeout=120) as response, (f/'events.jsonl').open('w') as log:
                for raw in response:
                    line = raw.decode().strip()
                    if stop.is_set(): error = 'hard_budget_stop'; break
                    if not line.startswith('data:'): continue
                    if line[5:].strip() == '[DONE]': break
                    event = json.loads(line[5:]); kind = event.get('type')
                    safe = self.transport.scrub(event); events.append(safe); log.write(json.dumps(safe, ensure_ascii=False)+'\n'); log.flush()
                    if kind in ['tool_call.created', 'tool_call.in_progress'] and event.get('tool_call_id'):
                        cid = event['tool_call_id']
                        if cid not in calls and event.get('tool_name'):
                            calls[cid] = event['tool_name']; print('TOOL', label, event['tool_name'], flush=True)
                    if kind == 'usage.token': usages.append(safe)
                    if len(calls) > 48 or len(usages) > 24: error = 'tool_or_turn_cap'; interrupt()
                    if kind in ['run.failed', 'request_user_input']: error = kind; interrupt()
                    if kind == 'run.completed': completed = True
                    if kind == 'tool_call.result':
                        result = event.get('result')
                        if isinstance(result, str):
                            try: result = json.loads(result)
                            except ValueError: result = {}
                        if isinstance(result, dict):
                            for item in result.get('files') or []:
                                url = item.get('url') or ''
                                if item.get('name') == 'deliverables.zip' and urllib.parse.urlsplit(url).scheme == 'https':
                                    with urllib.request.urlopen(url, timeout=60) as download: archive = download.read(30_000_001)
                                    if len(archive) > 30_000_000: raise ValueError('Native archive too large')
        except Exception as exc:
            error = type(exc).__name__; interrupt()
            save(f/'exception.json', {'type': error, 'detail': self.transport.scrub(str(exc))})
        finally: timer.cancel()
        texts = '\n'.join(s for e in events if e.get('type') == 'tool_call.result' for s in self.strings(e.get('result')))
        hashes = re.findall(r'SBP_NATIVE_ZIP_SHA256:\s*([0-9a-f]{64})', texts)
        manifest = None
        if archive is not None:
            (f/'deliverables.zip').write_bytes(archive)
            if not hashes or sha(archive) != hashes[-1]: raise ValueError('Native ZIP hash does not match download')
            manifest = unpack_output(archive, f)
            assert manifest['input_sha256'] == sha((source/'data/object.js').read_bytes())
        target_hash = sha((candidate if candidate is not None else self.target.read_text()).encode()) if not no_skills else None
        read_match = any(e.get('type') == 'tool_call.result' and e.get('tool_name') == 'read' and (candidate if candidate is not None else self.target.read_text()).strip() in '\n'.join(self.strings(e.get('result'))) for e in events) if not no_skills else None
        seen_hashes = re.findall(r'SBP_ACTIVE_SKILL_SHA256:\s*([0-9a-f]{64})', texts)
        metrics = {key: sum(e.get(field, 0) or 0 for e in usages) for key, field in [('input_tokens', 'prompt_tokens'), ('output_tokens', 'completion_tokens'), ('total_tokens', 'total_tokens'), ('cache_read_tokens', 'cache_read_tokens'), ('cache_write_tokens', 'cache_write_tokens')]}
        metrics.update({'llm_turns': len(usages), 'tool_calls': len(calls)})
        result = {'label': label, 'task': task, 'completed': completed, 'error': error, 'elapsed_sec': round(time.monotonic()-began, 3), 'output_received': manifest is not None, 'native_zip_sha256': sha(archive) if archive else None, 'file_hashes': manifest['files'] if manifest else {}, 'skill_sha256': target_hash, 'target_skill_read_verified': bool(read_match and target_hash in seen_hashes) if not no_skills else None, 'external_skill_tools_observed': [n for n in calls.values() if 'skill' in n.lower()], 'supplied_benchmark_skills': not no_skills, 'tokens': metrics, 'profy_cost_usd': None}
        save(f/'usage.json', usages); save(f/'run_summary.json', result)
        result['score'] = self.grade(task, f)
        save(f/'result.json', result)
        print('DONE', label, json.dumps({'score': result['score'], 'elapsed_sec': result['elapsed_sec'], 'skill_read_verified': result['target_skill_read_verified']}), flush=True)
        return result

    def evolve(self):
        f = self.out/'dev_original'; result = json.loads((f/'result.json').read_text())
        assert result['completed'] and result['output_received'] and result['target_skill_read_verified'] and not result['external_skill_tools_observed'], 'Development execution invalid'
        events = [json.loads(line) for line in (f/'events.jsonl').read_text().splitlines()]
        trajectory = {'task': DEV, 'public_instruction': (self.bench/DEV/'task.md').read_text().split('---', 2)[2].strip(), 'events': [e for e in events if e.get('type') in ['tool_call.in_progress', 'tool_call.result']], 'output_manifest': result['file_hashes']}
        metrics = {**result['tokens'], 'strict': result['score']['strict']}
        return evolve(self.workspace, self.target, self.out/'evolution', trajectory, metrics, self.transport.router_key, self.transport.scrub)


def main():
    p = argparse.ArgumentParser(); p.add_argument('phase', choices=['setup', 'dev', 'evolve', 'candidate', 'test', 'report'])
    p.add_argument('--workspace', required=True); p.add_argument('--out', required=True); p.add_argument('--keys-file', required=True)
    args = p.parse_args(); study = Study(args)
    if args.phase == 'setup':
        for t in [DEV, TEST]: study.setup_grader(t)
        print('SCORING_ENV_READY', flush=True)
    elif args.phase == 'dev': study.solve('dev_original', DEV)
    elif args.phase == 'evolve': study.evolve()
    elif args.phase == 'candidate': study.solve('dev_candidate', DEV, (study.out/'evolution/candidate_SKILL.md').read_text())
    elif args.phase == 'test':
        original = json.loads((study.out/'dev_original/result.json').read_text()); candidate = json.loads((study.out/'dev_candidate/result.json').read_text())
        assert candidate['score']['strict'] >= original['score']['strict'] and candidate['target_skill_read_verified'] and candidate['output_received'] and not candidate['external_skill_tools_observed'], 'Candidate comparison not eligible'
        frozen = (study.out/'evolution/candidate_SKILL.md').read_text()
        save(study.out/'frozen.json', {'before_sha256': sha(study.target.read_bytes()), 'after_sha256': sha(frozen.encode()), 'development_before': original['score'], 'development_after': candidate['score'], 'native_promotion_called': False})
        for label, skills in [('no-skills', False), ('with-skills', True), ('with-CogniLife-skills', True)]:
            study.solve(label, TEST, frozen if label == 'with-CogniLife-skills' else None, not skills)
    else:
        rows = [json.loads(f.read_text()) for f in study.out.glob('*/result.json')]
        save(study.out/'results_summary.json', rows)
        print(json.dumps([{'label': r['label'], 'score': r['score'], 'elapsed_sec': r['elapsed_sec'], 'tokens': r['tokens']} for r in rows], ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
