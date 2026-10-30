"""Bounded, byte-preserving NTFS compression of seven completed evidence owners."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from ntfs_research_storage_v1 import allocated_bytes, attributes, COMPRESSED
from bounded_parallel_evaluation_archive_v2 import production_available
from hu_completed_evidence_compression_20260924 import write

PREFIX='completed-raw-json-preservation-v1'
BASE=Path('S:/GTOpen-research')
CONTROL=BASE/(PREFIX+'-control')
MANIFEST=OUT/f'{PREFIX}-manifest.json'
OWNERS=('sampled-physical-dense-evaluation-v1','sampled-physical-allin-evaluation-v2',
    'sampled-physical-hybrid-evaluation-v2','sampled-physical-dense-pilot-v1',
    'sampled-physical-allin-pilot-v1','sampled-physical-hybrid-pilot-v1',
    'sampled-physical-hybrid-allin-pilot-v1')
NAMES={'queries.json','profiles.json','policies.json','updates.json'}
BLOCKED_REGS=[OUT/'weighted-complete-evaluation-study-v1-registration.json',
              OUT/'board-training-pipeline-queue-v2-registration.json']
AMENDMENT=OUT/'COMPLETED-RAW-JSON-PRESERVATION-AMENDMENT.md'


def norm(path): return os.path.normcase(os.path.abspath(path))


def safe_path(path, control=False):
    p=Path(path); assert p.is_absolute() and p.resolve()==p
    if control: assert p.parent==CONTROL and p.suffix=='.json'
    else:
        relative=p.relative_to(BASE)
        assert relative.parts[0] in OWNERS and p.name in NAMES and len(relative.parts)>=3
        assert not any(x in ('objects','checkpoint-objects','models') for x in relative.parts)
    for item in (p,*p.parents): assert not attributes(item)&0x400, 'Reparse path: '+str(item)
    assert p.is_file()
    return p


def owners_idle():
    for p in psutil.process_iter(['pid','cmdline']):
        if p.pid==os.getpid(): continue
        cmd=' '.join(p.info['cmdline'] or []).lower()
        assert not any(name.lower() in cmd for name in OWNERS), 'Evidence owner is active'
        assert not any('hu_sampled_physical_'+name in cmd for name in ('dense','allin','hybrid')), 'Related historical worker is active'


def dependencies():
    inputs={str(p):sha(p) for p in [Path(__file__).resolve(),AMENDMENT,
        ROOT/'tools/research/ntfs_research_storage_v1.py',
        ROOT/'tools/research/hu_completed_evidence_compression_20260924.py',*BLOCKED_REGS]}
    blocked=set()
    for p in BLOCKED_REGS: blocked.update(norm(x) for x in read(p)['inputs'])
    for owner in OWNERS:
        rp=OUT/f'{owner}-result.json'; result=read(rp)
        assert result['terminal'] and result['production_modified'] is False
        inputs[str(rp)]=sha(rp)
        if 'evaluation' in owner:
            reg=OUT/f'{owner}-registration.json'; assert result['registration_sha256']==sha(reg)
            assert Path(read(reg)['store'])==BASE/owner
            assert result['completed_evaluation_deals']==16384
            inputs[str(reg)]=sha(reg)
        else:
            assert Path(result['store'])==BASE/owner and result['completed_iterations']==78
            assert [x['iteration'] for x in result['steps']]==list(range(1,79))
    return inputs,blocked


def describe(path):
    p=safe_path(path); before=p.stat(); digest=sha(p); after=p.stat()
    assert before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns
    assert not attributes(p)&COMPRESSED
    return dict(path=str(p),bytes=after.st_size,mtime_ns=after.st_mtime_ns,
                sha256=digest,allocated_before=allocated_bytes(p))


def verify(record,control=False):
    p=safe_path(record['path'],control); s=p.stat()
    assert s.st_size==record['bytes'] and s.st_mtime_ns==record['mtime_ns']
    assert sha(p)==record['sha256'],'Logical bytes changed: '+str(p)
    return p


def plan():
    began=time.monotonic(); assert not MANIFEST.exists()
    assert production_available() and psutil.virtual_memory().available>20_000_000_000
    owners_idle(); inputs,blocked=dependencies()
    candidates=read(OUT/'board-next-study-compression-candidates-v2.json')['candidates']
    paths=sorted(r['path'] for r in candidates if Path(r['owner']).name in OWNERS and Path(r['path']).name in NAMES)
    assert len(paths)==len(set(paths)) and paths
    assert not any(norm(p) in blocked for p in paths)
    with ThreadPoolExecutor(max_workers=4) as pool: records=list(pool.map(describe,paths))
    assert 50_000_000_000<sum(r['bytes'] for r in records)<64_000_000_000
    for p,h in inputs.items(): assert sha(p)==h,p
    owners_idle(); assert time.monotonic()-began<1800
    save(MANIFEST,dict(inputs=inputs,records=records,logical_bytes=sum(r['bytes'] for r in records),
        allocated_before=sum(r['allocated_before'] for r in records),seconds=time.monotonic()-began,
        excludes_model_objects=True,excludes_active_registered_inputs=True,compression_performed=False))
    print(json.dumps(dict(manifest=str(MANIFEST),files=len(records),seconds=time.monotonic()-began)),flush=True)


def compress_batch(records,control,guard):
    guard()
    paths=[verify(r,control) for r in records]
    command=Path(os.environ['SystemRoot'])/'System32/compact.exe'
    began=time.monotonic()
    process=subprocess.Popen([str(command),'/C','/Q',*[str(p) for p in paths]],
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        while process.poll() is None:
            guard(); assert time.monotonic()-began<300
            try: process.wait(timeout=2)
            except subprocess.TimeoutExpired: pass
        assert process.returncode==0
    finally:
        if process.poll() is None: process.terminate(); process.wait(timeout=20)
    result=[]
    for r in records:
        p=verify(r,control); assert attributes(p)&COMPRESSED
        result.append(dict(path=str(p),sha256=r['sha256'],allocated_before=r['allocated_before'],
                           allocated_after=allocated_bytes(p)))
    return result


def run(control=False):
    began=time.monotonic(); stop=threading.Event()
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    owners_idle(); manifest=read(MANIFEST)
    for p,h in manifest['inputs'].items(): assert sha(p)==h,p
    inputs=dict(manifest['inputs']); inputs[str(MANIFEST)]=sha(MANIFEST)
    prefix=PREFIX+('-control' if control else '')
    rp=OUT/f'{prefix}-registration.json'; result_path=OUT/f'{prefix}-result.json'
    journal=OUT/prefix; lock=OUT/f'{PREFIX}.lock'
    assert not result_path.exists() and not lock.exists()
    records=manifest['records']
    if control:
        assert not CONTROL.exists(); CONTROL.mkdir()
        selected=[]
        for name in sorted(NAMES):
            options=sorted((r for r in records if Path(r['path']).name==name),key=lambda r:r['bytes'])
            selected.extend([options[0],options[-1]])
        records=[]
        for i,r in enumerate(selected):
            verify(r); p=CONTROL/f'{i:02d}-{Path(r["path"]).name}'; shutil.copyfile(r['path'],p)
            records.append(dict(path=str(p),bytes=p.stat().st_size,mtime_ns=p.stat().st_mtime_ns,
                sha256=sha(p),allocated_before=allocated_bytes(p)))
            assert records[-1]['sha256']==r['sha256']
        assert sum(r['bytes'] for r in records)<100_000_000
        try: verify(dict(records[0],sha256='0'*64),True)
        except AssertionError: pass
        else: raise AssertionError('Accepted wrong hash')
        try: safe_path(records[0]['path'],False)
        except AssertionError: pass
        else: raise AssertionError('Accepted outside evidence path')
    else:
        cp=OUT/f'{PREFIX}-control-result.json'; c=read(cp)
        assert c['passed'] and c['source_sha256']==sha(__file__)
        assert c['registration_sha256']==sha(OUT/f'{PREFIX}-control-registration.json')
        inputs[str(cp)]=sha(cp)
    assert production_available() and psutil.cpu_percent(interval=1)<50
    if rp.exists():
        reg=read(rp); assert reg['inputs']==inputs and reg['records']==records and reg['control']==control
    else:
        journal.mkdir()
        save(rp,dict(inputs=inputs,records=records,control=control,workers=4,batch_size=32,
            maximum_seconds=7200,maximum_file_bytes=64_000_000_000,production_modified=False,
            no_deletions=True,no_relocations=True,byte_preserving=True))
    def guard():
        assert not stop.is_set() and time.monotonic()-began<7200
        assert production_available() and psutil.virtual_memory().available>20_000_000_000
        assert psutil.disk_usage('S:/').free>40_000_000_000
    totals=[]
    with lock.open('x') as f: f.write(str(os.getpid()))
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            pending={}
            for start in range(0,len(records),32):
                batch=records[start:start+32]; target=journal/f'batch-{start:06d}.json'
                if target.exists():
                    prior=read(target)
                    assert len(prior)==len(batch)
                    for r,v in zip(batch,prior):
                        p=verify(r,control)
                        assert v['path']==str(p) and v['sha256']==r['sha256']
                        assert attributes(p)&COMPRESSED and allocated_bytes(p)==v['allocated_after']
                    totals.extend(prior)
                else: pending[pool.submit(compress_batch,batch,control,guard)]=target
            try:
                for future in as_completed(pending):
                    rows=future.result(); save(pending[future],rows); totals.extend(rows)
                    write(OUT/f'{prefix}-status.json',dict(state='running',pid=os.getpid(),files=len(totals),
                        total_files=len(records),saved_bytes=sum(x['allocated_before']-x['allocated_after'] for x in totals),
                        seconds=time.monotonic()-began))
            except BaseException:
                stop.set()
                for future in pending: future.cancel()
                raise
        assert len(totals)==len(records)
        owners_idle()
        for p,h in inputs.items(): assert sha(p)==h,p
        report=dict(passed=True,registration_sha256=sha(rp),source_sha256=sha(__file__),files=len(records),
            logical_bytes=sum(r['bytes'] for r in records),allocated_before=sum(x['allocated_before'] for x in totals),
            allocated_after=sum(x['allocated_after'] for x in totals),
            saved_bytes=sum(x['allocated_before']-x['allocated_after'] for x in totals),
            seconds=time.monotonic()-began,production_modified=False,deleted_files=0,relocated_files=0,
            control=control,independent_readback_pending=True,
            journals={str(p):sha(p) for p in sorted(journal.glob('batch-*.json'))})
        save(result_path,report); write(OUT/f'{prefix}-status.json',dict(report,state='complete',pid=os.getpid()))
        print(json.dumps({k:v for k,v in report.items() if k!='journals'}),flush=True)
    except BaseException as exc:
        write(OUT/f'{prefix}-status.json',dict(state='interrupted',pid=os.getpid(),error=repr(exc),
            files=len(totals),resume='Verify immutable manifest and completed batches before resume.'))
        raise
    finally:
        assert lock.read_text()==str(os.getpid()); lock.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser(); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--plan',action='store_true'); group.add_argument('--control',action='store_true'); group.add_argument('--run',action='store_true')
    options=parser.parse_args()
    if options.plan: plan()
    else: run(options.control)
