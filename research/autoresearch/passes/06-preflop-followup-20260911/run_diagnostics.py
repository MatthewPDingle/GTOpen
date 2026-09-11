"""Read saved learning state after phase A, without touching live sessions."""
from run_experiment import HERE, LAB, idle
from run_phase_a import jobs
import hashlib
import json
from pathlib import Path
import subprocess
import time

PREVIOUS = HERE.parent / '05-preflop-convergence-20260911'
CASES = [('six-native-b', 'six-native-b', 'candidate_self'),
         ('six-reference-tight-a', 'six-native-b', 'reference_self'),
         ('eight-native-a', 'eight-native-a', 'candidate_self'),
         ('eight-s64-a', 'eight-s64-a', 'candidate_self'),
         ('modeled-native-a', 'modeled-native-a', 'candidate_self')]


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def main():
    for name, *_ in jobs:
        record = json.loads((HERE / 'raw' / f'{name}-exit.json').read_text())
        if record.get('returncode') != 0 or record.get('reason'):
            raise RuntimeError('Phase A must finish normally before diagnostics')
    exe = LAB / 'target/release/examples/convergence_diagnostics.exe'
    for name, audit_name, q_key in CASES:
        idle()
        snapshot = LAB / 'target/convergence' / name / 'final.gtop'
        audit = PREVIOUS / 'raw' / f'{audit_name}-local-v3.json'
        output = HERE / 'raw' / f'{name}-learning-diagnostics.json'
        log = output.with_suffix('.log')
        exit_path = HERE / 'raw' / f'{name}-learning-diagnostics-exit.json'
        if any(p.exists() for p in (output, log, exit_path)):
            raise RuntimeError(f'Output already exists for {name}')
        record = dict(name=name, audit_name=audit_name, action_value_source=q_key,
                      input_sha256=digest(snapshot), audit_sha256=digest(audit),
                      exe_sha256=digest(exe))
        started = time.monotonic()
        reason = None
        with log.open('x') as stream:
            process = subprocess.Popen([str(exe), str(snapshot), str(audit), str(output)],
                                       cwd=LAB, stdout=stream, stderr=subprocess.STDOUT,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                while process.poll() is None:
                    time.sleep(1)
                    idle()
                    if time.monotonic() - started > 300:
                        raise RuntimeError('Diagnostic time cap')
            except Exception as error:
                reason = str(error)
                if process.poll() is None:
                    process.kill()
            process.wait(timeout=30)
        record.update(returncode=process.returncode, reason=reason,
                      seconds=time.monotonic() - started)
        if digest(snapshot) != record['input_sha256']:
            record['reason'] = 'Input snapshot changed'
        exit_path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
        print(json.dumps(record), flush=True)
        if record['reason'] or process.returncode:
            raise RuntimeError(record['reason'] or 'Diagnostic failed')


if __name__ == '__main__':
    main()
