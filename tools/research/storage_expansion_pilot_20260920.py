"""Admission-checked, unchanged-native-binary pilot of the selected broader panel."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import psutil
from loopback_research_validation import idle
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
SUB=ROOT/'research/preflop-evolution/conditional-hu-20260919/subtree.json'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert idle() and not (OUT/'running.lock').exists()
    assert read(OUT/'long-ram-v1-review.json')['passed']
    assert read(OUT/'expansion-capacity-v1-status.json')['step']=='complete-awaiting-strategic-pilot'
    selection=read(OUT/'expansion-capacity-v1-selection.json');count=selection['selected_boards'];assert count in [128,112,96]
    for p,h in selection['evidence'].items():assert sha(ROOT/p)==h,p
    for p,h in read(OUT/'expansion-capacity-v1-freeze.json')['inputs'].items():assert sha(ROOT/p)==h,p
    prior=read(OUT/'connected-v2-runtime-freeze.json')
    src=[(p,h) for p,h in prior['executables'].items() if 'stored' in p];assert len(src)==1
    exe=ROOT/'target/qualified-paging'/('ssd-connected-v2-'+Path(src[0][0]).name);assert sha(exe)==src[0][1]
    plan=read(OUT/f'expansion-capacity-{count}.json');capacity=plan['totals']
    ram=capacity['ram_payload_total_bytes']
    # The audit constructs board-then-pot, while the actual study constructs pot-then-board.
    # Add the largest new game's allocation to the final shared allocation and ALL metadata;
    # this overbounds constructor overlap regardless of admission order.
    device=capacity['steady_gpu_payload_bytes']+max(sum(r['workspace_components_bytes']) for r in plan['rows'])
    assert device>=capacity['constructor_gpu_payload_upper_bytes']
    available=psutil.virtual_memory().available
    freegpu=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2
    assert ram<=72_000_000_000 and device<=18_000_000_000
    assert available>=ram+26_000_000_000 and freegpu>=device+3_000_000_000
    manifest=OUT/f'expansion-train-{count}.json';dest=OUT/'expansion-pilot-v1-result.json';assert not dest.exists()
    scratch=Path('S:/GTOpen-research/expansion-pilot-v1');assert not scratch.exists();scratch.mkdir()
    inputs=[Path(__file__),SUB,manifest,OUT/'EXPANSION-PILOT-PROTOCOL.md',OUT/'expansion-capacity-v1-selection.json',
        OUT/'long-ram-v1-review.json',OUT/'expansion-capacity-v1-freeze.json',OUT/'connected-v2-runtime-freeze.json']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    with (OUT/'expansion-pilot-v1-freeze.json').open('x') as f:json.dump(dict(inputs=frozen,exe=str(exe),exe_sha256=sha(exe),
        available_host_bytes=available,available_gpu_bytes=freegpu,order_independent_constructor_gpu_payload_upper_bytes=device,
        selected_boards=count,iterations=20),f,indent=2)
    status=dict(step='running',pid=os.getpid(),created=psutil.Process().create_time(),selected_boards=count)
    def report():(OUT/'expansion-pilot-v1-status.json').write_text(json.dumps(status,indent=2))
    with (OUT/'running.lock').open('x') as f:f.write(str(os.getpid()))
    env=os.environ.copy();env.update(GTO_STORAGE_RAM_BYTES='72000000000',GTO_STORAGE_WRITE_CAP='0',
        GTO_SSD_STUDY_DIR=str(scratch),GTO_RESEARCH_MAX_SECONDS='1800',GTO_RESEARCH_PROTOCOL=str((OUT/'EXPANSION-PILOT-PROTOCOL.md').relative_to(ROOT)))
    try:
        report()
        result=subprocess.run([sys.executable,'tools/research/loopback_research_validation.py',str(exe),'expansion-pilot-v1',
            str(SUB.relative_to(ROOT)),str(manifest.relative_to(ROOT)),str(dest.relative_to(ROOT)),'20'],cwd=ROOT,env=env)
        assert result.returncode==0,'Pilot failed; retain diagnostics'
        for p,h in frozen.items():assert sha(ROOT/p)==h,p
        assert sha(exe)==src[0][1]
        status['step']='complete-awaiting-review'
    except Exception as e:status.update(step='stopped-for-review',error=repr(e));raise
    finally:report();(OUT/'running.lock').unlink()
    print(json.dumps(status),flush=True)
if __name__=='__main__':main()
