"""Wait on this admitted live trainer, then audit completed arms using idle CPUs."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from reboot_research_idle_v1 import idle

PREFIX = 'weighted-study-audit-queue-v1'


def main():
    source = OUT / 'weighted-stratified-study-v1-registration.json'
    reg = read(source)
    status = read(OUT / 'weighted-stratified-study-v1-status.json')
    process = psutil.Process(status['pid'])
    command = process.cmdline()
    assert process.is_running() and any('weighted_stratified_study_20260927.py' in arg for arg in command)
    identity = dict(pid=process.pid, create_time=process.create_time(), command=command)
    control_path = OUT / 'weighted-training-readback-parallel-v1-w4-9266201-stratified-0002-result.json'
    control = read(control_path)
    assert control['passed'] and control['completed_updates'] == 2 and not control['complete_arm']
    control_reg = OUT / 'weighted-training-readback-parallel-v1-w4-9266201-stratified-0002-registration.json'
    assert control['readback_registration_sha256'] == sha(control_reg)
    assert control['source_registration_sha256'] == sha(source)
    script = ROOT / 'tools/research/weighted_training_readback_parallel_v1.py'
    paths = [source, script, Path(__file__), control_path, control_reg, *Path(__file__).parent.glob('*.py')]
    inputs = {str(p): sha(p) for p in paths}
    registration = OUT / f'{PREFIX}-registration.json'
    save(registration, dict(inputs=inputs, trainer=identity, maximum_seconds=43200,
                           workers=4, arms=[a['name'] for a in reg['arms']],
                           policy='Audit completed endpoints only; never restart a missing trainer',
                           production_modified=False))
    started = time.monotonic()
    results = []
    for arm in reg['arms']:
        progress = Path(reg['store']) / arm['name'] / 'progress.json'
        while True:
            assert time.monotonic() - started < 43200, 'Queue time budget reached'
            complete = progress.exists() and read(progress)['completed'] == reg['generations']
            if complete:
                break
            if not process.is_running() or process.create_time() != identity['create_time']:
                raise RuntimeError('Original trainer is no longer live; incomplete arm was not audited')
            time.sleep(30)
        # Recheck competing work instead of blindly filling every CPU core.
        while True:
            assert time.monotonic() - started < 43200
            listening = any(c.status == psutil.CONN_LISTEN and c.laddr.port == 56708
                            for c in psutil.net_connections(kind='tcp'))
            if ((not listening or idle()) and psutil.virtual_memory().available > 24_000_000_000
                    and psutil.cpu_percent(interval=1) < 60):
                break
            time.sleep(30)
        for path, digest in inputs.items():
            assert sha(path) == digest, path
        output = OUT / f"{PREFIX}-{arm['name']}.log"
        with output.open('x', encoding='utf-8') as log:
            done = subprocess.run([sys.executable, str(script), '--arm', arm['name'], '--generations', '78',
                                   '--workers', '4', '--publish'], stdout=log, stderr=subprocess.STDOUT,
                                  cwd=ROOT, timeout=43200 - (time.monotonic() - started),
                                  creationflags=subprocess.CREATE_NO_WINDOW)
        if done.returncode:
            raise RuntimeError(f"Independent audit failed for {arm['name']}; see {output}")
        result_path = OUT / f"weighted-training-readback-parallel-v1-w4-{arm['name']}-0078-result.json"
        result = read(result_path)
        assert result['passed'] and result['complete_arm'] and result['completed_updates'] == 78
        assert result['source_registration_sha256'] == sha(source)
        results.append(dict(arm=arm['name'], result=str(result_path), sha256=sha(result_path)))
        print(json.dumps(results[-1]), flush=True)
    save(OUT / f'{PREFIX}-result.json', dict(passed=True, registration_sha256=sha(registration),
         results=results, seconds=time.monotonic() - started, accuracy_qualified=False, production_modified=False))


if __name__ == '__main__':
    main()
