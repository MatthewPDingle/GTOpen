"""CPU fixtures for identical visible features; no training or fresh payoff tests."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import hashlib,json,sys,time
from pathlib import Path
import numpy as np

ROOT=Path('T:/Dev/GTOpen/tools/research')
sys.path.append(str(ROOT))
from sampled_visible_poker_features_v1 import visible_summaries
from sampled_visible_features_bulk_v1 import features as reference_features
from visible_summary_vector_v1 import summaries

def control():
    started=time.monotonic();rng=np.random.default_rng(9294201)
    # Suit groups, wheel/straight flush, two trips, three pairs and board-only hands.
    examples=[
        [48,49,50,51,44,40,36], [48,49,50,44,45,46,40],
        [48,49,44,45,40,41,36], [48,0,4,8,12,20,24],
        [0,5,8,13,16,52,52], [0,5,24,28,32,36,40],
        [48,45,40,37,32,52,52], [0,1,8,13,18,23,28],
        [0,5,8,13,16,21,24], [0,5,48,49,50,51,44],
        [48,49,52,52,52,52,52]]
    rows=[]
    for size in (2,5,6,7):
        for _ in range(10000):
            rows.append([*map(int,rng.choice(52,size=size,replace=False)),*[52]*(7-size)])
    cards=np.asarray(examples+rows,dtype=np.int16)
    before=time.monotonic();reference=np.array([visible_summaries(list(map(int,r[:2])),[int(c) for c in r[2:] if c!=52]) for r in cards])
    old_seconds=time.monotonic()-before
    before=time.monotonic();candidate=summaries(cards);new_seconds=time.monotonic()-before
    assert candidate.dtype==reference.dtype==np.float32 and candidate.shape==reference.shape
    assert np.array_equal(candidate,reference)
    assert set(np.argmax(reference[np.any(reference,axis=1),:9],axis=1))==set(range(9))
    # Every visible subset can be reordered within its private/public groups.
    shuffled=cards.copy();shuffled[:,:2]=shuffled[:,:2][:,::-1]
    for n in (5,6,7):
        mask=np.sum(cards!=52,axis=1)==n;shuffled[mask,2:n]=shuffled[mask,2:n][:,::-1]
    assert np.array_equal(summaries(shuffled),candidate)
    rejected=0
    for invalid in (np.zeros((1,6),dtype=np.int16),np.zeros((1,7),dtype=float),
        np.array([[0,1,2,52,52,52,52]]),np.array([[0,0,2,3,4,52,52]]),
        np.array([[0,1,52,2,3,4,52]]),np.array([[-1,1,2,3,4,52,52]]),
        np.array([[0,1,2,3,54,52,52]]),np.zeros((1,7),dtype=bool)):
        try:summaries(invalid)
        except ValueError:rejected+=1
        else:raise AssertionError('Invalid cards accepted')
    assert np.array_equal(summaries(np.zeros((0,7),dtype=np.int16)),np.zeros((0,33),dtype=np.float32))
    result=dict(passed=True,rows=len(cards),all_categories=True,exact_float32_features=True,
        card_order_invariance=True,invalid_inputs_rejected=rejected,reference_seconds=old_seconds,
        vector_seconds=new_seconds,observed_ratio=old_seconds/new_seconds,seconds=time.monotonic()-started,
        gpu_used=False,new_payoff_test_deals=0,training_modified=False,accuracy_claim=False,
        limitation='Synthetic CPU feature control only; full reservoir and CUDA fit parity remain required.',
        inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),Path(__file__).with_name('visible_summary_vector_v1.py'),ROOT/'sampled_visible_poker_features_v1.py')})
    print(json.dumps(result),flush=True)

if __name__=='__main__':control()
