import json,tempfile,unittest,zipfile
from pathlib import Path
from checkpoint_xlsx import checkpoint

class CheckpointTests(unittest.TestCase):
    def test_keeps_model_answer_and_skill_but_excludes_received_code_and_gold(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'round-12';e=root/'evolution';e.mkdir(parents=True)
            (e/'candidate_SKILL.md').write_text('new candidate')
            (e/'request_0.json').write_text('RECEIVED_PROMPT_BODY')
            (e/'provenance.json').write_text(json.dumps({'context':'RECEIVED_CONTEXT_BODY'}))
            parent=root/'parent_skills/xlsx';parent.mkdir(parents=True)
            (parent/'SKILL.md').write_text('old candidate');(parent/'recalc.py').write_text('RECEIVED_PROGRAM_BODY')
            phase=root/'development/with-CogniLife-skills';phase.mkdir(parents=True)
            (phase/'run_summary.json').write_text('{}')
            out=phase/'grading-only/output/fs/root';out.mkdir(parents=True)
            (out/'gdp.xlsx').write_bytes(b'ACTUAL_MODEL_ANSWER')
            (phase/'grading-only/output/original_verifier_stdout.log').write_text('HIDDEN_TEST_SOURCE_BODY')
            payload=json.loads(checkpoint(root,Path(d)/'export').read_text())
            with zipfile.ZipFile(payload['binary_entries'][0]['local_path']) as z:
                content=b'\n'.join(z.read(n) for n in z.namelist())
                self.assertIn(b'ACTUAL_MODEL_ANSWER',content)
                for marker in [b'RECEIVED_PROMPT_BODY',b'RECEIVED_CONTEXT_BODY',b'RECEIVED_PROGRAM_BODY',b'HIDDEN_TEST_SOURCE_BODY']:self.assertNotIn(marker,content)
            self.assertTrue(any(e['path'].endswith('/SKILL.md') and e['content']=='new candidate' for e in payload['text_entries']))
