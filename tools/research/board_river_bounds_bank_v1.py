"""Research-only per-model river projection before own-reach policy averaging."""
from copy import deepcopy
import numpy as np
from board_training_bank_layout_v1 import prepare_layout,validate_queries
from shared_visible_query_arrays_v1 import prepare
from sampled_visible_hybrid_gpu_bank_bulk_v1 import prepare_tables
from sampled_physical_bank_v1 import histories
from board_river_strength_features_v1 import geometry
from board_river_bounds_math_v1 import project,policy


def make_layout(documents,weights,*,guard,**args):
    documents=list(documents)
    result=prepare_layout(documents,weights,guard=guard,**args)
    scales=np.asarray([d['advantage_scales'] for d in documents],dtype=np.float64)
    if scales.shape!=(result['count'],2) or not np.isfinite(scales).all() or np.any(scales<=0):
        raise ValueError('Every saved model/player needs its own finite positive scale')
    result['scales']=scales.copy()
    return result


def prepare_queries(query,layout,catalog):
    query=deepcopy(query);validate_queries(layout,query)
    arrays=prepare(query);obs=query['observations']
    active=np.asarray([o['active_features'] for o in obs],dtype=np.int64)
    arity=np.asarray([o['n'] for o in obs],dtype=np.int64)
    phases=np.asarray([o['phase'] for o in obs],dtype=np.int64)
    if (not np.array_equal(active[:,14],133+arrays.actors)
            or not np.array_equal(active[:,15],135+phases)):
        raise ValueError('Observation actor/phase differs from visible encoding')
    eligible,public=geometry(active,arity,catalog)
    links=histories(obs)
    # Track direct projection separately from altered weights inherited on river.
    affected=np.array([any(eligible[j] for j,_ in link) for link in links])
    assert not np.any(affected&(phases<3))
    return dict(queries=query,arrays=arrays,arity=arity,phase=phases,eligible=eligible,
                public=public,history=links,reach_affected=affected)


def cpu_probabilities(scores,actors,arity,eligible,public,scales,enabled):
    if enabled:
        scores=scores.copy()
        for actor in (0,1):
            ids=np.flatnonzero(actors==actor)
            if len(ids):scores[ids]=project(scores[ids],arity[ids],eligible[ids],public[ids],scales[actor])
    return policy(scores,arity)


def cpu_accumulate(numerator,denominator,p,actors,weights,history):
    reach=weights[actors].copy()
    for i,prior in enumerate(history):
        for ancestor,action in prior:reach[i]*=p[ancestor,action]
    numerator+=p*reach[:,None];denominator+=reach


def cpu_finish(numerator,denominator,legal):
    supported=denominator>0;out=np.zeros_like(numerator)
    out[supported]=numerator[supported]/denominator[supported,None]
    out[~supported]=legal[~supported]/legal[~supported].sum(axis=1,keepdims=True)
    assert np.isfinite(out).all() and np.all(out>=0) and np.all(out[~legal]==0)
    assert np.max(abs(out.sum(axis=1)-1))<1e-12
    return out,denominator


def cpu_average(layout,prepared,*,enabled,guard):
    validate_queries(layout,prepared['queries']);a=prepared['arrays'];n=len(a.actors)
    ids,values,mask=prepare_tables(prepared['queries'],layout['tables'],layout['context_source'])
    ids=np.asarray(ids,dtype=np.int64)
    numerator=np.zeros((n,4));denominator=np.zeros(n)
    for g in range(layout['count']):
        guard();scores=np.zeros((n,4))
        for actor in (0,1):
            selected=np.flatnonzero(a.actors==actor);y=a.features[selected]
            for layer in range(3):
                w=layout['parameters'][f'w{layer}'][g,actor];b=layout['parameters'][f'b{layer}'][g,actor]
                y=y@w.T+b
                if layer!=2:y=np.maximum(y,0.)
            scores[selected]=y
        p=cpu_probabilities(scores,a.actors,prepared['arity'],prepared['eligible'],prepared['public'],layout['scales'][g],enabled)
        if len(ids):p[ids]=np.where(mask[g,:,None],values[g],p[ids])
        cpu_accumulate(numerator,denominator,p,a.actors,layout['weights'][:,g],prepared['history'])
    return cpu_finish(numerator,denominator,a.legal)


def cuda_probabilities(scores,actors,legal,eligible,public,scales,enabled):
    """Independent batched tensor implementation; scales are [models, players]."""
    import torch
    if enabled:
        scores=scores.clone();unit=scales[:,actors[eligible]]
        p,c,r,_=public[eligible].T
        delta=(scores[:,eligible,1]-scores[:,eligible,0])*unit
        bounded=torch.maximum(torch.minimum(delta,p-r),-c)
        adjustment=(bounded-delta)/(2*unit)
        scores[:,eligible,0]-=adjustment;scores[:,eligible,1]+=adjustment
    positive=torch.clamp(scores,min=0)*legal
    mass=positive.sum(dim=2,keepdim=True)
    fallback=torch.nn.functional.one_hot(scores.masked_fill(~legal,-torch.inf).argmax(dim=2),4).double()
    return torch.where(mass>0,positive/mass.clamp_min(1e-300),fallback)


def cuda_accumulate(numerator,denominator,p,actors,weights,prior,action,valid):
    import torch
    reach=weights[actors].transpose(0,1).clone()
    for j in range(prior.shape[1]):
        factors=p[:,prior[:,j],action[:,j]]
        reach*=torch.where(valid[:,j],factors,1.)
    for m in range(len(p)):
        numerator+=p[m]*reach[m].unsqueeze(1);denominator+=reach[m]


def cuda_finish(numerator,denominator,legal):
    import torch
    supported=denominator>0;out=torch.empty_like(numerator)
    out[supported]=numerator[supported]/denominator[supported].unsqueeze(1)
    out[~supported]=legal[~supported].double()/legal[~supported].sum(dim=1,keepdim=True)
    assert torch.isfinite(out).all() and not (out<0).any() and not (out*~legal).any()
    assert (out.sum(dim=1)-1).abs().max()<1e-12
    return out.cpu().numpy(),denominator.cpu().numpy()


class CudaBank:
    def __init__(self,layout,*,guard):
        import torch
        guard()
        if not torch.cuda.is_available() or torch.backends.cuda.matmul.allow_tf32 or torch.backends.cudnn.allow_tf32:
            raise ValueError('Explicit float64 CUDA configuration required')
        self.layout=layout
        self.parameters={k:torch.tensor(v,device='cuda') for k,v in layout['parameters'].items()}
        self.weights=torch.tensor(layout['weights'],device='cuda');self.scales=torch.tensor(layout['scales'],device='cuda')
        self.count=layout['count']

    def prepare(self,prepared):
        import torch
        validate_queries(self.layout,prepared['queries']);a=prepared['arrays']
        values={k:torch.tensor(getattr(a,k),device='cuda') for k in ('features','actors','legal','prior','action','valid')}
        for k in ('eligible','public'):values[k]=torch.tensor(prepared[k],device='cuda')
        ids,table,mask=prepare_tables(prepared['queries'],self.layout['tables'],self.layout['context_source'])
        values.update(table_ids=torch.tensor(ids,dtype=torch.long,device='cuda'),table=torch.tensor(table,device='cuda'),
                      table_mask=torch.tensor(mask,device='cuda'))
        values['ids']=[torch.nonzero(values['actors']==p).flatten() for p in (0,1)]
        return values

    def average_prepared(self,a,*,enabled,chunk,guard):
        import torch
        if type(chunk) is not int or chunk<1:raise ValueError('Positive model chunk required')
        n=len(a['actors']);numerator=torch.zeros((n,4),dtype=torch.float64,device='cuda')
        denominator=torch.zeros(n,dtype=torch.float64,device='cuda')
        with torch.no_grad():
            for start in range(0,self.count,chunk):
                guard();stop=min(start+chunk,self.count);count=stop-start
                scores=torch.zeros((count,n,4),dtype=torch.float64,device='cuda')
                for player,indices in enumerate(a['ids']):
                    if not len(indices):continue
                    y=a['features'][indices].unsqueeze(0).expand(count,-1,-1)
                    for layer in range(3):
                        w=self.parameters[f'w{layer}'][start:stop,player];b=self.parameters[f'b{layer}'][start:stop,player]
                        y=torch.bmm(y,w.transpose(1,2))+b.unsqueeze(1)
                        if layer!=2:y=torch.relu(y)
                    scores[:,indices]=y
                assert torch.isfinite(scores).all()
                p=cuda_probabilities(scores,a['actors'],a['legal'],a['eligible'],a['public'],self.scales[start:stop],enabled)
                ids=a['table_ids']
                if len(ids):p[:,ids]=torch.where(a['table_mask'][start:stop,:,None],a['table'][start:stop],p[:,ids])
                cuda_accumulate(numerator,denominator,p,a['actors'],self.weights[:,start:stop],a['prior'],a['action'],a['valid'])
        return cuda_finish(numerator,denominator,a['legal'])
