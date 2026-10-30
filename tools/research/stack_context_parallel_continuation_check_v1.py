"""One-shot parallel scheduling and four-process CUDA inference control.

Uses existing completed first-cycle models and retained native preflop catalogs.
No model fitting, fresh physical deals or scientific evaluation. Does not stop
the original study. These are compatibility checks, not a full-cycle speedup.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
    CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONDONTWRITEBYTECODE='1')
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import sys
import time
import traceback
import numpy as np
import psutil
import torch
import stack_context_parallel_continuation_v1 as runner
import stack_context_full_policy_v1 as full
from stack_context_current_policy_v1 import CurrentPolicy
from stack_context_preflop_export_v1 import queries_from_catalog

NAME = runner.NAME+'-check'
STORE = Path('S:/GTOpen-research')/NAME
OUT = runner.legacy.OUT


def record(path, value):
    runner.save(path, value)


def scheduling_control():
    legacy = runner.legacy
    original = legacy.train; order = legacy.ORDER; status = legacy.status
    context = mp.get_context('spawn'); stop = context.Event(); calls = []; stages = []
    def fake(spec, runtime, native, guard):
        assert legacy.ORDER == ('A-baseline',) and list(runtime) == ['A-baseline']
        for cycle in range(1, 5):
            legacy.status('training', arm='A-baseline', cycle=cycle, phase='start')
            calls.append(cycle)
            if cycle == 2:stop.set()
        return True
    try:
        legacy.train = fake
        answer = runner.arm_loop('A-baseline', {}, {}, {}, lambda:None, stop,
            lambda stage, **values:stages.append((stage, values)))
        assert answer is False and calls == [1, 2]
        assert legacy.ORDER == order and legacy.status is status
        stop.clear(); calls.clear()
        def fail(*args):raise RuntimeError('preserved non-boundary failure')
        legacy.train = fail
        try:runner.arm_loop('A-baseline', {}, {}, {}, lambda:None, stop, lambda *a, **k:None)
        except RuntimeError as e:assert str(e) == 'preserved non-boundary failure'
        else:raise AssertionError('Failure swallowed')
        assert legacy.ORDER == order and legacy.status is status
    finally:
        legacy.train = original
    # Actual live runner must not be mistaken for a normal released owner.
    assert legacy.LOCK.exists()
    assert psutil.Process(runner.LEGACY_PID).create_time() == runner.LEGACY_CREATED
    return dict(stopped_before_third_cycle=True, completed_cycle_order=[1, 2],
        non_boundary_failure_propagated=True, module_state_restored=True, live_legacy_identity_confirmed=True)


def cuda_worker(arm, reference, start, stop, ready):
    try:
        spec = runner.legacy.read(runner.legacy.REG)
        prepared = runner.legacy.read(OUT/'stack-context-population-v1-result.json')
        rt = runner.runtime_for(arm, spec, prepared)
        model = full.read_model(runner.legacy.STORE/arm/'objects', reference, rt['registry'], rt['resources'])
        source = next(r for r in prepared['contexts'].values() if r['depth'] == 20)
        context_source = Path(source['context_path']).read_text()
        query, _ = queries_from_catalog(context_source, runner.legacy.read(source['physical_catalog']))
        torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
        torch.cuda.set_per_process_memory_fraction(2_000_000_000/torch.cuda.get_device_properties(0).total_memory)
        engine = CurrentPolicy(model, rt['registry'], context_sha256=source['context_sha256'],
                               resources=rt['resources'], device='cuda')
        ready.put(arm)
        if not start.wait(timeout=180) or stop.is_set():raise RuntimeError('Parallel check start admission failed')
        begin = time.time()
        p = engine.infer(engine.prepare(query))
        torch.cuda.synchronize()
        ended = time.time()
        np.save(STORE/(arm+'-cuda.npy'), p, allow_pickle=False)
        record(STORE/(arm+'-worker.json'), dict(arm=arm, pid=os.getpid(), process_created=psutil.Process().create_time(),
            begin=begin, end=ended, cuda_reserved_bytes=torch.cuda.memory_reserved(),
            model_sha256=reference['sha256'], rows=len(p)))
    except BaseException as error:
        stop.set()
        record(STORE/(arm+'-failure.json'), dict(error=repr(error), traceback=traceback.format_exc()))
        raise


def main():
    attempt, output, failure = (OUT/(NAME+s+'.json') for s in ('-attempt', '-result', '-failure'))
    if any(p.exists() for p in (STORE, attempt, output, failure)):
        raise ValueError('Preserve completed or failed check; no automatic repeat')
    require = runner.require
    require(runner.legacy.production_available() and psutil.virtual_memory().available > 40_000_000_000,
            'Insufficient idle headroom for bounded check')
    gpu = runner.legacy.gpu_snapshot()
    require(gpu['free_bytes'] > 12_000_000_000 and gpu['utilization_percent'] < 65, 'Yield to heavy GPU work')
    spec = runner.legacy.read(runner.legacy.REG); runner.legacy.verify(spec['inputs'])
    prepared = runner.legacy.read(OUT/'stack-context-population-v1-result.json')
    refs = {}; paths = {Path(__file__).resolve(), Path(runner.__file__).resolve(), runner.legacy.REG}
    for arm in runner.ARMS:
        progress = runner.legacy.read(runner.legacy.STORE/arm/'progress.json')
        first = progress['updates'][0]['checkpoint']
        objects = runner.legacy.STORE/arm/'objects'
        checkpoint = json.loads(runner.legacy.read_object(objects, first))
        require(checkpoint['completed_cycles'] == 1, 'Retained first complete model required')
        refs[arm] = checkpoint['next_model']; paths.update((objects/first['file'], objects/refs[arm]['file']))
    paths.add(OUT/'stack-context-population-v1-result.json')
    paths.update(Path(p) for p in prepared['artifacts'])
    for module in list(sys.modules.values()):
        p = getattr(module, '__file__', None)
        if p and Path(p).is_relative_to(runner.legacy.ROOT) and Path(p).suffix == '.py':paths.add(Path(p))
    inputs = {str(p):runner.sha(p) for p in paths}
    record(attempt, dict(inputs=inputs, models=refs, cuda_processes=4, per_process_cap=2_000_000_000,
        new_fits=False, scientific_evaluation=False, maximum_seconds=600))
    STORE.mkdir(); began = time.monotonic(); processes = []
    try:
        scheduling = scheduling_control()
        source = next(r for r in prepared['contexts'].values() if r['depth'] == 20)
        text = Path(source['context_path']).read_text()
        query, _ = queries_from_catalog(text, runner.legacy.read(source['physical_catalog']))
        torch.set_num_threads(1)
        for arm in runner.ARMS:
            rt = runner.runtime_for(arm, spec, prepared)
            model = full.read_model(runner.legacy.STORE/arm/'objects', refs[arm], rt['registry'], rt['resources'])
            p, _, _ = full.predict(model, rt['registry'], query, context_sha256=source['context_sha256'],
                resources=rt['resources'], device='cpu')
            np.save(STORE/(arm+'-reference.npy'), p, allow_pickle=False)
        ctx = mp.get_context('spawn'); start = ctx.Event(); stop = ctx.Event(); ready = ctx.Queue()
        for arm in runner.ARMS:
            process = ctx.Process(target=cuda_worker, args=(arm, refs[arm], start, stop, ready))
            process.start(); processes.append((arm, process))
        admitted = [ready.get(timeout=180) for _ in runner.ARMS]
        require(set(admitted) == set(runner.ARMS) and not stop.is_set(), 'All four CUDA workers must initialize successfully')
        start.set()
        for arm, process in processes:
            process.join(timeout=180)
            require(not process.is_alive() and process.exitcode == 0, 'Parallel worker did not complete successfully')
        records = []
        for arm in runner.ARMS:
            a = np.load(STORE/(arm+'-reference.npy'), allow_pickle=False)
            b = np.load(STORE/(arm+'-cuda.npy'), allow_pickle=False)
            error = float(np.max(np.abs(a-b)))
            require(a.shape == b.shape and error < 1e-10 and np.array_equal(a > 0, b > 0),
                    'Concurrent inference differs from serial full reference')
            row = runner.legacy.read(STORE/(arm+'-worker.json'))
            require(row['cuda_reserved_bytes'] <= 2_000_000_000, 'Worker exceeded fixed CUDA cap')
            records.append(dict(**row, maximum_reference_error=error))
        require(min(r['end'] for r in records) > max(r['begin'] for r in records), 'CUDA scoring intervals did not overlap')
        require(time.monotonic()-began < 600, 'Check time bound exceeded')
        runner.legacy.verify(inputs); runner.legacy.verify(spec['inputs'])
        result = dict(complete=True, passed=True, seconds=time.monotonic()-began, inputs=inputs,
            runner_sha256=runner.sha(runner.__file__), scheduling=scheduling, concurrent_cuda=records,
            peak_sum_cuda_reserved_bytes=sum(r['cuda_reserved_bytes'] for r in records),
            full_cycle_throughput_measured=False, exact_fit_replay_checked=False, new_fits=False,
            new_scientific_deals=False, scientific_accuracy_qualified=False, production_modified=False,
            artifacts={str(p):runner.sha(p) for p in STORE.iterdir() if p.is_file()})
        record(output, result)
        print(json.dumps(dict(passed=True, seconds=result['seconds'], concurrent_arms=4,
            maximum_reference_error=max(r['maximum_reference_error'] for r in records))))
    except BaseException as error:
        # Never touch the live scientific trainer. Only these bounded fixture
        # processes are signalled, and all check evidence remains on disk.
        if 'stop' in locals():stop.set()
        if 'start' in locals():start.set()
        for _, process in processes:process.join(timeout=180)
        record(failure, dict(error=repr(error), traceback=traceback.format_exc(), preserve_evidence=True,
            automatic_retry_allowed=False))
        raise


if __name__ == '__main__':main()
