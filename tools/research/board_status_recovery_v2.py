"""Preserve the fixed evaluation while deferring only pre-lock GPU admission.

Uses the qualified v1 status override and follow-up stages. Each rejected
admission retains a distinct wrapper registration/failure. Any other failure,
or any failure after admission, remains terminal and is never retried here.
"""
import argparse
from pathlib import Path
import time
import json
import board_status_recovery_v1 as base
from board_full_followup_queue_v1 import OUT, ROOT, read, sha, require, bound_result, available
from board_prefix_publication_v1 import atomic_json
from windows_progress_publication_v1 import status_only

SCRIPT = Path(__file__).resolve()
NAME = 'board-status-recovery-v2'
WRAPPER = 'board-admission-status-recovery-v1'
CONTROL = 'board-admission-deferral-control-v1-result.json'
OLD_PROOF = base.proof
OLD_PREFLIGHT = base.preflight


def early_gpu_rejection(error, filename):
    if not isinstance(error, AssertionError) or error.__traceback__ is None:
        return False
    trace = error.__traceback__
    while trace.tb_next is not None:
        trace = trace.tb_next
    return (Path(trace.tb_frame.f_code.co_filename).resolve() == Path(filename).resolve()
            and trace.tb_frame.f_code.co_name == 'run' and trace.tb_lineno == 110)


def admissions(invoke, wait_idle, accept_deferral, record, *, limit=8):
    for attempt in range(1, limit + 1):
        wait_idle()
        try:
            return attempt, invoke(attempt)
        except BaseException as error:
            if not accept_deferral(error, attempt):
                raise
            record(attempt)
            if attempt == limit:
                raise


def proof():
    OLD_PROOF()
    path = OUT / CONTROL
    value = read(path)
    require(value['passed'] and value['only_exact_prelock_gpu_assertion_accepted'] and
            value['successful_admission_runs_once'] and value['other_errors_not_retried'] and
            value['retry_limit_enforced'], 'Admission deferral controls required')
    for p, digest in value['inputs'].items():
        require(sha(p) == digest, 'Changed admission control input: ' + p)
    return path


def preflight():
    prefix = 'board-evaluation-resource-wrapper-v1-status-recovery1'
    pp, rp = [OUT / f'{prefix}-{suffix}.json' for suffix in ('failure', 'registration')]
    previous = read(pp)
    require(previous['completed_scans'] == 0 and previous['error'] == 'AssertionError()'
            and previous['registration_sha256'] == sha(rp), 'Inspect different prior rejection')
    log = OUT / 'board-status-recovery-v1-evaluation.log'
    text = log.read_text(encoding='utf-8')
    require('line 110, in run' in text and 'assert utilization < 10 and free > 6000' in text,
            'Expected pre-lock admission rejection required')
    checkpoint, paths = OLD_PREFLIGHT()
    paths += [pp, rp, log, OUT / 'board-status-recovery-v1-failure.json', OLD_PROOF()]
    return checkpoint, paths


def recovered_evaluation():
    proof()
    queue_reg = OUT / f'{NAME}-registration.json'
    registered = read(queue_reg)
    for p, digest in registered['inputs'].items():
        require(sha(p) == digest, 'Changed recovery source: ' + p)
    import board_complete_evaluation_study_v1 as driver
    from board_evaluation_resource_wrapper_v1 import main as wrapped
    # This exact frozen assertion is before lock acquisition, inventory, bank
    # loading, archive creation and drawing any test deals.
    require(Path(driver.__file__).read_text().splitlines()[109].strip() ==
            'assert utilization < 10 and free > 6000', 'Frozen admission location changed')
    rp = OUT / f'{WRAPPER}-registration.json'
    atomic_json(rp, dict(queue_registration_sha256=sha(queue_reg),
        control_sha256=sha(OUT / CONTROL), inputs=registered['inputs'],
        maximum_admission_attempts=8, maximum_seconds=43200,
        scope='Repeat only the exact pre-lock GPU admission assertion, with zero inventory scans, '
              'no new checkpoints and no new archive attempt. Never retry scientific work. '
              'Every frozen resource guard remains unchanged.',
        production_modified=False, partial_payoffs_inspected=False))
    began = time.monotonic(); deferred = []
    original = driver.write_status
    checkpoint_names = sorted(p.name for p in driver.STORE.glob('checkpoint-*.json'))
    archive_names = sorted(p.name for p in driver.STORE.glob('attempt-*'))
    def deadline():
        require(time.monotonic() - began < 43200, 'Admission recovery deadline reached')
    def wait_idle():
        stable = 0
        while stable < 4:
            deadline()
            stable = stable + 1 if available(True) else 0
            if stable < 4:
                time.sleep(5 if stable else 30)
    def invoke(index):
        deadline()
        attempt = f'status-recovery2-{index:02d}'
        with status_only(driver):
            wrapped('evaluation', run=True, resume=True, attempt=attempt)
        require(driver.write_status is original, 'Status dependency not restored')
        return attempt
    def accept(error, index):
        if not early_gpu_rejection(error, driver.__file__):
            return False
        prefix = f'board-evaluation-resource-wrapper-v1-status-recovery2-{index:02d}'
        failure = read(OUT / f'{prefix}-failure.json')
        require(failure['completed_scans'] == 0 and failure['error'] == repr(error) and
                failure['registration_sha256'] == sha(OUT / f'{prefix}-registration.json'),
                'A rejection after any inventory scan is not deferrable')
        require(driver.write_status is original and not driver.LOCK.exists() and not driver.OTHER.exists(),
                'Another worker or unrestored dependency: stop for inspection')
        require(sorted(p.name for p in driver.STORE.glob('checkpoint-*.json')) == checkpoint_names and
                sorted(p.name for p in driver.STORE.glob('attempt-*')) == archive_names and
                not (OUT / f'{driver.PREFIX}-result.json').exists(), 'Scientific work began; do not retry')
        return True
    def record(index):
        deferred.append(index)
        print(json.dumps(dict(state='GPU admission deferred before scientific work', attempt=index,
            completed_deals=17408)), flush=True)
    try:
        count, attempt = admissions(invoke, wait_idle, accept, record)
        child_prefix = 'board-evaluation-resource-wrapper-v1-' + attempt
        child = bound_result(child_prefix)
        require(child['dependency_restored'] and len(child['scans']) == 1 and
                child['scientific_output_sha256'] == sha(OUT / f'{driver.PREFIX}-result.json'),
                'Complete admitted evaluation required')
        atomic_json(OUT / f'{WRAPPER}-result.json', dict(passed=True,
            registration_sha256=sha(rp), scientific_output_sha256=child['scientific_output_sha256'],
            scientific_output=child['scientific_output'], dependency_restored=True,
            status_dependency_restored=driver.write_status is original,
            successful_wrapper=str(OUT / f'{child_prefix}-result.json'),
            successful_wrapper_sha256=sha(OUT / f'{child_prefix}-result.json'),
            admission_attempts=count, deferred_attempts=deferred,
            seconds=time.monotonic()-began, production_modified=False))
    except BaseException as error:
        atomic_json(OUT / f'{WRAPPER}-failure.json', dict(passed=False,
            registration_sha256=sha(rp), error=repr(error), deferred_attempts=deferred,
            seconds=time.monotonic()-began))
        raise


def main(run=False):
    base.NAME = NAME
    base.SCRIPT = SCRIPT
    base.WRAPPER = WRAPPER
    base.proof = proof
    base.preflight = preflight
    base.PRIOR = [*base.PRIOR, dict(pid=77652, created=1790547315.2982726),
                  dict(pid=76680, created=1790547830.0906672)]
    base.main(run)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--resume-evaluation', action='store_true')
    args = parser.parse_args()
    recovered_evaluation() if args.resume_evaluation else main(args.run)
