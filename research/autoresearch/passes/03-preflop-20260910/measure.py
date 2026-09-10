"""Bound a single frozen benchmark and preserve raw evidence; no code generation."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUN = json.loads((HERE / 'run.json').read_text(encoding='utf-8'))
LAB = Path(RUN['worktree'])

def live_busy():
    for path in ['status', 'preflop/status', 'reports/status']:
        with urllib.request.urlopen(f"http://127.0.0.1:56708/api/{path}", timeout=3) as response:
            state = json.load(response)
        if state.get('state') == 'running' or state.get('running'):
            return True
    return False

def main():
    run_id, fixture, iterations = sys.argv[1:4]
    if live_busy():
        raise SystemExit('User workload active; research deferred.')
    deadline = dt.datetime.fromisoformat(RUN['deadline_utc'].replace('Z', '+00:00'))
    if dt.datetime.now(dt.timezone.utc) >= deadline:
        raise SystemExit('Research deadline reached; no new experiment started.')
    raw = HERE / 'raw'
    raw.mkdir(exist_ok=True)
    log = raw / f'{run_id}.log'
    if log.exists():
        raise SystemExit('Run ID already exists; choose a unique ID.')
    exe = LAB / 'target/release/examples/preflop_research_bench.exe'
    env = os.environ.copy()
    env['PATH'] = str(ROOT / '.cuda-nvrtc/nvidia/cuda_nvrtc/bin') + os.pathsep + env['PATH']
    env['SOLVER_THREADS'] = '16'
    env['RAYON_NUM_THREADS'] = '16'
    commit = subprocess.check_output(['git','-C',str(LAB),'rev-parse','HEAD'],text=True).strip()
    record = {'id': run_id, 'utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'commit': commit,
              'fixture': fixture, 'fixture_sha256': hashlib.sha256(Path(fixture).read_bytes()).hexdigest(),
              'iterations': int(iterations), 'executable_sha256': hashlib.sha256(exe.read_bytes()).hexdigest()}
    start = time.monotonic()
    reason = None
    with log.open('w', encoding='utf-8') as output:
        proc = subprocess.Popen([str(exe),fixture,iterations,*sys.argv[4:]], cwd=LAB, env=env,
                                stdout=output, stderr=subprocess.STDOUT,
                                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        (HERE/'active.json').write_text(json.dumps({**record,'pid':proc.pid,'log':str(log)}),encoding='utf-8')
        while proc.poll() is None:
            time.sleep(3)
            try:
                busy = live_busy()
            except Exception as error:
                reason = f'Cannot verify user server: {error}'
                busy = True
            if busy or time.monotonic()-start > 600:
                reason = reason or ('User workload started; benchmark interrupted' if busy else '600 second experiment timeout')
                proc.kill()  # Only the benchmark process created above; never the app.
                proc.wait()
                break
    record.update(seconds=time.monotonic()-start, returncode=proc.returncode, reason=reason,
                  rows=[json.loads(line[6:]) for line in log.read_text(encoding='utf-8').splitlines() if line.startswith('BENCH ')])
    with (HERE/'events.jsonl').open('a',encoding='utf-8') as out:
        out.write(json.dumps(record)+'\n')
    (HERE/'active.json').write_text(json.dumps({'running':False,'last':run_id}),encoding='utf-8')
    print(json.dumps(record),flush=True)
    return proc.returncode

if __name__ == '__main__':
    sys.exit(main())
