"""Guard and freeze one paging research process; never touch production state."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
import integrated_coverage_queue as guard

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/representative-coverage-20260919'

def run():
    exe=Path(sys.argv[1]).resolve();label=sys.argv[2];extra=sys.argv[3:]
    assert label.replace('-','').isalnum()
    lock=OUT/'running.lock'
    # Also refuse a concurrently running symmetry experiment.
    assert not (OUT.parent/'symmetric-bridge-20260919/running.lock').exists()
    with lock.open('x') as f:f.write(str(os.getpid()))
    child=None;started=time.monotonic();error=None;samples=[];sample_at=0
    limit=float(os.environ.get('GTO_RESEARCH_MAX_SECONDS','7200'))
    assert 0<limit<=43200, 'Research deadline must be positive and at most 12 hours'
    try:
        assert guard.idle(),'Production is active; not starting research.'
        inputs=[exe,Path(__file__),OUT/'PAGING-PROTOCOL.md',ROOT/'crates/solver/src/gpu/mod.rs',
                ROOT/'crates/solver/src/gpu/continuation_paging.rs',ROOT/'crates/solver/tests/continuation_paging.rs']
        source=ROOT/'crates/solver/examples/integrated_continuation_paged.rs'
        if source.exists():inputs.append(source)
        if exe.stem in ['continuation_transfer','continuation_transfer_streamed']:
            inputs.extend([ROOT/f'crates/solver/examples/{exe.stem}.rs',
                           ROOT/'crates/solver/Cargo.toml',ROOT/'crates/solver/tests/continuation_policy_json.rs',
                           ROOT/'tools/research/continuation_transfer_review.py',
                           ROOT/'tools/research/continuation_transfer_aggregate.py',
                           OUT/'TRANSFER-CONTROLS.md',OUT/'STREAMED-TRANSFER-PROTOCOL.md',
                           OUT/'HOLDOUT-PROTOCOL.md'])
        if os.environ.get('GTO_RESEARCH_PROTOCOL'):
            inputs.append((ROOT/os.environ['GTO_RESEARCH_PROTOCOL']).resolve())
        inputs.extend((ROOT/x).resolve() for x in extra if (ROOT/x).is_file())
        record=OUT/(label+'-freeze.json');assert not record.exists()
        record.write_text(json.dumps(dict(inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
            command=[str(exe),*extra],maximum_seconds=limit,registered_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())),indent=2))
        for p in inputs[1:]:
            dest=OUT/'snapshots'/label/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
        env=os.environ.copy();env['RAYON_NUM_THREADS']='4';env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+';'+env['PATH']
        with (OUT/(label+'.log')).open('x') as log:
            child=subprocess.Popen([str(exe),*extra],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
            while child.poll() is None:
                time.sleep(2)
                if time.monotonic()-started>limit:
                    child.terminate();child.wait(timeout=20)
                    raise RuntimeError('Registered research deadline reached; retained checkpoints.')
                if not guard.idle():
                    child.terminate();child.wait(timeout=20)
                    raise RuntimeError('Production became active; stopped only research child.')
                if time.monotonic() >= sample_at:
                    ram=psutil.virtual_memory().available
                    vram=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2
                    samples.append(dict(seconds=time.monotonic()-started,free_host_bytes=ram,free_gpu_bytes=vram))
                    (OUT/(label+'-resources.json')).write_text(json.dumps(samples,indent=2))
                    sample_at=time.monotonic()+10
                    if ram<20_000_000_000 or vram<3_000_000_000:
                        child.terminate();child.wait(timeout=20)
                        raise RuntimeError('Memory reserve reached; stopped only research child.')
        if child.returncode:raise RuntimeError(f'Research exited {child.returncode}')
    except Exception as ex:
        error=str(ex);raise
    finally:
        if child is not None and child.poll() is None:child.terminate();child.wait(timeout=20)
        result=dict(exit_code=child.returncode if child else None,error=error,seconds=time.monotonic()-started)
        (OUT/(label+'-status.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
        lock.unlink()

if __name__=='__main__':run()
