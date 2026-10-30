"""Lossless transparent LZX preservation of one completed historical checkpoint.

Exact folder and historical hashes only; no deletion, relocation, retraining,
new checkpoint format or mutation of model content. Four bounded CPU/I/O workers.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading
import time
import psutil
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha
from ntfs_research_storage_v1 import allocated_bytes,attributes
from board_prefix_publication_v1 import atomic_json
from bounded_parallel_evaluation_archive_v2 import production_available

PREFIX='completed-seed-checkpoint-preservation-v1'
OWNER='strategic-weighted112-seed-v1'
SOURCE=Path('S:/GTOpen-research')/OWNER/'iteration-20'
OLD=ROOT/'research/preflop-evolution/ssd-storage-20260920'
COMPACT=Path(os.environ['SystemRoot'])/'System32/compact.exe'
ACTIVE=('weighted-complete-evaluation-study-v1','weighted-complete-evaluation-queue-v1',
        'board-training-pipeline-queue-v2','board-prefix-followup-queue-v1')
REG=OUT/f'{PREFIX}-registration.json'


def safe_path(name):
    assert isinstance(name,str) and Path(name).name==name
    assert name in ('complete','index.json','preflop.bin') or (
        name.startswith('entry-') and name.endswith('-generation-0.bin') and name[6:-17].isdigit())
    path=SOURCE/name
    assert path.is_absolute() and path.resolve()==path and path.parent==SOURCE and path.is_file()
    for item in (path,*path.parents):assert not attributes(item)&0x400,str(item)
    return path


def own_compactor(info):
    command=info['cmdline'] or []
    return (info['ppid']==os.getpid() and len(command)==5
        and os.path.normcase(command[0])==os.path.normcase(str(COMPACT))
        and command[1:4]==['/C','/EXE:LZX','/Q'] and Path(command[4]).parent==SOURCE)


def owners_idle():
    for p in psutil.process_iter(['pid','ppid','cmdline']):
        if p.pid==os.getpid() or own_compactor(p.info):continue
        command=' '.join(p.info['cmdline'] or []).lower()
        assert OWNER.lower() not in command and 'storage_strategic_seed_' not in command,'Historical owner active'
        assert 'storage_strategic_segment_' not in command,'Historical checkpoint worker active'


def qualifications():
    review_path=OLD/f'{OWNER}-review.json';status_path=OLD/f'{OWNER}-status.json'
    snapshot_path=OLD/f'{OWNER}-snapshot.json'
    review=read(review_path);status=read(status_path);snapshot=read(snapshot_path)
    assert review['seed_and_fresh_restore_passed'] and review['restored_scientific_checkpoint_exact']
    assert review['iterations']==20 and review['boards']==112 and Path(review['snapshot']['path'])==SOURCE
    assert status['step']=='complete-seed-and-restore-qualified'
    assert snapshot==review['snapshot']
    expected=snapshot['files'];assert len(expected)==227
    assert set(expected)=={p.name for p in SOURCE.iterdir()}
    paths=[Path(__file__).resolve(),review_path,status_path,snapshot_path,
        OUT/'checkpoint-lzx-storage-control-v1-registration.json',OUT/'checkpoint-lzx-storage-control-v1-result.json',
        OUT/'completed-checkpoint-storage-queue-v1-registration.json',OUT/'completed-checkpoint-storage-queue-v1-result.json',
        ROOT/'tools/research/ntfs_research_storage_v1.py',ROOT/'tools/research/board_prefix_publication_v1.py']
    control=read(paths[5]);assert control['passed'] and control['original_unchanged']
    assert control['registration_sha256']==sha(paths[4])
    earlier=read(paths[7]);assert earlier['passed'] and earlier['state']=='complete'
    assert earlier['registration_sha256']==sha(paths[6]) and earlier['deleted_files']==0
    for operation,digest in review['result_sha256'].items():
        p=OLD/f'{OWNER}-{operation}-result.json';assert sha(p)==digest;paths.append(p)
    blocked=set()
    for prefix in ACTIVE:
        p=OUT/f'{prefix}-registration.json';paths.append(p)
        blocked.update(os.path.normcase(str(Path(name).resolve())) for name in read(p)['inputs'])
    records=[]
    for name,digest in sorted(expected.items()):
        p=safe_path(name);s=p.stat();assert os.path.normcase(str(p)) not in blocked
        records.append(dict(name=name,sha256=digest,bytes=s.st_size,mtime_ns=s.st_mtime_ns,
            allocated_before=allocated_bytes(p)))
    assert sum(r['bytes'] for r in records)==snapshot['bytes']<70_000_000_000
    return records,{str(p):sha(p) for p in paths}


def verify(record):
    path=safe_path(record['name']);before=path.stat()
    assert before.st_size==record['bytes'] and before.st_mtime_ns==record['mtime_ns']
    with path.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
    after=path.stat()
    assert digest==record['sha256'] and after.st_size==before.st_size and after.st_mtime_ns==before.st_mtime_ns
    return path


def main(run=False):
    records,inputs=qualifications();owners_idle()
    assert production_available() and psutil.virtual_memory().available>24_000_000_000
    assert psutil.disk_usage('S:/').free>40_000_000_000
    if not run:
        print(json.dumps(dict(ready=True,source=str(SOURCE),files=len(records),
            logical_bytes=sum(r['bytes'] for r in records),allocated_bytes=sum(r['allocated_before'] for r in records),
            registered_active_inputs_excluded=True,compression_started=False)))
        return
    assert psutil.cpu_percent(interval=1)<30
    assert not REG.exists() and not (OUT/f'{PREFIX}-result.json').exists()
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    atomic_json(REG,dict(inputs=inputs,source=str(SOURCE),records=records,workers=4,
        maximum_seconds=2400,maximum_compact_seconds=180,algorithm='Windows transparent LZX',
        production_modified=False,no_deletion=True,original_paths_preserved=True,
        historical_restore_already_qualified=True,native_restore_repeated=False))
    journal=OUT/PREFIX;journal.mkdir();began=time.monotonic();stop=threading.Event();completed=[]
    probe_lock=threading.Lock();last_probe=[0.]
    def guard():
        assert not stop.is_set() and time.monotonic()-began<2400
        with probe_lock:
            now=time.monotonic()
            if now-last_probe[0]>5:
                assert production_available() and psutil.virtual_memory().available>20_000_000_000
                assert psutil.disk_usage('S:/').free>40_000_000_000
                owners_idle();last_probe[0]=now
    def compress(record):
        guard();path=verify(record)
        if path.suffix=='.bin':
            child=subprocess.Popen([str(COMPACT),'/C','/EXE:LZX','/Q',str(path)],
                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            began_file=time.monotonic()
            try:
                while child.poll() is None:
                    guard();assert time.monotonic()-began_file<180
                    try:child.wait(timeout=1)
                    except subprocess.TimeoutExpired:pass
                assert child.returncode==0,'Compression failed: '+str(path)
            finally:
                if child.poll() is None:child.terminate();child.wait(timeout=20)
        verify(record)
        result=dict(name=record['name'],sha256=record['sha256'],allocated_before=record['allocated_before'],
            allocated_after=allocated_bytes(path))
        atomic_json(journal/(record['name']+'.json'),result)
        return result
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            pending=[pool.submit(compress,r) for r in records]
            try:
                for future in as_completed(pending):
                    completed.append(future.result())
                    if len(completed)%16==0:
                        print(json.dumps(dict(files_verified=len(completed),total_files=len(records),
                            recovered_bytes=sum(r['allocated_before']-r['allocated_after'] for r in completed),
                            seconds=time.monotonic()-began)),flush=True)
            except BaseException:stop.set();raise
        assert set(r['name'] for r in records)=={p.name for p in SOURCE.iterdir()}
        for p,h in inputs.items():assert sha(p)==h,p
        owners_idle()
        result=dict(passed=True,registration_sha256=sha(REG),source=str(SOURCE),files_verified=len(completed),
            logical_bytes=sum(r['bytes'] for r in records),allocated_before=sum(r['allocated_before'] for r in records),
            allocated_after=sum(r['allocated_after'] for r in completed),
            recovered_bytes=sum(r['allocated_before']-r['allocated_after'] for r in completed),
            records=sorted(completed,key=lambda r:r['name']),seconds=time.monotonic()-began,
            independent_readback_required=True,gpu_used=False,production_modified=False,
            no_deletion=True,all_logical_hashes_sizes_mtimes_preserved=True,native_restore_repeated=False)
        atomic_json(OUT/f'{PREFIX}-result.json',result)
        print(json.dumps({k:v for k,v in result.items() if k!='records'}),flush=True)
    except BaseException as exc:
        atomic_json(OUT/f'{PREFIX}-failure.json',dict(passed=False,error=repr(exc),registration_sha256=sha(REG),
            files_verified=len(completed),seconds=time.monotonic()-began,production_modified=False))
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true')
    main(parser.parse_args().run)
