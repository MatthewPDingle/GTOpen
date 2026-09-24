"""Global storage admission before the already prepared candidate study.

This wrapper draws no poker samples and cannot change the study's counts,
seeds or policy. It accounts for all three generated-research storage roots.
"""
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from hu_completed_evidence_compression_20260924 import digest,read,write
from ntfs_research_storage_v1 import allocated_bytes,attributes
from reboot_research_idle_v1 import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='root-retained-global-storage-admission-v1'
ROOTS=[Path('S:/GTOpen-research'),Path('T:/GTOpen-research'),ROOT/'research']
LIMIT=800_000_000_000
METADATA_RESERVE=2_000_000_000
STUDY=ROOT/'tools/research/hu_root_retained_wider_study_20260924.py'


def stable_file(path):
    started=time.monotonic()
    while attributes(path)&0x400:
        st=path.lstat()
        # WOF is transparent file compression, not a redirected pathname.
        if st.st_reparse_tag==0x80000017:return
        # Observed while compact.exe is converting an existing file. Do not
        # accept a link or count the transitional representation as final.
        assert st.st_reparse_tag==0 and not path.is_symlink(),str(path)
        assert time.monotonic()-started<30,'File did not settle: '+str(path)
        time.sleep(.25)


def measure():
    start=time.monotonic();rows=[];last_probe=0.
    for root in ROOTS:
        assert root.is_dir()
        logical=allocated=count=0
        for folder,dirs,files in os.walk(root,followlinks=False):
            now=time.monotonic();assert now-start<600
            if now-last_probe>2:
                assert idle();last_probe=now
            # Do not hide linked trees or count files outside the declared roots.
            for name in dirs:
                assert not attributes(Path(folder)/name)&0x400
            for name in files:
                p=Path(folder)/name
                try:
                    stable_file(p)
                    logical+=p.stat().st_size;allocated+=allocated_bytes(p);count+=1
                except FileNotFoundError:
                    # Only mutable controller status temporary files may disappear.
                    assert p.suffix=='.tmp' or p.name.startswith('.partial-')
        rows.append(dict(root=str(root),files=count,logical_bytes=logical,allocated_file_bytes=allocated))
    return rows


def main(run=False):
    start=time.monotonic();psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    assert idle()
    if run:
        for prefix in ['root-retained-fresh-pilot-v1','root-retained-study-continuation-v1']:
            status=read(OUT/(prefix+'-status.json'))
            assert status['state']=='complete'
            pid=status.get('controller_pid')
            if pid and psutil.pid_exists(pid):
                command=' '.join(psutil.Process(pid).cmdline())
                assert 'root_retained' not in command
    rows=measure();total=sum(r['allocated_file_bytes'] for r in rows)
    recovered=read(OUT/'completed-evidence-compression-v1-result.json')
    assert recovered['passed'] and recovered['state']=='complete' and recovered['deleted_files']==0
    allocation_cap=min(50_000_000_000,recovered['saved_bytes'])
    projected=total+allocation_cap+METADATA_RESERVE
    snapshot=dict(roots=rows,total_allocated_file_bytes=total,limit_bytes=LIMIT,
        planned_study_allocation_cap=allocation_cap,metadata_and_rounding_reserve=METADATA_RESERVE,
        projected_allocated_bytes=projected,storage_admitted=projected<=LIMIT,
        seconds=time.monotonic()-start,scope='Generated research roots only; user hand histories, saves, source and binaries outside these roots excluded.',
        gpu_used=False,production_modified=False)
    if not run:
        print(__import__('json').dumps(snapshot),flush=True);return
    assert snapshot['storage_admitted'],'Preserve studies and finish more compression before launch'
    # Training and its audit must be terminal; the study checks all remaining
    # endpoint, numeric, source, GPU-exclusive and free-volume admission gates.
    rp=OUT/(PREFIX+'-registration.json');assert not rp.exists()
    write(rp,dict(snapshot=snapshot,inputs={str(p):digest(p) for p in
        [Path(__file__),STUDY,ROOT/'tools/research/ntfs_research_storage_v1.py']},
        scope='Additional global storage gate only; does not replace candidate-specific admission or alter evaluation design.'))
    result=subprocess.run([sys.executable,str(STUDY),'--run'],cwd=ROOT,
        creationflags=subprocess.CREATE_NO_WINDOW)
    write(OUT/(PREFIX+'-result.json'),dict(passed=result.returncode==0,exit_code=result.returncode,
        registration_sha256=digest(rp),production_modified=False))
    raise SystemExit(result.returncode)


if __name__=='__main__':
    assert sys.argv[1:] in (['--check'],['--run'])
    main(run=sys.argv[1:] == ['--run'])
