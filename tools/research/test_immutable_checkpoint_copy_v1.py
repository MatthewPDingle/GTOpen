"""Boundary checks for copying immutable state into an owned new directory."""
import json
from pathlib import Path
import tempfile
import unittest
from sampled_physical_root_evaluation_v1 import ROOT
from sampled_visible_hybrid_checkpoint_v1 import publish, encoded
from immutable_checkpoint_copy_v1 import copy_closure


class CopyBoundaries(unittest.TestCase):
    def setUp(self):
        self.base = (ROOT/'target/checkpoint-copy-unit-tests').resolve()
        self.base.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=self.base)
        self.root = Path(self.temporary.name).resolve()
        self.assertTrue(self.root.is_relative_to(self.base))
        self.source = self.root/'source'
        self.leaf = publish(self.source, 'payload', b'fixture bytes', suffix='npz')
        self.checkpoint = publish(self.source, 'checkpoint', encoded(dict(child=self.leaf)))
        self.target = self.root/'copied'

    def tearDown(self):
        # TemporaryDirectory recursively removes only this verified owned path.
        self.assertTrue(Path(self.temporary.name).resolve().is_relative_to(self.base))
        self.temporary.cleanup()

    def copy(self, **kwargs):
        return copy_closure(self.source, self.target, kwargs.get('checkpoint', self.checkpoint),
                            maximum_bytes=kwargs.get('maximum_bytes',1000), guard=lambda:None)

    def test_complete_closure_and_source_preserved(self):
        before = {p.name:p.read_bytes() for p in self.source.iterdir()}
        result = self.copy()
        self.assertEqual(len(result['objects']), 2)
        self.assertEqual(before, {p.name:p.read_bytes() for p in self.source.iterdir()})
        self.assertEqual(before, {p.name:p.read_bytes() for p in self.target.iterdir()})

    def test_bad_hash_rejected_before_destination_creation(self):
        (self.source/self.leaf['file']).write_bytes(b'corrupted fixture')
        with self.assertRaises(ValueError): self.copy()
        self.assertFalse(self.target.exists())

    def test_escape_rejected_before_destination_creation(self):
        with self.assertRaises(ValueError):
            self.copy(checkpoint=dict(file='../outside.json', sha256='0'*64))
        self.assertFalse(self.target.exists())

    def test_budget_rejected_before_destination_creation(self):
        with self.assertRaises(ValueError): self.copy(maximum_bytes=1)
        self.assertFalse(self.target.exists())

    def test_existing_destination_preserved(self):
        self.target.mkdir()
        marker=self.target/'keep'; marker.write_bytes(b'unchanged')
        with self.assertRaises(ValueError): self.copy()
        self.assertEqual(marker.read_bytes(),b'unchanged')


if __name__ == '__main__':
    unittest.main()
