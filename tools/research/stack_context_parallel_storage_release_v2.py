"""Lossless compression of completed checkpoint test files; no deletion or retraining."""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json,time,traceback,shutil
import psutil
from completed_flop_fixture_compression_20260927 import compress
from hu_completed_evidence_compression_20260924 import digest,read,write
from ntfs_research_storage_v1 import attributes,allocated_bytes
from bounded_parallel_evaluation_archive_v2 import production_available
from hu_paired_continuation_support_20260925 import LOCK,OTHER

ROOT=Path('T:/Dev/GTOpen')
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
OLD=ROOT/'research/preflop-evolution/ssd-storage-20260920'
from hu_completed_evidence_reserve_20260923 import NAMES
SOURCES=tuple(Path('S:/GTOpen-research')/name for name in NAMES)
NAME='stack-context-parallel-storage-release-v2'
TARGET=6_000_000_000

def save(path,value):
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,sort_keys=True);f.write('\n')

def safe(path):
    assert path.is_absolute() and path.resolve()==path and any(path.is_relative_to(root) for root in SOURCES)
    for p in (path,*path.parents):assert not attributes(p)&0x400,str(p)
    assert path.is_file() and not attributes(path)&0x200,str(path)

def main():
    attempt,result,failure,status=(OUT/(NAME+s+'.json') for s in ('-attempt','-result','-failure','-status'))
    assert not any(p.exists() for p in (attempt,result,failure,status))
    assert not LOCK.exists() and not OTHER.exists() and not (OLD/'running.lock').exists()
    oldstatus=read(OLD/'checkpoint-long-v1-status.json');review=read(OLD/'checkpoint-long-v1-review.json')
    assert oldstatus['step']=='complete-fresh-process-resume-qualified' and review['passed']
    assert review['all_scientific_checkpoints_exact']
    completed_proofs=[]
    for name,folder in zip(NAMES,SOURCES):
        paths=[OUT/(name+'-'+suffix+'.json') for suffix in ('registration','result','independent-review','status')]
        reg,res,audit,st=map(read,paths)
        assert st['state']=='complete' and res['terminal'] and audit['passed']
        assert audit.get('registration_sha256',audit.get('source_registration_sha256'))==digest(paths[0])
        if 'result_sha256' in audit:assert audit['result_sha256']==digest(paths[1])
        else:assert audit['terminal_complete'] and audit['evidence_hashes'][str(paths[1])]==digest(paths[1])
        assert Path(reg['store']).resolve()==folder.resolve() and folder.is_dir()
        completed_proofs.extend(paths)
    assert not psutil.pid_exists(31052) and not psutil.pid_exists(99304)
    for p in psutil.process_iter(['pid','cmdline']):
        if p.pid==os.getpid():continue
        command=' '.join(p.info['cmdline'] or [])
        assert not any(s in command for s in ('storage_checkpoint_long_20260920.py','stack_context_parallel_continuation_v2.py --run','stack_context_matched_learning_v1.py --run')),command
    assert production_available() and shutil.disk_usage('S:/').free>40_000_000_000
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    inputs={str(p):digest(p) for p in (Path(__file__).resolve(),OLD/'checkpoint-long-v1-status.json',OLD/'checkpoint-long-v1-review.json',
        ROOT/'tools/research/completed_flop_fixture_compression_20260927.py',ROOT/'tools/research/hu_completed_evidence_compression_20260924.py',
        OUT/'completed-flop-fixture-compression-v1-control-result.json',OUT/'stack-context-parallel-admission-v2-failure.json',
        OUT/'stack-context-parallel-continuation-v2-check-result.json',OUT/'stack-context-parallel-storage-candidates-v1.json')}
    inputs.update({str(p):digest(p) for p in completed_proofs})
    inputs[str(ROOT/'tools/research/hu_completed_evidence_reserve_20260923.py')]=digest(ROOT/'tools/research/hu_completed_evidence_reserve_20260923.py')
    inputs[str(OUT/'stack-context-parallel-storage-release-v1-failure.json')]=digest(OUT/'stack-context-parallel-storage-release-v1-failure.json')
    gate=read(OUT/'completed-flop-fixture-compression-v1-control-result.json')
    assert gate['passed'] and gate['source_sha256']==digest(ROOT/'tools/research/completed_flop_fixture_compression_20260927.py')
    candidates=[]
    for p in (p for root in SOURCES for p in root.rglob('*')):
        assert not attributes(p)&0x400,str(p)
        if not p.is_file():continue
        s=p.stat()
        if s.st_size<1_000_000 or s.st_file_attributes&0xa00:continue
        safe(p);candidates.append(dict(path=str(p),bytes=s.st_size,mtime_ns=s.st_mtime_ns,allocated=allocated_bytes(p)))
    candidates.sort(key=lambda r:(-r['allocated'],r['path']))
    assert candidates and sum(r['allocated'] for r in candidates)<60_000_000_000
    save(attempt,dict(inputs=inputs,candidates=candidates,maximum_seconds=1800,target_saved_bytes=TARGET,workers=4,
        preserve_paths_bytes_sizes_mtimes=True,deletes_allowed=False,active_study_modified=False,production_modified=False))
    started=time.monotonic();rows=[];error=None
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    def guard():
        assert time.monotonic()-started<1800
        assert LOCK.read_text().strip()==str(os.getpid()) and not OTHER.exists()
        assert production_available() and shutil.disk_usage('S:/').free>40_000_000_000 and psutil.virtual_memory().available>24_000_000_000
    def work(record):
        guard();p=Path(record['path']);safe(p)
        assert p.stat().st_size==record['bytes'] and p.stat().st_mtime_ns==record['mtime_ns']
        record=dict(record,sha256=digest(p));token=__import__('hashlib').sha256(str(p).encode()).hexdigest()
        save(OUT/(NAME+'-'+token+'-before.json'),record)
        result=compress(p,record,guard)
        save(OUT/(NAME+'-'+token+'-after.json'),result)
        return result
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            for start in range(0,len(candidates),4):
                guard();rows.extend(pool.map(work,candidates[start:start+4]))
                saved=sum(r['allocated_before']-r['allocated_after'] for r in rows)
                report=dict(stage='compressing-completed-fixtures',pid=os.getpid(),process_created=psutil.Process().create_time(),
                    files_verified=len(rows),saved_bytes=saved,seconds=time.monotonic()-started)
                write(status,report);print(json.dumps(report),flush=True)
                if saved>=TARGET:break
        # Admission still requires the unchanged independent global cap check.
        for p,h in inputs.items():assert digest(p)==h,p
        for r in rows:
            p=Path(r['path']);assert digest(p)==r['sha256'] and p.stat().st_size==r['bytes'] and p.stat().st_mtime_ns==r['mtime_ns']
        save(result,dict(complete=True,passed=True,target_met=saved>=TARGET,attempt_sha256=digest(attempt),rows=rows,saved_bytes=saved,seconds=time.monotonic()-started,
            all_processed_bytes_sizes_paths_mtimes_unchanged=True,deleted_files=0,scientific_attempts_repeated=0,production_modified=False))
        write(status,dict(report,stage='complete'))
    except BaseException as exc:
        error=repr(exc);save(failure,dict(error=error,traceback=traceback.format_exc(),rows=rows,preserve_all_evidence=True));raise
    finally:
        assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()

if __name__=='__main__':main()
