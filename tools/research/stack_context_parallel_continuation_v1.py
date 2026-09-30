"""Operational parallel continuation of the same admitted four-arm study.

The original training implementation, configuration, seeds, targets, fits and
cycle archives remain byte-identical. Each spawned process owns one arm and
uses the original sequential cycle loop. No already-started cycle is retried.
The default command only reports readiness. A verified normal legacy exit and
complete checkpoints are mandatory before --run. This file is not yet admitted.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
    CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONDONTWRITEBYTECODE='1')
import argparse
import ctypes
import json
import multiprocessing as mp
from pathlib import Path
import sys
import time
import traceback
import uuid
import psutil
import torch
import stack_context_matched_learning_v1 as legacy
from board_prefix_publication_v1 import atomic_json
from sampled_physical_root_evaluation_v1 import sha, save
from board_study_storage_v1 import measure
from global_research_inventory_v3 import measure as inventory

NAME = 'stack-context-parallel-continuation-v1'
PLAN = legacy.OUT/'STACK-CONTEXT-PARALLEL-CONTINUATION-PLAN.md'
CONTROL = legacy.OUT/(NAME+'-check-result.json')
AMENDMENT = legacy.OUT/(NAME+'-amendment.json')
HANDOFF = legacy.OUT/(NAME+'-legacy-handoff.json')
STATUS = legacy.OUT/(NAME+'-status.json')
FAILURE = legacy.OUT/(NAME+'-failure.json')
ARMS = tuple(legacy.ORDER)
MAX_CONCURRENT = 4
MAX_LOGICAL = 70_000_000_000
LEGACY_PID = 32368
LEGACY_CREATED = 1790732866.143808


class BoundaryYield(Exception):
    pass


def require(ok, message):
    if not ok:raise ValueError(message)


def logical_bytes(root):
    # Another arm may retire only its verified scratch copies during the walk.
    # A vanished entry is expected; other filesystem errors are not suppressed.
    total = 0
    for path in Path(root).rglob('*'):
        try:
            if path.is_file():total += path.stat().st_size
        except FileNotFoundError:
            continue
    return total


def complete_boundaries():
    require(not legacy.FAILURE.exists() and not FAILURE.exists(), 'Preserve terminal failure; no automatic retry')
    result = {}
    for arm in ARMS:
        folder = legacy.STORE/arm
        progress = legacy.read(folder/'progress.json')
        require(progress['registration_sha256'] == sha(legacy.REG), 'Changed scientific registration')
        count = progress['completed_cycles']
        require(type(count) is int and 0 <= count <= 64 and len(progress['updates']) == count,
                'Invalid complete cycle prefix')
        require(not (folder/f'cycle-{count+1:04d}').exists() and not (folder/f'archive-{count+1:04d}').exists(),
                'Partly started next cycle; do not recollect or hide it')
        if count:
            record = progress['updates'][-1]; archive = legacy.STORE/record['archive']
            require(sha(archive/'index.json') == record['archive_index_sha256']
                and sha(archive/'retired.json') == record['retirement_sha256'], 'Last cycle not fully archived/committed')
        result[arm] = count
    return result


def runtime_for(arm, spec, prepared):
    entries = legacy.read(legacy.POPULATION/'entries.json')
    registry = (legacy.RelativeRegistry if arm.endswith('relative') else legacy.Registry)(entries)
    resources, inputs, _ = legacy.resources_for(registry, prepared, 0 if arm.startswith('A-') else 1)
    require(registry.sha256 == spec['arms'][arm]['config']['registry_sha256'], 'Changed arm registry')
    return dict(registry=registry, resources=resources, inputs=inputs)


def arm_loop(arm, spec, runtime, native, guard, stop, publish):
    """Reuse the admitted cycle loop; changes below affect only this process."""
    original_order, original_status = legacy.ORDER, legacy.status
    def status(stage, **values):
        if stage == 'training' and values.get('phase') == 'start' and stop.is_set():
            raise BoundaryYield('Operator/peer requested stop before any next-cycle work')
        publish(stage, **values)
    try:
        legacy.ORDER = (arm,)
        legacy.status = status
        try:
            return legacy.train(spec, {arm:runtime}, native, guard)
        except BoundaryYield:
            return False
    finally:
        legacy.ORDER, legacy.status = original_order, original_status


def worker(arm, spec, native, stop, invocation):
    path = legacy.OUT/(NAME+'-'+arm+'-status.json')
    outcome = legacy.STORE/(NAME+'-'+invocation+'-'+arm+'.json')
    def publish(stage, **values):
        atomic_json(path, dict(stage=stage, arm=arm, pid=os.getpid(), process_created=psutil.Process().create_time(),
            unix=time.time(), **{k:v for k,v in values.items() if k != 'arm'}), replace=True)
    try:
        publish('loading-existing-arm')
        prepared = legacy.read(legacy.OUT/'stack-context-population-v1-result.json')
        runtime = runtime_for(arm, spec, prepared)
        torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
        torch.cuda.set_per_process_memory_fraction(2_000_000_000/torch.cuda.get_device_properties(0).total_memory)
        guard = legacy.Guard(legacy.read(legacy.ATTEMPT)['admitted_unix'])
        # One supervisor checks total storage. Per-arm walks would race with
        # verified raw-copy retirement in other independently owned folders.
        guard.last_size = float('inf')
        complete = arm_loop(arm, spec, runtime, native, guard, stop, publish)
        save(outcome, dict(arm=arm, complete=complete, stopped_at_complete_boundary=not complete,
            pid=os.getpid(), process_created=psutil.Process().create_time(), unix=time.time(),
            progress_sha256=sha(legacy.STORE/arm/'progress.json')))
        publish('arm-complete' if complete else 'complete-boundary-awaiting-resume')
    except BaseException as error:
        stop.set()  # Other arms may finish their current cycles, never retry.
        save(outcome, dict(arm=arm, failed=True, error=repr(error), traceback=traceback.format_exc(),
            automatic_retry_allowed=False, pid=os.getpid(), process_created=psutil.Process().create_time()))
        publish('terminal-failure')
        raise


def wait_legacy():
    """Hold a real Windows process handle; never infer exit from a stale PID."""
    require(not HANDOFF.exists(), 'Existing handoff evidence must be consumed, not rewritten')
    process = psutil.Process(LEGACY_PID)
    require(abs(process.create_time()-LEGACY_CREATED) < .01 and
            any('stack_context_matched_learning_v1.py' in part for part in process.cmdline()), 'Wrong legacy process identity')
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    kernel.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel.OpenProcess(0x00100000 | 0x1000, False, LEGACY_PID)
    require(handle, 'Cannot observe the legacy process handle')
    try:
        require(abs(process.create_time()-LEGACY_CREATED) < .01, 'Process identity changed while opening handle')
        print(json.dumps(dict(stage='waiting-for-existing-normal-boundary', pid=LEGACY_PID,
            stopping_legacy=False, registered_training_unchanged=True)), flush=True)
        while True:
            code = kernel.WaitForSingleObject(handle, 30000)
            if code == 0:break
            require(code == 258, 'Failed process wait; do not interpret as completed')
            require(time.time()-legacy.read(legacy.ATTEMPT)['admitted_unix'] < 72*3600,
                    'Original scientific deadline reached')
        exit_code = ctypes.c_ulong()
        require(kernel.GetExitCodeProcess(handle, ctypes.byref(exit_code)), 'Cannot obtain definitive process exit')
        require(exit_code.value == 0, 'Legacy runner exited abnormally; preserve evidence')
        status = legacy.read(legacy.STATUS)
        require(status['pid'] == LEGACY_PID and abs(status['process_created']-LEGACY_CREATED) < .01 and
            status['stage'] in ('complete-boundary-awaiting-resume', 'training-complete-awaiting-fresh-evaluation'),
            'Legacy did not publish a normal complete boundary')
        require(not legacy.LOCK.exists() and not legacy.OTHER.exists() and not legacy.FAILURE.exists(),
                'Legacy ownership/failure unresolved')
        boundaries = complete_boundaries()
        save(HANDOFF, dict(pid=LEGACY_PID, process_created=LEGACY_CREATED, observed_exit_code=0,
            verified_process_handle=True, normal_boundary_status=status, completed_cycles=boundaries,
            registration_sha256=sha(legacy.REG), unix=time.time(), stopped_or_restarted_legacy=False))
    finally:
        kernel.CloseHandle(handle)


def main(run=False, wait=False):
    if not run:
        print(json.dumps(dict(prepared=True, admitted=AMENDMENT.exists(), research_owner_present=legacy.LOCK.exists(),
            normal_handoff_observed=HANDOFF.exists(), check_present=CONTROL.exists(), maximum_concurrent_arms=MAX_CONCURRENT)))
        return
    require(not legacy.RESULT.exists() and not legacy.FAILURE.exists() and not FAILURE.exists(), 'Terminal study; do not duplicate/retry')
    control = legacy.read(CONTROL)
    require(control['passed'] and control['complete'] and control['runner_sha256'] == sha(__file__), 'Qualified parallel runner required')
    legacy.verify(control['inputs'])
    if wait and not HANDOFF.exists():wait_legacy()
    handoff = legacy.read(HANDOFF)
    require(handoff['observed_exit_code'] == 0 and handoff['verified_process_handle'] is True
            and handoff['registration_sha256'] == sha(legacy.REG), 'Verified normal same-attempt handoff required')
    require(not legacy.LOCK.exists() and not legacy.OTHER.exists(), 'Another live owner; do not duplicate')
    boundaries = complete_boundaries()
    spec = legacy.read(legacy.REG); legacy.verify(spec['inputs'])
    require(time.time()-legacy.read(legacy.ATTEMPT)['admitted_unix'] < 72*3600, 'Original deadline is unchanged')
    ready, probe = legacy.available()
    if not ready or psutil.virtual_memory().available < 40_000_000_000:
        print(json.dumps(dict(deferred=True, reason='resource-admission', probe=probe))); return
    accounting = inventory(); allocated = sum(row['allocated_file_bytes'] for row in accounting)
    own = measure(legacy.STORE)['allocated_file_bytes']
    require(allocated+max(0, MAX_LOGICAL-own) <= 800_000_000_000, 'Expanded transient reservation exceeds global cap')
    require(probe['free_bytes'] >= 12_000_000_000, 'Four trainers need VRAM headroom above their 8GB combined reservation')
    native = {key:legacy.ROOT/'target/release/examples'/name for key, name in dict(
        bridge='hu_sampled_allin_history_bridge_v1.exe', trace='hu_sampled_action_trace_v2.exe',
        integration='hu_sampled_profile_allin_evaluation_v1.exe', river='hu_river_two_stage_stream_v1.exe',
        board='hu_fixed_board_tree_v1.exe').items()}
    for path in native.values():require(sha(path) == spec['inputs'][str(path)], 'Changed native executable')
    expected = dict(format=1, reason='User requested parallel independent runs and better hardware utilization on 2026-09-30',
        original_registration_sha256=sha(legacy.REG), runner_sha256=sha(__file__), plan_sha256=sha(PLAN),
        check_sha256=sha(CONTROL), maximum_concurrent_arms=4, target_workers_per_arm=4, board_workers_per_arm=1,
        cuda_bytes_per_arm=2_000_000_000, maximum_combined_cuda_bytes=8_000_000_000,
        maximum_new_logical_bytes=MAX_LOGICAL, global_allocated_cap=800_000_000_000,
        resource_policy='Share light desktop/video use; retain original active-solve, heavy-GPU, RAM and disk checks',
        science_unchanged=True, original_72_hour_deadline_unchanged=True, fresh_scientific_attempt=False,
        operational_changes=['independent arms overlap', 'isolated status files', 'one global storage observer',
            '70GB transient logical reservation instead of 45GB', 'up to 8GB combined CUDA instead of one 2GB trainer'])
    if AMENDMENT.exists():require(legacy.read(AMENDMENT) == expected, 'Changed admitted operational amendment')
    with legacy.LOCK.open('x') as stream:stream.write(str(os.getpid()))
    invocation = uuid.uuid4().hex; ctx = mp.get_context('spawn'); stop = ctx.Event(); processes = []
    try:
        if not AMENDMENT.exists():save(AMENDMENT, expected)
        save(legacy.STORE/(NAME+'-invocation-'+invocation+'.json'), dict(pid=os.getpid(),
            process_created=psutil.Process().create_time(), unix=time.time(), boundaries=boundaries, admission=accounting))
        for arm in ARMS:
            if boundaries[arm] == 64:continue
            process = ctx.Process(target=worker, args=(arm, spec, native, stop, invocation), name=arm)
            process.start(); processes.append((arm, process))
        last_report = 0.; pressure = None
        while any(p.is_alive() for _, p in processes):
            for arm, process in processes:
                if process.exitcode not in (None, 0):stop.set()
            if time.monotonic()-last_report > 30:
                size = logical_bytes(legacy.STORE)
                if size > MAX_LOGICAL:
                    pressure = 'Logical evidence cap exceeded'; stop.set()
                atomic_json(STATUS, dict(stage='parallel-training' if not stop.is_set() else 'draining-current-cycles',
                    pid=os.getpid(), process_created=psutil.Process().create_time(), unix=time.time(), logical_bytes=size,
                    arms=[dict(arm=a, pid=p.pid, alive=p.is_alive(), exit_code=p.exitcode) for a,p in processes]), replace=True)
                last_report = time.monotonic()
            for _, process in processes:process.join(timeout=.2)
        failures = [(arm, p.exitcode) for arm,p in processes if p.exitcode != 0]
        require(not failures and pressure is None, 'Parallel failure requires review: '+repr((failures, pressure)))
        outcomes = [legacy.read(legacy.STORE/(NAME+'-'+invocation+'-'+arm+'.json')) for arm,_ in processes]
        require(all(not r.get('failed') for r in outcomes), 'Arm failed; no automatic retry')
        legacy.verify(spec['inputs']); complete_boundaries()
        progress = {arm:legacy.read(legacy.STORE/arm/'progress.json') for arm in ARMS}
        complete = all(row['completed_cycles'] == 64 for row in progress.values())
        if complete:
            save(legacy.RESULT, dict(training_complete=True, scientific_evaluation_complete=False, accuracy_qualified=False,
                registration_sha256=sha(legacy.REG), arms=progress, storage=measure(legacy.STORE), production_modified=False,
                operational_amendment_sha256=sha(AMENDMENT)))
        atomic_json(STATUS, dict(stage='training-complete-awaiting-fresh-evaluation' if complete else 'complete-boundary-awaiting-resume',
            pid=os.getpid(), process_created=psutil.Process().create_time(), unix=time.time(),
            completed_cycles={arm:p['completed_cycles'] for arm,p in progress.items()}), replace=True)
    except BaseException as error:
        stop.set()
        # Never kill another arm midway through a scientific cycle. Preserve
        # the parent ownership until every child has actually stopped.
        for _, process in processes:process.join()
        save(FAILURE, dict(error=repr(error), traceback=traceback.format_exc(), automatic_retry_allowed=False,
            invocation=invocation, original_registration_sha256=sha(legacy.REG)))
        raise
    finally:
        if legacy.LOCK.exists() and legacy.LOCK.read_text() == str(os.getpid()):legacy.LOCK.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--run', action='store_true'); parser.add_argument('--wait', action='store_true')
    args = parser.parse_args(); main(run=args.run, wait=args.wait)
