"""Refresh existing research artifacts while one verified queue owner runs.

QUEUE_PID. Bounded presentation helper only: never starts or stops a solve,
changes a gate, accesses production, pushes Git, or reads browser sessions.
"""
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'
DEADLINE = datetime.fromisoformat('2026-09-20T09:05:00+09:30').timestamp()
RENDER = ROOT/'tools/research/overnight_reference_report.py'


def revision(names):
    return tuple((name,(OUT/name).stat().st_mtime_ns,(OUT/name).stat().st_size)
                 if (OUT/name).exists() else (name,None,None) for name in names)


def main():
    owner = psutil.Process(int(sys.argv[1]))
    assert 'overnight_accuracy_queue_20260919.py' in ' '.join(owner.cmdline())
    created = owner.create_time()
    assert owner.is_running()
    lock = OUT/'report-watch.lock'
    with lock.open('x') as f:
        f.write(str(os.getpid()))
    initial = time.monotonic()
    last_key = None
    last_state = None
    last_render = -float('inf')
    renders = failures = 0

    def running():
        try:
            return owner.is_running() and owner.create_time() == created
        except psutil.NoSuchProcess:
            return False

    try:
        with (OUT/'report-watch.log').open('x') as log:
            while time.time() < DEADLINE:
                alive = running()
                key = revision(['report47-full-result.json','independent-transfer-summary.json'])
                state = revision(['overnight-accuracy-status.json'])
                needs_render = key != last_key or not alive or (state != last_state and time.monotonic()-last_render >= 300)
                if needs_render:
                    env = os.environ.copy()
                    env['OPENBLAS_NUM_THREADS'] = '1'
                    env['OMP_NUM_THREADS'] = '1'
                    env['MPLBACKEND'] = 'Agg'
                    try:
                        completed = subprocess.run([sys.executable,str(RENDER)],cwd=ROOT,env=env,
                            stdout=log,stderr=subprocess.STDOUT,timeout=60,
                            creationflags=subprocess.CREATE_NO_WINDOW)
                        assert completed.returncode == 0, f'Render exit {completed.returncode}'
                        last_key,last_state = key,state
                        last_render = time.monotonic()
                        renders += 1
                    except (AssertionError,subprocess.TimeoutExpired) as ex:
                        # A writer may be between JSON truncate and completion.
                        # Keep the solve untouched; retry the presentation only.
                        failures += 1
                        print(f'Render attempt failed: {ex}',file=log,flush=True)
                    status=dict(watcher_pid=os.getpid(),queue_pid=owner.pid,queue_creation_time=created,
                        queue_alive=alive,renders=renders,failed_render_attempts=failures,
                        elapsed_seconds=time.monotonic()-initial,updated=datetime.now().astimezone().isoformat())
                    (OUT/'report-watch-status.json').write_text(json.dumps(status,indent=2)+'\n')
                    print(json.dumps(status),flush=True)
                if not alive:
                    break
                time.sleep(20)
    finally:
        lock.unlink()


if __name__ == '__main__':
    main()
