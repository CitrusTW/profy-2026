"""Offline integration checks: no API, apt, downloads, images or paid work."""
import io,json,tempfile,unittest
from pathlib import Path
from native_support import archive_rows,choose_target,copy_targets,extract_inputs,input_manifest,read_transport,registry,select_rows,sha,transport_pieces
from remote_native import changed_files,root_file

class NativeAdapterTests(unittest.TestCase):
    def test_original_pytest_stdout_without_ctrf(self):
        from remote_grade import pytest_counts
        self.assertEqual(pytest_counts('All tests passed!\n==== 6 passed, 2 warnings in 2.73s ====\n'),{'passed':6})
        self.assertEqual(pytest_counts('=== 1 failed, 5 passed in 1s ===\n'),{'failed':1,'passed':5})
        self.assertEqual(pytest_counts(''),{})
    def test_recovery_selection_transport_and_staging_exclude_groundtruth(self):
        spec=registry()['xlsx-recover-data']
        rows=[('Dockerfile',b'FROM ubuntu:24.04\nCOPY nasa_budget_incomplete.xlsx /root/nasa_budget_incomplete.xlsx\n',0o644),('nasa_budget_incomplete.xlsx',b'incomplete public bytes',0o644),('groundtruth/complete.xlsx',b'never transmit',0o644),('skills/pdf/SKILL.md',b'original pdf',0o644)]
        selected=select_rows(rows,spec);data=archive_rows(selected)
        pieces,manifest=transport_pieces(data)
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)
            for n,b in pieces:(base/n).write_bytes(b)
            meta={'transport':manifest,'input_sha256':sha(data)}
            with read_transport(base,meta) as buffer:extract_inputs(buffer,base/'source',input_manifest(selected))
            self.assertEqual({p.relative_to(base/'source').as_posix() for p in (base/'source').rglob('*') if p.is_file()},{'Dockerfile','nasa_budget_incomplete.xlsx'})
            self.assertEqual((base/'source/nasa_budget_incomplete.xlsx').read_bytes(),b'incomplete public bytes')
        changed=rows.copy();changed[0]=('Dockerfile',b'COPY groundtruth /root/groundtruth\n',0o644)
        with self.assertRaises(ValueError):select_rows(changed,spec)

    def test_directory_copy_keeps_contents_not_extra_source_component(self):
        spec={'copies':[['workspace','/app/workspace']],'directory_sources':['workspace'],'public_input_files':['workspace/dataset/img/007.jpg','workspace/dataset/img/009.jpg']}
        rows=[('Dockerfile',b'COPY workspace /app/workspace\n',0o644),('workspace/dataset/img/007.jpg',b'one',0o644),('workspace/dataset/img/009.jpg',b'two',0o644),('unrelated/secret',b'no',0o644)]
        chosen=select_rows(rows,spec)
        mapping=copy_targets(spec,[n for n,b,m in chosen])
        self.assertEqual(mapping,{'workspace/dataset/img/007.jpg':'/app/workspace/dataset/img/007.jpg','workspace/dataset/img/009.jpg':'/app/workspace/dataset/img/009.jpg'})
        with self.assertRaises(ValueError):select_rows(rows+[('workspace/groundtruth.xlsx',b'no',0o644)],spec)

    def test_target_replacement_preserves_pdf_and_resource_bytes(self):
        rows=[('skills/pdf/SKILL.md',b'PDF parent',0o644),('skills/xlsx/SKILL.md',b'XLSX frozen parent',0o644),('skills/xlsx/scripts/tool.py',b'unchanged resource',0o755)]
        parent=choose_target(rows,'xlsx',sha(b'XLSX frozen parent'))
        self.assertEqual(parent,'XLSX frozen parent')
        selected=[(n,b'candidate' if n=='skills/xlsx/SKILL.md' else b,m) for n,b,m in rows]
        self.assertEqual(dict((n,b) for n,b,m in selected)['skills/pdf/SKILL.md'],b'PDF parent')
        self.assertEqual(selected[2],rows[2])
        with self.assertRaises(ValueError):choose_target(rows,'absent')
        with self.assertRaises(ValueError):choose_target(rows,'xlsx',sha(b'PDF parent'))

    def test_chunk_reassembly_detects_order_piece_and_total_corruption(self):
        # Incompressible deterministic input exercises multiple transport pieces.
        import random
        raw=random.Random(17).randbytes(1_100_000)
        data=archive_rows([('large.jpg',raw,0o644)])
        pieces,manifest=transport_pieces(data)
        self.assertGreater(len(pieces),1)
        self.assertTrue(all(len(b)<=450000 for n,b in pieces))
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)
            for n,b in pieces:(base/n).write_bytes(b)
            meta={'transport':manifest,'input_sha256':sha(data)}
            with read_transport(base,meta) as buffer:
                extract_inputs(buffer,base/'source',{'large.jpg':{'size':len(raw),'sha256':sha(raw),'mode':0o644}})
            self.assertEqual((base/'source/large.jpg').read_bytes(),raw)
            with self.assertRaises(ValueError):read_transport(base,{**meta,'transport':list(reversed(manifest))})
            with self.assertRaises(ValueError):read_transport(base,{**meta,'input_sha256':'0'*64})
            name,body=pieces[0];(base/name).write_bytes(bytes([body[0]^1])+body[1:])
            with self.assertRaises(ValueError):read_transport(base,meta)

    def test_changed_exports_cover_both_logical_roots_without_skill_escape(self):
        with tempfile.TemporaryDirectory() as d:
            work=Path(d);(work/'root').mkdir();(work/'app/workspace').mkdir(parents=True)
            (work/'root/input.xlsx').write_bytes(b'initial')
            (work/'app/workspace/result.xlsx').write_bytes(b'answer')
            (work/'root/.cache').mkdir();(work/'root/.cache/internal').write_bytes(b'cache')
            state={'work':d,'original_file_sha256':{'/root/input.xlsx':sha(b'initial')}}
            self.assertEqual(changed_files(state),['/app/workspace/result.xlsx'])
            (work/'root/escape').symlink_to('/etc/passwd')
            with self.assertRaises(AssertionError):root_file(state,'/root/escape')
            with self.assertRaises(AssertionError):root_file(state,'/app/../etc/passwd')
            with self.assertRaises(AssertionError):root_file(state,'/root/bench_skills/xlsx/SKILL.md')

if __name__=='__main__':unittest.main()
