"""Complete audited baseline/stratified banks in fixed crossed-policy order."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import json
from pathlib import Path
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha
from preflop_allin_matrix_v1 import AllinMatrix
from composite_showdown_bank_v1 import load_bank as baseline_bank, training_gates as baseline_gates
from weighted_completed_bank_v1 import load_bank as weighted_bank
from weighted_training_policy_v1 import average as weighted_average
from weighted_training_gpu_bank_v1 import WeightedCudaBank64
from action_integrated_policy_v1 import ActionIntegratedCpuBank64
from action_integrated_policy_shared_v1 import ActionIntegratedCudaBankShared64
from weighted_learning_cuda_control_20260927 import LOCK, OTHER
from bounded_parallel_evaluation_archive_v2 import production_available
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2')

ARMS = ('9266201-baseline', '9266201-stratified', '9266301-baseline', '9266301-stratified')
TRAINING = OUT / 'weighted-stratified-study-v1-registration.json'
TRAINING_RESULT = OUT / 'weighted-stratified-study-v1-training-result.json'
CONTEXT = OUT / 'bb-context-candidate.json'
MATRIX = OUT / 'preflop-allin-matrix-control-v1-matrix.json'
CATALOG = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
TEST_DEALS = 65536
TEST_SEED = 9278101


def complete_training_paths():
    """No partial-bank evaluation or admission based on mutable progress files."""
    reg, result = read(TRAINING), read(TRAINING_RESULT)
    assert reg['generations'] == 78
    assert [a['name'] for a in reg['arms']] == list(ARMS[1::2])
    assert result['training_complete'] and result['registration_sha256'] == sha(TRAINING)
    assert result['store'] == reg['store']
    paths = [TRAINING, TRAINING_RESULT, CONTEXT, MATRIX, CATALOG,
             OUT / 'WEIGHTED-STRATIFIED-STUDY-PLAN.md', *baseline_gates()]
    for name in ARMS[1::2]:
        prefix = f'weighted-training-readback-parallel-v1-w4-{name}-0078'
        ap, ar = [OUT / f'{prefix}-{s}.json' for s in ('result', 'registration')]
        audit = read(ap)
        assert audit['passed'] and audit['complete_arm'] and audit['arm'] == name
        assert audit['completed_updates'] == 78 and audit['bb_roots_reconstructed'] == 39936
        assert audit['source_registration_sha256'] == sha(TRAINING)
        assert audit['readback_registration_sha256'] == sha(ar)
        endpoint = result['arms'][name]
        assert endpoint['completed'] == 78 and endpoint['checkpoint'] == audit['final_checkpoint']
        paths.extend([ap, ar, Path(endpoint['metrics_path'])])
    return paths


def args_for_banks():
    source = CONTEXT.read_text()
    matrix = AllinMatrix(read(MATRIX), source)
    return dict(context_source=source, catalog_source=CATALOG.read_text(),
                matrix_sha256=sha(MATRIX), entry_mass=matrix.btn_mass)


class WeightedReferenceBank:
    def __init__(self, documents, weights, args):
        self.documents, self.weights = documents, weights
        self.args = {k: v for k, v in args.items() if k != 'context_source'}

    def average(self, queries, *, guard):
        return weighted_average(queries, self.documents, completed_iterations=78,
                                weights_by_player=self.weights, guard=guard,
                                device='cpu', **self.args)


def load_banks(*, guard, reference=False):
    args = args_for_banks()
    banks, references, identities, timings = [], [], [], []
    for index, name in enumerate(ARMS):
        guard()
        began = time.monotonic()
        if index % 2:
            docs, weights, identity = weighted_bank(name, bank_args=args, guard=guard)
            bank = WeightedCudaBank64(docs, weights, completed_iterations=78,
                                     models_per_chunk=8, guard=guard, **args)
            if reference:
                references.append(WeightedReferenceBank(docs, weights, args))
        else:
            docs, weights, identity = baseline_bank(OUT, name, completed=78,
                purpose='evaluation', bank_args=args, guard=guard)
            bank = ActionIntegratedCudaBankShared64(docs, weights, completed_iterations=78,
                                                   models_per_chunk=8, guard=guard, **args)
            if reference:
                references.append(ActionIntegratedCpuBank64(docs, weights_by_player=weights,
                                                           completed_iterations=78, **args))
        assert len(docs) == 78 and np.array_equal(weights, np.tile(np.arange(1., 79.), (2, 1)))
        banks.append(bank)
        identities.append(identity)
        timings.append(time.monotonic() - began)
        del docs
    return banks, references, identities, timings, args


def runtime_guard(store, *, maximum_seconds, maximum_bytes, gpu=True):
    started = time.monotonic()
    last = size_at = 0.
    store = Path(store)
    assert store.parent == Path('S:/GTOpen-research') and store.name.startswith('weighted-complete-')
    def guard():
        nonlocal last, size_at
        now = time.monotonic()
        assert now - started < maximum_seconds, 'Evaluation invocation limit reached'
        if now - last > 2:
            assert production_available() and not OTHER.exists(), 'Production activity or competing research'
            assert psutil.virtual_memory().available > 24_000_000_000
            assert psutil.disk_usage('S:/').free > 40_000_000_000
            if gpu:
                import torch
                assert torch.cuda.mem_get_info()[0] > 3_000_000_000
            last = now
        if store.exists() and now - size_at > 10:
            total = 0
            for p in store.rglob('*'):
                try:
                    if p.is_file():
                        total += p.stat().st_size
                except FileNotFoundError:
                    # Only verified owned scratch is allowed to disappear.
                    assert p.is_relative_to(store / '.batch-work')
            assert total < maximum_bytes, 'Evidence storage bound reached'
            size_at = now
    return guard


def setup_cuda():
    import torch
    assert torch.cuda.is_available()
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False


def catalog_roots(banks, references, args, *, guard):
    rows = json.loads(args['catalog_source'])['native_observations']
    query = dict(context_source=args['context_source'], observations=[r['observation'] for r in rows])
    assert len(rows) == 265 and all(o['own_history'] == [] for o in query['observations'])
    roots, checks = [], []
    for index, bank in enumerate(banks):
        p, reach = bank.average(query, guard=guard)
        assert np.array_equal(reach, np.full(265, 3081.))
        root = np.zeros((169, 4))
        seen = set()
        for row, probability in zip(rows, p):
            if row['player'] == 0:
                assert row['hand_class'] not in seen
                root[row['hand_class']] = probability
                seen.add(row['hand_class'])
        assert seen == set(range(169))
        roots.append(root)
        if references:
            cp, cr = references[index].average(query, guard=guard)
            error = float(np.max(abs(p - cp)))
            assert error < 1e-10 and np.array_equal(cr, reach)
            checks.append(dict(bank=index, maximum_policy_error=error,
                               maximum_reach_error=0., observations=265))
    return roots, checks
