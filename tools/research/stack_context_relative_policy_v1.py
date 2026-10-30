"""Versioned relative-input shared networks with context-local tables and own-reach averaging.

This is an inference/model-object contract, not a resumable training checkpoint.
"""
import copy
import json
import numpy as np
from stack_context_relative_inputs_v1 import SPEC,encoded
from weighted_preflop_table_v1 import Table
from sampled_visible_hybrid_checkpoint_v1 import publish,read_object

TYPE='stack-context-relative-policy-v1'
SHAPES={'w0':(64,387),'b0':(64,),'w1':(64,64),'b1':(64,),'w2':(4,64),'b2':(4,)}
SCALE='advantage_bb / context_starting_stack'

def uniform_networks():
    return [{k:([1.]*int(np.prod(s)) if k=='b2' else [0.]*int(np.prod(s))) for k,s in SHAPES.items()} for _ in (0,1)]

def model(registry,*,generation,networks,preflop_tables):
    value=dict(format=1,policy_type=TYPE,representation=SPEC,registry=registry.manifest,
        registry_sha256=registry.sha256,generation=generation,networks=copy.deepcopy(networks),
        preflop_tables=copy.deepcopy(preflop_tables),target_scaling=SCALE)
    validate(value,registry);return value

def initial(registry):
    return model(registry,generation=0,networks=uniform_networks(),
                 preflop_tables={key:[None,None] for key in registry.fit_contexts})

def validate(value,registry):
    if registry.manifest.get('representation')!=SPEC:raise ValueError('Relative registry required')
    if (value.get('format')!=1 or value.get('policy_type')!=TYPE or value.get('representation')!=SPEC
            or value.get('registry_sha256')!=registry.sha256 or value.get('registry')!=registry.manifest
            or value.get('target_scaling')!=SCALE):
        raise ValueError('Wrong shared-model format, representation, scaling or registry')
    generation=value.get('generation')
    if type(generation) is not int or generation<0:raise ValueError('Nonnegative complete model generation required')
    networks=value['networks']
    if not isinstance(networks,list) or len(networks)!=2:raise ValueError('Two player networks required')
    for net in networks:
        if set(net)!=set(SHAPES):raise ValueError('Wrong network parameter layout')
        for key,shape in SHAPES.items():
            array=np.asarray(net[key],dtype=np.float32)
            if array.shape!=(int(np.prod(shape)),) or not np.isfinite(array).all():
                raise ValueError('Finite 387-input network parameters required')
    tables=value['preflop_tables']
    if not isinstance(tables,dict) or set(tables)!=set(registry.fit_contexts):
        raise ValueError('Exactly the fitting contexts may own learned tables')
    for key,pair in tables.items():
        if not isinstance(pair,list) or len(pair)!=2:raise ValueError('Two table slots per context required')
        for actor,table in enumerate(pair):
            if table is None:continue
            parsed=Table(table,registry.source(key));source=table['source_reservoir']
            if parsed.player!=actor or source['player']!=actor or source['context_sha256']!=key:
                raise ValueError('Table context or actor mismatch')
            if sum(r['count'] for r in table['rows'])>source['retained']:
                raise ValueError('Table counts exceed retained observations')
    if generation==0 and (networks!=uniform_networks() or any(t is not None for pair in tables.values() for t in pair)):
        raise ValueError('Initial shared model must be uniform without learned tables')

def predict(value,registry,queries,*,context_sha256,device='cpu'):
    validate(value,registry)
    if device not in ('cpu','cuda'):raise ValueError('Explicit CPU/CUDA inference required')
    prepared=registry.prepare(queries,context_sha256=context_sha256);observations=queries['observations']
    x=prepared['features'].astype(np.float64);actors=np.asarray([o['actor'] for o in observations])
    arity=np.asarray([o['n'] for o in observations]);scores=np.zeros((len(x),4))
    if device=='cuda':
        import torch
        if torch.backends.cuda.matmul.allow_tf32 or torch.backends.cudnn.allow_tf32:raise ValueError('Disable TF32')
    for actor,net in enumerate(value['networks']):
        ids=np.flatnonzero(actors==actor)
        if not len(ids):continue
        y=x[ids]
        if device=='cuda':y=torch.as_tensor(y,device='cuda')
        for layer in range(3):
            w=np.asarray(net[f'w{layer}'],dtype=np.float32).astype(np.float64).reshape(SHAPES[f'w{layer}'])
            b=np.asarray(net[f'b{layer}'],dtype=np.float32).astype(np.float64)
            if device=='cpu':
                if layer==0:
                    y=(y[:,:362].copy()@w[:,:362].copy().T+b)+y[:,362:].copy()@w[:,362:].copy().T
                else:y=y@w.T+b
                if layer<2:y=np.maximum(y,0.)
            else:
                if layer==0:
                    y=(y[:,:362].contiguous()@torch.as_tensor(w[:,:362].copy(),device='cuda').T+torch.as_tensor(b,device='cuda'))+y[:,362:].contiguous()@torch.as_tensor(w[:,362:].copy(),device='cuda').T
                else:y=y@torch.as_tensor(w,device='cuda').T+torch.as_tensor(b,device='cuda')
                if layer<2:y=torch.relu(y)
        scores[ids]=y if device=='cpu' else y.cpu().numpy()
    if not np.isfinite(scores).all():raise ValueError('Nonfinite network scores')
    legal=np.arange(4)[None,:]<arity[:,None]
    p=np.maximum(scores,0.)*legal;sums=p.sum(1);positive=sums>0
    p[positive]/=sums[positive,None]
    ids=np.flatnonzero(~positive);p[ids,np.argmax(np.where(legal,scores,-np.inf),axis=1)[ids]]=1.
    for table in value['preflop_tables'].get(context_sha256,[None,None]):
        if table is not None:p,_=Table(table,registry.source(context_sha256)).apply(observations,p)
    if not np.isfinite(p).all() or np.any(p<0) or np.any(p[~legal]) or np.max(abs(p.sum(1)-1))>1e-12:
        raise ValueError('Invalid shared-model policy')
    return p,prepared

def average(documents,registry,queries,*,context_sha256,weights_by_player,device,guard):
    weights=np.asarray(weights_by_player,dtype=np.float64)
    if (not documents or weights.shape!=(2,len(documents)) or not np.isfinite(weights).all()
            or np.any(weights<=0) or not np.isfinite(weights.sum())):raise ValueError('Complete positive mixture weights required')
    actor=np.asarray([o['actor'] for o in queries['observations']]);n=len(actor)
    numerator=np.zeros((n,4));denominator=np.zeros(n)
    for generation,value in enumerate(documents):
        guard()
        if value['generation']!=generation:raise ValueError('Unplayed/reordered generation in average')
        p,prepared=predict(value,registry,queries,context_sha256=context_sha256,device=device)
        reach=weights[actor,generation].copy()
        for i,history in enumerate(prepared['own_history']):
            for parent,action in history:reach[i]*=p[parent,action]
        numerator+=reach[:,None]*p;denominator+=reach
    support=denominator>0;result=np.zeros_like(numerator)
    result[support]=numerator[support]/denominator[support,None]
    for i in np.flatnonzero(~support):result[i,:queries['observations'][i]['n']]=1./queries['observations'][i]['n']
    if not np.isfinite(result).all() or np.max(abs(result.sum(1)-1))>1e-12:raise ValueError('Invalid average')
    return result,denominator

def write_model(directory,value,registry):
    validate(value,registry)
    return dict(publish(directory,'relativestackmodel',encoded(value)),generation=value['generation'])

def read_model(directory,reference,registry):
    value=json.loads(read_object(directory,reference));validate(value,registry)
    if reference['generation']!=value['generation']:raise ValueError('Wrong model reference generation')
    return value


def extend_from_362(value,source_registry,target_registry):
    """Explicit neutral lift, never an implicit old-checkpoint migration."""
    import stack_context_policy_v1 as original
    original.validate(value,source_registry)
    if source_registry.manifest['contexts']!=target_registry.manifest['contexts']:
        raise ValueError('Identical contexts and fit/heldout roles required')
    networks=copy.deepcopy(value['networks'])
    for net in networks:
        old=np.asarray(net['w0'],dtype=np.float32).reshape(64,362)
        new=np.zeros((64,387),dtype=np.float32);new[:,:362]=old;net['w0']=new.reshape(-1).tolist()
    return model(target_registry,generation=value['generation'],networks=networks,
                 preflop_tables=value['preflop_tables'])
