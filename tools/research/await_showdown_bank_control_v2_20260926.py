"""One bounded CPU control after a selected registered arm and audit complete."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import time
import sys
import psutil
from compact_showdown_full_bank_control_20260926 import main as control, readiness
from sampled_physical_root_evaluation_v1 import sha, save
from later_average_support_v1 import OUT, read
from reboot_research_idle_v1 import idle

assert len(sys.argv) == 2
LABEL = sys.argv[1]
assert LABEL in ('9266201-baseline', '9266201-corrected', '9266301-baseline', '9266301-corrected')
PREFIX = 'compact-showdown-full-bank-'+LABEL+'-v1'
JOURNAL = OUT/f'await-showdown-bank-control-v2-{LABEL}.json'


def main():
    assert not JOURNAL.exists() and not (OUT/f'{PREFIX}-registration.json').exists()
    start = time.monotonic(); handles = []
    for proc in psutil.process_iter(['pid', 'cmdline', 'create_time']):
        args = proc.info['cmdline'] or []
        names = {Path(arg).name for arg in args}
        training = 'hu_showdown_matched_training_20260926.py' in names and '--worker' in args
        audit = 'compact_showdown_training_review_v2.py' in names and LABEL in args
        if training or audit:
            handles.append(proc)
    assert handles, 'A verified live producer or auditor is required'
    binding = dict(controller_pid=os.getpid(), source_sha256=sha(Path(__file__).resolve()),
        observed_processes=[dict(pid=p.pid, created=p.create_time()) for p in handles],
        target_arm=LABEL, maximum_wait_seconds=5400, gpu_used=False,
        scope='Wait for the full completed arm and audit, then invoke the existing CPU bank control once. No training or evaluation sampling.')
    def status(state, **extra):
        tmp = JOURNAL.with_suffix('.tmp')
        save(tmp, dict(binding, state=state, seconds=time.monotonic()-start, **extra)); tmp.replace(JOURNAL)
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    status('waiting'); print(json.dumps(dict(state='waiting', controller_pid=os.getpid(), arm=LABEL)), flush=True)
    try:
        while not readiness(LABEL)['ready'] or not idle():
            assert time.monotonic()-start < 5400, 'Wait deadline; no automatic retry'
            assert any(p.is_running() for p in handles), 'Producer/auditor exited before readiness'
            time.sleep(15)
        status('checking')
        control(LABEL)
        result = OUT/f'{PREFIX}-result.json'
        assert read(result)['passed']
        status('complete', result_sha256=sha(result))
    except BaseException as exc:
        status('failed', error=repr(exc)); raise


if __name__ == '__main__':
    main()
