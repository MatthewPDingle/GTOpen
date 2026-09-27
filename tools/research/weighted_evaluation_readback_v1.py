"""Bounded CPU readback of frozen batch evidence, preserving input order."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
from collections import deque
import concurrent.futures
import math
import multiprocessing
from pathlib import Path
import time
import psutil
from later_average_support_v1 import load_complete_cache
from owned_columnar_evaluation_archive_v1 import ColumnarEvaluationReader
from hu_showdown_complete_evaluation_review_20260926 import verify_batch, verify_stability, NAMES, GAINS
from bounded_parallel_evaluation_archive_v2 import production_available

STATE = None


def worker_guard():
    assert psutil.virtual_memory().available > 20_000_000_000
    assert production_available()


def initialize(store, manifests, source, roots):
    global STATE
    # Worker checks occur around a batch; the parent checks every two seconds.
    reader = ColumnarEvaluationReader(store, manifests, guard=lambda: None)
    STATE = reader, Path(store), source, load_complete_cache(), roots


def check_one(job):
    worker_guard()
    name, batch = job
    reader, store, source, cache, roots = STATE
    value = verify_batch(reader, store / name, batch, source, cache, roots)
    worker_guard()
    return name, value


def parallel(jobs, *, store, manifests, source, roots, guard, workers=4):
    if type(workers) is not int or not 1 <= workers <= 8:
        raise ValueError('One through eight independent CPU workers required')
    pool = concurrent.futures.ProcessPoolExecutor(max_workers=workers,
        mp_context=multiprocessing.get_context('spawn'), initializer=initialize,
        initargs=(store, manifests, source, roots))
    pending, seen = deque(), set()
    jobs = iter(jobs)
    def submit_next():
        item = next(jobs, None)
        if item is None:
            return
        name = item[0]
        if name in seen or name not in manifests:
            raise ValueError('Duplicate or unregistered evidence batch')
        seen.add(name)
        pending.append((name, pool.submit(check_one, item), time.monotonic()))
    try:
        for _ in range(2 * workers):
            submit_next()
        while pending:
            guard()
            name, future, submitted = pending.popleft()
            while True:
                guard()
                assert time.monotonic() - submitted < 300, 'Readback batch timeout; no automatic retry'
                try:
                    actual, value = future.result(timeout=2)
                    break
                except concurrent.futures.TimeoutError:
                    pass
            assert actual == name
            yield name, value
            submit_next()
    except BaseException:
        # Terminate only children owned by this executor; input evidence remains.
        for process in list(pool._processes.values()):
            if process.is_alive():
                process.terminate()
        raise
    finally:
        pool.shutdown(wait=True, cancel_futures=True)


def verify_analysis(analysis, values, context, *, expected_deals, control_only):
    """Scalar sums and explicit interval formula, separate from the accumulator."""
    n = len(values)
    assert n == expected_deals == analysis['deals'] and n > 1
    assert analysis['profile_order'] == list(NAMES)
    assert analysis['family_error_probability'] == .05 and analysis['accuracy_qualified'] is False
    assert analysis['control_only'] is control_only and analysis['bounds_best_response_above'] is False
    assert len(analysis['contrasts']) == 8 and all(len(v) == 8 for v in values)
    bound = 2 * context['config']['stack'] + context['dead_money']
    error = 0.
    for i, row in enumerate(analysis['contrasts']):
        assert row['name'] == GAINS[i] and row['count'] == n and row['family_error_probability'] == .05
        assert row['bounds_best_response_above'] is False
        x = [v[i] for v in values]
        assert all(math.isfinite(v) and -bound <= v <= bound for v in x)
        mean = math.fsum(x) / n
        variance = math.fsum((v - mean) ** 2 for v in x) / (n - 1)
        radius = math.sqrt(2 * variance * math.log(32 / .05) / n) + 7 * (2 * bound) * math.log(32 / .05) / (3 * (n - 1))
        for key, expected in dict(mean=mean, sample_variance=variance, standard_error=math.sqrt(variance / n),
                                  radius=radius, lower=max(-bound, mean - radius), upper=min(bound, mean + radius)).items():
            difference = abs(row[key] - expected)
            assert math.isfinite(difference) and difference < 1e-8, key
            error = max(error, difference)
    return error
