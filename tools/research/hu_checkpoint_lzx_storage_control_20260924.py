"""Storage-only LZX roundtrip on one copied, immutable binary record."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import psutil
from ntfs_research_storage_v1 import allocated_bytes, attributes
from reboot_research_idle_v1 import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='checkpoint-lzx-storage-control-v1'
STORE=Path('T:/GTOpen-research')/PREFIX


def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def save(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())


def main():
    start=time.monotonic();psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    assert idle() and shutil.disk_usage('T:/').free>40_000_000_000 and not STORE.exists()
    source=Path('S:/GTOpen-research/strategic-segments-v1/strategic-weighted112-2000-v1/final/entry-111-generation-0.bin')
    previous=OUT/'checkpoint-ntfs-storage-control-v1-registration.json'
    p=json.loads(previous.read_bytes());h=sha(source)
    assert h==p['source_sha256'] and source.stat().st_mtime_ns==p['source_mtime_ns']
    reg=OUT/(PREFIX+'-registration.json')
    save(reg,dict(source=str(source),source_sha256=h,logical_bytes=source.stat().st_size,
        source_mtime_ns=source.stat().st_mtime_ns,previous_registration_sha256=sha(previous),
        script_sha256=sha(Path(__file__)),store=str(STORE),production_modified=False,
        scope='Copy one completed binary checkpoint record; LZX compress, hash, decompress and hash. No original mutation or native checkpoint restore.'))
    STORE.mkdir();dest=STORE/source.name;shutil.copyfile(source,dest)
    original_alloc=allocated_bytes(source);assert sha(dest)==h
    compact=Path(os.environ['SystemRoot'])/'System32/compact.exe'
    results={}
    for label,args in [('compressed',['/C','/EXE:LZX']),('restored',['/U','/EXE'])]:
        assert idle();began=time.monotonic()
        call=subprocess.run([str(compact),*args,'/Q',str(dest)],capture_output=True,text=True,
                            timeout=300,creationflags=subprocess.CREATE_NO_WINDOW)
        assert call.returncode==0,call.stdout+call.stderr
        assert sha(dest)==h and dest.stat().st_size==p['source_logical_bytes']
        results[label]=dict(allocated_file_bytes=allocated_bytes(dest),attributes=attributes(dest),
            sha256=h,seconds=time.monotonic()-began,compact_output=call.stdout)
    assert results['compressed']['allocated_file_bytes']<p['source_logical_bytes']
    assert results['restored']['allocated_file_bytes']==p['source_logical_bytes']
    assert sha(source)==h and allocated_bytes(source)==original_alloc
    assert source.stat().st_mtime_ns==p['source_mtime_ns']
    # Retain the verified fixture in its smaller representation.
    call=subprocess.run([str(compact),'/C','/EXE:LZX','/Q',str(dest)],capture_output=True,
        text=True,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW)
    assert call.returncode==0 and sha(dest)==h
    save(OUT/(PREFIX+'-result.json'),dict(passed=True,registration_sha256=sha(reg),
        results=results,final_allocated_file_bytes=allocated_bytes(dest),seconds=time.monotonic()-start,
        original_unchanged=True,gpu_used=False,production_modified=False,
        limitation='Single binary record, reversible logical byte preservation only; not collection-wide savings or a native restore benchmark.'))
    print(json.dumps(results),flush=True)


if __name__=='__main__':main()
