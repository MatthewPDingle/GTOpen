"""Sequential, byte-preserving compression of eight completed checkpoints."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from hu_completed_evidence_compression_20260924 import digest,read,write
from reboot_research_idle_v1 import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
OLD=ROOT/'research/preflop-evolution/ssd-storage-20260920'
PREFIX='completed-checkpoint-storage-queue-v1'
ORDER=[f'strategic-{weight}112-{iteration}-v1' for iteration in (500,1000,1500,2000)
       for weight in ('weighted','equal')]
WORKER=ROOT/'tools/research/hu_completed_checkpoint_lzx_20260924.py'


def same_process(identity):
    if identity is None:return False
    try:
        p=psutil.Process(identity['pid'])
        return p.is_running() and p.create_time()==identity['created']
    except psutil.NoSuchProcess:return False


def verified_result(name):
    prefix='checkpoint-lzx-'+name
    rp=OUT/(prefix+'-registration.json');result=read(OUT/(prefix+'-result.json'));reg=read(rp)
    assert result['state']=='complete' and result['passed'] and result['deleted_files']==0
    assert result['registration_sha256']==digest(rp)
    assert result['files_verified']==result['total_files']==len(reg['expected_sha256'])==227
    assert reg['dependencies'][str(WORKER)]==digest(WORKER)
    before=after=0
    for i,n in enumerate(sorted(reg['expected_sha256'])):
        b=read(OUT/prefix/f'{i:04d}-before.json');a=read(OUT/prefix/f'{i:04d}-after.json')
        assert b['name']==a['name']==n and b['sha256']==a['sha256']==reg['expected_sha256'][n]
        before+=b['allocated'];after+=a['allocated']
    assert result['allocated_before']==before and result['allocated_after']==after
    assert result['saved_bytes']==before-after
    return dict(name=name,result_sha256=digest(OUT/(prefix+'-result.json')),
                saved_bytes=result['saved_bytes'],files=result['files_verified'])


def main():
    start=time.monotonic();child=None;records=[];error=None
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    assert idle()
    rp=OUT/(PREFIX+'-registration.json');assert not rp.exists()
    current=read(OUT/('checkpoint-lzx-'+ORDER[0]+'-status.json'))
    watched=None
    if current['state']=='running':
        p=psutil.Process(current['controller_pid']);cmd=' '.join(p.cmdline())
        assert WORKER.name in cmd and ORDER[0] in cmd
        watched=dict(pid=p.pid,created=p.create_time())
    else:
        verified_result(ORDER[0])
    inputs={str(p):digest(p) for p in [Path(__file__),WORKER,
        ROOT/'tools/research/hu_completed_evidence_compression_20260924.py',
        ROOT/'tools/research/ntfs_research_storage_v1.py']}
    for name in ORDER:
        review=OLD/(name+'-review.json');d=read(review)
        assert d['segment_passed'] and len(d['snapshot']['files'])==227
        assert Path(d['snapshot']['path']).resolve()==(Path('S:/GTOpen-research/strategic-segments-v1')/name/'final').resolve()
        inputs[str(review)]=digest(review)
    for name in ORDER[1:]:
        assert not (OUT/('checkpoint-lzx-'+name+'-registration.json')).exists()
    write(rp,dict(inputs=inputs,order=ORDER,watched_first=watched,maximum_seconds=12*3600,
        operation='Windows transparent LZX only; original review hashes verified for every file',
        deletes_allowed=False,production_modified=False,gpu_used=False,automatic_retry=False))
    def guard():
        assert time.monotonic()-start<12*3600 and idle()
        for volume in ['S:/','T:/']:assert psutil.disk_usage(volume).free>40_000_000_000
    def status(stage,**extra):
        write(OUT/(PREFIX+'-status.json'),dict(state='running',stage=stage,controller_pid=os.getpid(),
            records=records,saved_bytes=sum(r['saved_bytes'] for r in records),
            seconds=time.monotonic()-start,production_modified=False,**extra))
    try:
        while same_process(watched):
            guard();status('waiting-for-first-checkpoint',watched=watched);time.sleep(5)
        records.append(verified_result(ORDER[0]))
        for name in ORDER[1:]:
            guard()
            for p,h in inputs.items():assert digest(Path(p))==h
            with (OUT/(PREFIX+'-'+name+'.log')).open('x',encoding='utf-8') as log:
                child=subprocess.Popen([sys.executable,str(WORKER),'--checkpoint',name],cwd=ROOT,
                    stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                identity=dict(pid=child.pid,created=psutil.Process(child.pid).create_time())
                while child.poll() is None:
                    guard();status(name,worker=identity)
                    try:child.wait(timeout=5)
                    except subprocess.TimeoutExpired:pass
                assert child.returncode==0,'Preserve partial compression; no automatic retry'
            records.append(verified_result(name));print(json.dumps(records[-1]),flush=True)
        result=dict(passed=True,state='complete',registration_sha256=digest(rp),records=records,
            saved_bytes=sum(r['saved_bytes'] for r in records),seconds=time.monotonic()-start,
            deleted_files=0,production_modified=False,gpu_used=False)
        write(OUT/(PREFIX+'-result.json'),result);write(OUT/(PREFIX+'-status.json'),result)
        print(json.dumps(result),flush=True)
    except BaseException as exc:
        error=repr(exc)
        if child is not None and child.poll() is None:
            # The child checks activity between files. Let the current file finish.
            try:child.wait(timeout=200)
            except subprocess.TimeoutExpired:
                subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],capture_output=True,
                    timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
        write(OUT/(PREFIX+'-status.json'),dict(state='stopped',error=error,records=records,
            seconds=time.monotonic()-start,production_modified=False,gpu_used=False))
        raise


if __name__=='__main__':
    assert sys.argv[1:]==['--run']
    main()
