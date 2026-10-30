"""CPU-only routing tests; synthetic bank objects do not qualify actual models."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2')
import copy
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch
import numpy as np
from board_prefix_publication_v1 import atomic_json
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha
import board_complete_evaluation_support_v1 as support

PREFIX = 'board-complete-evaluation-support-control-v1'


def main():
    began = time.monotonic()
    rp, dest = [OUT / f'{PREFIX}-{s}.json' for s in ('registration', 'result')]
    assert not rp.exists() and not dest.exists()
    candidates, paths = support.design()
    control = read(OUT / 'weighted-stratified-study-v1-registration.json')
    inputs = {str(p): sha(p) for p in [*paths, *Path(__file__).parent.glob('*.py')]}
    atomic_json(rp, dict(inputs=inputs, scope='Read-only actual design and missing-input gate; synthetic bank routing and rejection tests.',
        gpu_used=False, model_predictions_tested=False, production_modified=False))
    checks = []

    def reject(label, fn):
        try:
            fn()
        except (ValueError, AssertionError):
            checks.append(label)
            return
        raise AssertionError('Unexpected admission: ' + label)

    support.validate_design(control, candidates)
    changes = [
        ('swapped-seeds', lambda x: x.reverse()),
        ('wrong-control', lambda x: x[0].update(control=x[1]['control'])),
        ('changed-board-seed', lambda x: x[0]['config']['board_root'].update(board_seed=7)),
        ('changed-board-count', lambda x: x[0]['config']['board_root'].update(boards_per_generation=8)),
        ('changed-physical-budget', lambda x: x[0]['config']['board_root'].update(physical_budget=256)),
        ('changed-optimizer-budget', lambda x: x[0]['config'].update(fit_steps=256)),
        ('changed-physical-seed', lambda x: x[0]['config'].update(sampler_seed=1)),
    ]
    for label, mutate in changes:
        altered = copy.deepcopy(candidates); mutate(altered)
        reject(label, lambda: support.validate_design(control, altered))
    actual_candidates, _, pending = support.readiness()
    assert actual_candidates == candidates and pending, 'This preparation test expects genuine candidate training still pending'
    assert tuple(support.ARMS) == ('9266201-stratified', '9266201-board-root',
                                   '9266301-stratified', '9266301-board-root')
    assert (support.TEST_DEALS, support.TEST_SEED) == (65536, 9281101)
    with patch.object(support, 'weighted_bank', side_effect=AssertionError('Must reject before loading')), \
         patch.object(support, 'board_bank', side_effect=AssertionError('Must reject before loading')):
        try:
            support.load_banks(guard=lambda: None)
        except ValueError as exc:
            assert 'not ready' in str(exc)
        else:
            raise AssertionError('Partial training admitted')

    loaded, constructed = [], []
    defect = [None]
    fake_args = dict(context_source='synthetic-context', catalog_source='synthetic-catalog',
                     matrix_sha256='0'*64, entry_mass=np.ones(169)/169)

    def fake_load(name, **kw):
        loaded.append(name)
        assert kw['bank_args'] is fake_args
        docs = [dict(generation=g) for g in range(78)]
        weights = np.tile(np.arange(1., 79.), (2, 1))
        identity = dict(arm=name, completed_iterations=78, purpose='evaluation',
                        unplayed_excluded=dict(generation=78))
        if 'board-root' in name:
            i = list(support.ARMS[1::2]).index(name)
            identity['root_config'] = copy.deepcopy(candidates[i]['config']['board_root'])
        if defect[0] == 'partial': docs.pop()
        if defect[0] == 'reordered': docs[0], docs[1] = docs[1], docs[0]
        if defect[0] == 'unplayed': docs[-1] = dict(generation=78)
        if defect[0] == 'wrong-weights': weights[0, 0] = 2
        if defect[0] == 'wrong-label': identity['arm'] = 'different-arm'
        if defect[0] == 'wrong-purpose': identity['purpose'] = 'exploration'
        if defect[0] == 'wrong-excluded': identity['unplayed_excluded']['generation'] = 79
        if defect[0] == 'wrong-root' and 'root_config' in identity:
            identity['root_config']['board_seed'] = 1
        return docs, weights, identity

    def ctor(kind, docs, weights, **kw):
        assert len(docs) == 78 and kw['completed_iterations'] == 78 and kw['models_per_chunk'] == 8
        if kind == 'board':
            assert kw['root_config'] == candidates[len(constructed)//2]['config']['board_root']
        else:
            assert 'root_config' not in kw
        constructed.append(kind)
        return dict(kind=kind)

    with patch.object(support, 'readiness', return_value=(candidates, [], [])), \
         patch.object(support, 'args_for_banks', return_value=fake_args), \
         patch.object(support, 'weighted_bank', side_effect=fake_load), \
         patch.object(support, 'board_bank', side_effect=fake_load), \
         patch.object(support, 'WeightedCudaBank64', side_effect=lambda *a, **k: ctor('weighted', *a, **k)), \
         patch.object(support, 'BoardRootCudaBank64', side_effect=lambda *a, **k: ctor('board', *a, **k)):
        banks, references, identities, _, args = support.load_banks(guard=lambda: None, reference=True)
        assert loaded == list(support.ARMS) and constructed == ['weighted', 'board', 'weighted', 'board']
        assert len(banks) == len(references) == len(identities) == 4 and args is fake_args
        assert [type(r).__name__ for r in references] == ['WeightedReferenceBank', 'BoardReferenceBank']*2
        for i in (1, 3):
            assert references[i].args['root_config'] == candidates[i//2]['config']['board_root']
            assert 'context_source' not in references[i].args
            with patch.object(support, 'board_average', return_value=('probabilities', 'reach')) as avg:
                query = {'context_source': 'synthetic-context', 'observations': []}
                assert references[i].average(query, guard=lambda: None) == ('probabilities', 'reach')
                assert avg.call_args.kwargs['completed_iterations'] == 78
                assert avg.call_args.kwargs['device'] == 'cpu'
                assert avg.call_args.kwargs['root_config'] == candidates[i//2]['config']['board_root']
        for problem in ('partial', 'reordered', 'unplayed', 'wrong-weights', 'wrong-label',
                        'wrong-purpose', 'wrong-excluded', 'wrong-root'):
            loaded.clear(); constructed.clear(); defect[0] = problem
            reject(problem, lambda: support.load_banks(guard=lambda: None, reference=True))
        defect[0] = None; loaded.clear(); constructed.clear()
        _, references, _, _, _ = support.load_banks(guard=lambda: None, reference=False)
        assert references == [] and loaded == list(support.ARMS)
    for p, h in inputs.items():
        assert sha(p) == h, p
    assert 'torch' not in sys.modules, 'Routing control must not initialize CUDA or import torch'
    output = dict(passed=True, registration_sha256=sha(rp), seconds=time.monotonic()-began,
        rejected_cases=checks, actual_training_pending=pending, routing_order=list(support.ARMS),
        read_only_design_verified=True, synthetic_bank_routing_verified=True,
        actual_full_banks_loaded=False, gpu_used=False, fresh_test_deals_drawn=0,
        full_bank_equivalence_qualified=False, accuracy_qualified=False, production_modified=False)
    atomic_json(dest, output)
    print(json.dumps(output), flush=True)


if __name__ == '__main__':
    main()
