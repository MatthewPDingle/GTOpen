"""Exact uniform-opponent river oracle for a restricted call/fold diagnostic."""
from collections import Counter
from itertools import combinations, permutations
import math
import numpy as np

def rank_five(cards):
    if len(cards)!=5 or len(set(cards))!=5 or any(type(c) is not int or not 0<=c<52 for c in cards):
        raise ValueError('Five distinct cards required')
    ranks=sorted((c//4+2 for c in cards),reverse=True)
    groups=sorted(((n,r) for r,n in Counter(ranks).items()),reverse=True)
    flush=len({c%4 for c in cards})==1
    unique=sorted(set(ranks))
    straight=(unique[-1] if len(unique)==5 and unique[-1]-unique[0]==4 else
              5 if unique==[2,3,4,5,14] else 0)
    if flush and straight: category,kickers=8,[straight]
    elif groups[0][0]==4: category,kickers=7,[groups[0][1],groups[1][1]]
    elif [x[0] for x in groups]==[3,2]: category,kickers=6,[groups[0][1],groups[1][1]]
    elif flush: category,kickers=5,ranks
    elif straight: category,kickers=4,[straight]
    elif groups[0][0]==3: category,kickers=3,[groups[0][1]]+sorted((r for n,r in groups[1:]),reverse=True)
    elif [x[0] for x in groups]==[2,2,1]: category,kickers=2,sorted((r for n,r in groups if n==2),reverse=True)+[r for n,r in groups if n==1]
    elif groups[0][0]==2: category,kickers=1,[groups[0][1]]+sorted((r for n,r in groups[1:]),reverse=True)
    else: category,kickers=0,ranks
    return category*15**5+sum(r*15**(4-i) for i,r in enumerate(kickers))

def rank_seven(cards):
    if len(cards)!=7 or len(set(cards))!=7: raise ValueError('Seven distinct cards required')
    return max(rank_five(list(five)) for five in combinations(cards,5))

def board_group(board):
    if len(board)!=5 or len(set(board))!=5 or any(type(c) is not int or not 0<=c<52 for c in board):
        raise ValueError('Five distinct board cards required')
    return min(tuple(sorted(c//4*4+p[c%4] for c in board)) for p in permutations(range(4)))

def conditional_counts(board,hands,ranks):
    board_group(board)
    expected=np.asarray(list(combinations([c for c in range(52) if c not in board],2)),dtype=np.int64)
    h=np.asarray(hands);r=np.asarray(ranks)
    if h.shape!=(1081,2) or h.dtype.kind not in 'iu' or not np.array_equal(h,expected):
        raise ValueError('Complete ordered board-legal holding list required')
    if r.shape!=(1081,) or r.dtype.kind not in 'iu' or np.any(r<0):
        raise ValueError('Nonnegative exact integer ranks required')
    legal=((h[:,0,None]!=h[None,:,0])&(h[:,0,None]!=h[None,:,1])&
           (h[:,1,None]!=h[None,:,0])&(h[:,1,None]!=h[None,:,1]))
    counts=np.stack(((legal&(r[:,None]>r[None,:])).sum(1),
                     (legal&(r[:,None]==r[None,:])).sum(1),
                     (legal&(r[:,None]<r[None,:])).sum(1)),axis=1)
    if not np.all(counts.sum(1)==990): raise ValueError('Opponent enumeration mass mismatch')
    if counts[:,0].sum()!=counts[:,2].sum(): raise ValueError('Pair complement mismatch')
    return counts

def price(row):
    if row['phase']!=3 or [a['kind'] for a in row['actions']]!=['fold','call']:
        raise ValueError('Exactly two river actions, fold and terminal call, required')
    p,c,rate,cap=(row[k] for k in ('pot','call_cost','rake_fraction','rake_cap'))
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in (p,c,rate,cap)):
        raise ValueError('Finite public price required')
    if p<=0 or c<=0 or not 0<=rate<=1 or cap<0: raise ValueError('Invalid public price')
    if row['actions'][0]['increment']!=0 or not math.isclose(row['actions'][1]['increment'],c):
        raise ValueError('Action price mismatch')
    rake=min(cap,rate*(p+c)) if cap>0 else rate*(p+c)
    net=p+c-rake
    if net<=0: raise ValueError('Positive distributable pot required')
    return dict(pot=p,call_cost=c,rake=rake,net_pot=net,equity_threshold=c/net,
                endpoints_loss_tie_win=[-c,net/2-c,net-c])

def call_advantage(counts,row):
    n=np.asarray(counts)
    if n.ndim!=2 or n.shape[1]!=3 or n.dtype.kind not in 'iu' or np.any(n<0) or not np.all(n.sum(1)==990):
        raise ValueError('Exact win/tie/loss counts with mass 990 required')
    g=price(row)
    endpoints=np.asarray(g['endpoints_loss_tie_win'])[[2,1,0]]
    return n.astype(np.float64)@endpoints/990

def decision_regret(call_probability,advantage):
    p,d=np.broadcast_arrays(np.asarray(call_probability,dtype=float),np.asarray(advantage,dtype=float))
    if not np.isfinite(p).all() or not np.isfinite(d).all() or np.any((p<0)|(p>1)):
        raise ValueError('Finite legal call probabilities and advantages required')
    return np.maximum(d,0)-p*d
