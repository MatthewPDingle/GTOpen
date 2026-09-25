"""Experimental bulk-feature variant; original arithmetic and validation retained.

Not installed in the live matched trial. CPU/CUDA qualification is separate.
"""
import numpy as np
from exact_initial_hybrid_checkpoint_v1 import validate_model
from sampled_physical_preflop_table_v1 import Table
from sampled_visible_features_bulk_v1 import features


def predict(queries, model, *, catalog_source, matrix_sha256, entry_mass, device):
    if device not in ('cpu','cuda'):raise ValueError('Explicit CPU/CUDA inference required')
    exact=validate_model(model,queries['context_source'],catalog_source,matrix_sha256,entry_mass)
    obs=queries['observations'];exact.validate_queries(obs)
    if not obs:raise ValueError('Nonempty observations required')
    x=features(obs).astype(np.float64)
    actors=np.array([o['actor'] for o in obs]);arity=np.array([o['n'] for o in obs])
    if any(type(o['actor']) is not int or o['actor'] not in (0,1) or type(o['n']) is not int or o['n'] not in (2,3,4) for o in obs):
        raise ValueError('Invalid observation actor or action menu')
    scores=np.zeros((len(obs),4),dtype=np.float64)
    for player,net in enumerate(model['base_model']['networks']):
        ids=np.flatnonzero(actors==player)
        if not len(ids):continue
        y=x[ids]
        if device=='cuda':
            import torch
            if torch.backends.cuda.matmul.allow_tf32 or torch.backends.cudnn.allow_tf32:
                raise ValueError('Explicitly disable TF32')
            y=torch.as_tensor(y,device='cuda')
        for layer,shape in enumerate(((64,302),(64,64),(4,64))):
            w=np.asarray(net[f'w{layer}'],dtype=np.float32).astype(np.float64).reshape(shape)
            b=np.asarray(net[f'b{layer}'],dtype=np.float32).astype(np.float64)
            if device=='cpu':
                y=y@w.T+b
                if layer<2:y=np.maximum(y,0.)
            else:
                import torch
                y=y@torch.as_tensor(w,device='cuda').T+torch.as_tensor(b,device='cuda')
                if layer<2:y=torch.relu(y)
        scores[ids]=y if device=='cpu' else y.cpu().numpy()
    if not np.isfinite(scores).all():raise ValueError('Nonfinite network output')
    legal=np.arange(4)[None,:]<arity[:,None]
    p=np.maximum(scores,0.)*legal;sums=p.sum(1);positive=sums>0
    p[positive]/=sums[positive,None]
    ids=np.flatnonzero(~positive)
    p[ids,np.argmax(np.where(legal,scores,-np.inf),axis=1)[ids]]=1.
    coverage=[]
    for table in model['base_model']['preflop_tables']:
        if table is None:coverage.append(0)
        else:
            p,matched=Table(table,queries['context_source']).apply(obs,p);coverage.append(len(matched))
    p,matched=exact.apply(obs,p)
    if np.max(abs(p.sum(1)-1))>1e-12 or np.any(p<0) or np.any(p[~legal]):
        raise ValueError('Invalid resulting current policy')
    return scores,p,dict(base_table_rows=coverage,exact_btn_rows=len(matched))


def probabilities(queries, model, **kwargs):
    _,p,coverage=predict(queries,model,**kwargs)
    return p,coverage
