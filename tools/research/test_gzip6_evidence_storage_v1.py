"""Qualify stronger lossless compression without changing decoded evidence."""
import ast
import json
from pathlib import Path
import tempfile
import unittest
from sampled_evidence_archive_v1 import read_artifact, digest
from owned_batch_archive_gzip6_v1 import OwnedBatchArchive, ARTIFACTS

BASE=Path(__file__).resolve().parent


class StorageTests(unittest.TestCase):
    def test_only_compression_level_changes(self):
        old=(BASE/'sampled_evidence_archive_v1.py').read_text()
        new=(BASE/'sampled_evidence_archive_gzip6_v1.py').read_text()
        self.assertEqual(new,old.replace('compression_level=1','compression_level=6').replace('compresslevel=1','compresslevel=6'))
        old=(BASE/'owned_batch_archive_v1.py').read_text()
        new=(BASE/'owned_batch_archive_gzip6_v1.py').read_text()
        self.assertEqual(new,old.replace('from sampled_evidence_archive_v1 import','from sampled_evidence_archive_gzip6_v1 import'))

    def fixture(self,root):
        owner=OwnedBatchArchive.create(root,guard=lambda:None)
        path=owner.begin('test-000000');path.mkdir()
        expected={name:(json.dumps({'exact':[0.12345678901234567,1e-100], 'name':name})+'\n').encode()
                  for name in ARTIFACTS|{'residuals.json'}}
        for name,raw in expected.items():(path/name).write_bytes(raw)
        return owner,path,expected

    def test_original_reader_and_owned_release(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();owner,path,expected=self.fixture(root)
            identity=owner.publish('test-000000');target=root/'test-000000'
            manifest=json.loads((target/'manifest.json').read_text())
            self.assertEqual(manifest['compression_level'],6)
            for name,raw in expected.items():
                self.assertEqual(read_artifact(target,manifest,name,guard=lambda:None),raw)
            self.assertEqual(owner.release('test-000000'),identity)
            self.assertFalse(path.exists())
            self.assertEqual(owner.release('test-000000'),identity)

    def test_corrupt_archive_retains_scratch(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();owner,path,expected=self.fixture(root)
            owner.publish('test-000000');target=root/'test-000000'
            packed=target/'profiles.json.gz';raw=packed.read_bytes()
            packed.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
            with self.assertRaises(ValueError):owner.release('test-000000')
            for name,raw in expected.items():self.assertEqual((path/name).read_bytes(),raw)

    def test_unexpected_scratch_retained(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();owner,path,expected=self.fixture(root)
            owner.publish('test-000000');(path/'unowned.txt').write_text('keep')
            with self.assertRaises(ValueError):owner.release('test-000000')
            self.assertEqual((path/'unowned.txt').read_text(),'keep')
            for name,raw in expected.items():self.assertEqual((path/name).read_bytes(),raw)


if __name__=='__main__':unittest.main(verbosity=2)
