import io,tarfile,unittest,tempfile
from unittest.mock import patch
from pathlib import Path
from prebuilt_catalog import catalog,BUILDER
from remote_native import root_file,execute
from study import archive_rows,host_command_kind,setup_receipts,forbidden_skill_read
from remote_setup import cloud_only

class StudyTests(unittest.TestCase):
    def test_data_archive_contains_no_skill_body_and_preserves_modes(self):
        data=archive_rows([('Dockerfile',b'FROM ubuntu:24.04\n',0o644),('run.sh',b'echo ok\n',0o755),('skills/x/SKILL.md',b'PRIVATE CONDITION',0o644)],empty_skills=True)
        with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as t:
            self.assertEqual(set(t.getnames()),{'Dockerfile','run.sh','skills'})
            self.assertEqual(t.getmember('run.sh').mode,0o755)
            self.assertEqual(t.extractfile('run.sh').read(),b'echo ok\n')
    def test_heredoc_keeps_commands_inside_container(self):
        self.assertEqual(host_command_kind("python3 remote_tools.py exec <<'SB_COMMAND'\npython -c 'print(1)'\nSB_COMMAND"),'container')
        self.assertIsNone(host_command_kind('python3 remote_tools.py exec <<SB_COMMAND\necho hi\nSB_COMMAND'))
        self.assertIsNone(host_command_kind("python3 remote_tools.py exec <<'SB_COMMAND'\necho hi\nSB_COMMAND\ncat /etc/passwd\nSB_COMMAND"))
        self.assertIsNone(host_command_kind('python3 remote_setup.py; cat /etc/passwd'))
    def test_prebuilt_catalog_rejects_changed_source(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for name in ['same','changed']:
                p=root/'tasks'/name;p.mkdir(parents=True);(p/'task.md').touch()
            remote={'tree':[{'path':'tasks/'+n+'/environment','sha':('good' if n=='same' else 'different'),'type':'tree'} for n in ['same','changed']]}
            tags={'tags':['skillsbench-v1.1-'+n+'-'+BUILDER[:12] for n in ['same','changed']]}
            with patch('prebuilt_catalog.get',side_effect=[remote,{'token':'anonymous-test'},tags]),patch('prebuilt_catalog.subprocess.check_output',return_value='good'):
                row=catalog(root)
            self.assertEqual(row['matching_and_available'],1)
            self.assertFalse(row['image_layers_downloaded'])
            self.assertEqual(row['model_calls'],0)
    def test_ready_receipt_can_arrive_from_background_await(self):
        result={'type':'tool_call.result','tool_name':'awaitbash','result':'CGL_CASE_READY:{"task":"example"}'}
        self.assertEqual(setup_receipts([result,result],lambda x:[x]),[{'task':'example'}])
        self.assertEqual(setup_receipts([{'type':'output.text.delta','result':result['result']}],lambda x:[x]),[])
        truncated={**result,'result':'CGL_CASE_READY:{"task":"exam'}
        self.assertEqual(setup_receipts([truncated],lambda x:[x]),[])
    def test_plain_read_cannot_silently_import_builtin_skill(self):
        event=lambda p:{'tool_name':'read','parameters':{'file_path':p}}
        self.assertTrue(forbidden_skill_read(event('/mnt/skills/public/xlsx/SKILL.md'),True,['xlsx']))
        self.assertTrue(forbidden_skill_read(event('/mnt/skills/public/xlsx/SKILL.md'),False,['xlsx']))
        self.assertFalse(forbidden_skill_read(event('/home/user/workspace/bench_skills/xlsx/SKILL.md'),False,['xlsx']))
        self.assertTrue(forbidden_skill_read(event('bench_skills/xlsx/../other/SKILL.md'),False,['xlsx']))
    def test_native_export_cannot_escape_task_root(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'root';root.mkdir();(root/'gdp.xlsx').touch()
            self.assertEqual(root_file({'work':d},'/root/gdp.xlsx'),root/'gdp.xlsx')
            with self.assertRaises(AssertionError):root_file({'work':d},'/root/../etc/passwd')
            (root/'link').symlink_to('/etc/passwd')
            with self.assertRaises(AssertionError):root_file({'work':d},'/root/link')
    def test_native_no_skill_blocks_shell_import_before_execution(self):
        with self.assertRaisesRegex(RuntimeError,'extra skill access refused'):
            execute(Path('/not-used'),{'skill_sha256':None},'exec','cat /mnt/skills/public/xlsx/SKILL.md')
    def test_cloud_script_refuses_local_execution(self):
        with self.assertRaisesRegex(RuntimeError,'Cloud-only'):cloud_only()

if __name__=='__main__':unittest.main()
