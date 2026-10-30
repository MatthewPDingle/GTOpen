"""Continue the registered stages after the already-running first segment.

No retries, altered endpoints, reserved evaluation, or production mutations.
The segment runner owns resource checks, its GPU child and its deadline.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import psutil
from storage_phase_run_20260920 import ROOT, OUT, EVIDENCE, read, sha
from storage_strategic_segment_20260920 import label


def check_completed(stage, status, review, result, result_digest, guard):
    assert status['step'] == 'complete-segment-reviewed'
    assert (status['branch'], status['start'], status['target']) == (stage['branch'], stage['start'], stage['target'])
    assert review['segment_passed'] is True
    assert (review['branch'], review['start'], review['target']) == (stage['branch'], stage['start'], stage['target'])
    assert review['result_sha256'] == result_digest
    assert guard['exit_code'] == 0 and guard['error'] is None
    assert result['resumed_iteration'] == stage['start']
    assert [r['iteration'] for r in result['records']] == stage['evaluation_iterations']
    assert review['final_within_panel_gap'] == result['records'][-1]['evaluation']['gap_total']
    assert review['restored_scientific_boundary_exact'] is (stage['start'] > 0)
    expected = ('underconverged' if review['final_within_panel_gap'] > .01 else 'within-panel-threshold') if stage['target'] == 2000 else 'intermediate'
    assert review['endpoint_status'] == expected
    assert review['accuracy_claim'] is False and review['production_ready'] is False


def preflight():
    registration_path = OUT/'strategic-segments-v1-registration.json'
    registration = read(registration_path)
    schedule_path = OUT/'strategic-segments-v1-proposed-schedule.json'
    assert registration['reviewed_for_launch'] is True and sha(schedule_path) == registration['schedule_sha256']
    plan = read(schedule_path)
    expected = [(b, s, t) for b, first in [('weighted', 20), ('equal', 0)]
                for s, t in zip([first, 500, 1000, 1500], [500, 1000, 1500, 2000])]
    assert [(s['branch'], s['start'], s['target']) for s in plan['stages']] == expected
    files = [Path(__file__), OUT/'STRATEGIC-QUEUE-PROTOCOL.md', registration_path, schedule_path]
    frozen = {**plan['inputs_sha256'], **registration['inputs_sha256'],
              **{str(p.relative_to(ROOT)): sha(p) for p in files}}
    for path, digest in frozen.items():
        assert sha(ROOT/path) == digest, path
    first = plan['stages'][0]
    live = read(OUT/(label(first['branch'], first['target'])+'-status.json'))
    assert live['step'] == 'running'
    parent = psutil.Process(live['pid'])
    assert parent.create_time() == live['created']
    args = parent.cmdline()
    assert any('storage_strategic_segment_20260920.py' in a for a in args)
    assert args[-2:] == ['weighted', '500']
    assert not (OUT/'strategic-segments-v1-queue.lock').exists()
    return plan, frozen, parent


def main():
    plan, frozen, parent = preflight()
    if sys.argv[1:] == ['--preflight']:
        print(json.dumps(dict(preflight_passed=True, active_segment_pid=parent.pid, active_segment_created=parent.create_time(), remaining_segments=7)))
        return
    assert not sys.argv[1:]
    path = OUT/'strategic-segments-v1-queue-status.json'
    status = dict(step='waiting-for-active-segment', pid=os.getpid(), created=psutil.Process().create_time(),
                  parent_pid=parent.pid, parent_created=parent.create_time())
    with (OUT/'strategic-segments-v1-queue-freeze.json').open('x') as f:
        json.dump(dict(inputs_sha256=frozen, active_segment=status), f, indent=2)
    with path.open('x') as f:
        json.dump(status, f, indent=2)
    lock = OUT/'strategic-segments-v1-queue.lock'
    with lock.open('x') as f:
        f.write(str(os.getpid()))

    def report():
        path.write_text(json.dumps(status, indent=2))
        print(json.dumps(status), flush=True)

    def verify():
        for p, digest in frozen.items():
            assert sha(ROOT/p) == digest, p

    try:
        report()
        # A timeout here means the same process is still running, never failure
        # or permission to restart it. Its existing guard owns the deadline.
        while True:
            try:
                parent.wait(timeout=30)
                break
            except psutil.TimeoutExpired:
                pass
        completed = []
        for ordinal, stage in enumerate(plan['stages']):
            verify()
            name = label(stage['branch'], stage['target'])
            if ordinal:
                status.update(step='running-segment', branch=stage['branch'], target=stage['target'])
                report()
                subprocess.run([sys.executable, str(ROOT/'tools/research/storage_strategic_segment_20260920.py'),
                                stage['branch'], str(stage['target'])], cwd=ROOT, check=True)
            verify()
            result_path = OUT/(name+'-result.json')
            review_path = OUT/(name+'-review.json')
            check_completed(stage, read(OUT/(name+'-status.json')), read(review_path), read(result_path),
                            sha(result_path), read(EVIDENCE/(name+'-status.json')))
            completed.append(dict(branch=stage['branch'], target=stage['target'],
                                  review_sha256=sha(review_path), result_sha256=sha(result_path)))
            status['completed'] = completed
            report()
        with (OUT/'strategic-final-policies-v1-freeze.json').open('x') as f:
            json.dump(dict(policies=[c for c in completed if c['target'] == 2000],
                           registration_sha256=sha(OUT/'strategic-segments-v1-registration.json'),
                           reserved_panel_not_evaluated=True, accuracy_claim=False, production_ready=False), f, indent=2)
        status['step'] = 'complete-training-awaiting-reserved-comparison'
    except Exception as ex:
        status.update(step='stopped-for-review', error=repr(ex))
        raise
    finally:
        report()
        lock.unlink()


if __name__ == '__main__':
    main()
