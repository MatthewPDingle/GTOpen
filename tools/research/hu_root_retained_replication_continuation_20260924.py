"""Watch the admitted root-retained trial, then independently audit it once.

Never restarts training, chooses a checkpoint or deploys a result. This controller stops after the training audit; quality tests are separate.
"""
import os
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from reboot_research_idle_v1 import idle

PREFIX = 'root-retained-replication-continuation-v1'
TRAIN = 'root-retained-replication-v1'
LOCK = ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
STAGES = (('training-audit', 'hu_root_retained_replication_review_20260924.py', (), 7320),)


def verify(inputs):
    for p, h in inputs.items():
        assert sha(p) == h, p


def identity(pid):
    process = psutil.Process(pid)
    return dict(pid=pid, created=process.create_time(), parent=process.ppid(), command=process.cmdline())


def alive(wanted):
    try:
        return identity(wanted['pid']) == wanted
    except psutil.NoSuchProcess:
        return False


def main():
    assert sys.argv[1:] == ['--run']
    rp = OUT/f'{PREFIX}-registration.json'
    assert not rp.exists(), 'Preserve earlier continuation attempts'
    trp, tsp = [OUT/f'{TRAIN}-{s}.json' for s in ('registration', 'status')]
    reg_hash = sha(trp)
    reg, state = read(trp), read(tsp)
    assert state['state'] == 'running' and idle() and not OTHER.exists()
    assert reg['config']['max_iterations'] == 78 and reg['control_only'] is False
    controller, worker = [identity(state[k]) for k in ('controller_pid', 'worker_pid')]
    assert worker['parent'] == controller['pid']
    for item in (controller, worker):
        assert any(Path(arg).name == 'hu_root_retained_replication_20260924.py' for arg in item['command'])
        assert '--control' not in item['command']
    assert '--run' in controller['command'] and '--worker' in worker['command']
    assert LOCK.read_text().strip() == str(controller['pid'])
    assert not (OUT/f'{TRAIN}-readback-registration.json').exists()
    inputs = dict(reg['inputs'])
    files = [Path(__file__).resolve(), trp, OUT/'ROOT-RETAINED-REPLICATION-PLAN.md']
    files += [ROOT/'tools/research'/filename for _, filename, _, _ in STAGES]
    inputs.update({str(p): sha(p) for p in files})
    verify(inputs)
    save(rp, dict(inputs=inputs, watched_controller=controller, watched_worker=worker,
        training_registration_sha256=sha(trp), stages=STAGES,
        training_wait_deadline=controller['created']+reg['maximum_seconds']+120,
        production_modified=False, checkpoint_selection=False, automatic_retry=False,
        scope='Dependent execution only; do not restart or change the live registered trial. Only the training readback is scheduled here; quality evaluation is separate.'))
    started = time.monotonic(); records = []; child = None; error = None
    final_state = 'complete'; current_stage = 'waiting-for-training'
    def status(**extra):
        path = OUT/f'{PREFIX}-status.json'; tmp = path.with_suffix('.tmp')
        save(tmp, dict(state='running', stage=current_stage, controller_pid=os.getpid(),
            watched_training_pid=controller['pid'], seconds=time.monotonic()-started,
            stages=records, production_modified=False, **extra))
        tmp.replace(path)
    status()
    try:
        last_status = time.monotonic()
        while alive(controller):
            assert time.time() < controller['created']+reg['maximum_seconds']+120
            assert sha(trp) == reg_hash, 'Training registration changed'
            if time.monotonic()-last_status >= 30:
                latest = Path(reg['store'])/'latest.json'
                status(completed_training_updates=read(latest)['completed_iterations'] if latest.exists() else 0)
                last_status = time.monotonic()
            time.sleep(5)
        terminal = read(tsp)
        assert terminal['state'] == 'complete' and terminal['error'] is None and terminal['exit_code'] == 0, terminal
        assert not alive(worker) and not LOCK.exists() and not OTHER.exists()
        result = read(OUT/f'{TRAIN}-result.json')
        assert result['passed'] and result['terminal'] and result['completed_iterations'] == 78
        assert result['registration_sha256'] == sha(trp)
        records.append(dict(stage='training', exit_code=0, result_sha256=sha(OUT/f'{TRAIN}-result.json')))
        for label, filename, arguments, cap in STAGES:
            current_stage = label
            verify(inputs)
            assert idle() and not LOCK.exists() and not OTHER.exists()
            before = time.monotonic()
            env = os.environ.copy()
            env.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
            with (OUT/f'{PREFIX}-{label}.log').open('x') as stream:
                child = subprocess.Popen([sys.executable, str(ROOT/'tools/research'/filename), *arguments],
                    cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                status(worker_pid=child.pid)
                while child.poll() is None:
                    assert time.monotonic()-before < cap, f'{label} controller deadline'
                    try:
                        child.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        pass
            records.append(dict(stage=label, exit_code=child.returncode, seconds=time.monotonic()-before))
            assert child.returncode == 0, f'{label} failed; inspect preserved log'
            print(records[-1], flush=True)
        verify(inputs)
        result_path = OUT/f'{TRAIN}-independent-review.json'
        reviewed = read(result_path)
        assert reviewed['passed'] and reviewed['completed_updates'] == 78
        assert reviewed['source_result_sha256'] == sha(OUT/f'{TRAIN}-result.json')
        evidence = dict(training_review_sha256=sha(result_path))
        save(OUT/f'{PREFIX}-result.json', dict(passed=True, state=final_state,
            registration_sha256=sha(rp), stages=records, evidence=evidence,
            seconds=time.monotonic()-started, production_modified=False, accuracy_qualified=False,
            next_step='Interpret all results; this controller does not qualify or deploy a model.'))
    except BaseException as exc:
        error = repr(exc)
        raise
    finally:
        if child is not None and child.poll() is None:
            subprocess.run(['taskkill', '/PID', str(child.pid), '/T', '/F'], capture_output=True,
                timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
            child.wait(timeout=30)
            if LOCK.exists() and LOCK.read_text().strip() == str(child.pid):
                assert not psutil.pid_exists(child.pid)
                LOCK.unlink()
        path = OUT/f'{PREFIX}-status.json'; tmp = path.with_suffix('.tmp')
        save(tmp, dict(state='stopped' if error else final_state, error=error,
            controller_pid=os.getpid(), stage=current_stage, stages=records,
            seconds=time.monotonic()-started, production_modified=False))
        tmp.replace(path)


if __name__ == '__main__':
    main()
