"""Exhaustive finite-domain proof checks, independent of poker test outcomes."""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import random
import time
from bounded_pair_proposal_v1 import proposal,observation
from board_prefix_publication_v1 import atomic_json

OUT=Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
NAME='bounded-pair-proposal-control-v1'
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json')


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not REG.exists() and not RESULT.exists(),'Preserve old control evidence'
    inputs={str(p):sha(p) for p in (Path(__file__),Path(__file__).with_name('bounded_pair_proposal_v1.py'),
                                   OUT/'REACH-WEIGHTED-EVALUATION-DESIGN.md')}
    atomic_json(REG,dict(inputs=inputs,seed=29101,cases=64,maximum_seconds=20,
        exact_rational_arithmetic=True,new_poker_deals=0,gpu_used=False,
        purpose='Finite-support unbiasedness and bounds only; no qualified floating sampler or poker implementation.'))
    start=time.monotonic();rng=random.Random(29101);checks=0;rejections=0
    for case in range(64):
        masses=[rng.randrange(0,20) for _ in range(8)];masses[0]=1000000 if case%4==0 else 1
        p=[F(v,sum(masses)) for v in masses]
        lower=[];upper=[];outcomes=[];chance=[]
        for i in range(8):
            lower.append([F(rng.randrange(-100,101),7) for _ in range(8)])
            upper.append([v+(F(0) if i%3==0 else F(rng.randrange(1,501),13)) for v in lower[-1]])
            outcomes.append([lower[-1],[(a+b)/2 for a,b in zip(lower[-1],upper[-1])],upper[-1]])
            w=[rng.randrange(1,10) for _ in range(3)];chance.append([F(v,sum(w)) for v in w])
        plan=proposal(p,lower,upper);assert sum(plan['q'])==1
        target=[sum(p[i]*chance[i][b]*outcomes[i][b][j] for i in range(8) for b in range(3)) for j in range(8)]
        actual=[F(0)]*8
        for i in range(8):
            if not plan['q'][i]:continue
            for b in range(3):
                y=observation(plan,i,outcomes[i][b])
                for j,v in enumerate(y):
                    assert plan['center'][j]-plan['z']<=v<=plan['center'][j]+plan['z']
                    actual[j]+=plan['q'][i]*chance[i][b]*v;checks+=1
        assert actual==target
    # Every positive-mass interval is a point: analytical answer, no draws.
    deterministic=proposal([F(1,3),F(2,3),0],[[1,-5],[7,4],[-100,-100]],[[1,-5],[7,4],[100,100]])
    assert deterministic['deterministic'] and deterministic['center']==(F(5),F(1))
    assert not any(deterministic['q'])
    invalid=(lambda:proposal([F(1,2)],[[0]],[[1]]),
             lambda:proposal([2,-1],[[0],[0]],[[1],[1]]),
             lambda:proposal([1],[[2]],[[1]]),
             lambda:proposal([1],[[0,1]],[[2]]),
             lambda:proposal([1.0],[[0]],[[1]]),
             lambda:observation(deterministic,0,[1,-5]),
             lambda:observation(proposal([1],[[0]],[[1]]),0,[2]))
    for fn in invalid:
        try:fn()
        except ValueError:rejections+=1
        else:raise AssertionError('Invalid plan/outcome accepted')
    assert time.monotonic()-start<20
    for p,h in inputs.items():assert sha(p)==h
    result=dict(passed=True,registration_sha256=sha(REG),cases=64,contrasts_per_case=8,
        exact_expectation_equalities=512,pointwise_bound_checks=checks,invalid_rejections=rejections,
        deterministic_zero_support_case=True,seconds=time.monotonic()-start,gpu_used=False,new_poker_deals=0,
        poker_sampler_qualified=False,floating_error_bound_qualified=False,accuracy_claim=False)
    atomic_json(RESULT,result);print(json.dumps(result),flush=True)


if __name__=='__main__':main()
