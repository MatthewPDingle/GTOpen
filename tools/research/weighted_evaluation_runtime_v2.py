"""Resource guard for resumable evaluation with nested attempt archives."""
from pathlib import Path
import re
import time
import psutil
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import OTHER


def owned_scratch_path(path, root):
    try:
        parts = Path(path).relative_to(root).parts
    except ValueError:
        return False
    return (len(parts) >= 3 and re.fullmatch(r'attempt-[0-9a-f]{32}', parts[0]) is not None
            and parts[1] == '.batch-work')


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
                    # A worker may retire verified scratch during this inventory.
                    # Durable archives, metadata and checkpoints may not disappear.
                    assert owned_scratch_path(p, store)
            assert total < maximum_bytes, 'Evidence storage bound reached'
            size_at = now
    return guard
