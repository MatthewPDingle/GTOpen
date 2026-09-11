"""Run expanded offline audits only after the registered GPU queue finishes.

Rebuild convergence_local first. Preserve v1 results and record unsuccessful
audits explicitly; missing/canceled checks must never become passing gates.
"""
from run_experiment import idle, LAB, HERE
import hashlib
import json
import subprocess
import time

LARGE = ['eight-s128-a', 'eight-native-a', 'eight-s64-a', 'eight-s128-b',
         'modeled-native-a', 'modeled-s128-a']
CASES = [(name, 'six-reference-tight-a') for name in
         ['six-native-b', 'six-s64-a', 'six-s128-a', 'six-s128-b', 'six-s128-c']]
CASES += [(name, 'eight-native-a') for name in LARGE[:4]]
CASES += [(name, 'modeled-native-a') for name in LARGE[4:]]


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def require_finished_queue():
    active = json.loads((HERE / 'active.json').read_text())
    if active.get('running') is not False:
        raise RuntimeError('GPU queue is still active; defer CPU audits')
    for name in LARGE:
        exit_record = json.loads((HERE / 'raw' / f'{name}-exit.json').read_text())
        if exit_record.get('returncode') != 0 or exit_record.get('reason'):
            raise RuntimeError(f'{name} did not finish normally; inspect before audits')
        if not (LAB / 'target/convergence' / name / 'final.gtop').exists():
            raise RuntimeError(f'Missing final snapshot for {name}')


def main():
    require_finished_queue()
    exe = LAB / 'target/release/examples/convergence_local.exe'
    exe_hash = digest(exe)
    old = json.loads((HERE / 'raw/six-native-b-local-exit.json').read_text())
    if exe_hash == old['exe_sha256']:
        raise RuntimeError('Build the expanded audit executable before running v2')
    for name, reference_name in CASES:
        require_finished_queue()
        idle()
        candidate = LAB / 'target/convergence' / name / 'final.gtop'
        reference = LAB / 'target/convergence' / reference_name / 'final.gtop'
        output = HERE / 'raw' / f'{name}-local-v2.json'
        log = output.with_suffix('.log')
        record_path = HERE / 'raw' / f'{name}-local-v2-exit.json'
        if any(path.exists() for path in [output, log, record_path]):
            raise RuntimeError(f'Audit output already exists: {name}')
        record = dict(name=name, reference_name=reference_name,
                      exe_sha256=exe_hash, candidate_sha256=digest(candidate),
                      reference_sha256=digest(reference))
        idle()
        started = time.monotonic()
        reason = None
        with log.open('x') as stream:
            process = subprocess.Popen([str(exe), str(candidate), str(reference), str(output)],
                                       cwd=LAB, stdout=stream, stderr=subprocess.STDOUT,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                while process.poll() is None:
                    time.sleep(1)
                    idle()
                    if time.monotonic() - started > 1800:
                        raise RuntimeError('Local audit wall-clock cap reached')
            except Exception as error:
                reason = str(error)
                if process.poll() is None:
                    process.kill()
            process.wait(timeout=30)
        record.update(returncode=process.returncode, reason=reason,
                      seconds=time.monotonic() - started)
        if process.returncode == 0 and reason is None:
            result = json.loads(output.read_text())
            if not result.get('rows') or any('candidate_self' not in row for row in result['rows']):
                record['reason'] = 'Expanded candidate-self audit is missing'
        record_path.write_text(json.dumps(record, indent=2))
        print(json.dumps(record), flush=True)
        if record['reason'] or process.returncode:
            raise RuntimeError(record['reason'] or f'Audit failed: {name}')


if __name__ == '__main__':
    main()
