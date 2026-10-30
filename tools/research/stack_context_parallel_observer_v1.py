"""Observe one existing study helper; never start, stop or modify study work.

Process identity is PID plus creation time and exact script path. GPU activity
is device-wide, not attribution to research. Arm status can outlive its phase;
only published cycle counts prove completed work. CPU samples may miss short
children. This is operational telemetry, not a scientific evaluation.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import time
import traceback
import psutil

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
STORE = Path('S:/GTOpen-research/stack-context-matched-learning-v1')
NAME = 'stack-context-parallel-observer-v1'
HELPER_PID = 31052
HELPER_CREATED = 1790739066.0216312
HELPER_SCRIPT = ROOT/'tools/research/stack_context_parallel_admission_v2.py'
ADMISSION = 'stack-context-parallel-admission-v2'
TRAINER = 'stack-context-parallel-continuation-v2'
ARMS = ('A-baseline', 'A-relative', 'B-baseline', 'B-relative')
MAX_SECONDS = 25*3600
MAX_LOG_BYTES = 25_000_000


def read(path):
    try:
        return json.loads(path.read_bytes())
    except FileNotFoundError:
        return None


def write_new(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, sort_keys=True, allow_nan=False)
        stream.write('\n')


def live_helper():
    try:
        p = psutil.Process(HELPER_PID)
        if abs(p.create_time()-HELPER_CREATED) >= .01:
            return None
        command = p.cmdline()
        if not any(Path(arg) == HELPER_SCRIPT for arg in command):
            return None
        return p
    except psutil.NoSuchProcess:
        return None


def gpu_snapshot():
    answer = subprocess.run(['nvidia-smi',
        '--query-gpu=utilization.gpu,memory.used,memory.free,power.draw',
        '--format=csv,noheader,nounits'], capture_output=True, text=True,
        timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
    if answer.returncode:
        return dict(unavailable=True, exit_code=answer.returncode)
    values = answer.stdout.strip().splitlines()[0].split(',')
    return dict(zip(('utilization_percent', 'used_mib', 'free_mib', 'power_watts'),
                    (float(v.strip()) for v in values)))


def snapshot(progress_cache=None):
    cache = {} if progress_cache is None else progress_cache
    now = time.time(); helper = live_helper()
    result = dict(unix=now, utc=datetime.datetime.fromtimestamp(now, datetime.timezone.utc).isoformat(),
        helper_identity_live=helper is not None, system_cpu_percent=psutil.cpu_percent(interval=0.1),
        available_ram_bytes=psutil.virtual_memory().available, gpu=gpu_snapshot(),
        admission=read(OUT/(ADMISSION+'-status.json')),
        continuation=read(OUT/(TRAINER+'-status.json')), arms={}, processes=[])
    for arm in ARMS:
        status = read(OUT/(TRAINER+'-'+arm+'-status.json'))
        path = STORE/arm/'progress.json'
        stamp = path.stat().st_mtime_ns
        if cache.get(arm, {}).get('stamp') != stamp:
            progress = read(path)
            last = progress['updates'][-1] if progress['updates'] else None
            cache[arm] = dict(stamp=stamp, completed_cycles=progress['completed_cycles'],
                last_published_cycle_seconds=None if last is None else last['collection_seconds'],
                recovered_without_repeat=False if last is None else last.get('recovered_without_scientific_repeat', False))
        result['arms'][arm] = dict(cache[arm], reported_status=status,
            reported_status_age_seconds=None if status is None else now-status['unix'])
    if helper:
        for process in [helper, *helper.children(recursive=True)]:
            try:
                with process.oneshot():
                    cpu = process.cpu_times()
                    result['processes'].append(dict(pid=process.pid, created=process.create_time(),
                        name=process.name(), cpu_seconds=cpu.user+cpu.system,
                        rss_bytes=process.memory_info().rss, threads=process.num_threads()))
            except psutil.NoSuchProcess:
                pass
    result['terminal_files'] = [str(path) for path in
        (OUT/(ADMISSION+'-result.json'), OUT/(ADMISSION+'-failure.json'),
         OUT/(TRAINER+'-training-result.json'), OUT/(TRAINER+'-failure.json')) if path.exists()]
    return result


def watch():
    attempt, result, failure, log = (OUT/(NAME+suffix) for suffix in
        ('-attempt.json', '-result.json', '-failure.json', '.jsonl'))
    if any(p.exists() for p in (attempt, result, failure, log)):
        raise ValueError('Observer already has evidence; do not duplicate it')
    if live_helper() is None:
        raise ValueError('The specified helper identity is not live')
    started = time.time(); cache = {}; first_counts = None; last = None; count = 0
    write_new(attempt, dict(pid=psutil.Process().pid, created=psutil.Process().create_time(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        helper_pid=HELPER_PID, helper_created=HELPER_CREATED, helper_script=str(HELPER_SCRIPT),
        maximum_seconds=MAX_SECONDS, maximum_log_bytes=MAX_LOG_BYTES,
        waiting_interval_seconds=60, active_interval_seconds=15,
        scientific_work_started=False, registered_inputs_changed=False, production_modified=False))
    psutil.cpu_percent(interval=0.1)
    try:
        with log.open('x', encoding='utf-8', newline='\n') as stream:
            while True:
                last = snapshot(cache); count += 1
                counts = {a:r['completed_cycles'] for a,r in last['arms'].items()}
                if first_counts is None:
                    first_counts = counts
                line = json.dumps(last, separators=(',', ':'), allow_nan=False)+'\n'
                if stream.tell()+len(line.encode()) > MAX_LOG_BYTES:
                    reason = 'telemetry-byte-bound'; break
                stream.write(line); stream.flush()
                if not last['helper_identity_live']:
                    reason = 'tracked-helper-ended-or-identity-changed'; break
                if last['terminal_files']:
                    # A terminal file is not evidence that its owner has exited.
                    # Keep observing the same live process while it drains.
                    pass
                if time.time()-started >= MAX_SECONDS:
                    reason = 'telemetry-time-bound'; break
                active = len(last['processes']) > 2
                time.sleep(15 if active else 60)
        write_new(result, dict(observer_complete=True, reason=reason, samples=count,
            elapsed_seconds=time.time()-started, first_published_counts=first_counts,
            last_published_counts={a:r['completed_cycles'] for a,r in last['arms'].items()},
            last_helper_identity_live=last['helper_identity_live'], terminal_files=last['terminal_files'],
            log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),
            research_success_inferred=False, production_modified=False))
    except BaseException as error:
        write_new(failure, dict(error=repr(error), traceback=traceback.format_exc(),
            telemetry_only=True, study_processes_untouched=True))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--watch', action='store_true')
    args = parser.parse_args()
    if args.watch:
        watch()
    else:
        print(json.dumps(snapshot(), separators=(',', ':'), allow_nan=False))
