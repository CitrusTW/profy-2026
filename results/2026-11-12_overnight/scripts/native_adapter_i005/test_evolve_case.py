import copy,unittest,argparse
import json,tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from evolve_case import improved,run
class EvolutionCaseChecks(unittest.TestCase):
    def test_failed_or_contaminated_case_cannot_be_selected_for_fewer_tokens(self):
        b={'task':'fixture','completed':True,'error':None,'output_received':True,'target_skill_read_verified':True,'condition_valid':True,'external_skill_tools_observed':[],'score':{'strict':1,'tests':2,'passed':2,'failed':0,'skipped':0,'original_source_before_after_verified':True},'tokens':{'total_tokens':100}}
        a=copy.deepcopy(b);a['tokens']['total_tokens']=95
        self.assertTrue(improved(a,b,'fixture'))
        a['condition_valid']=False
        self.assertFalse(improved(a,b,'fixture'))
        a['condition_valid']=True;a['score']['failed']=1
        self.assertFalse(improved(a,b,'fixture'))
        a=copy.deepcopy(b);a['tokens']['total_tokens']=96
        self.assertFalse(improved(a,b,'fixture'))
    def test_global_round_bounds_fail_before_any_model_call(self):
        for n in [9,31]:
            with self.assertRaises(AssertionError):run(argparse.Namespace(allow_paid=True,round=n))
    def test_different_validation_resources_rejected_before_evolution(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);base=root/'base';val=root/'val';base.mkdir();val.mkdir()
            target=root/'SKILL.md';target.write_text('original')
            row={'task':'validation-task','completed':True,'error':None,'output_received':True,'target_skill_read_verified':True,'condition_valid':True,'external_skill_tools_observed':[],'score':{'strict':1,'tests':1,'passed':1,'failed':0,'skipped':0,'original_source_before_after_verified':True}}
            (val/'result.json').write_text(json.dumps(row))
            for p,h in [(base,'one'),(val,'different')]:
                (p/'case_config.json').write_text(json.dumps({'skill_hashes':{'bench_skills/xlsx/recalc.py':h}}))
            args=argparse.Namespace(allow_paid=True,round=12,out=str(root/'rounds'),baseline=str(base),validation_baseline=str(val),task='dev-task')
            with patch('evolve_case.DockerStudy',return_value=SimpleNamespace(target=target,skill_name='xlsx')),patch('evolve_case.evolve') as model:
                with self.assertRaisesRegex(AssertionError,'resources differ'):run(args)
                model.assert_not_called()
if __name__=='__main__':unittest.main()
