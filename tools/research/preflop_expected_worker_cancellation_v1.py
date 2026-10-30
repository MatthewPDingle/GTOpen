"""Cooperative cancellation for exactly owned spawned research pools.

No PID-based termination, native retry, or unrelated process control. Workers
check the shared event at native polling and CPU-operation boundaries; cleanup
waits for those checks and cancels jobs which have not started.
"""
from contextlib import contextmanager


@contextmanager
def coordinated_pool(executor, cancel_event):
    try:
        yield executor
    except BaseException:
        cancel_event.set()
        executor.shutdown(wait=True, cancel_futures=True)
        raise
    else:
        executor.shutdown(wait=True)
