"""Bounded S: execution for the unchanged complete-policy comparison."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from reboot_research_idle_v1 import idle
from hu_paired_continuation_support_20260925 import LOCK,OTHER,frozen_inputs
from hu_root_retained_storage_admitted_study_20260924 import measure,LIMIT,METADATA_RESERVE


def guard_for(reg,*,gpu=True):
    started=time.monotonic();last=last_size=0.
    store=Path(reg['store'])
    assert store.parent.resolve()==Path('S:/GTOpen-research').resolve()
    def guard():
        nonlocal last,last_size
        now=time.monotonic();assert now-started<reg['maximum_seconds']
        if now-last>2:
            assert idle() and not OTHER.exists()
            assert psutil.virtual_memory().available>=20_000_000_000
            assert shutil.disk_usage('S:/').free>=40_000_000_000
            assert shutil.disk_usage('T:/').free>=1_000_000_000
            if gpu:
                import torch
                assert torch.cuda.mem_get_info()[0]>=3_000_000_000
            last=now
        if now-last_size>10:
            paths=list(OUT.glob(reg['prefix']+'*'))
            if store.exists():paths.extend(store.rglob('*'))
            assert sum(p.stat().st_size for p in paths if p.is_file())<=reg['maximum_output_bytes']
            last_size=now
    return guard


def launch(script,prefix,extra,*,cap,seconds):
    assert idle() and not LOCK.exists() and not OTHER.exists()
    rp=OUT/f'{prefix}-registration.json';assert not rp.exists()
    store=Path(extra['store'])
    assert store.resolve()==(Path('S:/GTOpen-research')/prefix).resolve() and not store.exists()
    # Refuse an accidental second use of the originally named heldout study.
    assert not (OUT/'later-action-complete-evaluation-study-v1-registration.json').exists()
    inputs,trials=frozen_inputs()
    for name in extra['extra_inputs']:inputs[str(name)]=sha(name)
    amendment=OUT/'LATER-ACTION-RECOVERED-EVALUATION-ROUTING.md';inputs[str(amendment)]=sha(amendment)
    roots=measure();total=sum(r['allocated_file_bytes'] for r in roots)
    future=8_000_000_000 if extra['mode']=='control' else 0
    assert total+cap+future+METADATA_RESERVE<=LIMIT
    assert shutil.disk_usage('S:/').free>=40_000_000_000+cap
    reg=dict(inputs=inputs,trials=trials,prefix=prefix,storage_inventory=roots,
        projected_allocated_bytes=total+cap+future+METADATA_RESERVE,
        subsequent_evaluation_reserve_bytes=future,maximum_output_bytes=cap,
        maximum_seconds=seconds,production_modified=False,**extra)
    save(rp,reg);child=None;error=None;acquired=False;started=time.monotonic()
    try:
        with LOCK.open('x') as stream:stream.write(str(os.getpid()))
        acquired=True;guard=guard_for(reg,gpu=False);guard()
        with (OUT/f'{prefix}.log').open('x') as log:
            child=subprocess.Popen([sys.executable,str(script),'--worker'],cwd=ROOT,
                stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            save(OUT/f'{prefix}-admission.json',dict(controller_pid=os.getpid(),worker_pid=child.pid,
                registration_sha256=sha(rp),production_modified=False))
            while child.poll() is None:
                guard()
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:pass
        assert child.returncode==0,'Preserve failed evaluation; no automatic retry'
        assert read(OUT/f'{prefix}-result.json')['passed']
    except BaseException as exc:error=repr(exc);raise
    finally:
        if child is not None and child.poll() is None:
            for descendant in reversed(psutil.Process(child.pid).children(recursive=True)):
                try:descendant.terminate()
                except psutil.NoSuchProcess:pass
            child.terminate();child.wait(timeout=20)
        if acquired:
            assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()
        save(OUT/f'{prefix}-status.json',dict(state='failed' if error else 'complete',error=error,
            exit_code=child.returncode if child else None,seconds=time.monotonic()-started,production_modified=False))
