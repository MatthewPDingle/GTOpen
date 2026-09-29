"""Retained-policy integration tests; no fitting or fresh scientific evaluation.

Zero extension here is an inference fixture, not a resumable training migration
or a statement about the old network's target units. Only CPU parity is tested.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np

import stack_context_full_policy_v1 as full
import stack_context_policy_v1 as base
import stack_context_relative_policy_v1 as relative
from stack_context_inputs_v1 import Registry, digest
from stack_context_relative_inputs_v1 import Registry as RelativeRegistry
from board_training_policy_v1 import probabilities, average as legacy_average
from board_training_checkpoint_v1 import model_document, validate_model
from preflop_allin_matrix_v1 import AllinMatrix
from river_posterior64_v1 import subset

OUT = Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
STORE = Path('S:/GTOpen-research')


class FullContextPolicyTests(unittest.TestCase):
    identities = {}

    @classmethod
    def read(cls, path, expected=None):
        path = Path(path); raw = path.read_bytes(); sha = hashlib.sha256(raw).hexdigest()
        if expected is not None:
            assert sha == expected, path
        cls.identities[str(path)] = sha
        return json.loads(raw)

    @classmethod
    def setUpClass(cls):
        source_path = OUT / 'bb-context-candidate.json'
        cls.read(source_path); cls.source = source_path.read_text(); cls.key = digest(cls.source)
        public_path = STORE / 'public-economics-control-v1/public.json'
        public_proof = cls.read(OUT / 'public-economics-control-v1-result.json')
        assert public_proof['passed']
        public = cls.read(public_path, public_proof['artifacts'][str(public_path)])
        assert public['context_source'] == cls.source
        matrix_path = OUT / 'preflop-allin-matrix-control-v1-matrix.json'
        matrix = AllinMatrix(cls.read(matrix_path), cls.source)
        catalog_path = STORE / 'preflop-catalog-control-v1/native-preflop-catalog.json'
        catalog = cls.read(catalog_path); cls.catalog_source = catalog_path.read_text()
        cls.catalog_queries = dict(context_source=cls.source,
            observations=[r['observation'] for r in catalog['native_observations']])
        entry = dict(name='retained-200bb', split='fit', context_source=cls.source, public_document=public)
        cls.registries = [Registry([entry]), RelativeRegistry([entry])]
        rows = cls.read(OUT / 'river-learned-batch-cost-v1-registration.json')['policies']
        preflight = cls.read(OUT / 'river-training-preflight-v1.json')
        native = cls.read(OUT / 'river-posterior64-native-control-v1-result.json')
        assert native['passed'] and native['complete']
        cls.fixtures = []
        for row, pre in zip(rows, preflight['arms']):
            assert row['arm'] == pre['arm'] and row['folder'] == pre['objects']
            resources = dict(catalog_source=cls.catalog_source,
                matrix_sha256=cls.identities[str(matrix_path)], entry_mass=matrix.btn_mass,
                root_config=row['root_config'])
            args = dict(context_source=cls.source, **resources)
            checkpoint = cls.read(Path(pre['objects']) / pre['source_checkpoint']['file'],
                                  pre['source_checkpoint']['sha256'])
            originals = []
            for generation in (0, 1, 77):
                ref = checkpoint['played_bank'][generation]
                path = Path(pre['objects']) / ref['file']; cls.read(path, ref['sha256'])
                originals.append(model_document(pre['objects'], ref, **args))
            case = 'd000-' + row['arm']
            record = next(c for c in native['cases'] if c['case'] == case)
            path = OUT / 'river-posterior64-native-control-v1' / case / 'full/full-export.json'
            export = cls.read(path, record['artifacts']['full\\full-export.json'])
            # Retain real ancestor links while bounding implementation-test work.
            q = export['queries']; selected = np.linspace(0, len(q['observations'])-1, 512, dtype=int)
            q, _ = subset(q, selected)
            assert {o['phase'] for o in q['observations']} == {0, 1, 2, 3}
            cls.fixtures.append(dict(resources={cls.key:resources}, args=args, originals=originals, queries=q))

    @classmethod
    def lift(cls, old, registry, resources):
        api = relative if registry.manifest['representation']['input_width'] == 387 else base
        width = api.SHAPES['w0'][1]; networks = copy.deepcopy(old['networks'])
        for net in networks:
            w = np.zeros((64, width), dtype=np.float32)
            w[:, :302] = np.asarray(net['w0'], dtype=np.float32).reshape(64, 302)
            net['w0'] = w.reshape(-1).tolist()
        shared = api.model(registry, generation=old['generation'], networks=networks,
                           preflop_tables={cls.key:old['preflop_tables']})
        root, exact, _ = validate_model(old, context_source=cls.source, **resources[cls.key])
        args = resources[cls.key]
        local = full.local_document(catalog_source=args['catalog_source'], matrix_sha256=args['matrix_sha256'],
                                   root_config=args['root_config'], root=root, exact=exact)
        return full.model(registry, shared, {cls.key:local}, resources)

    def test_complete_policy_preserves_all_streets_and_both_overrides(self):
        for fixture in self.fixtures:
            old = fixture['originals'][-1]
            for q in (fixture['queries'], self.catalog_queries):
                expected, old_coverage = probabilities(q, old, device='cpu', **{k:v for k,v in fixture['args'].items() if k!='context_source'})
                for registry in self.registries:
                    value = self.lift(old, registry, fixture['resources'])
                    actual, _, coverage = full.predict(value, registry, q, context_sha256=self.key,
                                                       resources=fixture['resources'])
                    np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-10)
                    for name in ('exact_btn_rows', 'board_root_rows'):
                        self.assertEqual(coverage[name], old_coverage[name])
                    if q is self.catalog_queries:
                        self.assertGreater(coverage['exact_btn_rows'], 0)
                        self.assertEqual(coverage['board_root_rows'], 169)

    def test_played_average_uses_overridden_own_reach(self):
        weights = np.array([[1., 2.], [3., 4.]])
        for fixture in self.fixtures:
            q = fixture['queries']; originals = fixture['originals'][:2]
            expected, own = legacy_average(q, originals, completed_iterations=2,
                weights_by_player=weights, guard=lambda:None, device='cpu',
                **{k:v for k,v in fixture['args'].items() if k!='context_source'})
            for registry in self.registries:
                models = [self.lift(m, registry, fixture['resources']) for m in originals]
                actual, reach = full.average(models, registry, q, context_sha256=self.key,
                    resources=fixture['resources'], weights_by_player=weights, device='cpu', guard=lambda:None)
                np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-10)
                np.testing.assert_allclose(reach, own, rtol=0, atol=1e-10)

    def test_model_roundtrip(self):
        fixture = self.fixtures[0]
        for registry in self.registries:
            value = self.lift(fixture['originals'][-1], registry, fixture['resources'])
            with tempfile.TemporaryDirectory(prefix='gtopen-full-context-') as folder:
                ref = full.write_model(folder, value, registry, fixture['resources'])
                self.assertEqual(full.read_model(folder, ref, registry, fixture['resources']), value)

    def test_reject_missing_swapped_or_stale_state(self):
        fixture = self.fixtures[0]; registry = self.registries[1]
        value = self.lift(fixture['originals'][-1], registry, fixture['resources'])
        variants = []
        bad = copy.deepcopy(value); bad['local_states'] = {}; variants.append(bad)
        bad = copy.deepcopy(value); bad['generation'] -= 1; variants.append(bad)
        bad = copy.deepcopy(value); bad['override_order'].reverse(); variants.append(bad)
        bad = copy.deepcopy(value); bad['local_states'][self.key]['catalog_sha256'] = '0'*64; variants.append(bad)
        bad = copy.deepcopy(value); bad['local_states'][self.key]['matrix_sha256'] = '0'*64; variants.append(bad)
        bad = copy.deepcopy(value); bad['shared']['preflop_tables'][self.key][0] = None; variants.append(bad)
        for bad in variants:
            with self.assertRaises(ValueError):
                full.validate(bad, registry, fixture['resources'])
        with self.assertRaises(ValueError):
            full.validate(value, registry, {})
        with self.assertRaises(ValueError):
            full.average([value], registry, fixture['queries'], context_sha256=self.key,
                resources=fixture['resources'], weights_by_player=[[1.],[1.]], device='cpu', guard=lambda:None)


if __name__ == '__main__':
    unittest.main()
