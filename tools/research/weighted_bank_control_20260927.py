"""Compare the typed accelerated weighted bank with the scalar/reference average."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import copy
from pathlib import Path
import subprocess
import time
import numpy as np
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha, save
from weighted_learning_cuda_control_20260927 import safe_read_only_resources, LOCK, OTHER
from preflop_allin_matrix_v1 import AllinMatrix
import weighted_training_checkpoint_v1 as checkpoint
from weighted_training_policy_v1 import average, probabilities
from weighted_training_gpu_bank_v1 import WeightedCudaBank64
from sampled_physical_bank_v1 import histories

PREFIX = 'weighted-bank-control-v1'


def main():
    import torch
    torch.set_num_threads(2)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    assert safe_read_only_resources() and not LOCK.exists() and not OTHER.exists()
    query = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.free', '--format=csv,noheader,nounits'],
                           capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
    assert query.returncode == 0
    utilization, free = map(float, query.stdout.strip().splitlines()[0].split(','))
    assert utilization < 20 and free > 4000
    result_path = OUT / 'weighted-training-pilot-v1-result.json'
    pilot = read(result_path)
    assert pilot['passed'] and pilot['exact_restart_replay']
    store = Path(pilot['store'])
    objects = store / 'objects'
    qp = store / 'average-queries.json'
    cp = OUT / 'bb-context-candidate.json'
    mp = OUT / 'preflop-allin-matrix-control-v1-matrix.json'
    cat = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    matrix = AllinMatrix(read(mp), cp.read_text())
    args = dict(context_source=cp.read_text(), catalog_source=cat.read_text(), matrix_sha256=sha(mp), entry_mass=matrix.btn_mass)
    state = checkpoint.restore_checkpoint(objects, pilot['final_checkpoint'], pilot['config'], **args)
    docs = [checkpoint.model_document(objects, reference, **args) for reference in state['played_bank']]
    inputs = {str(p): sha(p) for p in [result_path, qp, cp, mp, cat, *objects.iterdir(), *Path(__file__).parent.glob('*.py')]}
    assert all(pilot['artifacts'][str(p)] == sha(p) for p in [qp, *objects.iterdir()])
    registration = OUT / f'{PREFIX}-registration.json'
    save(registration, dict(inputs=inputs, tolerance=1e-10, maximum_seconds=300,
                           chunks=[1, 2, 8], production_modified=False, accuracy_qualified=False))
    started = time.monotonic()
    last = 0.
    acquired = False
    def guard():
        nonlocal last
        assert time.monotonic() - started < 300
        if time.monotonic() - last > 3:
            assert safe_read_only_resources() and torch.cuda.mem_get_info()[0] > 3_000_000_000
            last = time.monotonic()
    try:
        with LOCK.open('x') as f:
            f.write(str(os.getpid()))
        acquired = True
        q = read(qp)
        weights = np.tile(np.arange(1., 3.), (2, 1))
        policy_args = {k: v for k, v in args.items() if k != 'context_source'}
        reference, reach = average(q, docs, completed_iterations=2, weights_by_player=weights, guard=guard, device='cpu', **policy_args)
        policies = [probabilities(q, doc, device='cpu', **policy_args)[0] for doc in docs]
        history = histories(q['observations'])
        assert any(history)
        numerator = np.zeros_like(reference)
        denominator = np.zeros_like(reach)
        for i, o in enumerate(q['observations']):
            for g, policy in enumerate(policies):
                mass = weights[o['actor'], g]
                for ancestor, action in history[i]:
                    mass *= policy[ancestor, action]
                numerator[i] += mass * policy[i]
                denominator[i] += mass
        for i, o in enumerate(q['observations']):
            if denominator[i]:
                numerator[i] /= denominator[i]
            else:
                numerator[i, :o['n']] = 1. / o['n']
        assert np.max(abs(numerator - reference)) < 1e-10 and np.max(abs(denominator - reach)) < 1e-10
        cases = []
        for chunk in (1, 2, 8):
            bank = WeightedCudaBank64(docs, weights, completed_iterations=2, models_per_chunk=chunk, guard=guard, **args)
            got, gr = bank.average(q, guard=guard)
            error = float(np.max(abs(got - reference)))
            reach_error = float(np.max(abs(gr - reach)))
            assert error < 1e-10 and reach_error < 1e-10
            cases.append(dict(chunk=chunk, policy_error=error, reach_error=reach_error))
        rejected = []
        for label, changed, count in [('reordered', docs[::-1], 2), ('incomplete', docs[:1], 2),
                                      ('unplayed', docs + [checkpoint.model_document(objects, state['next_model'], **args)], 2)]:
            try:
                WeightedCudaBank64(changed, weights, completed_iterations=count, guard=guard, **args)
            except ValueError:
                rejected.append(label)
            else:
                raise AssertionError('Accepted ' + label)
        bad = copy.deepcopy(q)
        root = next(o for o in bad['observations'] if int(o['hi']) == 1)
        root['own_history'] = [[0, 0]]
        try:
            bank.average(bad, guard=guard)
        except (ValueError, TypeError):
            rejected.append('invalid root ancestry')
        else:
            raise AssertionError('Accepted invalid root ancestry')
        for path, digest in inputs.items():
            assert sha(path) == digest, path
        result = dict(passed=True, cases=cases, rejected=rejected, observations=len(q['observations']),
                      registration_sha256=sha(registration), seconds=time.monotonic() - started,
                      accuracy_qualified=False, production_modified=False)
        save(OUT / f'{PREFIX}-result.json', result)
        print(result, flush=True)
    finally:
        if acquired:
            assert LOCK.read_text() == str(os.getpid())
            LOCK.unlink()


if __name__ == '__main__':
    main()
