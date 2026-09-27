"""One bounded follow-up for the already-running matched board-root study.

Runs the prepared audits, full-bank control, fixed evaluation and report in
order. No scientific settings change, retries, upstream termination, deployment,
or GitHub writes. Defaults to read-only readiness.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil
from board_prefix_publication_v1 import atomic_json
from bounded_parallel_evaluation_archive_v2 import production_available

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'board-full-followup-queue-v1'
UPSTREAM = 'board-full-training-resource-wrapper-v1-initial'
TRAINING = 'board-root-matched-continuation-v1'
AUDIT = 'board-matched-complete-readback-v1'
CONTROL = 'board-complete-evaluation-control-v1'
EVALUATION = 'weighted-complete-board-root-study-v1'
LOCKS = [ROOT/'research/preflop-evolution'/p/'running.lock' for p in
         ('representative-coverage-20260919','symmetric-bridge-20260919')]
STAGES = (
    ('training-audit','board_matched_complete_readback_v2.py',['--workers','8'],False,43800,
     [f'{AUDIT}-registration.json',f'{AUDIT}-result.json']),
    ('bank-control','board_evaluation_resource_wrapper_v1.py',['--stage','control','--run'],True,7800,
     [f'{CONTROL}-registration.json',f'{CONTROL}-result.json',
      'board-control-resource-wrapper-v1-initial-registration.json','board-control-resource-wrapper-v1-initial-result.json']),
    ('control-audit','board_complete_control_readback_v1.py',['--run'],False,2400,
     [f'{CONTROL}-readback-registration.json',f'{CONTROL}-independent-review.json']),
    ('evaluation','board_evaluation_resource_wrapper_v1.py',['--stage','evaluation','--run'],True,43800,
     [f'{EVALUATION}-registration.json',f'{EVALUATION}-result.json',
      'board-evaluation-resource-wrapper-v1-initial-registration.json','board-evaluation-resource-wrapper-v1-initial-result.json']),
    ('evaluation-audit','board_complete_study_readback_v1.py',['--run'],False,7800,
     [f'{EVALUATION}-readback-registration.json',f'{EVALUATION}-independent-review.json']),
    ('report','board_final_findings_v1.py',['--run'],False,600,
     ['BOARD-FINAL-FINDINGS.md','board-final-all-hand-classes.json','board-final-costs.json',
      'board-final-gains.png','board-final-report-evidence.json']),
)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise RuntimeError(message)


def live(identity):
    try:
        p = psutil.Process(identity['pid'])
        return p.is_running() and p.create_time() == identity['created']
    except psutil.NoSuchProcess:
        return False


def dependency_ready(*, alive, success_exists, failure_exists):
    require(not failure_exists, 'Training wrapper reported failure; inspect its retained evidence')
    require(alive or success_exists, 'Original training process ended without a completed result')
    return success_exists and not alive


def bound_result(prefix):
    rp,pp = OUT/f'{prefix}-registration.json',OUT/f'{prefix}-result.json'
    value = read(pp)
    require(value['passed'] and value['registration_sha256'] == sha(rp), 'Unverified result: '+prefix)
    return value


def validate(stage):
    if stage == 'training':
        wrapper, result = bound_result(UPSTREAM),bound_result(TRAINING)
        require(wrapper['dependency_restored'] and wrapper['scientific_output_sha256'] == sha(OUT/f'{TRAINING}-result.json'),
                'Training wrapper does not bind the completed study')
        require(result['training_complete'] and result['generations_per_arm'] == 78 and
                [a['arm'] for a in result['arms']] == ['9266201-board-root','9266301-board-root'] and
                all(a['completed'] == 78 for a in result['arms']), 'Both complete fixed training arms are required')
    elif stage == 'training-audit':
        value = bound_result(AUDIT)
        require(value['complete_training'] and value['reader_version'] == 2 and
                value['source_result_sha256'] == sha(OUT/f'{TRAINING}-result.json') and len(value['arms']) == 2 and
                all(a['generations'] == 78 and a['boards_checked'] == 312 and a['physical_roots_checked'] == 39936
                    for a in value['arms']), 'Full candidate training audit required')
    elif stage in ('bank-control','evaluation'):
        prefix = CONTROL if stage == 'bank-control' else EVALUATION
        suffix = 'control' if stage == 'bank-control' else 'evaluation'
        value,wrapper = bound_result(prefix),bound_result(f'board-{suffix}-resource-wrapper-v1-initial')
        require(wrapper['dependency_restored'] and wrapper['scientific_output_sha256'] == sha(OUT/f'{prefix}-result.json'),
                'Verified resource wrapper required')
        require(value['complete'], 'Full fixed endpoint required')
        if stage == 'bank-control':
            require(value['control_only'] and value['deals'] == 64 and value['fresh_test_deals_drawn'] == 0 and
                    len(value['cpu_checks']) == 8 and len(value['root_cpu_checks']) == 4, 'Full-bank numerical checks required')
        else:
            require(value['mode'] == 'study' and value['deals'] == 65536 and value['test_seed'] == 9281101,
                    'Fixed prospective evaluation required')
    elif stage in ('control-audit','evaluation-audit'):
        prefix = CONTROL if stage == 'control-audit' else EVALUATION
        value = read(OUT/f'{prefix}-independent-review.json')
        require(value['passed'] and value['source_result_sha256'] == sha(OUT/f'{prefix}-result.json') and
                value['source_registration_sha256'] == sha(OUT/f'{prefix}-registration.json') and
                value['readback_registration_sha256'] == sha(OUT/f'{prefix}-readback-registration.json') and
                value['deals'] == (64 if stage == 'control-audit' else 65536), 'Matching independent evaluation audit required')
        if stage == 'evaluation-audit':
            require(value['batches'] == 2048, 'Every fixed test batch must be audited')
    elif stage == 'report':
        value = read(OUT/'board-final-report-evidence.json')
        require(value['interpretation_pending'] and value['visual_review_pending'] and not value['accuracy_qualified'],
                'Scientific interpretation and visual inspection remain manual')
        require(len(value['outputs']) == 4, 'Incomplete final report')
        for path,digest in {**value['inputs'],**value['outputs']}.items():
            require(sha(path) == digest, 'Changed report evidence: '+path)
    else:
        raise ValueError(stage)


def available(gpu):
    if any(p.exists() for p in LOCKS) or psutil.virtual_memory().available <= 28_000_000_000:
        return False
    if psutil.cpu_percent(interval=1) >= 30 or not production_available():
        return False
    if gpu:
        if psutil.disk_usage('S:/').free <= 40_500_000_000:
            return False
        probe = subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.free','--format=csv,noheader,nounits'],
            capture_output=True,text=True,timeout=5,creationflags=subprocess.CREATE_NO_WINDOW)
        if probe.returncode:
            return False
        util,free = map(float,probe.stdout.strip().splitlines()[0].split(','))
        return util < 10 and free > 6000
    return True


def stop_owned(child, identity):
    if child is None or child.poll() is not None or identity is None or not live(identity):
        return
    owner = psutil.Process(identity['pid'])
    descendants = owner.children(recursive=True)
    for p in reversed(descendants):
        try:
            p.terminate()
        except psutil.NoSuchProcess:
            pass
    child.terminate()
    child.wait(timeout=20)
    psutil.wait_procs(descendants,timeout=20)


def main(upstream_pid, run=False):
    owner = psutil.Process(upstream_pid)
    command = owner.cmdline()
    require(owner.is_running() and any(Path(x).name == 'board_full_resource_wrapper_v1.py' for x in command)
            and '--run' in command and '--stage' in command and 'training' in command,
            'Identify the original live training wrapper')
    upstream = dict(pid=upstream_pid,created=owner.create_time(),command=command)
    rp = OUT/f'{NAME}-registration.json'
    require(not rp.exists(), 'Preserve the existing follow-up registration')
    require(not (OUT/f'{UPSTREAM}-failure.json').exists(), 'Inspect the training failure first')
    proof_path = OUT/f'{NAME}-control-result.json'
    proof = read(proof_path)
    require(proof['passed'] and proof['dependency_states_checked'] == 8 and proof['reused_pid_rejected'] and
            proof['mismatched_process_preserved'] and proof['owned_synthetic_process_stopped'] and
            proof['stage_order_and_arguments_checked'] and proof['scientific_stages_started'] == 0,
            'Verified queue-control checks required')
    for path,digest in proof['inputs'].items():
        require(sha(path) == digest, 'Changed queue qualification source: '+path)
    paths = [proof_path,OUT/f'{UPSTREAM}-registration.json',OUT/f'{TRAINING}-registration.json',
        OUT/'BOARD-ROOT-MATCHED-STUDY-PLAN.md',OUT/'board-final-findings-control-v1-result.json',
        *Path(__file__).parent.glob('*.py')]
    require(all(p.is_file() for p in paths), 'Missing registered prerequisites')
    for _,script,_,_,_,outputs in STAGES:
        require((ROOT/'tools/research'/script).is_file(), 'Missing stage script')
        require(not any((OUT/name).exists() for name in outputs), 'Inspect existing stage evidence before queueing')
    if not run:
        print(json.dumps(dict(ready_to_queue=True,upstream=upstream,stages=[s[0] for s in STAGES],
            work_started=False,production_modified=False)),flush=True)
        return
    inputs = {str(p):sha(p) for p in paths}
    atomic_json(rp,dict(inputs=inputs,upstream=upstream,stages=STAGES,maximum_seconds=172800,
        policy='One invocation per stage, preserve evidence, never retry or restart training automatically.',
        production_modified=False,accuracy_qualified=False))
    began = time.monotonic(); completed = []; child = child_identity = None
    def deadline():
        require(time.monotonic()-began < 172800, 'Follow-up queue deadline reached')
    def status(state, **fields):
        value = dict(state=state,pid=psutil.Process().pid,seconds=time.monotonic()-began,**fields)
        atomic_json(OUT/f'{NAME}-status.json',value,replace=True)
        print(json.dumps(value),flush=True)
    def sources():
        for path,digest in inputs.items():
            require(sha(path) == digest, 'Changed queued source: '+path)
        for row in completed:
            for path,digest in row['outputs'].items():
                require(sha(path) == digest, 'Changed completed stage: '+path)
    try:
        status('waiting for identified trainer',upstream=upstream)
        while True:
            deadline()
            alive = live(upstream)
            if dependency_ready(alive=alive,success_exists=(OUT/f'{UPSTREAM}-result.json').exists(),
                                failure_exists=(OUT/f'{UPSTREAM}-failure.json').exists()):
                break
            time.sleep(30)
        sources();validate('training')
        for name,script,args,gpu,limit,outputs in STAGES:
            status('waiting for available resources',stage=name)
            while not available(gpu):
                deadline();time.sleep(30)
            deadline();sources()
            require(not any((OUT/filename).exists() for filename in outputs), 'Stage already started elsewhere: '+name)
            logpath = OUT/f'{NAME}-{name}.log'
            start = time.monotonic()
            with logpath.open('x',encoding='utf-8') as log:
                child = subprocess.Popen([sys.executable,str(ROOT/'tools/research'/script),*args],cwd=ROOT,
                    stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                child_identity = dict(pid=child.pid,created=psutil.Process(child.pid).create_time())
                status('running stage',stage=name,child=child_identity,log=str(logpath))
                while child.poll() is None:
                    deadline();require(time.monotonic()-start < limit, 'Stage time limit reached: '+name)
                    time.sleep(5)
            require(child.returncode == 0, 'Stage failed; inspect '+str(logpath))
            child = child_identity = None
            validate(name)
            completed.append(dict(stage=name,outputs={str(OUT/p):sha(OUT/p) for p in outputs},
                                  seconds=time.monotonic()-start))
            status('stage complete',stage=name)
        sources()
        atomic_json(OUT/f'{NAME}-result.json',dict(passed=True,registration_sha256=sha(rp),stages=completed,
            seconds=time.monotonic()-began,interpretation_pending=True,visual_review_pending=True,
            accuracy_qualified=False,production_modified=False))
        status('comparison ready for interpretation')
    except BaseException as error:
        atomic_json(OUT/f'{NAME}-failure.json',dict(passed=False,registration_sha256=sha(rp),error=repr(error),
            stages_completed=completed,seconds=time.monotonic()-began,production_modified=False))
        status('stopped for inspection',error=repr(error))
        raise
    finally:
        stop_owned(child,child_identity)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--upstream-pid',type=int,required=True)
    parser.add_argument('--run',action='store_true')
    options = parser.parse_args();main(options.upstream_pid,options.run)
