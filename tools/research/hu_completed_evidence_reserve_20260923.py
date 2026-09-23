"""Reclaim storage losslessly from explicitly completed, audited old studies.

May run beside a new study; never touches its output, checkpoints or sources.
"""
import os
import shutil
import subprocess
import time
from pathlib import Path
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha, save
from hu_completed_evidence_ntfs_compression_20260923 import snapshot
from compressed_research_store_v1 import inventory

PREFIX = 'completed-evidence-reserve-v1'
NAMES = (
    'sampled-physical-root-study-gpu-v1',
    'sampled-physical-dense-evaluation-v1',
    'sampled-physical-allin-evaluation-v2',
    'sampled-physical-hybrid-evaluation-v2',
    'sampled-visible-hybrid-completion-pilot-v1',
    'sampled-physical-hybrid-allin-pilot-v1',
    'sampled-physical-allin-pilot-v1',
    'sampled-physical-hybrid-pilot-v1',
    'sampled-physical-dense-pilot-v1',
)


def main():
    started = time.monotonic()
    inputs = {str(Path(__file__).resolve()): sha(Path(__file__))}
    folders = []
    for name in NAMES:
        paths = [OUT / f'{name}-{suffix}.json'
                 for suffix in ('registration', 'result', 'independent-review', 'status')]
        registration, result, audit, status = map(read, paths)
        assert status['state'] == 'complete' and result['terminal'] and audit['passed']
        assert audit.get('registration_sha256', audit.get('source_registration_sha256')) == sha(paths[0])
        if 'result_sha256' in audit:
            assert audit['result_sha256'] == sha(paths[1])
        else:
            assert audit['terminal_complete']
            assert audit['evidence_hashes'][str(paths[1])] == sha(paths[1])
        folder = Path(registration['store']).resolve()
        assert folder == Path('S:/GTOpen-research', name).resolve()
        assert folder.is_dir() and not folder.is_symlink()
        folders.append(folder)
        inputs.update({str(p): sha(p) for p in paths})
    rp = OUT / f'{PREFIX}-registration.json'
    save(rp, dict(inputs=inputs, folders=list(map(str, folders)),
        operation='Lossless NTFS compression of completed audited stores; preserve every decoded byte, path, size and last-write time. No deletes or relocation.',
        maximum_seconds=1800, production_modified=False, active_study_modified=False))
    records = []
    error = None
    try:
        for index, folder in enumerate(folders):
            assert time.monotonic() - started < 1800
            before = snapshot(folder)
            manifest = OUT / f'{PREFIX}-{index}-manifest.json'
            save(manifest, before)
            free_before = shutil.disk_usage(folder).free
            with (OUT / f'{PREFIX}-{index}.log').open('x') as stream:
                result = subprocess.run(['compact.exe', '/C', f'/S:{folder}', '/Q'],
                    stdout=stream, stderr=subprocess.STDOUT, timeout=600,
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            assert result.returncode == 0
            after = snapshot(folder)
            assert before == after
            disk = inventory(folder, lambda: None)
            record = dict(folder=str(folder), files_verified=len(before),
                manifest_sha256=sha(manifest), all_bytes_sizes_paths_mtimes_unchanged=True,
                logical_bytes=disk['logical_bytes'], allocated_bytes=disk['allocated_bytes'],
                free_before=free_before, free_after=shutil.disk_usage(folder).free,
                free_space_caveat='Concurrent evaluation writes affect volume-wide free space.')
            records.append(record)
            print(record, flush=True)
        for p, h in inputs.items():
            assert sha(p) == h
        save(OUT / f'{PREFIX}-result.json', dict(passed=True, registration_sha256=sha(rp),
            records=records, seconds=time.monotonic()-started,
            production_modified=False, active_study_modified=False))
    except BaseException as exc:
        error = repr(exc)
        raise
    finally:
        save(OUT / f'{PREFIX}-status.json', dict(state='stopped' if error else 'complete',
            error=error, records=records, seconds=time.monotonic()-started))


if __name__ == '__main__':
    main()
