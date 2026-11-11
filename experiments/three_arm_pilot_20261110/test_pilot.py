import base64
import gzip
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch
from pilot import DEV, INPUTS, SKILL, Pilot, candidate_document, decode_file, exported_file, proposal_gate, public_writer_evidence, shared_experience, sha, skill_read_evidence, tool_calls
from report_v2 import invoice_diagnostic

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

    def test_long_proposal_gets_one_bounded_revision_before_development(self):
        def response(body):
            return io.BytesIO(json.dumps({'choices':[{'message':{'content':json.dumps({'body':body,'rationale':'fixture'})}}]}).encode())
        with tempfile.TemporaryDirectory() as temp:
            pilot = Pilot.__new__(Pilot)
            pilot.out = Path(temp)
            pilot.router_key = 'TEST_CREDENTIAL_NOT_REAL'
            pilot.scrub = lambda value:value
            before = {'score':{'tests':1,'passed':1,'failed':0,'strict':1}}
            experience = {'public_task':'PUBLIC TASK','run_completed':True,'elapsed_sec':1,'tools':[]}
            old = 'PRIVATE_ORIGINAL_SKILL_TEXT\n'*10
            with patch('pilot.urllib.request.urlopen',side_effect=[response('x'*1000),response('Compare by stable IDs; preserve evidence.')]) as request:
                candidate = pilot.propose(before,old,experience)
            self.assertEqual(request.call_count,2)
            self.assertLess(len(candidate.encode()),len(old.encode()))
            second = json.loads((pilot.out/'writer_request_2.json').read_text())
            self.assertIn('UTF-8 bytes',second['messages'][-1]['content'])
            self.assertNotIn('PRIVATE_ORIGINAL_SKILL_TEXT',str(second))
            self.assertTrue((pilot.out/'candidate_rejection_1.json').exists())

    def test_invalid_update_stops_before_any_heldout_test(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            pilot=Pilot.__new__(Pilot)
            pilot.out=root/'results'; pilot.out.mkdir()
            pilot.bench=root/'tasks'; pilot.expert=root/'expert'; pilot.dev_inputs=root/'dev'
            skill=pilot.expert/SKILL; skill.parent.mkdir(parents=True); skill.write_text('initial skill')
            for task,names in INPUTS.items():
                folder=pilot.dev_inputs if task==DEV else pilot.bench/task/'environment'
                folder.mkdir(parents=True)
                for name in names: (folder/name).write_bytes(b'fixture')
            taskfile=pilot.bench/DEV/'task.md'; taskfile.parent.mkdir(parents=True)
            taskfile.write_text('---\nname: fixture\n---\nPUBLIC TASK')
            pilot.reservations=1
            pilot.solve=Mock(return_value={'score':{'tests':1,'passed':1},'completed':True,
                                          'error':None,'elapsed_sec':1,'tool_names':[],'output_received':True})
            pilot.propose=Mock(side_effect=ValueError('candidate rejected'))
            with redirect_stdout(io.StringIO()): pilot.run()
            self.assertEqual(pilot.solve.call_count,1)
            summary=json.loads((pilot.out/'summary.json').read_text())
            self.assertEqual(summary['status'],'stopped_before_heldout_test')
            self.assertEqual(summary['test_results'],[])
            self.assertFalse((pilot.out/'frozen_test_configuration.json').exists())

    def test_runtime_skill_requires_exact_read_and_computed_hash(self):
        skill='A new reusable procedure.'
        events=[{'type':'tool_call.result','tool_name':'read','tool_call_id':'read-one',
                 'result':{'file_path':'/session/expert/'+SKILL,'content':{'data':skill}}},
                {'type':'tool_call.result','tool_name':'bash','result':{'content':{'data':'PILOT_ACTIVE_SKILL_SHA256:'+sha(skill.encode())}}}]
        self.assertTrue(skill_read_evidence(events,skill)['verified'])
        self.assertFalse(skill_read_evidence(events,'Different old skill')['verified'])
        self.assertFalse(skill_read_evidence(events[:1],skill)['verified'])

    def test_report_diagnostic_keeps_original_output_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp); (folder/'scoring_only').mkdir()
            reference=[{'invoice_page_number':1,'reason':'Issue','po_number':None},
                       {'invoice_page_number':2,'reason':'Issue','po_number':'x'},
                       {'invoice_page_number':3,'reason':'Clean','po_number':'y'}]
            actual=[{'invoice_page_number':1,'reason':'Issue','po_number':'invalid'},
                    {'invoice_page_number':3,'reason':'Issue','po_number':'y'}]
            (folder/'scoring_only/ground_truth.json').write_text(json.dumps(reference))
            output=folder/'fraud_report.json'; output.write_text(json.dumps(actual))
            before=output.read_bytes(); diagnostic=invoice_diagnostic(folder)
            self.assertEqual(diagnostic['missed_pages'],1)
            self.assertEqual(diagnostic['extra_pages'],1)
            self.assertEqual(diagnostic['exact_field_differences'],{'po_number':1})
            self.assertEqual(output.read_bytes(),before)

    def test_candidate_rejects_development_only_instructions(self):
        for body in ['Write /root/diff_report.json','Compare employee fields','Prepare the HR report']:
            with self.assertRaisesRegex(ValueError,'GENERAL record-reconciliation'):
                candidate_document(body,'x'*2000)

if __name__ == '__main__':
    unittest.main()
