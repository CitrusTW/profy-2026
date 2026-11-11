"""Tests for the new experiment output-contract guard; no model calls."""
import tempfile
import unittest
from pathlib import Path
from continue30 import contract_check


class CompatibilityChecks(unittest.TestCase):
    def test_equivalent_triangle_storage_is_classified_not_rewritten(self):
        indexed='v 0 0 0\nv 1 0 0\nv 0 1 0\nv 1 1 0\nf 1 2 3\nf 2 4 3\n'
        expanded='v 0 0 0\nv 1 0 0\nv 0 1 0\nv 1 0 0\nv 1 1 0\nv 0 1 0\nf 1 2 3\nf 4 5 6\n'
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'output').mkdir();p=root/'output/fixture.obj'
            p.write_text(indexed)
            self.assertFalse(contract_check(root)['passed']);self.assertEqual(p.read_text(),indexed)
            p.write_text(expanded)
            self.assertTrue(contract_check(root)['passed']);self.assertEqual(p.read_text(),expanded)

    def test_empty_or_invalid_references_do_not_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'output').mkdir()
            self.assertFalse(contract_check(root)['passed'])
            (root/'output/bad.obj').write_text('v 0 0 0\nv 1 0 0\nv 0 1 0\nf 0 1 2\n')
            self.assertFalse(contract_check(root)['passed'])


if __name__=='__main__':unittest.main()
