"""Ordered native-event publication and future-status boundaries."""
import copy
import json
from pathlib import Path
from concurrent.futures import Future
import tempfile
import unittest
import numpy as np
from stack_context_training_pipeline_v1 import wait,identities
from stack_context_river_workers_v1 import commit
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir,ARRAYS
from sampled_physical_reservoir_v1 import checked_row
from sampled_physical_root_evaluation_v1 import sha


class WorkerTests(unittest.TestCase):
    def test_ordered_insertions_and_foreign_results(self):
        source=Path('S:/GTOpen-research/stack-geometry-control-v1/fixtures/stack-20-context.json').read_text()
        catalog=json.loads(Path('S:/GTOpen-research/stack-context-resources-v1/stack-20/initial-catalog.json').read_bytes())
        observations=[next(r['observation'] for r in catalog['native_observations'] if r['player']==p) for p in (0,1)]
        reservoirs=[WeightedPhysicalReservoir(3,p,123+p,source) for p in (0,1)]
        expected=copy.deepcopy(reservoirs);events=[]
        for i in range(10):
            for actor in (1,0):
                o=observations[actor];values=[float(i+j) if j<o['n'] else 0. for j in range(4)]
                row=checked_row(o,values);events.append((actor,row,1,1.+i/10))
                expected[actor].add(o,values,1,deal_weight=1.+i/10)
        key=reservoirs[0].context_sha256
        result=dict(context_sha256=key,model_sha256='a'*64,registry_sha256='b'*64,start=0,counts=[10,10],events=events)
        args=dict(expected_start=0,iteration=1,expected_context_sha256=key,expected_model_sha256='a'*64,expected_registry_sha256='b'*64)
        for field,value in (('context_sha256','c'*64),('model_sha256','c'*64),('registry_sha256','c'*64),('start',169),('counts',[9,10])):
            bad=copy.deepcopy(result);bad[field]=value
            with self.assertRaises(ValueError):commit(bad,reservoirs,**args)
            self.assertEqual([r.seen for r in reservoirs],[0,0])
        commit(result,reservoirs,**args)
        for left,right in zip(reservoirs,expected):
            self.assertEqual(left.summary(),right.summary());self.assertEqual(left.rng.bit_generator.state,right.rng.bit_generator.state)
            for name in ARRAYS:np.testing.assert_array_equal(getattr(left,name),getattr(right,name))

    def test_terminal_timeout_is_not_mistaken_for_observation_timeout(self):
        value=Future();value.set_result(7);self.assertEqual(wait(value,lambda:None),7)
        error=Future();error.set_exception(TimeoutError('worker deadline'))
        with self.assertRaisesRegex(TimeoutError,'worker deadline'):wait(error,lambda:None)

    def test_native_identity_requires_registered_unchanged_bytes(self):
        with tempfile.TemporaryDirectory(prefix='gtopen-worker-contract-') as folder:
            path=Path(folder)/'source';path.write_text('original')
            config=dict(source_identities={str(path):sha(path)})
            self.assertEqual(identities(config,[path]),config['source_identities'])
            path.write_text('changed')
            with self.assertRaises(ValueError):identities(config,[path])
            with self.assertRaises(ValueError):identities(dict(source_identities={}),[path])


if __name__=='__main__':unittest.main(verbosity=2)
