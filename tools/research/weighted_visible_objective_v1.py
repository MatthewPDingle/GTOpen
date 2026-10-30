"""Weighted grouped least squares; weights multiply loss, not target values."""
import numpy as np
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from sampled_visible_features_bulk_v1 import features


def grouped_rows(reservoir):
    if not isinstance(reservoir,WeightedPhysicalReservoir) or not reservoir.size:
        raise ValueError('Nonempty explicitly weighted reservoir required')
    n=reservoir.size
    _,first,inverse,counts=np.unique(reservoir.keys[:n],axis=0,return_index=True,return_inverse=True,return_counts=True)
    active=reservoir.active[first].copy();arity=reservoir.arity[first].copy()
    if (not np.array_equal(active[inverse],reservoir.active[:n]) or not np.array_equal(arity[inverse],reservoir.arity[:n])
        or np.any(arity<2) or np.any(arity>4) or np.any(active>=269) or np.any(np.diff(active.astype(int),axis=1)<=0)):
        raise ValueError('Invalid or conflicting observation geometry')
    w=reservoir.deal_weights[:n];values=reservoir.values[:n]
    legal=np.arange(4)[None,:]<reservoir.arity[:n,None]
    if (not np.isfinite(w).all() or np.any(w<=0) or np.any(w>65536) or not np.isfinite(values).all() or np.any(values[~legal])):
        raise ValueError('Invalid weighted target')
    scale=max(.01,float(np.sqrt(np.sum(values**2*w[:,None])/(4*w.sum()))))
    if not np.isfinite(scale):raise ValueError('Scale overflow')
    mass=np.bincount(inverse,weights=w,minlength=len(counts))
    means=np.zeros((len(counts),4),dtype=np.float64)
    targets=values/scale
    np.add.at(means,inverse,targets*w[:,None]);means/=mass[:,None]
    denominator=float(np.dot(mass,arity.astype(np.float64)))
    variance=float(np.sum((targets-means[inverse])**2*legal*w[:,None])/denominator)
    if not np.isfinite(means).all() or not np.isfinite(denominator) or denominator<=0 or not np.isfinite(variance):
        raise ValueError('Objective overflow')
    return dict(active=active,arity=arity,counts=counts,masses=mass,targets=means,scale=scale,
        denominator=denominator,variance=variance,examples=n,method='source-deal-weighted-visible-objective-v1')


class PreparedWeightedObjective:
    def __init__(self,grouped,device,*,dtype,guard):
        import torch
        guard();device=torch.device(device)
        if device.type not in ('cpu','cuda') or dtype not in (torch.float32,torch.float64):raise ValueError('Explicit numeric backend required')
        if grouped.get('method')!='source-deal-weighted-visible-objective-v1':raise ValueError('Weighted grouped data required')
        visible=features([dict(active_features=row.tolist()) for row in grouped['active']])
        weights=(np.arange(4)[None,:]<grouped['arity'][:,None])*grouped['masses'][:,None]
        self.x=torch.as_tensor(visible,dtype=dtype,device=device)
        self.target=torch.as_tensor(grouped['targets'],dtype=dtype,device=device)
        self.weight=torch.as_tensor(weights,dtype=dtype,device=device)
        self.denominator=grouped['denominator'];guard()

    def objective(self,model,chunk_size,guard,backward=False):
        import torch
        if type(chunk_size) is not int or chunk_size<1:raise ValueError('Positive chunk size required')
        parameter=next(model.parameters())
        if parameter.dtype!=self.x.dtype or parameter.device!=self.x.device:raise ValueError('Model/backend mismatch')
        total=torch.zeros((),dtype=torch.float64,device=self.x.device)
        for start in range(0,len(self.x),chunk_size):
            guard();stop=min(start+chunk_size,len(self.x))
            loss=((model(self.x[start:stop])-self.target[start:stop]).square()*self.weight[start:stop]).sum()/self.denominator
            total+=loss.detach().double()
            if backward:loss.backward()
        value=float(total)
        if not np.isfinite(value):raise ValueError('Nonfinite weighted objective')
        return value
