import base64
import gzip
import unittest
from pilot import decode_file, exported_file, proposal_gate, public_writer_evidence, shared_experience, sha, tool_calls

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

    def test_old_experience_packet_does_not_replace_current_export(self):
        def packet(raw):
            data=base64.b64encode(gzip.compress(raw)).decode()
            return f'PILOT_SHA256:{sha(raw)}\nPILOT_BYTES:{len(raw)}\nPILOT_PART_1_OF_1:{data}'
        old,current=b'{"old":1}',b'{"current":2}'
        events=[{'type':'tool_call.result','tool_name':'read','result':packet(old)},
                {'type':'tool_call.result','tool_name':'bash','result':packet(current)},
                {'type':'output.text.delta','delta':'SHA256: `'+sha(current)+'`'}]
        self.assertEqual(exported_file(events),current)

    def test_native_tool_events_are_deduplicated(self):
        events=[{'type':'tool_call.in_progress','tool_call_id':'one','tool_name':'bash'},
                {'type':'tool_call.in_progress','tool_call_id':'one','tool_name':'bash'},
                {'type':'tool_call.in_progress','tool_call_id':'two','tool_name':'read'}]
        self.assertEqual(tool_calls(events),['bash','read'])

    def test_shared_experience_excludes_skill_text_and_old_export(self):
        result = {'completed':True,'error':None,'elapsed_sec':1,'tool_names':['read'],
                  'output_received':True,'observed_tool_results':['PRIVATE_SKILL PILOT_PART'],
                  'score':{'hidden_answer':'DO_NOT_SEND'}}
        shared = shared_experience('PUBLIC TASK',result)
        self.assertNotIn('PRIVATE_SKILL',str(shared))
        self.assertNotIn('PILOT_PART',str(shared))
        self.assertNotIn('DO_NOT_SEND',str(shared))

if __name__ == '__main__':
    unittest.main()
