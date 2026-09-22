"""Fresh physical deals for a bounded sparse-table growth measurement."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import hashlib
import itertools
import json
from pathlib import Path
import struct
import time
import numpy as np
from storage_strategic_common_prior_20260920 import PAIRS,MASKS,CLASSES,COUNTS

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-growth-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    started=time.monotonic();target=OUT/(PREFIX+'-deals.bin');meta=OUT/(PREFIX+'-deals.json')
    assert not target.exists() and not meta.exists()
    paths=[OUT/'bb-context-candidate.json',OUT/'capacity-existing112-manifest.json',
        OUT/'sampled-deal-oracle-v1-result.json',Path(__file__),
        ROOT/'tools/research/storage_strategic_common_prior_20260920.py']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths}
    context=json.loads(paths[0].read_text());boards=json.loads(paths[1].read_text())['boards']
    refs=json.loads(paths[2].read_text())['contexts'][1]['rows']
    weights=np.array(context['incoming_class_mass'])[:,CLASSES]/COUNTS[CLASSES]
    weights/=weights.max(1)[:,None];weights[weights<1e-5]=0
    lives=[];first=[];masses=[];cards=[]
    for board,ref in zip(boards,refs,strict=True):
        cs=[4*'23456789TJQKA'.index(board['board'][i])+'cdhs'.index(board['board'][i+1]) for i in (0,2,4)]
        legal=(MASKS&np.uint64(sum(1<<c for c in cs)))==0;live=weights*legal
        by_card=np.bincount(PAIRS.ravel(),weights=np.repeat(live[1],2),minlength=52)
        available=np.maximum(live[1].sum()-by_card[PAIRS[:,0]]-by_card[PAIRS[:,1]]+live[1],0)
        marginal=live[0]*available;mass=float(marginal.sum())
        assert board['board']==ref['board'] and abs(mass/ref['compatible_pair_mass']-1)<1e-12
        lives.append(live);first.append(marginal/mass);masses.append(mass);cards.append(cs)
    bp=np.array([b['weight'] for b in boards])*masses;bp/=bp.sum()
    assert np.max(abs(bp-np.array([r['board_probability'] for r in refs])))<1e-14
    rng=np.random.Generator(np.random.PCG64(2026092203));perms=list(itertools.permutations(range(4)))
    count=262144;board_counts=np.zeros(112,dtype=int);perm_counts=np.zeros(24,dtype=int);class_counts=np.zeros((2,169),dtype=int)
    data=bytearray(b'GTDEAL01'+struct.pack('<Q',count))
    for _ in range(count):
        b=int(rng.choice(112,p=bp));i=int(rng.choice(len(PAIRS),p=first[b]))
        second=lives[b][1]*((MASKS&MASKS[i])==0);second/=second.sum();j=int(rng.choice(len(PAIRS),p=second))
        p=int(rng.integers(24));perm=perms[p]
        cs=[int(c) for c in PAIRS[i]]+[int(c) for c in PAIRS[j]]+cards[b]
        cs=[4*(c//4)+perm[c%4] for c in cs]
        remaining=[c for c in range(52) if c not in cs];cs.extend(int(c) for c in rng.choice(remaining,2,replace=False))
        assert len(set(cs))==9
        cs[:2]=sorted(cs[:2]);cs[2:4]=sorted(cs[2:4]);cs[4:7]=sorted(cs[4:7]);data.extend(cs)
        board_counts[b]+=1;perm_counts[p]+=1;class_counts[0,CLASSES[i]]+=1;class_counts[1,CLASSES[j]]+=1
    assert len(data)==16+count*9
    assert all(sha(ROOT/p)==h for p,h in frozen.items());target.write_bytes(data)
    result={'inputs':frozen,'deals':count,'seed':2026092203,'numpy_version':np.__version__,
        'generator':'PCG64; qualified joint board/private law; shared uniform suit permutation; uniform ordered runout without replacement',
        'binary_format':'GTDEAL01 magic, little-endian u64 deal count, 9 u8 cards/deal: own0 pair, own1 pair, sorted flop, turn, river',
        'sha256':sha(target),'generation_seconds':time.monotonic()-started,
        'board_counts':board_counts.tolist(),'suit_permutation_counts':perm_counts.tolist(),
        'sampled_classes':(class_counts>0).sum(1).tolist(),
        'note':'Full 169/96 class support remains; this is a fresh training/resource sample, not a held-out strategic evaluation.'}
    # Report actual support by class rather than physical-combo count.
    result['full_supported_classes']=[len(set(int(CLASSES[i]) for i in np.flatnonzero(weights[p]>0))) for p in range(2)]
    meta.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['inputs','board_counts','suit_permutation_counts']}))

if __name__=='__main__':main()
