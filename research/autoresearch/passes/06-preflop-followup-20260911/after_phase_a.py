"""Defer compilation/CPU diagnostics until all serial GPU timings finish."""
from run_experiment import HERE, LAB, idle
from run_phase_a import jobs
import json
import subprocess
import sys
import time


def guarded(name, command, cap):
    idle()
    output = HERE / 'raw' / f'{name}.log'
    record_path = HERE / 'raw' / f'{name}-exit.json'
    if output.exists() or record_path.exists():
        raise RuntimeError(f'Existing output for {name}')
    started = time.monotonic()
    reason = None
    with output.open('x') as stream:
        child = subprocess.Popen(command, cwd=LAB, stdout=stream, stderr=subprocess.STDOUT,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            while child.poll() is None:
                time.sleep(1)
                idle()
                if time.monotonic() - started > cap:
                    raise RuntimeError('Owned validation time cap')
        except Exception as error:
            reason = str(error)
            if child.poll() is None:
                # Cargo and the diagnostics driver launch children. Terminate
                # only this freshly spawned owned tree, never the live server.
                subprocess.run(['taskkill', '/PID', str(child.pid), '/T', '/F'],
                               stdout=stream, stderr=subprocess.STDOUT,
                               creationflags=subprocess.CREATE_NO_WINDOW, check=False)
        child.wait(timeout=30)
    record = dict(name=name, command=command, returncode=child.returncode,
                  reason=reason, seconds=time.monotonic()-started)
    record_path.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(record),flush=True)
    if child.returncode or reason:
        raise RuntimeError(reason or f'{name} failed')


def main():
    started = time.monotonic()
    while True:
        finished = []
        for name, *_ in jobs:
            path = HERE / 'raw' / f'{name}-exit.json'
            if path.exists():
                try:
                    result = json.loads(path.read_text())
                except json.JSONDecodeError:
                    continue  # The serial runner may still be writing this record.
                if result.get('returncode') != 0 or result.get('reason'):
                    raise RuntimeError(f'Timed trial failed: {name}')
                finished.append(name)
        if len(finished) == len(jobs):
            break
        if time.monotonic()-started > 15000:
            raise RuntimeError('Deferred validation wait cap; inspect phase A')
        time.sleep(1)
    guarded('phase-b-quality-tests', ['cargo','test','--release','-p','solver',
        '--features','preflop-research','--lib','convergence_quality','--','--nocapture'], 600)
    guarded('phase-b-diagnostic-build', ['cargo','build','--release','-p','solver',
        '--features','preflop-research','--example','convergence_diagnostics'], 600)
    guarded('phase-b-snapshot-diagnostics', [sys.executable,str(HERE/'run_diagnostics.py')], 600)
    guarded('phase-b-diagnostic-summary', [sys.executable,str(HERE/'summarize_diagnostics.py')], 60)


if __name__ == '__main__':
    main()
