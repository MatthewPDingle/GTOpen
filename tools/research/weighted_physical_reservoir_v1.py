"""Separately typed uniform visit reservoir with source-deal importance weights."""
import copy
import json
import math
from pathlib import Path
import numpy as np
from sampled_physical_reservoir_v1 import PhysicalReservoir, checked_row

METHOD='physical-visit-reservoir-with-deal-weights-v1'
ARRAYS=('keys','active','arity','values','iterations','deal_weights')


def checked_weight(value):
    if isinstance(value,(bool,np.bool_)) or not isinstance(value,(int,float,np.integer,np.floating)):
        raise ValueError('Explicit numeric importance weight required')
    value=float(value)
    if not math.isfinite(value) or not 0<value<=65536:
        raise ValueError('Positive bounded importance weight required')
    return value


class WeightedPhysicalReservoir(PhysicalReservoir):
    def __init__(self,capacity,player,seed,context_source):
        super().__init__(capacity,player,seed,context_source)
        self.deal_weights=np.zeros(capacity,dtype=np.float64)

    def add(self,observation,values,iteration,*,deal_weight):
        if observation['actor']!=self.player:raise ValueError('Wrong player')
        if type(iteration) is not int or not 1<=iteration<2**64:raise ValueError('Positive iteration required')
        weight=checked_weight(deal_weight)
        row=checked_row(observation,values)
        self._insert(row,iteration,deal_weight=weight)

    def _insert(self,row,iteration,*,deal_weight):
        weight=checked_weight(deal_weight)
        if type(iteration) is not int or not 1<=iteration<2**64:raise ValueError('Positive iteration required')
        if self.seen>=2**63-1:raise OverflowError('Visit counter exhausted')
        self.seen+=1
        slot=self.seen-1 if self.seen<=self.capacity else int(self.rng.integers(self.seen))
        if slot<self.capacity:
            self.keys[slot],self.active[slot],self.arity[slot],self.values[slot]=row
            self.iterations[slot]=iteration;self.deal_weights[slot]=weight

    def summary(self):
        value=super().summary()
        value.update(method=METHOD,retained_weight=float(self.deal_weights[:self.size].sum()),
            allocated_payload_bytes=value['allocated_payload_bytes']+self.deal_weights.nbytes)
        return value

    def save(self,path):
        metadata=dict(format=2,method=METHOD,capacity=self.capacity,player=self.player,seen=self.seen,
            context_sha256=self.context_sha256,rng=copy.deepcopy(self.rng.bit_generator.state))
        with Path(path).open('xb') as f:
            np.savez(f,metadata=np.array(json.dumps(metadata)),**{k:getattr(self,k)[:self.size] for k in ARRAYS})

    @classmethod
    def load(cls,path,context_source):
        with np.load(path,allow_pickle=False) as data:
            if set(data.files)!=set(ARRAYS)|{'metadata'}:raise ValueError('Explicit weighted checkpoint arrays required')
            m=json.loads(str(data['metadata']))
            if m.get('format')!=2 or m.get('method')!=METHOD or type(m.get('seen')) is not int or not 0<=m['seen']<2**63:
                raise ValueError('Unsupported weighted checkpoint')
            result=cls(m['capacity'],m['player'],0,context_source)
            if result.context_sha256!=m['context_sha256']:raise ValueError('Changed context')
            size=min(m['seen'],m['capacity'])
            for name in ARRAYS:
                target=getattr(result,name);source=data[name]
                if source.dtype!=target.dtype or source.shape!=target[:size].shape:raise ValueError('Checkpoint array mismatch')
                target[:size]=source
            for i in range(size):
                checked_row(dict(hi=str(result.keys[i,0]),lo=str(result.keys[i,1]),actor=result.player,
                    n=int(result.arity[i]),active_features=result.active[i].astype(int).tolist()),result.values[i])
                checked_weight(result.deal_weights[i])
                if result.iterations[i]==0:raise ValueError('Missing iteration')
            result.rng.bit_generator.state=m['rng'];result.seen=m['seen']
            return result
