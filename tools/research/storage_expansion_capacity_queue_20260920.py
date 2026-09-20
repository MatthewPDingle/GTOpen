"""Wait for the identified long run, review it, then plan frozen candidates on CPU."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from loopback_research_validation import idle
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
SUB=ROOT/'research/preflop-evolution/conditional-hu-20260919/subtree.json'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    status=dict(step='waiting-for-long-run',pid=os.getpid(),created=psutil.Process().create_time(),completed=[])
    def report():(OUT/'expansion-capacity-v1-status.json').write_text(json.dumps(status,indent=2))
    assert not (OUT/'expansion-capacity-v1-status.json').exists();report()
    parent=read(OUT/'long-ram-v1-status.json');deadline=time.monotonic()+3900
    while True:
        try:p=psutil.Process(parent['pid']);alive=p.create_time()==parent['created']
        except psutil.NoSuchProcess:alive=False
        if not alive:break
        assert time.monotonic()<deadline,'Long-run wait bound'
        time.sleep(5)
    assert read(OUT/'long-ram-v1-status.json')['step']=='complete-awaiting-review','Long run did not complete'
    review=OUT/'long-ram-v1-review.json'
    if not review.exists():subprocess.run([sys.executable,'tools/research/storage_long_ram_review_20260920.py'],cwd=ROOT,check=True)
    assert read(review)['passed']
    assert idle() and not (OUT/'running.lock').exists()
    registration=read(OUT/'expansion-registration-freeze.json')
    for p,h in registration['inputs_sha256'].items():assert sha(ROOT/p)==h,p
    provenance=read(OUT/'capacity-v1-runtime-freeze.json')
    exe=ROOT/'target/qualified-paging/capacity-v1-audit.exe';assert sha(exe)==provenance['sha256']
    inputs=[Path(__file__),review,OUT/'EXPANSION-REGISTRATION.md',OUT/'expansion-registration-freeze.json',OUT/'capacity-v1-runtime-freeze.json',SUB]
    inputs += [OUT/f'expansion-train-{n}.json' for n in [128,112,96]]
    frozen={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    with (OUT/'expansion-capacity-v1-freeze.json').open('x') as f:json.dump(dict(inputs=frozen,executable=str(exe),exe_sha256=sha(exe)),f,indent=2)
    env=os.environ.copy();env.update(GTO_RESEARCH_PROTOCOL=str((OUT/'EXPANSION-REGISTRATION.md').relative_to(ROOT)),GTO_RESEARCH_MAX_SECONDS='900',RAYON_NUM_THREADS='4')
    with (OUT/'running.lock').open('x') as f:f.write(str(os.getpid()))
    try:
        for n in [128,112,96]:
            status['step']=f'planning-{n}';report();assert idle()
            dest=OUT/f'expansion-capacity-{n}.json';assert not dest.exists()
            code=subprocess.call([sys.executable,'tools/research/loopback_research_validation.py',str(exe),f'expansion-capacity-v1-{n}',
                str(SUB.relative_to(ROOT)),str((OUT/f'expansion-train-{n}.json').relative_to(ROOT)),str(dest.relative_to(ROOT)),'cpu'],cwd=ROOT,env=env)
            assert code==0,f'Planning {n} failed'
            for p,h in frozen.items():assert sha(ROOT/p)==h,p
            status['completed'].append(n);report()
        host=psutil.virtual_memory().available
        gpu=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2
        candidates=[];selected=None
        for n in [128,112,96]:
            result=read(OUT/f'expansion-capacity-{n}.json');assert len(result['rows'])==2*n
            t=result['totals'];ram=t['ram_payload_total_bytes'];device=t['constructor_gpu_payload_upper_bytes']
            reasons=[]
            if ram>72_000_000_000:reasons.append('fixed host payload cap')
            if device>18_000_000_000:reasons.append('fixed device payload cap')
            if ram+26_000_000_000>host:reasons.append('current host reserve')
            if device+3_000_000_000>gpu:reasons.append('current device reserve')
            candidates.append(dict(boards=n,totals=t,eligible=not reasons,reasons=reasons))
            if not reasons and selected is None:selected=n
        selection=dict(selected_boards=selected,candidates=candidates,available_host_bytes=host,available_gpu_bytes=gpu,
            training_started=False,rule='Largest candidate passing all frozen capacity-only limits; recheck before launch.',
            evidence={str((OUT/f'expansion-capacity-{n}.json').relative_to(ROOT)):sha(OUT/f'expansion-capacity-{n}.json') for n in [128,112,96]})
        with (OUT/'expansion-capacity-v1-selection.json').open('x') as f:json.dump(selection,f,indent=2)
        status.update(step='complete-awaiting-strategic-pilot',selected_boards=selected)
    except Exception as e:status.update(step='stopped-for-review',error=repr(e));raise
    finally:report();(OUT/'running.lock').unlink()
    print(json.dumps(status),flush=True)
if __name__=='__main__':main()
