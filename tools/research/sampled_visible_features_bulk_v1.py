"""Byte-compatible visible features with bulk decoding and per-call reuse.

Original card-summary code remains the reference. No persistent cache, new
features, changed history, hidden cards, precision change or training behavior.
"""
import numpy as np
from sampled_visible_poker_features_v1 import WIDTH, visible_summaries

_STARTS = np.asarray([v for i in range(7) for v in (19*i,19*i+14)]
                     + [133,135,139] + [155+6*i for i in range(19)],dtype=np.int16)
_WIDTHS = np.asarray([14,5]*7+[2,4,16]+[6]*19,dtype=np.int16)


def features(observations):
    """Validate every original one-hot group and emit the original float32 rows."""
    n=len(observations)
    if n==0:return np.zeros((0,269+WIDTH),dtype=np.float32)
    rows=[o['active_features'] for o in observations]
    # Check Python integer semantics before narrowing; bool, float and overflowing
    # integer inputs must not silently become valid indices through conversion.
    if any(len(row)!=36 or any(type(a) is not int or not 0<=a<269 for a in row)
           for row in rows):
        raise ValueError('Invalid original feature row')
    active=np.sort(np.asarray(rows,dtype=np.int16),axis=1)
    selected=active-_STARTS
    if np.any(selected<0) or np.any(selected>=_WIDTHS):
        raise ValueError('Invalid one-hot group')
    # Exactly one sorted element inside each disjoint interval also rejects
    # duplicate indices and groups with either missing or extra entries.
    ranks=selected[:,:14:2];suits=selected[:,1:14:2]
    missing=ranks==13
    if np.any(missing!=(suits==4)):
        raise ValueError('Mismatched missing card')
    counts=np.asarray([0,3,4,5],dtype=np.int16)[selected[:,15]]+2
    if np.any(missing!=(np.arange(7)[None,:]>=counts[:,None])):
        raise ValueError('Future-card leakage or incomplete visible board')
    history=selected[:,17:]
    after_end=np.maximum.accumulate(history==0,axis=1)
    if np.any(after_end & (history!=0)):
        raise ValueError('Noncontiguous public history')
    cards=ranks*4+suits
    cards[missing]=52
    ordered=np.sort(cards,axis=1)
    if np.any((ordered[:,1:]==ordered[:,:-1]) & (ordered[:,1:]!=52)):
        raise ValueError('Distinct visible cards required')
    # Summaries are invariant to order inside hole/board groups. Keep those
    # groups separate; the original one-hot inputs below retain every index.
    cards[:,:2]=np.sort(cards[:,:2],axis=1)
    cards[:,2:]=np.sort(cards[:,2:],axis=1)
    unique,inverse=np.unique(cards,axis=0,return_inverse=True)
    summaries=np.empty((len(unique),WIDTH),dtype=np.float32)
    for i,row in enumerate(unique.tolist()):
        summaries[i]=visible_summaries(row[:2],[c for c in row[2:] if c!=52])
    x=np.zeros((n,269+WIDTH),dtype=np.float32)
    x[np.arange(n)[:,None],active]=1.
    x[:,269:]=summaries[inverse]
    return x
