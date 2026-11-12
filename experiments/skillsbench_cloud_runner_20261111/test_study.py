import io,tarfile,unittest
from study import archive_rows,host_command_kind
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
    def test_cloud_script_refuses_local_execution(self):
        with self.assertRaisesRegex(RuntimeError,'Cloud-only'):cloud_only()

if __name__=='__main__':unittest.main()
