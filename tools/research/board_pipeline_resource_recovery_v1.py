"""Resume only the unstarted GPU control after the recorded offline-port failure.

Preserve the old failure and completed report. The scientific control, its inputs,
and its limits are unchanged. A new recovery record authenticates the corrected
read-only inventory and the genuinely completed remaining stage.
"""
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha
from board_prefix_publication_v1 import atomic_json
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK, OTHER
from global_research_inventory_v2 import measure

NAME = 'board-pipeline-resource-recovery-v1'
ORIGINAL = 'board-training-pipeline-queue-v2'
CONTROL = 'board-training-pipeline-control-v1'


def main():
    began = time.monotonic()
    old_reg = OUT/f'{ORIGINAL}-registration.json'
    old_failure = OUT/f'{ORIGINAL}-failure.json'
    old_result = OUT/f'{ORIGINAL}-result.json'
    rp = OUT/f'{NAME}-registration.json'
    failure = read(old_failure)
    assert not old_result.exists() and not rp.exists()
    assert failure['registration_sha256'] == sha(old_reg) and not failure['passed']
    assert 'ConnectionRefusedError(10061' in failure['error']
    assert [x['script'] for x in failure['completed']] == ['weighted_final_findings_v1.py']
    for row in failure['completed']:
        assert sha(row['result']) == row['sha256']
        for path, digest in read(row['result'])['outputs'].items(): assert sha(path) == digest
    for path, digest in read(old_reg)['inputs'].items(): assert sha(path) == digest, path
    proof = OUT/'global-research-inventory-control-v2-result.json'
    checked = read(proof)
    assert checked['passed'] and checked['activity_rejections'] == 3
    for path, digest in checked['inputs'].items(): assert sha(path) == digest
    for suffix in ('registration', 'result'):
        assert not (OUT/f'{CONTROL}-{suffix}.json').exists(), 'Inspect existing control instead of retrying'
    assert not Path('S:/GTOpen-research', CONTROL).exists()
    assert not LOCK.exists() and not OTHER.exists()
    assert production_available() and psutil.cpu_percent(interval=1) < 30
    assert psutil.virtual_memory().available > 28_000_000_000
    gpu = subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.free','--format=csv,noheader,nounits'],
                         capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
    assert gpu.returncode == 0
    util, free = map(float, gpu.stdout.strip().splitlines()[0].split(','))
    assert util < 20 and free > 6000
    inventory = measure()
    total = sum(row['allocated_file_bytes'] for row in inventory)
    assert total + 8_000_000_000 <= 800_000_000_000
    assert psutil.disk_usage('S:/').free > 50 * 2**30
    paths = [old_reg, old_failure, proof, *Path(__file__).parent.glob('*.py')]
    inputs = {str(p):sha(p) for p in paths}
    atomic_json(rp, dict(inputs=inputs, original_registration_sha256=sha(old_reg),
        original_failure_sha256=sha(old_failure), resume_after_completed_report=True,
        inventory=inventory, allocated_bytes=total, reserved_bytes=8_000_000_000,
        allocation_ceiling_bytes=800_000_000_000, maximum_stage_seconds=1860,
        scientific_script='board_training_pipeline_control_v1.py', production_modified=False,
        scope='Operational queue recovery only; unchanged genuine GPU control, preserved original failure and report.'))
    child = None
    try:
        log = OUT/f'{NAME}.log'
        with log.open('x', encoding='utf-8') as stream:
            child = subprocess.Popen([sys.executable, str(ROOT/'tools/research/board_training_pipeline_control_v1.py')],
                cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
            atomic_json(OUT/f'{NAME}-child.json', dict(pid=child.pid, created=psutil.Process(child.pid).create_time()))
            assert child.wait(timeout=1860) == 0, 'GPU control failed; preserve artifacts and inspect'
        child = None
        result_path = OUT/f'{CONTROL}-result.json'
        control = read(result_path)
        assert control['passed'] and control['registration_sha256'] == sha(OUT/f'{CONTROL}-registration.json')
        assert control['exact_restart_replay'] and control['trained_generations'] == 2
        for path, digest in inputs.items(): assert sha(path) == digest, path
        result = dict(passed=True, registration_sha256=sha(old_reg),
            stages=[*failure['completed'], dict(script='board_training_pipeline_control_v1.py', result=str(result_path), sha256=sha(result_path))],
            recovery_registration=str(rp), recovery_registration_sha256=sha(rp),
            resumed_from_failure=str(old_failure), resumed_from_failure_sha256=sha(old_failure),
            seconds_this_recovery=time.monotonic()-began, production_modified=False)
        atomic_json(old_result, result)
        atomic_json(OUT/f'{NAME}-result.json', dict(passed=True, registration_sha256=sha(rp),
            resumed_result=str(old_result), resumed_result_sha256=sha(old_result), production_modified=False))
        print(json.dumps(dict(passed=True, recovered_result=str(old_result))), flush=True)
    except BaseException as error:
        atomic_json(OUT/f'{NAME}-failure.json', dict(passed=False, registration_sha256=sha(rp), error=repr(error)))
        raise
    finally:
        if child is not None and child.poll() is None:
            owner = psutil.Process(child.pid)
            descendants = owner.children(recursive=True)
            for process in reversed(descendants):
                try: process.terminate()
                except psutil.NoSuchProcess: pass
            child.terminate()
            child.wait(timeout=20)
            psutil.wait_procs(descendants, timeout=20)


if __name__ == '__main__': main()
