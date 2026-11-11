import base64
import gzip
import unittest
from pilot import decode_file, proposal_gate, public_writer_evidence, sha

class PilotTests(unittest.TestCase):
    def test_output_transport_requires_exact_hash(self):
        raw = b'{"value": 7}'
        encoded = base64.b64encode(gzip.compress(raw)).decode()
        packet = f'PILOT_SHA256:{sha(raw)}\nPILOT_BYTES:{len(raw)}\nPILOT_PART_1_OF_1:{encoded}'
        self.assertEqual(decode_file([packet]),raw)
        with self.assertRaises(ValueError):
            decode_file([packet.replace(sha(raw),'0'*64)])

    def test_conflicting_parts_rejected(self):
        with self.assertRaises(ValueError):
            decode_file(['PILOT_PART_1_OF_1:YWJj','PILOT_PART_1_OF_1:ZGVm'])

    def test_gate_cannot_hide_quality_drop(self):
        before = {'tests':10,'passed':10}
        self.assertFalse(proposal_gate(before,{'tests':10,'passed':9},'long content','short')['accepted'])
        self.assertFalse(proposal_gate(before,before,'same','same')['accepted'])
        self.assertTrue(proposal_gate(before,before,'long content','short')['accepted'])
        self.assertFalse(proposal_gate({'tests':0,'passed':0},{'tests':0,'passed':0},'long','x')['accepted'])

    def test_writer_cannot_receive_private_fields(self):
        score = {'tests':2,'passed':1,'failed':1,'strict':0,'private':'DO_NOT_SEND'}
        experience = {'public_task':'PUBLIC TASK','run_completed':True,'elapsed_sec':4,
                      'tools':['read'],'observed_tool_results':['PRIVATE_EXPERT_TEXT'],
                      'private_expert':'DO_NOT_SEND'}
        payload = public_writer_evidence(score,experience,1000)
        self.assertNotIn('PRIVATE',str(payload))
        self.assertNotIn('DO_NOT_SEND',str(payload))
        self.assertEqual(payload['execution_metrics']['tool_call_count'],1)

if __name__ == '__main__':
    unittest.main()
