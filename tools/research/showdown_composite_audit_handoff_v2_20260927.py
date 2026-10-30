"""Wait for the identified live continuation, then run its independent audit.

No training restart, result fabrication, sampling, or production mutation.
The auditor retains all its own full-evidence admission and reconstruction gates.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from hu_paired_continuation_support_20260925 import LOCK, OTHER
from reboot_research_idle_v1 import idle

PREFIX = 'showdown-composite-audit-handoff-v2'
CONTINUATION = 'showdown-fourth-arm-continuation-v1'
AUDIT = 'showdown-training-readback-composite-v1-9266301-corrected-0078'
TRAINING_SCRIPT = 'hu_showdown_fourth_arm_continuation_20260927.py'
AUDITOR = ROOT/'tools/research/compact_showdown_training_review_composite_v1.py'


def write_status(path, value):
    temporary = path.with_suffix('.tmp')
    save(temporary, value)
    temporary.replace(path)


def identify(pid, role):
    process = psutil.Process(pid)
    command = process.cmdline()
    assert process.is_running() and role in command
    assert any(Path(arg).name == TRAINING_SCRIPT for arg in command)
    return dict(pid=pid, created=process.create_time(), command=command)


def still_live(identity):
    try:
        process = psutil.Process(identity['pid'])
        return process.is_running() and process.create_time() == identity['created']
    except psutil.NoSuchProcess:
        return False


def main():
    rp, result_path, status_path = [OUT/f'{PREFIX}-{suffix}.json'
                                   for suffix in ('registration', 'result', 'status')]
    assert not any(p.exists() for p in (rp, result_path, status_path))
    assert not (OUT/f'{AUDIT}-registration.json').exists()
    assert not (OUT/f'{AUDIT}-result.json').exists()
    progress = read(OUT/f'{CONTINUATION}-status.json')
    assert progress['state'] == 'running' and idle() and not OTHER.exists()
    worker = identify(progress['worker_pid'], '--worker')
    controller = identify(psutil.Process(worker['pid']).ppid(), '--run')
    assert LOCK.read_text().strip() == str(controller['pid'])
    dependencies = [Path(__file__).resolve(), AUDITOR,
        ROOT/'tools/research/composite_showdown_evidence_v1.py',
        ROOT/'tools/research/reboot_research_idle_v1.py',
        OUT/f'{CONTINUATION}-registration.json']
    inputs = {str(p): sha(p) for p in dependencies}
    registration = dict(inputs=inputs, worker=worker, controller=controller,
        maximum_wait_seconds=7200, maximum_audit_process_seconds=21720,
        audit_prefix=AUDIT, production_modified=False,
        scope='Bounded process handoff only; independent audit checks full original and resumed evidence.')
    save(rp, registration)
    started = time.monotonic(); child = None; error = None; last = 0.
    try:
        while still_live(worker) or still_live(controller):
            assert time.monotonic()-started < registration['maximum_wait_seconds']
            if time.monotonic()-last >= 30:
                assert idle() and not OTHER.exists()
                write_status(status_path, dict(state='waiting-for-training', supervisor_pid=os.getpid(),
                    worker_pid=worker['pid'], seconds=time.monotonic()-started, production_modified=False))
                last = time.monotonic()
            time.sleep(5)
        # Missing processes alone never imply successful completion.
        terminal = read(OUT/f'{CONTINUATION}-status.json')
        result = read(OUT/f'{CONTINUATION}-result.json')
        assert terminal['state'] == 'complete' and terminal['exit_code'] == 0
        assert result['passed'] and result['terminal'] and result['completed_iterations'] == 78
        assert result['final_restore_verified']
        assert result['registration_sha256'] == inputs[str(OUT/f'{CONTINUATION}-registration.json')]
        assert not LOCK.exists() and not OTHER.exists() and idle()
        for path, expected in inputs.items():
            assert sha(path) == expected, path
        assert not (OUT/f'{AUDIT}-registration.json').exists()
        assert not (OUT/f'{AUDIT}-result.json').exists()
        with (OUT/f'{PREFIX}.log').open('x') as log:
            child = subprocess.Popen([sys.executable, str(AUDITOR), '9266301-corrected', '78'],
                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
            began = time.monotonic()
            write_status(status_path, dict(state='auditing', supervisor_pid=os.getpid(), auditor_pid=child.pid,
                training_result_sha256=sha(OUT/f'{CONTINUATION}-result.json'),
                seconds=time.monotonic()-started, production_modified=False))
            while child.poll() is None:
                assert time.monotonic()-began < registration['maximum_audit_process_seconds']
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    pass
        assert child.returncode == 0, 'Audit failed; preserve evidence, no automatic retry'
        audit = read(OUT/f'{AUDIT}-result.json')
        assert audit['passed'] and audit['complete_arm'] and audit['composite_completed_arm']
        assert audit['completed_updates'] == 78 and audit['bb_roots_reconstructed'] == 39936
        assert audit['readback_registration_sha256'] == sha(OUT/f'{AUDIT}-registration.json')
        assert audit['continuation_result_sha256'] == sha(OUT/f'{CONTINUATION}-result.json')
        for path, expected in inputs.items():
            assert sha(path) == expected, path
        save(result_path, dict(passed=True, registration_sha256=sha(rp),
            audit_result_sha256=sha(OUT/f'{AUDIT}-result.json'), seconds=time.monotonic()-started,
            production_modified=False, accuracy_qualified=False))
    except BaseException as exc:
        error = repr(exc)
        save(result_path, dict(passed=False, error=error, registration_sha256=sha(rp),
            seconds=time.monotonic()-started, production_modified=False))
        raise
    finally:
        if child is not None and child.poll() is None:
            # Only the auditor launched by this process; never touch training.
            child.terminate(); child.wait(timeout=20)
        write_status(status_path, dict(state='failed' if error else 'complete', error=error,
            exit_code=child.returncode if child else None, seconds=time.monotonic()-started,
            production_modified=False))


if __name__ == '__main__':
    assert sys.argv[1:] == ['--run']
    main()
