import gzip,io,os,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from cloud_runtime_bridge import get,MemoryUpload
from cloud_proot_check import upload_chunks,reconstruction,SCRIPT

class RuntimeTests(unittest.TestCase):
    def test_public_download_rejects_oversized_header(self):
        response=io.BytesIO(b'x');response.headers={'Content-Length':'100'}
        with patch('cloud_runtime_bridge.urllib.request.urlopen',return_value=response):
            with self.assertRaisesRegex(ValueError,'RAM bound'):get('https://example.org/public',10)

    def test_public_download_rejects_oversized_stream(self):
        response=io.BytesIO(b'01234567890');response.headers={}
        with patch('cloud_runtime_bridge.urllib.request.urlopen',return_value=response):
            with self.assertRaisesRegex(ValueError,'RAM bound'):get('https://example.org/public',10)

    def test_chunk_reconstruction_preserves_bytes(self):
        original=b'a'*1000001;seen=[];uploads=[];parts={}
        def upload(blob,user):
            self.assertIsInstance(blob,MemoryUpload);self.assertLessEqual(len(blob.data),500000)
            seen.append(blob);return {'filename':blob.name}
        with tempfile.TemporaryDirectory() as d:
            upload_chunks(SimpleNamespace(transport=SimpleNamespace(upload=upload)),'public.bin',original,'test',Path(d),uploads,parts)
            old=Path.cwd()
            try:
                os.chdir(d)
                for blob in seen:Path(blob.name).write_bytes(blob.data)
                exec(reconstruction(parts),{})
                self.assertEqual(Path('public.bin').read_bytes(),original)
                Path(seen[0].name).write_bytes(b'changed')
                with self.assertRaises(AssertionError):exec(reconstruction(parts),{})
            finally:os.chdir(old)

    def test_cloud_integrity_check_precedes_execution(self):
        compile('PROOT_SHA="a"\nROOTFS_SHA="b"\n'+SCRIPT,'<cloud-only>','exec')
        self.assertLess(SCRIPT.index('assert hashlib.sha256(binary'),SCRIPT.index('binary.chmod'))
        self.assertIn('shutil.rmtree(work)',SCRIPT)

if __name__=='__main__':unittest.main()
