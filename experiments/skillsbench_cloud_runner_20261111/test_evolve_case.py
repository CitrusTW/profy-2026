import copy,unittest,argparse
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
if __name__=='__main__':unittest.main()
