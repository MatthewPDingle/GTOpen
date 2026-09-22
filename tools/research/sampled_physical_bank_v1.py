"""Stream played network pairs into an own-reach-weighted behavioral average."""
import numpy as np
from sampled_batch_model_v1 import predict


def histories(observations):
    result=[]
    for i,o in enumerate(observations):
        history=o['own_history'];seen=set();converted=[]
        for depth,item in enumerate(history):
            if len(item)!=3 or any(type(v) is not int for v in item):
                raise ValueError('Invalid own-history link')
            prior,action,n=item
            if not 0<=prior<len(observations) or prior==i or prior in seen:
                raise ValueError('Invalid or repeated ancestor')
            ancestor=observations[prior]
            if (ancestor['actor']!=o['actor'] or n!=ancestor['n'] or not 0<=action<n
                    or ancestor['phase']>o['phase'] or ancestor['own_history']!=history[:depth]):
                raise ValueError('Own-history chain is inconsistent')
            seen.add(prior);converted.append((prior,action))
        result.append(converted)
    return result


def average(queries, model_pairs, weights_by_player, *, device, guard):
    obs=queries['observations'];history=histories(obs)
    weights=np.asarray(weights_by_player,dtype=np.float64)
    if weights.ndim!=2 or weights.shape[0]!=2 or weights.shape[1]==0 or not np.isfinite(weights).all() or np.any(weights<=0):
        raise ValueError('Two positive finite model-weight sequences required')
    if not np.isfinite(weights.sum()):raise ValueError('Model weight overflow')
    numerator=np.zeros((len(obs),4));denominator=np.zeros(len(obs));processed=0
    actors=np.array([o['actor'] for o in obs],dtype=np.int64)
    if np.any((actors!=0)&(actors!=1)):raise ValueError('Invalid actor')
    for m,networks in enumerate(model_pairs):
        guard()
        if m>=weights.shape[1]:raise ValueError('Too many played models')
        _,p=predict(obs,networks,device)
        reach=weights[actors,m].copy()
        for i,prior in enumerate(history):
            for index,action in prior:reach[i]*=p[index,action]
        numerator+=p*reach[:,None];denominator+=reach;processed+=1
    if processed!=weights.shape[1]:raise ValueError('Incomplete played model bank')
    supported=denominator>0;result=np.zeros_like(numerator)
    result[supported]=numerator[supported]/denominator[supported,None]
    for i in np.flatnonzero(~supported):result[i,:obs[i]['n']]=1./obs[i]['n']
    if np.max(np.abs(result.sum(1)-1))>1e-12:raise ValueError('Invalid averaged policy')
    return result,denominator
