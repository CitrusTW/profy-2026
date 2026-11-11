"""Small offline checks for OBJ representation diagnosis, not a new benchmark."""
import runpy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.extend(['/private/tmp/cognilife-e2e-env/lib/python3.12/site-packages','/private/tmp/cgl-expert-preflight-deps'])
import numpy as np
from diagnose_indexing import read_obj


class DiagnosisChecks(unittest.TestCase):
    def test_indices_preserve_triangle_corners(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'fixture.obj'
            p.write_text('v 0 0 0\nv 1 0 0\nv 0 1 0\nf -3 -2 -1\n')
            vertices, faces=read_obj(p,np)
            self.assertTrue(np.array_equal(vertices[faces],vertices))
            p.write_text('v 0 0 0\nf 0 0 0\n')
            with self.assertRaises(ValueError):read_obj(p,np)

    def test_original_metric_is_not_representation_invariant(self):
        scorer=Path(__file__).resolve().parents[3]/'04_项目数据与代码/skillsbench/tasks/threejs-structure-parser/verifier/test_outputs.py'
        metric=runpy.run_path(str(scorer))['chamfer_distance']
        x=np.arange(401,dtype=np.float32)
        positions=np.stack([x,x*x,np.zeros_like(x)],axis=1)
        faces=np.array([[0,i,i+1] for i in range(1,400)]).reshape(-1)
        expanded=positions[faces]
        self.assertGreater(metric(positions,expanded),0)
        self.assertEqual(metric(expanded,expanded),0)
        self.assertTrue(np.array_equal(np.unique(positions,axis=0),np.unique(expanded,axis=0)))


if __name__=='__main__':unittest.main()
