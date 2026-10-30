"""Scalar readback across disjoint immutable evaluation attempts."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
from collections import deque
import concurrent.futures
import json
import multiprocessing
from pathlib import Path
import re
import time
from later_average_support_v1 import load_complete_cache
from owned_columnar_evaluation_archive_v1 import ColumnarEvaluationReader, unlinked, read_bounded, digest
from weighted_evaluation_readback_v1 import worker_guard, verify_batch


class RoutedReader:
    def __init__(self, root, routes, *, guard):
        self.root = unlinked(root)
        self.routes = dict(routes)
        self.guard = guard
        self.readers = {}
        if not routes or set(routes) != {f'test-{i:06d}' for i in range(0, 32 * len(routes), 32)}:
            raise ValueError('Complete contiguous batch routing required')
        groups = {}
        for name, route in self.routes.items():
            if (set(route) != {'attempt', 'owner_sha256', 'manifest_sha256', 'summary_sha256'}
                    or not re.fullmatch(r'attempt-[0-9a-f]{32}', route['attempt'])):
                raise ValueError('Invalid or escaping attempt route')
            groups.setdefault(route['attempt'], {})[name] = route['manifest_sha256']
        for attempt, manifests in groups.items():
            guard()
            folder = unlinked(self.root / attempt)
            if folder.parent != self.root:
                raise ValueError('Attempt outside study')
            owner = read_bounded(folder / 'archive-owner.json', 4096)
            if json.loads(owner)['root'] != str(folder):
                raise ValueError('Wrong archive owner root')
            for name in manifests:
                if self.routes[name]['owner_sha256'] != digest(owner):
                    raise ValueError('Wrong archive owner identity')
            self.readers[attempt] = ColumnarEvaluationReader(folder, manifests, guard=guard)

    def read_bytes(self, path):
        self.guard()
        path = unlinked(path)
        name = path.parent.name
        if path.parent.parent != self.root or name not in self.routes or path.exists():
            raise ValueError('Unknown or ambiguous routed evidence')
        route = self.routes[name]
        raw = self.readers[route['attempt']].read_bytes(self.root / route['attempt'] / name / path.name)
        if path.name == 'summary.json' and digest(raw) != route['summary_sha256']:
            raise ValueError('Routed summary identity changed')
        return raw


STATE = None


def initialize(store, routes, source, roots):
    global STATE
    reader = RoutedReader(store, routes, guard=lambda: None)
    STATE = reader, Path(store), source, load_complete_cache(), roots


def check_one(job):
    worker_guard()
    name, batch = job
    reader, store, source, cache, roots = STATE
    value = verify_batch(reader, store / name, batch, source, cache, roots)
    worker_guard()
    return name, value


def parallel(jobs, *, store, routes, source, roots, guard, workers=4):
    if type(workers) is not int or not 1 <= workers <= 8:
        raise ValueError('One through eight independent CPU workers required')
    pool = concurrent.futures.ProcessPoolExecutor(max_workers=workers,
        mp_context=multiprocessing.get_context('spawn'), initializer=initialize,
        initargs=(store, routes, source, roots))
    pending, seen = deque(), set()
    jobs = iter(jobs)
    def submit_next():
        item = next(jobs, None)
        if item is None:
            return
        name = item[0]
        if name in seen or name not in routes:
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

