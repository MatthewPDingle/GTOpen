"""Physical deals for integrated sampled-poker qualification; no fitted policy."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import hashlib
import itertools
import json
from pathlib import Path
import time
import numpy as np
from storage_strategic_common_prior_20260920 import PAIRS, MASKS, CLASSES, COUNTS

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    target=OUT/'sampled-poker-v1-fixture.json'
    assert not target.exists()
    paths=[OUT/'bb-context-candidate.json',OUT/'capacity-existing112-manifest.json',
           OUT/'sampled-deal-oracle-v1-result.json',Path(__file__),
           ROOT/'tools/research/storage_strategic_common_prior_20260920.py']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths}
    context=json.loads(paths[0].read_text());boards=json.loads(paths[1].read_text())['boards']
    reference=json.loads(paths[2].read_text())['contexts'][1]
    assert reference['context']=='bb_context'
    w=np.array(context['incoming_class_mass'])[:,CLASSES]/COUNTS[CLASSES]
    w/=w.max(1)[:,None];w[w<1e-5]=0
    live=[];first=[];masses=[];cards=[]
    for b,ref in zip(boards,reference['rows'],strict=True):
        cs=[4*'23456789TJQKA'.index(b['board'][i])+'cdhs'.index(b['board'][i+1]) for i in (0,2,4)]
        mask=sum(1<<c for c in cs);row=w*((MASKS&np.uint64(mask))==0)
        counts=np.bincount(PAIRS.ravel(),weights=np.repeat(row[1],2),minlength=52)
        available=np.maximum(row[1].sum()-counts[PAIRS[:,0]]-counts[PAIRS[:,1]]+row[1],0)
        marginal=row[0]*available;mass=float(marginal.sum())
        assert b['board']==ref['board'] and abs(mass/ref['compatible_pair_mass']-1)<1e-12
        live.append(row);first.append(marginal/mass);masses.append(mass);cards.append(cs)
    bp=np.array([b['weight'] for b in boards])*masses;bp/=bp.sum()
    assert np.max(abs(bp-np.array([r['board_probability'] for r in reference['rows']])))<1e-14
    rng=np.random.Generator(np.random.PCG64(2026092201))
    permutations=list(itertools.permutations(range(4)))
    deals=[];board_counts=np.zeros(112,dtype=int);perm_counts=np.zeros(24,dtype=int)
    class_counts=np.zeros((2,169),dtype=int)
    for _ in range(8192):
        b=int(rng.choice(112,p=bp));i=int(rng.choice(len(PAIRS),p=first[b]))
        second=live[b][1]*((MASKS&MASKS[i])==0);second/=second.sum()
        j=int(rng.choice(len(PAIRS),p=second));p=int(rng.integers(24));perm=permutations[p]
        canonical=[int(x) for x in PAIRS[i]]+[int(x) for x in PAIRS[j]]+cards[b]
        physical=[4*(c//4)+perm[c%4] for c in canonical]
        remaining=[c for c in range(52) if c not in physical]
        physical.extend(int(c) for c in rng.choice(remaining,size=2,replace=False))
        assert len(set(physical))==9 and all(0<=c<52 for c in physical)
        physical[:2]=sorted(physical[:2]);physical[2:4]=sorted(physical[2:4]);physical[4:7]=sorted(physical[4:7])
        assert w[0,i]>0 and w[1,j]>0
        board_counts[b]+=1;perm_counts[p]+=1
        class_counts[0,CLASSES[i]]+=1;class_counts[1,CLASSES[j]]+=1
        deals.append(physical)
    expected=8192*bp
    # Sanity screen, not proof of exact sampling or a strategic statistical test.
    standardized=abs(board_counts-expected)/np.sqrt(expected*(1-bp))
    assert float(standardized.max())<8 and (board_counts>0).all() and (perm_counts>0).all()
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    result={'inputs':frozen,'created_at_unix':time.time(),'seed':2026092201,
        'generator':'numpy PCG64; categorical draws from qualified law; shared uniform suit permutation; uniform ordered turn/river without replacement',
        'numpy_version':np.__version__,'deals':deals,'board_counts':board_counts.tolist(),
        'suit_permutation_counts':perm_counts.tolist(),'sampled_classes':(class_counts>0).sum(1).tolist(),
        'max_board_count_standardized_deviation':float(standardized.max()),
        'scope':'Qualification fixture. Full target support retained; finite sample need not visit every hand/context. Not a convergence result.'}
    target.write_text(json.dumps(result,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['deals','inputs','board_counts','suit_permutation_counts']}))

if __name__=='__main__':main()
