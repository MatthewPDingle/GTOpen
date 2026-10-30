"""Freeze and qualify lossless physical-poker observation inputs; CPU only."""
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-observation-v1'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')

def reference(hi,lo):
    actor=lo>>42
    assert actor in (0,1)
    cards=[lo>>(6*i)&63 for i in range(7)]
    candidates=[]
    for perm in itertools.permutations(range(4)):
        c=[63 if c==63 else 4*(c//4)+perm[c%4] for c in cards]
        c[:2]=sorted(c[:2]);c[2:5]=sorted(c[2:5])
        code=(actor<<42)+sum(v<<(6*i) for i,v in enumerate(c))
        candidates.append((code,c))
    code,c=min(candidates)
    if hi<2**63:phase=0;public=hi-1;history=[]
    else:
        public=hi%16
        digits=oct((hi-2**63)//16)[2:]
        assert digits[0]=='1'
        history=[int(t) for t in digits[1:]]
        phase=1+(c[5]!=63)+(c[6]!=63)
    active=[];offset=0
    for v in c:
        active.append(offset+(13 if v==63 else v//4));offset+=14
        active.append(offset+(4 if v==63 else v%4));offset+=5
    for width,value in [(2,actor),(4,phase),(16,public)]:active.append(offset+value);offset+=width
    for token in history+[0]*(19-len(history)):active.append(offset+token);offset+=6
    assert offset==269
    return code,active

def main():
    executable=ROOT/'target/release/examples/hu_sampled_observation_control.exe'
    context=OUT/'bb-context-candidate.json';fixture=OUT/'sampled-poker-v1-fixture.json'
    paths=[Path(__file__),executable,context,fixture,
        ROOT/'crates/solver/examples/hu_sampled_observation_control.rs',
        ROOT/'crates/solver/examples/research_sampled/observation_v1.rs',
        ROOT/'crates/solver/examples/research_sampled/poker_reference_v1.rs',
        ROOT/'crates/solver/examples/research_sampled/state.rs']
    reg=OUT/(PREFIX+'-registration.json');assert not reg.exists()
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths}
    save(reg,dict(inputs=frozen,maximum_seconds=120,production_modified=False,
        scope='CPU-only observation and legal-action controls; no fitting, GPU work or strategic evaluation.',
        symmetry_scope='Fixed class-only incoming ranges and uniformly permuted suits; not arbitrary suit-specific locked ranges.',
        context_scope='Registered BB/BTN subtree only. Node IDs and action tokens require this context hash.',
        feature_width=269,feature_contents='Own two cards, visible flop/ordered turn/river, actor, street, public preflop node or postflop branch, complete public action history. Unknown cards explicit.'))
    output=OUT/(PREFIX+'-result.json');started=time.perf_counter()
    run=subprocess.run([str(executable),str(context),str(fixture),str(output)],cwd=ROOT,
        capture_output=True,text=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    (OUT/(PREFIX+'.log')).write_text(run.stdout+run.stderr,encoding='utf-8',newline='\n')
    assert run.returncode==0,run.stderr
    result=json.loads(output.read_text());assert result['passed']
    for row in result['golden']:
        hi,lo=int(row['input_hi']),int(row['input_lo'])
        canonical,active=reference(hi,lo)
        assert str(canonical)==row['canonical_lo'] and str(hi)==row['canonical_hi']
        assert active==row['active_features']
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    save(OUT/(PREFIX+'-review.json'),dict(passed=True,inputs_verified=len(frozen),
        independent_golden_comparisons=len(result['golden']),registration_sha256=sha(reg),
        result_sha256=sha(output),seconds=time.perf_counter()-started,
        physical_poker_training_qualified=False,production_modified=False))
    print(run.stdout,end='')

if __name__=='__main__':main()
