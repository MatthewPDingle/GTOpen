"""Single-model visible-feature prediction with exact retained-preflop overrides."""
import numpy as np
from sampled_visible_initialization_v1 import features
from sampled_visible_hybrid_checkpoint_v1 import validate_model,FEATURE_SPEC
from sampled_physical_preflop_table_v1 import Table


def predict(queries,model,device='cpu'):
    import torch
    if device not in ('cpu','cuda'):raise ValueError('Explicit CPU or CUDA device required')
    context=queries['context_source'];validate_model(model,context)
    observations=queries['observations']
    if not observations:raise ValueError('Nonempty visible observations required')
    x=features(observations)
    actors=np.array([o['actor'] for o in observations]);arity=np.array([o['n'] for o in observations])
    if any(type(o['actor']) is not int or o['actor'] not in (0,1) or type(o['n']) is not int or o['n'] not in (2,3,4) for o in observations):
        raise ValueError('Invalid actor or legal action count')
    scores=np.zeros((len(observations),4))
    for player in (0,1):
        ids=np.flatnonzero(actors==player)
        if not len(ids):continue
        with torch.random.fork_rng(devices=[]):
            net=torch.nn.Sequential(torch.nn.Linear(FEATURE_SPEC['input_width'],64),torch.nn.ReLU(),
                torch.nn.Linear(64,64),torch.nn.ReLU(),torch.nn.Linear(64,4))
        with torch.no_grad():
            for layer,j in enumerate((0,2,4)):
                net[j].weight.copy_(torch.tensor(model['networks'][player][f'w{layer}']).reshape(net[j].weight.shape))
                net[j].bias.copy_(torch.tensor(model['networks'][player][f'b{layer}']))
            net=net.to(device)
            scores[ids]=net(torch.from_numpy(x[ids]).to(device)).cpu().numpy().astype(float)
    if not np.isfinite(scores).all():raise ValueError('Nonfinite visible network scores')
    legal=np.arange(4)[None,:]<arity[:,None]
    result=np.maximum(scores,0)*legal;sums=result.sum(1);positive=sums>0
    result[positive]/=sums[positive,None]
    ids=np.flatnonzero(~positive)
    result[ids,np.argmax(np.where(legal,scores,-np.inf),axis=1)[ids]]=1.
    covered=[0,0]
    for player,document in enumerate(model['preflop_tables']):
        if document is not None:
            result,indices=Table(document,context).apply(observations,result);covered[player]=len(indices)
    assert np.max(abs(result.sum(1)-1))<1e-12 and not np.any(result[~legal])
    return scores,result,covered


def probabilities(queries,model,device):
    _,result,covered=predict(queries,model,device)
    return result,covered
