"""One independent CPU readback; retain every bounded numerical discrepancy."""
import time
STARTED = time.monotonic()
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
from concurrent.futures import ThreadPoolExecutor
from itertools import permutations
import hashlib
import json
from pathlib import Path
import threading
import traceback
import numpy as np
import psutil
from board_prefix_publication_v1 import atomic_json
from stack_price_learning_data_v2 import public_factors
from stack_equity_priced_comparison_v1 import numpy_scores, ARMS
from stack_board_balanced_metrics_v1 import reference_context, compare_evaluations, evaluation_summary, TOLERANCE_POLICY
from stack_board_balanced_sampler_v1 import board_cell, allocation
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK, OTHER

OUT = Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
NAME = 'stack-equity-priced-learning-v1'
STORE = Path('S:/GTOpen-research') / NAME
GEOMETRY = Path('S:/GTOpen-research/stack-geometry-control-v1')
DEST, ATTEMPT, FAILURE, STATUS = (OUT / (NAME + s + '.json') for s in
                                ('-readback-v1', '-readback-attempt', '-readback-failure', '-readback-status'))
_mutex, _last = threading.Lock(), 0.


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def status(state, **values):
    record = dict(state=state, pid=os.getpid(), process_created=psutil.Process().create_time(), unix=time.time(), **values)
    with _mutex:
        atomic_json(STATUS, record, replace=True)
    print(json.dumps(record), flush=True)


def guard():
    global _last
    with _mutex:
        now = time.monotonic()
        assert now - STARTED < 1800, 'Registered readback execution budget exhausted'
        if now - _last < 2:
            return
        assert production_available() and not OTHER.exists()
        assert psutil.virtual_memory().available > 24_000_000_000
        assert psutil.cpu_percent(interval=None) < 75, 'Heavy CPU work takes priority'
        _last = now


def independently_rebuild_gates(tests, seeds, heldout):
    rows = []
    for seed in seeds:
        means, absolute = {}, True
        for arm in ARMS:
            contexts = next(t['score']['contexts'] for t in tests
                            if (t['seed'], t['arm'], t['split']) == (seed, arm, 'test'))
            selected = [c for c in contexts if c['stack'] in heldout]
            assert len(selected) == 2 and {c['stack'] for c in selected} == set(heldout)
            means[arm] = sum(c['mean_regret_bb'] / c['stack'] for c in selected) / len(selected)
            if arm == ARMS[1]:
                absolute = all(c['mean_regret_bb'] <= c['stack'] / 1000 for c in selected)
        before, after = means[ARMS[0]], means[ARMS[1]]
        rows.append(dict(seed=seed, baseline=before, candidate=after, absolute_gate=absolute,
                         passed=bool(before > 0 and after <= before * .8 and absolute)))
    return rows


def run():
    rp, pp, result_path = (OUT / (NAME + suffix + '.json') for suffix in ('-registration', '-prepared', '-result'))
    reg, prepared, result = read(rp), read(pp), read(result_path)
    assert result['passed'] and result['complete'] and prepared['passed'] and prepared['complete']
    assert result['registration_sha256'] == prepared['registration_sha256'] == sha(rp)
    assert result['preparation_sha256'] == sha(pp)
    assert reg['readback_tolerances'] == TOLERANCE_POLICY
    assert reg['arms'] == list(ARMS) and reg['seeds'] == [9297601, 9297602]
    assert reg['fitting_depths'] == [20, 40, 100, 200, 400] and reg['heldout_depths'] == [60, 150]
    assert reg['steps'] == 8192 and reg['batch_size'] == 4096 and reg['checkpoints'] == [0, 1024, 4096, 8192]
    checked = {}

    def check(path, digest):
        guard()
        assert sha(path) == digest, path
        checked[str(path)] = digest

    def check_ref(ref):
        assert result['artifacts'].get(ref['file'], reg['inputs'].get(ref['file'])) == ref['sha256']
        check(ref['file'], ref['sha256'])

    for path in (rp, pp, result_path):
        check(path, sha(path))
    for mapping in (reg['inputs'], prepared['artifacts'], result['artifacts']):
        for path, digest in mapping.items():
            check(path, digest)
    chosen = read(result['selection']['file'])
    check_ref(result['selection'])
    assert chosen['registration_sha256'] == sha(rp) and chosen['preparation_sha256'] == sha(pp)
    for field in ('test_labels_prepared', 'stress_labels_prepared', 'heldout_labels_prepared'):
        assert chosen[field] is False
    assert chosen['shared_batch_objects'] and chosen['evaluation_dtype'] == 'widened-float64'
    assert len(result['fits']) == len(chosen['candidates']) == 4 and len(result['paired_fits']) == 2
    assert {(c['seed'], c['arm']) for c in chosen['candidates']} == {(s, a) for s in reg['seeds'] for a in ARMS}
    for pair in result['paired_fits']:
        assert pair['seed'] in reg['seeds'] and pair['shared_batch_objects']
        assert pair['steps'] == 8192 and pair['batch_size'] == 4096 and pair['learning_rate'] == .001
        assert pair['training_dtype'] == 'float32' and pair['evaluation_dtype'] == 'widened-float64'
        assert [b['step'] for b in pair['shared_batch_probes']] == list(range(0, 8192, 1024))
        left, right = pair['fits']
        assert [c['batch_rng_sha256'] for c in left['checkpoints']] == [c['batch_rng_sha256'] for c in right['checkpoints']]
    for fit in result['fits']:
        assert [c['step'] for c in fit['checkpoints']] == reg['checkpoints']
        best = min(fit['checkpoints'], key=lambda c: (c['validation']['context_balanced_mean_regret_stack_fraction'], c['step']))
        assert fit['selected'] == best
        assert next(c for c in chosen['candidates'] if (c['seed'], c['arm']) == (fit['seed'], fit['arm']))['selected'] == best
        for checkpoint in fit['checkpoints']:
            check_ref(checkpoint['weights'])
    expected = {(b['split'], b['index']): b for b in reg['reused_training_boards'] + reg['boards']}
    assert len(expected) == len(result['board_records']) == 1344
    assert len({(b['split'], b['index']) for b in result['board_records']}) == 1344
    groups = set()
    for board in result['board_records']:
        e = expected[(board['split'], board['index'])]
        assert board['board'] == e['board'] and board['canonical_group'] == e['canonical_group']
        cards = board['board']
        assert len(cards) == len(set(cards)) == 5 and all(type(c) is int and 0 <= c < 52 for c in cards)
        canonical = min(tuple(sorted((c // 4) * 4 + p[c % 4] for c in cards)) for p in permutations(range(4)))
        assert canonical == tuple(board['canonical_group']) and canonical not in groups
        groups.add(canonical)
        if board['split'] in ('validation', 'test', 'stress'):
            assert canonical not in set(map(tuple, reg['excluded_groups']))
            assert board['cell'] == board_cell(cards)
        check_ref(board)
        check_ref(dict(file=board['extra_file'], sha256=board['extra_sha256']))
    assert {cell: sum(b['split'] == 'stress' and b['cell'] == cell for b in reg['boards'])
            for cell in allocation(64)} == allocation(64)
    datasets = {}
    for split, count in (('test', 128), ('stress', 64)):
        records = [b for b in result['board_records'] if b['split'] == split]
        assert len(records) == count
        cards, counts = [], []
        for board in records:
            with np.load(board['file'], allow_pickle=False) as f, np.load(board['extra_file'], allow_pickle=False) as x:
                assert f['features'].shape == (1081, 362) and x['features'].shape == (1081, 25)
                cards.append(np.concatenate((f['features'], x['features']), axis=1).astype(np.float32))
                counts.append(f['counts'].copy())
        cards, counts = np.concatenate(cards), np.concatenate(counts)
        assert counts.dtype.kind in 'iu' and np.all(counts >= 0) and np.all(counts.sum(1) == 990)
        datasets[split] = dict(cards=cards, equity=(counts[:, 0] + counts[:, 1] / 2) / 990,
            category=np.argmax(cards[:, 269:278], axis=1), board_count=count,
            board_keys=[dict(index=b['index'], canonical_group=b['canonical_group']) for b in records])
    contexts = [public_factors(read(GEOMETRY / f'stack-{d}-public.json')) for d in reg['fitting_depths'] + reg['heldout_depths']]
    assert len(result['tests']) == 8
    assert {(t['seed'], t['arm'], t['split']) for t in result['tests']} == {
        (s, a, split) for s in reg['seeds'] for a in ARMS for split in ('test', 'stress')}

    def one(job):
        candidate, split = job
        seed, arm = candidate['seed'], candidate['arm']
        data = datasets[split]
        with np.load(candidate['selected']['weights']['file'], allow_pickle=False) as f:
            weights = {k: f[k].copy() for k in f.files}
        original = next(t for t in result['tests'] if (t['seed'], t['arm'], t['split']) == (seed, arm, split))
        assert original['board_keys'] == data['board_keys'] and original['selected_step'] == candidate['selected']['step']
        rebuilt = []
        for context in contexts:
            guard()
            def rows():
                for state, public in zip(context['economics'], context['features']):
                    guard()
                    # Preserve original float32 feature construction before
                    # widening. Weights and matrix arithmetic are float64.
                    x = np.concatenate((data['cards'][:, :362] + public, data['cards'][:, 362:]), axis=1)
                    e = np.broadcast_to(state, (len(x), 5))
                    yield numpy_scores(weights, arm, x, e)
            rebuilt.append(reference_context(rows(), data['equity'], context['economics'], data['category'],
                context['stack'], data['board_count'], detail=True, guard=guard))
            status('context_read_back', seed=seed, arm=arm, split=split, stack=context['stack'])
        score = evaluation_summary(rebuilt)
        proof = compare_evaluations(original['score'], score)
        # Numeric disagreement is collected, not an early abort or a retry.
        return dict(seed=seed, arm=arm, split=split, score=score, comparison=proof)

    jobs = [(c, split) for split in ('test', 'stress') for c in chosen['candidates']]
    with ThreadPoolExecutor(max_workers=4) as pool:
        replayed = list(pool.map(one, jobs))
    gates = independently_rebuild_gates(replayed, reg['seeds'], reg['heldout_depths'])
    gate_agreement = all(g['passed'] == next(old for old in result['diagnostic_gates'] if old['seed'] == g['seed'])['passed'] for g in gates)
    passed = all(t['comparison']['passed'] for t in replayed) and gate_agreement
    payload = dict(passed=passed, complete=True, inputs=checked, verified_files=len(checked),
        cpu_replayed=replayed, diagnostic_gates=gates, gate_decisions_agree=gate_agreement,
        tolerance_policy=TOLERANCE_POLICY, all_numeric_context_comparisons_attempted=True,
        rows_replayed=sum(t['score']['rows'] for t in replayed), seconds=time.monotonic() - STARTED,
        new_training=False, new_poker_labels=False, production_modified=False, preflop_accuracy_qualified=False)
    guard()
    assert len(json.dumps(payload, allow_nan=False).encode()) < 128_000_000
    atomic_json(DEST, payload)
    status('complete' if passed else 'numeric_verification_failed', passed=passed, gates=gates,
           rows=payload['rows_replayed'], seconds=payload['seconds'])
    return passed


def main():
    assert not any(p.exists() for p in (LOCK, OTHER, ATTEMPT, DEST, FAILURE))
    assert production_available() and psutil.cpu_percent(interval=1) < 50
    assert psutil.virtual_memory().available > 28_000_000_000
    with LOCK.open('x') as stream:
        stream.write(str(os.getpid()))
    try:
        atomic_json(ATTEMPT, dict(pid=os.getpid(), process_created=psutil.Process().create_time(), source_sha256=sha(__file__)))
        return run()
    except BaseException as error:
        atomic_json(FAILURE, dict(error=repr(error), traceback=traceback.format_exc(), retry_allowed=False))
        status('terminal_error', error=repr(error))
        raise
    finally:
        assert LOCK.read_text() == str(os.getpid())
        LOCK.unlink()


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
