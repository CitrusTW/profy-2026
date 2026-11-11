"""Local trust-boundary and original-tool checks. Zero model calls."""
import asyncio
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from native_evolution import original_components, tool_schema
from run import sha, unpack_output

WORKSPACE = Path(__file__).resolve().parents[3]


class AdapterChecks(unittest.TestCase):
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
