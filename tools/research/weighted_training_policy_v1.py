"""Explicit weighted-model inference and own-reach policy averaging."""
import json
import numpy as np
from weighted_training_checkpoint_v1 import validate_model
from weighted_preflop_table_v1 import Table
from sampled_physical_preflop_table_v1 import validate_preflop, Table as BaseTable
from sampled_visible_features_bulk_v1 import features
from sampled_physical_root_evaluation_v1 import hand_class
from sampled_physical_bank_v1 import histories


class RootTable:
    def __init__(self,state,context_source,catalog_source):
        self.player = 0; self.context = json.loads(context_source); self.rows = {}
        root = self.context['nodes'][0]
        if root['kind'] != 0 or root['actor'] != 0 or [a['kind'] for a in root['actions']] != ['fold','call','raise','jam']:
            raise ValueError('Four-action BB root required')
        catalog = json.loads(catalog_source)
        if catalog['context_source'] != context_source: raise ValueError('Changed catalog')
        probabilities = state.probabilities(np.full((169,4),.25)); seen = set()
        for item in catalog['native_observations']:
            if item['player'] != 0: continue
            o = item['observation']; key = validate_preflop(o,self.context,0)
            if key[0] != 1 or o['phase'] != 0 or o['n'] != 4 or o['own_history'] != []:
                raise ValueError('Invalid root catalog row')
            c = hand_class([key[1]&63,(key[1]>>6)&63])
            if c != item['hand_class'] or c in seen: raise ValueError('Invalid catalog class')
            seen.add(c)
            if state.counts[c]: self.rows[key] = (4,tuple(sorted(o['active_features'])),probabilities[c])
        if seen != set(range(169)): raise ValueError('Complete root catalog required')

    def apply(self,obs,p):
        for o in obs:
            if int(o['hi']) == 1 and (o['actor'] != 0 or o['own_history'] != []):
                raise ValueError('Root must have no own-action ancestors')
        return BaseTable.apply(self,obs,p)


def probabilities(queries, model, *, device, catalog_source, matrix_sha256, entry_mass):
    if device not in ('cpu','cuda'): raise ValueError('Explicit inference device required')
    source = queries['context_source']
    root,_,exact = validate_model(model,context_source=source,catalog_source=catalog_source,
        matrix_sha256=matrix_sha256,entry_mass=entry_mass)
    obs = queries['observations']
    if not obs: raise ValueError('Nonempty observations required')
    x = features(obs).astype(np.float64)
    if any(type(o['actor']) is not int or o['actor'] not in (0,1) or type(o['n']) is not int or o['n'] not in (2,3,4) for o in obs):
        raise ValueError('Invalid actor or action menu')
    actors = np.array([o['actor'] for o in obs]); arity = np.array([o['n'] for o in obs]); scores = np.zeros((len(obs),4))
    for player,net in enumerate(model['networks']):
        ids = np.flatnonzero(actors == player)
        if not len(ids): continue
        y = x[ids]
        if device == 'cuda':
            import torch
            if torch.backends.cuda.matmul.allow_tf32 or torch.backends.cudnn.allow_tf32: raise ValueError('Disable TF32')
            y = torch.as_tensor(y,device='cuda')
        for layer,shape in enumerate(((64,302),(64,64),(4,64))):
            w = np.asarray(net[f'w{layer}'],dtype=np.float32).astype(np.float64).reshape(shape)
            b = np.asarray(net[f'b{layer}'],dtype=np.float32).astype(np.float64)
            if device == 'cpu':
                y = y@w.T+b
                if layer < 2: y = np.maximum(y,0.)
            else:
                y = y@torch.as_tensor(w,device='cuda').T+torch.as_tensor(b,device='cuda')
                if layer < 2: y = torch.relu(y)
        scores[ids] = y if device == 'cpu' else y.cpu().numpy()
    if not np.isfinite(scores).all(): raise ValueError('Nonfinite network scores')
    legal = np.arange(4)[None,:] < arity[:,None]
    p = np.maximum(scores,0.)*legal; sums = p.sum(1); positive = sums > 0
    p[positive] /= sums[positive,None]
    ids = np.flatnonzero(~positive); p[ids,np.argmax(np.where(legal,scores,-np.inf),axis=1)[ids]] = 1.
    coverage = []
    for t in model['preflop_tables']:
        if t is None: coverage.append(0)
        else:
            p,rows = Table(t,source).apply(obs,p); coverage.append(len(rows))
    p,er = exact.apply(obs,p); p,rr = RootTable(root,source,catalog_source).apply(obs,p)
    if np.max(abs(p.sum(1)-1)) > 1e-12 or np.any(p < 0) or np.any(p[~legal]): raise ValueError('Invalid policy')
    return p,dict(weighted_table_rows=coverage,exact_btn_rows=len(er),weighted_root_rows=len(rr))


def average(queries, documents, *, completed_iterations, weights_by_player, guard, **args):
    documents = list(documents); weights = np.asarray(weights_by_player,dtype=np.float64)
    if (type(completed_iterations) is not int or completed_iterations < 1 or len(documents) != completed_iterations
            or weights.shape != (2,completed_iterations) or not np.isfinite(weights).all() or np.any(weights <= 0)
            or not np.isfinite(weights.sum())): raise ValueError('Complete ordered played models and positive weights required')
    obs = queries['observations']; history = histories(obs); actors = np.array([o['actor'] for o in obs])
    numerator = np.zeros((len(obs),4)); denominator = np.zeros(len(obs))
    for g,model in enumerate(documents):
        guard()
        if model['generation'] != g: raise ValueError('Unplayed or reordered model in average')
        p,_ = probabilities(queries,model,**args)
        reach = weights[actors,g].copy()
        for i,prior in enumerate(history):
            for index,action in prior: reach[i] *= p[index,action]
        numerator += p*reach[:,None]; denominator += reach
    supported = denominator > 0; result = np.zeros_like(numerator)
    result[supported] = numerator[supported]/denominator[supported,None]
    for i in np.flatnonzero(~supported): result[i,:obs[i]['n']] = 1./obs[i]['n']
    if not np.isfinite(result).all() or np.max(abs(result.sum(1)-1)) > 1e-12: raise ValueError('Invalid average')
    return result,denominator
