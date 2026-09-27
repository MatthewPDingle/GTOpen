"""Fresh full-file hash/metadata readback; does not call the compression verifier."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import time
import psutil
from sampled_physical_root_evaluation_v1 import sha, save
from later_average_support_v1 import OUT, read
from ntfs_research_storage_v1 import allocated_bytes, attributes, COMPRESSED
from bounded_parallel_evaluation_archive_v2 import production_available

PREFIX='completed-raw-json-preservation-v1'


def main(control=False):
    began=time.monotonic(); prefix=PREFIX+('-control' if control else '')
    rp=OUT/f'{prefix}-registration.json'; result_path=OUT/f'{prefix}-result.json'
    result=read(result_path); reg=read(rp)
    assert result['passed'] and result['registration_sha256']==sha(rp) and result['control']==control
    assert reg['no_deletions'] and reg['no_relocations'] and reg['byte_preserving']
    assert production_available() and psutil.virtual_memory().available>20_000_000_000
    inputs={str(p):sha(p) for p in [Path(__file__).resolve(),rp,result_path]}
    for p,h in reg['inputs'].items(): assert sha(p)==h,p
    inputs.update(reg['inputs'])
    allocated={}
    for path,digest in result['journals'].items():
        assert sha(path)==digest; inputs[path]=digest
        for row in read(path):
            assert row['path'] not in allocated
            allocated[row['path']]=row
    records=reg['records']; assert len(records)==len(allocated)==result['files']
    assert {r['path'] for r in records}==set(allocated)
    regpath=OUT/f'{prefix}-readback-registration.json'; assert not regpath.exists()
    save(regpath,dict(inputs=inputs,files=len(records),workers=4,maximum_seconds=1800,
        scope='Independent full logical-file hashes, lengths, modification times and physical allocations.',production_modified=False))
    def check(record):
        assert time.monotonic()-began<1800 and psutil.virtual_memory().available>20_000_000_000
        p=Path(record['path']); before=p.stat()
        with p.open('rb') as stream: h=hashlib.file_digest(stream,'sha256').hexdigest()
        after=p.stat(); assert before.st_size==after.st_size==record['bytes']
        assert before.st_mtime_ns==after.st_mtime_ns==record['mtime_ns']
        assert h==record['sha256']==allocated[str(p)]['sha256']
        assert attributes(p)&COMPRESSED and not attributes(p)&0x400
        actual=allocated_bytes(p); assert actual==allocated[str(p)]['allocated_after']
        assert record['allocated_before']==allocated[str(p)]['allocated_before']
        return actual
    try:
        with ThreadPoolExecutor(max_workers=4) as pool: amounts=list(pool.map(check,records))
        assert sum(amounts)==result['allocated_after']
        assert sum(r['bytes'] for r in records)==result['logical_bytes']
        assert sum(r['allocated_before'] for r in records)-sum(amounts)==result['saved_bytes']
        for p,h in inputs.items(): assert sha(p)==h,p
        assert production_available()
        value=dict(passed=True,source_result_sha256=sha(result_path),source_registration_sha256=sha(rp),
            readback_registration_sha256=sha(regpath),files=len(records),saved_bytes=result['saved_bytes'],
            logical_bytes=result['logical_bytes'],workers=4,seconds=time.monotonic()-began,
            production_modified=False,deleted_files=0,relocated_files=0)
        save(OUT/f'{prefix}-independent-review.json',value); print(json.dumps(value),flush=True)
    except BaseException as exc:
        save(OUT/f'{prefix}-readback-failure.json',dict(passed=False,error=repr(exc),
            readback_registration_sha256=sha(regpath)))
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--control',action='store_true')
    main(parser.parse_args().control)
