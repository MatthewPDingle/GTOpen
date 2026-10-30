"""Freeze synthetic policy fixtures and verify physical traversal integration."""
import hashlib
import json
from pathlib import Path
import subprocess
import time
import numpy as np
from loopback_research_validation import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-network-adapter-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')

def main():
    assert idle()
    observation=OUT/'sampled-observation-v1-result.json';reference=json.loads(observation.read_text());assert reference['passed']
    artifact=OUT/(PREFIX+'-fixture.json');assert not artifact.exists()
    rng=np.random.default_rng(2026092301);networks=[]
    for player in range(2):
        n={}
        for layer,(before,after) in enumerate([(269,64),(64,64),(64,4)]):
            n[f'w{layer}']=rng.uniform(-.04,.04,(after,before)).astype(np.float32).flatten().tolist()
            n[f'b{layer}']=(rng.uniform(-.02,.02,after).astype(np.float32) if layer<2 else np.array([.7,.5,.3,.2],dtype=np.float32)).tolist()
        networks.append(n)
    golden=[]
    for row in reference['golden']:
        lo=int(row['input_lo']);net=networks[(lo>>42)&1];x=np.zeros(269,dtype=np.float32);x[row['active_features']]=1.
        for layer,shape in enumerate([(64,269),(64,64),(4,64)]):
            w=np.asarray(net[f'w{layer}'],dtype=np.float32).reshape(shape);b=np.asarray(net[f'b{layer}'],dtype=np.float32)
            x=w@x+b
            if layer<2:x=np.maximum(x,0)
        values=x.astype(float);n=row['legal_actions'];p=np.zeros(4);p[:n]=np.maximum(values[:n],0)
        if p.sum()>0:p/=p.sum()
        else:p[int(np.argmax(values[:n]))]=1.
        golden.append(dict(hi=row['input_hi'],lo=row['input_lo'],n=n,scores=values.tolist(),policy=p.tolist()))
    save(artifact,dict(seed=2026092301,networks=networks,golden=golden,deal_indices=[i*503%8192 for i in range(16)],
        variants=['positive mixed neural scores','negative scores highest legal fallback','zero scores legal tie fallback','illegal highest score must be masked'],
        trained=False))
    executable=ROOT/'target/release/examples/hu_sampled_network_control.exe'
    context=OUT/'bb-context-candidate.json';deals=OUT/'sampled-poker-v1-fixture.json'
    paths=[Path(__file__),executable,artifact,context,deals,observation,
        ROOT/'tools/research/loopback_research_validation.py']+[ROOT/'crates/solver/examples'/p for p in [
        'hu_sampled_network_control.rs','research_sampled/state.rs','research_sampled/poker_reference_v1.rs',
        'research_sampled/observation_v1.rs','research_sampled/network_v1.rs','research_sampled/policy_walk_v1.rs']]
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths};reg=OUT/(PREFIX+'-registration.json');assert not reg.exists()
    save(reg,dict(inputs=frozen,maximum_seconds=180,no_gpu=True,production_modified=False,
        scope='Fixed BB/BTN geometry, synthetic 269-64-64-4 float32 weights. Neural policy callback sees only observable key and legal arity.',
        checks='Independent NumPy scores; all four policy families compared record by record against frozen scalar table traversal.',
        tolerances=dict(score_and_policy=2e-6,traversal_values=1e-10),
        caveat='Neither learned poker ranges nor GPU inference performance is qualified. Full tables exist only in the finite verification oracle.'))
    result=OUT/(PREFIX+'-result.json');started=time.monotonic()
    run=subprocess.run([str(executable),str(context),str(deals),str(artifact),str(result)],cwd=ROOT,
        timeout=180,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
    (OUT/(PREFIX+'.log')).write_text(run.stdout+run.stderr,encoding='utf-8',newline='\n')
    assert run.returncode==0,run.stderr
    data=json.loads(result.read_text());assert data['passed']
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    save(OUT/(PREFIX+'-review.json'),dict(passed=True,inputs_verified=len(frozen),seconds=time.monotonic()-started,
        registration_sha256=sha(reg),result_sha256=sha(result),physical_poker_convergence_qualified=False,production_modified=False))
    print(run.stdout,end='')

if __name__=='__main__':main()
