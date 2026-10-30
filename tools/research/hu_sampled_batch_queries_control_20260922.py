"""Freeze bounded physical-query cache checks; CPU-only implementation control."""
import hashlib
import json
from pathlib import Path
import subprocess
import time
from loopback_research_validation import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-batch-queries-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')

def main():
    assert idle()
    exe=ROOT/'target/release/examples/hu_sampled_batch_queries_control.exe'
    context=OUT/'bb-context-candidate.json';deals=OUT/'sampled-poker-v1-fixture.json'
    synthetic=OUT/'sampled-network-adapter-v1-fixture.json';trained=OUT/'sampled-physical-gpu-v1-weights.json'
    prerequisite=OUT/'sampled-physical-gpu-v1-review.json';assert json.loads(prerequisite.read_text())['passed']
    paths=[Path(__file__),exe,context,deals,synthetic,trained,prerequisite,ROOT/'tools/research/loopback_research_validation.py']+[ROOT/'crates/solver/examples'/p for p in [
        'hu_sampled_batch_queries_control.rs','research_sampled/state.rs','research_sampled/poker_reference_v1.rs',
        'research_sampled/observation_v1.rs','research_sampled/network_v1.rs','research_sampled/policy_walk_v1.rs','research_sampled/batch_queries_v1.rs']]
    frozen={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in paths}
    reg=OUT/(PREFIX+'-registration.json');assert not reg.exists()
    save(reg,dict(inputs=frozen,maximum_seconds=180,maximum_raw_queries=100000,no_gpu=True,production_modified=False,
        scope='16 frozen physical deals, all legal public decision histories for each deal. Bounded per-batch observable queries, not a persistent strategy forest.',
        controls='Cached and direct policies/records must be exactly equal for both synthetic and fixed-data-fitted networks and four legal regret-matching variants.',
        negative_controls='Query budget, empty batch, duplicate physical card, missing query; cache cannot silently return uniform play.',
        caveat='Global suit canonicalization requires this registered symmetric context. This is neither new strategic evidence nor a GPU performance benchmark.'))
    output=OUT/(PREFIX+'-result.json');started=time.monotonic()
    run=subprocess.run([str(exe),str(context),str(deals),str(synthetic),str(trained),str(output)],cwd=ROOT,
        timeout=180,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
    (OUT/(PREFIX+'.log')).write_text(run.stdout+run.stderr,encoding='utf-8',newline='\n')
    assert run.returncode==0,run.stderr
    result=json.loads(output.read_text());assert result['passed']
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    save(OUT/(PREFIX+'-review.json'),dict(passed=True,inputs_verified=len(frozen),seconds=time.monotonic()-started,
        registration_sha256=sha(reg),result_sha256=sha(output),physical_poker_convergence_qualified=False,production_modified=False))
    print(run.stdout,end='')

if __name__=='__main__':main()
