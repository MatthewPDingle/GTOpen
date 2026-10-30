"""Reopen every preserved historical seed file; no compression or model fitting."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import time
import psutil
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha
from board_prefix_publication_v1 import atomic_json
from ntfs_research_storage_v1 import allocated_bytes,attributes

PREFIX='completed-seed-checkpoint-preservation-v1'


def main():
    began=time.monotonic();psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    assert psutil.cpu_percent(interval=1)<50 and psutil.virtual_memory().available>20_000_000_000
    rp=OUT/f'{PREFIX}-registration.json';result_path=OUT/f'{PREFIX}-result.json'
    reg=read(rp);result=read(result_path)
    assert result['passed'] and result['registration_sha256']==sha(rp)
    source=Path(reg['source'])
    assert source==Path('S:/GTOpen-research/strategic-weighted112-seed-v1/iteration-20')
    assert result['source']==str(source)
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    expected=read(ROOT/'research/preflop-evolution/ssd-storage-20260920/strategic-weighted112-seed-v1-review.json')['snapshot']
    assert expected['path']==str(source) and len(expected['files'])==len(reg['records'])==227
    assert set(expected['files'])=={p.name for p in source.iterdir()}
    assert {r['name']:r['sha256'] for r in reg['records']}==expected['files']
    by_name={r['name']:r for r in result['records']};assert len(by_name)==227
    before={str(p):sha(p) for p in (Path(__file__).resolve(),rp,result_path)}
    def verify(record):
        name=record['name'];assert Path(name).name==name
        path=source/name;assert path.resolve()==path and path.is_file()
        for parent in (path,*path.parents):assert not attributes(parent)&0x400
        first=path.stat();assert first.st_size==record['bytes'] and first.st_mtime_ns==record['mtime_ns']
        digest=hashlib.sha256()
        with path.open('rb') as stream:
            while block:=stream.read(8*1024*1024):digest.update(block)
        last=path.stat();assert first.st_size==last.st_size and first.st_mtime_ns==last.st_mtime_ns
        assert digest.hexdigest()==record['sha256']==expected['files'][name]
        allocation=allocated_bytes(path)
        row=by_name[name]
        assert row['sha256']==record['sha256'] and row['allocated_before']==record['allocated_before']
        assert allocation==row['allocated_after']
        journal=read(OUT/PREFIX/(name+'.json'));assert journal==row
        return allocation
    with ThreadPoolExecutor(max_workers=4) as pool:allocation=sum(pool.map(verify,reg['records']))
    assert allocation==result['allocated_after']
    assert sum(r['bytes'] for r in reg['records'])==result['logical_bytes']==expected['bytes']
    assert sum(r['allocated_before'] for r in reg['records'])==result['allocated_before']
    assert result['allocated_before']-allocation==result['recovered_bytes']
    for p,h in before.items():assert sha(p)==h,p
    assert time.monotonic()-began<600
    review=dict(passed=True,inputs=before,source_registration_sha256=sha(rp),source_result_sha256=sha(result_path),
        files_verified=227,logical_bytes=result['logical_bytes'],allocated_bytes=allocation,
        recovered_bytes=result['recovered_bytes'],seconds=time.monotonic()-began,workers=4,
        every_historical_hash_size_mtime_and_journal_verified=True,gpu_used=False,
        compression_performed=False,native_restore_repeated=False,production_modified=False)
    atomic_json(OUT/f'{PREFIX}-independent-review.json',review)
    print(json.dumps(review),flush=True)


if __name__=='__main__':main()
