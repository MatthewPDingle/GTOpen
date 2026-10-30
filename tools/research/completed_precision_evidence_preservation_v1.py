"""Lossless NTFS preservation of two completed, independently reviewed stores."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import threading
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha
from board_prefix_publication_v1 import atomic_json
from bounded_parallel_evaluation_archive_v2 import production_available
from hu_completed_evidence_ntfs_compression_20260923 import snapshot
from ntfs_research_storage_v1 import allocated_bytes
from weighted_learning_cuda_control_20260927 import LOCK, OTHER

PREFIX = 'completed-precision-evidence-preservation-v1'
OWNERS = ('sampled-physical-allin-population-diagnostic-v1', 'board-precision-repeat-v1')
COMPACT = Path(os.environ['SystemRoot']) / 'System32/compact.exe'


def list_files(folder):
    assert folder.resolve() == folder and folder.parent == Path('S:/GTOpen-research') and folder.name in OWNERS
    for parent in (folder, *folder.parents):
        assert not parent.lstat().st_file_attributes & 0x400
    result = []
    def fail(error):
        raise error
    for parent, directories, files in os.walk(folder, followlinks=False, onerror=fail):
        for name in directories + files:
            path = Path(parent) / name
            st = path.lstat()
            assert not st.st_file_attributes & 0x400
            if name in files:
                assert path.is_file() and st.st_nlink == 1
                result.append(path)
    return sorted(result)


def main(run=False):
    inputs = {str(p): sha(p) for p in (Path(__file__).resolve(),
        ROOT / 'tools/research/hu_completed_evidence_ntfs_compression_20260923.py',
        ROOT / 'tools/research/ntfs_research_storage_v1.py')}
    folders = []
    for i, name in enumerate(OWNERS):
        rp, result_path = [OUT / f'{name}-{suffix}.json' for suffix in ('registration', 'result')]
        review_path = OUT / f'{name}-{"independent-review" if i == 0 else "review"}.json'
        result, review = read(result_path), read(review_path)
        assert result['passed'] and result['registration_sha256'] == sha(rp)
        assert review['passed'] and review['registration_sha256'] == sha(rp)
        assert review['result_sha256' if i == 0 else 'pilot_result_sha256'] == sha(result_path)
        inputs.update({str(p): sha(p) for p in (rp, result_path, review_path)})
        folder = Path('S:/GTOpen-research') / name
        files = list_files(folder)
        assert files and sum(p.stat().st_size for p in files) < 6_000_000_000
        folders.append(folder)
    assert production_available() and not LOCK.exists() and not OTHER.exists()
    if not run:
        print(json.dumps(dict(ready=True, folders=[str(p) for p in folders], compression_started=False)))
        return
    assert psutil.cpu_percent(interval=1) < 30
    rp = OUT / f'{PREFIX}-registration.json'
    assert not rp.exists() and not (OUT / f'{PREFIX}-result.json').exists()
    previous = OUT / 'completed-wide-maturity-preservation-v1-independent-review.json'
    assert read(previous)['passed']
    inputs[str(previous)] = sha(previous)
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    began = time.monotonic()
    probe_lock = threading.Lock()
    last_probe = [0.]
    def guard():
        assert time.monotonic()-began < 1800
        with probe_lock:
            if time.monotonic()-last_probe[0] > 3:
                assert production_available() and LOCK.read_text() == str(os.getpid()) and not OTHER.exists()
                assert psutil.disk_usage('S:/').free > 40_000_000_000
                assert psutil.virtual_memory().available > 20_000_000_000
                for p in psutil.process_iter(['pid', 'ppid', 'cmdline']):
                    if p.pid == os.getpid() or p.info['ppid'] == os.getpid():
                        continue
                    command = ' '.join(p.info['cmdline'] or []).lower()
                    assert not any(name in command for name in OWNERS), 'Completed owner is active'
                last_probe[0] = time.monotonic()
    def preserve(folder):
        guard()
        files = list_files(folder)
        before = snapshot(folder)
        amount_before = sum(allocated_bytes(p) for p in files)
        manifest = OUT / f'{PREFIX}-{folder.name}-manifest.json'
        atomic_json(manifest, before)
        child = subprocess.Popen([str(COMPACT), '/C', '/Q', f'/S:{folder}'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        started = time.monotonic()
        try:
            while child.poll() is None:
                guard()
                assert time.monotonic()-started < 600
                try:
                    child.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    pass
            assert child.returncode == 0
        finally:
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=20)
        assert list_files(folder) == files and snapshot(folder) == before
        amount_after = sum(allocated_bytes(p) for p in files)
        value = dict(folder=str(folder), files_verified=len(files), manifest=str(manifest),
            manifest_sha256=sha(manifest), allocated_before=amount_before, allocated_after=amount_after,
            recovered_bytes=amount_before-amount_after, all_logical_hashes_sizes_mtimes_preserved=True)
        atomic_json(OUT / f'{PREFIX}-{folder.name}-receipt.json', value)
        print(json.dumps(value), flush=True)
        return value
    with LOCK.open('x') as stream:
        stream.write(str(os.getpid()))
    try:
        guard()
        atomic_json(rp, dict(inputs=inputs, folders=[str(p) for p in folders], workers=2,
            maximum_seconds=1800, maximum_folder_seconds=600, no_deletion=True, no_relocation=True,
            note='Physical storage changes future I/O timings; logical evidence remains unchanged.', production_modified=False))
        with ThreadPoolExecutor(max_workers=2) as pool:
            records = list(pool.map(preserve, folders))
        for p, h in inputs.items():
            assert sha(p) == h, p
        guard()
        atomic_json(OUT / f'{PREFIX}-result.json', dict(passed=True, registration_sha256=sha(rp),
            records=records, recovered_bytes=sum(r['recovered_bytes'] for r in records),
            seconds=time.monotonic()-began, production_modified=False, deleted_files=0))
    except BaseException as error:
        atomic_json(OUT / f'{PREFIX}-failure.json', dict(passed=False, error=repr(error),
            seconds=time.monotonic()-began))
        raise
    finally:
        assert LOCK.read_text() == str(os.getpid())
        LOCK.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true')
    main(parser.parse_args().run)
