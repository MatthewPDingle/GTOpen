"""New preparation path; only visible-summary evaluation is vectorized."""
import numpy as np
from sampled_physical_bank_v1 import histories
from shared_visible_query_arrays_v1 import SharedQueryArrays
from visible_summaries_vector_v1 import features


def arrays(queries):
    observations=queries['observations']
    if not observations:raise ValueError('Nonempty query batch required')
    history=histories(observations);x=features(observations).astype(np.float64)
    actors=np.empty(len(observations),np.int64);mask=np.zeros((len(observations),4),dtype=bool)
    depth=max(map(len,history),default=0);prior=np.zeros((len(observations),depth),np.int64)
    action=np.zeros_like(prior);valid=np.zeros_like(prior,dtype=bool)
    for i,o in enumerate(observations):
        active,n,actor=o['active_features'],o['n'],o['actor']
        if len(active)!=36 or len(set(active))!=36 or any(type(j) is not int or not 0<=j<269 for j in active):raise ValueError('Invalid visible feature row')
        if type(actor) is not int or actor not in (0,1) or type(n) is not int or n not in (2,3,4):raise ValueError('Invalid actor or legal menu')
        x[i,active]=1;actors[i]=actor;mask[i,:n]=True
        for j,(index,a) in enumerate(history[i]):prior[i,j],action[i,j],valid[i,j]=index,a,True
    values=(x,actors,mask,prior,action,valid)
    for a in values:a.flags.writeable=False
    return SharedQueryArrays(*values)


def prepare(engine,queries):
    if queries['context_source']!=engine.context_source:raise ValueError('Current policy context mismatch')
    a=arrays(queries);obs=queries['observations'];table=a.legal.astype(np.float64);table/=table.sum(1,keepdims=True)
    mask=np.zeros(len(obs),dtype=bool)
    for t in engine.tables:
        table,ids=t.apply(obs,table);mask[np.asarray(ids,dtype=int)]=True
    return dict(queries=queries,arrays=a,table=table,mask=mask,arity=np.asarray([o['n'] for o in obs],dtype=int))
