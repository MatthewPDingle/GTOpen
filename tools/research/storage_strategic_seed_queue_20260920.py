"""Launch the registered weighted seed only after the live checkpoint suite succeeds."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from storage_phase_run_20260920 import ROOT, OUT, read, sha
from storage_weighted_input_preflight_20260920 import expected_manifest


def main():
    prior = read(OUT/'checkpoint-pipeline-v1-status.json')
    parent = psutil.Process(prior['pid'])
    assert parent.create_time() == prior['created']
    assert prior['step'] == 'storage_checkpoint_long_20260920.py'
    assert any('storage_checkpoint_queue_20260920.py' in a for a in parent.cmdline())
    expected_manifest()
    files = [Path(__file__), ROOT/'tools/research/storage_strategic_seed_20260920.py',
             ROOT/'tools/research/storage_weighted_input_preflight_20260920.py',
             OUT/'STRATEGIC-SEED-PROTOCOL.md', OUT/'STRATEGIC-COMPARISON-PLAN.md',
             OUT/'weighted-input-readback-v1.json', OUT/'weighted-input-readback-v1-review.json',
             OUT/'expansion-train-112-chance-weight-v1.json']
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in files}
    with (OUT/'strategic-seed-pipeline-v1-freeze.json').open('x') as f:
        json.dump(dict(inputs=hashes), f, indent=2)
    status = dict(step='waiting-for-checkpoint-qualification', pid=os.getpid(),
                  created=psutil.Process().create_time(), parent_pid=parent.pid,
                  parent_created=parent.create_time())
    path = OUT/'strategic-seed-pipeline-v1-status.json'
    with path.open('x') as f:
        json.dump(status, f, indent=2)

    def report():
        path.write_text(json.dumps(status, indent=2))
        print(json.dumps(status), flush=True)

    started = time.monotonic()
    try:
        while True:
            try:
                parent.wait(timeout=30)
                break
            except psutil.TimeoutExpired:
                assert time.monotonic()-started < 6000, 'Observation deadline; inspect the same job without restarting'
        assert read(OUT/'checkpoint-pipeline-v1-status.json')['step'] == 'complete-checkpoint-resume-qualified'
        assert read(OUT/'checkpoint-long-v1-review.json')['passed']
        for p, digest in hashes.items():
            assert sha(ROOT/p) == digest, p
        status['step'] = 'storage_strategic_seed_20260920.py'
        report()
        subprocess.run([sys.executable, str(ROOT/'tools/research/storage_strategic_seed_20260920.py')],
                       cwd=ROOT, check=True)
        assert read(OUT/'strategic-weighted112-seed-v1-review.json')['seed_and_fresh_restore_passed']
        status['step'] = 'complete-seed-and-restore-qualified'
    except Exception as e:
        status.update(step='stopped-for-review', error=repr(e))
        raise
    finally:
        report()


if __name__ == '__main__':
    main()
