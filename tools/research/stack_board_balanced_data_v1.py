"""Preparation and bounded resources for a new balanced-board comparison."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from itertools import combinations
from pathlib import Path
import hashlib, json, subprocess, sys, threading, time
import numpy as np
import psutil
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import path_within_research
from owned_windows_job_v1 import OwnedJob
from stack_board_relative_features_v1 import relative_features
from stack_board_relative_data_v1 import extended_context, load, cpu_admission
from stack_price_learning_data_v2 import card_factors
from stack_price_reference_v1 import board_group, conditional_counts
from stack_price_reference_control_v1 import native, RANKS
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import OTHER

SPLITS = ('fit_random', 'fit_structured', 'validation', 'test', 'stress')
LIMIT = 512_000_000

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def worker(request):
    assert sys.stdin.readline().strip() == 'OWNED_START'
    req = json.loads(Path(request).read_bytes())
    store = path_within_research(Path(req['store']))
    assert Path(request).parent == store and store.is_dir()
    records = []
    for task in req['tasks']:
        started = time.monotonic()
        split, index, board = task['split'], task['index'], task['board']
        assert split in SPLITS and type(index) is int and index >= 0
        group = board_group(board)
        assert list(group) == task['canonical_group']
        raw = native(RANKS, board)
        hands = np.asarray([r['hand'] for r in raw['rows']], dtype=np.int64)
        ranks = np.asarray([r['rank'] for r in raw['rows']], dtype=np.int64)
        counts = conditional_counts(board, hands, ranks)
        factors = card_factors(board)
        assert np.array_equal(hands, factors['hands'])
        expected = np.asarray(list(combinations([c for c in range(52) if c not in board], 2)))
        assert np.array_equal(hands, expected)
        canonical = factors['canonical_cards']
        assert canonical.shape == (1081, 7)
        base = store / f'{split}-board-{index}.npz'
        with base.open('xb') as stream:
            np.savez_compressed(stream, features=factors['features'], counts=counts,
                hands=hands, canonical_cards=canonical, lo_actor_zero=factors['lo_actor_zero'])
        extra = np.asarray([relative_features(c[:2], c[2:]) for c in canonical.tolist()])
        ext = store / f'{split}-extra-{index}.npz'
        with ext.open('xb') as stream:
            np.savez_compressed(stream, features=extra)
        records.append(dict(task, file=str(base), sha256=sha(base), extra_file=str(ext),
            extra_sha256=sha(ext), seconds=time.monotonic()-started))
    print(json.dumps(records), flush=True)

def prepare(tasks, store, guard, progress):
    store = path_within_research(Path(store))
    assert store.is_dir() and tasks
    assert len({(t['split'], t['index']) for t in tasks}) == len(tasks)
    start = time.monotonic()
    results = []
    cancel = threading.Event()
    batches = [tasks[i::8] for i in range(min(8, len(tasks)))]
    with OwnedJob() as job:
        def launch(batch):
            if cancel.is_set():
                raise RuntimeError('Preparation cancelled')
            req = store / f"request-{batch[0]['split']}-{batch[0]['index']}.json"
            atomic_json(req, dict(store=str(store), tasks=batch))
            proc = subprocess.Popen([sys.executable, '-B', __file__, str(req)],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=dict(os.environ, CUDA_VISIBLE_DEVICES='-1'), creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                job.assign(proc)
                out, err = proc.communicate(b'OWNED_START\n', timeout=600)
                if proc.returncode:
                    raise RuntimeError(err.decode(errors='replace')[-3000:])
                rows = json.loads(out)
                assert sorted((r['split'], r['index']) for r in rows) == sorted((t['split'], t['index']) for t in batch)
                return rows
            except BaseException:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait(timeout=10)
                raise
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(launch, batch) for batch in batches}
            try:
                while futures:
                    guard()
                    done, futures = wait(futures, timeout=2, return_when=FIRST_COMPLETED)
                    for future in done:
                        results.extend(future.result())
                    if done:
                        progress('preparing', completed=len(results), total=len(tasks))
            except BaseException:
                cancel.set()
                job.close()
                for future in futures:
                    future.cancel()
                raise
        accounting = job.accounting()
        assert accounting['active_processes'] == 0
    return sorted(results, key=lambda r:(r['split'], r['index'])), dict(seconds=time.monotonic()-start, job=accounting)

class Guard:
    def __init__(self, store, seconds, progress, *, gpu=False):
        self.store = Path(store)
        self.deadline = time.monotonic()+seconds
        self.progress, self.gpu = progress, gpu
        self.last = self.last_storage = self.last_gpu = self.wait_seconds = 0.
        self.probes = []
        psutil.cpu_percent(interval=None)
    def common(self):
        assert time.monotonic() < self.deadline, 'Registered work budget exhausted'
        assert production_available() and not OTHER.exists(), 'Production or another study takes priority'
        assert psutil.virtual_memory().available > 24_000_000_000
        assert psutil.disk_usage('S:/').free > 40_000_000_000
        assert psutil.cpu_percent(interval=None) < 75, 'Heavy CPU work takes priority'
    def __call__(self):
        now = time.monotonic()
        if now-self.last < 2:
            return
        self.common()
        self.last = now
        if now-self.last_storage > 20:
            size = 0
            for path in self.store.rglob('*'):
                try:
                    if path.is_file():
                        size += path.stat().st_size
                except FileNotFoundError:
                    assert path.name.startswith('.partial-')
            assert size < LIMIT
            self.last_storage = now
        if self.gpu:
            import torch
            from river_matched_training_pilot_v1 import gpu_snapshot, memory_admitted, CUDA_BUDGET_BYTES
            assert torch.cuda.memory_allocated() <= CUDA_BUDGET_BYTES and torch.cuda.memory_reserved() <= CUDA_BUDGET_BYTES
            if now-self.last_gpu > 30:
                torch.cuda.synchronize()
                time.sleep(1.2)
                began = time.monotonic()
                announced = False
                while True:
                    self.common()
                    probe = gpu_snapshot()
                    reserved = torch.cuda.memory_reserved()
                    self.probes.append(dict(own_reserved_bytes=reserved, **probe))
                    if probe['utilization_percent'] < 65 and memory_admitted(probe['free_bytes'], reserved):
                        break
                    if not announced:
                        self.progress('yielding_to_heavy_gpu_work', **probe)
                        announced = True
                    time.sleep(5)
                self.wait_seconds += time.monotonic()-began
                self.last_gpu = time.monotonic()

if __name__ == '__main__':
    assert len(sys.argv) == 2
    worker(sys.argv[1])
