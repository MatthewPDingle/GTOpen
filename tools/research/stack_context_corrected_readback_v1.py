"""Run the explicitly reviewed corrected audit once; never train or evaluate.

Preserve the failed v6 reader. Its original absolute deadline remains binding.
CPU-only reference verification yields to active production work and RAM pressure.
"""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import psutil
import stack_context_corrected_audit_provenance_v1 as provenance
from river_matched_training_pilot_v1 import LOCK, OTHER, production_available

ROOT, OUT = provenance.ROOT, provenance.OUT
NAME = 'stack-context-corrected-readback-v1'
READER = 'stack-context-matched-readback-v7'
SOURCE = ROOT / 'tools/research/stack_context_matched_readback_v7.py'
CONTROL = OUT / 'stack-context-corrected-readback-check-v1-result.json'
COMMAND = ['C:/Program Files/Python312/python.exe', '-B', str(SOURCE), '--run']
ATTEMPT, RESULT, FAILED, OWNER, STATUS = (OUT / (NAME + s + '.json') for s in ('-attempt', '-result', '-failure', '-owner', '-status'))
read, sha, require = provenance.read, provenance.sha, provenance.require


def publish(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, sort_keys=True, separators=(',', ':'), allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())


def status(stage, **fields):
    temporary = STATUS.with_suffix('.writing')
    with temporary.open('w', encoding='utf-8') as stream:
        json.dump(dict(stage=stage, pid=os.getpid(), created=psutil.Process().create_time(), unix=time.time(), **fields), stream)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, STATUS)


def validate_control(control, review):
    require(control['complete'] is True and control['passed'] is True
            and control['reader_sha256'] == sha(SOURCE)
            and control['runner_sha256'] == sha(__file__)
            and control['provenance_sha256'] == sha(provenance.__file__)
            and control['original_reader_sha256'] == sha(ROOT / 'tools/research/stack_context_matched_readback_v6.py')
            and control['original_deadline_unix'] == review['original_deadline_unix'] == 1790934006.0150957
            and control['unchanged_numerical_and_authenticity_checks'] is True
            and control['full_scope'] == dict(training_chance_cycles=256, evaluation_archives=896,
                preflop_reference_replays=28, postflop_reference_batches=14, comparisons=56, torch_threads=4)
            and control['new_scientific_work'] is False, 'Unqualified or expanded corrected audit')


def main(run=False):
    if not run:
        print(json.dumps(dict(prepared=True, started=ATTEMPT.exists(), complete=RESULT.exists(), command=COMMAND)))
        return
    reader_paths = [OUT / (READER + s + '.json') for s in ('-attempt', '-result', '-failure')]
    require(not any(p.exists() for p in (ATTEMPT, RESULT, FAILED, OWNER, LOCK, OTHER, *reader_paths)),
            'Do not duplicate or retry an admitted corrected audit')
    review = provenance.reviewed_failure()
    control = read(CONTROL)
    validate_control(control, review)
    for path, identity in control['inputs'].items():
        require(sha(path) == identity, 'Changed qualification input: ' + path)
    owner = dict(pid=os.getpid(), created=psutil.Process().create_time(), unix=time.time(),
        runner_sha256=sha(__file__), reader_sha256=sha(SOURCE), provenance_sha256=sha(provenance.__file__),
        control_sha256=sha(CONTROL), original_audit_deadline_unix=review['original_deadline_unix'],
        failed_readback_sha256=review['failed_readback_sha256'], child_command=COMMAND,
        launcher_command=[sys.executable, '-B', str(Path(__file__).resolve()), '--run'])
    publish(OWNER, owner)
    publish(ATTEMPT, owner)
    try:
        while True:
            require(time.time() < review['original_deadline_unix'], 'Original audit deadline expired; preserve evidence')
            require(not LOCK.exists() and not OTHER.exists() and not any(p.exists() for p in reader_paths),
                    'Another study or corrected reader has been admitted')
            if production_available() and psutil.virtual_memory().available >= 40_000_000_000:
                break
            status('waiting-for-cpu-resources')
            time.sleep(30)
        prefix = OUT / (NAME + '-reader')
        with Path(str(prefix) + '-stdout.log').open('xb') as stdout, Path(str(prefix) + '-stderr.log').open('xb') as stderr:
            child = subprocess.Popen(COMMAND, cwd=ROOT, stdout=stdout, stderr=stderr,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            actual = psutil.Process(child.pid)
            started = dict(pid=child.pid, created=actual.create_time(), parent_pid=os.getpid(), unix=time.time(),
                command=COMMAND, evaluation_result_sha256=sha(OUT / 'stack-context-matched-evaluation-v5-result.json'))
            require(actual.ppid() == os.getpid() and actual.cmdline() == COMMAND, 'Unexpected admitted reader identity')
            publish(str(prefix) + '-started.json', started)
            status('corrected-reader-running', child=started)
            code = child.wait()
        finished = dict(**started, exit_code=code, finished_unix=time.time(),
            stdout_sha256=sha(str(prefix) + '-stdout.log'), stderr_sha256=sha(str(prefix) + '-stderr.log'))
        publish(str(prefix) + '-finished.json', finished)
        require(code == 0, 'Corrected audit failed; preserve without retry')
        reader_path = OUT / (READER + '-result.json')
        reader, attempt = read(reader_path), read(reader_paths[0])
        require(all(reader[k] is True for k in ('complete', 'passed', 'independent_readback_complete',
                    'corrected_checker', 'failed_readback_preserved'))
                and reader['evaluation_result_sha256'] == started['evaluation_result_sha256']
                and reader['original_audit_deadline_unix'] == owner['original_audit_deadline_unix']
                and reader['preserved_failed_readback_sha256'] == owner['failed_readback_sha256']
                and attempt['pid'] == started['pid'] and abs(attempt['process_created'] - started['created']) < .01
                and attempt['torch_threads'] == 4 and attempt['new_scientific_work'] is False
                and not any(p.exists() for p in (LOCK, OTHER, reader_paths[2])), 'Incomplete corrected audit or unreleased ownership')
        require(time.time() < review['original_deadline_unix'], 'Original audit deadline exceeded')
        validate_control(read(CONTROL), review)
        for path, identity in review['inputs'].items():
            require(sha(path) == identity, 'Changed preserved evidence: ' + path)
        publish(RESULT, dict(complete=True, passed=True, unix=time.time(), reader_result_sha256=sha(reader_path),
            evaluation_result_sha256=started['evaluation_result_sha256'], control_sha256=sha(CONTROL),
            independent_readback_complete=True, failed_readback_preserved=True,
            original_audit_deadline_unix=review['original_deadline_unix'], new_scientific_work=False,
            native_execution=False, fitting=False, gpu_used=False, production_modified=False, broad_goal_complete=False))
        status('independent-readback-complete-root-analysis-outstanding')
    except BaseException as error:
        publish(FAILED, dict(error=repr(error), traceback=traceback.format_exc(), unix=time.time(),
            automatic_retry_allowed=False, preserve_evidence=True, production_modified=False))
        raise
    finally:
        if OWNER.exists() and read(OWNER) == owner:
            OWNER.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true')
    main(parser.parse_args().run)
