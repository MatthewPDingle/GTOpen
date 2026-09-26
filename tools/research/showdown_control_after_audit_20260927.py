"""Bounded local audit -> complete-bank control -> scalar review handoff.

Never draws the fresh study stream, changes training, retries failure, or edits
production. Each child retains its own scientific/resource admission gates.
"""
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
from showdown_composite_audit_handoff_v2_20260927 import write_status, still_live

PREFIX = 'showdown-control-after-audit-v1'
HANDOFF = 'showdown-composite-audit-handoff-v2'
AUDIT = 'showdown-training-readback-composite-v1-9266301-corrected-0078'
CONTROL = 'showdown-composite-evaluation-control-v1'
RUNNER = ROOT/'tools/research/hu_showdown_composite_evaluation_v1_20260927.py'
REVIEWER = ROOT/'tools/research/hu_showdown_composite_evaluation_review_v1_20260927.py'


def identify(pid, script_name):
    process = psutil.Process(pid)
    command = process.cmdline()
    assert process.is_running() and any(Path(a).name == script_name for a in command)
    return dict(pid=pid, created=process.create_time(), command=command)


def qualified_audit(inputs):
    status = read(OUT/f'{HANDOFF}-status.json')
    assert status['state'] == 'complete' and status['exit_code'] == 0
    handoff, audit = [read(OUT/f'{p}-result.json') for p in (HANDOFF, AUDIT)]
    assert handoff['passed'] and handoff['registration_sha256'] == inputs[str(OUT/f'{HANDOFF}-registration.json')]
    assert handoff['audit_result_sha256'] == sha(OUT/f'{AUDIT}-result.json')
    assert audit['passed'] and audit['complete_arm'] and audit['composite_completed_arm']
    assert audit['completed_updates'] == 78 and audit['bb_roots_reconstructed'] == 39936
    assert audit['readback_registration_sha256'] == inputs[str(OUT/f'{AUDIT}-registration.json')]
    assert audit['continuation_result_sha256'] == sha(OUT/'showdown-fourth-arm-continuation-v1-result.json')
    assert not LOCK.exists() and not OTHER.exists() and idle()
    for path, expected in inputs.items():
        assert sha(path) == expected, path


def main():
    rp, pp, sp = [OUT/f'{PREFIX}-{s}.json' for s in ('registration', 'result', 'status')]
    assert not any(p.exists() for p in (rp, pp, sp))
    assert not (OUT/f'{CONTROL}-registration.json').exists()
    assert not (OUT/f'{CONTROL}-result.json').exists()
    live = read(OUT/f'{HANDOFF}-status.json')
    assert live['state'] == 'auditing' and idle() and not LOCK.exists() and not OTHER.exists()
    auditor = identify(live['auditor_pid'], 'compact_showdown_training_review_composite_v1.py')
    supervisor = identify(live['supervisor_pid'], 'showdown_composite_audit_handoff_v2_20260927.py')
    assert psutil.Process(auditor['pid']).ppid() == supervisor['pid']
    paths = [Path(__file__).resolve(), RUNNER, REVIEWER,
        ROOT/'tools/research/composite_showdown_bank_v1.py',
        ROOT/'tools/research/showdown_composite_audit_handoff_v2_20260927.py',
        OUT/f'{HANDOFF}-registration.json', OUT/f'{AUDIT}-registration.json',
        OUT/'SHOWDOWN-COMPLETE-EVALUATION-PLAN.md', OUT/'SHOWDOWN-COMPOSITE-EVALUATION-ROUTING.md']
    inputs = {str(p): sha(p) for p in paths}
    registration = dict(inputs=inputs, auditor=auditor, audit_supervisor=supervisor,
        maximum_wait_seconds=21720, maximum_control_seconds=15000, maximum_review_seconds=21720,
        production_modified=False, fresh_study_allowed=False,
        scope='Only the fixed 64 reused-deal complete-bank control and its independent review.')
    save(rp, registration)
    started = time.monotonic(); child = None; error = None; last = 0.
    try:
        while still_live(auditor) or still_live(supervisor):
            assert time.monotonic()-started < registration['maximum_wait_seconds']
            if time.monotonic()-last >= 30:
                assert idle() and not OTHER.exists()
                write_status(sp, dict(state='waiting-for-audit', supervisor_pid=os.getpid(),
                    auditor_pid=auditor['pid'], seconds=time.monotonic()-started, production_modified=False))
                last = time.monotonic()
            time.sleep(5)
        qualified_audit(inputs)
        assert not (OUT/f'{CONTROL}-registration.json').exists()
        for stage, script, argument, limit in (
            ('control', RUNNER, '--control', registration['maximum_control_seconds']),
            ('review', REVIEWER, 'control', registration['maximum_review_seconds']),
        ):
            for path, expected in inputs.items():
                assert sha(path) == expected, path
            assert idle() and not LOCK.exists() and not OTHER.exists()
            with (OUT/f'{PREFIX}-{stage}.log').open('x') as log:
                child = subprocess.Popen([sys.executable, str(script), argument], cwd=ROOT,
                    stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                began = time.monotonic()
                write_status(sp, dict(state=stage, supervisor_pid=os.getpid(), child_pid=child.pid,
                    seconds=time.monotonic()-started, production_modified=False))
                while child.poll() is None:
                    assert time.monotonic()-began < limit
                    try:
                        child.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        pass
            assert child.returncode == 0, 'Child failed; preserve attempt, no automatic retry'
            result = read(OUT/f'{CONTROL}-result.json')
            assert result['passed'] and result['complete'] and result['mode'] == 'control' and result['deals'] == 64
            assert result['registration_sha256'] == sha(OUT/f'{CONTROL}-registration.json')
            if stage == 'control':
                status = read(OUT/f'{CONTROL}-status.json')
                assert status['state'] == 'complete' and status['exit_code'] == 0
            else:
                review = read(OUT/f'{CONTROL}-independent-review.json')
                assert review['passed'] and review['deals'] == 64
                assert review['source_result_sha256'] == sha(OUT/f'{CONTROL}-result.json')
                assert review['source_registration_sha256'] == sha(OUT/f'{CONTROL}-registration.json')
        save(pp, dict(passed=True, registration_sha256=sha(rp),
            control_result_sha256=sha(OUT/f'{CONTROL}-result.json'),
            control_review_sha256=sha(OUT/f'{CONTROL}-independent-review.json'),
            seconds=time.monotonic()-started, production_modified=False, fresh_deals_sampled=0,
            accuracy_qualified=False))
    except BaseException as exc:
        error = repr(exc)
        save(pp, dict(passed=False, error=error, registration_sha256=sha(rp),
            seconds=time.monotonic()-started, production_modified=False))
        raise
    finally:
        if child is not None and child.poll() is None:
            descendants = psutil.Process(child.pid).children(recursive=True)
            child.terminate()
            for process in descendants:
                try:
                    process.terminate()
                except psutil.NoSuchProcess:
                    pass
            child.wait(timeout=20)
        write_status(sp, dict(state='failed' if error else 'complete', error=error,
            exit_code=child.returncode if child else None, seconds=time.monotonic()-started,
            production_modified=False))


if __name__ == '__main__':
    assert sys.argv[1:] == ['--run']
    main()
