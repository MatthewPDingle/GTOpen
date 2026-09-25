"""Read-only resource sampling of the already running compact evaluation.

Does not import its worker, inspect poker outcomes, change scheduling, or launch
evaluation jobs. Whole-device utilization includes unrelated applications.
"""
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

import psutil

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'later-action-evaluation-hardware-sample-v1'
WORKER = 49536
CONTROLLER = 41192
SAMPLES = 61
INTERVAL = 5.


def write_new(path, document):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(document, stream, indent=2)


def progress():
    path = OUT/'later-action-compact-evaluation-study-v1.log'
    with path.open('rb') as stream:
        stream.seek(max(0, path.stat().st_size-4096))
        for line in reversed(stream.read().decode('utf-8').splitlines()):
            if line.startswith('{"deals":'):
                record = json.loads(line)
                return {key: record[key] for key in ('deals', 'total', 'seconds')}
    return None


def main():
    registration = OUT/f'{PREFIX}-registration.json'
    result = OUT/f'{PREFIX}-result.json'
    assert not registration.exists() and not result.exists()
    worker, controller = psutil.Process(WORKER), psutil.Process(CONTROLLER)
    births = {p.pid: p.create_time() for p in (worker, controller)}
    assert worker.ppid() == CONTROLLER
    assert 'hu_later_action_compact_evaluation_20260925.py' in ' '.join(worker.cmdline())
    assert '--worker' in worker.cmdline()
    smi = shutil.which('nvidia-smi')
    assert smi
    write_new(registration, dict(worker=WORKER, controller=CONTROLLER,
        process_births=births, samples=SAMPLES, interval_seconds=INTERVAL,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        started=datetime.datetime.now().astimezone().isoformat(),
        purpose='Resource use during the existing evaluation, not a throughput experiment',
        no_poker_outcomes_read=True, live_sources_modified=False,
        limitations='CPU subprocesses shorter than the sample interval may be missed; GPU and whole-computer counters include other applications.'))
    records = []
    start = time.monotonic()
    psutil.cpu_percent(None)
    error = None
    try:
        for index in range(SAMPLES):
            delay = start + index*INTERVAL - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            for pid, birth in births.items():
                if psutil.Process(pid).create_time() != birth:
                    raise RuntimeError('Observed process identity changed')
            processes = []
            for p in [worker, *worker.children(recursive=True)]:
                try:
                    with p.oneshot():
                        cpu = p.cpu_times()
                        processes.append(dict(pid=p.pid, birth=p.create_time(),
                            cpu_seconds=cpu.user+cpu.system, rss=p.memory_info().rss,
                            threads=p.num_threads()))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            response = subprocess.run([smi,
                '--query-gpu=utilization.gpu,utilization.memory,memory.used,memory.total',
                '--format=csv,noheader,nounits'], capture_output=True, text=True,
                timeout=10, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            gpu = [float(value.strip()) for value in response.stdout.strip().split(',')]
            records.append(dict(seconds=time.monotonic()-start,
                cpu_percent=psutil.cpu_percent(None), ram_available=psutil.virtual_memory().available,
                gpu_percent=gpu[0], gpu_memory_activity_percent=gpu[1],
                gpu_used_mib=gpu[2], gpu_total_mib=gpu[3],
                processes=processes, progress=progress()))
            if index % 12 == 0:
                print(json.dumps(dict(sample=index, progress=records[-1]['progress'])), flush=True)
    except Exception as exc:
        error = repr(exc)
        raise
    finally:
        write_new(result, dict(complete=error is None and len(records)==SAMPLES,
            error=error, registration_sha256=hashlib.sha256(registration.read_bytes()).hexdigest(),
            seconds=time.monotonic()-start, records=records,
            production_modified=False, research_run_modified=False))


if __name__ == '__main__':
    main()
