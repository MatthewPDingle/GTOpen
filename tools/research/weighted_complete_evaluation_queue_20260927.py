"""Wait for the admitted trainer/auditor, then run qualified evaluation stages."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK, OTHER

PREFIX = 'weighted-complete-evaluation-queue-v1'
STAGES = (
    ('weighted_complete_evaluation_control_20260927.py', 'weighted-complete-evaluation-control-v1-result.json', True, 7500),
    ('weighted_complete_control_review_20260927.py', 'weighted-complete-evaluation-control-v1-independent-review.json', False, 2100),
    ('weighted_complete_evaluation_study_v2.py', 'weighted-complete-evaluation-study-v1-result.json', True, 43500),
    ('weighted_complete_study_review_20260927.py', 'weighted-complete-evaluation-study-v1-independent-review.json', False, 7500),
)


def identity(pid, script):
    process = psutil.Process(pid)
    assert process.is_running() and any(script in arg for arg in process.cmdline())
    return dict(pid=pid, created=process.create_time(), command=process.cmdline())


def live(record):
    try:
        process = psutil.Process(record['pid'])
        return process.is_running() and process.create_time() == record['created']
    except psutil.NoSuchProcess:
        return False


def qualify_helpers():
    paths = []
    for prefix, key, script in (
        ('parallel-evaluation-archive-v2-control', 'worker_source_sha256', 'bounded_parallel_evaluation_archive_v2.py'),
        ('weighted-evaluation-readback-control-v1', 'source_sha256', 'weighted_evaluation_readback_v1.py'),
        ('weighted-complete-checkpoint-control-v1', 'helper_sha256', 'weighted_evaluation_checkpoint_v1.py'),
        ('weighted-routed-readback-control-v1', 'helper_sha256', 'weighted_routed_evaluation_readback_v1.py'),
    ):
        rp, pp = [OUT / f'{prefix}-{s}.json' for s in ('registration', 'result')]
        result = read(pp)
        assert result['passed'] and result['registration_sha256'] == sha(rp)
        assert result[key] == sha(ROOT / 'tools/research' / script)
        paths.extend([rp, pp])
    proof_path = OUT / 'weighted-complete-driver-control-v2-integration-proof.json'
    proof = read(proof_path)
    assert proof['passed'] and proof['mechanical_driver_only'] and proof['final_statistics_exactly_equal']
    assert proof['driver_sha256'] == sha(ROOT / 'tools/research/weighted_complete_evaluation_study_v2.py')
    assert proof['runtime_sha256'] == sha(ROOT / 'tools/research/weighted_evaluation_runtime_v2.py')
    paths.append(proof_path)
    return paths


def main(check_only=False):
    paths = qualify_helpers()
    status = read(OUT / 'weighted-stratified-study-v1-status.json')
    trainer = identity(status['pid'], 'weighted_stratified_study_20260927.py')
    processes = []
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        if p.info['name'].lower() in ('python.exe', 'python') and any(
                'weighted_study_audit_queue_20260927.py' in arg for arg in (p.info['cmdline'] or [])):
            processes.append(p.pid)
    assert len(processes) == 1, 'Expected the one admitted audit queue'
    auditor = identity(processes[0], 'weighted_study_audit_queue_20260927.py')
    rp = OUT / f'{PREFIX}-registration.json'
    assert not rp.exists()
    for script, result, _, _ in STAGES:
        assert (ROOT / 'tools/research' / script).is_file() and not (OUT / result).exists()
    if check_only:
        print(json.dumps(dict(ready_to_queue=True, trainer_pid=trainer['pid'], auditor_pid=auditor['pid'], stages=4)), flush=True)
        return
    paths += [OUT / 'weighted-stratified-study-v1-registration.json', OUT / 'weighted-study-audit-queue-v1-registration.json']
    inputs = {str(p): sha(p) for p in [*paths, *Path(__file__).parent.glob('*.py')]}
    save(rp, dict(inputs=inputs, trainer=trainer, auditor=auditor, maximum_seconds=86400,
                  stages=STAGES, policy='Never restart a missing trainer or retry failed stages automatically.',
                  production_modified=False, accuracy_qualified=False))
    started = time.monotonic()
    child = None
    def check_time():
        assert time.monotonic() - started < 86400, 'Queue deadline reached'
    def await_result(path, process):
        while not path.exists():
            check_time()
            assert live(process), 'Expected upstream process ended without its completed result'
            time.sleep(30)
    results = []
    try:
        await_result(OUT / 'weighted-stratified-study-v1-training-result.json', trainer)
        await_result(OUT / 'weighted-study-audit-queue-v1-result.json', auditor)
        audit = read(OUT / 'weighted-study-audit-queue-v1-result.json')
        assert audit['passed'] and len(audit['results']) == 2
        for script, result_name, gpu, limit in STAGES:
            while True:
                check_time()
                ready = production_available() and psutil.virtual_memory().available > 26_000_000_000
                ready = ready and psutil.cpu_percent(interval=1) < 50
                if gpu:
                    ready = ready and not LOCK.exists() and not OTHER.exists()
                    status = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.free',
                        '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=5,
                        creationflags=subprocess.CREATE_NO_WINDOW)
                    if status.returncode == 0:
                        utilization, free = map(float, status.stdout.strip().splitlines()[0].split(','))
                        ready = ready and utilization < 20 and free > 6000
                    else:
                        ready = False
                if ready:
                    break
                time.sleep(30)
            for path, digest in inputs.items():
                assert sha(path) == digest, path
            log_path = OUT / f'{PREFIX}-{Path(script).stem}.log'
            print(json.dumps(dict(starting=script, log=str(log_path))), flush=True)
            began = time.monotonic()
            with log_path.open('x', encoding='utf-8') as log:
                child = subprocess.Popen([sys.executable, str(ROOT / 'tools/research' / script)], cwd=ROOT,
                    stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                while child.poll() is None:
                    check_time()
                    assert time.monotonic() - began < limit, 'Stage timeout; preserve evidence'
                    time.sleep(5)
            assert child.returncode == 0, 'Stage failed; inspect ' + str(log_path)
            child = None
            result_path = OUT / result_name
            assert read(result_path)['passed']
            results.append(dict(script=script, result=str(result_path), sha256=sha(result_path)))
            print(json.dumps(dict(completed=script, seconds=time.monotonic() - began)), flush=True)
        save(OUT / f'{PREFIX}-result.json', dict(passed=True, registration_sha256=sha(rp), stages=results,
             seconds=time.monotonic() - started, interpretation_pending=True, accuracy_qualified=False, production_modified=False))
    except BaseException as error:
        save(OUT / f'{PREFIX}-failure.json', dict(passed=False, registration_sha256=sha(rp), error=repr(error),
             stages_completed=results, seconds=time.monotonic() - started, production_modified=False))
        raise
    finally:
        if child is not None and child.poll() is None:
            # Only the process tree launched by this queue; never upstream work.
            for p in reversed(psutil.Process(child.pid).children(recursive=True)):
                try:
                    p.terminate()
                except psutil.NoSuchProcess:
                    pass
            child.terminate()
            child.wait(timeout=20)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-only', action='store_true')
    main(parser.parse_args().check_only)
