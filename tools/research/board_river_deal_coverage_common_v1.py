"""Frozen experiment identifiers and unbiased finite-posterior label sampling."""
import hashlib
from pathlib import Path
import numpy as np
from board_later_fit_holdout_run_v1 import ROOT,OUT,LOCK,OTHER,read,sha,verify

PREFIX='board-river-deal-coverage-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
CONTEXT=OUT/'bb-context-candidate.json'
PLAN=OUT/'BOARD-RIVER-DEAL-COVERAGE-PLAN.md'
LIMIT=2_000_000_000
DEALS=224
TRAIN_DEALS=192
DEAL_SEED=9289962
SELECT_SEED=9289963
LABEL_SEED=9289964
MODEL_SEEDS=(9289971,9289972,9289973)
BANDS=(('under10',0.,10.),('10to50',10.,50.),('50to100',50.,100.),('100to200',100.,200.),('200plus',200.,float('inf')))
EXE=ROOT/'target/release/examples/hu_river_conditional_queries_v1.exe'
QUERY_EXE=ROOT/'target/release/examples/hu_sampled_bank_bridge.exe'


def sampled_labels(case_id,bank,posterior,outcomes,endpoints):
    p=np.asarray(posterior,dtype=np.float64);y=np.asarray(endpoints,dtype=np.float64)[np.asarray(outcomes,dtype=int)]
    assert p.ndim==1 and y.shape==p.shape and np.isfinite(p).all() and np.all(p>=0)
    assert np.isfinite(y).all() and abs(p.sum()-1)<1e-12
    expected=float(p@y);variance=float(p@((y-expected)**2));samples=[]
    for repeat in range(3):
        digest=hashlib.sha256(f'{LABEL_SEED}|{case_id}|{bank}|{repeat}'.encode()).digest()
        seed=int.from_bytes(digest[:16],'big');rng=np.random.Generator(np.random.PCG64(seed))
        indices=rng.choice(len(p),size=16,replace=True,p=p)
        assert np.all(p[indices]>0)
        samples.append(dict(repetition=repeat,seed=str(seed),opponent_indices=indices.tolist(),
            one=float(y[indices[0]]),sixteen=float(y[indices].mean())))
    return dict(exact=expected,single_sample_variance=variance,mean16_variance=variance/16,samples=samples)


def canonical_board(cards):
    # Full board as a suit-isomorphism group, independent of private cards.
    import itertools
    assert len(cards)==5 and len(set(cards))==5
    return min(tuple(sorted(c//4*4+perm[c%4] for c in cards)) for perm in itertools.permutations(range(4)))

OLD_PREFIX='board-river-target-learning-v1'
OLD_STORE=Path('S:/GTOpen-research')/OLD_PREFIX
ASSIGN_SEED=9289961
