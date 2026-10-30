"""Visible-row-only batched inference for the fixed 269-input poker adapter."""
import numpy as np


def predict(observations, networks, device='cpu'):
    import torch
    if device not in ('cpu','cuda'):
        raise ValueError('Explicit CPU or CUDA device required')
    if len(networks)!=2 or not observations:
        raise ValueError('Two fixed player networks and a nonempty batch required')
    x=np.zeros((len(observations),269),np.float32)
    actors=np.empty(len(observations),np.int64);mask=np.zeros((len(observations),4))
    for i,o in enumerate(observations):
        active=o['active_features'];n=o['n'];actor=o['actor']
        if len(active)!=36 or len(set(active))!=36 or any(type(j) is not int or not 0<=j<269 for j in active):
            raise ValueError('Invalid visible feature row')
        if actor not in (0,1) or n not in (2,3,4):raise ValueError('Invalid actor or legal menu')
        x[i,active]=1;actors[i]=actor;mask[i,:n]=1
    scores=np.zeros((len(x),4))
    for player in (0,1):
        ids=np.flatnonzero(actors==player)
        if not len(ids):continue
        # Loading fixed weights must not consume the caller's CPU training RNG.
        with torch.random.fork_rng(devices=[]):
            model=torch.nn.Sequential(torch.nn.Linear(269,64),torch.nn.ReLU(),torch.nn.Linear(64,64),torch.nn.ReLU(),torch.nn.Linear(64,4))
        with torch.no_grad():
            for layer,j in enumerate((0,2,4)):
                model[j].weight.copy_(torch.tensor(networks[player][f'w{layer}']).reshape(model[j].weight.shape))
                model[j].bias.copy_(torch.tensor(networks[player][f'b{layer}']))
            model=model.to(device)
            scores[ids]=model(torch.from_numpy(x[ids]).to(device)).cpu().numpy().astype(float)
    if not np.isfinite(scores).all():raise ValueError('Nonfinite network output')
    p=np.maximum(scores,0)*mask;sums=p.sum(axis=1);positive=sums>0
    p[positive]/=sums[positive,None]
    for i in np.flatnonzero(~positive):p[i,int(np.argmax(scores[i,:observations[i]['n']]))]=1.
    assert np.max(np.abs(p.sum(axis=1)-1))<1e-12 and not np.any(p*(1-mask))
    return scores,p


def policy_document(queries, probabilities):
    if np.asarray(probabilities).shape!=(len(queries['observations']),4):
        raise ValueError('Policy rows do not match the exported query count')
    return dict(format=1,context=queries['context'],batch=queries['batch'],policies=[
        dict(hi=o['hi'],lo=o['lo'],actor=o['actor'],n=o['n'],probabilities=list(map(float,p)))
        for o,p in zip(queries['observations'],probabilities)])
