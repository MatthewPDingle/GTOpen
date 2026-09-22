"""Guard one late-state entropy probe. No strategic convergence or deployment."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
from loopback_research_validation import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'


def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    label='hu-wide-maturity-v1'
    evidence=ROOT/'research/preflop-evolution/representative-coverage-20260919'
    destination=Path('S:/GTOpen-research/hu-wide-maturity-v1')
    exe=ROOT/'target/release/examples/hu_wide_state_maturity.exe'
    registration=OUT/'wide-maturity-v1-registration.json'
    reference_json=OUT/'wide-maturity-reference.json'
    reference=Path('S:/GTOpen-research/hu-wide-cold-replay-v1/reference-step-07/entry-0-generation-0.bin')
    assert not registration.exists() and not reference_json.exists() and not destination.exists()
    previous=json.loads((OUT/'wide-cold-replay-v1-review.json').read_text())
    assert previous['passed'] is True
    reference_sha=previous['checkpoint_hashes'][str(reference)]
    assert sha(reference)==reference_sha
    with reference_json.open('x') as f:json.dump({'path':str(reference),'sha256':reference_sha},f,indent=2)
    row=next(r for r in json.loads((OUT/'capacity-texture-result.json').read_text())['rows'] if r['board']=='KsQd9d' and r['preflop_leaf']==2)
    conservative_device=row['retained_gpu_payload_bytes']+sum(row['workspace_components_bytes'])
    expected_write=4*(row['canonical_state_bytes']+72)
    assert expected_write<16*2**30
    assert idle() and psutil.virtual_memory().available>40*2**30
    assert shutil.disk_usage('S:/').free>80*2**30
    vram=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])*2**20
    assert conservative_device<vram-3*2**30
    assert not (evidence/'running.lock').exists()
    inputs=[p for p in (ROOT/'crates/solver/src').rglob('*') if p.suffix in ['.rs','.cu']]
    inputs += [exe,Path(__file__),ROOT/'Cargo.lock',ROOT/'crates/solver/Cargo.toml',
        ROOT/'crates/solver/examples/hu_wide_state_maturity.rs',ROOT/'tools/research/loopback_research_validation.py',
        ROOT/'tools/research/paged_continuation_validation.py',reference_json,
        OUT/'bb-context-candidate.json',OUT/'capacity-texture-result.json',OUT/'wide-cold-replay-v1-review.json']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    record={'inputs':frozen,'reference':{'path':str(reference),'sha256':reference_sha},
        'created_at_unix':time.time(),'maximum_seconds':900,'iterations':2000,
        'snapshot_iterations':[4,100,500,2000],'expected_write_bytes':expected_write,
        'conservative_device_bytes':conservative_device,'free_gpu_bytes':vram,
        'scope':'Single full-support KsQd9d call continuation with registered changing reaches; entropy measurement, not equilibrium',
        'trajectory':'Same schedule as prior four-iteration exact recovery control; repeated modulo-23 factors and zero BB own reach at iteration 2',
        'gate':'New resident trajectory and CPU canonical export must reproduce prior iteration-4 checkpoint byte for byte before continuing',
        'no_automatic_retry':True,'no_strategy_claim':True}
    with registration.open('x') as f:json.dump(record,f,indent=2)
    destination.mkdir()
    env=os.environ.copy();env['GTO_RESEARCH_MAX_SECONDS']='900';env['GTO_RESEARCH_PROTOCOL']=str(registration.relative_to(ROOT))
    cmd=[sys.executable,str(ROOT/'tools/research/loopback_research_validation.py'),str(exe),label,
        str((OUT/'bb-context-candidate.json').relative_to(ROOT)),str(destination),str(reference_json.relative_to(ROOT))]
    run=subprocess.run(cmd,cwd=ROOT,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
    for suffix in ['.log','-status.json','-resources.json','-freeze.json']:
        source=evidence/(label+suffix)
        if source.exists():
            target=OUT/(label+suffix);assert not target.exists();shutil.copyfile(source,target)
    assert run.returncode==0,'probe stopped; preserve partial evidence, no retry'
    guard=json.loads((OUT/(label+'-status.json')).read_text())
    assert guard['error'] is None and guard['exit_code']==0
    for p,h in frozen.items():assert sha(ROOT/p)==h,p
    assert sha(reference)==reference_sha
    result=json.loads((destination/'result.json').read_text())
    assert result['iterations']==2000 and result['player_sweeps']==4000
    assert result['reference_at_four_exact'] and not result['convergence_claim'] and not result['strategic_accuracy_claim']
    assert [r['iteration'] for r in result['snapshots']]==record['snapshot_iterations']
    snapshots={r['path']:sha(Path(r['path'])) for r in result['snapshots']}
    assert sum(Path(p).stat().st_size for p in snapshots)==expected_write
    assert snapshots[str(destination/'iteration-0004.bin')]==reference_sha
    review={'passed':True,'result':result,'guard':guard,'snapshots':snapshots,
        'source_hashes_verified':len(frozen),'registration_sha256':sha(registration),
        'production_modified':False,'strategic_accuracy_claim':False}
    with (OUT/'wide-maturity-v1-review.json').open('x') as f:json.dump(review,f,indent=2)
    print(json.dumps(review,indent=2))


if __name__=='__main__':main()
