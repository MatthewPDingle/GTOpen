"""Independently read every preserved byte after wide replay compression."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha
from board_prefix_publication_v1 import atomic_json
from ntfs_research_storage_v1 import allocated_bytes
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK, OTHER


def main():
    prefix = 'completed-wide-maturity-preservation-v1'
    rp, result_path = [OUT / f'{prefix}-{s}.json' for s in ('registration', 'result')]
    reg, result = read(rp), read(result_path)
    assert result['passed'] and result['registration_sha256'] == sha(rp)
    assert reg['no_deletion'] and reg['original_paths_preserved'] and result['all_logical_hashes_sizes_mtimes_preserved']
    assert not LOCK.exists() and not OTHER.exists() and production_available()
    source = Path('S:/GTOpen-research/hu-wide-maturity-v1')
    assert Path(reg['source']) == source
    expected = read(OUT / 'wide-maturity-v1-review.json')['snapshots']
    by_name = {r['name']: r for r in result['records']}
    assert len(by_name) == len(reg['records']) == len(expected) == result['files_verified'] == 4
    assert {source / n for n in by_name} == {Path(p) for p in expected} == set(source.glob('*.bin'))
    inputs = {str(p): sha(p) for p in (Path(__file__).resolve(), rp, result_path)}
    inputs.update(reg['inputs'])
    for p, h in inputs.items():
        assert sha(p) == h, p
    readback_reg = OUT / f'{prefix}-readback-registration.json'
    assert not readback_reg.exists()
    atomic_json(readback_reg, dict(inputs=inputs, workers=4, maximum_seconds=1800,
        scope='All original logical hashes, sizes, modification times, paths, file identities and allocated bytes.',
        native_restore_repeated=False, production_modified=False))
    began = time.monotonic()
    def check(record):
        assert time.monotonic()-began < 1800 and psutil.virtual_memory().available > 20_000_000_000
        path = source / record['name']
        assert path.resolve() == path and path.is_relative_to(source)
        before = path.stat()
        assert before.st_nlink == 1 and not path.lstat().st_file_attributes & 0x400
        with path.open('rb') as stream:
            actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        after = path.stat()
        assert before.st_size == after.st_size == record['bytes']
        assert before.st_mtime_ns == after.st_mtime_ns == record['mtime_ns']
        assert actual == record['sha256'] == expected[str(path)] == by_name[record['name']]['sha256']
        amount = allocated_bytes(path)
        assert amount == by_name[record['name']]['allocated_after']
        assert record['allocated_before'] == by_name[record['name']]['allocated_before']
        return amount
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            amounts = list(pool.map(check, reg['records']))
        recovered = sum(r['allocated_before'] for r in reg['records']) - sum(amounts)
        assert recovered == result['recovered_bytes']
        for p, h in inputs.items():
            assert sha(p) == h, p
        assert production_available() and not LOCK.exists() and not OTHER.exists()
        value = dict(passed=True, source_registration_sha256=sha(rp), source_result_sha256=sha(result_path),
            readback_registration_sha256=sha(readback_reg), files=4, logical_bytes=13_761_477_472,
            allocated_bytes=sum(amounts), recovered_bytes=recovered, seconds=time.monotonic()-began,
            native_restore_repeated=False, production_modified=False, deleted_files=0)
        atomic_json(OUT / f'{prefix}-independent-review.json', value)
        print(json.dumps(value), flush=True)
    except BaseException as error:
        atomic_json(OUT / f'{prefix}-readback-failure.json', dict(passed=False,
            error=repr(error), readback_registration_sha256=sha(readback_reg)))
        raise


if __name__ == '__main__':
    main()
