"""One-shot, byte-preserving compression of six completed storage fixtures."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
from hu_paired_continuation_support_20260925 import LOCK, OTHER
from ntfs_research_storage_v1 import allocated_bytes, attributes, COMPRESSED
from reboot_research_idle_v1 import idle
from hu_completed_evidence_compression_20260924 import digest, read, write

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
SOURCE = ROOT/'research/preflop-evolution/representative-coverage-20260919/flop-storage-fixtures'
PREFIX = 'completed-flop-fixture-compression-v1'
CANDIDATES = OUT/'completed-flop-fixture-compression-candidates-v1.json'
NAMES = {f'fixture-{board}-{iteration}.gto' for board in (0, 1) for iteration in (1, 100, 1000)}


def safe_path(path, parent):
    path = Path(path)
    assert path.is_absolute() and path.parent == parent and path.resolve() == path
    for item in (path, *path.parents):
        assert not attributes(item) & 0x400, 'Reparse point'
    assert path.is_file()
    return path


def verify(path, record):
    assert path.stat().st_size == record['bytes']
    assert path.stat().st_mtime_ns == record['mtime_ns']
    assert digest(path) == record['sha256'], 'File hash changed'


def compress(path, record, guard):
    verify(path, record)
    before = allocated_bytes(path)
    command = Path(os.environ['SystemRoot'])/'System32/compact.exe'
    started = time.monotonic()
    process = subprocess.Popen([str(command), '/C', '/Q', str(path)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        while process.poll() is None:
            guard()
            assert time.monotonic()-started < 300, 'Compression timeout'
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass
        assert process.returncode == 0
    finally:
        if process.poll() is None:
            process.terminate(); process.wait(timeout=20)
    verify(path, record)
    assert attributes(path) & COMPRESSED
    return dict(path=str(path), sha256=record['sha256'], bytes=record['bytes'],
        mtime_ns=record['mtime_ns'], allocated_before=before,
        allocated_after=allocated_bytes(path), seconds=time.monotonic()-started)


def main(control=False):
    started = time.monotonic()
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    prefix = PREFIX+('-control' if control else '')
    rp, result, status = [OUT/f'{prefix}-{s}.json' for s in ('registration','result','status')]
    assert not any(p.exists() for p in (rp, result, status))
    assert not LOCK.exists() and not OTHER.exists() and idle()
    for process in psutil.process_iter(['pid','cmdline']):
        if process.pid != os.getpid():
            assert not any(Path(a).name == 'continuation_flop_storage_run.py'
                for a in (process.info['cmdline'] or [])), 'Fixture owner is live'
    inputs = {str(p):digest(p) for p in (Path(__file__).resolve(),
        ROOT/'tools/research/ntfs_research_storage_v1.py',
        ROOT/'tools/research/hu_completed_evidence_compression_20260924.py',
        OUT/'SHOWDOWN-COMPLETED-FIXTURE-STORAGE-AMENDMENT.md')}
    with LOCK.open('x') as stream:
        stream.write(str(os.getpid()))
    rows = []; error = None; registered = False
    def guard():
        assert time.monotonic()-started < 1800
        assert LOCK.read_text().strip() == str(os.getpid()) and not OTHER.exists()
        assert idle() and shutil.disk_usage('T:/').free >= 40_000_000_000
    try:
        guard()
        if control:
            path = OUT/f'{prefix}-sample.bin'
            data = bytes(range(256))*4096
            with path.open('xb') as stream:
                stream.write(data)
            records = [dict(path=str(path), bytes=len(data), mtime_ns=path.stat().st_mtime_ns,
                sha256=hashlib.sha256(data).hexdigest())]
            safe_path(path, OUT)
            try:
                verify(path, {**records[0], 'sha256':'0'*64})
                raise RuntimeError('Wrong hash accepted')
            except AssertionError:
                pass
            try:
                safe_path(path, SOURCE)
                raise RuntimeError('Outside path accepted')
            except AssertionError:
                pass
        else:
            candidate = read(CANDIDATES)
            assert candidate['eligible_completed_fixtures'] and not candidate['compression_performed']
            for path, expected in candidate['inputs'].items():
                assert digest(path) == expected
            assert read(SOURCE/'fixtures.json')['complete']
            assert read(SOURCE.parent/'flop-storage-status.json')['passed']
            records = candidate['files']
            assert len(records) == 6 and {Path(r['path']).name for r in records} == NAMES
            for record in records:
                path = safe_path(record['path'], SOURCE)
                assert not attributes(path) & COMPRESSED
                verify(path, record)
                assert allocated_bytes(path) == record['allocated_bytes']
            gate = OUT/f'{PREFIX}-control-result.json'
            assert read(gate)['passed'] and read(gate)['source_sha256'] == digest(__file__)
            cp = OUT/'showdown-composite-evaluation-control-v1-result.json'
            cr = OUT/'showdown-composite-evaluation-control-v1-independent-review.json'
            assert read(cp)['passed'] and read(cr)['passed']
            assert read(cr)['source_result_sha256'] == digest(cp)
            inputs.update(candidate['inputs'])
            inputs.update({str(p):digest(p) for p in (CANDIDATES, gate, cp, cr)})
        write(rp, dict(inputs=inputs, files=records, maximum_seconds=1800,
            maximum_file_seconds=300, control=control, deletes_allowed=False,
            production_modified=False, free_reserve_bytes=40_000_000_000))
        registered = True
        for record in records:
            guard()
            row = compress(Path(record['path']), record, guard)
            rows.append(row)
            write(status, dict(state='running', controller_pid=os.getpid(), rows=rows))
            print(json.dumps(row), flush=True)
        for record in records:
            verify(Path(record['path']), record)
        for path, expected in inputs.items():
            assert digest(path) == expected
        complete = dict(passed=True, registration_sha256=digest(rp), source_sha256=digest(__file__),
            rows=rows, saved_bytes=sum(r['allocated_before']-r['allocated_after'] for r in rows),
            seconds=time.monotonic()-started, production_modified=False, deleted_files=0)
        write(result, complete)
        print(json.dumps({k:v for k,v in complete.items() if k != 'rows'}), flush=True)
    except BaseException as exc:
        error = repr(exc)
        write(result, dict(passed=False, error=error, rows=rows,
            registration_sha256=digest(rp) if registered else None, production_modified=False))
        raise
    finally:
        write(status, dict(state='failed' if error else 'complete', error=error,
            rows=rows, seconds=time.monotonic()-started, production_modified=False))
        assert LOCK.read_text().strip() == str(os.getpid())
        LOCK.unlink()


if __name__ == '__main__':
    assert sys.argv[1:] in (['--control'], ['--run'])
    main(control=sys.argv[1:] == ['--control'])
