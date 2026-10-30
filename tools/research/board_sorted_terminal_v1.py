"""Float64 fixed-river terminal reductions with explicit card removal.

Returns unnormalized counterfactual masses. No range normalization, policy
inputs, chance weights, tree propagation or GPU inference is implemented here.
"""
import numpy as np


def checked(hands,ranks):
    h=np.asarray(hands);r=np.asarray(ranks)
    if h.ndim!=2 or h.shape[1]!=2 or r.shape!=(len(h),):
        raise ValueError('One rank per two-card holding required')
    if h.dtype.kind not in 'iu' or r.dtype.kind not in 'iu' or np.any(h<0) or np.any(h>=52):
        raise ValueError('Integer physical cards and strengths required')
    if np.any(h[:,0]>=h[:,1]) or len(np.unique(h[:,0]*52+h[:,1]))!=len(h):
        raise ValueError('Unique sorted two-card holdings required')
    return h.astype(np.int64),r


def masses(hero_hands,hero_ranks,opponent_hands,opponent_ranks,opponent_reach):
    h,hr=checked(hero_hands,hero_ranks);o,orr=checked(opponent_hands,opponent_ranks)
    reach=np.asarray(opponent_reach,dtype=np.float64)
    if reach.shape!=(len(o),) or not np.isfinite(reach).all() or np.any(reach<0):
        raise ValueError('Finite nonnegative reach for each opponent holding required')
    order=np.argsort(orr,kind='stable');o=o[order];orr=orr[order];reach=reach[order]
    prefix=np.r_[0.,np.cumsum(reach)]
    cards=np.arange(52)[:,None]
    contains=(o[None,:,0]==cards)|(o[None,:,1]==cards)
    bycard=np.concatenate([np.zeros((52,1)),np.cumsum(contains*reach,axis=1)],axis=1)
    low=np.searchsorted(orr,hr,side='left');high=np.searchsorted(orr,hr,side='right')
    lower=prefix[low]-bycard[h[:,0],low]-bycard[h[:,1],low]
    higher=prefix[-1]-prefix[high]
    higher-=bycard[h[:,0],-1]-bycard[h[:,0],high]
    higher-=bycard[h[:,1],-1]-bycard[h[:,1],high]
    lookup=np.zeros(52*52);lookup[o[:,0]*52+o[:,1]]=reach
    same=lookup[h[:,0]*52+h[:,1]]
    valid=prefix[-1]-bycard[h[:,0],-1]-bycard[h[:,1],-1]+same
    tied=valid-lower-higher
    return dict(win=lower,lose=higher,tie=tied,valid=valid)


def values(mass,win,lose,tie):
    if not np.isfinite([win,lose,tie]).all():raise ValueError('Finite payouts required')
    return win*mass['win']+lose*mass['lose']+tie*mass['tie']
