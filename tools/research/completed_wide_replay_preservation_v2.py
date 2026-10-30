"""Preserve all 16 completed wide replay checkpoints with transparent LZX.

Only the exact paths and hashes in the historical successful review qualify.
No deletion, relocation, format conversion or model-content modification.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha
from ntfs_research_storage_v1 import allocated_bytes, attributes
from board_prefix_publication_v1 import atomic_json
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK, OTHER

PREFIX = 'completed-wide-replay-preservation-v2'
OWNER = 'hu-wide-cold-replay-v1'
SOURCE = Path('S:/GTOpen-research') / OWNER
COMPACT = Path(os.environ['SystemRoot']) / 'System32/compact.exe'
REG = OUT / f'{PREFIX}-registration.json'


def safe_path(name):
    names = {f'{kind}-step-{i:02d}/entry-0-generation-0.bin'
             for kind in ('candidate', 'reference') for i in range(8)}
    assert name in names
    path = SOURCE / name
    assert path.resolve() == path and path.is_file()
    for item in (path, *path.parents):
        assert not attributes(item) & 0x400, str(item)
    assert path.stat().st_nlink == 1, 'Do not mutate shared hard-linked fixtures'
    return path


def owners_idle():
    for process in psutil.process_iter(['pid', 'ppid', 'cmdline']):
        if process.pid == os.getpid():
            continue
        args = process.info['cmdline'] or []
        if (process.info['ppid'] == os.getpid() and len(args) == 5
                and os.path.normcase(args[0]) == os.path.normcase(str(COMPACT))
                and args[1:4] == ['/C', '/EXE:LZX', '/Q']
                and Path(args[4]).is_relative_to(SOURCE)):
            continue
        command = ' '.join(args).lower()
        assert not any(n in command for n in (OWNER, 'hu_wide_cold_replay', 'hu_wide_maturity')), 'Historical owner active'


def initial_qualifications():
    review_path = OUT / 'wide-cold-replay-v1-review.json'
    original_reg = OUT / 'wide-cold-replay-v1-registration.json'
    status_path = OUT / f'{OWNER}-status.json'
    review, status = read(review_path), read(status_path)
    assert review['passed'] and review['registration_sha256'] == sha(original_reg)
    assert review['result']['all_checkpoint_bytes_equal'] and review['result']['all_values_bitwise_equal']
    assert status['exit_code'] == 0 and status['error'] is None
    expected = review['checkpoint_hashes']
    assert len(expected) == 16
    assert {Path(p) for p in expected} == set(SOURCE.glob('*/*.bin'))
    control_reg = OUT / 'checkpoint-lzx-storage-control-v1-registration.json'
    control_result = OUT / 'checkpoint-lzx-storage-control-v1-result.json'
    control = read(control_result)
    assert control['passed'] and control['original_unchanged']
    assert control['registration_sha256'] == sha(control_reg)
    rejection = OUT / 'board-matched-storage-rejected-48506a3e.json'
    budget = read(rejection)
    assert not budget['passed'] and budget['global_allocated_bytes'] + 16_000_000_000 < 800_000_000_000
    assert not (OUT / 'board-root-matched-continuation-v1-registration.json').exists()
    paths = [Path(__file__).resolve(), review_path, original_reg, status_path,
             control_reg, control_result, rejection, OUT / 'BOARD-WIDE-REPLAY-PRESERVATION.md',
             ROOT / 'tools/research/ntfs_research_storage_v1.py',
             ROOT / 'tools/research/board_prefix_publication_v1.py']
    records = []
    for name, digest in sorted(expected.items()):
        relative = Path(name).relative_to(SOURCE).as_posix()
        path = safe_path(relative)
        st = path.stat()
        records.append(dict(name=relative, sha256=digest, bytes=st.st_size,
                            mtime_ns=st.st_mtime_ns, allocated_before=allocated_bytes(path)))
    assert sum(r['bytes'] for r in records) == review['result']['bytes_written'] == 55_045_909_888
    return records, {str(p): sha(p) for p in paths}


def qualifications():
    current, inputs = initial_qualifications()
    old_reg = OUT / 'completed-wide-replay-preservation-v1-registration.json'
    old_failure = OUT / 'completed-wide-replay-preservation-v1-failure.json'
    original, failure = read(old_reg), read(old_failure)
    assert not failure['passed'] and failure['error'].startswith('FileExistsError(')
    assert failure['registered'] and not (OUT / 'completed-wide-replay-preservation-v1-result.json').exists()
    for p, digest in original['inputs'].items():
        assert sha(p) == digest, p
    by_name = {r['name']: r for r in current}
    for row in original['records']:
        assert all(row[k] == by_name[row['name']][k] for k in ('name','sha256','bytes','mtime_ns'))
    assert len(by_name) == len(original['records']) == 16
    inputs.update(original['inputs'])
    inputs.update({str(p):sha(p) for p in (Path(__file__).resolve(), old_reg, old_failure)})
    for p in (OUT / 'completed-wide-replay-preservation-v1').glob('*.json'):
        inputs[str(p)] = sha(p)
    return original['records'], inputs


def verify(record):
    path = safe_path(record['name'])
    before = path.stat()
    assert before.st_size == record['bytes'] and before.st_mtime_ns == record['mtime_ns']
    with path.open('rb') as stream:
        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
    after = path.stat()
    assert actual == record['sha256'] and after.st_size == before.st_size and after.st_mtime_ns == before.st_mtime_ns
    return path


def main(run=False):
    records, inputs = qualifications()
    owners_idle()
    assert production_available() and not LOCK.exists() and not OTHER.exists()
    assert psutil.virtual_memory().available > 24_000_000_000 and psutil.disk_usage('S:/').free > 56_000_000_000
    if not run:
        print(json.dumps(dict(ready=True, files=len(records), source=str(SOURCE),
            logical_bytes=sum(r['bytes'] for r in records), compression_started=False)))
        return
    assert psutil.cpu_percent(interval=1) < 30
    assert not REG.exists() and not (OUT / f'{PREFIX}-result.json').exists()
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    with LOCK.open('x') as stream:
        stream.write(str(os.getpid()))
    began = time.monotonic()
    stop = threading.Event()
    probe_lock = threading.Lock()
    last_probe = [0.]
    completed = []
    registered = False
    def guard():
        assert not stop.is_set() and time.monotonic()-began < 3600
        with probe_lock:
            if time.monotonic()-last_probe[0] > 5:
                assert LOCK.read_text() == str(os.getpid()) and not OTHER.exists()
                assert production_available() and psutil.virtual_memory().available > 20_000_000_000
                assert psutil.disk_usage('S:/').free > 40_000_000_000
                owners_idle()
                last_probe[0] = time.monotonic()
    def compress(record):
        guard()
        path = verify(record)
        old_receipt = OUT / 'completed-wide-replay-preservation-v1' / (record['name'].split('/')[0]+'.json')
        if old_receipt.exists():
            value = read(old_receipt)
            assert value['name'] == record['name'] and value['sha256'] == record['sha256']
            assert value['allocated_before'] == record['allocated_before']
            assert value['allocated_after'] == allocated_bytes(path)
            atomic_json(OUT / PREFIX / old_receipt.name, value)
            return value
        child = subprocess.Popen([str(COMPACT), '/C', '/EXE:LZX', '/Q', str(path)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        started = time.monotonic()
        try:
            while child.poll() is None:
                guard()
                assert time.monotonic()-started < 600
                try:
                    child.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    pass
            assert child.returncode == 0, 'Compression failed: ' + str(path)
        finally:
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=20)
        verify(record)
        value = dict(name=record['name'], sha256=record['sha256'],
                     allocated_before=record['allocated_before'], allocated_after=allocated_bytes(path))
        atomic_json(OUT / PREFIX / (record['name'].split('/')[0]+'.json'), value)
        return value
    try:
        guard()
        atomic_json(REG, dict(inputs=inputs, source=str(SOURCE), records=records, workers=4,
            maximum_seconds=3600, maximum_file_seconds=600, scratch_reserve_bytes=16_000_000_000,
            algorithm='Windows transparent LZX', no_deletion=True, native_restore_repeated=False,
            original_paths_preserved=True, production_modified=False))
        registered = True
        (OUT / PREFIX).mkdir()
        with ThreadPoolExecutor(max_workers=4) as pool:
            pending = [pool.submit(compress, r) for r in records]
            try:
                for future in as_completed(pending):
                    completed.append(future.result())
                    status = dict(files_verified=len(completed), total_files=16,
                        recovered_bytes=sum(r['allocated_before']-r['allocated_after'] for r in completed),
                        seconds=time.monotonic()-began, pid=os.getpid())
                    atomic_json(OUT / f'{PREFIX}-status.json', status, replace=True)
                    print(json.dumps(status), flush=True)
            except BaseException:
                stop.set()
                raise
        assert {SOURCE/r['name'] for r in records} == set(SOURCE.glob('*/*.bin'))
        for p, digest in inputs.items():
            assert sha(p) == digest, p
        owners_idle()
        atomic_json(OUT / f'{PREFIX}-result.json', dict(passed=True, registration_sha256=sha(REG),
            records=sorted(completed, key=lambda r:r['name']), files_verified=16,
            recovered_bytes=sum(r['allocated_before']-r['allocated_after'] for r in completed),
            seconds=time.monotonic()-began, no_deletion=True, all_logical_hashes_sizes_mtimes_preserved=True,
            native_restore_repeated=False, production_modified=False))
    except BaseException as error:
        atomic_json(OUT / f'{PREFIX}-failure.json', dict(passed=False, error=repr(error),
            registered=registered, files_verified=len(completed), seconds=time.monotonic()-began))
        raise
    finally:
        assert LOCK.read_text() == str(os.getpid())
        LOCK.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true')
    main(parser.parse_args().run)
