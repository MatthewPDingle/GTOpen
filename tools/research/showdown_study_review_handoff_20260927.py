"""Wait for the exact admitted study, then independently review its full result."""
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

PREFIX = 'showdown-study-review-handoff-v1'
STUDY = 'showdown-composite-evaluation-study-v1'
RUNNER = ROOT/'tools/research/hu_showdown_composite_evaluation_v1_20260927.py'
REVIEWER = ROOT/'tools/research/hu_showdown_composite_evaluation_review_v1_20260927.py'


def identify(pid, role):
    p = psutil.Process(pid)
    command = p.cmdline()
    assert p.is_running() and role in command
    assert any(Path(a).name == RUNNER.name for a in command)
    return dict(pid=pid, created=p.create_time(), command=command)


def qualified_study(inputs):
    for path, expected in inputs.items():
        assert sha(path) == expected
    rp = OUT/f'{STUDY}-registration.json'
    reg = read(rp)
    result = read(OUT/f'{STUDY}-result.json')
    status = read(OUT/f'{STUDY}-status.json')
    assert status['state'] == 'complete' and status['exit_code'] == 0
    assert result['passed'] and result['complete'] and result['mode'] == 'study'
    assert result['registration_sha256'] == sha(rp)
    assert result['deals'] == reg['deals'] == 65536 and reg['test_seed'] == 9267201
    assert len(result['archive_manifest_hashes']) == len(result['batch_summary_hashes']) == 2048
    assert not LOCK.exists() and not OTHER.exists() and idle()


def main():
    rp, result_path, status_path = [OUT/f'{PREFIX}-{suffix}.json'
        for suffix in ('registration','result','status')]
    assert not any(p.exists() for p in (rp, result_path, status_path))
    assert not (OUT/f'{STUDY}-result.json').exists()
    assert not (OUT/f'{STUDY}-readback-registration.json').exists()
    admission_path = OUT/f'{STUDY}-admission.json'
    admission = read(admission_path)
    worker = identify(admission['worker_pid'], '--worker')
    controller = identify(admission['controller_pid'], '--study')
    assert psutil.Process(worker['pid']).ppid() == controller['pid']
    assert LOCK.read_text().strip() == str(controller['pid'])
    assert idle() and not OTHER.exists()
    paths = [Path(__file__).resolve(), RUNNER, REVIEWER,
        ROOT/'tools/research/showdown_composite_audit_handoff_v2_20260927.py',
        admission_path, OUT/f'{STUDY}-registration.json',
        OUT/'SHOWDOWN-COMPLETE-EVALUATION-PLAN.md', OUT/'SHOWDOWN-COMPOSITE-EVALUATION-ROUTING.md',
        OUT/'SHOWDOWN-COMPLETED-FIXTURE-STORAGE-AMENDMENT.md',
        OUT/'completed-flop-fixture-compression-v1-independent-review.json']
    inputs = {str(p):sha(p) for p in paths}
    assert admission['registration_sha256'] == inputs[str(OUT/f'{STUDY}-registration.json')]
    save(rp, dict(inputs=inputs, worker=worker, controller=controller,
        maximum_wait_seconds=86520, maximum_review_seconds=21720,
        scope='Review the single fixed 65536-deal study only after verified successful exit.',
        retries_allowed=False, production_modified=False, sampling_allowed=False))
    started = time.monotonic(); child = None; error = None; last = 0.
    try:
        while still_live(worker) or still_live(controller):
            assert time.monotonic()-started < 86520
            if time.monotonic()-last >= 60:
                write_status(status_path, dict(state='waiting-for-study', supervisor_pid=os.getpid(),
                    worker_pid=worker['pid'], seconds=time.monotonic()-started, production_modified=False))
                last = time.monotonic()
            time.sleep(5)
        qualified_study(inputs)
        with (OUT/f'{PREFIX}.log').open('x') as log:
            child = subprocess.Popen([sys.executable,str(REVIEWER),'study'],cwd=ROOT,
                stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            began = time.monotonic()
            write_status(status_path,dict(state='reviewing',supervisor_pid=os.getpid(),
                reviewer_pid=child.pid,seconds=time.monotonic()-started,production_modified=False))
            while child.poll() is None:
                assert time.monotonic()-began < 21720
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    pass
        assert child.returncode == 0, 'Review failed; preserve evidence, no automatic retry'
        review = read(OUT/f'{STUDY}-independent-review.json')
        assert review['passed'] and review['deals'] == 65536
        assert review['source_registration_sha256'] == sha(OUT/f'{STUDY}-registration.json')
        assert review['source_result_sha256'] == sha(OUT/f'{STUDY}-result.json')
        save(result_path,dict(passed=True,registration_sha256=sha(rp),
            study_result_sha256=sha(OUT/f'{STUDY}-result.json'),
            study_review_sha256=sha(OUT/f'{STUDY}-independent-review.json'),
            seconds=time.monotonic()-started,production_modified=False,accuracy_qualified=False))
    except BaseException as exc:
        error = repr(exc)
        save(result_path,dict(passed=False,error=error,registration_sha256=sha(rp),
            seconds=time.monotonic()-started,production_modified=False))
        raise
    finally:
        if child is not None and child.poll() is None:
            child.terminate(); child.wait(timeout=20)
        write_status(status_path,dict(state='failed' if error else 'complete',error=error,
            exit_code=child.returncode if child else None,seconds=time.monotonic()-started,
            production_modified=False))


if __name__ == '__main__':
    assert sys.argv[1:] == ['--run']
    main()
