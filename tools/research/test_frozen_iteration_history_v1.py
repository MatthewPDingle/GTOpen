"""Reject discontinuous or mutated training histories before accepting an audit."""
import json
from pathlib import Path
import tempfile
import unittest
from sampled_physical_root_evaluation_v1 import ROOT
from sampled_visible_hybrid_checkpoint_v1 import publish,encoded
from frozen_iteration_history_v1 import FrozenHistory,verify_snapshot


class HistoryBoundaries(unittest.TestCase):
    def setUp(self):
        self.base=(ROOT/'target/iteration-history-unit-tests').resolve()
        self.base.mkdir(exist_ok=True)
        self.temporary=tempfile.TemporaryDirectory(dir=self.base)
        self.root=Path(self.temporary.name).resolve()
        assert self.root.is_relative_to(self.base)
        self.store=self.root/'history';self.store.mkdir()
        self.objects=self.root/'objects'
        self.model=publish(self.objects,'model',encoded({'generation':0}))
        self.checkpoint=publish(self.objects,'checkpoint',encoded({'model':self.model}))
        self.folder=self.store/'iteration-0001';self.folder.mkdir()
        self.metrics=self.folder/'metrics.json'
        self.metrics.write_text(json.dumps(dict(iteration=1,used_model=self.model,checkpoint=self.checkpoint)))
        self.segment=dict(first=1,last=1,store=str(self.store),objects=str(self.objects))

    def tearDown(self):
        assert Path(self.temporary.name).resolve().is_relative_to(self.base)
        self.temporary.cleanup()

    def test_gaps_overlaps_and_truncated_mapping_rejected(self):
        for segments,count in (([dict(self.segment,first=2,last=2)],2),
                               ([self.segment,self.segment],2),([self.segment],2)):
            with self.assertRaises(ValueError):FrozenHistory(segments,count)

    def test_iteration_identity_cannot_be_relabelled(self):
        value=json.loads(self.metrics.read_text());value['iteration']=2
        self.metrics.write_text(json.dumps(value))
        with self.assertRaises(ValueError):
            FrozenHistory([self.segment],1).snapshot(maximum_bytes=10000,guard=lambda:None)

    def test_checkpoint_corruption_detected(self):
        (self.objects/self.model['file']).write_bytes(b'changed model')
        with self.assertRaises(ValueError):
            FrozenHistory([self.segment],1).snapshot(maximum_bytes=10000,guard=lambda:None)

    def test_native_evidence_mutation_detected_after_snapshot(self):
        native=self.folder/'native.json';native.write_bytes(b'{"value":1}')
        snapshot=FrozenHistory([self.segment],1).snapshot(maximum_bytes=10000,guard=lambda:None)
        verify_snapshot(snapshot,lambda:None)
        native.write_bytes(b'{"value":2}')
        with self.assertRaises(ValueError):verify_snapshot(snapshot,lambda:None)


if __name__=='__main__':unittest.main()
