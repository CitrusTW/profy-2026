"""Offline checks of DEV-only iteration boundaries; all trajectories here are fixtures."""
import asyncio
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from native_evolution import original_components, prepare_evolution
from iterate import evidence, eligible

WORKSPACE = Path(__file__).resolve().parents[3]
DEV = 'threejs-to-obj'
TARGET = WORKSPACE/'04_项目数据与代码/skillsbench/tasks'/DEV/'environment/skills/threejs/SKILL.md'


def history(index, task=DEV):
    call_id = 'synthetic-'+str(index)
    return {'request': {'input': 'Public DEV fixture: '+task}, 'events': [
        {'type': 'tool_call.in_progress', 'tool_call_id': call_id, 'tool_name': 'read', 'parameters': {'path': 'public-input.txt'}},
        {'type': 'tool_call.result', 'tool_call_id': call_id, 'tool_name': 'read', 'result': 'Synthetic public development content.'},
        {'type': 'output.text.delta', 'delta': 'Synthetic completed development.'},
    ]}


def measurement(chars, note, tokens=100):
    return {'strict': 1, 'skill_chars': chars, 'skill_version_note': note, 'total_tokens': tokens,
            'input_tokens': tokens-10, 'output_tokens': 10, 'llm_turns': 1, 'tool_calls': 1}


class IterativeChecks(unittest.TestCase):
    def setUp(self):
        self.block_network = patch('urllib.request.urlopen', side_effect=AssertionError('Offline tests must not call a provider'))
        self.block_network.start()
        self.addCleanup(self.block_network.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.target = self.folder/'parent_skills/threejs/SKILL.md'
        self.target.parent.mkdir(parents=True)
        self.original = TARGET.read_text()
        self.parent = self.original+'\n<!-- Synthetic parent-version fixture '+('x'*2000)+' -->\n'
        self.target.write_text(self.parent)

    def test_multi_history_keeps_each_versions_measured_stats(self):
        metrics = [measurement(len(self.original), 'original hash-fixture'),
                   measurement(len(self.parent), 'rejected proposal hash-fixture', 200)]
        request, provenance, _ = prepare_evolution(WORKSPACE, self.target, self.folder,
                                                   [history(0), history(1)], metrics)
        stats = request['messages'][-1]['content']
        self.assertIn(f'Run 0 (skill ~{len(self.original)} chars) [original hash-fixture]', stats)
        self.assertIn(f'Run 1 (skill ~{len(self.parent)} chars) [rejected proposal hash-fixture]', stats)
        self.assertIn('total_tokens=100', stats)
        self.assertIn('total_tokens=200', stats)
        self.assertEqual(provenance['development_history_runs'], 2)
        self.assertEqual(provenance['parent_sha256'], hashlib.sha256(self.parent.encode()).hexdigest())
        self.assertEqual(sum(m['role']=='tool' for m in request['messages']), 2)

    def test_native_stats_limits_and_history_count(self):
        for histories, measurements in [([], []), ([history(0)], []),
                                          ([history(i) for i in range(21)], [measurement(100, 'fixture')]*21),
                                          ([history(0)], [measurement(100, 'fixture', 10_000_001)]),
                                          ([history(0)], [measurement(100, 'x'*121)])]:
            with self.subTest(count=len(measurements)), self.assertRaises(ValueError):
                prepare_evolution(WORKSPACE, self.target, self.folder, histories, measurements)

    def test_original_gate_fetches_current_parent_not_benchmark_original(self):
        gate, _, config, store, *_ = original_components(WORKSPACE, self.target, self.folder)
        scores = {d: 50 for d in list(gate['QUALITY_DIMENSIONS'])+['step_economy', 'exploration_replacement']}
        asyncio.run(gate['evolution_log'](action='suggest_skill_improvement', skill_name='threejs', summary='Synthetic fixture',
            diff_summary='Synthetic fixture', improved_content='Synthetic proposed content', before_scores=scores,
            after_scores={**scores, 'step_economy': 100}, improved_dimensions='step_economy', config=config))
        self.assertEqual(len(store.rows), 1)
        actual = store.rows[0]['suggestion_content']['rubric_scores']['before']['context_footprint']
        self.assertEqual(actual, gate['_context_footprint_score'](len(self.parent)))
        self.assertNotEqual(actual, gate['_context_footprint_score'](len(self.original)))

    def test_nondev_receipt_rejected_before_reading_its_history(self):
        folder = self.folder/'nondev-fixture'; folder.mkdir()
        (folder/'result.json').write_text(json.dumps({'task': 'threejs-structure-parser'}))
        with self.assertRaisesRegex(ValueError, 'Only DEV'):
            evidence(folder, 'Synthetic fixture')

    def test_nondev_input_marker_rejected_from_dev_receipt(self):
        folder = self.folder/'contaminated-dev-fixture'; folder.mkdir()
        text = 'Synthetic fixture'
        row = {'task': DEV, 'completed': True, 'output_received': True, 'target_skill_read_verified': True,
               'error': None, 'external_skill_tools_observed': [], 'skill_sha256': hashlib.sha256(text.encode()).hexdigest()}
        (folder/'result.json').write_text(json.dumps(row))
        (folder/'request.json').write_text(json.dumps(history(0, 'threejs-structure-parser')['request']))
        (folder/'events.jsonl').write_text('')
        with self.assertRaises(ValueError):
            evidence(folder, text)

    def test_tool_ids_cannot_collide_across_histories(self):
        with self.assertRaises(ValueError):
            prepare_evolution(WORKSPACE, self.target, self.folder,
                              [history(0), history(0)], [measurement(100, 'fixture')]*2)

    def test_selection_requires_real_output_and_complete_pass(self):
        row = {'task': DEV, 'score': {'strict': 1, 'skipped': 0, 'tests': 3, 'passed': 3, 'failed': 0, 'original_returncode': 0},
               'completed': True, 'error': None, 'target_skill_read_verified': True,
               'external_skill_tools_observed': [], 'output_received': True, 'tokens': {'total_tokens': 90}}
        self.assertTrue(eligible(row, 100))
        self.assertFalse(eligible({**row, 'output_received': False}, 100))
        self.assertFalse(eligible({**row, 'score': {**row['score'], 'tests': 0, 'passed': 0}}, 100))


if __name__ == '__main__':
    unittest.main()
