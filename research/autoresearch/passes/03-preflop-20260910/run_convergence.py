"""Run only a predeclared convergence pair, with app and ten-hour deadline guards."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from measure import HERE, ROOT, LAB, live_busy

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    run_id = sys.argv[1]
    protocol = json.loads((HERE/'convergence-protocol.json').read_text(encoding='utf-8'))
    spec = protocol['runs'][run_id]
    exe = Path(spec['executable'])
    input_path = Path(spec['input'])
    output = Path(spec['output'])
    log = HERE/'raw'/f'{run_id}.log'
    if log.exists() or output.exists():
        raise SystemExit('Run/output already exists; never overwrite a trajectory.')
    frozen = [(exe, spec['executable_sha256']), (input_path, spec['input_sha256'])]
    frozen += [(Path(x['path']), x['sha256']) for x in protocol['frozen_dependencies']]
    for path, expected in frozen:
        if sha(path) != expected:
            raise SystemExit(f'Frozen artifact changed: {path}')
    deadline = dt.datetime.fromisoformat(protocol['deadline_utc'].replace('Z', '+00:00'))
    now = dt.datetime.now(dt.timezone.utc)
    if now >= deadline or (deadline-now).total_seconds() < spec['timeout_seconds']:
        raise SystemExit('Insufficient time left in fixed research window for this bounded run.')
    if live_busy():
        raise SystemExit('User workload active; convergence comparison deferred.')
    env = os.environ.copy()
    for key in list(env):
        if key.startswith(('PREFLOP_MW_', 'PREFLOP_PHASE_', 'PREFLOP_GPU_')):
            del env[key]
    env.update(SOLVER_THREADS='16', RAYON_NUM_THREADS='16',
               REALIZATION_FIT=protocol['calibration_fit'], PREFLOP_GPU_LAYOUT_STATS='1')
    env['PATH'] = str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin') + os.pathsep + env['PATH']
    cmd = [str(exe), str(input_path), str(spec['budget_mb']), str(spec['additional_iterations']),
           str(spec['target_gap_bb']), str(spec['check_every']), str(output)]
    record = dict(event='convergence_validation', id=run_id, utc=now.isoformat(),
                  command=cmd, compiled_source=spec['compiled_source'],
                  executable_sha256=spec['executable_sha256'], input_sha256=spec['input_sha256'],
                  protocol_sha256=sha(HERE/'convergence-protocol.json'),
                  timeout_seconds=spec['timeout_seconds'], exception='predeclared final convergence gate')
    start = time.monotonic()
    reason = None
    with log.open('w', encoding='utf-8') as stream:
        proc = subprocess.Popen(cmd, cwd=LAB, env=env, stdout=stream, stderr=subprocess.STDOUT,
                                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        (HERE/'active.json').write_text(json.dumps(dict(record, pid=proc.pid, log=str(log))), encoding='utf-8')
        while proc.poll() is None:
            time.sleep(3)
            try:
                busy = live_busy()
            except Exception as error:
                busy = True
                reason = f'Cannot verify user server: {error}'
            expired = dt.datetime.now(dt.timezone.utc) >= deadline
            timed_out = time.monotonic()-start > spec['timeout_seconds']
            if busy or expired or timed_out:
                reason = reason or ('User workload started' if busy else 'Research deadline' if expired else 'Predeclared convergence timeout')
                proc.kill()  # Only this offline child, never the app.
                proc.wait()
                break
    rows = [json.loads(l[len('CONVERGENCE '):]) for l in log.read_text(encoding='utf-8').splitlines()
            if l.startswith('CONVERGENCE ')]
    result = next((r for r in reversed(rows) if r.get('phase') == 'result'), None)
    record.update(seconds=time.monotonic()-start, returncode=proc.returncode, reason=reason, result=result)
    with (HERE/'events.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(record)+'\n')
    (HERE/'active.json').write_text(json.dumps(dict(running=False,last=run_id)),encoding='utf-8')
    print(json.dumps(record), flush=True)
    if proc.returncode == 0 and result is None:
        raise SystemExit('Missing verified final result.')
    return proc.returncode

if __name__ == '__main__':
    sys.exit(main())
