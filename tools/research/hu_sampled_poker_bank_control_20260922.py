"""Freeze the physical-observation model-bank mixture control; CPU only."""
import hashlib
import json
from pathlib import Path
import subprocess
import time
from loopback_research_validation import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-poker-bank-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')

def main():
    assert idle()
    executable=ROOT/'target/release/examples/hu_sampled_poker_bank_control.exe'
    context=OUT/'bb-context-candidate.json';deals=OUT/'sampled-poker-v1-fixture.json';fixture=OUT/'sampled-network-adapter-v1-fixture.json'
    prerequisite=OUT/'sampled-network-adapter-v1-review.json';assert json.loads(prerequisite.read_text())['passed']
    paths=[Path(__file__),executable,context,deals,fixture,prerequisite,ROOT/'tools/research/loopback_research_validation.py']+[ROOT/'crates/solver/examples'/p for p in [
        'hu_sampled_poker_bank_control.rs','research_sampled/state.rs','research_sampled/poker_reference_v1.rs',
        'research_sampled/observation_v1.rs','research_sampled/network_v1.rs','research_sampled/policy_bank_v1.rs']]
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths};reg=OUT/(PREFIX+'-registration.json');assert not reg.exists()
    save(reg,dict(inputs=frozen,maximum_seconds=180,no_gpu=True,production_modified=False,
        scope='Fixed physical BB/BTN subtree, synthetic policy models. Compare full terminal distributions for four fixed physical deals.',
        oracle='Independently draw one model per player at root and hold it throughout the trajectory. Sum all nine model-pair distributions.',
        candidate='At each observable query, derive own earlier decisions, multiply each model by own prior reach and its weight, then average its current policy.',
        model_weights=[[1,2,4],[3,2,1]],probability_tolerance=1e-12,
        negative_controls='Naive per-decision probability averaging must differ; zero own-reach model cannot supply evidence at an unreachable query.',
        caveat='Implementation identity, not poker strength or a bound on a learned policy. Global suit symmetry requires the registered context.'))
    output=OUT/(PREFIX+'-result.json');started=time.monotonic()
    run=subprocess.run([str(executable),str(context),str(deals),str(fixture),str(output)],cwd=ROOT,
        timeout=180,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
    (OUT/(PREFIX+'.log')).write_text(run.stdout+run.stderr,encoding='utf-8',newline='\n')
    assert run.returncode==0,run.stderr
    result=json.loads(output.read_text());assert result['passed']
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    save(OUT/(PREFIX+'-review.json'),dict(passed=True,inputs_verified=len(frozen),seconds=time.monotonic()-started,
        registration_sha256=sha(reg),result_sha256=sha(output),physical_poker_convergence_qualified=False,production_modified=False))
    print(run.stdout,end='')

if __name__=='__main__':main()
