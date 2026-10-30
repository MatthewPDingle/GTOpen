"""Run a bounded, provenance-recorded test binary while production is idle."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import time
import integrated_coverage_queue as guard

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/symmetric-bridge-20260919'

def run():
    exe=Path(sys.argv[1]).resolve()
    label=sys.argv[2]
    assert label.replace('-','').isalnum()
    extra=sys.argv[3:]
    lock=OUT/'running.lock'
    with lock.open('x') as f:f.write(str(os.getpid()))
    child=None
    try:
        assert guard.idle(),'Production is active; not starting research.'
        inputs=[exe,Path(__file__),OUT/'PROTOCOL.md',ROOT/'crates/solver/src/gpu/mod.rs',
            ROOT/'crates/solver/src/gpu/continuation.rs',ROOT/'crates/solver/tests/continuation_symmetry.rs',
            ROOT/'crates/solver/src/gpu/continuation_projection.cu',OUT/'PROJECTION-PROTOCOL.md']
        if (OUT/'FIXED-RANGE-PROTOCOL.md').exists():inputs.append(OUT/'FIXED-RANGE-PROTOCOL.md')
        if 'integrated_continuation_compact' in exe.name:
            inputs.extend([OUT/'CONNECTED-PROTOCOL.md',ROOT/'crates/solver/examples/integrated_continuation_compact.rs'])
            inputs.extend((ROOT/x).resolve() for x in extra if (ROOT/x).is_file())
        freeze={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
        record=OUT/(label+'-freeze.json')
        assert not record.exists(),'Preserve prior test registrations; use a new label.'
        record.write_text(json.dumps({'inputs':freeze,'command':[str(exe),*extra],
            'registered_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())},indent=2))
        # Preserve each registered source version, including failed candidates.
        for path in inputs[1:]:
            target=OUT/'snapshots'/label/path.relative_to(ROOT)
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
        env=os.environ.copy();env['RAYON_NUM_THREADS']='4'
        env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+';'+env['PATH']
        started=time.monotonic()
        with (OUT/(label+'.log')).open('x') as log:
            child=subprocess.Popen([str(exe),*extra],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
            while child.poll() is None:
                time.sleep(2)
                if not guard.idle():
                    child.terminate();child.wait(timeout=20)
                    raise RuntimeError('Production became active; stopped only research child.')
        result={'exit_code':child.returncode,'seconds':time.monotonic()-started}
        (OUT/(label+'-status.json')).write_text(json.dumps(result,indent=2))
        print(json.dumps(result),flush=True)
        if child.returncode:raise SystemExit(child.returncode)
    finally:
        if child is not None and child.poll() is None:child.terminate();child.wait(timeout=20)
        lock.unlink()

if __name__=='__main__':run()
