import unittest
from library_tasks import LibraryStudy
from run import attached_skill_read,target_file_read

class LibraryTests(unittest.TestCase):
    def test_target_reader_requires_expected_attached_path(self):
        self.assertTrue(target_file_read({'tool_name':'read','parameters':{'file_path':'/session/bench_skills/mesh-analysis/SKILL.md'}},'mesh-analysis'))
        self.assertFalse(target_file_read({'tool_name':'read','parameters':{'file_path':'/native/mesh-analysis/SKILL.md'}},'mesh-analysis'))
        self.assertFalse(target_file_read({'tool_name':'read','parameters':{'file_path':'/session/bench_skills/other/SKILL.md'}},'mesh-analysis'))
    def test_only_attached_file_reader_is_allowed(self):
        e={'tool_name':'skills_read','parameters':{'package':'/session/bench_skills/mesh-analysis'}}
        self.assertTrue(attached_skill_read(e,False,{'mesh-analysis'}));self.assertFalse(attached_skill_read(e,True,{'mesh-analysis'}))
        e['parameters']['package']='/native/skills/mesh-analysis'
        self.assertFalse(attached_skill_read(e,False,{'mesh-analysis'}))
        e['parameters']['package']='/session/bench_skills/../mesh-analysis'
        self.assertFalse(attached_skill_read(e,False,{'mesh-analysis'}))
    def test_no_skill_prompt_has_no_skill_file(self):
        s=object.__new__(LibraryStudy);s.names=['mesh-analysis'];s.skill_name='mesh-analysis'
        setup,common=s.instructions('3d-scan-calc',True)
        self.assertNotIn('bench_skills',setup+common)
        self.assertIn('immutable',common)
        self.assertIn('Never package /verifier',common)
    def test_original_skill_read_and_hash_required(self):
        s=object.__new__(LibraryStudy);s.names=['mesh-analysis'];s.skill_name='mesh-analysis'
        setup,_=s.instructions('3d-scan-calc',False)
        self.assertIn('bench_skills/mesh-analysis/SKILL.md',setup)
        self.assertIn('SBP_ACTIVE_SKILL_SHA256',setup)

if __name__=='__main__':unittest.main()
