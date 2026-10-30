"""Exact zero-sum counterexample: local convergence need not preserve root play.

Independent mathematical control, not a reproduction of the poker result.
Uses rational arithmetic and exhaustive pure best responses.
"""
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'


def value(enter, x):
    # A and B are equally likely private types, visible only to Player 1.
    # Fold pays zero. On Enter, A pays zero against either action; B pays
    # +1 against X and -1 against Y. Player 2 cannot observe A versus B.
    return F(1,2)*enter[1]*(2*x-1)


def evaluate(enter, x):
    v = value(enter,x)
    p1_best = max(value(s,x) for s in product([F(0),F(1)],repeat=2))
    p2_best = min(value(enter,y) for y in [F(0),F(1)])
    probability = sum(enter)/2
    # Player 1 has no action within the continuation. Player 2 chooses
    # one action for both private types; it cannot maximize by hidden type.
    post_gap = v-p2_best
    assert post_gap >= 0 and p1_best-v >= 0
    return dict(value=v,full_gap=p1_best-p2_best,
                p1_root_gain=p1_best-v,p2_gain=post_gap,
                reached_post_gap=post_gap,
                conditional_post_gap=post_gap/probability)


def main():
    results=[]
    for epsilon in [F(0),F(1,1000000)]:
        enter=(F(1),epsilon)
        baseline=evaluate(enter,F(0))
        reconstructed=evaluate(enter,F(1))
        assert baseline['full_gap']==epsilon/2
        assert reconstructed['full_gap']==(1+epsilon)/2
        assert reconstructed['reached_post_gap']==epsilon
        assert reconstructed['conditional_post_gap']==2*epsilon/(1+epsilon)
        assert reconstructed['p1_root_gain']==(1-epsilon)/2
        results.append(dict(rare_type_entry=str(epsilon),
                            baseline={k:str(v) for k,v in baseline.items()},
                            rebuilt={k:str(v) for k,v in reconstructed.items()}))
    result=dict(passed=True,arithmetic='exact fractions',
                zero_sum=True,hidden_type_respected=True,cases=results,
                interpretation='A mathematical counterexample, not evidence that this mechanism caused the poker transfer result. The zero-entry case has exact local equilibria; the positive-entry case has small but nonzero local residual.')
    target=OUT/'reconstruction-toy-control.json'
    with target.open('x') as f:
        json.dump(result,f,indent=2)
    print(json.dumps(result))


if __name__=='__main__':
    main()
