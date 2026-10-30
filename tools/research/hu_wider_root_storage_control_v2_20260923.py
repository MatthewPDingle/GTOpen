"""Copy completed control into newly compressed output and verify all bytes."""
from pathlib import Path
import shutil
import os
import time
import psutil
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from reboot_research_idle_v1 import idle
from compressed_research_store_v1 import create_parent,inventory,compressed
from wider_root_readback_v1 import review

PREFIX='wider-root-storage-control-v2'
STORE=Path('S:/GTOpen-research')/PREFIX


def main():
    start=time.monotonic();last_idle=[0.]
    def guard():
        assert time.monotonic()-start<300 and psutil.virtual_memory().available>20_000_000_000
        assert shutil.disk_usage(STORE.parent).free>40_000_000_000
        if time.monotonic()-last_idle[0]>2:
            assert idle();last_idle[0]=time.monotonic()
    guard();rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists() and not STORE.exists()
    oldrp=OUT/'wider-root-evaluation-control-v1-registration.json'
    oldpp=OUT/'wider-root-evaluation-control-v1-result.json'
    oldap=OUT/'wider-root-readback-control-v1-result.json'
    reg,outer,audit=[read(p) for p in (oldrp,oldpp,oldap)]
    assert outer['passed'] and outer['registration_sha256']==sha(oldrp) and audit['passed']
    src=Path(reg['store']);assert src==Path('S:/GTOpen-research/wider-root-evaluation-control-v1')
    assert sha(src/'result.json')==outer['result_sha256']
    paths=[Path(__file__),ROOT/'tools/research/hu_wider_root_storage_control_20260923.py',
        OUT/'wider-root-storage-control-v1-registration.json',ROOT/'tools/research/compressed_research_store_v1.py',
        ROOT/'tools/research/wider_root_readback_v1.py',oldrp,oldpp,oldap]
    inputs=dict(reg['inputs']);inputs.update({str(p):sha(p) for p in paths})
    for p,h in inputs.items():assert sha(p)==h,p
    save(rp,dict(inputs=inputs,source=str(src),store=str(STORE),maximum_seconds=300,
        planned_deals=174336,source_deals=466,planning_multiplier=1.5,reserve_bytes=40_000_000_000,
        operation='Copy completed evidence into a new NTFS-compressed directory; verify every decoded byte and run scalar readback. No original or active file is changed.',
        gpu_used=False,production_modified=False))
    before={}
    for p in sorted(src.rglob('*')):
        guard();assert not p.is_symlink()
        if p.is_file():before[str(p.relative_to(src))]=dict(sha256=sha(p),bytes=p.stat().st_size,mtime_ns=p.stat().st_mtime_ns)
    STORE.mkdir();log=create_parent(STORE/'compressed',guard)
    (OUT/f'{PREFIX}-compact.log').write_text(log,newline='\n')
    dest=STORE/'compressed'/'evaluation';dest.mkdir();assert compressed(dest)
    copy_start=time.monotonic()
    for name,info in before.items():
        guard();p=dest/name;p.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src/name,p)
        # NTFS may defer compression of cached writes. Flush each completed copy
        # before measuring physical allocation; do not infer failure from a
        # just-closed file's transient allocation.
        with p.open('r+b') as flushed:os.fsync(flushed.fileno())
        os.utime(p,ns=((src/name).stat().st_atime_ns,info['mtime_ns']))
    copy_seconds=time.monotonic()-copy_start
    stats=inventory(dest,guard)
    assert {x['path'] for x in stats['files']}==set(before)
    assert stats['compressed_files']==len(before) and stats['allocated_bytes']<stats['logical_bytes']
    for name,info in before.items():
        guard()
        for p in (src/name,dest/name):assert sha(p)==info['sha256'] and p.stat().st_size==info['bytes'] and p.stat().st_mtime_ns==info['mtime_ns']
    scalar=review(OUT/'bb-context-candidate.json',dest,reg['config'],reg['exact'],reg['cache_sha256'],guard)
    save(OUT/f'{PREFIX}-manifest.json',dict(source_files=before,copy_inventory=stats))
    free=shutil.disk_usage(STORE).free;projected=stats['allocated_bytes']*174336/466*1.5
    for p,h in inputs.items():assert sha(p)==h,p
    guard()
    result=dict(passed=True,registration_sha256=sha(rp),files_verified=len(before),
        logical_bytes=stats['logical_bytes'],allocated_bytes=stats['allocated_bytes'],
        allocated_to_logical_ratio=stats['allocated_bytes']/stats['logical_bytes'],
        copy_seconds=copy_seconds,seconds=time.monotonic()-start,scalar_readback=scalar,
        drive_free_bytes=free,rough_projected_bytes_with_50pct_margin=projected,
        estimate_fits_reserve=projected+40_000_000_000<free,
        source_unchanged=True,active_study_modified=False,production_modified=False,gpu_used=False,
        limitation='Four-model artifact storage control, not a guaranteed bound for a 78-model run. Candidate-specific admission and ongoing physical free-space guards remain required.')
    save(OUT/f'{PREFIX}-result.json',result);print(result)


if __name__=='__main__':main()
