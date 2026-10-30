"""One frozen matched equity-pricing experiment; research-only terminal river."""
import time
INVOKED = time.monotonic()
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONDONTWRITEBYTECODE='1')
import argparse
import gc
import json
from pathlib import Path
import sys
import traceback
import uuid
import numpy as np
import torch
import river_matched_training_pilot_v1 as pilot
from global_research_inventory_v3 import measure as inventory
from stack_board_balanced_data_v1 import prepare, load, extended_context, cpu_admission, Guard as BaseGuard
from stack_board_balanced_sampler_v1 import _select, allocation, board_cell
from stack_price_reference_control_v1 import native, NATIVE, RANKS, public_key
from stack_price_reference_v1 import price
from stack_price_learning_data_v2 import public_factors
from stack_board_balanced_metrics_v1 import TOLERANCE_POLICY
import stack_equity_priced_comparison_v1 as comparison

ROOT, OUT = pilot.ROOT, pilot.OUT
NAME = 'stack-equity-priced-learning-v1'
STORE = Path('S:/GTOpen-research') / NAME
REG, PREPARED, RESULT, STATUS = (OUT / (NAME + s + '.json')
                                for s in ('-registration', '-prepared', '-result', '-status'))
GEOMETRY = Path('S:/GTOpen-research/stack-geometry-control-v1')
DEPTHS, HELDOUT, SEEDS = (20, 40, 100, 200, 400), (60, 150), (9297601, 9297602)
LIMIT, RESERVE, SECONDS = 256_000_000, 128_000_000, 3600
read, sha, write = pilot.read, pilot.sha, pilot.atomic_json


def progress(state, **values):
    pilot.STATUS = STATUS
    pilot.status(state, **values)
    print(json.dumps(dict(state=state, **values)), flush=True)


class Guard(BaseGuard):
    def __init__(self, seconds, *, gpu=False):
        super().__init__(STORE, seconds, progress, gpu=gpu)
        self.small_limit_checked = 0.

    def __call__(self):
        super().__call__()
        if time.monotonic() - self.small_limit_checked > 20:
            assert sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()) < LIMIT
            self.small_limit_checked = time.monotonic()


def select_fresh_boards(excluded):
    # New scientific split contract: training is reused, not redrawn. Reuse the
    # qualified sampler engine with zero NEW fit boards and unchanged quotas.
    return _select(9297600, excluded, (('fit_random', 0), ('fit_structured', 0),
                   ('validation', 128), ('test', 128), ('stress', 64)),
                   max_candidates=100000, max_bucket_candidates=10000)


def specification():
    old_reg = OUT / 'stack-board-balanced-learning-v1-registration.json'
    old_result = OUT / 'stack-board-balanced-learning-v1-result.json'
    old = read(old_reg)
    result = read(old_result)
    assert result['complete'] and result['registration_sha256'] == sha(old_reg)
    # The old independent verification FAILED; only reuse immutable reference
    # data, never promote its numerical policy measurements as verified truth.
    training = [r for r in result['board_records'] if r['split'] in ('fit', 'fit_random')]
    assert len(training) == 1024
    excluded = set(map(tuple, old['excluded_probe_groups']))
    excluded.update(tuple(r['canonical_group']) for r in result['board_records'])
    assert len({tuple(r['canonical_group']) for r in training}) == 1024
    paths = [Path(__file__), old_reg, old_result, NATIVE, RANKS,
             ROOT / 'tools/research/stack_equity_priced_readback_v1.py',
             ROOT / 'tools/research/test_stack_equity_priced_run_v1.py',
             OUT / 'STACK-EQUITY-PRICED-CANDIDATE.md']
    for name in ('stack-equity-priced-control-v1', 'stack-equity-priced-integration-control-v1'):
        rp, proof_path = OUT / (name + '-registration.json'), OUT / (name + '-result.json')
        proof = read(proof_path)
        assert proof['passed'] and proof['registration_sha256'] == sha(rp)
        pilot.verify(read(rp)['inputs'])
        paths.extend((rp, proof_path))
    for r in training:
        for key, digest in (('file', 'sha256'), ('extra_file', 'extra_sha256')):
            assert sha(r[key]) == r[digest]
            paths.append(Path(r[key]))
    for d in (*DEPTHS, *HELDOUT):
        paths.extend((GEOMETRY / f'stack-{d}-public.json', GEOMETRY / 'fixtures' / f'stack-{d}-context.json'))
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and Path(path).is_relative_to(ROOT) and Path(path).suffix == '.py':
            paths.append(Path(path))
    boards = select_fresh_boards(excluded)
    assert len(boards) == 320 and len({tuple(b['canonical_group']) for b in boards}) == 320
    assert not {tuple(b['canonical_group']) for b in boards} & excluded
    return dict(format=1, inputs={str(p): sha(p) for p in paths},
        authorization='Active user goal: Proceed with your study. I will check in later.',
        scope=comparison.equity_model.SCOPE, reused_training_boards=training, boards=boards,
        excluded_groups=sorted(excluded), board_seed=9297600, seeds=list(SEEDS), arms=list(comparison.ARMS),
        fitting_depths=list(DEPTHS), heldout_depths=list(HELDOUT),
        fitting_boards=1024, validation_boards=128, test_boards=128, stress_boards=64,
        steps=comparison.STEPS, batch_size=comparison.BATCH_SIZE, checkpoints=list(comparison.CHECKPOINTS),
        optimizer=dict(type='Adam', learning_rate=.001, betas=[.9, .999], eps=1e-8, weight_decay=0, foreach=False),
        sampling='One shared batch per update; uniform depth, state within depth, and training holding',
        training_dtype='float32', evaluation_dtype='widened-float64 for both arms',
        objective='Same two-action stack-normalized value MSE; exact zero fold value only in candidate',
        selection='Minimum equally weighted context normalized decision loss; earliest checkpoint on ties',
        primary='Equity-pricing versus direct-value, fresh random test at 60/150bb, each seed separately',
        minimum_relative_improvement=.2, maximum_mean_loss_stack_fraction=.001,
        unequal_capacity=True, learned_parameters=dict(direct_value=58504, equity_priced=16513),
        stress_allocation=allocation(64), maximum_work_seconds=SECONDS, maximum_preparation_seconds=600,
        readback_maximum_seconds=1800, readback_workers=4, preparation_workers=8,
        readback_tolerances=TOLERANCE_POLICY, readback_collect_all_numeric_failures=True,
        maximum_new_bytes=LIMIT, reserve_bytes=RESERVE, global_allocated_cap=pilot.GLOBAL_LIMIT,
        maximum_cuda_bytes=pilot.CUDA_BUDGET_BYTES, external_cuda_headroom_bytes=2_000_000_000,
        retry_started_attempt=False, historical_readback_remains_failed=True,
        preflop_accuracy_qualified=False, production_modified=False)


def inventory_admission():
    rows = inventory()
    allocated = sum(r['allocated_file_bytes'] for r in rows)
    assert allocated + LIMIT + RESERVE <= pilot.GLOBAL_LIMIT
    return dict(rows=rows, allocated_bytes=allocated)


def qualified_context(depth):
    public = public_factors(read(GEOMETRY / f'stack-{depth}-public.json'))
    control = native(NATIVE, ['control', GEOMETRY / 'fixtures' / f'stack-{depth}-context.json'])
    assert control['passed']
    lookup = {public_key(row): row for row in control['templates'] if row['legal_actions'] == 2}
    assert set(lookup) == {r['hi'] for r in public['rows']}
    for row in public['rows']:
        actual = lookup[row['hi']]
        assert actual['actor'] == row['actor'] and actual['call_ends_showdown']
        assert np.max(abs(np.asarray(price(row)['endpoints_loss_tie_win']) - actual['endpoints_loss_tie_win'])) < 1e-9
    return extended_context(public), control


def prepare_stage(spec):
    assert not any(p.exists() for p in (REG, PREPARED, RESULT, STORE))
    probe = cpu_admission()
    if not probe['admitted']:
        progress('deferred_before_preparation', probe=probe)
        return
    with pilot.LOCK.open('x') as stream:
        stream.write(str(os.getpid()))
    try:
        accounting = inventory_admission()
        write(REG, spec)
        pilot.create(STORE)
        guard = Guard(600 - (time.monotonic() - INVOKED))
        guard()
        records, timing = prepare([b for b in spec['boards'] if b['split'] == 'validation'], STORE, guard, progress)
        for depth in DEPTHS:
            guard()
            _, proof = qualified_context(depth)
            write(STORE / f'fitting-{depth}-terminal-control.json', proof)
        for lo in range(0, len(records) + len(spec['reused_training_boards']), 16):
            guard()
            load((spec['reused_training_boards'] + records)[lo:lo + 16])
        pilot.verify(spec['inputs'])
        guard()
        assert not torch.cuda.is_initialized()
        write(PREPARED, dict(passed=True, complete=True, registration_sha256=sha(REG),
            records=spec['reused_training_boards'] + records, seconds=time.monotonic() - INVOKED,
            timing=timing, accounting=accounting, training_started=False, test_labels_prepared=False,
            stress_labels_prepared=False, artifacts={str(p): sha(p) for p in STORE.rglob('*') if p.is_file()}))
        progress('prepared_for_gpu', seconds=time.monotonic() - INVOKED, training_boards=1024, validation_boards=128)
    except BaseException as error:
        write(OUT / (NAME + '-prepare-interruption-' + uuid.uuid4().hex[:8] + '.json'),
              dict(error=repr(error), traceback=traceback.format_exc()))
        raise
    finally:
        assert pilot.LOCK.read_text() == str(os.getpid())
        pilot.LOCK.unlink()


def gates(tests):
    rows = []
    for seed in SEEDS:
        groups = [[c for c in next(t for t in tests if (t['seed'], t['arm'], t['split']) ==
                  (seed, arm, 'test'))['score']['contexts'] if c['stack'] in HELDOUT] for arm in comparison.ARMS]
        assert all({c['stack'] for c in group} == set(HELDOUT) and len(group) == 2 for group in groups)
        before, after = (float(np.mean([c['mean_regret_stack_fraction'] for c in group])) for group in groups)
        absolute = all(c['mean_regret_stack_fraction'] <= .001 for c in groups[1])
        rows.append(dict(seed=seed, baseline=before, candidate=after, absolute_gate=absolute,
                         relative_reduction=1 - after / before if before else None,
                         passed=bool(before > 0 and after <= .8 * before and absolute)))
    return rows


def run_stage(spec):
    assert read(REG) == json.loads(json.dumps(spec)), 'Frozen specification changed'
    prepared = read(PREPARED)
    assert prepared['passed'] and prepared['complete'] and prepared['registration_sha256'] == sha(REG)
    assert not prepared['training_started'] and not prepared['test_labels_prepared'] and not prepared['stress_labels_prepared']
    pilot.verify(prepared['artifacts'])
    pilot.verify(spec['inputs'])
    attempt = STORE / 'gpu-attempt.json'
    assert not RESULT.exists() and not attempt.exists(), 'Do not retry a started scientific attempt'
    ready, probe = pilot.available()
    if not ready:
        progress('prepared_waiting_for_gpu', probe=probe)
        return
    with pilot.LOCK.open('x') as stream:
        stream.write(str(os.getpid()))
    try:
        accounting = inventory_admission()
        write(attempt, dict(registration_sha256=sha(REG), preparation_sha256=sha(PREPARED), accounting=accounting, probe=probe))
        guard = Guard(SECONDS - prepared['seconds'] - (time.monotonic() - INVOKED), gpu=True)
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.cuda.set_per_process_memory_fraction(pilot.CUDA_BUDGET_BYTES / torch.cuda.get_device_properties(0).total_memory)
        contexts = [extended_context(public_factors(read(GEOMETRY / f'stack-{d}-public.json'))) for d in DEPTHS]
        guard()
        train = comparison.Dataset(load(spec['reused_training_boards']), contexts, terminal_call_confirmed=True)
        validation = comparison.Dataset(load([r for r in prepared['records'] if r['split'] == 'validation']), contexts, terminal_call_confirmed=True)
        paired, fits = [], []
        for seed in SEEDS:
            guard()
            folder = STORE / f'seed-{seed}'
            pilot.create(folder)
            progress('starting_paired_fit', seed=seed)
            fitted = comparison.fit_pair(seed, train, validation, folder, guard, progress)
            write(STORE / f'paired-fit-{seed}.json', fitted)
            paired.append(fitted)
            fits.extend(fitted['fits'])
        selected = dict(registration_sha256=sha(REG), preparation_sha256=sha(PREPARED),
            candidates=[dict(seed=f['seed'], arm=f['arm'], selected=f['selected']) for f in fits],
            test_labels_prepared=False, stress_labels_prepared=False, heldout_labels_prepared=False,
            shared_batch_objects=True, evaluation_dtype='widened-float64')
        frozen = STORE / 'frozen-selection.json'
        write(frozen, selected)
        del train, validation
        gc.collect()
        torch.cuda.empty_cache()
        progress('selection_frozen', sha256=sha(frozen))
        fresh, timing = prepare([b for b in spec['boards'] if b['split'] in ('test', 'stress')], STORE, guard, progress)
        heldout = []
        for depth in HELDOUT:
            guard()
            context, proof = qualified_context(depth)
            write(STORE / f'heldout-{depth}-terminal-control.json', proof)
            heldout.append(context)
        tests = []
        for split in ('test', 'stress'):
            records = [b for b in fresh if b['split'] == split]
            data = comparison.Dataset(load(records), contexts + heldout, terminal_call_confirmed=True)
            for chosen in selected['candidates']:
                guard()
                seed, arm = chosen['seed'], chosen['arm']
                progress('final_test', split=split, seed=seed, arm=arm)
                model = comparison.load(chosen['selected']['weights'], seed, arm, 'cuda')
                result = dict(split=split, seed=seed, arm=arm, selected_step=chosen['selected']['step'],
                    board_keys=[dict(index=b['index'], canonical_group=b['canonical_group']) for b in records],
                    score=comparison.evaluate(model, arm, data, guard, detail=True))
                write(STORE / f'{split}-{seed}-{arm}.json', result)
                tests.append(result)
                del model
            del data
            gc.collect()
            torch.cuda.empty_cache()
        checks = gates(tests)
        pilot.verify(spec['inputs'])
        guard()
        result = dict(passed=True, complete=True, registration_sha256=sha(REG), preparation_sha256=sha(PREPARED),
            selection=dict(file=str(frozen), sha256=sha(frozen)), paired_fits=paired, fits=fits, tests=tests,
            board_records=prepared['records'] + fresh, diagnostic_gates=checks,
            diagnostic_gate_passed=all(g['passed'] for g in checks), fresh_test_preparation=timing,
            artifacts={str(p): sha(p) for p in STORE.rglob('*') if p.is_file()},
            total_work_seconds=prepared['seconds'] + time.monotonic() - INVOKED,
            resource_wait_seconds=guard.wait_seconds, peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
            training_started=True, independent_readback_complete=False, preflop_accuracy_qualified=False,
            production_modified=False)
        assert result['total_work_seconds'] < SECONDS
        write(RESULT, result)
        progress('complete', gates=checks, total_work_seconds=result['total_work_seconds'])
    except BaseException as error:
        write(OUT / (NAME + '-gpu-interruption-' + uuid.uuid4().hex[:8] + '.json'),
              dict(error=repr(error), traceback=traceback.format_exc()))
        raise
    finally:
        assert pilot.LOCK.read_text() == str(os.getpid())
        pilot.LOCK.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=('prepare', 'run'))
    args = parser.parse_args()
    spec = specification()
    (prepare_stage if args.stage == 'prepare' else run_stage)(spec)
