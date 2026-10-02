"""Actual spawn/Event software control; no typed science or native execution.

The pool initializer is replaced with a synthetic guard-only state. The real
river pool transports the shared Event to a real spawned child and the real
river guard observes it. Static checks cover the real initializer assignment.
Existing source controls and their retained evidence are left intact.
"""
import ast
import copy
import json
import multiprocessing
import os
from pathlib import Path
import sys
import time
from unittest.mock import patch

sys.dont_write_bytecode = True
STAGE = Path(__file__).resolve().parent
sys.path[:0] = [str(STAGE), r'T:\Dev\GTOpen\tools\research']
import preflop_expected_river_workers_v1 as worker


def _forbid_resource_poll(*args, **kwargs):
    raise AssertionError('Cancelled guard reached resource polling')


def _initialize_guard_control(*args):
    assert len(args) == len(worker._INIT_FIELDS)+1
    assert multiprocessing.current_process().name != 'MainProcess'
    assert multiprocessing.get_start_method() == 'spawn'
    event = args[-1]
    assert event is not None and callable(event.is_set)
    now = time.monotonic()
    worker._STATE = dict(cancel_event=event, began=now, last_guard=now,
        runtime_limits=dict(max_worker_seconds=60), retained_sentinel=[1, 2, 3])
    worker.psutil.virtual_memory = _forbid_resource_poll
    worker.psutil.disk_usage = _forbid_resource_poll
    worker.psutil.net_connections = _forbid_resource_poll


def _probe():
    worker.guard()
    return dict(pid=os.getpid(), parent_pid=os.getppid(), start_method=multiprocessing.get_start_method(),
        cancelled=worker._STATE['cancel_event'].is_set(), sentinel=worker._STATE['retained_sentinel'])


def _observe_cancelled():
    # Make polling due; cancellation must still win before the mocked poll.
    worker._STATE['last_guard'] = 0.
    before = copy.deepcopy(worker._STATE['retained_sentinel'])
    try: worker.guard()
    except InterruptedError as error:
        assert worker._STATE['retained_sentinel'] == before
        return dict(pid=os.getpid(), interrupted=True, message=str(error), retained_state_unchanged=True)
    raise AssertionError('Shared parent cancellation event was ignored')


def main():
    source = Path(worker.__file__).resolve()
    tree = ast.parse(source.read_text(encoding='utf-8'))
    initialize = next(v for v in tree.body if isinstance(v, ast.FunctionDef) and v.name == 'initialize')
    assert initialize.args.args[-1].arg == 'cancel_event'
    assert isinstance(initialize.args.defaults[-1], ast.Constant) and initialize.args.defaults[-1].value is None
    assert any(isinstance(v, ast.keyword) and v.arg == 'cancel_event'
        and isinstance(v.value, ast.Name) and v.value.id == 'cancel_event' for v in ast.walk(initialize))
    args = {name:None for name in worker._INIT_FIELDS}
    args['runtime_limits'] = dict(max_worker_seconds=60, native_timeout_seconds=60, river_native_timeout_seconds=60)
    # Existing callers still omit cancel_event without changing required fields.
    with patch.object(worker, 'ProcessPoolExecutor') as mocked_pool:
        worker.pool(1, **args)
        assert mocked_pool.call_args.kwargs['initargs'][-1] is None
    event = multiprocessing.get_context('spawn').Event()
    began = time.monotonic()
    with patch.object(worker, 'initialize', _initialize_guard_control):
        with worker.pool(1, cancel_event=event, **args) as pool:
            ready = pool.submit(_probe).result(timeout=30)
            assert ready['pid'] != os.getpid() and ready['parent_pid'] == os.getpid()
            assert ready['start_method'] == 'spawn' and ready['cancelled'] is False
            event.set()
            observed = pool.submit(_observe_cancelled).result(timeout=10)
            assert ready['pid'] == observed['pid'] and observed['interrupted']
    print(json.dumps(dict(passed=True, controls='spawn/Event software only',
        optional_initializer_and_pool_compatible=True, actual_spawn_event_shared=True,
        cancellation_precedes_resource_polling=True, retained_state_unchanged=True,
        native_executions=0, science_executions=0, seconds=time.monotonic()-began,
        child_pid=ready['pid'], worker_sha256=worker.sha(source), control_sha256=worker.sha(__file__))))


if __name__ == '__main__': main()
