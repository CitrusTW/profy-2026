"""Local trust-boundary and original-tool checks. Zero model calls."""
import asyncio
import io
import json
import tempfile
import unittest
import zipfile
import argparse
from unittest.mock import patch
from pathlib import Path

from native_evolution import original_components, tool_schema, prepare_evolution, development_messages, evolve, EVOLUTION_MODEL, EVOLUTION_WIRE_MODEL, EVOLUTION_URL, evolution_http_request
from candidate_check import check_candidate
from run import sha, unpack_output, Study, ProfyTransport, load_own_transport, replay_original_gate

WORKSPACE = Path(__file__).resolve().parents[3]
TARGET = WORKSPACE/'04_项目数据与代码/skillsbench/tasks/threejs-to-obj/environment/skills/threejs/SKILL.md'
OLD_RUN = WORKSPACE/'01_任务结果/2026-11-10_skillsbench_evolution/run-01'


class AdapterChecks(unittest.TestCase):
    def setUp(self):
        self.network = patch('urllib.request.urlopen', side_effect=AssertionError('Offline check attempted a network request'))
        self.network.start()
        self.addCleanup(self.network.stop)

    def test_evolution_http_requires_stable_end_user(self):
        request = evolution_http_request({'model': EVOLUTION_MODEL}, 'synthetic-key', 'fixture-run-id')
        self.assertIn('fixture-run-id', request.get_header('X-title'))
        self.assertEqual(request.full_url, EVOLUTION_URL)
        self.assertEqual(json.loads(request.data)['model'], EVOLUTION_MODEL)
        with self.assertRaises(ValueError):
            evolution_http_request({}, 'synthetic-key', '')

    def test_original_context_and_development_history(self):
        result = json.loads((OLD_RUN/'dev_original/result.json').read_text())
        trajectory = {'request': json.loads((OLD_RUN/'dev_original/request.json').read_text()),
                      'events': [json.loads(s) for s in (OLD_RUN/'dev_original/events.jsonl').read_text().splitlines()]}
        metrics = {**result['tokens'], 'strict': result['score']['strict']}
        original_read = Path.read_text
        def dev_only(path, *a, **kw):
            if 'threejs-structure-parser' in path.parts or 'with-CogniLife-skills' in path.parts:
                raise AssertionError('Validation evidence was read during evolution preparation')
            return original_read(path, *a, **kw)
        with tempfile.TemporaryDirectory() as tmp, patch.object(Path, 'read_text', dev_only):
            request, provenance, components = prepare_evolution(WORKSPACE, TARGET, tmp, trajectory, metrics)
            again, provenance2, _ = prepare_evolution(WORKSPACE, TARGET, tmp, trajectory, metrics)
        self.assertEqual(request, again)
        self.assertEqual(provenance, provenance2)
        self.assertEqual(request['model'], EVOLUTION_WIRE_MODEL)
        self.assertEqual(provenance['endpoint'], EVOLUTION_URL)
        self.assertNotIn('gpt-4.1', json.dumps(request))
        system = request['messages'][0]['content']
        for name in ['security_fence', 'identity', 'soul', 'tool_calling', 'workflow', 'plugin_registry', 'skill_registry']:
            self.assertIsNotNone(provenance['context']['layers'][name])
        self.assertIn('expert/obj-exporter', system)
        self.assertIn('expert/threejs', system)
        self.assertTrue(system.endswith('<!-- BEGIN_DYNAMIC -->'))
        self.assertEqual(request['messages'][1], {'role': 'user', 'content': trajectory['request']['input']})
        calls = [c for m in request['messages'] for c in m.get('tool_calls', [])]
        results = [m for m in request['messages'] if m['role'] == 'tool']
        self.assertEqual(len(calls), 9)
        self.assertEqual([c['id'] for c in calls], [m['tool_call_id'] for m in results])
        self.assertFalse(components[3].rows)

    def test_history_rejects_missing_duplicate_and_orphan_results(self):
        call = {'type': 'tool_call.in_progress', 'tool_call_id': 'c1', 'tool_name': 'read', 'parameters': {'path': 'public.txt'}}
        result = {'type': 'tool_call.result', 'tool_call_id': 'c1', 'tool_name': 'read', 'result': 'fixture'}
        for events in [[call], [result], [call, call], [call, {**result, 'tool_name': 'write'}]]:
            with self.subTest(events=events), self.assertRaises(ValueError):
                development_messages({'input': 'fixture'}, events)
        valid = development_messages({'input': 'fixture'}, [call, result])
        self.assertEqual(valid[-1]['content'], 'fixture')

    def test_paid_entry_points_disabled_before_keys_or_attempt_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = argparse.Namespace(workspace=str(WORKSPACE), out=tmp, keys_file='/not-a-real-key-file', allow_paid=False)
            study = Study(args)
            for operation in [lambda: study.transport, lambda: study.solve('disabled', 'threejs-to-obj'), study.evolve,
                              lambda: evolve(None, None, None, None, None, None, None)]:
                with self.assertRaisesRegex(RuntimeError, 'Paid operations disabled'):
                    operation()
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_old_candidate_cannot_be_relabelled_as_new_model(self):
        result = check_candidate(OLD_RUN, TARGET)
        self.assertFalse(result['structural_and_dev_pass'])
        self.assertIn('configured_evolver_model', result['failed_checks'])
        self.assertTrue(result['checks']['candidate_matches_pending'])
        self.assertFalse(result['semantic_applicability_verified'])
        self.assertEqual(result['measured_development']['total_tokens']['delta'], 9348)

    def test_frozen_payload_original_gate_replay(self):
        result = replay_original_gate(WORKSPACE, TARGET, OLD_RUN/'evolution/pending.json')
        self.assertTrue(result['original_gate_admitted'])
        self.assertTrue(result['suggestion_content_unchanged'])

    def test_candidate_lineage_corruption_and_execution_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'evolution').mkdir()
            body = '---\nname: threejs\ndescription: fixture only\n---\nFixture only.\n'
            (root/'evolution/candidate_SKILL.md').write_text(body)
            def write(path, value):
                path.parent.mkdir(exist_ok=True)
                path.write_text(json.dumps(value))
            write(root/'evolution/pending.json', {'suggestion_content': {'skill_name': 'threejs', 'improved_content': body}})
            write(root/'evolution/summary.json', {'model': EVOLUTION_MODEL, 'endpoint': EVOLUTION_URL, 'accepted_by_original_gate': True})
            request = {'model': EVOLUTION_WIRE_MODEL, 'messages': [{'role': 'user', 'content': 'synthetic fixture only'}]}
            write(root/'evolution/request_1.json', request)
            write(root/'evolution/provenance.json', {'model': EVOLUTION_MODEL, 'endpoint': EVOLUTION_URL, 'parent_sha256': sha(TARGET.read_bytes()), 'request_sha256': sha(json.dumps(request, ensure_ascii=False, sort_keys=True).encode())})
            base = {'task': 'threejs-to-obj', 'completed': True, 'error': None, 'output_received': True,
                    'target_skill_read_verified': True, 'external_skill_tools_observed': [],
                    'score': {'tests': 3, 'passed': 3, 'failed': 0, 'skipped': 0, 'strict': 1, 'original_returncode': 0}}
            write(root/'dev_original/result.json', {**base, 'skill_sha256': sha(TARGET.read_bytes())})
            write(root/'dev_candidate/result.json', {**base, 'skill_sha256': sha(body.encode())})
            result = check_candidate(root, TARGET)
            self.assertTrue(result['structural_and_dev_pass'])
            self.assertFalse(result['full_paper_method_verified'])
            write(root/'evolution/request_1.json', {**request, 'model': 'openai/gpt-4.1'})
            self.assertFalse(check_candidate(root, TARGET)['checks']['recorded_request_model'])
            write(root/'evolution/request_1.json', request)
            (root/'evolution/candidate_SKILL.md').write_text(body+'tampered')
            result = check_candidate(root, TARGET)
            self.assertFalse(result['checks']['candidate_matches_pending'])
            self.assertFalse(result['checks']['dev_candidate skill read'])
            (root/'evolution/candidate_SKILL.md').write_text(body)
            write(root/'dev_candidate/result.json', {**base, 'skill_sha256': sha(body.encode()), 'completed': False, 'error': 'timeout'})
            self.assertFalse(check_candidate(root, TARGET)['checks']['dev_candidate execution'])

    def test_transport_needs_no_openrouter_key_and_redacts_secrets(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'synthetic-keys.md'
            path.write_text('sk-pro-fixture-value\nexpert identifier: fixture-id')
            transport = ProfyTransport(load_own_transport(WORKSPACE), path)
            self.assertEqual(transport.expert_id, 'fixture-id')
            self.assertEqual(transport.scrub({'k': 'sk-pro-fixture-value sk-or-fixture-value'}), {'k': '[REDACTED] [REDACTED]'})

    def test_original_tools_and_gate(self):
        target = WORKSPACE/'04_项目数据与代码/skillsbench/tasks/threejs-to-obj/environment/skills/threejs/SKILL.md'
        with tempfile.TemporaryDirectory() as tmp:
            gate, skill, config, store, stats, start, system = original_components(WORKSPACE, target, tmp)
            activate = asyncio.run(skill['skill'](action='activate', name='expert/threejs', config=config))
            self.assertIn(target.read_text(), activate)
            self.assertIn('expert/threejs', asyncio.run(skill['skill'](action='discover', config=config)))
            self.assertIn('evolution mode', system)
            self.assertIn('builtin/evolution', start)
            self.assertEqual(tool_schema(gate['evolution_log'])['function']['name'], 'evolution_log')
            dims = list(gate['QUALITY_DIMENSIONS'])+['step_economy', 'exploration_replacement']
            scores = {d: 50 for d in dims}
            base = dict(action='suggest_skill_improvement', skill_name='threejs', summary='fixture', diff_summary='fixture', improved_content='fixture', before_scores=scores, improved_dimensions='step_economy', config=config)
            rejected = asyncio.run(gate['evolution_log'](**base, after_scores={**scores, 'workflow_clarity': 0, 'step_economy': 100}))
            self.assertIn('quality regression', rejected)
            self.assertFalse(store.rows)
            accepted = asyncio.run(gate['evolution_log'](**base, after_scores={**scores, 'step_economy': 100}))
            self.assertIn('Suggestion submitted', accepted)
            row = store.rows[0]['suggestion_content']
            self.assertEqual(row['rubric_scores']['before']['context_footprint'], gate['_context_footprint_score'](len(target.read_text())))

    def test_lossless_output_and_path_rejection(self):
        payload = b'v 1 2 3\nf 1 2 3\n'
        for bad in [False, True]:
            stream = io.BytesIO()
            with zipfile.ZipFile(stream, 'w') as z:
                name = '../escape.obj' if bad else 'output/object.obj'
                z.writestr(name, payload)
                z.writestr('manifest.json', json.dumps({'input_sha256': 'fixture', 'files': {name: sha(payload)}}))
            with tempfile.TemporaryDirectory() as tmp:
                if bad:
                    with self.assertRaises(AssertionError): unpack_output(stream.getvalue(), Path(tmp))
                else:
                    unpack_output(stream.getvalue(), Path(tmp))
                    self.assertEqual((Path(tmp)/'output/object.obj').read_bytes(), payload)


if __name__ == '__main__': unittest.main()
