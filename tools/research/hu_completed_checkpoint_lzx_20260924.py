"""Compress one reviewed, completed S: checkpoint without changing its bytes."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
from hu_completed_evidence_compression_20260924 import digest, read, write
from ntfs_research_storage_v1 import allocated_bytes, attributes
from reboot_research_idle_v1 import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
OLD=ROOT/'research/preflop-evolution/ssd-storage-20260920'
ALLOWED={f'strategic-{weight}112-{iteration}-v1' for weight in ('weighted','equal')
         for iteration in (500,1000,1500,2000)}


def main(name):
    assert name in ALLOWED
    start=time.monotonic();psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    prefix='checkpoint-lzx-'+name
    source=(Path('S:/GTOpen-research/strategic-segments-v1')/name/'final').resolve()
    assert source.parent.name==name and source.is_dir()
    rp=OUT/(prefix+'-registration.json');status=OUT/(prefix+'-status.json')
    journal=OUT/prefix
    control=OUT/'checkpoint-lzx-storage-control-v1-result.json'
    assert read(control)['passed'] and read(control)['original_unchanged']
    # The earlier T: recovery must finish first; no overlapping compression jobs.
    recovery=OUT/'completed-evidence-compression-v1-result.json'
    finished=read(recovery);assert finished['passed'] and finished['state']=='complete'
    try:
        proc=psutil.Process(finished['controller_pid'])
        assert 'hu_completed_evidence_compression_20260924.py' not in ' '.join(proc.cmdline())
    except psutil.NoSuchProcess:pass
    review_path=OLD/(name+'-review.json');review=read(review_path)
    assert review['segment_passed'] and Path(review['snapshot']['path']).resolve()==source
    expected=review['snapshot']['files']
    assert set(expected)=={p.name for p in source.iterdir() if p.is_file()}
    assert all(Path(n).name==n and not (attributes(source/n)&0x400) for n in expected)
    before_files={n:dict(size=(source/n).stat().st_size,mtime_ns=(source/n).stat().st_mtime_ns)
                  for n in expected}
    assert sum(x['size'] for x in before_files.values())<70_000_000_000
    deps={str(p):digest(p) for p in [Path(__file__),review_path,control,recovery,
        ROOT/'tools/research/hu_completed_evidence_compression_20260924.py',
        ROOT/'tools/research/ntfs_research_storage_v1.py']}
    def guard():
        assert time.monotonic()-start<4*3600 and idle()
        assert shutil.disk_usage('S:/').free>40_000_000_000
    guard()
    if not rp.exists():
        journal.mkdir()
        write(rp,dict(source=str(source),files=before_files,expected_sha256=expected,
            dependencies=deps,algorithm='Windows transparent LZX',delete_allowed=False,
            production_modified=False))
    reg=read(rp)
    assert reg['files']==before_files and reg['expected_sha256']==expected and reg['dependencies']==deps
    compact=Path(os.environ['SystemRoot'])/'System32/compact.exe'
    before=after=0;count=0;error=None
    try:
        for number,n in enumerate(sorted(expected)):
            guard();p=source/n
            assert digest(p)==expected[n]
            bp=journal/f'{number:04d}-before.json';ap=journal/f'{number:04d}-after.json'
            if not bp.exists():write(bp,dict(name=n,sha256=expected[n],allocated=allocated_bytes(p)))
            b=read(bp);assert b['name']==n and b['sha256']==expected[n]
            if not ap.exists():
                if p.suffix=='.bin':
                    result=subprocess.run([str(compact),'/C','/EXE:LZX','/Q',str(p)],
                        capture_output=True,text=True,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
                    assert result.returncode==0,result.stdout+result.stderr
                assert digest(p)==expected[n] and p.stat().st_size==reg['files'][n]['size']
                assert p.stat().st_mtime_ns==reg['files'][n]['mtime_ns']
                write(ap,dict(name=n,sha256=expected[n],allocated=allocated_bytes(p)))
            a=read(ap);assert a['sha256']==expected[n] and a['allocated']==allocated_bytes(p)
            before+=b['allocated'];after+=a['allocated'];count+=1
            progress=dict(state='running',controller_pid=os.getpid(),files_verified=count,
                total_files=len(expected),allocated_before=before,allocated_after=after,
                saved_bytes=before-after,seconds=time.monotonic()-start,source=str(source),
                production_modified=False,deleted_files=0)
            write(status,progress)
            if count%16==0:print(json.dumps(progress),flush=True)
        assert set(expected)=={p.name for p in source.iterdir() if p.is_file()}
        for p,h in deps.items():assert digest(p)==h
        progress.update(state='complete',passed=True,registration_sha256=digest(rp))
        write(OUT/(prefix+'-result.json'),progress);write(status,progress)
        print(json.dumps(progress),flush=True)
    except BaseException as exc:
        write(status,dict(state='stopped',error=repr(exc),controller_pid=os.getpid(),
            files_verified=count,seconds=time.monotonic()-start,source=str(source),
            production_modified=False,deleted_files=0))
        raise


if __name__=='__main__':
    assert len(sys.argv)==3 and sys.argv[1]=='--checkpoint'
    main(sys.argv[2])
