"""Verify generalized resources against retained narrower-range evidence."""
import copy
import io
import itertools
import json
from pathlib import Path
import sys
import time
import unittest
import stack_context_resources_v1 as resources
import numpy as np
from sampled_allin_protocol_v3 import AllinCache
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_physical_root_evaluation_v1 import sha,save

INPUTS={}


def read(path):
    path=Path(path);INPUTS[str(path)]=sha(path)
    return json.loads(path.read_bytes())


class ResourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        out=resources.OUT
        p=out/'bb-context-candidate.json';read(p);cls.source=p.read_text()
        review=read(out/'stack-context-complete-allin-cache-v1-readback.json')
        assert review['passed'] and review['complete']
        assert review['result_sha256']==sha(out/'stack-context-complete-allin-cache-v1-result.json')
        INPUTS[str(out/'stack-context-complete-allin-cache-v1-result.json')]=review['result_sha256']
        cls.cache=AllinCache(review['cache_artifact'],review['cache_sha256'])
        INPUTS[review['cache_artifact']]=review['cache_sha256']
        cls.keys=sorted(cls.cache.rows)
        cls.sizes=np.array([len({tuple(sorted(4*(c//4)+p[c%4] for c in key[:2])+sorted(4*(c//4)+p[c%4] for c in key[2:]))
            for p in itertools.permutations(range(4))}) for key in cls.keys])
        cls.matrix=AllinMatrix(read(out/'preflop-allin-matrix-control-v1-matrix.json'),cls.source)
        cls.physical=read('S:/GTOpen-research/board-root-components-control-v1/preflop-catalog.json')
        cls.initial=read('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
        cls.pop,cls.direct=resources.population(cls.source,cls.keys,cls.sizes)

    def test_original_narrower_ranges_and_missing_coverage(self):
        self.assertEqual(self.pop['physical_pairs'],776650)
        self.assertEqual(len(self.pop['rows']),47478)
        np.testing.assert_allclose(self.direct,self.matrix.mass,atol=1e-12,rtol=0)
        self.assertLess(resources.independent_matrix(self.source,self.pop,self.cache,self.matrix,self.direct),1e-11)
        with self.assertRaises(ValueError):
            resources.population(self.source,self.keys,self.sizes*2)
        # A missing supported orbit must fail; no renormalization of partial coverage.
        k=next(i for i,k in enumerate(self.keys) if k==tuple(self.pop['rows'][0]['private_cards']))
        with self.assertRaises(ValueError):
            resources.population(self.source,self.keys[:k]+self.keys[k+1:],np.delete(self.sizes,k))

    def test_original_catalog_and_identity_rejections(self):
        result=resources.catalog(self.source,self.physical,self.matrix)
        actual={(r['player'],r['hand_class']):r['observation'] for r in result['native_observations']}
        expected={(r['player'],r['hand_class']):dict(r['observation'],own_history=[]) for r in self.initial['native_observations']}
        self.assertEqual(actual,expected)
        bad=dict(self.physical,context_source=self.source+' ')
        with self.assertRaises(ValueError):resources.catalog(self.source,bad,self.matrix)
        bad=dict(self.physical,rows=self.physical['rows'][1:])
        with self.assertRaises(ValueError):resources.catalog(self.source,bad,self.matrix)
        bad=copy.deepcopy(self.physical);bad['rows'][0]['observation']['actor']=1
        with self.assertRaises(ValueError):resources.catalog(self.source,bad,self.matrix)

    def test_corrupt_cashflows_rejected(self):
        bad=copy.deepcopy(self.matrix);bad.bb[0,0]+=.01
        with self.assertRaises(ValueError):resources.independent_matrix(self.source,self.pop,self.cache,bad,self.direct)
        bad=copy.deepcopy(self.matrix);bad.btn_fold+=1
        with self.assertRaises(ValueError):resources.independent_matrix(self.source,self.pop,self.cache,bad,self.direct)


if __name__=='__main__':
    path=resources.OUT/'stack-context-resources-v1-tests.json'
    attempt=resources.OUT/'stack-context-resources-v1-tests-attempt.json'
    if path.exists() or attempt.exists():raise ValueError('Preserve existing recorded implementation test')
    for m in list(sys.modules.values()):
        p=getattr(m,'__file__',None)
        if p and Path(p).is_relative_to(resources.ROOT) and Path(p).suffix=='.py':INPUTS[str(Path(p).resolve())]=sha(p)
    save(attempt,dict(inputs=INPUTS,scientific_training=False))
    began=time.monotonic();log=io.StringIO()
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ResourceTests))
    changed=[p for p,h in INPUTS.items() if sha(p)!=h]
    save(path,dict(complete=True,passed=result.wasSuccessful() and not changed,tests=result.testsRun,
        seconds=time.monotonic()-began,inputs=INPUTS,changed_inputs=changed,log=log.getvalue(),scientific_training=False))
    print(log.getvalue(),flush=True)
    if not result.wasSuccessful() or changed:raise SystemExit(1)
