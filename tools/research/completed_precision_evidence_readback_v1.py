"""Full fresh checksum readback of the two preserved precision evidence stores."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import time
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha
from ntfs_research_storage_v1 import allocated_bytes
from board_prefix_publication_v1 import atomic_json
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK, OTHER


def main():
    prefix = 'completed-precision-evidence-preservation-v1'
    rp, result_path = [OUT / f'{prefix}-{s}.json' for s in ('registration', 'result')]
    reg, result = read(rp), read(result_path)
    assert result['passed'] and result['registration_sha256'] == sha(rp)
    assert production_available() and not LOCK.exists() and not OTHER.exists()
    inputs = dict(reg['inputs'])
    inputs.update({str(p): sha(p) for p in (Path(__file__).resolve(), rp, result_path)})
    jobs = []
    for record in result['records']:
        manifest = Path(record['manifest'])
        assert sha(manifest) == record['manifest_sha256']
        inputs[str(manifest)] = sha(manifest)
        folder = Path(record['folder'])
        assert str(folder) in reg['folders']
        files = read(manifest)
        assert len(files) == record['files_verified']
        assert set(files) == {str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file()}
        for name, before in files.items():
            path = folder / name
            assert path.resolve() == path and path.is_relative_to(folder)
            jobs.append((path, before))
    for p, h in inputs.items():
        assert sha(p) == h, p
    review_reg = OUT / f'{prefix}-readback-registration.json'
    atomic_json(review_reg, dict(inputs=inputs, workers=4, files=len(jobs), maximum_seconds=1800))
    started = time.monotonic()
    def check(job):
        assert time.monotonic()-started < 1800
        path, before = job
        st = path.stat()
        assert st.st_nlink == 1 and not path.lstat().st_file_attributes & 0x400
        assert st.st_size == before['bytes'] and st.st_mtime_ns == before['mtime_ns']
        with path.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        assert digest == before['sha256']
        assert path.stat().st_size == st.st_size and path.stat().st_mtime_ns == st.st_mtime_ns
        return allocated_bytes(path)
    with ThreadPoolExecutor(max_workers=4) as pool:
        amounts = list(pool.map(check, jobs))
    assert sum(amounts) == sum(r['allocated_after'] for r in result['records'])
    assert result['recovered_bytes'] == sum(r['allocated_before'] for r in result['records'])-sum(amounts)
    for p, h in inputs.items():
        assert sha(p) == h, p
    assert production_available() and not LOCK.exists() and not OTHER.exists()
    value = dict(passed=True, source_result_sha256=sha(result_path), source_registration_sha256=sha(rp),
        readback_registration_sha256=sha(review_reg), files=len(jobs), recovered_bytes=result['recovered_bytes'],
        seconds=time.monotonic()-started, production_modified=False, deleted_files=0)
    atomic_json(OUT / f'{prefix}-independent-review.json', value)
    print(json.dumps(value), flush=True)


if __name__ == '__main__':
    main()
