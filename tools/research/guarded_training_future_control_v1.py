"""Exercise observation expiry, real task failure, bounded expiry and priority."""
from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError
import hashlib
import json
from pathlib import Path
import time
from guarded_training_future_v1 import result


def main():
    checked = []; calls = []
    def guard(): calls.append(time.monotonic())
    def delayed_value(): time.sleep(.035); return 19
    with ThreadPoolExecutor(max_workers=1) as pool:
        assert result(pool.submit(delayed_value), guard, maximum_wait_seconds=1, poll_seconds=.005) == 19
    assert len(calls) >= 2; checked.append('observation_timeouts_keep_live_task')
    real_error = TimeoutError('actual child failure')
    def delayed_error(): time.sleep(.02); raise real_error
    with ThreadPoolExecutor(max_workers=1) as pool:
        try: result(pool.submit(delayed_error), guard, maximum_wait_seconds=1, poll_seconds=.005)
        except TimeoutError as error: assert error is real_error
        else: raise AssertionError('Child failure swallowed')
    checked.append('actual_task_timeout_propagates')
    pending = Future()
    try: result(pending, guard, maximum_wait_seconds=.015, poll_seconds=.005)
    except TimeoutError as error: assert 'bounded wait' in str(error) and not pending.done()
    else: raise AssertionError('Unbounded wait')
    checked.append('bounded_pending_deadline')
    completed = Future(); completed.set_result(23)
    assert result(completed, lambda: time.sleep(.02), maximum_wait_seconds=.01, poll_seconds=.005) == 23
    checked.append('completed_work_survives_delayed_readback')
    stopped = RuntimeError('priority workload')
    def priority(): raise stopped
    try: result(completed, priority)
    except RuntimeError as error: assert error is stopped
    else: raise AssertionError('Priority check skipped')
    checked.append('resource_priority_preserved')
    for maximum, poll in ((0, 1), (float('nan'), 1), (1, float('inf')), (1, 2)):
        try: result(completed, guard, maximum_wait_seconds=maximum, poll_seconds=poll)
        except ValueError: pass
        else: raise AssertionError('Invalid bound accepted')
    checked.append('invalid_wait_parameters_rejected')
    print(json.dumps(dict(passed=True, checks=checked, gpu_used=False, new_poker_deals=0,
        inputs={str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                (Path(__file__), Path(__file__).with_name('guarded_training_future_v1.py'))})), flush=True)


if __name__ == '__main__': main()
