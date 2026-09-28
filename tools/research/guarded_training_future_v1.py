"""Poll live worker futures without mistaking a short observation for failure."""
from concurrent.futures import TimeoutError
import math
import time


def result(future, guard, *, maximum_wait_seconds=1200., poll_seconds=2.):
    if (not math.isfinite(maximum_wait_seconds) or not math.isfinite(poll_seconds)
            or maximum_wait_seconds <= 0 or not 0 < poll_seconds <= maximum_wait_seconds):
        raise ValueError('Positive bounded wait and polling intervals required')
    deadline = time.monotonic()+maximum_wait_seconds
    while True:
        guard()
        # Completed work stays complete if resource admission delayed readback.
        # A task's own exception is propagated, including its own TimeoutError.
        if future.done():
            return future.result()
        remaining = deadline-time.monotonic()
        if remaining <= 0:
            raise TimeoutError('Training worker did not finish within its bounded wait')
        try:
            return future.result(timeout=min(poll_seconds, remaining))
        except TimeoutError:
            if future.done():
                return future.result()
