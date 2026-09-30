"""Archive/recover retained native-cycle bytes; no new solves or fits."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import json
from pathlib import Path
import shutil
import time
import traceback
import psutil
import stack_context_cycle_archive_v1 as archive
from board_study_storage_v1 import create, measure
from global_research_inventory_v3 import measure as inventory
from owned_columnar_evaluation_archive_v1 import durable, encoded
from river_matched_training_pilot_v1 import ROOT, OUT, LOCK, OTHER, production_available

NAME = 'stack-context-cycle-archive-control-v1'
STORE = Path('S:/GTOpen-research') / NAME
SOURCE = Path('S:/GTOpen-research/stack-context-native-cycle-control-v4/cycle-1')
TOKEN = 'stack-context-cycle-archive-control-v1-new-copies'
REG, ATTEMPT, RESULT, FAILURE = (OUT / (NAME + suffix + '.json') for suffix in
                                ('-registration', '-attempt', '-result', '-failure'))


def read(path):
    return json.loads(Path(path).read_bytes())


def main():
    if any(path.exists() for path in (STORE, REG, ATTEMPT, RESULT, FAILURE, LOCK, OTHER)):
        raise ValueError('Existing control attempt or research owner')
    start = time.monotonic(); last = 0
    def guard():
        nonlocal last
        now = time.monotonic()
        if now - start > 1800:
            raise RuntimeError('Archive control 30-minute bound')
        if now - last > 2:
            if (not production_available() or OTHER.exists() or psutil.virtual_memory().available < 24_000_000_000
                    or psutil.disk_usage('S:/').free < 40_000_000_000):
                raise RuntimeError('Yield to production/resource pressure')
            last = now
    guard()
    original_result = OUT / 'stack-context-native-cycle-control-v4-result.json'
    original_review = OUT / 'stack-context-native-cycle-control-v4-readback-result.json'
    # Find the actual independently completed readback by its fixed prefix.
    original_review = OUT / 'stack-context-native-cycle-readback-v1-result.json'
    main_result = read(original_result); review = read(original_review)
    if not main_result['passed'] or not review['passed']:
        raise ValueError('Qualified original cycle required')
    files = sorted(path for path in SOURCE.rglob('*') if path.is_file())
    identities = {str(path): archive.sha(path) for path in files}
    if any(main_result['artifacts'].get(path) != value for path, value in identities.items()):
        raise ValueError('Original cycle changed')
    accounting = inventory()
    if sum(row['allocated_file_bytes'] for row in accounting) + 8_000_000_000 > 800_000_000_000:
        raise ValueError('Global research allocation cap')
    scripts = [Path(__file__).resolve(), Path(archive.__file__), ROOT / 'tools/research/owned_research_archive_v1.py',
               ROOT / 'tools/research/parallel_owned_archive_v1.py', ROOT / 'tools/research/owned_columnar_evaluation_archive_v1.py']
    with LOCK.open('x') as stream:
        stream.write(str(os.getpid()))
    try:
        create(STORE)
        durable(STORE / 'archive-owner.json', encoded(dict(format=1, token=TOKEN, purpose='new-research-scratch-v1')))
        durable(REG, encoded(dict(inputs={str(path): archive.sha(path) for path in scripts},
                original_result_sha256=archive.sha(original_result), original_review_sha256=archive.sha(original_review),
                originals=identities, original_bytes=sum(path.stat().st_size for path in files), workers=4,
                maximum_seconds=1800, maximum_reservation_bytes=8_000_000_000, new_labels=False, new_fits=False)))
        durable(ATTEMPT, encoded(dict(pid=os.getpid(), process_created=psutil.Process().create_time(), registration_sha256=archive.sha(REG))))
        copies = STORE / 'copies'; copies.mkdir()
        for path in files:
            guard(); target = copies / path.relative_to(SOURCE); target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            if archive.sha(target) != identities[str(path)]:
                raise ValueError('Copy differs')
        copied = time.monotonic()
        print(json.dumps(dict(stage='copied', files=len(files), seconds=copied-start)), flush=True)
        destination = STORE / 'archive'
        packed = archive.archive_cycle(copies, destination, root=STORE, token=TOKEN, guard=guard, workers=4, retire=False)
        compressed = time.monotonic()
        print(json.dumps(dict(stage='compressed-and-readback', packed_bytes=packed['packed_bytes'], seconds=compressed-copied)), flush=True)
        # A changed raw duplicate must be preserved and refused.
        target = copies / 'metrics.json'; original = target.read_bytes()
        target.write_bytes(original + b' ')
        try:
            archive.finish_retirement(destination, root=STORE, token=TOKEN, guard=guard)
        except ValueError as error:
            if 'Changed or unregistered raw' not in str(error):
                raise
        else:
            raise ValueError('Changed duplicate was accepted')
        if sum(1 for path in copies.rglob('*') if path.is_file()) != len(files):
            raise ValueError('Refusal removed a raw file')
        target.write_bytes(original)
        def interrupt(count):
            if count == 7:
                raise InterruptedError('simulated retirement interruption')
        try:
            archive.finish_retirement(destination, root=STORE, token=TOKEN, guard=guard, on_retired=interrupt)
        except InterruptedError:
            pass
        else:
            raise ValueError('Retirement interruption not exercised')
        if sum(1 for path in copies.rglob('*') if path.is_file()) != len(files)-7:
            raise ValueError('Unexpected interruption boundary')
        completed = archive.finish_retirement(destination, root=STORE, token=TOKEN, guard=guard)
        plan, _ = archive.verify_index(destination, root=STORE, token=TOKEN, guard=guard)
        if {str(SOURCE / row['path']): row['sha256'] for row in plan['members']} != identities:
            raise ValueError('Archive plan differs from pinned original bytes')
        for path, expected in identities.items():
            guard()
            if archive.sha(path) != expected:
                raise ValueError('Legacy original changed')
        durable(RESULT, encoded(dict(complete=True, passed=True, registration_sha256=archive.sha(REG),
            files=len(files), original_bytes=plan['raw_bytes'], packed_bytes=packed['packed_bytes'],
            ratio=plan['raw_bytes']/packed['packed_bytes'], copy_seconds=copied-start,
            archive_and_readback_seconds=compressed-copied, seconds=time.monotonic()-start,
            changed_duplicate_rejected=True, partial_retirement_recovered=True, legacy_originals_unchanged=True,
            storage=measure(STORE), index_sha256=archive.sha(destination/'index.json'),
            new_labels=False, new_fits=False, **{'retirement':completed})))
        print(json.dumps(dict(passed=True, ratio=plan['raw_bytes']/packed['packed_bytes'], seconds=time.monotonic()-start)), flush=True)
    except BaseException as error:
        durable(FAILURE, encoded(dict(error=repr(error), traceback=traceback.format_exc(), retry_allowed=False)))
        raise
    finally:
        if LOCK.exists() and LOCK.read_text() == str(os.getpid()):
            LOCK.unlink()


if __name__ == '__main__':
    main()
