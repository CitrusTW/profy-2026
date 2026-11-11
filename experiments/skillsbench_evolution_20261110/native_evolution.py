"""Adapter for received Evolution functions; original source stays outside this repo."""
import ast
import asyncio
import inspect
import hashlib
import json
import os
import re
import runpy
import sys
import time
import typing
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

EVOLUTION_MODEL = 'gpt-6.1-sol'
EVOLUTION_WIRE_MODEL = 'openai/gpt-6.1-sol'
EVOLUTION_URL = 'https://openrouter.ai/api/v1/chat/completions'
MISSING_IMPLEMENTATIONS = {
    'capability_gap_classifier': 'No callable implementation identified in the received source.',
    'semantic_applicability_check': 'No executable check that learned advice applies to another task was identified.',
    'native_acceptance_and_promotion': 'Not connected: local pending storage is not native acceptance or promotion.',
}


def require_paid(allowed):
    if not allowed:
        raise RuntimeError('Paid operations disabled. Offline checks do not require keys.')


def yaml_module():
    try:
        import yaml
    except ImportError:
        # shortcut: reuse the installed review environment; install PyYAML normally on another machine.
        sys.path.append('/private/tmp/cognilife-review-env/lib/python3.12/site-packages')
        import yaml
    return yaml


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
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and names and n.target.id in names:
            nodes.append(n)
        elif isinstance(n, ast.ClassDef) and names and n.name in names:
            nodes.append(n)
    env = namespace if namespace is not None else {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), str(path), 'exec'), env)
    return env


def original_methods(path, class_name, names, namespace):
    cls = next(n for n in ast.parse(Path(path).read_text()).body if isinstance(n, ast.ClassDef) and n.name == class_name)
    nodes = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in names]
    exec(compile(ast.fix_missing_locations(ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), *nodes], type_ignores=[])), str(path), 'exec'), namespace)
    return namespace


class LocalSkills:
    def __init__(self, root, target, workflow):
        yaml = yaml_module()
        models = runpy.run_path(str(root/'models/skills.py'))
        registry = root/'skills/registry.py'
        env = load_functions(registry, {'_normalize_str_list', 'FRONTMATTER_ONLY_PATTERN'}, {
            're': re, 'yaml': yaml, 'logger': SilentLog(), **models,
        })
        original_methods(registry, 'BuiltinRegistry', {'_parse_frontmatter_only'}, env)
        original_methods(registry, 'SkillContext', {'build_discovery_prompt'}, env)
        cls = next(n for n in ast.parse(registry.read_text()).body if isinstance(n, ast.ClassDef) and n.name == 'SkillContext')
        self._DISCOVERY_SCOPE_ORDER = next(ast.literal_eval(n.value) for n in cls.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '_DISCOVERY_SCOPE_ORDER' for t in n.targets))
        self._discovery = env['build_discovery_prompt']
        self.paths = {'expert/'+p.parent.name: p for p in sorted(Path(target).parent.parent.glob('*/SKILL.md'))}
        self.paths['builtin/evolution'] = Path(workflow)
        self.texts = {n: p.read_text() for n, p in self.paths.items()}
        self.metas = {}
        for name, path in self.paths.items():
            meta = env['_parse_frontmatter_only'](self, path)
            if meta is None or meta.name != name.split('/', 1)[1]:
                raise ValueError('Invalid original skill metadata: '+name)
            self.metas[name] = meta.model_copy(update={'name': name})

    def build_discovery_prompt(self):
        return self._discovery(self)

    def get_enabled_skill_metas(self):
        return [m for m in self.metas.values() if m.enabled]

    def _all_metas(self):
        return self.metas

    def resolve_qualified_name(self, name):
        matches = [n for n in self.texts if self.metas[n].enabled and (n == name or n.split('/', 1)[1] == name)]
        return SimpleNamespace(status='resolved' if len(matches) == 1 else 'not_found', qualified_name=matches[0] if len(matches) == 1 else None)

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
    skills = LocalSkills(root, target, evo/'skills/evolution/SKILL.md')
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


def build_system(workspace, skills, functions, evolution_prompt):
    """Call the received static assembler; no replacement learning instructions."""
    root = Path(workspace)/'04_项目数据与代码/Profy-main/services/agent-runtime/src'
    fingerprint = runpy.run_path(str(root/'base/prompts/fingerprint.py'))
    env = {**fingerprint, '__file__': str(root/'harness/context/prompt.py'), '__name__': __name__,
           'Path': Path, 'dataclass': dataclass, '_re': re, 'logger': SilentLog(), '_HAS_TIKTOKEN': False}
    names = {'PromptLayer', 'ContextManager', 'PromptManager', 'STATIC_PIPELINE', '_PROMPTS_DIR',
             'SECURITY_CLOSING_REMINDER', 'DYNAMIC_BOUNDARY_MARKER', '_PLACEHOLDER_RE', '_encoding',
             'tag', 'read_prompt_file', 'count_tokens', '_get_encoding', '_render_template', '_skipped_placeholder'}
    env = load_functions(root/'harness/context/prompt.py', names, env)
    compose = runpy.run_path(str(root/'plugins/utils/static.py'))['compose_plugin_registry']
    descriptions = [SimpleNamespace(name=f.__name__, description=inspect.getdoc(f)) for f in functions]
    manager = object.__new__(env['ContextManager'])
    system, layers, counts = manager.build_static_prompt(
        tools_description=env['PromptManager'].format_tools(descriptions),
        skills_discovery=skills.build_discovery_prompt(),
        plugin_registry=compose(plugin_prompts=[('profy-evolution', evolution_prompt)]),
        working_directory='', web_workspace_dir='/home/user/workspace/web',
        sandbox_environment=False, desktop_environment=False, plan_mode=False,
    )
    return system, {'layers': layers.to_dict(), 'token_estimates': counts,
                    'token_counting': 'original heuristic fallback; not billed tokens'}


def development_messages(request, events):
    """Map recorded public DEV events to roleful messages, refusing incomplete calls."""
    messages = [{'role': 'user', 'content': request['input']}]
    pending, seen = {}, set()
    text = ''
    def flush_text():
        nonlocal text
        if text:
            if pending:
                raise ValueError('Assistant text while a tool result is missing')
            messages.append({'role': 'assistant', 'content': text})
            text = ''
    for event in events:
        kind = event.get('type')
        if kind == 'output.text.delta':
            text += event.get('delta') or ''
        elif kind == 'tool_call.in_progress':
            flush_text()
            cid = event['tool_call_id']
            if cid in seen or not isinstance(event.get('parameters'), dict):
                raise ValueError('Duplicate or incomplete tool call: '+cid)
            call = {'id': cid, 'type': 'function', 'function': {'name': event['tool_name'], 'arguments': json.dumps(event['parameters'], ensure_ascii=False)}}
            if pending:
                if 'tool_calls' not in messages[-1]:
                    raise ValueError('Interleaved new call before previous tool group completed')
                messages[-1]['tool_calls'].append(call)
            else:
                messages.append({'role': 'assistant', 'content': None, 'tool_calls': [call]})
            pending[cid] = event['tool_name']; seen.add(cid)
        elif kind == 'tool_call.result':
            cid = event['tool_call_id']
            if cid not in pending or pending[cid] != event.get('tool_name') or 'result' not in event:
                raise ValueError('Orphan or mismatched tool result: '+cid)
            value = event['result']
            messages.append({'role': 'tool', 'tool_call_id': cid, 'content': value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)})
            del pending[cid]
    flush_text()
    if pending:
        raise ValueError('Missing tool results: '+','.join(pending))
    return messages


def prepare_evolution(workspace, target, out, trajectory, metrics):
    gate, skill, config, store, stats, start, evolution_prompt = original_components(workspace, target, out)
    functions = [skill['skill'], gate['evolution_log']]
    system, context = build_system(workspace, config['configurable']['skill_context'], functions, evolution_prompt)
    histories = trajectory if isinstance(trajectory, list) else [trajectory]
    measurements = metrics if isinstance(metrics, list) else [metrics]
    if len(histories) != len(measurements) or not 1 <= len(measurements) <= 20:
        raise ValueError('Expected 1..20 matching DEV histories and measured run records')
    model_path = Path(workspace)/'04_项目数据与代码/Profy-main/services/agent-runtime/src/models/evolution.py'
    native_stats = runpy.run_path(str(model_path))['EvolutionRunStats']
    runs = [native_stats(run_index=i, **{k: m.get(k) for k in ['total_tokens', 'input_tokens', 'output_tokens', 'llm_turns', 'tool_calls']},
                        skill_chars=m.get('skill_chars', len(Path(target).read_text())), success=bool(m['strict']),
                        skill_version_note=m.get('skill_version_note', 'original SkillsBench skill')) for i, m in enumerate(measurements)]
    messages = [{'role': 'system', 'content': system}]
    for history in histories:
        messages.extend(development_messages(history['request'], history['events']))
    call_ids = [call['id'] for message in messages for call in message.get('tool_calls', [])]
    if len(call_ids) != len(set(call_ids)):
        raise ValueError('Tool call IDs collide across development histories')
    messages.append({'role': 'user', 'content': start+stats['_format_run_stats'](runs)})
    request = {'model': EVOLUTION_WIRE_MODEL, 'max_tokens': 6500, 'messages': messages,
               'tools': [tool_schema(f) for f in functions], 'tool_choice': 'auto'}
    provenance = {'model': EVOLUTION_MODEL, 'wire_model': EVOLUTION_WIRE_MODEL, 'endpoint': EVOLUTION_URL,
                  'parent_sha256': hashlib.sha256(Path(target).read_bytes()).hexdigest(),
                  'request_sha256': hashlib.sha256(json.dumps(request, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
                  'development_history_runs': len(runs),
                  'context': context, 'missing_implementations': MISSING_IMPLEMENTATIONS,
                  'history_adapter': 'public DEV SSE roles and complete tool-call/result pairs; not native DB replay'}
    return request, provenance, (gate, skill, config, store)


def tool_schema(fn):
    props, required = {}, []
    for name, p in inspect.signature(fn).parameters.items():
        if name == 'config':
            continue
        props[name] = {'type': 'object' if name.endswith('_scores') else 'string'}
        if p.default is inspect.Parameter.empty:
            required.append(name)
    return {'type': 'function', 'function': {'name': fn.__name__, 'description': inspect.getdoc(fn), 'parameters': {'type': 'object', 'properties': props, 'required': required, 'additionalProperties': False}}}


def evolution_http_request(body, key, end_user):
    if not end_user:
        raise ValueError('Evolution requires a stable run identifier')
    return urllib.request.Request(EVOLUTION_URL, data=json.dumps(body).encode(), headers={
        'Authorization': 'Bearer '+key, 'Content-Type': 'application/json',
        'X-Title': 'SkillsBench evolution '+end_user}, method='POST')


def evolve(workspace, target, out, trajectory, metrics, api_key, scrub, *, allow_paid=False):
    require_paid(allow_paid)
    out = Path(out); out.mkdir(exist_ok=True)
    if any(out.iterdir()):
        raise RuntimeError('Evolution directory must be new; preserve existing evidence')
    prepared, provenance, components = prepare_evolution(workspace, target, out, trajectory, metrics)
    gate, skill, config, store = components
    (out/'provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2))
    messages = prepared['messages']
    receipts = []
    began = time.monotonic()
    for turn in range(8):
        request = {**prepared, 'messages': messages}
        (out/f'request_{turn+1}.json').write_text(json.dumps(request, ensure_ascii=False, indent=2))
        req = evolution_http_request(request, api_key, 'sb-evolution-'+out.parent.name)
        try:
            with urllib.request.urlopen(req, timeout=180) as response:
                result = json.load(response)
        except urllib.error.HTTPError as exc:
            detail = scrub(exc.read(65536).decode(errors='replace'))
            (out/f'transport_error_{turn+1}.json').write_text(json.dumps({'status': exc.code, 'detail': detail}, ensure_ascii=False, indent=2))
            raise RuntimeError('Evolution HTTP '+str(exc.code)+'; saved error, no automatic retry') from None
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
                output = (asyncio.run(gate['evolution_log'](**args, config=config)) if args.get('skill_name') == Path(target).parent.name
                          else 'Error: this experiment only permits updating the preselected target skill.')
            else:
                output = 'Error: evolution is read-only except for the original evolution_log suggestion tool.'
            messages.append({'role': 'tool', 'tool_call_id': call['id'], 'content': output})
        if store.rows:
            break
    (out/'tool_transcript.json').write_text(json.dumps(messages, ensure_ascii=False, indent=2))
    summary = {'accepted_by_original_gate': bool(store.rows), 'model': EVOLUTION_MODEL, 'wire_model': EVOLUTION_WIRE_MODEL, 'endpoint': EVOLUTION_URL, 'requests': len(receipts), 'usage': receipts, 'elapsed_sec': round(time.monotonic()-began, 3), 'storage': 'external adapter local pending, not Profy database', 'source_functions_modified': False, 'native_promoted': False, 'semantic_applicability_verified': False, 'missing_implementations': MISSING_IMPLEMENTATIONS}
    (out/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    if not store.rows:
        return None, summary
    candidate = store.rows[0]['suggestion_content']['improved_content']
    if not candidate.strip() or len(candidate) > 60000:
        raise ValueError('Candidate transport/body invalid')
    (out/'candidate_SKILL.md').write_text(candidate)
    return candidate, summary
