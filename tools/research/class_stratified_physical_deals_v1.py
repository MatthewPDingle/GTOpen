"""Research-only full-deck BB-class stratification with explicit deal weights.

Not a drop-in training sampler: every downstream observation/target needs its
source-deal weight. The existing unweighted training/evaluation paths are unchanged.
"""
import copy
import numpy as np
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS, MASKS, CLASSES

METHOD='bb-class-stratified-physical-deals-v1'


class ClassStratifiedDeals:
    def __init__(self, context_source, *, seed):
        self.base=PhysicalDeals(context_source,mode='full_deck',seed=seed)
        self.mass=np.bincount(CLASSES,weights=self.base.first[0],minlength=169)
        self.active=np.flatnonzero(self.mass>0)
        if not len(self.active):raise ValueError('Nonempty physical class support required')
        self.indices={int(c):np.flatnonzero((CLASSES==c)&(self.base.first[0]>0)) for c in self.active}
        self.probabilities={c:self.base.first[0][ids]/self.mass[c] for c,ids in self.indices.items()}
        self.batches=0

    def sample(self,count):
        if type(count) is not int or not len(self.active)<=count<=65536:
            raise ValueError('At least one deal per supported class and at most 65536 required')
        rng=self.base.rng;k=len(self.active)
        allocation=np.zeros(169,dtype=np.int64)
        allocation[self.active]=count//k
        remainder=count%k
        if remainder:allocation[rng.choice(self.active,size=remainder,replace=False)]+=1
        order=np.repeat(np.arange(169),allocation)
        rng.shuffle(order)
        weights_by_class=np.zeros(169,dtype=np.float64)
        weights_by_class[self.active]=count*self.mass[self.active]/allocation[self.active]
        deals=[]
        for c in order:
            c=int(c);i=int(rng.choice(self.indices[c],p=self.probabilities[c]))
            second=self.base.live[0][1]*((MASKS&MASKS[i])==0)
            second=second/second.sum()
            j=int(rng.choice(len(PAIRS),p=second))
            physical=[int(x) for x in PAIRS[i]]+[int(x) for x in PAIRS[j]]
            remaining=[x for x in range(52) if x not in physical]
            physical.extend(int(x) for x in rng.choice(remaining,size=5,replace=False))
            physical[:2]=sorted(physical[:2]);physical[2:4]=sorted(physical[2:4]);physical[4:7]=sorted(physical[4:7])
            assert len(set(physical))==9
            deals.append(physical)
        self.base.draws+=count;self.batches+=1
        return dict(format=1,method=METHOD,context_sha256=self.base.context_sha256,
            deals=deals,hand_classes=order.tolist(),class_counts=allocation.tolist(),
            class_mass=self.mass.tolist(),deal_weights=weights_by_class[order].tolist(),
            weight_meaning='Conditional-allocation importance weight N*p(class)/n(class); apply to every source-deal contribution.',
            training_qualified=False)

    def checkpoint(self):
        return dict(format=1,method=METHOD,base=self.base.checkpoint(),batches=self.batches)

    @classmethod
    def restore(cls,state,context_source):
        if state.get('format')!=1 or state.get('method')!=METHOD:
            raise ValueError('Explicit stratified checkpoint identity required')
        if type(state.get('batches')) is not int or state['batches']<0:
            raise ValueError('Invalid batch counter')
        if state['base'].get('mode')!='full_deck' or state['base'].get('manifest_sha256') is not None:
            raise ValueError('Full-deck source required')
        result=cls(context_source,seed=0)
        result.base=PhysicalDeals.restore(copy.deepcopy(state['base']),context_source)
        result.batches=state['batches']
        if (result.batches==0)!=(result.base.draws==0) or result.base.draws<result.batches*len(result.active):
            raise ValueError('Draw and batch counters disagree')
        return result
