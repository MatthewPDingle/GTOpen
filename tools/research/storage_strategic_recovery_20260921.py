"""Reviewed continuation after the equal-1500 pre-launch RAM refusal.

Keep the original queue and all scientific inputs immutable. Wait for the
original admission reserve, then invoke each remaining segment once only.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from storage_phase_run_20260920 import ROOT, OUT, EVIDENCE, read, sha
from storage_strategic_queue_20260920 import check_completed
from storage_strategic_segment_20260920 import label
from loopback_research_validation import idle

PREFIX = 'strategic-segments-v1-recovery-20260921'


def reviewed_prefix(plan, stopped):
    assert stopped['step'] == 'stopped-for-review'
    assert (stopped['branch'], stopped['target']) == ('equal', 1500)
    assert len(stopped['completed']) == 6
    try:
        prior = psutil.Process(stopped['pid'])
        assert prior.create_time() != stopped['created'], 'Original queue is still alive'
    except psutil.NoSuchProcess:
        pass
    for stage, recorded in zip(plan['stages'][:6], stopped['completed']):
        name = label(stage['branch'], stage['target'])
        result, review = OUT/(name+'-result.json'), OUT/(name+'-review.json')
        check_completed(stage, read(OUT/(name+'-status.json')), read(review), read(result),
                        sha(result), read(EVIDENCE/(name+'-status.json')))
        assert recorded == dict(branch=stage['branch'], target=stage['target'],
                                review_sha256=sha(review), result_sha256=sha(result))
    assert [(s['branch'], s['start'], s['target']) for s in plan['stages'][6:]] == [
        ('equal', 1000, 1500), ('equal', 1500, 2000)]
    for stage in plan['stages'][6:]:
        name = label(stage['branch'], stage['target'])
        assert not list(OUT.glob(name+'*')) and not list(EVIDENCE.glob(name+'*'))
        assert not (Path('S:/GTOpen-research/strategic-segments-v1')/name).exists()


def main():
    assert sys.argv[1:] in ([], ['--preflight'])
    status_path = OUT/'strategic-segments-v1-queue-status.json'
    stopped = read(status_path)
    frozen = read(OUT/'strategic-segments-v1-queue-freeze.json')['inputs_sha256']
    frozen = {**frozen, str(Path(__file__).relative_to(ROOT)): sha(Path(__file__)),
              str((OUT/'STRATEGIC-RECOVERY-20260921.md').relative_to(ROOT)):
                  sha(OUT/'STRATEGIC-RECOVERY-20260921.md')}

    def verify():
        for path, digest in frozen.items():
            assert sha(ROOT/path) == digest, path

    verify()
    plan = read(OUT/'strategic-segments-v1-proposed-schedule.json')
    reviewed_prefix(plan, stopped)
    lock = OUT/'strategic-segments-v1-queue.lock'
    for path in [lock, OUT/'running.lock', EVIDENCE/'running.lock']:
        assert not path.exists(), str(path)
    required = read(OUT/'expansion-capacity-112.json')['totals']['ram_payload_total_bytes']+26_000_000_000
    if sys.argv[1:]:
        print(json.dumps(dict(preflight_passed=True, completed_stages=6,
                              available=psutil.virtual_memory().available, required=required)))
        return
    with (OUT/(PREFIX+'-stopped-queue.json')).open('x') as f:
        json.dump(stopped, f, indent=2)
    with (OUT/(PREFIX+'-freeze.json')).open('x') as f:
        json.dump(dict(inputs_sha256=frozen, reviewed_failure='RAM admission before any equal-1500 artifacts or native launch',
                       stopped_queue_sha256=sha(OUT/(PREFIX+'-stopped-queue.json'))), f, indent=2)
    status = dict(step='waiting-for-resource-admission', pid=os.getpid(),
                  created=psutil.Process().create_time(), completed=stopped['completed'], recovery=PREFIX)
    with lock.open('x') as f:
        f.write(str(os.getpid()))

    def report():
        status_path.write_text(json.dumps(status, indent=2))
        (OUT/(PREFIX+'-status.json')).write_text(json.dumps(status, indent=2))
        print(json.dumps(status), flush=True)

    try:
        for stage in plan['stages'][6:]:
            deadline = time.monotonic()+12*3600
            while True:
                verify()
                available = psutil.virtual_memory().available
                production_idle = idle()
                if available >= required and production_idle:
                    break
                status.update(step='waiting-for-resource-admission', branch=stage['branch'], target=stage['target'],
                              available_ram_bytes=available, required_ram_bytes=required, production_idle=production_idle)
                report()
                assert time.monotonic() < deadline, 'Admission unavailable for 12 hours; review required'
                time.sleep(900)
            status.update(step='running-segment', branch=stage['branch'], target=stage['target'])
            report()
            subprocess.run([sys.executable, str(ROOT/'tools/research/storage_strategic_segment_20260920.py'),
                            stage['branch'], str(stage['target'])], cwd=ROOT, check=True)
            verify()
            name = label(stage['branch'], stage['target'])
            result, review = OUT/(name+'-result.json'), OUT/(name+'-review.json')
            check_completed(stage, read(OUT/(name+'-status.json')), read(review), read(result),
                            sha(result), read(EVIDENCE/(name+'-status.json')))
            status['completed'].append(dict(branch=stage['branch'], target=stage['target'],
                                            review_sha256=sha(review), result_sha256=sha(result)))
            report()
        with (OUT/'strategic-final-policies-v1-freeze.json').open('x') as f:
            json.dump(dict(policies=[c for c in status['completed'] if c['target']==2000],
                           registration_sha256=sha(OUT/'strategic-segments-v1-registration.json'),
                           reserved_panel_not_evaluated=True, accuracy_claim=False, production_ready=False), f, indent=2)
        status['step'] = 'complete-training-awaiting-reserved-comparison'
    except Exception as exc:
        status.update(step='stopped-for-review', error=repr(exc))
        raise
    finally:
        report()
        lock.unlink()


if __name__ == '__main__':
    main()
