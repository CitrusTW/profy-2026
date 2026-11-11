import argparse
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from network_family import NetworkStudy, DEV, TEST
from iterate import evidence
from run import Study, sha
from native_evolution import require_paid


class NetworkTests(unittest.TestCase):
    def test_latest_stop_overrides_old_allow_paid_flag(self):
        with patch('native_evolution.Path.exists',return_value=True):
            with self.assertRaisesRegex(RuntimeError,'latest user instruction'):
                require_paid(True)

    def test_no_skills_adapter_does_not_include_skill_instructions(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);s=root/'04_项目数据与代码/skillsbench/tasks'/DEV/'environment/skills/economic-dispatch/SKILL.md'
            s.parent.mkdir(parents=True);s.write_text('only public skill')
            with patch('run.load_own_transport',return_value=argparse.Namespace(strings=lambda value: [])):
                study=NetworkStudy(argparse.Namespace(workspace=d,out=d,allow_paid=False))
            setup,common=study.instructions(DEV,True)
            self.assertNotIn('bench_skills',setup+common)
            setup,common=study.instructions(DEV,False)
            self.assertIn('bench_skills/economic-dispatch/SKILL.md',setup)
            self.assertNotIn(TEST,setup+common)
            self.assertEqual(study.input_file(DEV)[1],'network.json')

    def test_general_evidence_rejects_evaluation_task(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'result.json').write_text(json.dumps({'task':TEST}))
            with self.assertRaises(ValueError):evidence(p,'skill',DEV,TEST)

    def test_threejs_transport_instructions_preserved(self):
        study=object.__new__(Study)
        setup,common=study.instructions('threejs-to-obj',False)
        self.assertIn('three@0.175.0',common)
        self.assertIn('data/object.js',common)
        self.assertIn('bench_skills/threejs/SKILL.md',setup)
        self.assertNotIn('network.json',common)


if __name__=='__main__':unittest.main()
