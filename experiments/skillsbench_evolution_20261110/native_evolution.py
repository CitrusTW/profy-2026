"""Adapter for received Evolution functions; original source stays outside this repo."""
import ast
import asyncio
import inspect
import json
import os
import time
import typing
import urllib.request
from pathlib import Path
from types import SimpleNamespace


class SilentLog:
    def __getattr__(self, name):
        return lambda *a, **k: None


def load_functions(path, names=None, namespace=None):
    """Execute original function bodies/constants, omitting framework decorators/imports."""
    tree = ast.parse(Path(path).read_text())
    nodes = [ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0)]
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and (names is None or n.name in names):
            n.decorator_list = []
            nodes.append(n)
        elif isinstance(n, ast.Assign) and (names is None or any(isinstance(t, ast.Name) and t.id in names for t in n.targets)):
            nodes.append(n)
    env = namespace if namespace is not None else {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), str(path), 'exec'), env)
    return env


class LocalSkills:
    def __init__(self, target, workflow):
        self.paths = {'expert/threejs': Path(target), 'builtin/evolution': Path(workflow)}
        self.texts = {'expert/threejs': Path(target).read_text(), 'builtin/evolution': Path(workflow).read_text()}
        self.metas = {n: SimpleNamespace(name=n, description=t.split('description:', 1)[1].split('\n')[0].strip(), tags=[], auto_load_references=[]) for n, t in self.texts.items()}

    def get_enabled_skill_metas(self):
        return list(self.metas.values())

    def _all_metas(self):
        return self.metas

    def resolve_qualified_name(self, name):
        matches = [n for n in self.texts if n == name or n.split('/', 1)[1] == name]
        return SimpleNamespace(status='resolved' if len(matches) == 1 else 'not_found', qualified_name=matches[0] if matches else None)

    async def activate_skill(self, name, **kwargs):
        n = self.resolve_qualified_name(name).qualified_name
        if not n:
            return None
        folder = self.paths[n].parent
        resources = {d: [p.relative_to(folder/d).as_posix() for p in (folder/d).rglob('*') if p.is_file()] for d in ['scripts', 'references', 'assets', 'templates', 'workflows'] if (folder/d).is_dir()}
        return SimpleNamespace(name=n, description=self.metas[n].description, content=self.texts[n], resources=resources, skill_dir=folder)

    async def load_skill_resource(self, skill_name, resource_type, resource_name, **kwargs):
        name = self.resolve_qualified_name(skill_name).qualified_name
        folders = {'reference': 'references', 'asset': 'assets', 'template': 'templates', 'workflow': 'workflows'}
        if not name or resource_type not in folders or Path(resource_name).is_absolute() or '..' in Path(resource_name).parts:
            return None
        base = self.paths[name].parent/folders[resource_type]
        path = base/resource_name
        if not path.is_file() or not path.resolve().is_relative_to(base.resolve()):
            return None
        return SimpleNamespace(path=str(path), content=path.read_text())

    async def fetch_skill_content(self, scope, name, **kwargs):
        content = self.texts.get(scope+'/'+name)
        return SimpleNamespace(content=content) if content is not None else None


class PendingStore:
    def __init__(self, out):
        self.out = Path(out)
        self.rows = []

    async def create_evolution_suggestion(self, **kwargs):
        if self.rows:
            return None
        self.rows.append(kwargs)
        (self.out/'pending.json').write_text(json.dumps(kwargs, ensure_ascii=False, indent=2))
        return 'external-adapter-pending-1'


def original_components(workspace, target, out):
    root = Path(workspace)/'04_项目数据与代码/Profy-main/services/agent-runtime/src'
    evo = root/'plugins/builtin/evolution'
    skills = LocalSkills(target, evo/'skills/evolution/SKILL.md')
    store = PendingStore(out)
    env = {'os': os, 'Literal': typing.Literal, 'Optional': typing.Optional, 'logger': SilentLog(), 'get_core_client': lambda: store}
    gate = load_functions(evo/'tools/evolution_log.py', namespace=env)
    assert gate['_active_rubric']() == 'quality_eff', 'Original default rubric changed'
    names = {'skill', '_get_skill_context', '_get_user_id', '_get_expert_identifier', '_is_internal_invoke', '_skill_discover', '_skill_activate', '_skill_execute', '_build_resource_hint', '_build_auto_loaded_references'}
    skill = load_functions(root/'plugins/builtin/skill/tools/skill.py', names, {'logger': SilentLog()})
    config = {'configurable': {'expert_identifier': 'external-skillsbench-case', 'user_id': 'experiment-owner', 'skill_context': skills, 'is_internal_invoke': True}}
    statnames = {'_format_run_stats', '_RUN_STATS_LINE_MAX_CHARS', '_RUN_STATS_BLOCK_MAX_CHARS'}
    stats = load_functions(root/'api/agent.py', statnames)
    tree = ast.parse((root/'api/agent.py').read_text())
    endpoint = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == 'evolution_endpoint')
    message = next(n for n in endpoint.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'message' for t in n.targets))
    start = ast.literal_eval(message.value.left)
    return gate, skill, config, store, stats, start, (evo/'prompts/EVOLUTION.md').read_text()


def tool_schema(fn):
    props, required = {}, []
    for name, p in inspect.signature(fn).parameters.items():
        if name == 'config':
            continue
        props[name] = {'type': 'object' if name.endswith('_scores') else 'string'}
        if p.default is inspect.Parameter.empty:
            required.append(name)
    return {'type': 'function', 'function': {'name': fn.__name__, 'description': inspect.getdoc(fn), 'parameters': {'type': 'object', 'properties': props, 'required': required, 'additionalProperties': False}}}


def evolve(workspace, target, out, trajectory, metrics, router_key, scrub):
    out = Path(out); out.mkdir(exist_ok=True)
    gate, skill, config, store, stats, start, system = original_components(workspace, target, out)
    stat = SimpleNamespace(run_index=0, total_tokens=metrics.get('total_tokens'), input_tokens=metrics.get('input_tokens'), output_tokens=metrics.get('output_tokens'), llm_turns=metrics.get('llm_turns'), tool_calls=metrics.get('tool_calls'), skill_chars=len(Path(target).read_text()), success=bool(metrics['strict']), skill_version_note='original SkillsBench skill')
    messages = [{'role': 'system', 'content': system}, {'role': 'user', 'content': json.dumps({'development_execution': trajectory}, ensure_ascii=False)}, {'role': 'user', 'content': start+stats['_format_run_stats']([stat])}]
    tools = [tool_schema(skill['skill']), tool_schema(gate['evolution_log'])]
    receipts = []
    began = time.monotonic()
    for turn in range(8):
        request = {'model': 'openai/gpt-4.1', 'temperature': 0, 'max_tokens': 6500, 'messages': messages, 'tools': tools, 'tool_choice': 'auto'}
        (out/f'request_{turn+1}.json').write_text(json.dumps(request, ensure_ascii=False, indent=2))
        req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(request).encode(), headers={'Authorization': 'Bearer '+router_key, 'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=180) as response:
            result = json.load(response)
        (out/f'response_{turn+1}.json').write_text(json.dumps(scrub(result), ensure_ascii=False, indent=2))
        receipts.append(result.get('usage') or {})
        reply = result['choices'][0]['message']
        messages.append({k: reply[k] for k in ['role', 'content', 'tool_calls'] if k in reply})
        calls = reply.get('tool_calls') or []
        print('EVOLUTION_TURN', turn+1, [c['function']['name'] for c in calls], flush=True)
        if not calls:
            break
        for call in calls:
            args = json.loads(call['function']['arguments'])
            name = call['function']['name']
            if name == 'skill' and (args.get('action') in ['discover', 'activate'] or (args.get('action') == 'execute' and args.get('resource_type') != 'script')):
                output = asyncio.run(skill['skill'](**args, config=config))
            elif name == 'evolution_log':
                output = asyncio.run(gate['evolution_log'](**args, config=config))
            else:
                output = 'Error: evolution is read-only except for the original evolution_log suggestion tool.'
            messages.append({'role': 'tool', 'tool_call_id': call['id'], 'content': output})
        if store.rows:
            break
    (out/'tool_transcript.json').write_text(json.dumps(messages, ensure_ascii=False, indent=2))
    summary = {'accepted_by_original_gate': bool(store.rows), 'model': 'openai/gpt-4.1', 'requests': len(receipts), 'usage': receipts, 'elapsed_sec': round(time.monotonic()-began, 3), 'storage': 'external adapter local pending, not Profy database', 'source_functions_modified': False}
    (out/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    if not store.rows:
        return None, summary
    candidate = store.rows[0]['suggestion_content']['improved_content']
    if not candidate.strip() or len(candidate) > 60000:
        raise ValueError('Candidate transport/body invalid')
    (out/'candidate_SKILL.md').write_text(candidate)
    return candidate, summary
