"""One explicit checkpoint recovery plus the already-prepared readback/report.

The frozen scientific driver and resource wrapper are unchanged. Only mutable
progress publication gains bounded sharing-conflict retries. No intermediate
payoff is printed, no new sample is chosen, and no stage retries automatically.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import argparse
from pathlib import Path
import subprocess
import sys
import time
import json
import psutil
from board_full_followup_queue_v1 import (ROOT, OUT, LOCKS, EVALUATION,
    read, sha, require, live, available, stop_owned, validate, bound_result)
from board_prefix_publication_v1 import atomic_json
from windows_progress_publication_v1 import publish_progress, status_only

NAME = 'board-status-recovery-v1'
ATTEMPT = 'status-recovery1'
WRAPPER = 'board-evaluation-resource-wrapper-v1-' + ATTEMPT
PRIOR = [dict(pid=52928, created=1790522310.8170736),
         dict(pid=69396, created=1790544462.3017652)]
SCRIPT = Path(__file__).resolve()


def proof():
    path = OUT / 'windows-progress-publication-control-v1-result.json'
    value = read(path)
    require(value['passed'] and all(value[k] for k in (
        'real_sharing_collision_recovered', 'persistent_denial_bounded',
        'unrelated_error_propagated', 'scope_restored_on_success_and_failure',
        'non_status_path_rejected', 'delete_sharing_reader_retry_qualified')),
        'Passed operational publication control required')
    for p, digest in value['inputs'].items():
        require(sha(p) == digest, 'Changed publication qualification source: ' + p)
    return path


def preflight():
    require(not any(live(p) for p in PRIOR), 'Previous evaluation/queue still running')
    require(not any(p.exists() for p in LOCKS), 'Research work already active')
    require(not (OUT / f'{EVALUATION}-result.json').exists(), 'Preserve completed evaluation')
    require(not (OUT / f'{NAME}-registration.json').exists(), 'Preserve this recovery attempt')
    for stage in ('training', 'training-audit', 'bank-control', 'control-audit'):
        validate(stage)
    old_failure = OUT / 'board-evaluation-resource-wrapper-v1-initial-failure.json'
    failure = read(old_failure)
    require(failure['error'] == "PermissionError(13, 'Access is denied')" and
        failure['registration_sha256'] == sha(OUT / 'board-evaluation-resource-wrapper-v1-initial-registration.json'),
        'Inspect any different failure before recovery')
    log = OUT / 'board-full-followup-queue-v1-evaluation.log'
    evidence = log.read_text(encoding='utf-8')
    require('in write_status' in evidence and 'os.replace(temporary, path)' in evidence and
        '[WinError 5]' in evidence, 'Expected status publication failure evidence missing')
    import board_complete_evaluation_study_v1 as driver
    from weighted_evaluation_checkpoint_v1 import restore_latest
    require(sha(driver.REG) == '127088852b6bd3bd4c900b076872b449385c5c693803eb3e276f239b513a4497',
        'Fixed scientific registration changed')
    for path, digest in read(driver.REG)['inputs'].items():
        require(sha(path) == digest, 'Changed scientific input: ' + path)
    began = time.monotonic()
    def guard():
        require(time.monotonic() - began < 300, 'Checkpoint validation timed out')
    sampler, _, routes, checkpoint = restore_latest(driver.STORE,
        registration_sha256=sha(driver.REG), bank_identities_sha256=sha(driver.STORE / 'bank-identities.json'),
        context_source=driver.CONTEXT.read_text(), total_deals=65536, seed=9281101, guard=guard)
    require(sampler.draws == 17408 and len(routes) == 544 and checkpoint['sha256'] ==
        'b25c2ff8e157d025b7731ba8253efbea7d48f5b5f00fad34f18424ec9ee9a95c',
        'Recovery checkpoint differs from inspected committed prefix')
    paths = [proof(), old_failure, log, driver.REG, driver.STORE / checkpoint['file'],
        OUT / 'board-full-followup-queue-v1-failure.json',
        *SCRIPT.parent.glob('*.py')]
    for suffix in ('readback-registration', 'independent-review'):
        require(not (OUT / f'{EVALUATION}-{suffix}.json').exists(), 'Preserve existing readback attempt')
    require(not (OUT / 'board-final-report-evidence.json').exists(), 'Preserve report')
    require(not (OUT / f'{WRAPPER}-registration.json').exists(), 'Preserve resource wrapper attempt')
    return checkpoint, paths


def recovered_evaluation():
    reg = read(OUT / f'{NAME}-registration.json')
    proof()
    for path, digest in reg['inputs'].items():
        require(sha(path) == digest, 'Changed recovery input: ' + path)
    import board_complete_evaluation_study_v1 as driver
    from board_evaluation_resource_wrapper_v1 import main as wrapped
    original = driver.write_status
    with status_only(driver):
        wrapped('evaluation', run=True, resume=True, attempt=ATTEMPT)
    require(driver.write_status is original, 'Status dependency not restored')


def main(run=False):
    checkpoint, paths = preflight()
    if not run:
        print(json.dumps(dict(ready=True, checkpoint=checkpoint, archived_batches_verified=544,
            registered_chance_prefix_verified=True, fresh_test_deals_drawn=0)), flush=True)
        return
    stages = [('evaluation', SCRIPT, ['--resume-evaluation'], True, 43800),
        ('evaluation-audit', ROOT / 'tools/research/board_complete_study_readback_v1.py', ['--run'], False, 7800),
        ('report', ROOT / 'tools/research/board_final_findings_v1.py', ['--run'], False, 600)]
    inputs = {str(p): sha(p) for p in paths}
    rp = OUT / f'{NAME}-registration.json'
    atomic_json(rp, dict(inputs=inputs, checkpoint=checkpoint, archived_batches_verified=544,
        registered_chance_prefix_verified=True, prior_processes=PRIOR, attempt=ATTEMPT,
        scope='Only mutable status publication adds bounded retries for Windows errors 5, 32, 33. '
              'Frozen numerical driver and resource wrapper remain mandatory and unchanged.',
        stages=[s[0] for s in stages], total_deals=65536, test_seed=9281101,
        maximum_seconds=86400, prior_attempts_preserved=True, partial_payoffs_inspected=False,
        production_modified=False, accuracy_qualified=False))
    began = time.monotonic(); completed = []; child = identity = None
    def deadline():
        require(time.monotonic() - began < 86400, 'Recovery follow-up deadline')
    def status(state, **fields):
        value = dict(state=state, pid=os.getpid(), seconds=time.monotonic()-began, **fields)
        publish_progress(OUT / f'{NAME}-status.json', value)
        print(json.dumps(value), flush=True)
    def sources():
        for p, digest in inputs.items():
            require(sha(p) == digest, 'Recovery source changed: ' + p)
    try:
        for name, script, args, gpu, limit in stages:
            status('waiting for available resources', stage=name)
            while not available(gpu):
                deadline(); time.sleep(30)
            deadline(); sources()
            start = time.monotonic()
            log = OUT / f'{NAME}-{name}.log'
            with log.open('x', encoding='utf-8') as stream:
                child = subprocess.Popen([sys.executable, str(script), *args], cwd=ROOT,
                    stdout=stream, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                identity = dict(pid=child.pid, created=psutil.Process(child.pid).create_time())
                status('running stage', stage=name, child=identity, log=str(log))
                while child.poll() is None:
                    deadline(); require(time.monotonic()-start < limit, 'Stage deadline: ' + name)
                    time.sleep(5)
            require(child.returncode == 0, 'Stage failed; inspect ' + str(log))
            child = identity = None
            if name == 'evaluation':
                result, wrapper = bound_result(EVALUATION), bound_result(WRAPPER)
                require(result['complete'] and result['deals'] == 65536 and result['test_seed'] == 9281101
                    and wrapper['dependency_restored'] and wrapper['scientific_output_sha256'] ==
                    sha(OUT / f'{EVALUATION}-result.json'), 'Incomplete recovered evaluation')
            else:
                validate(name)
            completed.append(dict(stage=name, seconds=time.monotonic()-start))
            status('stage complete', stage=name)
        sources()
        atomic_json(OUT / f'{NAME}-result.json', dict(passed=True, registration_sha256=sha(rp),
            stages=completed, seconds=time.monotonic()-began, interpretation_pending=True,
            visual_review_pending=True, accuracy_qualified=False, production_modified=False))
        status('comparison ready for interpretation')
    except BaseException as error:
        atomic_json(OUT / f'{NAME}-failure.json', dict(passed=False, registration_sha256=sha(rp),
            error=repr(error), stages_completed=completed, seconds=time.monotonic()-began))
        raise
    finally:
        stop_owned(child, identity)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--run', action='store_true')
    modes.add_argument('--resume-evaluation', action='store_true')
    args = parser.parse_args()
    if args.resume_evaluation:
        recovered_evaluation()
    else:
        main(args.run)
