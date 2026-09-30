"""Once-only read-only authentication of the completed interrupted boundaries."""
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, 'T:/Dev/GTOpen/tools/research')
import psutil
import stack_context_interruption_provenance_v1 as proof

NAME = 'stack-context-interruption-readback-v1'


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, sort_keys=True, allow_nan=False)
        stream.write('\n')


def main():
    process = psutil.Process()
    process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    attempt, result, failure = (proof.OUT / (NAME + suffix + '.json')
        for suffix in ('-attempt', '-result', '-failure'))
    proof.require(not any(p.exists() for p in (attempt, result, failure)), 'Readback already attempted')
    control = proof.OUT / 'stack-context-interruption-provenance-check-v1-result.json'
    check = proof.read(control)
    proof.require(check.get('complete') is True and check.get('passed') is True
        and check['inputs'][str(Path(proof.__file__).resolve())] == proof.sha(proof.__file__),
        'Qualified verifier identity differs')
    began = time.monotonic()
    inputs = {str(p): proof.sha(p) for p in (Path(__file__).resolve(), Path(proof.__file__).resolve(), control)}
    save(attempt, dict(pid=process.pid, created=process.create_time(), unix=time.time(), inputs=inputs,
        read_only=True, scientific_fits=0, native_calls=0, gpu=False))
    try:
        identity, files = proof.verify_recovery()
        for path in files:
            inputs[str(path)] = proof.sha(path)
        for path, digest in check['inputs'].items():
            proof.require(proof.sha(path) == digest, 'Qualification input changed')
        value = dict(complete=True, passed=True, unix=time.time(), seconds=time.monotonic()-began,
            inputs=inputs, recovery=identity, retained_files_bound=identity['retained_files_bound'],
            actual_recovered_boundaries_reviewed=True, full_archive_payload_readback_outstanding=True,
            full_training_complete=False, scientific_evaluation_complete=False,
            scientific_fits=0, native_calls=0, gpu=False, production_modified=False)
        save(result, value)
        print(json.dumps({k:v for k,v in value.items() if k != 'inputs'}), flush=True)
    except BaseException as error:
        save(failure, dict(complete=False, passed=False, unix=time.time(), seconds=time.monotonic()-began,
            error=repr(error), inputs=inputs))
        raise


if __name__ == '__main__':
    main()
